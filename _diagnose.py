import glob, re

# Find Unicode replacement characters (U+FFFD) and also literal ?
# that appear in text content (not in URLs/attributes)
replacement_char = '\ufffd'

files = (glob.glob('articles/*.html') +
         glob.glob('newarticlestools/articles/**/*.html', recursive=True) +
         glob.glob('reports/*.html'))

fffd_files = []
for f in files:
    try:
        c = open(f, encoding='utf-8').read()
    except Exception:
        try:
            c = open(f, encoding='cp1252').read()
        except Exception:
            continue
    
    count = c.count(replacement_char)
    if count:
        fffd_files.append((count, f))

fffd_files.sort(reverse=True)
print(f'Files with U+FFFD replacement char: {len(fffd_files)}')
for n, f in fffd_files[:20]:
    print(f'  {n:4d}  {f}')

# Also show mojibake in a sample article
print()
sample_articles = files[:5]
for f in sample_articles:
    c = open(f, encoding='utf-8', errors='replace').read()
    # show first 300 chars of body text
    m = re.search(r'<body[^>]*>(.*)', c, re.DOTALL)
    if m:
        body = re.sub(r'<[^>]+>', '', m.group(1))
        body = body.replace('\n', ' ').strip()
        print(f'\n--- {f} ---')
        print(body[:300])
        break
