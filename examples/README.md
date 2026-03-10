# Examples

This folder contains example scripts demonstrating how to use the Facebook Comment Exporter.

## Files

### demo.py
A comprehensive demo showing all major features:
- Basic usage (one-liner)
- Advanced usage with custom settings
- Login for private posts
- Report generation

Run with:
```bash
cd examples
python demo.py
```

### Quick Examples

#### Extract comments to CSV
```python
from fb_comment_exporter import quick_scrape

comments = quick_scrape(
    "https://facebook.com/post/12345",
    "comments.csv"
)
```

#### Extract with custom settings
```python
from fb_comment_exporter import FacebookCommentScraper

with FacebookCommentScraper(
    headless=True,
    max_scrolls=50,
    scroll_pause=1.5
) as scraper:
    comments = scraper.scrape_comments("https://facebook.com/post/12345")
    scraper.export_to_csv(comments, "output.csv")
    scraper.export_to_json(comments, "output.json")
```

#### Generate insight report
```python
from fb_comment_exporter.report_template import generate_report_markdown

# After extracting comments
report = generate_report_markdown(comments)
print(report)

# Or save to file
with open("report.md", "w") as f:
    f.write(report)
```

## Need Help?

Check the main [README](../README.md) for full documentation.