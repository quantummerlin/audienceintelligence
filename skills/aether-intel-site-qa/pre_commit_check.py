#!/usr/bin/env python3
"""
pre_commit_check.py — Aether Intel pre-flight checker

Run this BEFORE committing to catch issues locally. Pass the HTML files
you're about to commit as arguments.

Usage:
    python3 pre_commit_check.py articles/my-new-article.html
    python3 pre_commit_check.py articles/*.html
    python3 pre_commit_check.py --check-images images/articles/my-image.png

CHECKS RUN
──────────
For HTML files:
  1. style.css link present
  2. main.js script loaded
  3. <main> element OR .standalone-nav present
  4. No expired external image URLs (hyperagent.com/api/files, usergenerated/threads)
  5. Hero image src uses /images/articles/ path
  6. No unescaped > before 4-digit years (>2026 type artifacts)
  7. No bare <p>transcript</p> or <p>skills</p> blocks
  8. No em dashes (— U+2014 or &mdash;) in article body text — hard error

For image files (--check-images):
  8. File is not 0 bytes
  9. Magic bytes match the file extension

KNOWN BUG PATTERNS (what this prevents)
────────────────────────────────────────
┌─────────────────────────────────────┬───────────────────────────────────────────┐
│ Bug                                 │ Prevention                                │
├─────────────────────────────────────┼───────────────────────────────────────────┤
│ 0-byte image after commit           │ Always use encoding:'base64' in Composio  │
│                                     │ upserts. Never pre-encode with Python.    │
├─────────────────────────────────────┼───────────────────────────────────────────┤
│ CDN cache masking real file size    │ Verify via /git/blobs/SHA not /contents/  │
│                                     │ Use image_verify.py after commits.        │
├─────────────────────────────────────┼───────────────────────────────────────────┤
│ Expired hyperagent.com image URLs   │ Always store hero images in /images/      │
│                                     │ articles/ in the repo. Never use hosted   │
│                                     │ thread URLs — they expire.                │
├─────────────────────────────────────┼───────────────────────────────────────────┤
│ App shell (nav/ticker) disappears   │ Every article must have BOTH:             │
│ when navigating to article          │  1. <link href="/css/style.css">          │
│                                     │  2. <main> OR .standalone-nav class       │
│                                     │ main.js wraps standalone-nav in <main>    │
│                                     │ automatically, but only if style.css is   │
│                                     │ loaded first.                             │
├─────────────────────────────────────┼───────────────────────────────────────────┤
│ >2026 text artifacts in articles    │ Escape > as &gt; in HTML text content.    │
│                                     │ Common in Related Articles descriptions.  │
├─────────────────────────────────────┼───────────────────────────────────────────┤
│ "transcript" text in article body   │ Strip raw source text before publishing.  │
│                                     │ Review article body before committing.    │
├─────────────────────────────────────┼───────────────────────────────────────────┤
│ Slideshow slides/dots/data mismatch │ When editing index.html: update ALL THREE │
│                                     │ sections: slide divs, dot buttons, and    │
│                                     │ SLIDES_DATA array. Keep counts identical. │
├─────────────────────────────────────┼───────────────────────────────────────────┤
│ Dead article links in grid          │ Don't add card to articles.html unless    │
│                                     │ the .html file actually exists in repo.   │
├─────────────────────────────────────┼───────────────────────────────────────────┤
│ Em dash (—) in article text         │ Em dashes read as formal/stiff and repel  │
│                                     │ readers. Replace with:                    │
│                                     │  - Comma (mid-sentence continuation)      │
│                                     │  - Colon (explanatory clause)             │
│                                     │  - Period (complete thought)              │
│                                     │  - Hyphen only in compound modifiers      │
│                                     │ Also avoid &mdash; HTML entity.           │
└─────────────────────────────────────┴───────────────────────────────────────────┘
"""

import os
import re
import sys
from pathlib import Path

ISSUE = "❌"
WARN  = "⚠️ "
OK    = "✅"

EXTERNAL_IMG_PATTERNS = [
    r'hyperagent\.com/api/files',
    r'usergenerated/threads/',
    r'hyperagent\.com/usergenerated',
]

MAGIC_BYTES = {
    "png":  bytes([0x89, 0x50, 0x4e, 0x47]),
    "jpg":  bytes([0xff, 0xd8, 0xff]),
    "jpeg": bytes([0xff, 0xd8, 0xff]),
    "gif":  b"GIF8",
    "webp": b"RIFF",
}

all_issues = []

def issue(path, msg, severity=ISSUE):
    all_issues.append((severity, path, msg))
    print(f"  {severity} {msg}")

def ok(msg):
    print(f"  {OK} {msg}")

def check_html(path, html):
    print(f"\n── {path} ──")
    errors = 0

    # 1. style.css
    if 'href="/css/style.css"' not in html and "href='/css/style.css'" not in html:
        issue(path, 'Missing <link href="/css/style.css"> — add before </head>')
        errors += 1
    else:
        ok("style.css linked")

    # 2. main.js
    if 'src="/js/main.js"' not in html and "src='/js/main.js'" not in html:
        issue(path, 'Missing <script src="/js/main.js"> — app shell won\'t inject')
        errors += 1
    else:
        ok("main.js loaded")

    # 3. <main> or standalone-nav
    has_main = bool(re.search(r'<main[\s>]', html, re.IGNORECASE))
    has_sn   = 'class="standalone-nav"' in html or "class='standalone-nav'" in html
    if not has_main and not has_sn:
        issue(path, "No <main> element and no .standalone-nav — app shell can't inject content")
        errors += 1
    elif not has_main and has_sn:
        ok(".standalone-nav detected (main.js will wrap in <main> automatically)")
    else:
        ok("<main> element present")

    # 4. External image URLs (deduplicated — one report per unique URL)
    all_srcs = re.findall(r'src=["\']([^"\']+)["\']', html, re.IGNORECASE)
    bad_srcs = []
    for src in all_srcs:
        if any(re.search(p, src, re.IGNORECASE) for p in EXTERNAL_IMG_PATTERNS):
            if src not in bad_srcs:
                bad_srcs.append(src)
    for src in bad_srcs:
        issue(path, f"External/expiring image URL: {src[:80]}")
        issue(path, "  → Generate the image and commit to /images/articles/ instead", WARN)
        errors += 1

    # 5. Hero image in /images/ and WebP format
    hero = re.search(
        r'<img[^>]*class=["\'][^"\']*hero[^"\']*["\'][^>]*src=["\']([^"\']+)["\']'
        r'|src=["\']([^"\']+)["\'][^>]*class=["\'][^"\']*hero[^"\']*["\']',
        html, re.IGNORECASE
    )
    if hero:
        src = hero.group(1) or hero.group(2)
        if not src.startswith("/images/"):
            issue(path, f"Hero image not in /images/: {src[:80]}", WARN)
        elif src.endswith(".png"):
            issue(path, f"Hero image is PNG — convert to WebP first (93-97% smaller): {src[:80]}", WARN)
            issue(path, "  → from PIL import Image; img.save(buf, 'WEBP', quality=82)", WARN)
        else:
            ok(f"Hero image: {src}")

    # 6. Unescaped > before years
    # Find ">YYYY" patterns in non-attribute, non-tag positions
    no_tags = re.sub(r'<[^>]+>', '', html)
    bad_gt = re.findall(r'>\d{4}', no_tags)
    if bad_gt:
        issue(path, f"Unescaped '>' before year in text content: {bad_gt[:3]} — use &gt;", WARN)

    # 7. Raw source text leaking
    body = re.sub(r'<head>.*?</head>', '', html, flags=re.DOTALL|re.IGNORECASE)
    body = re.sub(r'<script[^>]*>.*?</script>', '', body, flags=re.DOTALL|re.IGNORECASE)
    body = re.sub(r'<style[^>]*>.*?</style>', '', body, flags=re.DOTALL|re.IGNORECASE)

    if re.search(r'<p>\s*transcript\s*</p>', body, re.IGNORECASE):
        issue(path, "Bare <p>transcript</p> found — raw source text leaked into body", WARN)

    if re.search(r'<p>\s*skills?\s*</p>', body, re.IGNORECASE):
        issue(path, "Bare <p>skills</p> found — raw source text leaked into body", WARN)

    # 8. Em dashes — hard error
    # Strip tags so we only check visible text (not href/src attributes etc.)
    text_only = re.sub(r'<[^>]+>', ' ', body)
    em_dash_hits = []
    for m in re.finditer(r'.{0,30}(—|&mdash;).{0,30}', text_only):
        snippet = m.group(0).strip()
        if snippet not in em_dash_hits:
            em_dash_hits.append(snippet)
        if len(em_dash_hits) >= 3:
            break

    if em_dash_hits:
        issue(path, f"Em dash (—) found in article text — readers find these off-putting. "
                    f"Replace with a comma, colon, or period.")
        for snippet in em_dash_hits:
            issue(path, f"  context: …{snippet}…")
        issue(path, "  → mid-sentence: use comma  |  explanatory: use colon  |  complete thought: use period")
        errors += len(em_dash_hits)

    if errors == 0:
        ok(f"All checks passed")

    return errors


def check_image(path_str):
    print(f"\n── {path_str} ──")
    p = Path(path_str)

    if not p.exists():
        issue(path_str, "File not found locally")
        return 1

    size = p.stat().st_size
    if size == 0:
        issue(path_str, "File is 0 bytes — likely base64 encoding corruption")
        issue(path_str, "  → Recommit using encoding:'base64' in Composio upserts array", WARN)
        return 1

    ext = p.suffix.lstrip(".").lower()
    magic = MAGIC_BYTES.get(ext)
    if magic:
        with open(p, "rb") as f:
            header = f.read(8)
        if not header.startswith(magic):
            issue(path_str, f"Wrong magic bytes for .{ext} — file may be corrupt (got {header[:4].hex()})")
            return 1

    ok(f"{size:,} bytes — valid {ext.upper()}")
    return 0


def check_index_slideshow(html_path):
    print(f"\n── Slideshow sync ({html_path}) ──")
    try:
        html = open(html_path).read()
    except FileNotFoundError:
        issue(html_path, "File not found locally — skipping slideshow check", WARN)
        return

    slide_count = len(re.findall(r'id=["\']slide-\d+["\']', html))
    if slide_count == 0:
        slide_count = len(re.findall(r'class=["\'][^"\']*hero-slide[^"\']*["\']', html))

    dots = len(re.findall(r'class=["\'][^"\']*\bdot\b[^"\']*["\']', html, re.IGNORECASE))

    data_match = re.search(r'const\s+SLIDES_DATA\s*=\s*\[(.+?)\];', html, re.DOTALL)
    data_count = 0
    if data_match:
        data_count = len(re.findall(r'\{', data_match.group(1)))

    print(f"  Slide divs:  {slide_count}")
    print(f"  Dot buttons: {dots}")
    print(f"  SLIDES_DATA: {data_count}")

    if slide_count == dots == data_count and slide_count > 0:
        ok(f"Slideshow in sync ({slide_count} slides)")
    else:
        issue(html_path, f"Slideshow mismatch — slides:{slide_count} dots:{dots} data:{data_count}")
        issue(html_path, "  → Update ALL THREE sections in sync when adding/removing slides", WARN)


def main():
    args = sys.argv[1:]
    check_images_flag = "--check-images" in args
    html_args = [a for a in args if a.endswith(".html") and not a.startswith("--")]
    img_args  = [a for a in args if re.search(r'\.(png|jpg|jpeg|gif|webp)$', a, re.I)]

    if not args:
        print(__doc__)
        return 0

    print("🔍 Aether Intel Pre-Commit Check\n")

    for f in html_args:
        if not os.path.exists(f):
            issue(f, "File not found")
            continue
        html = open(f, encoding="utf-8", errors="replace").read()
        check_html(f, html)

        # If it's index.html, also check slideshow sync
        if os.path.basename(f) == "index.html":
            check_index_slideshow(f)

    if check_images_flag or img_args:
        for f in img_args:
            check_image(f)

    # Summary
    print(f"\n{'─'*60}")
    if not all_issues:
        print(f"{OK} All checks passed — safe to commit.")
        return 0

    errors   = [i for i in all_issues if i[0] == ISSUE]
    warnings = [i for i in all_issues if i[0] == WARN]
    print(f"Found {len(errors)} error(s) and {len(warnings)} warning(s):\n")
    for sev, path, msg in all_issues:
        print(f"  {sev} [{path}] {msg}")

    if errors:
        print(f"\n{ISSUE} Fix errors before committing.")
        return 1

    print(f"\n{WARN} Warnings found — review before committing.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
