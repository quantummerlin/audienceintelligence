"""
YouTube Comment Scraper
=======================
Selenium-based scraper that extracts comments from public YouTube videos
(regular videos and Shorts).  Same architecture as the Facebook & Instagram
scrapers: Comment dataclass, crash-safe checkpointing, rolling DOM harvest,
CSV/JSON export.

Platform quirks handled
-----------------------
* Cookie consent ("Accept all" / "Reject all") banner
* Lazy-loaded comment section (scroll into view to trigger)
* "Show more replies" / "N replies" expansion
* Sort toggle (Top comments ↔ Newest first)
* Shorts vs regular video layout
* "Read more" text expansion
* Pinned / highlighted comments
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
    WebDriverException,
)
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager

# ---------------------------------------------------------------------------
# Localised button / link texts
# ---------------------------------------------------------------------------

COOKIE_TEXTS = [
    "Accept all",
    "Accept All",
    "Reject all",
    "I agree",
    "Accetta tutto",
    "Tout accepter",
    "Alle akzeptieren",
    "Aceptar todo",
]

SORT_NEWEST_TEXTS = [
    "Newest first",
    "Più recenti",
    "Les plus récents",
    "Neueste zuerst",
    "Más recientes",
]

READ_MORE_TEXTS = [
    "Read more",
    "Show more",
    "Mostra altro",
    "Lire la suite",
    "Mehr anzeigen",
    "Mostrar más",
]

SHOW_REPLIES_TEXTS = [
    "replies",
    "reply",
    "risposte",
    "risposta",
    "réponses",
    "réponse",
    "Antworten",
    "Antwort",
    "respuestas",
    "respuesta",
]


# ---------------------------------------------------------------------------
# Comment data-class
# ---------------------------------------------------------------------------

@dataclass
class Comment:
    author: str = ""
    text: str = ""
    timestamp: Optional[str] = None
    likes: Optional[int] = None
    replies_count: Optional[int] = None
    comment_id: Optional[str] = None
    url: Optional[str] = None
    is_reply: bool = False
    reply_to: Optional[str] = None
    is_pinned: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    def fingerprint(self) -> str:
        raw = f"{self.author}::{self.text}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Main scraper
# ---------------------------------------------------------------------------

class YouTubeCommentScraper:
    """Selenium-based YouTube comment scraper with crash-safe checkpointing."""

    def __init__(
        self,
        headless: bool = True,
        scroll_pause: float = 2.5,
        max_scrolls: int = 200,
        timeout: int = 30,
        expand_replies: bool = True,
        max_reply_expansions: int = 50,
        sort_newest: bool = False,
        chrome_profile_dir: Optional[str] = None,
    ):
        self.headless = headless
        self.scroll_pause = scroll_pause
        self.max_scrolls = max_scrolls
        self.timeout = timeout
        self.expand_replies = expand_replies
        self.max_reply_expansions = max_reply_expansions
        self.sort_newest = sort_newest
        self.chrome_profile_dir = chrome_profile_dir

        self.driver: Optional[webdriver.Chrome] = None
        self._all_comments: Dict[str, Comment] = {}
        self._total_reply_expansions = 0
        self._clicked_reply_keys: Set[str] = set()

    # ------------------------------------------------------------------
    # Driver setup
    # ------------------------------------------------------------------

    def _init_driver(self):
        opts = ChromeOptions()
        if self.headless:
            opts.add_argument("--headless=new")

        # Performance flags
        for flag in [
            "--disable-extensions",
            "--disable-plugins-discovery",
            "--disable-translate",
            "--disable-sync",
            "--disable-background-networking",
            "--disable-default-apps",
            "--mute-audio",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-gpu",
            "--disable-dev-shm-usage",
            "--no-sandbox",
        ]:
            opts.add_argument(flag)

        # Block images & notifications
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2,
        }
        if self.chrome_profile_dir:
            opts.add_argument(f"--user-data-dir={self.chrome_profile_dir}")
        opts.add_experimental_option("prefs", prefs)

        # Automation disguise
        opts.add_experimental_option("excludeSwitches", ["enable-automation"])
        opts.add_experimental_option("useAutomationExtension", False)

        service = ChromeService(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=opts)
        self.driver.set_page_load_timeout(self.timeout)
        self.driver.implicitly_wait(3)

        # Remove webdriver flag
        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument",
            {"source": "Object.defineProperty(navigator,'webdriver',{get:()=>undefined})"},
        )

    # ------------------------------------------------------------------
    # Safe click
    # ------------------------------------------------------------------

    def _safe_click(self, el):
        try:
            self.driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
            time.sleep(0.15)
            el.click()
        except WebDriverException:
            try:
                self.driver.execute_script("arguments[0].click();", el)
            except Exception:
                pass

    # ------------------------------------------------------------------
    # Checkpoint system
    # ------------------------------------------------------------------

    @staticmethod
    def _make_checkpoint_path(url: str, directory: str = "outputs") -> str:
        # Extract video ID for a clean slug
        vid = YouTubeCommentScraper._extract_video_id(url) or ""
        slug = re.sub(r"[^a-zA-Z0-9]", "_", vid)[:40] if vid else re.sub(r"[^a-zA-Z0-9]", "_", url.split("?")[0])[-60:]
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, f"yt_ckpt_{slug}.json")

    def _save_checkpoint(self, path: str, url: str) -> None:
        data = {
            "url": url,
            "saved_at": datetime.now().isoformat(),
            "comments": [c.to_dict() for c in self._all_comments.values()],
        }
        tmp = path + ".tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False)
            os.replace(tmp, path)
        except Exception as e:
            print(f"  [checkpoint] save failed: {e}")

    def _load_checkpoint(self, path: str) -> int:
        if not os.path.exists(path):
            return 0
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            loaded = 0
            for cd in data.get("comments", []):
                c = Comment(**{k: v for k, v in cd.items() if k in Comment.__dataclass_fields__})
                fp = c.fingerprint()
                if fp not in self._all_comments:
                    self._all_comments[fp] = c
                    loaded += 1
            return loaded
        except Exception as e:
            print(f"  [checkpoint] load failed: {e}")
            return 0

    @staticmethod
    def _clear_checkpoint(path: str) -> None:
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    # ------------------------------------------------------------------
    # URL helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from various YouTube URL formats."""
        # youtube.com/watch?v=ID
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]
        # youtu.be/ID
        if "youtu.be" in parsed.hostname or "":
            return parsed.path.strip("/").split("/")[0] if parsed.path.strip("/") else None
        # youtube.com/shorts/ID
        m = re.search(r"/shorts/([a-zA-Z0-9_-]+)", parsed.path)
        if m:
            return m.group(1)
        # youtube.com/embed/ID
        m = re.search(r"/embed/([a-zA-Z0-9_-]+)", parsed.path)
        if m:
            return m.group(1)
        return None

    @staticmethod
    def _is_shorts_url(url: str) -> bool:
        return bool(re.search(r"/shorts/", url))

    @staticmethod
    def _normalise_url(url: str) -> str:
        """Normalise to a standard youtube.com/watch?v=ID URL."""
        url = url.strip()
        vid = YouTubeCommentScraper._extract_video_id(url)
        if vid:
            return f"https://www.youtube.com/watch?v={vid}"
        return url

    # ------------------------------------------------------------------
    # Cookie / overlay dismissal
    # ------------------------------------------------------------------

    def _dismiss_cookie_banner(self):
        """Dismiss YouTube's cookie consent (GDPR) dialog."""
        for text in COOKIE_TEXTS:
            try:
                for btn in self.driver.find_elements(
                    By.XPATH,
                    f"//button[contains(.,'{text}')] | "
                    f"//tp-yt-paper-button[contains(.,'{text}')] | "
                    f"//ytd-button-renderer[contains(.,'{text}')]//button",
                ):
                    if btn.is_displayed():
                        self._safe_click(btn)
                        time.sleep(1)
                        return
            except Exception:
                pass

        # Also try the consent forms
        try:
            forms = self.driver.find_elements(By.CSS_SELECTOR, "form[action*='consent']")
            for form in forms:
                btns = form.find_elements(By.CSS_SELECTOR, "button")
                for btn in btns:
                    if btn.is_displayed():
                        self._safe_click(btn)
                        time.sleep(1)
                        return
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Sort toggle
    # ------------------------------------------------------------------

    def _sort_by_newest(self):
        """Switch from 'Top comments' to 'Newest first'."""
        try:
            # Find the sort dropdown
            sort_menu = self.driver.find_elements(
                By.CSS_SELECTOR,
                "yt-sort-filter-sub-menu-renderer tp-yt-paper-button,"
                "#sort-menu tp-yt-paper-button,"
                "yt-dropdown-menu tp-yt-paper-button",
            )
            for btn in sort_menu:
                if btn.is_displayed() and ("Top" in btn.text or "Sort" in btn.text):
                    self._safe_click(btn)
                    time.sleep(1)
                    break

            # Click "Newest first"
            for text in SORT_NEWEST_TEXTS:
                for opt in self.driver.find_elements(
                    By.XPATH,
                    f"//tp-yt-paper-item[contains(.,'{text}')] | "
                    f"//a[contains(.,'{text}')] | "
                    f"//yt-formatted-string[contains(.,'{text}')]",
                ):
                    if opt.is_displayed():
                        self._safe_click(opt)
                        time.sleep(2)
                        print("  Sorted to: Newest first")
                        return
        except Exception:
            pass

    # ------------------------------------------------------------------
    # Scroll to comments section
    # ------------------------------------------------------------------

    def _scroll_to_comments(self) -> bool:
        """YouTube loads comments lazily — scroll down until the comments
        section appears in the DOM."""
        for attempt in range(15):
            # Check if comments section exists
            try:
                comments_section = self.driver.find_element(
                    By.CSS_SELECTOR, "ytd-comments#comments"
                )
                if comments_section.is_displayed():
                    # Scroll it into view
                    self.driver.execute_script(
                        "arguments[0].scrollIntoView({block:'start'});",
                        comments_section,
                    )
                    time.sleep(1)
                    return True
            except NoSuchElementException:
                pass

            # Scroll down incrementally to trigger lazy load
            self.driver.execute_script(
                f"window.scrollBy(0, {400 + attempt * 200});"
            )
            time.sleep(1.5)

        print("  Warning: could not find comments section")
        return False

    # ------------------------------------------------------------------
    # Comment DOM extraction
    # ------------------------------------------------------------------

    def _extract_author(self, el) -> str:
        """Extract author name from a comment renderer element."""
        for sel in [
            "#author-text span",
            "#author-text",
            "a#author-text",
            "#header-author h3 a span",
            "ytd-channel-name yt-formatted-string a",
        ]:
            try:
                found = el.find_element(By.CSS_SELECTOR, sel)
                name = found.text.strip()
                if name:
                    return name
            except (NoSuchElementException, StaleElementReferenceException):
                continue
        return ""

    def _extract_text(self, el) -> str:
        """Extract comment text from a comment renderer element."""
        for sel in [
            "#content-text",
            "yt-attributed-string#content-text",
            "#content yt-formatted-string",
            "#comment-content #content-text",
        ]:
            try:
                text_el = el.find_element(By.CSS_SELECTOR, sel)
                text = text_el.text.strip()
                if text:
                    return text
            except (NoSuchElementException, StaleElementReferenceException):
                continue
        return ""

    def _extract_timestamp(self, el) -> Optional[str]:
        """Extract publish timestamp from a comment element."""
        for sel in [
            "#published-time-text a",
            "#published-time-text",
            "a.yt-simple-endpoint[href*='lc=']",
            "#header-author yt-formatted-string.published-time-text a",
        ]:
            try:
                ts_el = el.find_element(By.CSS_SELECTOR, sel)
                ts = ts_el.text.strip()
                if ts:
                    # Clean up "(edited)" suffix
                    ts = re.sub(r"\s*\(edited\)\s*$", "", ts).strip()
                    return ts
            except (NoSuchElementException, StaleElementReferenceException):
                continue
        return None

    def _extract_likes(self, el) -> Optional[int]:
        """Extract like count from a comment element."""
        for sel in [
            "#vote-count-middle",
            "span#vote-count-middle",
        ]:
            try:
                like_el = el.find_element(By.CSS_SELECTOR, sel)
                raw = like_el.text.strip()
                if not raw:
                    continue
                # Handle "1.2K", "5K", "12", etc.
                raw = raw.replace(",", "")
                m = re.match(r"^([\d.]+)\s*[Kk]$", raw)
                if m:
                    return int(float(m.group(1)) * 1000)
                m = re.match(r"^([\d.]+)\s*[Mm]$", raw)
                if m:
                    return int(float(m.group(1)) * 1_000_000)
                if raw.isdigit():
                    return int(raw)
            except (NoSuchElementException, StaleElementReferenceException):
                continue
        return None

    def _extract_reply_count(self, thread_el) -> Optional[int]:
        """Extract reply count from a comment thread element."""
        try:
            # "N replies" button
            reply_btn = thread_el.find_element(
                By.CSS_SELECTOR,
                "#more-replies button, ytd-comment-replies-renderer #more-replies button",
            )
            t = reply_btn.text.strip().lower()
            m = re.search(r"(\d+)\s*(?:reply|replies|repl)", t)
            if m:
                return int(m.group(1))
            if "reply" in t or "replies" in t:
                return 1
        except (NoSuchElementException, StaleElementReferenceException):
            pass

        # Check if replies are already expanded
        try:
            replies = thread_el.find_elements(
                By.CSS_SELECTOR,
                "ytd-comment-replies-renderer ytd-comment-renderer",
            )
            if replies:
                return len(replies)
        except Exception:
            pass

        return None

    def _is_pinned(self, el) -> bool:
        """Check if a comment is pinned."""
        try:
            pinned = el.find_element(
                By.CSS_SELECTOR,
                "#pinned-comment-badge, ytd-pinned-comment-badge-renderer",
            )
            return pinned.is_displayed()
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def _extract_comment_id(self, el) -> Optional[str]:
        """Extract comment ID from the permalink."""
        try:
            link = el.find_element(By.CSS_SELECTOR, "a[href*='lc=']")
            href = link.get_attribute("href") or ""
            m = re.search(r"lc=([a-zA-Z0-9_-]+)", href)
            if m:
                return m.group(1)
        except (NoSuchElementException, StaleElementReferenceException):
            pass
        return None

    # ------------------------------------------------------------------
    # Comment harvesting
    # ------------------------------------------------------------------

    def _harvest_top_level_comments(self) -> int:
        """Extract all currently visible top-level comment threads."""
        added = 0
        try:
            threads = self.driver.find_elements(
                By.CSS_SELECTOR,
                "ytd-comment-thread-renderer",
            )
            for thread in threads:
                try:
                    # Top-level comment is the first ytd-comment-renderer
                    comment_el = thread.find_element(
                        By.CSS_SELECTOR, "ytd-comment-view-model, ytd-comment-renderer"
                    )

                    author = self._extract_author(comment_el)
                    text = self._extract_text(comment_el)

                    if not text or len(text.strip()) < 1:
                        continue

                    comment = Comment(
                        author=author,
                        text=text.strip(),
                        timestamp=self._extract_timestamp(comment_el),
                        likes=self._extract_likes(comment_el),
                        replies_count=self._extract_reply_count(thread),
                        comment_id=self._extract_comment_id(comment_el),
                        is_reply=False,
                        is_pinned=self._is_pinned(comment_el),
                    )

                    fp = comment.fingerprint()
                    if fp not in self._all_comments:
                        self._all_comments[fp] = comment
                        added += 1

                    # Also harvest any already-expanded replies
                    if self.expand_replies:
                        added += self._harvest_replies(thread, author)

                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue

        except Exception:
            pass

        return added

    def _harvest_replies(self, thread_el, parent_author: str = "") -> int:
        """Extract replies within a comment thread."""
        added = 0
        try:
            reply_els = thread_el.find_elements(
                By.CSS_SELECTOR,
                "ytd-comment-replies-renderer ytd-comment-view-model,"
                "ytd-comment-replies-renderer ytd-comment-renderer",
            )
            for reply_el in reply_els:
                try:
                    author = self._extract_author(reply_el)
                    text = self._extract_text(reply_el)

                    if not text or len(text.strip()) < 1:
                        continue

                    reply = Comment(
                        author=author,
                        text=text.strip(),
                        timestamp=self._extract_timestamp(reply_el),
                        likes=self._extract_likes(reply_el),
                        comment_id=self._extract_comment_id(reply_el),
                        is_reply=True,
                        reply_to=parent_author,
                    )

                    fp = reply.fingerprint()
                    if fp not in self._all_comments:
                        self._all_comments[fp] = reply
                        added += 1

                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue
        except Exception:
            pass

        return added

    # ------------------------------------------------------------------
    # Reply expansion
    # ------------------------------------------------------------------

    def _expand_reply_threads(self) -> int:
        """Click 'N replies' buttons to expand reply threads."""
        expanded = 0
        if self._total_reply_expansions >= self.max_reply_expansions:
            return 0

        try:
            # Find "View N replies" / "N replies" / "View reply" buttons
            reply_btns = self.driver.find_elements(
                By.CSS_SELECTOR,
                "ytd-comment-replies-renderer #more-replies button,"
                "ytd-comment-replies-renderer ytd-button-renderer button",
            )
            for btn in reply_btns:
                if self._total_reply_expansions >= self.max_reply_expansions:
                    break
                try:
                    if not btn.is_displayed():
                        continue

                    btn_text = btn.text.strip().lower()
                    # Skip "Show less" buttons
                    if "less" in btn_text or "fewer" in btn_text:
                        continue

                    # Only click if it looks like a reply expansion
                    is_reply_btn = any(kw in btn_text for kw in SHOW_REPLIES_TEXTS)
                    if not is_reply_btn and btn_text:
                        continue

                    # Dedup by text + position
                    loc = btn.location
                    loc_key = f"{btn_text[:30]}@{loc.get('x',0):.0f},{loc.get('y',0):.0f}"
                    if loc_key in self._clicked_reply_keys:
                        continue
                    self._clicked_reply_keys.add(loc_key)

                    self._safe_click(btn)
                    expanded += 1
                    self._total_reply_expansions += 1
                    time.sleep(1.0)

                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue
        except Exception:
            pass

        # Also look for "Show more replies" continuation buttons
        try:
            more_btns = self.driver.find_elements(
                By.CSS_SELECTOR,
                "ytd-continuation-item-renderer button,"
                "ytd-comment-replies-renderer ytd-continuation-item-renderer button",
            )
            for btn in more_btns:
                if self._total_reply_expansions >= self.max_reply_expansions:
                    break
                try:
                    if btn.is_displayed():
                        self._safe_click(btn)
                        expanded += 1
                        self._total_reply_expansions += 1
                        time.sleep(1.0)
                except Exception:
                    continue
        except Exception:
            pass

        if expanded:
            print(f"  Expanded {expanded} reply threads")
        return expanded

    # ------------------------------------------------------------------
    # Read more expansion
    # ------------------------------------------------------------------

    def _expand_read_more(self) -> int:
        """Click 'Read more' links to expand truncated comments."""
        expanded = 0
        for text in READ_MORE_TEXTS:
            try:
                for btn in self.driver.find_elements(
                    By.XPATH,
                    f"//tp-yt-paper-button[contains(.,'{text}')] | "
                    f"//button[contains(.,'{text}')] | "
                    f"//span[contains(.,'{text}')]/ancestor::tp-yt-paper-button",
                ):
                    try:
                        if btn.is_displayed():
                            self._safe_click(btn)
                            expanded += 1
                            time.sleep(0.15)
                    except Exception:
                        continue
            except Exception:
                pass
        return expanded

    # ------------------------------------------------------------------
    # Main scraping engine
    # ------------------------------------------------------------------

    def _scrape_batched(self, video_url: str, checkpoint_path: Optional[str] = None) -> List[Comment]:
        """
        Main scraping engine. Scrolls through comments, harvests visible ones
        each iteration.  Checkpoints every 50 new comments.
        """
        MAX_STALL = 8
        CHECKPOINT_EVERY = 50

        # Resume from checkpoint
        self._all_comments = {}
        if checkpoint_path:
            loaded = self._load_checkpoint(checkpoint_path)
            if loaded:
                print(f"  [checkpoint] Resumed {loaded} comments from previous run")

        print(f"Navigating to: {video_url}")
        self.driver.get(video_url)
        time.sleep(5)

        # Dismiss cookie consent
        self._dismiss_cookie_banner()
        time.sleep(1)

        # Scroll down to trigger comment section loading
        print("  Scrolling to comments section...")
        if not self._scroll_to_comments():
            # For shorts, comments may be in a different location
            print("  Trying alternative scroll...")
            self.driver.execute_script("window.scrollTo(0, 600);")
            time.sleep(3)

        time.sleep(2)

        # Sort by newest if requested
        if self.sort_newest:
            self._sort_by_newest()

        self._clicked_reply_keys = set()
        iteration = 0
        no_new = 0
        last_total = len(self._all_comments)
        since_last_checkpoint = 0

        while iteration < self.max_scrolls:
            # 1. Expand "Read more" on truncated comments
            if iteration % 5 == 0:
                self._expand_read_more()

            # 2. Expand reply threads
            if self.expand_replies and iteration % 3 == 0:
                self._expand_reply_threads()

            # 3. Harvest all visible comments
            added = self._harvest_top_level_comments()
            total = len(self._all_comments)

            if total > last_total:
                no_new = 0
                since_last_checkpoint += total - last_total
                print(f"  Iter {iteration + 1}: {total} comments (+{total - last_total})")

                if checkpoint_path and since_last_checkpoint >= CHECKPOINT_EVERY:
                    self._save_checkpoint(checkpoint_path, video_url)
                    print(f"  [checkpoint] Saved {total} comments")
                    since_last_checkpoint = 0
            else:
                no_new += 1
                if no_new <= 3 or no_new % 3 == 0:
                    print(f"  Iter {iteration + 1}: no new (stall {no_new}/{MAX_STALL}, total={total})")

            last_total = total

            if no_new >= MAX_STALL:
                print("  No new comments — done")
                break

            # 4. Scroll down to load more
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.scroll_pause)
            iteration += 1

        # Final harvest
        self._expand_read_more()
        time.sleep(0.5)
        if self.expand_replies:
            self._expand_reply_threads()
            time.sleep(0.5)
        self._harvest_top_level_comments()

        # Save final checkpoint
        if checkpoint_path:
            self._save_checkpoint(checkpoint_path, video_url)
            print(f"  [checkpoint] Final save: {len(self._all_comments)} comments")

        print(f"Collection complete: {len(self._all_comments)} unique comments")
        return list(self._all_comments.values())

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scrape_comments(
        self,
        video_url: str,
        checkpoint_dir: str = "outputs",
    ) -> List[Comment]:
        """Scrape all comments from a YouTube video.

        Works with regular videos, Shorts, and various URL formats
        (youtube.com/watch, youtu.be, youtube.com/shorts).

        Uses rolling batched DOM collection with crash-safe checkpointing.
        """
        video_url = self._normalise_url(video_url)

        if not self.driver:
            self._init_driver()

        ckpt = self._make_checkpoint_path(video_url, checkpoint_dir)

        try:
            comments = self._scrape_batched(video_url, checkpoint_path=ckpt)
            self._clear_checkpoint(ckpt)
        except Exception as e:
            print(f"  Scrape error: {e}")
            if self._all_comments:
                self._save_checkpoint(ckpt, video_url)
                print(f"  [checkpoint] Crash-saved {len(self._all_comments)} comments")
                print(f"  Re-run with the same URL to resume.")
            comments = list(self._all_comments.values())

        print(f"Extracted {len(comments)} total comments")
        return comments

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    @staticmethod
    def export_to_csv(
        comments: List[Comment],
        filepath: str,
        include_headers: bool = True,
    ):
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            if include_headers:
                writer.writerow([
                    "Author", "Comment", "Timestamp", "Likes",
                    "Replies", "Is Reply", "Reply To", "Pinned",
                    "Comment ID", "URL",
                ])
            for c in comments:
                writer.writerow([
                    c.author, c.text, c.timestamp or "",
                    c.likes if c.likes is not None else "",
                    c.replies_count if c.replies_count is not None else "",
                    "Yes" if c.is_reply else "No",
                    c.reply_to or "",
                    "Yes" if c.is_pinned else "No",
                    c.comment_id or "",
                    c.url or "",
                ])
        print(f"Exported {len(comments)} comments to {filepath}")

    @staticmethod
    def export_to_json(comments: List[Comment], filepath: str):
        data = {
            "platform": "youtube",
            "exported_at": datetime.now().isoformat(),
            "total_comments": len(comments),
            "comments": [c.to_dict() for c in comments],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Exported {len(comments)} comments to {filepath}")

    # ------------------------------------------------------------------
    # Context manager & cleanup
    # ------------------------------------------------------------------

    def close(self):
        if self.driver:
            self.driver.quit()
            self.driver = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


# ---------------------------------------------------------------------------
# Convenience
# ---------------------------------------------------------------------------

def quick_scrape(url: str, output: str = "yt_comments.csv", headless: bool = True) -> List[Comment]:
    with YouTubeCommentScraper(headless=headless) as scraper:
        comments = scraper.scrape_comments(url)
        scraper.export_to_csv(comments, output)
        return comments


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <youtube_video_url> [output.csv]")
        sys.exit(1)
    url = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "yt_comments.csv"
    comments = quick_scrape(url, output, headless=False)
    print(f"\nDone -- {len(comments)} comments saved to {output}")
