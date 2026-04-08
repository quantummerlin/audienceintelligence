"""
Social Media Video / Audio Downloader — core logic.

Uses yt-dlp to download video or audio from Facebook, YouTube, Instagram,
TikTok, Twitter/X, Reddit, Twitch, Vimeo, Dailymotion, and 1000+ other sites.
Supports quality selection, audio-only (MP3) extraction, and progress reporting.
"""

import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Callable

try:
    import yt_dlp
    YTDLP_AVAILABLE = True
except ImportError:
    YTDLP_AVAILABLE = False


PLATFORM_PATTERNS = [
    (r"youtube\.com|youtu\.be", "YouTube"),
    (r"instagram\.com", "Instagram"),
    (r"tiktok\.com", "TikTok"),
    (r"twitter\.com|x\.com|t\.co", "Twitter/X"),
    (r"facebook\.com|fb\.com|fb\.watch", "Facebook"),
    (r"reddit\.com|redd\.it", "Reddit"),
    (r"twitch\.tv", "Twitch"),
    (r"vimeo\.com", "Vimeo"),
    (r"dailymotion\.com", "Dailymotion"),
    (r"pinterest\.com", "Pinterest"),
    (r"linkedin\.com", "LinkedIn"),
    (r"snapchat\.com", "Snapchat"),
]

_HISTORY_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "outputs", "download_history.json"
)


def _json_cookies_to_netscape(json_path: str) -> str:
    """
    Convert a JSON cookies file (exported by browser extensions like
    'Get cookies.txt LOCALLY') to Netscape format that yt-dlp accepts.
    Returns the path to a temporary .txt file.
    """
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    # Support both [{...}, ...] and {"cookies": [{...}, ...]}
    if isinstance(data, dict):
        cookies = data.get("cookies", [])
    else:
        cookies = data

    lines = ["# Netscape HTTP Cookie File", "# Generated automatically from JSON export", ""]
    for c in cookies:
        domain = c.get("domain", "")
        include_sub = "TRUE" if domain.startswith(".") else "FALSE"
        path = c.get("path", "/")
        secure = "TRUE" if c.get("secure") else "FALSE"
        # session cookies have no expiration; use 0
        expires = int(c.get("expirationDate") or 0)
        name = c.get("name", "")
        value = c.get("value", "")
        lines.append("\t".join([domain, include_sub, path, secure, str(expires), name, value]))

    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix="_cookies.txt", delete=False, encoding="utf-8"
    )
    tmp.write("\n".join(lines))
    tmp.close()
    return tmp.name


@dataclass
class DownloadResult:
    url: str
    filename: str = ""
    title: str = ""
    platform: str = ""
    duration_seconds: int = 0
    filesize_bytes: int = 0
    resolution: str = ""
    audio_only: bool = False
    subtitle_file: str = ""
    thumbnail_file: str = ""
    success: bool = False
    error: str = ""


class FacebookVideoDownloader:
    """
    Downloads video, audio, or thumbnails from Facebook, YouTube, Instagram,
    TikTok, Twitter/X, Reddit, Twitch, Vimeo, Dailymotion, and 1000+ other sites.

    Parameters
    ----------
    output_dir : str
        Directory where downloaded files are saved.
    quality : str
        One of ``"best"``, ``"worst"``, or a height like ``"720"``.
        Ignored when audio_only or thumbnail_only is True.
    audio_only : bool
        Extract audio only and save as MP3 (requires ffmpeg).
    thumbnail_only : bool
        Save the video thumbnail image only — no video downloaded.
    subtitles : bool
        Download available subtitles as .srt alongside the video.
    embed_thumbnail : bool
        Embed thumbnail as album art in the MP3 (requires ffmpeg, audio_only must be True).
    start_time : str | None
        Trim start, e.g. ``"1:30"`` or ``"90"`` (seconds).
    end_time : str | None
        Trim end, e.g. ``"4:00"`` or ``"240"`` (seconds).
    proxy : str | None
        Proxy URL, e.g. ``"http://user:pass@host:port"`` or ``"socks5://host:port"``.
    filename_template : str | None
        yt-dlp output template, e.g. ``"%(title)s.%(ext)s"``.
        Defaults to ``"%(uploader)s_%(id)s.%(ext)s"``.
    chrome_profile_dir : str | None
        Path to a saved Chrome profile dir for cookie-based auth.
    progress_callback : callable | None
        Called with a dict of yt-dlp progress info during download.
    """

    def __init__(
        self,
        output_dir: str = "outputs",
        quality: str = "best",
        audio_only: bool = False,
        thumbnail_only: bool = False,
        subtitles: bool = False,
        embed_thumbnail: bool = False,
        start_time: Optional[str] = None,
        end_time: Optional[str] = None,
        proxy: Optional[str] = None,
        filename_template: Optional[str] = None,
        chrome_profile_dir: Optional[str] = None,
        cookies_from_browser: Optional[str] = None,
        cookies_file: Optional[str] = None,
        progress_callback: Optional[Callable] = None,
    ):
        if not YTDLP_AVAILABLE:
            raise RuntimeError(
                "yt-dlp is not installed. Run: pip install yt-dlp"
            )

        self.output_dir = output_dir
        self.quality = quality
        self.audio_only = audio_only
        self.thumbnail_only = thumbnail_only
        self.subtitles = subtitles
        self.embed_thumbnail = embed_thumbnail
        self.start_time = start_time
        self.end_time = end_time
        self.proxy = proxy
        self.filename_template = filename_template
        self.chrome_profile_dir = chrome_profile_dir
        self.cookies_from_browser = cookies_from_browser
        self.cookies_file = cookies_file
        self.progress_callback = progress_callback or self._default_progress

        os.makedirs(self.output_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_info(self, url: str) -> dict:
        """
        Fetch metadata for a URL without downloading anything.

        Returns a dict with keys: title, platform, duration_seconds, uploader,
        view_count, formats (list of quality strings), is_playlist, playlist_count.
        Returns {"error": "..."} on failure.
        """
        url = url.strip()
        opts = self._base_ydl_opts()
        opts["quiet"] = True
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    return {"error": "No info returned"}
                seen: set = set()
                quality_summary = []
                for fmt in info.get("formats", []):
                    h = fmt.get("height")
                    if h and h not in seen:
                        seen.add(h)
                        quality_summary.append(f"{h}p")
                quality_summary.sort(key=lambda x: int(x[:-1]), reverse=True)
                return {
                    "title": info.get("title", ""),
                    "platform": self._detect_platform(url),
                    "duration_seconds": info.get("duration", 0) or 0,
                    "uploader": info.get("uploader") or info.get("channel", ""),
                    "view_count": info.get("view_count"),
                    "formats": quality_summary,
                    "is_playlist": info.get("_type") == "playlist",
                    "playlist_count": info.get("playlist_count"),
                }
        except Exception as exc:
            return {"error": str(exc)}

    def download(self, url: str) -> DownloadResult:
        """Download video/audio/thumbnail from any supported URL."""
        url = url.strip()
        if not url.lower().startswith(("http://", "https://")):
            return DownloadResult(
                url=url,
                success=False,
                error="Please provide a full URL starting with http:// or https://",
            )

        result = DownloadResult(url=url, audio_only=self.audio_only)
        result.platform = self._detect_platform(url)
        ydl_opts = self._build_ydl_opts(result)

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if info:
                    # For playlists use first entry for per-item metadata
                    entry = info
                    if info.get("_type") == "playlist":
                        entries = info.get("entries") or []
                        entry = entries[0] if entries else info
                    result.title = info.get("title", "")
                    result.duration_seconds = entry.get("duration", 0) or 0
                    result.filesize_bytes = (
                        entry.get("filesize") or entry.get("filesize_approx") or 0
                    )
                    if self.thumbnail_only:
                        result.resolution = "thumbnail"
                    elif self.audio_only:
                        result.resolution = "audio only (MP3)"
                    else:
                        height = entry.get("height")
                        width = entry.get("width")
                        if height and width:
                            result.resolution = f"{width}x{height}"
                        elif height:
                            result.resolution = f"{height}p"
                    result.success = True
                    # Resolve final filename (mp3 after ffmpeg conversion)
                    self._resolve_final_filename(result)
                    self._save_history(result)
        except yt_dlp.utils.DownloadError as exc:
            msg = str(exc)
            if "login" in msg.lower() or "private" in msg.lower() or "age" in msg.lower():
                result.error = (
                    "Content is private, age-restricted, or requires login.\n"
                    "Make sure you are logged in to your Chrome profile and "
                    "pass the chrome_profile_dir when creating the downloader."
                )
            else:
                result.error = msg
        except Exception as exc:
            result.error = str(exc)

        return result

    def list_formats(self, url: str) -> list:
        """Return a list of available formats for a URL."""
        url = url.strip()
        formats = []
        ydl_opts = self._base_ydl_opts()

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if info and "formats" in info:
                    for fmt in info["formats"]:
                        formats.append({
                            "format_id": fmt.get("format_id", ""),
                            "ext": fmt.get("ext", ""),
                            "resolution": fmt.get("resolution") or (
                                f"{fmt.get('width', '?')}x{fmt.get('height', '?')}"
                                if fmt.get("width") or fmt.get("height") else "audio only"
                            ),
                            "filesize": fmt.get("filesize") or fmt.get("filesize_approx"),
                            "vcodec": fmt.get("vcodec", ""),
                            "acodec": fmt.get("acodec", ""),
                            "note": fmt.get("format_note", ""),
                        })
        except Exception:
            pass

        return formats

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_platform(url: str) -> str:
        for pattern, name in PLATFORM_PATTERNS:
            if re.search(pattern, url, re.IGNORECASE):
                return name
        return "Unknown"

    def _build_output_template(self) -> str:
        template = self.filename_template or "%(uploader)s_%(id)s.%(ext)s"
        return os.path.join(self.output_dir, template)

    def _format_selector(self) -> str:
        if self.audio_only or self.thumbnail_only:
            return "bestaudio/best"
        q = self.quality.lower().strip()
        if q == "best":
            # Accept m4a audio stream too so Instagram/Facebook merges succeed
            return "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo[ext=mp4]+bestaudio/bestvideo+bestaudio/best"
        if q == "worst":
            return "worstvideo[ext=mp4]+worstaudio/worstvideo+worstaudio/worst"
        # numeric height e.g. "720"
        if q.isdigit():
            h = int(q)
            return (
                f"bestvideo[height<={h}][ext=mp4]+bestaudio[ext=m4a]"
                f"/bestvideo[height<={h}][ext=mp4]+bestaudio"
                f"/bestvideo[height<={h}]+bestaudio"
                f"/best[height<={h}]/best"
            )
        # passthrough custom selectors
        return q

    def _base_ydl_opts(self) -> dict:
        opts: dict = {
            "quiet": True,
            "no_warnings": False,
            "ignoreerrors": False,
            "nocheckcertificate": False,
            "http_headers": {
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                )
            },
        }

        # Cookie authentication — cookies file > browser > saved profile
        if self.cookies_file and os.path.isfile(self.cookies_file):
            # Auto-convert JSON exports to Netscape format
            if self.cookies_file.lower().endswith(".json"):
                converted = _json_cookies_to_netscape(self.cookies_file)
                opts["cookiefile"] = converted
            else:
                opts["cookiefile"] = self.cookies_file
        elif self.cookies_from_browser:
            opts["cookiesfrombrowser"] = (self.cookies_from_browser,)
        elif self.chrome_profile_dir and os.path.isdir(self.chrome_profile_dir):
            opts["cookiesfrombrowser"] = ("chrome", self.chrome_profile_dir, None, None)

        if self.proxy:
            opts["proxy"] = self.proxy

        return opts

    def _build_ydl_opts(self, result: DownloadResult) -> dict:
        opts = self._base_ydl_opts()
        opts["format"] = self._format_selector()
        opts["outtmpl"] = self._build_output_template()
        opts["progress_hooks"] = [self._make_progress_hook(result)]

        if self.thumbnail_only:
            opts["skip_download"] = True
            opts["writethumbnail"] = True
            opts["postprocessors"] = [{"key": "FFmpegThumbnailsConvertor", "format": "jpg"}]

        elif self.audio_only:
            postprocessors: list = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
            if self.embed_thumbnail:
                opts["writethumbnail"] = True
                postprocessors.append({"key": "EmbedThumbnail", "already_have_thumbnail": False})
            opts["postprocessors"] = postprocessors

        else:
            # Always remux/convert final output to mp4
            opts["merge_output_format"] = "mp4"
            video_postprocessors: list = [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}]
            if self.embed_thumbnail:
                opts["writethumbnail"] = True
                video_postprocessors.append({"key": "EmbedThumbnail", "already_have_thumbnail": False})
            opts["postprocessors"] = video_postprocessors
            if self.subtitles:
                opts["writesubtitles"] = True
                opts["writeautomaticsub"] = True
                opts["subtitlesformat"] = "srt/vtt/best"

        # Clip / trim
        if (self.start_time or self.end_time) and not self.thumbnail_only:
            start_sec = self._parse_time(self.start_time) if self.start_time else 0.0
            end_sec = self._parse_time(self.end_time) if self.end_time else float("inf")
            opts["download_ranges"] = yt_dlp.utils.download_range_func(None, [(start_sec, end_sec)])
            opts["force_keyframes_at_cuts"] = True

        return opts

    @staticmethod
    def _parse_time(t: str) -> float:
        """Convert '1:30', '1:30:00', or '90' to seconds."""
        parts = t.strip().split(":")
        try:
            if len(parts) == 1:
                return float(parts[0])
            elif len(parts) == 2:
                return int(parts[0]) * 60 + float(parts[1])
            else:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
        except (ValueError, IndexError):
            return 0.0

    def _make_progress_hook(self, result: DownloadResult):
        def hook(d: dict):
            if d.get("status") == "finished":
                fname = d.get("filename", "") or d.get("info_dict", {}).get("_filename", "")
                result.filename = fname
                # If audio_only, ffmpeg will rename to .mp3 after this hook fires.
                # Store a best-guess mp3 path; _resolve_final_filename fixes it later.
                if self.audio_only and fname:
                    import os as _os
                    base = _os.path.splitext(fname)[0]
                    result._expected_mp3 = base + ".mp3"
            self.progress_callback(d)
        return hook

    def _resolve_final_filename(self, result: DownloadResult):
        """After yt-dlp finishes, find the actual output file on disk."""
        import os as _os
        import glob as _glob
        # If we expected an mp3 and it exists, use that
        expected = getattr(result, '_expected_mp3', None)
        if expected and _os.path.exists(expected):
            result.filename = expected
            return
        # For video mode: ffmpeg may have remuxed to .mp4
        if not self.audio_only and result.filename:
            base = _os.path.splitext(result.filename)[0]
            mp4_path = base + ".mp4"
            if _os.path.exists(mp4_path):
                result.filename = mp4_path
                return
        # If stored path exists as-is, keep it
        if result.filename and _os.path.exists(result.filename):
            return
        # Last resort: find the newest matching file in output_dir
        exts = ('mp4', 'mp3', 'm4a', 'webm', 'mkv', 'jpg', 'jpeg', 'png', 'ogg', 'opus')
        candidates = []
        for ext in exts:
            candidates.extend(_glob.glob(_os.path.join(self.output_dir, f'*.{ext}')))
        if candidates:
            result.filename = max(candidates, key=_os.path.getmtime)

    @staticmethod
    def _default_progress(d: dict):
        status = d.get("status", "")
        if status == "downloading":
            pct = d.get("_percent_str", "").strip()
            speed = d.get("_speed_str", "").strip()
            eta = d.get("_eta_str", "").strip()
            total = d.get("_total_bytes_str", d.get("_total_bytes_estimate_str", "")).strip()
            parts = [p for p in [pct, total, speed, f"ETA {eta}" if eta else ""] if p]
            print(f"\r  Downloading: {' | '.join(parts)}          ", end="", flush=True)
        elif status == "finished":
            print(f"\r  Download complete.                                    ")
        elif status == "error":
            print(f"\r  Error during download.                                ")

    def _save_history(self, result: DownloadResult):
        """Append a successful download record to download_history.json."""
        os.makedirs(os.path.dirname(os.path.abspath(_HISTORY_FILE)), exist_ok=True)
        history = []
        if os.path.isfile(_HISTORY_FILE):
            try:
                with open(_HISTORY_FILE, encoding="utf-8") as f:
                    history = json.load(f)
            except Exception:
                history = []
        history.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "url": result.url,
            "title": result.title,
            "platform": result.platform,
            "filename": result.filename,
            "duration_seconds": result.duration_seconds,
            "resolution": result.resolution,
            "audio_only": result.audio_only,
        })
        with open(_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)


# ---------------------------------------------------------------------------
# Convenience function
# ---------------------------------------------------------------------------

def download_video(
    url: str,
    output_dir: str = "outputs",
    quality: str = "best",
    audio_only: bool = False,
    thumbnail_only: bool = False,
    subtitles: bool = False,
    embed_thumbnail: bool = False,
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    proxy: Optional[str] = None,
    filename_template: Optional[str] = None,
    chrome_profile_dir: Optional[str] = None,
) -> DownloadResult:
    """One-shot helper: download video/audio/thumbnail from any supported URL."""
    downloader = FacebookVideoDownloader(
        output_dir=output_dir,
        quality=quality,
        audio_only=audio_only,
        thumbnail_only=thumbnail_only,
        subtitles=subtitles,
        embed_thumbnail=embed_thumbnail,
        start_time=start_time,
        end_time=end_time,
        proxy=proxy,
        filename_template=filename_template,
        chrome_profile_dir=chrome_profile_dir,
    )
    return downloader.download(url)
