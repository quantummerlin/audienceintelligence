#!/usr/bin/env python3
"""
Instagram Comment Exporter — CLI
=================================
Command-line interface for the Instagram comment scraper.

Usage:
    python -m ig_comment_exporter.cli <url> [options]
    ig-export <url> [options]

Examples:
    ig-export https://www.instagram.com/p/ABC123/
    ig-export https://www.instagram.com/reel/XYZ789/ -o comments.json -f json
    ig-export https://www.instagram.com/p/ABC123/ --no-headless --max-scrolls 200
"""

import argparse
import sys
from pathlib import Path

from .scraper import InstagramCommentScraper


def main():
    parser = argparse.ArgumentParser(
        prog="ig-export",
        description="Extract comments from any public Instagram post or reel.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  ig-export https://www.instagram.com/p/ABC123/\n"
            "  ig-export https://www.instagram.com/reel/XYZ789/ -o out.json -f json\n"
            "  ig-export https://www.instagram.com/p/ABC123/ --no-headless\n"
        ),
    )

    parser.add_argument("url", help="Instagram post or reel URL")

    parser.add_argument(
        "-o", "--output",
        default="ig_comments.csv",
        help="Output file path (default: ig_comments.csv)",
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
        default=150,
        help="Maximum scroll iterations (default: 150)",
    )

    parser.add_argument(
        "--scroll-pause",
        type=float,
        default=2.0,
        help="Pause between scrolls in seconds (default: 2.0)",
    )

    parser.add_argument(
        "--max-load-more",
        type=int,
        default=60,
        help="Maximum 'load more' clicks (default: 60)",
    )

    parser.add_argument(
        "--max-reply-expansions",
        type=int,
        default=40,
        help="Maximum reply thread expansions (default: 40)",
    )

    parser.add_argument(
        "--no-expand-replies",
        action="store_true",
        help="Skip expanding reply threads",
    )

    parser.add_argument(
        "--username",
        help="Instagram username for login (optional)",
    )

    parser.add_argument(
        "--password",
        help="Instagram password for login (optional)",
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

    print(f"Instagram Comment Exporter v1.0.0")
    print(f"Target: {args.url}")
    print(f"Output: {output_path}")
    print("-" * 50)

    try:
        with InstagramCommentScraper(
            headless=not args.no_headless,
            max_scrolls=args.max_scrolls,
            scroll_pause=args.scroll_pause,
            expand_replies=not args.no_expand_replies,
            max_load_more_clicks=args.max_load_more,
            max_reply_expansions=args.max_reply_expansions,
        ) as scraper:

            comments = scraper.scrape_comments(
                args.url,
                login_username=args.username,
                login_password=args.password,
            )

            if not comments:
                print("\nNo comments found. Possible reasons:")
                print("  - Post has no comments")
                print("  - Post is private (try --username and --password)")
                print("  - Instagram login wall blocked access")
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
