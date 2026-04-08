import json

with open('bosco_comments.json', encoding='utf-8') as f:
    data = json.load(f)

# Only show the extra posts (last 3)
for post in data[-3:]:
    print(f"\n{'='*80}")
    print(f"POST: {post['post_id']} | r/{post['subreddit']} | {post['topic']}")
    print('='*80)
    for c in sorted(post['comments'], key=lambda x: x['score'], reverse=True):
        body = c['body'].replace('\n', ' ').strip()
        print(f"  [{c['score']:4}] u/{c['author']}: {body}")
