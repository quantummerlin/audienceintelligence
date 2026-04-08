"""
Reddit Gold Miner — interactive CLI
Mine entire subreddits (posts + comments) using PullPush.io.
No API key or Reddit account required.

Usage: python reddit_miner.py
"""

import json
import os
import sys
from datetime import datetime, timezone
from typing import Optional

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reddit_comment_exporter.scraper import RedditScraper

OUTPUTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "outputs")
os.makedirs(OUTPUTS_DIR, exist_ok=True)

BANNER = """
╔══════════════════════════════════════════╗
║       🪙  Reddit Gold Miner  🪙          ║
║   PullPush-powered subreddit scraper    ║
║   No API key · No login · No limits    ║
╚══════════════════════════════════════════╝
"""

MINE_OPTIONS = {
    "1": "Mine entire subreddit  (posts + all comments)",
    "2": "Mine posts only",
    "3": "Mine comments only",
    "4": "Mine a single post's comments (by post URL or ID)",
    "5": "View recent history",
    "6": "Quit",
}

FORMAT_OPTIONS = {
    "1": ("CSV",  "csv"),
    "2": ("JSON", "json"),
    "3": ("Both", "both"),
}


# ---------------------------------------------------------------------------
# Input helpers
# ---------------------------------------------------------------------------

def ask(prompt: str, default: str = "") -> str:
    hint = f" [{default}]" if default else ""
    val  = input(f"  {prompt}{hint}: ").strip()
    return val or default


def ask_yes_no(prompt: str, default: bool = False) -> bool:
    hint = "[Y/n]" if default else "[y/N]"
    ans  = input(f"  {prompt} {hint}: ").strip().lower()
    if not ans:
        return default
    return ans.startswith("y")


def pick_format() -> str:
    print()
    print("Output format:")
    for k, (label, _) in FORMAT_OPTIONS.items():
        print(f"  [{k}] {label}")
    choice = input("  Choice [1]: ").strip() or "1"
    _, fmt = FORMAT_OPTIONS.get(choice, FORMAT_OPTIONS["1"])
    return fmt


DATE_RANGE_OPTIONS = {
    "1": "Today",
    "2": "This week  (last 7 days)",
    "3": "This month (last 30 days)",
    "4": "This year  (last 365 days)",
    "5": "All time",
    "6": "Custom date range",
}


def parse_date(s: str) -> int:
    """Parse YYYY-MM-DD (or YYYY-MM-DD HH:MM:SS) to unix timestamp."""
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            dt = datetime.strptime(s.strip(), fmt)
            return int(dt.replace(tzinfo=timezone.utc).timestamp())
        except ValueError:
            continue
    raise ValueError(f"Cannot parse date: {s!r}  — use YYYY-MM-DD")


def pick_date_range():
    """Ask for a date range preset or custom dates. Returns (after_ts, before_ts)."""
    from datetime import timedelta
    print()
    print("  Date range:")
    for k, label in DATE_RANGE_OPTIONS.items():
        print(f"    [{k}] {label}")
    print()
    choice = input("  Choice [5]: ").strip() or "5"

    now = datetime.now(tz=timezone.utc)

    if choice == "1":   # Today
        after_ts  = int(now.replace(hour=0, minute=0, second=0, microsecond=0).timestamp())
        before_ts = None
    elif choice == "2": # Last 7 days
        after_ts  = int((now - timedelta(days=7)).timestamp())
        before_ts = None
    elif choice == "3": # Last 30 days
        after_ts  = int((now - timedelta(days=30)).timestamp())
        before_ts = None
    elif choice == "4": # Last 365 days
        after_ts  = int((now - timedelta(days=365)).timestamp())
        before_ts = None
    elif choice == "5": # All time
        after_ts  = None
        before_ts = None
    elif choice == "6": # Custom
        after_str  = ask("Start date (YYYY-MM-DD, Enter to skip)")
        before_str = ask("End date   (YYYY-MM-DD, Enter to skip)")
        after_ts   = parse_date(after_str)  if after_str  else None
        before_ts  = parse_date(before_str) if before_str else None
    else:
        print("  Invalid choice — using All time.")
        after_ts  = None
        before_ts = None

    return after_ts, before_ts


def pick_cap(prompt: str) -> Optional[int]:
    val = ask(prompt, default="")
    if not val:
        return None
    try:
        return int(val)
    except ValueError:
        print("  Invalid number — no cap applied.")
        return None


def extract_post_id(url_or_id: str) -> str:
    """Extract Reddit post ID from a URL like reddit.com/r/sub/comments/abc123/..."""
    url_or_id = url_or_id.strip().rstrip("/")
    if "reddit.com" in url_or_id:
        parts = url_or_id.split("/")
        try:
            idx = parts.index("comments")
            return parts[idx + 1]
        except (ValueError, IndexError):
            pass
    # Assume raw ID was given
    return url_or_id.split("/")[-1]


def ts_to_str(ts: int) -> str:
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

def make_filename(subreddit: str, content_type: str, ext: str) -> str:
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    return os.path.join(OUTPUTS_DIR, f"reddit_{subreddit}_{content_type}_{ts}.{ext}")


def save_results(scraper: RedditScraper, data: list, content_type: str, fmt: str) -> list:
    paths = []
    sub   = scraper.subreddit
    if fmt in ("csv", "both"):
        path = make_filename(sub, content_type, "csv")
        if content_type == "posts":
            scraper.save_posts_csv(data, path)
        else:
            scraper.save_comments_csv(data, path)
        paths.append(path)
        print(f"\n  ✓ CSV saved → {path}")
    if fmt in ("json", "both"):
        path = make_filename(sub, content_type, "json")
        scraper.save_json(data, path)
        paths.append(path)
        print(f"  ✓ JSON saved → {path}")
    return paths


def progress(msg: str):
    print(f"  {msg}")


# ---------------------------------------------------------------------------
# Modes
# ---------------------------------------------------------------------------

def mode_full(subreddit: str):
    """Mine posts + all comments for a subreddit."""
    after_ts, before_ts = pick_date_range()
    post_cap    = pick_cap("Max posts to fetch (Enter = unlimited)")
    comment_cap = pick_cap("Max comments to fetch (Enter = unlimited)")
    fmt         = pick_format()

    scraper = RedditScraper(
        subreddit    = subreddit,
        after        = after_ts,
        before       = before_ts,
        max_posts    = post_cap,
        max_comments = comment_cap,
        output_dir   = OUTPUTS_DIR,
        on_progress  = progress,
    )

    print(f"\n  Mining r/{subreddit} — posts + comments…")
    print("  (This may take a while for large subreddits.  Ctrl+C to stop.)\n")

    posts = scraper.mine_posts()
    print(f"\n  Posts collected: {len(posts)}")
    post_paths = save_results(scraper, posts, "posts", fmt)

    comments = scraper.mine_comments()
    print(f"\n  Comments collected: {len(comments)}")
    comment_paths = save_results(scraper, comments, "comments", fmt)

    scraper.save_history({
        "mode":        "full",
        "subreddit":   subreddit,
        "posts":       len(posts),
        "comments":    len(comments),
        "after":       ts_to_str(after_ts)  if after_ts  else None,
        "before":      ts_to_str(before_ts) if before_ts else None,
        "files":       post_paths + comment_paths,
        "scraped_at":  datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


def mode_posts_only(subreddit: str):
    after_ts, before_ts = pick_date_range()
    post_cap = pick_cap("Max posts to fetch (Enter = unlimited)")
    fmt      = pick_format()

    scraper = RedditScraper(
        subreddit   = subreddit,
        after       = after_ts,
        before      = before_ts,
        max_posts   = post_cap,
        output_dir  = OUTPUTS_DIR,
        on_progress = progress,
    )

    print(f"\n  Mining posts from r/{subreddit}…\n")
    posts = scraper.mine_posts()
    print(f"\n  Posts collected: {len(posts)}")
    paths = save_results(scraper, posts, "posts", fmt)

    scraper.save_history({
        "mode":       "posts",
        "subreddit":  subreddit,
        "posts":      len(posts),
        "after":      ts_to_str(after_ts)  if after_ts  else None,
        "before":     ts_to_str(before_ts) if before_ts else None,
        "files":      paths,
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


def mode_comments_only(subreddit: str):
    after_ts, before_ts = pick_date_range()
    comment_cap = pick_cap("Max comments to fetch (Enter = unlimited)")
    fmt         = pick_format()

    scraper = RedditScraper(
        subreddit    = subreddit,
        after        = after_ts,
        before       = before_ts,
        max_comments = comment_cap,
        output_dir   = OUTPUTS_DIR,
        on_progress  = progress,
    )

    print(f"\n  Mining comments from r/{subreddit}…\n")
    comments = scraper.mine_comments()
    print(f"\n  Comments collected: {len(comments)}")
    paths = save_results(scraper, comments, "comments", fmt)

    scraper.save_history({
        "mode":       "comments",
        "subreddit":  subreddit,
        "comments":   len(comments),
        "after":      ts_to_str(after_ts)  if after_ts  else None,
        "before":     ts_to_str(before_ts) if before_ts else None,
        "files":      paths,
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


def mode_single_post(subreddit: str):
    print()
    raw = ask("Post URL or ID (e.g. https://reddit.com/r/sub/comments/abc123/title)")
    if not raw:
        print("  No input — returning.")
        return

    post_id = extract_post_id(raw)
    fmt     = pick_format()

    scraper = RedditScraper(
        subreddit   = subreddit,
        output_dir  = OUTPUTS_DIR,
        on_progress = progress,
    )

    print(f"\n  Fetching comments for post ID: {post_id}…\n")
    comments = scraper.mine_comments(post_id=post_id)
    print(f"\n  Comments collected: {len(comments)}")
    paths = save_results(scraper, comments, f"post_{post_id}", fmt)

    scraper.save_history({
        "mode":       "single_post",
        "subreddit":  subreddit,
        "post_id":    post_id,
        "comments":   len(comments),
        "files":      paths,
        "scraped_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    })


def show_history():
    history = RedditScraper.load_history()
    if not history:
        print("\n  No history yet.")
        return
    print(f"\n  {'─'*60}")
    print(f"  {'RECENT REDDIT MINING HISTORY':^60}")
    print(f"  {'─'*60}")
    for i, rec in enumerate(history[:10], 1):
        sub        = rec.get("subreddit", "?")
        mode       = rec.get("mode", "?")
        scraped_at = rec.get("scraped_at", "?")
        posts      = rec.get("posts", "")
        comments   = rec.get("comments", "")
        counts     = []
        if posts:      counts.append(f"{posts} posts")
        if comments:   counts.append(f"{comments} comments")
        count_str  = ", ".join(counts) if counts else ""
        files      = rec.get("files", [])
        print(f"\n  [{i}] r/{sub}  ({mode})  —  {scraped_at}")
        if count_str: print(f"      {count_str}")
        for f in files:
            print(f"      → {f}")
    print()


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def main():
    print(BANNER)

    while True:
        print("What would you like to do?")
        for k, label in MINE_OPTIONS.items():
            print(f"  [{k}] {label}")
        print()

        choice = input("  Enter choice: ").strip()

        if choice == "6":
            print("\n  Goodbye! Happy mining. 🪙\n")
            break

        if choice == "5":
            show_history()
            continue

        if choice not in {"1", "2", "3", "4"}:
            print("  Invalid choice.\n")
            continue

        print()
        raw_sub   = ask("Subreddit name (without r/)").strip().lower()
        subreddit = raw_sub[2:] if raw_sub.startswith("r/") else raw_sub
        if not subreddit:
            print("  No subreddit entered.\n")
            continue

        try:
            if choice == "1":
                mode_full(subreddit)
            elif choice == "2":
                mode_posts_only(subreddit)
            elif choice == "3":
                mode_comments_only(subreddit)
            elif choice == "4":
                mode_single_post(subreddit)
        except KeyboardInterrupt:
            print("\n\n  Stopped by user. Partial results may have been saved.\n")

        print()


if __name__ == "__main__":
    main()
