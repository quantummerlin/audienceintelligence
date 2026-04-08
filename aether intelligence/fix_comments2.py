import re

# Read the HTML file
with open('aether-intelligence/index.html', 'r') as f:
    content = f.read()

# Vary the comment counts
variations = [
    "16,834 Comments",
    "17,456 Comments", 
    "16,291 Comments",
    "17,789 Comments"
]

count = 0
def replace_17k(match):
    global count
    if count < len(variations):
        result = variations[count]
        count += 1
        return result
    return match.group(0)

content = re.sub(r'17,091 Comments', replace_17k, content)

with open('aether-intelligence/index.html', 'w') as f:
    f.write(content)

print(f"Replaced {count} occurrences of 17,091 Comments")