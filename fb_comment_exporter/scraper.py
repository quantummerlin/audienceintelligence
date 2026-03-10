"""
Facebook Comment Exporter
A free, open-source tool to extract comments from Facebook posts.
"""

import os
import time
import csv
import json
import re
import hashlib
from datetime import datetime
from typing import List, Dict, Optional, Set
from dataclasses import dataclass, asdict, field

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException,
        ElementClickInterceptedException, StaleElementReferenceException,
        MoveTargetOutOfBoundsException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False


# ---------------------------------------------------------------------------
# Localised button text lists
# ---------------------------------------------------------------------------

COOKIE_ALLOW_TEXTS = [
    "Allow all cookies", "Allow all", "Accept all", "Accept All",
    "Alle akzeptieren", "Tout autoriser", "Aceptar todo", "Accetta tutto",
    "Aceitar tudo", "Alle cookies toestaan", "OK", "Continue", "Got it",
]

DISMISS_POPUP_TEXTS = [
    "Not now", "Close", "Skip", "Maybe later", "No thanks",
    "Non adesso", "Fermer", "Cerrar", "Schliessen",
]

LOGIN_WALL_CLOSE = ["Close", "Not now", "Non adesso", "Fermer", "Cerrar"]

SEE_MORE_TEXTS = [
    "See more", "Vedi altro", "Voir plus", "Ver mas", "Mehr anzeigen",
    "Xem them", "Read more", "Show more",
]

VIEW_MORE_COMMENTS_TEXTS = [
    "View more comments", "more comments", "Visualizza altri commenti",
    "Ver mas comentarios", "Afficher plus de commentaires",
    "Mehr Kommentare anzeigen", "More comments",
]

VIEW_MORE_REPLIES_TEXTS = [
    "more replies", "View replies", "Visualizza risposte",
    "Ver respuestas", "Voir les reponses", "Antworten",
]

SORT_ALL_TEXTS = [
    "All comments", "Most recent", "Tutti i commenti",
    "Tous les commentaires", "Todos los comentarios",
]

TIME_KEYWORDS = [
    "ago", "hour", "minute", "day", "week", "yesterday",
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Comment:
    """Represents a single Facebook comment or reply."""
    author: str
    text: str
    timestamp: Optional[str] = None
    likes: Optional[int] = None
    replies_count: Optional[int] = None
    comment_id: Optional[str] = None
    url: Optional[str] = None
    is_reply: bool = False
    reply_to: Optional[str] = None

    def to_dict(self) -> Dict:
        return asdict(self)

    def fingerprint(self) -> str:
        raw = f"{self.author}::{self.text}"
        return hashlib.md5(raw.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Main scraper
# ---------------------------------------------------------------------------

class FacebookCommentScraper:
    """
    Selenium-based Facebook comment scraper.

    Usage:
        with FacebookCommentScraper(headless=False) as scraper:
            comments = scraper.scrape_comments("https://facebook.com/...")
            scraper.export_to_csv(comments, "output.csv")
    """

    def __init__(
        self,
        headless: bool = True,
        scroll_pause: float = 2.5,
        max_scrolls: int = 100,
        timeout: int = 30,
        expand_replies: bool = True,
        max_load_more_clicks: int = 30,
        max_reply_expansions: int = 20,
        chrome_profile_dir: Optional[str] = None,
    ):
        if not SELENIUM_AVAILABLE:
            raise ImportError("Selenium is required: pip install selenium")
        self.headless = headless
        self.scroll_pause = scroll_pause
        self.max_scrolls = max_scrolls
        self.timeout = timeout
        self.expand_replies = expand_replies
        self.max_load_more_clicks = max_load_more_clicks
        self.max_reply_expansions = max_reply_expansions
        self.chrome_profile_dir = chrome_profile_dir
        self._total_load_more_clicks = 0
        self._all_comments: Dict[str, Comment] = {}  # fingerprint -> Comment, global across scrolls
        self.driver = None
        self._wait = None
        self._interceptor_injected = False

    # ------------------------------------------------------------------
    # Driver setup
    # ------------------------------------------------------------------

    def _init_driver(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless=new")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1440,900")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        options.add_argument("--lang=en-US,en;q=0.9")
        # Memory / performance optimisations
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        options.add_argument("--disable-translate")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-default-apps")
        options.add_argument("--mute-audio")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        )
        # Block images — cuts Chrome RAM usage by ~30-40 % with no effect on comment text
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.images": 2,
            "profile.managed_default_content_settings.images": 2,
        })
        options.add_experimental_option("excludeSwitches", ["enable-logging"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument("--disable-blink-features=AutomationControlled")

        # Persistent profile — keeps cookies/login between runs
        if self.chrome_profile_dir:
            os.makedirs(self.chrome_profile_dir, exist_ok=True)
            options.add_argument(f"--user-data-dir={self.chrome_profile_dir}")
            print(f"Using Chrome profile: {self.chrome_profile_dir}")

        if WEBDRIVER_MANAGER_AVAILABLE:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)
        else:
            self.driver = webdriver.Chrome(options=options)

        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )
        self._wait = WebDriverWait(self.driver, self.timeout)
        return self.driver

    # ------------------------------------------------------------------
    # Utility helpers
    # ------------------------------------------------------------------

    def _safe_click(self, element) -> bool:
        try:
            self.driver.execute_script(
                "arguments[0].scrollIntoView({block:'center'});", element
            )
            time.sleep(0.3)
            self.driver.execute_script("arguments[0].click();", element)
            return True
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Network interception (fast path)
    # ------------------------------------------------------------------

    _INTERCEPTOR_JS = """
if (!window._fbCapturedResponses) {
    window._fbCapturedResponses = [];
    window._fbSeenHashes = new Set();

    function _fbCapture(text) {
        if (!text || text.length < 50) return;
        // Only store responses that likely contain comment data
        if (!text.includes('"body"') && !text.includes('"author"') &&
            !text.includes('"comment"') && !text.includes('"node"')) return;
        // Deduplicate by first 200 chars
        var h = text.substring(0, 200);
        if (window._fbSeenHashes.has(h)) return;
        window._fbSeenHashes.add(h);
        window._fbCapturedResponses.push(text);
    }

    // Intercept fetch
    var _origFetch = window.fetch;
    window.fetch = function() {
        var args = arguments;
        return _origFetch.apply(this, args).then(function(resp) {
            try {
                resp.clone().text().then(function(t) { _fbCapture(t); });
            } catch(e) {}
            return resp;
        });
    };

    // Intercept XHR
    var _origOpen = XMLHttpRequest.prototype.open;
    var _origSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.open = function() {
        this._fbUrl = arguments[1] || '';
        return _origOpen.apply(this, arguments);
    };
    XMLHttpRequest.prototype.send = function() {
        var xhr = this;
        xhr.addEventListener('load', function() {
            try { _fbCapture(xhr.responseText); } catch(e) {}
        });
        return _origSend.apply(this, arguments);
    };
}
"""

    def _inject_interceptor(self):
        """Inject JS network interceptor into the page."""
        if not self._interceptor_injected:
            self.driver.execute_script(self._INTERCEPTOR_JS)
            self._interceptor_injected = True

    def _read_captured_responses(self) -> List[str]:
        """Pull all captured network response strings from the browser."""
        try:
            return self.driver.execute_script(
                "return window._fbCapturedResponses || [];"
            ) or []
        except Exception:
            return []

    def _clear_captured_responses(self):
        try:
            self.driver.execute_script(
                "window._fbCapturedResponses = []; window._fbSeenHashes = new Set();"
            )
        except Exception:
            pass

    @staticmethod
    def _walk(obj, key):
        """Recursively find all values for a given key in nested dicts/lists."""
        results = []
        if isinstance(obj, dict):
            if key in obj:
                results.append(obj[key])
            for v in obj.values():
                results.extend(FacebookCommentScraper._walk(v, key))
        elif isinstance(obj, list):
            for item in obj:
                results.extend(FacebookCommentScraper._walk(item, key))
        return results

    @staticmethod
    def _extract_text_from_node(node: dict) -> str:
        """Pull comment body text from a GraphQL comment node."""
        # Try common FB GraphQL shapes
        for path in [
            ["body", "text"],
            ["message", "text"],
            ["message"],
            ["body"],
        ]:
            obj = node
            for k in path:
                if isinstance(obj, dict):
                    obj = obj.get(k)
                else:
                    obj = None
                    break
            if isinstance(obj, str) and obj.strip():
                return obj.strip()
        return ""

    @staticmethod
    def _extract_author_from_node(node: dict) -> str:
        """Pull author name from a GraphQL comment node."""
        for path in [
            ["author", "name"],
            ["commenter", "name"],
            ["author", "short_name"],
        ]:
            obj = node
            for k in path:
                if isinstance(obj, dict):
                    obj = obj.get(k)
                else:
                    obj = None
                    break
            if isinstance(obj, str) and obj.strip():
                return obj.strip()
        return ""

    @staticmethod
    def _extract_timestamp_from_node(node: dict) -> Optional[str]:
        for key in ["created_time", "timestamp", "creation_time"]:
            v = node.get(key)
            if isinstance(v, (int, str)) and v:
                return str(v)
        return None

    @staticmethod
    def _extract_likes_from_node(node: dict) -> Optional[int]:
        for path in [
            ["feedback", "reactors", "count"],
            ["feedback", "reaction_count", "count"],
            ["like_count"],
            ["likers", "count"],
        ]:
            obj = node
            for k in path:
                if isinstance(obj, dict):
                    obj = obj.get(k)
                else:
                    obj = None
                    break
            if isinstance(obj, int):
                return obj
        return None

    def _parse_graphql_responses(self, responses: List[str]) -> List[Comment]:
        """Parse captured GraphQL JSON blobs and extract Comment objects."""
        comments: List[Comment] = []
        seen: Set[str] = set()

        for raw in responses:
            # FB responses often start with "for (;;);" — strip it
            text = raw.lstrip()
            if text.startswith("for (;;);"):
                text = text[9:]

            # Some responses are newline-delimited JSON
            blobs = []
            for line in text.splitlines():
                line = line.strip()
                if line.startswith("{") or line.startswith("["):
                    blobs.append(line)
            if not blobs:
                blobs = [text]

            for blob in blobs:
                try:
                    data = json.loads(blob)
                except Exception:
                    # Try to find JSON objects embedded in the text
                    for m in re.finditer(r'\{[^{}]{20,}\}', blob):
                        try:
                            data = json.loads(m.group())
                            nodes = FacebookCommentScraper._walk(data, "node")
                            for node in nodes:
                                if not isinstance(node, dict):
                                    continue
                                text_val = FacebookCommentScraper._extract_text_from_node(node)
                                if not text_val:
                                    continue
                                author = FacebookCommentScraper._extract_author_from_node(node)
                                c = Comment(
                                    author=author,
                                    text=text_val,
                                    timestamp=FacebookCommentScraper._extract_timestamp_from_node(node),
                                    likes=FacebookCommentScraper._extract_likes_from_node(node),
                                )
                                fp = c.fingerprint()
                                if fp not in seen:
                                    seen.add(fp)
                                    comments.append(c)
                        except Exception:
                            pass
                    continue

                # Walk the parsed JSON for comment nodes
                nodes = self._walk(data, "node")
                nodes += self._walk(data, "edges")

                for node in nodes:
                    if isinstance(node, list):
                        # edges array — each item has a "node"
                        for edge in node:
                            if isinstance(edge, dict) and "node" in edge:
                                nodes.append(edge["node"])
                        continue
                    if not isinstance(node, dict):
                        continue

                    text_val = self._extract_text_from_node(node)
                    if not text_val:
                        continue
                    author = self._extract_author_from_node(node)
                    c = Comment(
                        author=author,
                        text=text_val,
                        timestamp=self._extract_timestamp_from_node(node),
                        likes=self._extract_likes_from_node(node),
                    )
                    fp = c.fingerprint()
                    if fp not in seen:
                        seen.add(fp)
                        comments.append(c)

        return comments

    def _fast_click_load_more(self, panel=None) -> int:
        """Rapidly click all 'View more comments' buttons with minimal wait."""
        return self._click_view_more_everywhere(panel)

    # ------------------------------------------------------------------
    # Checkpoint helpers  (auto-save every N comments so crashes don't
    # lose progress; the checkpoint is cleared on clean finish)
    # ------------------------------------------------------------------

    @staticmethod
    def _make_checkpoint_path(post_url: str, outputs_dir: str = "outputs") -> str:
        """Return a deterministic checkpoint JSON path for a given URL."""
        import re
        slug = re.sub(r"[^\w]+", "_", post_url)[:60].strip("_")
        os.makedirs(outputs_dir, exist_ok=True)
        return os.path.join(outputs_dir, f"_checkpoint_{slug}.json")

    def _save_checkpoint(self, path: str, post_url: str) -> None:
        """Persist current _all_comments to a JSON checkpoint file."""
        try:
            data = {
                "url": post_url,
                "saved_at": datetime.now().isoformat(),
                "count": len(self._all_comments),
                "comments": [c.to_dict() for c in self._all_comments.values()],
            }
            tmp = path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(tmp, path)  # atomic on most OSes
        except Exception as e:
            print(f"  [checkpoint] save failed: {e}")

    def _load_checkpoint(self, path: str) -> int:
        """Load a checkpoint file back into _all_comments. Returns number loaded."""
        if not os.path.exists(path):
            return 0
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            loaded = 0
            for d in data.get("comments", []):
                c = Comment(**{k: d.get(k) for k in Comment.__dataclass_fields__})
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
        """Delete checkpoint file after a successful run."""
        try:
            if os.path.exists(path):
                os.remove(path)
        except Exception:
            pass

    def _harvest_visible(self) -> int:
        """Extract all currently visible article elements and add to self._all_comments.
        Returns number of NEW comments added this harvest."""
        added = 0
        try:
            articles = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            for article in articles:
                try:
                    c = self._parse_article(article)
                    if c and c.text:
                        fp = c.fingerprint()
                        if fp not in self._all_comments:
                            self._all_comments[fp] = c
                            added += 1
                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue
        except Exception:
            pass
        return added

    def _click_one_load_more(self, panel=None) -> bool:
        """Find and click exactly ONE 'View more comments' button that has not
        been clicked before (tracked by location hash). Returns True if clicked."""
        search_texts = VIEW_MORE_COMMENTS_TEXTS
        scopes = []
        if panel:
            try:
                _ = panel.tag_name
                scopes.append(panel)
            except StaleElementReferenceException:
                pass
        scopes.append(self.driver)

        for scope in scopes:
            for text in search_texts:
                try:
                    els = scope.find_elements(
                        By.XPATH,
                        f".//*[@role='button'][contains(.,'{text}')] "
                        f"| .//a[contains(.,'{text}')]",
                    )
                    for el in els:
                        try:
                            if not el.is_displayed():
                                continue
                            # Identify button by its text + location to avoid re-clicking
                            loc = el.location
                            loc_key = f"{el.text.strip()[:40]}@{loc.get('x',0):.0f},{loc.get('y',0):.0f}"
                            if loc_key in self._clicked_button_keys:
                                continue
                            self._clicked_button_keys.add(loc_key)
                            self._safe_click(el)
                            self._total_load_more_clicks += 1
                            return True
                        except StaleElementReferenceException:
                            continue
                        except Exception:
                            continue
                except Exception:
                    pass
        return False

    def _scrape_batched(self, post_url: str, checkpoint_path: Optional[str] = None) -> List[Comment]:
        """
        Main scraping engine. Scrolls through comment panel/page in steps,
        harvesting all visible comments each iteration into a global dedup dict.
        Progress is measured by NEW UNIQUE COMMENTS added — not buttons clicked.
        Stops when no new comments appear for MAX_STALL consecutive iterations.

        If checkpoint_path is provided, existing progress is loaded at startup
        and saved to disk every CHECKPOINT_EVERY new comments, so a Chrome crash
        never loses more than ~50 comments.
        """
        MAX_STALL = 6
        CHECKPOINT_EVERY = 50  # save to disk after this many new comments

        is_reel = self._is_reel_url(post_url)

        # --- Resume from checkpoint if one exists ---
        self._all_comments = {}
        if checkpoint_path:
            loaded = self._load_checkpoint(checkpoint_path)
            if loaded:
                print(f"  [checkpoint] Resumed {loaded} comments from previous run: {checkpoint_path}")

        print(f"Navigating to: {post_url}")
        self.driver.get(post_url)
        time.sleep(7 if is_reel else 5)
        self._dismiss_overlays()
        time.sleep(1)

        if is_reel:
            print("Reel detected — opening comment panel...")
            self._open_reel_comments()
            time.sleep(2)
        else:
            self._try_switch_to_all_comments()

        panel = self._find_comment_panel() if is_reel else None
        if panel:
            print("  Comment panel found — will scroll inside it")
        else:
            print("  No panel found — scrolling full page")

        self._clicked_button_keys: Set[str] = set()
        iteration = 0
        no_new = 0
        last_total = len(self._all_comments)  # start from resumed count
        since_last_checkpoint = 0

        while iteration < self.max_scrolls:
            # 1. Expand any "See more" links first
            if iteration % 5 == 0:
                self._expand_see_more()

            # 2. Harvest everything currently visible
            added = self._harvest_visible()
            total = len(self._all_comments)

            if total > last_total:
                no_new = 0
                since_last_checkpoint += total - last_total
                print(f"  Iter {iteration+1}: {total} comments collected (+{total - last_total})")
                # 3. Auto-save checkpoint every CHECKPOINT_EVERY new comments
                if checkpoint_path and since_last_checkpoint >= CHECKPOINT_EVERY:
                    self._save_checkpoint(checkpoint_path, post_url)
                    print(f"  [checkpoint] Saved {total} comments → {checkpoint_path}")
                    since_last_checkpoint = 0
            else:
                no_new += 1
                print(f"  Iter {iteration+1}: no new comments (stall {no_new}/{MAX_STALL}, total={total})")

            last_total = total

            if no_new >= MAX_STALL:
                print("  No new comments — done loading")
                break

            if self._total_load_more_clicks >= self.max_load_more_clicks:
                print(f"  Click cap reached ({self.max_load_more_clicks})")
                break

            # 4. Click one "View more comments" button
            clicked = self._click_one_load_more(panel)
            if clicked:
                time.sleep(self.scroll_pause)

            # 5. Scroll down to load next batch and reveal more buttons
            if panel:
                try:
                    h = self.driver.execute_script("return arguments[0].scrollHeight", panel)
                    top = self.driver.execute_script("return arguments[0].scrollTop", panel)
                    step = max(400, h // 8)
                    self.driver.execute_script(
                        f"arguments[0].scrollTop = {top + step};", panel
                    )
                except Exception:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            else:
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            time.sleep(self.scroll_pause if not clicked else self.scroll_pause * 0.5)
            iteration += 1

        # Final harvest after all loading is done
        self._expand_see_more()
        time.sleep(1)
        self._harvest_visible()

        # Save final checkpoint then clear it
        if checkpoint_path:
            self._save_checkpoint(checkpoint_path, post_url)
            print(f"  [checkpoint] Final save: {len(self._all_comments)} comments")

        print(f"Batched collection complete: {len(self._all_comments)} unique comments")
        return list(self._all_comments.values())

    def _dismiss_overlays(self):
        """Close cookie banners, login walls, notification modals."""
        for text in COOKIE_ALLOW_TEXTS:
            try:
                for btn in self.driver.find_elements(
                    By.XPATH, f"//button[contains(.,'{text}')]"
                ):
                    if btn.is_displayed():
                        self._safe_click(btn)
                        time.sleep(0.8)
                        break
            except Exception:
                pass

        for text in LOGIN_WALL_CLOSE + DISMISS_POPUP_TEXTS:
            try:
                for btn in self.driver.find_elements(
                    By.XPATH,
                    f"//*[@role='button' and contains(.,'{text}')] | //button[contains(.,'{text}')]",
                ):
                    if btn.is_displayed():
                        self._safe_click(btn)
                        time.sleep(0.5)
            except Exception:
                pass

        try:
            ActionChains(self.driver).send_keys(Keys.ESCAPE).perform()
        except Exception:
            pass

    def _try_switch_to_all_comments(self):
        """Click sort dropdown and select All comments."""
        try:
            sort_btns = self.driver.find_elements(
                By.XPATH,
                "//*[@role='button'][contains(.,'Most relevant') or contains(.,'All comments') "
                "or contains(.,'Top comments') or contains(.,'Piu rilevanti') "
                "or contains(.,'Plus pertinents')]",
            )
            for btn in sort_btns:
                if btn.is_displayed():
                    self._safe_click(btn)
                    time.sleep(1.5)
                    for opt_text in SORT_ALL_TEXTS:
                        for opt in self.driver.find_elements(
                            By.XPATH,
                            f"//*[@role='menuitem'][contains(.,'{opt_text}')] "
                            f"| //*[@role='option'][contains(.,'{opt_text}')]",
                        ):
                            if opt.is_displayed():
                                self._safe_click(opt)
                                time.sleep(2)
                                print("Sorted to: All comments")
                                return
                    break
        except Exception:
            pass

    def _expand_see_more(self) -> int:
        """Click all See more links to expand truncated comment text."""
        expanded = 0
        for text in SEE_MORE_TEXTS:
            elems = self.driver.find_elements(
                By.XPATH,
                f"//*[@role='button'][.='{text}'] "
                f"| //div[@role='button'][contains(.,'{text}')] "
                f"| //span[@role='button'][contains(.,'{text}')]",
            )
            for el in elems:
                try:
                    if el.is_displayed():
                        self._safe_click(el)
                        expanded += 1
                        time.sleep(0.25)
                except Exception:
                    pass
        if expanded:
            print(f"  Expanded {expanded} truncated sections")
        return expanded

    def _expand_view_more_comments(self, per_pass_limit: int = 8) -> int:
        """Click View more comments buttons, respecting global cap."""
        total = 0
        stall = 0
        while stall < 3:
            if self._total_load_more_clicks >= self.max_load_more_clicks:
                print(f"  Reached max_load_more_clicks ({self.max_load_more_clicks}) — stopping")
                break
            if total >= per_pass_limit:
                break
            clicked = 0
            for text in VIEW_MORE_COMMENTS_TEXTS:
                for el in self.driver.find_elements(
                    By.XPATH,
                    f"//*[@role='button'][contains(.,'{text}')] "
                    f"| //a[contains(.,'{text}')]",
                ):
                    try:
                        if el.is_displayed():
                            self._safe_click(el)
                            clicked += 1
                            total += 1
                            self._total_load_more_clicks += 1
                            time.sleep(self.scroll_pause)
                            if total >= per_pass_limit:
                                break
                            if self._total_load_more_clicks >= self.max_load_more_clicks:
                                break
                    except Exception:
                        pass
                if total >= per_pass_limit:
                    break
            stall = 0 if clicked else stall + 1
            if clicked:
                print(f"  Loaded more comments (clicks this session: {self._total_load_more_clicks})")
        return total

    def _expand_view_more_replies(self) -> int:
        """Click View X more replies buttons, capped to avoid browser overload."""
        total = 0
        for text in VIEW_MORE_REPLIES_TEXTS:
            if total >= self.max_reply_expansions:
                break
            for el in self.driver.find_elements(
                By.XPATH,
                f"//*[@role='button'][contains(.,'{text}')] "
                f"| //span[@role='button'][contains(.,'{text}')]",
            ):
                try:
                    if el.is_displayed():
                        self._safe_click(el)
                        total += 1
                        time.sleep(0.6)
                        if total >= self.max_reply_expansions:
                            break
                except Exception:
                    pass
        if total:
            print(f"  Expanded {total} reply threads")
        return total

    # ------------------------------------------------------------------
    # Scrolling
    # ------------------------------------------------------------------

    def _scroll_to_load_comments(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        scrolls = 0
        no_change = 0

        while scrolls < self.max_scrolls and no_change < 3:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(self.scroll_pause)
            # Limit clicks per scroll pass to avoid DOM overload
            self._expand_view_more_comments(per_pass_limit=5)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            no_change = 0 if new_height != last_height else no_change + 1
            last_height = new_height
            scrolls += 1
            print(f"  Scroll {scrolls}/{self.max_scrolls}")
            if self._total_load_more_clicks >= self.max_load_more_clicks:
                print("  Load-more cap reached — stopping scroll")
                break

    # ------------------------------------------------------------------
    # Comment element extraction
    # ------------------------------------------------------------------

    def _clean_text(self, el) -> str:
        try:
            raw = el.text.strip()
            for sm in SEE_MORE_TEXTS:
                if raw.endswith(sm):
                    raw = raw[: -len(sm)].strip()
            return raw
        except StaleElementReferenceException:
            return ""

    # Time suffixes that get appended to author names in article text
    _TIME_SUFFIX_RE = re.compile(
        r"\s+(?:\d+\s+(?:second|minute|hour|day|week|month|year)s?\s+ago"
        r"|yesterday|just now|\d{1,2}[:/]\d{2}|about an? \w+).*$",
        re.IGNORECASE,
    )

    def _strip_time_suffix(self, name: str) -> str:
        """Remove trailing timestamp from a name string."""
        return self._TIME_SUFFIX_RE.sub("", name).strip()

    def _extract_author(self, article_el) -> str:
        try:
            label = article_el.get_attribute("aria-label") or ""
            m = re.search(r"(?:Comment|Reply) by (.+?)(?:\.|$)", label)
            if m:
                return self._strip_time_suffix(m.group(1).strip())
        except Exception:
            pass

        for selector in [
            "a[role='link'] strong",
            "a[role='link'] span[dir='auto']",
            "h2 a", "h3 a",
        ]:
            try:
                el = article_el.find_element(By.CSS_SELECTOR, selector)
                name = self._strip_time_suffix(el.text.strip())
                if name:
                    return name
            except (NoSuchElementException, StaleElementReferenceException):
                pass

        try:
            for link in article_el.find_elements(By.CSS_SELECTOR, "a[role='link']"):
                name = self._strip_time_suffix(link.text.strip())
                if name and len(name) > 1 and "\n" not in name:
                    return name
        except Exception:
            pass

        return ""

    def _extract_text(self, article_el, author: str) -> str:
        candidates = []
        try:
            for div in article_el.find_elements(
                By.CSS_SELECTOR, "div[dir='auto'], span[dir='auto']"
            ):
                t = self._clean_text(div)
                if t and t != author and len(t) > 1:
                    candidates.append(t)
        except Exception:
            pass

        if candidates:
            return max(candidates, key=len)

        try:
            el = article_el.find_element(By.CSS_SELECTOR, "[data-ad-preview='message']")
            return self._clean_text(el)
        except (NoSuchElementException, StaleElementReferenceException):
            pass

        try:
            raw = article_el.text.strip()
            if author and raw.startswith(author):
                raw = raw[len(author) :].strip()
            return raw
        except Exception:
            pass

        return ""

    _TIMESTAMP_RE = re.compile(
        r"^\d+[smhdw]$"  # short: 17h, 2d, 1w, 30m
        r"|\d+\s+(?:second|minute|hour|day|week|month|year)s?\s+ago"
        r"|yesterday|just now|about an? \w+"
        r"|\b(?:January|February|March|April|May|June|July|August"
        r"|September|October|November|December)\b"
        r"|\d{1,2}[/:]\d{2}",
        re.IGNORECASE,
    )

    def _is_valid_timestamp(self, ts: str) -> bool:
        return bool(self._TIMESTAMP_RE.search(ts))

    def _extract_timestamp(self, article_el) -> Optional[str]:
        for selector in [
            "a[href*='?comment_id'] span",
            "a[href*='/comment/'] span",
            "abbr[data-utime]",
            "abbr",
        ]:
            try:
                el = article_el.find_element(By.CSS_SELECTOR, selector)
                ts = (
                    el.get_attribute("title")
                    or el.get_attribute("data-utime")
                    or el.text
                )
                if ts and ts.strip() and self._is_valid_timestamp(ts):
                    return ts.strip()
            except (NoSuchElementException, StaleElementReferenceException):
                pass

        try:
            for link in article_el.find_elements(By.CSS_SELECTOR, "a"):
                label = link.get_attribute("aria-label") or ""
                if self._is_valid_timestamp(label):
                    return label.strip()
                text = link.text or ""
                if self._is_valid_timestamp(text):
                    return text.strip()
        except Exception:
            pass

        return None

    def _extract_likes(self, article_el) -> Optional[int]:
        for selector in [
            "span[aria-label*='reaction']",
            "span[aria-label*='like']",
            "span[aria-label*='Like']",
            "span[aria-label*='reazione']",
            "span[aria-label*='mi piace']",
            "div[aria-label*='reaction']",
        ]:
            try:
                el = article_el.find_element(By.CSS_SELECTOR, selector)
                label = el.get_attribute("aria-label") or ""
                m = re.search(r"(\d[\d,]*)", label)
                if m:
                    return int(m.group(1).replace(",", ""))
                t = el.text.strip()
                if t.isdigit():
                    return int(t)
            except (NoSuchElementException, StaleElementReferenceException):
                pass
        return None

    def _extract_replies_count(self, article_el) -> Optional[int]:
        try:
            for el in article_el.find_elements(
                By.XPATH,
                ".//span[contains(.,'repl') or contains(.,'rispost') or contains(.,'reponse')]",
            ):
                m = re.search(r"(\d+)", el.text)
                if m:
                    return int(m.group(1))
        except Exception:
            pass
        return None

    def _parse_article(self, article_el) -> Optional[Comment]:
        try:
            author = self._extract_author(article_el)
            text = self._extract_text(article_el, author)
            if not text:
                return None
            # Filter noise: skip articles where text is just the author name
            # or a variation with a timestamp
            cleaned = self._strip_time_suffix(text)
            if not cleaned or cleaned == author or cleaned == self._strip_time_suffix(author):
                return None
            # Skip very short fragments that look like timestamps or UI labels
            if len(cleaned) < 3 or self._is_valid_timestamp(cleaned.strip()):
                return None
            return Comment(
                author=author,
                text=cleaned,
                timestamp=self._extract_timestamp(article_el),
                likes=self._extract_likes(article_el),
                replies_count=self._extract_replies_count(article_el),
            )
        except StaleElementReferenceException:
            return None
        except Exception:
            return None

    # ------------------------------------------------------------------
    # Reel-specific helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _is_reel_url(url: str) -> bool:
        return bool(re.search(r"/(reel|reels)/|/share/r/", url))

    def _find_comment_panel(self):
        """Return the scrollable comment panel element for a Reel, or None."""
        selectors = [
            "div[data-pagelet='VideoPageReelsFeedUFI']",
            "div[data-pagelet*='UFI']",
            "div[aria-label='Comment']",
            "div[aria-label='Comments']",
            "div[role='complementary']",
        ]
        for sel in selectors:
            try:
                panels = self.driver.find_elements(By.CSS_SELECTOR, sel)
                for p in panels:
                    if p.is_displayed() and p.size.get('height', 0) > 100:
                        return p
            except Exception:
                pass

        # Fallback: find the tallest scrollable div that contains comment text
        try:
            candidates = self.driver.find_elements(
                By.XPATH,
                "//div[@role='main']//div[contains(@style,'overflow') or "
                "@data-overscroll-x] | //div[contains(@aria-label,'comment')]"
            )
            for c in candidates:
                h = c.size.get('height', 0)
                if h > 200:
                    return c
        except Exception:
            pass
        return None

    def _click_view_more_everywhere(self, panel=None) -> int:
        """Click every visible 'View more comments' / 'View X more replies' button
        found both inside the panel and globally on the page."""
        clicked = 0
        search_texts = VIEW_MORE_COMMENTS_TEXTS + VIEW_MORE_REPLIES_TEXTS
        # Search scopes: panel first, then full page (avoids missing buttons outside panel)
        scopes = []
        if panel:
            try:
                _ = panel.tag_name  # check not stale
                scopes.append(panel)
            except StaleElementReferenceException:
                pass
        scopes.append(self.driver)

        seen_els = set()
        for scope in scopes:
            for text in search_texts:
                if self._total_load_more_clicks >= self.max_load_more_clicks:
                    return clicked
                try:
                    els = scope.find_elements(
                        By.XPATH,
                        f".//*[@role='button'][contains(.,'{text}')] "
                        f"| .//a[contains(.,'{text}')]",
                    )
                    for el in els:
                        try:
                            el_id = el.id
                            if el_id in seen_els:
                                continue
                            seen_els.add(el_id)
                            if el.is_displayed():
                                self._safe_click(el)
                                clicked += 1
                                self._total_load_more_clicks += 1
                                time.sleep(self.scroll_pause)
                                if self._total_load_more_clicks >= self.max_load_more_clicks:
                                    return clicked
                        except StaleElementReferenceException:
                            continue
                        except Exception:
                            continue
                except Exception:
                    pass
        return clicked

    def _scroll_reel_panel(self, panel):
        """Load all reel comments by scrolling the panel AND clicking
        'View more comments' buttons — whichever keeps producing new content."""
        iteration = 0
        no_progress = 0
        # Track progress by article count, not scroll height (height often stays the same)
        last_count = len(self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']"))

        # Re-find panel each iteration to avoid stale references
        def get_panel():
            try:
                _ = panel.tag_name
                return panel
            except StaleElementReferenceException:
                return self._find_comment_panel()

        while iteration < self.max_scrolls and no_progress < 8:
            p = get_panel()

            # 1. Scroll panel to bottom (incremental steps help trigger lazy loading)
            if p:
                try:
                    current_top = self.driver.execute_script("return arguments[0].scrollTop", p)
                    scroll_height = self.driver.execute_script("return arguments[0].scrollHeight", p)
                    step = max(300, scroll_height // 10)
                    new_top = min(current_top + step, scroll_height)
                    self.driver.execute_script("arguments[0].scrollTop = arguments[0];", p)
                    self.driver.execute_script(f"arguments[0].scrollTop = {new_top};", p)
                except Exception:
                    pass

            time.sleep(self.scroll_pause)

            # 2. Click every "View more" button visible
            clicked = self._click_view_more_everywhere(p)

            if clicked:
                time.sleep(self.scroll_pause)  # wait for content to render

            # 3. Measure progress by number of article elements
            new_count = len(self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']"))
            if new_count > last_count or clicked > 0:
                no_progress = 0
                print(f"  Reel scroll {iteration+1}: {new_count} elements (+{new_count-last_count}), clicked {clicked} buttons")
            else:
                no_progress += 1
                print(f"  Reel scroll {iteration+1}: no change ({new_count} elements, stall {no_progress}/8)")

            last_count = new_count
            iteration += 1

            if self._total_load_more_clicks >= self.max_load_more_clicks:
                print(f"  Reached max_load_more_clicks ({self.max_load_more_clicks})")
                break

    def _open_reel_comments(self):
        """Make sure the reel comment panel is open and visible."""
        # Try clicking a Comments button if the panel is collapsed
        for text in ["Comment", "Comments", "Commenta", "Commentaires"]:
            try:
                btns = self.driver.find_elements(
                    By.XPATH,
                    f"//*[@aria-label='{text}'] | //*[@role='button'][@aria-label='{text}']"
                )
                for btn in btns:
                    if btn.is_displayed():
                        self._safe_click(btn)
                        time.sleep(1.5)
                        return
            except Exception:
                pass

    def _extract_reel_comments(self, panel=None) -> List[Comment]:
        """Extract comments from the reel panel (or full page if no panel found)."""
        comments: List[Comment] = []
        seen: Set[str] = set()
        scope = panel if panel else self.driver

        # Expand See more inside panel
        for text in SEE_MORE_TEXTS:
            try:
                for el in scope.find_elements(
                    By.XPATH, f".//*[@role='button'][.='{text}']"
                ):
                    if el.is_displayed():
                        self._safe_click(el)
                        time.sleep(0.2)
            except Exception:
                pass

        # Try standard article elements first
        articles = scope.find_elements(By.CSS_SELECTOR, "div[role='article']")

        # If none, look for comment blocks by structure
        if not articles:
            articles = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")

        print(f"  Found {len(articles)} comment elements")

        for article in articles:
            try:
                comment = self._parse_article(article)
                if comment and comment.text:
                    fp = comment.fingerprint()
                    if fp not in seen:
                        seen.add(fp)
                        comments.append(comment)
            except StaleElementReferenceException:
                continue
            except Exception:
                continue

        return comments

    # ------------------------------------------------------------------
    # Main orchestration
    # ------------------------------------------------------------------

    def _login(self, email: str, password: str):
        try:
            email_el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "email"))
            )
            pass_el = self.driver.find_element(By.ID, "pass")
            email_el.clear()
            email_el.send_keys(email)
            pass_el.clear()
            pass_el.send_keys(password)
            pass_el.send_keys(Keys.RETURN)
            time.sleep(6)
            print("Login submitted")
        except TimeoutException:
            print("No login form found — may already be logged in or post is public")

    def scrape_comments(
        self,
        post_url: str,
        login_email: Optional[str] = None,
        login_password: Optional[str] = None,
        checkpoint_dir: str = "outputs",
    ) -> List[Comment]:
        """Scrape all comments (and replies) from a Facebook post or reel.

        Uses rolling batched DOM collection — harvests visible comments every
        scroll step so no comments are lost to Facebook's virtualised list.
        Progress is auto-saved every 50 comments so a crash won't lose work;
        on the next run the checkpoint is automatically resumed.
        Falls back to mbasic if nothing is found.
        """
        if not self.driver:
            self._init_driver()

        if login_email and login_password:
            print("Logging in...")
            self.driver.get("https://www.facebook.com/login")
            time.sleep(3)
            self._login(login_email, login_password)

        # Compute a per-URL checkpoint path
        ckpt = self._make_checkpoint_path(post_url, checkpoint_dir)

        # ---- Primary path: batched rolling DOM collector ----
        try:
            comments = self._scrape_batched(post_url, checkpoint_path=ckpt)
            # Clean finish — remove checkpoint
            self._clear_checkpoint(ckpt)
        except Exception as e:
            print(f"  Batched scrape error: {e}")
            # Save whatever we managed to collect before the crash
            if self._all_comments:
                self._save_checkpoint(ckpt, post_url)
                print(f"  [checkpoint] Crash-saved {len(self._all_comments)} comments → {ckpt}")
                print(f"  Re-run the script with the same URL to resume from this checkpoint.")
            comments = list(self._all_comments.values())

        # ---- Last resort: mbasic ----
        if len(comments) <= 2:
            print(f"  Only {len(comments)} found — trying mbasic.facebook.com...")
            try:
                mbasic = self._scrape_mbasic(post_url, login_email, login_password)
                if len(mbasic) > len(comments):
                    print(f"  mbasic returned {len(mbasic)} — using that")
                    comments = mbasic
            except Exception as e:
                print(f"  mbasic failed: {e}")

        print(f"Extracted {len(comments)} total comments")
        return comments

    def _scrape_dom(self, post_url: str) -> List[Comment]:
        """Legacy DOM-based scrape (slow but reliable fallback)."""
        print(f"DOM scrape: {post_url}")
        self._interceptor_injected = False
        self.driver.get(post_url)
        wait_secs = 7 if self._is_reel_url(post_url) else 4
        time.sleep(wait_secs)
        self._dismiss_overlays()
        time.sleep(1)

        comments: List[Comment] = []
        seen: Set[str] = set()

        try:
            if self._is_reel_url(post_url):
                self._open_reel_comments()
                time.sleep(1.5)
                panel = self._find_comment_panel()
                if panel:
                    self._scroll_reel_panel(panel)
                else:
                    self._scroll_to_load_comments()
            else:
                self._try_switch_to_all_comments()
                self._scroll_to_load_comments()
                if self.expand_replies:
                    self._expand_view_more_replies()

            time.sleep(1)
            self._expand_see_more()
            time.sleep(1)

            all_articles = self.driver.find_elements(By.CSS_SELECTOR, "div[role='article']")
            print(f"  Found {len(all_articles)} article elements")
            for article in all_articles:
                try:
                    c = self._parse_article(article)
                    if c and c.text:
                        fp = c.fingerprint()
                        if fp not in seen:
                            seen.add(fp)
                            comments.append(c)
                except StaleElementReferenceException:
                    continue
                except Exception:
                    continue
        except Exception as e:
            err = str(e)
            if "invalid session" not in err and "disconnected" not in err:
                print(f"  DOM scrape error: {e}")

        return comments

    # ------------------------------------------------------------------
    # mbasic.facebook.com fallback
    # ------------------------------------------------------------------

    def _scrape_mbasic(
        self,
        post_url: str,
        login_email: Optional[str] = None,
        login_password: Optional[str] = None,
    ) -> List[Comment]:
        mobile_url = re.sub(
            r"https?://(www\.)?facebook\.com",
            "https://mbasic.facebook.com",
            post_url,
        )
        try:
            self.driver.get(mobile_url)
            time.sleep(3)

            if login_email and login_password:
                try:
                    email_el = self.driver.find_element(By.NAME, "email")
                    pass_el = self.driver.find_element(By.NAME, "pass")
                    email_el.send_keys(login_email)
                    pass_el.send_keys(login_password)
                    pass_el.send_keys(Keys.RETURN)
                    time.sleep(4)
                    self.driver.get(mobile_url)
                    time.sleep(3)
                except NoSuchElementException:
                    pass

            # Page through all comments
            for _ in range(self.max_scrolls // 5):
                try:
                    see_more = self.driver.find_element(
                        By.XPATH,
                        "//a[contains(.,'See More Comments') or contains(.,'More Comments') "
                        "or contains(.,'piu commenti') or contains(.,'piu Commenti')]",
                    )
                    self._safe_click(see_more)
                    time.sleep(2)
                except NoSuchElementException:
                    break

            comments: List[Comment] = []
            seen: Set[str] = set()

            containers = self.driver.find_elements(
                By.XPATH, "//div[contains(@id,'comment_')]"
            )
            if not containers:
                containers = self.driver.find_elements(By.XPATH, "//div[h3]")

            for container in containers:
                try:
                    author = ""
                    try:
                        h = container.find_element(By.XPATH, ".//h3 | .//h2 | .//strong")
                        author = h.text.strip()
                    except NoSuchElementException:
                        pass

                    text = ""
                    for d in container.find_elements(By.XPATH, ".//div | .//p"):
                        t = d.text.strip()
                        if t and t != author and len(t) > 2:
                            text = t
                            break

                    if not text:
                        continue

                    c = Comment(author=author, text=text)
                    fp = c.fingerprint()
                    if fp not in seen:
                        seen.add(fp)
                        comments.append(c)
                except StaleElementReferenceException:
                    continue

            return comments
        except Exception as e:
            print(f"  mbasic scrape failed: {e}")
            return []

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
            "exported_at": datetime.now().isoformat(),
            "total_comments": len(comments),
            "comments": [c.to_dict() for c in comments],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print(f"Exported {len(comments)} comments to {filepath}")

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

def quick_scrape(url: str, output: str = "comments.csv", headless: bool = True) -> List[Comment]:
    with FacebookCommentScraper(headless=headless) as scraper:
        comments = scraper.scrape_comments(url)
        scraper.export_to_csv(comments, output)
        return comments


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python scraper.py <facebook_post_url> [output.csv]")
        sys.exit(1)
    url = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else "comments.csv"
    comments = quick_scrape(url, output, headless=False)
    print(f"\nDone -- {len(comments)} comments saved to {output}")
