"""
Report HTML Template — Audience Intelligence
=============================================
Professional dark-theme HTML/CSS template for rendering the 15-section
Audience Intelligence Report.  Designed for print-to-PDF via Chrome.
"""

from __future__ import annotations
from datetime import datetime
from typing import Any, Dict, List, Optional
import html as html_mod
import re


# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

REPORT_CSS = r"""
/* ═══════════════════════════════════════════════════════════
   Audience Intelligence — PDF Report Stylesheet
   ═══════════════════════════════════════════════════════════ */

@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

@page {
    size: A4;
    margin: 18mm 16mm 22mm 16mm;
}

:root {
    --bg: #0b0f1e;
    --surface: #111827;
    --card: #1a2235;
    --card-alt: #1e293b;
    --border: rgba(255,255,255,0.07);
    --border-accent: rgba(99,102,241,0.25);
    --primary: #6366f1;
    --primary-light: #818cf8;
    --accent: #22d3ee;
    --accent-light: #67e8f9;
    --success: #34d399;
    --warn: #fbbf24;
    --danger: #f87171;
    --text: #e2e8f0;
    --muted: #94a3b8;
    --heading: #f8fafc;
    --ff: 'Inter', system-ui, -apple-system, sans-serif;
    --mono: 'JetBrains Mono', 'Fira Code', monospace;
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html { font-size: 11pt; }
body {
    font-family: var(--ff);
    background: var(--bg);
    color: var(--text);
    line-height: 1.65;
    -webkit-font-smoothing: antialiased;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
}
a { color: var(--accent); text-decoration: none; }

/* ── Cover Page ── */
.cover {
    page-break-after: always;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    text-align: center;
    padding: 60px 40px;
    background: linear-gradient(160deg, #0b0f1e 0%, #111827 40%, #1a1a3e 100%);
    position: relative;
    overflow: hidden;
}
.cover::before {
    content: '';
    position: absolute;
    top: -40%; left: -20%;
    width: 140%; height: 140%;
    background: radial-gradient(ellipse at 30% 50%, rgba(99,102,241,0.08) 0%, transparent 60%),
                radial-gradient(ellipse at 70% 60%, rgba(34,211,238,0.06) 0%, transparent 50%);
    pointer-events: none;
}
.cover__badge {
    display: inline-block;
    padding: 6px 20px;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    background: rgba(99,102,241,0.15);
    color: var(--primary-light);
    border: 1px solid rgba(99,102,241,0.2);
    margin-bottom: 28px;
    position: relative;
}
.cover__title {
    font-size: 2.8rem;
    font-weight: 800;
    line-height: 1.15;
    color: var(--heading);
    margin-bottom: 12px;
    position: relative;
}
.cover__title span {
    background: linear-gradient(135deg, var(--primary-light), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.cover__subtitle {
    font-size: 1.2rem;
    color: var(--muted);
    max-width: 520px;
    margin-bottom: 48px;
    position: relative;
}
.cover__meta {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 16px;
    width: 100%;
    max-width: 600px;
    position: relative;
}
.cover__meta-item {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 14px;
}
.cover__meta-label {
    font-size: 0.65rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 4px;
}
.cover__meta-value {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--heading);
}
.cover__footer {
    position: absolute;
    bottom: 32px;
    font-size: 0.7rem;
    color: var(--muted);
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── Table of Contents ── */
.toc {
    page-break-after: always;
    padding: 60px 40px;
    background: var(--bg);
}
.toc__title {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--heading);
    margin-bottom: 32px;
    padding-bottom: 16px;
    border-bottom: 2px solid var(--border-accent);
}
.toc__list {
    list-style: none;
    counter-reset: toc-counter;
}
.toc__item {
    counter-increment: toc-counter;
    display: flex;
    align-items: baseline;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
    font-size: 0.95rem;
    color: var(--text);
    transition: color 0.2s;
}
.toc__item::before {
    content: counter(toc-counter, decimal-leading-zero);
    font-family: var(--mono);
    font-size: 0.8rem;
    font-weight: 600;
    color: var(--primary-light);
    margin-right: 16px;
    min-width: 28px;
}
.toc__item-title {
    flex: 1;
    font-weight: 600;
}

/* ── Section Layout ── */
.section {
    page-break-inside: avoid;
    margin-bottom: 36px;
    padding: 28px 32px;
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    position: relative;
}
.section::before {
    content: '';
    position: absolute;
    top: 0; left: 0;
    width: 4px;
    height: 100%;
    border-radius: 16px 0 0 16px;
    background: linear-gradient(180deg, var(--primary), var(--accent));
}
.section__number {
    font-family: var(--mono);
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--primary-light);
    margin-bottom: 4px;
}
.section__title {
    font-size: 1.35rem;
    font-weight: 800;
    color: var(--heading);
    margin-bottom: 18px;
    padding-bottom: 12px;
    border-bottom: 1px solid var(--border);
}
.section__content p {
    margin-bottom: 12px;
    color: var(--text);
    line-height: 1.7;
}
.section__content ul, .section__content ol {
    margin: 10px 0 14px 0;
    padding-left: 0;
    list-style: none;
}
.section__content li {
    padding: 6px 0 6px 20px;
    position: relative;
    line-height: 1.6;
}
.section__content ul li::before {
    content: '›';
    position: absolute;
    left: 0;
    color: var(--accent);
    font-weight: 700;
}
.section__content ol {
    counter-reset: li-counter;
}
.section__content ol li {
    counter-increment: li-counter;
}
.section__content ol li::before {
    content: counter(li-counter) '.';
    position: absolute;
    left: 0;
    color: var(--primary-light);
    font-weight: 700;
    font-family: var(--mono);
    font-size: 0.85em;
}

/* ── Quote Block (for representative comments) ── */
.quote {
    background: var(--card);
    border-left: 3px solid var(--accent);
    border-radius: 0 10px 10px 0;
    padding: 14px 18px;
    margin: 10px 0;
    font-style: italic;
    color: var(--muted);
    font-size: 0.92rem;
    line-height: 1.55;
}
.quote__author {
    display: block;
    font-style: normal;
    font-weight: 600;
    font-size: 0.78rem;
    color: var(--primary-light);
    margin-top: 6px;
}

/* ── Data Cards / Stats ── */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 12px;
    margin: 16px 0;
}
.stat-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 14px;
    text-align: center;
}
.stat-value {
    font-size: 1.6rem;
    font-weight: 800;
    color: var(--heading);
    font-family: var(--mono);
}
.stat-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 4px;
}
.stat-card--positive .stat-value { color: var(--success); }
.stat-card--negative .stat-value { color: var(--danger); }
.stat-card--neutral .stat-value { color: var(--warn); }
.stat-card--accent .stat-value { color: var(--accent); }
.stat-card--primary .stat-value { color: var(--primary-light); }

/* ── Sentiment Bar ── */
.sentiment-bar {
    display: flex;
    height: 28px;
    border-radius: 14px;
    overflow: hidden;
    margin: 16px 0;
    border: 1px solid var(--border);
}
.sentiment-bar__segment {
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.7rem;
    font-weight: 700;
    color: #fff;
    min-width: 28px;
    transition: flex 0.3s;
}
.sentiment-bar__segment--positive { background: var(--success); }
.sentiment-bar__segment--negative { background: var(--danger); }
.sentiment-bar__segment--neutral { background: var(--warn); }
.sentiment-bar__segment--curious { background: var(--accent); }

/* ── Cluster / Theme Card ── */
.cluster-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 18px;
    margin: 10px 0;
    page-break-inside: avoid;
}
.cluster-card__header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 10px;
}
.cluster-card__name {
    font-weight: 700;
    font-size: 1rem;
    color: var(--heading);
}
.cluster-card__count {
    font-family: var(--mono);
    font-size: 0.78rem;
    font-weight: 600;
    color: var(--accent);
    background: rgba(34,211,238,0.1);
    padding: 3px 10px;
    border-radius: 999px;
}

/* ── Table ── */
.report-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    margin: 14px 0;
    font-size: 0.88rem;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border);
}
.report-table thead th {
    background: var(--card);
    color: var(--heading);
    font-weight: 700;
    font-size: 0.72rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 12px 14px;
    text-align: left;
    border-bottom: 2px solid var(--border-accent);
}
.report-table tbody td {
    padding: 11px 14px;
    border-bottom: 1px solid var(--border);
    vertical-align: top;
}
.report-table tbody tr:last-child td {
    border-bottom: none;
}
.report-table tbody tr:nth-child(even) {
    background: rgba(255,255,255,0.015);
}

/* ── Priority / Rating Badges ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}
.badge--hot { background: rgba(248,113,113,0.15); color: var(--danger); }
.badge--warm { background: rgba(251,191,36,0.15); color: var(--warn); }
.badge--cold { background: rgba(148,163,184,0.15); color: var(--muted); }
.badge--high { background: rgba(52,211,153,0.15); color: var(--success); }
.badge--medium { background: rgba(99,102,241,0.15); color: var(--primary-light); }

/* ── Score Display ── */
.score-display {
    display: flex;
    align-items: center;
    gap: 20px;
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 24px 28px;
    margin: 16px 0;
}
.score-circle {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 2rem;
    font-weight: 800;
    font-family: var(--mono);
    color: var(--heading);
    background: conic-gradient(var(--primary) calc(var(--score-pct) * 1%), var(--card-alt) 0);
    border: 3px solid var(--border-accent);
    flex-shrink: 0;
}
.score-details {
    flex: 1;
}
.score-details h4 {
    font-size: 1rem;
    font-weight: 700;
    color: var(--heading);
    margin-bottom: 4px;
}
.score-details p {
    font-size: 0.88rem;
    color: var(--muted);
    line-height: 1.5;
}

/* ── Reply Card (Top 10 Comments) ── */
.reply-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 18px;
    margin: 10px 0;
    page-break-inside: avoid;
}
.reply-card__rank {
    font-family: var(--mono);
    font-size: 0.7rem;
    font-weight: 700;
    color: var(--primary-light);
    margin-bottom: 6px;
}
.reply-card__comment {
    font-style: italic;
    color: var(--text);
    padding: 10px 14px;
    background: var(--card-alt);
    border-left: 3px solid var(--accent);
    border-radius: 0 8px 8px 0;
    margin-bottom: 10px;
    font-size: 0.9rem;
}
.reply-card__reason {
    font-size: 0.82rem;
    color: var(--muted);
    margin-bottom: 8px;
}
.reply-card__suggestion {
    font-size: 0.88rem;
    color: var(--success);
    padding: 8px 12px;
    background: rgba(52,211,153,0.06);
    border-radius: 8px;
    border: 1px solid rgba(52,211,153,0.12);
}
.reply-card__suggestion strong {
    color: var(--success);
}

/* ── Content Ideas Card ── */
.idea-card {
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 18px;
    margin: 10px 0;
    page-break-inside: avoid;
}
.idea-card__title {
    font-weight: 700;
    color: var(--heading);
    margin-bottom: 6px;
}
.idea-card__format {
    font-family: var(--mono);
    font-size: 0.72rem;
    font-weight: 600;
    color: var(--accent);
    background: rgba(34,211,238,0.08);
    padding: 2px 8px;
    border-radius: 6px;
    display: inline-block;
    margin-bottom: 6px;
}
.idea-card__rationale {
    font-size: 0.88rem;
    color: var(--muted);
}

/* ── Footer ── */
.page-footer {
    text-align: center;
    padding: 40px 20px;
    font-size: 0.72rem;
    color: var(--muted);
    letter-spacing: 0.04em;
    border-top: 1px solid var(--border);
    margin-top: 40px;
}
.page-footer strong {
    color: var(--primary-light);
    font-weight: 700;
}

/* ── Markdown-rendered content ── */
.md h3, .md h4 {
    color: var(--heading);
    font-weight: 700;
    margin: 16px 0 8px 0;
}
.md h3 { font-size: 1.05rem; }
.md h4 { font-size: 0.95rem; }
.md strong { color: var(--heading); }
.md em { color: var(--accent); font-style: italic; }
.md code {
    font-family: var(--mono);
    font-size: 0.85em;
    background: var(--card);
    padding: 2px 6px;
    border-radius: 4px;
    color: var(--accent);
}

/* ── Print overrides ── */
@media print {
    body { background: var(--bg); }
    .section { break-inside: avoid; }
    .cover { break-after: page; }
    .toc { break-after: page; }
}
"""


# ---------------------------------------------------------------------------
# HTML Helpers
# ---------------------------------------------------------------------------

def _esc(text: str) -> str:
    """Escape HTML entities."""
    if not text:
        return ""
    return html_mod.escape(str(text))


def _nl2br(text: str) -> str:
    """Convert newlines to <br> tags."""
    if not text:
        return ""
    return _esc(text).replace("\n", "<br>\n")


def _render_markdown_light(text: str) -> str:
    """Very lightweight Markdown→HTML for report content.
    Handles: **bold**, *italic*, `code`, - bullet lists, > blockquotes.
    """
    if not text:
        return ""
    text = _esc(text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    # Inline code
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Line breaks → <br>
    text = text.replace("\n", "<br>\n")
    return text


def _sentiment_bar(positive: float, negative: float, neutral: float, curious: float = 0) -> str:
    """Render a horizontal stacked sentiment bar."""
    segs = []
    for pct, cls, label in [
        (positive, "positive", "Positive"),
        (neutral, "neutral", "Neutral"),
        (negative, "negative", "Negative"),
        (curious, "curious", "Curious"),
    ]:
        if pct > 0:
            segs.append(
                f'<div class="sentiment-bar__segment sentiment-bar__segment--{cls}" '
                f'style="flex:{pct}">{pct:.0f}%</div>'
            )
    return f'<div class="sentiment-bar">{"".join(segs)}</div>'


def _stat_card(value: str, label: str, variant: str = "") -> str:
    cls = f" stat-card--{variant}" if variant else ""
    return (
        f'<div class="stat-card{cls}">'
        f'<div class="stat-value">{_esc(str(value))}</div>'
        f'<div class="stat-label">{_esc(label)}</div>'
        f'</div>'
    )


def _quote_block(text: str, author: str = "") -> str:
    html = f'<div class="quote">{_render_markdown_light(text)}'
    if author:
        html += f'<span class="quote__author">— {_esc(author)}</span>'
    html += '</div>'
    return html


def _cluster_card(name: str, count: int, quotes: List[str]) -> str:
    q_html = "".join(_quote_block(q) for q in quotes[:3])
    return (
        f'<div class="cluster-card">'
        f'<div class="cluster-card__header">'
        f'<span class="cluster-card__name">{_esc(name)}</span>'
        f'<span class="cluster-card__count">{count} comments</span>'
        f'</div>{q_html}</div>'
    )


def _reply_card(rank: int, comment: str, reason: str, suggestion: str) -> str:
    return (
        f'<div class="reply-card">'
        f'<div class="reply-card__rank">#{rank}</div>'
        f'<div class="reply-card__comment">{_render_markdown_light(comment)}</div>'
        f'<div class="reply-card__reason">{_render_markdown_light(reason)}</div>'
        f'<div class="reply-card__suggestion"><strong>Suggested Reply:</strong> '
        f'{_render_markdown_light(suggestion)}</div>'
        f'</div>'
    )


def _idea_card(title: str, fmt: str, rationale: str) -> str:
    return (
        f'<div class="idea-card">'
        f'<div class="idea-card__title">{_esc(title)}</div>'
        f'<span class="idea-card__format">{_esc(fmt)}</span>'
        f'<div class="idea-card__rationale">{_render_markdown_light(rationale)}</div>'
        f'</div>'
    )


def _score_display(score: int, reasoning: str, prediction: str = "") -> str:
    pct = score * 10
    return (
        f'<div class="score-display" style="--score-pct:{pct}">'
        f'<div class="score-circle">{score}</div>'
        f'<div class="score-details">'
        f'<h4>Viral Probability Score</h4>'
        f'<p>{_render_markdown_light(reasoning)}</p>'
        + (f'<p style="margin-top:8px;color:var(--accent);font-weight:600;">'
           f'{_render_markdown_light(prediction)}</p>' if prediction else '')
        + '</div></div>'
    )


def _badge(text: str, variant: str = "medium") -> str:
    return f'<span class="badge badge--{variant}">{_esc(text)}</span>'


# ---------------------------------------------------------------------------
# Section Renderers
# ---------------------------------------------------------------------------

SECTION_TITLES = [
    "Overview",
    "Sentiment Analysis",
    "Key Themes & Clusters",
    "Audience Questions",
    "Audience Frustrations",
    "Audience Desires & Requests",
    "Viral Content Triggers",
    "Content Opportunities",
    "Engagement Opportunities",
    "Lead & Sales Opportunities",
    "Future Product Opportunities",
    "Audience Profile",
    "Top 10 Comments to Reply To",
    "Strategic Recommendations",
    "Viral Probability Score",
]


def _render_section(num: int, title: str, content_html: str) -> str:
    return (
        f'<div class="section">'
        f'<div class="section__number">Section {num:02d}</div>'
        f'<h2 class="section__title">{_esc(title)}</h2>'
        f'<div class="section__content md">{content_html}</div>'
        f'</div>'
    )


def _render_generic_section(num: int, title: str, data: Any) -> str:
    """Render a section from text or list data when no specialised renderer exists."""
    if isinstance(data, str):
        content = _render_markdown_light(data)
    elif isinstance(data, list):
        items = "".join(f"<li>{_render_markdown_light(str(i))}</li>" for i in data)
        content = f"<ul>{items}</ul>"
    elif isinstance(data, dict):
        # Render each key as a sub-heading with its value
        parts = []
        for k, v in data.items():
            parts.append(f"<h4>{_esc(str(k))}</h4>")
            if isinstance(v, list):
                items = "".join(f"<li>{_render_markdown_light(str(i))}</li>" for i in v)
                parts.append(f"<ul>{items}</ul>")
            elif isinstance(v, str):
                parts.append(f"<p>{_render_markdown_light(v)}</p>")
            else:
                parts.append(f"<p>{_esc(str(v))}</p>")
        content = "".join(parts)
    else:
        content = f"<p>{_esc(str(data))}</p>"
    return _render_section(num, title, content)


def _render_overview_section(data: dict) -> str:
    """Section 1: Overview with stat cards."""
    cards = []
    if "platform" in data:
        cards.append(_stat_card(str(data["platform"]).title(), "Platform", "accent"))
    if "total_raw" in data:
        cards.append(_stat_card(str(data["total_raw"]), "Raw Comments"))
    if "total_clean" in data:
        cards.append(_stat_card(str(data["total_clean"]), "Clean Comments", "positive"))
    if "removed" in data:
        cards.append(_stat_card(str(data["removed"]), "Removed", "negative"))

    stats_html = f'<div class="stats-grid">{"".join(cards)}</div>' if cards else ""
    summary = _render_markdown_light(data.get("summary", ""))

    return _render_section(1, "Overview", stats_html + f"<p>{summary}</p>")


def _render_sentiment_section(data: dict) -> str:
    """Section 2: Sentiment Analysis with bar chart."""
    pos = data.get("positive", 0)
    neg = data.get("negative", 0)
    neut = data.get("neutral", 0)
    cur = data.get("curious", 0)

    bar = _sentiment_bar(pos, neg, neut, cur)

    cards = [
        _stat_card(f"{pos:.0f}%", "Positive", "positive"),
        _stat_card(f"{neg:.0f}%", "Negative", "negative"),
        _stat_card(f"{neut:.0f}%", "Neutral", "neutral"),
    ]
    if cur:
        cards.append(_stat_card(f"{cur:.0f}%", "Curious", "accent"))
    grid = f'<div class="stats-grid">{"".join(cards)}</div>'

    tones = data.get("tones", "")
    shifts = data.get("shifts", "")
    extra = ""
    if tones:
        extra += f"<h4>Dominant Emotional Tones</h4><p>{_render_markdown_light(tones)}</p>"
    if shifts:
        extra += f"<h4>Sentiment Shifts</h4><p>{_render_markdown_light(shifts)}</p>"

    return _render_section(2, "Sentiment Analysis", bar + grid + extra)


def _render_clusters_section(data: Any) -> str:
    """Section 3: Key Themes & Clusters."""
    if isinstance(data, list):
        cards = ""
        for cl in data:
            if isinstance(cl, dict):
                cards += _cluster_card(
                    cl.get("name", "Theme"),
                    cl.get("count", 0),
                    cl.get("quotes", cl.get("examples", [])),
                )
            else:
                cards += f"<p>{_render_markdown_light(str(cl))}</p>"
        return _render_section(3, "Key Themes & Clusters", cards)
    return _render_generic_section(3, "Key Themes & Clusters", data)


def _render_top_comments_section(data: Any) -> str:
    """Section 13: Top 10 Comments to Reply To."""
    if isinstance(data, list):
        cards = ""
        for i, item in enumerate(data, 1):
            if isinstance(item, dict):
                cards += _reply_card(
                    i,
                    item.get("comment", ""),
                    item.get("reason", item.get("why", "")),
                    item.get("suggestion", item.get("reply", "")),
                )
            else:
                cards += _quote_block(str(item))
        return _render_section(13, "Top 10 Comments to Reply To", cards)
    return _render_generic_section(13, "Top 10 Comments to Reply To", data)


def _render_content_opportunities_section(data: Any) -> str:
    """Section 8: Content Opportunities."""
    if isinstance(data, list):
        cards = ""
        for item in data:
            if isinstance(item, dict):
                cards += _idea_card(
                    item.get("title", item.get("hook", "")),
                    item.get("format", ""),
                    item.get("rationale", item.get("why", "")),
                )
            else:
                cards += f"<p>{_render_markdown_light(str(item))}</p>"
        return _render_section(8, "Content Opportunities", cards)
    return _render_generic_section(8, "Content Opportunities", data)


def _render_leads_section(data: Any) -> str:
    """Section 10: Lead & Sales Opportunities."""
    if isinstance(data, dict):
        # Render lead counts by quality
        counts_html = ""
        for quality in ["hot", "warm", "cold"]:
            if quality in data:
                counts_html += _stat_card(
                    str(data[quality]),
                    f"{quality.title()} Leads",
                    {"hot": "negative", "warm": "neutral", "cold": ""}.get(quality, ""),
                )
        grid = f'<div class="stats-grid">{counts_html}</div>' if counts_html else ""

        rest_keys = [k for k in data if k not in ("hot", "warm", "cold")]
        rest_html = ""
        for k in rest_keys:
            v = data[k]
            if isinstance(v, list):
                items = "".join(f"<li>{_render_markdown_light(str(i))}</li>" for i in v)
                rest_html += f"<h4>{_esc(str(k).replace('_', ' ').title())}</h4><ul>{items}</ul>"
            elif isinstance(v, str):
                rest_html += f"<h4>{_esc(str(k).replace('_', ' ').title())}</h4><p>{_render_markdown_light(v)}</p>"

        return _render_section(10, "Lead & Sales Opportunities", grid + rest_html)
    return _render_generic_section(10, "Lead & Sales Opportunities", data)


def _render_viral_score_section(data: Any) -> str:
    """Section 15: Viral Probability Score."""
    if isinstance(data, dict):
        score = int(data.get("score", 5))
        reasoning = data.get("reasoning", "")
        prediction = data.get("prediction", "")
        drivers = data.get("drivers", "")
        comparison = data.get("comparison", "")

        display = _score_display(score, reasoning, prediction)
        extra = ""
        if drivers:
            extra += f"<h4>Key Drivers</h4><p>{_render_markdown_light(drivers)}</p>"
        if comparison:
            extra += f"<h4>Platform Comparison</h4><p>{_render_markdown_light(comparison)}</p>"

        return _render_section(15, "Viral Probability Score", display + extra)
    elif isinstance(data, (int, float)):
        return _render_section(15, "Viral Probability Score",
                               _score_display(int(data), ""))
    return _render_generic_section(15, "Viral Probability Score", data)


# Mapping of section indices to specialised renderers
SPECIALISED_RENDERERS = {
    1: _render_overview_section,
    2: _render_sentiment_section,
    3: _render_clusters_section,
    8: _render_content_opportunities_section,
    10: _render_leads_section,
    13: _render_top_comments_section,
    15: _render_viral_score_section,
}


# ---------------------------------------------------------------------------
# Main Render Function
# ---------------------------------------------------------------------------

def render_report_html(analysis: Dict[str, Any]) -> str:
    """
    Render a complete Audience Intelligence Report as a standalone HTML
    document from a structured analysis dict.

    Expected top-level keys (all optional — missing sections are skipped):
        meta: {platform, url, client, date, total_raw, total_clean}
        sections: {
            overview: {...},
            sentiment: {...},
            clusters: [...],
            questions: str | list,
            frustrations: str | list,
            desires: str | list,
            viral_triggers: str | list,
            content_opportunities: [...],
            engagement_opportunities: str | list,
            leads: {...},
            product_opportunities: str | list,
            audience_profile: str | dict,
            top_comments: [...],
            recommendations: str | list,
            viral_score: {score, reasoning, ...}
        }

    If the data is a flat dict keyed by section number/name, it will
    also be handled.
    """

    meta = analysis.get("meta", {})
    sections_data = analysis.get("sections", analysis)

    # Build cover page
    platform = meta.get("platform", sections_data.get("platform", "Social Media"))
    client = meta.get("client", sections_data.get("client", ""))
    post_url = meta.get("url", sections_data.get("url", ""))
    date = meta.get("date", datetime.now().strftime("%d %B %Y"))
    total_raw = meta.get("total_raw", sections_data.get("total_raw", ""))
    total_clean = meta.get("total_clean", sections_data.get("total_clean", ""))

    cover_meta_items = []
    if platform:
        cover_meta_items.append(
            f'<div class="cover__meta-item">'
            f'<div class="cover__meta-label">Platform</div>'
            f'<div class="cover__meta-value">{_esc(str(platform).title())}</div></div>'
        )
    if total_raw or total_clean:
        val = total_clean or total_raw
        cover_meta_items.append(
            f'<div class="cover__meta-item">'
            f'<div class="cover__meta-label">Comments Analysed</div>'
            f'<div class="cover__meta-value">{_esc(str(val))}</div></div>'
        )
    cover_meta_items.append(
        f'<div class="cover__meta-item">'
        f'<div class="cover__meta-label">Report Date</div>'
        f'<div class="cover__meta-value">{_esc(date)}</div></div>'
    )
    if client:
        cover_meta_items.append(
            f'<div class="cover__meta-item">'
            f'<div class="cover__meta-label">Prepared For</div>'
            f'<div class="cover__meta-value">{_esc(client)}</div></div>'
        )

    cover_html = (
        f'<div class="cover">'
        f'<div class="cover__badge">Audience Intelligence Report</div>'
        f'<h1 class="cover__title"><span>Audience Intelligence</span><br>Report</h1>'
        f'<p class="cover__subtitle">Deep-dive analysis of audience sentiment, themes, '
        f'opportunities, and strategic recommendations.</p>'
        f'<div class="cover__meta">{"".join(cover_meta_items)}</div>'
        f'<div class="cover__footer">Quantum Merlin Ltd &middot; audienceintelligence.quantummerlin.com</div>'
        f'</div>'
    )

    # Build table of contents
    toc_items = "".join(
        f'<li class="toc__item"><span class="toc__item-title">{_esc(t)}</span></li>'
        for t in SECTION_TITLES
    )
    toc_html = (
        f'<div class="toc">'
        f'<h2 class="toc__title">Table of Contents</h2>'
        f'<ol class="toc__list">{toc_items}</ol>'
        f'</div>'
    )

    # Map section keys to numbers
    KEY_MAP = {
        "overview": 1,
        "sentiment": 2,
        "clusters": 3, "themes": 3, "key_themes": 3,
        "questions": 4, "audience_questions": 4,
        "frustrations": 5, "audience_frustrations": 5,
        "desires": 6, "audience_desires": 6, "requests": 6,
        "viral_triggers": 7, "viral_content_triggers": 7,
        "content_opportunities": 8,
        "engagement_opportunities": 9, "engagement": 9,
        "leads": 10, "lead_opportunities": 10, "sales": 10,
        "product_opportunities": 11, "future_products": 11,
        "audience_profile": 12, "profile": 12, "demographics": 12,
        "top_comments": 13, "top_10": 13, "replies": 13,
        "recommendations": 14, "strategic_recommendations": 14, "strategy": 14,
        "viral_score": 15, "viral_probability": 15,
    }

    # Collect section data
    section_data_by_num: Dict[int, Any] = {}
    for key, val in sections_data.items():
        num = KEY_MAP.get(key)
        if num:
            section_data_by_num[num] = val
        else:
            # Try numeric keys: "1", "01", "section_1"
            m = re.match(r"(\d+)", str(key))
            if m:
                n = int(m.group(1))
                if 1 <= n <= 15:
                    section_data_by_num[n] = val

    # Render each section
    sections_html = ""
    for num in range(1, 16):
        data = section_data_by_num.get(num)
        if data is None:
            continue
        renderer = SPECIALISED_RENDERERS.get(num)
        if renderer:
            sections_html += renderer(data)
        else:
            sections_html += _render_generic_section(num, SECTION_TITLES[num - 1], data)

    # Footer
    footer_html = (
        f'<div class="page-footer">'
        f'Generated by <strong>Audience Intelligence</strong> &middot; '
        f'Quantum Merlin Ltd &middot; {_esc(date)}<br>'
        f'audienceintelligence.quantummerlin.com'
        f'</div>'
    )

    # Assemble full document
    return (
        f'<!DOCTYPE html><html lang="en"><head>'
        f'<meta charset="UTF-8">'
        f'<meta name="viewport" content="width=device-width, initial-scale=1.0">'
        f'<title>Audience Intelligence Report'
        + (f' — {_esc(client)}' if client else '')
        + f'</title>'
        f'<style>{REPORT_CSS}</style>'
        f'</head><body>'
        f'{cover_html}'
        f'{toc_html}'
        f'<main style="padding:20px 0">{sections_html}</main>'
        f'{footer_html}'
        f'</body></html>'
    )
