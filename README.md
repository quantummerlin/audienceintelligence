# 📊 Facebook Comment Exporter

A **free, open-source** tool to extract and analyze comments from Facebook posts. Export comments to CSV or JSON, and generate insight reports.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8%2B-brightgreen.svg)
![Status](https://img.shields.io/badge/status-active-success.svg)

---

## ✨ Features

- **🎯 Free Comment Extraction** - Export comments from any public Facebook post
- **📝 Multiple Export Formats** - CSV and JSON output supported
- **🤖 Automated Scraping** - Auto-scrolls to load all comments
- **📊 Insight Reports** - Generate analysis reports (paid service)
- **⚙️ CLI & Python API** - Use from command line or import as module
- **🔒 Headless Mode** - Run without visible browser window

---

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/fb-comment-exporter.git
cd fb-comment-exporter

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

```bash
# Export comments to CSV
python fb_comment_exporter/cli.py "https://facebook.com/post/12345"

# Export to JSON
python fb_comment_exporter/cli.py "https://facebook.com/post/12345" -f json -o comments.json

# Show browser window (for debugging)
python fb_comment_exporter/cli.py "https://facebook.com/post/12345" --no-headless
```

### Python API

```python
from fb_comment_exporter import FacebookCommentScraper

# Simple one-liner
comments = quick_scrape("https://facebook.com/post/12345", "output.csv")

# Or with full control
with FacebookCommentScraper(headless=True) as scraper:
    comments = scraper.scrape_comments("https://facebook.com/post/12345")
    scraper.export_to_csv(comments, "comments.csv")
    scraper.export_to_json(comments, "comments.json")
```

---

## 📋 CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `url` | Facebook post URL (required) | - |
| `-o, --output` | Output file path | `comments.csv` |
| `-f, --format` | Output format: `csv` or `json` | `csv` |
| `--no-headless` | Show browser window | `False` |
| `--max-scrolls` | Max scroll operations | `100` |
| `--scroll-pause` | Seconds between scrolls | `2.0` |
| `--email` | Facebook email (for private posts) | - |
| `--password` | Facebook password | - |

---

## 📊 Output Format

### CSV Output

```csv
Author,Comment,Timestamp,Likes,Replies,Comment ID,URL
John Smith,"Great video!",2024-01-15,15,2,,
Jane Doe,"How much does this cost?",2024-01-15,5,0,,
```

### JSON Output

```json
{
  "exported_at": "2024-01-15T10:30:00",
  "total_comments": 150,
  "comments": [
    {
      "author": "John Smith",
      "text": "Great video!",
      "timestamp": "2024-01-15",
      "likes": 15,
      "replies_count": 2
    }
  ]
}
```

---

## 📈 Comment Intelligence Reports (Paid Service)

The free exporter extracts raw comments. For deeper insights, we offer **manual analysis reports**:

### Sample Report Preview

| Metric | Value |
|--------|-------|
| Total Comments | 1,284 |
| Positive Sentiment | 72% |
| Purchase Intent | 89 comments |
| Top Questions | "Where to buy?", "Price?" |

### Report Includes

- **🔥 Purchase Intent Detection** - Find warm leads ready to buy
- **❓ Top Questions** - Most asked questions by your audience
- **💡 Content Ideas** - What your audience wants to see
- **⭐ Top Fans** - Most engaged commenters
- **⚠️ Reputation Alerts** - Complaints and concerns

### Pricing

| Report Type | Price |
|-------------|-------|
| Single Post Analysis | $19 |
| Monthly Reports (4 posts) | $59 |
| Custom Enterprise | Contact |

**Order a report:** Send your post URL to `your-email@example.com`

---

## 🔧 How It Works

1. **Navigate** to the Facebook post URL
2. **Auto-scroll** to load all comments
3. **Extract** comment data (author, text, likes, etc.)
4. **Export** to your preferred format

---

## ⚠️ Important Notes

- **Public posts only** - Private posts require login credentials
- **Rate limits** - Facebook may limit automated scraping
- **Educational use** - Use responsibly and respect Facebook's ToS
- **Updates** - Facebook UI changes may require selector updates

---

## 🛠️ Technical Requirements

- Python 3.8+
- Google Chrome browser
- ChromeDriver (auto-managed by Selenium)

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 💬 Support

- **Issues:** [GitHub Issues](https://github.com/YOUR_USERNAME/fb-comment-exporter/issues)
- **Email:** your-email@example.com

---

## ⭐ Star History

If this tool helped you, please consider giving it a star! ⭐

---

<div align="center">

**Made with ❤️ for creators and marketers**

[⬆ Back to Top](#-facebook-comment-exporter)

</div>