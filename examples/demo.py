#!/usr/bin/env python3
"""
Demo script showing how to use Facebook Comment Exporter
"""

import sys
sys.path.insert(0, '..')

from fb_comment_exporter import FacebookCommentScraper, quick_scrape


def demo_basic_usage():
    """Basic usage example - one-liner"""
    print("=== Basic Usage Demo ===\n")
    
    # Example URL (replace with real Facebook post URL)
    url = "https://www.facebook.com/posts/EXAMPLE"
    
    print(f"URL: {url}")
    print("This would extract all comments and save to comments.csv\n")
    
    # Uncomment below to run with real URL:
    # comments = quick_scrape(url, "comments.csv")
    # print(f"Extracted {len(comments)} comments")


def demo_advanced_usage():
    """Advanced usage with full control"""
    print("\n=== Advanced Usage Demo ===\n")
    
    url = "https://www.facebook.com/posts/EXAMPLE"
    output_csv = "output/comments.csv"
    output_json = "output/comments.json"
    
    print("Creating scraper with custom settings...")
    print("  - Headless mode: True")
    print("  - Max scrolls: 50")
    print("  - Scroll pause: 1.5 seconds\n")
    
    # Uncomment below to run with real URL:
    # with FacebookCommentScraper(
    #     headless=True,
    #     max_scrolls=50,
    #     scroll_pause=1.5
    # ) as scraper:
    #     comments = scraper.scrape_comments(url)
    #     
    #     # Export to both formats
    #     scraper.export_to_csv(comments, output_csv)
    #     scraper.export_to_json(comments, output_json)
    #     
    #     print(f"Total comments: {len(comments)}")
    #     
    #     # Print first 5 comments
    #     for i, comment in enumerate(comments[:5], 1):
    #         print(f"{i}. {comment.author}: {comment.text[:50]}...")


def demo_with_login():
    """Example with login for private posts"""
    print("\n=== Login Demo ===\n")
    
    url = "https://www.facebook.com/posts/PRIVATE_POST"
    
    print("For private posts, you can provide login credentials:")
    print("  scraper.scrape_comments(url, login_email='your@email.com', login_password='yourpass')\n")
    
    print("WARNING: Never hardcode credentials in scripts!")
    print("    Use environment variables instead:\n")
    print("    import os")
    print("    email = os.environ.get('FB_EMAIL')")
    print("    password = os.environ.get('FB_PASSWORD')")


def demo_report_generation():
    """Demo report generation from extracted comments"""
    print("\n=== Report Generation Demo ===\n")
    
    # Sample comments
    sample_comments = [
        {"author": "John Doe", "text": "This is amazing! Love it! 😍", "likes": 5},
        {"author": "Jane Smith", "text": "How much does this cost?", "likes": 3},
        {"author": "Bob Wilson", "text": "Where can I buy this? Link please!", "likes": 2},
        {"author": "Alice Brown", "text": "Can you make a tutorial?", "likes": 10},
        {"author": "Charlie Green", "text": "Great content! Keep it up! 🔥", "likes": 7},
        {"author": "Diana Prince", "text": "Disappointed with the shipping delay", "likes": 1},
        {"author": "Eve Adams", "text": "When is part 2 coming?", "likes": 4},
        {"author": "Frank Miller", "text": "This is terrible, waste of money", "likes": 0},
    ]
    
    # Import report module
    from fb_comment_exporter.report_template import (
        analyze_comments, 
        generate_report_markdown,
        generate_html_report
    )
    
    # Generate analysis
    insight = analyze_comments(sample_comments)
    
    print(f"Total Comments: {insight.total_comments}")
    print(f"Positive: {insight.sentiment_breakdown['positive']}%")
    print(f"Negative: {insight.sentiment_breakdown['negative']}%")
    print(f"Purchase Intent: {insight.purchase_intent_count} comments")
    
    print("\n--- Sample Report Preview ---\n")
    
    # Generate markdown report
    report = generate_report_markdown(sample_comments)
    print(report[:500] + "...\n")
    
    print("Full report can be generated as:")
    print("  - Markdown (.md)")
    print("  - HTML (.html) for web viewing")


if __name__ == "__main__":
    print("=" * 50)
    print("Facebook Comment Exporter - Demo")
    print("=" * 50)
    
    demo_basic_usage()
    demo_advanced_usage()
    demo_with_login()
    demo_report_generation()
    
    print("\n" + "=" * 50)
    print("Demo complete! Check the source code for details.")
    print("=" * 50)