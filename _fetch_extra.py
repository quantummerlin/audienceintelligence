"""Fetch the remaining high-comment posts and append to bosco_comments.json"""
import json, time, sys
try:
    import requests
except ImportError:
    sys.exit("need requests")

HEADERS = {"User-Agent": "AudienceIntelligence/1.0 (research)"}

EXTRA_POSTS = [
    ("1rpwvmg", "PensieriItaliani",        125, "odore di democrazia"),
    ("1rpxq7m", "opinioninonrichieste",     34, "mio dio che schifo"),
    ("1rdl8w5", "Italia",                   70, "bambini morti genitori tv"),
]

def fetch(post_id):
    url = f"https://www.reddit.com/comments/{post_id}.json?limit=500&depth=1"
    try:
        r = requests.get(url, headers=HEADERS, timeout=20)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code}"); return []
        data = r.json()
        if not isinstance(data, list) or len(data) < 2:
            return []
        result = []
        for c in data[1].get("data",{}).get("children",[]):
            if c.get("kind") == "t1":
                cd = c["data"]
                body = cd.get("body","").strip()
                if body and body not in ("[deleted]","[removed]",""):
                    result.append({"id": cd.get("id",""), "author": cd.get("author",""), 
                                   "body": body, "score": cd.get("score",0),
                                   "created_utc": cd.get("created_utc",0)})
        return result
    except Exception as e:
        print(f"  Error: {e}"); return []

with open("bosco_comments.json", encoding="utf-8") as f:
    data = json.load(f)

for post_id, sub, nc, topic in EXTRA_POSTS:
    print(f"Fetching r/{sub} {post_id} (~{nc}) — {topic}...")
    comments = fetch(post_id)
    print(f"  Got {len(comments)}")
    data.append({"post_id": post_id, "subreddit": sub, "topic": topic,
                 "expected_comments": nc, "fetched_comments": len(comments),
                 "comments": comments})
    time.sleep(1.5)

with open("bosco_comments.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

total = sum(len(p["comments"]) for p in data)
print(f"\nTotal: {total} comments across {len(data)} posts")
