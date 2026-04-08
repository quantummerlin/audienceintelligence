import json

with open('bosco_comments.json', encoding='utf-8') as f:
    data = json.load(f)

for post in data:
    if not post['comments']:
        continue
    print(f"\n{'='*80}")
    print(f"POST: {post['post_id']} | r/{post['subreddit']} | {post['topic']}")
    print(f"Fetched: {post['fetched_comments']} comments")
    print('='*80)
    for c in sorted(post['comments'], key=lambda x: x['score'], reverse=True):
        body = c['body'].replace('\n', ' ').strip()
        print(f"  [{c['score']:4}] u/{c['author']}: {body}")
