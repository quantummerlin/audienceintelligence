import re

# Read the HTML file
with open('aether-intelligence/index.html', 'r') as f:
    content = f.read()

# List of different comment counts to use
comment_counts = [
    "18,247 Comments",  # Report #002
    "19,342 Comments",  # Report #003
    "17,891 Comments",  # Report #004
    "21,056 Comments",  # Report #005
    "20,147 Comments",  # Report #006
    "19,892 Comments",  # Report #007
]

# Find all occurrences and replace
count = 0
def replace_match(match):
    global count
    if count < len(comment_counts):
        result = comment_counts[count]
        count += 1
        return result
    return match.group(0)

# Replace the 20,946 Comments patterns
content = re.sub(r'20,946 Comments', replace_match, content)

# Write back
with open('aether-intelligence/index.html', 'w') as f:
    f.write(content)

print(f"Replaced {count} occurrences")