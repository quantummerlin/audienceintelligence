#!/usr/bin/env python3
"""
HTML Audit — prevents the bugs we've already had hit us once:

1. Orphan content between </main> and </body> (the 10 hero-slide-img divs bug,
   the static <footer class="site-footer"> leftover bug, the duplicate
   <nav class="mobile-bottom-nav"> bug)

2. Static markup that should ONLY come from JS injection (mobile-bottom-nav,
   sidebar, now-bar are all injected by main.js — hardcoded duplicates cause
   ghost UI)

3. Duplicate IDs (HTML requires unique IDs; duplicates break querySelector and
   accessibility)

4. Tag imbalance (unclosed tags, mismatched tags) that break layouts

5. Inline SW registration (must be centralised in main.js with
   updateViaCache:'none' — anything else risks stale-SW issues)

Fails the build with a non-zero exit code if any issue is found.
"""

import os
import re
import sys
from collections import Counter

# Directories to scan (relative to repo root)
SCAN_DIRS = ['.', 'articles', 'models', 'tools', 'skills', 'reports', 'resources']
# Sub-projects with their own structure that we don't audit
EXCLUDE_DIRS = ('inbox/', 'newarticlestools/', 'aether intelligence/', 'docs/',
                'examples/', 'node_modules/', '.git/')

# Tags that don't need closing
VOID_TAGS = {
    'meta', 'link', 'br', 'hr', 'img', 'input', 'source', 'track', 'wbr',
    'area', 'base', 'col', 'embed', 'param',
    'path', 'line', 'polyline', 'polygon', 'rect', 'circle', 'ellipse',
    'use', 'stop'
}

# Markup that should ONLY be injected by JS, never hardcoded
JS_INJECTED_PATTERNS = [
    (r'<nav\s+class=["\']mobile-bottom-nav["\']', 'mobile-bottom-nav (injected by main.js)'),
    (r'<aside\s+class=["\']sidebar["\']', 'sidebar (injected by main.js)'),
    (r'<footer\s+class=["\']now-bar["\']', 'now-bar (injected by main.js)'),
    (r'<footer\s+id=["\']aether-footer["\']', 'aether-footer (injected by footer.js)'),
]


def find_html_files():
    files = []
    for root, dirs, fnames in os.walk('.'):
        # Skip excluded directories
        rel_root = os.path.relpath(root, '.')
        if any(rel_root.startswith(p.rstrip('/')) for p in EXCLUDE_DIRS):
            continue
        for f in fnames:
            if f.endswith('.html'):
                path = os.path.join(rel_root, f) if rel_root != '.' else f
                files.append(path)
    return files


def audit_file(path):
    """Returns a list of issue strings, or [] if clean."""
    issues = []
    try:
        with open(path, encoding='utf-8', errors='replace') as f:
            raw = f.read()
    except Exception as e:
        return [f"Failed to read: {e}"]

    if len(raw) < 200:
        return []  # Skip stubs

    # 1. Orphan content between </main> and </body>
    main_match = re.search(r'</main>(.*?)</body>', raw, re.DOTALL)
    if main_match:
        tail = main_match.group(1)
        # Strip out scripts and comments (legitimate things to have there)
        clean = re.sub(r'<script\b[^>]*?(?:/>|>.*?</script>)', '', tail, flags=re.DOTALL)
        clean = re.sub(r'<!--.*?-->', '', clean, flags=re.DOTALL)
        stripped = clean.strip()
        if len(stripped) > 30:
            preview = re.sub(r'\s+', ' ', stripped)[:120]
            issues.append(f"orphan content between </main> and </body> ({len(stripped)} chars): {preview}")

    # 2. JS-injected markup that's hardcoded in HTML
    for pattern, desc in JS_INJECTED_PATTERNS:
        if re.search(pattern, raw):
            issues.append(f"hardcoded {desc} — must come from JS only")

    # 3. Duplicate IDs
    ids = re.findall(r'\sid="([^"]+)"', raw)
    dupes = {k: v for k, v in Counter(ids).items() if v > 1}
    if dupes:
        issues.append(f"duplicate IDs: {dupes}")

    # 4. Tag balance (excluding script and style content)
    html = re.sub(r'<!--.*?-->', '', raw, flags=re.DOTALL)
    html = re.sub(r'<script\b[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r'<style\b[^>]*>.*?</style>', '', html, flags=re.DOTALL | re.IGNORECASE)

    tag_re = re.compile(r'<(/?)(\w+)([^>]*)>')
    stack = []
    tag_issues = []
    for m in tag_re.finditer(html):
        is_close, tag, attrs = m.groups()
        tag = tag.lower()
        if tag in VOID_TAGS or attrs.rstrip().endswith('/'):
            continue
        if is_close:
            if not stack:
                tag_issues.append(f"stray </{tag}>")
            elif stack[-1] != tag:
                if tag in stack:
                    while stack and stack[-1] != tag:
                        stack.pop()
                    if stack:
                        stack.pop()
                else:
                    tag_issues.append(f"mismatch: closing </{tag}> while inside <{stack[-1]}>")
            else:
                stack.pop()
        else:
            stack.append(tag)
    if stack:
        issues.append(f"unclosed tags at EOF: {stack}")
    if tag_issues:
        issues.append(f"tag issues: {tag_issues[:3]}")

    # 5. Inline SW registration (should be in main.js only)
    if 'serviceWorker.register' in raw:
        # But allow main.js itself to register
        if not path.endswith('main.js'):
            issues.append("inline serviceWorker.register found — must be in main.js only")

    return issues


def main():
    files = find_html_files()
    print(f"Scanning {len(files)} HTML files...\n")

    total_issues = 0
    for path in sorted(files):
        issues = audit_file(path)
        if issues:
            total_issues += len(issues)
            print(f"\n❌ {path}")
            for issue in issues:
                print(f"     {issue}")

    if total_issues == 0:
        print("✅ All HTML files passed audit.")
        return 0
    else:
        print(f"\n❌ Audit failed: {total_issues} issue(s) found across the repo.")
        print("\nFix the issues above and commit again. These checks exist because")
        print("orphan content and duplicate static markup have caused real visible")
        print("bugs (the 2,000px gap between hero and articles, duplicate footers, etc.)")
        return 1


if __name__ == '__main__':
    sys.exit(main())
