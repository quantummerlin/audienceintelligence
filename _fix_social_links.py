import re, pathlib

packs = list(pathlib.Path('inbox/processed').glob('*-social.html'))
for p in packs:
    c = p.read_text(encoding='utf-8')
    c2 = re.sub(r'<a href="\.\./articles/[^"]+\.html"[^>]+>.*?</a>', '', c)
    if c2 != c:
        p.write_text(c2, encoding='utf-8')
        print(f'Fixed: {p.name}')
    else:
        print(f'No match: {p.name}')
