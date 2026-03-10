"""
Facebook Comment Exporter
A free, open-source tool to extract comments from Facebook posts.
"""

from .scraper import (
    FacebookCommentScraper,
    Comment,
    quick_scrape
)

__version__ = "1.0.0"
__author__ = "Open Source Contributors"
__all__ = [
    "FacebookCommentScraper",
    "Comment", 
    "quick_scrape"
]