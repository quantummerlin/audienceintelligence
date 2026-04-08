"""
Injects Open Graph + Twitter Card meta tags into all reports and articles.
Run from the repo root: python _add_og_tags.py
"""
import os, re

BASE_URL = "https://ai.quantummerlin.com"
OG_IMAGE = f"{BASE_URL}/logo.png"
SITE_NAME = "Aether Intelligence"
DEFAULT_DESC = "Insights extracted from 200,000+ real online conversations. Patterns, trends, and signal you won't find anywhere else."

def make_og_block(title, desc, url):
    # Escape any quotes in title/desc for HTML attribute safety
    title = title.replace('"', '&quot;')
    desc  = desc.replace('"', '&quot;')
    return (
        f'    <meta property="og:type" content="article">\n'
        f'    <meta property="og:title" content="{title}">\n'
        f'    <meta property="og:description" content="{desc}">\n'
        f'    <meta property="og:image" content="{OG_IMAGE}">\n'
        f'    <meta property="og:url" content="{url}">\n'
        f'    <meta property="og:site_name" content="{SITE_NAME}">\n'
        f'    <meta name="twitter:card" content="summary_large_image">\n'
        f'    <meta name="twitter:title" content="{title}">\n'
        f'    <meta name="twitter:description" content="{desc}">\n'
        f'    <meta name="twitter:image" content="{OG_IMAGE}">\n'
    )

def process(filepath, rel_url):
    with open(filepath, encoding='utf-8') as f:
        c = f.read()

    if 'og:title' in c:
        return False  # already has OG tags

    # Extract <title>
    tm = re.search(r'<title>(.+?)</title>', c, re.DOTALL)
    title = tm.group(1).strip() if tm else SITE_NAME

    # Extract meta description
    dm = re.search(r'<meta\s+name="description"\s+content="([^"]+)"', c)
    desc = dm.group(1).strip() if dm else DEFAULT_DESC

    url = f"{BASE_URL}/{rel_url}".replace('\\', '/')
    og = make_og_block(title, desc, url)

    # Insert right after </title>
    new_c = re.sub(r'(</title>)', r'\1\n' + og, c, count=1)

    if new_c == c:
        print(f"  SKIP (no </title> found): {rel_url}")
        return False

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_c)
    return True


added = 0

# --- Reports ---
report_dir = 'reports'
for fn in sorted(os.listdir(report_dir)):
    if fn.endswith('.html'):
        if process(os.path.join(report_dir, fn), f'reports/{fn}'):
            added += 1
            print(f"  ✓ reports/{fn}")

# --- Articles ---
article_dir = 'articles'
for fn in sorted(os.listdir(article_dir)):
    if fn.endswith('.html') and fn != 'index.html':
        if process(os.path.join(article_dir, fn), f'articles/{fn}'):
            added += 1
            print(f"  ✓ articles/{fn}")

print(f"\nDone — OG tags added to {added} files.")
print('\nNow run:')
print('  git add reports/ articles/ && git commit -m "Add OG/Twitter meta tags to all reports and articles" && git push origin main')
