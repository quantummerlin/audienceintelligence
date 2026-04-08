"""
Social Media Video / Audio Downloader — interactive runner.
Supports: Facebook, YouTube, Instagram, TikTok, Twitter/X, Reddit,
          Twitch, Vimeo, Dailymotion, Pinterest, LinkedIn, and 1000+ more.
Run with: python download_video.py
"""

import json
import os
import sys

# Make the package importable without a pip install
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fb_video_downloader.downloader import FacebookVideoDownloader, _HISTORY_FILE

CHROME_PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")

QUALITY_OPTIONS = {
    "1": ("Best quality", "best"),
    "2": ("1080p", "1080"),
    "3": ("720p", "720"),
    "4": ("480p", "480"),
    "5": ("Worst (smallest file)", "worst"),
}

MODE_OPTIONS = {
    "1": ("Video (MP4)", "video"),
    "2": ("Audio only (MP3)", "audio"),
    "3": ("Thumbnail only (image)", "thumbnail"),
}


def pick_mode() -> str:
    """Return 'video', 'audio', or 'thumbnail'."""
    print()
    print("Select download mode:")
    for key, (label, _) in MODE_OPTIONS.items():
        print(f"  [{key}] {label}")
    print()
    choice = input("Enter choice [1]: ").strip() or "1"
    label, mode = MODE_OPTIONS.get(choice, MODE_OPTIONS["1"])
    print(f"  Mode: {label}")
    return mode


def pick_quality() -> str:
    print()
    print("Select video quality:")
    for key, (label, _) in QUALITY_OPTIONS.items():
        print(f"  [{key}] {label}")
    print()
    choice = input("Enter choice [1]: ").strip() or "1"
    label, value = QUALITY_OPTIONS.get(choice, QUALITY_OPTIONS["1"])
    print(f"  Quality: {label}")
    return value


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    hint = "[Y/n]" if default else "[y/N]"
    answer = input(f"  {prompt} {hint}: ").strip().lower()
    if not answer:
        return default
    return answer.startswith("y")


def pick_trim() -> tuple:
    """Ask for optional start/end timestamps. Returns (start, end) strings or (None, None)."""
    print()
    if not ask_yes_no("Trim / clip a segment?", default=False):
        return None, None
    start = input("  Start time (e.g. 1:30 or 90s, Enter to skip): ").strip() or None
    end = input("  End time   (e.g. 4:00 or 240s, Enter to skip): ").strip() or None
    if start or end:
        print(f"  Trim: {start or 'beginning'} → {end or 'end'}")
    return start, end


def pick_proxy() -> str:
    """Ask for an optional proxy URL."""
    print()
    proxy = input("  Proxy URL (Enter to skip): ").strip() or None
    if proxy:
        print(f"  Proxy: {proxy}")
    return proxy


def pick_filename_template() -> str:
    """Ask for an optional custom filename template."""
    print()
    print("  Custom filename? (yt-dlp template, e.g. %(title)s.%(ext)s)")
    tmpl = input("  Template (Enter for default): ").strip() or None
    return tmpl


_BROWSER_OPTIONS = {
    "1": ("Firefox (recommended — most reliable)", "firefox"),
    "2": ("Microsoft Edge (must be fully closed incl. background processes)", "edge"),
    "3": ("Chrome (may fail on Chrome 127+ due to DPAPI)", "chrome"),
    "4": ("Cookies file — export via 'Get cookies.txt LOCALLY' extension (most reliable)", "file"),
    "5": ("No authentication (public content only)", None),
}


def pick_auth() -> tuple:
    """Ask which authentication method to use. Returns (cookies_from_browser, cookies_file)."""
    print()
    print("  --- Authentication ---")
    print("  Instagram requires a logged-in session. Pick your browser:")
    print("  (Note: Chrome 127+ blocks cookie access — use Firefox or Edge instead)")
    print()
    for key, (label, _) in _BROWSER_OPTIONS.items():
        print(f"  [{key}] {label}")
    print()
    choice = input("  Enter choice [1]: ").strip() or "1"
    label, value = _BROWSER_OPTIONS.get(choice, _BROWSER_OPTIONS["1"])
    print(f"  Auth: {label}")

    if value == "file":
        print()
        path = input("  Path to cookies.txt file: ").strip()
        if not os.path.isfile(path):
            print(f"  Warning: file not found: {path}")
        return None, path or None

    if value is not None:
        print("  Close the browser completely before continuing.")
    return value, None


def show_info_preview(dl: FacebookVideoDownloader, url: str) -> bool:
    """Fetch and display info, ask user to confirm. Returns True to proceed."""
    print()
    print("  Fetching info...")
    info = dl.get_info(url)
    if "error" in info:
        print(f"  Could not fetch info: {info['error']}")
        print("  Proceeding anyway...")
        return True

    print()
    print(f"  Title    : {info.get('title') or '(unknown)'}")
    if info.get("uploader"):
        print(f"  Channel  : {info['uploader']}")
    dur = info.get("duration_seconds", 0)
    if dur:
        minutes, secs = divmod(int(dur), 60)
        print(f"  Duration : {minutes}m {secs:02d}s")
    if info.get("formats"):
        print(f"  Available: {', '.join(info['formats'])}")
    if info.get("is_playlist"):
        count = info.get("playlist_count") or "?"
        print(f"  Playlist : {count} items")
    print()
    return ask_yes_no("Proceed with download?", default=True)


def view_history(n: int = 15):
    """Print the last n downloaded items."""
    print()
    print("=" * 60)
    print("  Download History (most recent first)")
    print("=" * 60)
    if not os.path.isfile(_HISTORY_FILE):
        print("  No history found yet.")
        return
    try:
        with open(_HISTORY_FILE, encoding="utf-8") as f:
            history = json.load(f)
    except Exception as e:
        print(f"  Could not read history: {e}")
        return
    entries = list(reversed(history[-n:]))
    for i, entry in enumerate(entries, 1):
        ts = entry.get("timestamp", "")[:16].replace("T", " ")
        platform = entry.get("platform", "")
        title = entry.get("title") or entry.get("url", "")
        res = entry.get("resolution", "")
        print(f"  {i:>2}. [{ts}] [{platform}] {title}")
        if res:
            print(f"       {res}")
    print()
    print(f"  Total downloads: {len(history)}")
    print("=" * 60)


def format_bytes(num: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if num < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} TB"


def main():
    print("=" * 60)
    print("  Social Media Video / Audio Downloader")
    print("  Supports: YouTube, Facebook, Instagram, TikTok,")
    print("            Twitter/X, Reddit, Twitch, Vimeo + more")
    print("=" * 60)

    print()
    url = input("Paste video URL: ").strip()
    if not url:
        print("No URL entered. Exiting.")
        return

    mode = pick_mode()  # 'video', 'audio', 'thumbnail'
    audio_only = mode == "audio"
    thumbnail_only = mode == "thumbnail"
    quality = "best" if (audio_only or thumbnail_only) else pick_quality()

    # Options depending on mode
    subtitles = False
    embed_thumbnail = False
    start_time = end_time = None
    proxy = None
    filename_template = None

    print()
    print("  --- Options ---")

    if mode == "video":
        subtitles = ask_yes_no("Download subtitles/captions? (.srt)", default=False)

    if mode == "audio":
        embed_thumbnail = ask_yes_no("Embed thumbnail as album art in MP3?", default=True)

    if mode != "thumbnail":
        start_time, end_time = pick_trim()

    proxy = pick_proxy()
    filename_template = pick_filename_template()

    # Cookie auth
    cookies_from_browser, cookies_file = pick_auth()

    os.makedirs("outputs", exist_ok=True)

    # Build downloader for info preview
    downloader = FacebookVideoDownloader(
        output_dir="outputs",
        quality=quality,
        audio_only=audio_only,
        thumbnail_only=thumbnail_only,
        subtitles=subtitles,
        embed_thumbnail=embed_thumbnail,
        start_time=start_time,
        end_time=end_time,
        proxy=proxy,
        filename_template=filename_template,
        cookies_from_browser=cookies_from_browser,
        cookies_file=cookies_file,
    )

    if not show_info_preview(downloader, url):
        print("  Cancelled.")
        return

    print()
    print("  Starting download...")
    print("-" * 60)

    result = downloader.download(url)

    print()
    print("=" * 60)

    if result.success:
        print("  Done!")
        if result.platform:
            print(f"  Platform  : {result.platform}")
        print(f"  Title     : {result.title or '(unknown)'}")
        if result.duration_seconds:
            minutes, secs = divmod(int(result.duration_seconds), 60)
            print(f"  Duration  : {minutes}m {secs:02d}s")
        if result.resolution:
            print(f"  Output    : {result.resolution}")
        if result.filesize_bytes:
            print(f"  File size : {format_bytes(result.filesize_bytes)}")
        filename = result.filename or "(see outputs/ folder)"
        print(f"  Saved to  : {os.path.abspath(filename) if result.filename else filename}")
    else:
        print("  Download failed.")
        print(f"  Reason: {result.error}")
        print()
        print("  Troubleshooting tips:")
        print("  - Make sure yt-dlp is installed: pip install yt-dlp")
        print("  - For private content, log in first via: python run.py")
        print("  - Ensure ffmpeg is on PATH for audio/trim/thumbnail features")
        print("    (https://ffmpeg.org/download.html)")

    print("=" * 60)


def batch_main():
    """Download multiple URLs from a text file, one URL per line."""
    print("=" * 60)
    print("  Social Media Downloader — Batch Mode")
    print("=" * 60)
    print()

    path = input("Path to text file with URLs (one per line): ").strip()
    if not os.path.isfile(path):
        print(f"File not found: {path}")
        return

    with open(path, encoding="utf-8") as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith("#")]

    if not urls:
        print("No URLs found in file.")
        return

    print(f"\n  Found {len(urls)} URL(s).")

    mode = pick_mode()
    audio_only = mode == "audio"
    thumbnail_only = mode == "thumbnail"
    quality = "best" if (audio_only or thumbnail_only) else pick_quality()

    subtitles = False
    embed_thumbnail = False
    start_time = end_time = None
    proxy = None
    filename_template = None

    print()
    print("  --- Options (applied to all URLs) ---")
    if mode == "video":
        subtitles = ask_yes_no("Download subtitles/captions?", default=False)
    if mode == "audio":
        embed_thumbnail = ask_yes_no("Embed thumbnail as album art?", default=True)
    if mode != "thumbnail":
        start_time, end_time = pick_trim()
    proxy = pick_proxy()
    filename_template = pick_filename_template()

    cookies_from_browser, cookies_file = pick_auth()
    os.makedirs("outputs", exist_ok=True)

    downloader = FacebookVideoDownloader(
        output_dir="outputs",
        quality=quality,
        audio_only=audio_only,
        thumbnail_only=thumbnail_only,
        subtitles=subtitles,
        embed_thumbnail=embed_thumbnail,
        start_time=start_time,
        end_time=end_time,
        proxy=proxy,
        filename_template=filename_template,
        cookies_from_browser=cookies_from_browser,
        cookies_file=cookies_file,
    )

    succeeded, failed = 0, 0
    for i, url in enumerate(urls, 1):
        print(f"\n[{i}/{len(urls)}] {url}")
        print("-" * 60)
        result = downloader.download(url)
        print()
        if result.success:
            label = result.title or result.filename
            platform = f" [{result.platform}]" if result.platform else ""
            print(f"  OK{platform}: {label}")
            succeeded += 1
        else:
            print(f"  FAIL: {result.error}")
            failed += 1

    print()
    print("=" * 60)
    print(f"  Batch complete: {succeeded} succeeded, {failed} failed.")
    print("=" * 60)


if __name__ == "__main__":
    if "--batch" in sys.argv:
        batch_main()
    elif "--history" in sys.argv:
        view_history()
    else:
        main()
