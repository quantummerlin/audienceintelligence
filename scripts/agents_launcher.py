#!/usr/bin/env python3
"""
agents_launcher.py — Aether Intel Agents Launcher

Auto-updates the Aether Intel Agents page when a new agent is published:
  1. Converts hero PNG -> WebP at quality=82 (93-97% size reduction)
  2. Prepends the agent to the agents.html slideshow (grows to MAX_SLIDES)
  3. Adds an agent card to the "Latest Agents" grid (prepend, trim to MAX_GRID)
  4. Updates data/agents.json with the new agent listing entry
  5. Returns JSON with updated file contents ready for GITHUB_COMMIT_MULTIPLE_FILES

USAGE
-----
Called with a JSON config on stdin or via --config argument:

  python3 agents_launcher.py --config '{
    "agent_id":   "claude-business-strategist",
    "title":      "Claude Business Strategist",
    "url":        "/agents/claude-business-strategist.html",
    "desc":       "Senior strategy advisor that runs structured three-pass analysis.",
    "hero":       "/images/agents/claude-business-strategist-hero.webp",
    "badge":      "badge-business",
    "cat":        "Business",
    "model_hint": "sonnet",
    "tags":       ["strategy", "decisions", "analysis"],
    "png_path":   "/agent/stored_files/abc123_hero.png"
  }'

CONFIG FIELDS
-------------
  agent_id    Slug matching the filename of /agents/{slug}.json (required)
  title       Agent display name (required)
  url         Landing page URL  /agents/{slug}.html  (required)
  desc        Card teaser sentence (required)
  hero        Repo path for the WebP hero image (required)
  badge       CSS class — see BADGE OPTIONS below (required)
  cat         Category label shown in badge (required)
  model_hint  Recommended model (haiku | sonnet | opus | gpt-4o | etc.) (required)
  tags        Free-form tags for search/filter (optional, default: [])
  png_path    Local path to source PNG for automatic WebP conversion (optional)

BADGE OPTIONS
-------------
  badge-business -> green, for business/strategy/money agents
  badge-dev      -> blue, for developer/coding/security agents
  badge-agents   -> purple, for AI agent/automation/orchestration agents
  badge-ethics   -> red/orange, for society/labor/policy agents
  badge-secondary -> grey, for general-purpose agents

WHAT GETS UPDATED
-----------------
  agents.html:
    - New <div class="hero-slide-img"> prepended to slides track
      (slideshow grows to MAX_SLIDES, then drops oldest)
    - Dot buttons rebuilt to match slide count
    - var AGENTS_SLIDES_DATA entry prepended
    - New agent-card prepended to agents-grid
    - Grid trimmed to MAX_GRID cards max

  data/agents.json:
    - New listing entry prepended to "agents" array
    - Trimmed to MAX_AGENTS items max
    - "updated" field set to today

OUTPUT
------
Prints JSON to stdout:
  {
    "agents_html":        "<updated agents.html content>",
    "agents_json":        "<updated data/agents.json content>",
    "slides_count":       N,
    "grid_count":         N,
    "dropped_slide":      "{ old last slide data }" or null,
    "webp_base64":        "<base64 WebP>",       # only when png_path provided
    "webp_bytes":         87432,                  # only when png_path provided
    "hero_reduction_pct": 94.1                    # only when png_path provided
  }

ENVIRONMENT
-----------
  GITHUB_TOKEN   Optional — avoids rate limiting when fetching from GitHub
"""

import os
import re
import sys
import json
import base64
import datetime
import subprocess
import urllib.request
import argparse
from pathlib import Path

OWNER  = "quantummerlin"
REPO   = "audienceintelligence"
BRANCH = "main"
BASE_RAW = f"https://raw.githubusercontent.com/{OWNER}/{REPO}/{BRANCH}"
BASE_API = f"https://api.github.com/repos/{OWNER}/{REPO}/contents"
MAX_SLIDES = 8     # slideshow caps at 8, grows from 1
MAX_GRID   = 24    # latest-agents grid max cards
MAX_AGENTS = 100   # registry max entries

# Path to the WebP converter (sibling skill)
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
    """Fetch current file content via GitHub Contents API.

    raw.githubusercontent.com is CDN-cached and can return stale content for
    several minutes after a commit, which used to cause this launcher to
    clobber recent edits when it re-committed. The Contents API returns the
    canonical bytes via blob SHA, no CDN cache layer.
    """
    api_url = (
        f"{BASE_API}/{path.lstrip('/')}?ref={BRANCH}"
    )
    req = urllib.request.Request(api_url, headers=gh_headers())
    with urllib.request.urlopen(req, timeout=15) as r:
        payload = json.loads(r.read().decode("utf-8"))
    raw_b64 = payload.get("content", "").replace("\n", "")
    return base64.b64decode(raw_b64).decode("utf-8", errors="replace")


def fetch_via_api(path):
    """Fetch a file via the GitHub Contents API. Bypasses CDN cache. Returns text content."""
    import base64
    url = f"{BASE_API}/{path.lstrip('/')}?ref={BRANCH}"
    req = urllib.request.Request(url, headers=gh_headers())
    with urllib.request.urlopen(req, timeout=15) as r:
        data = json.loads(r.read().decode("utf-8"))
    if "content" not in data:
        raise RuntimeError(f"No content in API response for {path}: {data.get('message', 'unknown')}")
    return base64.b64decode(data["content"]).decode("utf-8", errors="replace")


# -- Hero image WebP conversion --------------------------------------------

def convert_hero_png(config):
    """Convert PNG at config["png_path"] to WebP via convert_to_webp.py."""
    png_path = config["png_path"]
    if not Path(png_path).exists():
        raise RuntimeError(f"png_path not found: {png_path}")

    converter = Path(CONVERTER_SCRIPT).resolve()
    if not converter.exists():
        # Fallback: inline PIL conversion
        from PIL import Image
        import io, base64
        img = Image.open(png_path).convert("RGB")
        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=82, method=6)
        webp_bytes = buf.getvalue()
        png_bytes = Path(png_path).stat().st_size
        reduction = round((1 - len(webp_bytes) / png_bytes) * 100, 1) if png_bytes else 0
        return {
            "webp_base64":        base64.b64encode(webp_bytes).decode("ascii"),
            "webp_bytes":         len(webp_bytes),
            "hero_reduction_pct": reduction,
        }

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


# -- Slideshow updater -----------------------------------------------------

def parse_agents_slides_data(html):
    """Extract AGENTS_SLIDES_DATA array as a list of raw entry strings."""
    m = re.search(
        r'((?:var|const|let)\s+AGENTS_SLIDES_DATA\s*=\s*\[)(.*?)(\];)',
        html, re.DOTALL
    )
    if not m:
        raise ValueError("Could not find AGENTS_SLIDES_DATA array in agents.html")

    array_body = m.group(2)
    span = m.span()

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


def build_agents_slides_entry(config):
    """Build an AGENTS_SLIDES_DATA JS object string."""
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


def update_agents_slides_data(html, config):
    """Prepend new entry. Grow until MAX_SLIDES, then drop oldest."""
    span, entries, open_str, close_str = parse_agents_slides_data(html)

    # Filter out any placeholder entries (those with href="#about" or starting with intro)
    # so the first real agent replaces the intro placeholder cleanly.
    is_placeholder = lambda e: 'href:  "#' in e or 'href: "#' in e
    placeholders = [e for e in entries if is_placeholder(e)]
    real_entries = [e for e in entries if not is_placeholder(e)]

    new_entry = build_agents_slides_entry(config)
    new_list = [new_entry] + real_entries

    dropped = None
    if len(new_list) > MAX_SLIDES:
        dropped = new_list[-1]
        new_list = new_list[:MAX_SLIDES]
    elif len(new_list) < MAX_SLIDES and placeholders:
        # Keep enough placeholders to reach a sensible visible count (min 1)
        # but don't artificially pad — let it grow naturally.
        pass

    joined = ",\n      ".join(new_list)
    new_block = f"{open_str}\n      {joined}\n    {close_str}"
    updated = html[:span[0]] + new_block + html[span[1]:]
    return updated, dropped, len(new_list)


def update_slide_divs(html, config, target_count):
    """Prepend new hero-slide-img, trim to target_count."""
    hero_img = config["hero"]
    new_div = (
        f'<div class="hero-slide-img" '
        f'style="background-image:url(\'{hero_img}\');background-color:#0d1020;">'
        f'</div>'
    )

    pattern = r'<div class="hero-slide-img"[^>]*></div>'
    matches = list(re.finditer(pattern, html))
    if len(matches) == 0:
        raise ValueError("No hero-slide-img divs found in agents.html")

    # Detect placeholder slides (background-image referencing intro/coming-soon)
    is_placeholder = lambda m: 'intro-hero' in m.group(0) or 'coming-soon' in m.group(0) or 'placeholder' in m.group(0)
    real_matches = [m for m in matches if not is_placeholder(m)]
    placeholder_matches = [m for m in matches if is_placeholder(m)]

    first_start = matches[0].start()
    last_end    = matches[-1].end()

    # Build new ordered list: new agent first, then real existing, then placeholders if room
    kept_real = [m.group(0) for m in real_matches]
    new_list = [new_div] + kept_real
    if len(new_list) < target_count and placeholder_matches:
        # Pad with placeholders until target_count
        needed = target_count - len(new_list)
        new_list = new_list + [m.group(0) for m in placeholder_matches[:needed]]
    new_list = new_list[:target_count]

    block = "\n        ".join(new_list)
    updated = html[:first_start] + block + html[last_end:]
    return updated


def rebuild_dot_buttons(html, target_count):
    """Rebuild #agentSlideDots with target_count buttons. Slide 1 active."""
    dots_container_start = html.find('id="agentSlideDots"')
    if dots_container_start == -1:
        raise ValueError("No agentSlideDots container found in agents.html")

    dots = ['<button class="hero-dot active" aria-label="Slide 1"></button>']
    for n in range(2, target_count + 1):
        dots.append(f'<button class="hero-dot" aria-label="Slide {n}"></button>')

    all_dots = list(re.finditer(r'<button[^>]+class="hero-dot[^"]*"[^>]*></button>', html[dots_container_start:]))
    if not all_dots:
        raise ValueError("No hero-dot buttons found in agentSlideDots")

    first_start = dots_container_start + all_dots[0].start()
    last_end    = dots_container_start + all_dots[-1].end()

    line_start = html.rfind('\n', 0, first_start) + 1
    indent = html[line_start:first_start]

    new_block = (f"\n{indent}").join(dots)
    updated = html[:first_start] + new_block + html[last_end:]
    return updated


# -- Agent card grid updater ----------------------------------------------

def build_agent_card(config):
    """Build a single agent-card <div> HTML string."""
    url   = config["url"]
    title = config["title"]
    desc  = config["desc"]
    badge = config["badge"]
    cat   = config["cat"]
    model = config.get("model_hint", "sonnet")
    slug  = config["agent_id"]
    hero  = config["hero"]

    return (
        f'<div class="agent-card" data-category="{cat.lower()}" data-name="{title.lower()}">\n'
        f'          <div class="agent-card-img-wrap">\n'
        f'            <img src="{hero}" alt="{title}" class="agent-card-img" loading="lazy" '
        f'onerror="this.style.background=\'linear-gradient(135deg,rgba(129,140,248,0.18),rgba(34,211,238,0.07))\';this.removeAttribute(\'src\')">\n'
        f'          </div>\n'
        f'          <div class="agent-card-body">\n'
        f'            <div class="agent-card-meta">\n'
        f'              <span class="badge {badge}">{cat}</span>\n'
        f'              <span class="agent-model">{model}</span>\n'
        f'            </div>\n'
        f'            <h3 class="agent-card-title">{title}</h3>\n'
        f'            <p class="agent-card-desc">{desc}</p>\n'
        f'            <div class="agent-card-actions">\n'
        f'              <button class="btn-agent-download" onclick="downloadAgent(\'{slug}\', \'json\')">\n'
        f'                <svg viewBox="0 0 24 24"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        f'<polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg>\n'
        f'                Download\n'
        f'              </button>\n'
        f'              <a href="{url}" class="agent-detail-link">Details →</a>\n'
        f'            </div>\n'
        f'          </div>\n'
        f'        </div>'
    )


def update_agents_grid(html, config):
    """Prepend new agent card to <div class=\"agents-grid\" id=\"agentsGrid\">. Trim to MAX_GRID."""
    GRID_OPEN   = 'id="agentsGrid">'
    CARD_MARKER = 'class="agent-card'

    grid_pos = html.find(GRID_OPEN)
    if grid_pos == -1:
        raise ValueError('Could not find id="agentsGrid" in agents.html')

    after_open = grid_pos + len(GRID_OPEN)
    new_card   = build_agent_card(config)

    # Remove any empty-state placeholder div inside the grid
    empty_pattern = r'<div class="agents-empty-state">.*?</div>'
    grid_body_match = re.search(GRID_OPEN + r'(.*?)</div>', html[grid_pos:], re.DOTALL)
    if grid_body_match and '<div class="agents-empty-state">' in grid_body_match.group(1):
        html = re.sub(empty_pattern, '', html, count=1, flags=re.DOTALL)
        # Re-find positions after removal
        grid_pos = html.find(GRID_OPEN)
        after_open = grid_pos + len(GRID_OPEN)

    html = html[:after_open] + '\n\n          ' + new_card + '\n' + html[after_open:]

    # Walk forward to find closing </div> of agents-grid
    grid_pos = html.find(GRID_OPEN)
    scan_from = grid_pos + len(GRID_OPEN)
    depth = 1
    i = scan_from
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
        raise ValueError('Could not locate closing </div> for agents-grid')

    # Collect card start positions
    card_starts = []
    search = scan_from
    while search < grid_close:
        marker = html.find(CARD_MARKER, search)
        if marker == -1 or marker >= grid_close:
            break
        div_start = html.rfind('<div ', 0, marker)
        if div_start not in card_starts:
            card_starts.append(div_start)
        search = marker + len(CARD_MARKER)

    if len(card_starts) > MAX_GRID:
        cut_pos = card_starts[MAX_GRID]
        last_nl = html.rfind('\n', scan_from, cut_pos)
        cut_clean = last_nl if last_nl != -1 else cut_pos
        html = html[:cut_clean] + '\n        ' + html[grid_close:]
        card_count = MAX_GRID
    else:
        card_count = len(card_starts)

    return html, card_count


# -- data/agents.json updater ----------------------------------------------

def update_agents_json(agents_json_str, config):
    """Prepend listing entry. Trim to MAX_AGENTS."""
    try:
        data = json.loads(agents_json_str)
    except json.JSONDecodeError:
        data = {"schema_version": 1, "updated": "", "agents": []}

    if "agents" not in data:
        data["agents"] = []
    if "schema_version" not in data:
        data["schema_version"] = 1

    new_entry = {
        "agent_id":  config["agent_id"],
        "title":     config["title"],
        "desc":      config["desc"],
        "hero":      config["hero"],
        "badge":     config["badge"],
        "category":  config["cat"].lower(),
        "category_label": config["cat"],
        "model_hint": config.get("model_hint", "sonnet"),
        "tags":      config.get("tags", []),
        "url":       config["url"],
        "date":      datetime.date.today().isoformat(),
    }

    # Remove any existing entry with same agent_id (handle re-publish)
    data["agents"] = [a for a in data["agents"] if a.get("agent_id") != config["agent_id"]]
    data["agents"].insert(0, new_entry)
    data["agents"] = data["agents"][:MAX_AGENTS]
    data["updated"] = datetime.date.today().isoformat()

    return json.dumps(data, indent=2, ensure_ascii=False)


# -- Combined agents.html updater ------------------------------------------

def update_agents_html(html, config):
    """Apply slideshow + grid updates. Returns (updated_html, dropped, slide_count, grid_count)."""
    html, dropped, slide_count = update_agents_slides_data(html, config)
    html = update_slide_divs(html, config, slide_count)
    html = rebuild_dot_buttons(html, slide_count)
    html, grid_count = update_agents_grid(html, config)
    return html, dropped, slide_count, grid_count


# -- Main ------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Aether Intel Agents Launcher")
    parser.add_argument("--config", type=str, help="JSON config string")
    parser.add_argument("--dry-run", action="store_true", help="Print diffs without final JSON")
    args = parser.parse_args()

    if args.config:
        config = json.loads(args.config)
    else:
        raw = sys.stdin.read().strip()
        if not raw:
            print("ERROR: No config provided. Pass --config JSON or pipe on stdin.", file=sys.stderr)
            sys.exit(1)
        config = json.loads(raw)

    required = ["agent_id", "title", "url", "desc", "hero", "badge", "cat", "model_hint"]
    missing = [f for f in required if f not in config]
    if missing:
        print(f"ERROR: Missing required config fields: {missing}", file=sys.stderr)
        sys.exit(1)

    print("Aether Intel Agents Launcher", file=sys.stderr)
    print(f"   Agent: {config['title']}", file=sys.stderr)
    print(f"   URL:   {config['url']}", file=sys.stderr)

    # Step 1: convert hero PNG -> WebP
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

    # Step 2: fetch current files (use API to bypass CDN cache)
    print("\nFetching current files from GitHub…", file=sys.stderr)
    try:
        agents_html = fetch_via_api("agents.html")
        print(f"   OK  agents.html ({len(agents_html):,} bytes)", file=sys.stderr)
    except Exception as e:
        print(f"   ERROR: Failed to fetch agents.html: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        agents_json_str = fetch_via_api("data/agents.json")
        print(f"   OK  data/agents.json ({len(agents_json_str):,} bytes)", file=sys.stderr)
    except Exception as e:
        print(f"   INFO: data/agents.json not found, starting fresh.", file=sys.stderr)
        agents_json_str = '{"schema_version": 1, "updated": "", "agents": []}'

    # Step 3: update agents.html
    print("\nUpdating agents slideshow and card grid…", file=sys.stderr)
    try:
        new_html, dropped, slide_count, grid_count = update_agents_html(agents_html, config)

        # Verify alignment
        img_count = len(re.findall(r'class="hero-slide-img"', new_html))
        dot_count = len(re.findall(r'<button[^>]+class="hero-dot[^"]*"', new_html))
        _, entries, _, _ = parse_agents_slides_data(new_html)
        data_count = len(entries)

        print(f"   OK  Slides: {img_count}, Dots: {dot_count}, AGENTS_SLIDES_DATA: {data_count}", file=sys.stderr)
        if img_count != dot_count or dot_count != data_count:
            print(f"   WARNING: slide counts don't match!", file=sys.stderr)

        if dropped:
            print(f"   Dropped oldest slide: {dropped[:60].strip()}...", file=sys.stderr)
        print(f"   Agent card grid: {grid_count} cards (max {MAX_GRID})", file=sys.stderr)
    except Exception as e:
        print(f"   ERROR: Update failed: {e}", file=sys.stderr)
        import traceback; traceback.print_exc(file=sys.stderr)
        sys.exit(1)

    # Step 4: update data/agents.json
    print("\nUpdating data/agents.json…", file=sys.stderr)
    try:
        new_json = update_agents_json(agents_json_str, config)
        json_data = json.loads(new_json)
        print(f"   OK  {len(json_data['agents'])} agents in registry", file=sys.stderr)
    except Exception as e:
        print(f"   ERROR: agents.json update failed: {e}", file=sys.stderr)
        sys.exit(1)

    if args.dry_run:
        print("\n[DRY RUN] Would commit:", file=sys.stderr)
        print(f"  - agents.html ({len(new_html):,} bytes)", file=sys.stderr)
        print(f"  - data/agents.json ({len(new_json):,} bytes)", file=sys.stderr)
        if webp_result:
            print(f"  - hero image ({webp_result['webp_bytes']:,} bytes WebP)", file=sys.stderr)
        return

    result = {
        "agents_html":   new_html,
        "agents_json":   new_json,
        "slides_count":  slide_count,
        "grid_count":    grid_count,
        "dropped_slide": dropped,
    }
    if webp_result:
        result["webp_base64"]        = webp_result["webp_base64"]
        result["webp_bytes"]         = webp_result["webp_bytes"]
        result["hero_reduction_pct"] = webp_result["hero_reduction_pct"]

    print("\nDone. Output JSON ready for commit.", file=sys.stderr)
    print(json.dumps(result))


if __name__ == "__main__":
    main()
