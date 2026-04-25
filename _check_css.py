import glob, re, os

files = glob.glob('newarticlestools/articles/**/*.html', recursive=True)[:5]
for f in files:
    c = open(f, encoding='utf-8').read()
    css = re.findall(r"href=[\"'](.*?\.css)", c)
    print(f + ':', css)
