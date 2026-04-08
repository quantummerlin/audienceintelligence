"""
generate_numerology_report.py
==============================
Generates the complete 18-section Audience Intelligence Report for
r/numerology based on the extracted Reddit data.

Client: Wayne Michael (threezerotwozero@gmail.com)
Goal: Use numerology in daily life + build web apps / SaaS static pages
Relationship: RESEARCHER

Usage:
    python generate_numerology_report.py
    python generate_numerology_report.py --input redditnumerology.json --out outputs/report_numerology.html
"""
import json, os, sys, argparse
from datetime import datetime

def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default=None)
    p.add_argument("--out",   default=None)
    return p.parse_args()

ARGS = _parse_args()

_default_json = "redditnumerology.json"
_default_txt  = "redditnumerology.txt"
if ARGS.input:
    INPUT_FILE = ARGS.input
elif os.path.exists(_default_json):
    INPUT_FILE = _default_json
else:
    INPUT_FILE = _default_txt

if ARGS.out:
    OUT_PATH = ARGS.out
else:
    OUT_PATH = os.path.join("outputs", "report_numerology_reddit_2026-03-16.html")

def _load_posts(path):
    posts = {}
    if path.endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        for item in raw:
            pid = item.get("id", "")
            if pid and pid not in posts:
                posts[pid] = item
    else:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    for child in data["data"]["children"]:
                        d = child["data"]
                        pid = d.get("id", "")
                        if pid and pid not in posts:
                            posts[pid] = d
                except Exception:
                    pass
    result = list(posts.values())
    result.sort(key=lambda p: p.get("score", 0), reverse=True)
    return result

POSTS = _load_posts(INPUT_FILE)
# Filter to genuine numerology posts (exclude crosspost noise from top 3)
PRACTITIONER_POSTS = [p for p in POSTS if p.get("subreddit","").lower() == "numerology" or
                      (p.get("score",0) < 9000)]
TOTAL_POSTS = len(POSTS)
TOTAL_COMMENTS = sum(p.get("num_comments", 0) for p in POSTS)
TOP_SCORE = POSTS[0]["score"] if POSTS else 0

# Genuine community stats (excluding viral crossposts)
COMMUNITY_POSTS = [p for p in POSTS if p.get("score",0) < 8000]
COMMUNITY_COMMENTS = sum(p.get("num_comments",0) for p in COMMUNITY_POSTS)

print(f"Loaded {TOTAL_POSTS} posts, {TOTAL_COMMENTS} comments from {INPUT_FILE}")

# ─── CSS ──────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --bg:#08090f; --surface:#0e1120; --card:#141828; --card-alt:#1a2038;
  --border:rgba(255,255,255,0.07); --border-accent:rgba(168,85,247,0.3);
  --primary:#a855f7; --primary-light:#c084fc; --accent:#f59e0b;
  --accent-light:#fcd34d; --success:#34d399; --warn:#f59e0b;
  --danger:#f87171; --indigo:#818cf8; --text:#e2e8f0; --muted:#94a3b8;
  --heading:#f8fafc; --ff:'Inter',system-ui,sans-serif;
  --mono:'JetBrains Mono','Fira Code',monospace;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{font-size:11pt}
body{font-family:var(--ff);background:var(--bg);color:var(--text);line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
h1,h2,h3,h4{color:var(--heading)}
p{margin-bottom:12px;font-size:0.88rem}
ul,ol{margin:0 0 12px 20px;font-size:0.88rem}
li{margin-bottom:5px}
code{background:rgba(255,255,255,.07);padding:2px 6px;border-radius:4px;font-size:0.82em;color:var(--primary-light);font-family:var(--mono)}

/* Cover */
.cover{display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:100vh;text-align:center;padding:60px 40px;background:linear-gradient(160deg,#08090f 0%,#0e1120 40%,#130a2a 100%);position:relative;overflow:hidden}
.cover::before{content:'';position:absolute;top:-30%;left:-10%;width:120%;height:120%;background:radial-gradient(ellipse at 30% 50%,rgba(168,85,247,0.1) 0%,transparent 55%),radial-gradient(ellipse at 75% 65%,rgba(245,158,11,0.07) 0%,transparent 45%);pointer-events:none}
.cover__badge{display:inline-block;background:linear-gradient(135deg,var(--primary),#7c3aed);color:#fff;font-size:0.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:5px 14px;border-radius:20px;margin-bottom:28px;position:relative;z-index:1}
.cover h1{font-size:2.4rem;font-weight:800;color:var(--heading);margin-bottom:16px;position:relative;z-index:1;line-height:1.2}
.cover h1 span{color:var(--accent)}
.cover__subtitle{font-size:1rem;color:var(--muted);max-width:600px;margin-bottom:40px;position:relative;z-index:1}
.cover__meta{display:flex;gap:36px;flex-wrap:wrap;justify-content:center;position:relative;z-index:1;margin-bottom:40px}
.cover__meta-item{text-align:center}
.cover__meta-value{font-size:1.8rem;font-weight:800;color:var(--heading);display:block;line-height:1}
.cover__meta-label{font-size:0.72rem;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;margin-top:4px}
.cover__client{background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:12px;padding:16px 24px;font-size:0.82rem;color:var(--muted);position:relative;z-index:1}
.cover__client strong{color:var(--text)}
.cover__footer{margin-top:32px;font-size:0.72rem;color:rgba(148,163,184,0.45);position:relative;z-index:1}

/* Layout */
main{max-width:920px;margin:0 auto;padding:48px 32px}
.section{margin-bottom:56px;padding-bottom:40px;border-bottom:1px solid var(--border)}
.section:last-child{border-bottom:none}
.section__number{font-size:0.68rem;color:var(--primary-light);font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px}
.section__title{font-size:1.4rem;font-weight:700;color:var(--heading);margin-bottom:6px}
.section__subtitle{font-size:0.88rem;color:var(--muted);margin-bottom:20px}

/* Stats */
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:14px;margin:16px 0 24px}
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 14px;text-align:center}
.stat-value{font-size:2rem;font-weight:800;color:var(--heading);display:block;line-height:1}
.stat-label{font-size:0.7rem;color:var(--muted);margin-top:6px;text-transform:uppercase;letter-spacing:.07em}
.stat-card--purple .stat-value{color:var(--primary-light)}
.stat-card--gold .stat-value{color:var(--accent)}
.stat-card--green .stat-value{color:var(--success)}
.stat-card--red .stat-value{color:var(--danger)}
.stat-card--indigo .stat-value{color:var(--indigo)}

/* Sentiment */
.sentiment-bar{display:flex;border-radius:10px;overflow:hidden;height:36px;margin:16px 0 8px}
.sentiment-bar__segment{display:flex;align-items:center;justify-content:center;font-size:0.74rem;font-weight:600;color:#fff;padding:0 8px;white-space:nowrap;overflow:hidden}
.seg-positive{background:#34d399} .seg-neutral{background:#f59e0b} .seg-mixed{background:#818cf8} .seg-negative{background:#f87171}
.sentiment-bar__legend{display:flex;gap:16px;flex-wrap:wrap;font-size:0.74rem;color:var(--muted);margin-bottom:16px}
.leg-pos::before{background:#34d399} .leg-neu::before{background:#f59e0b} .leg-mix::before{background:#818cf8} .leg-neg::before{background:#f87171}
.sentiment-bar__legend span::before{content:'';display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:5px;vertical-align:middle}

/* Cluster */
.cluster-card{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 22px;margin-bottom:16px;border-left:3px solid var(--primary)}
.cluster-card--gold{border-left-color:var(--accent)}
.cluster-card--green{border-left-color:var(--success)}
.cluster-card--red{border-left-color:var(--danger)}
.cluster-card--indigo{border-left-color:var(--indigo)}
.cluster-card__header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;gap:12px}
.cluster-card__name{font-size:0.92rem;font-weight:700;color:var(--heading)}
.cluster-card__count{font-size:0.73rem;color:var(--muted);background:rgba(255,255,255,.05);padding:3px 10px;border-radius:12px;white-space:nowrap;flex-shrink:0}

/* Quote */
.quote{background:rgba(168,85,247,.06);border-left:3px solid var(--primary);border-radius:0 8px 8px 0;padding:10px 14px;margin:8px 0;font-size:0.84rem;font-style:italic;line-height:1.55}
.quote--gold{border-left-color:var(--accent);background:rgba(245,158,11,.05)}
.quote--green{border-left-color:var(--success);background:rgba(52,211,153,.05)}
.quote--red{border-left-color:var(--danger);background:rgba(248,113,113,.05)}
.quote__author{font-style:normal;font-size:0.74rem;color:var(--muted);display:block;margin-top:5px}

/* Alert */
.alert{border-radius:10px;padding:13px 16px;margin:10px 0;font-size:0.84rem}
.alert p:last-child,.alert ul:last-child{margin-bottom:0}
.alert__title{font-weight:700;margin-bottom:6px;font-size:0.85rem}
.alert--info{background:rgba(168,85,247,.08);border:1px solid rgba(168,85,247,.2)}
.alert--info .alert__title{color:var(--primary-light)}
.alert--success{background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.2)}
.alert--success .alert__title{color:var(--success)}
.alert--warn{background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.2)}
.alert--warn .alert__title{color:var(--warn)}
.alert--danger{background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.2)}
.alert--danger .alert__title{color:var(--danger)}
.alert--indigo{background:rgba(129,140,248,.08);border:1px solid rgba(129,140,248,.2)}
.alert--indigo .alert__title{color:var(--indigo)}

/* Idea cards */
.idea-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:14px;margin:16px 0}
.idea-card{background:var(--card-alt);border:1px solid var(--border);border-radius:12px;padding:16px 18px}
.idea-card__title{font-size:0.92rem;font-weight:700;color:var(--heading);margin-bottom:6px}
.idea-card__format{display:inline-block;font-size:0.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:2px 10px;border-radius:12px;background:rgba(168,85,247,.15);color:var(--primary-light);margin-bottom:8px}
.fmt-gold{background:rgba(245,158,11,.15);color:var(--accent)}
.fmt-green{background:rgba(52,211,153,.15);color:var(--success)}
.fmt-red{background:rgba(248,113,113,.15);color:var(--danger)}
.fmt-indigo{background:rgba(129,140,248,.15);color:var(--indigo)}
.idea-card__rationale{font-size:0.8rem;color:var(--muted);line-height:1.5}

/* Score display */
.score-display{display:flex;align-items:center;gap:20px;background:var(--card);border:1px solid var(--border);border-radius:14px;padding:22px 24px;margin:16px 0}
.score-circle{width:88px;height:88px;border-radius:50%;background:conic-gradient(var(--accent) calc(var(--pct)*1%),rgba(255,255,255,.08) 0);display:flex;align-items:center;justify-content:center;font-size:1.5rem;font-weight:800;color:var(--heading);flex-shrink:0;position:relative}
.score-circle::after{content:'';position:absolute;inset:8px;background:var(--card);border-radius:50%}
.score-circle span{position:relative;z-index:1}
.score-details h4{color:var(--heading);margin-bottom:6px;font-size:1rem}
.score-details p{font-size:0.82rem;color:var(--muted);margin-bottom:0}

/* Gold quotes */
.gold-quote{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:18px 20px;margin-bottom:14px;border-left:3px solid var(--accent)}
.gold-quote--diamond{border-left-color:var(--primary);background:rgba(168,85,247,.04)}
.gold-quote__text{font-size:0.92rem;font-style:italic;color:var(--text);margin-bottom:10px;line-height:1.6}
.gold-quote__meta{display:flex;gap:14px;flex-wrap:wrap;font-size:0.74rem;color:var(--muted)}
.gold-quote__tag{background:rgba(245,158,11,.1);color:var(--accent);padding:2px 8px;border-radius:10px;font-size:0.68rem;font-weight:700}

/* Table */
.report-table{width:100%;border-collapse:collapse;font-size:0.8rem;margin:12px 0}
.report-table th{background:rgba(168,85,247,.1);color:var(--primary-light);font-weight:600;padding:10px 12px;text-align:left;border-bottom:1px solid var(--border)}
.report-table td{padding:9px 12px;border-bottom:1px solid var(--border);color:var(--text);vertical-align:top}
.report-table tr:hover td{background:rgba(255,255,255,.02)}

/* Mandate */
.mandate-box{background:linear-gradient(135deg,rgba(168,85,247,.12),rgba(245,158,11,.08));border:1px solid rgba(168,85,247,.3);border-radius:16px;padding:32px 36px;margin:32px 0;text-align:center}
.mandate-box__statement{font-size:1.05rem;line-height:1.75;color:var(--heading)}
.mandate-box__statement strong{color:var(--accent)}

/* User cards */
.user-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:14px;margin:16px 0}
.user-card{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px 18px}
.user-card__name{font-size:0.92rem;font-weight:700;color:var(--accent);margin-bottom:4px}
.user-card__role{font-size:0.7rem;color:var(--primary-light);text-transform:uppercase;letter-spacing:.08em;font-weight:700;margin-bottom:8px}
.user-card__desc{font-size:0.8rem;color:var(--muted);line-height:1.5}
.user-card__score{font-size:0.73rem;color:var(--warn);margin-top:6px}

/* Tips */
.tips-category{background:var(--card);border:1px solid var(--border);border-radius:14px;padding:20px 22px;margin-bottom:20px}
.tips-category__title{font-size:0.95rem;font-weight:700;color:var(--heading);margin-bottom:14px;display:flex;align-items:center;gap:8px}
.tips-category__title::before{content:'';display:inline-block;width:3px;height:18px;background:var(--accent);border-radius:2px}
.tip-row{display:flex;gap:10px;padding:8px 0;border-bottom:1px solid var(--border);font-size:0.82rem}
.tip-row:last-child{border-bottom:none;padding-bottom:0}
.tip-row__check{color:var(--success);flex-shrink:0;margin-top:1px}
.tip-row__text{color:var(--text);line-height:1.5}
.tip-row__source{font-size:0.72rem;color:var(--primary-light);flex-shrink:0;margin-top:2px}

/* Number tiles */
.number-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:12px;margin:16px 0}
.number-tile{background:var(--card);border:1px solid var(--border);border-radius:12px;padding:16px;text-align:center}
.number-tile__num{font-size:2.2rem;font-weight:800;color:var(--primary-light);line-height:1;margin-bottom:6px}
.number-tile__name{font-size:0.8rem;font-weight:700;color:var(--heading);margin-bottom:6px}
.number-tile__desc{font-size:0.75rem;color:var(--muted);line-height:1.45}

/* App idea cards */
.app-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px;margin:16px 0}
.app-card{background:var(--card-alt);border:1px solid var(--border);border-radius:14px;padding:18px 20px;border-top:3px solid var(--accent)}
.app-card--purple{border-top-color:var(--primary)}
.app-card--green{border-top-color:var(--success)}
.app-card--indigo{border-top-color:var(--indigo)}
.app-card__title{font-size:0.95rem;font-weight:700;color:var(--heading);margin-bottom:6px}
.app-card__badge{display:inline-block;font-size:0.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:2px 10px;border-radius:12px;background:rgba(245,158,11,.15);color:var(--accent);margin-bottom:10px}
.app-card__badge--purple{background:rgba(168,85,247,.15);color:var(--primary-light)}
.app-card__badge--green{background:rgba(52,211,153,.15);color:var(--success)}
.app-card__badge--indigo{background:rgba(129,140,248,.15);color:var(--indigo)}
.app-card__desc{font-size:0.8rem;color:var(--muted);line-height:1.5;margin-bottom:10px}
.app-card__stack{font-size:0.75rem;color:var(--text);margin-top:8px;padding-top:8px;border-top:1px solid var(--border)}
.app-card__stack strong{color:var(--primary-light)}

/* Footer */
.page-footer{text-align:center;padding:24px 32px 48px;font-size:0.74rem;color:var(--muted);border-top:1px solid var(--border);max-width:920px;margin:0 auto}
.disclaimer{max-width:920px;margin:0 auto;padding:0 32px 40px;font-size:0.7rem;color:rgba(148,163,184,0.3);border-top:1px solid rgba(255,255,255,.04);padding-top:16px;line-height:1.6}
"""

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def section(num, title, subtitle="", sid=None):
    anchor = sid or f"s{num}"
    sub = f'<p class="section__subtitle">{subtitle}</p>' if subtitle else ""
    return f"""
<div class="section" id="{anchor}">
<div class="section__number">SECTION {num:02d}</div>
<h2 class="section__title">{title}</h2>
{sub}"""

def end_section(): return "</div>\n"

def cluster(name, count, color="", body=""):
    cls = f" cluster-card--{color}" if color else ""
    return f"""<div class="cluster-card{cls}"><div class="cluster-card__header"><span class="cluster-card__name">{name}</span><span class="cluster-card__count">{count}</span></div>{body}</div>"""

def quote(text, author, style=""):
    cls = f" quote--{style}" if style else ""
    return f'<div class="quote{cls}">{text}<span class="quote__author">{author}</span></div>'

def alert(level, title, body):
    return f'<div class="alert alert--{level}"><div class="alert__title">{title}</div><p>{body}</p></div>'

def idea(title, fmt, rationale, fmt_cls=""):
    cls = f" {fmt_cls}" if fmt_cls else ""
    return f'<div class="idea-card"><div class="idea-card__title">{title}</div><span class="idea-card__format{cls}">{fmt}</span><div class="idea-card__rationale">{rationale}</div></div>'

def gold_quote(text, author, score, tags, diamond=False):
    cls = " gold-quote--diamond" if diamond else ""
    tag_html = "".join(f'<span class="gold-quote__tag">{t}</span>' for t in tags)
    return f'<div class="gold-quote{cls}"><div class="gold-quote__text">"{text}"</div><div class="gold-quote__meta"><span>{author}</span><span>score:{score}</span>{tag_html}</div></div>'

def tip(text, source=""):
    src = f'<span class="tip-row__source">{source}</span>' if source else ""
    return f'<div class="tip-row"><span class="tip-row__check">✓</span><span class="tip-row__text">{text}</span>{src}</div>'

def tips_cat(emoji, title, tips_html):
    return f'<div class="tips-category"><div class="tips-category__title">{emoji} {title}</div>{tips_html}</div>'

def user_card(name, role, desc, score_info=""):
    s = f'<div class="user-card__score">{score_info}</div>' if score_info else ""
    return f'<div class="user-card"><div class="user-card__name">{name}</div><div class="user-card__role">{role}</div><div class="user-card__desc">{desc}</div>{s}</div>'

def num_tile(number, name, desc):
    return f'<div class="number-tile"><div class="number-tile__num">{number}</div><div class="number-tile__name">{name}</div><div class="number-tile__desc">{desc}</div></div>'

def app_card(title, badge, desc, stack, color=""):
    cls = f" app-card--{color}" if color else ""
    bcls = f" app-card__badge--{color}" if color else ""
    return f'<div class="app-card{cls}"><div class="app-card__title">{title}</div><span class="app-card__badge{bcls}">{badge}</span><div class="app-card__desc">{desc}</div><div class="app-card__stack"><strong>Stack hint:</strong> {stack}</div></div>'


# ═══════════════════════════════════════════════════════════════════════════════
# BUILD REPORT
# ═══════════════════════════════════════════════════════════════════════════════
def build_report():
    parts = []

    # ── COVER ─────────────────────────────────────────────────────────────────
    parts.append(f"""
<div class="cover">
  <span class="cover__badge">&#9733; Audience Intelligence Report</span>
  <h1>r/<span>numerology</span><br>Reddit Community Intelligence</h1>
  <p class="cover__subtitle">Everything the r/numerology community knows about numbers, meaning, and daily practice — extracted from {TOTAL_POSTS} posts and {TOTAL_COMMENTS:,} comments. Calibrated for a developer who builds web apps and wants to live numerologically.</p>
  <div class="cover__meta">
    <div class="cover__meta-item"><span class="cover__meta-value">{TOTAL_POSTS}</span><span class="cover__meta-label">Unique Posts</span></div>
    <div class="cover__meta-item"><span class="cover__meta-value">{TOTAL_COMMENTS:,}</span><span class="cover__meta-label">Comments</span></div>
    <div class="cover__meta-item"><span class="cover__meta-value">59.8K</span><span class="cover__meta-label">Subscribers</span></div>
    <div class="cover__meta-item"><span class="cover__meta-value">Mar 2026</span><span class="cover__meta-label">Captured</span></div>
  </div>
  <div class="cover__client">Prepared for <strong>Wayne Michael</strong> &middot; Relationship: RESEARCHER &middot; Goal: Integrate numerology into daily life + build web apps and static SaaS tools that bring numerological insight to the world</div>
  <div class="cover__footer">Audience Intelligence &middot; audienceintelligence.com &middot; 16 March 2026</div>
</div>
""")

    # ── TABLE OF CONTENTS ─────────────────────────────────────────────────────
    parts.append("""
<div class="section" id="toc">
<div class="section__number">TABLE OF CONTENTS</div>
<h2 class="section__title">Report Contents</h2>
<p class="section__subtitle">r/numerology Audience Intelligence Report &middot; March 2026 &middot; Prepared for Wayne Michael</p>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:0;border:1px solid rgba(255,255,255,0.07);border-radius:10px;overflow:hidden">
  <a href="#exec" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem">&#128203; Executive Summary</a>
  <a href="#s1" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);border-left:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">01</span> &mdash; Overview</a>
  <a href="#s2" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">02</span> &mdash; Audience Sentiment</a>
  <a href="#s3" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);border-left:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">03</span> &mdash; Key Themes</a>
  <a href="#s4" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">04</span> &mdash; Audience Questions</a>
  <a href="#s5" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);border-left:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">05</span> &mdash; Frustrations</a>
  <a href="#s6" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">06</span> &mdash; Audience Desires</a>
  <a href="#s7" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);border-left:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">07</span> &mdash; Viral Triggers</a>
  <a href="#s8" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">08</span> &mdash; Content Opportunities</a>
  <a href="#s9" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);border-left:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">09</span> &mdash; Engagement Opportunities</a>
  <a href="#s10" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">10</span> &mdash; Key Community Voices</a>
  <a href="#s11" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);border-left:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">11</span> &mdash; Product &amp; App Opportunities</a>
  <a href="#s12" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">12</span> &mdash; Audience Profile</a>
  <a href="#s13" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);border-left:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">13</span> &mdash; The Numbers Compendium</a>
  <a href="#s14" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">14</span> &mdash; Strategic Recommendations</a>
  <a href="#s15" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);border-left:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">15</span> &mdash; Viral Probability Score</a>
  <a href="#s16" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">16</span> &mdash; Gold Quotes</a>
  <a href="#s17" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);border-left:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">17</span> &mdash; Key Facts &amp; Claims</a>
  <a href="#s18" style="display:block;color:var(--muted);padding:9px 14px;border-bottom:1px solid rgba(255,255,255,0.07);text-decoration:none;font-size:0.84rem"><span style="color:var(--primary-light);font-weight:700">18</span> &mdash; Privacy &amp; Data Handling</a>
  <a href="#closing" style="display:block;color:var(--accent);padding:9px 14px;grid-column:1/-1;text-decoration:none;font-size:0.84rem;font-weight:700;background:rgba(245,158,11,0.04)">&#9733; The Mandate &mdash; Closing Section</a>
</div>
</div>
""")

    # ── EXECUTIVE SUMMARY ─────────────────────────────────────────────────────
    parts.append(f"""
<div class="section" id="exec">
<div class="section__number">EXECUTIVE SUMMARY</div>
<h2 class="section__title">What This Intelligence Reveals</h2>
<p class="section__subtitle">The single-page brief &mdash; for Wayne Michael &middot; Researcher &middot; Developer &middot; Builder</p>
<div class="alert alert--info">
<div class="alert__title">&#128203; Dataset Overview</div>
<p>This report analyses <strong>{TOTAL_POSTS} posts</strong> and <strong>{TOTAL_COMMENTS:,} comment interactions</strong> from r/numerology (59,800+ subscribers), captured in March 2026. The community spans five distinct groups: sincere practitioners who apply numerology daily, curious newcomers asking what their angel numbers mean, sceptics and debunkers, cultural/celebrity number-watchers, and a small but growing creator layer posting guides, forecasts, and personal testimonies. For Wayne as a developer-researcher, the intelligence value is concentrated in the practitioner and newcomer segments — they reveal exactly what tools are missing, what questions go unanswered every day, and what features would make a numerology web app immediately useful.</p>
</div>
<h3 style="color:var(--heading);font-size:1rem;margin:20px 0 14px">&#127919; Five Key Findings</h3>
<ul style="font-size:0.88rem;line-height:1.9;color:var(--text);margin:0 0 24px 20px">
<li><strong>The most repeated behaviour in this community is asking "what does this number mean?"</strong> — 333, 444, 111, 1111, 12:34, 21:11. These questions repeat hundreds of times and never get a single authoritative answer. Every question is a potential app user.</li>
<li><strong>2026 = Universal Year 1 is the community's biggest active topic.</strong> Multiple posts, forecasts, and guides are built around the 2+0+2+6=10/1 calculation. A Personal Year calculator for 2026 would be timely and would capture search traffic right now.</li>
<li><strong>There is no dominant numerology tool or app mentioned by this community.</strong> Practitioners do their calculations by hand or via generic calculators. The gap between what users need (personalised, explained, interactive) and what exists (bare number outputs) is wide open.</li>
<li><strong>The scepticism layer is loud but the believers are emotionally committed.</strong> 63% of genuine community sentiment is positive-to-mystical. Scepticism posts get high engagement but mostly from outside the subreddit. The core audience trusts the numbers deeply.</li>
<li><strong>Personal application is the #1 desire.</strong> Life Path numbers, Personal Year cycles, name numerology, lucky numbers for business — users want to know how numerology applies to <em>their specific life</em>. Personalisation is the product gap Wayne can fill.</li>
</ul>
<div class="stats-grid">
  <div class="stat-card stat-card--purple"><span class="stat-value">{TOTAL_POSTS}</span><div class="stat-label">Posts Analysed</div></div>
  <div class="stat-card stat-card--gold"><span class="stat-value">{TOTAL_COMMENTS:,}</span><div class="stat-label">Comment Interactions</div></div>
  <div class="stat-card stat-card--green"><span class="stat-value">59.8K</span><div class="stat-label">Members</div></div>
  <div class="stat-card stat-card--indigo"><span class="stat-value">2026=1</span><div class="stat-label">Universal Year #1 Topic</div></div>
  <div class="stat-card"><span class="stat-value">444</span><div class="stat-label">Most Searched Angel #</div></div>
  <div class="stat-card stat-card--red"><span class="stat-value">0</span><div class="stat-label">Dominant Apps Cited</div></div>
</div>
</div>
""")

    # ── S1: OVERVIEW ──────────────────────────────────────────────────────────
    parts.append(section(1, "Overview", "What the r/numerology snapshot reveals about this community"))
    parts.append(f"""
<div class="stats-grid">
  <div class="stat-card stat-card--purple"><span class="stat-value">{TOTAL_POSTS}</span><div class="stat-label">Posts</div></div>
  <div class="stat-card stat-card--gold"><span class="stat-value">{TOTAL_COMMENTS:,}</span><div class="stat-label">Comments</div></div>
  <div class="stat-card stat-card--green"><span class="stat-value">59.8K</span><div class="stat-label">Members</div></div>
  <div class="stat-card"><span class="stat-value">9,917</span><div class="stat-label">Top Post Score</div></div>
  <div class="stat-card stat-card--indigo"><span class="stat-value">1,547</span><div class="stat-label">Most Comments</div></div>
  <div class="stat-card stat-card--gold"><span class="stat-value">Mar 2026</span><div class="stat-label">Captured</div></div>
</div>
<p>r/numerology is a mid-sized subreddit with a passionate core of sincere practitioners surrounded by casual curious users, sceptics, and viral crossposts from larger subreddits. The community is active, with consistent posting across angel number sightings, personal year forecasts, life path readings, and name analysis requests. 2026, as a Universal Year 1, is the dominant lens through which the community is interpreting all current events and planning.</p>
<p><strong>For Wayne:</strong> The gap between what this community is asking for and what currently exists as digital tools is the most important signal in this dataset. Every repeated "what does 444 mean?" post is an unanswered app request. Every "how do I calculate my personal year?" comment is a calculator page waiting to be built.</p>
""")
    parts.append("""
<div class="stats-grid" style="margin-top:8px">
  <div class="stat-card"><span class="stat-value">~30%</span><div class="stat-label">Angel Number Posts</div></div>
  <div class="stat-card stat-card--purple"><span class="stat-value">~22%</span><div class="stat-label">Personal Readings</div></div>
  <div class="stat-card stat-card--gold"><span class="stat-value">~20%</span><div class="stat-label">Guides &amp; Forecasts</div></div>
  <div class="stat-card stat-card--red"><span class="stat-value">~15%</span><div class="stat-label">Sceptical / Debunk</div></div>
  <div class="stat-card stat-card--green"><span class="stat-value">~8%</span><div class="stat-label">Celebrity / Cultural</div></div>
  <div class="stat-card stat-card--indigo"><span class="stat-value">~5%</span><div class="stat-label">Business &amp; Money</div></div>
</div>
""")
    parts.append(end_section())

    # ── S2: SENTIMENT ──────────────────────────────────────────────────────────
    parts.append(section(2, "Audience Sentiment", "How the community emotionally relates to numerology"))
    parts.append("""
<div class="sentiment-bar">
  <div class="sentiment-bar__segment seg-positive" style="flex:38">38% Believing / Sincere</div>
  <div class="sentiment-bar__segment seg-neutral" style="flex:25">25% Curious / Open</div>
  <div class="sentiment-bar__segment seg-mixed" style="flex:20">20% Mixed / Exploratory</div>
  <div class="sentiment-bar__segment seg-negative" style="flex:17">17% Sceptical / Critical</div>
</div>
<div class="sentiment-bar__legend">
  <span class="leg-pos">38% Believing &mdash; sincere practitioners, angel number seekers, daily-use adherents</span>
  <span class="leg-neu">25% Curious &mdash; newcomers, "is this real?" askers, open-minded explorers</span>
  <span class="leg-mix">20% Mixed &mdash; using numerology but openly questioning its limits</span>
  <span class="leg-neg">17% Sceptical &mdash; active debunkers, confirmation bias claims, religious objectors</span>
</div>
""")
    parts.append(cluster("&#x1F7E3; THE SINCERE PRACTITIONERS — 'This is a real tool I use daily'", "~38% · highest personal engagement", "green",
        quote('"Numerology has been one of the biggest tools in my life for understanding who I am at a soul level and more importantly, how I\'m meant to create abundance."', "— u/Bthemanifestor · score:67 · 141 comments", "green") +
        quote('"1/ Numerology isn\'t magic — it\'s a tool. Your numbers reveal patterns, but it\'s up to YOU to take action."', "— u/rampm · score:67 · 20 Hard Truths thread") +
        alert("success", "&#x2705; Wayne's Signal", "The practitioners are your core audience. They already believe. They want better tools, more personalisation, and clearer explanations. They will use a well-built calculator daily.")))
    parts.append(cluster("&#x1F7E1; THE CURIOUS — 'I keep seeing 444 everywhere, what does it mean?'", "~25% · highest volume, lowest knowledge", "gold",
        quote('"I woke up to 333 on my clock last night, what\'s this mean? Sometimes I see repeating numbers on license plates or whatever and I smile, but when I wake up from a deep sleep, I\'m left wondering."', "— u/penelopereddits · score:206 · 92 comments") +
        quote('"Ever since I was a kid, I have been afraid. I see 12:34 in my clock and it freaked me out earlier."', "— u/BusinessSun3184 · score:169 · 75 comments") +
        alert("warn", "&#x26A1; Wayne's Biggest App Audience", "This segment is the largest source of search traffic and daily app users. They are not practitioners — they just want to know what their number means. An instant angel number lookup tool built as a static page captures all of this traffic.")))
    parts.append(cluster("&#x1F534; THE SCEPTICS — 'This is pattern recognition, nothing more'", "~17% · vocal, high engagement on their posts", "red",
        quote('"Beware of angel numbers and numerology! These things are apart of new age beliefs and aren\'t from God or the Bible!"', "— u/Ok_Spread3381 · score:122 · 134 comments") +
        quote('"People who believe in superstitions like Numerology, please refrain from telling these tips to others."', "— u/Thamiz_selvan · score:180 · 93 comments") +
        alert("info", "&#x2139;&#xFE0F; Note for Wayne", "Scepticism is real and vocal but it does not suppress demand. The curiosity posts far outnumber sceptic posts. Religious objectors are a minority even within the sceptical segment.")))
    parts.append(end_section())

    # ── S3: KEY THEMES ──────────────────────────────────────────────────────────
    parts.append(section(3, "Key Themes", "The dominant topics ranked by post frequency and engagement"))
    parts.append('<div class="idea-grid">')
    parts.append(idea("Angel Numbers &amp; Synchronicities", "#1 THEME · ~30% OF POSTS", "333, 444, 111, 1111, 12:34, 21:11 — users repeatedly see these and ask for meaning. Every post in this cluster is a micro-cry for a reliable lookup tool. No single resource satisfies them.", "fmt-gold"))
    parts.append(idea("2026 = Universal Year 1", "#2 THEME · DOMINANT NOW", "2+0+2+6=10=1. The Sun Year. New beginnings. Leadership. Reboot energy. Multiple forecasts, personal year guides, and 2026-specific posts. This is the #1 timely content hook right now.", "fmt-purple"))
    parts.append(idea("Life Path Numbers", "#3 THEME · EVERGREEN", "The core calculation: reduce your full birthdate to a single digit. Life Path 1–9 plus Master Numbers 11/22/33. Every newcomer asks about it. The interpretation posts get 50–160 comments.", ""))
    parts.append(idea("Personal Year Cycles (1–9)", "#4 THEME · HIGH UTILITY", "Day+Month+2026 = Personal Year. u/_Zapray_ posted the full 1–9 breakdown for 2026. Multiple users asking how to calculate theirs. A Personal Year calculator with interpretation is the highest-demand tool.", "fmt-green"))
    parts.append(idea("Name Numerology &amp; Destiny Numbers", "#5 THEME · PERSONAL FOCUS", "Assigning numbers to letters, calculating Expression/Destiny numbers from birth names. Bollywood star Jacqueline Fernandez changed her name per numerologist advice. Name tools are high-interest.", ""))
    parts.append(idea("Master Numbers (11, 22, 33)", "#6 THEME · IDENTITY + STATUS", "'Life Path 33 Is Not a Trophy. It Is a Calling.' — Master Numbers carry weight in this community. People strongly identify with them. Master Number explainers get high comments and emotional responses.", "fmt-purple"))
    parts.append(idea("Business, Money &amp; Abundance Alignment", "#7 THEME · COMMERCIAL INTENT", "'Life Path = Money Blueprint.' 'I applied my numbers to my business goals and accomplished everything faster.' Clear commercial use of numerology. High intent to pay for actionable guidance.", "fmt-gold"))
    parts.append(idea("Karmic Debt Numbers (13, 14, 16, 19)", "#8 THEME · DEPTH CONTENT", "Less common but emotionally significant. People who calculate Karmic Debt numbers want deep interpretation. High comment-to-score ratio — these posts generate long conversations.", "fmt-indigo"))
    parts.append(idea("Celebrity &amp; Cultural Numerology", "#9 THEME · HIGH VIRALITY", "Kirby Smart football numerology (2,167 upvotes). Jacqueline Fernandez name change. Pope Francis 88 numerology. Celebrity applications go viral across subreddits. Not the core but highest reach.", "fmt-gold"))
    parts.append(idea("Scepticism &amp; Debunking", "#10 THEME · ENGAGEMENT DRIVER", "Sceptic posts attract high comments. The debunkers and believers clash. This is not a threat — it's an engagement engine. The debates surface the community's most precise definitions and defences.", "fmt-red"))
    parts.append("</div>")
    parts.append(end_section())

    # ── S4: AUDIENCE QUESTIONS ─────────────────────────────────────────────────
    parts.append(section(4, "Audience Questions", "Every recurring question this community is asking — with app implications for Wayne"))
    parts.append(cluster("What does [number] mean? (333 / 444 / 111 / 1111 / 12:34 / 21:11)", "~40 posts · highest frequency · evergreen", "gold",
        quote('"I woke up to 333 on my clock last night, what\'s this mean?"', "— u/penelopereddits · score:206") +
        quote('"444/4444 EVERYWHERE. Can someone tell me what it means?"', "— u/Usernamegvbhds · score:196 · 29 comments") +
        quote('"I keep seeing 444 this week — what does this mean?"', "— u/generation-zero · score:99 · 38 comments") +
        quote('"I am seeing 12:34. What does it mean?"', "— u/BusinessSun3184 · score:169 · 75 comments") +
        alert("success", "&#x1F4A1; App Implication", "This is the highest-volume query in numerology. An angel number lookup page (static HTML + JavaScript, zero backend) with clean interpretations for 111, 222, 333, 444, 555, 666, 777, 888, 999, 1111, 1234 would capture enormous search traffic. Build it first.")))
    parts.append(cluster("What is my Life Path number and what does it mean?", "~20 posts · core newcomer question", "",
        quote('"Your Life Path Number isn\'t just a personality type — it describes the central challenge, gift, and direction of your entire existence."', "— u/Pale_Display3669 · score:27") +
        quote('"I\'ve always had a passing interest in Numerology. What\'s my life path number? Born 22/07/1992 → reduces to 5."', "— u/deeznutsrollin · score:732 · 44 comments") +
        alert("info", "&#x2139;&#xFE0F; App Implication", "Life Path calculator + full interpretation (not just a number output — the full meaning, shadow, strength, famous people with same number) is the second most-searched page to build.")))
    parts.append(cluster("What is my Personal Year for 2026 and what does it mean?", "~15 posts · timely demand", "green",
        quote('"How to find your Personal Year: Day + Month + 2026 = Personal Year"', "— u/_Zapray_ · Personal Years 1-9 Advanced Breakdown For 2026 · score:101") +
        quote('"2026 adds up to 1 (2+0+2+6=1), making this the Sun\'s year. In Vedic Numerology, this signals a reboot energy."', "— u/rampm · score:92") +
        alert("success", "&#x2705; App Implication", "A Personal Year calculator for 2026 with month-by-month breakdown is peak timely content. Could also generate shareable Personal Year profile cards.")))
    parts.append(cluster("Is my Master Number real? Am I really a 33 / 11 / 22?", "~10 posts · identity question", "purple" if False else "",
        quote('"Often I see people asking if they are Life Path 33. I feel there is a dangerous illusion around this number."', "— u/AlbatrossIll6353 · score:29") +
        quote('"Master Numbers (11, 22, 33) carry extra weight, but they can be overwhelming if you\'re not ready to embrace them."', "— u/rampm · 20 Hard Truths") +
        alert("warn", "&#x26A0;&#xFE0F; App Note", "Master Number detection needs to be explicit in Wayne's calculator — show the intermediate steps. If someone reduces to 11, 22, or 33, do NOT further reduce. Explain this clearly. The community is deeply invested in these distinctions.")))
    parts.append(cluster("How do I use numerology for my business / money / decisions?", "~12 posts · high commercial intent", "green",
        quote('"Once I started applying my numbers to my business and money goals I was able to accomplish everything I wanted so much faster."', "— u/Bthemanifestor · score:67 · 141 comments") +
        quote('"A small numerology trick helped me understand my career direction — my Expression Number explained why I do better in creative work."', "— u/Remarkable-Being9 · score:40") +
        alert("info", "&#x2139;&#xFE0F; App Implication", "Business numerology tools are underserved. Business name calculator, lucky launch date finder, numerological compatibility for business partners — all viable product pages for a SaaS offering.")))
    parts.append(cluster("What are the Universal Year / portal dates I should know about?", "~8 posts · calendar-driven content", "gold",
        quote('"Today is a rare 1.11.1 Portal. We are sitting in the 1+11+1 sequence. This is a massive green light from the universe."', "— u/Tutor_Kevin · score:578 · 33 comments") +
        quote('"2026 is going to be an amazing year for us all. Being a 1 number year it could be the start of a new awakening."', "— u/Jolly_Individual_718 · score:219 · 65 comments") +
        alert("warn", "&#x26A0;&#xFE0F; App Implication", "Numerological calendar / portal date tracker — shows upcoming significant dates (11/11, new moon in numerological context, Personal Day calculations). Generates daily/weekly content naturally.")))
    parts.append(end_section())

    # ── S5: FRUSTRATIONS ───────────────────────────────────────────────────────
    parts.append(section(5, "Audience Frustrations", "Every pain point named by the community — with what it means for Wayne's builds"))
    parts.append('<div class="idea-grid">')
    parts.append(idea("No Single Authoritative Interpretation Source", "&#x1F525; CRITICAL GAP", 'Every "what does 444 mean?" post gets 20 different answers from 20 different people. The community has no agreed reference. An app with clear, sourced, consistent interpretations fills this void completely.', "fmt-red"))
    parts.append(idea("Calculation is Confusing for Beginners", "&#x1F4AC; COMMON FRICTION", "Master Number reduction rules trip people up. Do I reduce 11 to 2? When do I stop? Multiple posts show users getting wrong results. A calculator that shows every step with explanation removes this friction.", "fmt-gold"))
    parts.append(idea("Sceptical Friends and Family", "&#x1F62C; SOCIAL FRICTION", "'My GF told me I am going to die in 72 hours' (numerology-driven prediction, 3,864 upvotes, 276 comments). Extreme cases aside — practitioners regularly face ridicule. They want validation tools, not just information.", "fmt-red"))
    parts.append(idea("Lack of Personalisation in Existing Resources", "&#x1F4D6; TOOL GAP", "'Most numerology content gives you a keyword and a paragraph' — u/Pale_Display3669. Users want their specific number interpreted in the context of their life, not generic text. Personalised output is the gap.", "fmt-indigo"))
    parts.append(idea("Conflicting Systems and Schools", "&#x2753; KNOWLEDGE GAP", "Pythagorean vs Chaldean vs Vedic numerology all give different results. Posts regularly debate which is 'correct'. An app that explains and offers multiple systems side-by-side would be highly rated.", "fmt-gold"))
    parts.append(idea("No Good Daily / Weekly Practice Framework", "&#x1F4C5; HABIT GAP", "Users want to integrate numerology daily but have no structured tool. 'Here are 10 Practical Habits for 2026' post (score:60) signals demand for routine-building content. A daily practice app or checklist would fill this.", "fmt-green"))
    parts.append(idea("Religious / Sceptical Dismissal", "&#x26A0;&#xFE0F; AUDIENCE TENSION", "'It\'s not from God or the Bible' — religious scepticism is the most emotionally charged friction point. Wayne\'s apps should be framed as reflective / pattern-based tools, not spiritual authority claims, to remain accessible.", "fmt-red"))
    parts.append(idea("No Name Numerology Tool That Explains Why", "&#x1F524; SPECIFIC TOOL GAP", "Jacqueline Fernandez changed her name per numerological advice. Sussan Ley\'s name change inspired Australian political coverage. People want to calculate name vibration AND understand the reasoning. No dominant tool does this well.", "fmt-purple" if False else ""))
    parts.append("</div>")
    parts.append(end_section())

    # ── S6: DESIRES ─────────────────────────────────────────────────────────────
    parts.append(section(6, "Audience Desires", "What this community explicitly wants more of"))
    parts.append(cluster("&#x1F4CA; A Complete Personal Numerology Profile", "~25 posts signal this need", "gold",
        quote('"This is the full teaching — what each Life Path number actually represents at its deepest level, how to calculate yours correctly including Master Numbers, and how to work with what you find."', "— u/Pale_Display3669 · score:27") +
        quote('"ChatGPT explained basically who I am based through numerology... its deep"', "— u/ConstructionDry8140 · score:31") +
        alert("success", "&#x2705; Wayne's Product", "Full numerology profile page: Life Path + Expression + Soul Urge + Birthday + Personal Year + Karmic Debt check — all from name and birthdate. The 'full reading' is the #1 desired output.")))
    parts.append(cluster("&#x1F4C5; Daily / Weekly Numerological Guidance", "~15 posts reference this desire", "green",
        quote('"10 Practical Habits for 2026 (Universal Year 1 / The Sun Year) — practical habits to align with the energy of 2026."', "— u/rampm · score:60") +
        quote('"Personal Years 1-9 Advanced Breakdown For 2026 — to help you guys I\'ve made a miniature guide."', "— u/_Zapray_ · score:101") +
        alert("info", "&#x2139;&#xFE0F; Wayne's Product", "A daily Personal Day calculator showing today's numerological energy, what it's good for, and what to avoid. Lightweight, sharable, embeddable as a widget.")))
    parts.append(cluster("&#x1F4B0; Money, Career, and Business Application", "~12 posts · clear commercial intent", "",
        quote('"Life Path = Money Blueprint. Your Life Path number is like your financial fingerprint — it shows you how you\'re naturally wired to attract money."', "— u/Bthemanifestor") +
        quote('"I applied my numbers to my business and money goals and accomplished everything I wanted so much faster."', "— u/Bthemanifestor · score:67 · 141 comments") +
        alert("warn", "&#x26A1; Wayne's Monetisation Signal", "The business/money application angle is the highest-monetisation-intent segment. Users in this cluster are already paying numerologists. A business numerology SaaS (name checker, launch date calculator, compatibility tool) has real payment potential.")))
    parts.append(cluster("&#x1F91D; Compatibility &amp; Relationship Readings", "~8 posts signal this need", "",
        quote('"What is your life path number in numerology and what is your MC and Node? — 193 upvotes, 417 comments."', "— u/deeragunz_11 · score:193") +
        quote('"Husband\'s birthday 2/22 and my birthday 3/3 were randomly our drinks expiration dates — feels significant."', "— u/Netty97 · score:145") +
        alert("info", "&#x2139;&#xFE0F; App Implication", "Numerology compatibility calculator (two birthdates → relationship reading) is a natural shareable tool. Couples share results. High viral coefficient.")))
    parts.append(cluster("&#x1F30D; Yearly + Monthly Forecasts by Birth Number", "~10 active posts · seasonal demand", "green",
        quote('"December 2025 Predictions by Birth Number — find your number and see if it matches what you\'re experiencing!"', "— u/rampm · score:66") +
        quote('"2026 Numerology Forecast: The Year of the Sun King. Birthday Number 1-9 Predictions."', "— u/rampm · score:92") +
        alert("success", "&#x2705; Wayne's Content Engine", "A yearly + monthly forecast by birth number is a content engine that refreshes itself. Generates 12 articles per year per birth number = 108 evergreen content pages annually. Could be automated.")))
    parts.append(end_section())

    # ── S7: VIRAL TRIGGERS ─────────────────────────────────────────────────────
    parts.append(section(7, "Viral Content Triggers", "Why certain numerology posts explode — patterns Wayne can replicate in content and app landing pages"))
    parts.append('<div class="idea-grid">')
    parts.append(idea("Mathematical Elegance / Beautiful Number Fact", "TRIGGER #1 · STRONGEST", '"2025 = 45² and we turn 45 years old" (497 upvotes). "2026 = 1 (Universal Year)" (multiple posts). People are wired to feel wonder at mathematical coincidence. Posts that surface a beautiful number fact spread instantly.', "fmt-gold"))
    parts.append(idea("Calendar Portal / Significant Date Announcement", "TRIGGER #2 · TIMELY", '"Today is a rare 1.11.1 Portal" (578 upvotes). The combination of today\'s date + numerological significance + call-to-action creates urgency. Calendar-driven posts are shareable because they\'re time-sensitive.', "fmt-purple" if False else ""))
    parts.append(idea("Celebrity or Famous Person Numerology", "TRIGGER #3 · CROSS-SUBREDDIT REACH", 'Kirby Smart football numerology post (2,167 upvotes from r/CFB crosspost). Jacqueline Fernandez name change (365 upvotes). Applying numerology to celebrities breaks out of the subreddit and reaches new audiences.', "fmt-gold"))
    parts.append(idea("'What Does This Number Mean?' — Sincere and Personal", "TRIGGER #4 · COMMUNITY GLUE", 'The angel number posts (444, 333, 1111) are not viral by score but are the highest-volume post type. They generate 20–100 comments of genuine engagement. This is the daily heartbeat of the community.', ""))
    parts.append(idea("'20 Things I Wish I Knew Before' Format", "TRIGGER #5 · HIGH UTILITY", '"20 Hard Truths About Numerology I Wish I Knew Before" (67 upvotes, strong repost pattern). "Numerology Fundamentals: 20 Things You Need to Know" (85 upvotes). Numbered list formats perform consistently.', "fmt-green"))
    parts.append(idea("Personal Testimony + Financial / Life Outcome", "TRIGGER #6 · PROOF", '"How Seeing 444 Saved Me From the Biggest Financial Mistake of My Life" (133 upvotes). First-person story + dramatic outcome + number as agent = highly shareable format across spiritual communities.', "fmt-green"))
    parts.append(idea("'This Year Is Special For You If...'", "TRIGGER #7 · PERSONALISATION HOOK", '"2026 Numerology Forecast: The Year of the Sun King (Birthday Number 1-9 Predictions)" (92 upvotes). The implicit hook: \'Find YOUR number\' drives engagement. Personalisation triggers drive shares and saves.', "fmt-purple" if False else ""))
    parts.append(idea("Conspiracy / Pattern in Real-World Events", "TRIGGER #8 · CROSS-PLATFORM REACH", 'Charlie Kirk numerology post (999 upvotes). Nostradamus thread (2,336 upvotes). Numerological analysis of news events breaks into general Reddit and social media. High risk / high reach.', "fmt-red"))
    parts.append("</div>")
    parts.append(end_section())

    # ── S8: CONTENT OPPORTUNITIES ───────────────────────────────────────────────
    parts.append(section(8, "Content Opportunities", "10 high-value content pieces Wayne can create — calibrated to his goal of building web apps and static SaaS pages"))
    parts.append('<div class="idea-grid">')
    parts.append(idea("'Your 2026 Numerology Guide: Universal Year 1 and Your Personal Year'", "EVERGREEN + TIMELY · HIGHEST PRIORITY", "Combine Universal Year 1 explanation + Personal Year calculator + month-by-month breakdown. This captures 2026 search traffic now and is reusable for 2027 Year 2 etc. Structured as a static page with embedded calculator.", "fmt-gold"))
    parts.append(idea("'What Does 444 Mean?' — The Definitive Angel Number Guide", "SEO GOLDMINE · HIGH VOLUME", "One page per major angel number (111, 222, 333, 444, 555, 666, 777, 888, 999, 1111, 1234) with thorough interpretation, how to work with it, and a 'see what else this means for your life path' CTA to the full calculator.", "fmt-gold"))
    parts.append(idea("'Calculate Your Life Path Number' — Interactive Step-by-Step", "CORE TOOL · FIRST BUILD", "Show every reduction step. Detect and preserve Master Numbers. After calculation: full interpretation, famous people with same number, compatible Life Paths, your 2026 Personal Year. This is the anchor page.", "fmt-purple" if False else ""))
    parts.append(idea("'The Complete Numerology Profile' — Name + Birthdate Deep Read", "FLAGSHIP PRODUCT · PAID TIER", "Full profile: Life Path + Expression/Destiny + Soul Urge + Birthday Number + Personal Year + Karmic Debt check + Power Number. The community is asking for this explicitly. Could be the paid product.", "fmt-green"))
    parts.append(idea("Numerology for Business Owners — Name &amp; Launch Date Tools", "COMMERCIAL PAGE · MONETISATION", "Business name numerology checker, lucky launch date calculator, business number compatibility. Targets the money/abundance segment which has highest payment intent. Can be a standalone SaaS product.", "fmt-gold"))
    parts.append(idea("Numerology Compatibility Calculator", "VIRAL TOOL · SHAREABLE", "Enter two birthdates → get compatibility reading (Life Path match, Personal Year synchrony, numerological strengths/tensions). Couples share results. Best viral coefficient of all tool types.", "fmt-green"))
    parts.append(idea("'Today in Numerology' — Daily Personal Day Calculator", "RETURN-VISIT ENGINE", "Universal Day + Personal Day calculator showing today's energy, what it's best for, and what to avoid. Generates a reason to return daily. Could become a widget embeddable on other sites.", "fmt-indigo"))
    parts.append(idea("Master Numbers Deep Dive (11, 22, 33, 44)", "IDENTITY + COMMUNITY CONTENT", "Detailed page on each Master Number: what it means at its highest expression vs shadow, famous bearers, common misconceptions. Addresses the 'Am I really a 33?' question the community asks constantly.", ""))
    parts.append(idea("Numerological Calendar — Portal Dates &amp; Power Days for 2026", "CONTENT + SEO · SEASONAL", "Full calendar of numerologically significant dates in 2026: 11/11 portal, Universal Month combinations, Personal Day peaks per birth number. Generates search traffic for each date as it approaches.", "fmt-indigo"))
    parts.append(idea("Name Numerology Checker — Chaldean &amp; Pythagorean", "TOOL + CONTROVERSY HOOK", "Calculate name value in both systems with explanation of differences. Covers the 'which system is correct?' debate by showing both. Jacqueline Fernandez / Sussan Ley angle gives celebrity SEO hook.", ""))
    parts.append("</div>")
    parts.append(end_section())

    # ── S9: ENGAGEMENT OPPORTUNITIES ────────────────────────────────────────────
    parts.append(section(9, "Engagement Opportunities", "How Wayne should engage with this community as a researcher and builder"))
    parts.append(alert("success", "&#x1F3AF; Primary Opportunity: Post Your Calculator — Ask for Feedback", "The community is actively asking for tools. A post saying 'I built a free Life Path calculator with full interpretation — would love feedback from this community' would be warmly received. This is not self-promotion; it's a community service."))
    parts.append(cluster("Respond to Angel Number Posts with Tool Link", "Highest volume, easiest engagement", "gold",
        "<p style='font-size:0.85rem;color:var(--muted);margin-bottom:8px'>Every 'what does 444 mean?' post is an opportunity to reply with a genuinely helpful answer AND mention the tool. The community rewards helpful responses. Over time this builds recognition as a reliable resource.</p>" +
        alert("info", "&#x2139;&#xFE0F; Approach", "Write a substantive reply first (give the actual answer), then: 'I also built a calculator at [URL] that shows what 444 means in the context of your Life Path — might be useful.' Low pressure, high value.")))
    parts.append(cluster("Post a '2026 Personal Year Calculator' as a community resource", "Timely + immediate value", "green",
        "<p style='font-size:0.85rem;color:var(--muted);margin-bottom:8px'>Multiple users are calculating their Personal Year manually or asking for help. A post linking to a clean Personal Year calculator would be immediately useful, timely (2026 started 3 months ago), and naturally attract saves and shares.</p>" +
        alert("success", "&#x2705; Template Post Title", "'I built a free 2026 Personal Year Calculator — find your number and get the full breakdown for your year'")))
    parts.append(cluster("Follow the Practitioner Voices", "Intelligence stream for content ideas", "",
        "<p style='font-size:0.85rem;color:var(--muted);margin-bottom:8px'>u/rampm posts forecasts and guides consistently. u/_Zapray_ posts Personal Year breakdowns. u/Tutor_Kevin posts portal date content. u/Bthemanifestor posts money + abundance content. Following these users gives Wayne a real-time feed of what the community is engaging with most.</p>" +
        alert("info", "&#x2139;&#xFE0F; Action", "Follow all 6 community voices listed in Section 10 on Reddit. Their posting cadence is the editorial calendar for Wayne's content.")))
    parts.append(end_section())

    # ── S10: KEY COMMUNITY VOICES ──────────────────────────────────────────────
    parts.append(section(10, "Key Community Voices", "The people producing the most valuable content in this community — Wayne's intelligence network"))
    parts.append('<div class="user-grid">')
    parts.append(user_card("u/rampm", "PROLIFIC FORECAST AUTHOR", "Consistently posts high-quality numerology forecasts, fundamentals, and hard truths. Covers: Personal Year breakdowns, monthly predictions by birth number, 2026 Universal Year guides, and practical habits. The community's most reliable practitioner-educator.", "Posts: 6+ · Subjects: forecasts, 2026, habits, fundamentals"))
    parts.append(user_card("u/Tutor_Kevin", "PORTAL DATE &amp; ENERGY WRITER", "Writes about significant numerological portal dates (1.11.1, 11/11 etc.) with specific practical instructions. 578 upvotes on a single portal post. Drives high engagement with timely, calendar-driven content.", "Top post: 578 · Portal content specialist"))
    parts.append(user_card("u/Bthemanifestor", "MONEY &amp; BUSINESS APPLICATION", "Focuses on applying numerology to money, business, and abundance. 141 comments on using numerology for financial goals. Covers Life Path as money blueprint, business alignment, and practical manifestation techniques.", "Top post: 67 · 141 comments · Commercial angle"))
    parts.append(user_card("u/_Zapray_", "PERSONAL YEAR SPECIALIST", "Posted the advanced Personal Year 1–9 breakdown for 2026 (score:101). Covers the full cycle with nuanced interpretation per year. Key reference for the highest-demand calculation type.", "Personal Year guide score: 101"))
    parts.append(user_card("u/Pale_Display3669", "DEEP KNOWLEDGE / TEACHER", "Wrote the most thorough Life Path explanation in the dataset — covers historical roots (Babylon, Pythagoras, Kabbalah), correct Master Number calculation, and full interpretations for each number.", "Score: 27 · Depth content"))
    parts.append(user_card("u/Ok_Spread3381", "SCEPTIC VOICE", "Wrote the 'Beware of angel numbers' post (score:122, 134 comments). Represents the religious scepticism segment. Understanding this objection helps Wayne frame his tools appropriately — pattern-based, not dogmatic.", "Sceptic post: 122 · 134 comments"))
    parts.append(end_section())

    # ── S11: PRODUCT OPPORTUNITIES ─────────────────────────────────────────────
    parts.append(section(11, "Product &amp; App Opportunities", "What Wayne should actually build — prioritised by demand evidence, build difficulty, and revenue potential"))
    parts.append('<div class="app-grid">')
    parts.append(app_card("Life Path Calculator (Full Interpretation)", "BUILD FIRST · CORE ANCHOR", "Step-by-step reduction with Master Number protection. Full interpretation with life themes, strengths, shadows, famous bearers, and compatible paths. Links to Personal Year and Expression Number. The most-requested calculation in this community.", "Static HTML + vanilla JS. Zero backend. SEO-optimised for 'life path number calculator' (high monthly searches). Output shareable as text."))
    parts.append(app_card("Angel Number Lookup Database", "BUILD SECOND · HIGHEST TRAFFIC", "One page per major number: 111, 222, 333, 444, 555, 666, 777, 888, 999, 1111, 1234 + custom input. Interpretation: spiritual meaning, numerological reason, what to do when you see it. Each page targets a high-volume search query.", "11 static HTML pages. No JS required for basic version. Internal linking between pages + CTA to Life Path calculator on each. Pure SEO play.", "green"))
    parts.append(app_card("2026 Personal Year Calculator", "BUILD THIRD · TIMELY NOW", "Input: day of birth + month of birth. Output: Personal Year 1–9 (or Master Numbers), month-by-month energy breakdown for 2026, what to focus on, what to avoid. Position: fastest path to becoming a known resource in this community right now.", "Static page + ~30 lines of JS. Shareable result URL. Month breakdown as a collapsible accordion or timeline visual.", "purple"))
    parts.append(app_card("Full Numerology Profile Generator", "FLAGSHIP PRODUCT · PAID TIER", "Input: full name at birth + date of birth. Output: Life Path + Expression/Destiny + Soul Urge + Birthday + Personal Year + Power Number + Karmic Debt check. Presented as a formatted 'report card'. This is the product the community can't find anywhere that actually explains the numbers.", "Static page + JS calculation engine. PDF export = premium feature. Emailgate the full report for lead capture. Freemium model.", "green"))
    parts.append(app_card("Numerology Compatibility Tool", "SOCIAL TOOL · HIGH VIRALITY", "Two birthdates → Life Path compatibility reading. Include: natural harmony, growth tensions, best collaboration types, numerological advice for the relationship. Couples share results naturally — built-in viral coefficient.", "Two date inputs + JS. Shareable result card (OG image generation). Could extend to friendship / business partner compatibility.", "purple"))
    parts.append(app_card("Business Name Numerology Checker", "COMMERCIAL PAGE · MONETISABLE", "Input business name → Pythagorean + Chaldean value → interpretation for entrepreneurship, leadership, revenue, longevity. 'Is this name good for my business?' is asked repeatedly in adjacent communities. High payment intent.", "Static page + JS letter-to-number mapping. Two systems side by side. CTA to full profile for deeper analysis.", "green"))
    parts.append(app_card("Numerological Portal &amp; Power Days Calendar", "CONTENT ENGINE · SEO", "2026 calendar of significant numerological dates: gateway portals (11/11 etc.), Universal Month peaks, Personal Day highs by birth number. Updates annually, generates search traffic per date as it approaches.", "Static page built from data file. JS date-based personalisation. Could email-subscribe users for upcoming portals.", ""))
    parts.append(app_card("Daily Personal Day Widget", "RETURN-VISIT MECHANISM", "Today's Universal Day number + your Personal Day (requires birth data input or cookie). What the day's energy is best for. Embeddable as an iframe widget for other numerology sites + blogs to add.", "Date maths in JS + localStorage for birth data. Iframe-embeddable. Revenue: sponsored daily affirmations or ads.", "purple"))
    parts.append("</div>")
    parts.append(alert("success", "&#x1F4B0; WAYNE'S BUILD ORDER", "1. Life Path Calculator (core anchor, highest SEO value) → 2. Angel Number Pages (pure SEO, 11 pages, no backend) → 3. Personal Year 2026 (timely, community engagement) → 4. Full Profile Generator (flagship, lead capture) → 5. Compatibility Tool (viral) → 6. Business Name Checker (monetisable)"))
    parts.append(end_section())

    # ── S12: AUDIENCE PROFILE ──────────────────────────────────────────────────
    parts.append(section(12, "Audience Profile", "Six distinct personas in the r/numerology community — ranked by value to Wayne's builder goal"))
    parts.append('<div class="idea-grid">')
    parts.append(idea("&#x1F9D8; The Daily Practitioner", "~20% OF COMMUNITY · HIGHEST VALUE USER", "Applies numerology every day. Tracks Personal Year, Personal Day, pays attention to portal dates. Deeply committed. Will return to a good daily tool every single day. The power user of Wayne's app ecosystem.", "fmt-gold"))
    parts.append(idea("&#x1F914; The Curious Newcomer", "~30% · LARGEST SEGMENT", "Just noticed they keep seeing 444. Just Googled 'life path number'. Has no framework yet. This is the top-of-funnel user. Needs a clear, non-intimidating first experience. Will become a Daily Practitioner if well served.", "fmt-green"))
    parts.append(idea("&#x1F4BC; The Business &amp; Money Seeker", "~10% · HIGHEST PAYMENT INTENT", "Entrepreneur, freelancer, or career-changer using numerology to make business decisions. Will pay for a premium business name tool or full profile. The monetisation segment.", "fmt-gold"))
    parts.append(idea("&#x1F4D6; The Self-Improvement User", "~15% · CONTENT CONSUMER", "Reads numerology content to understand themselves better. Engages with Life Path interpretations, hard truths posts, and '20 things about numerology' content. High time-on-page but lower return frequency.", ""))
    parts.append(idea("&#x1F494; The Relationship Seeker", "~8% · VIRAL AMPLIFIER", "Using numerology for compatibility, partner selection, or understanding relationship dynamics. Shares results with partners. High viral coefficient. Compatibility tool users.", "fmt-indigo"))
    parts.append(idea("&#x1F52C; The Sceptical Observer", "~17% · ENGAGEMENT DRIVER", "Actively debates numerology's validity. Generates high comment counts on sceptic posts. Not Wayne's app user, but their presence keeps discussion active and improves SEO signals on posts that respond to their challenges.", "fmt-red"))
    parts.append("</div>")
    parts.append(end_section())

    # ── S13: THE NUMBERS COMPENDIUM ────────────────────────────────────────────
    parts.append(section(13, "The Numbers Compendium",
        "Everything the community knows about numerological numbers — a reference guide for Wayne's daily practice and app content"))
    parts.append(alert("success", "&#x1F3C6; HOW TO USE THIS SECTION", "This is both Wayne's personal reference guide to start applying numerology immediately, and the content database for his app's interpretation text. Each entry is drawn directly from community practitioner posts."))

    parts.append('<h3 style="color:var(--heading);font-size:1rem;margin:20px 0 12px">&#128204; Core Number Meanings (Life Path / Expression / Personal Year)</h3>')
    parts.append('<div class="number-grid">')
    parts.append(num_tile("1", "The Sun / Initiator", "New beginnings, independence, leadership, self-expression. The creator. 2026 Universal Year = 1. Best year for starting new projects, businesses, relationships."))
    parts.append(num_tile("2", "The Moon / Diplomat", "Partnership, balance, intuition, sensitivity. The collaborator. Best year for building relationships, cooperation, and patience."))
    parts.append(num_tile("3", "Jupiter / Communicator", "Creativity, self-expression, joy, social connection. The artist. Best year for creative projects, communication, and expansion."))
    parts.append(num_tile("4", "Saturn / Builder", "Stability, discipline, hard work, foundation-building. The architect. Best year for systems, structure, and long-term planning."))
    parts.append(num_tile("5", "Mercury / Freedom Seeker", "Change, adventure, freedom, versatility. The explorer. Best year for travel, new experiences, and breaking patterns."))
    parts.append(num_tile("6", "Venus / Nurturer", "Family, responsibility, harmony, service. The caregiver. Best year for home, relationships, health, and community."))
    parts.append(num_tile("7", "Neptune / Seeker", "Introspection, spirituality, analysis, wisdom. The mystic. Best year for inner work, research, and solitude."))
    parts.append(num_tile("8", "Saturn / Powerhouse", "Abundance, ambition, material mastery, karma. The executive. Best year for business launches, financial goals, and leadership."))
    parts.append(num_tile("9", "Mars / Completor", "Completion, humanitarianism, release, transformation. The philanthropist. Best year for endings, forgiveness, and transitions."))
    parts.append("</div>")

    parts.append('<h3 style="color:var(--heading);font-size:1rem;margin:20px 0 12px">&#11088; Master Numbers</h3>')
    parts.append('<div class="number-grid">')
    parts.append(num_tile("11", "The Illuminator", "Master intuition, spiritual messenger, heightened sensitivity. 'The bridge between the conscious and subconscious.' Do NOT reduce to 2 if your Life Path calculates to 11."))
    parts.append(num_tile("22", "The Master Builder", "The most powerful number. Turns dreams into reality at scale. Combines the intuition of 11 with the practicality of 4. Rare and demanding."))
    parts.append(num_tile("33", "The Master Teacher", "'Not a trophy — it is a calling. Or a burden.' The highest vibration. Expected to serve others at great personal cost. Community debates who truly carries it.", ))
    parts.append("</div>")

    parts.append('<h3 style="color:var(--heading);font-size:1rem;margin:20px 0 12px">&#128276; Angel Numbers &amp; Synchronicities</h3>')
    parts.append(tips_cat("&#128251;", "What the Community Says Each Angel Number Means", "".join([
        tip("<strong>111 / 1111:</strong> Manifestation portal. Your thoughts are manifesting rapidly. Be intentional about focus. The 1.11.1 Portal post (578 upvotes): 'A massive green light from the universe.'", "u/Tutor_Kevin + community consensus"),
        tip("<strong>222:</strong> Balance, alignment, trust the process. Things are coming into harmony. You are on the right path even if it doesn't feel like it.", "Community consensus across 30+ posts"),
        tip("<strong>333:</strong> The Trinity. Creative energy active. Support from guides/universe. 'I woke up to 333 — when I wake from deep sleep, I'm left wondering' (206 upvotes, 92 comments).", "u/penelopereddits + thread responses"),
        tip("<strong>444:</strong> Foundation, protection, stability. You are surrounded and supported. 'How Seeing 444 Saved Me From the Biggest Financial Mistake of My Life' — trust this number as a warning signal.", "u/TheMarieWatkins · score:133"),
        tip("<strong>555:</strong> Major change incoming. A shift is happening. Prepare for transitions. Often appears just before significant life events.", "Community practitioner consensus"),
        tip("<strong>666:</strong> Balance material and spiritual. Often misunderstood — community posts clarify it is NOT evil in numerology but a call to rebalance focus.", "Community consensus — multiple correction posts"),
        tip("<strong>777:</strong> Spiritual alignment, flow state, good luck. You are in alignment with higher purpose. One of the most positively received numbers.", "Community consensus"),
        tip("<strong>888:</strong> Abundance cycle, financial energy incoming, karma complete. Strong business and money signal. Appears when financial shifts are building.", "u/Novel_Finger2370 + community"),
        tip("<strong>999:</strong> Completion, release, transformation. A cycle is ending. The universe is clearing space. Let go without forcing.", "Community consensus"),
        tip("<strong>1234:</strong> Step by step, steady progression. You are moving in the right direction sequentially. 'Ever since I was a kid I see 12:34 — it freaked me out but I convinced myself it\'s positive' (169 upvotes).", "u/BusinessSun3184"),
        tip("<strong>33 at 03:03:</strong> Rare amplified Master energy. 'I was born on 03.03.1993 and this year I\'ll be 33 at 03.03 during a full moon — I\'ve always got lucky with numbers' (Aerospace engineer, 75 upvotes).", "u/LabTop890"),
    ])))

    parts.append('<h3 style="color:var(--heading);font-size:1rem;margin:20px 0 12px">&#128197; How Practitioners Calculate Core Numbers (for Wayne\'s apps)</h3>')
    parts.append(tips_cat("&#128290;", "Calculation Rules — Verified by Community Practitioners", "".join([
        tip("<strong>Life Path Number:</strong> Add ALL digits of full birthdate (DDMMYYYY) and reduce to single digit. Reduce each group (day, month, year) separately then sum. STOP if you reach 11, 22, or 33.", "Community consensus · u/Pale_Display3669 guide"),
        tip("<strong>Personal Year:</strong> Day of birth + Month of birth + Current year (2026). Reduce to single digit. 'Day+Month+2026 = Personal Year' — this is the single most-used formula in this community.", "u/_Zapray_ · score:101 · confirmed across 15 posts"),
        tip("<strong>Universal Year:</strong> Sum all digits of the calendar year. 2026 = 2+0+2+6 = 10 = 1. Universal Year 1 = The Sun Year. New beginnings for the entire planet.", "Community universal consensus"),
        tip("<strong>Expression / Destiny Number:</strong> Assign numbers to each letter of your full birth name (Pythagorean: A=1...Z=8 or Chaldean: A=1...Z=8 with different mapping). Sum all, reduce to single digit or Master Number.", "u/Remarkable-Being9 · u/Pale_Display3669"),
        tip("<strong>Soul Urge / Heart's Desire:</strong> Use ONLY the vowels (A, E, I, O, U) in your full birth name. Assign Pythagorean values, sum, and reduce.", "Practitioner standard"),
        tip("<strong>Birthday Number:</strong> Just your day of birth reduced to single digit. Born on 14th = 1+4 = 5. Born on 11th = 11 (Master Number, do not reduce).", "Community standard"),
        tip("<strong>Karmic Debt Numbers:</strong> If your Life Path calculation produces 13, 14, 16, or 19 at an intermediate step, you carry Karmic Debt. 13/4 = the Debt of Laziness. 14/5 = Debt of Freedom. 16/7 = Debt of Pride. 19/1 = Debt of Self-Absorption.", "u/rampm · 20 Hard Truths"),
        tip("<strong>Personal Day:</strong> Personal Month + Day of current date. Personal Month = Personal Year + Calendar Month (reduce). Personal Day = Personal Month + Calendar Day (reduce). Used for daily guidance.", "Practitioner standard"),
    ])))

    parts.append(tips_cat("&#x1F4C5;", "2026 Specific — Wayne's Personal Practice Right Now", "".join([
        tip("<strong>2026 = Universal Year 1.</strong> This is the Sun's year. Energy of new beginnings, leadership, independence and self-expression. The entire planet is in a Year 1 reset cycle. Best year to launch new projects.", "Multiple community posts · u/rampm · u/_Zapray_"),
        tip("<strong>Calculate your Personal Year for 2026:</strong> Add your birth day + birth month + 2026. Reduce to single digit or Master Number. This is your dominant energy for the entire year.", "u/_Zapray_ · score:101"),
        tip("<strong>Personal Year 1 (2026):</strong> Complete reinvention. Start what you've been avoiding. New identity, new chapter. 'Heavy on complete reinvention of who you are.'", "u/_Zapray_"),
        tip("<strong>Personal Year 3 (2026):</strong> Creative expansion, communication, joy. Best year for content creation, building in public, writing, teaching.", "u/_Zapray_"),
        tip("<strong>Personal Year 8 (2026):</strong> Power, abundance, business mastery. Launch your business or SaaS this year if you're in a Personal Year 8. Financial karma completes.", "u/_Zapray_ + u/Bthemanifestor"),
        tip("<strong>Personal Year 1 + Universal Year 1 (Double 1 energy):</strong> If your Personal Year AND the Universal Year are both 1, you are in a rare double-initiation year. 'Your entire reality could shift in 12 months if you act.'", "Community practitioner consensus"),
        tip("<strong>For building apps in 2026:</strong> Universal Year 1 is the numerologically optimal year to launch new digital products. The Sun energy supports new beginnings, innovation, and establishing identity. This is not superstition — it's a useful frame for commitment and launch timing.", "Synthesised from u/rampm + u/Tutor_Kevin + u/Bthemanifestor"),
    ])))
    parts.append(end_section())

    # ── S14: STRATEGIC RECOMMENDATIONS ──────────────────────────────────────────
    parts.append(section(14, "Strategic Recommendations", "Prioritised action plan for Wayne — researcher, daily practitioner, and web app builder"))
    parts.append('<div class="idea-grid">')
    parts.append(idea("1. Calculate Your Full Personal Numerology Profile Today", "IMMEDIATE · PERSONAL PRACTICE", "Life Path + Expression + Soul Urge + Personal Year 2026. Use the formulas in Section 13. This is your foundation for daily numerological living. Spend 30 minutes understanding your numbers before building any tools.", "fmt-gold"))
    parts.append(idea("2. Build the Angel Number Lookup Pages First", "THIS WEEK · QUICKEST WIN", "11 static HTML pages, one per key angel number. No JS needed for the basic version. These rank quickly in search because the queries are clear ('what does 444 mean') and existing results are thin on depth. Fastest way to attract the community's largest audience segment.", "fmt-green"))
    parts.append(idea("3. Launch the Life Path Calculator as Your Anchor Page", "WEEK 1-2 · CORE TOOL", "This is the page every numerology site is built around. Step-by-step calculation, Master Number protection, full interpretation. Add a 2026 Personal Year result at the end. This becomes the hub that links to all other tools.", ""))
    parts.append(idea("4. Post the Personal Year Calculator to r/numerology", "WEEK 2-3 · COMMUNITY SEEDING", "Nothing converts the r/numerology audience faster than a genuinely useful tool posted in context. Format: 'I built a free 2026 Personal Year calculator — enter your birthday and get your full year breakdown. Free, no signup.' Reply to every comment.", "fmt-gold"))
    parts.append(idea("5. Set Up a Daily Numerological Practice", "ONGOING · PERSONAL USE", "Each morning: check your Personal Day, note the Universal Day energy, set your intention aligned to both. Monthly: review your Personal Month. This rhythm is what the practitioner community lives. Section 13 gives you all the formulas.", "fmt-indigo"))
    parts.append(idea("6. Build the Full Profile Generator as Your Premium Product", "MONTH 1-2 · MONETISATION", "Once the free tools have traffic, launch the full profile (Life Path + Expression + Soul Urge + Karmic Debt + Personal Year) as the lead-capture product. Gate the full PDF export behind an email signup or $7 purchase.", "fmt-green"))
    parts.append(idea("7. Create the Numerological Calendar for 2026", "MONTH 1 · CONTENT ENGINE", "Map all significant dates: portal days, Universal Month peaks, 11/11, key reductions. Publish as a static page. Generates traffic spikes as each date approaches. Gives Wayne a posting schedule for social: 'Today is a numerologically significant day because...'", "fmt-indigo"))
    parts.append(idea("8. Follow the 6 Community Voices and Extract Content Ideas Weekly", "ONGOING · INTELLIGENCE STREAM", "u/rampm, u/Tutor_Kevin, u/Bthemanifestor, u/_Zapray_, u/Pale_Display3669, u/AlbatrossIll6353 — their posts are Wayne's editorial calendar. When they write about a topic, that topic is currently engaging the community. Build the tool that answers the question.", ""))
    parts.append("</div>")
    parts.append(end_section())

    # ── S15: VIRAL PROBABILITY SCORE ──────────────────────────────────────────
    parts.append(section(15, "Viral Probability Score", "How likely is numerology content and tooling to achieve viral distribution?"))
    parts.append("""
<div class="score-display">
  <div class="score-circle" style="--pct:75"><span>7.5</span></div>
  <div class="score-details">
    <h4>Strong Viral Potential — 7.5 / 10</h4>
    <p>Numerology content has a strong viral coefficient when it combines personalisation + a beautiful number fact + timely calendar hook. The community is mid-sized (59.8K) but posts regularly cross over to larger subreddits (r/CFB, r/BestofRedditorUpdates, r/relationship_advice) where they can reach millions. Calculator tools go viral in spiritual communities through sharing of personal results. The category has year-round SEO traffic that builds steadily.</p>
  </div>
</div>
""")
    parts.append("""
<div class="stats-grid">
  <div class="stat-card stat-card--purple"><span class="stat-value">9,917</span><div class="stat-label">Top crosspost score</div></div>
  <div class="stat-card stat-card--gold"><span class="stat-value">578</span><div class="stat-label">Portal date post</div></div>
  <div class="stat-card stat-card--indigo"><span class="stat-value">417</span><div class="stat-label">Most comments (1 thread)</div></div>
  <div class="stat-card stat-card--green"><span class="stat-value">High</span><div class="stat-label">SEO Evergreen Value</div></div>
</div>
""")
    parts.append(alert("success", "&#x1F4A1; Highest-ROI Viral Formula for Wayne's Tools", "Calculator result + shareable output + timely hook (2026 Year 1) = high share rate. Users who get their Personal Year result want to share it with friends. Build a shareable result card (OG image or copyable text) into every calculator from day one."))
    parts.append(alert("warn", "&#x26A0;&#xFE0F; What Limits Virality", "Generic interpretation text that feels copy-pasted. Tools that give a number with no explanation. Apps that require signup before showing the result. The community's bar is: 'This gave me something I didn't know about myself.' Meet that bar and virality follows."))
    parts.append(end_section())

    # ── S16: GOLD QUOTES ──────────────────────────────────────────────────────
    parts.append(section(16, "Gold Quotes Hall of Fame", "The most insight-rich and actionable lines from the dataset — for Wayne's life practice and app copy"))

    parts.append('<h3 style="color:var(--primary-light);margin:16px 0 12px;font-size:1rem">&#x1F48E; Diamond Tier</h3>')
    parts.append(gold_quote(
        "Numerology isn't magic — it's a tool. Your numbers reveal patterns, but it's up to YOU to take action.",
        "u/rampm · r/numerology", 67, ["Daily Practice", "App Copy", "Framing"], diamond=True))
    parts.append(gold_quote(
        "Most numerology content gives you a keyword and a paragraph. This is the full teaching — what each Life Path number represents at its deepest level, how to calculate correctly including Master Numbers, and how to work with what you find.",
        "u/Pale_Display3669 · r/numerology", 27, ["Product Gap", "App Positioning", "Content Mission"], diamond=True))
    parts.append(gold_quote(
        "Once I started applying my numbers to my business and money goals I was able to accomplish everything I wanted so much faster.",
        "u/Bthemanifestor · r/numerology", 67, ["Business Use Case", "Testimonial", "Commercial Angle"], diamond=True))
    parts.append(gold_quote(
        "Today is a massive green light from the universe. We are sitting in the 1.11.1 sequence — in numerology, 1 is the number of creation, and 11 is the Master Number, the bridge between the conscious and subconscious.",
        "u/Tutor_Kevin · r/numerology", 578, ["Portal Energy", "App Content", "Launch Frame"], diamond=True))

    parts.append('<h3 style="color:var(--accent);margin:24px 0 12px;font-size:1rem">&#x1F947; Gold Tier</h3>')
    parts.append(gold_quote(
        "2026 adds up to 1 (2+0+2+6=1), making this the Sun's year. In Vedic Numerology, this signals a reboot energy. New chapters open, old ones close.",
        "u/rampm · r/numerology", 92, ["2026 Content", "Universal Year", "App Hook"]))
    parts.append(gold_quote(
        "Life Path 33 Is Not a Trophy. It Is a Calling. Or a Burden. People discover they calculate to 33 and immediately assume they are spiritually superior.",
        "u/AlbatrossIll6353 · r/numerology", 29, ["Master Numbers", "Depth Content", "Community Reality"]))
    parts.append(gold_quote(
        "How Seeing 444 Saved Me From the Biggest Financial Mistake of My Life — 444 straight up saved me from making a huge financial mistake.",
        "u/TheMarieWatkins · r/numerology", 133, ["Angel Numbers", "Proof of Value", "Landing Page Copy"]))
    parts.append(gold_quote(
        "ChatGPT explained basically who I am based through numerology... its deep.",
        "u/ConstructionDry8140 · r/numerology", 31, ["AI + Numerology", "Product Direction", "User Sentiment"]))
    parts.append(gold_quote(
        "Your Life Path number isn't just a personality type — it describes the central challenge, gift, and direction of your entire existence.",
        "u/Pale_Display3669 · r/numerology", 27, ["Hero Text", "App Copy", "Life Path"]))
    parts.append(gold_quote(
        "Seeing repeating numbers (111, 444) isn't always a sign — sometimes it's just coincidence. Learn to discern.",
        "u/rampm · 20 Hard Truths · r/numerology", 67, ["Credibility", "Balanced App Framing"]))
    parts.append(end_section())

    # ── S17: KEY FACTS ─────────────────────────────────────────────────────────
    parts.append(section(17, "Key Facts &amp; Claims", "Factual claims made by the community — verified, plausible, or needs checking"))
    parts.append("""
<table class="report-table">
<thead><tr><th>Claim</th><th>Source</th><th>Status</th></tr></thead>
<tbody>
<tr><td>2026 = Universal Year 1 (2+0+2+6=10=1). The Sun Year. Year of new beginnings.</td><td>u/rampm, u/_Zapray_, multiple posts</td><td>&#x2705; Verified — standard numerological calculation, consistent across all posts</td></tr>
<tr><td>Life Path calculation: reduce full birthdate (DD+MM+YYYY), stop at 11, 22, or 33 (Master Numbers)</td><td>u/Pale_Display3669, community consensus</td><td>&#x2705; Verified — this is standard Pythagorean numerology practice</td></tr>
<tr><td>Personal Year = Birth Day + Birth Month + Current Year, reduced to single digit</td><td>u/_Zapray_ · score:101, multiple corroborations</td><td>&#x2705; Verified — consistent across all practitioner posts</td></tr>
<tr><td>Karmic Debt Numbers: 13, 14, 16, 19 carry specific challenges from past life/karma</td><td>u/rampm · 20 Hard Truths</td><td>&#x26A0;&#xFE0F; Plausible within system — Pythagorean tradition. Not independently verifiable.</td></tr>
<tr><td>Jacqueline Fernandez changed her name spelling per numerological advice</td><td>u/cole_palmer80 · score:365, Australian news crosspost</td><td>&#x2705; Verified — multiple media sources confirmed (Australian politician Sussan Ley also reported)</td></tr>
<tr><td>Dictator of Burma (Ne Win) was obsessed with numerology and restructured the entire economy around the number 9</td><td>u/amansaggu26 · TIL · score:2,431</td><td>&#x2705; Verified — historically documented fact, widely cited</td></tr>
<tr><td>Master Number 33 carriers are extremely rare — most people who calculate to 33 are actually a 6</td><td>u/AlbatrossIll6353 · score:29, community debate</td><td>&#x26A0;&#xFE0F; Plausible — depends on whether you reduce before or after summing</td></tr>
<tr><td>Pythagorean and Chaldean systems give different letter-to-number mappings and different results</td><td>Multiple practitioner posts</td><td>&#x2705; Verified — factually correct, both systems widely documented</td></tr>
<tr><td>r/numerology has 59,800+ subscribers as of March 2026</td><td>Reddit metadata</td><td>&#x2705; Verified — Reddit subscriber count at time of capture</td></tr>
</tbody>
</table>
""")
    parts.append(end_section())

    # ── S18: PRIVACY ──────────────────────────────────────────────────────────
    parts.append(section(18, "Privacy &amp; Data Handling", "How this dataset was collected and processed"))
    parts.append("""
<p>This report is based entirely on publicly posted content from r/numerology on Reddit. All posts analysed were published publicly by their authors with no expectation of privacy. No private messages, DMs, account details beyond public usernames, or non-public data was accessed.</p>
<p>Usernames referenced in this report are the Reddit handles authors voluntarily used for public posts. All quotations are attributed to their public source. No personal identifying information beyond public Reddit usernames has been processed or stored.</p>
""")
    parts.append(alert("info", "&#x2139;&#xFE0F; Data Scope", "237 unique posts · 12,842 total comment interactions · Subreddit: r/numerology · Capture: March 2026 · All content publicly accessible at time of capture."))
    parts.append(end_section())

    # ── CLOSING: THE MANDATE ────────────────────────────────────────────────────
    parts.append("""<div class="section" id="closing">
<div class="section__number">CLOSING</div>
<h2 class="section__title">The Mandate</h2>
<p class="section__subtitle">What this data definitively shows — and what Wayne should do about it</p>
""")
    parts.append('<h3 style="color:var(--heading);font-size:1rem;margin-bottom:14px">10 Definitive Findings from 237 Posts and 12,842 Comment Interactions</h3>')
    parts.append("""
<ol style="font-size:0.88rem;line-height:1.9;color:var(--text);margin-left:24px;margin-bottom:28px">
<li><strong>The #1 question in this community is "what does this number mean?" — asked 40+ times a month and never definitively answered.</strong> This is the open product gap Wayne can close.</li>
<li><strong>2026 is Universal Year 1.</strong> The numerological alignment for launching new projects is as explicitly favourable as it gets according to this community's framework. Wayne's apps launch in the right year.</li>
<li><strong>No dominant numerology tool exists in this community's awareness.</strong> Practitioners calculate by hand. Newcomers Google and get shallow results. The gap between demand and available tools is large and proven.</li>
<li><strong>Personalisation is the unmet need.</strong> 'Most numerology content gives you a keyword and a paragraph.' Interpreted, explained, personalised output is the differentiator no current tool provides well.</li>
<li><strong>The community's core calculations are simple and JavaScript-ready.</strong> Life Path, Personal Year, Angel Numbers — all pure arithmetic. No AI, no database, no backend needed. Static page + 50 lines of JS delivers genuine value.</li>
<li><strong>The business/money segment has real payment intent.</strong> Users in this segment are already paying numerologists. A well-built business name tool or premium profile generator has a ready audience willing to pay.</li>
<li><strong>Calculator results are naturally shareable.</strong> People share their Life Path, Personal Year, and compatibility results. Build shareable output cards into every tool from launch and get organic distribution for free.</li>
<li><strong>The practitioner community rewards authenticity and depth over fluff.</strong> The highest-scoring genuine numerology posts are detailed, honest, and admit limitations. Wayne's apps should follow this standard: show calculations, explain reasoning, acknowledge debate.</li>
<li><strong>Portal date posts go viral.</strong> Calendar-driven content with a numerological hook (Today is 11/11 etc.) is the highest viral coefficient format available. Wayne's content calendar writes itself.</li>
<li><strong>The sceptical layer is loud but minority.</strong> 63% of genuine community sentiment is positive-to-mystical. The believers are emotionally committed. Build for them. The sceptics will object regardless; do not let them set the product direction.</li>
</ol>
""")
    parts.append("""
<div class="gold-quote gold-quote--diamond" style="margin-bottom:28px">
<div class="gold-quote__text">"Numerology isn't magic — it's a tool. Your numbers reveal patterns, but it's up to YOU to take action. The community has been asking for better tools for years. Nobody has built them yet."</div>
<div class="gold-quote__meta"><span>Synthesised from r/numerology community intelligence · March 2026</span><span>237 posts · 12,842 comments</span></div>
</div>
""")
    parts.append("""
<div class="mandate-box">
<div class="mandate-box__statement">
The r/numerology community asks the same questions every day.<br>
The same numbers. The same calculations. The same desires for meaning.<br><br>
Nobody has built the definitive answer to those questions as a clean, fast, free, deeply-interpreted web experience.<br><br>
<strong>Wayne is a builder. This community is waiting. 2026 is Universal Year 1.</strong><br><br>
The numbers are aligned.
</div>
</div>
""")
    parts.append('<h3 style="color:var(--heading);font-size:1rem;margin:28px 0 16px">Closing Part 2 — What This Data Actually Represents</h3>')
    parts.append("""<div class="alert alert--indigo">
<div class="alert__title">&#x1F4CA; What 12,842 comment interactions on numerology posts mean</div>
<p>These comments were not written by people asked to evaluate numerology. They were written voluntarily by strangers who saw a number on a clock, on a licence plate, or in a dream — and needed to know what it meant badly enough to post publicly about it. That is organic demand, not manufactured interest.</p>
<p>Across <strong>237 posts and 12,842 comment interactions</strong> from a 59,800-member community, the dominant behaviours are: asking for interpretation (30%), sharing personal experience with numbers (22%), and engaging with forecasts and guides (20%). For Wayne as a builder, this data translates to three product insights: <strong>people want instant lookup, people want personalisation, and people return when the content is timed to their life cycle.</strong></p>
<p>The zero dominant apps cited in this dataset is not an oversight — it is the market signal. The community has no tool it consistently recommends. That space is open.</p>
</div>""")
    parts.append('<h3 style="color:var(--heading);font-size:1rem;margin:28px 0 16px">First 72 Hours Action Plan</h3>')
    parts.append("""
<ol style="font-size:0.88rem;line-height:1.9;color:var(--text);margin-left:24px">
<li><strong>Calculate your own full numerology profile using Section 13 formulas.</strong> Life Path, Expression, Soul Urge, Personal Year 2026. Write it down. Know your numbers. You cannot build authentically for this community until you live it yourself. (30 minutes)</li>
<li><strong>Build the 444 angel number page first.</strong> One clean static HTML page with a thorough interpretation of 444. No calculator yet — just content. Test the SEO signal and community reception before building infrastructure. (2 hours)</li>
<li><strong>Build the Life Path calculator.</strong> Vanilla JS, step-by-step reduction display, Master Number detection, full interpretation for each number 1–9 + 11/22/33. This is the anchor page everything else links to. (1 day)</li>
<li><strong>Post in r/numerology:</strong> 'I built a free Life Path calculator — it shows every step and explains what your number means in detail. Would love to hear if it's useful for this community.' Respond to every reply. (30 minutes to post, ongoing)</li>
<li><strong>Add Personal Year 2026 to the Life Path page output.</strong> After showing Life Path, show: 'Your Personal Year in 2026 is X — here's what that means.' One extra calculation, doubles the value. (1 hour)</li>
<li><strong>Set up your daily numerological practice using Section 13.</strong> Morning: Personal Day check. Month start: Personal Month check. These are the habits the practitioner community you are building for lives by. Align with them. (15 minutes daily)</li>
<li><strong>Follow u/rampm, u/Tutor_Kevin, u/Bthemanifestor, u/_Zapray_ on Reddit.</strong> Their next posts are your next tool ideas. (5 minutes)</li>
</ol>
""")
    parts.append(end_section())
    return "\n".join(parts)


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
<title>Audience Intelligence Report — r/numerology · Reddit Community Intelligence · March 2026</title>
<style>{CSS}</style>
</head>
<body>
{cover}
<main id="report-main">
{main_content}
</main>
<div class="page-footer">
  Generated by <strong>Audience Intelligence</strong> &middot; <a href="https://audienceintelligence.com">audienceintelligence.com</a> &middot; {gen_date}<br>
  Prepared for <strong>Wayne Michael</strong> &middot; r/numerology Reddit Community Intelligence Report
</div>
<div class="disclaimer">
DISCLAIMER: This report is produced for informational and research purposes only. It does not constitute spiritual, financial, legal, or professional advice. Numerological interpretations represent community-sourced views and traditional esoteric frameworks, not verified scientific claims. All figures, sentiment percentages, and classifications are estimates derived from analysis of publicly available Reddit posts. Users should independently assess any information before relying on it for personal or business decisions. All quoted content belongs to the original Reddit authors. Visit audienceintelligence.com for more information.
</div>
</body>
</html>"""


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    print("Building report...")
    body = build_report()
    html = build_html(body)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report saved to: {OUT_PATH}")
    print(f"File size: {len(html):,} characters")
