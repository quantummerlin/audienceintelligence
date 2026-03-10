"""
Comment Intelligence Report Template
Sample report showing what the paid service delivers.

This module provides analysis functions for generating insight reports
from extracted comments.
"""

import re
from collections import Counter
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class CommentInsight:
    """Analysis results for a set of comments."""
    total_comments: int
    sentiment_breakdown: Dict[str, float]
    top_questions: List[Tuple[str, int]]
    purchase_intent_count: int
    content_requests: List[Tuple[str, int]]
    top_fans: List[Tuple[str, int]]
    complaints: List[Tuple[str, int]]


# Keywords for different intent types
PURCHASE_INTENT_KEYWORDS = [
    "buy", "price", "cost", "order", "purchase", "how much",
    "where can i get", "link", "link please", "available",
    "ship", "shipping", "discount", "promo", "code"
]

QUESTION_KEYWORDS = [
    "how", "what", "when", "where", "why", "can you", "could you",
    "is this", "does this", "will you", "are there"
]

CONTENT_REQUEST_KEYWORDS = [
    "tutorial", "part 2", "next part", "make a video", "do more",
    "behind the scenes", "bts", "show us", "explain", "breakdown"
]

COMPLAINT_KEYWORDS = [
    "disappointed", "bad", "terrible", "awful", "waste", "scam",
    "broken", "doesn't work", "not working", "refund", "hate",
    "worst", "poor", "issue", "problem", "complaint"
]

POSITIVE_KEYWORDS = [
    "love", "amazing", "awesome", "great", "best", "incredible",
    "fantastic", "perfect", "beautiful", "wow", "fire", "lit",
    "brilliant", "excellent", "outstanding", "😍", "🔥", "💯"
]

NEGATIVE_KEYWORDS = [
    "hate", "terrible", "awful", "worst", "bad", "disappointing",
    "poor", "waste", "scam", "fake", "boring", "👎", "😡"
]


def analyze_comments(comments: List[Dict]) -> CommentInsight:
    """
    Analyze a list of comments and generate insights.
    
    Args:
        comments: List of comment dictionaries with 'author', 'text', etc.
        
    Returns:
        CommentInsight object with analysis results
    """
    total = len(comments)
    
    # Sentiment analysis (simple keyword-based)
    positive = 0
    negative = 0
    
    for comment in comments:
        text = comment.get('text', '').lower()
        has_positive = any(kw in text for kw in POSITIVE_KEYWORDS)
        has_negative = any(kw in text for kw in NEGATIVE_KEYWORDS)
        
        if has_positive and not has_negative:
            positive += 1
        elif has_negative and not has_positive:
            negative += 1
    
    neutral = total - positive - negative
    
    sentiment = {
        'positive': round(positive / total * 100, 1) if total > 0 else 0,
        'neutral': round(neutral / total * 100, 1) if total > 0 else 0,
        'negative': round(negative / total * 100, 1) if total > 0 else 0
    }
    
    # Extract questions
    questions = []
    for comment in comments:
        text = comment.get('text', '')
        if text.strip().endswith('?') or any(kw in text.lower() for kw in QUESTION_KEYWORDS):
            questions.append(text.strip())
    
    top_questions = Counter(questions).most_common(10)
    
    # Purchase intent detection
    purchase_intent = sum(
        1 for c in comments 
        if any(kw in c.get('text', '').lower() for kw in PURCHASE_INTENT_KEYWORDS)
    )
    
    # Content requests
    content_requests = []
    for comment in comments:
        text = comment.get('text', '').lower()
        for keyword in CONTENT_REQUEST_KEYWORDS:
            if keyword in text:
                content_requests.append(keyword)
    
    top_content_requests = Counter(content_requests).most_common(5)
    
    # Top fans (most active commenters)
    authors = [c.get('author', 'Anonymous') for c in comments]
    top_fans = Counter(authors).most_common(5)
    
    # Complaints
    complaints = []
    for comment in comments:
        text = comment.get('text', '').lower()
        for keyword in COMPLAINT_KEYWORDS:
            if keyword in text:
                complaints.append((keyword, comment.get('text', '')[:100]))
                break
    
    complaint_keywords = Counter([c[0] for c in complaints]).most_common(5)
    
    return CommentInsight(
        total_comments=total,
        sentiment_breakdown=sentiment,
        top_questions=top_questions,
        purchase_intent_count=purchase_intent,
        content_requests=top_content_requests,
        top_fans=top_fans,
        complaints=complaint_keywords
    )


def generate_report_markdown(comments: List[Dict], post_url: str = "") -> str:
    """
    Generate a markdown-formatted insight report.
    
    Args:
        comments: List of comment dictionaries
        post_url: Original post URL (for reference)
        
    Returns:
        Markdown-formatted report string
    """
    insight = analyze_comments(comments)
    
    report = f"""# 📊 Comment Intelligence Report

## Overview

| Metric | Value |
|--------|-------|
| Total Comments | {insight.total_comments} |
| Positive Sentiment | {insight.sentiment_breakdown['positive']}% |
| Neutral Sentiment | {insight.sentiment_breakdown['neutral']}% |
| Negative Sentiment | {insight.sentiment_breakdown['negative']}% |

"""
    
    if post_url:
        report += f"**Source:** {post_url}\n\n"
    
    # Purchase Intent Section
    report += f"""---

## 🔥 Purchase Intent Detection

**{insight.purchase_intent_count}** comments detected with potential buying interest.

These are warm leads interested in your product/service. Consider following up!

"""
    
    # Questions Section
    if insight.top_questions:
        report += """---

## ❓ Top Audience Questions

| Question | Mentions |
|----------|----------|
"""
        for question, count in insight.top_questions[:5]:
            q_text = question[:60] + "..." if len(question) > 60 else question
            report += f"| {q_text} | {count} |\n"
    
    # Content Requests Section
    if insight.content_requests:
        report += """
---

## 💡 Content Ideas From Comments

Your audience is requesting:

"""
        for request, count in insight.content_requests:
            report += f"- **{request.title()}** ({count} mentions)\n"
    
    # Top Fans Section
    if insight.top_fans:
        report += """
---

## ⭐ Most Engaged Fans

These commenters are your biggest supporters:

"""
        for fan, count in insight.top_fans:
            if fan and fan != 'Anonymous':
                report += f"- **{fan}** - {count} comments\n"
    
    # Complaints Section
    if insight.complaints:
        report += """
---

## ⚠️ Reputation Alerts

Detected concerns in comments:

"""
        for keyword, count in insight.complaints:
            report += f"- **{keyword}** mentioned {count} times\n"
    
    # Recommendations
    report += """
---

## 📋 Recommended Actions

"""
    recommendations = []
    
    if insight.purchase_intent_count > 10:
        recommendations.append(
            "1. **High purchase intent detected** - Consider pinning product link in comments"
        )
    
    if insight.top_questions:
        recommendations.append(
            "2. **Create FAQ post** - Address the top questions from your audience"
        )
    
    if insight.content_requests:
        recommendations.append(
            "3. **Content opportunity** - Your audience wants specific content. Listen to them!"
        )
    
    if insight.sentiment_breakdown['negative'] > 10:
        recommendations.append(
            "4. **Address concerns** - Negative sentiment detected. Consider responding to complaints"
        )
    
    if not recommendations:
        recommendations.append(
            "1. **Great engagement!** - Keep doing what you're doing"
        )
    
    report += "\n".join(recommendations)
    
    report += """

---

*Report generated by Facebook Comment Exporter*
*Want detailed analysis? Contact us for a full report!*
"""
    
    return report


def generate_html_report(comments: List[Dict], post_url: str = "") -> str:
    """
    Generate an HTML-formatted insight report.
    
    Args:
        comments: List of comment dictionaries
        post_url: Original post URL
        
    Returns:
        HTML-formatted report string
    """
    insight = analyze_comments(comments)
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Comment Intelligence Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, sans-serif;
            line-height: 1.6;
            color: #333;
            background: #f5f5f5;
            padding: 20px;
        }}
        
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2em;
            margin-bottom: 10px;
        }}
        
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 20px;
            padding: 30px;
            background: #f8f9fa;
        }}
        
        .metric {{
            text-align: center;
            padding: 20px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #667eea;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 0.9em;
            margin-top: 5px;
        }}
        
        .section {{
            padding: 30px;
            border-bottom: 1px solid #eee;
        }}
        
        .section:last-child {{
            border-bottom: none;
        }}
        
        .section h2 {{
            color: #333;
            margin-bottom: 15px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .sentiment-bar {{
            display: flex;
            height: 30px;
            border-radius: 15px;
            overflow: hidden;
            margin: 20px 0;
        }}
        
        .sentiment-positive {{
            background: #10b981;
        }}
        
        .sentiment-neutral {{
            background: #6b7280;
        }}
        
        .sentiment-negative {{
            background: #ef4444;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #eee;
        }}
        
        th {{
            background: #f8f9fa;
            font-weight: 600;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .alert {{
            background: #fef3cd;
            border-left: 4px solid #f59e0b;
            padding: 15px;
            margin: 15px 0;
            border-radius: 0 8px 8px 0;
        }}
        
        .success {{
            background: #d1fae5;
            border-left: 4px solid #10b981;
        }}
        
        .cta {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .cta h3 {{
            margin-bottom: 10px;
        }}
        
        .cta p {{
            opacity: 0.9;
            margin-bottom: 20px;
        }}
        
        .btn {{
            display: inline-block;
            background: white;
            color: #667eea;
            padding: 12px 30px;
            border-radius: 25px;
            text-decoration: none;
            font-weight: 600;
            transition: transform 0.2s;
        }}
        
        .btn:hover {{
            transform: scale(1.05);
        }}
        
        .list-item {{
            display: flex;
            justify-content: space-between;
            padding: 10px 0;
            border-bottom: 1px solid #f0f0f0;
        }}
        
        .badge {{
            background: #667eea;
            color: white;
            padding: 2px 10px;
            border-radius: 10px;
            font-size: 0.85em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Comment Intelligence Report</h1>
            <p>Deep insights from your audience engagement</p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{insight.total_comments}</div>
                <div class="metric-label">Total Comments</div>
            </div>
            <div class="metric">
                <div class="metric-value">{insight.purchase_intent_count}</div>
                <div class="metric-label">Purchase Intent</div>
            </div>
            <div class="metric">
                <div class="metric-value">{insight.sentiment_breakdown['positive']}%</div>
                <div class="metric-label">Positive</div>
            </div>
            <div class="metric">
                <div class="metric-value">{len(insight.top_questions)}</div>
                <div class="metric-label">Questions</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🎭 Sentiment Breakdown</h2>
            <div class="sentiment-bar">
                <div class="sentiment-positive" style="width: {insight.sentiment_breakdown['positive']}%"></div>
                <div class="sentiment-neutral" style="width: {insight.sentiment_breakdown['neutral']}%"></div>
                <div class="sentiment-negative" style="width: {insight.sentiment_breakdown['negative']}%"></div>
            </div>
            <p>
                <span style="color: #10b981;">●</span> Positive: {insight.sentiment_breakdown['positive']}% &nbsp;&nbsp;
                <span style="color: #6b7280;">●</span> Neutral: {insight.sentiment_breakdown['neutral']}% &nbsp;&nbsp;
                <span style="color: #ef4444;">●</span> Negative: {insight.sentiment_breakdown['negative']}%
            </p>
        </div>
"""
    
    if insight.purchase_intent_count > 0:
        html += f"""
        <div class="section">
            <h2>🔥 Purchase Intent Detected</h2>
            <div class="alert success">
                <strong>{insight.purchase_intent_count} comments</strong> show buying interest!
                These are warm leads ready to convert.
            </div>
        </div>
"""
    
    if insight.top_questions:
        html += """
        <div class="section">
            <h2>❓ Top Audience Questions</h2>
            <table>
                <thead>
                    <tr>
                        <th>Question</th>
                        <th>Mentions</th>
                    </tr>
                </thead>
                <tbody>
"""
        for question, count in insight.top_questions[:5]:
            q_text = question[:50] + "..." if len(question) > 50 else question
            html += f"""
                    <tr>
                        <td>{q_text}</td>
                        <td><span class="badge">{count}</span></td>
                    </tr>
"""
        html += """
                </tbody>
            </table>
        </div>
"""
    
    if insight.content_requests:
        html += """
        <div class="section">
            <h2>💡 Content Requests</h2>
"""
        for request, count in insight.content_requests:
            html += f"""
            <div class="list-item">
                <span>{request.title()}</span>
                <span class="badge">{count} requests</span>
            </div>
"""
        html += """
        </div>
"""
    
    html += """
        <div class="cta">
            <h3>Want a Detailed Analysis?</h3>
            <p>Get custom reports with reply recommendations, lead export, and more!</p>
            <a href="#" class="btn">Order Full Report →</a>
        </div>
    </div>
</body>
</html>
"""
    
    return html


if __name__ == "__main__":
    # Sample comments for testing
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
    
    print("Generating sample report...\n")
    print(generate_report_markdown(sample_comments))