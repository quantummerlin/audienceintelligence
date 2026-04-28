#!/usr/bin/env python3
"""
_sync_index.py — AI.QM Content Index Sync Tool
================================================
Run this after adding new reports to keep _content_index.json fresh,
and to see what topics still need data collection.

Usage:
    python _sync_index.py              # scan reports/, update index, show queue
    python _sync_index.py --queue      # show only collection queue
    python _sync_index.py --gaps       # show only coverage gaps
"""

import os, re, json, sys
from datetime import datetime

REPORTS_DIR      = "reports"
INDEX_FILE       = "_content_index.json"
INDEX_HTML       = os.path.join(REPORTS_DIR, "index.html")


# ── Helpers ────────────────────────────────────────────────────────────────────

def extract_meta(html: str) -> dict:
    """Pull title, date, category from report HTML."""
    def first(pattern, default=""):
        m = re.search(pattern, html, re.IGNORECASE | re.DOTALL)
        return re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else default

    title   = first(r"<title>(.*?)</title>")
    eyebrow = first(r'class=["\'](?:report-eyebrow|eyebrow)["\'][^>]*>(.*?)<')
    h1      = first(r"<h1[^>]*>(.*?)</h1>")
    # Try to find a date in eyebrow or meta
    date_m  = re.search(r"(202\d[-/]\d{2}[-/]\d{2}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\w* 202\d)", html)
    date    = date_m.group(0) if date_m else ""
    return {"title": title or h1 or "", "eyebrow": eyebrow, "date": date}


def slug_from_filename(fn: str) -> str:
    return fn.replace(".html", "")


def infer_category(slug: str, title: str) -> str:
    s = (slug + " " + title).lower()
    if any(k in s for k in ["gpt", "claude", "gemini", "llama", "mistral", "deepseek", "hermes", "seedance", "openai", "anthropic", "openrouter"]): return "AI Models"
    if any(k in s for k in ["agent", "coding", "vibe-cod", "cursor"]): return "AI Dev"
    if any(k in s for k in ["money", "income", "hustle", "etsy", "dropship"]): return "Money"
    if any(k in s for k in ["hook", "viral", "social", "marketing"]): return "Hooks"
    if any(k in s for k in ["startup", "idea", "competitor", "opportunity"]): return "Opportunities"
    if any(k in s for k in ["animation", "website", "design"]): return "Dev"
    if any(k in s for k in ["security", "engineering", "surveillance", "spy"]): return "Security"
    if any(k in s for k in ["health", "ptsd", "ocd", "sobriety", "icu"]): return "Health"
    if any(k in s for k in ["psychology", "mindset", "manifest"]): return "Psychology"
    return "Culture"


def infer_source(slug: str, html: str) -> str:
    if "youtube" in html.lower() or "videos" in html.lower():
        return "youtube"
    if "reddit" in html.lower() or "upvote" in html.lower():
        return "reddit"
    return "unknown"


# ── Scan ───────────────────────────────────────────────────────────────────────

def scan_reports() -> list[dict]:
    files = sorted(f for f in os.listdir(REPORTS_DIR)
                   if f.endswith(".html") and f != "index.html")
    results = []
    for fn in files:
        path = os.path.join(REPORTS_DIR, fn)
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            html = fh.read()
        meta  = extract_meta(html)
        slug  = slug_from_filename(fn)
        cat   = infer_category(slug, meta["title"])
        src   = infer_source(slug, html)
        mtime = os.path.getmtime(path)
        results.append({
            "slug":     slug,
            "title":    meta["title"] or slug,
            "category": cat,
            "source":   src,
            "date":     meta["date"] or datetime.utcfromtimestamp(mtime).strftime("%Y-%m-%d"),
            "priority": "normal",
        })
    return results


# ── Merge (preserve manual overrides in existing index) ────────────────────────

def merge(scanned: list[dict], existing: list[dict]) -> list[dict]:
    existing_map = {r["slug"]: r for r in existing}
    merged = []
    for r in scanned:
        old = existing_map.get(r["slug"], {})
        merged.append({
            **r,
            "title":    old.get("title") or r["title"],      # prefer old if hand-edited
            "category": old.get("category") or r["category"],
            "date":     old.get("date") or r["date"],
            "priority": old.get("priority", "normal"),
        })
    return sorted(merged, key=lambda x: x.get("date", ""), reverse=True)


# ── Print helpers ──────────────────────────────────────────────────────────────

SEP  = "─" * 72
BOLD = "\033[1m"
CYAN = "\033[96m"
YEL  = "\033[93m"
RED  = "\033[91m"
GRN  = "\033[92m"
RST  = "\033[0m"


def print_queue(queue: list[dict]):
    print(f"\n{BOLD}{CYAN}📋  COLLECTION QUEUE ({len(queue)} topics){RST}")
    print(SEP)
    for item in queue:
        tag = {
            "HIGH":   f"{RED}▲ HIGH  {RST}",
            "MEDIUM": f"{YEL}● MED   {RST}",
            "LOW":    f"○ LOW   ",
        }.get(item.get("priority", "LOW"), "")
        src = f"[{item['type'].upper()}]"
        print(f"  {tag}{src:<10} {BOLD}{item['topic']}{RST}")
        print(f"           Query : {item.get('suggested_query','')}")
        if item.get("suggested_subreddit"):
            print(f"           Sub   : {item['suggested_subreddit']}")
        print(f"           Why   : {item['reason'][:80]}")
        print()


def print_gaps(gaps: dict):
    print(f"\n{BOLD}{YEL}🕳️  COVERAGE GAPS{RST}")
    print(SEP)
    for k, v in gaps.items():
        label = k.replace("_", " ").title()
        print(f"  {BOLD}{label}{RST}")
        if isinstance(v, list):
            print("    " + " · ".join(v))
        else:
            print(f"    {v}")
    print()


# ── Main ───────────────────────────────────────────────────────────────────────

def main():
    show_queue = "--queue" in sys.argv
    show_gaps  = "--gaps"  in sys.argv
    queue_only = show_queue and not show_gaps
    gaps_only  = show_gaps  and not show_queue

    # Load existing index
    existing_reports = []
    existing_queue   = []
    existing_gaps    = {}
    if os.path.exists(INDEX_FILE):
        with open(INDEX_FILE, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        existing_reports = data.get("reports", [])
        existing_queue   = data.get("collection_queue", [])
        existing_gaps    = data.get("coverage_gaps", {})

    # Scan disk
    scanned  = scan_reports()
    new_slugs = {r["slug"] for r in scanned} - {r["slug"] for r in existing_reports}
    merged   = merge(scanned, existing_reports)

    # Write updated index
    updated = {
        "_meta": {
            "site":         "ai.quantummerlin.com",
            "last_updated": datetime.utcnow().strftime("%Y-%m-%d"),
            "total_reports": len(merged),
            "note": "Run _sync_index.py after adding new reports to auto-update this file"
        },
        "reports":          merged,
        "collection_queue": existing_queue,
        "coverage_gaps":    existing_gaps,
    }
    with open(INDEX_FILE, "w", encoding="utf-8") as fh:
        json.dump(updated, fh, indent=2, ensure_ascii=False)

    # Print summary
    if not (queue_only or gaps_only):
        print(f"\n{BOLD}{GRN}✅  Content Index Synced{RST}  →  {INDEX_FILE}")
        print(f"   Reports scanned : {len(scanned)}")
        print(f"   New since last  : {len(new_slugs) or 'none'}")
        if new_slugs:
            for s in sorted(new_slugs):
                print(f"   {GRN}+ {s}{RST}")
        print(f"   Index written   : {INDEX_FILE}")

    if not gaps_only:
        print_queue(existing_queue)

    if not queue_only:
        print_gaps(existing_gaps)

    # Reminder for top HIGH items
    high = [q for q in existing_queue if q.get("priority") == "HIGH"]
    if high and not (queue_only or gaps_only):
        print(f"{BOLD}Next collection to run:{RST}")
        top = high[0]
        print(f"  Topic  : {top['topic']}")
        print(f"  Type   : {top['type']}")
        print(f"  Query  : {top.get('suggested_query','')}")
        if top.get("suggested_subreddit"):
            print(f"  Sub    : {top['suggested_subreddit']}")
        print()


if __name__ == "__main__":
    main()
