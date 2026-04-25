#!/usr/bin/env python3
"""
Comprehensive mojibake fix for all HTML files.
Handles both:
  1. UTF-8 files with mojibake (UTF-8 bytes decoded as cp1252)
  2. Files actually saved as Windows-1252 that need converting to UTF-8
"""
import os, sys, re


def fix_mojibake_in_text(text):
    """
    Walk through text and repair Windows-1252-interpreted UTF-8 sequences.
    For each char encodable as cp1252 that looks like a UTF-8 lead byte,
    try to collect continuation bytes and decode as UTF-8.
    """
    result = []
    i = 0
    n = len(text)
    while i < n:
        c = text[i]
        try:
            b = c.encode('cp1252')[0]
        except (UnicodeEncodeError, IndexError):
            result.append(c)
            i += 1
            continue

        if 0xC2 <= b <= 0xDF:
            need = 1
        elif 0xE0 <= b <= 0xEF:
            need = 2
        elif 0xF0 <= b <= 0xF4:
            need = 3
        else:
            result.append(c)
            i += 1
            continue

        seq = [b]
        j = i + 1
        ok = True
        for _ in range(need):
            if j >= n:
                ok = False; break
            try:
                b2 = text[j].encode('cp1252')[0]
            except (UnicodeEncodeError, IndexError):
                ok = False; break
            if 0x80 <= b2 <= 0xBF:
                seq.append(b2)
                j += 1
            else:
                ok = False; break

        if ok:
            try:
                fixed = bytes(seq).decode('utf-8')
                result.append(fixed)
                i = j
                continue
            except (UnicodeDecodeError, ValueError):
                pass

        result.append(c)
        i += 1
    return ''.join(result)


MARKERS = ['\u00e2\u20ac', '\u00c2\u00b7', '\u00c3\u2014', '\u00c2\u00a0',
           '\u00c2\u00a9', '\u00c2\u00ae', '\u00c3\u00a2', '\u00c2\u00bb',
           '\u00c2\u00b4', '\u00c3\u00b3', '\u00c3\u00a9', '\u00c3\u00bc',
           '\u00c3\u00a0', '\u00c3\u00af', '\u00c3\u00b1']


def has_mojibake(text):
    return any(m in text for m in MARKERS)


def fix_cp1252_charset_tag(content):
    """Update charset meta tag to utf-8."""
    return re.sub(
        r'(<meta[^>]+charset=)["\']?[^"\'>\s]+["\']?',
        r'\1"utf-8"',
        content, flags=re.IGNORECASE)


SKIP = {'build', 'node_modules', '.git', 'chrome_profile', '__pycache__',
        'fb_comment_exporter.egg-info'}


def scan_and_fix(root, dry_run=False):
    total_files = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP]
        for fname in filenames:
            if not fname.endswith('.html'):
                continue
            fpath = os.path.join(dirpath, fname)
            rel = os.path.relpath(fpath, root)
            try:
                # Try utf-8
                try:
                    content = open(fpath, encoding='utf-8').read()
                    enc = 'utf-8'
                except UnicodeDecodeError:
                    content = open(fpath, encoding='cp1252').read()
                    enc = 'cp1252'

                if enc == 'cp1252':
                    fixed = fix_cp1252_charset_tag(content)
                    if not dry_run:
                        open(fpath, 'w', encoding='utf-8').write(fixed)
                    print(f'  cp1252->utf8: {rel}')
                    total_files += 1
                    continue

                if not has_mojibake(content):
                    continue

                fixed = fix_mojibake_in_text(content)
                if fixed != content:
                    if not dry_run:
                        open(fpath, 'w', encoding='utf-8').write(fixed)
                    diff = abs(len(content) - len(fixed)) + sum(
                        1 for a, b in zip(content, fixed) if a != b)
                    print(f'  {diff:5d} chars fixed: {rel}')
                    total_files += 1

            except Exception as e:
                print(f'  ERROR {rel}: {e}')

    return total_files


if __name__ == '__main__':
    root = os.path.dirname(os.path.abspath(__file__))
    dry = '--dry-run' in sys.argv
    print(f'{"[DRY RUN] " if dry else ""}Fixing HTML files in: {root}\n')
    n = scan_and_fix(root, dry_run=dry)
    print(f'\n{"Would fix" if dry else "Fixed"} {n} file(s).')
