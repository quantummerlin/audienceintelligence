"""
report_agent.py — LLM-powered Audience Intelligence Report Generator
======================================================================
Reads a CSV of comments + a context JSON file (or prompts interactively),
builds the full super-prompt, calls an LLM API, and produces a
professional HTML report with the reply strategy matrix.

Usage:
    python report_agent.py comments.csv
    python report_agent.py comments.csv --context context.json
    python report_agent.py comments.csv --context context.json --out my_report.html
    python report_agent.py --new-context   # guided wizard to create context.json

Requirements:
    pip install openai
    Set OPENAI_API_KEY environment variable, OR pass --api-key

Context JSON shape (see --new-context to generate interactively):
{
  "client_name":       "The Trevallion-Birmingham Family Support Campaign",
  "client_goal":       "Gather public sentiment for campaign website, recruit allies, build legal evidence",
  "post_author":       "MP Emanuele Pozzolo — Italian politician, not affiliated with campaign",
  "client_relationship": "SUPPORTERS",   // CREATOR | SUPPORTERS | RESEARCHERS | OPPONENTS
  "client_platforms":  "Campaign website, Facebook page, press releases",
  "reply_identity": {
    "page_name":   "Truth Protects The Innocent",
    "page_handle": "@veritaprotegge",
    "tone":        "Warm, factual, grateful for support, never aggressive",
    "goals":       "Drive traffic to petition, recruit allies, correct misinformation"
  },
  "reply_preferences": {
    "want_reply_advice": true,
    "reply_goals": ["traffic", "allies", "correct_misinfo", "thank_supporters", "boost_reach"],
    "capacity":    "MEDIUM",   // LOW (top 3) | MEDIUM (top 10) | HIGH (everything)
    "avoid_topics": ["political party debates", "attacks on the MP personally"],
    "include_do_not_reply_list": true
  },
  "post_url": "https://www.facebook.com/reel/1924420691613532",
  "language_hint": "Italian"
}
"""

import argparse
import csv
import json
import os
import sys
import textwrap
from datetime import datetime
from pathlib import Path
from typing import Optional

# ──────────────────────────────────────────────────────────────────────────────
# 1.  CSV LOADER
# ──────────────────────────────────────────────────────────────────────────────

def load_comments_from_csv(path: str) -> list[dict]:
    """Load comments from any CSV.  Tries common column names automatically."""
    comments = []
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # normalise column names to lowercase
            norm = {k.lower().strip(): v for k, v in row.items()}

            text = (
                norm.get("text") or norm.get("comment") or norm.get("message") or
                norm.get("content") or norm.get("body") or ""
            ).strip()
            if not text:
                continue

            author = (
                norm.get("author") or norm.get("name") or norm.get("user") or
                norm.get("username") or norm.get("from") or "Anonymous"
            ).strip()

            try:
                likes = int(float(norm.get("likes") or norm.get("like_count") or 0))
            except (ValueError, TypeError):
                likes = 0

            timestamp = (
                norm.get("timestamp") or norm.get("date") or norm.get("time") or
                norm.get("created_at") or ""
            ).strip()

            comments.append({
                "author": author,
                "text": text,
                "likes": likes,
                "timestamp": timestamp,
            })
    return comments


# ──────────────────────────────────────────────────────────────────────────────
# 2.  INTERACTIVE CONTEXT WIZARD
# ──────────────────────────────────────────────────────────────────────────────

def wizard_new_context(save_path: str = "context.json") -> dict:
    """Interactive Q&A to build a context.json file."""
    print("\n" + "═" * 60)
    print("  AUDIENCE INTELLIGENCE — CONTEXT WIZARD")
    print("  Press ENTER to skip any field (use defaults)")
    print("═" * 60 + "\n")

    def ask(prompt, default=""):
        val = input(f"  {prompt}\n  > ").strip()
        return val if val else default

    def ask_yn(prompt, default=True):
        hint = "[Y/n]" if default else "[y/N]"
        val = input(f"  {prompt} {hint}\n  > ").strip().lower()
        if val in ("y", "yes"):
            return True
        if val in ("n", "no"):
            return False
        return default

    def ask_choice(prompt, options, default=""):
        opts_str = " / ".join(f"{i+1}:{o}" for i, o in enumerate(options))
        val = input(f"  {prompt}\n  Options: {opts_str}\n  > ").strip()
        try:
            idx = int(val) - 1
            if 0 <= idx < len(options):
                return options[idx]
        except ValueError:
            if val.upper() in options:
                return val.upper()
        return default if default else options[0]

    ctx = {}

    print("── ABOUT THE CLIENT ─────────────────────────────────────")
    ctx["client_name"] = ask("Client name / organisation?",
                             "Unnamed Client")
    ctx["client_goal"] = ask(
        "What does the client want to achieve with this analysis?\n"
        "  e.g. Gather sentiment, recruit allies, find content ideas",
        "Understand audience sentiment and identify content opportunities"
    )
    ctx["post_author"] = ask(
        "Who made the post being analysed?\n"
        "  e.g. 'MP Emanuele Pozzolo — not affiliated with client'",
        "Unknown"
    )
    ctx["client_relationship"] = ask_choice(
        "Client's relationship to the post?",
        ["CREATOR", "SUPPORTERS", "RESEARCHERS", "OPPONENTS"],
        "SUPPORTERS"
    )
    ctx["client_platforms"] = ask(
        "Where will this intelligence be used?\n"
        "  e.g. 'Facebook page, website, press release'",
        "Social media and website"
    )
    ctx["post_url"] = ask("URL of the post being analysed?", "")
    ctx["language_hint"] = ask("Primary language of comments? (leave blank for auto-detect)", "")

    print("\n── REPLY PREFERENCES ────────────────────────────────────")
    want_reply = ask_yn("Do you want reply recommendations?", True)
    ctx["reply_preferences"] = {"want_reply_advice": want_reply}

    if want_reply:
        print("\n  Reply goals (comma-separated from list):")
        print("  traffic / allies / correct_misinfo / thank_supporters / boost_reach / intelligence")
        goals_raw = input("  > ").strip()
        ctx["reply_preferences"]["reply_goals"] = (
            [g.strip() for g in goals_raw.split(",") if g.strip()]
            or ["traffic", "allies", "correct_misinfo"]
        )

        ctx["reply_preferences"]["capacity"] = ask_choice(
            "How many replies can you manage?",
            ["LOW", "MEDIUM", "HIGH"],
            "MEDIUM"
        )
        avoid = ask(
            "Topics to AVOID engaging with? (comma-separated)\n"
            "  e.g. 'political party debates, attacks on MP'",
            ""
        )
        ctx["reply_preferences"]["avoid_topics"] = (
            [t.strip() for t in avoid.split(",") if t.strip()]
        )
        ctx["reply_preferences"]["include_do_not_reply_list"] = ask_yn(
            "Include a DO NOT REPLY list?", True
        )

        print("\n── REPLY IDENTITY ───────────────────────────────────────")
        ctx["reply_identity"] = {
            "page_name": ask("Facebook page name?", ctx["client_name"]),
            "page_handle": ask("Page handle / @username?", ""),
            "tone": ask(
                "Reply tone / voice?\n"
                "  e.g. 'Warm, factual, never aggressive, always human'",
                "Warm and factual"
            ),
            "goals": ask(
                "Reply goals?\n"
                "  e.g. 'Drive petition signatures, recruit allies, correct misinfo'",
                "Drive engagement and build support"
            ),
        }
    else:
        ctx["reply_identity"] = {}

    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(ctx, f, indent=2, ensure_ascii=False)
    print(f"\n  [OK] Context saved to {save_path}\n")
    return ctx


def load_context(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def extract_context_from_report(text: str) -> dict:
    """Mine a pre-written report.txt for client metadata so the HTML header
    is accurate even without a separate context.json."""
    import re

    ctx = default_context()

    # Build a flat lookup of tab-table rows: {field_label: value}
    fields: dict[str, str] = {}
    for line in text.splitlines():
        if "\t" in line:
            parts = line.split("\t", 1)
            if len(parts) == 2:
                key = parts[0].strip().lower()
                val = parts[1].strip()
                fields[key] = val

    # Client name — try several possible labels
    for label in ("client / organisation", "client/organisation", "client name",
                  "organisation", "client"):
        if label in fields and fields[label] not in ("", "unnamed client"):
            # Strip anything after " — " to keep it short
            ctx["client_name"] = re.split(r"\s+[\u2014\u2013\-]{1,2}\s+", fields[label])[0].strip()
            break

    # Client relationship
    for label in ("client relationship to post", "client relationship", "relationship"):
        if label in fields:
            val = fields[label].upper()
            for rel in ("CREATOR", "SUPPORTERS", "RESEARCHERS", "OPPONENTS"):
                if rel in val:
                    ctx["client_relationship"] = rel
                    break
            break

    # Reply preference
    for label in ("do you want reply recommendations?", "reply recommendations",
                  "want reply advice"):
        if label in fields:
            ctx.setdefault("reply_preferences", {})["want_reply_advice"] = (
                fields[label].strip().upper().startswith("YES")
            )
            break

    # Post URL
    for label in ("post url", "url", "post link"):
        if label in fields and fields[label].startswith("http"):
            ctx["post_url"] = fields[label]
            break

    # Language hint
    for label in ("language", "primary language", "language hint"):
        if label in fields:
            ctx["language_hint"] = fields[label]
            break

    return ctx


def default_context(url: str = "") -> dict:
    return {
        "client_name": "Unnamed Client",
        "client_goal": "Understand audience sentiment and identify content opportunities",
        "post_author": "Unknown",
        "client_relationship": "RESEARCHERS",
        "client_platforms": "General",
        "post_url": url,
        "language_hint": "",
        "reply_identity": {},
        "reply_preferences": {"want_reply_advice": False},
    }


# ──────────────────────────────────────────────────────────────────────────────
# 3.  PROMPT BUILDER
# ──────────────────────────────────────────────────────────────────────────────

RELATIONSHIP_GUIDANCE = {
    "CREATOR": "The client made this post. Reply advice is direct — what THEY should say.",
    "SUPPORTERS": "The client did NOT make this post but supports the cause. Reply advice focuses on amplification, recruitment, and engagement on behalf of the campaign, not the original poster.",
    "RESEARCHERS": "The client is purely analytical. No reply advice needed — deliver a neutral, evidence-based analysis.",
    "OPPONENTS": "The client opposes the position in the post. Focus on counter-strategy, messaging weaknesses to exploit, and risk areas.",
}

CAPACITY_GUIDANCE = {
    "LOW":    "Provide the top 3 most important replies only.",
    "MEDIUM": "Provide up to 10 prioritised replies.",
    "HIGH":   "Provide the full reply strategy for all valuable comment categories.",
}


def build_prompt(ctx: dict, comments: list[dict], max_comments: int = 500) -> str:
    rel = ctx.get("client_relationship", "RESEARCHERS")
    rel_note = RELATIONSHIP_GUIDANCE.get(rel, "")
    prefs = ctx.get("reply_preferences", {})
    want_reply = prefs.get("want_reply_advice", False)
    capacity = prefs.get("capacity", "MEDIUM")
    avoid = prefs.get("avoid_topics", [])
    avoid_str = "\n".join(f"  - {t}" for t in avoid) if avoid else "  - None specified"
    include_dnr = prefs.get("include_do_not_reply_list", True)
    rep_id = ctx.get("reply_identity", {})
    lang_hint = ctx.get("language_hint", "")
    lang_note = f"NOTE: Comments are primarily in {lang_hint}. Analyse in that language; write the report in English." if lang_hint else ""

    # build context block header
    ctx_block = f"""
═══════════════════════════════════════════════════════════
AUDIENCE INTELLIGENCE REPORT — CONTEXT BLOCK
═══════════════════════════════════════════════════════════

CLIENT NAME / ORGANISATION:
{ctx.get('client_name', 'Unnamed Client')}

CLIENT GOAL:
{ctx.get('client_goal', 'Understand audience sentiment')}

POST AUTHOR / CONTENT CREATOR:
{ctx.get('post_author', 'Unknown')}

CLIENT RELATIONSHIP TO POST:
{rel} — {rel_note}

CLIENT'S OWN PLATFORMS:
{ctx.get('client_platforms', 'Not specified')}

REPLY ADVICE REQUESTED: {'YES' if want_reply else 'NO'}
{f'''
REPLY IDENTITY:
  Page Name:    {rep_id.get('page_name', '')}
  Handle:       {rep_id.get('page_handle', '')}
  Tone / Voice: {rep_id.get('tone', '')}
  Reply Goals:  {rep_id.get('goals', '')}

REPLY CAPACITY: {CAPACITY_GUIDANCE.get(capacity, '')}

TOPICS TO AVOID:
{avoid_str}

INCLUDE DO-NOT-REPLY LIST: {'YES' if include_dnr else 'NO'}
''' if want_reply else ''}
POST URL:
{ctx.get('post_url', 'Not provided')}

{lang_note}

═══════════════════════════════════════════════════════════
"""

    # truncate comments for token safety
    sample = comments[:max_comments]
    comments_block = "\n".join(
        f"[{i+1}] {c['author']} (likes:{c['likes']}) — {c['text']}"
        for i, c in enumerate(sample)
    )

    reply_sections = ""
    if want_reply:
        reply_sections = """
SECTION 16 — REPLY STRATEGY MATRIX

Using the context above, produce a reply strategy section. For each GREEN tier comment output a reply-card. For RED/GREY tier use alert--danger. For BLUE tier use alert--info. Use SPECIFIC comments from the dataset with exact text.

<div class="reply-card">
<div class="reply-card__rank">#1 — Author Name (N likes)</div>
<div class="reply-card__comment">Exact quoted comment text</div>
<div class="reply-card__reason">Why this comment is valuable to reply to</div>
<div class="reply-card__suggestion"><strong>Suggested Reply:</strong> Ready-to-post reply text</div>
</div>

<div class="alert alert--danger">
<div class="alert__title">❌ Do Not Reply — Author Name</div>
<p>Why not to reply, and what to do instead</p>
</div>

<div class="alert alert--info">
<div class="alert__title">🔵 Private Message — Author Name</div>
<p>What they have and your private message goal</p>
</div>
"""

    # HTML component reference injected into the prompt
    html_guide = """
═══════════════════════════════════════════════════════════
HTML COMPONENT REFERENCE — USE THESE IN YOUR OUTPUT
═══════════════════════════════════════════════════════════

You MUST use these HTML components in your report. Do not use plain text lists for data that fits a component. The renderer passes these through directly into the final PDF-ready report.

COMMENT CLUSTERS (one per cluster — Section 1):
<div class="cluster-card">
<div class="cluster-card__header">
<span class="cluster-card__name">🔴 Cluster 1 — "Cluster Title"</span>
<span class="cluster-card__count">~N comments · XX%</span>
</div>
<p style="font-size:0.85rem;color:var(--muted);margin-bottom:8px">Brief description.</p>
<div class="quote">Comment text <span class="quote__author">— Author (N likes)</span></div>
<div class="alert alert--info"><div class="alert__title">Campaign Value</div><p>Why this matters to the client</p></div>
</div>

SENTIMENT BAR + STAT CARDS (Section 2 — once only):
<div class="sentiment-bar">
<div class="sentiment-bar__segment sentiment-bar__segment--positive" style="flex:65">65% Positive</div>
<div class="sentiment-bar__segment sentiment-bar__segment--negative" style="flex:20">20% Negative</div>
<div class="sentiment-bar__segment sentiment-bar__segment--neutral" style="flex:15">15% Neutral</div>
</div>
<div class="stats-grid">
<div class="stat-card stat-card--positive"><div class="stat-value">65%</div><div class="stat-label">Positive / Supportive</div></div>
<div class="stat-card stat-card--negative"><div class="stat-value">20%</div><div class="stat-label">Sceptical / Negative</div></div>
<div class="stat-card stat-card--neutral"><div class="stat-value">15%</div><div class="stat-label">Neutral / Questioning</div></div>
</div>
Variants: --positive (green) | --negative (red) | --neutral (yellow) | --accent (cyan)

STATS GRID (for any 3+ comparable numbers):
<div class="stats-grid">
<div class="stat-card stat-card--accent"><div class="stat-value">799</div><div class="stat-label">Total Comments</div></div>
<div class="stat-card stat-card--positive"><div class="stat-value">87%</div><div class="stat-label">Support Rate</div></div>
</div>

ALERT BOXES:
<div class="alert alert--warn"><div class="alert__title">⚠️ Critical Insight</div><p>Finding text</p></div>
<div class="alert alert--danger"><div class="alert__title">⚠️ Action Required</div><p>Urgent item</p></div>
<div class="alert alert--success"><div class="alert__title">✅ Opportunity</div><p>High-value opportunity</p></div>
<div class="alert alert--info"><div class="alert__title">ℹ️ Note</div><p>Background info</p></div>

VIRAL SCORE (Section 15):
<div class="score-display">
<div class="score-circle" style="--score-pct:90">9.0</div>
<div class="score-details"><h4>Viral Probability Score</h4><p>9.0 / 10 — Key reasoning</p></div>
</div>

GOLD QUOTES HALL OF FAME:
<h3 style="color:var(--accent);margin:24px 0 12px;">💎 Diamond Tier — Defining Statements</h3>
<div class="gold-quote gold-quote--diamond">
<div class="gold-quote__text">"Exact quote"</div>
<div class="gold-quote__meta"><span>Author · Platform</span><span>N likes</span></div>
<p style="font-size:0.82rem;color:var(--muted);margin-top:10px;"><strong>Why Diamond:</strong> Explanation. <span style="color:var(--warn);">Recommended Use: Social Media · Press Release</span></p>
</div>
<h3 style="color:var(--warn);margin:24px 0 12px;">🥇 Gold Tier</h3>
<div class="gold-quote">
<div class="gold-quote__text">"Exact quote"</div>
<div class="gold-quote__meta"><span>Author · Platform</span><span>N likes</span><span>Recommended Use</span></div>
</div>

IDEA CARDS (content opportunities, campaign products, personas):
<div class="idea-card">
<div class="idea-card__title">Idea Title Here</div>
<span class="idea-card__format">FORMAT / TYPE</span>
<div class="idea-card__rationale">Why this works for this specific client/audience.</div>
</div>

CLOSING MANDATE BOX (one, at the very end):
<div class="mandate-box">
<div class="mandate-box__statement">
The data mandate in 2–3 sentences.<br><br>
<strong>Final closing call to action.</strong>
</div>
</div>

TABLES (structured data with headers):
<table class="report-table"><thead><tr><th>Col 1</th><th>Col 2</th></tr></thead>
<tbody><tr><td>Data</td><td>Data</td></tr></tbody></table>

QUOTE BLOCKS: <div class="quote">Text <span class="quote__author">— Author (N likes)</span></div>

RULES:
- cluster-card for ALL comment clusters — never plain lists
- sentiment-bar + stats-grid at the START of the sentiment section
- stats-grid for any 3+ comparable numbers
- Every Critical Insight gets an alert box
- Gold Quotes MUST use gold-quote/gold-quote--diamond components
- End with mandate-box
- Plain commentary between components: <p>text</p> or <h4>subheading</h4>
═══════════════════════════════════════════════════════════
"""

    prompt = f"""{ctx_block}

You are an expert audience researcher, market analyst, and social media strategist producing a professional Audience Intelligence Report.

{html_guide}

Calibrate EVERY section to the client's goal, relationship, and platform. This is not a generic analysis — it is intelligence for a specific client with a specific purpose.

STEP 1 – Clean the Data
• Ignore duplicates, spam, bots, emoji-only comments
• Focus on meaningful audience feedback

STEP 2 – Comment Clustering
Group comments into clusters. OUTPUT EACH CLUSTER AS A cluster-card (see HTML reference).
For each: title | count | 3–5 quote blocks | campaign value alert

STEP 3 – Full Report

SECTION 1 — OVERVIEW
Use a stats-grid for key numbers (total comments, support rate, platforms, top engagement).
Then write a brief summary paragraph.

SECTION 2 — AUDIENCE SENTIMENT
Start with the sentiment-bar and stats-grid. Then explain emotional tone.
Use alert--warn for any critical or surprising sentiment finding.

SECTION 3 — KEY THEMES (RANKED BY PREVALENCE)
Use idea-cards for the top themes (title + % + explanation).

SECTION 4 — AUDIENCE QUESTIONS
Group by type with bold subheadings. Use alert--danger for questions the campaign MUST answer.

SECTION 5 — AUDIENCE FRUSTRATIONS
Use idea-cards for each named frustration.

SECTION 6 — AUDIENCE DESIRES
Use idea-cards for each named desire.

SECTION 7 — VIRAL CONTENT TRIGGERS
Use a score-display for each trigger (Score X/10) with explanation.

SECTION 8 — CONTENT OPPORTUNITIES
Each as an idea-card (title, format badge, rationale). Calibrated to client's platforms.

SECTION 9 — ENGAGEMENT OPPORTUNITIES
Each as an idea-card. How the CLIENT specifically should engage.

SECTION 10 — LEAD / ALLY OPPORTUNITIES
Use alert--success for high-value leads. Include who, what they have, approach.

SECTION 11 — CAMPAIGN OPPORTUNITIES
Use idea-cards. Include realistic impact estimates.

SECTION 12 — AUDIENCE PROFILE
Use stats-grid for demographics. Describe each persona as an idea-card.

SECTION 13 — TOP COMMENTS WORTH REPLYING TO
reply-card for GREEN tier. alert--danger for DO NOT REPLY. alert--info for PRIVATE MESSAGE.

SECTION 14 — STRATEGIC RECOMMENDATIONS
Use idea-cards with numbered priorities. Bold the specific action.

SECTION 15 — VIRAL PROBABILITY SCORE
score-display component. Key drivers. End with the mandate-box closing statement.
{reply_sections}

═══════════════════════════════════════════════════════════
COMMENTS TO ANALYSE ({len(sample)} of {len(comments)} total):
═══════════════════════════════════════════════════════════

{comments_block}
"""
    return prompt


# ──────────────────────────────────────────────────────────────────────────────
# 4.  LLM CALLER
# ──────────────────────────────────────────────────────────────────────────────

def call_openai(prompt: str, api_key: str, model: str = "gpt-4o") -> str:
    try:
        from openai import OpenAI
    except ImportError:
        sys.exit("[ERROR] openai package not installed. Run: pip install openai")

    client = OpenAI(api_key=api_key)
    print(f"  Calling {model}… (this may take 30-90 seconds for large comment sets)")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert audience researcher and social media strategist. "
                    "You produce professional Audience Intelligence Reports in HTML. "
                    "When given HTML component templates to use, you MUST use them exactly as specified — "
                    "never substitute plain text for a component that has been defined. "
                    "Your output will be rendered directly into a PDF-quality dark-theme report. "
                    "Reports are calibrated to the specific client goal — never generic."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        max_tokens=4096,
        temperature=0.3,
    )
    return response.choices[0].message.content


# ──────────────────────────────────────────────────────────────────────────────
# 5.  HTML REPORT GENERATOR
# ──────────────────────────────────────────────────────────────────────────────

def _parse_report_sections(text: str) -> list[dict]:
    """Split a report.txt into a list of sections.
    Each section: {id: 'A'|'1'|..., title: str, body: str}
    Lines before the first section become id='_header'.
    """
    import re
    sections: list[dict] = []
    current: dict = {"id": "_header", "title": "", "body_lines": []}

    for line in text.splitlines():
        stripped = line.strip()

        # ═══ dividers → skip them, they're just visual separators
        if re.match(r"^[═─]{4,}$", stripped):
            continue

        # SECTION X — TITLE
        m = re.match(r"^SECTION\s+([A-Z0-9]+)\s+[\u2014\u2013\-]+\s+(.+)$", stripped)
        if m:
            sections.append(current)
            current = {"id": m.group(1), "title": m.group(2).strip(), "body_lines": []}
            continue

        # Numbered section heading: "1. Comment Clusters" etc
        m = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if m and len(stripped) < 100:
            sections.append(current)
            current = {"id": m.group(1), "title": m.group(2).strip(), "body_lines": []}
            continue

        # ALL CAPS heading without SECTION prefix (e.g. GOLD QUOTES HALL OF FAME)
        if (re.match(r"^[A-Z\s\u2014\u2013/&\-\u2019\u201C\u201D:]+$", stripped)
                and len(stripped) > 6 and len(stripped) < 80
                and stripped not in ("YES", "NO", "MEDIUM", "HIGH", "LOW")
                and not stripped.startswith("URGENT")
                and "\t" not in line):
            sections.append(current)
            sid = stripped[:20].replace(" ", "_").lower()
            current = {"id": sid, "title": stripped.title(), "body_lines": []}
            continue

        current["body_lines"].append(line)

    sections.append(current)
    # Remove empty header if nothing captured
    return [s for s in sections if s["body_lines"] or s["id"] != "_header"]


def _render_section_body(body_lines: list[str]) -> str:
    """Convert the body lines of a section into styled HTML with rich visual components."""
    import re
    import html as _html

    def esc(s: str) -> str:
        return _html.escape(s, quote=False)

    def inline_fmt(s: str) -> str:
        s = esc(s)
        s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
        # Emoji badge colouring
        s = s.replace("🟢", '<span style="color:var(--success)">🟢</span>')
        s = s.replace("🔴", '<span style="color:var(--danger)">🔴</span>')
        s = s.replace("🟡", '<span style="color:var(--warn)">🟡</span>')
        s = s.replace("🟠", '<span style="color:var(--warn)">🟠</span>')
        s = s.replace("🔵", '<span style="color:var(--accent)">🔵</span>')
        s = s.replace("💎", '<span style="color:var(--accent)">💎</span>')
        s = s.replace("🥇", '<span style="color:var(--warn)">🥇</span>')
        s = s.replace("⚪", '<span style="color:var(--muted)">⚪</span>')
        # Tier labels
        s = re.sub(r"GREEN TIER",  '<span class="badge badge--high">GREEN TIER</span>', s)
        s = re.sub(r"YELLOW TIER", '<span class="badge badge--warm">YELLOW TIER</span>', s)
        s = re.sub(r"RED TIER",    '<span class="badge badge--hot">RED TIER</span>', s)
        s = re.sub(r"BLUE TIER",   '<span class="badge badge--medium">BLUE TIER</span>', s)
        s = re.sub(r"GREY TIER",   '<span class="badge badge--cold">GREY TIER</span>', s)
        return s

    html_parts: list[str] = []
    in_ul = False
    in_cluster = False
    in_gold_section = ""  # "diamond" or "gold" or ""
    table_buf: list[list[str]] = []

    def flush_ul():
        nonlocal in_ul
        if in_ul:
            html_parts.append("</ul>")
            in_ul = False

    def flush_cluster():
        nonlocal in_cluster
        if in_cluster:
            html_parts.append("</div>")  # close cluster-card
            in_cluster = False

    def flush_table():
        nonlocal table_buf, in_gold_section
        if not table_buf:
            return

        # Special handling: if we're in gold section and table has Quote/Author cols
        # render as gold-quote cards instead of a table
        first = table_buf[0]
        first_lower = [h.lower().strip() for h in first]
        is_gold_table = (
            in_gold_section == "gold"
            and len(first) >= 3
            and any("quote" in h for h in first_lower)
        )
        if is_gold_table:
            # Find column indices
            quote_idx = next((i for i, h in enumerate(first_lower) if "quote" in h), 1)
            author_idx = next((i for i, h in enumerate(first_lower) if "author" in h), 2)
            use_idx = next((i for i, h in enumerate(first_lower) if "use" in h), -1)
            for row in table_buf[1:]:  # skip header
                q_text = row[quote_idx] if quote_idx < len(row) else ""
                q_author = row[author_idx] if author_idx < len(row) else ""
                q_use = row[use_idx] if use_idx >= 0 and use_idx < len(row) else ""
                # Clean quote marks from text
                q_text_clean = q_text.strip().strip('""\u201C\u201D\u00AB\u00BB')
                html_parts.append('<div class="gold-quote">')
                html_parts.append(f'<div class="gold-quote__text">{q_text_clean}</div>')
                meta_spans = f'<span>{q_author}</span>'
                if q_use:
                    meta_spans += f'<span>{q_use}</span>'
                html_parts.append(f'<div class="gold-quote__meta">{meta_spans}</div>')
                html_parts.append('</div>')
            table_buf.clear()
            return

        html_parts.append('<table class="report-table">')
        first = table_buf[0]
        is_header = any(
            h.lower().strip() in ("field", "detail", "metric", "value", "batch",
                           "trigger", "score", "platform", "estimate", "#",
                           "author", "likes", "action", "category", "use case",
                           "guideline", "status", "name", "role", "factor",
                           "rating", "cluster", "count", "prevalence", "tier",
                           "quote", "use for", "cited by", "fact", "verified?",
                           "mentioned by", "personal names ok?", "consent required?",
                           "reasoning", "report title")
            for h in first
        )
        start_idx = 0
        if is_header:
            html_parts.append("<thead><tr>" +
                "".join(f"<th>{c}</th>" for c in first) +
                "</tr></thead>")
            start_idx = 1
        html_parts.append("<tbody>")
        for row in table_buf[start_idx:]:
            html_parts.append("<tr>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>")
        html_parts.append("</tbody></table>")
        table_buf.clear()

    # ── Pre-scan: detect master totals block, sentiment table, decision tree ──
    # Build the HTML line by line with look-ahead
    i = 0
    lines = body_lines

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # ── Raw HTML passthrough (LLM already produced HTML components) ──
        if stripped.startswith("<") and not stripped.startswith("<!"):
            flush_ul()
            flush_table()
            # Don't close cluster on HTML passthrough — LLM manages its own divs
            html_parts.append(stripped)
            i += 1
            continue

        # ── Decision tree / box-drawing characters → code block ──
        if stripped and any(ch in stripped for ch in "┌┐└┘│├┤┬┴─┼▼▶"):
            flush_ul()
            flush_table()
            flush_cluster()
            tree_lines = []
            while i < len(lines):
                s = lines[i].strip()
                if s and any(ch in s for ch in "┌┐└┘│├┤┬┴─┼▼▶"):
                    tree_lines.append(esc(lines[i].rstrip()))
                    i += 1
                elif not s and tree_lines:
                    # peek ahead — if next line has box chars, include the blank
                    if i + 1 < len(lines) and any(ch in lines[i+1] for ch in "┌┐└┘│├┤┬┴─┼▼▶"):
                        tree_lines.append("")
                        i += 1
                    else:
                        break
                else:
                    break
            html_parts.append(f'<div class="decision-tree">{chr(10).join(tree_lines)}</div>')
            continue

        # ── Master totals block: lines with LABEL: VALUE format (aligned stats) ──
        m_stat_line = re.match(r"^([A-Z][A-Z\s/\(\)\-—]+?):\s{2,}(.+)$", stripped)
        if m_stat_line:
            flush_ul()
            flush_table()
            flush_cluster()
            stat_lines = []
            while i < len(lines):
                s = lines[i].strip()
                m_stat = re.match(r"^([A-Z][A-Z\s/\(\)\-—]+?):\s+(.+)$", s)
                if m_stat:
                    stat_lines.append((m_stat.group(1).strip(), m_stat.group(2).strip()))
                    i += 1
                elif s.startswith("—") or s.startswith("–"):
                    # sub-stat like "— Facebook (3 posts): 918"
                    m_sub = re.match(r"^[—–]\s*(.+?):\s+(.+)$", s)
                    if m_sub:
                        stat_lines.append((m_sub.group(1).strip(), m_sub.group(2).strip()))
                    i += 1
                elif not s:
                    i += 1
                    break
                else:
                    break
            if stat_lines:
                html_parts.append('<div class="stats-grid">')
                variants = ["--accent", "--primary", "--positive", "--neutral", ""]
                for idx, (label, value) in enumerate(stat_lines):
                    variant = variants[idx % len(variants)]
                    cls = f" stat-card{variant}" if variant else " stat-card"
                    html_parts.append(
                        f'<div class="{cls.strip()}">'
                        f'<div class="stat-value">{esc(value)}</div>'
                        f'<div class="stat-label">{esc(label)}</div></div>'
                    )
                html_parts.append('</div>')
            continue

        # ── Sentiment table with emoji percentages → sentiment-bar + stat-cards ──
        m_sent = re.match(r"^(🟢|🔴|🟡|🟠|⚪)\s+(.+?):\s+([\d~]+)%.*?(\d+)%.*?(\d+)%.*?(\d+)%.*?~?(\d+)%", stripped)
        if not m_sent:
            m_sent = re.match(r"^(🟢|🔴|🟡|🟠|⚪)\s+(.+?):\s+.+?~?(\d+)%\s*$", stripped)
        if m_sent:
            flush_ul()
            flush_table()
            flush_cluster()
            # Collect all sentiment lines
            sent_rows = []
            while i < len(lines):
                s = lines[i].strip()
                m_s = re.match(r"^(🟢|🔴|🟡|🟠|⚪)\s+(.+?):\s+.*?~?(\d+)%\s*$", s)
                if m_s:
                    emoji = m_s.group(1)
                    label = m_s.group(2).strip()
                    pct = m_s.group(3)
                    cls_map = {"🟢": "positive", "🔴": "negative", "🟡": "neutral", "🟠": "curious", "⚪": "neutral"}
                    sent_rows.append((emoji, label, int(pct), cls_map.get(emoji, "neutral")))
                    i += 1
                elif not s or re.match(r"^[═─]{4,}$", s):
                    i += 1
                    if not s:
                        break
                else:
                    break
            if sent_rows:
                # Sentiment bar
                html_parts.append('<div class="sentiment-bar">')
                for emoji, label, pct, cls in sent_rows:
                    html_parts.append(
                        f'<div class="sentiment-bar__segment sentiment-bar__segment--{cls}" '
                        f'style="flex:{pct}">{pct}% {esc(label)}</div>'
                    )
                html_parts.append('</div>')
                # Stat cards
                card_cls_map = {"positive": "--positive", "negative": "--negative", "neutral": "--neutral", "curious": "--accent"}
                html_parts.append('<div class="stats-grid">')
                for emoji, label, pct, cls in sent_rows:
                    card_cls = card_cls_map.get(cls, "")
                    html_parts.append(
                        f'<div class="stat-card stat-card{card_cls}">'
                        f'<div class="stat-value">~{pct}%</div>'
                        f'<div class="stat-label">{esc(label)}</div></div>'
                    )
                html_parts.append('</div>')
            continue

        # ── Cluster header: "Cluster N: 'Title' — Subtitle" ──
        m_cluster = re.match(
            r"^Cluster\s+(\d+):\s*['\"\u201C\u201D]?(.+?)['\"\u201C\u201D]?\s*[\u2014\u2013\-]+\s*(.+)$",
            stripped
        )
        if m_cluster:
            flush_ul()
            flush_table()
            flush_cluster()
            cluster_num = m_cluster.group(1)
            cluster_name = m_cluster.group(2).strip()
            cluster_sub = m_cluster.group(3).strip()
            # Look ahead for "Size: X% ..."
            count_label = ""
            if i + 1 < len(lines):
                m_size = re.match(r"^Size:\s*(.+)$", lines[i + 1].strip())
                if m_size:
                    count_label = m_size.group(1).strip()
                    i += 1
            in_cluster = True
            html_parts.append('<div class="cluster-card">')
            html_parts.append('<div class="cluster-card__header">')
            html_parts.append(
                f'<span class="cluster-card__name">Cluster {cluster_num} — {esc(cluster_name)}</span>'
            )
            if count_label:
                html_parts.append(f'<span class="cluster-card__count">{esc(count_label)}</span>')
            html_parts.append('</div>')
            if cluster_sub:
                html_parts.append(f'<p style="font-size:0.85rem;color:var(--muted);margin-bottom:8px">{inline_fmt(cluster_sub)}</p>')
            i += 1
            continue

        # ── Cluster header variant (no quotes): "Cluster N: Title" ──
        m_cluster2 = re.match(r"^Cluster\s+(\d+):\s+(.+)$", stripped)
        if m_cluster2 and not m_cluster:
            flush_ul()
            flush_table()
            flush_cluster()
            cluster_num = m_cluster2.group(1)
            cluster_rest = m_cluster2.group(2).strip()
            count_label = ""
            if i + 1 < len(lines):
                m_size = re.match(r"^Size:\s*(.+)$", lines[i + 1].strip())
                if m_size:
                    count_label = m_size.group(1).strip()
                    i += 1
            in_cluster = True
            html_parts.append('<div class="cluster-card">')
            html_parts.append('<div class="cluster-card__header">')
            html_parts.append(f'<span class="cluster-card__name">Cluster {cluster_num} — {esc(cluster_rest)}</span>')
            if count_label:
                html_parts.append(f'<span class="cluster-card__count">{esc(count_label)}</span>')
            html_parts.append('</div>')
            i += 1
            continue

        # ── Campaign value / Critical Insight → alert box ──
        m_alert = re.match(r"^Campaign value:\s*(.+)$", stripped, re.IGNORECASE)
        if m_alert:
            flush_ul()
            flush_table()
            value = m_alert.group(1).strip()
            # Determine alert variant
            val_upper = value.upper()
            if "HIGHEST" in val_upper or "DIAMOND" in val_upper or "VERY HIGH" in val_upper:
                alert_cls = "alert--success"
            elif "HIGH" in val_upper:
                alert_cls = "alert--info"
            elif "CRITICAL" in val_upper or "MONITOR" in val_upper:
                alert_cls = "alert--warn"
            elif "DO NOT" in val_upper:
                alert_cls = "alert--danger"
            else:
                alert_cls = "alert--info"
            html_parts.append(
                f'<div class="alert {alert_cls}">'
                f'<div class="alert__title">Campaign Value</div>'
                f'<p style="font-size:0.85rem;color:var(--text)">{inline_fmt(value)}</p></div>'
            )
            i += 1
            continue

        # Critical Insight: → alert
        if stripped.lower().startswith("critical insight"):
            flush_ul()
            flush_table()
            title_text = stripped
            body_text = ""
            i += 1
            # Collect the paragraph(s) following the insight heading
            insight_lines = []
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    i += 1
                    break
                insight_lines.append(s)
                i += 1
            body_text = " ".join(insight_lines)
            html_parts.append(
                f'<div class="alert alert--warn">'
                f'<div class="alert__title">⚠️ {esc(title_text)}</div>'
                f'<p style="font-size:0.85rem;color:var(--text)">{inline_fmt(body_text)}</p></div>'
            )
            continue

        # ACTION REQUIRED → alert danger
        if stripped.upper().startswith("ACTION REQUIRED"):
            flush_ul()
            flush_table()
            html_parts.append(
                f'<div class="alert alert--danger">'
                f'<div class="alert__title">⚠️ Action Required</div>'
                f'<p style="font-size:0.85rem;color:var(--text)">{inline_fmt(stripped)}</p></div>'
            )
            i += 1
            continue

        # ── DIAMOND quote: "DIAMOND #N — Batch N" ──
        m_diamond = re.match(r"^DIAMOND\s+#(\d+)", stripped, re.IGNORECASE)
        if m_diamond:
            flush_ul()
            flush_table()
            flush_cluster()
            diamond_label = stripped
            i += 1
            # Collect the quoted text and meta
            quote_text = ""
            meta_parts = []
            extra_p = []
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    i += 1
                    if quote_text:
                        break
                    continue
                # Quote line: starts with "
                if s.startswith(("\u201C", '"', "\u00AB")) and not quote_text:
                    # Parse: "text" — Author, details
                    m_q = re.match(r'^[\u201C"\u00AB](.+?)[\u201D"\u00BB]?\s*[\u2014\u2013\-]+\s*(.+)$', s)
                    if m_q:
                        quote_text = m_q.group(1)
                        attribution = m_q.group(2)
                        meta_parts.append(attribution)
                    else:
                        quote_text = s.strip('""\u201C\u201D\u00AB\u00BB')
                    i += 1
                    continue
                # Multi-line quote continuation with translation in ()
                if quote_text and s.startswith("(") and s.endswith(")"):
                    # translation line
                    extra_p.append(s)
                    i += 1
                    continue
                # Attribution line: starts with —
                if s.startswith(("\u2014", "\u2013", "—", "–")):
                    attr = s.lstrip("\u2014\u2013—– ").strip()
                    meta_parts = [attr] if attr else meta_parts
                    i += 1
                    continue
                # USE FOR line
                if s.upper().startswith("USE FOR:"):
                    meta_parts.append(s)
                    i += 1
                    continue
                break

            if quote_text:
                html_parts.append('<div class="gold-quote gold-quote--diamond">')
                html_parts.append(f'<div class="gold-quote__text">{inline_fmt(quote_text)}</div>')
                if extra_p:
                    for ep in extra_p:
                        html_parts.append(f'<p style="font-size:0.82rem;color:var(--muted);margin-top:6px">{inline_fmt(ep)}</p>')
                if meta_parts:
                    spans = "".join(f"<span>{inline_fmt(m)}</span>" for m in meta_parts)
                    html_parts.append(f'<div class="gold-quote__meta">{spans}</div>')
                html_parts.append('</div>')
            continue

        # ── Gold quote table: "#\tQuote\tAuthor..." ──
        # Already handled by generic tab-table logic, but let's detect gold quote
        # rows inside the Gold Quotes section (tab-separated with #, Quote, Author cols)

        # ── Score display: "Viral Probability Assessment: 9.0 / 10" ──
        m_score = re.match(r"^(Viral\s+Probability\s+.+?):\s*([\d.]+)\s*/\s*(\d+)", stripped)
        if m_score:
            flush_ul()
            flush_table()
            flush_cluster()
            score_title = m_score.group(1)
            score_val = m_score.group(2)
            score_max = m_score.group(3)
            try:
                pct = int(float(score_val) / float(score_max) * 100)
            except (ValueError, ZeroDivisionError):
                pct = 0
            html_parts.append(
                f'<div class="score-display">'
                f'<div class="score-circle" style="--score-pct:{pct}">{esc(score_val)}</div>'
                f'<div class="score-details">'
                f'<h4>{esc(score_title)}</h4>'
                f'<p>{esc(score_val)} / {esc(score_max)}</p>'
                f'</div></div>'
            )
            i += 1
            continue

        # ── Reply recommendation: "🟢 #N:" or "🔴 #N:" ──
        m_reply = re.match(r"^(🟢|🔴|🟡|🔵)\s+#(\d+):\s+(.+)$", stripped)
        if m_reply:
            flush_ul()
            flush_table()
            flush_cluster()
            reply_emoji = m_reply.group(1)
            reply_rank = m_reply.group(2)
            reply_author = m_reply.group(3)
            i += 1
            # Collect body of the reply card
            comment_text = ""
            reason_lines = []
            suggestion_lines = []
            current_field = "body"
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    i += 1
                    break
                if s.startswith(("🟢 #", "🔴 #", "🟡 #", "🔵 #")):
                    break
                if s.startswith("Comment:"):
                    comment_text = s[8:].strip().strip('""\u201C\u201D')
                    current_field = "comment"
                elif s.startswith("Translation:"):
                    comment_text += " " + s[12:].strip().strip('""\u201C\u201D')
                elif s.startswith("Decision:"):
                    reason_lines.append(s[9:].strip())
                    current_field = "reason"
                elif s.startswith("Goal:"):
                    reason_lines.append(s)
                    current_field = "reason"
                elif s.startswith("Reply ("):
                    suggestion_lines.append(s)
                    current_field = "suggestion"
                elif s.startswith("Action:"):
                    reason_lines.append(s)
                    current_field = "reason"
                elif s.startswith("PM ("):
                    suggestion_lines.append(s)
                    current_field = "suggestion"
                else:
                    if current_field == "suggestion":
                        suggestion_lines.append(s)
                    elif current_field == "reason":
                        reason_lines.append(s)
                    elif current_field == "comment":
                        comment_text += " " + s
                    else:
                        reason_lines.append(s)
                i += 1

            html_parts.append('<div class="reply-card">')
            html_parts.append(f'<div class="reply-card__rank">#{reply_rank} — {esc(reply_author)}</div>')
            if comment_text:
                html_parts.append(f'<div class="reply-card__comment">{inline_fmt(comment_text)}</div>')
            if reason_lines:
                html_parts.append(f'<div class="reply-card__reason">{inline_fmt(" ".join(reason_lines))}</div>')
            if suggestion_lines:
                html_parts.append(
                    f'<div class="reply-card__suggestion"><strong>Suggested Reply:</strong> '
                    f'{inline_fmt(" ".join(suggestion_lines))}</div>'
                )
            html_parts.append('</div>')
            continue

        # ── Script blocks: "Script A: Title" → reply-card ──
        m_script = re.match(r"^Script\s+([A-Z]):\s+(.+)$", stripped)
        if m_script:
            flush_ul()
            flush_table()
            flush_cluster()
            script_id = m_script.group(1)
            script_title = m_script.group(2)
            i += 1
            script_lines = []
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    i += 1
                    break
                if re.match(r"^Script\s+[A-Z]:", s):
                    break
                script_lines.append(s)
                i += 1
            html_parts.append('<div class="reply-card">')
            html_parts.append(f'<div class="reply-card__rank">Script {script_id}</div>')
            html_parts.append(f'<div class="reply-card__comment">{esc(script_title)}</div>')
            if script_lines:
                html_parts.append(f'<div class="reply-card__suggestion">{inline_fmt(" ".join(script_lines))}</div>')
            html_parts.append('</div>')
            continue

        # ── Content / Opportunity / Lead / Persona numbered items → idea-card ──
        m_idea = re.match(
            r"^(Content|Opportunity|Lead|Persona|Priority)\s+(\d+):\s+(.+)$",
            stripped
        )
        if m_idea:
            flush_ul()
            flush_table()
            flush_cluster()
            idea_type = m_idea.group(1)
            idea_num = m_idea.group(2)
            idea_title = m_idea.group(3)
            i += 1
            # Collect body text
            idea_body_lines = []
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    i += 1
                    break
                # Stop if next item or section
                if re.match(r"^(Content|Opportunity|Lead|Persona|Priority)\s+\d+:", s):
                    break
                idea_body_lines.append(s)
                i += 1
            html_parts.append('<div class="idea-card">')
            html_parts.append(f'<div class="idea-card__title">{idea_type} {idea_num}: {esc(idea_title)}</div>')
            html_parts.append(f'<span class="idea-card__format">{esc(idea_type)}</span>')
            if idea_body_lines:
                html_parts.append(f'<div class="idea-card__rationale">{inline_fmt(" ".join(idea_body_lines))}</div>')
            html_parts.append('</div>')
            continue

        # ── Theme / Trigger / Frustration / Desire / numbered items → idea card ──
        m_theme = re.match(
            r"^(Theme|Trigger|Frustration|Desire)\s+(\d+):\s+(.+)$",
            stripped
        )
        if m_theme:
            flush_ul()
            flush_table()
            flush_cluster()
            item_type = m_theme.group(1)
            item_num = m_theme.group(2)
            item_title = m_theme.group(3)
            i += 1
            item_body = []
            while i < len(lines):
                s = lines[i].strip()
                if not s:
                    i += 1
                    break
                if re.match(r"^(Theme|Trigger|Frustration|Desire)\s+\d+:", s):
                    break
                item_body.append(s)
                i += 1
            # Extract score if present (e.g., "Score: 10/10")
            score_text = ""
            m_sc = re.match(r"(.+?)\s*\(Score:\s*([\d.]+/\d+)\)", item_title)
            if m_sc:
                item_title = m_sc.group(1).strip()
                score_text = m_sc.group(2)

            html_parts.append('<div class="idea-card">')
            html_parts.append(f'<div class="idea-card__title">{esc(item_title)}</div>')
            fmt_label = item_type
            if score_text:
                fmt_label += f" {item_num} — {score_text}"
            else:
                fmt_label += f" {item_num}"
            html_parts.append(f'<span class="idea-card__format">{esc(fmt_label)}</span>')
            if item_body:
                html_parts.append(f'<div class="idea-card__rationale">{inline_fmt(" ".join(item_body))}</div>')
            html_parts.append('</div>')
            continue

        # ── Numbered list items: "1. Title" / "2. Title" (for campaign items) ──
        m_num_item = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if m_num_item and len(stripped) < 120:
            # Check if it's a numbered campaign item (short title + body below)
            flush_ul()
            flush_table()
            num = m_num_item.group(1)
            title = m_num_item.group(2)
            # Peek ahead: if next line has sub-fields (Key:, Format:, etc.) → idea card
            has_subfields = False
            if i + 1 < len(lines):
                next_s = lines[i + 1].strip()
                if re.match(r"^(Audience demand|Format|Purpose|Risk|Projected|Key language|Demographics|Emotional state|Behaviour|Campaign value|How to reach|Representative|Design|Distribution|Action|Role|Comment|Value|Recommendation|Username):", next_s, re.IGNORECASE):
                    has_subfields = True
            if has_subfields:
                flush_cluster()
                i += 1
                sub_lines = []
                while i < len(lines):
                    s = lines[i].strip()
                    if not s:
                        i += 1
                        break
                    if re.match(r"^\d+\.\s+", s) and len(s) < 120:
                        break
                    sub_lines.append(s)
                    i += 1
                html_parts.append('<div class="idea-card">')
                html_parts.append(f'<div class="idea-card__title">{esc(title)}</div>')
                html_parts.append(f'<span class="idea-card__format">#{num}</span>')
                if sub_lines:
                    html_parts.append(f'<div class="idea-card__rationale">{inline_fmt(chr(10).join(sub_lines).replace(chr(10), "<br>"))}</div>')
                html_parts.append('</div>')
                continue

        # ── Tab-separated → table row ──
        if "\t" in stripped:
            flush_ul()
            cols = [inline_fmt(c.strip()) for c in stripped.split("\t")]
            table_buf.append(cols)
            i += 1
            continue
        else:
            flush_table()

        # ── Empty line ──
        if not stripped:
            flush_ul()
            i += 1
            continue

        # ── Horizontal rules ──
        if re.match(r"^[═─=\-]{4,}$", stripped):
            flush_ul()
            i += 1
            continue

        # ── Sub-headings ──
        if stripped.startswith("### "):
            flush_ul()
            html_parts.append(f'<h4 style="color:var(--heading);margin:16px 0 8px">{inline_fmt(stripped[4:])}</h4>')
            i += 1
            continue
        if stripped.startswith("## "):
            flush_ul()
            html_parts.append(f'<h3 style="color:var(--heading);margin:20px 0 10px">{inline_fmt(stripped[3:])}</h3>')
            i += 1
            continue

        # ── Diamond / Gold tier headers ──
        if "💎" in stripped and ("DIAMOND" in stripped.upper() or "Diamond" in stripped):
            flush_ul()
            flush_cluster()
            in_gold_section = "diamond"
            html_parts.append(f'<h3 style="color:var(--accent);margin:24px 0 12px;">{inline_fmt(stripped)}</h3>')
            i += 1
            continue
        if "🥇" in stripped and ("GOLD" in stripped.upper() or "Gold" in stripped):
            flush_ul()
            flush_cluster()
            in_gold_section = "gold"
            html_parts.append(f'<h3 style="color:var(--warn);margin:24px 0 12px;">{inline_fmt(stripped)}</h3>')
            i += 1
            continue

        # ── Batch sub-heading: "Batch N: Title" ──
        m_batch = re.match(r"^(Batch\s+\d+:.*)$", stripped)
        if m_batch:
            flush_ul()
            html_parts.append(
                f'<h4 style="color:var(--accent);margin:18px 0 8px;font-weight:700">'
                f'{inline_fmt(m_batch.group(1))}</h4>')
            i += 1
            continue

        # ── Questions label lines (e.g., "Questions About the Case") ──
        m_q_header = re.match(r"^(Questions\s+.+)$", stripped)
        if m_q_header and len(stripped) < 60:
            flush_ul()
            html_parts.append(f'<h4 style="color:var(--primary-light);margin:16px 0 8px">{inline_fmt(stripped)}</h4>')
            i += 1
            continue

        # ── Reply Strategy headers ──
        m_strategy = re.match(r"^(Reply Decision Framework|Pre-Written Reply Scripts|Summary Table:.*)$", stripped)
        if m_strategy:
            flush_ul()
            html_parts.append(f'<h4 style="color:var(--primary-light);margin:16px 0 8px;letter-spacing:0.06em">{inline_fmt(stripped)}</h4>')
            i += 1
            continue

        # ── What could push / reduce sections ──
        if re.match(r"^What could (push|reduce)", stripped):
            flush_ul()
            html_parts.append(f'<h4 style="color:var(--warn);margin:16px 0 8px">{inline_fmt(stripped)}</h4>')
            i += 1
            continue

        # ── ALL CAPS label lines ──
        if (re.match(r"^[A-Z][A-Z\s\u2014\u2013:&\-/\(\)]+$", stripped)
                and len(stripped) < 60 and "\t" not in stripped
                and stripped not in ("YES", "NO", "MEDIUM", "HIGH", "LOW")):
            flush_ul()
            html_parts.append(
                f'<h4 style="color:var(--primary-light);margin:16px 0 8px;letter-spacing:0.06em">'
                f'{inline_fmt(stripped)}</h4>')
            i += 1
            continue

        # ── "Representative quotes" / "Representative quote:" → sub-heading ──
        if stripped.lower().startswith("representative quote"):
            flush_ul()
            html_parts.append(f'<h4 style="color:var(--accent);margin:12px 0 6px;font-size:0.88rem">{inline_fmt(stripped)}</h4>')
            i += 1
            continue

        # ── "For the campaign:" → sub-heading ──
        if stripped.lower().startswith("for the campaign:"):
            flush_ul()
            html_parts.append(
                f'<div class="alert alert--info">'
                f'<div class="alert__title">Campaign Note</div>'
                f'<p style="font-size:0.85rem;color:var(--text)">{inline_fmt(stripped[17:].strip())}</p></div>'
            )
            i += 1
            continue

        # ── Bullets ──
        if re.match(r"^[\u2022\-\*\u2192]\s", stripped):
            if not in_ul:
                flush_table()
                html_parts.append("<ul>")
                in_ul = True
            content = inline_fmt(stripped[2:])
            html_parts.append(f"<li>{content}</li>")
            i += 1
            continue

        # ── Quoted text with attribution (inside or outside clusters) ──
        if stripped.startswith(("\u201C", '"', "\u00AB")):
            flush_ul()
            # Parse: "text" — Author (details)
            m_q = re.match(r'^[\u201C"\u00AB](.+?)[\u201D"\u00BB]?\s*[\u2014\u2013\-]+\s*(.+)$', stripped)
            if m_q:
                q_text = m_q.group(1)
                q_author = m_q.group(2)
                if in_gold_section == "diamond":
                    html_parts.append('<div class="gold-quote gold-quote--diamond">')
                    html_parts.append(f'<div class="gold-quote__text">{inline_fmt(q_text)}</div>')
                    html_parts.append(f'<div class="gold-quote__meta"><span>{inline_fmt(q_author)}</span></div>')
                    html_parts.append('</div>')
                elif in_gold_section == "gold":
                    html_parts.append('<div class="gold-quote">')
                    html_parts.append(f'<div class="gold-quote__text">{inline_fmt(q_text)}</div>')
                    html_parts.append(f'<div class="gold-quote__meta"><span>{inline_fmt(q_author)}</span></div>')
                    html_parts.append('</div>')
                else:
                    html_parts.append(f'<div class="quote">{inline_fmt(q_text)}<span class="quote__author">— {inline_fmt(q_author)}</span></div>')
            else:
                html_parts.append(f'<div class="quote">{inline_fmt(stripped)}</div>')
            i += 1
            continue

        # ── "Cross-platform consistency:" / "Strongest in:" → small detail ──
        if re.match(r"^(Cross-platform consistency|Strongest in|Present in|NEW —)", stripped):
            html_parts.append(f'<p style="font-size:0.82rem;color:var(--muted);margin:2px 0">{inline_fmt(stripped)}</p>')
            i += 1
            continue

        # ── End of report line → mandate-box ──
        if stripped.lower().startswith("end of report"):
            flush_ul()
            flush_table()
            flush_cluster()
            html_parts.append(
                '<div class="mandate-box">'
                f'<div class="mandate-box__statement">{inline_fmt(stripped)}</div>'
                '</div>'
            )
            i += 1
            continue

        # ── Normal paragraph ──
        flush_ul()
        html_parts.append(f"<p>{inline_fmt(stripped)}</p>")
        i += 1

    flush_ul()
    flush_table()
    flush_cluster()
    return "\n".join(html_parts)


def generate_html_report(
    llm_output: str,
    ctx: dict,
    comments: list[dict],
    csv_path: str,
    n_comments_hint: Optional[int] = None,
) -> str:
    """Generate a professional dark-theme HTML report from text content."""
    import re as _re

    n_comments = n_comments_hint if n_comments_hint is not None else len(comments)
    client_name = ctx.get("client_name", "")
    post_url = ctx.get("post_url", "")
    gen_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    gen_date = datetime.now().strftime("%d %B %Y")
    rel = ctx.get("client_relationship", "")

    # Extract title / subtitle from first few lines
    header_lines = llm_output.split("\n")[:6]
    report_title = "Audience Intelligence Report"
    report_subtitle = ""
    for line in header_lines:
        line = line.strip()
        if not line or _re.match(r"^[═─]{4,}$", line):
            continue
        if "AUDIENCE INTELLIGENCE" in line.upper():
            continue
        if not report_subtitle:
            report_subtitle = line  # e.g. "Truth Protects The Innocent Campaign"
        elif not _re.match(r"^Prepared:", line):
            report_title = report_subtitle
            report_subtitle = line
            break

    page_title = f"Audience Intelligence Report — {client_name}" if client_name else "Audience Intelligence Report"

    # Parse sections
    sections = _parse_report_sections(llm_output)

    # Import CSS from template module
    try:
        from report_generator.template import REPORT_CSS
    except ImportError:
        REPORT_CSS = ""

    # Build section cards
    sections_html = ""
    sec_counter = 0
    toc_items = []
    for sec in sections:
        if sec["id"] == "_header":
            continue
        sec_counter += 1
        body_html = _render_section_body(sec["body_lines"])
        if not body_html.strip():
            continue

        # Section number label
        sid = sec["id"]
        if sid.isdigit():
            num_label = f"Section {int(sid):02d}"
        else:
            num_label = f"Section {sid}"

        anchor = f"sec-{sid.lower()}"
        toc_items.append((num_label, sec["title"], anchor))

        sections_html += (
            f'<div class="section" id="{anchor}">'
            f'<div class="section__number">{num_label}</div>'
            f'<h2 class="section__title">{sec["title"]}</h2>'
            f'<div class="section__content md">{body_html}</div>'
            f'</div>\n'
        )

    # Cover page
    cover_meta = ""
    if n_comments:
        cover_meta += (
            f'<div class="cover__meta-item">'
            f'<div class="cover__meta-label">Comments Analysed</div>'
            f'<div class="cover__meta-value">{n_comments:,}</div></div>'
        )
    cover_meta += (
        f'<div class="cover__meta-item">'
        f'<div class="cover__meta-label">Report Date</div>'
        f'<div class="cover__meta-value">{gen_date}</div></div>'
    )
    if client_name:
        cover_meta += (
            f'<div class="cover__meta-item">'
            f'<div class="cover__meta-label">Prepared For</div>'
            f'<div class="cover__meta-value">{client_name}</div></div>'
        )
    if rel:
        cover_meta += (
            f'<div class="cover__meta-item">'
            f'<div class="cover__meta-label">Relationship</div>'
            f'<div class="cover__meta-value">{rel.title()}</div></div>'
        )

    # TOC
    toc_html = ""
    if toc_items:
        toc_entries = "".join(
            f'<li class="toc__item">'
            f'<a href="#{anchor}" style="color:var(--text);text-decoration:none;display:flex;align-items:baseline;width:100%">'
            f'<span class="toc__item-title" style="flex:1">{title}</span></a></li>'
            for _num, title, anchor in toc_items
        )
        toc_html = (
            f'<div class="toc">'
            f'<h2 class="toc__title">Table of Contents</h2>'
            f'<ol class="toc__list">{toc_entries}</ol>'
            f'</div>'
        )

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{page_title}</title>
  <meta name="description" content="Audience Intelligence Report — {n_comments} comments analysed">
  <meta name="author" content="quantumtoolsmith.gumroad.com">
  <style>{REPORT_CSS}</style>
</head>
<body>

<div class="cover">
  <div class="cover__badge">Audience Intelligence Report</div>
  <h1 class="cover__title"><span>{report_title}</span></h1>
  <p class="cover__subtitle">{report_subtitle}</p>
  <div class="cover__meta">{cover_meta}</div>
  <div class="cover__footer">Quantum Merlin Ltd &middot; quantumtoolsmith.gumroad.com</div>
</div>

{toc_html}

<main style="max-width:900px;margin:0 auto;padding:20px 40px">
{sections_html}
</main>

<div class="page-footer">
  Generated by <strong>Audience Intelligence</strong> &middot;
  Quantum Merlin Ltd &middot; {gen_date}<br>
  quantumtoolsmith.gumroad.com
</div>

</body>
</html>"""


# ──────────────────────────────────────────────────────────────────────────────
# 6.  MAIN
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="LLM-powered Audience Intelligence Report from a CSV of comments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""
        Examples:
          # Guided wizard to create a context file first
          python report_agent.py --new-context

          # Run with existing context
          python report_agent.py comments.csv --context context.json

          # Run with default (no context) — analysis only
          python report_agent.py comments.csv

          # Specify output path and model
          python report_agent.py comments.csv --context ctx.json --out report.html --model gpt-4o

          # Convert a pre-written report.txt directly to HTML (no LLM needed)
          python report_agent.py --from-report report.txt
          python report_agent.py --from-report report.txt --out outputs/my_report.html
          python report_agent.py --from-report report.txt --context context.json
        """)
    )
    parser.add_argument("csv", nargs="?", help="Path to CSV file of comments")
    parser.add_argument("--context", "-c",  help="Path to context JSON file")
    parser.add_argument("--out",     "-o",  help="Output HTML path (default: auto-named in outputs/)")
    parser.add_argument("--model",          default="gpt-4o", help="OpenAI model to use (default: gpt-4o)")
    parser.add_argument("--max-comments",   type=int, default=500, help="Max comments to send to LLM (default: 500)")
    parser.add_argument("--api-key",        help="OpenAI API key (or set OPENAI_API_KEY env var)")
    parser.add_argument("--new-context",    action="store_true", help="Run the interactive context wizard")
    parser.add_argument("--save-prompt",    action="store_true", help="Save the assembled prompt to prompt_assembled.txt for inspection")
    parser.add_argument("--from-report",    metavar="TXT",
                        help="Convert a pre-written report.txt directly to HTML (skips CSV loading and LLM call)")
    args = parser.parse_args()

    # ─── wizard mode ───
    if args.new_context:
        out_ctx = args.context or "context.json"
        wizard_new_context(out_ctx)
        print(f"[OK] Context saved to {out_ctx}")
        print("     Now run: python report_agent.py <your_comments.csv> --context " + out_ctx)
        sys.exit(0)

    # ─── from-report mode: convert a pre-written report.txt → HTML ───
    if args.from_report:
        import re as _re
        report_path = args.from_report
        if not os.path.exists(report_path):
            sys.exit(f"[ERROR] Report file not found: {report_path}")

        print(f"\n[1/2] Reading report from {report_path} ...")
        with open(report_path, encoding="utf-8") as f:
            report_text = f.read()
        print(f"      {len(report_text):,} characters read.")

        # Try to extract comment count from the report header
        _m = _re.search(r"\((\d[\d,]+)\s+[Cc]omments?\)", report_text[:800])
        n_hint = int(_m.group(1).replace(",", "")) if _m else None

        if args.context and os.path.exists(args.context):
            ctx = load_context(args.context)
            print(f"      Context loaded from {args.context}")
        else:
            ctx = extract_context_from_report(report_text)
            print(f"      Context extracted from report: client='{ctx.get('client_name')}', rel={ctx.get('client_relationship')}")

        print("[2/2] Generating HTML report ...")
        html = generate_html_report(report_text, ctx, [], report_path, n_comments_hint=n_hint)

        if args.out:
            out_path = args.out
        else:
            os.makedirs("outputs", exist_ok=True)
            stem = Path(report_path).stem
            ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = f"outputs/report_{stem}_{ts}.html"

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

        print(f"\n[OK] Report saved to: {out_path}")
        print(f"     Open in your browser to view.\n")
        sys.exit(0)

    if not args.csv:
        parser.print_help()
        sys.exit(1)

    # ─── load comments ───
    csv_path = args.csv
    if not os.path.exists(csv_path):
        sys.exit(f"[ERROR] CSV file not found: {csv_path}")

    print(f"\n[1/5] Loading comments from {csv_path} ...")
    comments = load_comments_from_csv(csv_path)
    if not comments:
        sys.exit("[ERROR] No comments found in CSV. Check column names (text/comment/message).")
    print(f"      {len(comments)} comments loaded.")

    # ─── load context ───
    print("[2/5] Loading context ...")
    if args.context:
        if not os.path.exists(args.context):
            sys.exit(f"[ERROR] Context file not found: {args.context}")
        ctx = load_context(args.context)
        print(f"      Context loaded from {args.context}")
    else:
        ctx = default_context(url="")
        print("      No context file provided — using defaults (analysis-only mode).")
        print("      Tip: run 'python report_agent.py --new-context' to create one.")

    # ─── API key ───
    api_key = args.api_key or os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        sys.exit(
            "[ERROR] No OpenAI API key found.\n"
            "Set environment variable: $env:OPENAI_API_KEY = 'sk-...'\n"
            "Or pass: --api-key sk-..."
        )

    # ─── build prompt ───
    print("[3/5] Building prompt ...")
    prompt = build_prompt(ctx, comments, max_comments=args.max_comments)
    if args.save_prompt:
        with open("prompt_assembled.txt", "w", encoding="utf-8") as f:
            f.write(prompt)
        print("      Prompt saved to prompt_assembled.txt")
    n_chars = len(prompt)
    print(f"      Prompt length: {n_chars:,} characters (~{n_chars//4:,} tokens)")

    # ─── call LLM ───
    print(f"[4/5] Calling LLM ({args.model}) ...")
    llm_output = call_openai(prompt, api_key=api_key, model=args.model)
    print(f"      Response: {len(llm_output):,} characters")

    # ─── generate HTML ───
    print("[5/5] Generating HTML report ...")
    html = generate_html_report(llm_output, ctx, comments, csv_path)

    # ─── save ───
    if args.out:
        out_path = args.out
    else:
        os.makedirs("outputs", exist_ok=True)
        stem = Path(csv_path).stem
        ts   = datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = f"outputs/agent_report_{stem}_{ts}.html"

    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n[OK] Report saved to: {out_path}")
    print(f"     Open in your browser to view.\n")


if __name__ == "__main__":
    main()
