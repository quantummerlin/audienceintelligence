import os

reports_dir = r'reports'
count = 0
for fname in os.listdir(reports_dir):
    if not fname.endswith('.html'):
        continue
    path = os.path.join(reports_dir, fname)
    with open(path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
    if '../articles/' in content:
        continue
    new_content = content.replace(
        '<a href="../index.html#reports">Reports</a>',
        '<a href="../index.html#reports">Reports</a>\n                <a href="../articles/">Articles</a>'
    )
    if new_content != content:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        count += 1

print(f'Updated {count} report files')
