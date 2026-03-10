"""
Instagram Comment Scraper
=========================
Selenium-based scraper that extracts comments from public Instagram posts and
reels.  Follows the same architecture as the Facebook scraper: Comment dataclass,
crash-safe checkpointing, rolling DOM harvest, CSV/JSON export.

Platform quirks handled
-----------------------
* Cookie consent (GDPR) banner
* Login-wall overlay (dismissed via Escape / "Not now" click)
* "View all N comments" link on post pages
* "Load more comments" / pagination (+ / "View more replies")
* "See translation" / "more" text expansion
* Reel vs. regular post differences
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import tempfile
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional, Set

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
    "Allow all cookies",
    "Allow essential and optional cookies",
    "Accept all",
    "Accept All",
    "Accept",
    "Accetta tutti",
    "Tout accepter",
    "Alle akzeptieren",
    "Aceptar todo",
]

DISMISS_TEXTS = [
    "Not Now",
    "Not now",
    "Decline",
    "Close",
    "Chiudi",
    "Non ora",
    "Pas maintenant",
    "Nicht jetzt",
    "Ahora no",
]

LOGIN_WALL_TEXTS = [
    "Not Now",
    "Not now",
    "Close",
    "Chiudi",
    "Non ora",
]

VIEW_ALL_COMMENTS_TEXTS = [
    "View all",
    "View all comments",
    "Load more comments",
    "Visualizza tutti",
    "Voir tous les",
    "Alle Kommentare",
    "Ver todos",
]

VIEW_MORE_REPLIES_TEXTS = [
    "View replies",
    "View more replies",
    "View all replies",
    "Hide replies",  # toggle — already expanded
    "replies",
    "Visualizza risposte",
    "Voir les réponses",
    "Antworten ansehen",
    "Ver respuestas",
]

SEE_MORE_TEXTS = [
    "more",
    "See translation",
    "See original",
    "Altro",
    "Voir la traduction",
    "Mehr anzeigen",
    "Ver traducción",
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

    def to_dict(self) -> dict:
        return asdict(self)

    def fingerprint(self) -> str:
        raw = f"{self.author}::{self.text}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Main scraper
# ---------------------------------------------------------------------------

class InstagramCommentScraper:
    """Selenium-based Instagram comment scraper with crash-safe checkpointing."""

    def __init__(
        self,
        headless: bool = True,
        scroll_pause: float = 2.0,
        max_scrolls: int = 150,
        timeout: int = 30,
        expand_replies: bool = True,
        max_load_more_clicks: int = 60,
        max_reply_expansions: int = 40,
        chrome_profile_dir: Optional[str] = None,
    ):
        self.headless = headless
        self.scroll_pause = scroll_pause
        self.max_scrolls = max_scrolls
        self.timeout = timeout
        self.expand_replies = expand_replies
        self.max_load_more_clicks = max_load_more_clicks
        self.max_reply_expansions = max_reply_expansions
        self.chrome_profile_dir = chrome_profile_dir

        self.driver: Optional[webdriver.Chrome] = None
        self._all_comments: Dict[str, Comment] = {}
        self._total_load_more_clicks = 0
        self._total_reply_expansions = 0

    # ------------------------------------------------------------------
    # Driver setup
    # ------------------------------------------------------------------

    def _init_driver(self):
        opts = ChromeOptions()
        if self.headless:
            opts.add_argument("--headless=new")

        # Performance flags (same as FB scraper)
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

        # Block images & notifications to speed things up
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
    # Safe click helper
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
        slug = re.sub(r"[^a-zA-Z0-9]", "_", url.split("?")[0])[-80:]
        os.makedirs(directory, exist_ok=True)
        return os.path.join(directory, f"ig_ckpt_{slug}.json")

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
    # Overlay / popup dismissal
    # ------------------------------------------------------------------

    def _dismiss_overlays(self):
        """Close cookie banners, login walls, notification prompts."""

        # Cookie consent
        for text in COOKIE_TEXTS:
            try:
                for btn in self.driver.find_elements(
                    By.XPATH,
                    f"//button[contains(.,'{text}')]",
                ):
                    if btn.is_displayed():
                        self._safe_click(btn)
                        time.sleep(0.8)
                        break
            except Exception:
                pass

        # Login wall / "Not now" prompts
        for text in LOGIN_WALL_TEXTS + DISMISS_TEXTS:
            try:
                for btn in self.driver.find_elements(
                    By.XPATH,
                    f"//button[contains(.,'{text}')] | //*[@role='button'][contains(.,'{text}')]",
                ):
                    if btn.is_displayed():
                        self._safe_click(btn)
                        time.sleep(0.5)
            except Exception:
                pass

        # Escape key to dismiss any remaining modal
        try:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
            time.sleep(0.3)
        except Exception:
            pass

    def _dismiss_login_wall(self):
        """Instagram may show a full-page login wall; try to dismiss it."""
        # Look for "Not now" / close buttons in dialogs
        for text in LOGIN_WALL_TEXTS:
            try:
                for btn in self.driver.find_elements(
                    By.XPATH,
                    f"//button[contains(.,'{text}')] | "
                    f"//div[@role='dialog']//button[contains(.,'{text}')]",
                ):
                    if btn.is_displayed():
                        self._safe_click(btn)
                        time.sleep(0.5)
                        return True
            except Exception:
                pass

        # Try close buttons (svg X icons)
        try:
            for btn in self.driver.find_elements(
                By.CSS_SELECTOR,
                "div[role='dialog'] button[aria-label='Close'],"
                "div[role='dialog'] button svg[aria-label='Close']",
            ):
                parent = btn if btn.tag_name == "button" else btn.find_element(By.XPATH, "./ancestor::button")
                if parent.is_displayed():
                    self._safe_click(parent)
                    time.sleep(0.5)
                    return True
        except Exception:
            pass

        return False

    # ------------------------------------------------------------------
    # URL helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_reel_url(url: str) -> bool:
        return bool(re.search(r"/reel/|/reels/", url))

    @staticmethod
    def _normalise_url(url: str) -> str:
        """Ensure the URL is a full Instagram post URL."""
        url = url.strip()
        if not url.startswith("http"):
            url = "https://www.instagram.com/" + url.lstrip("/")
        return url

    # ------------------------------------------------------------------
    # Comment DOM extraction
    # ------------------------------------------------------------------

    def _extract_author_from_element(self, el) -> str:
        """Extract author username from a comment element."""
        # Try username links (a tags with href to user profile)
        for sel in [
            "a[href*='/'] span",
            "a h3",
            "a span",
            "h3",
        ]:
            try:
                found = el.find_element(By.CSS_SELECTOR, sel)
                name = found.text.strip()
                if name and len(name) > 0 and "\n" not in name:
                    return name
            except (NoSuchElementException, StaleElementReferenceException):
                continue
        return ""

    def _extract_text_from_element(self, el, author: str) -> str:
        """Extract comment text from a comment element."""
        candidates = []
        try:
            # Instagram typically puts comment text in spans
            for span in el.find_elements(By.CSS_SELECTOR, "span[dir='auto'], span"):
                t = span.text.strip()
                if (
                    t
                    and t != author
                    and len(t) > 1
                    and t not in SEE_MORE_TEXTS
                    and not t.startswith("Verified")
                    and t != "Reply"
                    and not re.match(r"^\d+[smhdw]$", t)
                    and not re.match(r"^\d+ likes?$", t, re.IGNORECASE)
                ):
                    candidates.append(t)
        except Exception:
            pass

        if candidates:
            # Return the longest candidate — usually the full comment text
            return max(candidates, key=len)

        # Fallback: full text minus author
        try:
            raw = el.text.strip()
            if author and raw.startswith(author):
                raw = raw[len(author):].strip()
            lines = [
                ln for ln in raw.split("\n")
                if ln.strip()
                and ln.strip() != "Reply"
                and ln.strip() not in SEE_MORE_TEXTS
                and not re.match(r"^\d+[smhdw]$", ln.strip())
                and not re.match(r"^\d+ likes?$", ln.strip(), re.IGNORECASE)
            ]
            if lines:
                return " ".join(lines)
        except Exception:
            pass

        return ""

    def _extract_timestamp_from_element(self, el) -> Optional[str]:
        """Extract timestamp from a comment element."""
        # Instagram uses <time> elements with datetime attrs
        try:
            time_el = el.find_element(By.TAG_NAME, "time")
            dt = time_el.get_attribute("datetime")
            if dt:
                return dt
            return time_el.text.strip() or None
        except (NoSuchElementException, StaleElementReferenceException):
            pass

        # Fallback: look for relative time text (17h, 2d, 1w)
        try:
            for a in el.find_elements(By.CSS_SELECTOR, "a time, a span"):
                t = a.text.strip()
                if re.match(r"^\d+[smhdw]$", t):
                    return t
        except Exception:
            pass

        return None

    def _extract_likes_from_element(self, el) -> Optional[int]:
        """Extract like count from a comment element."""
        try:
            # Look for "X likes" or "X like" text
            for span in el.find_elements(By.CSS_SELECTOR, "span, button span"):
                t = span.text.strip().lower()
                m = re.match(r"^(\d[\d,]*)\s*likes?$", t)
                if m:
                    return int(m.group(1).replace(",", ""))
        except Exception:
            pass

        # Aria-label approach
        try:
            for btn in el.find_elements(By.CSS_SELECTOR, "button[aria-label]"):
                label = btn.get_attribute("aria-label") or ""
                m = re.search(r"(\d[\d,]*)\s*like", label, re.IGNORECASE)
                if m:
                    return int(m.group(1).replace(",", ""))
        except Exception:
            pass

        return None

    def _extract_reply_count_from_element(self, el) -> Optional[int]:
        """Extract reply count from a comment element."""
        try:
            for btn in el.find_elements(By.CSS_SELECTOR, "button, span"):
                t = btn.text.strip().lower()
                m = re.search(r"view\s+(\d+)\s+repl", t)
                if m:
                    return int(m.group(1))
                if "view replies" in t or "view all replies" in t:
                    return 1  # at least one
        except Exception:
            pass
        return None

    # ------------------------------------------------------------------
    # Comment harvesting
    # ------------------------------------------------------------------

    def _find_comment_elements(self) -> list:
        """Find all comment container elements on the page."""
        elements = []

        # Instagram comment structure:
        # - Post page: comments in a scrollable section on the right (desktop)
        #   or below the post (mobile layout)
        # - Each comment is typically in a <li> or <div> with specific structure

        # Strategy 1: article-based comments section (desktop view)
        try:
            # Comments on desktop are often in a <ul> after the post content
            comment_list = self.driver.find_elements(By.CSS_SELECTOR, "ul ul li")
            if comment_list:
                elements.extend(comment_list)
        except Exception:
            pass

        # Strategy 2: div-based comment containers
        if not elements:
            try:
                # Look for comment blocks with username + text pattern
                sections = self.driver.find_elements(
                    By.CSS_SELECTOR,
                    "div[role='dialog'] ul > div,"
                    "article ul > div,"
                    "div[class] > ul > div",
                )
                elements.extend(sections)
            except Exception:
                pass

        # Strategy 3: find elements containing username links + text spans
        if not elements:
            try:
                # Comments often have this structure:
                # <div><a href="/username/"><span>username</span></a> <span>comment text</span></div>
                page_divs = self.driver.find_elements(
                    By.XPATH,
                    "//div[.//a[contains(@href,'/')]/span and .//span[@dir='auto']]",
                )
                # Filter to actual comment containers (small enough to be single comments)
                for div in page_divs:
                    try:
                        h = div.size.get("height", 0)
                        if 20 < h < 500:
                            elements.append(div)
                    except Exception:
                        pass
            except Exception:
                pass

        return elements

    def _harvest_comments(self) -> int:
        """Extract all currently visible comments into self._all_comments.
        Returns the number of NEW comments added."""
        added = 0
        elements = self._find_comment_elements()

        for el in elements:
            try:
                author = self._extract_author_from_element(el)
                text = self._extract_text_from_element(el, author)

                if not text or len(text.strip()) < 2:
                    continue

                # Skip if the text is just the author name
                if text.strip() == author:
                    continue

                comment = Comment(
                    author=author,
                    text=text.strip(),
                    timestamp=self._extract_timestamp_from_element(el),
                    likes=self._extract_likes_from_element(el),
                    replies_count=self._extract_reply_count_from_element(el),
                )

                fp = comment.fingerprint()
                if fp not in self._all_comments:
                    self._all_comments[fp] = comment
                    added += 1

            except StaleElementReferenceException:
                continue
            except Exception:
                continue

        return added

    # ------------------------------------------------------------------
    # Comment loading / expansion
    # ------------------------------------------------------------------

    def _click_view_all_comments(self) -> bool:
        """Click 'View all N comments' link on the post page."""
        for text in VIEW_ALL_COMMENTS_TEXTS:
            try:
                for btn in self.driver.find_elements(
                    By.XPATH,
                    f"//button[contains(.,'{text}')] | "
                    f"//a[contains(.,'{text}')] | "
                    f"//span[contains(.,'{text}')]/ancestor::button | "
                    f"//span[contains(.,'{text}')]/ancestor::a",
                ):
                    if btn.is_displayed():
                        self._safe_click(btn)
                        self._total_load_more_clicks += 1
                        return True
            except Exception:
                pass
        return False

    def _click_load_more_comments(self) -> bool:
        """Click a 'Load more comments' / pagination button.
        Instagram uses a (+) circle or text button to load older comments."""
        if self._total_load_more_clicks >= self.max_load_more_clicks:
            return False

        # Look for the "+" circle button (load more) — it's usually an SVG circle
        try:
            plus_btns = self.driver.find_elements(
                By.XPATH,
                "//button[contains(@class,'load') or @aria-label='Load more comments']"
                " | //button[.//*[name()='svg'][.//*[name()='circle']]]"
                " | //*[@aria-label='Load more comments']",
            )
            for btn in plus_btns:
                try:
                    if btn.is_displayed():
                        self._safe_click(btn)
                        self._total_load_more_clicks += 1
                        return True
                except Exception:
                    continue
        except Exception:
            pass

        # Text-based load more buttons
        for text in VIEW_ALL_COMMENTS_TEXTS:
            try:
                for btn in self.driver.find_elements(
                    By.XPATH,
                    f"//button[contains(.,'{text}')] | //a[contains(.,'{text}')]",
                ):
                    if btn.is_displayed():
                        self._safe_click(btn)
                        self._total_load_more_clicks += 1
                        return True
            except Exception:
                pass

        return False

    def _expand_replies(self) -> int:
        """Click 'View replies' buttons to expand reply threads."""
        expanded = 0
        if self._total_reply_expansions >= self.max_reply_expansions:
            return 0

        for text in VIEW_MORE_REPLIES_TEXTS:
            if self._total_reply_expansions >= self.max_reply_expansions:
                break
            try:
                for btn in self.driver.find_elements(
                    By.XPATH,
                    f"//button[contains(.,'{text}')] | //span[contains(.,'{text}')]/ancestor::button",
                ):
                    if self._total_reply_expansions >= self.max_reply_expansions:
                        break
                    try:
                        if btn.is_displayed():
                            # Don't expand "Hide replies"
                            btn_text = btn.text.strip().lower()
                            if "hide" in btn_text:
                                continue
                            self._safe_click(btn)
                            expanded += 1
                            self._total_reply_expansions += 1
                            time.sleep(0.8)
                    except StaleElementReferenceException:
                        continue
                    except Exception:
                        continue
            except Exception:
                pass

        if expanded:
            print(f"  Expanded {expanded} reply threads")
        return expanded

    def _expand_see_more(self) -> int:
        """Click 'more' links to expand truncated comment text."""
        expanded = 0
        for text in SEE_MORE_TEXTS:
            try:
                for btn in self.driver.find_elements(
                    By.XPATH,
                    f"//button[.='{text}'] | //span[@role='button'][.='{text}'] "
                    f"| //button[contains(.,'{text}')]",
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
    # Scrolling
    # ------------------------------------------------------------------

    def _find_scroll_container(self):
        """Find the scrollable container for comments (dialog or section)."""
        # In post dialog view, comments are in a scrollable div inside the dialog
        try:
            dialogs = self.driver.find_elements(By.CSS_SELECTOR, "div[role='dialog']")
            for dialog in dialogs:
                if dialog.is_displayed():
                    # Find the scrollable section within dialog
                    scrollables = dialog.find_elements(
                        By.XPATH,
                        ".//ul/ancestor::div[contains(@style,'overflow') or "
                        "contains(@style,'scroll')]",
                    )
                    if scrollables:
                        return scrollables[0]
                    return dialog
        except Exception:
            pass

        # On direct post page, the comments section itself may scroll
        try:
            sections = self.driver.find_elements(
                By.CSS_SELECTOR,
                "section, article",
            )
            for s in sections:
                if s.is_displayed() and s.size.get("height", 0) > 200:
                    return s
        except Exception:
            pass

        return None

    def _scroll_container(self, container) -> None:
        """Scroll a container element down by a step."""
        try:
            h = self.driver.execute_script("return arguments[0].scrollHeight", container)
            top = self.driver.execute_script("return arguments[0].scrollTop", container)
            step = max(400, h // 6)
            self.driver.execute_script(f"arguments[0].scrollTop = {top + step};", container)
        except Exception:
            # Fallback: scroll the whole page
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

    # ------------------------------------------------------------------
    # Main scraping engine
    # ------------------------------------------------------------------

    def _scrape_batched(self, post_url: str, checkpoint_path: Optional[str] = None) -> List[Comment]:
        """
        Main scraping engine.  Scrolls through comments, harvests visible ones
        each iteration, clicks load-more / expand-replies buttons.
        Checkpoints every 50 new comments.
        """
        MAX_STALL = 8
        CHECKPOINT_EVERY = 50

        # --- Resume from checkpoint ---
        self._all_comments = {}
        if checkpoint_path:
            loaded = self._load_checkpoint(checkpoint_path)
            if loaded:
                print(f"  [checkpoint] Resumed {loaded} comments from previous run")

        print(f"Navigating to: {post_url}")
        self.driver.get(post_url)
        time.sleep(5)
        self._dismiss_overlays()
        time.sleep(1)

        # Dismiss login wall if it appears
        self._dismiss_login_wall()
        time.sleep(0.5)

        # Click "View all comments" if it exists
        if self._click_view_all_comments():
            print("  Clicked 'View all comments'")
            time.sleep(3)
            self._dismiss_overlays()
            time.sleep(1)

        container = self._find_scroll_container()
        if container:
            print("  Scroll container found")
        else:
            print("  No scroll container — will scroll full page")

        iteration = 0
        no_new = 0
        last_total = len(self._all_comments)
        since_last_checkpoint = 0

        while iteration < self.max_scrolls:
            # 1. Expand truncated text
            if iteration % 3 == 0:
                self._expand_see_more()

            # 2. Expand reply threads
            if self.expand_replies and iteration % 4 == 0:
                self._expand_replies()

            # 3. Harvest visible comments
            added = self._harvest_comments()
            total = len(self._all_comments)

            if total > last_total:
                no_new = 0
                since_last_checkpoint += total - last_total
                print(f"  Iter {iteration + 1}: {total} comments (+{total - last_total})")

                if checkpoint_path and since_last_checkpoint >= CHECKPOINT_EVERY:
                    self._save_checkpoint(checkpoint_path, post_url)
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

            # 4. Load more comments
            clicked = self._click_load_more_comments()
            if clicked:
                time.sleep(self.scroll_pause)

            # 5. Scroll to reveal more
            if container:
                self._scroll_container(container)
            else:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(self.scroll_pause if not clicked else self.scroll_pause * 0.6)
            iteration += 1

        # Final harvest
        self._expand_see_more()
        time.sleep(0.5)
        self._harvest_comments()

        # Save final checkpoint
        if checkpoint_path:
            self._save_checkpoint(checkpoint_path, post_url)
            print(f"  [checkpoint] Final save: {len(self._all_comments)} comments")

        print(f"Collection complete: {len(self._all_comments)} unique comments")
        return list(self._all_comments.values())

    # ------------------------------------------------------------------
    # Login
    # ------------------------------------------------------------------

    def _login(self, username: str, password: str):
        """Log in to Instagram."""
        try:
            print("Navigating to Instagram login...")
            self.driver.get("https://www.instagram.com/accounts/login/")
            time.sleep(4)

            # Accept cookies first
            self._dismiss_overlays()
            time.sleep(1)

            user_el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
            )
            pass_el = self.driver.find_element(By.CSS_SELECTOR, "input[name='password']")

            user_el.clear()
            user_el.send_keys(username)
            time.sleep(0.3)
            pass_el.clear()
            pass_el.send_keys(password)
            time.sleep(0.3)
            pass_el.send_keys(Keys.RETURN)
            time.sleep(6)

            # Dismiss "Save login info?" / "Turn on notifications?" prompts
            self._dismiss_overlays()
            time.sleep(1)
            self._dismiss_overlays()

            print("Login submitted")
        except TimeoutException:
            print("No login form found — may already be logged in")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def scrape_comments(
        self,
        post_url: str,
        login_username: Optional[str] = None,
        login_password: Optional[str] = None,
        checkpoint_dir: str = "outputs",
    ) -> List[Comment]:
        """Scrape all comments from an Instagram post or reel.

        Uses rolling batched DOM collection with crash-safe checkpointing.
        """
        post_url = self._normalise_url(post_url)

        if not self.driver:
            self._init_driver()

        if login_username and login_password:
            self._login(login_username, login_password)

        ckpt = self._make_checkpoint_path(post_url, checkpoint_dir)

        try:
            comments = self._scrape_batched(post_url, checkpoint_path=ckpt)
            self._clear_checkpoint(ckpt)
        except Exception as e:
            print(f"  Scrape error: {e}")
            if self._all_comments:
                self._save_checkpoint(ckpt, post_url)
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
                    "Replies", "Is Reply", "Reply To", "Comment ID", "URL",
                ])
            for c in comments:
                writer.writerow([
                    c.author, c.text, c.timestamp or "",
                    c.likes if c.likes is not None else "",
                    c.replies_count if c.replies_count is not None else "",
                    "Yes" if c.is_reply else "No",
                    c.reply_to or "",
                    c.comment_id or "",
                    c.url or "",
                ])
        print(f"Exported {len(comments)} comments to {filepath}")

    @staticmethod
    def export_to_json(comments: List[Comment], filepath: str):
        data = {
            "platform": "instagram",
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

def quick_scrape(url: str, output: str = "ig_comments.csv", headless: bool = True) -> List[Comment]:
    with InstagramCommentScraper(headless=headless) as scraper:
        comments = scraper.scrape_comments(url)
        scraper.export_to_csv(comments, output)
        return comments


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <instagram_post_url> [output.csv]")
        sys.exit(1)
    url = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "ig_comments.csv"
    comments = quick_scrape(url, output, headless=False)
    print(f"\nDone -- {len(comments)} comments saved to {output}")
