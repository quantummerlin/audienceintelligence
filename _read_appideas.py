import json

with open('_appideas_extracted.json', encoding='utf-8') as f:
    posts = json.load(f)

# Deduplicate by title (keep highest score), skip NSFW/adult
seen = {}
for p in posts:
    t = p['title'].lower().strip()
    if any(w in t for w in ['nsfw', 'sexting', 'sex', 'porn', 'adult', 'girly', 'onlyfans', 'naughty', 'erotic', 'nude']):
        continue
    if t not in seen or p['score'] > seen[t]['score']:
        seen[t] = p

clean = sorted(seen.values(), key=lambda x: x['score'], reverse=True)
print(f'Clean unique posts: {len(clean)}')
print()

# Print full selftext of top 25 unique clean posts
for i, p in enumerate(clean[:25]):
    print(f'=== #{i+1} [{p["score"]} pts | {p["num_comments"]} cmts] ===')
    print(f'TITLE: {p["title"]}')
    print(f'TEXT: {p["selftext"][:1000]}')
    print()
