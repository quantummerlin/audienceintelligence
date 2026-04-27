"""
process_inbox.py
================
Drop any JSON dataset OR FOLDER into inbox/ and run this script.

Generates 2 content outputs per file:
  1.  reports/[slug].html                       — Full QM intelligence report
  2.  inbox/processed/[slug]-social.html        — Social content pack (hooks, threads, scripts)

Then moves the source JSON to inbox/processed/.

AI NEWS FOCUS: Content angles lean toward AI, tech, and digital culture.

Usage:
    python process_inbox.py                    # recursively process all JSON in inbox/
    python process_inbox.py inbox/myfile.json  # process one specific file
    python process_inbox.py inbox/myfolder/    # process all JSON in a specific folder

Folders dropped into inbox/ are scanned recursively.
The processed/ subfolder is always skipped.
Articles are NOT generated (use the report + social pack instead).

Files are processed in chunks of CHUNK_SIZE (default 3) with gc.collect()
between chunks to prevent memory buildup on large batches.

No external dependencies — stdlib only.
"""

import json, os, re, sys, math
from datetime import datetime
from collections import Counter
from pathlib import Path

# ─────────────────────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────────────────────
INBOX_DIR     = Path("inbox")
PROCESSED_DIR = INBOX_DIR / "processed"
REPORTS_DIR   = Path("reports")

SITE_NAME   = "AI.quantummerlin"
SITE_URL    = "https://ai.quantummerlin.com"
GA4_ID      = "G-VW4LGE7L1T"
ADSENSE_ID  = "ca-pub-3480541530392777"
LOGO_URL    = f"{SITE_URL}/logo.png"
TODAY       = datetime.now().strftime("%B %d, %Y")
TODAY_ISO   = datetime.now().strftime("%Y-%m-%d")

# Topics that get an AI-specific angle automatically
AI_KEYWORDS = {
    "chatgpt","gpt","claude","gemini","llm","openai","anthropic","mistral",
    "ai","artificial intelligence","machine learning","deepmind","copilot",
    "cursor","llama","vibe coding","agentic","automation","neural","model",
    "prompt","sora","midjourney","stable diffusion","dall-e","kling",
    "perplexity","bolt","v0","lovable","coding agent","github copilot",
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text)
    return text[:60].strip("-")


def word_count(texts):
    return sum(len(t.split()) for t in texts if t)


def score_sentence(sentence: str, keywords: set) -> float:
    """Simple relevance score: upvote-weighted keyword density."""
    words = set(sentence.lower().split())
    hits  = len(words & keywords)
    length_bonus = min(len(sentence) / 200, 1.0)
    return hits + length_bonus


def extract_top_sentences(texts, n=12, min_len=60):
    """Pull the n most interesting sentences across all texts."""
    sentences = []
    for t in texts:
        if not t:
            continue
        for s in re.split(r"(?<=[.!?])\s+", t):
            s = s.strip()
            if len(s) >= min_len and len(s) <= 500:
                sentences.append(s)
    # Score by length-weighted variety (longest unique ones first)
    seen = set()
    unique = []
    for s in sorted(sentences, key=len, reverse=True):
        key = s[:30].lower()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique[:n]


def top_ngrams(texts, n=2, top_k=20):
    """Return most common n-grams as topic signals."""
    STOPWORDS = {
        "the","and","a","an","to","of","in","is","it","i","my","me","that","this",
        "was","for","on","are","with","as","at","be","by","from","or","but","not",
        "have","had","he","she","we","they","so","if","do","did","up","out","about",
        "what","when","how","who","which","would","could","should","will","just",
        "like","than","then","there","been","has","its","also","more","very",
        "can","all","you","your","their","our","his","her","one","some","no",
        "any","now","get","got","into","know","think","time","way","new","good",
        "don","t","s","ve","ll","re","m","d","because","even","still","after",
        "back","just","only","other","same","such","too","over","through","already",
    }
    words = []
    for t in texts:
        if not t:
            continue
        toks = re.findall(r"[a-z']+", t.lower())
        toks = [w for w in toks if w not in STOPWORDS and len(w) > 2]
        if n == 1:
            words.extend(toks)
        else:
            words.extend([" ".join(toks[i:i+n]) for i in range(len(toks)-n+1)])
    return Counter(words).most_common(top_k)


def detect_ai_topic(texts_combined: str) -> bool:
    low = texts_combined.lower()
    return any(kw in low for kw in AI_KEYWORDS)


def generate_hooks(top_sentences, topic_name, is_ai):
    """Generate 8 viral hook starters from the data."""
    hooks = []
    prefix = "🤖 " if is_ai else "📊 "
    if top_sentences:
        s = top_sentences[0]
        hooks.append(f"I analysed thousands of real people talking about {topic_name}… this is what nobody is saying publicly.")
        hooks.append(f"The data doesn't lie. {s[:120]}…")
        hooks.append(f"Everyone has an opinion on {topic_name}. Here's what 10,000+ real people actually think.")
        hooks.append(f"Stop guessing what your audience wants. I read every comment so you don't have to. 🧵")
    if is_ai:
        hooks.append(f"The AI community just told us exactly what's broken about {topic_name}. Thread 👇")
        hooks.append(f"Real users. Real complaints. Real AI pain points. This is the {topic_name} thread nobody linked.")
        hooks.append(f"Before you build your next AI product — read what these 10,000 people said first.")
        hooks.append(f"The gap between AI marketing and AI reality is massive. Here's the proof.")
    else:
        hooks.append(f"Most people in {topic_name} communities share the same 3 fears. Here they are.")
        hooks.append(f"I found the signal in the noise. {topic_name} — decoded from real conversations.")
        hooks.append(f"Your competitors aren't reading their community. You should be.")
        hooks.append(f"This is what {topic_name} looks like from the inside.")
    return hooks[:8]


# ─────────────────────────────────────────────────────────────────────────────
# JSON FORMAT DETECTION & NORMALISATION
# ─────────────────────────────────────────────────────────────────────────────

def _parse_yt_views(views_str: str) -> int:
    """Convert '20,012 views' or '1.2M views' to int."""
    if not views_str:
        return 0
    s = str(views_str).lower().replace(",","").replace(" views","").strip()
    try:
        if s.endswith("m"):
            return int(float(s[:-1]) * 1_000_000)
        if s.endswith("k"):
            return int(float(s[:-1]) * 1_000)
        return int(float(re.sub(r"[^0-9.]","",s)) if s else 0)
    except (ValueError, TypeError):
        return 0


def normalise(raw) -> dict:
    """
    Accept any of:
      A) YouTube search export  {"query":"...", "videos":[{...}]}
      B) Reddit API Listing     {"kind":"Listing","data":{"children":[{"kind":"t3","data":{...}}]}}
      C) Array of post dicts    [{...}, ...]
      D) Array of comment strings ["text","text"]
      E) Aether flat export     [{"post_id":..., "title":..., "comments":[...]}]
    Returns: {"posts": [...], "source": str}
    """
    if isinstance(raw, dict):
        # ── YouTube search export ──────────────────────────────────────
        if "videos" in raw and isinstance(raw.get("videos"), list):
            query = raw.get("query","")
            posts = []
            for v in raw["videos"]:
                # Pull transcript text if available (string) or skip if error object
                transcript = v.get("transcript","")
                if isinstance(transcript, dict):
                    transcript = ""  # {"error":"..."} — no usable text
                body_parts = [
                    v.get("description",""),
                    transcript or "",
                ]
                body = " ".join(p for p in body_parts if p).strip()
                posts.append({
                    "id":        v.get("videoId",""),
                    "title":     v.get("title",""),
                    "body":      body,
                    "score":     _parse_yt_views(v.get("views","")),
                    "url":       v.get("url",""),
                    "author":    v.get("channel",""),
                    "subreddit": query,   # use query as the "community" label
                    "comments":  [],
                })
            return {"posts": posts, "source": "youtube_search"}

        # ── Reddit API listing ─────────────────────────────────────────
        children = raw.get("data", {}).get("children", [])
        posts = []
        for c in children:
            d = c.get("data", c)
            posts.append({
                "id":        d.get("id",""),
                "title":     d.get("title",""),
                "body":      d.get("selftext","") or d.get("body",""),
                "score":     d.get("score", 0),
                "url":       d.get("url",""),
                "author":    d.get("author",""),
                "subreddit": d.get("subreddit",""),
                "comments":  [],
            })
        return {"posts": posts, "source": "reddit_api_listing"}

    if isinstance(raw, list):
        if not raw:
            return {"posts": [], "source": "empty"}

        first = raw[0]

        # Array of strings → treat as comment corpus
        if isinstance(first, str):
            posts = [{"id": str(i), "title": "", "body": t, "score": 0,
                      "url": "", "author": "", "subreddit": "", "comments": []}
                     for i, t in enumerate(raw)]
            return {"posts": posts, "source": "string_corpus"}

        # Aether flat export (has "post_id" key)
        if "post_id" in first:
            posts = []
            for p in raw:
                comments = [{"body": c.get("body",""), "score": c.get("score",0)}
                            for c in p.get("comments", [])]
                posts.append({
                    "id":        p.get("post_id",""),
                    "title":     p.get("title",""),
                    "body":      p.get("selftext","") or p.get("body",""),
                    "score":     p.get("score",0),
                    "url":       p.get("url",""),
                    "author":    p.get("author",""),
                    "subreddit": p.get("subreddit",""),
                    "comments":  comments,
                })
            return {"posts": posts, "source": "aether_flat"}

        # Generic post array
        posts = []
        for p in raw:
            d = p.get("data", p)
            comments_raw = d.get("comments", [])
            comments = []
            for c in comments_raw:
                if isinstance(c, str):
                    comments.append({"body": c, "score": 0})
                elif isinstance(c, dict):
                    comments.append({"body": c.get("body","") or c.get("text",""), "score": c.get("score",0)})
            posts.append({
                "id":        d.get("id","") or d.get("post_id",""),
                "title":     d.get("title",""),
                "body":      d.get("selftext","") or d.get("body","") or d.get("content",""),
                "score":     d.get("score",0) or d.get("upvotes",0),
                "url":       d.get("url",""),
                "author":    d.get("author",""),
                "subreddit": d.get("subreddit",""),
                "comments":  comments,
            })
        return {"posts": posts, "source": "generic_array"}

    return {"posts": [], "source": "unknown"}


# ─────────────────────────────────────────────────────────────────────────────
# DATA ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def analyse(data: dict, filename: str) -> dict:
    posts    = data["posts"]
    source   = data["source"]
    is_yt    = (source == "youtube_search")

    all_titles   = [p["title"] for p in posts if p["title"]]
    all_bodies   = [p["body"]  for p in posts if p["body"]]
    all_comments = [c["body"]  for p in posts for c in p.get("comments",[]) if c.get("body")]

    # For YT: titles are the richest signal — include them in body analysis
    if is_yt:
        all_texts = all_titles + all_bodies
    else:
        all_texts = all_bodies + all_comments

    subreddits = Counter(p["subreddit"] for p in posts if p["subreddit"])
    top_sub    = subreddits.most_common(1)[0][0] if subreddits else "community"

    # Guess topic name
    stem = Path(filename).stem
    if is_yt:
        # Strip yt_ prefix and timestamp suffix from filename
        stem = re.sub(r"^yt_", "", stem, flags=re.I)
        stem = re.sub(r"_\d{10,}$", "", stem)
    else:
        stem = re.sub(r"^(reddit|outputs?[-_]?)", "", stem, flags=re.I)
    topic_name = (top_sub or stem or "this community").replace("-"," ").replace("_"," ").strip()

    # Stats
    total_posts    = len(posts)
    total_comments = len(all_comments)
    total_words    = word_count(all_texts)
    total_score    = sum(p["score"] for p in posts)
    avg_score      = int(total_score / max(total_posts,1))
    top_posts      = sorted(posts, key=lambda x: x["score"], reverse=True)[:8]

    # Top comments by score (for YT, use top posts as verbatims since no comments)
    if is_yt:
        scored_comments = [{"body": p["title"], "score": p["score"]} for p in top_posts]
    else:
        scored_comments = sorted(
            [c for p in posts for c in p.get("comments",[]) if c.get("body")],
            key=lambda x: x.get("score",0),
            reverse=True
        )[:20]

    # Interesting sentences
    top_sentences = extract_top_sentences(all_texts, n=16)

    # Topic signals
    bigrams  = top_ngrams(all_texts, n=2, top_k=24)
    trigrams = top_ngrams(all_texts, n=3, top_k=16)

    is_ai   = detect_ai_topic(" ".join(all_texts[:50]))
    hooks   = generate_hooks(top_sentences, topic_name, is_ai)

    # Derive key patterns from top bigrams
    patterns = []
    for phrase, count in bigrams[:10]:
        if count >= 2:
            patterns.append({"phrase": phrase, "count": count})

    return {
        "filename":       filename,
        "stem":           stem,
        "source":         source,
        "is_yt":          is_yt,
        "topic_name":     topic_name,
        "top_sub":        top_sub,
        "subreddits":     dict(subreddits.most_common(6)),
        "total_posts":    total_posts,
        "total_comments": total_comments,
        "total_words":    total_words,
        "total_score":    total_score,
        "avg_score":      avg_score,
        "top_posts":      top_posts,
        "scored_comments":scored_comments,
        "top_sentences":  top_sentences,
        "bigrams":        bigrams,
        "trigrams":       trigrams,
        "is_ai":          is_ai,
        "hooks":          hooks,
        "patterns":       patterns,
        "all_texts":      all_texts,
        "all_titles":     all_titles,
    }


# ─────────────────────────────────────────────────────────────────────────────
# SHARED CSS — QM BRAND
# ─────────────────────────────────────────────────────────────────────────────

QM_CSS = """
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cinzel+Decorative:wght@700;900&family=Orbitron:wght@400;600;700;800;900&family=Exo+2:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root {
  --cyan:#00f5ff; --magenta:#ff00ff; --pink:#ff1493; --purple:#9d00ff;
  --gold:#ffd700; --green:#00ff88; --blue:#00a8ff;
  --bg:#0a0a0f; --bg2:#0d0d18; --card:rgba(20,20,39,0.9);
  --card2:rgba(30,30,55,0.85); --border:rgba(0,245,255,0.12);
  --txt:#fff; --txt2:rgba(255,255,255,0.68); --txt3:rgba(255,255,255,0.38);
  --ff-display:'Orbitron',monospace; --ff-body:'Exo 2',sans-serif;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html{scroll-behavior:smooth;-webkit-font-smoothing:antialiased}
body{font-family:var(--ff-body);background:var(--bg);color:var(--txt);line-height:1.7;overflow-x:hidden}
a{color:var(--cyan);text-decoration:none}
a:hover{opacity:.8}
h1,h2,h3,h4{font-family:var(--ff-display)}
img{max-width:100%}
.container{max-width:900px;margin:0 auto;padding:0 24px}

/* ── NAV ── */
.site-nav{
  position:sticky;top:0;z-index:100;
  background:rgba(10,10,15,.92);backdrop-filter:blur(20px);
  border-bottom:1px solid rgba(0,245,255,.08);
  padding:14px 0;
}
.site-nav .container{display:flex;align-items:center;justify-content:space-between;gap:12px}
.nav-logo{font-family:var(--ff-display);font-size:.9rem;font-weight:900;letter-spacing:.04em;display:flex;align-items:baseline;gap:0}
.nav-logo .ai{background:linear-gradient(135deg,#00f5ff,#9d00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.nav-logo .qm{color:rgba(255,255,255,.4);font-size:.7rem}
.nav-links{display:flex;gap:18px;flex-wrap:wrap}
.nav-links a{font-size:.78rem;color:var(--txt2);font-family:var(--ff-display);letter-spacing:.04em;transition:color .2s}
.nav-links a:hover{color:var(--cyan)}

/* ── HERO ── */
.report-hero{
  padding:72px 0 56px;
  background:linear-gradient(160deg,#050015,#0a0a0f 50%,#050015);
  position:relative;overflow:hidden;
}
.report-hero::before{
  content:'';position:absolute;inset:0;
  background:radial-gradient(ellipse at 20% 40%,rgba(0,245,255,.07),transparent 55%),
             radial-gradient(ellipse at 80% 60%,rgba(157,0,255,.06),transparent 55%);
  pointer-events:none;
}
.hero-eyebrow{
  display:inline-flex;align-items:center;gap:8px;
  padding:5px 14px;border-radius:20px;margin-bottom:18px;
  background:rgba(0,245,255,.08);border:1px solid rgba(0,245,255,.22);
  font-family:var(--ff-display);font-size:.6rem;font-weight:700;
  color:var(--cyan);letter-spacing:.12em;
}
.hero-title{
  font-family:'Cinzel Decorative',serif;
  font-size:clamp(1.6rem,4.5vw,2.8rem);font-weight:700;line-height:1.2;
  background:linear-gradient(135deg,#00f5ff 0%,#ff00ff 55%,#ffd700 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  filter:drop-shadow(0 0 18px rgba(0,245,255,.3));margin-bottom:16px;
}
.hero-sub{font-size:1rem;color:var(--txt2);max-width:620px;line-height:1.7;margin-bottom:28px}
.hero-stats{display:flex;flex-wrap:wrap;gap:28px;padding-top:24px;border-top:1px solid rgba(255,255,255,.06)}
.hs{text-align:center}
.hs-val{font-family:var(--ff-display);font-size:1.6rem;font-weight:800;background:linear-gradient(135deg,#00f5ff,#ff00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;display:block}
.hs-lbl{font-size:.62rem;color:var(--txt3);text-transform:uppercase;letter-spacing:.1em;margin-top:2px}

/* ── SECTIONS ── */
.report-body{padding:56px 0}
.section{margin-bottom:56px;padding-bottom:40px;border-bottom:1px solid rgba(255,255,255,.05)}
.section:last-child{border-bottom:none}
.sec-label{font-family:var(--ff-display);font-size:.58rem;color:var(--cyan);font-weight:700;letter-spacing:.18em;text-transform:uppercase;margin-bottom:6px}
.sec-title{font-family:var(--ff-display);font-size:1.3rem;font-weight:700;color:#fff;margin-bottom:6px}
.sec-sub{font-size:.88rem;color:var(--txt2);margin-bottom:22px}

/* ── CARDS ── */
.card{background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:20px 22px;margin-bottom:12px;border-left:3px solid var(--cyan)}
.card-cyan{border-left-color:var(--cyan)}
.card-gold{border-left-color:var(--gold)}
.card-pink{border-left-color:var(--pink)}
.card-purple{border-left-color:var(--purple)}
.card-green{border-left-color:var(--green)}
.card-hd{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;margin-bottom:8px}
.card-name{font-size:.92rem;font-weight:700;color:#fff}
.card-tag{font-size:.65rem;color:var(--txt3);background:rgba(255,255,255,.05);padding:3px 9px;border-radius:10px;white-space:nowrap}

/* ── QUOTES ── */
.quote{background:rgba(0,245,255,.04);border-left:3px solid var(--cyan);border-radius:0 10px 10px 0;padding:12px 16px;margin:10px 0;font-size:.88rem;font-style:italic;line-height:1.6;color:var(--txt2)}
.quote-score{font-size:.62rem;color:var(--txt3);font-style:normal;margin-top:5px;display:block}
.quote-gold{border-left-color:var(--gold);background:rgba(255,215,0,.04)}
.quote-pink{border-left-color:var(--pink);background:rgba(255,20,147,.04)}

/* ── STATS GRID ── */
.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin:16px 0}
.stat{background:var(--card);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:16px 12px;text-align:center}
.stat-val{font-family:var(--ff-display);font-size:1.7rem;font-weight:800;display:block;line-height:1;margin-bottom:5px}
.stat-lbl{font-size:.63rem;color:var(--txt3);text-transform:uppercase;letter-spacing:.08em}
.stat-cyan .stat-val{background:linear-gradient(135deg,#00f5ff,#9d00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.stat-gold .stat-val{background:linear-gradient(135deg,#ffd700,#ff8c00);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
.stat-pink .stat-val{background:linear-gradient(135deg,#ff1493,#ff00ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}

/* ── PATTERN PILLS ── */
.patterns{display:flex;flex-wrap:wrap;gap:8px;margin:14px 0}
.pattern-pill{padding:6px 14px;border-radius:20px;font-size:.75rem;font-weight:600;font-family:var(--ff-display);letter-spacing:.02em;cursor:default}
.pp-cyan{background:rgba(0,245,255,.1);border:1px solid rgba(0,245,255,.25);color:var(--cyan)}
.pp-gold{background:rgba(255,215,0,.1);border:1px solid rgba(255,215,0,.25);color:var(--gold)}
.pp-pink{background:rgba(255,20,147,.1);border:1px solid rgba(255,20,147,.25);color:var(--pink)}
.pp-purple{background:rgba(157,0,255,.1);border:1px solid rgba(157,0,255,.25);color:#c86fff}
.pp-green{background:rgba(0,255,136,.1);border:1px solid rgba(0,255,136,.25);color:var(--green)}

/* ── HOOKS ── */
.hook-card{background:var(--card2);border:1px solid rgba(255,215,0,.12);border-radius:12px;padding:16px 18px;margin-bottom:10px;display:flex;gap:12px;align-items:flex-start}
.hook-num{font-family:var(--ff-display);font-size:.7rem;font-weight:800;color:var(--gold);flex-shrink:0;min-width:22px;margin-top:1px}
.hook-text{font-size:.88rem;color:var(--txt2);line-height:1.55}
.hook-copy-btn{flex-shrink:0;padding:4px 10px;background:rgba(255,215,0,.1);border:1px solid rgba(255,215,0,.22);border-radius:8px;color:var(--gold);font-size:.62rem;font-family:var(--ff-display);font-weight:700;cursor:pointer;transition:all .2s;user-select:none}
.hook-copy-btn:hover{background:rgba(255,215,0,.18)}

/* ── TOPIC CLOUD ── */
.topic-cloud{display:flex;flex-wrap:wrap;gap:7px;margin:14px 0}
.topic-tag{padding:5px 12px;border-radius:20px;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.08);font-size:.74rem;color:var(--txt2);letter-spacing:.01em}
.topic-tag.hot{background:rgba(0,245,255,.08);border-color:rgba(0,245,255,.2);color:var(--cyan)}

/* ── CTA BOX ── */
.cta-box{background:linear-gradient(135deg,rgba(0,245,255,.05),rgba(157,0,255,.05));border:1px solid rgba(0,245,255,.12);border-radius:16px;padding:36px;text-align:center;margin:40px 0}
.cta-box h3{font-family:var(--ff-display);font-size:1.1rem;margin-bottom:10px;color:#fff}
.cta-box p{font-size:.88rem;color:var(--txt2);margin-bottom:20px}
.cta-btn{display:inline-flex;align-items:center;gap:8px;padding:12px 28px;background:linear-gradient(135deg,#00f5ff,#9d00ff);color:#fff;border-radius:50px;font-family:var(--ff-display);font-size:.78rem;font-weight:700;letter-spacing:.06em;box-shadow:0 5px 22px rgba(0,245,255,.28);transition:all .25s}
.cta-btn:hover{transform:translateY(-2px);box-shadow:0 8px 30px rgba(0,245,255,.38)}

/* ── FOOTER ── */
.site-footer{background:var(--bg2);border-top:1px solid rgba(255,255,255,.05);padding:36px 0;text-align:center}
.site-footer p{font-size:.75rem;color:var(--txt3);line-height:1.8}
.site-footer a{color:var(--txt3);transition:color .2s}
.site-footer a:hover{color:var(--cyan)}

/* ── RESPONSIVE ── */
@media(max-width:680px){
  .report-hero{padding:48px 0 36px}
  .hero-title{font-size:clamp(1.2rem,6vw,1.8rem)}
  .hero-stats{gap:16px}
  .stats-grid{grid-template-columns:repeat(2,1fr)}
  .nav-links{display:none}
}
</style>
"""

QM_HEAD_EXTRAS = f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={GA4_ID}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{GA4_ID}');</script>
<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ADSENSE_ID}" crossorigin="anonymous"></script>
"""

QM_NAV = f"""
<nav class="site-nav">
  <div class="container">
    <a href="{SITE_URL}" class="nav-logo">
      <span class="ai">AI</span><span style="color:rgba(255,255,255,.3);font-size:1.1rem">.</span><span class="qm">QM</span>
    </a>
    <div class="nav-links">
      <a href="{SITE_URL}">Home</a>
      <a href="{SITE_URL}#models">Models</a>
      <a href="{SITE_URL}#news">News</a>
      <a href="{SITE_URL}#tools">Tools</a>
      <a href="{SITE_URL}/reports/">Reports</a>
    </div>
  </div>
</nav>
"""

QM_FOOTER = f"""
<footer class="site-footer">
  <div class="container">
    <p>
      <strong style="color:rgba(255,255,255,.6);font-family:var(--ff-display);font-size:.7rem">AI.QUANTUMMERLIN.COM</strong><br>
      Intelligence extracted from real communities.<br>
      <a href="{SITE_URL}">Home</a> &nbsp;·&nbsp;
      <a href="{SITE_URL}/methodology.html">Methodology</a> &nbsp;·&nbsp;
      <a href="https://quantummerlin.com" target="_blank" rel="noopener">🔮 quantummerlin.com</a><br>
      &copy; {datetime.now().year} Quantum Merlin
    </p>
  </div>
</footer>
"""

ADSENSE_BLOCK = f"""
<div style="margin:36px 0;text-align:center">
  <ins class="adsbygoogle" style="display:block" data-ad-client="{ADSENSE_ID}"
       data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
  <script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>
</div>
"""

COPY_JS = """
<script>
document.querySelectorAll('.hook-copy-btn').forEach(btn=>{
  btn.addEventListener('click',()=>{
    const text=btn.closest('.hook-card').querySelector('.hook-text').textContent.trim();
    navigator.clipboard.writeText(text).then(()=>{
      const orig=btn.textContent;btn.textContent='COPIED!';
      setTimeout(()=>btn.textContent=orig,1500);
    }).catch(()=>{});
  });
});
document.querySelectorAll('.copy-btn').forEach(btn=>{
  btn.addEventListener('click',()=>{
    const target=document.getElementById(btn.dataset.target);
    if(!target)return;
    navigator.clipboard.writeText(target.textContent.trim()).then(()=>{
      const orig=btn.textContent;btn.textContent='✓ Copied';
      setTimeout(()=>btn.textContent=orig,1500);
    });
  });
});
</script>
"""

PILL_CLASSES = ["pp-cyan","pp-gold","pp-pink","pp-purple","pp-green"]
STAT_CLASSES  = ["stat-cyan","stat-gold","stat-pink","stat-cyan","stat-gold"]


def fmt_num(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(n)


# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT 1 — INTELLIGENCE REPORT
# ─────────────────────────────────────────────────────────────────────────────

def build_report(a: dict) -> str:
    slug       = slugify(a["topic_name"])
    topic      = a["topic_name"].title()
    is_ai      = a["is_ai"]
    ai_tag     = "AI · " if is_ai else ""
    eyebrow    = f"✦ {ai_tag}INTELLIGENCE REPORT · {TODAY}"
    title_line = f"What {fmt_num(a['total_words'])}+ words on {topic} actually reveal"

    # Top posts HTML
    top_posts_html = ""
    for i, p in enumerate(a["top_posts"][:6], 1):
        title = p["title"] or p["body"][:80]
        body  = p["body"][:220].replace("<","&lt;").replace(">","&gt;") if p["body"] else ""
        score = fmt_num(p["score"])
        top_posts_html += f"""
        <div class="card card-{'cyan' if i<=2 else 'purple' if i<=4 else 'gold'}">
          <div class="card-hd">
            <span class="card-name">#{i} — {title[:90]}</span>
            <span class="card-tag">▲ {score}</span>
          </div>
          <p style="font-size:.84rem;color:var(--txt2)">{body}{'…' if body else ''}</p>
        </div>"""

    # Top verbatims HTML
    verbatims_html = ""
    pill_styles = ["quote","quote-gold","quote-pink","quote","quote-gold","quote-pink"]
    for i, c in enumerate(a["scored_comments"][:10]):
        body  = c["body"][:320].replace("<","&lt;").replace(">","&gt;")
        score = c.get("score",0)
        ps    = pill_styles[i % len(pill_styles)]
        verbatims_html += f"""
        <div class="{ps}">
          {body}{'…' if len(c['body'])>320 else ''}
          {f'<span class="quote-score">▲ {fmt_num(score)} upvotes</span>' if score else ''}
        </div>"""

    # Patterns HTML
    patterns_html = "<div class='patterns'>"
    for i, (phrase, cnt) in enumerate(a["bigrams"][:18]):
        pcls = PILL_CLASSES[i % len(PILL_CLASSES)]
        patterns_html += f"<span class='pattern-pill {pcls}'>{phrase} ({cnt})</span>"
    patterns_html += "</div>"

    # Key sentences
    sentences_html = ""
    for s in a["top_sentences"][:8]:
        sentences_html += f"<div class='quote'>{s.replace('<','&lt;').replace('>','&gt;')}</div>"

    # Stats — labels differ for YT vs Reddit
    _lbl_posts    = "Videos"        if a.get("is_yt") else "Posts"
    _lbl_comments = "Channels"      if a.get("is_yt") else "Comments"
    _lbl_score    = "Total Views"   if a.get("is_yt") else "Total Upvotes"
    stats_html = f"""
    <div class="stats-grid">
      <div class="stat stat-cyan"><span class="stat-val">{fmt_num(a['total_words'])}</span><span class="stat-lbl">Words Analysed</span></div>
      <div class="stat stat-gold"><span class="stat-val">{fmt_num(a['total_posts'])}</span><span class="stat-lbl">{_lbl_posts}</span></div>
      <div class="stat stat-pink"><span class="stat-val">{fmt_num(a['total_comments']) if not a.get('is_yt') else fmt_num(len(set(p['author'] for p in a.get('top_posts',[]))))}</span><span class="stat-lbl">{_lbl_comments}</span></div>
      <div class="stat stat-cyan"><span class="stat-val">{fmt_num(a['total_score'])}</span><span class="stat-lbl">{_lbl_score}</span></div>
    </div>"""

    # Hooks for report CTA
    hooks_preview = "".join(
        f"<div class='hook-card'><span class='hook-num'>H{i+1}</span><span class='hook-text'>{h}</span><button class='hook-copy-btn'>COPY</button></div>"
        for i, h in enumerate(a["hooks"][:4])
    )

    # Trigram signals
    signals_html = "<div class='topic-cloud'>"
    for i, (phrase, cnt) in enumerate(a["trigrams"][:12]):
        cls = "hot" if i < 4 else ""
        signals_html += f"<span class='topic-tag {cls}'>{phrase}</span>"
    signals_html += "</div>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=5.0">
<title>{topic} Intelligence Report | {SITE_NAME}</title>
<meta name="description" content="Deep intelligence extracted from {fmt_num(a['total_words'])}+ words in the {topic} community. Patterns, verbatims, hooks, and opportunities.">
<link rel="canonical" href="{SITE_URL}/reports/{slug}.html">
<meta property="og:title" content="{topic} Intelligence Report | {SITE_NAME}">
<meta property="og:description" content="What {fmt_num(a['total_words'])}+ words on {topic} actually reveal.">
<meta property="og:image" content="{LOGO_URL}">
<meta property="og:url" content="{SITE_URL}/reports/{slug}.html">
<meta property="og:site_name" content="{SITE_NAME}">
<meta name="twitter:card" content="summary_large_image">
{QM_HEAD_EXTRAS}
{QM_CSS}
</head>
<body>
{QM_NAV}

<section class="report-hero">
  <div class="container">
    <div class="hero-eyebrow">{eyebrow}</div>
    <h1 class="hero-title">{title_line}</h1>
    <p class="hero-sub">
      Intelligence extracted from {fmt_num(a['total_posts'])} posts and {fmt_num(a['total_comments'])} comments
      in the <strong style="color:var(--cyan)">{topic}</strong> community.
      {fmt_num(a['total_words'])}+ words. {fmt_num(a['total_score'])} collective upvotes.
      The signal buried in the noise — surfaced.
    </p>
    <div class="hero-stats">
      <div class="hs"><span class="hs-val">{fmt_num(a['total_words'])}</span><span class="hs-lbl">Words</span></div>
      <div class="hs"><span class="hs-val">{fmt_num(a['total_posts'])}</span><span class="hs-lbl">Posts</span></div>
      <div class="hs"><span class="hs-val">{fmt_num(a['total_comments'])}</span><span class="hs-lbl">Comments</span></div>
      <div class="hs"><span class="hs-val">{fmt_num(a['total_score'])}</span><span class="hs-lbl">Upvotes</span></div>
    </div>
  </div>
</section>

{ADSENSE_BLOCK}

<div class="report-body">
<div class="container">

  <!-- SECTION 1: Overview Stats -->
  <div class="section">
    <p class="sec-label">Section 01</p>
    <h2 class="sec-title">The Numbers</h2>
    <p class="sec-sub">What the raw data looks like before the patterns emerge.</p>
    {stats_html}
  </div>

  <!-- SECTION 2: Top Posts -->
  <div class="section">
    <p class="sec-label">Section 02</p>
    <h2 class="sec-title">Highest-Signal Posts</h2>
    <p class="sec-sub">The posts that generated the most engagement — where the real conversations happened.</p>
    {top_posts_html}
  </div>

  <!-- SECTION 3: Community Verbatims -->
  <div class="section">
    <p class="sec-label">Section 03</p>
    <h2 class="sec-title">What They're Actually Saying</h2>
    <p class="sec-sub">Real quotes from the community, ranked by upvotes. These are not summaries — these are the exact words.</p>
    {verbatims_html}
  </div>

  {ADSENSE_BLOCK}

  <!-- SECTION 4: Patterns -->
  <div class="section">
    <p class="sec-label">Section 04</p>
    <h2 class="sec-title">Recurring Language Patterns</h2>
    <p class="sec-sub">Phrases that appeared repeatedly across the dataset — these are the mental models and vocabulary this community lives in.</p>
    {patterns_html}
  </div>

  <!-- SECTION 5: Key Signals -->
  <div class="section">
    <p class="sec-label">Section 05</p>
    <h2 class="sec-title">Key Sentences Extracted</h2>
    <p class="sec-sub">The most information-dense statements pulled from the corpus — representing the community's core beliefs and pain points.</p>
    {sentences_html}
  </div>

  <!-- SECTION 6: Topic Signals -->
  <div class="section">
    <p class="sec-label">Section 06</p>
    <h2 class="sec-title">Emerging Topic Signals</h2>
    <p class="sec-sub">Three-word phrases that appear as distinct topic clusters in the data.</p>
    {signals_html}
  </div>

  <!-- SECTION 7: Content Gold (Hooks) -->
  <div class="section">
    <p class="sec-label">Section 07</p>
    <h2 class="sec-title">Content Gold — Proven Hooks</h2>
    <p class="sec-sub">Hook angles generated directly from this dataset. Based on what the community cares about most.</p>
    {hooks_preview}
    <p style="margin-top:16px;font-size:.82rem;color:var(--txt3)">
      → Full social content pack: <a href="../inbox/processed/{slug}-social.html">view social pack</a>
    </p>
  </div>

  <!-- CTA -->
  <div class="cta-box">
    <h3>⚡ Need a Custom Dataset Report?</h3>
    <p>Drop your own community data and we'll extract the patterns, pain points, and content opportunities — formatted and ready to use.</p>
    <a href="https://quantumtoolsmith.gumroad.com" class="cta-btn" target="_blank" rel="noopener">🔮 Order Custom Report</a>
  </div>

</div>
</div>

{QM_FOOTER}
{COPY_JS}
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT 2 — LONG-FORM ARTICLE
# ─────────────────────────────────────────────────────────────────────────────

def build_article(a: dict) -> str:
    slug    = slugify(a["topic_name"])
    topic   = a["topic_name"].title()
    is_ai   = a["is_ai"]

    # Article title — generate narrative angle
    if is_ai:
        article_title  = f"The Real State of {topic}: What Thousands of AI Users Are Actually Saying"
        article_intro  = f"""The official narrative around {topic} is polished, curated, and carefully managed. The community's version is rawer, more honest — and far more useful.

We analysed {fmt_num(a['total_words'])}+ words of real discussion across {fmt_num(a['total_posts'])} posts and {fmt_num(a['total_comments'])} comments. What follows isn't a press release. It's what people actually think — the frustrations, the breakthroughs, the patterns that keep emerging no matter where you look."""
        angle_h2 = "Why the AI Community's Own Words Matter More Than Any Benchmark"
        angle_p  = f"""Every AI model gets a benchmark score. Every AI tool gets a Product Hunt launch. What almost nobody tracks is the sustained, unfiltered reaction from the people who use these things every day — the developers, the creators, the power users who've moved past the demo.

That's what this data captures. {fmt_num(a['total_score'])} upvotes worth of real signal from real people in the {topic} community."""
    else:
        article_title  = f"Inside {topic}: The Patterns Nobody Is Talking About"
        article_intro  = f"""Every community has two conversations: the one that happens publicly, and the one that happens when people feel safe enough to be honest. We read both.

Across {fmt_num(a['total_words'])}+ words, {fmt_num(a['total_posts'])} posts, and {fmt_num(a['total_comments'])} comments in the {topic} community, clear patterns emerged — patterns that repeat across demographics, time zones, and experience levels. This is what the data found."""
        angle_h2 = f"The Hidden Consensus Inside the {topic} Community"
        angle_p  = f"""Communities develop shared vocabularies. They develop shared fears. They develop shared frustrations — even when members have never interacted with each other. The {topic} dataset makes this visible in a way that no survey or focus group ever could.

{fmt_num(a['total_score'])} collective upvotes. The things people agreed with loudly, in public, at scale."""

    # Build 3 body sections from top sentences
    S = a["top_sentences"]
    sec1 = S[0:3] if len(S)>=3 else S
    sec2 = S[3:6] if len(S)>=6 else []
    sec3 = S[6:9] if len(S)>=9 else []

    def quote_block(sentences):
        return "".join(
            f'<blockquote style="border-left:3px solid var(--cyan);padding:12px 18px;margin:16px 0;background:rgba(0,245,255,.04);border-radius:0 10px 10px 0;font-style:italic;color:var(--txt2);font-size:.92rem">{s.replace("<","&lt;").replace(">","&gt;")}</blockquote>'
            for s in sentences
        )

    # Top bigrams as patterns
    pattern_list = "\n".join(
        f'<li style="margin-bottom:8px"><strong style="color:var(--cyan)">{phrase}</strong> — appeared {cnt} times across the dataset</li>'
        for phrase, cnt in a["bigrams"][:8]
    )

    # What to do next — content angles
    content_ideas = []
    for h in a["hooks"][:5]:
        content_ideas.append(
            f'<li style="margin-bottom:10px;font-size:.9rem;color:var(--txt2)">{h}</li>'
        )
    content_ideas_html = "\n".join(content_ideas)

    article_css = """
<style>
.article-container{max-width:720px;margin:0 auto;padding:0 24px}
.article-hero{padding:64px 0 48px;border-bottom:1px solid rgba(255,255,255,.06);margin-bottom:48px}
.article-cat{display:inline-flex;align-items:center;gap:6px;padding:4px 12px;border-radius:20px;background:rgba(0,245,255,.08);border:1px solid rgba(0,245,255,.2);font-family:var(--ff-display);font-size:.58rem;font-weight:700;color:var(--cyan);letter-spacing:.12em;margin-bottom:14px}
.article-title{font-family:'Cinzel Decorative',serif;font-size:clamp(1.5rem,4vw,2.4rem);font-weight:700;line-height:1.25;background:linear-gradient(135deg,#00f5ff,#ff00ff 60%,#ffd700);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:16px}
.article-meta{font-size:.76rem;color:var(--txt3);font-family:var(--ff-display);letter-spacing:.06em}
.article-body{font-size:1rem;line-height:1.8;color:var(--txt2)}
.article-body p{margin-bottom:1.4rem}
.article-body h2{font-family:var(--ff-display);font-size:1.1rem;font-weight:700;color:#fff;margin:2.5rem 0 .9rem;letter-spacing:.03em}
.article-body h3{font-size:.95rem;font-weight:700;color:var(--cyan);margin:1.8rem 0 .7rem;font-family:var(--ff-display)}
.article-body ul,ol{margin:0 0 1.4rem 22px}
.article-body li{margin-bottom:.5rem}
.pull-quote{font-size:1.25rem;font-style:italic;color:#fff;border-left:4px solid var(--gold);padding:16px 24px;margin:2.5rem 0;background:rgba(255,215,0,.05);border-radius:0 12px 12px 0;line-height:1.5}
@media(max-width:600px){.article-title{font-size:1.4rem}}
</style>
"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=5.0">
<title>{article_title} | {SITE_NAME}</title>
<meta name="description" content="We analysed {fmt_num(a['total_words'])}+ words from the {topic} community. Here's what the data actually shows.">
<link rel="canonical" href="{SITE_URL}/articles/{slug}-article.html">
<meta property="og:title" content="{article_title}">
<meta property="og:description" content="Real patterns from {fmt_num(a['total_words'])}+ words of community discussion.">
<meta property="og:image" content="{LOGO_URL}">
<meta property="og:url" content="{SITE_URL}/articles/{slug}-article.html">
<meta name="twitter:card" content="summary_large_image">
{QM_HEAD_EXTRAS}
{QM_CSS}
{article_css}
</head>
<body>
{QM_NAV}

<div class="article-container">

  <div class="article-hero">
    <span class="article-cat">{'🤖 AI INTELLIGENCE' if is_ai else '📊 COMMUNITY INTELLIGENCE'}</span>
    <h1 class="article-title">{article_title}</h1>
    <div class="article-meta">
      {TODAY} &nbsp;·&nbsp; {fmt_num(a['total_words'])}+ words analysed &nbsp;·&nbsp;
      {fmt_num(a['total_posts'])} posts &nbsp;·&nbsp; {fmt_num(a['total_comments'])} comments
    </div>
  </div>

  {ADSENSE_BLOCK}

  <div class="article-body">

    <p>{article_intro.replace(chr(10), '</p><p>')}</p>

    <h2>{angle_h2}</h2>
    <p>{angle_p.replace(chr(10), '</p><p>')}</p>

    {quote_block(sec1)}

    <div class="pull-quote">
      "{S[0][:180] if S else 'The community has spoken.'}"
    </div>

    <h2>The Patterns That Keep Appearing</h2>
    <p>
      Across {fmt_num(a['total_posts'])} independent posts, certain language patterns emerged with unusual consistency.
      These aren't cherry-picked — they're the phrases and concepts that appeared most frequently in the corpus,
      surfaced algorithmically from the full dataset.
    </p>
    <ul>
      {pattern_list}
    </ul>

    {quote_block(sec2)}

    <h2>What Changed — And What Didn't</h2>
    <p>
      The {topic} community has been talking about these issues for some time.
      What's new is the intensity. The volume of posts. The specificity of the frustrations.
      Something has shifted — and the data makes it visible.
    </p>

    {quote_block(sec3)}

    {ADSENSE_BLOCK}

    <h2>What This Means for Content Creators and Builders</h2>
    <p>
      If you create content, build products, or market anything in or adjacent to {topic},
      this dataset is a gold mine. Here are the angles the community has already validated:
    </p>
    <ul>
      {content_ideas_html}
    </ul>

    <h2>The Bottom Line</h2>
    <p>
      Communities don't lie — at least not when they think nobody is listening.
      {fmt_num(a['total_score'])} upvotes across {fmt_num(a['total_posts'])} posts represents a level of signal
      that no survey could replicate. The community told us exactly what matters to them.
      The only question is whether you act on it.
    </p>

    <div class="cta-box" style="margin:48px 0 24px">
      <h3>⚡ See the Full Intelligence Report</h3>
      <p>The complete dataset breakdown — patterns, verbatims, hooks, and market signals.</p>
      <a href="../reports/{slug}.html" class="cta-btn">📊 View Full Report</a>
    </div>

  </div>
</div>

{QM_FOOTER}
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# OUTPUT 3 — SOCIAL CONTENT PACK
# ─────────────────────────────────────────────────────────────────────────────

def build_social_pack(a: dict) -> str:
    slug    = slugify(a["topic_name"])
    topic   = a["topic_name"].title()
    is_ai   = a["is_ai"]
    S       = a["top_sentences"]
    hooks   = a["hooks"]

    # Generate Twitter/X thread
    thread_items = []
    thread_items.append(f"🧵 I analysed {fmt_num(a['total_words'])}+ words from the {topic} community.\n\nHere's what {fmt_num(a['total_posts'])} posts and {fmt_num(a['total_comments'])} comments reveal that nobody is talking about. 👇")
    for i, (phrase, cnt) in enumerate(a["bigrams"][:5], 1):
        thread_items.append(f"{i}/ The phrase \"{phrase}\" appeared {cnt} times. That's not a coincidence — that's a pattern.")
    for i, sent in enumerate(S[:3], len(thread_items)):
        thread_items.append(f"{i+1}/ \"{sent[:220]}\"")
    thread_items.append(f"{len(thread_items)+1}/ The full intelligence report is live → {SITE_URL}/reports/{slug}.html")
    thread_items.append(f"RT if you found this useful. Follow for weekly AI community intelligence. 🔮")

    thread_html = ""
    for i, t in enumerate(thread_items):
        thread_html += f"""
        <div style="background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:18px 20px;margin-bottom:8px;position:relative">
          <div style="font-size:.72rem;color:var(--txt3);font-family:var(--ff-display);letter-spacing:.06em;margin-bottom:8px">TWEET {i+1}/{len(thread_items)}</div>
          <div id="tweet-{i}" style="font-size:.9rem;line-height:1.6;white-space:pre-wrap">{t.replace('<','&lt;').replace('>','&gt;')}</div>
          <button class="copy-btn" data-target="tweet-{i}" style="position:absolute;top:12px;right:12px;background:rgba(0,245,255,.1);border:1px solid rgba(0,245,255,.22);border-radius:8px;color:var(--cyan);font-size:.62rem;font-family:var(--ff-display);font-weight:700;padding:4px 10px;cursor:pointer">COPY</button>
        </div>"""

    # TikTok / Reels Scripts
    scripts = []
    if is_ai:
        scripts = [
            {
                "title": "The AI Reality Check",
                "hook": f"POV: I read everything the AI community said about {topic}.",
                "body": f"They didn't talk about benchmarks. They talked about [PATTERN_1]. And [PATTERN_2]. And [QUOTE].",
                "cta": f"Full breakdown at ai.quantummerlin.com"
            },
            {
                "title": "What Big Tech Isn't Telling You",
                "hook": f"I analysed {fmt_num(a['total_words'])} real words about {topic}. The official story is very different.",
                "body": "Here are 3 things the community keeps saying that nobody in the press is covering.",
                "cta": "Link in bio for the full intelligence report."
            },
            {
                "title": "The Pattern Nobody Noticed",
                "hook": f"{fmt_num(a['total_score'])} people upvoted the same thing about {topic}. That's the signal.",
                "body": f"When {fmt_num(a['total_comments'])} comments all point in the same direction, the data is trying to tell you something.",
                "cta": "Read the full breakdown → ai.quantummerlin.com"
            },
        ]
    else:
        scripts = [
            {
                "title": "The Community Truth",
                "hook": f"POV: I spent weeks in the {topic} community reading everything.",
                "body": "Here's what I found that nobody is saying publicly.",
                "cta": f"Full report at ai.quantummerlin.com/reports/{slug}.html"
            },
            {
                "title": "The Pattern",
                "hook": f"{fmt_num(a['total_posts'])} posts. {fmt_num(a['total_comments'])} comments. One pattern.",
                "body": f"The {topic} community keeps coming back to the same 3 things. Here's what they are.",
                "cta": "Follow for weekly community intelligence."
            },
        ]

    scripts_html = ""
    for i, sc in enumerate(scripts[:3]):
        scripts_html += f"""
        <div style="background:var(--card);border:1px solid rgba(157,0,255,.15);border-radius:14px;padding:20px 22px;margin-bottom:12px;position:relative">
          <div style="font-family:var(--ff-display);font-size:.68rem;font-weight:700;color:#c86fff;letter-spacing:.1em;margin-bottom:10px">📱 SCRIPT {i+1} — {sc['title'].upper()}</div>
          <div id="script-{i}" style="font-size:.88rem;line-height:1.8;color:var(--txt2)">
            <strong style="color:#fff;display:block;margin-bottom:6px">🎣 HOOK:</strong> {sc['hook']}<br><br>
            <strong style="color:#fff;display:block;margin-bottom:6px">📝 BODY:</strong> {sc['body']}<br><br>
            <strong style="color:#fff;display:block;margin-bottom:6px">📣 CTA:</strong> {sc['cta']}
          </div>
          <button class="copy-btn" data-target="script-{i}" style="position:absolute;top:12px;right:12px;background:rgba(157,0,255,.12);border:1px solid rgba(157,0,255,.25);border-radius:8px;color:#c86fff;font-size:.62rem;font-family:var(--ff-display);font-weight:700;padding:4px 10px;cursor:pointer">COPY</button>
        </div>"""

    # Hooks HTML (all 8)
    hooks_html = "".join(
        f"""<div class="hook-card"><span class="hook-num">H{i+1}</span><span class="hook-text">{h}</span><button class="hook-copy-btn">COPY</button></div>"""
        for i, h in enumerate(hooks)
    )

    # LinkedIn post
    linkedin = f"""🔍 I analysed {fmt_num(a['total_words'])}+ words from the {topic} community.

Here are the 3 patterns that kept emerging:

1. {a['bigrams'][0][0] if a['bigrams'] else 'Pattern 1'} — appeared repeatedly across unconnected posts
2. {a['bigrams'][1][0] if len(a['bigrams'])>1 else 'Pattern 2'} — the community's dominant concern
3. {a['bigrams'][2][0] if len(a['bigrams'])>2 else 'Pattern 3'} — shows up in top-voted comments consistently

The community told us exactly what they care about, what they fear, and what they want to exist.

The full intelligence report is live → {SITE_URL}/reports/{slug}.html

#AIIntelligence #CommunityData #ContentStrategy #ArtificialIntelligence"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0,maximum-scale=5.0">
<title>{topic} Social Content Pack | {SITE_NAME}</title>
{QM_HEAD_EXTRAS}
{QM_CSS}
<style>
.pack-header{{padding:48px 0 36px;border-bottom:1px solid rgba(255,255,255,.06);margin-bottom:40px}}
.tab-bar{{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:28px}}
.tab-btn{{padding:9px 18px;border-radius:20px;font-family:var(--ff-display);font-size:.68rem;font-weight:700;letter-spacing:.08em;cursor:pointer;border:1px solid rgba(255,255,255,.1);background:none;color:var(--txt2);transition:all .2s}}
.tab-btn.active{{background:rgba(0,245,255,.1);border-color:rgba(0,245,255,.28);color:var(--cyan)}}
.tab-content{{display:none}}.tab-content.active{{display:block}}
</style>
</head>
<body>
{QM_NAV}

<div class="container">

  <div class="pack-header">
    <div class="hero-eyebrow">✦ SOCIAL CONTENT PACK · {TODAY}</div>
    <h1 style="font-family:'Cinzel Decorative',serif;font-size:clamp(1.4rem,4vw,2.2rem);font-weight:700;background:linear-gradient(135deg,#ffd700,#00f5ff);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:10px">{topic} — Content Gold</h1>
    <p style="color:var(--txt2);font-size:.9rem;max-width:580px">
      Everything you need to publish. Hooks, threads, scripts, and LinkedIn posts — all derived from {fmt_num(a['total_words'])}+ words of real community data.
    </p>
    <div style="margin-top:12px;display:flex;gap:10px;flex-wrap:wrap">
      <a href="../reports/{slug}.html" style="padding:8px 16px;background:rgba(0,245,255,.08);border:1px solid rgba(0,245,255,.22);border-radius:20px;font-family:var(--ff-display);font-size:.65rem;font-weight:700;color:var(--cyan);letter-spacing:.06em">📊 Full Report</a>
    </div>
  </div>

  <!-- TABS -->
  <div class="tab-bar">
    <button class="tab-btn active" onclick="switchTab('hooks')">🎣 Hooks (8)</button>
    <button class="tab-btn" onclick="switchTab('thread')">🧵 X/Twitter Thread</button>
    <button class="tab-btn" onclick="switchTab('scripts')">📱 TikTok/Reels Scripts</button>
    <button class="tab-btn" onclick="switchTab('linkedin')">💼 LinkedIn Post</button>
  </div>

  <!-- HOOKS -->
  <div id="tab-hooks" class="tab-content active">
    <p style="font-size:.84rem;color:var(--txt3);margin-bottom:18px">Click COPY to grab any hook. Adapt to your voice and platform.</p>
    {hooks_html}
  </div>

  <!-- THREAD -->
  <div id="tab-thread" class="tab-content">
    <p style="font-size:.84rem;color:var(--txt3);margin-bottom:18px">{len(thread_items)}-tweet thread ready to post. Copy each tweet individually.</p>
    {thread_html}
  </div>

  <!-- SCRIPTS -->
  <div id="tab-scripts" class="tab-content">
    <p style="font-size:.84rem;color:var(--txt3);margin-bottom:18px">Short-form video scripts (30–60 sec). Replace [BRACKETS] with specific data from the report.</p>
    {scripts_html}
  </div>

  <!-- LINKEDIN -->
  <div id="tab-linkedin" class="tab-content">
    <p style="font-size:.84rem;color:var(--txt3);margin-bottom:18px">Professional post for LinkedIn. Edit the patterns to match specific findings from your report.</p>
    <div style="background:var(--card);border:1px solid rgba(255,255,255,.07);border-radius:14px;padding:22px;position:relative">
      <div id="linkedin-post" style="font-size:.9rem;line-height:1.8;white-space:pre-wrap;color:var(--txt2)">{linkedin.replace('<','&lt;').replace('>','&gt;')}</div>
      <button class="copy-btn" data-target="linkedin-post" style="margin-top:14px;padding:8px 18px;background:rgba(0,168,255,.1);border:1px solid rgba(0,168,255,.25);border-radius:8px;color:var(--blue);font-size:.7rem;font-family:var(--ff-display);font-weight:700;cursor:pointer">COPY LINKEDIN POST</button>
    </div>
  </div>

  <div style="padding:32px 0"></div>
</div>

{QM_FOOTER}
{COPY_JS}
<script>
function switchTab(name){{
  document.querySelectorAll('.tab-content').forEach(t=>t.classList.remove('active'));
  document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById('tab-'+name).classList.add('active');
  event.target.classList.add('active');
}}
</script>
</body>
</html>"""


# ─────────────────────────────────────────────────────────────────────────────
# PIPELINE
# ─────────────────────────────────────────────────────────────────────────────

def process_file(json_path: Path):
    print(f"\n{'='*60}")
    print(f"  Processing: {json_path.name}")
    print(f"{'='*60}")

    # Load
    with open(json_path, encoding="utf-8", errors="replace") as f:
        raw = json.load(f)

    # Normalise
    data = normalise(raw)
    if not data["posts"]:
        print("  ⚠ No posts found. Skipping.")
        return False

    print(f"  Format: {data['source']}")
    print(f"  Posts:  {len(data['posts'])}")

    # Analyse
    a = analyse(data, json_path.name)
    print(f"  Topic:  {a['topic_name']}")
    print(f"  Words:  {fmt_num(a['total_words'])}")
    print(f"  AI topic: {'Yes' if a['is_ai'] else 'No'}")

    slug = slugify(a["topic_name"])

    # Build outputs
    report_html = build_report(a)
    social_html = build_social_pack(a)

    # Ensure output dirs exist
    REPORTS_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)

    # Write files
    report_path = REPORTS_DIR   / f"{slug}.html"
    social_path = PROCESSED_DIR / f"{slug}-social.html"

    report_path.write_text(report_html, encoding="utf-8")
    social_path.write_text(social_html, encoding="utf-8")

    print(f"\n  ✅ Report  → {report_path}")
    print(f"  ✅ Social  → {social_path}")

    # Move source JSON to processed
    dest = PROCESSED_DIR / json_path.name
    json_path.rename(dest)
    print(f"  📦 Source  → {dest}")

    return True


CHUNK_SIZE = 3  # files processed per chunk before a pause/GC cycle


def collect_json_files(root: Path) -> list:
    """
    Recursively find all .json files under root,
    skipping the processed/ directory at any depth.
    """
    files = []
    for p in sorted(root.rglob("*.json")):
        # Skip anything inside a 'processed' folder
        if "processed" in [part.lower() for part in p.parts]:
            continue
        files.append(p)
    return files


def process_chunk(files: list, chunk_num: int, total_chunks: int) -> int:
    """Process a single chunk of files. Returns count of successes."""
    import gc
    print(f"\n  ── Chunk {chunk_num}/{total_chunks} ({len(files)} file(s)) ──")
    success = 0
    for f in files:
        try:
            if process_file(f):
                success += 1
        except MemoryError:
            print(f"  ⚠ MemoryError on {f.name} — skipping. Try a smaller file.")
        except Exception as e:
            print(f"  ⚠ Error on {f.name}: {e} — skipping.")
    gc.collect()  # free memory between chunks
    return success


def run_all(files: list):
    """Split files into chunks and process sequentially."""
    total   = len(files)
    chunks  = [files[i:i+CHUNK_SIZE] for i in range(0, total, CHUNK_SIZE)]
    n_chunks = len(chunks)

    print(f"\n  Processing {total} file(s) in {n_chunks} chunk(s) of {CHUNK_SIZE}.")

    success = 0
    for i, chunk in enumerate(chunks, 1):
        success += process_chunk(chunk, i, n_chunks)

    return success, total


def main():
    INBOX_DIR.mkdir(exist_ok=True)
    PROCESSED_DIR.mkdir(exist_ok=True)

    # Specific path passed as argument?
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        if not target.exists():
            print(f"Error: {target} not found.")
            sys.exit(1)

        if target.is_dir():
            files = collect_json_files(target)
            if not files:
                print(f"📭 No JSON files found in {target}")
                return
            print(f"📂 Scanning folder: {target}")
            print(f"📬 Found {len(files)} file(s)")
            success, total = run_all(files)
        else:
            # Single file — no chunking needed
            success = 1 if process_file(target) else 0
            total   = 1
    else:
        # No argument — scan inbox/ recursively
        files = collect_json_files(INBOX_DIR)
        if not files:
            print("📭 Nothing to process.")
            print("   Drop .json files or folders into inbox/ and run again.")
            print(f"   inbox/ → {INBOX_DIR.resolve()}")
            return

        print(f"📬 Found {len(files)} file(s) in inbox/ (recursive scan)")
        for f in files:
            rel = f.relative_to(INBOX_DIR)
            print(f"   📄 {rel}")

        success, total = run_all(files)

    print(f"\n{'='*60}")
    print(f"  Done. {success}/{total} files processed successfully.")
    print(f"  Reports  → reports/")
    print(f"  Social   → inbox/processed/")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
