import json

with open('redditfamiligianelbosco.json', encoding='utf-8') as f:
    posts = json.load(f)

FAMILY_KW = ['famiglia nel bosco','family in the wood','madre allontanata',
             'allontanare la madre','catherine','nathan','tribunale',
             'benefattore','romina power','garante','nordio',
             'bosco: il fallimento','sciopero della fame']

disc = [p for p in posts
        if p.get('subreddit','').lower() != 'tvitaliana'
        and any(k in (p.get('title','')+p.get('selftext','')).lower() for k in FAMILY_KW)]
disc.sort(key=lambda x: x.get('num_comments', 0), reverse=True)

for p in disc[:8]:
    title = p['title'][:80]
    sub = p['subreddit']
    nc = p.get('num_comments', 0)
    comments = p.get('comments', [])
    print(f"\n{'='*80}")
    print(f"POST: {title}")
    print(f"r/{sub} | score {p.get('score',0)} | {nc} comments | {len(comments)} stored")
    print('='*80)
    for c in comments[:25]:
        score = c.get('score', 0)
        body = c.get('body', '').replace('\n', ' ').strip()
        if len(body) > 300:
            body = body[:300] + '...'
        if body and body not in ('[deleted]', '[removed]'):
            print(f"  [{score:4}] {body}")
