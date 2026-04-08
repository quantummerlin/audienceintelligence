import json, os, re

def strip_html(t):
    return re.sub(r'<[^>]+>', '', str(t)).replace('&amp;', '&').replace('&#39;', "'").replace('&lt;','<').replace('&gt;','>').replace('&quot;','"').strip()

all_posts = []
for i in range(1, 7):
    fn = f'redditappideas{i}.json'
    if not os.path.exists(fn):
        print(f'{fn}: NOT FOUND')
        continue
    with open(fn, encoding='utf-8') as f:
        data = json.load(f)
    children = data.get('data', {}).get('children', [])
    print(f'{fn}: {len(children)} posts')
    for c in children:
        d = c.get('data', {})
        all_posts.append({
            'file': fn,
            'id': d.get('id',''),
            'title': d.get('title',''),
            'score': d.get('score', 0),
            'num_comments': d.get('num_comments', 0),
            'selftext': strip_html(d.get('selftext', ''))[:800],
            'subreddit': d.get('subreddit', ''),
            'upvote_ratio': d.get('upvote_ratio', 0),
        })

all_posts.sort(key=lambda x: x['score'], reverse=True)
print(f'\nTotal posts: {len(all_posts)}')
print('\nTop 40 by score:')
for p in all_posts[:40]:
    print(f'  [{p["score"]:5d} pts | {p["num_comments"]:3d} cmt] {p["title"][:85]}')

# Save for use in report generator
with open('_appideas_extracted.json', 'w', encoding='utf-8') as f:
    json.dump(all_posts, f, ensure_ascii=False, indent=2)
print('\nSaved to _appideas_extracted.json')
