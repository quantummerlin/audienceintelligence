"""
Instagram Comment Exporter — scrape comments from any public Instagram post or reel.

Usage:
    from ig_comment_exporter import InstagramCommentScraper, quick_scrape

    # One-liner
    comments = quick_scrape("https://www.instagram.com/p/ABC123/", "comments.csv")

    # Full control
    with InstagramCommentScraper(headless=True) as scraper:
        comments = scraper.scrape_comments("https://www.instagram.com/p/ABC123/")
        scraper.export_to_csv(comments, "comments.csv")
"""

from .scraper import InstagramCommentScraper, Comment, quick_scrape

__version__ = "1.0.0"
__all__ = ["InstagramCommentScraper", "Comment", "quick_scrape"]
