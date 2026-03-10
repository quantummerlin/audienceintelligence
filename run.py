"""
Simple launcher — paste a Facebook URL and get all comments exported automatically.
Run with: python run.py
"""

import os
import re
import sys
from datetime import datetime

# Make sure the package is importable even if not installed
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fb_comment_exporter.scraper import FacebookCommentScraper

# Persistent Chrome profile stored next to this script
CHROME_PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")


def sanitise_filename(url: str) -> str:
    """Turn a URL into a safe filename fragment."""
    slug = re.sub(r"[^a-zA-Z0-9]", "_", url)
    return slug[:60].strip("_")


def ensure_logged_in():
    """On first run, open Facebook so the user can log in and save the session."""
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    try:
        from webdriver_manager.chrome import ChromeDriverManager
        use_wdm = True
    except ImportError:
        use_wdm = False

    first_run = not os.path.exists(CHROME_PROFILE_DIR)

    options = Options()
    options.add_argument(f"--user-data-dir={CHROME_PROFILE_DIR}")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("useAutomationExtension", False)
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--window-size=1280,800")

    if use_wdm:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    else:
        driver = webdriver.Chrome(options=options)

    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

    if first_run:
        print()
        print("FIRST-TIME SETUP: Log in to Facebook in the browser that just opened.")
        print("Once you are fully logged in, come back here and press Enter.")
        driver.get("https://www.facebook.com/login")
    else:
        # Just verify we're still logged in
        driver.get("https://www.facebook.com/")

    driver.minimize_window()
    input("Press Enter once you are logged in to Facebook... ")

    # Check if actually logged in
    current = driver.current_url
    logged_in = "login" not in current and "facebook.com" in current
    driver.quit()

    if not logged_in and first_run:
        print("Could not confirm login \u2014 will try scraping anyway.")
    elif logged_in:
        print("Login confirmed \u2013 session saved.")

    return logged_in


def main():
    print("=" * 60)
    print("  Facebook Comment Exporter")
    print("=" * 60)
    print()

    # Ensure we have a saved Facebook session
    ensure_logged_in()
    print()

    url = input("Paste Facebook URL (post or reel): ").strip()
    if not url:
        print("No URL entered. Exiting.")
        return

    os.makedirs("outputs", exist_ok=True)

    # Check whether a crash checkpoint exists for this URL
    ckpt = FacebookCommentScraper._make_checkpoint_path(url, "outputs")
    if os.path.exists(ckpt):
        import json as _json
        try:
            with open(ckpt) as _f:
                _d = _json.load(_f)
            _n = _d.get("count", 0)
            print()
            print(f"  [RESUME] Found a saved checkpoint with {_n} comments from a previous run.")
            print(f"  File: {ckpt}")
            print(f"  It will be loaded automatically — you won't lose any progress.")
        except Exception:
            pass

    # Output filename based on timestamp
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = sanitise_filename(url)
    output_csv = os.path.join("outputs", f"comments_{ts}_{slug[:30]}.csv")
    output_json = os.path.join("outputs", f"comments_{ts}_{slug[:30]}.json")

    print()
    print(f"Output CSV   : {output_csv}")
    print(f"Output JSON  : {output_json}")
    print(f"Checkpoint   : {ckpt}  (auto-saved every 50 comments)")
    print()
    print("Opening Chrome... (do NOT close it)")
    print("-" * 60)

    comments = []
    try:
        with FacebookCommentScraper(
            headless=False,
            scroll_pause=2.0,
            max_scrolls=500,           # up to 500 scroll iterations
            max_load_more_clicks=500,  # up to 500 "View more" clicks (~1700+ comments)
            max_reply_expansions=50,
            expand_replies=True,
            chrome_profile_dir=CHROME_PROFILE_DIR,
        ) as scraper:
            comments = scraper.scrape_comments(url, checkpoint_dir="outputs")

            if comments:
                scraper.export_to_csv(comments, output_csv)
                scraper.export_to_json(comments, output_json)

    except Exception as e:
        print(f"\n  Fatal error: {e}")
        # If we have a partial checkpoint, load and export it now
        if os.path.exists(ckpt):
            import json as _json
            try:
                from fb_comment_exporter.scraper import Comment
                with open(ckpt, encoding="utf-8") as _f:
                    _d = _json.load(_f)
                from dataclasses import fields as _fields
                _field_names = {f.name for f in _fields(Comment)}
                comments = [
                    Comment(**{k: v for k, v in c.items() if k in _field_names})
                    for c in _d.get("comments", [])
                ]
                if comments:
                    FacebookCommentScraper.export_to_csv(comments, output_csv)
                    FacebookCommentScraper.export_to_json(comments, output_json)
                    print(f"\n  Exported {len(comments)} comments from crash checkpoint.")
            except Exception as e2:
                print(f"  Could not export checkpoint: {e2}")

    if not comments:
        print("\nNo comments found. The post may be private or require login.")
        if os.path.exists(ckpt):
            print(f"  Checkpoint still saved at: {ckpt}")
            print(f"  Re-run this script with the same URL to try again.")
        return

    print()
    print("=" * 60)
    print(f"  Done!  {len(comments)} comments exported.")
    print(f"  CSV  -> {os.path.abspath(output_csv)}")
    print(f"  JSON -> {os.path.abspath(output_json)}")
    print("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nCancelled.")
