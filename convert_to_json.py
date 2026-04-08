"""
convert_to_json.py
==================
Converts redditopenclaw.txt (NDJSON - one Listing object per line)
into a clean redditopenclaw.json array of unique post objects.

Usage: python convert_to_json.py
       python convert_to_json.py --input myfile.txt --output myfile.json
"""
import json
import argparse
from pathlib import Path

def convert(input_path: str, output_path: str):
    posts = {}  # keyed by post ID to deduplicate

    with open(input_path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                children = data["data"]["children"]
                for child in children:
                    post_data = child["data"]
                    post_id = post_data.get("id", "")
                    if post_id and post_id not in posts:
                        posts[post_id] = post_data
            except (json.JSONDecodeError, KeyError) as e:
                print(f"  [WARN] Skipping line {line_num}: {e}")

    result = list(posts.values())

    # Sort by score descending for easy reading
    result.sort(key=lambda p: p.get("score", 0), reverse=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"Done: {len(result)} unique posts saved to {output_path}")
    print(f"Top post: \"{result[0]['title']}\" (score: {result[0]['score']})")
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input",  default="redditopenclaw.txt",  help="Source NDJSON file")
    parser.add_argument("--output", default="redditopenclaw.json", help="Output JSON file")
    args = parser.parse_args()
    convert(args.input, args.output)
