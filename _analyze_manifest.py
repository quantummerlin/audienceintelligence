import json
from collections import Counter

with open('outputs/redditquantummanifestation.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

posts = data['data']['children']
print(f'Total posts: {len(posts)}')

subs = Counter(p['data']['subreddit'] for p in posts)
print('Subreddits:', dict(subs.most_common(20)))

# focus only on manifestation posts
manifest_posts = [p for p in posts if any(k in p['data']['subreddit'].lower() or k in (p['data']['title'] + p['data']['selftext']).lower()
    for k in ['manifest', 'law of attraction', 'loa', 'affirm', 'visuali', 'sp ', 'specific person', '3d', '4d', 'neville'])]
print(f'Manifestation-relevant posts: {len(manifest_posts)}')

# Key themes
all_text = ' '.join(p['data']['selftext'] + ' ' + p['data']['title'] for p in posts).lower()
themes = ['affirmation', 'visualization', 'specific person', 'law of attraction', 'neville', 'success story',
          'scripting', 'meditation', 'assume', 'revision', 'quantum', '3d', 'desire', 'reality', 'universe']
for t in themes:
    c = all_text.count(t)
    if c > 0:
        print(f'  {t}: {c}x')
