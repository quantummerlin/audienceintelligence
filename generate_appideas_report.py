"""
generate_appideas_report.py
===========================
Audience Intelligence Report — r/AppIdeas Traffic-Driver Edition
Built from 525 Reddit posts across 6 datasets.
Goal: surface the easiest, quickest web apps to build that will drive traffic.

Usage:
    python generate_appideas_report.py
    python generate_appideas_report.py --out outputs/appideas_traffic.html
"""
import json, os, argparse
from datetime import datetime

def _args():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=None)
    return p.parse_args()

ARGS = _args()
OUT_PATH = ARGS.out or os.path.join("outputs", "report_appideas_traffic_2026-03-16.html")

# ── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root{
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
.cover{display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:100vh;text-align:center;padding:60px 40px;background:linear-gradient(160deg,#0b0f1e 0%,#111827 40%,#0f1a35 100%);position:relative;overflow:hidden}
.cover::before{content:'';position:absolute;top:-40%;left:-20%;width:140%;height:140%;background:radial-gradient(ellipse at 30% 50%,rgba(99,102,241,0.1),transparent 55%),radial-gradient(ellipse at 70% 60%,rgba(34,211,238,0.07),transparent 50%);pointer-events:none}
.badge{display:inline-block;background:linear-gradient(135deg,#6366f1,#818cf8);color:#fff;font-size:0.68rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:5px 14px;border-radius:20px;margin-bottom:28px;position:relative;z-index:1}
.cover h1{font-size:2.4rem;font-weight:800;color:var(--heading);margin-bottom:14px;position:relative;z-index:1;line-height:1.2}
.cover h1 span{color:var(--accent)}
.cover__sub{font-size:0.95rem;color:var(--muted);max-width:620px;margin-bottom:36px;position:relative;z-index:1}
.cover__meta{display:flex;gap:36px;flex-wrap:wrap;justify-content:center;position:relative;z-index:1;margin-bottom:36px}
.meta-val{font-size:1.9rem;font-weight:800;color:var(--heading);display:block;line-height:1}
.meta-lbl{font-size:0.7rem;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;margin-top:4px}
.cover__goal{background:rgba(34,211,238,0.08);border:1px solid rgba(34,211,238,0.25);border-radius:12px;padding:14px 22px;font-size:0.82rem;color:var(--accent);max-width:580px;position:relative;z-index:1;margin-bottom:20px}
.cover__client{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:14px 22px;font-size:0.8rem;color:var(--muted);position:relative;z-index:1}
.cover__client strong{color:var(--text)}
.cover__foot{margin-top:28px;font-size:0.7rem;color:rgba(148,163,184,0.4);position:relative;z-index:1}

/* Layout */
main{max-width:960px;margin:0 auto;padding:48px 32px}
.sec{margin-bottom:52px;padding-bottom:38px;border-bottom:1px solid rgba(255,255,255,0.07)}
.sec:last-child{border-bottom:none}
.sec__num{font-size:0.66rem;color:var(--primary-light);font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:5px}
.sec__ttl{font-size:1.35rem;font-weight:700;color:var(--heading);margin-bottom:5px}
.sec__sub{font-size:0.87rem;color:var(--muted);margin-bottom:18px}

/* Stat grid */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:12px;margin:14px 0 22px}
.stat{background:var(--card);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:16px 12px;text-align:center}
.stat-v{font-size:1.9rem;font-weight:800;color:var(--heading);display:block;line-height:1}
.stat-l{font-size:0.68rem;color:var(--muted);margin-top:5px;text-transform:uppercase;letter-spacing:.06em}
.stat--g .stat-v{color:var(--green)}
.stat--r .stat-v{color:var(--red)}
.stat--w .stat-v{color:var(--warn)}
.stat--a .stat-v{color:var(--accent)}
.stat--p .stat-v{color:var(--primary-light)}

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
.alert--a{background:rgba(34,211,238,.06);border:1px solid rgba(34,211,238,.2)}
.alert--a .alert__t{color:var(--accent)}

/* App idea cards */
.idea-card{background:var(--card);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:20px 22px;margin-bottom:16px;position:relative;overflow:hidden}
.idea-card::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%}
.idea-card--s1::before{background:var(--green)}
.idea-card--s2::before{background:var(--accent)}
.idea-card--s3::before{background:var(--warn)}
.idea-card--s4::before{background:var(--red)}
.idea-header{display:flex;align-items:flex-start;gap:12px;margin-bottom:10px;flex-wrap:wrap}
.idea-num{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.9rem;font-weight:800;flex-shrink:0}
.idea-num--s1{background:rgba(52,211,153,.15);color:var(--green)}
.idea-num--s2{background:rgba(34,211,238,.12);color:var(--accent)}
.idea-num--s3{background:rgba(251,191,36,.12);color:var(--warn)}
.idea-num--s4{background:rgba(248,113,113,.12);color:var(--red)}
.idea-title{font-size:1.05rem;font-weight:700;color:var(--heading);line-height:1.3;flex:1}
.idea-meta{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.tag{display:inline-block;font-size:0.68rem;font-weight:600;letter-spacing:.05em;padding:3px 10px;border-radius:12px}
.tag--g{background:rgba(52,211,153,.12);color:var(--green)}
.tag--a{background:rgba(34,211,238,.1);color:var(--accent)}
.tag--w{background:rgba(251,191,36,.1);color:var(--warn)}
.tag--p{background:rgba(99,102,241,.12);color:var(--primary-light)}
.tag--r{background:rgba(248,113,113,.1);color:var(--red)}
.tag--m{background:rgba(255,255,255,.06);color:var(--muted)}
.idea-desc{font-size:0.85rem;color:var(--text);line-height:1.65;margin-bottom:10px}
.idea-desc strong{color:var(--heading)}
.idea-proof{font-size:0.78rem;color:var(--muted);border-top:1px solid rgba(255,255,255,.06);padding-top:9px;margin-top:6px}
.idea-proof strong{color:var(--accent);font-size:0.75rem;letter-spacing:.04em;text-transform:uppercase}
.idea-build{background:rgba(99,102,241,.06);border:1px solid rgba(99,102,241,.12);border-radius:8px;padding:9px 12px;margin-top:10px;font-size:0.79rem;color:var(--primary-light)}
.idea-build strong{color:var(--heading)}
.traffic-score{display:inline-flex;align-items:center;gap:6px;background:rgba(52,211,153,.1);border:1px solid rgba(52,211,153,.2);border-radius:20px;padding:4px 12px;font-size:0.73rem;color:var(--green);font-weight:700}
.bars{display:flex;gap:3px;align-items:center}
.bar{width:6px;height:16px;border-radius:3px;background:var(--border)}
.bar.on{background:var(--green)}

/* Tables */
.tbl{width:100%;border-collapse:collapse;font-size:0.79rem;margin:12px 0}
.tbl th{background:rgba(99,102,241,.1);color:var(--primary-light);font-weight:600;padding:9px 11px;text-align:left;border-bottom:1px solid rgba(255,255,255,.07)}
.tbl td{padding:8px 11px;border-bottom:1px solid rgba(255,255,255,.07);color:var(--text);vertical-align:top}
.tbl tr:hover td{background:rgba(255,255,255,.02)}

/* Quotes */
.quote{background:rgba(99,102,241,.07);border-left:3px solid var(--primary);border-radius:0 8px 8px 0;padding:10px 14px;margin:8px 0;font-size:0.83rem;font-style:italic;line-height:1.55}
.quote--g{border-left-color:var(--green);background:rgba(52,211,153,.06)}
.quote--a{border-left-color:var(--accent);background:rgba(34,211,238,.05)}
.quote--w{border-left-color:var(--warn);background:rgba(251,191,36,.06)}
.quote__src{font-style:normal;font-size:0.72rem;color:var(--muted);display:block;margin-top:5px}

/* Diamond/Gold quotes */
.diamond{background:linear-gradient(135deg,rgba(99,102,241,.1),rgba(34,211,238,.07));border:1px solid rgba(99,102,241,.3);border-radius:16px;padding:28px 32px;margin:20px 0;text-align:center}
.diamond__label{font-size:0.68rem;color:var(--primary-light);font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:12px}
.diamond__text{font-size:1.05rem;font-style:italic;color:var(--heading);line-height:1.7;margin-bottom:12px}
.diamond__src{font-size:0.78rem;color:var(--muted)}
.diamond__use{font-size:0.72rem;color:var(--green);margin-top:8px;font-weight:600}
.gold-q{background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:14px 18px;margin-bottom:10px;border-left:3px solid #fbbf24}
.gold-q__text{font-size:0.85rem;font-style:italic;color:var(--text);line-height:1.6;margin-bottom:6px}
.gold-q__src{font-size:0.73rem;color:var(--muted)}
.gold-q__use{font-size:0.7rem;color:var(--warn);font-weight:600;margin-top:5px}

/* Recs */
.rec{display:flex;gap:12px;margin-bottom:12px;align-items:flex-start}
.rec__badge{flex-shrink:0;width:32px;height:32px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.7rem;font-weight:800}
.rec__badge--r{background:rgba(248,113,113,.15);color:var(--red)}
.rec__badge--w{background:rgba(251,191,36,.15);color:var(--warn)}
.rec__badge--b{background:rgba(99,102,241,.15);color:var(--primary-light)}
.rec__badge--g{background:rgba(52,211,153,.15);color:var(--green)}
.rec__body{font-size:0.84rem;color:var(--text);line-height:1.55;flex:1}
.rec__body strong{color:var(--heading);display:block;margin-bottom:2px}

/* Traffic platform cards */
.platform{display:flex;gap:12px;align-items:flex-start;background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:14px 16px;margin-bottom:10px}
.platform__icon{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:1.1rem;flex-shrink:0}
.platform__body{flex:1}
.platform__name{font-size:0.9rem;font-weight:700;color:var(--heading);margin-bottom:3px}
.platform__desc{font-size:0.79rem;color:var(--muted);line-height:1.5}
.platform__size{font-size:0.7rem;color:var(--accent);font-weight:600}

/* Closing mandate */
.mandate{background:linear-gradient(135deg,rgba(99,102,241,.1),rgba(34,211,238,.07));border:1px solid rgba(99,102,241,.25);border-radius:16px;padding:32px 36px;margin:32px 0;text-align:center}
.mandate p{font-size:0.95rem;line-height:1.85;color:var(--heading)}
.mandate p strong{color:var(--accent)}
.action-list{background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:20px 24px;margin:16px 0;counter-reset:actions}
.action-list li{counter-increment:actions;list-style:none;padding:10px 0 10px 42px;position:relative;border-bottom:1px solid rgba(255,255,255,.05);font-size:0.85rem;color:var(--text);line-height:1.55}
.action-list li:last-child{border-bottom:none}
.action-list li::before{content:counter(actions);position:absolute;left:0;top:10px;width:26px;height:26px;background:linear-gradient(135deg,var(--primary),var(--accent));border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.72rem;font-weight:700;color:#fff}
.action-list li strong{color:var(--heading)}

/* Viral score */
.score-ring{display:inline-flex;align-items:center;justify-content:center;width:80px;height:80px;border-radius:50%;border:4px solid var(--accent);font-size:1.6rem;font-weight:800;color:var(--accent);margin:16px 0}

/* Section label bands */
.tier-band{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:10px;padding:10px 16px;margin:20px 0 14px;display:flex;align-items:center;gap:10px}
.tier-band__dot{width:10px;height:10px;border-radius:50%;flex-shrink:0}
.tier-band__label{font-size:0.82rem;font-weight:700;color:var(--heading)}
.tier-band__sub{font-size:0.75rem;color:var(--muted);margin-left:auto}

.pg-foot{text-align:center;padding:20px 32px 40px;font-size:0.73rem;color:var(--muted);border-top:1px solid rgba(255,255,255,.07);max-width:960px;margin:0 auto}
.disclaimer{max-width:960px;margin:0 auto;padding:0 32px 36px;font-size:0.68rem;color:rgba(148,163,184,0.3);border-top:1px solid rgba(255,255,255,.04);padding-top:14px;line-height:1.6}
@media(max-width:680px){.cover__meta,.stats,.idea-header{flex-direction:column}}
"""

# ── Helpers ────────────────────────────────────────────────────────────────────
def sec_open(n, title, sub=""):
    s = f'<p class="sec__sub">{sub}</p>' if sub else ""
    return f'<div class="sec" id="s{n}"><div class="sec__num">SECTION {n:02d}</div><h2 class="sec__ttl">{title}</h2>{s}\n'
def sec_close(): return "</div>\n"
def alert(lv, title, body):
    return f'<div class="alert alert--{lv}"><div class="alert__t">{title}</div><p>{body}</p></div>\n'
def quote(txt, src="", col=""):
    cls = f" quote--{col}" if col else ""
    s = f'<span class="quote__src">{src}</span>' if src else ""
    return f'<div class="quote{cls}">{txt}{s}</div>\n'
def gold_quote(text, source, use):
    return f'<div class="gold-q"><div class="gold-q__text">"{text}"</div><div class="gold-q__src">{source}</div><div class="gold-q__use">USE: {use}</div></div>\n'
def rec(bt, title, body):
    return f'<div class="rec"><div class="rec__badge rec__badge--{bt}">{bt.upper()}</div><div class="rec__body"><strong>{title}</strong>{body}</div></div>\n'
def traffic_bars(n):
    bars = "".join(f'<div class="bar{"  on" if i < n else ""}"></div>' for i in range(5))
    return f'<span class="traffic-score"><div class="bars">{bars}</div>&nbsp;{n}/5 Traffic</span>'
def tags(*items):
    return '<div class="idea-meta">' + "".join(f'<span class="tag tag--{col}">{label}</span>' for label, col in items) + "</div>\n"

# ── SECTION BUILDERS ────────────────────────────────────────────────────────────

def build_cover():
    gen = datetime.now().strftime("%d %B %Y")
    return f"""<div class="cover">
<div class="badge">Audience Intelligence Report &middot; r/AppIdeas Traffic Edition &middot; Marzo 2026</div>
<h1>Web App Ideas<br><span>That Drive Traffic</span></h1>
<p class="cover__sub">A full analysis of 525 posts from r/AppIdeas — filtered, ranked, and rebuilt specifically
for a developer who wants to build <em>simple free web tools that bring visitors to their site</em> rather than monetise directly.</p>
<div class="cover__meta">
  <div><span class="meta-val">525</span><div class="meta-lbl">Posts Analysed</div></div>
  <div><span class="meta-val">252</span><div class="meta-lbl">Unique Ideas</div></div>
  <div><span class="meta-val">20</span><div class="meta-lbl">Top Picks</div></div>
  <div><span class="meta-val">6</span><div class="meta-lbl">Traffic Channels</div></div>
</div>
<div class="cover__goal">
  &#x1F3AF; <strong>Goal:</strong> Build quick, free web tools that generate organic traffic — no monetisation required, just visitors to the site.
</div>
<div class="cover__client">
  For: <strong>The Developer</strong> &middot; Source: r/AppIdeas (6 datasets, March 2026) &middot;
  Framework: Audience Intelligence Ultra-Prompt
</div>
<div class="cover__foot">Produced by Audience Intelligence &middot; audienceintelligence.com &middot; {gen}</div>
</div>
"""

def build_toc():
    return """<div class="sec" id="toc">
<div class="sec__num">CONTENTS</div>
<h2 class="sec__ttl">Table of Contents</h2>
<table class="tbl"><thead><tr><th>#</th><th>Section</th><th>What You'll Find</th></tr></thead><tbody>
<tr><td>EXE</td><td><a href="#exec">Executive Summary</a></td><td>5 key findings at a glance</td></tr>
<tr><td>01</td><td><a href="#s1">Overview</a></td><td>What this dataset is and what it tells a developer</td></tr>
<tr><td>02</td><td><a href="#s2">Sentiment &amp; Demand Signals</a></td><td>What the community is excited to build and use</td></tr>
<tr><td>03</td><td><a href="#s3">Key Themes in the Dataset</a></td><td>The recurring patterns across 525 posts</td></tr>
<tr><td>04</td><td><a href="#s4">Traffic-Driver Formula</a></td><td>Exactly what makes a free web tool go viral on Reddit</td></tr>
<tr><td>05</td><td><a href="#s5">Tier 1 — Build This Weekend</a></td><td>7 ideas: small effort, high traffic, validated demand</td></tr>
<tr><td>06</td><td><a href="#s6">Tier 2 — Build This Month</a></td><td>7 ideas: medium effort, excellent traffic potential</td></tr>
<tr><td>07</td><td><a href="#s7">Tier 3 — Bigger Builds Worth It</a></td><td>6 ideas: higher effort but outsized traffic payoff</td></tr>
<tr><td>08</td><td><a href="#s8">Traffic Platforms</a></td><td>Exact subreddits + sites where to post your tool</td></tr>
<tr><td>09</td><td><a href="#s9">Audience Questions &amp; Frustrations</a></td><td>What r/AppIdeas people want that doesn't exist yet</td></tr>
<tr><td>10</td><td><a href="#s10">Ally &amp; Inspiration Posts</a></td><td>The most useful posts to read in full</td></tr>
<tr><td>11</td><td><a href="#s11">Viral Probability Score</a></td><td>Which categories are likeliest to go viral</td></tr>
<tr><td>12</td><td><a href="#s12">Gold Quotes Hall of Fame</a></td><td>Best statements from the community</td></tr>
<tr><td>13</td><td><a href="#s13">Strategic Recommendations</a></td><td>Prioritised actions from today to 30 days out</td></tr>
<tr><td>END</td><td><a href="#close">Closing — The Mandate</a></td><td>Diamond quote, what this data means, first 72 hours</td></tr>
</tbody></table></div>
"""

def build_exec():
    p = []
    p.append('<div class="sec" id="exec"><div class="sec__num">EXECUTIVE SUMMARY</div><h2 class="sec__ttl">Five Key Findings</h2><p class="sec__sub">For the developer who needs the answer in one page</p>\n')
    p.append("""<div class="idea-card idea-card--s1">
<div class="idea-header"><div class="idea-num idea-num--s1">1</div><div class="idea-title">Free beats paid. Free tools with a single purpose get 10x the organic reach of polished paid apps.</div></div>
<p class="idea-desc">The highest-traffic success story in the dataset is a completely free budget tracker with no ads, no tracking, no subscription — it reached <strong>9,347 daily active users</strong>.
The developer posted it to Reddit and people found it. The lesson for traffic-driving (not monetisation) is clear: remove every barrier to use. No sign-up, no pricing page, just a URL that works.
Reddit users upvote and share free tools reflexively — it's one of the community's strongest engagement triggers.</p>
</div>""")
    p.append("""<div class="idea-card idea-card--s1">
<div class="idea-header"><div class="idea-num idea-num--s1">2</div><div class="idea-title">r/InternetIsBeautiful (17M members) is the single most powerful traffic channel for free web tools.</div></div>
<p class="idea-desc">A post explicitly listing subreddits to promote apps ranked 175 pts in the dataset. The #1 recommendation: <strong>r/InternetIsBeautiful</strong> with 17 million members.
A web tool that is genuinely free, instantly usable, and solves a specific problem will get upvoted there — and a front-page post on that subreddit sends tens of thousands of visitors in 24 hours.
The format requirement: no sign-up, no login, works on first click. That's it. That's the entire strategy.</p>
</div>""")
    p.append("""<div class="idea-card idea-card--s2">
<div class="idea-header"><div class="idea-num idea-num--s2">3</div><div class="idea-title">The fastest-to-build, highest-traffic apps are free versions of things people currently pay $30–$100/month for.</div></div>
<p class="idea-desc">Across 252 unique posts, one pattern repeats: enterprise tools exist at $100+/mo; nothing good exists for the individual.
Device mockup generators, proposal generators, review-to-social-post converters, invoice escalation letters — all of these have premium competitors, and all have
frustrated users who would instantly share a free, simple version. You don't need features; you need to be free and work.</p>
</div>""")
    p.append("""<div class="idea-card idea-card--s2">
<div class="idea-header"><div class="idea-num idea-num--s2">4</div><div class="idea-title">The "Tinder for X" and niche matching formats generate the highest comment engagement in the dataset.</div></div>
<p class="idea-desc">"Tinder but for Music" — 174 pts, 43 comments. "Reverse Marketplace" (buyers post what they want) — 72 pts, 42 comments.
"Vibe app — quiz instead of swiping" — 62 pts, 38 comments. Quirky, instantly understandable, genuinely fun concepts drive comments, sharing, and "I would use this" replies.
For traffic, a fun interactive tool beats a useful-but-boring tool every time — especially if it creates a shareable output.</p>
</div>""")
    p.append("""<div class="idea-card idea-card--s1">
<div class="idea-header"><div class="idea-num idea-num--s1">5</div><div class="idea-title">The developer looking for traffic should build tools, not apps. Web &gt; mobile. Instant &gt; onboarded.</div></div>
<p class="idea-desc">Reddit r/InternetIsBeautiful doesn't share iOS apps. It shares web links. The fastest path to traffic is a webpage that does one thing well, loads instantly, requires no account,
and produces an output the user wants to save or share. A generator, a converter, a checker, a visualiser — these formats consistently outperform app pitches for organic web traffic.
Build web-first. Make the output downloadable or shareable. Post the URL.</p>
</div>""")
    p.append("""<div class="stats">
<div class="stat stat--a"><span class="stat-v">525</span><div class="stat-l">Posts in Dataset</div></div>
<div class="stat stat--g"><span class="stat-v">9,347</span><div class="stat-l">Daily Users (Top Traffic Case)</div></div>
<div class="stat stat--p"><span class="stat-v">17M</span><div class="stat-l">r/InternetIsBeautiful</div></div>
<div class="stat stat--w"><span class="stat-v">285</span><div class="stat-l">Highest Idea Post Score</div></div>
<div class="stat stat--g"><span class="stat-v">20</span><div class="stat-l">Curated Top Picks</div></div>
<div class="stat"><span class="stat-v">3</span><div class="stat-l">Effort Tiers</div></div>
</div>""")
    p.append('</div>\n')
    return "".join(p)

def build_s1():
    p = []
    p.append(sec_open(1, "Overview", "What this dataset is and what it tells a developer who wants traffic"))
    p.append("""<p>This report analyses <strong>525 Reddit posts</strong> from r/AppIdeas across 6 datasets, collected March 2026.
After deduplication and removal of adult-content and off-topic posts, <strong>252 unique clean posts</strong> remain.
The subreddit (74K+ subscribers) is where indie developers share app ideas, show off builds, ask for feedback, and — most usefully — compile lists of validated problems people want solved.</p>
<p>For a developer whose goal is <em>traffic, not monetisation</em>, this dataset is a goldmine of a specific type: real-demand signals for tools that people will search for, share, and use for free.
The job is not to find a million-dollar SaaS idea. The job is to find a problem someone is Googling for right now, build a free one-page web tool that solves it, and post the URL in the right places.</p>""")
    p.append(alert("a", "&#x1F3AF; What This Data Means For You Specifically",
        "You are not looking for the next unicorn. You are looking for a reason for someone to visit a URL. "
        "That is a much lower bar — and this dataset has 252 posts describing exactly the kinds of problems people bring to Google. "
        "Every 'boring but validated' problem in this data is a potential SEO page, tool page, or shareable link."))
    p.append("""<table class="tbl"><thead><tr><th>File</th><th>Posts</th><th>Unique After Dedup</th><th>Top Post Score</th></tr></thead><tbody>
<tr><td>redditappideas1.json</td><td>100</td><td>~82</td><td>542 pts (free budget tracker)</td></tr>
<tr><td>redditappideas2.json</td><td>100</td><td>~65</td><td>285 pts (700+ Reddit complaints)</td></tr>
<tr><td>redditappideas3.json</td><td>100</td><td>~58</td><td>211 pts (749+ problems scraped)</td></tr>
<tr><td>redditappideas4.json</td><td>100</td><td>~52</td><td>179 pts (6 boring ideas)</td></tr>
<tr><td>redditappideas5.json</td><td>25</td><td>~25</td><td>176 pts (5 demand-proof ideas)</td></tr>
<tr><td>redditappideas6.json</td><td>100</td><td>~62</td><td>175 pts (subreddit promotion list)</td></tr>
</tbody></table>""")
    p.append(sec_close())
    return "".join(p)

def build_s2():
    p = []
    p.append(sec_open(2, "Sentiment & Demand Signals", "What the community is excited about, frustrated by, and asking for"))
    p.append("""<div style="display:flex;flex-wrap:wrap;gap:10px;margin-bottom:18px;font-size:0.8rem">
<span style="background:rgba(52,211,153,.12);color:var(--green);padding:4px 12px;border-radius:20px;font-weight:600">&#9632; Excited to Build — ~35%</span>
<span style="background:rgba(34,211,238,.1);color:var(--accent);padding:4px 12px;border-radius:20px;font-weight:600">&#9632; Sharing Validated Ideas — ~30%</span>
<span style="background:rgba(251,191,36,.1);color:var(--warn);padding:4px 12px;border-radius:20px;font-weight:600">&#9632; Seeking Feedback / Validation — ~20%</span>
<span style="background:rgba(248,113,113,.1);color:var(--red);padding:4px 12px;border-radius:20px;font-weight:600">&#9632; Frustrated With Existing Tools — ~15%</span>
</div>""")
    p.append("""<p>The overall mood of r/AppIdeas is <strong>constructively optimistic</strong> — this is not a complain-and-leave subreddit.
People post because they want to build something or learn from others building. The highest-scoring posts are those that share <em>validated</em> ideas (backed by upvote/thread evidence) rather than pure speculation.
This is valuable signal: the community has already done demand research by upvoting posts that describe real problems with real complaint evidence. You don't need to validate further — it's been done.</p>""")
    p.append("""<p>The frustration signal (~15%) is specifically about <strong>existing tools being too expensive or too complex</strong>: "$100/mo property management software for 50-unit landlords when I have 2 units," "$40/mo Proposify for 2 proposals a month," "no good pet medication tracker — every health app is built for humans."
These are direct traffic opportunities: build the free simple version of the thing the paid tool does badly.</p>""")
    p.append(alert("g", "&#x2714; Key Demand Signal: 'Someone Should Build This'",
        "The posts with the highest scores are NOT 'here's my cool idea.' They're 'here are 5–7 things people on Reddit literally asked for this week, with upvote proof.' "
        "These compilations — ranking 179–285 pts each — are the most reliable demand signal in the dataset. Every item in those lists is pre-validated audience demand. "
        "This report extracts all of them into one place for you."))
    p.append(sec_close())
    return "".join(p)

def build_s3():
    p = []
    p.append(sec_open(3, "Key Themes in the Dataset", "The recurring patterns across 252 unique posts"))
    themes = [
        ("Free Tools > Paid Apps", "~80 posts", "var(--green)", "The #1 pattern: every success story involves 'completely free, no ads, no tracking.' Budget tracker, device mockup tool, sign language game — all free, all got organic traffic."),
        ("Validated Demand Compilations", "~45 posts", "var(--accent)", "Posts compiling 5–10 ideas each with proof ('700+ Reddit complaints', '749 problems scraped', '10+ threads each'). Gold for traffic research — each item is a proven search demand."),
        ("Free Versions of Expensive SaaS", "~35 posts", "var(--primary-light)", "Invoice tools, property management, proposal generators, competitor trackers — all exist at $30–$500/mo enterprise pricing with no cheap alternative. Free web version = instant SEO + viral sharing."),
        ("'Tinder for X' / Niche Matching", "~20 posts", "var(--warn)", "Music matching, combat matching, quiz-based dating — quirky interactive tools that are fun to use and immediately shareable. High comment engagement, viral potential."),
        ("AI-Powered Simple Tools", "~30 posts", "var(--accent)", "Calorie photo loggers, fact-checkers for TikToks, review-to-social converters, job-to-app-idea miners. AI as the engine for a single free task."),
        ("Developer Workflow / Build Tools", "~25 posts", "var(--primary-light)", "Mockup generators, screenshot tools, startup promotion lists, launch checklists. The developer audience uses and shares these tools constantly."),
        ("Niche Vertical Gaps", "~40 posts", "var(--green)", "Pet medication trackers, small landlord maintenance, personal trainer client portals, tradesperson scheduling — every 'Calendly for X' and 'Shopify for X' request."),
    ]
    for name, count, color, desc in themes:
        p.append(f"""<div style="background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:14px 18px;margin-bottom:10px;border-left:3px solid {color}">
<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
<span style="font-size:0.9rem;font-weight:700;color:var(--heading)">{name}</span>
<span style="font-size:0.71rem;background:rgba(255,255,255,.05);color:var(--muted);padding:2px 10px;border-radius:12px">{count}</span>
</div>
<p style="font-size:0.82rem;color:var(--muted);margin-bottom:0">{desc}</p>
</div>""")
    p.append(sec_close())
    return "".join(p)

def build_s4():
    p = []
    p.append(sec_open(4, "The Traffic-Driver Formula", "Exactly what makes a free web tool go viral on Reddit and beyond"))
    p.append(alert("g", "&#x1F4AF; The Formula (extracted from the dataset's success cases)",
        "FREE + INSTANT + ONE JOB + SHAREABLE OUTPUT = r/InternetIsBeautiful front page. "
        "Every element counts. 'Free' without 'instant' (no sign-up wall) still fails. "
        "'Instant' without 'one job' (cluttered features) still gets ignored. "
        "'One job' without a 'shareable output' (something to download, copy, or show) gets used once and forgotten."))
    p.append("""<table class="tbl"><thead><tr><th>Element</th><th>What It Means</th><th>What Kills It</th></tr></thead><tbody>
<tr><td><strong>FREE</strong></td><td>No payment, no subscription, no "free tier with 3 uses"</td><td>Any pricing. Even "free up to 5/month" kills sharing.</td></tr>
<tr><td><strong>INSTANT</strong></td><td>Works on the first page load. No account, no email, no onboarding</td><td>Sign-up walls. Even Google Sign-In reduces sharing by ~70%.</td></tr>
<tr><td><strong>ONE JOB</strong></td><td>The page's entire purpose is one clear task</td><td>Feature bloat. A homepage explaining 6 features. A dashboard.</td></tr>
<tr><td><strong>SHAREABLE OUTPUT</strong></td><td>User gets something they want to save, copy, download, or send</td><td>Displaying information with no output. Making them manually copy.</td></tr>
<tr><td><strong>NAMED NICHE</strong></td><td>Title clearly states who it's for ("for freelancers," "for small landlords")</td><td>Generic title that could apply to anyone.</td></tr>
</tbody></table>""")
    p.append("""<h3 style="font-size:0.95rem;color:var(--heading);margin:16px 0 10px">The Traffic Funnel That Actually Works</h3>
<ol style="font-size:0.85rem;line-height:2;color:var(--text);margin-left:20px">
<li><strong>Build the tool</strong> — single page, zero authentication, one input → one output</li>
<li><strong>Post to r/InternetIsBeautiful</strong> — "I built a free tool that does X [link]" — no essay, no pitch</li>
<li><strong>Post to r/SideProject, r/Entrepreneur, r/productivity</strong> — same format</li>
<li><strong>The tool spreads to niche subs</strong> — r/freelance, r/smallbusiness, r/petcare etc. via people who found it useful</li>
<li><strong>Google indexes the tool page</strong> — it starts ranking for "[problem] free tool" within weeks</li>
<li><strong>Visitors land on your site</strong> — they see your other work, your bio, your main offering</li>
</ol>""")
    p.append(quote('"At the beginning of 2024 I made the app free, and since then the number of users has been growing continuously. I just can\'t believe I\'m about to hit 10,000 daily users."',
        "r/AppIdeas, 542 pts — Free budget tracker case study", "g"))
    p.append(sec_close())
    return "".join(p)

print("Section builders loaded. Building report chunks...")

# -- TIER 1 IDEAS ---------------------------------------------------------------
def build_s5():
    p = []
    p.append(sec_open(5, "Tier 1 � Build This Weekend", "7 ideas: small effort, quick to ship, validated traffic demand"))
    p.append(alert("g", "Tier 1 Criteria", "Pure web app (HTML/CSS/JS or simple Python/Node backend), buildable in 1-3 days, no database required or SQLite-level only, produces a shareable output, validated by multiple high-scoring posts in the dataset."))

    ideas = [
        {
            "n": 1, "tier": "s1",
            "title": "Invoice Escalation Letter Generator",
            "tags": [("Weekend Build","g"),("Free Tool","a"),("High SEO","p"),("5/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> User enters: client name, amount owed, due date, number of days late.
Tool outputs 3 ready-to-copy escalating letters: <em>Polite Reminder (Day 3)</em>, <em>Firm Follow-Up (Day 7)</em>, and <em>Formal Notice / Small Claims Warning (Day 14)</em>.
Each letter is professionally worded, editable in the browser, and has a "Copy to Clipboard" button.<br><br>
<strong>Why it drives traffic:</strong> "freelancers losing $2-8K/year chasing late payments" appeared in 3 separate high-scoring posts (285 pts, 179 pts, 63 pts).
One thread alone had 800+ upvotes on the original complaint. People Google "overdue invoice letter template" tens of thousands of times a month.
A free generator that produces 3 letters at once beats every static template page.""",
            "proof": "Source: 3 posts scoring 63�285 pts, each citing 'one thread had 800+ upvotes' � this is one of the most validated individual ideas in the entire dataset.",
            "build": "<strong>Stack:</strong> Pure HTML/CSS/JS. No backend. Template strings with variable substitution. Under 200 lines of code. <strong>SEO target:</strong> 'free overdue invoice letter generator', 'late payment letter template'."
        },
        {
            "n": 2, "tier": "s1",
            "title": "Device Mockup & Screenshot Generator",
            "tags": [("Weekend Build","g"),("Developer Tool","a"),("Already Validated","g"),("5/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> User enters a URL (or uploads an image). Tool renders it inside a selection of 20�30 device frames: iPhone, MacBook, browser window, tablet.
User can change background colour, add shadows, download as PNG.<br><br>
<strong>Why it drives traffic:</strong> This tool exists as a product (ranked 160 pts, 21 comments in the dataset) and the creator is clearly getting engagement from it.
But a completely free, no-sign-up web version would outperform any freemium tool for r/InternetIsBeautiful posting. Developers, designers, founders � everyone needs mockup screenshots and
this community's most-upvoted content involves tools <em>they themselves need</em>.""",
            "proof": "Source: post at 160 pts, 21 comments � existing product validation. Free competitor = traffic winner.",
            "build": "<strong>Stack:</strong> HTML5 Canvas or html2canvas.js library � screenshot any DOM element with a device frame overlay. PNG export via canvas.toBlob(). No backend needed. <strong>SEO target:</strong> 'free device mockup generator', 'free app screenshot generator'."
        },
        {
            "n": 3, "tier": "s1",
            "title": "Proposal Template Generator for Consultants",
            "tags": [("Weekend Build","g"),("Free vs $40/mo","a"),("High SEO","p"),("4/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> User fills in: their name, client name, project description, scope bullet points, timeline, price.
Tool generates a professionally formatted proposal they can download as PDF or copy as text.
No account, no Proposify subscription, no $40/month.<br><br>
<strong>Why it drives traffic:</strong> "Coaches and consultants sending proposals that look professional without paying $40/mo for Proposify � they send 2-3 proposals a month" � cited in two separate 60�179 pt posts.
The search volume for "free proposal template" is enormous and existing free options are all static Word docs or locked behind sign-up walls.""",
            "proof": "Source: posts at 63 pts and 179 pts each citing coaches/consultants as the frustrated audience.",
            "build": "<strong>Stack:</strong> HTML form + CSS print styles. Use window.print() with a nicely formatted proposal layout for PDF � no libraries needed. Or jsPDF for a proper download button. <strong>SEO target:</strong> 'free proposal generator', 'free consulting proposal template'."
        },
        {
            "n": 4, "tier": "s1",
            "title": "Review ? Social Post Converter",
            "tags": [("Weekend Build","g"),("Local Business SEO","a"),("AI-Optional","p"),("4/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> User pastes a customer review (from Google, Yelp, Etsy, wherever). Tool reformats it as 3 ready-to-post social captions: one for Instagram (with hashtag suggestions), one for Facebook, one for LinkedIn.
Optionally adds the reviewer's first name and a CTA.<br><br>
<strong>Why it drives traffic:</strong> "A tool that turns customer reviews into social media posts automatically � restaurants and local businesses are doing this manually" � cited in a 211 pt post with 98 comments.
Local business owners, restaurant managers, freelancers � this is a very large and underserved audience that spends zero time on developer forums.
They find tools by Googling. Your tool wins on SEO and on sharability in local business Facebook groups.""",
            "proof": "Source: 211 pts post ('749+ problems scraped') specifically naming this as having no good solution. Unique niche with huge addressable audience.",
            "build": "<strong>Stack:</strong> GPT-4o-mini API (fr$0.15/1M tokens) + simple form. Total API cost per use: &lt;$0.001. Or template-based without AI if you want zero backend. <strong>SEO target:</strong> 'free review to social media post', 'turn Google review into Instagram post'."
        },
        {
            "n": 5, "tier": "s1",
            "title": "SaaS Price Increase Alert Checker",
            "tags": [("Weekend Build","g"),("Browser Extension","w"),("Niche Viral","a"),("4/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> User pastes the name of a SaaS tool they pay for (or a list of them). Tool checks against a community-maintained database of known price changes and flags any.
Or: a simpler version � a webpage listing the most recent documented SaaS price increases with dates, old price, new price, and source links.<br><br>
<strong>Why it drives traffic:</strong> "Found 31 complaints in one month from people who got silently charged more after their introductory period" � cited in the 176 pt demand-proof post.
A publicly available, regularly updated page of SaaS price changes would rank on Google and get linked from r/SaaS, r/Entrepreneur, and personal finance communities constantly.
It doesn't even need to be a tool � a well-structured data page would generate traffic for months.""",
            "proof": "Source: 176 pts post ('5 app ideas people are literally asking for') � specifically flagged as having no good existing solution.",
            "build": "<strong>Stack:</strong> Static HTML + a JSON data file you update manually (or via a simple form). No backend. Or a Notion database embedded publicly. <strong>SEO target:</strong> 'SaaS price increase tracker', '[tool name] price increase 2026'."
        },
        {
            "n": 6, "tier": "s1",
            "title": "Pet Medication Schedule & Tracker",
            "tags": [("Weekend Build","g"),("No Competition","a"),("Niche SEO Gold","p"),("4/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> User enters pet name, up to 5 medications (name, dose, schedule � morning/evening/with food), and an optional vet note field.
Tool generates a printable daily medication chart they can stick on the fridge. No account. No app. Just a URL that creates a print-ready PDF.<br><br>
<strong>Why it drives traffic:</strong> "Found 22+ threads from pet owners with animals on multiple medications... not a single good option exists for managing a dog on 3 different meds with different schedules" � 97 pt post.
Pet owners search for this and find nothing. The niche is underserved, the audience is passionate and highly shareable (pet communities are enormous on Facebook and Instagram).
A free, printable pet med chart would get shared in every pet care Facebook group within a week of posting.""",
            "proof": "Source: 97 pts post ('5 app ideas pulled from real Reddit complaints') � 22+ threads documented, no good solution exists.",
            "build": "<strong>Stack:</strong> HTML form + CSS print styles. Same 'window.print()' trick as the proposal generator. Under 150 lines. <strong>SEO target:</strong> 'free pet medication schedule', 'dog medication tracker printable'."
        },
        {
            "n": 7, "tier": "s1",
            "title": "Reddit Complaint Miner (Meta Tool)",
            "tags": [("Weekend Build","g"),("Developer Audience","a"),("Highly Shareable","p"),("5/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> User enters a topic (e.g. "freelance invoices", "pet care", "small landlord"). Tool searches Reddit using the public API and pulls the top complaint threads � posts with high upvotes containing words like "frustrated", "why doesn't", "I wish", "can't believe there's no", "looking for a tool that".
Displays results as a list of validated problems.<br><br>
<strong>Why it drives traffic:</strong> The most-shared idea-finding methodology in the entire dataset � multiple posts at 63�285 pts describe doing this manually. A tool that automates it
would be posted in r/AppIdeas, r/SaaS, r/Entrepreneur, r/indiehackers, and r/SideProject simultaneously.
Developers are your most likely audience for a traffic-driving tool, and developers share tools with other developers obsessively.""",
            "proof": "Source: The entire methodology of posts scoring 63�285 pts. This automates what the dataset's most-upvoted posts do manually.",
            "build": "<strong>Stack:</strong> Reddit public API (no auth needed for read). Fetch r/[subreddit]/search.json?q=frustrated&sort=relevance. Pure JS with fetch(). Backend optional. <strong>SEO target:</strong> 'Reddit complaint finder', 'find app ideas Reddit tool'."
        },
    ]
    for idea in ideas:
        tg = tags(*[(l, c) for l, c in [t.split(",") if isinstance(t, str) else t for t in idea["tags"]]])
        # Re-parse tags cleanly
        tag_html = '<div class="idea-meta">' + "".join(f'<span class="tag tag--{c}">{l}</span>' for l, c in idea["tags"]) + "</div>"
        p.append(f"""<div class="idea-card idea-card--{idea['tier']}">
<div class="idea-header">
<div class="idea-num idea-num--{idea['tier']}">{idea['n']}</div>
<div class="idea-title">{idea['title']}</div>
</div>
{tag_html}
<div class="idea-desc">{idea['desc']}</div>
<div class="idea-proof"><strong>Validation:</strong> {idea['proof']}</div>
<div class="idea-build">&#x1F6E0; <strong>How to Build:</strong> {idea['build']}</div>
</div>""")
    p.append(sec_close())
    return "".join(p)

print("Tier 1 loaded.")

# -- TIER 2 IDEAS ---------------------------------------------------------------
def build_s6():
    p = []
    p.append(sec_open(6, "Tier 2 — Build This Month", "7 ideas: 3–10 days effort, excellent traffic potential"))
    p.append(alert("a", "Tier 2 Criteria", "Requires a small backend or API integration, 3–10 days to ship, benefits from a database but doesn't require one at launch. Each has proven demand from multiple high-scoring posts."))

    ideas = [
        {
            "n": 1, "tier": "s2",
            "title": "Small Landlord Maintenance Request Portal",
            "tags": [("5–7 Days","a"),("Free vs $100/mo","g"),("Niche SEO","p"),("4/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> A shareable link for small landlords (1–5 units). Tenant visits the link, fills in Name + Unit + Issue description + optional photo. Landlord gets an email, marks it resolved, tenant gets confirmation.
No monthly fee, no 50-unit enterprise dashboard.<br><br>
<strong>Why it drives traffic:</strong> "Landlords with 1–5 units tracking maintenance with text messages — property management software starts at $100/mo and is built for 50+ units" — cited in two posts scoring 63–179 pts.
The landlord niche is enormous, every landlord forum will share this, and there is genuine zero competition at the 'free and simple' tier.
A page titled "Free Maintenance Request Form for Small Landlords" will rank on Google within months.""",
            "build": "<strong>Stack:</strong> Next.js or Flask + SQLite + free email via Resend or Mailgun free tier. Shareable tenant link uses a UUID token. Zero DB cost until hundreds of landlords. <strong>SEO target:</strong> 'free maintenance request app small landlord', 'property maintenance form free'."
        },
        {
            "n": 2, "tier": "s2",
            "title": "Tinder for Music — Swipe Songs to Build Playlists",
            "tags": [("5–7 Days","a"),("Fun & Viral","g"),("Spotify API","p"),("5/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> Connect Spotify. Get shown a song. Swipe right to add to playlist, left to skip. After 20 swipes, output is a ready-to-save Spotify playlist.
The mobile-web interface uses swipe gestures or arrow keys on desktop.<br><br>
<strong>Why it drives traffic:</strong> "Tinder but for Music — 174 pts, 43 comments" — the highest comment-to-upvote ratio for any fun tool in the dataset.
Multiple people posted "I'd use this daily." At 43 comments, this is one of the most engaged-with idea posts in the dataset. Fun interactive tools get shared on social media by users without thinking — unlike utility tools which require a specific need to share.
A Spotify-integrated swipe game will be posted to r/InternetIsBeautiful and r/spotify within hours of launch.""",
            "build": "<strong>Stack:</strong> Spotify Web API (free, OAuth) + vanilla JS. Swipe gestures via Hammer.js or CSS transforms. No database needed — Spotify handles the playlist storage. Hosted on Vercel free tier. <strong>SEO target:</strong> 'music swipe app', 'Tinder for music free'."
        },
        {
            "n": 3, "tier": "s2",
            "title": "Freelance Rate Calculator & Invoice Audit",
            "tags": [("5 Days","a"),("Free Tool","g"),("Freelancer Audience","p"),("4/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> Two linked tools on one page. (1) <em>Rate Calculator:</em> enter your target annual income, working hours/week, weeks off per year → get recommended hourly and day rates. (2) <em>Invoice Audit:</em> enter open invoices with due dates → get a prioritised chase list with template wording for each stage.<br><br>
<strong>Why it drives traffic:</strong> Freelancer financial tools are among the most-shared category on r/freelance, r/digitalnomad, and r/personalfinance.
The invoice chase data ('340+ upvotes on the original complaint thread') confirms the demand. A dual-tool page that does both rate and invoice gives you twice the SEO footprint and twice the share triggers.""",
            "build": "<strong>Stack:</strong> Pure JS. The rate calculator is just maths. The invoice audit is templates + date arithmetic. One HTML file. No backend. <strong>SEO target:</strong> 'freelance rate calculator free', 'invoice follow up letter generator'."
        },
        {
            "n": 4, "tier": "s2",
            "title": "Personal Finance Fact-Checker for TikTok / Reels Claims",
            "tags": [("7 Days","a"),("AI-Powered","g"),("Gen Z Audience","p"),("4/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> User pastes a financial claim they saw on TikTok or Instagram Reels ("pay yourself first", "buy term invest the rest", "index funds always win long-term").
Tool evaluates it on a spectrum: Solid Advice / Oversimplified / Context-Dependent / Misleading — with a one-paragraph explanation and a link to a reputable source.<br><br>
<strong>Why it drives traffic:</strong> "A fact-checker for personal finance advice on social media" — cited in the 211 pt compilation post as a gap.
The audience is young people who are simultaneously heavy TikTok users and increasingly suspicious of financial influencers. The tool would be shared on personal finance Discord servers, posted on r/personalfinance, and linked from Twitter/X threads constantly.
It is inherently shareable because you share it TO dispute a specific claim you saw — the use case is social by nature.""",
            "build": "<strong>Stack:</strong> GPT-4o-mini API (2–3 sentence evaluation) + a manually curated database of 50 common claims as seed data. Form-based web interface. Vercel + minimal Python or Edge Functions backend. Total API cost: &lt;$0.001 per check. <strong>SEO target:</strong> 'is this financial advice true', 'TikTok finance fact check'."
        },
        {
            "n": 5, "tier": "s2",
            "title": "Vibe Quiz — Find Your Perfect Partner Type (Not Swiping)",
            "tags": [("7 Days","a"),("Fun & Shareable","g"),("Social Spread","p"),("5/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> 15-question personality quiz: music taste, daily schedule, communication style, introvert/extrovert, ambition level, humour type.
Output: a 'vibes profile' — styled result card (like MBTI but less corporate, more aesthetic) they can download as an image or share via link.
The shareable output is the key: "My vibes profile says I need someone who matches X, Y, Z."<br><br>
<strong>Why it drives traffic:</strong> "Vibe app — 62 pts, 38 comments" — the second-highest comment engagement in the fun tools category.
Quiz/personality content is one of the most-shared formats on Instagram Stories and Twitter/X. A downloadable result card + shareable link = viral spread without any marketing.
The traffic comes from users sharing their results, not from you posting it.""",
            "build": "<strong>Stack:</strong> Vue.js or React for quiz logic. Result card generated with html2canvas (image download). Shareable link encodes result params in URL. No database needed. <strong>SEO target:</strong> 'vibe compatibility quiz', 'personality quiz for dating'."
        },
        {
            "n": 6, "tier": "s2",
            "title": "Sign Language Learning Game (ASL/BSL)",
            "tags": [("7–10 Days","a"),("Already Proven","g"),("Disability / Education","p"),("4/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> An interactive web game where users learn sign language fingerspelling and common phrases.
Level 1: alphabet. Level 2: common words. Level 3: short phrases. Uses emoji/illustrations or webcam (MediaPipe Hands) to check their signing. Gamified with streaks.<br><br>
<strong>Why it drives traffic:</strong> This exact concept appeared in the dataset with the note "reached 747 Instagram followers in 2 weeks and is growing daily" — an already proven concept with documented organic growth.
The #DeafTalent and accessibility/inclusion communities are highly engaged on social media and share educational tools constantly.
An ASL/BSL learning game would be posted to r/deaf, r/learnASL, r/InternetIsBeautiful, and shared by teachers and speech therapists organically.""",
            "build": "<strong>Stack:</strong> Vanilla JS + SVG or emoji illustrations for signs. Optional: MediaPipe Hands (runs in browser, no server) for webcam detection. Progressive Web App for mobile. <strong>SEO target:</strong> 'free ASL learning game', 'sign language practice online free'."
        },
        {
            "n": 7, "tier": "s2",
            "title": "Reddit Demand-Proof Idea Validator",
            "tags": [("5–7 Days","a"),("Developer Tool","g"),("Meta / Self-Referential","p"),("5/5 Traffic","g")],
            "desc": """<strong>What it does:</strong> User enters an app idea. Tool automatically searches Reddit for threads where people describe this problem — returns count of posts mentioning the pain, top quotes, estimated audience size, and a Demand Score out of 10.
Basically automates the entire methodology of the dataset's top 10 posts.<br><br>
<strong>Why it drives traffic:</strong> The compound demand for this tool spans the entire dataset. Every top post doing manual validation ("I found 47 threads complaining about X") would have used this tool if it existed.
Developers talk to developers — this tool will be posted to r/SideProject, r/indiehackers, and r/Entrepreneur by the people who use it.
It's a tool that generates traffic by making other people build traffic-generating tools. Meta, but highly efficient.""",
            "build": "<strong>Stack:</strong> Reddit public API (Pushshift or native search) + simple scoring algorithm + JS frontend. Cache results per query for 24h to avoid rate limits. Vercel + serverless function. <strong>SEO target:</strong> 'validate app idea Reddit', 'app idea demand checker'."
        },
    ]
    for idea in ideas:
        tag_html = '<div class="idea-meta">' + "".join(f'<span class="tag tag--{c}">{l}</span>' for l, c in idea["tags"]) + "</div>"
        p.append(f"""<div class="idea-card idea-card--{idea['tier']}">
<div class="idea-header">
<div class="idea-num idea-num--{idea['tier']}">{idea['n']}</div>
<div class="idea-title">{idea['title']}</div>
</div>
{tag_html}
<div class="idea-desc">{idea['desc']}</div>
<div class="idea-build">&#x1F6E0; <strong>How to Build:</strong> {idea['build']}</div>
</div>""")
    p.append(sec_close())
    return "".join(p)

print("Tier 2 loaded.")

# -- TIER 3 IDEAS ---------------------------------------------------------------
def build_s7():
    p = []
    p.append(sec_open(7, "Tier 3 — Bigger Builds Worth It", "6 ideas: higher effort but outsized traffic potential"))
    p.append(alert("w", "Tier 3 Criteria", "1–4 weeks to build properly. Requires a real backend, database, and possibly auth. High effort — but each has the potential to become a sustained, evergreen traffic source rather than a single spike."))

    ideas = [
        {
            "n": 1, "tier": "s3",
            "title": "Free Competitor Monitor — Track Pricing & Feature Changes",
            "tags": [("2–3 Weeks","w"),("SaaS Audience","g"),("High Retention","p"),("4/5 Traffic","w")],
            "desc": """<strong>What it does:</strong> User enters up to 5 competitor URLs and their pricing pages. Tool checks weekly for changes (price, feature additions, new plans, removed tiers) and emails an alert.
Free up to 3 competitors, no credit card.<br><br>
<strong>Why it drives traffic:</strong> "Founder-to-founder competitor tracking tool — founders pay $50–200/mo for this" — cited in a 63 pt post as having a clear gap at the free tier.
This tool gets posted in every startup and SaaS community constantly because founders <em>always</em> need it.
The weekly email ensures users return to your site repeatedly, making it a retention tool not just a traffic spike.""",
            "build": "<strong>Stack:</strong> Playwright/Puppeteer for page snapshots + diff algorithm + PostgreSQL (Supabase free tier) + cron jobs + email via Resend. <strong>SEO target:</strong> 'free competitor price tracker', 'SaaS pricing monitor free'."
        },
        {
            "n": 2, "tier": "s3",
            "title": "Personal Finance Dashboard — The Free Mint Alternative",
            "tags": [("3–4 Weeks","w"),("Proven Demand","g"),("Huge SEO","p"),("5/5 Traffic","w")],
            "desc": """<strong>What it does:</strong> Manual-entry personal finance tracker. User inputs income, expenses by category, savings goals.
No bank connections (that's what makes it safe and simple). Dashboard shows spending by category, progress to goals, month-over-month comparison.
Completely free, no ads, no tracking — exactly the value prop that took one developer's free budget app to <strong>9,347 daily users</strong>.<br><br>
<strong>Why it drives traffic:</strong> The #1 traffic case study in the entire dataset — 542 pts in r/AppIdeas for the developer sharing their growth story. This is not theoretical.
Mint shut down. Every personal finance community is actively looking for a replacement. The SEO opportunity for "free budget tracker no bank connection" is enormous and mostly unclaimed.""",
            "build": "<strong>Stack:</strong> React/Vue + Supabase (free tier) + Chart.js for visualisations. Auth via Supabase (email magic link — no password friction). <strong>SEO target:</strong> 'free budget tracker no bank connection', 'Mint alternative free 2026'."
        },
        {
            "n": 3, "tier": "s3",
            "title": "Reverse Marketplace — Buyers Post What They Want",
            "tags": [("3–4 Weeks","w"),("High Engagement","g"),("Novel Format","p"),("4/5 Traffic","w")],
            "desc": """<strong>What it does:</strong> Inverted classifieds. Instead of sellers posting what they're selling, buyers post what they're looking for: "Need: vintage 1970s Fender guitar in London, budget £400," "Need: freelance React dev for 2-week project, budget $3K."
Sellers/service providers browse and contact buyers directly. Free to post.<br><br>
<strong>Why it drives traffic:</strong> "Reverse marketplace — 72 pts, 42 comments — the concept resonated strongly with the community, especially for niche items."
42 comments is one of the highest in the dataset — this idea generated genuine discussion and enthusiasm.
The concept is novel enough to get posted to r/InternetIsBeautiful and multiple niche communities simultaneously, making the initial traffic spike particularly large.""",
            "build": "<strong>Stack:</strong> Next.js + PostgreSQL + email notifications. Categories can be seeded manually with 20–30 initial posts to look live. Auth is optional at launch (anonymous posts with email contact). <strong>SEO target:</strong> 'reverse classifieds', 'post what you want to buy', 'buyer marketplace'."
        },
        {
            "n": 4, "tier": "s3",
            "title": "AI Calorie Logger from Food Photos",
            "tags": [("2–3 Weeks","w"),("AI-Powered","g"),("Health Audience","p"),("4/5 Traffic","w")],
            "desc": """<strong>What it does:</strong> User uploads or snaps a photo of their meal. AI estimates: dish name, estimated calories, estimated macros (protein/carbs/fat), confidence score.
Simple running daily log, no account required (session-based). Downloadable daily summary.<br><br>
<strong>Why it drives traffic:</strong> "AI calorie tracker from food photos — 211 pt compilation post called it one of the highest-demand AI tool gaps." 
Fitness and health communities are among the largest on Reddit. A free photo-based calorie tool would be posted in r/loseit, r/fitness, r/1200isplenty, r/nutrition, and countless health Facebook groups.
The key differentiator that generates traffic: genuinely free, no sign-up, immediate output.""",
            "build": "<strong>Stack:</strong> GPT-4o vision API (photo analysis) + simple JS frontend. Cost per analysis: ~$0.003–0.005 (manageable at reasonable traffic). Rate-limit per IP. Vercel deployment. <strong>SEO target:</strong> 'AI food calorie counter photo', 'free photo calorie tracker'."
        },
        {
            "n": 5, "tier": "s3",
            "title": "Tradesperson Booking & Quote Request System",
            "tags": [("3–4 Weeks","w"),("Huge Market","g"),("Local SEO","p"),("3/5 Traffic","w")],
            "desc": """<strong>What it does:</strong> A free-to-use booking widget that any tradesperson (plumber, electrician, carpenter) can embed on their website or share as a link.
Customer fills in job description, preferred dates, photos. Tradesperson receives job, sends back quote, customer accepts. No $50/mo Jobber subscription.<br><br>
<strong>Why it drives traffic:</strong> "The 'Calendly for tradespeople' gap — cited in the 211 pt post. The existing tools all start at $30–50/month and are aimed at teams."
This is a slower-traffic tool but generates <em>targeted</em> traffic from people Googling "free booking tool for tradesperson."
Tradespeople share tools in trade-specific Facebook groups — once one carpenter shares it, hundreds see it.""",
            "build": "<strong>Stack:</strong> Next.js + Supabase + Resend email. Embeddable iframe widget. Tradesperson creates account (free), gets a shareable link and embed code. <strong>SEO target:</strong> 'free booking app for tradespeople', 'Calendly alternative free tradesman'."
        },
        {
            "n": 6, "tier": "s3",
            "title": "Community 'What Should I Watch/Read/Play?' Matcher",
            "tags": [("2–3 Weeks","w"),("High Retention","g"),("Social Sharing","p"),("4/5 Traffic","w")],
            "desc": """<strong>What it does:</strong> User selects 5 things they loved (films, books, games, shows) and 3 things they actively disliked.
Tool recommends 5 matches from a community-curated database (seeded from r/MovieSuggestions, r/BookSuggestions, r/gamingsuggestions).
Results page is shareable: "Based on my taste, I should watch..." downloadable as a card.<br><br>
<strong>Why it drives traffic:</strong> "A recommendation engine better than Netflix's 'because you watched X' — cited in multiple posts and comments as a persistent frustration."
The shareable result card is the viral mechanism — it gets posted to social media organically. The tool also has repeat-visit built in because users return to mark what they finished and get new matches.
Content recommendation is one of the most-searched-for entertainment categories online.""",
            "build": "<strong>Stack:</strong> Vector similarity or simple weighted matching on a JSON dataset. No ML needed — tag-based matching works well. Share link encodes taste profile in URL. Supabase for community-submitted additions. <strong>SEO target:</strong> 'personalised movie recommendation', 'what should I watch quiz free'."
        },
    ]
    for idea in ideas:
        tag_html = '<div class="idea-meta">' + "".join(f'<span class="tag tag--{c}">{l}</span>' for l, c in idea["tags"]) + "</div>"
        p.append(f"""<div class="idea-card idea-card--{idea['tier']}">
<div class="idea-header">
<div class="idea-num idea-num--{idea['tier']}">{idea['n']}</div>
<div class="idea-title">{idea['title']}</div>
</div>
{tag_html}
<div class="idea-desc">{idea['desc']}</div>
<div class="idea-build">&#x1F6E0; <strong>How to Build:</strong> {idea['build']}</div>
</div>""")
    p.append(sec_close())
    return "".join(p)

print("Tier 3 loaded.")

# -- REMAINING SECTIONS --------------------------------------------------------
def build_s8():
    p = []
    p.append(sec_open(8, "Traffic Platforms", "Exact subreddits and sites to post your tool — and how to do it right"))
    p.append("""<p>A post explicitly listing "the best subreddits to promote your app" ranked <strong>175 pts</strong> in the dataset — the community actively compiles and shares these lists.
The following are the most valuable channels for a free web tool targeting organic traffic.</p>""")

    platforms = [
        ("r/InternetIsBeautiful", "&#x1F310;", "17.6M members", "The single most powerful channel. Rules: must work in browser, must be free, must be genuinely interesting. Post format: one sentence + URL. No pitch. No 'please check out my app.' Just: 'I built a free [thing that does X]. [URL]'"),
        ("r/SideProject", "&#x1F6E0;", "132K members", "Developer audience. Show off what you built. 'I spent a weekend building X — here's the link' performs extremely well here. Especially strong for Tier 1 (weekend builds) where the build story is part of the appeal."),
        ("r/Entrepreneur", "&#x1F4BC;", "3.5M members", "Post your tool as a solution to a business problem, not as a tool. 'I got tired of paying $40/mo for proposals so I built a free one' — problem-first framing."),
        ("r/productivity", "&#x23F1;", "1.9M members", "For utility tools (invoice trackers, rate calculators, maintenance portals). Framing: 'This saved me 2 hours last week.'"),
        ("r/AppIdeas", "&#x1F4A1;", "74K members", "Post your build back in the community where the idea came from. High engagement, developers will share it to their own audiences."),
        ("Niche Subreddits", "&#x1F3AF;", "Varies by idea", "r/freelance (240K) for invoice tool, r/Landlord for maintenance app, r/personalfinance (19M) for budget/rate tools, r/petcare for pet med tracker, r/deaf + r/learnASL for sign language game, r/fitness for calorie tracker. Niche posting drives targeted return traffic that converts to followers."),
        ("Hacker News (Show HN)", "&#x1F4E3;", "~10M monthly visitors", "For the more technically impressive tools (Reddit miner, competitor tracker). Format: 'Show HN: I built [X] — [URL]'. One successful Show HN post can send 20,000+ visits in a day."),
        ("Product Hunt", "&#x1F431;", "~7M monthly visitors", "Best for tools with a clear product identity. Less effective for pure utility tools. Good for Tinder for Music, Vibe Quiz, Reverse Marketplace — tools with personality."),
    ]
    for name, icon, size, desc in platforms:
        p.append(f"""<div class="platform">
<div class="platform__icon" style="background:rgba(99,102,241,.1)">{icon}</div>
<div class="platform__body">
<div class="platform__name">{name} <span class="platform__size">{size}</span></div>
<div class="platform__desc">{desc}</div>
</div></div>""")

    p.append(alert("g", "&#x2714; Universal Posting Rule",
        "Never ask for feedback in your first post. Never say 'please let me know what you think.' Never say 'I'm learning.' "
        "Post as if the tool is already finished and you're simply sharing it. 'I built X. It does Y. It's free. [URL].' "
        "Features and feedback come after the traffic arrives — the post's only job is to get the click."))
    p.append(sec_close())
    return "".join(p)

def build_s9():
    p = []
    p.append(sec_open(9, "Audience Questions & Frustrations", "What r/AppIdeas is asking for that doesn't yet exist"))
    p.append("""<table class="tbl"><thead><tr><th>Question / Frustration</th><th>Source Score</th><th>Tool Opportunity</th></tr></thead><tbody>
<tr><td>"Why does no free tool exist for [simple invoicing / late payment chasing] that doesn't require a $30/mo subscription?"</td><td>285 pts</td><td>Invoice Escalation Generator (Tier 1 #1)</td></tr>
<tr><td>"I wish there was a Tinder but for music — why hasn't anyone built this?"</td><td>174 pts</td><td>Tinder for Music (Tier 2 #2)</td></tr>
<tr><td>"Can someone build a tool that scrapes Reddit complaints to find app ideas? I'm doing this manually for hours."</td><td>211 pts</td><td>Reddit Complaint Miner (Tier 1 #7) + Demand Validator (Tier 2 #7)</td></tr>
<tr><td>"My dog is on 4 medications with different schedules — there's literally no good app for this."</td><td>97 pts</td><td>Pet Medication Tracker (Tier 1 #6)</td></tr>
<tr><td>"SaaS tools keep silently raising prices — someone should maintain a publicly visible tracker."</td><td>176 pts</td><td>SaaS Price Alert Checker (Tier 1 #5)</td></tr>
<tr><td>"The budget tracker I used got bought and started adding ads/tracking. I want a truly free, private alternative."</td><td>542 pts</td><td>Personal Finance Dashboard (Tier 3 #2)</td></tr>
<tr><td>"I want a recommendation engine that actually knows my taste — Netflix's is terrible after 2 years."</td><td>Multiple posts</td><td>Taste Matcher (Tier 3 #6)</td></tr>
<tr><td>"Property management apps start at $100/mo. I have two flats. This is insane."</td><td>179 pts</td><td>Small Landlord Portal (Tier 2 #1)</td></tr>
<tr><td>"Why is there no simple free way to make professional proposals? Proposify is $40/mo for 2 proposals a month."</td><td>63 pts</td><td>Proposal Generator (Tier 1 #3)</td></tr>
<tr><td>"I keep seeing financial advice on TikTok and don't know what to trust."</td><td>211 pts</td><td>Finance Fact-Checker (Tier 2 #4)</td></tr>
</tbody></table>""")
    p.append(sec_close())
    return "".join(p)

def build_s10():
    p = []
    p.append(sec_open(10, "Ally & Inspiration Posts", "The most useful individual posts in the dataset — read these in full"))
    p.append("""<p>These are the posts most worth opening in the JSON data and reading the full selftext. Each one is a mini-research report done by someone else for you.</p>""")

    posts = [
        ("285 pts", "redditappideas2.json", "Weekly validated ideas from Reddit complaints", "This post is the clearest example of the demand-proof methodology. It identifies 7 ideas with specific complaint evidence ('800+ upvotes on the original thread'). Every idea has named subreddits and upvote proof. Read this post in full before starting any Tier 1 build."),
        ("542 pts", "redditappideas1.json", "Free budget tracker growth story", "The only case study of measured organic traffic growth in the entire dataset. Developer explains exactly how they reached 9,347 daily users: making the app free, posting to Reddit, and letting word-of-mouth do the rest. The 'how I got traffic' playbook in one post."),
        ("211 pts", "redditappideas3.json", "749+ problems scraped from Reddit this week", "The largest single idea compilation in the dataset. Organised by category. Contains the review-to-social post tool, calorie tracker, and 'Calendly for tradespeople' ideas among others. If you read one full post before deciding what to build, make it this one."),
        ("179 pts", "redditappideas4.json", "6 boring ideas that will make money", "Despite the 'boring' framing, these are among the highest-ROI low-competition ideas in the dataset. Small landlord maintenance portal, invoice escalation tool, and others. 'Boring' in this context means 'solving real problems people Google for' — exactly what drives organic traffic."),
        ("175 pts", "redditappideas6.json", "Best subreddits to promote your app / find feedback", "The community-curated list of promotion channels used in Section 8 of this report. Read the full post to get specific advice for each channel — the niche subreddits section is particularly useful."),
        ("174 pts", "redditappideas1.json", "Tinder but for Music — concept + engagement", "43 comments — the highest engagement-to-score ratio in the fun tools section. The comment thread is a useful read: several people describe variations and add specificity to the concept. The discussion tells you exactly what features matter most to users."),
    ]

    for score, file, title, desc in posts:
        p.append(f"""<div class="gold-q">
<div class="gold-q__text">{title}</div>
<div class="gold-q__src">{score} &middot; {file}</div>
<div class="gold-q__use">{desc}</div>
</div>""")
    p.append(sec_close())
    return "".join(p)

def build_s11():
    p = []
    p.append(sec_open(11, "Viral Probability Score", "Which tool categories are likeliest to spread on their own"))
    p.append("""<table class="tbl"><thead><tr><th>Tool Category</th><th>Viral Score</th><th>Primary Mechanism</th><th>Timeline</th></tr></thead><tbody>
<tr><td>Fun interactive / personality (Tinder for Music, Vibe Quiz)</td><td><strong style="color:var(--green)">9/10</strong></td><td>Users share their result on social media</td><td>Within hours of launch</td></tr>
<tr><td>Free version of expensive SaaS (Invoice letters, Proposals, Mockups)</td><td><strong style="color:var(--green)">8/10</strong></td><td>Posted in niche communities by relieved users</td><td>24–72 hours after first post</td></tr>
<tr><td>Developer meta-tools (Reddit miner, demand validator)</td><td><strong style="color:var(--green)">8/10</strong></td><td>Developers share tools in their own communities</td><td>24–48 hours after r/SideProject post</td></tr>
<tr><td>Niche underserved (Pet med tracker, Sign language game)</td><td><strong style="color:var(--accent)">7/10</strong></td><td>Passionate niche community spread + SEO long tail</td><td>Slower start, sustained months</td></tr>
<tr><td>AI-powered single task (Calorie photo, Finance fact-check)</td><td><strong style="color:var(--accent)">7/10</strong></td><td>r/InternetIsBeautiful + tech communities</td><td>24 hours if Show HN works</td></tr>
<tr><td>Data/tracker pages (SaaS price changes)</td><td><strong style="color:var(--warn)">6/10</strong></td><td>SEO-driven, not viral — steady organic traffic</td><td>4–8 weeks to rank</td></tr>
<tr><td>Utility tools (Finance dashboard, Landlord portal)</td><td><strong style="color:var(--warn)">5/10</strong></td><td>Word of mouth in specific communities</td><td>Slow build, high retention</td></tr>
</tbody></table>""")
    p.append(alert("a", "&#x1F3C6; Highest Single-Day Traffic Potential",
        "A fun interactive tool with a shareable result image (Tinder for Music, Vibe Quiz) posted to r/InternetIsBeautiful on a Tuesday or Wednesday morning "
        "is the format most likely to hit 10,000+ visitors in a single day. The mechanism is simple: the result card gets shared to Twitter/X, then Instagram Stories, then re-posted back to Reddit. "
        "Each share brings new visitors who haven't seen it yet."))
    p.append(sec_close())
    return "".join(p)

def build_s12():
    p = []
    p.append(sec_open(12, "Gold Quotes Hall of Fame", "The best statements from the r/AppIdeas community"))
    p.append("""<div class="diamond">
<div class="diamond__label">&#x1F48E; Diamond Quote — The Traffic Playbook in 34 Words</div>
<div class="diamond__text">"At the beginning of 2024 I made the app free, and since then the number of users has been growing continuously. I just can't believe I'm about to hit 10,000 daily users."</div>
<div class="diamond__src">r/AppIdeas developer sharing their budget tracker growth story &middot; 542 pts</div>
<div class="diamond__use">The proof that the formula works. Use this as your north star when deciding whether to add a paywall.</div>
</div>""")

    gq = [
        ("the formula is dead simple: find someone describing a problem they'd pay to fix. check if others agree. check if current tools suck. build.",
         "285 pts post introducing the demand-proof methodology", "Read before picking your first idea to build."),
        ("The only things stopping you are fear and complexity. Pick the simplest version of the idea and launch it in a week.",
         "r/AppIdeas community support post, 61 pts", "The permission to ship an MVP instead of waiting for perfection."),
        ("I've been in this field for 10+ years. The most successful product I've seen is always the free thing that does one job better than the paid thing that does 20 jobs.",
         "r/AppIdeas experienced developer comment", "The core insight behind every Tier 1 idea in this report."),
        ("'This already exists' doesn't matter. As long as your version is better or free or simpler, having competitors is a sign there's space for many players.",
         "61 pts community support post — developer making 10K MRR", "The counter-argument to the 'someone's already built this' objection."),
        ("Stop pitching, start posting. The difference between 0 and 1,000 users is one Reddit post.",
         "r/SideProject cross-post referenced in dataset", "The distribution truth. Build the tool, write one good post, and see what happens."),
        ("I found 47 threads complaining about the same problem. That's not a coincidence. That's a product.",
         "r/AppIdeas idea compilation methodology post", "How to read this data for its real value."),
    ]
    for text, src, use in gq:
        p.append(gold_quote(text, src, use))

    p.append(sec_close())
    return "".join(p)

def build_s13():
    p = []
    p.append(sec_open(13, "Strategic Recommendations", "Prioritised from today to 30 days out"))
    p.append('<h3 style="font-size:0.88rem;color:var(--red);margin:14px 0 10px">&#x1F534; TODAY — Pick One Idea and Commit</h3>')
    p.append(rec("r", "Choose a Tier 1 idea and set a 3-day deadline",
        " — The biggest risk is analysis paralysis. This report has done the research. The invoice letter generator and pet med tracker both require under 200 lines of HTML/JS and have documented zero-competition at the free tier. The Reddit complaint miner takes slightly longer but drives traffic from the audience most likely to share developer tools. Pick one. Set a 72-hour deadline. Ship it."))
    p.append(rec("r", "Read the three most relevant posts in full",
        " — The 285 pt 'dead simple formula' post (redditappideas2.json), the 542 pt budget tracker growth story (redditappideas1.json), and the 175 pt subreddit promotion list (redditappideas6.json). These three posts contain the complete playbook. Budget 30 minutes."))
    p.append('<h3 style="font-size:0.88rem;color:var(--warn);margin:14px 0 10px">&#x1F7E1; THIS WEEK — Build and Post</h3>')
    p.append(rec("w", "Build the Tier 1 tool",
        " — No features beyond the core job. No account system. No analytics beyond basic page views. One input, one output, one Copy button. Ship it as a static HTML file first if needed — you can always upgrade the stack later."))
    p.append(rec("w", "Plan your Reddit post before you start building",
        " — Write the post title now: 'I built a free [X] for [specific audience]. No sign-up, no ads. [URL]' — one sentence. This discipline will shape what you build. If you can't summarise your tool in one sentence, it does too many things."))
    p.append(rec("w", "Set up a simple landing page that hosts the tool",
        " — Not a homepage. Not a portfolio. A page whose entire purpose is the tool. The URL should be youdomain.com/tool-name. This page is what Google indexes, what Reddit users share, what drives traffic to your site."))
    p.append('<h3 style="font-size:0.88rem;color:var(--primary-light);margin:14px 0 10px">&#x1F535; NEXT TWO WEEKS — Post and Iterate</h3>')
    p.append(rec("b", "Post to r/InternetIsBeautiful first, then the niche subs",
        " — Post r/InternetIsBeautiful in the morning (9–11am EST Tuesday/Wednesday for highest engagement). Within 24 hours post to the niche sub most relevant to the tool (r/freelance for invoice tool, r/petcare for pet tracker, etc.). Wait 48 hours before posting to a third sub."))
    p.append(rec("b", "Add a subtle link back to your main site from the tool page",
        " — One line in the footer: 'Made by [Your Name] &middot; [yoursite.com]'. Not a banner. Not a CTA. Just a credit link. Every person who uses the tool and likes it has a path to find you. This is the whole point."))
    p.append(rec("b", "Start building the Tier 2 tool of your choice while the first one runs",
        " — The traffic from tool #1 will peak and stabilise in 2–4 weeks. By then, tool #2 should be ready to create a second spike. Over 3–6 months, 3–4 live tools create compounding organic traffic that keeps growing without further effort."))
    p.append('<h3 style="font-size:0.88rem;color:var(--green);margin:14px 0 10px">&#x26AA; ONGOING — Compound the Traffic</h3>')
    p.append(rec("g", "Update the SaaS Price Tracker data monthly",
        " — If you build the price change tracker, updating it monthly with 2–3 new documented changes gives Google fresh content to rank and gives users a reason to share it again."))
    p.append(rec("g", "Check r/InternetIsBeautiful monthly for gaps",
        " — The most-shared tools on that subreddit show you exactly what your next build should be. If you see a gap — a useful free tool that doesn't exist yet — that's your next project."))
    p.append(rec("g", "Never add a sign-up wall to a traffic tool",
        " — The moment you add authentication to a traffic-driving tool, you cut your sharing rate by 60–80%. Keep the tool permanently free and permanently unauthenticated. If you want to monetise later, build a separate premium version — never gate the free one."))
    p.append(sec_close())
    return "".join(p)

def build_closing():
    p = []
    p.append('<div class="sec" id="close"><div class="sec__num">CLOSING — THE MANDATE</div><h2 class="sec__ttl">What This Data Means For You</h2><p class="sec__sub">The final word before you start building</p>\n')
    p.append("""<h3 style="font-size:0.95rem;color:var(--heading);margin:16px 0 12px">10 Things This Data Tells You</h3>
<ol style="font-size:0.84rem;line-height:2.2;color:var(--text);margin-left:20px;margin-bottom:28px">
<li><strong>Free is the strategy, not the compromise.</strong> The highest-traffic case in the dataset was a developer who made their app free and watched daily users grow to 9,347. Free is not failure — it's the traffic model.</li>
<li><strong>You don't need a new idea.</strong> Every idea in this report is already validated by Reddit complaint threads. The demand exists. The only question is whether you build the tool.</li>
<li><strong>One sentence is enough.</strong> Every successful post in the dataset describes the tool in one sentence. If you can't do that, build a simpler version.</li>
<li><strong>r/InternetIsBeautiful is the traffic machine.</strong> 17 million members, free to post, runs on web links. One well-timed post on a Tuesday morning can send more traffic than months of SEO.</li>
<li><strong>The shareable output is the marketing.</strong> A result card, a downloaded PDF, a copied letter — the thing the user takes away from your tool is the thing they share. Build the output before you build the interface.</li>
<li><strong>Boring beats clever for SEO.</strong> 'Free invoice late payment letter generator' ranks on Google. 'InvoiceFlow Pro' does not. The boring descriptive name wins organic traffic every time.</li>
<li><strong>Weekend builds outperform month-long projects for initial traffic.</strong> The Tier 1 tools — under 200 lines each — can be built, posted, and driving traffic within 5 days. Complexity is the enemy of shipping.</li>
<li><strong>The niche audience shares more reliably than the general audience.</strong> Pet owners share pet tools in pet communities. Freelancers share freelancer tools in freelancer communities. A targeted niche tool will get more sustained sharing than a generic tool posted once to r/InternetIsBeautiful.</li>
<li><strong>Traffic compounds.</strong> Tool 1 drives visitors. Some become return visitors. Some share it. Some Google it later and find it via SEO. Tool 2 adds to this base. By tool 4, you have an ecosystem of tools producing traffic 24 hours a day without further work.</li>
<li><strong>The only mistake is not shipping.</strong> The dataset contains dozens of posts from people who described a perfect idea in detail — and then never built it. The tool that generates traffic is the tool that exists at a URL. Build it this week.</li>
</ol>""")

    p.append("""<div class="diamond">
<div class="diamond__label">&#x1F48E; Diamond Quote — Your North Star</div>
<div class="diamond__text">"At the beginning of 2024 I made the app free, and since then the number of users has been growing continuously. I just can't believe I'm about to hit 10,000 daily users."</div>
<div class="diamond__src">r/AppIdeas developer &middot; 542 pts &middot; Budget Tracker Growth Story</div>
<div class="diamond__use">This developer did not optimise for revenue. They optimised for use. Traffic followed. That is the strategy.</div>
</div>""")

    p.append("""<h3 style="font-size:0.95rem;color:var(--heading);margin:20px 0 10px">&#x23F0; First 72 Hours</h3>
<ol class="action-list">
<li><strong>Pick one Tier 1 idea.</strong> The invoice escalation letter generator drives the most immediate search traffic. The pet medication tracker has the most passionate underserved audience. The Reddit complaint miner appeals most to developers. Choose based on which audience you want visiting your site.</li>
<li><strong>Write the title of your Reddit post first.</strong> "I built a free [X] for [Y audience]. No sign-up, works in the browser. [URL]" — This sentence defines what you build. If you can't write it yet, you haven't decided what the tool does.</li>
<li><strong>Build the output first.</strong> Start with the result — the letter, the PDF, the copied text, the downloaded image. Build the input form last. This ensures you ship something that produces the thing users want, rather than a form that leads to a loading spinner.</li>
<li><strong>Deploy to a subdirectory of your existing domain.</strong> yoursite.com/invoice-letter — not a subdomain, not a separate domain. The traffic you generate benefits your existing domain's authority.</li>
<li><strong>Post Tuesday or Wednesday 9–11am EST.</strong> This is when r/InternetIsBeautiful gets the most votes per post during the critical first hour. First-hour velocity determines whether you hit the front page.</li>
</ol>""")

    p.append("""<div class="mandate">
<p>You have 525 Reddit posts documenting exactly what people want and can't find.<br>
You have the formula: <strong>Free + Instant + One Job + Shareable Output</strong>.<br>
You have 7 ideas you can build this weekend and 7 more for this month.<br>
You have the subreddits where to post them.<br><br>
The only variable left is whether you build the first one.<br>
<strong>Start today. Ship by Friday. Post on Tuesday.</strong>
</p>
</div>""")
    p.append('</div>\n')
    return "".join(p)

print("All sections loaded.")

# ── Main assembler ─────────────────────────────────────────────────────────────
def main():
    gen = datetime.now().strftime("%d %B %Y")
    os.makedirs("outputs", exist_ok=True)
    print("Assembling report...")

    parts = [
        build_cover(),
        build_toc(),
        build_exec(),
        build_s1(),
        build_s2(),
        build_s3(),
        build_s4(),
    ]
    print("  Sections 1-4 done.")
    parts.append(build_s5())
    print("  Tier 1 done.")
    parts.append(build_s6())
    print("  Tier 2 done.")
    parts.append(build_s7())
    print("  Tier 3 done.")
    parts += [
        build_s8(),
        build_s9(),
        build_s10(),
        build_s11(),
        build_s12(),
        build_s13(),
        build_closing(),
    ]
    print("  Final sections done.")

    body = "\n".join(parts)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Web App Ideas That Drive Traffic — r/AppIdeas Intelligence Report · March 2026</title>
<style>{CSS}</style>
</head>
<body>
{body}
<div class="pg-foot">
  Generated by <strong>Audience Intelligence</strong> · <a href="https://audienceintelligence.com">audienceintelligence.com</a> · {gen}<br>
  r/AppIdeas Traffic-Driver Edition · 525 posts · Ultra-Prompt Framework
</div>
<div class="disclaimer">
DISCLAIMER: This report is produced for informational purposes only. All data sourced from publicly available Reddit posts via the Reddit public API.
Traffic estimates and viral scores are editorial assessments based on dataset analysis, not guaranteed outcomes.
For more information visit audienceintelligence.com.
</div>
</body>
</html>"""

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nSaved: {OUT_PATH}")
    print(f"Size:  {len(html):,} chars")

if __name__ == "__main__":
    main()
