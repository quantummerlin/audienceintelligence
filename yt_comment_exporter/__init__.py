"""
YouTube Comment Exporter — scrape comments from any public YouTube video.

Usage:
    from yt_comment_exporter import YouTubeCommentScraper, quick_scrape

    # One-liner
    comments = quick_scrape("https://www.youtube.com/watch?v=dQw4w9WgXcQ", "comments.csv")

    # Full control
    with YouTubeCommentScraper(headless=True) as scraper:
        comments = scraper.scrape_comments("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        scraper.export_to_csv(comments, "comments.csv")
"""

from .scraper import YouTubeCommentScraper, Comment, quick_scrape

__version__ = "1.0.0"
__all__ = ["YouTubeCommentScraper", "Comment", "quick_scrape"]
