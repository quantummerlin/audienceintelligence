import re, os

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

cards = re.findall(r'href="reports/([^"]+)"', content)
print(f'Total report card links: {len(cards)}')
for slug in cards:
    path = 'reports/' + slug
    size = os.path.getsize(path) if os.path.exists(path) else -1
    status = 'REAL' if size > 1000 else ('STUB' if size == 3 else 'MISSING')
    print(f'  {status}  {size}b  {slug}')
