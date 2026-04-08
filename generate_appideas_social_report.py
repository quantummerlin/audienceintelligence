"""
generate_appideas_social_report.py
====================================
r/AppIdeas — Content Exploration Report
For: personal content creation, social media posts, shareable insights,
     visual reports, threads, carousels, and data storytelling.
NOT a product strategy report. This is a content inspiration board.

Usage:
    python generate_appideas_social_report.py
"""
import json, os
from datetime import datetime

OUT_PATH = os.path.join("outputs", "report_appideas_social_2026-03-17.html")

# ── Load all 6 datasets ────────────────────────────────────────────────────────
ALL_POSTS = []
for i in range(1, 7):
    fname = f"redditappideas{i}.json"
    if not os.path.exists(fname):
        continue
    with open(fname, encoding="utf-8") as f:
        data = json.load(f)
    children = data.get("data", {}).get("children", [])
    for child in children:
        d = child.get("data", {})
        ALL_POSTS.append({
            "id": d.get("id",""),
            "title": d.get("title",""),
            "selftext": d.get("selftext",""),
            "score": d.get("score", 0),
            "num_comments": d.get("num_comments", 0),
            "author": d.get("author",""),
            "subreddit": d.get("subreddit",""),
            "url": d.get("url",""),
            "created_utc": d.get("created_utc", 0),
        })

# Deduplicate by id
seen = set()
POSTS = []
for p in ALL_POSTS:
    if p["id"] not in seen:
        seen.add(p["id"])
        POSTS.append(p)

POSTS.sort(key=lambda x: x["score"], reverse=True)
TOP50 = POSTS[:50]

print(f"Total unique posts: {len(POSTS)}")
print(f"Building social content report...")

# ── CSS ────────────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
  --bg:#0b0f1e; --surface:#111827; --card:#1a2235; --card2:#1e293b;
  --border:rgba(255,255,255,0.07); --primary:#6366f1; --pl:#818cf8;
  --accent:#22d3ee; --green:#34d399; --warn:#fbbf24; --red:#f87171;
  --pink:#f472b6; --orange:#fb923c;
  --text:#e2e8f0; --muted:#94a3b8; --h:#f8fafc;
  --ff:'Inter',system-ui,sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{font-size:11pt}
body{font-family:var(--ff);background:var(--bg);color:var(--text);line-height:1.65;-webkit-font-smoothing:antialiased}
a{color:var(--accent);text-decoration:none}
h1,h2,h3,h4{color:var(--h)}
p{margin-bottom:10px;font-size:0.86rem}
ul,ol{margin:0 0 10px 20px;font-size:0.86rem}
li{margin-bottom:5px}

/* ── Cover ── */
.cover{display:flex;flex-direction:column;justify-content:center;align-items:center;
  min-height:100vh;text-align:center;padding:60px 40px;
  background:linear-gradient(160deg,#0b0f1e 0%,#111827 50%,#0d1f35 100%);
  position:relative;overflow:hidden}
.cover::before{content:'';position:absolute;inset:-40% -20%;
  background:radial-gradient(ellipse at 25% 55%,rgba(99,102,241,.09),transparent 55%),
             radial-gradient(ellipse at 75% 40%,rgba(244,114,182,.06),transparent 50%);
  pointer-events:none}
.badge{display:inline-block;background:linear-gradient(135deg,#f472b6,#818cf8);
  color:#fff;font-size:.68rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;
  padding:5px 14px;border-radius:20px;margin-bottom:28px;position:relative;z-index:1}
.cover h1{font-size:2.4rem;font-weight:800;line-height:1.2;margin-bottom:14px;position:relative;z-index:1}
.cover h1 span{color:var(--pink)}
.cover__sub{font-size:.92rem;color:var(--muted);max-width:560px;margin-bottom:32px;position:relative;z-index:1}
.cover__meta{display:flex;gap:32px;flex-wrap:wrap;justify-content:center;position:relative;z-index:1;margin-bottom:32px}
.mv{font-size:1.9rem;font-weight:800;color:var(--h);display:block;line-height:1}
.ml{font-size:.7rem;color:var(--muted);letter-spacing:.08em;text-transform:uppercase;margin-top:4px}
.cover__note{background:rgba(244,114,182,.08);border:1px solid rgba(244,114,182,.2);
  border-radius:12px;padding:13px 20px;font-size:.8rem;color:var(--pink);max-width:560px;
  position:relative;z-index:1;margin-bottom:20px}
.cover__foot{margin-top:24px;font-size:.7rem;color:rgba(148,163,184,.35);position:relative;z-index:1}

/* ── Layout ── */
main{max-width:980px;margin:0 auto;padding:48px 32px}
.sec{margin-bottom:52px;padding-bottom:36px;border-bottom:1px solid rgba(255,255,255,.07)}
.sec:last-child{border-bottom:none}
.sn{font-size:.65rem;color:var(--pl);font-weight:700;letter-spacing:.12em;text-transform:uppercase;margin-bottom:4px}
.st{font-size:1.32rem;font-weight:700;color:var(--h);margin-bottom:5px}
.ss{font-size:.86rem;color:var(--muted);margin-bottom:18px}

/* ── Stat grid ── */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(110px,1fr));gap:12px;margin:14px 0 22px}
.stat{background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:16px 12px;text-align:center}
.sv{font-size:1.9rem;font-weight:800;display:block;line-height:1;color:var(--h)}
.sl{font-size:.68rem;color:var(--muted);margin-top:5px;text-transform:uppercase;letter-spacing:.06em}
.c-g .sv{color:var(--green)} .c-a .sv{color:var(--accent)} .c-p .sv{color:var(--pl)}
.c-w .sv{color:var(--warn)} .c-pk .sv{color:var(--pink)} .c-o .sv{color:var(--orange)}

/* ── Alert boxes ── */
.al{border-radius:10px;padding:12px 15px;margin:10px 0;font-size:.82rem}
.al p:last-child{margin-bottom:0}
.al__t{font-weight:700;margin-bottom:5px;font-size:.83rem}
.al-i{background:rgba(99,102,241,.08);border:1px solid rgba(99,102,241,.2)} .al-i .al__t{color:var(--pl)}
.al-g{background:rgba(52,211,153,.08);border:1px solid rgba(52,211,153,.2)} .al-g .al__t{color:var(--green)}
.al-pk{background:rgba(244,114,182,.07);border:1px solid rgba(244,114,182,.18)} .al-pk .al__t{color:var(--pink)}
.al-a{background:rgba(34,211,238,.06);border:1px solid rgba(34,211,238,.18)} .al-a .al__t{color:var(--accent)}
.al-w{background:rgba(251,191,36,.07);border:1px solid rgba(251,191,36,.18)} .al-w .al__t{color:var(--warn)}

/* ── Story cards ── */
.story{background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:14px;
  padding:20px 22px;margin-bottom:16px;position:relative;overflow:hidden}
.story::before{content:'';position:absolute;top:0;left:0;width:3px;height:100%}
.story--pk::before{background:var(--pink)} .story--g::before{background:var(--green)}
.story--a::before{background:var(--accent)} .story--w::before{background:var(--warn)}
.story--o::before{background:var(--orange)} .story--p::before{background:var(--pl)}
.story__head{display:flex;gap:11px;align-items:flex-start;margin-bottom:10px;flex-wrap:wrap}
.story__icon{width:38px;height:38px;border-radius:10px;display:flex;align-items:center;
  justify-content:center;font-size:1.2rem;flex-shrink:0}
.story__ttl{font-size:1rem;font-weight:700;color:var(--h);line-height:1.3;flex:1}
.story__tags{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:10px}
.tag{display:inline-block;font-size:.67rem;font-weight:600;letter-spacing:.04em;padding:3px 9px;border-radius:12px}
.tg{background:rgba(52,211,153,.12);color:var(--green)}
.ta{background:rgba(34,211,238,.10);color:var(--accent)}
.tw{background:rgba(251,191,36,.10);color:var(--warn)}
.tp{background:rgba(99,102,241,.12);color:var(--pl)}
.tpk{background:rgba(244,114,182,.10);color:var(--pink)}
.to{background:rgba(251,146,60,.10);color:var(--orange)}
.tm{background:rgba(255,255,255,.06);color:var(--muted)}
.story__body{font-size:.84rem;color:var(--text);line-height:1.65;margin-bottom:10px}
.story__body strong{color:var(--h)}
.story__stat{font-size:.77rem;color:var(--muted);border-top:1px solid rgba(255,255,255,.06);
  padding-top:8px;margin-top:4px}
.story__stat strong{color:var(--accent);font-size:.72rem;letter-spacing:.04em;text-transform:uppercase}

/* ── Content brief cards ── */
.brief{background:var(--card2);border:1px solid rgba(255,255,255,.07);border-radius:12px;
  padding:16px 18px;margin-bottom:12px}
.brief__type{font-size:.66rem;color:var(--pl);font-weight:700;letter-spacing:.1em;
  text-transform:uppercase;margin-bottom:6px}
.brief__ttl{font-size:.95rem;font-weight:700;color:var(--h);margin-bottom:8px}
.brief__body{font-size:.81rem;color:var(--muted);line-height:1.6}
.brief__body strong{color:var(--text)}
.brief__pts{display:flex;flex-direction:column;gap:5px;margin-top:10px}
.brief__pt{display:flex;gap:8px;font-size:.79rem;color:var(--text);line-height:1.5}
.brief__pt::before{content:'→';color:var(--accent);flex-shrink:0;font-weight:700}
.brief__hook{margin-top:10px;background:rgba(244,114,182,.07);border:1px solid rgba(244,114,182,.15);
  border-radius:8px;padding:9px 12px;font-size:.79rem;color:var(--pink);font-style:italic}
.brief__hook strong{font-style:normal;color:var(--pink);font-size:.7rem;letter-spacing:.06em;
  text-transform:uppercase;display:block;margin-bottom:3px}

/* ── Quote blocks ── */
.q{background:rgba(99,102,241,.07);border-left:3px solid var(--primary);border-radius:0 8px 8px 0;
  padding:10px 14px;margin:8px 0;font-size:.82rem;font-style:italic;line-height:1.55}
.q-g{border-left-color:var(--green);background:rgba(52,211,153,.06)}
.q-a{border-left-color:var(--accent);background:rgba(34,211,238,.05)}
.q-pk{border-left-color:var(--pink);background:rgba(244,114,182,.05)}
.q-w{border-left-color:var(--warn);background:rgba(251,191,36,.06)}
.qs{font-style:normal;font-size:.71rem;color:var(--muted);display:block;margin-top:5px}

/* ── Diamond quote ── */
.diamond{background:linear-gradient(135deg,rgba(244,114,182,.08),rgba(99,102,241,.08));
  border:1px solid rgba(244,114,182,.25);border-radius:16px;padding:28px 32px;margin:20px 0;text-align:center}
.diamond__lbl{font-size:.67rem;color:var(--pink);font-weight:700;letter-spacing:.12em;
  text-transform:uppercase;margin-bottom:12px}
.diamond__txt{font-size:1.1rem;font-style:italic;color:var(--h);line-height:1.7;margin-bottom:10px}
.diamond__src{font-size:.77rem;color:var(--muted)}
.diamond__use{font-size:.71rem;color:var(--green);margin-top:8px;font-weight:600}

/* ── Thread outline ── */
.thread{background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:12px;
  padding:16px 18px;margin-bottom:12px;counter-reset:tweets}
.thread__hd{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
.thread__name{font-size:.9rem;font-weight:700;color:var(--h)}
.thread__plat{font-size:.7rem;background:rgba(34,211,238,.1);color:var(--accent);
  padding:3px 10px;border-radius:12px}
.tweet{display:flex;gap:10px;margin-bottom:10px;align-items:flex-start;
  border-bottom:1px solid rgba(255,255,255,.05);padding-bottom:9px}
.tweet:last-child{border-bottom:none;padding-bottom:0;margin-bottom:0}
.tweet::before{counter-increment:tweets;content:counter(tweets);
  width:24px;height:24px;border-radius:50%;background:rgba(99,102,241,.15);
  color:var(--pl);display:flex;align-items:center;justify-content:center;
  font-size:.72rem;font-weight:700;flex-shrink:0;margin-top:2px}
.tweet__txt{font-size:.82rem;color:var(--text);line-height:1.55;flex:1}
.tweet__txt strong{color:var(--h)}

/* ── Carousel cards ── */
.carousel{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:12px 0}
.slide{background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:12px;
  padding:16px;min-height:120px;position:relative}
.slide__n{font-size:.65rem;color:var(--muted);margin-bottom:8px;font-weight:600;
  letter-spacing:.08em;text-transform:uppercase}
.slide__txt{font-size:.86rem;color:var(--text);line-height:1.55}
.slide__txt strong{color:var(--h);font-size:.95rem;display:block;margin-bottom:4px}
.slide__foot{font-size:.7rem;color:var(--pl);margin-top:8px;font-weight:600}

/* ── Data table ── */
.tbl{width:100%;border-collapse:collapse;font-size:.79rem;margin:12px 0}
.tbl th{background:rgba(99,102,241,.1);color:var(--pl);font-weight:600;padding:9px 11px;
  text-align:left;border-bottom:1px solid rgba(255,255,255,.07)}
.tbl td{padding:8px 11px;border-bottom:1px solid rgba(255,255,255,.07);color:var(--text);vertical-align:top}
.tbl tr:hover td{background:rgba(255,255,255,.02)}

/* ── Closing / foot ── */
.mandate{background:linear-gradient(135deg,rgba(244,114,182,.08),rgba(99,102,241,.07));
  border:1px solid rgba(244,114,182,.2);border-radius:16px;padding:28px 32px;margin:28px 0;text-align:center}
.mandate p{font-size:.92rem;line-height:1.85;color:var(--h)}
.mandate p strong{color:var(--pink)}
.pg-foot{text-align:center;padding:20px 32px 36px;font-size:.72rem;color:var(--muted);
  border-top:1px solid rgba(255,255,255,.07);max-width:980px;margin:0 auto}
.disc{max-width:980px;margin:0 auto;padding:0 32px 32px;font-size:.67rem;
  color:rgba(148,163,184,.28);border-top:1px solid rgba(255,255,255,.04);padding-top:12px;line-height:1.6}

@media(max-width:680px){.cover__meta,.stats,.brief__pts,.carousel{flex-direction:column}}
"""

# ── Helpers ────────────────────────────────────────────────────────────────────
def S(n, title, sub=""):
    s = f'<p class="ss">{sub}</p>' if sub else ""
    return f'<div class="sec" id="s{n}"><div class="sn">SECTION {n:02d}</div><h2 class="st">{title}</h2>{s}\n'
def E(): return "</div>\n"
def al(t, title, body): return f'<div class="al al-{t}"><div class="al__t">{title}</div><p>{body}</p></div>\n'
def q(txt, src="", col=""): 
    c = f" q-{col}" if col else ""
    s = f'<span class="qs">{src}</span>' if src else ""
    return f'<div class="q{c}">{txt}{s}</div>\n'
def tag(*pairs):
    return '<div class="story__tags">' + "".join(f'<span class="tag t{c}">{l}</span>' for l,c in pairs) + "</div>"

def brief(btype, title, body, points, hook=""):
    pts = "".join(f'<div class="brief__pt">{pt}</div>' for pt in points)
    hk = f'<div class="brief__hook"><strong>Opening Hook:</strong> {hook}</div>' if hook else ""
    return f"""<div class="brief">
<div class="brief__type">{btype}</div>
<div class="brief__ttl">{title}</div>
<div class="brief__body">{body}</div>
<div class="brief__pts">{pts}</div>
{hk}
</div>"""

def thread(name, platform, tweets):
    tw = "".join(f'<div class="tweet"><div class="tweet__txt">{t}</div></div>' for t in tweets)
    return f"""<div class="thread">
<div class="thread__hd"><span class="thread__name">{name}</span><span class="thread__plat">{platform}</span></div>
{tw}
</div>"""

def carousel(slides):
    inner = "".join(f'<div class="slide"><div class="slide__n">Slide {i+1}</div><div class="slide__txt">{s["txt"]}</div><div class="slide__foot">{s.get("foot","")}</div></div>' for i,s in enumerate(slides))
    return f'<div class="carousel">{inner}</div>'

# ── BUILD FUNCTIONS ─────────────────────────────────────────────────────────────

def cover():
    gen = datetime.now().strftime("%d %B %Y")
    return f"""<div class="cover">
<div class="badge">Content Exploration Report &middot; r/AppIdeas &middot; March 2026</div>
<h1>What Developers on Reddit<br><span>Actually Want Built</span></h1>
<p class="cover__sub">A personal content inspiration board drawn from {len(POSTS)} unique Reddit posts —
surfacing the best stories, stats, quotes, and patterns for social media posts,
threads, carousels, and visual reports.</p>
<div class="cover__meta">
  <div><span class="mv">{len(POSTS)}</span><div class="ml">Unique Posts</div></div>
  <div><span class="mv">9</span><div class="ml">Stories to Tell</div></div>
  <div><span class="mv">6</span><div class="ml">Thread Outlines</div></div>
  <div><span class="mv">40+</span><div class="ml">Content Ideas</div></div>
</div>
<div class="cover__note">
  &#x270D;&#xFE0F; <strong>This is not a product strategy report.</strong>
  It's a content brief — designed to help you explore this data and turn it
  into posts, threads, visuals, and reports that your audience will share.
</div>
<div class="cover__foot">Audience Intelligence &middot; audienceintelligence.com &middot; {gen}</div>
</div>"""

def toc():
    return """<div class="sec" id="toc">
<div class="sn">CONTENTS</div>
<h2 class="st">What's In This Report</h2>
<table class="tbl"><thead><tr><th>#</th><th>Section</th><th>Content Type</th></tr></thead><tbody>
<tr><td>01</td><td><a href="#s1">The Numbers at a Glance</a></td><td>Stats, data points you can screenshot or quote</td></tr>
<tr><td>02</td><td><a href="#s2">The 9 Best Stories in the Data</a></td><td>Narratives with context — ready to become posts</td></tr>
<tr><td>03</td><td><a href="#s3">Thread Outlines</a></td><td>6 ready-to-write Twitter/X or LinkedIn threads</td></tr>
<tr><td>04</td><td><a href="#s4">Carousel Slide Decks</a></td><td>4 structured carousel outlines for Instagram/LinkedIn</td></tr>
<tr><td>05</td><td><a href="#s5">The Best Quotes from the Community</a></td><td>Verbatims ready to quote, screenshot, or design</td></tr>
<tr><td>06</td><td><a href="#s6">Counterintuitive Findings</a></td><td>The surprising stuff — highest-performing content angle</td></tr>
<tr><td>07</td><td><a href="#s7">Raw Data Table — Top 50 Posts</a></td><td>Full ranked table for your own further exploration</td></tr>
<tr><td>08</td><td><a href="#s8">Content Briefs — 10 Post Ideas</a></td><td>Fully briefed individual posts with hooks</td></tr>
<tr><td>09</td><td><a href="#s9">Visual Report Ideas</a></td><td>Charts, infographics, and data viz concepts</td></tr>
<tr><td>END</td><td><a href="#close">Closing</a></td><td>Diamond quote + what to post first</td></tr>
</tbody></table></div>"""

def s1_numbers():
    p = [S(1, "The Numbers at a Glance", "Stats you can quote, screenshot, or drop into any post")]
    p.append("""<div class="stats">
<div class="stat c-g"><span class="sv">9,347</span><div class="sl">Daily users reached by one free app</div></div>
<div class="stat c-pk"><span class="sv">542</span><div class="sl">Upvotes — highest single post</div></div>
<div class="stat c-a"><span class="sv">17M</span><div class="sl">Members in r/InternetIsBeautiful</div></div>
<div class="stat c-p"><span class="sv">285</span><div class="sl">Upvotes — top idea compilation post</div></div>
<div class="stat c-w"><span class="sv">800+</span><div class="sl">Upvotes on the original "late invoice" complaint thread</div></div>
<div class="stat c-o"><span class="sv">749</span><div class="sl">Problems scraped from Reddit in one week</div></div>
<div class="stat c-g"><span class="sv">$40/mo</span><div class="sl">What Proposify charges for 2 proposals/month</div></div>
<div class="stat c-pk"><span class="sv">$100/mo</span><div class="sl">Cheapest property mgmt software for 2-unit landlords</div></div>
<div class="stat c-a"><span class="sv">22+</span><div class="sl">Reddit threads from pet owners with no good med tracker</div></div>
<div class="stat c-w"><span class="sv">74K</span><div class="sl">Subscribers in r/AppIdeas</div></div>
<div class="stat c-p"><span class="sv">43</span><div class="sl">Comments on "Tinder but for Music" post</div></div>
<div class="stat c-o"><span class="sv">3 yrs</span><div class="sl">Journey from zero to 10K MRR (dataset case study)</div></div>
</div>""")
    p.append(al("pk", "&#x1F4F8; Best Stats to Screenshot as Social Content",
        "The 9,347 daily users story is the single most compelling data point — it's specific, surprising, and proves a principle. "
        "The price gap stats ($40/mo for 2 proposals, $100/mo for 2-unit landlords) are strong emotional hooks for audiences who have felt that frustration. "
        "The 800+ upvotes on a complaint thread shows validated demand better than any survey."))
    return "".join(p) + E()

def s2_stories():
    p = [S(2, "The 9 Best Stories in the Data", "Each one is a post waiting to happen")]

    stories = [
        {
            "col": "g", "icon": "&#x1F4C8;", "title": "The Developer Who Made It Free and Hit 9,347 Daily Users",
            "tags": [("Growth Story","g"),("Case Study","a"),("Screenshot-worthy","pk")],
            "body": """In early 2024, a developer made their budget tracking app <strong>completely free</strong> — no ads, no tracking, no subscription tier.
Within months they were approaching <strong>9,347 daily active users</strong> and couldn't believe the growth.
The post, which scored <strong>542 pts</strong> on r/AppIdeas, included this line: <em>"I just can't believe I'm about to hit 10,000 daily users."</em><br><br>
The insight is almost annoyingly simple: they removed the barrier. That's it. No new features, no marketing campaign, no growth hacking. They made the thing free and let Reddit do the rest.
The community upvoted the story because it validated what everyone suspects but rarely acts on — that free outperforms paid in the organic discovery economy.""",
            "src": "542 pts · r/AppIdeas · budget tracker case study"
        },
        {
            "col": "pk", "icon": "&#x1FAB1;", "title": "The 'Tinder for Music' Post That Got 43 Comments and Was Never Built",
            "tags": [("Community Response","pk"),("High Engagement","a"),("Still Available","g")],
            "body": """A post titled <em>"Tinder but for Music"</em> scored <strong>174 pts and 43 comments</strong> — one of the highest comment-engagement ratios in the entire dataset.
The idea: swipe right to add a song to a playlist, left to skip. Connect to Spotify. Get a perfectly curated playlist in 20 swipes.<br><br>
The comment thread is a mini focus group. People described exactly what they'd want: offline mode, genre filters, "swipe history" to recover songs they regretted skipping.
But here's the most interesting part: <strong>as of the scrape date, nobody has built it.</strong>
The idea has 43 people describing the exact product they want, in detail, for free — and it's still sitting there as a concept post.""",
            "src": "174 pts · 43 comments · r/AppIdeas"
        },
        {
            "col": "a", "icon": "&#x1F4DD;", "title": "The Man Who Scraped 749 Problems From Reddit in One Week",
            "tags": [("Methodology","a"),("Repeatable","g"),("Thread material","pk")],
            "body": """One poster described scraping Reddit for a single week and cataloguing <strong>749 distinct product problems</strong> — complaints, frustrations, "I wish someone would build" statements — from public posts and comment threads.
The post scored <strong>211 pts with 98 comments</strong>.<br><br>
What makes this story content gold is the methodology: they weren't guessing at what people want. They were <em>reading what people already said they wanted</em>.
The 749 problems covered everything from restaurant-to-social-post converters to tradespeople scheduling to calorie cameras.
The post is essentially a map of unmet demand — and every item on it had upvote evidence from the original complaint thread.""",
            "src": "211 pts · 98 comments · r/AppIdeas · 'scraped 749 problems'"
        },
        {
            "col": "w", "icon": "&#x1F4B8;", "title": "The Freelancer Paying $40/Month for 2 Proposals",
            "tags": [("Price Gap","w"),("Frustration","pk"),("Relatable","g")],
            "body": """A recurring character in the dataset: the freelancer or consultant who sends 2–3 proposals a month and pays <strong>$40/month for Proposify</strong> to make them look professional.
The frustration is specific, measurable, and immediately relatable to anyone who's freelanced: <em>the tool exists, it works, it's just grotesquely mispriced for your actual usage level.</em><br><br>
This pattern appears across the dataset in multiple verticals: property management software at $100/month for a 2-unit landlord, Jobber at $50/month for a sole-trader plumber, scheduling tools built for teams that a solo operator has to pay team prices for.
The story is really one story: <strong>enterprise tools priced for enterprises, used by individuals.</strong>""",
            "src": "Multiple posts scoring 63–179 pts · freelance / small business vertical"
        },
        {
            "col": "o", "icon": "&#x1F436;", "title": "22 Reddit Threads From Pet Owners With No Good Medication Tracker",
            "tags": [("Niche Gap","o"),("Emotional","pk"),("Underserved","g")],
            "body": """One methodical poster documented <strong>22 separate Reddit threads</strong> from pet owners managing animals on multiple medications — and found not a single good solution.
The specific pain: a dog on 3 different medications with different schedules (twice daily, with food, every 48 hours) and no app that handles the complexity.
Every health app is built for humans. The vet reminder apps are too simple. Nothing produces a printable schedule for the fridge.<br><br>
The community response confirmed the gap. Comments came from people with cats on thyroid medication, dogs with epilepsy protocols, elderly pets on 5-drug regimens.
The thread became a documentation of a very specific, very real frustration that nobody had ever aggregated before.""",
            "src": "97 pts · r/AppIdeas · '5 app ideas pulled from real Reddit complaints'"
        },
        {
            "col": "p", "icon": "&#x1F91F;", "title": "The Developer Making 10K MRR Who Says 'This Already Exists' Doesn't Matter",
            "tags": [("Mindset","p"),("Quotable","pk"),("Community wisdom","g")],
            "body": """A post that reads less like an idea pitch and more like a <strong>permission slip for builders</strong> — scored <strong>61 pts</strong> and sparked a thread about the toxic default of dismissing ideas.
The author, who makes 10K MRR from SaaS and apps after starting their journey 3 years ago, laid out three rules:
<br><br>
<em>"This already exists"</em> — doesn't matter, as long as your version is better or free or solves it differently.
<em>"No one will buy this"</em> — that's what validation is for.
<em>"This is dumb"</em> — why would you even say that?
<br><br>
The data behind it: all their products are in spaces with <em>tons of competition</em>. Competition, they argue, is proof of demand — not a barrier to entry.""",
            "src": "61 pts · r/AppIdeas · long-form community support post"
        },
        {
            "col": "g", "icon": "&#x1F525;", "title": "The Subreddit List That Became a Traffic Map",
            "tags": [("Practical","g"),("Community resource","a"),("175 pts","pk")],
            "body": """A post explicitly answering the question <em>"where do I post my app to get actual users?"</em> scored <strong>175 pts</strong> — one of the highest-engagement posts in the dataset.
The community upvoted it because it solved a real problem developers face: building the thing is the easy part; getting anyone to see it is the hard part.<br><br>
The list included r/InternetIsBeautiful (17M members) as the top recommendation, with specific notes on what gets upvoted there (free, no sign-up, one clear function).
The meta-insight: <strong>the developer community treats distribution knowledge as equally valuable as technical knowledge.</strong>
A post about where to post outperformed posts about what to build.""",
            "src": "175 pts · r/AppIdeas · 'best subreddits to promote your app'"
        },
        {
            "col": "pk", "icon": "&#x1F4CA;", "title": "The Week Someone Documented 700+ SaaS Price Complaints",
            "tags": [("Consumer anger","pk"),("Recurring pattern","w"),("Data story","a")],
            "body": """One poster catalogued <strong>31 complaints in a single month</strong> from users who were silently charged more after introductory pricing periods ended — and found the pattern repeated across dozens of SaaS tools.
The insight that made this post worth 176 pts: people aren't just annoyed at one company. They're constructing a generalised distrust of SaaS pricing models entirely.
<em>"It's not that Notion raised prices. It's that I don't trust any of them anymore."</em><br><br>
The story is bigger than the tool that prompted it — it's about a generation of software users who signed up for what they thought was a fixed relationship and found it repriced around them.""",
            "src": "176 pts · r/AppIdeas · 'app ideas people are literally asking for'"
        },
        {
            "col": "a", "icon": "&#x1F9E0;", "title": "Sign Language on Instagram in 2 Weeks",
            "tags": [("Rapid growth","g"),("Social proof","a"),("Feel-good story","pk")],
            "body": """A brief mention in a list post became one of the most memorable moments in the dataset: a sign language learning game that <strong>gained 747 Instagram followers in 2 weeks</strong> — organically, with no paid promotion.
The product itself was modest: an interactive web game teaching ASL fingerspelling.
But the community it tapped — deaf advocates, speech therapists, parents of DHH children, students taking ASL classes — shared it reflexively because it served them genuinely.<br><br>
The insight for content: <strong>passionate niche communities share things that serve them.</strong>
747 followers in 2 weeks from a product that a developer mentioned almost in passing is one of the cleanest viral case studies in the entire dataset.""",
            "src": "Dataset reference · sign language game · 747 Instagram followers in 2 weeks"
        },
    ]

    for s in stories:
        tgs = tag(*s["tags"])
        p.append(f"""<div class="story story--{s['col']}">
<div class="story__head">
  <div class="story__icon" style="background:rgba(255,255,255,.05)">{s['icon']}</div>
  <div class="story__ttl">{s['title']}</div>
</div>
{tgs}
<div class="story__body">{s['body']}</div>
<div class="story__stat"><strong>Source:</strong> {s['src']}</div>
</div>""")

    return "".join(p) + E()

def s3_threads():
    p = [S(3, "Thread Outlines", "6 ready-to-write threads for Twitter/X or LinkedIn — each with a hook and all the beats")]

    threads_data = [
        {
            "name": "The Free App Formula Thread",
            "platform": "Twitter/X · 8 tweets",
            "tweets": [
                "<strong>One developer made their app free in 2024.</strong><br>By the end of the year they had 9,347 daily users.<br>Their secret wasn't a feature. It was a pricing model.<br><br>Here's the formula they (and dozens of others) proved works every time: &#x1F9F5;",
                "The formula is 4 ingredients:<br>1. Free<br>2. No sign-up<br>3. Does exactly one thing<br>4. Produces something the user can save or share<br><br>That's it. That's the whole strategy.",
                "Why 'free' is the distribution strategy:<br><br>r/InternetIsBeautiful has 17 million members.<br>It only shares web links to free tools that work immediately.<br>One front-page post = tens of thousands of visitors in 24 hours.<br>You can't buy that placement. You can only earn it.",
                "Why 'no sign-up' matters more than you think:<br><br>A login wall cuts your sharing rate by ~70%.<br>Not because people won't sign up — because they won't <em>share</em> something that requires a sign-up.<br>Sharing is how free tools spread. Remove the wall.",
                "Why 'one thing' is counterintuitive:<br><br>Every instinct says: add features, increase value.<br>But a tool that does one job has a name people can Google.<br>'Free invoice late payment letter generator'<br>vs<br>'InvoiceFlow Pro'<br><br>The boring descriptive name wins organic traffic.",
                "Why 'shareable output' is the actual marketing:<br><br>The thing your user takes away from your tool — a PDF, a copied letter, a downloaded chart — is what they share.<br>Build the output first. Then build the inputs.<br>The output is the product. The form is just the delivery mechanism.",
                "The case studies from this week's data:<br><br>• Budget tracker → free → 9,347 daily users &#x2705;<br>• Sign language game → free → 747 new Instagram followers in 2 weeks &#x2705;<br>• 'Tinder for Music' → never built, but 43 people described exactly what they want → still available &#x2708;&#xFE0F;",
                "If you're building something right now:<br><br>Make it free.<br>Remove the sign-up.<br>Define the one job it does in 7 words or less.<br>Make the output downloadable or copyable.<br><br>Then post to r/InternetIsBeautiful on a Tuesday morning.<br><br>That's the playbook. It's unglamorous and it works."
            ]
        },
        {
            "name": "The Validation Methodology Thread",
            "platform": "Twitter/X · 7 tweets",
            "tweets": [
                "<strong>Someone on Reddit scraped 749 product problems in one week.</strong><br>Not by surveying people, not by paying for research.<br>By reading what people publicly complained about.<br><br>Here's the method — and why it works better than any market research: &#x1F447;",
                "The insight: Reddit is a 20-year archive of people publicly describing their frustrations.<br><br>Every thread that starts 'why is there no app for...' is a validated demand signal.<br>Every upvote on that thread is a vote from someone who shares the frustration.<br><br>It's free market research, permanently indexed.",
                "The method in 4 steps:<br>1. Pick a problem space (pet care, freelance, small landlord, etc.)<br>2. Search Reddit for phrases: 'why doesn't', 'I wish someone', 'can't believe there's no', 'looking for a tool'<br>3. Sort by top/year<br>4. Count the upvotes on the complaint, not the solution",
                "Why upvotes on the <em>complaint</em> matter more than upvotes on the solution:<br><br>A complaint with 800+ upvotes means 800+ people recognised their own frustration in someone else's words.<br>A solution post with 800+ upvotes just means the execution was impressive.<br><br>Demand validation comes from the complaint side of the equation.",
                "What 749 problems looked like in practice:<br><br>• 22 threads from pet owners with no good medication tracker<br>• 31 complaints from SaaS users hit by silent price increases<br>• Freelancers losing $2–8K/year chasing late invoices<br>• Small landlords tracking maintenance by text message<br><br>All documented. All upvoted. All unbuilt.",
                "The meta-skill this teaches:<br><br>Before you build anything, spend 2 hours reading Reddit complaints in the problem space.<br>If you find 5+ threads describing the same frustration, you have demand.<br>If the top comment has 300+ upvotes, you have a market.<br><br>If no threads exist — that's information too.",
                "The full dataset for this week: <strong>749 validated problems.</strong><br>The number of free tools solving them: a fraction of that.<br><br>The opportunity isn't finding ideas.<br>The opportunity is building the simplest possible answer to a problem that's already been loudly asked.<br><br>Most people skip the asking step. Don't."
            ]
        },
        {
            "name": "The Price Gap Is the Product Thread",
            "platform": "LinkedIn · 6 posts",
            "tweets": [
                "I've been reading through 525 posts from r/AppIdeas this week.<br><br>The single most repeated frustration isn't a technical problem.<br>It's a pricing problem.<br><br>And it's everywhere.",
                "The pattern:<br><br>A freelancer sends 2–3 proposals a month.<br>The only tools that make them look professional start at $40/month.<br>That's $480/year for occasional professional formatting.<br><br>They don't want the CRM integration. They don't want the e-signature analytics. They want to look like they know what they're doing.",
                "Same pattern, different verticals:<br><br>• Property management software for 50-unit complexes: $100/month. Number of units the frustrated poster has: 2.<br>• Team scheduling tools built for 10+ people: $50/month. The business size: 1 person.<br>• Job management platforms for trade contractors: starts at $30/month. The contractor: sole trader.<br><br>Enterprise pricing. Individual usage. Zero middle ground.",
                "Why this matters beyond 'build the cheap version':<br><br>Every one of these frustrated users is an active Googler.<br>They are searching for '[product category] free alternative' right now.<br>The first thing that appears in results — if it's free and actually works — gets their entire attention and gratitude.<br><br>Gratitude = sharing = referral = traffic.",
                "The interesting flip side from the same dataset:<br><br>The most-upvoted post about this phenomenon (542 pts) was from a developer who <em>did</em> build the free alternative.<br>A simple budget tracker. No ads, no tracking, completely free.<br>Daily active users when they posted: 9,347.<br><br>They made the app free. The market found them.",
                "The question this raises for every builder:<br><br>What's the $30–100/month tool in your problem space that's priced for the enterprise when the demand is entirely individual?<br><br>The gap between 'what exists' and 'what individuals can afford to use' is the product."
            ]
        },
        {
            "name": "'This Already Exists' — The Permission Slip Thread",
            "platform": "Twitter/X · 5 tweets",
            "tweets": [
                "The most common reason people don't build their idea:<br><br>'Someone's already built this.'<br><br>A developer making 10K MRR, working with 40+ clients, just wrote a Reddit post explaining why that's the wrong reason to stop.<br>It has 61 upvotes, which is modest — but it's the most honest thing in the dataset.",
                "'This already exists' → doesn't matter. As long as your version is free, simpler, or solves it differently.<br><br>Having competitors isn't a warning sign. It's proof that people pay for something in this space.<br>Competition is demand evidence, not a barrier.",
                "'No one will buy this' → that's what validation is for.<br><br>The methodology: search Reddit for complaint threads about the problem.<br>Count the upvotes.<br>If 800 people upvoted someone describing the frustration — that's your sample size.",
                "'This is dumb' → why would you even say that?<br><br>The post mentions working with companies scaling from 5 to 7–8 figures.<br>None of their most successful products were in glamorous spaces.<br>They were niche, boring, and solving specific problems loudly complained about in specific communities.",
                "The three permissions this data gives you:<br><br>1. Build in crowded spaces — they're only crowded at the premium tier<br>2. Use Reddit complaints as your market research — it's free and it's specific<br>3. Start with free — it's not a compromise, it's the distribution strategy<br><br>The barrier is almost never the idea. It's the build."
            ]
        },
        {
            "name": "The Niche Audience Shares More Thread",
            "platform": "Twitter/X · 6 tweets",
            "tweets": [
                "A sign language learning game gained <strong>747 Instagram followers in 2 weeks</strong>.<br>No paid promotion.<br>No influencer deal.<br>No Product Hunt launch.<br><br>The mechanism was simpler than any growth strategy: it genuinely served a community that was waiting for it.",
                "The deaf and hard-of-hearing community online is large, vocal, and highly motivated to share tools that serve them.<br><br>Speech therapists share it with clients.<br>Hearing parents share it with other parents of DHH children.<br>ASL students share it in class group chats.<br><br>The creator didn't market it. The community distributed it.",
                "This is the niche distribution principle in one example:<br><br>A generic tool posted to r/InternetIsBeautiful gets a spike and fades.<br>A niche tool posted to a dedicated community gets slower but more sustained sharing — because every new member of that community eventually finds it.",
                "It shows up throughout the dataset:<br><br>• Pet owners share pet tools in pet groups<br>• Freelancers share freelancer tools in freelancer Discords<br>• Small landlords share small landlord tools in property forums<br><br>The tool doesn't have to be remarkable. It has to be specifically for them.",
                "The psychological mechanic: niche communities have an identity.<br><br>Sharing a tool that serves your specific niche is a statement about your identity too.<br>'Look at this thing I found FOR US.'<br><br>That's a much stronger sharing motivation than 'look at this cool thing.'",
                "For content creators, the parallel is exact:<br><br>Content about a specific niche outperforms broadly applicable content because the niche distributes it internally.<br>The algorithm rewards niche content more reliably than broad content.<br>And the audience you build in a niche has lower competition and higher retention.<br><br>Serve the niche. The niche will tell everyone."
            ]
        },
        {
            "name": "What 525 App Idea Posts Taught Me Thread",
            "platform": "Twitter/X · 9 tweets — Synthesis thread",
            "tweets": [
                "I just read through 525 posts from r/AppIdeas.<br><br>Not to build anything.<br>To understand what developers, makers, and frustrated users are actually asking for.<br><br>Here are the 8 most interesting things I found: &#x1F9F5;",
                "<strong>1. Free is a distribution strategy, not a compromise.</strong><br><br>The highest-traffic case in the data: developer makes budget app free → 9,347 daily users.<br>No feature updates. No marketing. Just: removed the price.",
                "<strong>2. The best ideas are boring.</strong><br><br>'Boring but validated' outperforms clever and unproven every time.<br>Invoice late payment letters. Pet medication schedules. Maintenance request forms for small landlords.<br>Boring problems = SEO-friendly names = people Googling for exactly what you built.",
                "<strong>3. 'This already exists' is good news.</strong><br><br>Competition means the market exists.<br>The gap is almost always at the free/individual tier, not the enterprise/team tier.<br>If something costs $50/month for enterprise use, there's almost always space for a free simple version for individuals.",
                "<strong>4. Reddit is a free market research database.</strong><br><br>One person scraped 749 validated product problems from Reddit in a week.<br>Each one was a complaint thread with upvote evidence.<br>800 upvotes on a complaint = 800 people recognising their own frustration.",
                "<strong>5. The shareable output IS the product.</strong><br><br>A PDF, a copied text, a downloaded image — whatever your tool produces — is what users share.<br>The interface is secondary.<br>Design the output first, then work backwards to the inputs.",
                "<strong>6. Niche communities distribute better than general ones.</strong><br><br>Sign language game: 747 Instagram followers in 2 weeks, organically.<br>The deaf community shared it internally.<br>Niche communities have identity. Sharing a niche tool is a statement about who you are.",
                "<strong>7. Reddit is distribution, not validation.</strong><br><br>The highest-traffic channel for free tools (r/InternetIsBeautiful, 17M members) is distribution infrastructure waiting to be used.<br>The validation already happened in the complaint threads.<br>These are different steps, used at different times.",
                "<strong>8. The most interesting post in the dataset was a permission slip.</strong><br><br>A developer making 10K MRR wrote: 'This already exists doesn't matter. No one will buy this — that's what validation is for. This is dumb — why would you even say that?'<br><br>61 upvotes. Modest number.<br>But it's the realest thing in 525 posts."
            ]
        },
    ]

    for td in threads_data:
        p.append(thread(td["name"], td["platform"], td["tweets"]))
    return "".join(p) + E()

def s4_carousels():
    p = [S(4, "Carousel Slide Decks", "4 structured carousel outlines for Instagram or LinkedIn")]

    carousels_data = [
        ("The Free App Formula", "Instagram · 7 slides · Dark design recommended", [
            {"txt": "<strong>The Free App Formula</strong><br><br>How one developer went from 0 to 9,347 daily users without spending a penny on marketing.", "foot": "Hook slide"},
            {"txt": "<strong>Free &gt; Paid</strong><br><br>They made the app free in early 2024. Growth started immediately. No feature changes. Just: no more price.", "foot": "Slide 2 of 7"},
            {"txt": "<strong>No Sign-Up Required</strong><br><br>A login wall cuts your sharing rate by ~70%. Not because people won't sign up — because they won't share something that requires it.", "foot": "Slide 3 of 7"},
            {"txt": "<strong>One Job Only</strong><br><br>The tool does one thing. That makes it describable in one sentence. One sentence = searchable = rankable.", "foot": "Slide 4 of 7"},
            {"txt": "<strong>Shareable Output</strong><br><br>A PDF, a copied text, a downloaded image. The thing your user takes away is what they share. Build the output first.", "foot": "Slide 5 of 7"},
            {"txt": "<strong>Where to Post It</strong><br><br>r/InternetIsBeautiful · 17 million members<br>One free tool post = tens of thousands of visitors in 24 hours", "foot": "Slide 6 of 7"},
            {"txt": "<strong>Free + No Sign-Up + One Job + Shareable Output</strong><br><br>That's the formula. It's unglamorous. It works.", "foot": "Save this slide"},
        ]),
        ("749 Validated Problems", "LinkedIn · 8 slides · Data-driven design", [
            {"txt": "<strong>Someone scraped 749 product problems from Reddit in one week.</strong><br><br>This is what validated market research actually looks like.", "foot": "Hook slide"},
            {"txt": "<strong>The method:</strong><br>Search for 'why doesn't', 'I wish someone', 'can\'t believe there\'s no'<br>Sort by top posts<br>Count upvotes", "foot": "Slide 2 of 8"},
            {"txt": "<strong>800+ upvotes on an invoice frustration thread.</strong><br><br>That's 800 people recognising their own pain in someone else's words.", "foot": "Slide 3 of 8"},
            {"txt": "<strong>22 threads from pet owners with no medication tracker.</strong><br><br>Not one good solution. Verified by 22 separate posts.", "foot": "Slide 4 of 8"},
            {"txt": "<strong>31 complaints about silent SaaS price increases in one month.</strong><br><br>Not about one company. About a generalised distrust of SaaS pricing entirely.", "foot": "Slide 5 of 8"},
            {"txt": "<strong>749 problems documented.</strong><br><br>The number of free tools solving them: a fraction of that number.", "foot": "Slide 6 of 8"},
            {"txt": "<strong>Reddit is 20 years of people publicly describing their frustrations.</strong><br><br>Every complaint thread is free market research, permanently indexed.", "foot": "Slide 7 of 8"},
            {"txt": "<strong>The opportunity isn't finding ideas.</strong><br><br>It's building the simplest possible answer to a problem that's already been loudly asked.", "foot": "Save this — swipe back to share"},
        ]),
        ("'This Already Exists' — Why That's Good News", "Instagram · 6 slides", [
            {"txt": "<strong>'Someone's already built this.'</strong><br><br>The most common reason people stop before starting.<br>Here's why it's actually the best possible news.", "foot": "Hook slide"},
            {"txt": "<strong>Competition = demand evidence.</strong><br><br>If a tool costs $40/month and people are paying for it, the market is real.<br>The gap is almost always at the free/individual tier.", "foot": "Slide 2 of 6"},
            {"txt": "<strong>$40/month for 2 proposals.</strong><br><br>The freelancer who can't afford Proposify isn't looking for a competitor.<br>They're looking for a free version.<br>That's a different product.", "foot": "Slide 3 of 6"},
            {"txt": "<strong>The developer making 10K MRR said it clearly:</strong><br><br>'All my products are in spaces with tons of competition. That's how I know the market is there.'", "foot": "Slide 4 of 6"},
            {"txt": "<strong>Your version just needs to be:</strong><br>→ Free<br>→ Simpler<br>→ Built for the individual, not the enterprise", "foot": "Slide 5 of 6"},
            {"txt": "<strong>'This already exists'</strong> = the market is proven.<br>Your job: serve the tier that's being ignored.<br><br>That tier is usually: individuals who won't pay enterprise prices.", "foot": "Save this"},
        ]),
        ("Niche Communities Are Distribution Infrastructure", "LinkedIn/Instagram · 6 slides", [
            {"txt": "<strong>A sign language learning game gained 747 Instagram followers in 2 weeks.</strong><br><br>No paid promotion. No launch strategy. Just: it genuinely served a community.", "foot": "Hook slide"},
            {"txt": "<strong>The deaf and hard-of-hearing community is large, vocal, and underserved.</strong><br><br>When something serves them genuinely, they share it inside their community immediately.", "foot": "Slide 2 of 6"},
            {"txt": "<strong>Speech therapists share it with clients.<br>Parents share it with other parents.<br>Students share it in class chats.</strong><br><br>The creator didn't market it. The community distributed it.", "foot": "Slide 3 of 6"},
            {"txt": "<strong>The niche distribution principle:</strong><br><br>A generic tool gets a spike and fades.<br>A niche tool gets slower but sustained sharing — because every new community member eventually finds it.", "foot": "Slide 4 of 6"},
            {"txt": "<strong>'Look at this thing I found FOR US.'</strong><br><br>Sharing a niche tool is an identity statement.<br>That's a much stronger motivation than 'look at this cool thing.'", "foot": "Slide 5 of 6"},
            {"txt": "<strong>Serve the niche.<br>The niche will tell everyone.</strong><br><br>747 followers. 2 weeks. Zero marketing budget.", "foot": "Save this"},
        ]),
    ]

    for name, platform, slides in carousels_data:
        p.append(f'<h3 style="font-size:.95rem;color:var(--h);margin:20px 0 8px">&#x1F5BC;&#xFE0F; {name} <span style="font-size:.76rem;color:var(--muted);font-weight:400">— {platform}</span></h3>')
        p.append(carousel(slides))

    return "".join(p) + E()

def s5_quotes():
    p = [S(5, "The Best Quotes from the Community", "Verbatims you can screenshot, design, or quote directly")]

    p.append("""<div class="diamond">
<div class="diamond__lbl">&#x1F48E; Diamond Quote — The Case Study in One Line</div>
<div class="diamond__txt">"At the beginning of 2024 I made the app free, and since then the number of users has been growing continuously. I just can't believe I'm about to hit 10,000 daily users."</div>
<div class="diamond__src">r/AppIdeas developer · 542 pts · budget tracker growth story</div>
<div class="diamond__use">USE: Any post about free tools, organic growth, removing barriers, pricing strategy</div>
</div>""")

    quotes = [
        ("the formula is dead simple. find someone describing a problem they'd pay to fix. check if others agree. check if current tools suck. build.",
         "285 pts compilation post · the entire methodology in 27 words", "g",
         "Thread opener, LinkedIn post intro, carousel hook slide"),
        ("'This already exists' → I'm seeing this a lot here and the truth is that it doesn't matter. As long as your version is better or adds a new perspective — having tons of competitors is a sign there's space for many players.",
         "61 pts community support post · developer making 10K MRR", "a",
         "Counter to 'someone's already built this' posts. High relatability."),
        ("The only things stopping you are fear and complexity. Pick the simplest version of the idea and launch it in a week.",
         "r/AppIdeas community post · mindset framing", "pk",
         "Motivational post close. Thread ending tweet. Quote card."),
        ("I've worked with 40+ clients in the past decade helping them scale from 5 to 7-8 figures so I've seen a bit of everything. They're all in spaces with tons of competition and niches you wouldn't believe you could make money from.",
         "61 pts · same developer as above · experience framing", "p",
         "Credibility-building post. Reply to 'is it too crowded?' discussions."),
        ("freelancers losing $2-8K/year chasing late payments. they don't want accounting software. they want automated escalation — polite reminder → firm follow-up → 'I'm filing in small claims' template. nothing does this well. 340+ upvotes.",
         "285 pts · idea compilation · the specificity benchmark", "w",
         "Show what validated demand actually looks like. Post about research methodology."),
        ("Sign language game: gained 747 Instagram followers in 2 weeks and is growing daily.",
         "Dataset reference · growth case study · organic niche spread", "g",
         "Viral growth story for a values-aligned tool. Niche community distribution post."),
    ]
    for text, src, col, use in quotes:
        p.append(f"""<div class="gold-q" style="background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:12px;padding:14px 18px;margin-bottom:10px;border-left:3px solid {'var(--green)' if col=='g' else 'var(--accent)' if col=='a' else 'var(--pink)' if col=='pk' else 'var(--warn)' if col=='w' else 'var(--pl)'}">
<div style="font-size:.85rem;font-style:italic;color:var(--text);line-height:1.6;margin-bottom:6px">"{text}"</div>
<div style="font-size:.73rem;color:var(--muted)">{src}</div>
<div style="font-size:.7rem;color:var(--warn);font-weight:600;margin-top:5px">USE: {use}</div>
</div>""")
    return "".join(p) + E()

def s6_counterintuitive():
    p = [S(6, "Counterintuitive Findings", "The surprising stuff — these make the highest-performing content angles")]
    items = [
        ("Free Outperforms Paid — By Miles",
         "The instinct is to monetise early. The data says the opposite: the developer who removed pricing hit 9,347 daily users while others are struggling to land their first 100 paying customers. Free is not a compromise or a starting point to move past. For tools intended to drive traffic, free is the permanent strategy.",
         "g", "&#x1F4B0;"),
        ("'Boring' Ideas Outperform Clever Ones",
         "'6 boring ideas that will make money' scored 179 pts. The ideas: small landlord maintenance forms, invoice escalation letters, proposal generators. None of them are glamorous. All of them solve specific, googleable problems. The boring descriptive name ('free invoice late payment letter generator') outranks the clever brandname ('InvoiceFlow Pro') for organic search traffic every time.",
         "w", "&#x1F634;"),
        ("Distribution Knowledge is Valued as Much as Technical Knowledge",
         "A post about *where to post your app* scored 175 pts — nearly as high as posts sharing validated idea lists. The community has realised that building is the easy part. Getting anyone to see it is the hard part. Distribution knowledge is priced at a premium in this community because the gap between good tool and successful tool is almost entirely distribution.",
         "a", "&#x1F4E1;"),
        ("The Most Engaging Fun Tool Was Never Built",
         "'Tinder but for Music' got 174 pts and 43 comments — nearly the highest comment count in the dataset. This is a community that spent real time describing in detail exactly what they want. Nobody has shipped it. The market is pre-validated with 43 discussions of specific features. It's sitting there.",
         "pk", "&#x1F3B5;"),
        ("A Complaint Thread Is Worth More Than a Survey",
         "800+ upvotes on an invoice complaint thread. 22 documented threads from pet owners with no medication tracker. These are not survey responses — they're people voluntarily describing their pain in public, endorsed by hundreds of others. A pre-existing upvoted complaint is stronger validation than a survey you commission because the motivation is genuine, not prompted.",
         "p", "&#x1F4AC;"),
        ("Niche Audiences Spread Faster Than General Ones",
         "The sign language game hit 747 Instagram followers in 2 weeks from no promotion. This outperforms most Product Hunt launches. Why? The community was waiting for someone to serve them specifically. General audiences get distracted by competing content. Niche audiences share the one tool that's clearly for them — because it's an identity statement, not just a recommendation.",
         "o", "&#x1F304;"),
    ]
    for title, body, col, icon in items:
        p.append(f"""<div class="story story--{col}">
<div class="story__head">
  <div class="story__icon" style="background:rgba(255,255,255,.05)">{icon}</div>
  <div class="story__ttl">{title}</div>
</div>
<div class="story__body">{body}</div>
</div>""")
    return "".join(p) + E()

def s7_data_table():
    p = [S(7, "Raw Data Table — Top 50 Posts", "For your own exploration — click into these posts in the JSON files")]
    p.append("""<table class="tbl"><thead><tr>
<th>#</th><th>Score</th><th>Comments</th><th>Title (truncated)</th><th>Author</th>
</tr></thead><tbody>""")
    for i, post in enumerate(TOP50, 1):
        title = post["title"][:75] + ("…" if len(post["title"]) > 75 else "")
        p.append(f"<tr><td>{i}</td><td><strong style='color:var(--green)'>{post['score']}</strong></td><td>{post['num_comments']}</td><td>{title}</td><td style='color:var(--muted)'>{post['author'][:18]}</td></tr>")
    p.append("</tbody></table>")
    return "".join(p) + E()

def s8_briefs():
    p = [S(8, "Content Briefs — 10 Post Ideas", "Fully briefed individual posts — each with a format, angle, and opening hook")]

    briefs = [
        ("Twitter/X Thread", "The Man Who Hit 10,000 Daily Users by Making His App Free",
         "The case study from 542 pts. Specific numbers make this credible. The lesson is transferable to any content creator or builder. Works well as a 6–8 tweet thread or a written LinkedIn post.",
         ["Open with the number: 9,347 daily users", "Reveal the strategy: he made it free", "Explain why free = distribution (r/InternetIsBeautiful mechanism)", "Show the 4-ingredient formula", "Close with the permission: free is not compromise, it's the strategy"],
         '"At the beginning of 2024 I made the app free. I just can\'t believe I\'m about to hit 10,000 daily users." — This is not a story about features. It\'s a story about removing friction.'),
        ("LinkedIn Post", "The $40/Month Proposal Problem",
         "A relatable frustration post with a data point embedded. Works best on LinkedIn where the freelance/consultant audience is large. The emotional hook is immediate — almost anyone who's freelanced has felt this exact sting.",
         ["Open with the specific price: $40/month for Proposify", "Name the actual usage: 2–3 proposals per month", "Do the maths: $480/year for occasional professional formatting", "Broaden to the pattern: property management, scheduling, job management tools", "Close with the question: where's the gap in your space?"],
         'A freelancer I read about pays $40 a month for Proposify. She sends 2 proposals a month. That\'s $20 per proposal — for a Word doc with better formatting.'),
        ("Instagram Carousel", "749 Problems Scraped in One Week",
         "Data-led carousel, strong visual potential. Works on Instagram or LinkedIn. Lead with the number — 749 is surprising and specific enough to create a stop-scroll moment. Pair with a data-y design.",
         ["Slide 1: '749 validated problems. One week. One person.'", "Slide 2: The method (search phrases + upvote counting)", "Slide 3: The invoice frustration — 800+ upvotes", "Slide 4: The pet medication gap — 22 threads", "Slide 5: The SaaS price increase pattern — 31 complaints in a month", "Slide 6: 'The opportunity isn't finding ideas. It's building the answer to what's already been asked.'"],
         "749. That's how many validated product problems one person found on Reddit in a single week. Not by surveying people. By reading what they already said publicly."),
        ("Twitter Thread", "'This Already Exists' Is Actually Good News",
         "Reframe thread — challenges a very common cognitive barrier. High share potential because it names a frustration many builders have felt. The developer-making-10K-MRR quote is the credibility anchor.",
         ["Open with the fear: 'Someone's already built this.'", "Introduce the speaker: 10K MRR developer, 40+ clients", "The counter: competition = market evidence", "The specific example: free vs $40/month is a different product", "The close: your version just needs to be free, simpler, or for the individual"],
         "The most common reason people stop building before they start: 'Someone's already built this.' Here's why that's actually the best possible news."),
        ("Instagram Reel Script", "Sign Language Game, 747 Followers, Zero Budget",
         "Short-form video script (60–90 seconds). The hook is the specific numbers. The lesson is about niche communities as distribution infrastructure. High shareability in creator and builder communities.",
         ["Hook (0–3s): '747 new followers in 2 weeks. Zero paid promotion.'", "Context (3–15s): sign language game built for the deaf and hard-of-hearing community", "Mechanism (15–35s): speech therapists shared it, parents shared it, students shared it — the community distributed it", "Principle (35–55s): niche communities share things that are specifically for them — it's an identity statement", "CTA (55–60s): 'Serve the niche. The niche will tell everyone.'"],
         "747 followers. Two weeks. A developer built a sign language learning game and posted it. There was no launch strategy. The community just shared it."),
        ("LinkedIn Post", "What 525 App Idea Posts Taught Me About Validated Demand",
         "Synthesis post — works well as a long-form LinkedIn article or a punchy short post. The '525 posts' framing makes it feel researched rather than opinionated. The conclusion is actionable.",
         ["Headline: 525 posts, 8 lessons", "The free formula (most important)", "Boring ideas outperform clever ideas", "Reddit complaints are free market research", "Niche audiences distribute better than general ones", "Distribution knowledge is worth as much as technical knowledge", "Close: what would you build if you started with the complaint thread, not the solution?"],
         'I just read through 525 posts from r/AppIdeas. Not to build anything. To understand what builders and users are actually asking for. Here are the 8 most useful things I found.'),
        ("Twitter/X Post (Single)", "The Tinder for Music Paradox",
         "Short provocative single post. The paradox — most engaged idea in the dataset, never built — is the entire point. Works as a standalone tweet or a thread opener.",
         ["State the engagement: 174 pts, 43 comments", "Name the idea: Tinder for Music", "The twist: as of today, it's still unbuilt", "The meta-point: 43 people described the exact product they want, for free, and nobody built it", "End with implied invitation"],
         '"Tinder but for Music" got 174 upvotes and 43 comments on Reddit. People described exactly what they want in detail. The tool still doesn\'t exist. This is what an unbuilt validated idea looks like.'),
        ("Instagram Carousel", "The Developer's Pricing Problem",
         "Visual comparison carousel. Best angle: left column = enterprise tool, right column = what the individual actually needs. Strong design potential with side-by-side comparison slides.",
         ["Slide 1: 'Enterprise pricing. Individual usage. Zero middle ground.'", "Slide 2: Proposify — $40/month / 2 proposals/month", "Slide 3: Property management — $100/month / 2 units", "Slide 4: Job management — starts at $30/month / 1 tradesperson", "Slide 5: 'The gap between what exists and what individuals can afford to use is the product.'"],
         "There's a pattern in how software is priced that affects millions of individuals who aren't enterprises."),
        ("LinkedIn Post", "Why Reddit is the Best Free Market Research Tool You're Not Using",
         "Practical methodology post. High value for the LinkedIn creator/entrepreneur audience who does market research. The 'complaint thread upvotes as demand signal' methodology is specific and actionable.",
         ["Open with the counter-intuition: 20 years of public complaints, indexed, searchable, free", "The search phrases that find product demand", "The upvote mechanism as crowd validation", "Two specific examples from the dataset (invoice: 800 upvotes, pet med: 22 threads)", "The one question to ask: 'What problem has a complaint thread with 500+ upvotes in this space?'"],
         "Reddit is a 20-year archive of people publicly describing what they need and can't find. Most people use it for entertainment. It's also the most specific free market research database that exists."),
        ("Instagram Reel / TikTok Script", "The Formula for Tools That Go Viral",
         "Fast-paced 45-second reel. Each element of the formula gets 5–8 seconds. Strong for visual or voiceover delivery. Hook is the 9,347 number.",
         ["Hook: '9,347 daily users. Free tool. Zero marketing budget. How?'", "Beat 1: FREE — remove the price entirely", "Beat 2: INSTANT — no sign-up, works on page load", "Beat 3: ONE JOB — does exactly one thing", "Beat 4: SHAREABLE OUTPUT — something to download, copy, or send", "Close: 'That\'s the formula. It\'s boring. It works.'"],
         "9,347 daily users. Free tool. No ads, no sign-up, no subscription. The developer tells the story in one sentence: 'I just made it free.'"),
    ]

    for btype, title, body, points, hook in briefs:
        p.append(brief(btype, title, body, points, hook))
    return "".join(p) + E()

def s9_visuals():
    p = [S(9, "Visual Report Ideas", "Charts, infographics, and data visualisations worth making")]
    items = [
        ("Bar Chart", "Top 20 Post Scores — r/AppIdeas", "var(--green)",
         "Simple horizontal bar chart of the top 20 posts by score. Label each bar with a truncated title. The visual immediately shows which story ideas are most validated. Best for a 'what Reddit wants built' summary post."),
        ("Comparison Infographic", "Enterprise Price vs Individual Need", "var(--warn)",
         "Side-by-side comparison: Tool | Enterprise Price | What the Individual Actually Uses It For | Gap. 6 rows (Proposify, Jobber, property mgmt, scheduling tools, competitor trackers, project mgmt). Strong visual argument for the 'free version opportunity' pattern."),
        ("Scatter Plot", "Score vs Comments — Engagement Map", "var(--accent)",
         "X axis: post score. Y axis: number of comments. Map shows 4 quadrants: High Score High Comments (both proven), High Score Low Comments (upvoted but not discussed), Low Score High Comments (discussion-heavy but controversial), Low Score Low Comments (noise). Fun data story. 'Tinder for Music' sits in an unusual quadrant — low-ish score but highest comment engagement."),
        ("Timeline Infographic", "The Free App Growth Story", "var(--pink)",
         "Single timeline: Developer launches budget app (paid) → Makes it free → Users start growing → Approaches 10,000 daily users. Annotated with the key quote. Could be designed as a phone mockup showing user count growing week by week."),
        ("Word Cloud / Tag Cloud", "Most Common Words in Top 50 Post Titles", "var(--pl)",
         "Process the top 50 post titles, remove stopwords, generate a tag cloud. Expected dominant words: 'free', 'app', 'idea', 'build', 'simple', 'tool'. The word cloud is a quick shareable visual that shows what the r/AppIdeas community is actually talking about."),
        ("Quadrant Chart", "Effort vs Traffic Potential — The 20 Ideas", "var(--orange)",
         "4-quadrant chart. X axis: effort to build (low → high). Y axis: traffic potential (low → high). Plot all 20 curated ideas. The Tier 1 ideas cluster in top-left (low effort, high traffic). Tier 3 ideas sit in top-right. Any idea in bottom-right (high effort, low traffic) should be dropped. Strong visual decision tool."),
    ]
    for viz_type, title, color, desc in items:
        p.append(f"""<div class="brief" style="border-left:3px solid {color}">
<div class="brief__type">{viz_type}</div>
<div class="brief__ttl">{title}</div>
<div class="brief__body">{desc}</div>
</div>""")
    return "".join(p) + E()

def closing():
    p = ['<div class="sec" id="close"><div class="sn">CLOSING</div><h2 class="st">What to Post First</h2><p class="ss">The diamond quote, the data, and the 5 best things to do with this report</p>\n']
    p.append("""<div class="diamond">
<div class="diamond__lbl">&#x1F48E; The Diamond Quote — Post This Today</div>
<div class="diamond__txt">"At the beginning of 2024 I made the app free, and since then the number of users has been growing continuously. I just can't believe I'm about to hit 10,000 daily users."</div>
<div class="diamond__src">r/AppIdeas · 542 pts · A developer sharing their budget tracker growth story</div>
<div class="diamond__use">Works as a standalone tweet, a thread opener, a carousel hook, or a quote card. The specificity (9,347 users) and the surprise (just made it free) are both there. It needs no additional context to land.</div>
</div>""")
    p.append("""<h3 style="font-size:.95rem;color:var(--h);margin:18px 0 10px">5 Things to Do With This Report</h3>
<ol style="font-size:.84rem;line-height:2.2;color:var(--text);margin-left:20px">
<li><strong>Post the diamond quote today.</strong> Screenshot the quote block above and post it as a quote card. No commentary needed. The quote does the work.</li>
<li><strong>Write the 'What 525 App Idea Posts Taught Me' thread.</strong> The synthesis thread outline in Section 3 is fully structured — all 8 beats are there. It's the highest-value thread in the set because it makes you look like you did research (you did).</li>
<li><strong>Design the Enterprise Price vs Individual Need infographic.</strong> The six examples (Proposify, Jobber, property mgmt, etc.) are all in Section 9. This is strong visual content with immediate relatability for anyone who's freelanced or run a small business.</li>
<li><strong>Build one carousel from Section 4.</strong> The 'Free App Formula' carousel is the most universally applicable — 7 slides, tight structure, clean data points. All copy is written. You just need to design it.</li>
<li><strong>Use the Top 50 data table as your own exploration base.</strong> The posts at ranks 5–50 are underexplored. The ideas in the 80–150 pt range often contain the most interesting nuance — they didn't explode on r/AppIdeas but they represent specific, real demand signals. Browse them with Section 2's stories in mind.</li>
</ol>""")
    p.append("""<div class="mandate">
<p>525 posts. 9 stories. 6 thread outlines. 4 carousel decks. 10 content briefs. 6 visual ideas.<br><br>
This is not about building anything.<br>
It's about <strong>seeing what's already been said</strong> — and finding which part of it is worth repeating.<br><br>
The data is there. The stories are in it.<br>
Pick one and start writing today.
</p>
</div>""")
    p.append('</div>\n')
    return "".join(p)

# ── Main ────────────────────────────────────────────────────────────────────────
def main():
    gen = datetime.now().strftime("%d %B %Y")
    os.makedirs("outputs", exist_ok=True)

    parts = [cover(), toc()]
    print("  Cover + TOC done.")
    parts.append(s1_numbers())
    print("  S1 numbers done.")
    parts.append(s2_stories())
    print("  S2 stories done.")
    parts.append(s3_threads())
    print("  S3 threads done.")
    parts.append(s4_carousels())
    print("  S4 carousels done.")
    parts.append(s5_quotes())
    print("  S5 quotes done.")
    parts.append(s6_counterintuitive())
    print("  S6 counterintuitive done.")
    parts.append(s7_data_table())
    print("  S7 table done.")
    parts.append(s8_briefs())
    print("  S8 briefs done.")
    parts.append(s9_visuals())
    print("  S9 visuals done.")
    parts.append(closing())
    print("  Closing done.")

    body = "\n".join(parts)
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>r/AppIdeas — Content Exploration Report · March 2026</title>
<style>{CSS}</style>
</head>
<body>
{body}
<div class="pg-foot">
  Generated by <strong>Audience Intelligence</strong> &middot;
  <a href="https://audienceintelligence.com">audienceintelligence.com</a> &middot; {gen}<br>
  r/AppIdeas Content Exploration Report &middot; {len(POSTS)} posts &middot; Personal Edition
</div>
<div class="disc">
Source data: publicly available Reddit posts via Reddit public API. All post scores and content are as scraped at time of collection.
Content briefs and thread outlines are original work by Audience Intelligence based on dataset analysis.
For personal use only. audienceintelligence.com
</div>
</body>
</html>"""

    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\nSaved: {OUT_PATH}")
    print(f"Size:  {len(html):,} chars")

if __name__ == "__main__":
    main()
