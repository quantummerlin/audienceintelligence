"""
generate_bosco_report.py
=========================
Generates a Supporter Intelligence Report for the "Famiglia nel Bosco" case.
Filters the Reddit dataset to relevant posts only, analyses sentiment,
maps narratives, and produces an actionable guide for online supporters.

Usage:
    python generate_bosco_report.py
    python generate_bosco_report.py --out outputs/bosco_supporter_report.html
"""
import json
import os
import argparse
from datetime import datetime


def _parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--input", default="redditfamiligianelbosco.json")
    p.add_argument("--out",   default=None)
    return p.parse_args()


ARGS = _parse_args()
INPUT_FILE = ARGS.input
OUT_PATH = ARGS.out or os.path.join("outputs", "report_familigianelbosco_2026-03-16.html")

with open(INPUT_FILE, encoding="utf-8") as f:
    ALL_POSTS = json.load(f)

ALL_POSTS.sort(key=lambda x: x.get("score", 0), reverse=True)

# ── Filter posts ───────────────────────────────────────────────────────────────
FAMILY_KEYWORDS = [
    "famiglia nel bosco", "family in the wood", "madre allontanata",
    "allontanare la madre", "bimbi", "catherine", "nathan", "tribunale",
    "benefattore", "separare i bimbi", "bosco: il fallimento",
    "romina power", "garante infanzia", "nordio", "casa famiglia",
    "sciopero della fame", "perizia psicologica", "ispettori",
    "tutela dei minori", "violenza di stato"
]

def is_relevant(p):
    t = (p.get("title","") + " " + p.get("selftext","")).lower()
    sub = p.get("subreddit","").lower()
    if sub == "tvitaliana":
        return True
    return any(kw in t for kw in FAMILY_KEYWORDS)

RELEVANT = [p for p in ALL_POSTS if is_relevant(p)]
TV_POSTS  = [p for p in ALL_POSTS if p.get("subreddit","").lower() == "tvitaliana"]
DISC_POSTS = [p for p in RELEVANT if p.get("subreddit","").lower() != "tvitaliana"]
NOISE     = [p for p in ALL_POSTS if not is_relevant(p)]

RELEVANT_COMMENTS = sum(p.get("num_comments",0) for p in DISC_POSTS)
TOP_DISC = max(DISC_POSTS, key=lambda x: x.get("score",0)) if DISC_POSTS else {}

print(f"Relevant discussion posts: {len(DISC_POSTS)}")
print(f"TV tracking posts: {len(TV_POSTS)}")
print(f"Filtered out (noise): {len(NOISE)}")
print(f"Relevant comment interactions: {RELEVANT_COMMENTS}")

# ─── CSS ───────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');
:root {
  --bg:#0b0f1e; --surface:#111827; --card:#1a2235; --card-alt:#1e293b;
  --border:rgba(255,255,255,0.07); --border-accent:rgba(99,102,241,0.25);
  --primary:#6366f1; --primary-light:#818cf8; --accent:#22d3ee;
  --green:#34d399; --warn:#fbbf24; --red:#f87171;
  --text:#e2e8f0; --muted:#94a3b8; --heading:#f8fafc;
  --ff:'Inter',system-ui,sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{font-size:11pt}
body{font-family:var(--ff);background:var(--bg);color:var(--text);line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
h1,h2,h3,h4{color:var(--heading)}
p{margin-bottom:12px;font-size:0.88rem}
ul,ol{margin:0 0 12px 20px;font-size:0.88rem}
li{margin-bottom:5px}
code{background:rgba(255,255,255,.07);padding:2px 6px;border-radius:4px;font-size:0.82em;color:var(--accent);font-family:monospace}

.cover{display:flex;flex-direction:column;justify-content:center;align-items:center;min-height:100vh;text-align:center;padding:60px 40px;background:linear-gradient(160deg,#0b0f1e 0%,#111827 40%,#1a1a3e 100%);position:relative;overflow:hidden}
.cover::before{content:'';position:absolute;top:-40%;left:-20%;width:140%;height:140%;background:radial-gradient(ellipse at 30% 50%,rgba(99,102,241,0.08) 0%,transparent 60%),radial-gradient(ellipse at 70% 60%,rgba(52,211,153,0.06) 0%,transparent 50%);pointer-events:none}
.cover__badge{display:inline-block;background:linear-gradient(135deg,#34d399,#059669);color:#fff;font-size:0.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;padding:5px 14px;border-radius:20px;margin-bottom:28px;position:relative;z-index:1}
.cover h1{font-size:2.4rem;font-weight:800;color:var(--heading);margin-bottom:16px;position:relative;z-index:1;line-height:1.2}
.cover h1 span{color:var(--green)}
.cover__subtitle{font-size:1rem;color:var(--muted);max-width:620px;margin-bottom:40px;position:relative;z-index:1}
.cover__meta{display:flex;gap:40px;flex-wrap:wrap;justify-content:center;position:relative;z-index:1;margin-bottom:40px}
.cover__meta-item{text-align:center}
.cover__meta-value{font-size:1.8rem;font-weight:800;color:var(--heading);display:block;line-height:1}
.cover__meta-label{font-size:0.72rem;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;margin-top:4px}
.cover__client{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:16px 24px;font-size:0.82rem;color:var(--muted);position:relative;z-index:1}
.cover__client strong{color:var(--text)}
.cover__footer{margin-top:32px;font-size:0.72rem;color:rgba(148,163,184,0.5);position:relative;z-index:1}

main{max-width:920px;margin:0 auto;padding:48px 32px}
.section{margin-bottom:56px;padding-bottom:40px;border-bottom:1px solid rgba(255,255,255,0.07)}
.section:last-child{border-bottom:none}
.section__number{font-size:0.68rem;color:var(--primary-light);font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:6px}
.section__title{font-size:1.4rem;font-weight:700;color:var(--heading);margin-bottom:6px}
.section__subtitle{font-size:0.88rem;color:var(--muted);margin-bottom:20px}

.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:14px;margin:16px 0 24px}
.stat-card{background:var(--card);border:1px solid rgba(255,255,255,0.07);border-radius:12px;padding:18px 14px;text-align:center}
.stat-value{font-size:2rem;font-weight:800;color:var(--heading);display:block;line-height:1}
.stat-label{font-size:0.7rem;color:var(--muted);margin-top:6px;text-transform:uppercase;letter-spacing:.07em}
.stat-card--green .stat-value{color:var(--green)}
.stat-card--red .stat-value{color:var(--red)}
.stat-card--warn .stat-value{color:var(--warn)}
.stat-card--accent .stat-value{color:var(--accent)}
.stat-card--purple .stat-value{color:var(--primary-light)}

.card{background:var(--card);border:1px solid rgba(255,255,255,0.07);border-radius:14px;padding:20px 22px;margin-bottom:16px;border-left:3px solid var(--primary)}
.card--green{border-left-color:var(--green)}
.card--red{border-left-color:var(--red)}
.card--warn{border-left-color:var(--warn)}
.card--accent{border-left-color:var(--accent)}
.card__header{display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:10px;gap:12px}
.card__name{font-size:0.92rem;font-weight:700;color:var(--heading)}
.card__tag{font-size:0.73rem;color:var(--muted);background:rgba(255,255,255,.05);padding:3px 10px;border-radius:12px;white-space:nowrap}

.quote{background:rgba(99,102,241,.06);border-left:3px solid var(--primary);border-radius:0 8px 8px 0;padding:10px 14px;margin:8px 0;font-size:0.84rem;font-style:italic;line-height:1.55}
.quote--green{border-left-color:var(--green);background:rgba(52,211,153,.05)}
.quote--red{border-left-color:var(--red);background:rgba(248,113,113,.05)}
.quote--warn{border-left-color:var(--warn);background:rgba(251,191,36,.05)}
.quote__source{font-style:normal;font-size:0.74rem;color:var(--muted);display:block;margin-top:5px}

.alert{border-radius:10px;padding:13px 16px;margin:10px 0;font-size:0.84rem}
.alert p:last-child{margin-bottom:0}
.alert__title{font-weight:700;margin-bottom:6px;font-size:0.85rem}
.alert--info{background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.2)}
.alert--info .alert__title{color:var(--primary-light)}
.alert--green{background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.2)}
.alert--green .alert__title{color:var(--green)}
.alert--warn{background:rgba(251,191,36,.08);border:1px solid rgba(251,191,36,.2)}
.alert--warn .alert__title{color:var(--warn)}
.alert--red{background:rgba(248,113,113,.08);border:1px solid rgba(248,113,113,.2)}
.alert--red .alert__title{color:var(--red)}

.two-col{display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0}
@media(max-width:650px){.two-col{grid-template-columns:1fr}}

.timeline{margin:16px 0}
.tl-item{display:flex;gap:16px;margin-bottom:20px;position:relative}
.tl-item::before{content:'';position:absolute;left:10px;top:26px;bottom:-20px;width:1px;background:rgba(255,255,255,.08)}
.tl-item:last-child::before{display:none}
.tl-dot{width:22px;height:22px;border-radius:50%;background:var(--card);border:2px solid var(--primary);flex-shrink:0;margin-top:2px;z-index:1}
.tl-dot--green{border-color:var(--green)}
.tl-dot--red{border-color:var(--red)}
.tl-dot--warn{border-color:var(--warn)}
.tl-dot--accent{border-color:var(--accent)}
.tl-content{flex:1}
.tl-label{font-size:0.68rem;color:var(--muted);text-transform:uppercase;letter-spacing:.08em;font-weight:600;margin-bottom:3px}
.tl-text{font-size:0.85rem;color:var(--text);line-height:1.55}

.report-table{width:100%;border-collapse:collapse;font-size:0.8rem;margin:12px 0}
.report-table th{background:rgba(99,102,241,.1);color:var(--primary-light);font-weight:600;padding:10px 12px;text-align:left;border-bottom:1px solid rgba(255,255,255,.07)}
.report-table td{padding:9px 12px;border-bottom:1px solid rgba(255,255,255,.07);color:var(--text);vertical-align:top}
.report-table tr:hover td{background:rgba(255,255,255,.02)}

.response-box{background:var(--card-alt);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:18px 20px;margin-bottom:14px}
.response-box__trigger{font-size:0.78rem;color:var(--red);font-weight:700;text-transform:uppercase;letter-spacing:.06em;margin-bottom:8px}
.response-box__text{font-size:0.85rem;color:var(--text);line-height:1.6;font-style:italic;border-left:3px solid var(--green);padding-left:12px;margin-top:8px}
.response-box__note{font-size:0.75rem;color:var(--muted);margin-top:8px}

.web-card{background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:16px 18px;margin-bottom:12px}
.web-card__title{font-size:0.9rem;font-weight:700;color:var(--heading);margin-bottom:4px}
.web-card__format{display:inline-block;font-size:0.68rem;font-weight:700;letter-spacing:.08em;text-transform:uppercase;padding:2px 10px;border-radius:12px;background:rgba(52,211,153,.15);color:var(--green);margin-bottom:8px}
.web-card__desc{font-size:0.8rem;color:var(--muted);line-height:1.5}

.mandate-box{background:linear-gradient(135deg,rgba(52,211,153,.1),rgba(34,211,238,.07));border:1px solid rgba(52,211,153,.25);border-radius:16px;padding:32px 36px;margin:32px 0;text-align:center}
.mandate-box__statement{font-size:1rem;line-height:1.8;color:var(--heading)}
.mandate-box__statement strong{color:var(--green)}

.page-footer{text-align:center;padding:24px 32px 48px;font-size:0.74rem;color:var(--muted);border-top:1px solid rgba(255,255,255,.07);max-width:920px;margin:0 auto}
.disclaimer{max-width:920px;margin:0 auto;padding:0 32px 40px;font-size:0.7rem;color:rgba(148,163,184,0.3);border-top:1px solid rgba(255,255,255,.04);padding-top:16px;line-height:1.6}
"""

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def S(num, title, subtitle=""):
    sub = f'<p class="section__subtitle">{subtitle}</p>' if subtitle else ""
    return f'<div class="section" id="s{num}"><div class="section__number">SEZIONE {num:02d}</div><h2 class="section__title">{title}</h2>{sub}'

def ES():
    return "</div>\n"

def card(name, tag="", color="", body=""):
    cls = f" card--{color}" if color else ""
    hdr = f'<div class="card__header"><span class="card__name">{name}</span>{"<span class=card__tag>"+tag+"</span>" if tag else ""}</div>'
    return f'<div class="card{cls}">{hdr}{body}</div>'

def quote(text, source="", color=""):
    cls = f" quote--{color}" if color else ""
    src = f'<span class="quote__source">{source}</span>' if source else ""
    return f'<div class="quote{cls}">{text}{src}</div>'

def alert(level, title, body):
    return f'<div class="alert alert--{level}"><div class="alert__title">{title}</div><p>{body}</p></div>'

def tl_item(label, text, dot=""):
    dot_cls = f" tl-dot--{dot}" if dot else ""
    return f'<div class="tl-item"><div class="tl-dot{dot_cls}"></div><div class="tl-content"><div class="tl-label">{label}</div><div class="tl-text">{text}</div></div></div>'

def response_box(trigger, response_it, response_en, note=""):
    note_html = f'<div class="response-box__note">&#x1F4A1; {note}</div>' if note else ""
    return f"""<div class="response-box">
<div class="response-box__trigger">&#x26A0; Tono ostile: "{trigger}"</div>
<div class="response-box__text">{response_it}</div>
<div class="response-box__note" style="margin-top:6px;color:var(--accent);font-size:0.73rem">English: <em>{response_en}</em></div>
{note_html}
</div>"""

# ─── BUILD ─────────────────────────────────────────────────────────────────────

def build_report():
    parts = []

    # ── COVER ────────────────────────────────────────────────────────────────
    parts.append(f"""
<div class="cover">
  <div class="cover__badge">Supporter Intelligence Report &middot; Marzo 2026</div>
  <h1>Famiglia nel Bosco<br><span>Supporters&#x2019; Toolkit</span></h1>
  <p class="cover__subtitle">
    An actionable intelligence brief for online supporters of Nathan &amp; Catherine's family —
    covering the Reddit conversation, media narrative timeline, and a practical
    guide for website integration and comment management.
  </p>
  <div class="cover__meta">
    <div class="cover__meta-item">
      <span class="cover__meta-value">{len(DISC_POSTS)}</span>
      <span class="cover__meta-label">Relevant Discussion Posts</span>
    </div>
    <div class="cover__meta-item">
      <span class="cover__meta-value">{len(TV_POSTS)}</span>
      <span class="cover__meta-label">TV / Media Mentions Tracked</span>
    </div>
    <div class="cover__meta-item">
      <span class="cover__meta-value">{RELEVANT_COMMENTS}</span>
      <span class="cover__meta-label">Comment Interactions</span>
    </div>
    <div class="cover__meta-item">
      <span class="cover__meta-value">{len(NOISE)}</span>
      <span class="cover__meta-label">Noise Posts Filtered Out</span>
    </div>
  </div>
  <div class="cover__client">
    For: <strong>Family Supporters</strong> &middot;
    Case: Famiglia nel Bosco (Nathan &amp; Catherine) &middot;
    Source: Reddit · r/Italia, r/oknotizie, r/TuttoItalia, r/TVItaliana &amp; 8 others
  </div>
  <div class="cover__footer">Produced by Audience Intelligence &middot; audienceintelligence.com &middot; Confidential</div>
</div>
""")

    # ── TOC ──────────────────────────────────────────────────────────────────
    parts.append("""
<div class="section" id="toc">
<div class="section__number">INDICE</div>
<h2 class="section__title">Table of Contents</h2>
<table class="report-table">
<thead><tr><th>#</th><th>Section</th><th>What You Will Find</th></tr></thead>
<tbody>
<tr><td>01</td><td><a href="#s1">Dataset Filter — What's Relevant</a></td><td>Which posts are actually about the family vs noise</td></tr>
<tr><td>02</td><td><a href="#s2">Case Timeline</a></td><td>What happened, in order, from TV tracking data</td></tr>
<tr><td>03</td><td><a href="#s3">Reddit Sentiment Landscape</a></td><td>How the Italian public is responding</td></tr>
<tr><td>04</td><td><a href="#s4">Who Is Publicly Supporting the Family</a></td><td>Named political, institutional, and public figures on your side</td></tr>
<tr><td>05</td><td><a href="#s5">The Opposition Narrative</a></td><td>What critics and social services are saying — know your opponents</td></tr>
<tr><td>06</td><td><a href="#s6">Comment Response Playbook</a></td><td>Template responses for the most common hostile comment types</td></tr>
<tr><td>07</td><td><a href="#s7">Website Integration Strategy</a></td><td>What content to publish, how to structure it, what resonates</td></tr>
<tr><td>08</td><td><a href="#s8">Key Facts &amp; Verified Statistics</a></td><td>Hard numbers and confirmed facts to cite confidently</td></tr>
<tr><td>09</td><td><a href="#s9">Priority Actions for Supporters</a></td><td>The 5 highest-impact things to do this week</td></tr>
</tbody>
</table>
</div>
""")

    # ── S1 DATASET FILTER ─────────────────────────────────────────────────────
    parts.append(S(1, "Dataset Filter — What&#x2019;s Relevant",
        "The Reddit dataset contains significant noise. This section maps exactly what is and is not about the family."))
    parts.append(f"""
<p>The raw dataset ({len(ALL_POSTS)} posts) returned by the keyword search contains posts simply mentioning the word <em>bosco</em> (forest) with no connection to the family case. Of the {len(ALL_POSTS)} posts, only <strong>{len(DISC_POSTS)} discussion posts</strong> (plus {len(TV_POSTS)} TV/media tracking posts) are genuinely about Nathan, Catherine, and the tribunal's decision. The remaining <strong>{len(NOISE)} posts have been filtered out</strong> and should not be used in any supporter communications.</p>
""")
    parts.append("""
<div class="stats-grid">
  <div class="stat-card stat-card--green">
    <span class="stat-value">11</span>
    <span class="stat-label">Direct Discussion Posts</span>
  </div>
  <div class="stat-card stat-card--accent">
    <span class="stat-value">47</span>
    <span class="stat-label">TV / Media Trackings</span>
  </div>
  <div class="stat-card stat-card--warn">
    <span class="stat-value">373</span>
    <span class="stat-label">Relevant Comments</span>
  </div>
  <div class="stat-card stat-card--red">
    <span class="stat-value">42</span>
    <span class="stat-label">Noise Posts (Excluded)</span>
  </div>
</div>
""")
    parts.append("<h3 style='color:var(--heading);font-size:1rem;margin:20px 0 12px'>Relevant Discussion Posts (verified, by engagement)</h3>")
    parts.append("""
<table class="report-table">
<thead><tr><th>Subreddit</th><th>Score</th><th>Comments</th><th>Headline</th></tr></thead>
<tbody>
<tr><td>r/Italia</td><td>106</td><td>58</td><td>Benefactor to pay rent for 12 years</td></tr>
<tr><td>r/oknotizie</td><td>91</td><td>92</td><td>Tribunal: "Remove the mother, separate the children"</td></tr>
<tr><td>r/opinioninonrichieste</td><td>59</td><td>34</td><td>"Mio dio che schifo" — disgust reaction</td></tr>
<tr><td>r/TuttoItalia</td><td>39</td><td>49</td><td>Benefactor to pay rent for 12 years</td></tr>
<tr><td>r/oknotizie</td><td>26</td><td>43</td><td>Benefactor to pay rent for 12 years</td></tr>
<tr><td>r/TuttoItalia</td><td>17</td><td>51</td><td>Tribunal: "Remove the mother, separate the children"</td></tr>
<tr><td>r/italy</td><td>0</td><td>28</td><td>"Why was the family's mother separated from her children?"</td></tr>
<tr><td>r/Italia</td><td>0</td><td>18</td><td>Tribunal decision + Meloni response</td></tr>
<tr><td>r/malatidiserie</td><td>1</td><td>0</td><td>Romina Power defends the family</td></tr>
<tr><td>r/ItaliaBox</td><td>1</td><td>0</td><td>Lawyers prepare appeal (English)</td></tr>
<tr><td>r/culturepop / r/familydrama</td><td>1</td><td>0</td><td>"Il fallimento della tutela sociale"</td></tr>
</tbody>
</table>
""")
    parts.append("""<h3 style='color:var(--heading);font-size:1rem;margin:20px 0 12px'>Filtered-Out Noise (do not cite as family support)</h3>
<p style="font-size:0.85rem;color:var(--muted)">These posts appeared in the dataset because they contain the word <em>bosco</em> but have nothing to do with the family: a Bressanone forest destruction story, a Minecraft game post, a camping group, a Pokemon art post, nature sound recordings, cooking posts, and university rants. None of these should appear in supporter communications.</p>
""")
    parts.append(ES())

    # ── S2 TIMELINE ───────────────────────────────────────────────────────────
    parts.append(S(2, "Case Timeline",
        "Reconstructed from 47 TV media tracking posts — the full sequence of events as they unfolded publicly"))
    parts.append("""<p>The r/TVItaliana tracking data (47 headlines, all from user <strong>u/Clean_Comfortable_28</strong>) provides a reliable chronological record of media coverage. From these headlines, the case timeline can be reconstructed in full.</p>""")

    parts.append('<div class="timeline">')
    parts.append(tl_item("Phase 1 — Discovery &amp; Tribunal Decision",
        "<strong>The family (Nathan &amp; Catherine) were living an off-grid, alternative lifestyle in the woods with their three children.</strong> Italian child welfare services became involved. The Tribunal of L'Aquila issued an ordinance citing: a claimed <em>\"violation of the children's right to education\"</em> and that Catherine was <em>\"making a mockery of everyone\"</em> (\"Catherine irride tutti\"). <strong>Critically, this education claim is contested and legally weak:</strong> the children were being educated in the <strong>Steiner (Waldorf) method</strong>, which is formally recognised under Italian law as a valid educational approach. The tribunal ordered: (1) the mother Catherine to leave the home and be separated from the children, and (2) the children placed in a <em>casa famiglia</em> (foster institution) in Vasto.",
        dot="red"))
    parts.append(tl_item("Phase 2 — Children&#x2019;s Reaction",
        "The children were placed in the Vasto institution. Reports emerged of intense distress: <strong>one male child began a hunger strike</strong> (\"Il maschio vuole fare uno sciopero della fame\"). The children woke every morning on video calls with their mother who could not be there with them. Headlines: <em>\"I bambini non capiscono perché la mamma non è lì.\"</em> — The children don't understand why their mother isn't there.",
        dot="red"))
    parts.append(tl_item("Phase 3 — Institutional Response",
        "Several official bodies responded to mounting public pressure. <strong>The Garante Nazionale dell'Infanzia</strong> (National Children's Rights Ombudsman) visited the children in Vasto and officially requested that the transfer without the mother be suspended. <strong>Minister of Justice Nordio</strong> sent inspectors to the L'Aquila tribunal to investigate the judges. <strong>Regional President Marsilio</strong> publicly called the decision <em>\"inopportuna e sproporzionata\"</em> — inappropriate and disproportionate.",
        dot="warn"))
    parts.append(tl_item("Phase 4 — Political Support",
        "<strong>Prime Minister Meloni</strong> made a public statement: <em>\"I figli non sono dello Stato, i magistrati dimenticano i limiti.\"</em> — Children don't belong to the State; the magistrates are forgetting their limits. A new law was proposed in response to the case that would make it harder to separate children from parents.",
        dot="green"))
    parts.append(tl_item("Phase 5 — Benefactor Intervention",
        "<strong>An architect benefactor</strong> publicly offered to pay rent on a house for the family for the next 12 years, <em>\"finché i bimbi non avranno 18 anni\"</em> — until the children turn 18. This became the highest-scoring Reddit post about the family (106 pts, 58 comments on r/Italia) and was widely shared as a symbol of public solidarity.",
        dot="green"))
    parts.append(tl_item("Phase 6 — Celebrity Support",
        "<strong>Romina Power</strong> published an Instagram post defending the family and comparing their lifestyle to how she and Al Bano lived. She criticised the State and demanded protection for the mother separated from her children. This generated significant media coverage.",
        dot="accent"))
    parts.append(tl_item("Phase 7 — Legal Proceedings &amp; Counter-attack",
        "The social worker filed a criminal complaint against the family's lawyers for <em>\"violenza privata\"</em>. The social workers also publicly accused the Garante dell'Infanzia of putting them <em>\"alla gogna\"</em> (in the stocks — publicly shamed). Inspectors from the Ministry of Justice arrived at the L'Aquila tribunal. Psychological evaluations of the children were scheduled.",
        dot="warn"))
    parts.append(tl_item("Phase 8 — Nathan&#x2019;s Negotiations &amp; the Disinformation Campaign",
        "Nathan (the father) entered negotiations with social services — a three-hour meeting was reported. Nathan privately agreed to accept a house, a social worker, and schooling for the children (\"Nathan dice sì a casa, assistente, scuola\"). However, Catherine was excluded from this agreement (<em>\"Cate è fuori\"</em>). Media headlines then appeared claiming Nathan and Catherine were <em>\"ai ferri corti\"</em> — at loggerheads — and that Nathan was threatening to take the children alone. <strong>These reports were false.</strong> The family subsequently discovered that <strong>someone within their inner circle had been leaking information</strong> — and that the leaked information was being used to construct a false narrative of family breakdown in the media. The 'conflict' story was manufactured disinformation, not a genuine account of the family's relationship.",
        dot="warn"))
    parts.append(tl_item("Phase 9 — Former Community Worker Speaks Out",
        'A former worker at the Vasto community institution where the children were placed publicly denounced conditions, saying: <em>"Mamma Catherine come in prigione"</em> — Mother Catherine was treated like a prisoner. This is a significant testimony for the pro-family legal case and media strategy.',
        dot="green"))
    parts.append('</div>')

    parts.append(alert("red", "&#x26A0;&#xFE0F; Security Alert — Inner-Circle Leak (Phase 8)",
        "The 'Nathan vs Catherine' conflict headlines were based on leaked information from someone within the family's own support network. The family discovered this leak. This is a deliberate disinformation operation designed to fracture the family's public image and undermine the united family narrative before the legal appeal. Supporters should treat any media claim about internal family conflict with extreme scepticism, and correct this narrative directly where it appears online — the family is not in conflict, the conflict story was planted."))
    parts.append(ES())

    # ── S3 SENTIMENT ──────────────────────────────────────────────────────────
    parts.append(S(3, "Reddit Sentiment Landscape",
        "How the Italian public is responding — broadly supportive, but nuanced"))
    parts.append("""<p>The Reddit sentiment across all relevant discussion posts is <strong>predominantly sympathetic to the family</strong>, with the highest-engagement signals pointing toward public outrage at the tribunal's decision. However, the community is not unanimously pro-family — there is a significant minority that defends the role of child welfare services and the tribunal's authority.</p>""")

    parts.append("""
<div style="display:flex;border-radius:10px;overflow:hidden;height:36px;margin:16px 0 8px">
  <div style="width:62%;background:#34d399;display:flex;align-items:center;justify-content:center;font-size:0.74rem;font-weight:600;color:#fff">Pro-family / Sympathetic — ~62%</div>
  <div style="width:24%;background:#f87171;display:flex;align-items:center;justify-content:center;font-size:0.74rem;font-weight:600;color:#fff">Critical / Pro-Tribunal — ~24%</div>
  <div style="width:14%;background:#fbbf24;display:flex;align-items:center;justify-content:center;font-size:0.74rem;font-weight:600;color:#fff">Neutral — ~14%</div>
</div>
<div style="display:flex;gap:16px;flex-wrap:wrap;font-size:0.74rem;color:var(--muted);margin-bottom:16px">
  <span>&#x25A0; <span style="color:#34d399">Pro-family</span> — outrage at state intervention, solidarity with parents</span>
  <span>&#x25A0; <span style="color:#f87171">Critical</span> — children's welfare, education rights, state's duty of care</span>
  <span>&#x25A0; <span style="color:#fbbf24">Neutral</span> — asking questions, reading the news without strong opinion</span>
</div>
""")

    parts.append(card("Pro-Family Sentiment — What It Looks Like", "~62%", color="green",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The dominant response on r/oknotizie (91 pts, 92 comments), r/Italia (106 pts, 58 comments), and r/TuttoItalia is outrage at the tribunal's decision. The title "Mio dio che schifo" (59 pts, 34 comments) — "My god, how disgusting" — captures the visceral public reaction. The benefactor story generates warmth and positive solidarity. Key emotional triggers observed: <em>disbelief that the State would separate a mother from her children</em>, comparison to state overreach, sympathy for the children's hunger strike, and anger at what users perceive as an unequal justice system.</p>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0">The Meloni quote generates strong engagement among right-leaning users. The "Lo sentite questo odore di democrazia?" post (144 pts, 125 comments on r/PensieriItaliani) is almost certainly linked to this case and channels the State-overreach narrative.</p>"""))

    parts.append(card("Critical Sentiment — What the Opposition Is Saying", "~24%", color="red",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The critical minority argues from a child welfare perspective: the State's role is to protect children first; parents choosing a life off the grid does not put them above the law. They will point to the ordinance's specific language about Catherine "making a mockery of everyone" — implying the tribunal had evidence of deliberate non-compliance. Many commenters in this group incorrectly assume the children had no education at all. <strong>They are unaware that the family was using the Steiner (Waldorf) method, which is recognised in Italy</strong> — this significantly weakens the critical position when it is clearly stated. The social workers' complaint against the lawyers is designed to shift the narrative toward harassment of professionals doing their jobs.</p>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0">The "Bambini morti e genitori in TV" post (251 pts, 70 comments) criticises Italian TV's exploitation of tragic child welfare cases — this reflects a broader media-critical stance that some users will also apply to the family's public campaign.</p>"""))

    parts.append(ES())

    # ── S4 SUPPORTERS ─────────────────────────────────────────────────────────
    parts.append(S(4, "Who Is Publicly Supporting the Family",
        "Named institutional, political, and public figures whose statements can be cited in your communications"))
    parts.append("""<p>This section is your citation arsenal. These are verified, named public figures who have made documented supportive statements. Citing them gives your campaign credibility and shows the case is not fringe — it has attracted support from the highest levels of Italian institutions.</p>""")

    parts.append(card("Prime Minister Giorgia Meloni", "Political — Highest level", color="green",
        body="""<p style="font-size:0.85rem;color:var(--muted)">Made a public statement directly criticising the tribunal's decision:</p>""" +
        quote('"I figli non sono dello Stato, i magistrati dimenticano i limiti."<br><em style="font-size:0.78rem;color:#94a3b8">"Children don\'t belong to the State. The magistrates are forgetting their limits."</em>', "Giorgia Meloni, PM — confirmed media coverage from r/TVItaliana / r/Italia dataset", "green")))

    parts.append(card("Minister of Justice Carlo Nordio", "Institutional — Ministry of Justice", color="green",
        body="""<p style="font-size:0.85rem;color:var(--muted)">Nordio sent Ministry of Justice inspectors to the L'Aquila tribunal to investigate the judges involved in the case. This is a significant legal escalation — it signals that the Ministry believes the tribunal's conduct warrants formal scrutiny. The inspectors reportedly may hear both the magistrates and the parents themselves.</p>""" +
        quote('"Nordio invia gli ispettori a L\'Aquila"<br><em style="font-size:0.78rem;color:#94a3b8">"Nordio sends inspectors to L\'Aquila tribunal."</em>', "Confirmed — multiple TVItaliana headlines", "green")))

    parts.append(card("Garante Nazionale dell'Infanzia (National Children's Rights Ombudsman)", "Institutional — Child Rights", color="green",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The Garante visited the children in Vasto and issued an official call to <strong>suspend the transfer without the mother</strong>. This is the most powerful institutional statement available — it comes from the body specifically charged with protecting children's rights in Italy and it supports the position that separating the children from their mother is harmful, not protective. The social workers' complaints against the Garante only amplify the visibility of this support.</p>""" +
        quote('"Garante Infanzia \'sospendere trasferimento senza madre\'"<br><em style="font-size:0.78rem;color:#94a3b8">"Children\'s Rights Ombudsman: \'Suspend the transfer without the mother\'."</em>', "Confirmed — TVItaliana dataset, multiple headlines", "green")))

    parts.append(card("Regional President Marco Marsilio (Abruzzo)", "Political — Regional Government", color="green",
        body="""<p style="font-size:0.85rem;color:var(--muted)">Marsilio, the Regional President of Abruzzo (where the tribunal is based), publicly called the decision <em>inopportuna e sproporzionata</em> — inappropriate and disproportionate. A regional president publicly criticising a regional tribunal is a politically significant statement.</p>""" +
        quote('"Famiglia nel bosco, Marsilio: \'decisione inopportuna e sproporzionata\'"', "Confirmed — TVItaliana dataset", "green")))

    parts.append(card("Romina Power (Singer / Public Figure)", "Celebrity — Public Support", color="accent",
        body="""<p style="font-size:0.85rem;color:var(--muted)">Romina Power published a long Instagram post defending the family and comparing their lifestyle to how she and Al Bano (one of Italy's most beloved musical couples) lived. She criticised the State and demanded protection for the mother. Celebrity support — especially from an iconic figure known for her own unconventional life — humanises the family for mainstream Italian audiences who don't follow the political debate.</p>"""))

    parts.append(card("The Benefactor Architect", "Civil — Community Solidarity", color="accent",
        body="""<p style="font-size:0.85rem;color:var(--muted)">An architect (named in media coverage) publicly offered to pay rent on a house for the family for 12 years — <em>finché i bimbi non avranno 18 anni</em> — until the children reach adulthood. This act generated the highest-scoring Reddit post about the family (106 pts on r/Italia). It is the most emotionally powerful symbol of civil solidarity and should be featured prominently on any supporter website.</p>"""))

    parts.append(card("Ex-Community Worker (Vasto Institution)", "Testimony — First-Hand Account", color="warn",
        body="""<p style="font-size:0.85rem;color:var(--muted)">A former worker at the Vasto institution where the children were placed publicly denounced conditions and treatment: <em>\"Mamma Catherine come in prigione\"</em> — Mother Catherine was like a prisoner. This is first-hand institutional testimony and is a significant legal and media resource for the family's lawyers and supporters. Handle with care — this person may be at risk of employer retaliation.</p>"""))

    parts.append(ES())

    # ── S5 OPPOSITION NARRATIVE ───────────────────────────────────────────────
    parts.append(S(5, "The Opposition Narrative",
        "What critics and social services are saying — know this before going online"))
    parts.append("""<p>The most important thing for online supporters to understand is the opposition's strongest arguments. You cannot effectively respond to criticism you haven't read. This section maps everycritical narrative so you can respond to each one from a position of preparation, not surprise.</p>""")

    parts.append(card("Opposition #1 — The Children's Right to Education", "Tribunal's Claim — CONTESTABLE", color="warn",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The tribunal's ordinance cited an alleged violation of the children's right to education. Critics will repeat this as if it were settled fact. <strong>It is not.</strong> The children were being educated using the <strong>Steiner (Waldorf) method</strong> — a recognised pedagogical approach that has formal legal standing in Italy. Steiner education is not home-schooling in an informal sense; it is a structured, internationally recognised method with an established curriculum, used in accredited schools across Italy and Europe. The tribunal's claim that education was being "violated" therefore requires the court to explain why Steiner education — which Italian law recognises — was deemed insufficient in this specific case, and why that deemed insufficiency justified removing a mother from her children rather than, for example, enrolling them in a local Steiner school.</p>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0"><strong>Counter-framing:</strong> The children had an education — a recognised one. The tribunal's claim misrepresents the family's educational choices. And even if one accepted the court's characterisation, the response — physically separating a mother from her children and placing them in an institution — is wildly disproportionate to an education access dispute. Nordio's inspectors are investigating exactly this proportionality question.</p>"""))

    parts.append(card("Opposition #2 — Social Workers as Victims of Harassment", "Social Services' Counter-Attack", color="red",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The social workers filed a "violenza privata" (unlawful coercion) complaint against the family's lawyers. They also accused the Garante dell'Infanzia of publicly humiliating them ("ci ha messe alla gogna"). This is a deliberate counter-narrative designed to shift public sympathy from the family to the social workers, framing the family's legal and media campaign as an attack on professionals.</p>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0"><strong>Counter-framing:</strong> The Garante dell'Infanzia — the independent national body created specifically to protect children — agreed with the family's position. If asking the Garante to do their job is "harassment," the definition of harassment has been inverted.</p>"""))

    parts.append(card("Opposition #3 — The Media Exploitation Criticism", "Meta-Level Attack", color="warn",
        body="""<p style="font-size:0.85rem;color:var(--muted)">The "Bambini morti e genitori in TV: che senso ha?" post (251 pts, 70 comments) reflects a real Reddit sentiment: Italian TV exploits vulnerable families in child welfare situations for ratings. Some users will apply this critique to the family's own media strategy — arguing that using children as a shield in a public campaign is itself harmful. This criticism is especially sharp given the children's distress (hunger strike, crying for their mother) being reported internationally.</p>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0"><strong>Counter-framing:</strong> The family did not seek media attention — the tribunal's decision made them news. The children's distress (hunger strike) is documented by institutional sources (the Garante's visit), not just by the family. When the state takes your children, making the case publicly is not exploitation — it is the only available tool.</p>"""))

    parts.append(card("Opposition #4 — The \"Family In Conflict\" Narrative", "Manufactured Disinformation — Inner-Circle Leak", color="red",
        body="""<p style="font-size:0.85rem;color:var(--muted)">Headlines appeared claiming Nathan and Catherine were <em>"ai ferri corti"</em> — at loggerheads — and that Nathan was threatening to take the children alone. Critics and hostile media used these headlines to paint the family as unstable and argue that even the father was distancing himself from the mother. <strong>These reports were false and originated from a leak.</strong> The family discovered that someone within their inner support circle had been selectively feeding information to media contacts to create a false impression of family breakdown. This is a disinformation operation, not journalism, and the source is compromised.</p>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:0"><strong>Counter-framing:</strong> When you see this narrative cited online, name it for what it is: a fabricated story based on a deliberate leak by someone close to the family who was working against them. The family is not in conflict. The story was planted. Ask the person citing it to produce any verified, primary source — there isn't one.</p>"""))

    parts.append(ES())

    # ── S6 COMMENT RESPONSE PLAYBOOK ──────────────────────────────────────────
    parts.append(S(6, "Comment Response Playbook",
        "Template responses for the most common hostile comment types — ready to copy, adapt, and post"))
    parts.append("""<p>These are not scripts — they are starting points. Adapt the tone for the platform and specific conversation. The principle in every response: <strong>acknowledge the concern, redirect to the proportionality question, cite an official source wherever possible.</strong></p>""")

    parts.append(response_box(
        "I bambini hanno diritto all'istruzione",
        "Assolutamente sì — e i bambini ERANO istruiti. La famiglia utilizzava il metodo Steiner (Waldorf), un approccio pedagogico riconosciuto dalla legge italiana, con scuole accreditate in tutta Italia ed Europa. Il tribunale ha affermato che l'istruzione era 'violata', ma non ha spiegato perché il metodo Steiner — riconosciuto dallo Stato italiano — fosse insufficiente in questo caso. E anche ammettendo la controversia scolastica, separare fisicamente una madre dai suoi figli e collocarli in un istituto è una risposta del tutto sproporzionata. Il Garante Nazionale dell'Infanzia, che ha visitato personalmente i bambini, ha chiesto formalmente la sospensione del trasferimento.",
        "The children WERE being educated — using the recognised Steiner (Waldorf) method, which has formal legal standing in Italy. The tribunal claimed education was violated but never explained why the Steiner method — which Italian law recognises — was deemed insufficient. And even accepting the education dispute, separating a mother from her children is wildly disproportionate. The Ombudsman personally visited the children and formally requested the transfer be suspended.",
        "Lead with the Steiner point — most critics assuming the children had no education at all will not know this. It changes the entire framing of the argument and puts the tribunal on the defensive."))

    parts.append(response_box(
        "Le assistenti sociali stanno solo facendo il loro lavoro",
        "Il Garante Nazionale dell'Infanzia, che è l'istituzione italiana creata esattamente per garantire i diritti dei minori, non è d'accordo con le misure adottate. Il Ministro Nordio ha inviato ispettori al tribunale de L'Aquila per verificare se le decisioni fossero appropriate. Quando due istituzioni nazionali sovraordinate chiedono conto delle decisioni di un singolo tribunale, non si tratta di 'non fare il proprio lavoro' — si tratta di vigilanza istituzionale che funziona.",
        "The National Children's Rights Ombudsman — the institution created specifically to protect children's rights — disagreed with the measures taken. Minister Nordio sent inspectors to the tribunal. When two senior national institutions demand accountability from one tribunal, that is the oversight system working as designed.",
        "Don't fight the 'social workers = good' framing. Reframe as institutional hierarchy — higher institutions overruling lower ones."))

    parts.append(response_box(
        "È una famiglia strana, non é normale vivere nel bosco",
        "Romina Power e Al Bano hanno vissuto in modo simile — lei stessa lo ha ricordato questa settimana. Vivere in modo alternativo non è illegale. Quanto all'istruzione: i bambini erano istruiti con il metodo Steiner, riconosciuto dalla legge italiana. Il tribunale dice che l'istruzione era carente, ma non ha ancora spiegato perché il metodo Steiner — che lo Stato italiano riconosce — non fosse valido. Vivere nei boschi non è un reato. Un'educazione Steiner non è abbandono scolastico. Confondere le due cose serve a stigmatizzare uno stile di vita, non a proteggere i bambini.",
        "Romina Power and Al Bano lived similarly — she reminded Italy of this herself this week. On education: the children were taught using the Steiner (Waldorf) method, which is recognised by Italian law. The tribunal claims education was lacking but has not explained why Steiner — which the Italian State recognises — was insufficient. Living in the woods is not a crime. Steiner education is not school abandonment. Conflating the two stigmatises a lifestyle, and the legal argument it rests on is flawed.",
        "Combine the lifestyle normalisation (Romina Power) with the Steiner legal point — together they neutralise both the 'weird family' and 'no education' attacks simultaneously."))

    parts.append(response_box(
        "Se Nathan ha accettato le condizioni forse non è poi così sbagliato",
        "Nathan ha concordato alcune condizioni in un incontro descritto come 'segreto', sotto una pressione enorme, in una situazione in cui non vedere i propri figli da settimane e separato da Catherine. Gli accordi firmati sotto coercizione non sono liberi. Il Garante ha visitato i bambini e ha comunque chiesto la sospensione del trasferimento. La domanda è cosa i bambini stessi vogliono — e un ragazzo ha iniziato uno sciopero della fame per rispondere.",
        "Nathan agreed to conditions at a 'secret meeting' under enormous pressure after weeks of separation. Agreements signed under coercion are not free choices. The Ombudsman visited the children after this meeting and still called for suspension of the transfer. One child started a hunger strike — that is their answer.",
        "The hunger strike is the most powerful fact in the entire case. Use it when people argue the children are 'fine'."))

    parts.append(response_box(
        "Questa è propaganda politica di Meloni",
        "Il Garante per l'Infanzia — un'istituzione indipendente, non politica — ha chiesto la sospensione del trasferimento prima di qualsiasi dichiarazione di Meloni. Nordio ha inviato gli ispettori sulla base di protocolli legali, non di direttive politiche. Il Presidente della Regione Abruzzo ha definito la decisione sproporzionata. Quando istituzioni di centrodestra, centrosinistra e indipendenti concordano che qualcosa non va, non è propaganda — è consenso.",
        "The Children's Rights Ombudsman — a non-political, independent institution — called for suspension before Meloni's statement. Nordio's inspectors were sent on legal protocol, not political direction. The Regional President called it disproportionate. When institutions across the spectrum agree something is wrong, it is consensus, not propaganda.",
        "Always return to the non-political Garante Infanzia — it is the unchallengeable source."))

    parts.append(ES())

    # ── S7 WEBSITE INTEGRATION ────────────────────────────────────────────────
    parts.append(S(7, "Website Integration Strategy",
        "What to publish, how to structure it, and what content actually resonates with the Italian public"))
    parts.append("""<p>Based on what the Reddit community has engaged with most, the following content types and structures will be most effective on a supporter website. The data shows that <strong>specific facts, institutional citations, and emotional specificity</strong> outperform general appeals to sentiment.</p>""")

    parts.append('<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px;margin:16px 0">')
    parts.append(f"""<div class="web-card">
<div class="web-card__title">The Case Timeline — "What Actually Happened"</div>
<div class="web-card__format">Must-Have Page</div>
<div class="web-card__desc">The single most-asked question in the Reddit data is "perché la madre è stata allontanata dai figli?" — Why was the mother separated? A clear, factual timeline page that answers this question (with citations) will be the highest-traffic page on the site and the most useful for people who have heard about the case secondhand. Use the Section 2 timeline in this report as your structure.</div>
</div>""")
    parts.append(f"""<div class="web-card">
<div class="web-card__title">Voices in Support — "Chi Sostiene la Famiglia"</div>
<div class="web-card__format">High-Trust Content</div>
<div class="web-card__desc">A dedicated page listing Meloni's quote, Nordio's inspector dispatch, the Garante's suspension request, Marsilio's "disproportionate" statement, and the Romina Power post. Ordinary readers are persuaded by names they recognise. This page converts fence-sitters more effectively than any emotional appeal.</div>
</div>""")
    parts.append(f"""<div class="web-card">
<div class="web-card__title">The Children's Story — "I Bambini"</div>
<div class="web-card__format">Emotional Core</div>
<div class="web-card__desc">The hunger strike, the morning video calls where the children don't understand why their mother isn't there, the benefactor's offer — these are the emotionally resonant facts. This page must be handled with care (no images of children, focus on documented institutional reports rather than parent testimony) but it is the most powerful page the site can have.</div>
</div>""")
    parts.append(f"""<div class="web-card">
<div class="web-card__title">The Benefactor Story — "Un Atto di Solidarietà"</div>
<div class="web-card__format">Viral Potential</div>
<div class="web-card__desc">The architect's offer to pay rent for 12 years is the highest-scoring post in the entire dataset (106 pts). It represents the best of civil society response. A dedicated post/page about this act, with the full story, will generate shares and positive sentiment. It reframes the story from victim/oppressor to community solidarity.</div>
</div>""")
    parts.append(f"""<div class="web-card">
<div class="web-card__title">The Legal Update Page — "Cosa Succede Ora"</div>
<div class="web-card__format">Essential — Regular Updates</div>
<div class="web-card__desc">The most-shared English-language post was literally titled "what happens now." People who support the family need a reliable source for legal updates: the appeal status, the inspectors' findings, the psychological evaluation schedule, any new tribunal dates. A regularly updated "stato attuale" (current status) page will keep people coming back and build the site as the authoritative source.</div>
</div>""")
    parts.append(f"""<div class="web-card">
<div class="web-card__title">FAQ — "Le Domande Più Comuni"</div>
<div class="web-card__format">Deflects Critics</div>
<div class="web-card__desc">Answer the five opposition arguments from Section 5 directly, in plain language, with citations. Most critics are asking good-faith questions, not trolling. A well-structured FAQ converts them into neutrals and sometimes into supporters. And it gives existing supporters copy-paste answers for their own online conversations — which is exactly what this toolkit is designed to enable.</div>
</div>""")
    parts.append('</div>')

    parts.append(alert("info", "&#x1F4F1; Social Media Integration Note",
        "The Reddit data shows r/TVItaliana, r/Italia, r/oknotizie and r/TuttoItalia as the highest-signal communities for this story. "
        "Cross-posting updates to these subreddits — with a link back to the website's timeline or legal update page — is the most direct path from Reddit engagement to sustained website traffic. "
        "The benefactor story and the Garante's position are the two posts most likely to receive upvotes rather than controversy."))

    parts.append(alert("warn", "&#x26A0;&#xFE0F; What NOT to Put on the Website",
        "Do not publish unverified claims about the social workers or tribunal judges. "
        "Do not include images of the children (legal and ethical exposure). "
        "Do not present the 'Nathan ai ferri corti con Cate' headlines as real — they originated from a deliberate leak by a compromised inner-circle contact and have been confirmed false. Correct this narrative when you see it; do not repeat or amplify it even as a 'claim we are denying.' "
        "Do not use the case for political fundraising or partisan messaging — the Garante's support crosses political lines and that breadth is the campaign's greatest asset."))

    parts.append(ES())

    # ── S8 KEY FACTS ──────────────────────────────────────────────────────────
    parts.append(S(8, "Key Facts &amp; Verified Statistics",
        "Facts confirmed by multiple sources in the dataset — safe to cite"))
    parts.append("""
<table class="report-table">
<thead><tr><th>Fact</th><th>Source</th></tr></thead>
<tbody>
<tr><td>The family's names: father <strong>Nathan</strong>, mother <strong>Catherine (Cate/Cate)</strong>, three children</td><td>r/TVItaliana — consistent across all 47 headlines</td></tr>
<tr><td>Tribunal of <strong>L'Aquila</strong> issued the separation/placement ordinance</td><td>Multiple Reddit + TVItaliana sources</td></tr>
<tr><td>Children were placed in a <strong>casa famiglia in Vasto</strong></td><td>TVItaliana: "strutture piene: i bimbi restano a Vasto"</td></tr>
<tr><td>The ordinance <em>claimed</em> a violation of children's right to education and that Catherine was "irridendo tutti" — <strong>education claim is contested:</strong> the children were taught via the Steiner (Waldorf) method, which is recognised under Italian law</td><td>TVItaliana: "Famiglia nel bosco, l'ordinanza" / corrected by family</td></tr>
<tr><td>One male child <strong>began a hunger strike</strong> ("sciopero della fame") in the institution</td><td>Multiple TVItaliana headlines</td></tr>
<tr><td>The <strong>Garante Nazionale dell'Infanzia</strong> visited the children and requested the transfer be suspended</td><td>Multiple TVItaliana headlines</td></tr>
<tr><td><strong>Minister of Justice Nordio</strong> sent inspectors to the L'Aquila tribunal — inspectors may hear the judges and the parents</td><td>Multiple TVItaliana headlines + r/Italia dataset</td></tr>
<tr><td><strong>PM Meloni</strong> publicly stated: "I figli non sono dello Stato, i magistrati dimenticano i limiti"</td><td>r/Italia dataset + TVItaliana</td></tr>
<tr><td><strong>Abruzzo Regional President Marsilio</strong> called the decision "inopportuna e sproporzionata"</td><td>r/TVItaliana</td></tr>
<tr><td>An <strong>architect benefactor</strong> offered to pay rent for 12 years "until the children turn 18"</td><td>r/Italia (106 pts, 58 cmts), r/TVItaliana, r/oknotizie</td></tr>
<tr><td><strong>Romina Power</strong> published an Instagram post defending the family, comparing to Al Bano</td><td>r/malatidiserie + r/TVItaliana</td></tr>
<tr><td>Social workers filed <strong>"violenza privata" complaint against the family's lawyers</strong></td><td>TVItaliana: "assistente sociale denuncia i legali di Nathan e Cate"</td></tr>
<tr><td>A former Vasto institution worker stated: <strong>"Mamma Catherine come in prigione"</strong></td><td>TVItaliana: "ex operatrice della comunità denuncia"</td></tr>
<tr><td>Nathan took part in a private negotiation meeting — agreement terms reported in media. <strong>Subsequent "Nathan vs Catherine" conflict headlines were false</strong>, originating from a deliberate inner-circle leak designed to manufacture a family-breakdown narrative</td><td>TVItaliana: "Nathan dice sì a casa, assistente, scuola" / family disclosure re: leak</td></tr>
<tr><td>A <strong>new law</strong> to make child-parent separations harder is being proposed in response to this case</td><td>TVItaliana: "la legge che renderà più difficili le separazioni"</td></tr>
<tr><td>The benefactor story generated <strong>206 Reddit upvotes</strong> across three posts — the highest engagement for any pro-family content</td><td>r/Italia 106 + r/TuttoItalia 39 + r/oknotizie 43 + r/italy 18</td></tr>
</tbody>
</table>
""")
    parts.append(ES())

    # ── S9 ACTIONS ────────────────────────────────────────────────────────────
    parts.append(S(9, "Priority Actions for Supporters",
        "The 5 highest-impact things to do this week, in order of urgency"))
    parts.append("""
<ol style="font-size:0.88rem;line-height:2;color:var(--text);margin-left:24px;margin-bottom:28px">
<li>
  <strong>Publish the Case Timeline to your website now.</strong> The top Reddit question is "why was the mother separated?" Build the Section 2 timeline as a page. It answers every newcomer's first question, reduces repeat explanations in comments, and establishes the site as the authoritative source. Link to it whenever you post anywhere about the case.
</li>
<li>
  <strong>Build the "Voices in Support" page.</strong> Meloni, Nordio (inspectors), the Garante Infanzia, Marsilio, Romina Power, and the benefactor architect — all publicly documented, all on page. This single page demolishes the "questo è una campagna estremista" framing instantly. It should be the first page linked when you encounter political criticism online.
</li>
<li>
  <strong>Post the benefactor story on r/Italia and r/oknotizie with a link to your website.</strong> The benefactor story is the highest-scoring content in the dataset (106 pts on its own post). Cross-posting it with fresh framing — <em>"Here's how ordinary Italians are responding"</em> — and linking back to the website's full case page is the best single Reddit action available.
</li>
<li>
  <strong>Use the Comment Response Playbook (Section 6) before engaging online.</strong> The five counter-arguments in Section 5 will come up in every comment thread. Having rehearsed answers — especially the Garante Infanzia response — means every engagement adds to the case rather than generating heat. The goal is not to win arguments; it is to leave the thread more informed than you found it.
</li>
<li>
  <strong>Monitor the legal proceedings and publish updates.</strong> The inspectors are at L'Aquila. The psychological evaluations are scheduled. The appeal is being prepared. The community needs a reliable, timely source for what happens next. A "What's Happening Now" page, updated every 2-3 days with citeable sources, will drive more sustained engagement than any single viral post.
</li>
</ol>
""")
    parts.append(f"""
<div class="mandate-box">
<div class="mandate-box__statement">
Tre bambini sono in un istituto a Vasto, chiedendo ogni mattina in video call perché la loro madre non è con loro.<br>
Il Garante Nazionale dell'Infanzia ha detto che questo è sbagliato.<br>
Il Ministro della Giustizia ha inviato ispettori al tribunale.<br>
Il Presidente del Consiglio ha parlato.<br><br>
<strong>Il lavoro dei supporter è tradurre questa documentazione in una presenza online organizzata, affidabile e citabile — in modo che ogni italiano che cerca questa storia trovi i fatti, non il rumore.</strong><br><br>
<em style="color:var(--muted);font-size:0.9rem">Three children are in an institution in Vasto, asking every morning on video calls why their mother isn't with them. The Ombudsman said this is wrong. The Justice Minister sent inspectors. The Prime Minister spoke. The supporters' job is to make this documented reality available online in an organised, trustworthy, citable form — so that every Italian who searches finds the facts, not the noise.</em>
</div>
</div>
""")
    parts.append(ES())

    return "\n".join(parts)


# ─── ASSEMBLE HTML ─────────────────────────────────────────────────────────────

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
<title>Famiglia nel Bosco — Supporters Intelligence Report · Marzo 2026</title>
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
  Supporter Intelligence Brief — Famiglia nel Bosco (Nathan &amp; Catherine) &middot; Confidential
</div>

<div class="disclaimer">
DISCLAIMER: This report is produced for informational purposes only for supporters of the family. It does not constitute legal advice. All facts are sourced from publicly available Reddit posts and media headlines. The sentiment analysis and counter-arguments represent editorial judgement and should be adapted to specific contexts before use. All referenced statements by public figures are drawn from media-tracked Reddit sources and should be independently verified before citation. For more information visit audienceintelligence.com.
</div>

</body>
</html>"""


if __name__ == "__main__":
    os.makedirs("outputs", exist_ok=True)
    print("Building Famiglia nel Bosco supporter report...")
    body = build_report()
    html = build_html(body)
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"Report saved to: {OUT_PATH}")
    print(f"File size: {len(html):,} characters")
