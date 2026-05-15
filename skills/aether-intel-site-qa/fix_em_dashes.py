#!/usr/bin/env python3
"""
fix_em_dashes.py — Aether Intel em-dash auto-fixer

Companion to pre_commit_check.py. Finds em dashes (— U+2014, &mdash;) in
article HTML and replaces them with contextually correct punctuation.
Operates ONLY on visible text nodes — skips <head>, <script>, <style>,
and HTML attribute values.

REPLACEMENT RULES (applied in order per text node)
───────────────────────────────────────────────────
1. <cite> attribution  "— Name"               → "- Name"
   (em dash before a capitalised word inside <cite>)

2. Connector clause    "word — but/and/or/so…" → "word, but/and/or/so…"
   (em dash joining two independent clauses with a conjunction)

3. Explanatory lead    "phrase — the/a/an/it…" → "phrase: the/a/an/it…"
   (em dash that introduces a definition or elaboration)

4. Generic spaced      "word — word"           → "word, word"
   (fallback for any remaining spaced em dash)

5. &mdash; entity      &mdash;                 → ,

6. Bare em dash        word—word               → word-word
   (no space before — treat as a hyphen; runs before connector rules)

USAGE
─────
  # Preview changes without writing anything
  python3 fix_em_dashes.py --dry-run articles/38-my-article.html

  # Fix in-place (creates .bak backup automatically)
  python3 fix_em_dashes.py articles/38-my-article.html

  # Fix multiple files
  python3 fix_em_dashes.py articles/3*.html

  # Skip the backup
  python3 fix_em_dashes.py --no-backup articles/38-my-article.html

EXIT CODES
──────────
  0  All files clean (no em dashes found) or all fixes applied successfully
  1  Dry-run: em dashes found (would be fixed)
  2  Argument error
"""

import os
import re
import sys
import shutil
import argparse
from pathlib import Path

# ── ANSI colours (disabled if not a TTY) ─────────────────────────────────────
USE_COLOUR = sys.stdout.isatty()
RED    = "\033[91m" if USE_COLOUR else ""
GREEN  = "\033[92m" if USE_COLOUR else ""
YELLOW = "\033[93m" if USE_COLOUR else ""
CYAN   = "\033[96m" if USE_COLOUR else ""
BOLD   = "\033[1m"  if USE_COLOUR else ""
RESET  = "\033[0m"  if USE_COLOUR else ""

# ── Skip-zone tags: text inside these is never touched ───────────────────────
SKIP_TAGS = {"script", "style", "head", "code", "pre", "kbd", "samp"}

# ── Connector words that almost always follow a comma, not a colon ───────────
CONNECTORS = (
    r"but|and|or|nor|yet|so|for|although|though|even though|"
    r"because|since|while|whereas|unless|until|if|when|where|"
    r"however|therefore|thus|hence|meanwhile|otherwise|instead|"
    r"still|then|now|just|only|also|too|rather|instead"
)

# ── Article / determiner words that suggest an explanatory colon ─────────────
EXPLANATORY_LEADS = r"the|a|an|it|its|this|that|these|those|they|there|here|what|which|how"


# ── HTML text-node splitter ───────────────────────────────────────────────────

def iter_text_nodes(html):
    """
    Yield (start, end, text) for every text node in the HTML that is NOT
    inside a skip-tag block and NOT inside a tag's attribute list.

    Yields spans over the *original* html string so the caller can splice
    replacements back in.
    """
    skip_depth = 0      # depth inside a skip-tag
    i = 0
    n = len(html)

    while i < n:
        if html[i] == '<':
            # Find the closing >
            gt = html.find('>', i)
            if gt == -1:
                break           # malformed — stop

            tag_raw = html[i:gt + 1]  # full tag including < >

            # Is this a closing tag?
            is_close = tag_raw.startswith('</')
            # Extract tag name
            name_m = re.match(r'</?([A-Za-z][A-Za-z0-9]*)', tag_raw)
            tag_name = name_m.group(1).lower() if name_m else ""

            if tag_name in SKIP_TAGS:
                if is_close:
                    skip_depth = max(0, skip_depth - 1)
                else:
                    skip_depth += 1

            i = gt + 1
        else:
            # Text node — find where it ends
            end = html.find('<', i)
            if end == -1:
                end = n

            if skip_depth == 0 and end > i:
                yield i, end, html[i:end]

            i = end


# ── Replacement rules ─────────────────────────────────────────────────────────

def fix_cite_attribution(text):
    """— Name  →  - Name  (inside <cite> the em dash is an attribution marker)."""
    return re.sub(r'—\s*(?=[A-Z])', '- ', text)


def fix_connector_clause(text):
    """word — but/and/etc  →  word, but/and/etc"""
    pattern = rf'(?<=[^\s])[ \t]*—[ \t]*(?=(?:{CONNECTORS})\b)'
    return re.sub(pattern, ', ', text, flags=re.IGNORECASE)


def fix_explanatory_clause(text):
    """phrase — the/a/it/this/etc  →  phrase: the/a/it/this/etc"""
    pattern = rf'(?<=[^\s])[ \t]*—[ \t]*(?=(?:{EXPLANATORY_LEADS})\b)'
    return re.sub(pattern, ': ', text, flags=re.IGNORECASE)


def fix_generic_spaced(text):
    """word — word  →  word, word  (fallback for any remaining spaced em dash)"""
    return re.sub(r'(?<=[^\s])[ \t]*—[ \t]*', ', ', text)


def fix_mdash_entity(text):
    """&mdash;  →  ,  (entity form, applied in same pipeline)"""
    # Spaced entity
    text = re.sub(r'\s*&mdash;\s*', ', ', text, flags=re.IGNORECASE)
    return text


def fix_bare_hyphen(text):
    """word—word  →  word-word  (no space before —: treat as compound hyphen).
    Must run BEFORE the spaced rules so that connector patterns like
    'word—and' don't get picked up by the connector regex (which uses \\s*)."""
    return re.sub(r'(?<=[^\s])—', '-', text)


def fix_bare_remaining(text):
    """Final safety-net: any leftover — (start-of-node, edge cases) → -"""
    return text.replace('—', '-')


def apply_rules_to_text_node(text, in_cite=False):
    """Apply the full rule chain to a single text node."""
    if in_cite:
        # Inside <cite>: attribution pattern takes precedence
        text = fix_cite_attribution(text)

    text = fix_mdash_entity(text)
    text = fix_bare_hyphen(text)       # no-space-before: hyphen, runs first
    text = fix_connector_clause(text)
    text = fix_explanatory_clause(text)
    text = fix_generic_spaced(text)
    text = fix_bare_remaining(text)    # safety net for any stragglers
    return text


# ── Context tracker (are we inside a <cite>?) ────────────────────────────────

def is_in_cite(html, pos):
    """Return True if position pos is inside a <cite>…</cite> block."""
    before = html[:pos]
    opens  = len(re.findall(r'<cite\b', before, re.IGNORECASE))
    closes = len(re.findall(r'</cite\b', before, re.IGNORECASE))
    return opens > closes


# ── Main fixer ────────────────────────────────────────────────────────────────

def fix_html(html):
    """
    Apply all em-dash replacement rules to html.
    Returns (fixed_html, list_of_change_dicts).
    Each change dict: {orig, fixed, line_num}.
    """
    changes = []
    segments = []          # list of (start, end) for text nodes that changed
    replacements = {}      # start → new_text

    for start, end, text in iter_text_nodes(html):
        if '—' not in text and '&mdash;' not in text.lower():
            continue

        in_cite = is_in_cite(html, start)
        fixed = apply_rules_to_text_node(text, in_cite=in_cite)

        if fixed != text:
            replacements[start] = (end, fixed)
            # Record individual changes for the report (one per em-dash hit)
            for m in re.finditer(r'.{0,35}(—|&mdash;).{0,35}', text, re.IGNORECASE):
                snippet_orig  = m.group(0).strip()
                # Find corresponding fixed snippet for display
                offset = m.start()
                win_start = max(0, offset - 5)
                win_end   = min(len(fixed), offset + len(m.group(0)) + 5)
                snippet_fixed = fixed[win_start:win_end].strip()
                line_num = html[:start + m.start()].count('\n') + 1
                changes.append({
                    "orig":     snippet_orig,
                    "fixed":    snippet_fixed,
                    "line_num": line_num,
                })

    if not replacements:
        return html, []

    # Rebuild HTML by splicing in replacements (iterate in reverse order)
    parts = []
    cursor = len(html)
    for start in sorted(replacements.keys(), reverse=True):
        end, new_text = replacements[start]
        parts.append(html[end:cursor])
        parts.append(new_text)
        cursor = start
    parts.append(html[:cursor])
    fixed_html = "".join(reversed(parts))

    return fixed_html, changes


# ── CLI ───────────────────────────────────────────────────────────────────────

def print_changes(path, changes, dry_run):
    verb = "Would fix" if dry_run else "Fixed"
    print(f"\n{BOLD}{CYAN}── {path} ──{RESET}")
    if not changes:
        print(f"  {GREEN}✅ No em dashes found{RESET}")
        return

    print(f"  {YELLOW}{verb} {len(changes)} em-dash occurrence(s):{RESET}")
    for c in changes:
        print(f"  {RED}  L{c['line_num']:>4}  -{RESET}  …{c['orig']}…")
        print(f"  {GREEN}        +{RESET}  …{c['fixed']}…")


def main():
    parser = argparse.ArgumentParser(
        description="Fix em dashes in Aether Intel article HTML files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("files", nargs="*", help="HTML file(s) to process")
    parser.add_argument("--dry-run",   action="store_true",
                        help="Show what would change without writing files")
    parser.add_argument("--no-backup", action="store_true",
                        help="Skip creating .bak backup before overwriting")
    args = parser.parse_args()

    if not args.files:
        parser.print_help()
        sys.exit(2)

    total_changes = 0
    files_changed = 0

    for filepath in args.files:
        p = Path(filepath)
        if not p.exists():
            print(f"{RED}❌ Not found: {filepath}{RESET}")
            continue
        if p.suffix.lower() != ".html":
            print(f"{YELLOW}⚠️  Skipping non-HTML file: {filepath}{RESET}")
            continue

        html = p.read_text(encoding="utf-8", errors="replace")
        fixed, changes = fix_html(html)

        print_changes(filepath, changes, args.dry_run)

        if changes:
            total_changes += len(changes)
            files_changed += 1

        if changes and not args.dry_run:
            if not args.no_backup:
                bak = p.with_suffix(".html.bak")
                shutil.copy2(p, bak)
                print(f"  {CYAN}  backup → {bak}{RESET}")
            p.write_text(fixed, encoding="utf-8")
            print(f"  {GREEN}  ✅ Written{RESET}")

    # Summary
    print(f"\n{'─'*60}")
    if total_changes == 0:
        print(f"{GREEN}✅ No em dashes found — all files clean.{RESET}")
        sys.exit(0)

    if args.dry_run:
        print(f"{YELLOW}⚠️  Dry run: {total_changes} em dash(es) in {files_changed} file(s) — "
              f"re-run without --dry-run to fix.{RESET}")
        sys.exit(1)
    else:
        print(f"{GREEN}✅ Fixed {total_changes} em dash(es) across {files_changed} file(s).{RESET}")
        print(f"   Run pre_commit_check.py to verify before committing.")
        sys.exit(0)


if __name__ == "__main__":
    main()
