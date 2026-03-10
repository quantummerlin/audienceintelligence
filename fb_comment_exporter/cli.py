#!/usr/bin/env python3
"""
Command-line interface for Facebook Comment Exporter.
"""

import argparse
import sys
from pathlib import Path

try:
    from .scraper import FacebookCommentScraper, quick_scrape
except ImportError:
    import os
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from scraper import FacebookCommentScraper, quick_scrape


def main():
    parser = argparse.ArgumentParser(
        description="Export Facebook comments to CSV or JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python cli.py https://facebook.com/post/12345

  # Specify output file
  python cli.py https://facebook.com/post/12345 -o my_comments.csv

  # Export to JSON
  python cli.py https://facebook.com/post/12345 -f json -o comments.json

  # Visible browser mode (for debugging)
  python cli.py https://facebook.com/post/12345 --no-headless

  # With login (for private posts)
  python cli.py https://facebook.com/post/12345 --email user@email.com
        """
    )
    
    parser.add_argument(
        "url",
        help="URL of the Facebook post to scrape"
    )
    
    parser.add_argument(
        "-o", "--output",
        default="comments.csv",
        help="Output file path (default: comments.csv)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["csv", "json"],
        default="csv",
        help="Output format (default: csv)"
    )
    
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Show browser window (useful for debugging)"
    )
    
    parser.add_argument(
        "--max-scrolls",
        type=int,
        default=100,
        help="Maximum scroll operations (default: 100)"
    )
    
    parser.add_argument(
        "--scroll-pause",
        type=float,
        default=2.5,
        help="Seconds to wait between scrolls (default: 2.5)"
    )

    parser.add_argument(
        "--max-load-more",
        type=int,
        default=30,
        help="Max 'View more comments' button clicks to prevent browser crash (default: 30)"
    )

    parser.add_argument(
        "--max-reply-expansions",
        type=int,
        default=20,
        help="Max reply thread expansions (default: 20)"
    )

    parser.add_argument(
        "--no-expand-replies",
        action="store_true",
        help="Skip expanding reply threads (faster but fewer results)"
    )

    parser.add_argument(
        "--email",
        help="Facebook email for login (optional)"
    )
    
    parser.add_argument(
        "--password",
        help="Facebook password for login (optional)"
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    args = parser.parse_args()
    
    # Validate output format
    output_path = Path(args.output)
    if args.format == "csv" and output_path.suffix != ".csv":
        output_path = output_path.with_suffix(".csv")
    elif args.format == "json" and output_path.suffix != ".json":
        output_path = output_path.with_suffix(".json")
    
    print(f"Facebook Comment Exporter v1.0.0")
    print(f"Target: {args.url}")
    print(f"Output: {output_path}")
    print("-" * 50)
    
    try:
        with FacebookCommentScraper(
            headless=not args.no_headless,
            max_scrolls=args.max_scrolls,
            scroll_pause=args.scroll_pause,
            expand_replies=not args.no_expand_replies,
            max_load_more_clicks=args.max_load_more,
            max_reply_expansions=args.max_reply_expansions,
        ) as scraper:
            
            comments = scraper.scrape_comments(
                args.url,
                login_email=args.email,
                login_password=args.password
            )
            
            if not comments:
                print("\nNo comments found. Possible reasons:")
                print("  - Post has no comments")
                print("  - Post is private (try --email and --password)")
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