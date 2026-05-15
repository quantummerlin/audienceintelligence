#!/usr/bin/env python3
"""
skills_launcher.py — Aether Intel Skills Launcher

Auto-updates the Aether Intel Skills page when a new skill is published:
  1. Converts hero PNG -> WebP at quality=82 (93-97% size reduction)
  2. Prepends the skill to the skills.html slideshow (9 slides max)
  3. Adds a skill card to the "Latest Skills" grid (prepend, trim to 24)
  4. Updates data/skills.json with the new skill entry
  5. Returns JSON with updated file contents ready for GITHUB_COMMIT_MULTIPLE_FILES

USAGE
-----
Called with a JSON config on stdin or via --config argument:

  python3 skills_launcher.py --config '{
    "title":   "Prompt Chaining for Complex Tasks",
    "url":     "/skills/prompt-chaining.html",
    "desc":    "Break multi-step problems into sequential prompts.",
    "hero":    "/images/skills/prompt-chaining-hero.webp",
    "badge":   "badge-secondary",
    "cat":     "Prompts",
    "diff":    "Intermediate",
    "time":    "~30 min",
    "why":     "Most prompts fail because you ask too much in one shot.",
    "png_path": "/agent/stored_files/abc123_hero.png"
  }'

CONFIG FIELDS
-------------
  title      Skill title (string, required)
  url        Repo-relative URL  e.g. /skills/prompt-chaining.html  (required)
  desc       Short teaser sentence shown in cards / slides  (required)
  hero       Repo path for the WebP hero image  e.g. /images/skills/slug-hero.webp  (required)
  badge      CSS class -- see BADGE OPTIONS below  (required)
  cat        Category label shown in the badge  (required)
  diff       Difficulty: Beginner | Intermediate | Advanced  (optional, default: Intermediate)
  time       Learning time estimate  (optional, default: ~20 min)
  why        Why-it-matters one-liner for the card  (optional)
  png_path   Local path to the PNG from FetchStoredFile. When provided the
             launcher converts it to WebP automatically and includes
             webp_base64 in the output JSON.  (optional)

BADGE OPTIONS
-------------
  badge-secondary -> grey/default, for general prompting skills
  badge-agents    -> purple, for AI agent/automation skills
  badge-dev       -> blue, for developer/coding/security skills
  badge-business  -> green, for business/monetisation skills
  badge-tools     -> cyan, for tool guides

IMAGE FORMAT -- AUTOMATIC WEBP CONVERSION
------------------------------------------
Pass png_path in the config to trigger automatic conversion:

  config["png_path"] = "/agent/stored_files/abc123_hero.png"
  config["hero"]     = "/images/skills/slug-hero.webp"   # target repo path

Benchmark: PNG ~1,400 KB -> WebP q=82 ~90 KB (93-97% smaller).

OUTPUT
------
Prints JSON with:
  {
    "skills_html":    "<updated skills.html content>",
    "skills_json":    "<updated data/skills.json content>",
    "slides_count":   9,
    "grid_count":     12,
    "dropped_slide":  "{ old last slide data }",
    "webp_base64":    "<base64 WebP for commit>",  # only when png_path provided
    "webp_bytes":     87432,                        # only when png_path provided
    "hero_reduction_pct": 94.1                      # only when png_path provided
  }

ENVIRONMENT
-----------
  GITHUB_TOKEN   Optional -- avoids rate limiting when fetching from GitHub

WHAT GETS UPDATED
-----------------
  skills.html:
    - New <div class="hero-slide-img"> prepended to slides track
    - Old last slide removed (keeps 9 total)
    - Dot buttons rebuilt for 9 slides (slide 1 = active)
    - var SKILLS_SLIDES_DATA entry prepended, last entry removed
    - New skill-card prepended to skills-grid
    - Grid trimmed to 24 cards max

  data/skills.json:
    - New item prepended to "skills" array
    - Trimmed to 50 items max
    - "updated" field set to today
"""

import os
import re
import sys
import json
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
MAX_SLIDES = 9
MAX_GRID   = 24
MAX_SKILLS = 50

# Path to the WebP converter script
CONVERTER_SCRIPT = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "..",
    "aether-intel-webp-converter",
    "convert_to_webp.py",
)


# -- GitHub helpers --------------------------------------------------------

def gh_headers():
    token = os.environ.get("GITHUB_TOKEN", "")
    h = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if token:
        h["Authorization"] = f"Bearer {token}"
    return h

def fetch_raw(path):
    url = f"{BASE_RAW}/{path.lstrip('/')}"
    req = urllib.request.Request(url, headers=gh_headers())
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read().decode("utf-8", errors="replace")


# -- Hero image WebP conversion --------------------------------------------

def convert_hero_png(config):
    """
    Convert the PNG at config["png_path"] to WebP using convert_to_webp.py.

    Returns a dict with keys:
        webp_base64       (str)   base64-encoded WebP content for GitHub commit
        webp_bytes        (int)   size of the WebP in bytes
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


# -- Skills.html slideshow updater -----------------------------------------

def parse_skills_slides_data(html):
    """
    Extract the var SKILLS_SLIDES_DATA array as a list of raw entry strings.
    Returns (span, entries, open_str, close_str).
    """
    m = re.search(
        r'((?:var|const|let)\s+SKILLS_SLIDES_DATA\s*=\s*\[)(.*?)(\];)',
        html, re.DOTALL
    )
    if not m:
        raise ValueError("Could not find SKILLS_SLIDES_DATA array in skills.html")

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


def build_skills_slides_entry(config):
    """Build a SKILLS_SLIDES_DATA JS object string for the new skill."""
    title = config["title"].replace('"', '\\"')
    desc  = config["desc"].replace('"', '\\"')
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


def update_skills_slides_data(html, config):
    """
    Prepend new SKILLS_SLIDES_DATA entry, drop the oldest (last) entry.
    Returns (updated_html, dropped_entry_string).
    """
    span, entries, open_str, close_str = parse_skills_slides_data(html)
    if len(entries) == 0:
        raise ValueError("SKILLS_SLIDES_DATA has no entries")

    dropped = entries[-1]  # oldest slide
    new_entry = build_skills_slides_entry(config)
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

    # Find all hero-slide-img divs (empty pattern only — skills.html uses empty divs)
    pattern_empty = r'<div class="hero-slide-img"[^>]*></div>'
    empty_matches = list(re.finditer(pattern_empty, html))

    if len(empty_matches) == 0:
        raise ValueError("No hero-slide-img divs found in skills.html")

    first_start = empty_matches[0].start()
    last_end    = empty_matches[-1].end()

    # Rebuild: new + first (MAX_SLIDES-1) existing
    kept = empty_matches[:MAX_SLIDES - 1]
    kept_html = "\n        ".join(m.group(0) for m in kept)
    block = new_div + "\n        " + kept_html

    updated = html[:first_start] + block + html[last_end:]
    return updated


def rebuild_dot_buttons(html):
    """
    Replace the full set of hero-dot buttons with a clean MAX_SLIDES-button set.
    Slide 1 gets class="hero-dot active", slides 2-N get class="hero-dot".
    Only operates on the #skillSlideDots container.
    """
    # Find the skillSlideDots container
    dots_container_start = html.find('id="skillSlideDots"')
    if dots_container_start == -1:
        raise ValueError("No skillSlideDots container found in skills.html")

    # Build replacement dots
    dots = []
    dots.append('<button class="hero-dot active" aria-label="Slide 1"></button>')
    for n in range(2, MAX_SLIDES + 1):
        dots.append(f'<button class="hero-dot" aria-label="Slide {n}"></button>')

    # Find the first dot inside the container
    first_dot = re.search(r'<button[^>]+class="hero-dot[^"]*"[^>]*></button>', html[dots_container_start:])
    if not first_dot:
        raise ValueError("No hero-dot buttons found in skillSlideDots")

    all_dots = list(re.finditer(r'<button[^>]+class="hero-dot[^"]*"[^>]*></button>', html[dots_container_start:]))
    if not all_dots:
        raise ValueError("No hero-dot buttons found")

    first_start = dots_container_start + all_dots[0].start()
    last_end    = dots_container_start + all_dots[-1].end()

    # Get the indentation from the first button
    line_start = html.rfind('\n', 0, first_start) + 1
    indent = html[line_start:first_start]

    new_block = (f"\n{indent}").join(dots)
    updated = html[:first_start] + new_block + html[last_end:]
    return updated


# -- Skills card grid updater ----------------------------------------------

def build_skill_card(config):
    """Build a single skill-card <div> HTML string."""
    url   = config["url"]
    title = config["title"]
    desc  = config["desc"]
    badge = config["badge"]
    cat   = config["cat"]
    diff  = config.get("diff", "Intermediate")
    time_ = config.get("time", "~20 min")
    why   = config.get("why", "")
    slug  = url.rstrip('/').split('/')[-1].replace('.html', '')

    diff_cls = f"skill-diff-{diff.lower()}"

    why_html = f'\n            <p class="skill-card-why">{why}</p>' if why else ''

    return (
        f'<div class="skill-card" data-category="{cat.lower()}" data-name="{title.lower()}">\n'
        f'          <div class="skill-card-body">\n'
        f'            <div class="skill-card-meta">\n'
        f'              <span class="badge {badge}">{cat}</span>\n'
        f'              <span class="skill-diff {diff_cls}">{diff}</span>\n'
        f'              <span class="skill-time">{time_}</span>\n'
        f'            </div>\n'
        f'            <h3 class="skill-card-title">{title}</h3>{why_html}\n'
        f'            <p class="skill-card-desc">{desc}</p>\n'
        f'            <div class="skill-card-actions">\n'
        f'              <button class="btn-skill-download" onclick="downloadSkill(\'{slug}\')">\n'
        f'                <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        f'<polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>\n'
        f'                Download Free\n'
        f'              </button>\n'
        f'              <a href="{url}" class="skill-guide-link">Read the Guide →</a>\n'
        f'            </div>\n'
        f'          </div>\n'
        f'        </div>'
    )


def update_skills_grid(html, config):
    """
    Prepend a new skill card to <div class="skills-grid" id="skillsGrid"> and trim to MAX_GRID cards.
    Returns (updated_html, grid_card_count).
    """
    GRID_OPEN   = 'id="skillsGrid">'
    CARD_MARKER = 'class="skill-card'

    grid_pos = html.find(GRID_OPEN)
    if grid_pos == -1:
        raise ValueError('Could not find id="skillsGrid" in skills.html')

    after_open = grid_pos + len(GRID_OPEN)
    new_card   = build_skill_card(config)

    # Prepend new card immediately after the opening tag
    html = html[:after_open] + '\n\n          ' + new_card + '\n' + html[after_open:]

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
        raise ValueError('Could not locate closing </div> for skills-grid')

    # Collect all skill-card start positions within the grid
    card_starts = []
    search = scan_from
    while search < grid_close:
        marker = html.find(CARD_MARKER, search)
        if marker == -1 or marker >= grid_close:
            break
        # Walk back to the <div that owns this class attribute
        div_start = html.rfind('<div ', 0, marker)
        if div_start not in card_starts:
            card_starts.append(div_start)
        search = marker + len(CARD_MARKER)

    if len(card_starts) > MAX_GRID:
        cut_pos  = card_starts[MAX_GRID]
        last_nl  = html.rfind('\n', scan_from, cut_pos)
        cut_clean = last_nl if last_nl != -1 else cut_pos
        html = html[:cut_clean] + '\n        ' + html[grid_close:]
        card_count = MAX_GRID
    else:
        card_count = len(card_starts)

    return html, card_count


# -- data/skills.json updater ----------------------------------------------

def update_skills_json(skills_json_str, config):
    """Prepend new skill entry to skills.json, keep MAX_SKILLS items."""
    try:
        data = json.loads(skills_json_str)
    except json.JSONDecodeError:
        data = {"skills": [], "updated": ""}

    skills = data.get("skills", [])

    new_skill = {
        "title": config["title"],
        "slug":  config["url"].rstrip('/').split('/')[-1].replace('.html', ''),
        "desc":  config["desc"],
        "hero":  config["hero"],
        "badge": config["badge"],
        "cat":   config["cat"],
        "diff":  config.get("diff", "Intermediate"),
        "time":  config.get("time", "~20 min"),
        "date":  datetime.date.today().isoformat(),
        "url":   config["url"],
    }

    skills.insert(0, new_skill)
    skills = skills[:MAX_SKILLS]

    data["skills"]  = skills
    data["updated"] = datetime.date.today().isoformat()

    return json.dumps(data, indent=2, ensure_ascii=False)


# -- Combined skills.html updater ------------------------------------------

def update_skills_html(html, config):
    """Apply all slideshow AND grid updates to skills.html."""
    html, dropped    = update_skills_slides_data(html, config)
    html             = update_slide_divs(html, config)
    html             = rebuild_dot_buttons(html)
    html, grid_count = update_skills_grid(html, config)
    return html, dropped, grid_count


# -- Main ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Aether Intel Skills Launcher")
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
    required = ["title", "url", "desc", "hero", "badge", "cat"]
    missing = [f for f in required if f not in config]
    if missing:
        print(f"ERROR: Missing required config fields: {missing}", file=sys.stderr)
        sys.exit(1)

    print("Aether Intel Skills Launcher", file=sys.stderr)
    print(f"   Skill:  {config['title']}", file=sys.stderr)
    print(f"   URL:    {config['url']}", file=sys.stderr)

    # --- Step 1: Convert hero PNG -> WebP (if png_path provided) ---
    webp_result = None
    if config.get("png_path"):
        print(f"\nConverting hero PNG -> WebP…", file=sys.stderr)
        try:
            webp_result = convert_hero_png(config)
            kb_after = webp_result["webp_bytes"] // 1024
            print(f"   OK  -> {kb_after} KB WebP ({webp_result['hero_reduction_pct']}% reduction)", file=sys.stderr)
        except Exception as e:
            print(f"   WARNING: WebP conversion failed: {e}", file=sys.stderr)
            webp_result = None
    else:
        print(f"\n   (no png_path provided -- skipping WebP conversion)", file=sys.stderr)

    # --- Step 2: Fetch current files from GitHub ---
    print("\nFetching current files from GitHub…", file=sys.stderr)
    try:
        skills_html = fetch_raw("skills.html")
        print(f"   OK  skills.html ({len(skills_html):,} bytes)", file=sys.stderr)
    except Exception as e:
        print(f"   ERROR: Failed to fetch skills.html: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        skills_json_str = fetch_raw("data/skills.json")
        print(f"   OK  data/skills.json ({len(skills_json_str):,} bytes)", file=sys.stderr)
    except Exception as e:
        print(f"   INFO: data/skills.json not found — creating new: {e}", file=sys.stderr)
        skills_json_str = '{"skills": [], "updated": ""}'

    # --- Step 3: Update skills.html ---
    print("\nUpdating skills slideshow and card grid…", file=sys.stderr)
    try:
        new_skills_html, dropped_slide, grid_count = update_skills_html(skills_html, config)

        # Verify slideshow counts
        slide_count = len(re.findall(r'class="hero-slide-img"', new_skills_html))
        dot_count   = len(re.findall(r'<button[^>]+class="hero-dot[^"]*"', new_skills_html))
        _, entries, _, _ = parse_skills_slides_data(new_skills_html)
        data_count  = len(entries)

        print(f"   OK  Slides: {slide_count}, Dots: {dot_count}, SKILLS_SLIDES_DATA: {data_count}", file=sys.stderr)
        if slide_count != dot_count or dot_count != data_count:
            print(f"   WARNING: slide counts don't match! Expected all to be {MAX_SLIDES}", file=sys.stderr)

        print(f"   Dropped oldest slide: {dropped_slide[:60].strip()}...", file=sys.stderr)
        print(f"   Skill card grid: {grid_count} cards (max {MAX_GRID})", file=sys.stderr)
    except Exception as e:
        print(f"   ERROR: Skills update failed: {e}", file=sys.stderr)
        import traceback; traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    # --- Step 4: Update data/skills.json ---
    print("\nUpdating data/skills.json…", file=sys.stderr)
    try:
        new_skills_json = update_skills_json(skills_json_str, config)
        skills_data = json.loads(new_skills_json)
        print(f"   OK  {len(skills_data['skills'])} skills (new skill prepended)", file=sys.stderr)
    except Exception as e:
        print(f"   ERROR: skills.json update failed: {e}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("\n[DRY RUN] Would commit these files:", file=sys.stderr)
        print(f"  - skills.html ({len(new_skills_html):,} bytes)", file=sys.stderr)
        print(f"  - data/skills.json ({len(new_skills_json):,} bytes)", file=sys.stderr)
        if webp_result:
            print(f"  - hero image ({webp_result['webp_bytes']:,} bytes WebP)", file=sys.stderr)
        return

    # --- Step 5: Output result JSON for GITHUB_COMMIT_MULTIPLE_FILES ---
    result = {
        "skills_html":   new_skills_html,
        "skills_json":   new_skills_json,
        "slides_count":  slide_count,
        "grid_count":    grid_count,
        "dropped_slide": dropped_slide,
    }
    if webp_result:
        result["webp_base64"]         = webp_result["webp_base64"]
        result["webp_bytes"]          = webp_result["webp_bytes"]
        result["hero_reduction_pct"]  = webp_result["hero_reduction_pct"]

    print("\nDone. Output JSON ready for commit.", file=sys.stderr)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
