"""
Audience Intelligence Analyzer
================================
Generates a structured insight report from a scraped comment file.

Usage:
    python analyze.py <input_file> [options]

Input:
    - JSON checkpoint file (from fb_comment_exporter)
    - CSV file (exported comments)

Output:
    - HTML report (default, print to PDF via browser)
    - Markdown report (--format md)

Examples:
    python analyze.py outputs/_checkpoint_https_www_facebook_com_reel_1924420691613532.json
    python analyze.py outputs/comments.csv --format md --out report.md
    python analyze.py outputs/data.json --out report.html --client "Acme Corp"
"""

import json
import csv
import re
import sys
import argparse
import os
from collections import Counter
from datetime import datetime
from typing import List, Dict, Tuple, Optional


# ─────────────────────────────────────────────────────────────────
# Multilingual Sentiment Lexicons
# ─────────────────────────────────────────────────────────────────

POSITIVE_IT = [
    "bravo", "brava", "bravi", "bravissimo", "ottimo", "ottima", "ottimi",
    "grazie", "giusto", "giusta", "corretto", "esatto", "esatta", "vero",
    "sì", "si", "concordo", "d'accordo", "daccordo", "pienamente",
    "giusto", "rispetto", "diritto", "libertà", "amore", "pace",
    "felice", "bene", "bello", "bella", "aiutare", "aiuto", "speranza",
    "finalmente", "gioia", "benissimo", "perfetto", "bravo"
]

NEGATIVE_IT = [
    "vergogna", "vergognoso", "vergognosi", "schifo", "schifo", "schifo",
    "indecente", "scandaloso", "ingiusto", "ingiustizia", "inaccettabile",
    "inammissibile", "assurdo", "assurda", "ridicolo", "ridicola",
    "criminale", "bastardi", "bastardo", "maledetti", "maledetto",
    "orribile", "orrendo", "terribile", "pessimo", "pessima",
    "vergognatevi", "vigliacchi", "incompetenti", "corrotti", "corrotto",
    "schiavitù", "prigione", "sequestro", "stufo", "stufa", "basta",
    "tragedia", "disastro", "rovinato", "distrutto", "male", "mala",
    "incubo", "dolore", "sofferenza", "pianto", "triste", "tristezza",
    "stanco", "stanca", "deluso", "delusa", "amareggiato", "rabbia",
    "arrabbiato", "arrabbiata", "infuriato", "sdegno", "sdegnato",
    "disgusto", "disgustato", "rivoltante", "rivoltoso", "schifoso"
]

POSITIVE_EN = [
    "love", "amazing", "awesome", "great", "best", "incredible",
    "fantastic", "perfect", "beautiful", "wow", "fire", "brilliant",
    "excellent", "outstanding", "wonderful", "good", "nice", "agree",
    "right", "true", "bravo", "thanks", "thank", "yes"
]

NEGATIVE_EN = [
    "hate", "terrible", "awful", "worst", "bad", "disappointing",
    "poor", "waste", "scam", "fake", "boring", "shame", "disgrace",
    "unacceptable", "outrage", "wrong", "corrupt", "criminal", "monster"
]

POSITIVE_EMOJIS = ["😍", "🔥", "💯", "👏", "🙏", "❤️", "💪", "✅", "👍", "😊", "🥰"]
NEGATIVE_EMOJIS = ["👎", "😡", "🤬", "😤", "💀", "🤢"]

# Themes to detect (keyword groups → theme label)
THEME_PATTERNS = {
    "family_separation":    ["famiglia", "bambini", "figli", "genitori", "mamma", "papà", "separati", "allontanati", "togliere", "ridare"],
    "social_workers":       ["assistenti sociali", "assistente sociale", "assistenti", "psicologi", "psicologi"],
    "judiciary_criticism":  ["giudici", "giudice", "magistrati", "magistratura", "tribunale", "legge", "sentenza"],
    "political_reference":  ["governo", "politici", "meloni", "referendum", "parlamento", "stato", "istituzione"],
    "call_to_action":       ["fate qualcosa", "intervenite", "agite", "basta parole", "fatti", "azione"],
    "powerlessness":        ["nessuno fa", "parlate ma", "solo parole", "chiacchiere", "inutile"],
    "conspiracy_theory":    ["dietro", "giro di soldi", "losco", "interessi", "bibbiano"],
    "legal_reference":      ["decreto caivano", "legge", "obbligo scolastico", "potestà", "patria potestà"],
    "president_appeal":     ["mattarella", "presidente della repubblica", "president"],
}

# ─────────────────────────────────────────────────────────────────
# Loaders
# ─────────────────────────────────────────────────────────────────

def load_json_checkpoint(path: str) -> Tuple[List[Dict], str]:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return data.get("comments", []), data.get("url", "")


def load_csv(path: str) -> Tuple[List[Dict], str]:
    comments = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            comments.append({
                "author":   row.get("author", ""),
                "text":     row.get("text", ""),
                "timestamp": row.get("timestamp", ""),
                "likes":    int(row.get("likes", 0) or 0),
                "is_reply": row.get("is_reply", "false").lower() == "true",
            })
    return comments, ""


def load_input(path: str) -> Tuple[List[Dict], str]:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".json":
        return load_json_checkpoint(path)
    elif ext == ".csv":
        return load_csv(path)
    else:
        # Try JSON first
        try:
            return load_json_checkpoint(path)
        except:
            return load_csv(path)


# ─────────────────────────────────────────────────────────────────
# Analysis
# ─────────────────────────────────────────────────────────────────

def classify_sentiment(text: str) -> str:
    t = text.lower()
    pos_score = 0
    neg_score = 0

    for kw in POSITIVE_IT + POSITIVE_EN:
        if kw in t:
            pos_score += 1
    for kw in NEGATIVE_IT + NEGATIVE_EN:
        if kw in t:
            neg_score += 1
    for e in POSITIVE_EMOJIS:
        if e in text:
            pos_score += 1
    for e in NEGATIVE_EMOJIS:
        if e in text:
            neg_score += 1

    if pos_score > neg_score:
        return "positive"
    elif neg_score > pos_score:
        return "negative"
    else:
        return "neutral"


def extract_themes(comments: List[Dict]) -> Dict[str, int]:
    counts = Counter()
    for c in comments:
        text = c.get("text", "").lower()
        for theme, keywords in THEME_PATTERNS.items():
            if any(kw in text for kw in keywords):
                counts[theme] += 1
    return dict(counts.most_common())


def top_comments_by_likes(comments: List[Dict], n: int = 10) -> List[Dict]:
    liked = [c for c in comments if c.get("likes") and int(c.get("likes") or 0) > 0]
    return sorted(liked, key=lambda x: int(x.get("likes") or 0), reverse=True)[:n]


def extract_questions(comments: List[Dict]) -> List[str]:
    questions = []
    for c in comments:
        text = c.get("text", "").strip()
        if "?" in text:
            # Extract sentence(s) containing a question mark
            for sentence in re.split(r"[.!]", text):
                if "?" in sentence and len(sentence.strip()) > 5:
                    questions.append(sentence.strip())
    return questions


def top_phrases(comments: List[Dict], n: int = 15) -> List[Tuple[str, int]]:
    """Extract top 2-3 word recurring phrases."""
    phrase_counts = Counter()
    stop_words = {
        "di", "che", "la", "il", "lo", "i", "le", "un", "una", "e", "è", "ma",
        "non", "per", "con", "del", "dei", "delle", "da", "a", "in", "ha", "ho",
        "è", "si", "se", "sono", "mi", "ti", "vi", "ci", "ne", "lo", "li",
        "o", "poi", "già", "anche", "solo", "più", "bene", "fare", "fa",
        "the", "and", "for", "are", "this", "that", "with", "they"
    }
    for c in comments:
        words = re.findall(r"[a-zàáâãäåèéêëìíîïòóôõöùúûü]+", c.get("text", "").lower())
        words = [w for w in words if w not in stop_words and len(w) > 3]
        for i in range(len(words) - 1):
            bigram = f"{words[i]} {words[i+1]}"
            phrase_counts[bigram] += 1
        for i in range(len(words) - 2):
            trigram = f"{words[i]} {words[i+1]} {words[i+2]}"
            phrase_counts[trigram] += 1
    # Filter out very low counts
    return [(p, c) for p, c in phrase_counts.most_common(n * 3) if c >= 2][:n]


def audience_profile(comments: List[Dict]) -> Dict:
    """Infer rough audience profile from engagement patterns."""
    total = len(comments)
    top_liked = top_comments_by_likes(comments, 3)
    themes = extract_themes(comments)

    # Detect language
    it_markers = ["vergogna", "bambini", "famiglia", "genitori", "stato"]
    en_markers = ["the", "and", "this", "that", "with"]
    text_blob = " ".join(c.get("text", "") for c in comments[:50]).lower()
    is_italian = sum(1 for m in it_markers if m in text_blob) > sum(1 for m in en_markers if m in text_blob)

    # Dominant emotion from themes
    dominant_themes = list(themes.keys())[:3] if themes else []

    # Engagement distribution
    have_likes = [c for c in comments if int(c.get("likes") or 0) > 0]
    avg_likes = sum(int(c.get("likes") or 0) for c in have_likes) / len(have_likes) if have_likes else 0

    return {
        "language": "Italian" if is_italian else "English/Mixed",
        "dominant_themes": dominant_themes,
        "avg_likes_on_liked_comments": round(avg_likes, 1),
        "pct_top_commenters": round(len([c for c in Counter(c["author"] for c in comments).values() if c > 1]) / max(1, total) * 100, 1),
    }


def generate_actionable_insights(sentiment: Dict, themes: Dict, top_liked: List[Dict], questions: List[str]) -> List[str]:
    insights = []
    pct_neg = sentiment.get("negative_pct", 0)
    pct_pos = sentiment.get("positive_pct", 0)

    if pct_neg > 60:
        insights.append("Audience is predominantly **angry/outraged** — this post is triggering strong negative emotion. Any brand associated with this topic should tread carefully.")
    elif pct_neg > 30:
        insights.append("Mixed sentiment with notable negativity. The audience is divided and emotionally charged.")

    if pct_pos > 50:
        insights.append("Majority positive sentiment — strong brand/creator support in this audience.")

    if "call_to_action" in themes and themes["call_to_action"] > 10:
        insights.append("High 'call to action' comments — audience feels frustrated by inaction. Content that offers solutions or clear steps would resonate strongly.")

    if "powerlessness" in themes and themes["powerlessness"] > 10:
        insights.append("'Words but no action' frustration is a recurring theme — the audience values proof and results over statements.")

    if "political_reference" in themes and themes["political_reference"] > 15:
        insights.append("Strong political framing in comments. This audience is politically engaged and will respond to content that takes a clear stance.")

    if "judiciary_criticism" in themes and themes["judiciary_criticism"] > 10:
        insights.append("Criticism of judiciary/institutions is dominant — audience strongly distrusts official institutions.")

    if "family_separation" in themes and themes["family_separation"] > 20:
        insights.append("Family protection is the **core emotional trigger** — content about parental rights, child welfare, or family unity will resonate deeply.")

    if "president_appeal" in themes and themes["president_appeal"] > 5:
        insights.append("Audience appeals to political leaders (President, PM) — they believe only top-tier intervention can solve their concerns.")

    if questions:
        insights.append(f"**{len(questions)} questions found** in comments — consider creating FAQ content or a response video/post addressing these directly.")

    if not insights:
        insights.append("Engaged audience with mixed opinions. Consider diving deeper into the top-liked comments for specific content angles.")

    return insights


def run_analysis(comments: List[Dict], url: str = "") -> Dict:
    """Run full analysis and return structured results dict."""
    total = len(comments)
    if total == 0:
        return {"error": "No comments to analyze."}

    # Filter real comments (non-empty text)
    real = [c for c in comments if c.get("text", "").strip() and len(c.get("text", "").strip()) > 2]

    # Sentiment
    sentiments = [classify_sentiment(c["text"]) for c in real]
    sent_counter = Counter(sentiments)
    sentiment = {
        "positive_pct": round(sent_counter["positive"] / len(real) * 100, 1),
        "neutral_pct":  round(sent_counter["neutral"]  / len(real) * 100, 1),
        "negative_pct": round(sent_counter["negative"] / len(real) * 100, 1),
        "positive_n": sent_counter["positive"],
        "neutral_n":  sent_counter["neutral"],
        "negative_n": sent_counter["negative"],
    }

    themes    = extract_themes(real)
    top_liked = top_comments_by_likes(real, 10)
    questions = extract_questions(real)
    phrases   = top_phrases(real, 15)
    profile   = audience_profile(real)
    insights  = generate_actionable_insights(sentiment, themes, top_liked, questions)

    return {
        "url": url,
        "total_comments": total,
        "analyzed_comments": len(real),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "sentiment": sentiment,
        "themes": themes,
        "top_liked_comments": top_liked,
        "top_questions": questions[:10],
        "top_phrases": phrases,
        "audience_profile": profile,
        "actionable_insights": insights,
    }


# ─────────────────────────────────────────────────────────────────
# Report Generators
# ─────────────────────────────────────────────────────────────────

THEME_LABELS = {
    "family_separation":    "Family Separation",
    "social_workers":       "Social Workers",
    "judiciary_criticism":  "Judiciary Criticism",
    "political_reference":  "Political Reference",
    "call_to_action":       "Call to Action",
    "powerlessness":        "Frustration / Powerlessness",
    "conspiracy_theory":    "Conspiracy Theories",
    "legal_reference":      "Legal References",
    "president_appeal":     "Appeals to President / Leaders",
}


def generate_html(data: Dict, client_name: str = "") -> str:
    s = data["sentiment"]
    themes = data["themes"]
    profile = data["audience_profile"]
    top_liked = data["top_liked_comments"]
    questions = data["top_questions"]
    phrases   = data["top_phrases"]
    insights  = data["actionable_insights"]

    theme_rows = ""
    for theme, count in list(themes.items())[:8]:
        label = THEME_LABELS.get(theme, theme.replace("_", " ").title())
        pct = round(count / data["analyzed_comments"] * 100)
        bar_width = min(pct * 2, 100)
        theme_rows += f"""
        <tr>
          <td style="width:180px;font-weight:500">{label}</td>
          <td>
            <div style="background:#e5e7eb;border-radius:4px;height:16px;width:100%">
              <div style="background:#6366f1;border-radius:4px;height:16px;width:{bar_width}%"></div>
            </div>
          </td>
          <td style="width:60px;text-align:right;color:#6b7280">{count}</td>
        </tr>"""

    top_comment_rows = ""
    for i, c in enumerate(top_liked[:5], 1):
        text = c.get("text", "").replace("<", "&lt;").replace(">", "&gt;")
        if len(text) > 200:
            text = text[:200] + "…"
        top_comment_rows += f"""
        <tr>
          <td style="color:#6366f1;font-weight:700;width:30px">{i}</td>
          <td style="color:#374151">{text}</td>
          <td style="width:60px;text-align:right;color:#6b7280;white-space:nowrap">👍 {c.get('likes',0)}</td>
        </tr>"""

    question_html = ""
    for q in questions[:6]:
        q_esc = q.replace("<", "&lt;").replace(">", "&gt;")
        if len(q_esc) > 120:
            q_esc = q_esc[:120] + "…"
        question_html += f'<li style="margin-bottom:8px;color:#374151">{q_esc}</li>'

    phrase_html = ""
    for phrase, count in phrases[:12]:
        phrase_html += f'<span style="display:inline-block;background:#ede9fe;color:#4f46e5;padding:4px 10px;border-radius:12px;margin:4px;font-size:0.85em">{phrase} <strong>({count})</strong></span>'

    insight_html = ""
    for ins in insights:
        insight_html += f'<li style="margin-bottom:12px;line-height:1.6">{ins}</li>'

    pos_bar = s["positive_pct"]
    neu_bar = s["neutral_pct"]
    neg_bar = s["negative_pct"]

    banner = f"Prepared for {client_name}" if client_name else "Audience Intelligence Report"
    source_line = f'<p style="margin-top:6px;font-size:0.85em;opacity:0.8">Source: {data["url"]}</p>' if data.get("url") else ""

    # ── Open Graph / social sharing ──────────────────────────────────────────
    OG_IMAGE_URL = "https://public-files.gumroad.com/audienceintelligence-cover.png"
    # ↑ Replace with the direct URL to your Gumroad product cover image
    og_title   = f"Audience Intelligence Report – {client_name}" if client_name else "Audience Intelligence Report"
    s_pos = data['sentiment']['positive_pct']
    s_neg = data['sentiment']['negative_pct']
    og_desc = (
        f"{data['total_comments']} comments analysed · "
        f"{s_pos:.0f}% positive · {s_neg:.0f}% negative · "
        f"Powered by quantumtoolsmith.gumroad.com"
    )
    og_url     = data.get("url", "https://quantumtoolsmith.gumroad.com")
    page_title = f"Audience Intelligence Report{' – ' + client_name if client_name else ''}"
    # ────────────────────────────────────────────────────────────────────────

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{page_title}</title>

<!-- Primary Meta -->
<meta name="description" content="{og_desc}">
<meta name="author" content="quantumtoolsmith.gumroad.com">

<!-- Open Graph / Facebook -->
<meta property="og:type"        content="article">
<meta property="og:url"         content="{og_url}">
<meta property="og:title"       content="{og_title}">
<meta property="og:description" content="{og_desc}">
<meta property="og:image"       content="{OG_IMAGE_URL}">
<meta property="og:image:width"  content="1200">
<meta property="og:image:height" content="630">
<meta property="og:site_name"   content="Audience Intelligence by quantumtoolsmith">

<!-- Twitter Card -->
<meta name="twitter:card"        content="summary_large_image">
<meta name="twitter:title"       content="{og_title}">
<meta name="twitter:description" content="{og_desc}">
<meta name="twitter:image"       content="{OG_IMAGE_URL}">
<meta name="twitter:creator"     content="@quantumtoolsmith">

<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
  * {{ margin:0; padding:0; box-sizing:border-box; }}
  body {{ font-family:'Inter',sans-serif; background:#f1f5f9; color:#111; }}
  .page {{ max-width:820px; margin:0 auto; background:#fff; }}
  .header {{ background:linear-gradient(135deg,#4f46e5,#7c3aed); color:#fff; padding:36px 40px 28px; }}
  .header h1 {{ font-size:1.9em; font-weight:700; letter-spacing:-0.5px; }}
  .header p {{ margin-top:6px; opacity:0.85; font-size:0.95em; }}
  .meta-bar {{ background:#f8fafc; border-bottom:1px solid #e2e8f0; padding:12px 40px; display:flex; gap:32px; font-size:0.85em; color:#64748b; }}
  .meta-bar b {{ color:#374151; }}
  .section {{ padding:32px 40px; border-bottom:1px solid #f0f0f0; }}
  .section h2 {{ font-size:1.05em; font-weight:700; color:#1e293b; margin-bottom:18px; text-transform:uppercase; letter-spacing:0.5px; }}
  .kpi-row {{ display:flex; gap:16px; flex-wrap:wrap; }}
  .kpi {{ flex:1; min-width:120px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:16px 20px; text-align:center; }}
  .kpi .val {{ font-size:2em; font-weight:700; color:#4f46e5; }}
  .kpi .lbl {{ font-size:0.78em; color:#64748b; margin-top:4px; text-transform:uppercase; letter-spacing:0.4px; }}
  .sent-bar {{ display:flex; height:24px; border-radius:6px; overflow:hidden; margin:12px 0; }}
  .sent-pos {{ background:#22c55e; }}
  .sent-neu {{ background:#94a3b8; }}
  .sent-neg {{ background:#ef4444; }}
  .sent-legend {{ display:flex; gap:20px; font-size:0.82em; color:#64748b; }}
  .sent-legend span {{ display:flex; align-items:center; gap:5px; }}
  .dot {{ width:10px; height:10px; border-radius:50%; display:inline-block; }}
  table {{ width:100%; border-collapse:collapse; }}
  td, th {{ padding:10px 8px; text-align:left; border-bottom:1px solid #f0f4f8; font-size:0.9em; }}
  th {{ font-size:0.75em; text-transform:uppercase; letter-spacing:0.5px; color:#94a3b8; }}
  ul {{ padding-left:18px; }}
  .insights-list li {{ margin-bottom:14px; font-size:0.92em; line-height:1.65; }}
  .footer {{ background:#f8fafc; padding:20px 40px; font-size:0.78em; color:#94a3b8; text-align:center; }}
  .footer a {{ color:#94a3b8; text-decoration:none; }}
  .footer a:hover {{ color:#4f46e5; text-decoration:underline; }}
  .cta {{ background:linear-gradient(135deg,#4f46e5,#7c3aed); padding:36px 40px; text-align:center; }}
  .cta h3 {{ color:#fff; font-size:1.1em; font-weight:700; margin-bottom:8px; }}
  .cta p {{ color:rgba(255,255,255,0.85); font-size:0.92em; margin-bottom:20px; }}
  .cta-btn {{ background:#fff; color:#4f46e5; font-weight:700; font-size:0.95em; padding:12px 28px; border-radius:8px; text-decoration:none; display:inline-block; letter-spacing:0.2px; border:none; cursor:pointer; }}
  .cta-btn:hover {{ background:#f0edff; }}
  /* Pricing Modal */
  .modal-overlay {{ display:none; position:fixed; inset:0; background:rgba(0,0,0,0.65); z-index:1000; align-items:center; justify-content:center; padding:20px; }}
  .modal-box {{ background:#fff; border-radius:16px; padding:40px 36px 36px; max-width:700px; width:100%; position:relative; box-shadow:0 20px 60px rgba(0,0,0,0.35); }}
  .modal-close {{ position:absolute; top:12px; right:16px; font-size:1.6em; cursor:pointer; color:#94a3b8; background:none; border:none; line-height:1; padding:0; }}
  .modal-close:hover {{ color:#334155; }}
  .modal-title {{ font-size:1.25em; font-weight:800; color:#1e293b; text-align:center; margin-bottom:6px; }}
  .modal-sub {{ text-align:center; color:#64748b; font-size:0.88em; margin-bottom:28px; }}
  .tier-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:16px; }}
  .tier-card {{ border:2px solid #e2e8f0; border-radius:12px; padding:24px 18px 20px; text-align:center; transition:border-color 0.2s,box-shadow 0.2s; }}
  .tier-card:hover {{ border-color:#4f46e5; box-shadow:0 4px 18px rgba(79,70,229,0.12); }}
  .tier-card.featured {{ border-color:#4f46e5; background:#f5f3ff; }}
  .tier-badge {{ font-size:0.7em; font-weight:700; letter-spacing:1px; text-transform:uppercase; color:#4f46e5; margin-bottom:10px; }}
  .tier-price {{ font-size:2em; font-weight:800; color:#1e293b; line-height:1.1; }}
  .tier-price sup {{ font-size:0.45em; font-weight:600; vertical-align:super; color:#475569; }}
  .tier-price small {{ font-size:0.38em; font-weight:500; color:#64748b; }}
  .tier-limit {{ color:#64748b; font-size:0.82em; margin:8px 0 14px; }}
  .tier-features {{ text-align:left; font-size:0.8em; color:#475569; padding:0; list-style:none; margin:0 0 18px; }}
  .tier-features li {{ padding:3px 0; }}
  .tier-features li::before {{ content:"\2713\00a0\00a0"; color:#22c55e; font-weight:700; }}
  .tier-order {{ display:block; width:100%; padding:10px 0; border-radius:8px; background:#4f46e5; color:#fff; font-weight:700; text-decoration:none; font-size:0.88em; transition:background 0.2s; text-align:center; }}
  .tier-order:hover {{ background:#4338ca; }}
  @media(max-width:580px){{ .tier-grid {{ grid-template-columns:1fr; }} }}
  .header-brand {{ margin-top:10px; font-size:0.8em; opacity:0.7; }}
  .header-brand a {{ color:#fff; text-decoration:none; border-bottom:1px solid rgba(255,255,255,0.4); }}
  .header-brand a:hover {{ opacity:1; border-bottom-color:#fff; }}
  @media print {{
    body {{ background:#fff; }}
    .page {{ max-width:100%; }}
  }}
</style>
</head>
<body>
<div class="page">

  <div class="header">
    <h1>📊 Audience Intelligence Report</h1>
    <p>{banner}</p>
    {source_line}
    <div class="header-brand">by <a href="https://quantumtoolsmith.gumroad.com" target="_blank">quantumtoolsmith.gumroad.com</a></div>
  </div>

  <div class="meta-bar">
    <span>Generated: <b>{data['generated_at']}</b></span>
    <span>Comments analysed: <b>{data['analyzed_comments']}</b></span>
    <span>Language: <b>{profile['language']}</b></span>
  </div>

  <!-- KPIs -->
  <div class="section">
    <h2>Overview</h2>
    <div class="kpi-row">
      <div class="kpi"><div class="val">{data['total_comments']}</div><div class="lbl">Total Comments</div></div>
      <div class="kpi"><div class="val" style="color:#22c55e">{s['positive_pct']}%</div><div class="lbl">Positive</div></div>
      <div class="kpi"><div class="val" style="color:#ef4444">{s['negative_pct']}%</div><div class="lbl">Negative</div></div>
      <div class="kpi"><div class="val" style="color:#94a3b8">{s['neutral_pct']}%</div><div class="lbl">Neutral</div></div>
      <div class="kpi"><div class="val">{len(data['top_questions'])}</div><div class="lbl">Questions</div></div>
    </div>
  </div>

  <!-- Sentiment -->
  <div class="section">
    <h2>Sentiment Breakdown</h2>
    <div class="sent-bar">
      <div class="sent-pos" style="width:{pos_bar}%"></div>
      <div class="sent-neu" style="width:{neu_bar}%"></div>
      <div class="sent-neg" style="width:{neg_bar}%"></div>
    </div>
    <div class="sent-legend">
      <span><span class="dot" style="background:#22c55e"></span>Positive {s['positive_pct']}% ({s['positive_n']})</span>
      <span><span class="dot" style="background:#94a3b8"></span>Neutral {s['neutral_pct']}% ({s['neutral_n']})</span>
      <span><span class="dot" style="background:#ef4444"></span>Negative {s['negative_pct']}% ({s['negative_n']})</span>
    </div>
  </div>

  <!-- Themes -->
  <div class="section">
    <h2>Top Themes &amp; Topics</h2>
    <table>
      <thead><tr><th>Theme</th><th>Volume</th><th>Count</th></tr></thead>
      <tbody>{theme_rows}</tbody>
    </table>
  </div>

  <!-- Top Comments -->
  <div class="section">
    <h2>Top Comments by Engagement</h2>
    <table>
      <thead><tr><th>#</th><th>Comment</th><th>Likes</th></tr></thead>
      <tbody>{top_comment_rows}</tbody>
    </table>
  </div>

  <!-- Recurring Phrases -->
  <div class="section">
    <h2>Recurring Phrases &amp; Keywords</h2>
    <div style="margin-top:4px">{phrase_html}</div>
  </div>

  <!-- Questions -->
  {"<div class='section'><h2>Audience Questions</h2><ul>" + question_html + "</ul></div>" if questions else ""}

  <!-- Audience Profile -->
  <div class="section">
    <h2>Audience Profile Snapshot</h2>
    <table>
      <tbody>
        <tr><td style="font-weight:500;width:200px">Language</td><td>{profile['language']}</td></tr>
        <tr><td style="font-weight:500">Primary concerns</td><td>{", ".join(THEME_LABELS.get(t, t) for t in profile['dominant_themes'])}</td></tr>
        <tr><td style="font-weight:500">Avg likes (engaged)</td><td>{profile['avg_likes_on_liked_comments']}</td></tr>
      </tbody>
    </table>
  </div>

  <!-- Actionable Insights -->
  <div class="section">
    <h2>✅ Actionable Takeaways</h2>
    <ul class="insights-list">{insight_html}</ul>
  </div>

  <div class="cta">
    <h3>Want a Report Like This for Your Content?</h3>
    <p>Custom audience intelligence reports — sentiment, themes, top questions &amp; actionable insights delivered fast.</p>
    <button class="cta-btn" onclick="document.getElementById('pricing-modal').style.display='flex'">See Pricing &amp; Order →</button>
  </div>

  <div class="footer">
    Audience Intelligence Report · <a href="https://quantumtoolsmith.gumroad.com" target="_blank">quantumtoolsmith.gumroad.com</a> · {data['generated_at']}
  </div>

</div>

<!-- Pricing Modal -->
<div id="pricing-modal" class="modal-overlay" onclick="if(event.target===this)this.style.display='none'">
  <div class="modal-box">
    <button class="modal-close" onclick="document.getElementById('pricing-modal').style.display='none'">&times;</button>
    <div class="modal-title">Choose Your Report Tier</div>
    <div class="modal-sub">All tiers include sentiment analysis, theme breakdown, top comments &amp; actionable insights — delivered as a shareable HTML report.</div>
    <div class="tier-grid">

      <div class="tier-card">
        <div class="tier-badge">Starter</div>
        <div class="tier-price"><sup>$</sup>20<small> AUD</small></div>
        <div class="tier-limit">Up to 1,000 comments</div>
        <ul class="tier-features">
          <li>Sentiment breakdown</li>
          <li>Theme &amp; topic analysis</li>
          <li>Top 10 engaged comments</li>
          <li>Actionable insights</li>
          <li>24–48 hr delivery</li>
        </ul>
        <a class="tier-order" href="https://quantumtoolsmith.gumroad.com" target="_blank">Order Starter →</a>
      </div>

      <div class="tier-card featured">
        <div class="tier-badge">★ Most Popular</div>
        <div class="tier-price"><sup>$</sup>35<small> AUD</small></div>
        <div class="tier-limit">Up to 3,000 comments</div>
        <ul class="tier-features">
          <li>Everything in Starter</li>
          <li>Deeper phrase mining</li>
          <li>Full audience profile</li>
          <li>Top questions extracted</li>
          <li>Priority delivery</li>
        </ul>
        <a class="tier-order" href="https://quantumtoolsmith.gumroad.com" target="_blank">Order Standard →</a>
      </div>

      <div class="tier-card">
        <div class="tier-badge">Pro</div>
        <div class="tier-price"><sup>$</sup>50<small> AUD</small></div>
        <div class="tier-limit">Up to 5,000 comments</div>
        <ul class="tier-features">
          <li>Everything in Standard</li>
          <li>Extended phrase mining</li>
          <li>Full question extraction</li>
          <li>Markdown + HTML export</li>
          <li>Rush delivery</li>
        </ul>
        <a class="tier-order" href="https://quantumtoolsmith.gumroad.com" target="_blank">Order Pro →</a>
      </div>

    </div>
  </div>
</div>

</body>
</html>"""


def generate_markdown(data: Dict, client_name: str = "") -> str:
    s = data["sentiment"]
    themes = data["themes"]
    profile = data["audience_profile"]
    top_liked = data["top_liked_comments"]
    questions = data["top_questions"]
    insights  = data["actionable_insights"]

    banner = f"**Prepared for:** {client_name}  " if client_name else ""

    md = f"""# 📊 Audience Intelligence Report

{banner}
**Generated:** {data['generated_at']}  
**Source:** {data.get('url', 'N/A')}  
**Comments analysed:** {data['analyzed_comments']}

---

## Overview

| Metric | Value |
|--------|-------|
| Total Comments | {data['total_comments']} |
| Positive | {s['positive_pct']}% ({s['positive_n']}) |
| Neutral | {s['neutral_pct']}% ({s['neutral_n']}) |
| Negative | {s['negative_pct']}% ({s['negative_n']}) |
| Language | {profile['language']} |

---

## Sentiment Breakdown

Positive ██ {s['positive_pct']}%  
Neutral  ░░ {s['neutral_pct']}%  
Negative 🔴 {s['negative_pct']}%

---

## Top Themes & Topics

| Theme | Comments |
|-------|----------|
"""
    for theme, count in list(themes.items())[:8]:
        label = THEME_LABELS.get(theme, theme.replace("_", " ").title())
        md += f"| {label} | {count} |\n"

    md += "\n---\n\n## Top Comments by Engagement\n\n"
    for i, c in enumerate(top_liked[:5], 1):
        text = c.get("text", "")
        if len(text) > 200:
            text = text[:200] + "…"
        md += f"**{i}.** _{text}_ — 👍 {c.get('likes', 0)}\n\n"

    if questions:
        md += "\n---\n\n## Audience Questions\n\n"
        for q in questions[:8]:
            md += f"- {q}\n"

    md += "\n---\n\n## ✅ Actionable Takeaways\n\n"
    for ins in insights:
        md += f"- {ins}\n"

    md += "\n---\n\n## Audience Profile\n\n"
    md += f"- **Language:** {profile['language']}\n"
    md += f"- **Primary concerns:** {', '.join(THEME_LABELS.get(t, t) for t in profile['dominant_themes'])}\n"

    md += "\n\n---\n*Audience Intelligence Report · [quantumtoolsmith.gumroad.com](https://quantumtoolsmith.gumroad.com)*\n\n> Want a report like this for your content? Order at [quantumtoolsmith.gumroad.com](https://quantumtoolsmith.gumroad.com)\n"
    return md


# ─────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Generate an Audience Intelligence Report from scraped comments."
    )
    parser.add_argument("input", help="Path to JSON checkpoint or CSV file")
    parser.add_argument("--format", choices=["html", "md"], default="html", help="Output format (default: html)")
    parser.add_argument("--out", default="", help="Output file path (default: auto-named in outputs/)")
    parser.add_argument("--client", default="", help="Client name to include in report header")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"Error: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading comments from {args.input}...")
    comments, url = load_input(args.input)
    print(f"Loaded {len(comments)} comments.")

    print("Running analysis...")
    data = run_analysis(comments, url)

    print(f"\n=== Analysis Summary ===")
    print(f"  Total comments:  {data['total_comments']}")
    print(f"  Analyzed:        {data['analyzed_comments']}")
    print(f"  Positive:        {data['sentiment']['positive_pct']}%")
    print(f"  Neutral:         {data['sentiment']['neutral_pct']}%")
    print(f"  Negative:        {data['sentiment']['negative_pct']}%")
    print(f"  Top theme:       {next(iter(data['themes']), 'N/A')}")

    # Generate report
    if args.format == "html":
        report = generate_html(data, args.client)
        ext = ".html"
    else:
        report = generate_markdown(data, args.client)
        ext = ".md"

    # Determine output path
    if args.out:
        out_path = args.out
    else:
        os.makedirs("outputs", exist_ok=True)
        base = os.path.splitext(os.path.basename(args.input))[0]
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = os.path.join("outputs", f"report_{base}_{ts}{ext}")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)

    print(f"\n[OK] Report saved to: {out_path}")
    if args.format == "html":
        print("   Open in a browser and use File → Print → Save as PDF to deliver.")


if __name__ == "__main__":
    main()
