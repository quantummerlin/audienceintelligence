#!/usr/bin/env python3
"""
_reframe_reports.py
====================
Batch-update all existing report HTML files to article framing:
- Fix <title> (remove "Intelligence Report")
- Fix meta description (helpful, not "deep intelligence extracted from")
- Fix og:title / og:description
- Fix hero h1 ("What N+ words on X actually reveal" → readable title)
- Remove hero stats div (no upvote/comment counts in hero)
- Remove "INTELLIGENCE REPORT" from eyebrow
- Remove "Section 01", "Section 02" section labels
- Rename section headings to clear article headings
- Remove upvote scores from quote blocks
- Update nav link "Reports" → "Articles"
- Update footer text
Run once after switching to article format. Safe to re-run (idempotent).
"""

import os, re, sys

REPORTS_DIR = "reports"
DRY_RUN = "--dry-run" in sys.argv


def reframe(html: str, filename: str) -> str:
    original = html

    slug = filename.replace(".html", "")

    # ── 1. <title> — remove "Intelligence Report" suffix ──────────────────
    html = re.sub(
        r"(<title>)(.*?)\s*Intelligence Report\s*(.*?)(</title>)",
        lambda m: f"{m.group(1)}{m.group(2).strip()}{(' ' + m.group(3).strip()) if m.group(3).strip() else ''}{m.group(4)}",
        html, flags=re.IGNORECASE
    )

    # ── 2. og:title — same fix ──────────────────────────────────────────────
    html = re.sub(
        r'(property="og:title" content=")(.*?)\s*Intelligence Report\s*(.*?)(")',
        lambda m: f"{m.group(1)}{m.group(2).strip()}{(' ' + m.group(3).strip()) if m.group(3).strip() else ''}{m.group(4)}",
        html, flags=re.IGNORECASE
    )

    # ── 3. meta description — replace "Deep intelligence extracted from" ──
    html = re.sub(
        r'(<meta name="description" content=")Deep intelligence extracted from ([^"]+)\. Patterns, verbatims, hooks, and opportunities\.(")',
        lambda m: (
            f'{m.group(1)}We analysed {m.group(2).replace("+ words in the ", "real discussions about ").replace(" community", "")}. '
            f'Real opinions, key themes, and honest analysis — no sponsored content.{m.group(3)}'
        ),
        html, flags=re.IGNORECASE
    )

    # ── 4. og:description ──────────────────────────────────────────────────
    html = re.sub(
        r'(property="og:description" content=")What [^"]+ words on ([^"]+) actually reveal\.(")' ,
        lambda m: f'{m.group(1)}What people are actually saying about {m.group(2).strip()} — real opinions, no hype.{m.group(3)}',
        html, flags=re.IGNORECASE
    )

    # ── 5. hero h1: "What N+ words on X actually reveal" ──────────────────
    html = re.sub(
        r'(<h1 class="hero-title">)What [\d\.,]+[KM]?\+? words on (.*?) actually reveal(</h1>)',
        lambda m: f'{m.group(1)}{m.group(2).title()}: What People Are Actually Saying{m.group(3)}',
        html, flags=re.IGNORECASE
    )

    # ── 6. Eyebrow: "INTELLIGENCE REPORT" → "COMMUNITY RESEARCH" ──────────
    html = html.replace("INTELLIGENCE REPORT", "COMMUNITY RESEARCH")

    # ── 7. Hero sub — remove "Intelligence extracted from ... surfaced." ──
    html = re.sub(
        r"Intelligence extracted from [^<]{0,200}The signal buried in the noise — surfaced\.",
        "Real discussions. Real opinions. No marketing layer.",
        html, flags=re.DOTALL
    )
    # Clean up remaining "collective upvotes" phrasing
    html = re.sub(r"[\d\.,]+[KM]?\s*collective upvotes?\.",
                  "real people, real opinions.", html)

    # ── 8. Remove hero-stats div (the big number strip with upvotes) ───────
    html = re.sub(
        r'\s*<div class="hero-stats">.*?</div>(?=\s*(?:</div>|</section>))',
        "",
        html, flags=re.DOTALL
    )

    # ── 9. Remove section labels like <p class="sec-label">Section 01</p> ─
    html = re.sub(r'<p class="sec-label">Section \d+</p>\s*', '', html)

    # ── 10. Rename section h2 headings ─────────────────────────────────────
    replacements = {
        'The Numbers':               'Overview',
        'Highest-Signal Posts':      'Posts & Discussions',
        "What They're Actually Saying": 'What People Are Saying',
        'Recurring Language Patterns': 'Common Themes',
        'Key Sentences Extracted':   'Key Insights',
        'Emerging Topic Signals':    'Topics Being Discussed',
        'Content Gold — Proven Hooks': 'Key Takeaways',
    }
    for old, new in replacements.items():
        html = html.replace(
            f'<h2 class="sec-title">{old}</h2>',
            f'<h2 class="sec-title">{new}</h2>'
        )

    # ── 11. Remove upvote score spans inside quotes ─────────────────────────
    html = re.sub(r'<span class="quote-score">▲ [\d\.,KM]+ upvotes?</span>', '', html)
    # Also remove the tag badges from card headers (▲ score)
    html = re.sub(r'<span class="card-tag">▲ [\d\.,KM]+</span>', '', html)
    # Remove section number prefixes in card names "#1 — "
    html = re.sub(r'<span class="card-name">#\d+ — ', '<span class="card-name">', html)

    # ── 12. Nav link "Reports" → "Articles" ────────────────────────────────
    html = html.replace(
        '<a href="https://ai.quantummerlin.com/reports/">Reports</a>',
        '<a href="https://ai.quantummerlin.com/reports/">Articles</a>'
    )

    # ── 13. Update footer text ──────────────────────────────────────────────
    html = html.replace(
        "Intelligence extracted from real communities.",
        "Independent AI analysis — real data, no sponsored content."
    )
    # Footer nav: add Articles link if missing
    html = html.replace(
        '<a href="https://ai.quantummerlin.com/methodology.html">Methodology</a>',
        '<a href="https://ai.quantummerlin.com/reports/">Articles</a> &nbsp;·&nbsp;\n      <a href="https://ai.quantummerlin.com/methodology.html">Methodology</a>'
    ) if 'href="https://ai.quantummerlin.com/reports/"' not in html else html

    # ── 14. CTA box copy update ─────────────────────────────────────────────
    html = html.replace(
        "Need a Custom Dataset Report?",
        "More AI Analysis"
    )
    html = html.replace(
        "Drop your own community data and we'll extract the patterns, pain points, and content opportunities — formatted and ready to use.",
        "We publish regular deep-dives on AI tools, models, and what people are actually saying about them. No hype, no sponsored content."
    )
    html = html.replace(
        ">🔮 Order Custom Report</a>",
        '>Browse All Articles →</a>'
    )
    html = html.replace(
        'href="https://quantumtoolsmith.gumroad.com"',
        f'href="https://ai.quantummerlin.com/reports/"'
    )

    # ── 15. Rebrand "Aether Intelligence" → "AI.quantummerlin" ───────────────
    html = re.sub(r'Aether Intelligence', 'AI.quantummerlin', html)
    html = re.sub(r'<img[^>]+alt="AI\.quantummerlin"[^>]*>\s*\n?\s*AI\.quantummerlin',
                  'AI.quantummerlin', html)  # remove stale logo img + text duplicate

    # Update old-style header nav links to point to current site
    html = html.replace(
        'href="../index.html"',
        'href="https://ai.quantummerlin.com"'
    )
    html = html.replace(
        'href="index.html"',
        'href="https://ai.quantummerlin.com"'
    )

    return html


def main():
    files = [f for f in sorted(os.listdir(REPORTS_DIR))
             if f.endswith(".html") and f != "index.html"]

    changed = 0
    for fn in files:
        path = os.path.join(REPORTS_DIR, fn)
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            original = fh.read()
        updated = reframe(original, fn)
        if updated != original:
            changed += 1
            if DRY_RUN:
                print(f"[DRY] Would update: {fn}")
            else:
                with open(path, "w", encoding="utf-8") as fh:
                    fh.write(updated)
                print(f"✅  Updated: {fn}")
        else:
            print(f"─   No change: {fn}")

    print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Done — {changed}/{len(files)} files updated.")


if __name__ == "__main__":
    main()
