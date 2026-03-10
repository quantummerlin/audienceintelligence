#!/usr/bin/env python3
"""
YouTube Comment Exporter — CLI
================================
Command-line interface for the YouTube comment scraper.

Usage:
    python -m yt_comment_exporter.cli <url> [options]
    yt-export <url> [options]

Examples:
    yt-export https://www.youtube.com/watch?v=dQw4w9WgXcQ
    yt-export https://youtu.be/dQw4w9WgXcQ -o comments.json -f json
    yt-export https://www.youtube.com/shorts/ABC123 --no-headless
"""

import argparse
import sys
from pathlib import Path

from .scraper import YouTubeCommentScraper


def main():
    parser = argparse.ArgumentParser(
        prog="yt-export",
        description="Extract comments from any public YouTube video or Short.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  yt-export https://www.youtube.com/watch?v=dQw4w9WgXcQ\n"
            "  yt-export https://youtu.be/dQw4w9WgXcQ -o out.json -f json\n"
            "  yt-export https://www.youtube.com/shorts/ABC -o shorts.csv\n"
        ),
    )

    parser.add_argument("url", help="YouTube video or Shorts URL")

    parser.add_argument(
        "-o", "--output",
        default="yt_comments.csv",
        help="Output file path (default: yt_comments.csv)",
    )

    parser.add_argument(
        "-f", "--format",
        choices=["csv", "json"],
        default="csv",
        help="Output format (default: csv)",
    )

    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Show the browser window (useful for debugging)",
    )

    parser.add_argument(
        "--max-scrolls",
        type=int,
        default=200,
        help="Maximum scroll iterations (default: 200)",
    )

    parser.add_argument(
        "--scroll-pause",
        type=float,
        default=2.5,
        help="Pause between scrolls in seconds (default: 2.5)",
    )

    parser.add_argument(
        "--max-reply-expansions",
        type=int,
        default=50,
        help="Maximum reply thread expansions (default: 50)",
    )

    parser.add_argument(
        "--no-expand-replies",
        action="store_true",
        help="Skip expanding reply threads",
    )

    parser.add_argument(
        "--sort-newest",
        action="store_true",
        help="Sort comments by newest first (default: top comments)",
    )

    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 1.0.0",
    )

    args = parser.parse_args()

    # Validate output format
    output_path = Path(args.output)
    if args.format == "csv" and output_path.suffix != ".csv":
        output_path = output_path.with_suffix(".csv")
    elif args.format == "json" and output_path.suffix != ".json":
        output_path = output_path.with_suffix(".json")

    print(f"YouTube Comment Exporter v1.0.0")
    print(f"Target: {args.url}")
    print(f"Output: {output_path}")
    print("-" * 50)

    try:
        with YouTubeCommentScraper(
            headless=not args.no_headless,
            max_scrolls=args.max_scrolls,
            scroll_pause=args.scroll_pause,
            expand_replies=not args.no_expand_replies,
            max_reply_expansions=args.max_reply_expansions,
            sort_newest=args.sort_newest,
        ) as scraper:

            comments = scraper.scrape_comments(args.url)

            if not comments:
                print("\nNo comments found. Possible reasons:")
                print("  - Video has no comments or comments are disabled")
                print("  - Video is private or age-restricted")
                print("  - Cookie consent blocked loading")
                print("  - Page structure changed (needs selector update)")
                sys.exit(1)

            if args.format == "csv":
                scraper.export_to_csv(comments, str(output_path))
            else:
                scraper.export_to_json(comments, str(output_path))

            print("\n" + "=" * 50)
            print(f"SUCCESS: Exported {len(comments)} comments")
            print(f"File: {output_path.absolute()}")
            print("=" * 50)

    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
