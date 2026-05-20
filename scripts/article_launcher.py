#!/usr/bin/env python3
"""
article_launcher.py — Aether Intel Article Launcher

Auto-updates the Aether Intel homepage when a new article is published:
  1. Converts hero PNG -> WebP at quality=82 (93-97% size reduction)
  2. Prepends the article to the homepage slideshow (index.html)
  3. Adds the article headline to the news ticker (/data/ticker.json)
  4. Prepends an article card to the "Latest AI News" grid (index.html)
  5. Returns JSON with updated file contents ready for GITHUB_COMMIT_MULTIPLE_FILES

USAGE
-----
Called with a JSON config on stdin or via --config argument:

  python3 article_launcher.py --config '{
    "title":      "The Ghost Workers Powering ChatGPT",
    "url":        "/articles/28-chatgpt-ghost-workers-hidden-labor.html",
    "desc":       "86% struggle financially. Median pay under $23K.",
    "hero":       "/images/articles/28-chatgpt-ghost-workers-hidden-labor-hero.webp",
    "badge":      "badge-ethics",
    "cat":        "Human Cost",
    "ticker_text":"86% of ChatGPT data workers struggle financially",
    "ticker_tag": "warning",
    "png_path":   "/agent/stored_files/abc123_hero.png"
  }'

  Or pipe JSON on stdin:
  echo '{...}' | python3 article_launcher.py

CONFIG FIELDS
-------------
  title        Article headline (string, required)
  url          Repo-relative URL  e.g. /articles/28-slug.html  (required)
  desc         Short teaser sentence shown in cards / slides  (required)
  hero         Repo path for the WebP hero image  e.g. /images/articles/28-slug.webp  (required)
  badge        CSS class -- see BADGE OPTIONS below  (required)
  cat          Category label shown in the badge  (required)
  ticker_text  Short headline for the news ticker  (required)
  ticker_tag   Optional emoji prefix for the ticker item  (optional)
  png_path     Local path to the PNG from FetchStoredFile.  When provided the
               launcher converts it to WebP automatically and includes
               webp_base64 in the output JSON.  (optional)

BADGE OPTIONS
-------------
  badge-agents   -> purple, for AI agent/model articles
  badge-dev      -> blue, for developer/security/tech articles
  badge-business -> green, for business/creator/money articles
  badge-ethics   -> red/orange, for society/ethics/labor articles

IMAGE FORMAT -- AUTOMATIC WEBP CONVERSION
------------------------------------------
Pass png_path in the config to trigger automatic conversion:

  config["png_path"] = "/agent/stored_files/abc123_hero.png"
  config["hero"]     = "/images/articles/28-slug.webp"   # target repo path

The launcher calls convert_to_webp.py (quality=82, method=6) and adds
webp_base64 to the output JSON ready for GITHUB_COMMIT_MULTIPLE_FILES:

  {
    "path":     "images/articles/28-slug.webp",
    "content":  output["webp_base64"],
    "encoding": "base64"
  }

Benchmark: PNG ~1,400 KB -> WebP q=82 ~90 KB (93-97% smaller).
Homepage slideshow loads 8 slides: 11 MB PNG -> 0.7 MB WebP.

OUTPUT
------
Prints JSON with:
  {
    "index_html":         "<updated index.html content>",
    "ticker_json":        "<updated ticker.json content>",
    "slides_count":       8,
    "ticker_count":       12,
    "grid_count":         24,
    "dropped_slide":      "{ old last slide data }",
    "webp_base64":        "<base64 WebP for commit>",   # only when png_path provided
    "webp_bytes":         87432,                         # only when png_path provided
    "hero_reduction_pct": 94.1                           # only when png_path provided
  }

ENVIRONMENT
-----------
  GITHUB_TOKEN   Optional -- avoids rate limiting when fetching from GitHub

WHAT GETS UPDATED
-----------------
  index.html:
    - New <div class="hero-slide-img"> prepended to slides block
    - Old last slide removed (keeps 8 total)
    - Dot buttons rebuilt for 8 slides (slide 1 = active)
    - var SLIDES_DATA entry prepended, last entry removed
    - New article-card prepended to <div class="article-grid">
    - Grid trimmed to 24 cards max

  data/ticker.json:
    - New item prepended to "items" array
    - Trimmed to 12 items max
    - "updated" field set to today
"""

import os
import re
import sys
import json
import base64
import datetime
import subprocess
import urllib.request
import urllib.error
import argparse
from pathlib import Path

OWNER  = "quantummerlin"
REPO   = "audienceintelligence"
BRANCH = "main"
BASE_RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}"
MAX_SLIDES = 8
MAX_TICKER = 12
MAX_GRID   = 24

# Path to the WebP converter script (sibling skill in the agent workspace)
CONVERTER_SCRIPT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "aether-intel-webp-converter",
    "convert_to_webp.py",
)


# -- GitHub helpers ------------------------------------------------------------

def gh_headers():
    token = os.environ.get("GITHUB_TOKEN", "")
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def fetch_raw(path):
    """Fetch current file content via GitHub Contents API.

    The raw.githubusercontent.com CDN can serve stale content for several
    minutes after a commit, which previously caused this launcher to fetch an
    old index.html and clobber recent edits when re-committing. The Contents
    API returns the canonical bytes via blob SHA, no CDN cache layer.
    """
    api_url = (
        f"https://api.github.com/repos/{OWNER}/{REPO}/contents/"
        f"{path.lstrip('/')}?ref={BRANCH}"
    )
    req = urllib.request.Request(api_url, headers=gh_headers())
    with urllib.request.urlopen(req, timeout=15) as r:
        payload = json.loads(r.read().decode("utf-8"))
    raw_b64 = payload.get("content", "").replace("\n", "")
    return base64.b64decode(raw_b64).decode("utf-8", errors="replace")


# -- Hero image WebP conversion ------------------------------------------------

def convert_hero_png(config):
    """
    Convert the PNG at config["png_path"] to WebP using convert_to_webp.py.

    Returns a dict with keys:
        webp_base64        (str)   base64-encoded WebP content for GitHub commit
        webp_bytes         (int)   size of the WebP in bytes
        hero_reduction_pct (float) percentage size reduction vs source PNG

    Raises RuntimeError on any failure.
    """
    png_path = config["png_path"]

    if not Path(png_path).exists():
        raise RuntimeError(f"png_path not found: {png_path}")

    converter = Path(CONVERTER_SCRIPT).resolve()
    if not converter.exists():
        raise RuntimeError(
            f"convert_to_webp.py not found at {converter}. "
            "Fetch the aether-intel-webp-converter skill scripts first."
        )

    result_json = subprocess.check_output(
        [sys.executable, str(converter), png_path],
        stderr=subprocess.PIPE,
    )
    result = json.loads(result_json)

    if not result.get("success"):
        raise RuntimeError(f"WebP conversion failed: {result.get('error', 'unknown error')}")

    return {
        "webp_base64":        result["base64_content"],
        "webp_bytes":         result["webp_bytes"],
        "hero_reduction_pct": result["reduction_pct"],
    }


# -- Ticker updater ------------------------------------------------------------

def update_ticker(ticker_json_str, config):
    """Prepend new article item to ticker, keep MAX_TICKER items."""
    data = json.loads(ticker_json_str)
    items = data.get("items", [])

    new_item = {"text": config["ticker_text"]}
    if config.get("ticker_tag"):
        new_item["tag"] = config["ticker_tag"]

    items.insert(0, new_item)
    # Keep to max
    items = items[:MAX_TICKER]

    data["items"] = items
    data["updated"] = datetime.date.today().isoformat()

    return json.dumps(data, indent=2, ensure_ascii=False)


# -- Slideshow updater ---------------------------------------------------------

def parse_slides_data(html):
    """
    Extract the var SLIDES_DATA array as a list of raw entry strings.
    Returns (array_match_span, list_of_entry_strings).
    """
    # Match the full array block
    m = re.search(
        r'((?:var|const|let)\s+SLIDES_DATA\s*=\s*\[)(.*?)(\];)',
        html, re.DOTALL
    )
    if not m:
        raise ValueError("Could not find SLIDES_DATA array in index.html")

    array_body = m.group(2)
    span = m.span()

    # Split into individual { ... } entries using brace counting
    entries = []
    depth = 0
    start = None
    for i, ch in enumerate(array_body):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                entries.append(array_body[start:i+1])
                start = None

    return span, entries, m.group(1), m.group(3)


def build_slides_data_entry(config):
    """Build a SLIDES_DATA JS object string for the new article."""
    title = config["title"].replace('"', '\\"')
    desc  = config["desc"].replace('"', '\\"')
    # Encode & in cat/badge as &amp; for consistency with existing entries
    cat   = config["cat"].replace("&", "&amp;")
    badge = config["badge"]
    href  = config["url"]

    return (
        f'{{\n'
        f'        badge: "{badge}",\n'
        f'        cat:   "{cat}",\n'
        f'        title: "{title}",\n'
        f'        desc:  "{desc}",\n'
        f'        href:  "{href}"\n'
        f'      }}'
    )


def update_slides_data(html, config):
    """
    Prepend new SLIDES_DATA entry, drop the oldest (last) entry.
    Returns (updated_html, dropped_entry_string).
    """
    span, entries, open_str, close_str = parse_slides_data(html)
    if len(entries) == 0:
        raise ValueError("SLIDES_DATA has no entries")

    dropped = entries[-1]  # oldest slide
    new_entry = build_slides_data_entry(config)
    entries = [new_entry] + entries[:-1]  # prepend new, drop last

    # Rebuild the array body
    joined = ",\n      ".join(entries)
    new_block = f"{open_str}\n      {joined}\n    {close_str}"

    updated = html[:span[0]] + new_block + html[span[1]:]
    return updated, dropped


def update_slide_divs(html, config):
    """
    Prepend new hero-slide-img div, remove the last one.
    Returns updated_html.
    """
    hero_img = config["hero"]
    new_div = (
        f'<div class="hero-slide-img" '
        f'style="background-image:url(\'{hero_img}\');background-color:#0d1020;">'
        f'</div>'
    )

    # Find all hero-slide-img divs (handles both empty and with-content variants)
    # Pattern matches opening tag through the matching closing </div>
    # First try simple self-closing / empty pattern
    pattern_empty = r'<div class="hero-slide-img"[^>]*></div>'
    empty_matches = list(re.finditer(pattern_empty, html))

    if len(empty_matches) >= MAX_SLIDES:
        # All divs are empty -- simple replacement
        # Find first and last match positions
        first_start = empty_matches[0].start()
        last_end    = empty_matches[-1].end()

        # Rebuild: new + first (MAX_SLIDES-1) existing
        kept = empty_matches[:MAX_SLIDES - 1]
        kept_html = "\n        ".join(m.group(0) for m in kept)
        block = new_div + "\n        " + kept_html

        updated = html[:first_start] + block + html[last_end:]
        return updated

    # Divs have inner content -- use brace-depth style scan on the raw HTML
    # Find the first <div class="hero-slide-img" position
    first_pos = html.find('<div class="hero-slide-img"')
    if first_pos == -1:
        raise ValueError("No hero-slide-img divs found in index.html")

    # Collect all slide div spans via tag depth
    div_spans = []
    search_start = first_pos
    for _ in range(MAX_SLIDES + 5):  # guard against infinite loop
        open_pos = html.find('<div class="hero-slide-img"', search_start)
        if open_pos == -1:
            break
        # Find the matching </div>
        depth = 0
        i = open_pos
        close_pos = -1
        while i < len(html):
            if html[i:i+4] == '<div':
                depth += 1
                i += 4
            elif html[i:i+6] == '</div>':
                depth -= 1
                if depth == 0:
                    close_pos = i + 6
                    break
                i += 6
            else:
                i += 1
        if close_pos == -1:
            break
        div_spans.append((open_pos, close_pos))
        search_start = close_pos

    if len(div_spans) == 0:
        raise ValueError("Could not parse hero-slide-img divs")

    # Keep first (MAX_SLIDES-1) divs
    kept_divs = [html[s:e] for s, e in div_spans[:MAX_SLIDES - 1]]
    sep = "\n        "
    block = new_div + sep + sep.join(kept_divs)

    first_start = div_spans[0][0]
    last_end    = div_spans[-1][1]
    updated = html[:first_start] + block + html[last_end:]
    return updated


def rebuild_dot_buttons(html):
    """
    Replace the full set of hero-dot buttons with a clean 8-button set.
    Slide 1 gets class="hero-dot active", slides 2-8 get class="hero-dot".
    """
    # Build replacement block
    dots = []
    dots.append('<button class="hero-dot active" aria-label="Slide 1"></button>')
    for n in range(2, MAX_SLIDES + 1):
        dots.append(f'<button class="hero-dot" aria-label="Slide {n}"></button>')

    new_dots_html = "\n          ".join(dots)

    # Find and replace the existing dot buttons block
    # Match from the first hero-dot button to the last one
    first_dot = re.search(r'<button[^>]+class="hero-dot[^"]*"[^>]*></button>', html)
    if not first_dot:
        raise ValueError("No hero-dot buttons found in index.html")

    # Find all dot buttons
    all_dots = list(re.finditer(r'<button[^>]+class="hero-dot[^"]*"[^>]*></button>', html))
    if not all_dots:
        raise ValueError("No hero-dot buttons found")

    first_start = all_dots[0].start()
    last_end    = all_dots[-1].end()

    # Get the indentation from the first button
    # Find whitespace before the first button on its line
    line_start = html.rfind('\n', 0, first_start) + 1
    indent = html[line_start:first_start]

    new_block = (f"\n{indent}").join(dots)
    updated = html[:first_start] + new_block + html[last_end:]
    return updated


# -- Article-grid updater ------------------------------------------------------

def build_article_card(config):
    """Build a single article-card <a> HTML string for the Latest AI News grid."""
    url   = config["url"]
    hero  = config["hero"]
    title = config["title"]
    desc  = config["desc"]
    badge = config["badge"]
    cat   = config["cat"]
    # Escape double-quotes only in attribute positions
    alt   = title.replace('"', '&quot;')
    title_attr = title.replace('"', '&quot;')
    onerror = (
        "this.style.background='linear-gradient(135deg,rgba(129,140,248,0.15),"
        "rgba(34,211,238,0.05))';this.removeAttribute('src')"
    )
    return (
        f'<a href="{url}" class="article-card">\n'
        f'          <div class="article-card-img-wrap">\n'
        f'            <img src="{hero}" alt="{alt}" class="article-card-img" loading="lazy" onerror="{onerror}">\n'
        f'          </div>\n'
        f'          <div class="article-card-body">\n'
        f'            <span class="badge {badge}">{cat}</span>\n'
        f'            <h3 class="article-card-title">{title_attr}</h3>\n'
        f'            <p class="article-card-desc">{desc}</p>\n'
        f'          </div>\n'
        f'        </a>'
    )


def update_article_grid(html, config):
    """
    Prepend a new article card to <div class="article-grid"> and trim to MAX_GRID cards.
    Returns (updated_html, grid_card_count).
    """
    GRID_OPEN   = '<div class="article-grid">'
    CARD_MARKER = 'class="article-card"'

    grid_pos = html.find(GRID_OPEN)
    if grid_pos == -1:
        raise ValueError('Could not find <div class="article-grid"> in index.html')

    after_open = grid_pos + len(GRID_OPEN)
    new_card   = build_article_card(config)

    # Prepend new card immediately after the opening tag
    html = html[:after_open] + '\n          ' + new_card + '\n' + html[after_open:]

    # Re-find the grid opening position (offset changed after insertion)
    grid_pos  = html.find(GRID_OPEN)
    scan_from = grid_pos + len(GRID_OPEN)

    # Walk forward with div-depth tracking to find the closing </div> of the grid
    depth = 1
    i     = scan_from
    grid_close = -1
    while i < len(html):
        if html[i:i+4] == '<div':
            depth += 1
            i += 4
        elif html[i:i+6] == '</div>':
            depth -= 1
            if depth == 0:
                grid_close = i
                break
            i += 6
        else:
            i += 1

    if grid_close == -1:
        raise ValueError('Could not locate closing </div> for article-grid')

    # Collect all article-card start positions within the grid
    card_starts = []
    search = scan_from
    while search < grid_close:
        marker = html.find(CARD_MARKER, search)
        if marker == -1 or marker >= grid_close:
            break
        # Walk back to the <a that owns this class attribute
        a_start = html.rfind('<a ', 0, marker)
        if a_start not in card_starts:
            card_starts.append(a_start)
        search = marker + len(CARD_MARKER)

    if len(card_starts) > MAX_GRID:
        # Trim: everything from the (MAX_GRID)th card onward gets removed
        cut_pos  = card_starts[MAX_GRID]
        # Step back to the newline before the unwanted card to keep clean indentation
        last_nl  = html.rfind('\n', scan_from, cut_pos)
        cut_clean = last_nl if last_nl != -1 else cut_pos
        html = html[:cut_clean] + '\n        ' + html[grid_close:]
        card_count = MAX_GRID
    else:
        card_count = len(card_starts)

    return html, card_count


# -- Combined index.html updater -----------------------------------------------

def update_index_html(html, config):
    """Apply all slideshow AND grid updates to index.html. Returns (updated_html, dropped_slide, grid_count)."""
    html, dropped    = update_slides_data(html, config)
    html             = update_slide_divs(html, config)
    html             = rebuild_dot_buttons(html)
    html, grid_count = update_article_grid(html, config)
    return html, dropped, grid_count


# -- Main ----------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Aether Intel Article Launcher")
    parser.add_argument("--config", type=str, help="JSON config string")
    parser.add_argument("--dry-run", action="store_true", help="Print diffs without outputting final JSON")
    args = parser.parse_args()

    # Load config from --config arg or stdin
    if args.config:
        config = json.loads(args.config)
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            print("ERROR: No config provided. Pass --config JSON or pipe JSON on stdin.", file=sys.stderr)
            print(__doc__)
            sys.exit(1)
        config = json.loads(raw)

    # Validate required fields
    required = ["title", "url", "desc", "hero", "badge", "cat", "ticker_text"]
    missing = [f for f in required if f not in config]
    if missing:
        print(f"ERROR: Missing required config fields: {missing}", file=sys.stderr)
        sys.exit(1)

    print("Aether Intel Article Launcher", file=sys.stderr)
    print(f"   Article: {config['title']}", file=sys.stderr)
    print(f"   URL:     {config['url']}", file=sys.stderr)

    # --- Step 1: Convert hero PNG -> WebP (if png_path provided) ---
    webp_result = None
    if config.get("png_path"):
        print(f"\nConverting hero PNG -> WebP…", file=sys.stderr)
        print(f"   Source: {config['png_path']}", file=sys.stderr)
        try:
            webp_result = convert_hero_png(config)
            kb_before = 0
            png_p = Path(config["png_path"])
            if png_p.exists():
                kb_before = png_p.stat().st_size // 1024
            kb_after = webp_result["webp_bytes"] // 1024
            print(f"   OK  {kb_before} KB PNG -> {kb_after} KB WebP "
                  f"({webp_result['hero_reduction_pct']}% reduction)", file=sys.stderr)
        except Exception as e:
            print(f"   WARNING: WebP conversion failed: {e}", file=sys.stderr)
            print(f"   Continuing without webp_base64 in output.", file=sys.stderr)
            webp_result = None
    else:
        print(f"\n   (no png_path provided -- skipping WebP conversion)", file=sys.stderr)

    # --- Step 2: Fetch current files from GitHub ---
    print("\nFetching current files from GitHub…", file=sys.stderr)
    try:
        index_html = fetch_raw("index.html")
        print(f"   OK  index.html ({len(index_html):,} bytes)", file=sys.stderr)
    except Exception as e:
        print(f"   ERROR: Failed to fetch index.html: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        ticker_json_str = fetch_raw("data/ticker.json")
        print(f"   OK  data/ticker.json ({len(ticker_json_str):,} bytes)", file=sys.stderr)
    except Exception as e:
        print(f"   ERROR: Failed to fetch data/ticker.json: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Step 3: Update ticker ---
    print("\nUpdating ticker…", file=sys.stderr)
    try:
        new_ticker = update_ticker(ticker_json_str, config)
        ticker_data = json.loads(new_ticker)
        print(f"   OK  {len(ticker_data['items'])} items (new item prepended)", file=sys.stderr)
    except Exception as e:
        print(f"   ERROR: Ticker update failed: {e}", file=sys.stderr)
        sys.exit(1)

    # --- Step 4: Update slideshow + article grid ---
    print("\nUpdating slideshow and article grid…", file=sys.stderr)
    try:
        new_index, dropped_slide, grid_count = update_index_html(index_html, config)

        # Verify slideshow counts
        slide_count = len(re.findall(r'class="hero-slide-img"', new_index))
        dot_count   = len(re.findall(r'<button[^>]+class="hero-dot[^"]*"', new_index))
        _, entries, _, _ = parse_slides_data(new_index)
        data_count  = len(entries)

        print(f"   OK  Slides: {slide_count}, Dots: {dot_count}, SLIDES_DATA: {data_count}", file=sys.stderr)
        if slide_count != dot_count or dot_count != data_count or slide_count != MAX_SLIDES:
            print(f"   WARNING: slide counts don't match! Expected all to be {MAX_SLIDES}", file=sys.stderr)

        print(f"   Dropped oldest slide: {dropped_slide[:60].strip()}...", file=sys.stderr)
        print(f"   Article grid: {grid_count} cards (max {MAX_GRID})", file=sys.stderr)
    except Exception as e:
        print(f"   ERROR: Slideshow/grid update failed: {e}", file=sys.stderr)
        import traceback; traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("\n[DRY RUN] Would commit these files:", file=sys.stderr)
        print(f"  - index.html ({len(new_index):,} bytes)", file=sys.stderr)
        print(f"  - data/ticker.json ({len(new_ticker):,} bytes)", file=sys.stderr)
        if webp_result:
            print(f"  - hero image ({webp_result['webp_bytes']:,} bytes WebP)", file=sys.stderr)
        return

    # --- Step 5: Output result JSON for GITHUB_COMMIT_MULTIPLE_FILES ---
    result = {
        "index_html":    new_index,
        "ticker_json":   new_ticker,
        "slides_count":  slide_count,
        "ticker_count":  len(ticker_data["items"]),
        "grid_count":    grid_count,
        "dropped_slide": dropped_slide,
    }
    if webp_result:
        result["webp_base64"]        = webp_result["webp_base64"]
        result["webp_bytes"]         = webp_result["webp_bytes"]
        result["hero_reduction_pct"] = webp_result["hero_reduction_pct"]

    print("\nDone. Output JSON ready for commit.", file=sys.stderr)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
