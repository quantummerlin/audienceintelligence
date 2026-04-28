#!/usr/bin/env python3
"""
_cache_bust.py
==============
Stamps a fresh ?v=YYYYMMDDHHMMSS version onto Google Fonts <link> tags
in every .html file in the site root and reports/ folder.
Browser caches key off the full URL, so changing the query string forces a re-fetch.
Also updates the <meta name="version"> tag so you can see the deployed version.

Run by the pre-push git hook automatically.
Safe to run manually: python _cache_bust.py
"""

import os, re, glob
from datetime import datetime, timezone

VER   = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
STAMP = f"?v={VER}"


def bust_file(path: str) -> bool:
    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
        original = fh.read()

    html = original

    # 1. Update / add ?v= on Google Fonts stylesheet links
    # Matches: href="https://fonts.googleapis.com/...  with optional existing ?v=...
    html = re.sub(
        r'(href="https://fonts\.googleapis\.com/css2?[^"?]*)(?:\?v=\d+)?(")',
        lambda m: f'{m.group(1)}{STAMP}{m.group(2)}',
        html
    )

    # 2. Update / add <meta name="version"> in <head>
    if '<meta name="version"' in html:
        html = re.sub(
            r'<meta name="version" content="[^"]*">',
            f'<meta name="version" content="{VER}">',
            html
        )
    else:
        html = html.replace(
            '</head>',
            f'<meta name="version" content="{VER}">\n</head>',
            1
        )

    if html != original:
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(html)
        return True
    return False


def main():
    # Collect all HTML files in site root + reports/ + subdirs we own
    patterns = [
        "*.html",
        "reports/*.html",
    ]
    files = []
    for pat in patterns:
        files.extend(glob.glob(pat))

    changed = 0
    for path in sorted(files):
        if bust_file(path):
            changed += 1

    print(f"Cache bust v={VER} — {changed}/{len(files)} files updated.")


if __name__ == "__main__":
    main()
