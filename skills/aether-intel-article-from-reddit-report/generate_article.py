#!/usr/bin/env python3
"""
Aether Intel: Reddit Intelligence Report → Article Generator
Converts pre-extracted Reddit intelligence reports (openclaw.txt / maki_extracted.txt format)
into complete, publish-ready Aether Intel article HTML pages with auto-commit to GitHub.

Usage:
  python3 generate_article.py --report /path/to/report.txt --slug 24-openclaw-security-risks \
    --category "AI Agents" --badge badge-agents \
    [--focus "security and cost"] [--dry-run] [--article-num 24]

Credentials (injected via RunWithCredentials):
  OPENROUTER_API_KEY  — OpenRouter API key
  GITHUB_TOKEN        — GitHub personal access token with repo write access
"""

import argparse
import base64
import json
import os
import re
import sys
import urllib.request
import urllib.error
from datetime import datetime

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_MODEL = "claude-sonnet-4-5"  # Claude Sonnet 4.6 / claude-sonnet-4-5

GITHUB_API = "https://api.github.com"
GITHUB_OWNER = "quantummerlin"
GITHUB_REPO = "audienceintelligence"
GITHUB_BRANCH = "main"

SITE_BASE_URL = "https://ai.quantummerlin.com"
AUTHOR = "Quantum Merlin"
TODAY = datetime.now().strftime("%Y-%m-%d")
TODAY_LONG = datetime.now().strftime("%B %-d, %Y")

VALID_BADGES = [
    "badge-agents", "badge-tools", "badge-business",
    "badge-automation", "badge-secondary"
]

# ---------------------------------------------------------------------------
# PARSE REPORT
# ---------------------------------------------------------------------------

def parse_intelligence_report(filepath: str) -> dict:
    """
    Parse a Reddit intelligence report in either the openclaw.txt or maki_extracted.txt format.
    Returns a structured dict: {header, source, executive_summary, pain_points, product_ideas}
    """
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    result = {
        "header": "",
        "source": os.path.basename(filepath),
        "comments_analysed": "",
        "executive_summary": "",
        "pain_points": [],
        "product_ideas": [],
        "raw": raw[:2000],  # first 2000 chars for context
    }

    lines = raw.splitlines()

    # Extract header/meta line (first non-empty line)
    for line in lines[:10]:
        stripped = line.strip()
        if stripped:
            result["header"] = stripped
            break

    # Comments analysed
    m = re.search(r'([\d,]+)\s+comments?\s+anal[yz]', raw, re.IGNORECASE)
    if m:
        result["comments_analysed"] = m.group(1)

    # --- Executive Summary ---
    exec_match = re.search(
        r'(?:##?\s*)?Executive Summary\s*\n(.*?)(?=\n##?\s*Pain Points|\n---|\Z)',
        raw, re.DOTALL | re.IGNORECASE
    )
    if exec_match:
        result["executive_summary"] = exec_match.group(1).strip()

    # --- Pain Points ---
    # Match numbered pain point blocks
    # Handles "### 1. Title\n**Frequency..." and "### 1. Long title\nFrequency..."
    pain_section_match = re.search(
        r'##?\s*Pain Points\s*\n(.*?)(?=##?\s*Product Ideas|\Z)',
        raw, re.DOTALL | re.IGNORECASE
    )
    if pain_section_match:
        pain_section = pain_section_match.group(1)

        # Split on numbered headers
        entries = re.split(r'\n###?\s*\d+[\.\)]\s+', pain_section)
        for entry in entries[1:]:  # skip first empty chunk
            lines_e = entry.strip().splitlines()
            if not lines_e:
                continue
            title = lines_e[0].strip().rstrip('*').strip()

            # Frequency line
            freq = ""
            freq_m = re.search(
                r'Frequency[^:]*:?\s*[*_]*(.*?)[*_]*\n', entry, re.IGNORECASE
            )
            if freq_m:
                freq = freq_m.group(1).strip()

            # What it is
            what = ""
            what_m = re.search(
                r'What it is:?\s*[*_]*(.*?)(?=\n\n|\nEvidence|\nWhy|\Z)',
                entry, re.DOTALL | re.IGNORECASE
            )
            if what_m:
                what = what_m.group(1).strip().replace("\n", " ")

            # Evidence quotes
            quotes = re.findall(r'>\s*"?(.*?)"?\s*\n', entry)
            # Also try blockquote style
            if not quotes:
                quotes = re.findall(r'>\s*(.*?)\n', entry)

            # Why it matters
            why = ""
            why_m = re.search(
                r'Why it matters:?\s*[*_]*(.*?)(?=\n---|\n###|\Z)',
                entry, re.DOTALL | re.IGNORECASE
            )
            if why_m:
                why = why_m.group(1).strip().replace("\n", " ")

            result["pain_points"].append({
                "title": title,
                "frequency": freq,
                "what": what,
                "quotes": quotes[:2],  # max 2 quotes per pain point
                "why": why,
            })

    # --- Product Ideas (optional section) ---
    ideas_match = re.search(
        r'##?\s*Product Ideas?\s*\n(.*?)(?=\n##|\Z)',
        raw, re.DOTALL | re.IGNORECASE
    )
    if ideas_match:
        ideas_raw = ideas_match.group(1)
        ideas = re.findall(r'[-•*]\s*(.*?)\n', ideas_raw)
        result["product_ideas"] = [i.strip() for i in ideas if i.strip()][:6]

    return result


# ---------------------------------------------------------------------------
# GENERATE ARTICLE VIA OPENROUTER
# ---------------------------------------------------------------------------

ARTICLE_SYSTEM_PROMPT = """You are a senior tech journalist and AI analyst writing for Aether Intel —
an authoritative AI news and intelligence site. Your writing is direct, analytical, and grounded in
real evidence from the community. You turn raw intelligence data into compelling, insightful articles
that help AI builders, operators, and enthusiasts understand what matters and why.

Your style:
- Lead with the most important insight, not background
- Use real quotes from the data as powerful section anchors
- Write in confident, active prose — no hedging, no fluff
- Each section should add new insight, not repeat what came before
- Practical: readers should leave knowing something actionable

Output format: JSON object with these exact keys:
{
  "title": "Article headline (max 80 chars, punchy and specific)",
  "meta_description": "SEO meta description 140-160 chars",
  "og_title": "Social share title (can differ slightly from title)",
  "read_time": "X min read",
  "intro": "2-3 paragraph hook/intro in HTML (use <p> tags)",
  "sections": [
    {
      "heading": "Section heading",
      "body": "Section body in HTML (use <p>, <ul>, <li>, <strong>, <em>, blockquote with class article-quote)"
    }
  ],
  "conclusion": "1-2 paragraph conclusion/takeaway in HTML (use <p> tags)",
  "key_takeaways": ["Takeaway 1", "Takeaway 2", "Takeaway 3"]
}

For blockquotes use: <blockquote class="article-quote"><p>"quote text"</p></blockquote>
For section subheadings use: <h3 class="article-h3">text</h3>
For bullet lists use: <ul><li>item</li></ul>
For numbered lists use: <ol><li>item</li></ol>
Return ONLY valid JSON. No markdown fences, no preamble."""


def generate_article_with_claude(report: dict, category: str, focus: str, api_key: str) -> dict:
    """
    Send parsed report data to Claude Sonnet via OpenRouter and get back structured article JSON.
    """
    pain_points_text = ""
    for i, pp in enumerate(report["pain_points"], 1):
        pain_points_text += f"\n{i}. {pp['title']}\n"
        if pp["frequency"]:
            pain_points_text += f"   Frequency: {pp['frequency']}\n"
        if pp["what"]:
            pain_points_text += f"   What: {pp['what']}\n"
        if pp["quotes"]:
            for q in pp["quotes"]:
                pain_points_text += f'   Quote: "{q}"\n'
        if pp["why"]:
            pain_points_text += f"   Why it matters: {pp['why']}\n"

    ideas_text = ""
    if report["product_ideas"]:
        ideas_text = "\n\nProduct/Solution Ideas from the data:\n"
        for idea in report["product_ideas"]:
            ideas_text += f"- {idea}\n"

    user_prompt = f"""Convert this Reddit intelligence report into a compelling Aether Intel article.

Category: {category}
Focus angle: {focus if focus else "the most impactful insights for AI builders and operators"}
Comments analysed: {report['comments_analysed']}
Source: {report['source']}

EXECUTIVE SUMMARY:
{report['executive_summary'][:1500]}

TOP PAIN POINTS (evidence-backed):
{pain_points_text[:3000]}
{ideas_text}

Write a long-form article (aim for 800-1200 words of body content) that turns these raw insights into
actionable intelligence. Use the real quotes from the data as evidence. The article should feel
authoritative — like the analyst read 7,000+ comments so your reader doesn't have to.

Create 4-6 content sections. Make each one earn its place with distinct insight.
Return the structured JSON as specified."""

    payload = json.dumps({
        "model": ANTHROPIC_MODEL,
        "max_tokens": 4096,
        "system": ARTICLE_SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": user_prompt}
        ],
    }).encode("utf-8")

    req = urllib.request.Request(
        ANTHROPIC_API_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"OpenRouter API error {e.code}: {body}")

    response = json.loads(raw)
    content = response["content"][0]["text"].strip()

    # Strip markdown code fences if present
    content = re.sub(r'^```(?:json)?\s*', '', content)
    content = re.sub(r'\s*```$', '', content)

    try:
        article = json.loads(content)
    except json.JSONDecodeError as e:
        # Try to extract JSON from the response
        m = re.search(r'\{.*\}', content, re.DOTALL)
        if m:
            article = json.loads(m.group(0))
        else:
            raise RuntimeError(f"Could not parse JSON from Claude response: {e}\n\nRaw: {content[:500]}")

    return article


# ---------------------------------------------------------------------------
# BUILD HTML
# ---------------------------------------------------------------------------

def build_article_html(article: dict, slug: str, article_num: int, badge: str, category: str) -> str:
    """
    Assemble the complete Aether Intel article HTML page.
    """
    title = article["title"]
    meta_desc = article.get("meta_description", title)
    og_title = article.get("og_title", title)
    read_time = article.get("read_time", "8 min read")
    intro_html = article.get("intro", "<p>Article content.</p>")
    sections = article.get("sections", [])
    conclusion_html = article.get("conclusion", "")
    takeaways = article.get("key_takeaways", [])

    sections_html = ""
    for sec in sections:
        heading = sec.get("heading", "")
        body = sec.get("body", "")
        sections_html += f"""
        <h2 class="article-h2">{heading}</h2>
        {body}

        <hr class="article-divider">
        """

    takeaways_html = ""
    if takeaways:
        items = "\n          ".join(f"<li>{t}</li>" for t in takeaways)
        takeaways_html = f"""
        <div class="article-takeaways">
          <h3 class="article-h3">Key Takeaways</h3>
          <ul>
          {items}
          </ul>
        </div>"""

    canonical = f"{SITE_BASE_URL}/articles/{slug}.html"
    hero_img = f"/images/articles/{slug}-hero.png"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} – Aether Intel</title>
  <meta name="description" content="{meta_desc}">
  <meta name="robots" content="index, follow">
  <link rel="canonical" href="{canonical}">
  <!-- OG tags -->
  <meta property="og:title" content="{og_title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:type" content="article">
  <meta property="og:url" content="{canonical}">
  <meta property="og:image" content="{SITE_BASE_URL}{hero_img}">
  <meta property="article:published_time" content="{TODAY}">
  <meta property="article:author" content="{AUTHOR}">
  <!-- Twitter/X card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{og_title}">
  <meta name="twitter:description" content="{meta_desc}">
  <meta name="twitter:image" content="{SITE_BASE_URL}{hero_img}">
  <script async src="https://www.googletagmanager.com/gtag/js?id=G-VW4LGE7L1T"></script>
  <script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','G-VW4LGE7L1T');</script>
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-3480541530392777" crossorigin="anonymous"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Sora:wght@400;600;700;800&family=Space+Grotesk:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="/css/style.css">
</head>
<body>
<main>
  <article class="article-page">

    <!-- HERO -->
    <div class="article-hero">
      <div class="article-hero-img-wrap">
        <img src="{hero_img}" alt="{title}" class="article-hero-img" loading="eager" onerror="this.style.background='linear-gradient(135deg,rgba(129,140,248,0.15),rgba(34,211,238,0.05))';this.removeAttribute('src')">
      </div>
      <div class="article-hero-overlay">
        <div class="article-hero-content">
          <nav class="article-breadcrumb">
            <a href="/">Home</a>
            <span>&#x203a;</span>
            <a href="/articles.html">Articles</a>
            <span>&#x203a;</span>
            <span>{title}</span>
          </nav>
          <span class="badge {badge}">{category}</span>
          <h1 class="article-hero-title">{title}</h1>
          <div class="article-meta">
            <span class="article-meta-date">{TODAY_LONG}</span>
            <span class="article-meta-dot">&middot;</span>
            <span class="article-meta-read">{read_time}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- BODY -->
    <div class="article-layout">
      <div class="article-body">

        {intro_html}

        <hr class="article-divider">

        {sections_html}

        {conclusion_html}

        {takeaways_html}

      </div>
    </div>

    <!-- AD STRIP -->
    <div class="ad-strip">
      <ins class="adsbygoogle" style="display:block" data-ad-client="ca-pub-3480541530392777" data-ad-slot="auto" data-ad-format="auto" data-full-width-responsive="true"></ins>
      <script>(adsbygoogle=window.adsbygoogle||[]).push({{}});</script>
    </div>

  </article>
</main>
<script src="/js/main.js"></script>
<script src="/js/byok.js"></script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# GITHUB COMMIT
# ---------------------------------------------------------------------------

def get_github_file_sha(path: str, token: str):
    """Get the current SHA of a file (needed for updates). Returns None if file doesn't exist."""
    url = f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}?ref={GITHUB_BRANCH}"
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("sha")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def commit_to_github(html_content: str, slug: str, title: str, token: str) -> str:
    """
    Commit the article HTML to GitHub. Returns the commit URL.
    """
    path = f"articles/{slug}.html"
    encoded = base64.b64encode(html_content.encode("utf-8")).decode("utf-8")

    # Check if file exists (need SHA for updates)
    sha = get_github_file_sha(path, token)

    payload = {
        "message": f"feat: add article {slug}\n\nGenerated from Reddit intelligence report via Aether Intel article generator",
        "content": encoded,
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha
        payload["message"] = f"feat: update article {slug}"

    data = json.dumps(payload).encode("utf-8")
    url = f"{GITHUB_API}/repos/{GITHUB_OWNER}/{GITHUB_REPO}/contents/{path}"
    req = urllib.request.Request(
        url,
        data=data,
        method="PUT",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "Content-Type": "application/json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            commit_url = result.get("commit", {}).get("html_url", "committed")
            return commit_url
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"GitHub API error {e.code}: {body}")


# ---------------------------------------------------------------------------
# SAVE OUTPUT LOCALLY
# ---------------------------------------------------------------------------

def save_locally(html_content: str, slug: str) -> str:
    """Save the HTML to the workspace articles directory."""
    output_path = f"/agent/workspace/articles/{slug}.html"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output_path


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Convert Reddit intelligence report into Aether Intel article HTML"
    )
    parser.add_argument("--report", required=True, help="Path to intelligence report .txt file")
    parser.add_argument("--slug", required=True,
                        help="Article slug e.g. 24-openclaw-security-risks (no .html)")
    parser.add_argument("--category", default="AI Intelligence",
                        help="Article category label shown in badge")
    parser.add_argument("--badge", default="badge-agents",
                        choices=VALID_BADGES,
                        help="CSS badge class for category")
    parser.add_argument("--focus", default="",
                        help="Optional: specific angle to focus the article on")
    parser.add_argument("--article-num", type=int, default=0,
                        help="Article number for reference (optional)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Generate HTML locally without committing to GitHub")
    parser.add_argument("--no-commit", action="store_true",
                        help="Save locally and skip GitHub commit")

    args = parser.parse_args()

    # Validate slug
    if not re.match(r'^[\d]+-[a-z0-9-]+$', args.slug):
        print(f"ERROR: Slug must be format '24-some-slug' (lowercase, hyphens only). Got: {args.slug}")
        sys.exit(1)

    # Get article number from slug if not provided
    article_num = args.article_num
    if not article_num:
        m = re.match(r'^(\d+)-', args.slug)
        if m:
            article_num = int(m.group(1))

    print(f"[1/4] Parsing report: {args.report}")
    try:
        report = parse_intelligence_report(args.report)
    except FileNotFoundError:
        print(f"ERROR: Report file not found: {args.report}")
        sys.exit(1)

    print(f"      Source: {report['source']}")
    print(f"      Comments analysed: {report['comments_analysed']}")
    print(f"      Pain points found: {len(report['pain_points'])}")
    print(f"      Product ideas found: {len(report['product_ideas'])}")

    if not report["executive_summary"] and not report["pain_points"]:
        print("ERROR: Could not parse executive summary or pain points from report.")
        print("       Please check the report format matches openclaw.txt or maki_extracted.txt")
        sys.exit(1)

    print(f"\n[2/4] Generating article with Claude Sonnet via OpenRouter...")

    if args.dry_run:
        print("      DRY RUN — skipping API call, using stub article data")
        article = {
            "title": f"[DRY RUN] Article from {report['source']}",
            "meta_description": "Dry run article generation test.",
            "og_title": "[DRY RUN] Test Article",
            "read_time": "8 min read",
            "intro": "<p>This is a dry run. No API call was made.</p>",
            "sections": [
                {
                    "heading": "Dry Run Section",
                    "body": "<p>In production this would contain full article body from Claude.</p>"
                }
            ],
            "conclusion": "<p>End of dry run test.</p>",
            "key_takeaways": ["Dry run completed", "Parser is working", "Template renders correctly"]
        }
    else:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if not api_key:
            print("ERROR: ANTHROPIC_API_KEY environment variable not set.")
            sys.exit(1)

        try:
            article = generate_article_with_claude(report, args.category, args.focus, api_key)
        except Exception as e:
            print(f"ERROR: Article generation failed: {e}")
            sys.exit(1)

    print(f"      Title: {article.get('title', '(no title)')}")
    print(f"      Sections: {len(article.get('sections', []))}")

    print(f"\n[3/4] Building HTML...")
    html = build_article_html(article, args.slug, article_num, args.badge, args.category)
    print(f"      HTML length: {len(html):,} chars")

    # Always save locally
    local_path = save_locally(html, args.slug)
    print(f"      Saved locally: {local_path}")

    if args.dry_run or args.no_commit:
        print(f"\n[4/4] Skipping GitHub commit (--dry-run / --no-commit).")
        print(f"\n✓ Done. Review at: {local_path}")
        return

    print(f"\n[4/4] Committing to GitHub...")
    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        print("ERROR: GITHUB_TOKEN environment variable not set.")
        print(f"       Article saved locally at: {local_path}")
        sys.exit(1)

    try:
        commit_url = commit_to_github(html, args.slug, article.get("title", args.slug), token)
        print(f"      Committed: {commit_url}")
    except Exception as e:
        print(f"ERROR: GitHub commit failed: {e}")
        print(f"       Article saved locally at: {local_path}")
        sys.exit(1)

    print(f"\n✓ Article live at: {SITE_BASE_URL}/articles/{args.slug}.html")
    print(f"  Local copy: {local_path}")
    print(f"  Commit: {commit_url}")


if __name__ == "__main__":
    main()
