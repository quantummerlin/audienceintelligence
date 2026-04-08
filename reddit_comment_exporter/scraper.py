"""
Reddit Gold Miner — Scraper
Uses PullPush.io (community-run Pushshift replacement) to mine subreddits,
with an automatic fallback to Reddit's public JSON API for subs that
PullPush hasn't indexed.  No API key or Reddit account needed.
"""

import csv
import json
import os
import time
import logging
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import List, Dict, Optional, Iterator

import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# PullPush API base
# ---------------------------------------------------------------------------
PULLPUSH_BASE = "https://api.pullpush.io/reddit"
REDDIT_JSON_BASE = "https://www.reddit.com"
_HISTORY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "outputs", "reddit_history.json")

DEFAULT_BATCH   = 100   # max PullPush accepts per request
REQUEST_DELAY   = 1.0   # seconds between requests (be polite)
MAX_RETRIES     = 3
RETRY_BACKOFF   = 5     # seconds


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class RedditPost:
    id: str
    title: str
    author: str
    subreddit: str
    score: int
    upvote_ratio: float
    url: str
    selftext: str
    created_utc: int
    num_comments: int
    permalink: str
    is_self: bool
    flair: str = ""
    domain: str = ""

    @property
    def created_dt(self) -> str:
        return datetime.fromtimestamp(self.created_utc, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["created_dt"] = self.created_dt
        return d


@dataclass
class RedditComment:
    id: str
    post_id: str
    parent_id: str
    author: str
    subreddit: str
    body: str
    score: int
    created_utc: int
    permalink: str
    depth: int = 0

    @property
    def created_dt(self) -> str:
        return datetime.fromtimestamp(self.created_utc, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["created_dt"] = self.created_dt
        return d


# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------

class RedditScraper:
    """
    Mine Reddit posts and comments from any public subreddit using PullPush.io.

    Parameters
    ----------
    subreddit : str
        Subreddit name (without r/).
    after : int | None
        Unix timestamp — only fetch items after this date.
    before : int | None
        Unix timestamp — only fetch items before this date.
    max_posts : int | None
        Cap on number of posts to fetch (None = unlimited).
    max_comments : int | None
        Cap on number of comments to fetch per batch (None = unlimited).
    output_dir : str
        Directory to save output files.
    on_progress : callable | None
        Optional callback(message: str) for progress updates.
    """

    def __init__(
        self,
        subreddit: str,
        after: Optional[int] = None,
        before: Optional[int] = None,
        max_posts: Optional[int] = None,
        max_comments: Optional[int] = None,
        output_dir: str = "outputs",
        on_progress=None,
    ):
        _sub = subreddit.strip().lower()
        self.subreddit    = _sub[2:] if _sub.startswith("r/") else _sub
        self.after        = after
        self.before       = before
        self.max_posts    = max_posts
        self.max_comments = max_comments
        self.output_dir   = output_dir
        self.on_progress  = on_progress or (lambda msg: None)

        os.makedirs(self.output_dir, exist_ok=True)

        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "RedditGoldMiner/1.0 (audience-intelligence research tool)"
        })

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get(self, url: str, params: dict) -> Optional[dict]:
        """GET with retry logic."""
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                resp = self._session.get(url, params=params, timeout=30)
                resp.raise_for_status()
                return resp.json()
            except requests.exceptions.HTTPError as e:
                if resp.status_code == 429:
                    wait = RETRY_BACKOFF * attempt
                    self.on_progress(f"Rate limited — waiting {wait}s…")
                    time.sleep(wait)
                elif resp.status_code >= 500:
                    wait = RETRY_BACKOFF * attempt
                    self.on_progress(f"Server error {resp.status_code} — retrying in {wait}s…")
                    time.sleep(wait)
                else:
                    logger.error("HTTP error: %s", e)
                    raise
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                wait = RETRY_BACKOFF * attempt
                self.on_progress(f"Connection error ({e}) — retrying in {wait}s…")
                time.sleep(wait)
        return None

    @staticmethod
    def _parse_post(raw: dict) -> RedditPost:
        return RedditPost(
            id           = raw.get("id", ""),
            title        = raw.get("title", ""),
            author       = raw.get("author", "[deleted]"),
            subreddit    = raw.get("subreddit", ""),
            score        = int(raw.get("score", 0)),
            upvote_ratio = float(raw.get("upvote_ratio", 0.0)),
            url          = raw.get("url", ""),
            selftext     = raw.get("selftext", ""),
            created_utc  = int(raw.get("created_utc", 0)),
            num_comments = int(raw.get("num_comments", 0)),
            permalink    = f"https://reddit.com{raw.get('permalink', '')}",
            is_self      = bool(raw.get("is_self", False)),
            flair        = raw.get("link_flair_text") or "",
            domain       = raw.get("domain", ""),
        )

    @staticmethod
    def _parse_comment(raw: dict) -> RedditComment:
        link_id = raw.get("link_id", "").replace("t3_", "")
        parent  = raw.get("parent_id", "")
        depth   = 0 if parent.startswith("t3_") else 1
        return RedditComment(
            id          = raw.get("id", ""),
            post_id     = link_id,
            parent_id   = parent,
            author      = raw.get("author", "[deleted]"),
            subreddit   = raw.get("subreddit", ""),
            body        = raw.get("body", ""),
            score       = int(raw.get("score", 0)),
            created_utc = int(raw.get("created_utc", 0)),
            permalink   = f"https://reddit.com{raw.get('permalink', '')}",
            depth       = depth,
        )

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def iter_posts(self) -> Iterator[RedditPost]:
        """Yield posts — tries PullPush first, falls back to Reddit JSON."""
        pulled_any = False
        for post in self._iter_posts_pullpush():
            pulled_any = True
            yield post
        if not pulled_any:
            self.on_progress("PullPush had no data — trying Reddit JSON…")
            yield from self._iter_posts_reddit_json()

    def _iter_posts_pullpush(self) -> Iterator[RedditPost]:
        """
        Yield all posts from the subreddit via PullPush, oldest-first,
        paginating via the `before` timestamp cursor.
        """
        url    = f"{PULLPUSH_BASE}/search/submission/"
        before = self.before
        total  = 0

        self.on_progress(f"Fetching posts from r/{self.subreddit}…")

        while True:
            params: Dict = {
                "subreddit": self.subreddit,
                "size":      DEFAULT_BATCH,
                "sort":      "desc",
                "sort_type": "created_utc",
            }
            if before:
                params["before"] = before
            if self.after:
                params["after"] = self.after

            data = self._get(url, params)
            if not data:
                break

            items = data.get("data", [])
            if not items:
                break

            for raw in items:
                post = self._parse_post(raw)
                yield post
                total += 1
                if self.max_posts and total >= self.max_posts:
                    self.on_progress(f"Reached post cap of {self.max_posts}.")
                    return

            # Paginate: move cursor to oldest item in this batch
            oldest_ts = min(int(r.get("created_utc", 0)) for r in items)
            if self.after and oldest_ts <= self.after:
                break
            before = oldest_ts - 1

            self.on_progress(f"  Posts fetched so far: {total}")
            time.sleep(REQUEST_DELAY)

            if len(items) < DEFAULT_BATCH:
                break  # last page

    def _iter_posts_reddit_json(self) -> Iterator[RedditPost]:
        """Fallback: fetch posts via Reddit's public JSON API (/new)."""
        url = f"{REDDIT_JSON_BASE}/r/{self.subreddit}/new.json"
        after_cursor = None
        total = 0

        self.on_progress(f"Using Reddit JSON fallback for r/{self.subreddit}…")

        while True:
            params = {"limit": 100, "raw_json": 1}
            if after_cursor:
                params["after"] = after_cursor

            data = self._get(url, params)
            if not data or "data" not in data:
                break

            children = data["data"].get("children", [])
            if not children:
                break

            for child in children:
                raw = child.get("data", {})
                ts = int(raw.get("created_utc", 0))
                # Date filters
                if self.before and ts > self.before:
                    continue
                if self.after and ts < self.after:
                    return  # past our window (sorted newest-first)

                post = self._parse_post(raw)
                yield post
                total += 1
                if self.max_posts and total >= self.max_posts:
                    self.on_progress(f"Reached post cap of {self.max_posts}.")
                    return

            after_cursor = data["data"].get("after")
            if not after_cursor:
                break

            self.on_progress(f"  Posts fetched so far: {total}")
            time.sleep(REQUEST_DELAY)

    def iter_comments(self, post_id: Optional[str] = None) -> Iterator[RedditComment]:
        """Yield comments — tries PullPush first, falls back to Reddit JSON."""
        pulled_any = False
        for comment in self._iter_comments_pullpush(post_id=post_id):
            pulled_any = True
            yield comment
        if not pulled_any:
            self.on_progress("PullPush had no data — trying Reddit JSON…")
            yield from self._iter_comments_reddit_json(post_id=post_id)

    def _iter_comments_pullpush(self, post_id: Optional[str] = None) -> Iterator[RedditComment]:
        """Fetch comments via PullPush."""
        url    = f"{PULLPUSH_BASE}/search/comment/"
        before = self.before
        total  = 0

        label = f"post {post_id}" if post_id else f"r/{self.subreddit}"
        self.on_progress(f"Fetching comments from {label}…")

        while True:
            params: Dict = {
                "size":      DEFAULT_BATCH,
                "sort":      "desc",
                "sort_type": "created_utc",
            }
            if post_id:
                params["link_id"] = f"t3_{post_id}"
            else:
                params["subreddit"] = self.subreddit
            if before:
                params["before"] = before
            if self.after:
                params["after"] = self.after

            data = self._get(url, params)
            if not data:
                break

            items = data.get("data", [])
            if not items:
                break

            for raw in items:
                comment = self._parse_comment(raw)
                yield comment
                total += 1
                if self.max_comments and total >= self.max_comments:
                    self.on_progress(f"Reached comment cap of {self.max_comments}.")
                    return

            oldest_ts = min(int(r.get("created_utc", 0)) for r in items)
            if self.after and oldest_ts <= self.after:
                break
            before = oldest_ts - 1

            self.on_progress(f"  Comments fetched so far: {total}")
            time.sleep(REQUEST_DELAY)

            if len(items) < DEFAULT_BATCH:
                break

    def _iter_comments_reddit_json(self, post_id: Optional[str] = None) -> Iterator[RedditComment]:
        """Fallback: fetch comments via Reddit's public JSON API."""
        if post_id:
            url = f"{REDDIT_JSON_BASE}/comments/{post_id}.json"
        else:
            url = f"{REDDIT_JSON_BASE}/r/{self.subreddit}/comments.json"
        after_cursor = None
        total = 0

        label = f"post {post_id}" if post_id else f"r/{self.subreddit}"
        self.on_progress(f"Using Reddit JSON fallback for comments from {label}…")

        if post_id:
            # Single post returns [listing, comments_listing] — flatten the comment tree
            data = self._get(url, {"raw_json": 1, "limit": 500})
            if data and isinstance(data, list) and len(data) > 1:
                yield from self._flatten_comment_tree(data[1].get("data", {}).get("children", []))
            return

        while True:
            params = {"limit": 100, "raw_json": 1}
            if after_cursor:
                params["after"] = after_cursor

            data = self._get(url, params)
            if not data or "data" not in data:
                break

            children = data["data"].get("children", [])
            if not children:
                break

            for child in children:
                if child.get("kind") != "t1":
                    continue
                raw = child.get("data", {})
                ts = int(raw.get("created_utc", 0))
                if self.before and ts > self.before:
                    continue
                if self.after and ts < self.after:
                    return

                comment = self._parse_comment(raw)
                yield comment
                total += 1
                if self.max_comments and total >= self.max_comments:
                    self.on_progress(f"Reached comment cap of {self.max_comments}.")
                    return

            after_cursor = data["data"].get("after")
            if not after_cursor:
                break

            self.on_progress(f"  Comments fetched so far: {total}")
            time.sleep(REQUEST_DELAY)

    def _flatten_comment_tree(self, children: list) -> Iterator[RedditComment]:
        """Recursively flatten a Reddit comment tree into individual comments."""
        for child in children:
            if child.get("kind") != "t1":
                continue
            raw = child.get("data", {})
            ts = int(raw.get("created_utc", 0))
            if self.before and ts > self.before:
                continue
            if self.after and ts < self.after:
                continue
            yield self._parse_comment(raw)
            # Recurse into replies
            replies = raw.get("replies")
            if isinstance(replies, dict):
                reply_children = replies.get("data", {}).get("children", [])
                yield from self._flatten_comment_tree(reply_children)

    def mine_posts(self) -> List[RedditPost]:
        """Collect all posts into a list. Partial results returned on error."""
        results = []
        try:
            for post in self.iter_posts():
                results.append(post)
        except Exception as e:
            self.on_progress(f"Stopped after {len(results)} posts: {e}")
        return results

    def mine_comments(self, post_id: Optional[str] = None) -> List[RedditComment]:
        """Collect all comments into a list. Partial results returned on error."""
        results = []
        try:
            for comment in self.iter_comments(post_id=post_id):
                results.append(comment)
        except Exception as e:
            self.on_progress(f"Stopped after {len(results)} comments: {e}")
        return results

    def mine_full(self) -> Dict[str, list]:
        """
        Mine both posts and comments for the subreddit.
        Returns {"posts": [...], "comments": [...]}
        """
        posts    = self.mine_posts()
        comments = self.mine_comments()
        return {"posts": posts, "comments": comments}

    # ------------------------------------------------------------------
    # Export helpers
    # ------------------------------------------------------------------

    def save_posts_csv(self, posts: List[RedditPost], path: str) -> str:
        if not posts:
            return path
        fieldnames = list(posts[0].to_dict().keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for p in posts:
                writer.writerow(p.to_dict())
        return path

    def save_comments_csv(self, comments: List[RedditComment], path: str) -> str:
        if not comments:
            return path
        fieldnames = list(comments[0].to_dict().keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for c in comments:
                writer.writerow(c.to_dict())
        return path

    def save_json(self, data: list, path: str) -> str:
        with open(path, "w", encoding="utf-8") as f:
            json.dump([d.to_dict() if hasattr(d, "to_dict") else d for d in data], f, indent=2, ensure_ascii=False)
        return path

    # ------------------------------------------------------------------
    # History
    # ------------------------------------------------------------------

    def save_history(self, record: dict):
        os.makedirs(os.path.dirname(_HISTORY_FILE), exist_ok=True)
        history = []
        if os.path.exists(_HISTORY_FILE):
            try:
                with open(_HISTORY_FILE, encoding="utf-8") as f:
                    history = json.load(f)
            except (json.JSONDecodeError, IOError):
                history = []
        history.insert(0, record)
        history = history[:50]
        with open(_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    @staticmethod
    def load_history() -> list:
        if not os.path.exists(_HISTORY_FILE):
            return []
        try:
            with open(_HISTORY_FILE, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
