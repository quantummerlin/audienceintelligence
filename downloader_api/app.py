"""
Social Media Downloader — Flask API backend
Deploy on PythonAnywhere (paid tier — no outbound network restrictions).

Endpoints:
  POST /api/info            — fetch metadata without downloading
  POST /api/prepare         — start background download, returns token
  GET  /api/status/<token>  — poll download progress
  GET  /api/file/<token>    — download completed file
  GET  /api/health          — health check
"""

import json
import os
import shutil
import sys
import tempfile
import threading
import time
import uuid
from collections import defaultdict
from pathlib import Path

from flask import Flask, after_this_request, jsonify, request, send_file
from flask_cors import CORS

# ── Make fb_video_downloader importable ──────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ── Static ffmpeg (no system install needed on PythonAnywhere) ───────────────
try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    pass  # ffmpeg must be on PATH manually if not installed

from fb_video_downloader.downloader import FacebookVideoDownloader

# ── App ───────────────────────────────────────────────────────────────────────
app = Flask(__name__)

ALLOWED_ORIGINS = os.environ.get(
    "ALLOWED_ORIGINS",
    "https://ai.quantummerlin.com,http://localhost:8080,http://127.0.0.1:8080",
).split(",")

CORS(app, origins=ALLOWED_ORIGINS, methods=["GET", "POST", "OPTIONS"])

# ── Job store ─────────────────────────────────────────────────────────────────
_JOBS: dict = {}
_JOBS_LOCK = threading.Lock()
_TEMP_ROOT = tempfile.mkdtemp(prefix="viddown_")
_MAX_JOB_AGE = 600  # seconds before temp files are cleaned up

# ── Simple rate limiter ───────────────────────────────────────────────────────
_RATE: dict = defaultdict(list)   # ip -> [timestamps]
_RATE_LOCK = threading.Lock()
_RATE_LIMIT = 20   # requests
_RATE_WINDOW = 60  # seconds


def _check_rate(ip: str) -> bool:
    """Return True if request is allowed."""
    now = time.time()
    with _RATE_LOCK:
        timestamps = [t for t in _RATE[ip] if now - t < _RATE_WINDOW]
        timestamps.append(now)
        _RATE[ip] = timestamps
        return len(timestamps) <= _RATE_LIMIT


# ── Helpers ───────────────────────────────────────────────────────────────────

def _validate_url(url: str) -> bool:
    """Basic URL validation — must be http/https and not too long."""
    return (
        isinstance(url, str)
        and url.startswith(("http://", "https://"))
        and len(url) <= 2000
        and " " not in url
    )


def _is_valid_uuid(value: str) -> bool:
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, AttributeError):
        return False


def _cleanup_old_jobs():
    """Remove jobs and temp files older than _MAX_JOB_AGE seconds."""
    now = time.time()
    with _JOBS_LOCK:
        stale = [t for t, j in _JOBS.items() if now - j["created_at"] > _MAX_JOB_AGE]
        for token in stale:
            job = _JOBS.pop(token)
            job_dir = job.get("job_dir", "")
            if job_dir and os.path.isdir(job_dir):
                shutil.rmtree(job_dir, ignore_errors=True)


def _get_job(token: str) -> dict | None:
    _cleanup_old_jobs()
    with _JOBS_LOCK:
        return _JOBS.get(token)


def _update_progress(token: str, d: dict):
    pct_str = d.get("_percent_str", "").strip().rstrip("%")
    try:
        pct = float(pct_str) if pct_str else 0.0
    except ValueError:
        pct = 0.0
    with _JOBS_LOCK:
        if token in _JOBS:
            _JOBS[token]["progress"] = round(pct, 1)
            _JOBS[token]["speed"] = d.get("_speed_str", "").strip()
            _JOBS[token]["eta"] = d.get("_eta_str", "").strip()


def _run_download(token: str, url: str, opts: dict):
    """Background thread: run yt-dlp and update job status."""
    job_dir = os.path.join(_TEMP_ROOT, token)
    os.makedirs(job_dir, exist_ok=True)

    with _JOBS_LOCK:
        _JOBS[token]["job_dir"] = job_dir
        _JOBS[token]["status"] = "downloading"

    try:
        dl = FacebookVideoDownloader(
            output_dir=job_dir,
            quality=opts.get("quality", "best"),
            audio_only=opts.get("audio_only", False),
            thumbnail_only=opts.get("thumbnail_only", False),
            subtitles=opts.get("subtitles", False),
            embed_thumbnail=opts.get("embed_thumbnail", False),
            start_time=opts.get("start_time") or None,
            end_time=opts.get("end_time") or None,
            filename_template="%(title)s.%(ext)s",
            progress_callback=lambda d: _update_progress(token, d),
        )
        result = dl.download(url)

        if result.success:
            files = list(Path(job_dir).iterdir())
            main_exts = {".mp4", ".mp3", ".jpg", ".jpeg", ".webm", ".mkv", ".m4a"}
            main_files = [f for f in files if f.suffix.lower() in main_exts]
            if not main_files:
                main_files = files
            main_file = (
                max(main_files, key=lambda f: f.stat().st_size)
                if main_files else None
            )
            with _JOBS_LOCK:
                _JOBS[token].update({
                    "status":     "ready",
                    "filepath":   str(main_file) if main_file else "",
                    "filename":   main_file.name if main_file else "",
                    "title":      result.title,
                    "platform":   result.platform,
                    "resolution": result.resolution,
                    "duration":   result.duration_seconds,
                    "progress":   100.0,
                })
        else:
            with _JOBS_LOCK:
                _JOBS[token]["status"] = "error"
                _JOBS[token]["error"] = result.error

    except Exception as exc:
        with _JOBS_LOCK:
            _JOBS[token]["status"] = "error"
            _JOBS[token]["error"] = str(exc)


# ── Routes ────────────────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "temp_root": _TEMP_ROOT})


@app.route("/api/info", methods=["POST"])
def info():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    if not _check_rate(ip):
        return jsonify({"error": "Too many requests. Please slow down."}), 429

    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not _validate_url(url):
        return jsonify({"error": "Invalid URL"}), 400

    dl = FacebookVideoDownloader()
    result = dl.get_info(url)
    if "error" in result:
        return jsonify(result), 422
    return jsonify(result)


@app.route("/api/prepare", methods=["POST"])
def prepare():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr or "")
    if not _check_rate(ip):
        return jsonify({"error": "Too many requests. Please slow down."}), 429

    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not _validate_url(url):
        return jsonify({"error": "Invalid URL"}), 400

    mode = data.get("mode", "video")
    opts = {
        "quality":         data.get("quality", "best"),
        "audio_only":      mode == "audio",
        "thumbnail_only":  mode == "thumbnail",
        "subtitles":       bool(data.get("subtitles", False)),
        "embed_thumbnail": bool(data.get("embed_thumbnail", False)),
        "start_time":      data.get("start_time") or None,
        "end_time":        data.get("end_time") or None,
    }

    token = str(uuid.uuid4())
    with _JOBS_LOCK:
        _JOBS[token] = {
            "status":     "pending",
            "progress":   0.0,
            "speed":      "",
            "eta":        "",
            "filepath":   "",
            "filename":   "",
            "title":      "",
            "platform":   "",
            "resolution": "",
            "duration":   0,
            "error":      "",
            "job_dir":    "",
            "created_at": time.time(),
        }

    thread = threading.Thread(
        target=_run_download, args=(token, url, opts), daemon=True
    )
    thread.start()
    return jsonify({"token": token})


@app.route("/api/status/<token>", methods=["GET"])
def status(token: str):
    if not _is_valid_uuid(token):
        return jsonify({"error": "Invalid token"}), 400
    job = _get_job(token)
    if not job:
        return jsonify({"error": "Job not found or expired"}), 404
    return jsonify({
        "status":     job["status"],
        "progress":   job["progress"],
        "speed":      job["speed"],
        "eta":        job["eta"],
        "filename":   job["filename"],
        "title":      job["title"],
        "platform":   job["platform"],
        "resolution": job["resolution"],
        "duration":   job["duration"],
        "error":      job["error"],
    })


@app.route("/api/file/<token>", methods=["GET"])
def serve_file(token: str):
    if not _is_valid_uuid(token):
        return jsonify({"error": "Invalid token"}), 400
    job = _get_job(token)
    if not job:
        return jsonify({"error": "Job not found or expired"}), 404
    if job["status"] != "ready":
        return jsonify({"error": "File not ready yet"}), 409

    filepath = job.get("filepath", "")
    if not filepath or not os.path.isfile(filepath):
        return jsonify({"error": "File missing on server"}), 500

    # Resolve to real path to prevent path traversal
    real_path = os.path.realpath(filepath)
    real_root = os.path.realpath(_TEMP_ROOT)
    if not real_path.startswith(real_root):
        return jsonify({"error": "Forbidden"}), 403

    filename = job["filename"]

    @after_this_request
    def schedule_cleanup(response):
        job_dir = job.get("job_dir", "")
        if job_dir:
            def _delete():
                time.sleep(60)  # give browser time to finish receiving
                shutil.rmtree(job_dir, ignore_errors=True)
            threading.Thread(target=_delete, daemon=True).start()
        return response

    return send_file(real_path, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
