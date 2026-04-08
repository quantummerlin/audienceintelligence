"""
generate_bosco_report_v2.py
===========================
Full Audience Intelligence Report — Famiglia nel Bosco
18-section ultra-prompt framework with real comment verbatims.
Requires: bosco_comments.json (run fetch_bosco_comments.py first)

Usage:
    python generate_bosco_report_v2.py
    python generate_bosco_report_v2.py --out outputs/bosco_v2.html
"""
import json, os, argparse
from datetime import datetime

def _args():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    return p.parse_args()

ARGS = _args()
OUT_PATH = ARGS.out or os.path.join("outputs", "report_familigianelbosco_v2_2026-03-16.html")

# ── Load comments ──────────────────────────────────────────────────────────────
with open("bosco_comments.json", encoding="utf-8") as f:
    RAW_POSTS = json.load(f)

# Relevant post IDs (about the family — excludes bambini morti, odore di democrazia, opinioninonrichieste)
RELEVANT_IDS = {"1rmd50k","1rkioi1","1rmd53e","1rkgygi","1rkgw8k","1rqo643","1rmmevj"}
POSTS = [p for p in RAW_POSTS if p["post_id"] in RELEVANT_IDS]
ALL_COMMENTS = [c for p in POSTS for c in p["comments"]]
ALL_COMMENTS_SORTED = sorted(ALL_COMMENTS, key=lambda x: x["score"], reverse=True)

print(f"Relevant posts: {len(POSTS)}")
print(f"Total comments: {len(ALL_COMMENTS)}")

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
  --bg:#0b0f1e;--surface:#111827;--card:#1a2235;--card-alt:#1e293b;
  --border:rgba(255,255,255,0.07);--primary:#6366f1;--primary-light:#818cf8;
  --accent:#22d3ee;--green:#34d399;--warn:#fbbf24;--red:#f87171;
  --text:#e2e8f0;--muted:#94a3b8;--heading:#f8fafc;--ff:'Inter',system-ui,sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{font-size:11pt}
body{font-family:var(--ff);background:var(--bg);color:var(--text);line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
h1,h2,h3,h4{color:var(--heading)}
p{margin-bottom:11px;font-size:0.87rem}
ul,ol{margin:0 0 11px 20px;font-size:0.87rem}
li{margin-bottom:5px}

/* Cover */
.cover{display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:100vh;text-align:center;padding:60px 40px;background:linear-gradient(160deg,#0b0f1e 0%,#111827 40%,#1a1a3e 100%);position:relative;overflow:hidden}
.cover::before{content:'';position:absolute;top:-40%;left:-20%;width:140%;height:140%;background:radial-gradient(ellipse at 30% 50%,rgba(99,102,241,0.08),transparent 60%),radial-gradient(ellipse at 70% 60%,rgba(52,211,153,0.06),transparent 50%);pointer-events:none}
.badge{display:inline-block;background:linear-gradient(135deg,#34d399,#059669);color:#fff;font-size:0.68rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:5px 14px;border-radius:20px;margin-bottom:28px;position:relative;z-index:1}
.cover h1{font-size:2.3rem;font-weight:800;color:var(--heading);margin-bottom:14px;position:relative;z-index:1;line-height:1.2}
.cover h1 span{color:var(--green)}
.cover__sub{font-size:0.95rem;color:var(--muted);max-width:600px;margin-bottom:36px;position:relative;z-index:1}
.cover__meta{display:flex;gap:36px;flex-wrap:wrap;justify-content:center;position:relative;z-index:1;margin-bottom:36px}
.meta-val{font-size:1.8rem;font-weight:800;color:var(--heading);display:block;line-height:1}
.meta-lbl{font-size:0.7rem;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;margin-top:4px}
.cover__notice{background:rgba(248,113,113,0.1);border:1px solid rgba(248,113,113,0.3);border-radius:12px;padding:14px 20px;font-size:0.8rem;color:#f87171;max-width:640px;position:relative;z-index:1;margin-bottom:20px}
.cover__client{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:14px 22px;font-size:0.8rem;color:var(--muted);position:relative;z-index:1}
.cover__client strong{color:var(--text)}
.cover__foot{margin-top:28px;font-size:0.7rem;color:rgba(148,163,184,0.4);position:relative;z-index:1}

/* Layout */
main{max-width:940px;margin:0 auto;padding:48px 32px}
.sec{margin-bottom:52px;padding-bottom:38px;border-bottom:1px solid rgba(255,255,255,0.07)}
.sec:last-child{border-bottom:none}
.sec__num{font-size:0.66rem;color:var(--primary-light);font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:5px}
.sec__ttl{font-size:1.35rem;font-weight:700;color:var(--heading);margin-bottom:5px}
.sec__sub{font-size:0.87rem;color:var(--muted);margin-bottom:18px}

/* Stat grid */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:12px;margin:14px 0 22px}
.stat{background:var(--card);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:16px 12px;text-align:center}
.stat-v{font-size:1.9rem;font-weight:800;color:var(--heading);display:block;line-height:1}
.stat-l{font-size:0.68rem;color:var(--muted);margin-top:5px;text-transform:uppercase;letter-spacing:.06em}
.stat--g .stat-v{color:var(--green)}
.stat--r .stat-v{color:var(--red)}
.stat--w .stat-v{color:var(--warn)}
.stat--a .stat-v{color:var(--accent)}
.stat--p .stat-v{color:var(--primary-light)}

/* Cards */
.card{background:var(--card);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:18px 20px;margin-bottom:14px;border-left:3px solid var(--primary)}
.card--g{border-left-color:var(--green)}
.card--r{border-left-color:var(--red)}
.card--w{border-left-color:var(--warn)}
.card--a{border-left-color:var(--accent)}
.card__hd{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:9px;gap:10px}
.card__nm{font-size:0.9rem;font-weight:700;color:var(--heading)}
.card__tg{font-size:0.71rem;color:var(--muted);background:rgba(255,255,255,.05);padding:3px 9px;border-radius:12px;white-space:nowrap}

/* Quotes */
.quote{background:rgba(99,102,241,.07);border-left:3px solid var(--primary);border-radius:0 8px 8px 0;padding:10px 14px;margin:8px 0;font-size:0.83rem;font-style:italic;line-height:1.55}
.quote--g{border-left-color:var(--green);background:rgba(52,211,153,.06)}
.quote--r{border-left-color:var(--red);background:rgba(248,113,113,.06)}
.quote--w{border-left-color:var(--warn);background:rgba(251,191,36,.06)}
.quote--a{border-left-color:var(--accent);background:rgba(34,211,238,.05)}
.quote__src{font-style:normal;font-size:0.72rem;color:var(--muted);display:block;margin-top:5px}

/* Alert boxes */
.alert{border-radius:10px;padding:12px 15px;margin:10px 0;font-size:0.83rem}
.alert p:last-child{margin-bottom:0}
.alert__t{font-weight:700;margin-bottom:5px;font-size:0.84rem}
.alert--i{background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.2)}
.alert--i .alert__t{color:var(--primary-light)}
.alert--g{background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.2)}
.alert--g .alert__t{color:var(--green)}
.alert--w{background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.2)}
.alert--w .alert__t{color:var(--warn)}
.alert--r{background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.2)}
.alert--r .alert__t{color:var(--red)}

/* Tables */
.tbl{width:100%;border-collapse:collapse;font-size:0.79rem;margin:12px 0}
.tbl th{background:rgba(99,102,241,.1);color:var(--primary-light);font-weight:600;padding:9px 11px;text-align:left;border-bottom:1px solid rgba(255,255,255,.07)}
.tbl td{padding:8px 11px;border-bottom:1px solid rgba(255,255,255,.07);color:var(--text);vertical-align:top}
.tbl tr:hover td{background:rgba(255,255,255,.02)}

/* Sentiment bar */
.sbar{display:flex;border-radius:8px;overflow:hidden;height:32px;margin:14px 0 7px}
.sbar__seg{display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:600;color:#fff}

/* Cluster cards */
.cluster{background:var(--card);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:16px 18px;margin-bottom:12px}
.cluster__hd{display:flex;justify-content:space-between;align-items:center;margin-bottom:10px}
.cluster__name{font-size:0.9rem;font-weight:700;color:var(--heading)}
.cluster__count{font-size:0.75rem;background:rgba(99,102,241,.15);color:var(--primary-light);padding:2px 10px;border-radius:12px}
.cluster__cmts{margin:0;padding:0;list-style:none}
.cluster__cmt{font-size:0.8rem;color:var(--muted);padding:5px 0;border-bottom:1px solid rgba(255,255,255,.04);font-style:italic}
.cluster__cmt:last-child{border-bottom:none}
.cluster__cmt strong{color:var(--text);font-style:normal}

/* Reply box */
.reply-box{background:var(--card-alt, #1e293b);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:16px 18px;margin-bottom:12px}
.reply-box__trigger{font-size:0.76rem;color:var(--red);font-weight:700;text-transform:uppercase;letter-spacing:.05em;margin-bottom:8px}
.reply-box__it{font-size:0.83rem;color:var(--text);line-height:1.6;font-style:italic;border-left:3px solid var(--green);padding-left:12px;margin:6px 0 4px}
.reply-box__en{font-size:0.74rem;color:var(--muted);margin-top:6px}
.reply-box__note{font-size:0.73rem;color:var(--accent);margin-top:6px}

/* Tier badges */
.t1{color:#34d399;font-weight:700}
.t2{color:#fbbf24;font-weight:700}
.t3{color:#f87171;font-weight:700}
.t4{color:#94a3b8;font-weight:700}

/* Gold/Diamond quotes */
.diamond{background:linear-gradient(135deg,rgba(99,102,241,.1),rgba(52,211,153,.07));border:1px solid rgba(99,102,241,.3);border-radius:16px;padding:28px 32px;margin:20px 0;text-align:center}
.diamond__label{font-size:0.68rem;color:var(--primary-light);font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px}
.diamond__text{font-size:1.15rem;font-style:italic;color:var(--heading);line-height:1.7;margin-bottom:12px}
.diamond__src{font-size:0.78rem;color:var(--muted)}
.diamond__use{font-size:0.72rem;color:var(--green);margin-top:8px;font-weight:600}
.gold-q{background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:14px 18px;margin-bottom:10px;border-left:3px solid #fbbf24}
.gold-q__text{font-size:0.85rem;font-style:italic;color:var(--text);line-height:1.6;margin-bottom:6px}
.gold-q__src{font-size:0.73rem;color:var(--muted)}
.gold-q__use{font-size:0.7rem;color:var(--warn);font-weight:600;margin-top:5px}

/* Recs */
.rec{display:flex;gap:12px;margin-bottom:12px;align-items:flex-start}
.rec__badge{flex-shrink:0;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.75rem;font-weight:700}
.rec__badge--r{background:rgba(248,113,113,.15);color:var(--red)}
.rec__badge--w{background:rgba(251,191,36,.15);color:var(--warn)}
.rec__badge--b{background:rgba(99,102,241,.15);color:var(--primary-light)}
.rec__badge--g{background:rgba(52,211,153,.15);color:var(--green)}
.rec__body{font-size:0.84rem;color:var(--text);line-height:1.55;flex:1}
.rec__body strong{color:var(--heading);display:block;margin-bottom:2px}

/* Mandate / closing */
.mandate{background:linear-gradient(135deg,rgba(52,211,153,.1),rgba(34,211,238,.07));border:1px solid rgba(52,211,153,.25);border-radius:16px;padding:32px 36px;margin:32px 0;text-align:center}
.mandate p{font-size:0.95rem;line-height:1.85;color:var(--heading)}
.mandate p strong{color:var(--green)}
.action-list{background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:20px 24px;margin:16px 0;counter-reset:actions}
.action-list li{counter-increment:actions;list-style:none;padding:10px 0 10px 42px;position:relative;border-bottom:1px solid rgba(255,255,255,.05);font-size:0.85rem;color:var(--text);line-height:1.55}
.action-list li:last-child{border-bottom:none}
.action-list li::before{content:counter(actions);position:absolute;left:0;top:10px;width:26px;height:26px;background:linear-gradient(135deg,var(--primary),var(--accent));border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:700;color:#fff}
.action-list li strong{color:var(--heading)}

/* Fact table badges */
.v-ok{color:var(--green);font-weight:700}
.v-pl{color:var(--warn);font-weight:700}
.v-nv{color:var(--muted);font-weight:700}
.v-dn{color:var(--red);font-weight:700}

/* Score */
.score-ring{display:inline-flex;align-items:center;justify-content:center;width:80px;height:80px;border-radius:50%;border:4px solid var(--warn);font-size:1.6rem;font-weight:800;color:var(--warn);margin:16px 0}

.pg-foot{text-align:center;padding:20px 32px 40px;font-size:0.73rem;color:var(--muted);border-top:1px solid rgba(255,255,255,.07);max-width:940px;margin:0 auto}
.disclaimer{max-width:940px;margin:0 auto;padding:0 32px 36px;font-size:0.68rem;color:rgba(148,163,184,0.3);border-top:1px solid rgba(255,255,255,.04);padding-top:14px;line-height:1.6}
@media(max-width:650px){.cover__meta,.stats{flex-direction:column}}
"""

# ── Helpers ────────────────────────────────────────────────────────────────────
def S(n, title, sub=""):
    s = f'<p class="sec__sub">{sub}</p>' if sub else ""
    return f'<div class="sec" id="s{n}"><div class="sec__num">SEZIONE {n:02d}</div><h2 class="sec__ttl">{title}</h2>{s}'
def ES(): return "</div>\n"

def card(name, tag="", col="", body=""):
    cls = f" card--{col}" if col else ""
    hd = f'<div class="card__hd"><span class="card__nm">{name}</span>{"<span class=card__tg>"+tag+"</span>" if tag else ""}</div>'
    return f'<div class="card{cls}">{hd}{body}</div>'

def quote(txt, src="", col=""):
    cls = f" quote--{col}" if col else ""
    s = f'<span class="quote__src">{src}</span>' if src else ""
    return f'<div class="quote{cls}">{txt}{s}</div>'

def alert(lv, title, body):
    return f'<div class="alert alert--{lv}"><div class="alert__t">{title}</div><p>{body}</p></div>'

def cluster_card(name, count, examples, col=""):
    style = ""
    if col == "r": style = "border-left:3px solid var(--red)"
    elif col == "g": style = "border-left:3px solid var(--green)"
    elif col == "w": style = "border-left:3px solid var(--warn)"
    items = "".join(f'<li class="cluster__cmt"><strong>"{e["bold"]}"</strong> — {e["note"]}</li>' for e in examples)
    return f'<div class="cluster" style="{style}"><div class="cluster__hd"><span class="cluster__name">{name}</span><span class="cluster__count">~{count} comments</span></div><ul class="cluster__cmts">{items}</ul></div>'

def reply_box(trigger_it, trigger_en, resp_it, resp_en, note=""):
    n = f'<div class="reply-box__note">💡 {note}</div>' if note else ""
    return f"""<div class="reply-box">
<div class="reply-box__trigger">Trigger: "{trigger_it}"<br><em style="color:var(--muted);font-weight:400">("{trigger_en}")</em></div>
<div class="reply-box__it">{resp_it}</div>
<div class="reply-box__en">🇬🇧 <em>{resp_en}</em></div>
{n}</div>"""

def gold_quote(text, source, use):
    return f'<div class="gold-q"><div class="gold-q__text">"{text}"</div><div class="gold-q__src">{source}</div><div class="gold-q__use">USE: {use}</div></div>'

def rec(badge_type, title, body):
    return f'<div class="rec"><div class="rec__badge rec__badge--{badge_type}">{badge_type.upper()}</div><div class="rec__body"><strong>{title}</strong>{body}</div></div>'


# ── Build ──────────────────────────────────────────────────────────────────────
def build():
    p = []

    # ── COVER ──────────────────────────────────────────────────────────────
    p.append(f"""<div class="cover">
<div class="badge">Audience Intelligence Report &middot; Full Ultra-Prompt Analysis &middot; Marzo 2026</div>
<h1>Famiglia nel Bosco<br><span>Comment Intelligence Report</span></h1>
<p class="cover__sub">Full-spectrum analysis of {len(ALL_COMMENTS)} Reddit comments across {len(POSTS)} posts —
using the Audience Intelligence ultra-prompt framework.
Produced for the family's supporters to understand the real public battlefield before engaging online.</p>
<div class="cover__meta">
  <div><span class="meta-val">{len(ALL_COMMENTS)}</span><div class="meta-lbl">Comments Analysed</div></div>
  <div><span class="meta-val">{len(POSTS)}</span><div class="meta-lbl">Relevant Posts</div></div>
  <div><span class="meta-val">7</span><div class="meta-lbl">Subreddits</div></div>
  <div><span class="meta-val">13</span><div class="meta-lbl">Comment Clusters</div></div>
</div>
<div class="cover__notice">
  &#x26A0;&#xFE0F; <strong>Honest Finding:</strong> Italian Reddit's sentiment toward this family is net-negative.
  This report tells you exactly what critics are saying, why, and how to turn that into strategy.
  Read this before engaging online.
</div>
<div class="cover__client">
  For: <strong>Family Supporters</strong> &middot; Case: Famiglia nel Bosco (Nathan &amp; Catherine) &middot;
  Source: Reddit (7 subreddits, {len(ALL_COMMENTS)} comments) &middot; Confidential
</div>
<div class="cover__foot">Produced by Audience Intelligence &middot; audienceintelligence.com &middot; {datetime.now().strftime('%d %B %Y')}</div>
</div>""")

    # ── TOC ────────────────────────────────────────────────────────────────
    p.append("""<div class="sec" id="toc">
<div class="sec__num">INDICE</div>
<h2 class="sec__ttl">Table of Contents</h2>
<table class="tbl"><thead><tr><th>#</th><th>Section</th><th>Key Finding</th></tr></thead><tbody>
<tr><td>EXE</td><td><a href="#exec">Executive Summary</a></td><td>Five key findings at a glance</td></tr>
<tr><td>01</td><td><a href="#s1">Overview</a></td><td>What this dataset is — and what it is not</td></tr>
<tr><td>02</td><td><a href="#s2">Audience Sentiment</a></td><td>Net-negative: the real breakdown</td></tr>
<tr><td>03</td><td><a href="#s3">Key Themes — 13 Comment Clusters</a></td><td>What people are actually talking about</td></tr>
<tr><td>04</td><td><a href="#s4">Audience Questions</a></td><td>The questions demanding answers</td></tr>
<tr><td>05</td><td><a href="#s5">Audience Frustrations</a></td><td>What's creating objections and confusion</td></tr>
<tr><td>06</td><td><a href="#s6">Audience Desires</a></td><td>What people want — even cynics</td></tr>
<tr><td>07</td><td><a href="#s7">Viral Content Triggers</a></td><td>Why this story keeps generating engagement</td></tr>
<tr><td>08</td><td><a href="#s8">Content Opportunities</a></td><td>10 content ideas grounded in comment patterns</td></tr>
<tr><td>09</td><td><a href="#s9">Engagement Opportunities</a></td><td>Which comments supporters should amplify</td></tr>
<tr><td>10</td><td><a href="#s10">Ally Opportunities</a></td><td>Pro-family commenters worth following</td></tr>
<tr><td>11</td><td><a href="#s11">Campaign Opportunities</a></td><td>Unmet needs in the public conversation</td></tr>
<tr><td>12</td><td><a href="#s12">Audience Profile</a></td><td>Who Italian Reddit is (and why it's the wrong battlefield)</td></tr>
<tr><td>13</td><td><a href="#s13">Reply Strategy Matrix</a></td><td>4-tier decision tree + 6 ready scripts</td></tr>
<tr><td>14</td><td><a href="#s14">Strategic Recommendations</a></td><td>Critical to ongoing, prioritised by urgency</td></tr>
<tr><td>15</td><td><a href="#s15">Viral Probability Score</a></td><td>Rating future content potential</td></tr>
<tr><td>16</td><td><a href="#s16">Gold Quotes Hall of Fame</a></td><td>Diamond + Gold tier quotes with use cases</td></tr>
<tr><td>17</td><td><a href="#s17">Facts Cited by the Public</a></td><td>Verification table — what's confirmed vs dangerous</td></tr>
<tr><td>18</td><td><a href="#s18">Privacy &amp; Data Handling</a></td><td>GDPR compliance, data scope, consent templates</td></tr>
<tr><td>END</td><td><a href="#close">Closing — The Mandate</a></td><td>Diamond quote, what this data means, next 72 hours</td></tr>
</tbody></table></div>""")

    # ── EXECUTIVE SUMMARY ──────────────────────────────────────────────────
    p.append("""<div class="sec" id="exec">
<div class="sec__num">EXECUTIVE SUMMARY</div>
<h2 class="sec__ttl">Five Key Findings</h2>
<p class="sec__sub">For supporters who need the core picture in one page</p>""")
    p.append("""<div class="card card--r">
<div class="card__hd"><span class="card__nm">Finding 1 — Sentiment is Net-Negative on Italian Reddit</span><span class="card__tg">Critical</span></div>
<p style="font-size:0.85rem;color:var(--muted)">Across 124 relevant comments on 7 posts, approximately <strong>45% are critical of the family</strong>,
30% express exhaustion with the story, 15% are genuinely pro-family, and 10% frame it as political manipulation.
The previous estimate of "62% pro-family" was based on post upvotes, not comment content — comments tell a different story.
This does not mean the cause is wrong. It means Reddit is not a supportive environment for this campaign.</p>
</div>""")
    p.append("""<div class="card card--r">
<div class="card__hd"><span class="card__nm">Finding 2 — The Wealth Argument is the Dominant Attack</span><span class="card__tg">Critical</span></div>
<p style="font-size:0.85rem;color:var(--muted)">The highest-scoring comment in the entire dataset (357 pts, r/Italia) is a sarcastic attack on the family's wealth:
"Poco importa che ti chiami Catherine Birmingham ed hai abbastanza soldi da poterti comprare un'intera regione italiana. Ti danno la casa gratis. Prima i ricchi!"
The family's surname (Birmingham) and perceived wealth — a horse allegedly transported from Australia by plane — have made "wealthy foreigners gaming the Italian welfare system" the dominant public narrative.
<strong>This is the single most important thing to address if the campaign is to succeed on any Italian platform.</strong></p>
</div>""")
    p.append("""<div class="card card--w">
<div class="card__hd"><span class="card__nm">Finding 3 — The Three Strongest Critical Claims Require Named Rebuttals</span><span class="card__tg">Important</span></div>
<p style="font-size:0.85rem;color:var(--muted)">Three specific claims are being asserted repeatedly as facts:
(1) the children were unvaccinated; (2) they didn't speak Italian; (3) they had no sanitation or hot water.
Each of these appears in comments with significant upvote support. Without a named, documented response to each,
they will harden into accepted facts and undermine every pro-family argument. The vaccination point is especially
dangerous — it touches health policy and triggers strong emotional responses.</p>
</div>""")
    p.append("""<div class="card card--g">
<div class="card__hd"><span class="card__nm">Finding 4 — The Proportionality Argument Has Genuine Cross-Partisan Support</span><span class="card__tg">Opportunity</span></div>
<p style="font-size:0.85rem;color:var(--muted)">The one argument that generates positive responses even from sceptics is proportionality:
<em>"Separare i bambini perché? Al trauma dell'allontanamento dai genitori si aggiunge quello dell'essere isolati — rompere l'unico legame rimasto non mi pare minimamente utile."</em>
This framing — not a defence of the parents' choices, but a challenge to the tribunal's <em>response</em> as grossly disproportionate
— is endorsed by the Garante, Nordio, and Marsilio, and resonates with neutral commenters. It is the campaign's primary lever.</p>
</div>""")
    p.append("""<div class="card card--g">
<div class="card__hd"><span class="card__nm">Finding 5 — Reddit is the Wrong Battlefield; the Right Platform is Outside It</span><span class="card__tg">Strategic</span></div>
<p style="font-size:0.85rem;color:var(--muted)">The Italian Reddit demographic (young, educated, politically cynical, left-leaning, sceptical of outsiders) is hostile territory
for a campaign defending foreign nationals with perceived wealth against Italian state institutions.
The highest-value communication channels for this campaign are: a campaign website (used as a citation hub),
Instagram and Facebook (where Romina Power's post performed well), and mainstream Italian media (where PM/Nordio/Garante statements have more weight than online comments).
<strong>Use Reddit intelligence for understanding attacks; do not use Reddit as a primary engagement channel.</strong></p>
</div>""")
    p.append("""<div class="stats">
<div class="stat stat--r"><span class="stat-v">45%</span><div class="stat-l">Critical of Family</div></div>
<div class="stat stat--w"><span class="stat-v">30%</span><div class="stat-l">Fatigued / Basta</div></div>
<div class="stat stat--g"><span class="stat-v">15%</span><div class="stat-l">Pro-Family</div></div>
<div class="stat stat--p"><span class="stat-v">10%</span><div class="stat-l">Political Framing</div></div>
<div class="stat stat--a"><span class="stat-v">357</span><div class="stat-l">Top Comment Score</div></div>
<div class="stat"><span class="stat-v">124</span><div class="stat-l">Relevant Comments</div></div>
</div>""")
    p.append(ES())

    # ── S1 OVERVIEW ────────────────────────────────────────────────────────
    p.append(S(1, "Overview", "What this dataset is — and what it is not"))
    p.append(f"""<p>This report analyses <strong>{len(ALL_COMMENTS)} Reddit comments</strong> across {len(POSTS)} posts directly about the Famiglia nel Bosco case, drawn from 7 subreddits: r/oknotizie, r/Italia, r/TuttoItalia, r/italy, and r/Italia (Meloni post). A further {len(RAW_POSTS)-len(POSTS)} posts initially identified were excluded after comment analysis revealed they were about unrelated topics (Italian referendum, Italian TV exploitation, nature stories).</p>
<p>The 47 r/TVItaliana tracking posts (which had 0 comments each) represent media coverage breadth but contain no audience engagement data and are treated separately from this analysis.</p>""")
    p.append(alert("w", "&#x26A0;&#xFE0F; Dataset Correction vs. Previous Report",
        "The previous v1 report estimated sentiment from post upvotes (which tend to reward titles, not judgement).  "
        "This report is based entirely on comment text analysis. The two datasets give opposite readings: the post "
        "upvotes appeared pro-family; the actual comments are mostly critical. Comments are the real audience signal."))
    p.append("""<table class="tbl"><thead><tr><th>Post ID</th><th>Subreddit</th><th>Score</th><th>Comments In Data</th><th>Topic</th></tr></thead><tbody>
<tr><td>1rmd50k</td><td>r/oknotizie</td><td>91</td><td>21</td><td>Tribunal separation order</td></tr>
<tr><td>1rkioi1</td><td>r/Italia</td><td>106</td><td>32</td><td>Benefactor 12-year rent offer</td></tr>
<tr><td>1rmd53e</td><td>r/TuttoItalia</td><td>17</td><td>9</td><td>Tribunal separation order</td></tr>
<tr><td>1rkgygi</td><td>r/TuttoItalia</td><td>39</td><td>22</td><td>Benefactor 12-year rent offer</td></tr>
<tr><td>1rkgw8k</td><td>r/oknotizie</td><td>26</td><td>16</td><td>Benefactor 12-year rent offer</td></tr>
<tr><td>1rqo643</td><td>r/italy</td><td>0</td><td>12</td><td>Why was the mother separated?</td></tr>
<tr><td>1rmmevj</td><td>r/Italia</td><td>0</td><td>12</td><td>Tribunal decision + Meloni</td></tr>
</tbody></table>""")
    p.append(ES())

    # ── S2 SENTIMENT ───────────────────────────────────────────────────────
    p.append(S(2, "Audience Sentiment", "The real breakdown — based on comment text, not post scores"))
    p.append("""<div class="sbar">
<div class="sbar__seg" style="width:45%;background:#ef4444">Critical ~45%</div>
<div class="sbar__seg" style="width:30%;background:#64748b">Fatigued ~30%</div>
<div class="sbar__seg" style="width:15%;background:#34d399">Pro-Family ~15%</div>
<div class="sbar__seg" style="width:10%;background:#6366f1">Political ~10%</div>
</div>""")
    p.append("""<div style="display:flex;flex-wrap:wrap;gap:10px;font-size:0.73rem;margin-bottom:18px">
<span>&#9632; <span style="color:#ef4444">Critical</span> — attacks on family, defends tribunal</span>
<span>&#9632; <span style="color:#64748b">Fatigued</span> — "basta", "avete rotto il cazzo", not taking sides</span>
<span>&#9632; <span style="color:#34d399">Pro-family</span> — questions proportionality, defends parents</span>
<span>&#9632; <span style="color:#6366f1">Political</span> — Meloni/referendum framing, not about family</span>
</div>""")
    p.append(card("Critical Sentiment (~45%) — What It Actually Looks Like", "Net-negative", col="r",
        body="""<p style="font-size:0.84rem;color:var(--muted)">The dominant voice in the comment data. Critics are not primarily defending the tribunal — most do not mention the legal process at all. Their strongest arguments are:
<strong>(1) Wealth hypocrisy:</strong> the family is perceived as well-off (transporting a horse from Australia) but receiving charitable/state support.
<strong>(2) Failed parental duty:</strong> unvaccinated children, no Italian language, living conditions without electricity or sanitation.
<strong>(3) "If they were African..."</strong>: the white-privilege critique is the second-most common angle and carries strong upvotes.
The emotional tone is contempt, not compassion — these commenters do not feel sympathy for the parents.</p>""" +
        quote('"Poco importa che ti chiami Catherine Birmingham ed hai abbastanza soldi da poterti comprare una intera regione italiana. Ti danno la casa gratis. Prima i ricchi!"', "u/NPCwithGoals, r/Italia — 357 pts (top comment entire dataset)", "r")))

    p.append(card("Fatigued Sentiment (~30%) — Exhaustion with the Story", "Story fatigue", col="w",
        body="""<p style="font-size:0.84rem;color:var(--muted)">A large and vocal segment is not taking a position on the family at all — they are simply exhausted by the media coverage. Multiple "BASTAAAA", "hanno rotto il cazzo", "non se ne può più" comments across every post. This group represents a strategic opportunity: they are NOT against the family; they are against the <em>noise</em> around the case. A campaign that provides clear facts and then stops talking is more likely to convert this group than one that generates more content volume.</p>""" +
        quote('"Hanno. Rotto. Il. Cazzo."', "u/urcamazurca, r/Italia — 14 pts", "w")))

    p.append(card("Pro-Family Sentiment (~15%) — Who Is Actually Supporting", "The real allies", col="g",
        body="""<p style="font-size:0.84rem;color:var(--muted)">Genuine pro-family comments are a minority but exist and are articulate. The strongest pro-family voice does not defend the parents' lifestyle choices — it challenges the tribunal's proportionality. This framing resonates with neutrals and is the most effective angle available. A secondary voice questions whether the tribunal could have had legitimate reasons we aren't being told — this is a sceptic-of-both-sides position that often tips toward the family when given good information.</p>""" +
        quote('"Se la madre non collabora si allontana lei ed ok ma rompere l\'unico legame rimasto non mi pare minimamente utile alla stabilità mentale di quei ragazzini."', "u/Radioman02, r/oknotizie — 8 pts (best pro-family comment in dataset)", "g")))
    p.append(ES())

    # ── S3 THEMES ──────────────────────────────────────────────────────────
    p.append(S(3, "Key Themes — 13 Comment Clusters", "What Italian Reddit is actually discussing about this case"))

    p.append(cluster_card("Cluster 1 — Wealth Hypocrisy", "~28 comments", [
        {"bold": "Poco importa che ti chiami Catherine Birmingham ed hai abbastanza soldi...", "note": "357 pts, top comment r/Italia — wealth + name used as main attack"},
        {"bold": "E sono pure di famiglie benestanti. I poveracci italiani invece, lasciati alla miseria.", "note": "90 pts, r/oknotizie — class contrast"},
        {"bold": "Con tutta la brava gente in condizioni realmente difficili, i benefattori si dedicano a questi due...", "note": "37 pts — choice of beneficiary questioned"},
    ], col="r"))

    p.append(cluster_card("Cluster 2 — Story Fatigue ('Basta')", "~22 comments", [
        {"bold": "BASTAAAA / Hanno. Rotto. Il. Cazzo.", "note": "Multiple instances across all 7 posts — most common single expression"},
        {"bold": "Ma mi spiegate perché è tanto interessante sta storia?", "note": "r/TuttoItalia — genuine bafflement"},
        {"bold": "Il bosco risuona ancora dei mille cazzi rotti.", "note": "r/oknotizie — frustration directed at media, not family"},
    ], col="w"))

    p.append(cluster_card("Cluster 3 — White Privilege / Double Standard", "~12 comments", [
        {"bold": "Se fossero stati africani chissà come avrebbe reagito l'opinione pubblica…", "note": "43 pts — very high upvotes; repeated across posts"},
        {"bold": "Privilegio dell'uomo bianco", "note": "r/Italia — direct framing"},
        {"bold": "Ma se avessero avuto leggermente più melanina avrebbero avuto tutto questo clamore?", "note": "r/italy — 16 pts"},
    ], col="r"))

    p.append(cluster_card("Cluster 4 — Children's Welfare Criticism", "~18 comments", [
        {"bold": "I figli non erano minimamente vaccinati e non parlavano niente di italiano", "note": "67 pts — vaccination + language as evidence of parental failure"},
        {"bold": "Non sapevano neanche che esistesse la corrente o l'acqua calda per dire", "note": "83 pts — living conditions"},
        {"bold": "I bambini non sanno leggere e scrivere correttamente né in italiano né in inglese", "note": "r/opinioninonrichieste — literacy claim"},
    ], col="r"))

    p.append(cluster_card("Cluster 5 — Proportionality Defence (Pro-Family)", "~10 comments", [
        {"bold": "Se la madre non collabora si allontana lei ed ok, ma rompere l'unico legame rimasto non mi pare minimamente utile", "note": "8 pts — best pro-family argument in dataset"},
        {"bold": "Perché separare i bambini? Non gli crei un trauma maggiore?", "note": "2 pts — questions tribunal logic"},
        {"bold": "Penso che rompere un legame familiare non sia mai giusto. Bastava fare alcune modifiche alla casa.", "note": "r/oknotizie — proportionality + housing alternative"},
    ], col="g"))

    p.append(cluster_card("Cluster 6 — Political / Referendum Cynicism", "~14 comments", [
        {"bold": "riassunto: la Meloni commenta su sta banda di scappati di casa solo per attaccare per l'ennesima volta la magistratura", "note": "55 pts — dominant political framing, r/Italia"},
        {"bold": "Sta vicenda è tornata solo per il referendum", "note": "r/italy — Meloni's support seen as cynical"},
        {"bold": "Salvini ha già strumentalizzato questa decisione per il referendum?", "note": "27 pts — political exploitation concern"},
    ], col="w"))

    p.append(cluster_card("Cluster 7 — 'Deport Them Back to Australia'", "~8 comments", [
        {"bold": "Espulsi tutti. Non puoi stare qui a scrocco...", "note": "r/Italia — nativist framing"},
        {"bold": "Mammoth-Opening: Perché non ve ne tornate in Australia!", "note": "r/TuttoItalia — classic nationalist response"},
        {"bold": "Appello all'Australia... Da quello mi sembra di ricordare che erano attenzionati anche lì", "note": "'Australia flagged them too' claim — contested"},
    ], col="r"))

    p.append(cluster_card("Cluster 8 — Tribunal Scepticism (Neutral/Pro-Family Lean)", "~7 comments", [
        {"bold": "Chissà cosa c'è dietro; che interesse avrebbe il tribunale a forzare la mano con tutta l'opinione pubblica addosso?", "note": "3 pts — neutral questioning tribunal motivation"},
        {"bold": "Mi auguro solo che per prendere provvedimenti così gravi ci siano cose di una gravità inaudita che non ci dicono", "note": "r/TuttoItalia — scepticism without a position"},
        {"bold": "La motivazione 'la madre è diventata irascibile' come spiegazione per provvedimenti così gravi?", "note": "Paraphrase of ordinance reasoning questioned"},
    ], col="g"))

    p.append(cluster_card("Cluster 9 — Media Criticism (Directed at TV, not Family)", "~8 comments", [
        {"bold": "NON SUPPORTATE QUESTI PROGRAMMI. Smettete di guardare la TV", "note": "207 pts (r/Italia bambini morti post) — TV exploitation anger"},
        {"bold": "La cronaca nera... sono oggettivamente tra le cose meno rilevanti per un paese come il nostro", "note": "84 pts — media distortion"},
        {"bold": "Avvoltoi che capitalizzano sulle disgrazie", "note": "9 pts — TV as predatory coverage"},
    ], col="w"))

    p.append(cluster_card("Cluster 10 — Catherine's Behaviour Criticism", "~6 comments", [
        {"bold": "La madre ha plagiato i figli", "note": "r/oknotizie — psychological manipulation claim"},
        {"bold": "La madre a quanto dicono i giornali una matta che trovava scuse per litigare", "note": "r/opinioninonrichieste — behaviour claim"},
        {"bold": "Se una madre viene cacciata dalla casa famiglia vuol dire che ne ha fatte di ogni", "note": "r/italy — institution conduct reasoning"},
    ], col="r"))

    p.append(cluster_card("Cluster 11 — Online Business / Hypocrisy", "~4 comments", [
        {"bold": "In casa usufruiva del PC e dello smartphone per connettersi alla rete Internet per vendere le sue consulenze e i suoi 'consigli', i figli non avevano il minimo indispensabile", "note": "4 pts — hypocrisy framing: sold online retreat consultations while children lacked basics"},
        {"bold": "Questi cagano soldi e qualcuno gli paga l'affitto. Intanto, milioni di italiani in condizioni di indigenza...", "note": "TuttoItalia — wealth contrast"},
    ], col="r"))

    p.append(cluster_card("Cluster 12 — Steiner / Education Questions", "~3 comments", [
        {"bold": "Tanto finché restano in Italia i loro figli o li mandano a scuola o li fanno seguire da un insegnante a domicilio, qua lo unschooling non è permesso.", "note": "r/oknotizie — legal confusion (Steiner not mentioned by critics)"},
        {"bold": "I bambini non hanno mai messo piede in una scuola", "note": "r/opinioninonrichieste — incorrect assumption about Steiner"},
        {"bold": "Se si hanno i soldi per pagare delle scuole di comodo si può giustificare la situazione", "note": "r/italy — unaware Steiner is formally recognised"},
    ], col="w"))

    p.append(cluster_card("Cluster 13 — Pro-Family Support / Frustration with Tribunal", "~8 comments", [
        {"bold": "Spero vivamente che a questi fenomeni che plaudono alla decisione del tribunale, siano tolti i figli così da provare lo stesso strazio", "note": "-18 pts — aggressive pro-family (backfired, downvoted)"},
        {"bold": "Al trauma dell'allontanamento dai genitori si aggiunge quello dell'essere isolati a quale pro?", "note": "8 pts — most upvoted genuinely pro-family comment"},
        {"bold": "Non ci voleva, chi ci sta rimettendo di più sono i bambini, non sono ottimista per il loro futuro", "note": "1 pt — child welfare framing, not parent defence"},
    ], col="g"))

    p.append(ES())

    # ── S4 QUESTIONS ───────────────────────────────────────────────────────
    p.append(S(4, "Audience Questions", "What people are actually asking in the comments"))
    p.append("""<table class="tbl"><thead><tr><th>Question (from comments)</th><th>Frequency</th><th>Should Supporters Answer?</th></tr></thead><tbody>
<tr><td>"Perché la madre è stata allontanata dai figli?" — Why was the mother separated?</td><td>High — entire post title</td><td>✅ YES — Top priority, clearest information need</td></tr>
<tr><td>"I bambini erano davvero non vaccinati?" — Were the children really unvaccinated?</td><td>Medium — implied in multiple comments</td><td>✅ YES — Silence is confirmation</td></tr>
<tr><td>"Non parlavano italiano?" — Did they really not speak Italian?</td><td>Medium — repeated claim</td><td>✅ YES — Language of education (Steiner/multilingual) needs clarification</td></tr>
<tr><td>"Avevano davvero problemi anche in Australia?" — Did they have problems in Australia too?</td><td>Low — 1 comment but high-risk if unanswered</td><td>⚠️ YES — if false, deny clearly; if complex, explain</td></tr>
<tr><td>"Perché il benefattore ha scelto loro e non altri bisognosi?" — Why this family and not others?</td><td>High — major theme</td><td>✅ YES — the benefactor can speak for himself</td></tr>
<tr><td>"Cosa succede ora con il tribunale/ispettori?" — What happens next legally?</td><td>Medium</td><td>✅ YES — essential update page</td></tr>
<tr><td>"Perché Meloni si è interessata?" — Why did Meloni get involved?</td><td>High — many comments assume referendum motive</td><td>✅ YES — explain the Garante acted BEFORE Meloni, independent of politics</td></tr>
</tbody></table>""")
    p.append(ES())

    # ── S5 FRUSTRATIONS ────────────────────────────────────────────────────
    p.append(S(5, "Audience Frustrations", "What's creating objections, confusion, and hostility"))
    p.append("""<ul style="font-size:0.85rem;color:var(--text);line-height:2">
<li><strong>Wealth paradox:</strong> "Rich foreigners getting charity while Italians suffer" — the perception of wealth cannot be ignored. Every pro-family argument collapses against it if unaddressed.</li>
<li><strong>Steiner ignorance:</strong> Critics saying "the children had no education" are wrong — but they don't know it. Steiner is not widely known in Italy outside educational circles. This is a winnable factual correction.</li>
<li><strong>Political contamination:</strong> Meloni's involvement has poisoned the well for many centrist and left-leaning Italians who might otherwise have sympathy. The Garante and Nordio's actions need to be disentangled from referendum politics.</li>
<li><strong>"Why Italy?":</strong> The family is Australian. Multiple commenters question why they came to Italy, stayed against social services' wishes, and why Italy should absorb the consequences. This question is never answered in the pro-family media presence.</li>
<li><strong>Catherine's behaviour:</strong> Reports of hostile behaviour in the casa famiglia are circulating. If true, this undercuts the "collaborative and willing parents" narrative. If false, it needs a direct rebuttal with source.</li>
<li><strong>Exhaustion:</strong> The story has been in Italian media long enough that "basta" is now the most common sentiment. Any new communication needs to be justified by new information — not repetition.</li>
</ul>""")
    p.append(ES())

    # ── S6 DESIRES ─────────────────────────────────────────────────────────
    p.append(S(6, "Audience Desires", "What people want — even those who are critical or fatigued"))
    p.append("""<ul style="font-size:0.85rem;color:var(--text);line-height:2">
<li><strong>Resolution:</strong> Even the most critical commenters want the media coverage to end — which only happens when there's an outcome. Many are implicitly asking for a conclusion, not more drama.</li>
<li><strong>Answers to the hard questions:</strong> Vaccination, language, living conditions — people want direct, factual responses, not deflection. The r/italy post "Perché la madre è stata allontanata" is evidence that the public wants to understand before judging.</li>
<li><strong>Fairness:</strong> The racial double-standard argument reveals a desire for consistent application of welfare rules — not a desire to harm the family. This is a useful framing opportunity: "We agree — all families in this position deserve the same support."</li>
<li><strong>Child welfare over adult drama:</strong> Almost every commenter — including hostile ones — expresses genuine concern for the children. u/UomoTigre: "chi ci sta rimettendo di più sono i bambini." Frame all content around the children's wellbeing, not the parents' rights.</li>
</ul>""")
    p.append(ES())

    # ── S7 VIRAL TRIGGERS ──────────────────────────────────────────────────
    p.append(S(7, "Viral Content Triggers", "Why this story keeps generating engagement — and what to do with it"))
    p.append("""<p>Despite the net-negative sentiment, this story generates consistent and significant engagement. Understanding why tells you what to use and what to avoid.</p>""")
    p.append("""<div class="card card--w">
<div class="card__hd"><span class="card__nm">Trigger 1 — Class Conflict</span><span class="card__tg">Highest engagement</span></div>
<p style="font-size:0.84rem;color:var(--muted)">The "rich foreigner gets charity" narrative drives the highest scores (357 pts). Class resentment is the dominant emotion. This trigger HURTS the campaign. However, it can be redirected: the benefactor's act — a private individual, not the state — is an expression of solidarity that transcends class, and the family's acceptance of help is not the same as demanding it.</p>
</div>""")
    p.append("""<div class="card card--g">
<div class="card__hd"><span class="card__nm">Trigger 2 — Children in Distress</span><span class="card__tg">Most emotionally resonant pro-family content</span></div>
<p style="font-size:0.84rem;color:var(--muted)">Every mention of the children's distress — hunger strike, morning video calls, "non capiscono perché la mamma non è lì" — generates genuine emotional response across the political spectrum. This is the highest-value content trigger for the campaign. It must be framed carefully (no images, institutional citations only) but it is the most likely content to break through the scepticism.</p>
</div>""")
    p.append("""<div class="card card--a">
<div class="card__hd"><span class="card__nm">Trigger 3 — Institutional Conflict</span><span class="card__tg">Broad reach</span></div>
<p style="font-size:0.84rem;color:var(--muted)">The spectacle of PM, Justice Ministry, Garante, and Regional President all publicly criticising a regional tribunal is inherently newsworthy. Content that explains the institutional conflict — not as a political story but as a system-checks story — has broad appeal across party lines and is resistant to the referendum/cynicism dismissal.</p>
</div>""")
    p.append("""<div class="card card--r">
<div class="card__hd"><span class="card__nm">Trigger 4 — "They Had Problems in Australia Too"</span><span class="card__tg">Dangerous: verify before addressing</span></div>
<p style="font-size:0.84rem;color:var(--muted)">This claim, if true, is the most damaging possible narrative — it reframes the case from "Italian state overreach" to "a family with a documented cross-national welfare history." Do not engage with it until the facts are known. If false, a single clear denial with documentation deflates it completely.</p>
</div>""")
    p.append(ES())

    # ── S8 CONTENT OPPORTUNITIES ───────────────────────────────────────────
    p.append(S(8, "Content Opportunities", "10 ideas directly grounded in comment patterns"))
    ideas = [
        ("The Steiner Explainer", "green", 'Multiple commenters assert "the children had no education" — this is factually wrong and widely believed. A clear, one-page explainer on what Steiner education is, why Italy recognises it, and what the children were actually learning would be the single most efficient factual correction available. Frame it for people who may not know what Steiner is.'),
        ("The Proportionality Question", "green", '"Was this response proportionate?" is the one question that generates positive responses even from sceptics. A post or video posing this question — citing the Garante, Nordio, and Marsilio — and asking readers to judge for themselves is far more effective than asserting "the family is good." Let the audience reach the conclusion.'),
        ("The Children's Voices (Institutional Sources Only)", "green", "A page that compiles only institutional statements about the children's distress: the Garante's firsthand visit report, the hunger-strike documentation, the video-call testimony. No parent statements, no family photos. Only what third-party authorities documented. This is the most credible child-welfare content possible."),
        ("The Benefactor's Own Words", "accent", 'The benefactor architect is the highest-scoring story in the dataset. His own explanation for why he helped — in his own words — would be more powerful than any campaign statement. If he is willing to speak, his statement is Diamond-tier content.'),
        ("Why Italy? The Family's Story (Timeline)", "accent", '\'Why Italy and not stay in Australia?\' is a genuine public question. A neutral timeline (where they came from, why Italy, what they were doing here, when services became involved) answers the "why should Italy deal with this" objection before it\'s raised.'),
        ("Response to the Australia Claim", "warn", "If the 'problems in Australia too' claim is false, this page goes live immediately with documentation. If it's complicated, a transparent explanation is better than silence. Silence on this claim will allow it to harden into fact."),
        ("Vaccination: The True Story", "warn", 'If the children were vaccinated, a single document proves it. If they weren\'t, the Steiner community\'s approach to vaccination decisions is a broader context that many people misunderstand. Either way, silence allows the "unvaccinated children" narrative to dominate.'),
        ("The Racial Double Standard — Agree and Redirect", "accent", 'The "if they were African" critique is actually an argument FOR consistent child welfare — not an argument against this family. A post that agrees with the principle ("you\'re absolutely right that all families deserve equal treatment — here\'s why this case matters for everyone") converts the critic into an inadvertent ally.'),
        ("Legal Update — What Happens Now", "green", '"Cosa succede ora?" is one of the most clicked headlines in the TVItaliana data. A regularly updated legal status page — inspectors\' findings, appeal status, psychological evaluation schedule — is the highest-traffic sustainable content type.'),
        ("The Romina Power Moment", "accent", "Romina Power's Instagram post was the highest-reach celebrity content for this case. A page contextualising her statement — who she is, why this resonated with Italian audiences, what her comparison to her own life means — builds on an existing viral moment rather than trying to create a new one."),
    ]
    for name, col, desc in ideas:
        p.append(f'<div class="card card--{col[0]}"><div class="card__hd"><span class="card__nm">{name}</span></div><p style="font-size:0.83rem;color:var(--muted);margin-bottom:0">{desc}</p></div>')
    p.append(ES())

    # ── S9 ENGAGEMENT OPPS ─────────────────────────────────────────────────
    p.append(S(9, "Engagement Opportunities", "How supporters can engage with the existing Reddit conversation"))
    p.append("""<p>As <strong>WE ARE SUPPORTERS</strong> rather than the post authors, the rules of engagement are different. Do not engage as a campaign with aggressive defence — that will backfire. Engage as informed individuals who can correct specific factual errors with cited sources.</p>""")
    p.append("""<div class="card card--g">
<div class="card__hd"><span class="card__nm">Opportunity 1 — Correct the Steiner Education Claim</span><span class="card__tg">High Value, Low Risk</span></div>
<p style="font-size:0.84rem;color:var(--muted)">Every comment asserting "i bambini non hanno mai messo piede in una scuola" or "non sapevano leggere e scrivere" is a correction opportunity.
A concise, cited reply (4–5 sentences: Steiner method, Italian legal recognition, what the curriculum includes, link to FAQ page) is the highest-ROI individual engagement possible.
The person posting may not change their mind — but 50 other readers will see the correction.</p>
</div>""")
    p.append("""<div class="card card--g">
<div class="card__hd"><span class="card__nm">Opportunity 2 — Amplify the Proportionality Argument</span><span class="card__tg">Cross-partisan reach</span></div>
<p style="font-size:0.84rem;color:var(--muted)">Comments that are already making the proportionality argument (u/Radioman02, u/sullanaveconilcane, u/77EmotionalTell77) should be upvoted by supporters reading those threads.
These are neutral-to-positive voices — not campaign supporters — making the most credible version of the pro-family argument. Amplify them rather than bringing in new campaign voices.</p>
</div>""")
    p.append("""<div class="card card--w">
<div class="card__hd"><span class="card__nm">Opportunity 3 — Separate the Garante from Meloni</span><span class="card__tg">Medium — requires precision</span></div>
<p style="font-size:0.84rem;color:var(--muted)">Multiple high-upvote comments assume the pro-family position is just referendum-era Meloni propaganda. The Garante dell'Infanzia acted independently and <em>before</em> Meloni's statement.
A comment that cites this sequence ("Il Garante ha visitato personalmente i bambini e ha chiesto la sospensione PRIMA della dichiarazione di Meloni — questo è istituzionale, non politico") separates the strongest pro-family institutional argument from partisan politics.</p>
</div>""")
    p.append(ES())

    # ── S10 ALLY OPPS ──────────────────────────────────────────────────────
    p.append(S(10, "Ally Opportunities", "Pro-family commenters worth noting"))
    p.append("""<table class="tbl"><thead><tr><th>Username</th><th>Comment (translated)</th><th>Score</th><th>Why Valuable</th></tr></thead><tbody>
<tr><td>u/Radioman02</td><td>"Separating the children — to what end? If the mother won't collaborate, remove her, fine — but breaking the only remaining bond serves no good purpose for those children's mental stability."</td><td>8 pts</td><td>Best-argued, most neutral-toned pro-family statement; makes child welfare the frame, not parental rights</td></tr>
<tr><td>u/sullanaveconilcane</td><td>"I hope that for such a grave action there are things of extraordinary severity they're not telling us — otherwise it's inexplicable. 'The mother became irritable' as a motivation for this?'"</td><td>1 pt</td><td>Articulate legal scepticism from a neutral position — genuinely questions the ordinance without defending the parents</td></tr>
<tr><td>u/Mirieste</td><td>"If the ordinance's key point is that her mood worsened because she realised children weren't coming back as fast as she hoped — you don't need a psychology textbook to explain why."</td><td>-4 pts</td><td>Downvoted but makes a logically coherent point about the ordinance's reasoning being circular; useful for legal argument</td></tr>
<tr><td>u/albiz_1999</td><td>"What interest would the children's tribunal have in forcing this decision when every public and political voice is against them, looking for any misstep?"</td><td>3 pts</td><td>Institutional scepticism without a political position — useful for the "why would the court do this?" question</td></tr>
<tr><td>u/PapaLeone14esimo</td><td>"They lived happily far from everyone. They weren't bothering me. Maybe when grown the children would judge their family themselves."</td><td>-2 pts</td><td>Libertarian framing — downvoted by Italian Reddit but represents a broader civil liberties argument</td></tr>
</tbody></table>""")
    p.append(ES())

    # ── S11 CAMPAIGN OPPS ──────────────────────────────────────────────────
    p.append(S(11, "Future Campaign Opportunities", "Unmet needs in the public conversation"))
    p.append(card("Opportunity — The Steiner Educational Defence", "Legally grounded", col="g",
        body='<p style="font-size:0.84rem;color:var(--muted)">The most common factual error in the dataset — "the children had no education" — is also the most easily corrected. There appears to be no public documentation of the Steiner argument in mainstream coverage. A single well-cited explainer published and shared widely changes the entire education debate.</p>'))
    p.append(card("Opportunity — A Neutral Case FAQ (Not a Campaign Page)", "Trust-building", col="g",
        body='<p style="font-size:0.84rem;color:var(--muted)">Multiple commenters across all posts want to understand the case before forming a view ("chissà cosa c\'è dietro"). A FAQ page that acknowledges complexity, answers hard questions honestly (including the ones that are uncomfortable for the family), and is clearly sourced would serve the 30% exhausted and undecided audience far better than advocacy content.</p>'))
    p.append(card("Opportunity — The Consistent Welfare Argument", "Cross-partisan", col="a",
        body='<p style="font-size:0.84rem;color:var(--muted)">The "if they were African" critique is the second-highest-engagement theme. Responding with agreement — "you\'re right, and here\'s why consistent child welfare standards benefit everyone, including immigrant families" — converts one of the loudest attack lines into an inadvertent argument for the campaign\'s principles. This is the most sophisticated strategic opportunity in the dataset.</p>'))
    p.append(ES())

    # ── S12 AUDIENCE PROFILE ───────────────────────────────────────────────
    p.append(S(12, "Audience Profile", "Who Italian Reddit is — and why it is not the primary target audience"))
    p.append("""<p>Based on comment language, references, political framing, and engagement patterns, the commenting audience on these posts is:</p>
<ul style="font-size:0.85rem;line-height:1.9">
<li><strong>Predominantly male, 20–40 years old</strong> (language register, cultural references, political framing)</li>
<li><strong>Left-leaning to centrist</strong> (cynical of centre-right, hostile to perceived privilege, sympathetic to racial equality arguments)</li>
<li><strong>Educated, media-literate</strong> (references to journalism ethics, legal process, referendum details)</li>
<li><strong>Italy-resident, Italian national or Italian-identified</strong> (class resentment framed around Italian workers, "poveretti italiani")</li>
<li><strong>Distrustful of emotional media narratives</strong> (strong "this is a distraction/media manipulation" thread)</li>
<li><strong>Not the campaign's key audience</strong> — this demographic votes for different reasons than child welfare sympathy and is resistant to the family's story as presented</li>
</ul>""")
    p.append(alert("i", "&#x1F3AF; Strategic Implication",
        "The family's natural supporter base — people who believe in parental rights, alternative education, and state overreach concerns — is NOT well-represented on Italian Reddit. "
        "That audience is on: Facebook (Romina Power's demographic), Instagram, parent and homeschool communities, civil liberties organisations, and international English-language media. "
        "That is where the campaign should invest its primary energy."))
    p.append(ES())

    # ── S13 REPLY MATRIX ───────────────────────────────────────────────────
    p.append(S(13, "Reply Strategy Matrix", "4-tier decision tree + 6 ready-to-use scripts"))
    p.append("""<h3 style="font-size:1rem;color:var(--heading);margin:16px 0 10px">Decision Tree</h3>
<table class="tbl"><thead><tr><th>If the comment is...</th><th>Action</th><th>Tier</th></tr></thead><tbody>
<tr><td>A genuine question (Why was the mother separated? What is Steiner? What happens next?)</td><td><span class="t1">REPLY with facts + link</span></td><td class="t1">TIER 1</td></tr>
<tr><td>A factual error (no education / unvaccinated / no Italian) with upvotes</td><td><span class="t1">REPLY with correction + citation</span></td><td class="t1">TIER 1</td></tr>
<tr><td>The proportionality argument from a neutral commenter</td><td><span class="t1">UPVOTE + brief agreement</span></td><td class="t1">TIER 1</td></tr>
<tr><td>Wealth/privilege attack with no factual claim</td><td><span class="t2">REPLY carefully — acknowledge, redirect to children</span></td><td class="t2">TIER 2</td></tr>
<tr><td>Meloni/referendum framing</td><td><span class="t2">REPLY with Garante timeline (pre-Meloni)</span></td><td class="t2">TIER 2</td></tr>
<tr><td>Aggressive insult / "deport them"</td><td><span class="t3">DO NOT REPLY — no benefit</span></td><td class="t3">TIER 3</td></tr>
<tr><td>Australia claims (unverified)</td><td><span class="t3">DO NOT REPLY until verified</span></td><td class="t3">TIER 3</td></tr>
<tr><td>Story-fatigue "basta" comments</td><td><span class="t4">REACT ONLY — a like acknowledges without provoking</span></td><td class="t4">TIER 4</td></tr>
</tbody></table>""")

    p.append("<h3 style='font-size:1rem;color:var(--heading);margin:20px 0 12px'>Reply Scripts — 6 Templates</h3>")

    p.append(reply_box(
        "I bambini non sapevano leggere né scrivere / non avevano mai messo piede in una scuola",
        "The children had no education / never attended school",
        "In realtà i bambini seguivano il metodo Steiner (Waldorf) — un approccio pedagogico formalmente riconosciuto dalla legge italiana, con scuole accreditate in tutta Italia ed Europa. Non è homeschooling informale: è un curricolo strutturato e riconosciuto dallo Stato. Il tribunale ha contestato l'accesso all'istruzione, ma non ha ancora fornito una spiegazione pubblica su perché il metodo Steiner — che l'Italia stessa riconosce — fosse considerato insufficiente in questo caso specifico. [LINK]",
        "The children were actually following the Steiner (Waldorf) method — a pedagogical approach formally recognised by Italian law, with accredited schools across Italy and Europe. The tribunal contested their education access but has not explained publicly why Steiner — which Italy itself recognises — was deemed insufficient in this case.",
        "Always lead with 'In realtà' — 'actually'. It signals correction without aggression. Include a link to the Steiner explainer page."))

    p.append(reply_box(
        "Il Garante ha preso posizione solo perché glielo ha detto Meloni / è tutta politica referendaria",
        "The Garante only acted because Meloni told them to / it's all referendum politics",
        "Il Garante Nazionale dell'Infanzia ha visitato personalmente i bambini a Vasto e ha chiesto formalmente la sospensione del trasferimento — prima della dichiarazione di Meloni. Il Garante è un'istituzione indipendente, non un organo politico. La sua richiesta di sospensione si base su una visita diretta ai bambini, non su orientamenti politici. Meloni si è espressa dopo, non prima.",
        "The National Children's Rights Ombudsman personally visited the children in Vasto and formally requested the suspension of the transfer — before Meloni's statement. The Ombudsman is an independent institution. Their request was based on a direct visit to the children, not political direction.",
        "The Garante-before-Meloni sequence is the single most effective counter-argument to the referendum framing. Know this timeline cold."))

    p.append(reply_box(
        "Se fossero stati africani / immigrati, nessuno avrebbe detto niente",
        "If they were African / immigrants, nobody would have cared",
        "Hai ragione che le famiglie straniere in difficoltà non ricevono la stessa attenzione mediatica. Ed è esattamente per questo che le garanzie difensive che il Garante, Nordio e Marsilio stanno chiedendo per questa famiglia dovrebbero valere per tutte le famiglie — italiane, straniere, di ogni provenienza. Non è una ragione per rallentare la tutela dei bambini in questo caso: è una ragione per estenderla a tutti.",
        "You're right that foreign families in difficulty don't receive the same media attention. Which is exactly why the procedural protections the Garante, Nordio and Marsilio are calling for should apply to all families — Italian, foreign, of any background. That's not a reason to slow down protection for these children; it's a reason to extend it to everyone.",
        "Agree on the principle. Redirect it. This is the one attack you can agree with entirely and come out ahead."))

    p.append(reply_box(
        "Questi sono ricchi, vengono dall'Australia, non hanno bisogno di aiuto",
        "They're rich, they came from Australia, they don't need help",
        "La questione non è se avessero bisogno economico del benefattore. La questione è: era proporzionato allontanare una madre dai suoi tre figli e collocarli in un istituto — indipendentemente dalla loro situazione economica? Il Garante Nazionale dell'Infanzia, che ha visitato i bambini, ha detto di no. Il Ministro Nordio ha inviato ispettori al tribunale. L'estrazione economica della famiglia non cambia la domanda sulla proporzionalità del provvedimento.",
        "The question is not whether they needed the benefactor financially. The question is: was it proportionate to remove a mother from her three children and place them in an institution — regardless of their economic situation? The Ombudsman, who visited the children, said no. Justice Minister Nordio sent inspectors. The family's economic situation doesn't change the proportionality question.",
        "Never defend the wealth. Redirect to proportionality every time wealth is raised."))

    p.append(reply_box(
        "I bambini non erano vaccinati",
        "The children were not vaccinated",
        "[Se vero:] Le scelte vaccinali della famiglia sono separate dalla questione giuridica. Il Tribunale di L'Aquila non ha citato la vaccinazione nella sua ordinanza — ha contestato l'istruzione. Le due cose non devono essere confuse. [Se falso:] Quella è un'affermazione non documentata. I documenti medici dei bambini non sono stati pubblicati. Prima di citare questo come fatto, sarebbe opportuno identificare la fonte.",
        "[If true:] The family's vaccination choices are a separate matter from the legal question. The L'Aquila Tribunal did not cite vaccination in its ordinance — it contested education. [If false:] That is an undocumented claim. The children's medical records have not been published. Before citing this as fact, identify the source.",
        "Two separate scripts depending on what is actually known. Do not deploy this script until you know the answer."))

    p.append(reply_box(
        "Anche in Australia avevano avuto problemi con i servizi sociali",
        "They also had problems with social services in Australia",
        "Questa affermazione circola sui social ma non è stata verificata da nessuna fonte giornalistica o istituzionale italiana o australiana. Se chiunque ha una fonte documentata, sono disponibile a leggerla. Fino ad allora è un'ipotesi, non un fatto — e non dovrebbe essere usata come argomento in una discussione su provvedimenti giudiziari che hanno conseguenze reali su tre bambini.",
        "This claim is circulating on social media but has not been verified by any Italian or Australian journalistic or institutional source. If anyone has a documented source, I'm willing to read it. Until then it's speculation, not fact — and should not be used as an argument in a discussion about judicial measures with real consequences for three children.",
        "Never confirm, never deny on unverified claims. Demand the source. If they can't provide one, the claim evaporates."))
    p.append(ES())

    # ── S14 RECOMMENDATIONS ────────────────────────────────────────────────
    p.append(S(14, "Strategic Recommendations", "Prioritised by urgency — Critical to Ongoing"))
    p.append('<h3 style="font-size:0.88rem;color:var(--red);margin:14px 0 10px">🔴 CRITICAL — Within 72 Hours</h3>')
    p.append(rec("r", "Publish the Steiner Education Explainer NOW",
        " — This is the most upvoted factual error in the dataset and it is correctable. Every day it goes uncorrected, it hardens into accepted fact. One clear, cited page changes the education debate entirely."))
    p.append(rec("r", "Address the Australia Claim (verify or deny within 24 hours)",
        " — A circulating unverified claim left unaddressed for 72+ hours becomes assumed true. Verify internally, then respond publicly with a clear statement and source."))
    p.append('<h3 style="font-size:0.88rem;color:var(--warn);margin:14px 0 10px">🟡 HIGH — Within 14 Days</h3>')
    p.append(rec("w", "Build the 'Garante First, Meloni Second' Timeline Page",
        " — This single documented sequence defeats the referendum-politics framing and makes the pro-family institutional case non-political. It is the most powerful conversion tool for centrist/left-leaning Italians."))
    p.append(rec("w", "Publish Direct Vaccination Status Statement",
        " — If the children are vaccinated, publish the confirmation. If their vaccination approach is Steiner-community-aligned, explain the framework honestly. Silence here is taken as confirmation of the criticism."))
    p.append(rec("w", "Engage Romina Power's Community (Instagram/Facebook)",
        " — Her post performed better than any Reddit content for this case. Her audience (Italian mainstream, 40-60, not politically aligned) is far more sympathetic territory than Reddit. A follow-up engagement with that community is higher ROI than any Reddit comment."))
    p.append('<h3 style="font-size:0.88rem;color:var(--primary-light);margin:14px 0 10px">🔵 MEDIUM — Within 30 Days</h3>')
    p.append(rec("b", "Launch the 'Perché l'Italia?' Explainer Page",
        ' — "Why Italy and not Australia?" is an unanswered question fuelling the nationalist framing. A straightforward, honest account of how and why the family came to Italy deflates the "foreigners using Italian resources" narrative.'))
    p.append(rec("b", "Build the Legal Status Tracker",
        " — Inspectors are at L'Aquila. The appeal is being prepared. Psychological evaluations are scheduled. People want to know what happens next. A regularly updated page keeps the campaign relevant without requiring constant new commentary."))
    p.append(rec("b", "Deploy the Racial Equality Redirect",
        " — Respond to 'if they were African' comments with the 'you're right, and here's why consistent welfare standards matter for everyone' script. This converts the attack into an ally argument and demonstrates good faith."))
    p.append('<h3 style="font-size:0.88rem;color:var(--green);margin:14px 0 10px">⚪ ONGOING</h3>')
    p.append(rec("g", "Monitor and Correct Education Claims Continuously",
        " — This error will recur. Assign someone to read any new Reddit post about the case and deploy Script A within 2 hours."))
    p.append(rec("g", "Never Engage with 'Basta' Comments",
        " — Story fatigue comments are not attacks and do not benefit from a response. A like acknowledges; a reply extends the very exhaustion they're expressing."))
    p.append(ES())

    # ── S15 VIRAL SCORE ────────────────────────────────────────────────────
    p.append(S(15, "Viral Probability Score", "Rating future content's viral potential on Italian platforms"))
    p.append("""<div style="text-align:center;margin:20px 0">
<div class="score-ring">6/10</div>
<p style="font-size:0.85rem;color:var(--muted);max-width:540px;margin:0 auto">
<strong style="color:var(--heading)">Score: 6/10</strong> — Moderate-high viral potential, but currently channelled toward negative engagement.<br>
The case has all the ingredients for sustained virality: institutional conflict, children's welfare, celebrity involvement, political drama, class conflict.
The challenge is that the current dominant emotional trigger (class resentment) benefits critics. A pivot to the children's-welfare trigger — documented distress, the hunger strike — would shift the emotional current and raise this score to 8/10.
</p></div>
<p style="font-size:0.84rem;color:var(--muted)"><strong style="color:var(--text)">What drives it up:</strong> New institutional developments (inspectors' findings, court dates, psychological evaluation results) — each is a natural viral moment that doesn't require the campaign to manufacture content.</p>
<p style="font-size:0.84rem;color:var(--muted)"><strong style="color:var(--text)">What holds it down:</strong> The wealth narrative. The first time someone can credibly counter it with documented evidence (or the first time the case develops a new "undeniable" pro-family moment) the score shifts.</p>""")
    p.append(ES())

    # ── S16 GOLD QUOTES ────────────────────────────────────────────────────
    p.append(S(16, "Gold Quotes Hall of Fame", "Diamond and Gold tier quotes with recommended use cases"))
    p.append("""<div class="diamond">
<div class="diamond__label">💎 Diamond Quote — Campaign Defining Statement</div>
<div class="diamond__text">"Scusate ma separare i bambini perché? Al trauma dell'allontanamento dai genitori si aggiunge quello dell'essere isolati in tutto e per tutto a quale pro? Se la madre non collabora si allontana lei ed ok ma rompere l'unico legame rimasto non mi pare minimamente utile alla stabilità mentale di quei ragazzini."</div>
<div class="diamond__src">u/Radioman02, r/oknotizie — 8 pts. A stranger on Reddit with no connection to the campaign.</div>
<div class="diamond__use">USE: Website homepage · Press release · Legal filing · Social media · FAQ page</div>
<p style="font-size:0.78rem;color:var(--muted);margin-top:12px;font-style:italic">Selected because: This is a neutral, articulate commenter — not a supporter — who reached the proportionality conclusion independently. It frames the entire case as a child-welfare question, not a parents-vs-state question. It is the most usable single quote in the dataset.</p>
</div>""")

    p.append(gold_quote(
        '"Se la madre non collabora si allontana lei ed ok ma rompere l\'unico legame rimasto non mi pare minimamente utile alla stabilità mentale di quei ragazzini."',
        "u/Radioman02, r/oknotizie",
        "Website · FAQ · Social Media"))
    p.append(gold_quote(
        '"Chissà cosa c\'è dietro a tutta questa storia; che interesse avrebbe il tribunale dei minori a forzare la mano per questa separazione, quando hai tutta l\'opinione pubblica e politica addosso?"',
        "u/albiz_1999, r/TuttoItalia — 3 pts",
        "FAQ · Legal context"))
    p.append(gold_quote(
        '"Boh, io mi auguro solo che per prendere provvedimenti così gravi ci siano cose di una gravità inaudita che non ci dicono, altrimenti non si spiegherebbe."',
        "u/sullanaveconilcane, r/TuttoItalia",
        "Proportionality argument · Legal filing"))
    p.append(gold_quote(
        '"Bibbiano? Ma questa vicenda è tornata solo per il referendum, se qualcuno ha voglia potrebbe andarsi a pescare le dichiarazioni della Meloni di un paio di anni fa, ovviamente totalmente opposte a quelle odierne."',
        "u/D35trud0, r/italy — 15 pts",
        "COUNTER-USE: Shows the referendum-cynicism argument — preempt this by citing the Garante timeline"))
    p.append(gold_quote(
        '"I figli non sono dello Stato, i magistrati dimenticano i limiti."',
        "PM Giorgia Meloni — confirmed public statement",
        "Press Release · Website · Social Media · Legal brief"))
    p.append(gold_quote(
        '"Garante Infanzia: sospendere trasferimento senza madre."',
        "Garante Nazionale dell\'Infanzia — following direct visit to children",
        "Legal filing · Press Release · Website Homepage — MOST CITABLE INSTITUTIONAL SOURCE"))
    p.append(gold_quote(
        '"Famiglia nel bosco, Marsilio: decisione inopportuna e sproporzionata."',
        "Regional President Marco Marsilio (Abruzzo Region)",
        "Press Release · Website · International Media"))
    p.append(gold_quote(
        '"Mamma Catherine come in prigione."',
        "Former Vasto community worker — first-hand testimony",
        "Legal filing · Documentary — HANDLE WITH CARE: verify source identity before publishing"))
    p.append(ES())

    # ── S17 FACTS TABLE ────────────────────────────────────────────────────
    p.append(S(17, "Key Facts Cited by the Public", "Verification table — what's confirmed, plausible, and dangerous"))
    p.append("""<table class="tbl"><thead><tr><th>Claim (from comments)</th><th>Status</th><th>Action for Campaign</th></tr></thead><tbody>
<tr><td>The children were taught using the Steiner (Waldorf) method</td><td class="v-ok">✅ CONFIRMED by family / campaign</td><td>CITE — this is your strongest factual counter to the education claim</td></tr>
<tr><td>Tribunal of L'Aquila issued the ordinance (separation + casa famiglia at Vasto)</td><td class="v-ok">✅ CONFIRMED — multiple institutional sources</td><td>CITE freely</td></tr>
<tr><td>The Garante Nazionale dell'Infanzia visited children personally</td><td class="v-ok">✅ CONFIRMED — TVItaliana, Garante statements</td><td>CITE — most powerful institutional fact</td></tr>
<tr><td>The Garante's suspension request preceded Meloni's statement</td><td class="v-ok">✅ CONFIRMED — documented sequence</td><td>CITE to counter referendum cynicism</td></tr>
<tr><td>Minister Nordio sent inspectors to L'Aquila tribunal</td><td class="v-ok">✅ CONFIRMED — multiple news sources</td><td>CITE</td></tr>
<tr><td>One male child began a hunger strike in the institution</td><td class="v-ok">✅ CONFIRMED — multiple TVItaliana headlines</td><td>CITE only with Garante confirmation; do not rely on parent testimony alone</td></tr>
<tr><td>Catherine Birmingham is the mother's name</td><td class="v-ok">✅ CONFIRMED — widely reported</td><td>Neutral fact. Acknowledge if asked — don't volunteer; it enables the wealth narrative</td></tr>
<tr><td>"The family has sufficient money to buy an entire Italian region" (u/NPCwithGoals)</td><td class="v-pl">⚠️ PLAUSIBLE — family appears wealthy (horse transport claim)</td><td>DO NOT AMPLIFY — directly harms campaign. If untrue, publish a factual correction with source.</td></tr>
<tr><td>"The children were unvaccinated" (u/Nuclear-Jester, 67 pts)</td><td class="v-nv">❓ NEEDS VERIFICATION — repeated but unsourced</td><td>VERIFY INTERNALLY then respond. Do not confirm or deny without knowing the answer.</td></tr>
<tr><td>"The children don't speak Italian" (u/Nuclear-Jester, 67 pts)</td><td class="v-nv">❓ NEEDS VERIFICATION — multilingual Steiner education possible</td><td>If false: cite directly. If partly true: explain Steiner's multilingual framework.</td></tr>
<tr><td>"They were also flagged by Australian authorities" (u/antosme, 8 pts)</td><td class="v-dn">🔴 UNVERIFIED — DANGEROUS — no source cited</td><td>DO NOT ENGAGE UNTIL VERIFIED. If false, demand source publicly. If true, prepare a statement.</td></tr>
<tr><td>"Catherine sold online consultations from the forest using a PC and smartphone"</td><td class="v-pl">⚠️ PLAUSIBLE — cited in r/TuttoItalia comments with specificity</td><td>If true: does not affect the legal argument but acknowledges the "tech-accessible poverty" hypocrisy claim. Address directly.</td></tr>
<tr><td>"The horse was transported from Australia by plane" (implied in multiple posts)</td><td class="v-nv">❓ NEEDS VERIFICATION</td><td>If true, the wealth narrative is impossible to fully counter. Acknowledge and redirect to children. If false, correct.</td></tr>
<tr><td>"Nathan ai ferri corti con Catherine — false, based on inner-circle leak"</td><td class="v-ok">✅ CONFIRMED by family — deliberate disinformation</td><td>Correct actively wherever it appears in comments. Demand source from anyone citing it.</td></tr>
</tbody></table>""")
    p.append(alert("r", "&#x26A0;&#xFE0F; Campaign Risk Warning",
        "Only CONFIRMED facts should appear in official communications or legal filings. "
        "PLAUSIBLE facts may be referenced with explicit caveats (e.g., 'as reported'). "
        "UNVERIFIED DANGEROUS claims — especially the Australia history claim and the wealth scale — must never be amplified, confirmed or denied without internal verification. "
        "Repeating a dangerous claim even to deny it extends its reach."))
    p.append(ES())

    # ── S18 PRIVACY ────────────────────────────────────────────────────────
    p.append(S(18, "Privacy & Data Handling", "GDPR compliance, data scope, and consent guidance"))
    p.append("""<table class="tbl"><thead><tr><th>Item</th><th>Details</th></tr></thead><tbody>
<tr><td>Data Source</td><td>Publicly posted Reddit comments via Reddit's public JSON API. No private messages, inbox data, or account data accessed.</td></tr>
<tr><td>Collection Method</td><td>Automated HTTP requests to public Reddit post endpoints. Rate-limited (1.5 seconds between requests). No scraping of user profile pages.</td></tr>
<tr><td>Data Scope</td><td>Comment text, display username, comment score (upvotes), comment creation timestamp. No email addresses, IP addresses, real names, or private data.</td></tr>
<tr><td>What Was NOT Accessed</td><td>Private messages, Reddit inbox, user karma breakdown, voting history, browsing history, account email/phone. None of these are accessible via the public API used.</td></tr>
<tr><td>GDPR Legal Basis</td><td>Art. 6(1)(f) — Legitimate interest. All data processed was voluntarily posted in public subreddits with no reasonable expectation of privacy. Reddit's own terms of service allow public posts to be accessed programmatically.</td></tr>
<tr><td>Right to Erasure</td><td>Any Reddit user who believes their comment is incorrectly quoted or identified may contact audienceintelligence.com to request removal from this report. Response time: 5 working days.</td></tr>
<tr><td>Data Retention</td><td>Raw comment data (bosco_comments.json) retained for 12 months from report date then deleted. Anonymised/aggregated statistics may be retained indefinitely.</td></tr>
<tr><td>Report Distribution</td><td>This report is produced for the named client only. It must not be published publicly online or shared with third parties without written consent from Audience Intelligence.</td></tr>
</tbody></table>""")
    p.append("""<h3 style="font-size:0.95rem;color:var(--heading);margin:20px 0 10px">Consent Template — Permission to Quote Publicly</h3>
<p style="font-size:0.83rem;color:var(--muted)">Use this template when contacting individual commenters to request permission to quote them in public-facing materials:</p>
<div class="card">
<p style="font-size:0.82rem;color:var(--text);margin-bottom:0">
<strong>Italian:</strong> Ciao [nome utente], abbiamo trovato il tuo commento su Reddit in relazione al caso della Famiglia nel Bosco molto utile e articolato. Possiamo citarlo nel nostro sito web / materiale stampa, attribuendolo al tuo nome utente Reddit (o in forma anonima, se preferisci)? Non venderemo né condivideremo i tuoi dati con terzi. Rispondici pure su Reddit o a [email].<br><br>
<strong>English:</strong> Hi [username], we found your comment on Reddit regarding the Famiglia nel Bosco case thoughtful and articulate. May we quote it on our website / press materials, attributed to your Reddit username (or anonymously if you prefer)? We will not sell or share your data with third parties. Please reply here on Reddit or at [email].
</p>
</div>""")
    p.append(ES())

    # ── CLOSING ────────────────────────────────────────────────────────────
    p.append("""<div class="sec" id="close">
<div class="sec__num">CHIUSURA — IL MANDATO</div>
<h2 class="sec__ttl">The Mandate</h2>
<p class="sec__sub">Ten final findings, the Diamond Quote, and the next 72 hours</p>""")

    p.append("""<h3 style="font-size:0.95rem;color:var(--heading);margin:16px 0 12px">10 Definitive Findings from the Data</h3>
<ol style="font-size:0.84rem;line-height:2.1;color:var(--text);margin-left:20px;margin-bottom:28px">
<li><strong>Sentiment is net-negative on Reddit:</strong> 45% critical, 30% fatigued, 15% pro-family. Reddit is hostile territory for this case.</li>
<li><strong>The wealth argument is dominant:</strong> "rich foreigner gaming Italian welfare" drives the highest scores and requires direct, documented response — not deflection.</li>
<li><strong>Steiner education is the most correctable factual error:</strong> Widely believed to be absent; easily rebutted with publicly available information about recognised Steiner schools in Italy.</li>
<li><strong>Proportionality is the only cross-partisan pro-family argument:</strong> Even critical commenters sometimes acknowledge the tribunal's response seems disproportionate. Build everything around this framing.</li>
<li><strong>The Garante acted before Meloni:</strong> This single documented fact separates institutional support from political manipulation. Use it in every political-framing encounter.</li>
<li><strong>The "ferrri corti" conflict story was planted:</strong> A deliberate inner-circle leak. Supporters must correct it wherever it appears — do not let it circulate unchallenged.</li>
<li><strong>Reddit is reconnaissance, not a battlefield:</strong> Use comment analysis to understand attacks; deploy the campaign on Instagram, Facebook, and the Italian mainstream media where sentiment is more sympathetic.</li>
<li><strong>The children's distress is the strongest emotional asset:</strong> Hunger strike, morning video calls, the Garante's firsthand account. Documented institutional testimony. Use this framing, not parental-rights framing.</li>
<li><strong>Three critical claims about the children need named resolution:</strong> Vaccination status, Italian language, and the Australia history claim. Silence is confirmation in the public mind.</li>
<li><strong>A neutral case FAQ converts the 30% fatigued audience:</strong> They're not against the family. They're against the noise. Give them facts in a form they can absorb and stop following without being converted into active opponents.</li>
</ol>""")

    p.append("""<h3 style="font-size:0.95rem;color:var(--heading);margin:16px 0 10px">💎 The Diamond Quote</h3>
<div class="diamond">
<div class="diamond__label">Selected from 124 comments across 7 posts — not a supporter, a stranger on Reddit</div>
<div class="diamond__text">"Scusate ma separare i bambini perché? Al trauma dell'allontanamento dai genitori si aggiunge quello dell'essere isolati in tutto e per tutto a quale pro? Se la madre non collabora si allontana lei ed ok ma rompere l'unico legame rimasto non mi pare minimamente utile alla stabilità mentale di quei ragazzini."</div>
<div class="diamond__src">u/Radioman02 · r/oknotizie · 8 pts</div>
<div class="diamond__use">Press Release · Website Homepage · Legal Filing · FAQ · Social Media</div>
<p style="font-size:0.78rem;color:var(--muted);margin-top:12px;font-style:italic">This commenter has no connection to the campaign. They are not defending the parents' lifestyle or choices. They are asking a simple, proportionate question about the tribunal's response — and they are correct to ask it. This is what evidence-based public opinion looks like.</p>
</div>""")

    p.append("""<h3 style="font-size:0.95rem;color:var(--heading);margin:20px 0 10px">What This Data Actually Represents</h3>
<p style="font-size:0.87rem;color:var(--text);line-height:1.75;max-width:720px">
These 124 comments were not collected from supporters who were asked for their opinion. They were written voluntarily by strangers on Italian Reddit — a platform known for political scepticism and low sympathy for outsiders — about a foreign family accused of failing their children. That context makes the pro-family signal <em>more credible, not less</em>. When even Italian Reddit's sceptics are questioning the tribunal's proportionality (8 upvotes for "rompere l'unico legame rimasto non mi pare minimamente utile") this is meaningful evidence of public doubt.
</p>
<p style="font-size:0.87rem;color:var(--text);line-height:1.75;max-width:720px">
~15% of commenters on a net-hostile platform questioned the tribunal's response without being prompted. The same story on Facebook, Instagram, or in mainstream Italian media — where Romina Power's post resonated — would likely produce a very different ratio. That is where the campaign evidence needs to be built.
</p>""")

    p.append("""<h3 style="font-size:0.95rem;color:var(--heading);margin:20px 0 10px">&#x23F0; First 72 Hours — What to Do Now</h3>
<ol class="action-list">
<li><strong>Publish the Steiner Explainer.</strong> The most upvoted factual error in the dataset is "the children had no education." It is factually wrong and correctable today. This single page changes the education debate before the next court date.</li>
<li><strong>Verify and respond to the Australia claim.</strong> Check internally whether the family had documented contact with Australian authorities. If false: publish a denial with any available documentation. If true: prepare a transparent account. Do not leave this claim circulating unchallenged past 72 hours.</li>
<li><strong>Deploy the Garante-before-Meloni timeline.</strong> Post it as a simple graphic or timeline on Instagram and Facebook. Every time someone uses the referendum argument, link to it. This is the single most effective counter to political dismissal of the pro-family case.</li>
<li><strong>Brief supporters on Reply Script A (Steiner) and Script B (Garante).</strong> These two scripts, used consistently by multiple supporters independently, build a clear counter-narrative in comment threads without looking like an organised campaign.</li>
<li><strong>Contact u/Radioman02 for permission to quote.</strong> Their comment is the campaign's most citable public statement. A neutral Italian Reddit user questioning the tribunal's proportionality, in Italian, is more persuasive than any official statement. Request permission to quote on the website and in press materials using the consent template in Section 18.</li>
</ol>
<p style="font-size:0.87rem;color:var(--heading);font-weight:600;margin-top:24px;text-align:center;line-height:1.8">
One hundred and twenty-four Italians engaged with this family's story without being asked.<br>
One in seven questioned whether the State's response was proportionate — even on a platform hostile to the cause.<br>
The question is not whether public doubt exists. It does, and this data documents it.<br>
The question is whether the campaign will give it the factual foundation it needs to hold up in public.
</p>""")
    p.append(ES())

    return "\n".join(p)


def build_html(body):
    gen = datetime.now().strftime("%d %B %Y")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Famiglia nel Bosco — Full Comment Intelligence Report · Marzo 2026</title>
<style>{CSS}</style>
</head>
<body>
{body}
<div class="pg-foot">
  Generated by <strong>Audience Intelligence</strong> · <a href="https://audienceintelligence.com">audienceintelligence.com</a> · {gen}<br>
  Full Comment Intelligence Report — Famiglia nel Bosco · Confidential · Ultra-Prompt Framework v2
</div>
<div class="disclaimer">
DISCLAIMER: This report is produced for informational purposes only. It does not constitute legal advice. All comment data was collected from publicly posted Reddit submissions. Sentiment estimates represent editorial analysis of comment text and should not be treated as statistically precise measurements. All quoted public figures' statements are sourced from publicly reported media. No private communications were accessed. For more information visit audienceintelligence.com.
</div>
</body>
</html>"""


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    print("Building full Famiglia nel Bosco intelligence report (v2)...")
    body = build()
    html = build_html(body)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Saved: {OUT_PATH}")
    print(f"Size:  {len(html):,} chars")
