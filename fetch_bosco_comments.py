"""
fetch_bosco_comments.py
=======================
Fetches actual comment bodies for the top Famiglia nel Bosco discussion posts
using Reddit's public JSON API (no auth required).
Saves to bosco_comments.json for use in the full report.
"""
import json
import time
import os
import sys

try:
    import requests
except ImportError:
    sys.exit("requests not installed — run: pip install requests")

HEADERS = {"User-Agent": "AudienceIntelligence/1.0 (research; contact@audienceintelligence.com)"}

POST_IDS = [
    ("1rmd50k", "oknotizie",               92, "tribunale allontanare la madre"),
    ("1rkioi1", "Italia",                  58, "casa gratis 12 anni"),
    ("1rmd53e", "TuttoItalia",             51, "tribunale allontanare la madre"),
    ("1rkgygi", "TuttoItalia",             49, "casa gratis 12 anni"),
    ("1rkgw8k", "oknotizie",               43, "casa gratis 12 anni"),
    ("1rqo643", "italy",                   28, "perche la madre allontanata"),
    ("1rmmevj", "Italia",                  18, "tribunale + meloni"),
    ("1rpumh6", "malatidiserie",            0, "romina power"),
    ("1ruag0s", "culturepop",               0, "fallimento tutela sociale"),
]

def fetch_comments(post_id: str) -> list:
    url = f"https://www.reddit.com/comments/{post_id}.json?limit=500&depth=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        print(f"  HTTP {r.status_code}")
        if r.status_code != 200:
            return []
        try:
            data = r.json()
        except Exception as je:
            print(f"  JSON parse error: {je} — content: {r.text[:200]}")
            return []
        if not isinstance(data, list) or len(data) < 2:
            print(f"  Unexpected structure: {type(data)}")
            return []
        comments_listing = data[1].get("data", {}).get("children", [])
        result = []
        for c in comments_listing:
            if c.get("kind") == "t1":
                cd = c["data"]
                body = cd.get("body", "").strip()
                if body and body not in ("[deleted]", "[removed]", ""):
                    result.append({
                        "id": cd.get("id", ""),
                        "author": cd.get("author", "[deleted]"),
                        "body": body,
                        "score": cd.get("score", 0),
                        "created_utc": cd.get("created_utc", 0)
                    })
        return result
    except Exception as e:
        print(f"  Error fetching {post_id}: {e}")
        import traceback; traceback.print_exc()
    return []

def main():
    all_data = []
    for post_id, subreddit, expected_comments, topic in POST_IDS:
        print(f"Fetching r/{subreddit} post {post_id} (~{expected_comments} comments) — {topic}...")
        comments = fetch_comments(post_id)
        all_data.append({
            "post_id": post_id,
            "subreddit": subreddit,
            "topic": topic,
            "expected_comments": expected_comments,
            "fetched_comments": len(comments),
            "comments": comments
        })
        print(f"  Got {len(comments)} comments")
        time.sleep(1.5)  # be polite

    out_path = "bosco_comments.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)

    total = sum(len(p["comments"]) for p in all_data)
    print(f"\nSaved {total} comments from {len(all_data)} posts to {out_path}")

if __name__ == "__main__":
    main()
