from reddit_comment_exporter.scraper import RedditScraper
import traceback

def progress(msg):
    print(f'PROGRESS: {msg}')

scraper = RedditScraper(
    subreddit='AusFinance',
    after=None,
    before=None,
    max_posts=None,
    max_comments=None,
    output_dir='outputs',
    on_progress=progress,
)
print('sub:', repr(scraper.subreddit))

try:
    posts = scraper.mine_posts()
    print(f'Posts: {len(posts)}')
    if posts:
        print(f'  First: {posts[0].title[:60]}')
    else:
        print('NO POSTS FOUND')
except Exception as e:
    print(f'ERROR: {e}')
    traceback.print_exc()
