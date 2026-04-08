import json
import os

# Read from clean JSON (run convert_to_json.py first to generate it from .txt)
json_file = 'redditopenclaw.json'
txt_file  = 'redditopenclaw.txt'

if os.path.exists(json_file):
    with open(json_file, 'r', encoding='utf-8') as f:
        raw_posts = json.load(f)          # already a list of post dicts
    posts = [{'data': p} for p in raw_posts]
else:
    # Fallback: parse original NDJSON
    posts = []
    with open(txt_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                posts.extend(data['data']['children'])
            except Exception as e:
                print(f'Skip line: {e}')

print(f'Total posts: {len(posts)}')

# Deduplicate by title (no-op when reading from .json which is already deduped)
seen = set()
unique_posts = []
for p in posts:
    t = p['data'].get('title','')
    if t not in seen:
        seen.add(t)
        unique_posts.append(p)

print(f'Unique posts: {len(unique_posts)}')
total_comments = sum(p['data'].get('num_comments',0) for p in unique_posts)
print(f'Total comments referenced: {total_comments}')

sorted_posts = sorted(unique_posts, key=lambda p: p['data'].get('score', 0), reverse=True)

for i, p in enumerate(sorted_posts[:30]):
    d = p['data']
    body = d.get('selftext', '').strip()
    if body in ('[deleted]', '[removed]', ''):
        body = '(no body)'
    elif len(body) > 1200:
        body = body[:1200] + '...'
    print()
    print(f'=== RANK#{i+1} score={d["score"]} comments={d["num_comments"]} ===')
    print(f'TITLE: {d["title"]}')
    print(f'AUTHOR: u/{d["author"]}')
    print(f'FLAIR: {d.get("link_flair_text", "")}')
    print(f'BODY: {body}')
