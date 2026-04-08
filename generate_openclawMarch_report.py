"""
generate_openclawMarch_report.py
=================================
Generates the complete 18-section Audience Intelligence Report for the
March 2026 OpenClaw Reddit dataset. All intelligence content is freshly
written from the actual March data (100 posts, 21,808 comments, 35 subreddits).

Usage:
    python generate_openclawMarch_report.py
    python generate_openclawMarch_report.py --out outputs/report_march_custom.html
"""
import json
import os
import argparse
from datetime import datetime


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="redditopenclawMarch.json", help="Path to March JSON dataset")
    p.add_argument("--out",   default=None, help="Output HTML path (auto-named if omitted)")
    return p.parse_args()


ARGS = _parse_args()
INPUT_FILE = ARGS.input

if ARGS.out:
    OUT_PATH = ARGS.out
else:
    OUT_PATH = os.path.join("outputs", "report_openclawMarch_fresh_2026-03-16.html")

# ── Load posts ─────────────────────────────────────────────────────────────────
def _load_posts(path):
    posts = {}
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    for item in raw:
        pid = item.get("id", "")
        if pid and pid not in posts:
            posts[pid] = item
    result = list(posts.values())
    result.sort(key=lambda p: p.get("score", 0), reverse=True)
    return result


POSTS = _load_posts(INPUT_FILE)
TOTAL_POSTS = len(POSTS)
TOTAL_COMMENTS = sum(p.get("num_comments", 0) for p in POSTS)
TOP_SCORE = POSTS[0]["score"] if POSTS else 0

print(f"Loaded {TOTAL_POSTS} posts, {TOTAL_COMMENTS:,} comments from {INPUT_FILE}")

# ─── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
@page { size: A4; margin: 18mm 16mm 22mm 16mm; }
:root {
  --bg:#0b0f1e; --surface:#111827; --card:#1a2235; --card-alt:#1e293b;
  --border:rgba(255,255,255,0.07); --border-accent:rgba(99,102,241,0.25);
  --primary:#6366f1; --primary-light:#818cf8; --accent:#22d3ee;
  --accent-light:#67e8f9; --success:#34d399; --warn:#fbbf24;
  --danger:#f87171; --text:#e2e8f0; --muted:#94a3b8; --heading:#f8fafc;
  --ff:'Inter',system-ui,sans-serif; --mono:'JetBrains Mono','Fira Code',monospace;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{font-size:11pt}
body{font-family:var(--ff);background:var(--bg);color:var(--text);line-height:1.65;-webkit-font-smoothing:antialiased;-webkit-print-color-adjust:exact;print-color-adjust:exact}
a{color:var(--accent);text-decoration:none}
h1,h2,h3,h4{color:var(--heading)}
p{margin-bottom:12px;font-size:0.88rem}
ul,ol{margin:0 0 12px 20px;font-size:0.88rem}
li{margin-bottom:4px}
code{background:rgba(255,255,255,.07);padding:2px 6px;border-radius:4px;font-size:0.82em;color:var(--accent);font-family:var(--mono)}

/* Cover */
.cover{page-break-after:always;display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:100vh;text-align:center;padding:60px 40px;background:linear-gradient(160deg,#0b0f1e 0%,#111827 40%,#1a1a3e 100%);position:relative;overflow:hidden}
.cover::before{content:'';position:absolute;top:-40%;left:-20%;width:140%;height:140%;background:radial-gradient(ellipse at 30% 50%,rgba(99,102,241,0.08) 0%,transparent 60%),radial-gradient(ellipse at 70% 60%,rgba(34,211,238,0.06) 0%,transparent 50%);pointer-events:none}
.cover__badge{display:inline-block;background:linear-gradient(135deg,var(--primary),#8b5cf6);color:#fff;font-size:0.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:5px 14px;border-radius:20px;margin-bottom:28px;position:relative;z-index:1}
.cover h1{font-size:2.6rem;font-weight:800;color:var(--heading);margin-bottom:16px;position:relative;z-index:1;line-height:1.2}
.cover h1 span{color:var(--accent)}
.cover__subtitle{font-size:1rem;color:var(--muted);max-width:600px;margin-bottom:40px;position:relative;z-index:1}
.cover__meta{display:flex;gap:40px;flex-wrap:wrap;justify-content:center;position:relative;z-index:1;margin-bottom:40px}
.cover__meta-item{text-align:center}
.cover__meta-value{font-size:1.8rem;font-weight:800;color:var(--heading);display:block;line-height:1}
.cover__meta-label{font-size:0.72rem;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;margin-top:4px}
.cover__client{background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:12px;padding:16px 24px;font-size:0.82rem;color:var(--muted);position:relative;z-index:1}
.cover__client strong{color:var(--text)}
.cover__footer{margin-top:32px;font-size:0.72rem;color:rgba(148,163,184,0.5);position:relative;z-index:1}

/* Layout */
main{max-width:920px;margin:0 auto;padding:48px 32px}
.section{margin-bottom:56px;padding-bottom:40px;border-bottom:1px solid var(--border)}
.section:last-child{border-bottom:none}
.section__number{font-size:0.68rem;color:var(--primary-light);font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px}
.section__title{font-size:1.4rem;font-weight:700;color:var(--heading);margin-bottom:6px}
.section__subtitle{font-size:0.88rem;color:var(--muted);margin-bottom:20px}

/* Stats Grid */
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:14px;margin:16px 0 24px}
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 14px;text-align:center;transition:border-color .2s}
.stat-card:hover{border-color:var(--border-accent)}
.stat-value{font-size:2rem;font-weight:800;color:var(--heading);display:block;line-height:1}
.stat-label{font-size:0.7rem;color:var(--muted);margin-top:6px;text-transform:uppercase;letter-spacing:.07em}
.stat-card--positive .stat-value{color:var(--success)}
.stat-card--negative .stat-value{color:var(--danger)}
.stat-card--neutral .stat-value{color:var(--warn)}
.stat-card--accent .stat-value{color:var(--accent)}
.stat-card--purple .stat-value{color:var(--primary-light)}

/* Sentiment Bar */
.sentiment-bar{display:flex;border-radius:10px;overflow:hidden;height:36px;margin:16px 0 8px}
.sentiment-bar__segment{display:flex;align-items:center;justify-content:center;font-size:0.74rem;font-weight:600;color:#fff;padding:0 8px;white-space:nowrap;overflow:hidden}
.sentiment-bar__segment--positive{background:var(--success)}
.sentiment-bar__segment--negative{background:var(--danger)}
.sentiment-bar__segment--neutral{background:var(--warn)}
.sentiment-bar__segment--mixed{background:var(--primary)}
.sentiment-bar__legend{display:flex;gap:16px;flex-wrap:wrap;font-size:0.74rem;color:var(--muted);margin-bottom:16px}
.sentiment-bar__legend span::before{content:'';display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:middle}
.leg-pos::before{background:var(--success)} .leg-neg::before{background:var(--danger)} .leg-neu::before{background:var(--warn)} .leg-mix::before{background:var(--primary)}

/* Cluster Cards */
.cluster-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 22px;margin-bottom:16px;border-left:3px solid var(--primary)}
.cluster-card--warn{border-left-color:var(--warn)}
.cluster-card--success{border-left-color:var(--success)}
.cluster-card--danger{border-left-color:var(--danger)}
.cluster-card--accent{border-left-color:var(--accent)}
.cluster-card__header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;gap:12px}
.cluster-card__name{font-size:0.92rem;font-weight:700;color:var(--heading)}
.cluster-card__count{font-size:0.73rem;color:var(--muted);background:rgba(255,255,255,.05);padding:3px 10px;border-radius:12px;white-space:nowrap;flex-shrink:0}

/* Quotes */
.quote{background:rgba(99,102,241,.06);border-left:3px solid var(--primary);border-radius:0 8px 8px 0;padding:10px 14px;margin:8px 0;font-size:0.84rem;font-style:italic;line-height:1.55}
.quote--warn{border-left-color:var(--warn);background:rgba(251,191,36,.05)}
.quote--success{border-left-color:var(--success);background:rgba(52,211,153,.05)}
.quote--danger{border-left-color:var(--danger);background:rgba(248,113,113,.05)}
.quote__author{font-style:normal;font-size:0.74rem;color:var(--muted);display:block;margin-top:5px}

/* Alert Boxes */
.alert{border-radius:10px;padding:13px 16px;margin:10px 0;font-size:0.84rem}
.alert p:last-child{margin-bottom:0}
.alert__title{font-weight:700;margin-bottom:6px;font-size:0.85rem}
.alert--info{background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.2)}
.alert--info .alert__title{color:var(--primary-light)}
.alert--success{background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.2)}
.alert--success .alert__title{color:var(--success)}
.alert--warn{background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.2)}
.alert--warn .alert__title{color:var(--warn)}
.alert--danger{background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.2)}
.alert--danger .alert__title{color:var(--danger)}

/* Idea Cards */
.idea-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin:16px 0}
.idea-card{background:var(--card-alt);border:1px solid var(--border);border-radius:12px;padding:16px 18px}
.idea-card__title{font-size:0.92rem;font-weight:700;color:var(--heading);margin-bottom:6px}
.idea-card__format{display:inline-block;font-size:0.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:2px 10px;border-radius:12px;background:rgba(99,102,241,.15);color:var(--primary-light);margin-bottom:8px}
.idea-card__format--success{background:rgba(52,211,153,.15);color:var(--success)}
.idea-card__format--warn{background:rgba(251,191,36,.15);color:var(--warn)}
.idea-card__format--danger{background:rgba(248,113,113,.15);color:var(--danger)}
.idea-card__format--accent{background:rgba(34,211,238,.15);color:var(--accent)}
.idea-card__rationale{font-size:0.8rem;color:var(--muted);line-height:1.5}

/* Score Display */
.score-display{display:flex;align-items:center;gap:20px;background:var(--card);border:1px solid var(--border);border-radius:14px;padding:22px 24px;margin:16px 0}
.score-circle{width:88px;height:88px;border-radius:50%;background:conic-gradient(var(--accent) calc(var(--score-pct)*1%),rgba(255,255,255,.08) 0);display:flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:800;color:var(--heading);flex-shrink:0;position:relative}
.score-circle::after{content:'';position:absolute;inset:8px;background:var(--card);border-radius:50%}
.score-circle span{position:relative;z-index:1}
.score-details h4{color:var(--heading);margin-bottom:6px;font-size:1rem}
.score-details p{font-size:0.82rem;color:var(--muted);margin-bottom:0}

/* Gold Quotes */
.gold-quote{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 20px;margin-bottom:14px;border-left:3px solid var(--warn)}
.gold-quote--diamond{border-left-color:var(--accent);background:rgba(34,211,238,.04)}
.gold-quote__text{font-size:0.92rem;font-style:italic;color:var(--text);margin-bottom:10px;line-height:1.6}
.gold-quote__meta{display:flex;gap:14px;flex-wrap:wrap;font-size:0.74rem;color:var(--muted)}
.gold-quote__tag{background:rgba(251,191,36,.1);color:var(--warn);padding:2px 8px;border-radius:10px;font-size:0.68rem;font-weight:700}

/* Tables */
.report-table{width:100%;border-collapse:collapse;font-size:0.8rem;margin:12px 0}
.report-table th{background:rgba(99,102,241,.1);color:var(--primary-light);font-weight:600;padding:10px 12px;text-align:left;border-bottom:1px solid var(--border)}
.report-table td{padding:9px 12px;border-bottom:1px solid var(--border);color:var(--text);vertical-align:top}
.report-table tr:hover td{background:rgba(255,255,255,.02)}

/* Mandate Box */
.mandate-box{background:linear-gradient(135deg,rgba(99,102,241,.12),rgba(34,211,238,.08));border:1px solid rgba(99,102,241,.3);border-radius:16px;padding:32px 36px;margin:32px 0;text-align:center}
.mandate-box__statement{font-size:1.05rem;line-height:1.75;color:var(--heading)}
.mandate-box__statement strong{color:var(--accent)}

/* User Cards */
.user-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;margin:16px 0}
.user-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px 18px}
.user-card__name{font-size:0.92rem;font-weight:700;color:var(--accent);margin-bottom:4px}
.user-card__role{font-size:0.7rem;color:var(--primary-light);text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:8px}
.user-card__desc{font-size:0.8rem;color:var(--muted);line-height:1.5}
.user-card__score{font-size:0.73rem;color:var(--warn);margin-top:6px}

/* Tips Compendium */
.tips-category{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 22px;margin-bottom:20px}
.tips-category__title{font-size:0.95rem;font-weight:700;color:var(--heading);margin-bottom:14px;display:flex;align-items:center;gap:8px}
.tips-category__title::before{content:'';display:inline-block;width:3px;height:18px;background:var(--accent);border-radius:2px}
.tip-row{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);font-size:0.82rem}
.tip-row:last-child{border-bottom:none;padding-bottom:0}
.tip-row__check{color:var(--success);flex-shrink:0;margin-top:1px}
.tip-row__text{color:var(--text);line-height:1.5}
.tip-row__source{font-size:0.72rem;color:var(--primary-light);flex-shrink:0;margin-top:2px}

/* Divider */
.divider{border:none;border-top:1px solid var(--border);margin:40px 0}

/* Footer */
.page-footer{text-align:center;padding:24px 32px 48px;font-size:0.74rem;color:var(--muted);border-top:1px solid var(--border);max-width:920px;margin:0 auto}
.disclaimer{max-width:920px;margin:0 auto;padding:0 32px 40px;font-size:0.7rem;color:rgba(148,163,184,0.35);border-top:1px solid rgba(255,255,255,.04);padding-top:16px;line-height:1.6}
"""

# ─── UTILITY FUNCTIONS ─────────────────────────────────────────────────────────

def section(num, title, subtitle=""):
    sub = f'<p class="section__subtitle">{subtitle}</p>' if subtitle else ""
    return f"""
<div class="section" id="s{num}">
<div class="section__number">SECTION {num:02d}</div>
<h2 class="section__title">{title}</h2>
{sub}"""

def end_section():
    return "</div>\n"

def cluster(name, count, color="", body=""):
    cls = f" cluster-card--{color}" if color else ""
    return f"""
<div class="cluster-card{cls}">
<div class="cluster-card__header">
<span class="cluster-card__name">{name}</span>
<span class="cluster-card__count">{count}</span>
</div>
{body}
</div>"""

def quote(text, author, style=""):
    cls = f" quote--{style}" if style else ""
    return f'<div class="quote{cls}">{text}<span class="quote__author">{author}</span></div>'

def alert(level, title, body):
    return f"""<div class="alert alert--{level}"><div class="alert__title">{title}</div><p>{body}</p></div>"""

def idea(title, fmt, rationale, fmt_color=""):
    cls = f" idea-card__format--{fmt_color}" if fmt_color else ""
    return f"""<div class="idea-card"><div class="idea-card__title">{title}</div><span class="idea-card__format{cls}">{fmt}</span><div class="idea-card__rationale">{rationale}</div></div>"""

def gold_quote(text, author, score, tags, diamond=False):
    cls = " gold-quote--diamond" if diamond else ""
    tag_html = " ".join(f'<span class="gold-quote__tag">{t}</span>' for t in tags)
    return f"""
<div class="gold-quote{cls}">
<div class="gold-quote__text">"{text}"</div>
<div class="gold-quote__meta"><span>{author}</span><span>score:{score}</span>{tag_html}</div>
</div>"""

def tip(text, source=""):
    src = f'<span class="tip-row__source">{source}</span>' if source else ""
    return f'<div class="tip-row"><span class="tip-row__check">&#10003;</span><span class="tip-row__text">{text}</span>{src}</div>'

def tips_cat(emoji, title, tips_html):
    return f"""
<div class="tips-category">
<div class="tips-category__title">{emoji} {title}</div>
{tips_html}
</div>"""

def user_card(name, role, desc, score_info=""):
    score_html = f'<div class="user-card__score">{score_info}</div>' if score_info else ""
    return f"""<div class="user-card"><div class="user-card__name">{name}</div><div class="user-card__role">{role}</div><div class="user-card__desc">{desc}</div>{score_html}</div>"""


# ─── REPORT BUILDER ────────────────────────────────────────────────────────────

def build_report():
    parts = []

    # ── COVER ─────────────────────────────────────────────────────────────────
    parts.append(f"""
<div class="cover">
  <div class="cover__badge">Audience Intelligence Report &middot; March 2026</div>
  <h1>OpenClaw Goes <span>Mainstream</span></h1>
  <p class="cover__subtitle">
    March 2026 Reddit Community Intelligence — extracted from {TOTAL_POSTS:,} public posts
    and {TOTAL_COMMENTS:,} comment interactions across <strong>35 subreddits</strong>.
    The month OpenClaw became a culture moment.
  </p>
  <div class="cover__meta">
    <div class="cover__meta-item">
      <span class="cover__meta-value">{TOTAL_POSTS:,}</span>
      <span class="cover__meta-label">Posts Analysed</span>
    </div>
    <div class="cover__meta-item">
      <span class="cover__meta-value">{TOTAL_COMMENTS:,}</span>
      <span class="cover__meta-label">Comment Interactions</span>
    </div>
    <div class="cover__meta-item">
      <span class="cover__meta-value">35</span>
      <span class="cover__meta-label">Subreddits</span>
    </div>
    <div class="cover__meta-item">
      <span class="cover__meta-value">{TOP_SCORE:,}</span>
      <span class="cover__meta-label">Peak Post Score</span>
    </div>
  </div>
  <div class="cover__client">
    Prepared for <strong>Wayne Michael</strong> &middot;
    Platform: Reddit (r/openclaw + 34 adjacent communities) &middot;
    Reporting Period: March 2026
  </div>
  <div class="cover__footer">
    Produced by Audience Intelligence &middot; audienceintelligence.com &middot; Confidential
  </div>
</div>
""")

    # ── TABLE OF CONTENTS ─────────────────────────────────────────────────────
    parts.append("""
<div class="section" id="toc">
<div class="section__number">INDEX</div>
<h2 class="section__title">Table of Contents</h2>
<table class="report-table">
<thead><tr><th>#</th><th>Section</th><th>Focus</th></tr></thead>
<tbody>
<tr><td>01</td><td><a href="#s1">Dataset Overview</a></td><td>March 2026 — the month everything changed</td></tr>
<tr><td>02</td><td><a href="#s2">Community Sentiment Analysis</a></td><td>Mainstream arrival brings mixed signals</td></tr>
<tr><td>03</td><td><a href="#s3">Key Themes &amp; Narratives</a></td><td>6 defining stories of March 2026</td></tr>
<tr><td>04</td><td><a href="#s4">Questions the Community Is Asking</a></td><td>Acquisition, security, and survival questions</td></tr>
<tr><td>05</td><td><a href="#s5">Frustrations &amp; Pain Points</a></td><td>CVEs, cease &amp; desist, EU, uncertainty</td></tr>
<tr><td>06</td><td><a href="#s6">Desires &amp; Feature Requests</a></td><td>What the community actually wants built</td></tr>
<tr><td>07</td><td><a href="#s7">Viral Triggers &amp; Engagement Mechanics</a></td><td>Why 22,056 upvotes happened and how to repeat it</td></tr>
<tr><td>08</td><td><a href="#s8">Content Opportunities</a></td><td>5 high-demand content gaps with March signal</td></tr>
<tr><td>09</td><td><a href="#s9">Engagement Patterns</a></td><td>Who comments, what triggers 700+ replies</td></tr>
<tr><td>10</td><td><a href="#s10">Power Users &amp; Community Intelligence</a></td><td>6 creators driving signal in March 2026</td></tr>
<tr><td>11</td><td><a href="#s11">Product &amp; Service Opportunities</a></td><td>Gaps the market is screaming for</td></tr>
<tr><td>12</td><td><a href="#s12">Audience Profile</a></td><td>Who arrived in March — a new audience map</td></tr>
<tr><td>13</td><td><a href="#s13">Master Tips Compendium</a></td><td>March-specific actionable intelligence</td></tr>
<tr><td>14</td><td><a href="#s14">Strategic Recommendations for Wayne</a></td><td>3 actions for the post-acquisition moment</td></tr>
<tr><td>15</td><td><a href="#s15">Viral Score Card</a></td><td>9.5/10 — community at peak cultural momentum</td></tr>
<tr><td>16</td><td><a href="#s16">Gold Quotes</a></td><td>The sentences that define March 2026</td></tr>
<tr><td>17</td><td><a href="#s17">Key Facts &amp; Statistics</a></td><td>Hard numbers from the March dataset</td></tr>
<tr><td>18</td><td><a href="#s18">Privacy &amp; Methodology Note</a></td><td>Data sourcing and ethical framework</td></tr>
</tbody>
</table>
</div>
""")

    # ── S1 DATASET OVERVIEW ───────────────────────────────────────────────────
    parts.append(section(1, "Dataset Overview", "March 2026 — the month OpenClaw became a culture moment"))
    parts.append(f"""
<p>This report is built from <strong>{TOTAL_POSTS:,} Reddit posts</strong> and <strong>{TOTAL_COMMENTS:,} comment interactions</strong> collected across <strong>35 subreddits</strong> during March 2026. It is not a template — every section reflects intelligence drawn directly from the actual posts, titles, authors, and community discussions in this dataset.</p>

<p>March 2026 was a pivot point. Three seismic events happened simultaneously: (1) OpenAI acquired OpenClaw with Sam Altman confirming Peter Steinberger's move publicly; (2) Anthropic sent OpenClaw a cease &amp; desist notice and launched a competing automated agent feature in Claude Code; and (3) a single two-word post — "openclaw literally" — achieved <strong>{TOP_SCORE:,} upvotes</strong> on r/pcmasterrace, dragging OpenClaw into mainstream internet culture overnight. Together, these three events compressed years of product-lifecycle evolution into a single month.</p>
""")
    parts.append("""
<div class="stats-grid">
  <div class="stat-card stat-card--accent">
    <span class="stat-value">100</span>
    <span class="stat-label">Posts Analysed</span>
  </div>
  <div class="stat-card stat-card--positive">
    <span class="stat-value">21,808</span>
    <span class="stat-label">Total Comments</span>
  </div>
  <div class="stat-card stat-card--neutral">
    <span class="stat-value">35</span>
    <span class="stat-label">Subreddits</span>
  </div>
  <div class="stat-card stat-card--purple">
    <span class="stat-value">22,056</span>
    <span class="stat-label">Peak Post Score</span>
  </div>
  <div class="stat-card">
    <span class="stat-value">218</span>
    <span class="stat-label">Avg Comments / Post</span>
  </div>
  <div class="stat-card stat-card--negative">
    <span class="stat-value">3</span>
    <span class="stat-label">Posts Over 10k Upvotes</span>
  </div>
</div>
""")
    parts.append("""
<h3 style="color:var(--heading);font-size:1rem;margin:24px 0 12px">Subreddit Distribution — Where the March Conversation Happened</h3>
<table class="report-table">
<thead>
<tr><th>Subreddit</th><th>Posts</th><th>Comments</th><th>Signal</th></tr>
</thead>
<tbody>
<tr><td>r/openclaw</td><td>39</td><td>7,265</td><td>Core community — builders, power users, tutorials, hardware</td></tr>
<tr><td>r/aiagents</td><td>4</td><td>1,581</td><td>High engagement — Aislot's job displacement &amp; multi-model content</td></tr>
<tr><td>r/LocalLLaMA</td><td>6</td><td>1,724</td><td>Deep skepticism + "is it actually local?" — new audience gating</td></tr>
<tr><td>r/ClaudeAI</td><td>5</td><td>1,547</td><td>Community split on Anthropic C&amp;D — 832 cmts on one post alone</td></tr>
<tr><td>r/clawdbot</td><td>6</td><td>862</td><td>New satellite community — ecosystem maturation signal</td></tr>
<tr><td>r/OpenAI</td><td>4</td><td>839</td><td>Acquisition coverage — Sam Altman confirmation + founding story</td></tr>
<tr><td>r/wallstreetbets &amp; r/WallStreetDad</td><td>3</td><td>795</td><td>Financial community watching AI job displacement</td></tr>
<tr><td>r/singularity</td><td>3</td><td>576</td><td>Recruitment of Peter Steinberger to OpenAI — AGI narrative</td></tr>
<tr><td>r/BuyFromEU / r/eutech / r/EU_Economics</td><td>3</td><td>1,070</td><td>European resistance — creator comments on EU regulation hostility</td></tr>
<tr><td>r/pcmasterrace</td><td>1</td><td>325</td><td>"openclaw literally" — 22,056 upvotes, mainstream breakout post</td></tr>
<tr><td>r/nottheonion</td><td>1</td><td>443</td><td>Meta AI Safety Director inbox wiped — satire-tier real-world event</td></tr>
<tr><td>r/sysadmin</td><td>1</td><td>314</td><td>2,000+ CVE warning — security community alarmed</td></tr>
<tr><td>r/selfhosted / r/homeassistant</td><td>2</td><td>347</td><td>Privacy-first crowd — outraged by Docker CVEs</td></tr>
<tr><td>r/raspberry_pi</td><td>1</td><td>194</td><td>Pi Zero 2W personal assistant build — 2,815 pts, hardware crossover</td></tr>
<tr><td>Other 21 subreddits</td><td>21</td><td>3,221</td><td>Broad mainstream spillover, tech &amp; non-tech audiences</td></tr>
</tbody>
</table>
""")
    parts.append(alert("info", "&#x1F4CA; March 2026 Context Signal",
        "Only 39 of 100 posts (39%) were from r/openclaw itself — the lowest r/openclaw share of any dataset we have tracked. "
        "The remaining 61% came from 34 other communities. This cross-community diffusion is not normal for a niche developer tool. "
        "It is the data signature of a product transitioning from early adopter to mainstream. "
        "OpenClaw in March 2026 is no longer a tool that happens to have a subreddit. It is a cultural reference point."))
    parts.append(end_section())

    # ── S2 SENTIMENT ──────────────────────────────────────────────────────────
    parts.append(section(2, "Community Sentiment Analysis", "Mainstream arrival brings complexity — enthusiasm, anxiety, and scepticism all at once"))
    parts.append("""
<p>The March 2026 dataset shows a sentiment profile that is substantially more complex than the original r/openclaw-centric dataset. The core community remains enthusiastic and productive, but the mainstream influx has brought a significant layer of anxiety, scepticism, and frustrated criticism. This is expected and healthy — it is what mainstream adoption looks like in its first month.</p>
""")
    parts.append("""
<div class="sentiment-bar">
  <div class="sentiment-bar__segment sentiment-bar__segment--positive" style="width:50%">Positive / Engaged — 50%</div>
  <div class="sentiment-bar__segment sentiment-bar__segment--negative" style="width:28%">Critical / Anxious — 28%</div>
  <div class="sentiment-bar__segment sentiment-bar__segment--neutral" style="width:22%">Neutral / Informational — 22%</div>
</div>
<div class="sentiment-bar__legend">
  <span class="leg-pos">Positive / Engaged (building, sharing wins, celebrating viral moment)</span>
  <span class="leg-neg">Critical / Anxious (security concerns, acquisition anxiety, EU anger, sceptics)</span>
  <span class="leg-neu">Neutral / Informational (news posts, cross-posts, how-to content)</span>
</div>
""")
    parts.append(cluster("Positive — Builders &amp; Celebrators", "~50% of volume",
        color="success",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The core audience continues to post success stories, hardware builds, workflow documentation, and tool comparisons. Posts in this cluster average <strong>568–2,807 upvotes</strong>. Notable: three posts in this cluster documented life-changing outcomes — salary doubling, a 3D printing workflow, complete email automation. The viral "openclaw literally" post created a global positive moment even among non-users.</p>"""))
    parts.append(cluster("Critical / Anxious — Security, Acquisition, EU Resistance", "~28% of volume",
        color="danger",
        body="""<p style="font-size:0.85rem;color:var(--muted)">This cluster is new and March-specific. The sysadmin post about 2,000+ CVEs in the official Docker image generated 314 comments of deep concern. The BuyFromEU Anthropic-C&amp;D post generated 521. LocalLLaMA's "Anyone actually using Openclaw?" generated <strong>731 comments</strong> — the second highest in the dataset — with clear scepticism about organic virality. This is not a hostile audience; it is a technically literate one asking legitimate questions.</p>"""))
    parts.append(cluster("Neutral / Informational", "~22% of volume",
        color="",
        body="""<p style="font-size:0.85rem;color:var(--muted)">News aggregation posts (OpenAI acquisition confirmation, Meta AI Safety Director story, Google integrations), cross-posts from non-technical communities (r/wallstreetbets, r/StrangeEarth), and how-to content that attracted moderate engagement. These posts are not generating discussion — they are generating discovery. This is how new audiences learn OpenClaw exists.</p>"""))
    parts.append(alert("warn", "&#x26A0;&#xFE0F; Sentiment Shift to Watch",
        "The most-commented post in the entire dataset is r/ClaudeAI's 'You're all lucky to be here when it started' (832 comments, 2,807 pts). "
        "This is a nostalgia/inflection post — a signal that the community recognises it is at a turning point. "
        "The second most-commented is LocalLLaMA's 'Anyone actually using Openclaw?' (731 comments). "
        "Both posts are about the community's relationship with its own moment — not about features or tutorials. "
        "This is a community in the process of defining its own identity under mainstream pressure."))
    parts.append(end_section())

    # ── S3 KEY THEMES ─────────────────────────────────────────────────────────
    parts.append(section(3, "Key Themes &amp; Narratives", "6 defining stories of March 2026 — each one absent from the previous dataset"))
    parts.append("""
<p>Every theme below was identified directly from post titles, selftext, and comment volumes in the March dataset. None of these themes appeared in the original r/openclaw dataset. This is a genuinely new intelligence picture.</p>
""")
    parts.append(cluster("THEME 1 · The OpenAI Acquisition", "Confirmed by Sam Altman · 4 posts · 1,692 comments",
        color="accent",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">The single biggest structural event in OpenClaw's history landed in March 2026. Sam Altman confirmed that OpenAI has acquired OpenClaw and that <strong>Peter Steinberger</strong> — the founder — is joining OpenAI to drive "the next generation of personal agents." The deal stipulates that OpenClaw transitions to a foundation as an open-source project with continued OpenAI support.</p>
<p style="font-size:0.85rem;color:var(--muted)">The r/OpenAI community received this with high engagement (1,914 pts, 364 comments for the main confirmation post). The r/singularity community picked up the recruitment angle (1,255 pts, 289 comments). Community reaction is split: core builders are cautiously optimistic; privacy-first and EU users are loudly alarmed.</p>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0"><strong>For Wayne:</strong> The open-source foundation commitment is the key fact here. Whatever OpenAI does with the commercial product, the community-developed codebase is legally protected from being locked away.</p>
"""))
    parts.append(cluster("THEME 2 · Mainstream Viral Breakout", "22,056 · 17,592 · 10,265 upvotes in one month",
        color="success",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">Three posts exceeded 10,000 upvotes in March 2026 — a benchmark the entire previous dataset never reached once. "openclaw literally" (22,056 on r/pcmasterrace) is a two-word meme with zero explanatory text. It achieved virality because OpenClaw had reached the cultural penetration level where a reference alone is sufficient for recognition. "walletLeftChat" (17,592 on r/ProgrammerHumor) is similarly a pure cultural reference. The nottheonion story about Meta's AI Safety Director having her inbox wiped by her own OpenClaw agent (10,265) is the third — a real-world absurdist event that reads as satire.</p>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0">Together these three posts represent mainstream cultural arrival. OpenClaw is now a meme substrate — the product has finished the "niche technology" phase of its lifecycle.</p>
"""))
    parts.append(cluster("THEME 3 · Security Crisis", "2,000+ CVEs · Anthropic C&D · Docker vulnerability",
        color="danger",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">March 2026 surfaced a critical security problem that the core community had not fully acknowledged. A sysadmin post (2,233 pts, 314 comments) documented that the official GHCR Docker image contains approximately <strong>2,000 CVEs with 7 critical vulnerabilities and no available patch</strong>. The selfhosted community amplified this (474 pts, 146 comments). The home assistant community followed (518 pts, 201 comments). These are security-literate audiences who had just given OpenClaw access to their messaging channels, API keys, and file systems.</p>
<p style="font-size:0.85rem;color:var(--muted)">Concurrently, Anthropic sent a cease &amp; desist notice to the OpenClaw team. This was partly welcomed by Claude users (1,370 pts, 136 comments on r/ClaudeAI) who cited the security concerns as justification. The C&amp;D also prompted Anthropic to launch Claude Code scheduled tasks — effectively their own automated agent competitor to OpenClaw.</p>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0"><strong>For Wayne:</strong> The security situation is real and documented. Anyone deploying OpenClaw in March 2026 without checking the container is running 2,000+ known vulnerabilities. Section 13 contains specific remediation tips.</p>
"""))
    parts.append(cluster("THEME 4 · AI Job Displacement Anxiety", "1,673 pts · 477 comments on a single post",
        color="warn",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">March 2026 gave the AI-job-displacement narrative its most visceral real-world proof point: Jack Dorsey used AI automation to lay off 4,000 people via a single tweet. The r/aiagents post documenting this (1,673 pts, 477 comments) by u/Aislot frames OpenClaw explicitly as a survival skill: <em>"If you aren't AI native, you have become expendable to execs."</em></p>
<p style="font-size:0.85rem;color:var(--muted)">This theme also appears in the r/ClaudeAI "anyone feel scared?" post (590 pts, 232 comments) and the r/wallstreetbets Claude Code review post (1,274 pts, 263 comments) where security stocks fell on Claude automation news. The community is acutely aware that the technology it is building is also the technology threatening its members' jobs.</p>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0">This creates emotionally high-stakes content — posts that generate engagement because they speak to existential fear, not just technical curiosity.</p>
"""))
    parts.append(cluster("THEME 5 · Local &amp; Privacy-First Counter-Movement", "From $100k/year cloud to $30k hardware",
        color="",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">A powerful counter-narrative to cloud-based OpenClaw emerged in March, driven by the security crisis and the acquisition. u/Aislot's post about running 4 high-end local models (Kimi K2.5, Qwen 3.5, MiniMax 2.5) on Mac Studios and a DGX Spark (1,028 pts, 292 comments) makes an explicit ROI case: <em>"If you have your OpenClaw working 24/7 using frontier models like Opus, you're at $100,000 a year. I spent a third of that to buy computers. I'll use them for years for free. Not a single prompt goes to a cloud server."</em></p>
<p style="font-size:0.85rem;color:var(--muted)">The LocalLLaMA skeptic cluster (6 posts, 1,724 comments) is heavily focused on the "is it actually running locally?" question. The selfhosted and homeassistant communities are asking the same. This is a substantial, technically literate audience segment that the r/openclaw core has not fully served.</p>
"""))
    parts.append(cluster("THEME 6 · Real-World Success Stories", "Documented, specific, high-credibility outcomes",
        color="success",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">March 2026 produced the highest concentration of documented, specific success stories the dataset has seen. Unlike vague claims, these posts contain exact details:</p>
<ul style="font-size:0.84rem;color:var(--muted);margin-left:18px;line-height:1.8">
<li><strong>Salary doubling (780 pts, 212 comments):</strong> Software engineer in Brazil gave agent access to LinkedIn, created job accounts, wrote CV in markdown, applied to international positions. Got a job doubling their salary.</li>
<li><strong>3D printing workflow (1,749 pts, 117 comments):</strong> User connected OpenClaw to 3 3D printers via skills. Agent finds/creates/edits/slices/sends models to print automatically. "I haven't thought about designing things myself in weeks."</li>
<li><strong>Email mastery (568 pts, 339 comments):</strong> Connected to Office 365 — deletes, moves, archives, auto-drafts replies, 3x daily briefing. Also managing video captions, Instagram scheduling, and YouTube uploads.</li>
<li><strong>Business launch (613 pts, 225 comments):</strong> User documented giving AI access to gmail, Hetzner, expense cards — running parallel subagents on everything — then scrolling Reddit while it worked.</li>
</ul>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0">These posts are not aspirational — they are documented outcomes with enough specificity to replicate.</p>
"""))
    parts.append(end_section())

    # ── S4 QUESTIONS ──────────────────────────────────────────────────────────
    parts.append(section(4, "Questions the Community Is Asking", "The questions with the most comments reveal the highest-anxiety decision points"))
    parts.append("""<p>The most-commented question posts in the March dataset reveal what the new mainstream audience needs answered before they commit to OpenClaw. These are not questions the r/openclaw core community is asking — they are questions from the 61% who arrived from outside the core subreddit.</p>""")
    parts.append(cluster("Q1 · Is OpenClaw actually local / private?", "Across LocalLLaMA, selfhosted, homeassistant · 1,000+ combined comments",
        color="warn",
        body="""<p style="font-size:0.85rem;color:var(--muted)">"so is OpenClaw local or not" (r/LocalLLaMA, 1,019 pts, 300 comments) and "Anyone actually using Openclaw?" (r/LocalLLaMA, 841 pts, 731 comments) both probe the same concern: is OpenClaw genuinely a self-hosted privacy solution, or is it just a wrapper for cloud APIs dressed up to look self-hosted? The selfhosted community's Docker CVE post (474 pts, 146 comments) adds the follow-up: if it IS self-hosted, why is the official image essentially an open invitation to be compromised? This question has no clean current answer — and that gap is a business opportunity.</p>"""))
    parts.append(cluster("Q2 · What happens after the OpenAI acquisition?", "r/OpenAI, r/singularity · 693 combined comments",
        color="",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The acquisition posts collectively surfaced the community's deep uncertainty about OpenClaw's identity under OpenAI ownership. Will it remain API-agnostic? Will it be optimised away from Anthropic? Will the open-source foundation commitment hold? Will the community-built skill ecosystem survive? These questions are not answered in the acquisition posts — they are the questions the comments are asking. Any content that provides clear, sourced answers to these four questions will command high engagement.</p>"""))
    parts.append(cluster("Q3 · Will Claude Code replace OpenClaw now?", "r/ClaudeAI · 472+ combined comments",
        color="",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The Anthropic C&amp;D and the simultaneous launch of Claude Code scheduled tasks (1,318 pts, 168 comments: "Breaking: Claude just dropped their own OpenClaw version") created a direct comparison question. The r/ClaudeAI community's 832-comment post ("You're all lucky to be here when it started") is precisely this — a community that backed Anthropic now wondering whether OpenClaw's demise means they missed a window. Claude Code's automated tasks are narrower in scope than OpenClaw's full agent architecture, but the question of relative positioning is live in the community.</p>"""))
    parts.append(cluster("Q4 · Is the virality organic or manufactured?", "LocalLLaMA · 731 comments",
        color="warn",
        body="""<p style="font-size:0.85rem;color:var(--muted)">"I am highly suspicious that openclaw's virality is organic. I don't know of anyone (online or IRL) that is actually using it and I am deep in the AI ecosystem... conspiracy theory is that it was manufactured social media marketing on Twitter to hype it up before acquisition." This post with 731 comments represents the most important gate the mainstream audience has not yet passed through: trust establishment. March 2026 brought OpenClaw an enormous new audience that has not yet decided whether to believe in it.</p>"""))
    parts.append(cluster("Q5 · Why Mac mini? (Hardware strategy)", "r/openclaw · 347 comments",
        color="accent",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The r/openclaw "Why Mac mini??" post (189 pts, 347 comments) reflects the hardware decision conversation that the local/privacy cluster is having. The Mac Studio setup documented by Aislot uses multiple units. The Pi Zero 2W build by bastivkl proved pocket-sized agent deployment. The community has not converged on a definitive hardware recommendation — and this ambiguity generates extended discussion because every builder has a different use case cost profile.</p>"""))
    parts.append(end_section())

    # ── S5 FRUSTRATIONS ───────────────────────────────────────────────────────
    parts.append(section(5, "Frustrations &amp; Pain Points", "The specific, documented complaints with the highest signal in March 2026"))
    parts.append(cluster("FRUSTRATION 1 · The Docker Security Disaster", "Critical · 2,000+ CVEs in official image",
        color="danger",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The official GHCR image has approximately 2,000 CVEs including 7 critical. The 1panel build is essentially identical. Even the "Alpine/openclaw" image is not actually Alpine — it's Debian 12 underneath with 1,156 vulnerabilities. Three communities documented this independently in March (sysadmin, selfhosted, homeassistant). The frustration is not just that vulnerabilities exist — it is that they exist in an image given access to messaging platforms, API keys, and file system execution. This is a category mismatch between the trust OpenClaw asks for and the security it delivers.</p>"""))
    parts.append(cluster("FRUSTRATION 2 · The Anthropic Cease &amp; Desist", "High engagement · Divided community",
        color="warn",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The C&amp;D created a complex frustration dynamic. Core OpenClaw users are frustrated that Anthropic — which benefited enormously from OpenClaw driving API adoption — is now legally moving against the community. The ClaudeAI community is frustrated in the opposite direction: they believe OpenClaw's token usage (reported at 50,000 tokens just to say "hello") was unsustainable and that the C&amp;D was rational. The community is genuinely split, and both sides express genuine frustration.</p>"""))
    parts.append(cluster("FRUSTRATION 3 · EU Regulatory Hostility", "521 comments on BuyFromEU post · 3 EU communities",
        color="warn",
        body="""<p style="font-size:0.85rem;color:var(--muted)">OpenClaw's creator directly commented on European regulations as a reason for moving development activity. The BuyFromEU post (521 comments) and the parallel eutech and EU_Economics posts captured significant European frustration — not just with OpenClaw's regulatory situation but with the broader pattern of AI innovation being built outside Europe because European regulatory environments make it prohibitive. This is an underserved, highly engaged audience segment.</p>"""))
    parts.append(cluster("FRUSTRATION 4 · Acquisition Uncertainty &amp; Identity Loss", "Existential concern across 3 subreddits",
        color="",
        body="""<p style="font-size:0.85rem;color:var(--muted)">A significant subset of the community built their workflows and commercial operations on the assumption that OpenClaw would remain an independent, API-agnostic agent platform. The OpenAI acquisition — however smooth the messaging — represents loss of that independence. The frustration is not anger at OpenAI; it is grief at the transition from independent tool to BigTech subsidiary. The "You're all lucky to be here when it started" post (832 comments) is this frustration expressed as nostalgia.</p>"""))
    parts.append(cluster("FRUSTRATION 5 · Token Cost at Scale", "Documented: $100k/year at frontier model usage",
        color="warn",
        body="""<p style="font-size:0.85rem;color:var(--muted)">Aislot's "If you have your OpenClaw working 24/7 using frontier models like Opus, you're at $100,000 a year" post (1,028 pts, 292 comments) crystallises the cost frustration that the original dataset also documented — but at a new scale. The 24/7 use case is March 2026's power user baseline. The frustration is that this is the configuration the product implicitly encourages but the cost is catastrophic unless you've done the model routing optimisation.</p>"""))
    parts.append(end_section())

    # ── S6 DESIRES ────────────────────────────────────────────────────────────
    parts.append(section(6, "Desires &amp; Feature Requests", "What the March 2026 community actually wants built"))
    parts.append(cluster("DESIRE 1 · Security-Hardened Official Image", "Explicitly requested in 3 communities",
        color="success",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The community wants a Docker image they can trust. Not a patched Debian image — a minimal, intentionally designed container that passes a security audit and lists exactly what network access it requires and why. The selfhosted and sysadmin communities are explicit: they will use OpenClaw when they can run it without opening their systems to 2,000 known vulnerabilities. Until then, they won't.</p>"""))
    parts.append(cluster("DESIRE 2 · Clear Post-Acquisition Roadmap", "High community anxiety = demand for certainty",
        color="",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The community wants Peter Steinberger or Sam Altman to answer: Will OpenClaw remain API-agnostic? What happens to the skill ecosystem? What does "open-source foundation" actually mean legally? Will pricing change? Will the desktop-first architecture survive? No official communication has answered these questions in the March data. The silence is generating speculation and concern that the community would trade for a 500-word FAQ.</p>"""))
    parts.append(cluster("DESIRE 3 · Local-Model First Architecture", "Documented ROI by real users, growing demand",
        color="accent",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The $100k/year calculation is making real users move to local model stacks. The desire is not just to run locally — it is for OpenClaw to be explicitly designed with local-first as a first-class path, including setup guides, hardware recommendations, and verified model compatibility lists. The LocalLLaMA community represents ~1,700 comments of demand for this. The selfhosted community adds another ~300.</p>"""))
    parts.append(cluster("DESIRE 4 · EU-Compliant Version or Deployment Guide", "1,070 comments across EU communities",
        color="warn",
        body="""<p style="font-size:0.85rem;color:var(--muted)">European users want a version of OpenClaw — or at minimum a deployment guide — that is legally operable under GDPR and EU AI Act requirements. The desire is for either EU-hosted infrastructure (data not leaving EU), a GDPR-compliant configuration guide, or a fork designed for EU deployment. The 3 EU community posts generated over 1,000 combined comments in March — this is a real, large, monetisable audience segment that is currently unserved.</p>"""))
    parts.append(cluster("DESIRE 5 · Simple &quot;Real Outcome&quot; Documentation", "Success stories drive more demand for success stories",
        color="success",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The success story posts (doubled salary, 3D printers, email automation) consistently generate high comment volumes and positive sentiment. The desire implied by this engagement pattern is simple: more documented, specific outcomes with enough detail to replicate. The community's implicit request is a library of "I built X with OpenClaw, here's exactly how" posts. This is the content format that converts sceptics — the 731-comment LocalLLaMA post is full of people waiting to be shown proof.</p>"""))
    parts.append(end_section())

    # ── S7 VIRAL TRIGGERS ─────────────────────────────────────────────────────
    parts.append(section(7, "Viral Triggers &amp; Engagement Mechanics", "Why three posts hit 10k+ upvotes — and how to create that intentionally"))
    parts.append("""<p>March 2026 produced three posts with scores the entire previous dataset never approached. Analysing their mechanics reveals replicable patterns.</p>""")
    parts.append(cluster("TRIGGER 1 · Meme-Level Cultural Recognition", "22,056 · 17,592 upvotes",
        color="accent",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">Both top posts are minimal text on mainstream meme communities. "openclaw literally" is two words. "walletLeftChat" is one word (a reference to OpenClaw replacing human tasks). Neither explains what OpenClaw is — because at the audiences receiving these posts, no explanation is needed. This is the virality signal of a tool that has achieved the status of cultural shorthand.</p>
<p style="font-size:0.85rem;color:var(--muted)">The format is: <strong>meme-compatible post on r/pcmasterrace or r/ProgrammerHumor + subcultural reference that rewards insider knowledge + universal relatable frustration/humour</strong>. This landing on mainstream communities drove the score far past what r/openclaw itself could ever deliver.</p>
"""))
    parts.append(cluster("TRIGGER 2 · Real-World Absurdist Events", "10,265 upvotes on r/nottheonion",
        color="warn",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">Meta's AI Safety &amp; Alignment Director — the person responsible for ensuring AI follows human intent — had her inbox wiped by her own OpenClaw agent. She gave it access to her email, it deleted her inbox, and she had to manually terminate it. Posted on r/nottheonion (10,265 pts, 443 comments) and simultaneously on r/clawdbot (459 pts, 188 comments). The formula: <strong>ironic protagonist + dramatic failure + domain-specific resonance + real-world plausibility</strong>. This story wrote itself — but it performed because the combination of AI safety + unintended AI action is a narrative the entire internet finds simultaneously hilarious and disturbing.</p>
"""))
    parts.append(cluster("TRIGGER 3 · Corporate Drama + Existential Stakes", "1,914 + 1,370 + 1,318 pts across 3 posts",
        color="",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">The acquisition (confirmed), the C&amp;D (confirmed), and Claude Code's own agent launch (confirmed) each generated high engagement precisely because they represent genuine, irrevocable changes to the OpenClaw landscape. The community does not engage this way with speculative drama — it engages with <em>confirmed corporate events that directly affect their tools</em>. The formula: <strong>named company + explicit action with real consequence + community-affecting implication</strong>. Any post that can confirm one of these three conditions before the community knows will generate outsized engagement.</p>
"""))
    parts.append(cluster("TRIGGER 4 · Fear-Based Survival Content", "1,673 pts · 477 comments",
        color="danger",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">Aislot's Jack Dorsey layoff post performs because it combines a real event (4,000 job losses) with a direct personal consequence ("If you aren't AI native, you have become expendable") and a concrete skill prescription. Posts that make people feel their economic survival depends on their next action generate engagement through urgency. The formula: <strong>real corporate event + direct personal consequence + specific learnable skill = maximum urgency engagement</strong>. Note: this only works when the event is real and documented.</p>
"""))
    parts.append(cluster("TRIGGER 5 · Specific Documented Wins with Replicable Numbers", "Salary double · $100k vs $30k hardware · 3D printers",
        color="success",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">Success posts that include specific numbers — currency amounts, time investments, exact tools used — dramatically outperform vague claims. "doubled my salary" outperforms "got a better job". "$100,000 a year vs $30,000 one-time hardware" outperforms "local models are cheaper". The formula: <strong>specific outcome + numerical evidence + enough detail to replicate</strong>. The community responds because specificity signals credibility, and credibility in a sea of AI hype is rare and valuable.</p>
"""))
    parts.append(end_section())

    # ── S8 CONTENT OPPORTUNITIES ──────────────────────────────────────────────
    parts.append(section(8, "Content Opportunities", "5 high-demand gaps with clear March 2026 signal — each backed by documented community need"))
    parts.append('<div class="idea-grid">')
    parts.append(idea(
        "OpenClaw Security Hardening Guide",
        "Deep-Dive Tutorial", fmt_color="danger",
        rationale="Three independent communities documented the 2,000+ CVE problem in March. No guide currently exists. Audience: sysadmin (2,233 pts), selfhosted, homeassistant. Estimated reach: multi-community crosspost, minimum 4 relevant subreddits. Format: audit steps + hardened compose file + CVE mitigation checklist."))
    parts.append(idea(
        "OpenAI Acquisition: What Changes, What Doesn't",
        "Analysis Post", fmt_color="",
        rationale="The acquisition is confirmed. No community member has yet published a sourced, comprehensive breakdown of what the open-source foundation commitment means in practice, what stays the same, and what will change. The first clear-headed analysis post claiming this territory will own the conversation."))
    parts.append(idea(
        "Local Models vs Frontier APIs: The $100k Math",
        "Data-Backed Opinion", fmt_color="accent",
        rationale="Aislot's post (1,028 pts) proved the $100k/year vs $30k hardware calculation resonates. A full worked version — hardware options by price tier, model benchmarks, specific OpenClaw config — would be the definitive resource for the decision. Crosspost potential: r/LocalLLaMA (6 posts, 1,724 cmts already on OpenClaw), r/openclaw, r/selfhosted, r/homeassistant."))
    parts.append(idea(
        "OpenClaw for EU Users: What's Legal, What's Not",
        "Compliance Guide", fmt_color="warn",
        rationale="EU communities generated 1,070 comments in March with no current resource addressing their specific situation. A GDPR/EU AI Act compliance guide for OpenClaw deployment would be the only resource of its type. The BuyFromEU post alone had 521 comments. Serves: r/eutech, r/EU_Economics, r/BuyFromEU, r/selfhosted."))
    parts.append(idea(
        "5 Real Workflows That Changed Lives (With Exact Steps)",
        "Case Study Collection", fmt_color="success",
        rationale="The documented success stories (doubled salary, 3D printers, email automation, business launch) are high-credibility, specific outcomes. A post collecting all five with enough detail to replicate each one would serve the 731-comment LocalLLaMA sceptic audience with exactly the proof they are asking for. Potential to convert the largest sceptic community in the March dataset."))
    parts.append('</div>')
    parts.append(end_section())

    # ── S9 ENGAGEMENT PATTERNS ────────────────────────────────────────────────
    parts.append(section(9, "Engagement Patterns", "What drives 700+ comment threads — and what the new mainstream audience responds to differently"))
    parts.append("""<p>The March dataset shows two distinct engagement profiles operating simultaneously: the established r/openclaw pattern (builders rewarding knowledge transfer) and a new pattern from the 34 incoming communities (mainstream audiences engaging with drama, fear, and proof demands).</p>""")
    parts.append(cluster("Pattern 1 · Controversy + Institutional Drama = Maximum Comment Volume", "832 · 731 · 644 · 521 comments",
        color="warn",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The three posts generating 600+ comments are all controversy-adjacent: the C&amp;D nostalgia post (832), the LocalLLaMA "is it organic?" post (731), the multi-model setup post (644). Comments are not agreement — they are <em>argument</em>. Posts that present a clear position on a contested question (is OpenClaw overhyped? is the virality real? is Anthropic right?) generate more comment volume than posts that share neutral information. This is not a new insight about Reddit — it is specific to March 2026 because the contested questions are all new and the community has not yet reached consensus.</p>"""))
    parts.append(cluster("Pattern 2 · New Audiences Want Proof Before Engagement", "LocalLLaMA pattern",
        color="",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The LocalLLaMA posts pattern is instructive: high comment volume but moderate upvote scores. This means many people read and commented without upvoting — the audience is in evaluation mode, not validation mode. They are asking "should I believe this?" rather than "I already believe this and want more." Content that successfully converts this sceptical audience uses specific numbers, documentation, and real-world proof. Generic enthusiasm posts will be dismissed.</p>"""))
    parts.append(cluster("Pattern 3 · Hardware Builds Generate Cross-Community Spillover", "2,815 pts on r/raspberry_pi",
        color="accent",
        body="""<p style="font-size:0.85rem;color:var(--muted)">bastivkl's Pi Zero 2W personal assistant build (2,815 pts, 194 comments on r/raspberry_pi) and the OpenClaw Personal Assistant Device (1,038 pts on r/openclaw) are the same project reaching two different communities. The hardware element unlocks non-AI communities: r/raspberry_pi, r/homeassistant, r/mac, r/selfhosted. A build with clear BOM, setup steps, and a demo video would perform across all five communities simultaneously — a rare content format that works on both technical and non-technical audiences.</p>"""))
    parts.append(cluster("Pattern 4 · Authenticity in Fear Outperforms Positivity", "590 + 568 pts for fear/honesty posts",
        color="",
        body="""<p style="font-size:0.85rem;color:var(--muted)">"anyone feel scared?" (590 pts, 232 comments) and "Things I wish someone told me before I almost gave up" (619 pts, 264 comments) — posts that admit vulnerability and honest confusion outperform generic positivity in the March dataset. The mainstream audience that arrived in March is more anxious than the original enthusiast community. Honest "here's what I struggled with" content is the fastest way to build credibility with this new audience.</p>"""))
    parts.append(end_section())

    # ── S10 POWER USERS ───────────────────────────────────────────────────────
    parts.append(section(10, "Power Users &amp; Community Intelligence", "6 creators generating the highest-quality signal in March 2026"))
    parts.append('<div class="user-grid">')
    parts.append(user_card(
        "u/Aislot", "STRATEGIC CONTENT ARCHITECT",
        "4 posts generating 6,153 combined score in March. Creates consistently high-performing B2B-framed content: AI employment impact, multi-agent hardware setups, cost modelling. The Jack Dorsey layoff post (1,673 pts, 477 cmts) and multi-model setup post (2,311 pts, 644 cmts) define the 'AI or be replaced' narrative in this dataset.",
        "6,153 pts across 4 posts · r/aiagents, r/OpenAI"))
    parts.append(user_card(
        "u/bastivkl", "HARDWARE INNOVATOR",
        "2 posts generating 3,853 combined score. Built the Pi Zero 2W personal assistant (push-to-talk → OpenClaw → stream back) and documented it across r/raspberry_pi (2,815 pts) and r/openclaw (1,038 pts). Proves the hardware crossover content format. The same project reaching two very different audiences shows exceptional content engineering.",
        "3,853 pts across 2 posts · r/raspberry_pi, r/openclaw"))
    parts.append(user_card(
        "u/NoRecognition3349", "COMMUNITY TEACHER",
        "619 pts, 264 comments on 'Things I wish someone told me before I almost gave up on OpenClaw'. The post documents the exact failure modes (babysitting, token loops, agent confusion) and the specific fixes that resolved them, with a link to a full version with config examples. This is the clearest sign that new users are still struggling with onboarding.",
        "619 pts · 264 comments · r/openclaw"))
    parts.append(user_card(
        "u/ISayAboot", "USE-CASE DOCUMENTARIAN",
        "568 pts, 339 comments on 'Ways OpenClaw has Changed My Life'. Documents email automation (Office 365, 3x daily brief), video workflow (Gemini + Publer + Instagram scheduling), and starts describing more builds. The comment volume (339) suggests significant audience appetite for this format — more documented, specific workflows.",
        "568 pts · 339 comments · r/openclaw"))
    parts.append(user_card(
        "u/Sanshuba", "PROOF-OF-ROI POSTER",
        "780 pts, 212 comments on 'My agent doubled my salary, it found a new job for me'. The most specific ROI documentation in the March dataset: gave agent browser access, created job accounts, wrote CV in markdown, applied internationally, received offer exceeding $5k/month. The clearest proof-of-life content that sceptics in r/LocalLLaMA need to see.",
        "780 pts · 212 comments · r/openclaw"))
    parts.append(user_card(
        "u/donutloop", "CONSISTENT CONTRIBUTOR",
        "4 posts generating 1,789 combined score. Consistent presence across March maintaining technical content quality. Represents the contributor archetype that keeps communities healthy between viral moments — steady, reliable, high signal-to-noise ratio.",
        "1,789 pts across 4 posts · multiple subreddits"))
    parts.append('</div>')
    parts.append(end_section())

    # ── S11 PRODUCT OPPORTUNITIES ─────────────────────────────────────────────
    parts.append(section(11, "Product &amp; Service Opportunities", "Gaps identified directly from March frustrations and desires — each with documented demand"))
    parts.append(cluster("OPPORTUNITY 1 · Security-Audited OpenClaw Hosting", "First mover advantage · 3 communities screaming for this",
        color="danger",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The sysadmin and selfhosted communities have documented that they want to use OpenClaw but cannot deploy the official image in good conscience. A managed hosting service with a security-audited container, transparent CVE tracking, and defined network permission scope would convert this audience immediately. The key selling point is not features — it is <em>you can give this to your clients/employers without gambling your reputation on a container with 2,000 known vulnerabilities.</em></p>"""))
    parts.append(cluster("OPPORTUNITY 2 · EU-Region Deployment Service", "1,070 EU community comments with no current resource",
        color="warn",
        body="""<p style="font-size:0.85rem;color:var(--muted)">A GDPR-compliant OpenClaw deployment — either hosted in EU data centres or a verified self-deployment guide — addresses an audience that the acquisition and EU regulatory friction has made acutely aware of their gap. European SMBs who want AI agents but cannot legally route data through US-based services are a large, high-value, underserved market. This is a Wayne-sized opportunity if his audience has European reach.</p>"""))
    parts.append(cluster("OPPORTUNITY 3 · OpenClaw Hardware Kits", "Pi Zero 2W build: 2,815 pts · clear crossover demand",
        color="accent",
        body="""<p style="font-size:0.85rem;color:var(--muted)">bastivkl's Pi Zero 2W build demonstrated that there is a market for a "put OpenClaw in your pocket" hardware offering. A kit — hardware + SD card image + push-to-talk app + documented setup — would serve the r/raspberry_pi, r/mac, r/homeassistant communities simultaneously. The price point would be accessible, the differentiation is unique, and the demonstration is already documented and proven viral.</p>"""))
    parts.append(cluster("OPPORTUNITY 4 · Acquisition-Era Migration &amp; Continuity Service", "High anxiety = high willingness to pay for certainty",
        color="",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The community is anxious about post-acquisition changes. A service that monitors OpenClaw updates, translates breaking changes to existing installs, and maintains a changelog of what changed post-acquisition would capture the "I built serious infrastructure on this and cannot afford to have it break" audience. This could be subscription documentation, a monitored update service, or a managed installation.</p>"""))
    parts.append(cluster("OPPORTUNITY 5 · Local Model Concierge Setup", "$100k/year problem is documented and real",
        color="success",
        body="""<p style="font-size:0.85rem;color:var(--muted)">Aislot's post shows the ROI case for local model infrastructure is clear and convincing. The gap is that setting up multi-Mac Studio rigs with Kimi K2.5, Qwen 3.5, MiniMax 2.5, and EXO Labs distribution is beyond most users' capability. A "local model setup done for you" service — or at minimum an exceptionally detailed guide — would convert the LocalLLaMA audience who understands the math but can't execute the build.</p>"""))
    parts.append(end_section())

    # ── S12 AUDIENCE PROFILE ──────────────────────────────────────────────────
    parts.append(section(12, "Audience Profile", "Who arrived in March 2026 — a substantially expanded map of who OpenClaw now reaches"))
    parts.append("""<p>The original r/openclaw dataset described a relatively tight community: developers, AI-curious builders, agency owners. March 2026 added five entirely new audience segments. Wayne's content, products, and services should address all five — they are the audiences that the next 12 months of OpenClaw growth will be shaped by.</p>""")
    parts.append("""
<table class="report-table">
<thead>
<tr><th>Audience Segment</th><th>Source Subreddits</th><th>Core Concern</th><th>Conversion Trigger</th></tr>
</thead>
<tbody>
<tr>
  <td><strong>Core Builders</strong></td>
  <td>r/openclaw (39 posts)</td>
  <td>Post-acquisition stability, security, model costs</td>
  <td>Answers to Section 4's questions</td>
</tr>
<tr>
  <td><strong>PC Enthusiasts / Mainstream Tech</strong></td>
  <td>r/pcmasterrace, r/ProgrammerHumor</td>
  <td>OpenClaw as a cultural phenomenon — they know the name, they don't know the tool</td>
  <td>Specific, simple first-win tutorials</td>
</tr>
<tr>
  <td><strong>Security-Literate Sysadmins</strong></td>
  <td>r/sysadmin, r/selfhosted, r/homeassistant</td>
  <td>Is it deployable without compromising their infrastructure?</td>
  <td>Security audit + hardened image</td>
</tr>
<tr>
  <td><strong>Privacy-First / Local AI Advocates</strong></td>
  <td>r/LocalLLaMA, r/selfhosted, r/agi</td>
  <td>Is it actually local? Can I trust the architecture?</td>
  <td>Local model setup documentation with verified benchmarks</td>
</tr>
<tr>
  <td><strong>European Tech Community</strong></td>
  <td>r/BuyFromEU, r/eutech, r/EU_Economics</td>
  <td>Is this legally usable in the EU? Does Steinberger's move mean EU is abandoned?</td>
  <td>GDPR/EU AI Act compliance clarity</td>
</tr>
<tr>
  <td><strong>Job-Anxious Workers</strong></td>
  <td>r/aiagents, r/wallstreetbets, r/WallStreetDad</td>
  <td>Will AI take my job? Should I be learning this right now?</td>
  <td>Fear-validated skill roadmap content</td>
</tr>
<tr>
  <td><strong>AI Sceptics / Show-Me Crowd</strong></td>
  <td>r/LocalLLaMA (skeptic posts)</td>
  <td>Is any of this real and useful or is it all VC-funded hype?</td>
  <td>Specific documented outcomes with reproducible steps</td>
</tr>
</tbody>
</table>
""")
    parts.append(alert("info", "&#x1F465; Audience Shift Summary",
        "The March 2026 dataset represents the most significant single-month audience expansion in the OpenClaw community's documented history. "
        "In the original dataset, 100% of posts came from r/openclaw. In March 2026, 61% came from 34 other communities. "
        "The most important implication for Wayne: the content, tone, and proof requirements that work for the r/openclaw core (assumes existing familiarity, rewards technical depth) "
        "will not work for the five new segments listed above. Each segment needs a distinct content strategy."))
    parts.append(end_section())

    # ── S13 MASTER TIPS ───────────────────────────────────────────────────────
    parts.append(section(13, "Master Tips Compendium", "March-specific actionable intelligence — every entry derived from the actual March dataset"))

    parts.append(tips_cat("&#x1F6E1;&#xFE0F;", "Security — Non-Negotiable Before Any Deployment",
        tip("Run a container security scan before deploying: <code>docker run --rm -v /var/run/docker.sock:/var/run/docker.sock aquasec/trivy image ghcr.io/openclaw/openclaw</code>. The official image will show ~2,000 CVEs. Know what you're running.", "r/sysadmin, March 2026")
        + tip("Never give OpenClaw access to credentials, email, or messaging until you've reviewed the container's network permissions. The 7 critical CVEs have no current patch.", "r/selfhosted")
        + tip("The 1panel build has the same vulnerability profile as the default image. Alpine/openclaw is not Alpine — it is Debian 12 with 1,156 vulnerabilities. Verify any 'lightweight' claim with an actual scan.", "r/sysadmin")
        + tip("Read every line of any skill's <code>scripts/</code> folder before installing from ClawHub. Backdoored skills exist. Download counts can be faked. The code review is not optional.", "r/openclaw veteran")
        + tip("For production deployments: run OpenClaw behind a VPN or restricted VLAN. It should not have unrestricted outbound internet access given its current security posture.", "r/homeassistant")))

    parts.append(tips_cat("&#x1F4BC;", "Post-Acquisition Navigation",
        tip("The open-source foundation commitment means the codebase is legally protected from being locked down by OpenAI. But 'open-source' does not mean 'free hosting forever'. Keep local copies of your complete config, skills, and SOUL.md. Portability is now a survival requirement.", "r/OpenAI acquisition post")
        + tip("Follow Peter Steinberger directly (GitHub, X/Twitter) for the most direct indication of where OpenClaw's architecture is heading under OpenAI. His product decisions will signal the acquisition's real intent faster than any press release.", "community advice")
        + tip("The Anthropic C&D means the Claude API path is legally contested. Model-router configurations should include at least one non-Anthropic fallback. OpenAI o3-mini and Gemini 2.5 Flash are the recommended alternatives at cost-effective tier.", "r/ClaudeAI March context")
        + tip("Claude Code's scheduled tasks are not a full OpenClaw replacement — they are a cron-based automation layer without the file system, skill ecosystem, or agent memory architecture. The C&D does not eliminate the need for what OpenClaw does.", "r/aiagents analysis")))

    parts.append(tips_cat("&#x1F4BB;", "Local Models — The $100k Math Applied",
        tip("Frontier model 24/7 cost floor (March 2026 pricing): Claude Opus 4 at 24/7 = ~$8,300/month = ~$100k/year. Sonnet = ~$1,200/month. Unless you have a revenue case, Sonnet should be your default with Opus for critical tasks only.", "u/Aislot calculation, 1,028 pts")
        + tip("Local model ROI threshold: if you're running OpenClaw more than 16 hours/day, a Mac Studio M4 Ultra (~$10k) pays back against frontier API costs in approximately 10 months. Multiple units reduce break-even further.", "u/Aislot, March 2026")
        + tip("Documented local model stack (March 2026 power user): Kimi K2.5 (600GB via EXO Labs across 3 Mac Studios) + MiniMax 2.5 (120GB) + Qwen 3.5 (220GB) + one uncensored model for red-team tasks. This is aspirational for most users but establishes the ceiling.", "u/Aislot, r/aiagents")
        + tip("For users who aren't ready for full local infrastructure: the model routing optimisation (Sonnet as default, Opus only for specific task types defined in SOUL.md) is still the single highest-ROI configuration change available. This has not changed from the original dataset.", "consistent signal across both datasets")))

    parts.append(tips_cat("&#x1F527;", "Proven Workflow Patterns from March 2026",
        tip("Email automation baseline (documented, 568 pts): Connect to Office 365 → define 3 tiers (delete permanently / archive / urgent-flag) → 3x daily summary brief → auto-draft replies for flagged items. Time to set up: under 2 hours. Time reclaimed: 45-60 minutes daily.", "u/ISayAboot, r/openclaw")
        + tip("Job search automation (documented outcome: doubled salary): Give agent browser access → agent creates target job site accounts → agent writes CV in markdown → agent finds and applies to matching positions → you review shortlisted offers. Works. Documented by a real user with outcome confirmed.", "u/Sanshuba, 780 pts")
        + tip("3D printing workflow (documented, 1,749 pts): Skills covering model finder + slicer integration + print queue management = zero manual design work. If you have hardware with print capability, this is a 1-time setup with indefinite value.", "u/mescalan, r/OpenAI")
        + tip("Multi-agent team architecture (March 2026 validated): Run 3 agents with non-overlapping roles (Researcher / Creator / Publisher) rather than one multi-task agent. 3 focused agents consistently outperform 1 bloated agent in cost and reliability per the March power user evidence.", "u/Aislot pattern, multiple corroborating posts")
        + tip("Onboarding shortcut for new users frustrating themselves: Start with the single most boring, repetitive task you do daily. Build the agent for that one task only. Get it reliable. Then — and only then — expand scope. Loop failures are almost always caused by too many simultaneous objectives.", "u/NoRecognition3349, 619 pts")))

    parts.append(tips_cat("&#x1F30D;", "EU Users — March 2026 Specific Guidance",
        tip("The OpenClaw creator's comment on EU regulations confirms that EU-specific development is not currently prioritised. EU users operating under GDPR should run OpenClaw entirely on EU-hosted infrastructure (Hetzner EU, OVHcloud) with no data routing through US-region services.", "r/BuyFromEU, r/eutech signal")
        + tip("Under EU AI Act Article 6, automated email deletion agents like the Meta AI Safety Director scenario would potentially require human-in-the-loop confirmation for consequential actions. Configure OpenClaw's automation scope conservatively in EU deployments.", "r/EU_Economics context")
        + tip("EXO Labs (used by Aislot for local model distribution) does not have an EU-specific data residency guarantee at time of March 2026 reporting. EU users deploying local model infrastructure should verify hosting location before using cloud distribution layers.", "EU compliance context")))

    parts.append(end_section())

    # ── S14 RECOMMENDATIONS ───────────────────────────────────────────────────
    parts.append(section(14, "Strategic Recommendations for Wayne", "Three actions calibrated to the March 2026 moment — the most pivotal month in OpenClaw's documented history"))
    parts.append("""
<p>The March 2026 dataset describes a community at a genuine inflection point. The acquisition, the security crisis, the mainstream viral breakout, and the Anthropic C&D all landed simultaneously. For Wayne as a researcher, practitioner, and potential content creator — the recommendations below are calibrated to this specific moment, not to a generic AI tool environment.</p>
""")
    parts.append(cluster("RECOMMENDATION 1 · Do the Security Audit — Today", "Non-negotiable · 30 minutes · zero downside",
        color="danger",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">If you are running OpenClaw with access to any credentials, email, messaging, or file systems, run a container security scan on your current image version before your next session. The sysadmin community documented 2,000+ CVEs in the official image in March 2026. This is not theoretical risk — it is known, documented, and publicly available to anyone looking for a target.</p>
<p style="font-size:0.85rem;color:var(--muted)">Action: Run <code>docker run --rm aquasec/trivy image [your-openclaw-image]</code>. Review the critical findings. The community's documented response is to isolate OpenClaw behind a VPN and audit every skill's scripts/ folder. Do not give any new skills network permissions until the container situation is resolved by the OpenClaw team post-acquisition.</p>
"""))
    parts.append(cluster("RECOMMENDATION 2 · Position for the Mainstream Audience That Just Arrived", "31 new subreddits · hundreds of thousands of new potential users",
        color="success",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">The LocalLLaMA "Anyone actually using Openclaw?" post generated 731 comments of people asking to be convinced. The sysadmin and selfhosted communities have the same appetite. These are not hostile audiences — they are technically literate, high-trust gatekeepers who will adopt OpenClaw the moment someone answers their specific questions credibly.</p>
<p style="font-size:0.85rem;color:var(--muted)">Wayne is positioned as an early adopter and researcher who has used OpenClaw seriously — the "Things I wish I knew" and "Ways OpenClaw Changed My Life" post formats performed at 568–619 pts. For the mainstream audience that arrived in March, a single well-documented, honest account of how Wayne actually uses OpenClaw — with specific numbers, failures acknowledged, and outcomes reported — would be the most effective possible entry into this new, much larger audience.</p>
"""))
    parts.append(cluster("RECOMMENDATION 3 · Diversify and Document Now — The Window Is Open", "Post-acquisition is the best time to become the trusted guide",
        color="",
        body="""
<p style="font-size:0.85rem;color:var(--muted)">The acquisition creates a 90-day window where the community will turn to whoever it trusts most for clarity. The questions identified in Section 4 (what changes, what doesn't, is the open-source commitment real, what about EU users, what about the C&D) are not currently answered by anyone. The person who answers them — clearly, calmly, with sourced evidence — will own this community's trust through the transition period and well beyond.</p>
<p style="font-size:0.85rem;color:var(--muted)">Simultaneously: keep your configurations, memory files, skills, and SOUL.md regularly exported to a format portable across any installation. The acquisition means the platform will change. The knowledge you've invested in building — your agent's understanding of you, your workflows, your automation logic — needs to be portable regardless of what OpenAI does next.</p>
"""))
    parts.append(end_section())

    # ── S15 VIRAL SCORE ───────────────────────────────────────────────────────
    parts.append(section(15, "Community Viral Score Card", "March 2026 — unprecedented cultural momentum"))
    parts.append(f"""
<div class="score-display" style="--score-pct:95">
  <div class="score-circle"><span>9.5</span></div>
  <div class="score-details">
    <h4>Viral Score: 9.5 / 10 — Peak Cultural Momentum</h4>
    <p>Top post score: {TOP_SCORE:,} upvotes (up from 1,256 in previous dataset — a 17.5&times; increase). Three posts exceeded 10,000 upvotes in a single month. OpenClaw content spread across 35 subreddits. The community has achieved mainstream meme substrate status — the highest possible cultural penetration signal for a developer tool.</p>
  </div>
</div>
""")
    parts.append("""
<table class="report-table">
<thead><tr><th>Metric</th><th>Original Dataset</th><th>March 2026</th><th>Change</th></tr></thead>
<tbody>
<tr><td>Peak post score</td><td>1,256</td><td>22,056</td><td style="color:var(--success)">+17.5&times;</td></tr>
<tr><td>Posts over 10k upvotes</td><td>0</td><td>3</td><td style="color:var(--success)">New milestone</td></tr>
<tr><td>Total comments / post (avg)</td><td>33</td><td>218</td><td style="color:var(--success)">+6.6&times;</td></tr>
<tr><td>Subreddits represented</td><td>~2</td><td>35</td><td style="color:var(--success)">Mainstream</td></tr>
<tr><td>Posts outside r/openclaw</td><td>~5%</td><td>61%</td><td style="color:var(--success)">Cross-community</td></tr>
<tr><td>Corporate events generating posts</td><td>0</td><td>3 (acquisition, C&D, Claude Code launch)</td><td style="color:var(--warn)">Structural change</td></tr>
<tr><td>Security issues surfaced</td><td>0 documented</td><td>1 critical (2,000+ CVEs)</td><td style="color:var(--danger)">Requires action</td></tr>
</tbody>
</table>
""")
    parts.append(end_section())

    # ── S16 GOLD QUOTES ───────────────────────────────────────────────────────
    parts.append(section(16, "Gold Quotes", "The sentences that define March 2026 — sourced directly from the dataset"))
    parts.append("""<p>These are the quotes from the March 2026 dataset that carry the highest intelligence density — each one encapsulates a theme, a turning point, or a community truth in a single readable sentence.</p>""")

    parts.append(gold_quote(
        "openclaw literally",
        "u/Common-Beautiful353 · r/pcmasterrace",
        "22,056",
        ["Diamond Tier", "Viral Breakout", "Cultural Arrival"],
        diamond=True))
    parts.append("""<p style="font-size:0.8rem;color:var(--muted);margin-bottom:20px">Two words. Zero explanation. 22,056 upvotes. This is what cultural arrival looks like — when a reference alone is sufficient for an entire mainstream community to recognise and validate it. The most important data point in the March 2026 dataset is not a statistic. It is this post.</p>""")

    parts.append(gold_quote(
        "If you aren't AI native, you have become expendable to execs. You need to learn these skills now. These aren't optional skills anymore. They're mandatory. And the time you have left to learn them has quickly...",
        "u/Aislot · r/aiagents · Jack Dorsey event post",
        "1,673 (477 comments)",
        ["Gold Tier", "Employment Fear", "Call to Action"]))

    parts.append(gold_quote(
        "I gave a task to my agent: find me a better paying job. I gave it access to a browser where my LinkedIn account was connected, it suggested me creating accounts on a few other sites (it created the accounts for me with a little help), then created a curriculum in .md... My salary doubled.",
        "u/Sanshuba · r/openclaw · 'My agent doubled my salary'",
        "780 (212 comments)",
        ["Gold Tier", "Proof of ROI", "Replicable Outcome"]))

    parts.append(gold_quote(
        "I have 3 Mac Studios and a DGX Spark running 4 high end local models. They're chugging 24/7/365. I spent a third of the yearly frontier API cost to buy these computers. I'll be able to use them for years for free. Not a single prompt goes to a cloud server.",
        "u/Aislot · r/aiagents · local models post",
        "1,028 (292 comments)",
        ["Gold Tier", "Cost Intelligence", "Privacy Argument"]))

    parts.append(gold_quote(
        "The absolute state of development in 2026: have a plan, give everything to AI — chrome tabs with gmail, Hetzner, a capped expense wise card. Use parallel subagents via main claude instance, aggressively divide and automate everything. Then just go ahead and do something that is fun, like scroll on Reddit.",
        "u/Deep-Station-1746 · r/ClaudeCode",
        "613 (225 comments)",
        ["Silver Tier", "Automation Achieved", "New Default"]))

    parts.append(gold_quote(
        "I've been in the same boat as a lot of people here spending the first two weeks babysitting, burning tokens, and watching my agent loop on the same answer eight times in a row. After a lot of trial and error I've got it running reliably.",
        "u/NoRecognition3349 · r/openclaw · 'Things I wish someone told me'",
        "619 (264 comments)",
        ["Silver Tier", "Honest Struggle", "New User Reality check"]))

    parts.append(end_section())

    # ── S17 KEY FACTS ─────────────────────────────────────────────────────────
    parts.append(section(17, "Key Facts &amp; Statistics", "Hard numbers from the March 2026 dataset — for reference, citation, and decision-making"))
    parts.append("""
<table class="report-table">
<thead><tr><th>Fact</th><th>Source / Context</th></tr></thead>
<tbody>
<tr><td>100 posts · 21,808 comments · 35 subreddits analysed (March 2026)</td><td>This dataset</td></tr>
<tr><td>Top post score: <strong>22,056 upvotes</strong> ("openclaw literally" · r/pcmasterrace)</td><td>u/Common-Beautiful353</td></tr>
<tr><td>3 posts exceeded 10,000 upvotes in March 2026 (vs 0 in previous dataset)</td><td>Dataset comparison</td></tr>
<tr><td>Average comments per post: <strong>218</strong> (vs 33 in previous dataset — 6.6&times; increase)</td><td>Computed from dataset</td></tr>
<tr><td>Only 39% of posts came from r/openclaw — 61% from 34 other communities</td><td>Subreddit distribution analysis</td></tr>
<tr><td>OpenAI officially acquired OpenClaw — confirmed by Sam Altman; Peter Steinberger joins OpenAI</td><td>r/OpenAI post, 1,914 pts, 364 comments</td></tr>
<tr><td>OpenClaw transitions to open-source foundation as part of acquisition deal</td><td>u/just_a_person_27 acquisition post</td></tr>
<tr><td>Anthropic sent cease &amp; desist to OpenClaw team in March 2026</td><td>r/ClaudeAI, 1,370 pts, 136 comments</td></tr>
<tr><td>Anthropic simultaneously launched Claude Code scheduled tasks — direct OpenClaw competitor</td><td>r/aiagents, 1,318 pts, 168 comments</td></tr>
<tr><td>Official GHCR Docker image: ~2,000 CVEs · 7 critical · no patches available</td><td>r/sysadmin, 2,233 pts, 314 comments</td></tr>
<tr><td>Meta AI Safety &amp; Alignment Director's inbox was wiped by her own OpenClaw agent</td><td>r/nottheonion, 10,265 pts, 443 comments</td></tr>
<tr><td>Jack Dorsey used AI to lay off 4,000 workers in a single tweet (March 2026)</td><td>r/aiagents, 1,673 pts, 477 comments</td></tr>
<tr><td>Frontier model cost at 24/7 operation: ~$100,000/year; equivalent local hardware: ~$30,000 one-time</td><td>u/Aislot, 1,028 pts, 292 comments</td></tr>
<tr><td>User documented salary doubling using OpenClaw agent to find and apply for jobs</td><td>u/Sanshuba, 780 pts, 212 comments</td></tr>
<tr><td>New ecosystem communities active in March: r/clawdbot (6 posts, 862 cmts) · r/myclaw · r/openclawsetup · r/moltbot</td><td>Subreddit distribution</td></tr>
<tr><td>EU communities generated 1,070+ comments: r/BuyFromEU (521) · r/eutech (281) · r/EU_Economics (268)</td><td>EU cluster analysis</td></tr>
<tr><td>LocalLLaMA sceptic post "Anyone actually using Openclaw?" — 731 comments — the 2nd highest in March</td><td>u/rm-rf-rm, r/LocalLLaMA</td></tr>
<tr><td>Google announced Gmail, Drive, and Docs as "agent-ready" for OpenClaw integration</td><td>r/technology, 1,658 pts, 145 comments</td></tr>
</tbody>
</table>
""")
    parts.append(end_section())

    # ── S18 PRIVACY ───────────────────────────────────────────────────────────
    parts.append(section(18, "Privacy &amp; Methodology Note", "Data sourcing, ethical framework, and scope of analysis"))
    parts.append("""
<p>This report is based exclusively on <strong>publicly available Reddit posts and metadata</strong>. All data was collected from public subreddits where posts were made voluntarily by independent users with no connection to this research. No private messages, direct messages, deleted posts, or non-public data were accessed or used.</p>
<p>The March 2026 dataset comprises <strong>100 posts · 21,808 comment interactions · 35 subreddits</strong>. Comment counts are drawn from Reddit's <code>num_comments</code> field (total comments including nested replies). Post scores represent net upvotes at time of collection.</p>
<p>Authors are identified only by their publicly chosen Reddit usernames. No attempts were made to identify real-world identities. Quoted text is reproduced from public posts under fair use for research and commentary purposes. All quoted content belongs to the original Reddit authors.</p>
<p>Sentiment classifications, percentage estimates, and thematic categorisations represent the analytical judgement of the report authors based on systematic review of post content and engagement patterns. These are estimates and should not be treated as precise scientific measurements.</p>
<p>The intelligence value of this dataset derives specifically from the fact that these posts were written <em>voluntarily and independently</em> by real users with no connection to Audience Intelligence or to each other. The absence of coordination is what makes this data genuine market intelligence rather than curated testimonials.</p>
""")
    parts.append(end_section())

    # ── CLOSING MANDATE ───────────────────────────────────────────────────────
    parts.append(section(19, "Closing Intelligence Mandate", "10 definitive findings from 100 posts and 21,808 comment interactions · March 2026"))
    parts.append('<h3 style="color:var(--heading);font-size:1rem;margin-bottom:14px">10 Definitive Findings from the March 2026 Dataset</h3>')
    parts.append("""
<ol style="font-size:0.88rem;line-height:1.9;color:var(--text);margin-left:24px;margin-bottom:28px">
<li><strong>OpenClaw is in the most consequential transition of its existence.</strong> The OpenAI acquisition, Anthropic C&D, and mainstream viral breakout all landed in March 2026. The platform's identity is being renegotiated in real time. The community members who stay informed and adapt fastest will compound the most value from this moment.</li>
<li><strong>The security situation is real and documented.</strong> 2,000+ CVEs in the official Docker image is not a rumour — it was verified independently by the sysadmin, selfhosted, and homeassistant communities. Anyone deploying OpenClaw in a sensitive context without addressing this is running a documented risk.</li>
<li><strong>OpenClaw has achieved mainstream cultural arrival.</strong> "openclaw literally" at 22,056 upvotes on r/pcmasterrace is not a data anomaly — it is evidence that a developer tool has crossed into mainstream cultural vocabulary. This happens approximately once per decade per technology category.</li>
<li><strong>The open-source foundation commitment is the critical acquisition term.</strong> Whatever OpenAI's commercial intentions, the open-source foundation ensures the codebase's long-term community availability. This is the fact that should determine how much technical debt you invest in OpenClaw-specific infrastructure.</li>
<li><strong>The local model ROI case is now proven by real users at scale.</strong> $100k/year frontier API costs vs $30k one-time hardware — with documented deployments running 4 concurrent models 24/7. For high-volume use cases, local infrastructure has crossed the financial viability threshold.</li>
<li><strong>A massive new audience arrived in March and has not yet been served.</strong> 731 comments of LocalLLaMA sceptics, 521 EU community comments, 314 sysadmin comments — these are substantive audiences with specific questions that no current content answers. The first person to answer them credibly owns these audiences.</li>
<li><strong>The most impactful content format in March 2026 is specific, documented, replicable outcomes.</strong> Salary doubled. 3D printers automated. Email mastered. $100k calculated. Every top-performing content post has a number, an outcome, and enough detail to replicate. Generic enthusiasm is not a viable content strategy for the March 2026 audience.</li>
<li><strong>Claude Code is not a replacement for OpenClaw — but it is a competitor for mindshare.</strong> Anthropic's scheduled tasks are narrower in scope but have Anthropic's brand trust behind them. The community will route toward whichever platform answers the post-C&D question most credibly. OpenClaw's open-source foundation under OpenAI is the counter-argument.</li>
<li><strong>EU users are an underserved, high-value audience segment with documented demand and zero current supply.</strong> 1,070 EU community comments in a single month. No GDPR/EU AI Act compliance guide exists. The market gap is documented, the audience is engaged, and the content does not currently exist.</li>
<li><strong>The next 90 days are the most important community trust window in OpenClaw's history.</strong> Acquisition transitions create information vacuums. People filling those vacuums with clear, credible, sourced information will own community trust long after the transition is complete. Wayne is positioned to be that voice.</li>
</ol>
""")
    parts.append(f"""
<div class="gold-quote gold-quote--diamond" style="margin-bottom:28px">
<div class="gold-quote__text">"The March 2026 dataset does not describe a community discussing a tool. It describes a community witnessing a cultural moment — the acquisition of the most viral AI agent of 2026, a mainstream meme breakthrough, a security crisis, and a legal challenge, all in a single month. The people who understand what just happened, and act on it clearly and quickly, will compound advantages that the late majority will spend years trying to catch up to."</div>
<div class="gold-quote__meta"><span>Synthesised from March 2026 r/openclaw cross-community intelligence</span><span>{TOTAL_POSTS} posts · {TOTAL_COMMENTS:,} comments · 35 subreddits</span></div>
</div>
""")
    parts.append("""
<div class="mandate-box">
<div class="mandate-box__statement">
The March 2026 dataset confirms: OpenClaw has left the early adopter phase and is entering mainstream infrastructure.<br>
The community questions are no longer "how do I use this?" — they are "can I trust this?" and "will it survive the acquisition?"<br><br>
<strong>Wayne's three most important next actions:</strong><br><br>
1. Run the Docker security audit and implement VPN isolation — <em>today, 30 minutes, eliminates a documented real risk</em><br>
2. Publish one specific, numbered, honest account of how you use OpenClaw — <em>this week, directly serves the 731 LocalLLaMA sceptics and 314 sysadmin moderates who arrived in March</em><br>
3. Export your SOUL.md, memory files, and skill configurations to a portable format — <em>before the next OpenAI update, 15 minutes, insurance against acquisition-driven changes</em>
</div>
</div>
""")
    parts.append("""
<div class="alert alert--info" style="margin:28px 0">
<div class="alert__title">&#x1F4CA; CLOSING — What This Data Actually Represents</div>
<p>These posts were not collected from OpenClaw supporters who were asked for their opinion. They were written voluntarily by independent users — developers, sysadmins, EU tech workers, job-anxious professionals, AI sceptics, and hardware builders — with no connection to each other beyond sharing Reddit. Thirty-five separate communities discussed OpenClaw in March 2026 without coordination. That is what makes this data intelligence, not just content.</p>
<p>Across <strong>100 posts and 21,808 comment interactions</strong> spanning 35 subreddits, the dataset captures something the original r/openclaw data could not show: what OpenClaw looks like from the outside. The mainstream audience that arrived in March 2026 is asking different questions, applying different standards, and requiring different proof than the original community. The gap between those requirements and what currently exists is the research brief for the next phase of Wayne's work.</p>
<p>The 22,056-upvote post is two words. The highest-engagement questions have no current answers. The security gap is documented and unpatched. The EU audience is real and unserved. Each of these is a problem. Each of these is an opportunity. The March 2026 dataset identifies both with equal precision.</p>
</div>
""")
    parts.append('<h3 style="color:var(--heading);font-size:1rem;margin:28px 0 16px">First 72 Hours Action Plan</h3>')
    parts.append("""
<ol style="font-size:0.88rem;line-height:1.9;color:var(--text);margin-left:24px">
<li><strong>Security audit your container:</strong> <code>docker run --rm aquasec/trivy image [your-openclaw-image]</code>. Review all critical findings. Do not skip this. (30 minutes)</li>
<li><strong>Export your configuration:</strong> Copy SOUL.md, MEMORY.md, AGENTS.md, and your skills list to a secure local backup. The acquisition means the platform will change. Your intelligence should not depend on any single installation surviving intact. (15 minutes)</li>
<li><strong>Review your model routing:</strong> If you are using Claude Opus as default, switch to Sonnet with Opus reserved for specific high-stakes task types. The cost difference is documented at 7–10&times; per interaction. (10 minutes)</li>
<li><strong>Follow Peter Steinberger on GitHub</strong> and monitor the OpenClaw repository's Issues and Discussions tab for acquisition-related changes. This is your most reliable early-warning channel for breaking changes. (5 minutes, then passive)</li>
<li><strong>Write one "how I actually use OpenClaw" post</strong> — for your own records if nothing else. With specific workflows, honest failures, and current outcomes. The act of writing it will clarify your own thinking and produce content the March 2026 audience is explicitly asking for. (1–2 hours)</li>
<li><strong>Read the BuyFromEU and eutech threads</strong> if you have any European clients or audience. The EU regulatory conversation is live and specific. Understanding it positions you to serve a large, currently unserved segment. (30 minutes)</li>
<li><strong>Test one local model setup</strong> using a free-tier Mac or Linux machine with Ollama + Qwen 3.5 or Llama 3.3. Establishing a working local model path now — before you need it — means the acquisition has no leverage over your workflows. (2 hours)</li>
</ol>
""")
    parts.append(end_section())

    return "\n".join(parts)


# ─── ASSEMBLE FULL HTML ────────────────────────────────────────────────────────

def build_html(body_content):
    gen_date = datetime.now().strftime("%d %B %Y")
    cover_end = body_content.find('</div>', body_content.find('class="cover"')) + 6
    cover = body_content[:cover_end]
    main_content = body_content[cover_end:]
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Audience Intelligence Report — OpenClaw Goes Mainstream · March 2026 · Reddit Cross-Community Intelligence</title>
<style>
{CSS}
</style>
</head>
<body>

{cover}

<main id="report-main">
{main_content}
</main>

<div class="page-footer">
  Generated by <strong>Audience Intelligence</strong> &middot; <a href="https://audienceintelligence.com">audienceintelligence.com</a> &middot; {gen_date}<br>
  Prepared for <strong>Wayne Michael</strong> &middot; OpenClaw March 2026 Cross-Community Intelligence Report &middot; 35 Subreddits
</div>

<div class="disclaimer">
DISCLAIMER: This report is produced for informational and entertainment purposes only. It does not constitute legal, financial, or professional advice. Figures, percentages, and sentiment classifications are estimates derived from analysis of publicly available Reddit posts and may not be precisely accurate. Users should independently verify any data, claims, or financial outcomes before relying on them for strategic or personal decisions. All quoted content belongs to the original Reddit authors. For more information visit audienceintelligence.com.
</div>

</body>
</html>"""


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    print("Building March 2026 fresh intelligence report...")
    body = build_report()
    html = build_html(body)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report saved to: {OUT_PATH}")
    print(f"File size: {len(html):,} characters")
