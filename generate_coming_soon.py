"""
Generates proper "coming soon" preview pages for all stub report files,
reading title/excerpt/stats from the homepage card data.
"""
import re, os

# Read homepage to extract all report card data
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Parse report cards: extract slug, number, category, title, excerpt, stats
card_pattern = re.compile(
    r'<a href="reports/([^"]+)"\s+class="report-card[^"]*">.*?'
    r'<span class="report-number">(.*?)</span>.*?'
    r'(?:<span>[^<]*</span>\s*<span>\W*</span>\s*<span>([^<]*)</span>)?.*?'
    r'<h2 class="report-title">(.*?)</h2>.*?'
    r'<p class="report-excerpt">(.*?)</p>',
    re.DOTALL
)

cards = []
for m in card_pattern.finditer(html):
    slug = m.group(1)
    number = m.group(2).strip()
    category = (m.group(3) or '').strip()
    title = re.sub(r'<[^>]+>', '', m.group(4)).replace('<br>', ' ').strip()
    excerpt = re.sub(r'<[^>]+>', '', m.group(5)).strip()
    path = f'reports/{slug}'
    size = os.path.getsize(path) if os.path.exists(path) else -1
    is_stub = size <= 3
    cards.append({'slug': slug, 'number': number, 'category': category,
                  'title': title, 'excerpt': excerpt, 'is_stub': is_stub})

print(f'Found {len(cards)} cards, {sum(1 for c in cards if c["is_stub"])} stubs')

COMING_SOON_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Aether Intelligence</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {{ margin:0; padding:0; box-sizing:border-box; }}
        :root {{
            --bg-primary: #0a0a0f; --bg-secondary: #12121a; --bg-card: #1a1a25;
            --text-primary: #f0f0f5; --text-secondary: #8888a0;
            --accent: #6366f1; --warning: #f59e0b;
        }}
        body {{ font-family:'Inter',-apple-system,sans-serif; background:var(--bg-primary); color:var(--text-primary); line-height:1.7; min-height:100vh; }}
        .bg-gradient {{
            position:fixed; top:0; left:0; right:0; bottom:0;
            background: radial-gradient(ellipse at 20% 20%, rgba(99,102,241,0.08) 0%, transparent 50%),
                        radial-gradient(ellipse at 80% 80%, rgba(139,92,246,0.06) 0%, transparent 50%);
            pointer-events:none; z-index:0;
        }}
        .container {{ max-width:900px; margin:0 auto; padding:0 24px; position:relative; z-index:1; }}
        header {{ padding:20px 0; display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid rgba(255,255,255,0.05); }}
        .logo {{ font-size:1.1rem; font-weight:600; letter-spacing:-0.02em; color:var(--text-primary); display:flex; align-items:center; gap:10px; text-decoration:none; }}
        .logo-icon {{ width:32px; height:32px; border-radius:6px; object-fit:cover; }}
        nav a {{ color:var(--text-secondary); text-decoration:none; font-size:0.9rem; margin-left:32px; transition:color .2s; }}
        nav a:hover {{ color:var(--text-primary); }}
        .hero {{ padding:80px 0 60px; text-align:center; }}
        .report-tag {{
            display:inline-block; padding:6px 14px;
            background:rgba(99,102,241,0.1); border:1px solid rgba(99,102,241,0.2);
            border-radius:20px; font-size:0.8rem; color:var(--accent);
            margin-bottom:20px; letter-spacing:0.05em; text-transform:uppercase;
        }}
        .soon-badge {{
            display:inline-block; padding:6px 14px; margin-left:8px;
            background:rgba(245,158,11,0.12); border:1px solid rgba(245,158,11,0.2);
            border-radius:20px; font-size:0.8rem; color:var(--warning);
            letter-spacing:0.05em; text-transform:uppercase;
        }}
        h1 {{
            font-size:2.2rem; font-weight:600; line-height:1.2; letter-spacing:-0.02em; margin-bottom:20px;
            background:linear-gradient(180deg,#ffffff 0%,#a0a0b0 100%);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text;
        }}
        .hero-intro {{ font-size:1.05rem; color:var(--text-secondary); max-width:640px; margin:0 auto 40px; }}
        .preview-card {{
            background:var(--bg-card); border:1px solid rgba(255,255,255,0.06);
            border-radius:16px; padding:32px; margin:0 auto 40px; max-width:640px; text-align:left;
        }}
        .preview-title {{ font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; color:var(--text-secondary); margin-bottom:12px; }}
        .preview-card p {{ color:var(--text-secondary); font-size:0.95rem; line-height:1.75; }}
        .preview-topics {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:20px; }}
        .topic-pill {{
            padding:5px 12px; background:rgba(99,102,241,0.08); border:1px solid rgba(99,102,241,0.15);
            border-radius:20px; font-size:0.78rem; color:var(--accent);
        }}
        .notify-box {{
            background:linear-gradient(135deg,rgba(99,102,241,0.1),rgba(139,92,246,0.07));
            border:1px solid rgba(99,102,241,0.2); border-radius:20px;
            padding:36px; text-align:center; max-width:540px; margin:0 auto 60px;
        }}
        .notify-box h2 {{ font-size:1.4rem; margin-bottom:10px; }}
        .notify-box p {{ color:var(--text-secondary); font-size:0.92rem; margin-bottom:24px; }}
        .notify-form {{ display:flex; gap:10px; }}
        .notify-form input {{
            flex:1; padding:12px 16px; background:rgba(255,255,255,0.06);
            border:1px solid rgba(255,255,255,0.1); border-radius:10px;
            color:var(--text-primary); font-family:inherit; font-size:0.88rem;
        }}
        .notify-form input::placeholder {{ color:var(--text-secondary); }}
        .notify-form input:focus {{ outline:none; border-color:rgba(99,102,241,0.4); }}
        .notify-form button {{
            padding:12px 24px; background:var(--accent); color:white;
            border:none; border-radius:10px; font-family:inherit; font-size:0.88rem;
            font-weight:600; cursor:pointer; white-space:nowrap; transition:all .2s;
        }}
        .notify-form button:hover {{ background:#4f46e5; }}
        .back-link {{ text-align:center; padding-bottom:40px; }}
        .back-link a {{ color:var(--text-secondary); text-decoration:none; font-size:0.88rem; }}
        .back-link a:hover {{ color:var(--text-primary); }}
        @media(max-width:600px) {{ h1{{font-size:1.7rem;}} .notify-form{{flex-direction:column;}} nav{{display:none;}} }}
    </style>
</head>
<body>
    <div class="bg-gradient"></div>
    <div class="container">
        <header>
            <a href="../index.html" class="logo">
                <img src="../logo.png" alt="Aether Intelligence" class="logo-icon">
                Aether Intelligence
            </a>
            <nav>
                <a href="../index.html#reports">Reports</a>
                <a href="../articles/">Articles</a>
                <a href="../index.html#custom">Custom</a>
            </nav>
        </header>

        <section class="hero">
            <div>
                <span class="report-tag">{number} &bull; {category}</span>
                <span class="soon-badge">Coming Soon</span>
            </div>
            <h1>{title}</h1>
            <p class="hero-intro">{excerpt}</p>
        </section>

        <div class="preview-card">
            <div class="preview-title">What this report will cover</div>
            <p>{preview_desc}</p>
            <div class="preview-topics">
                {topic_pills}
            </div>
        </div>

        <div class="notify-box">
            <h2>Get notified when this drops</h2>
            <p>Join the list and get the full analysis delivered to your inbox the moment it's published.</p>
            <form class="notify-form" onsubmit="handleNotify(event)">
                <input type="email" placeholder="your@email.com" required>
                <button type="submit">Notify Me</button>
            </form>
        </div>

        <div class="back-link">
            <a href="../index.html#reports">← Browse all reports</a>
        </div>
    </div>
    <script>
    function handleNotify(e) {{
        e.preventDefault();
        var btn = e.target.querySelector('button');
        btn.textContent = '✓ You\'re on the list';
        btn.style.background = '#10b981';
        e.target.querySelector('input').disabled = true;
        btn.disabled = true;
    }}
    </script>
</body>
</html>'''

# Metadata for each stub: slug -> (preview_desc, topics)
STUB_META = {
    'banana-that-saved-a-life.html': (
        "A deep analysis of how small, everyday triggers reveal dangerous relationship patterns. We examine the moment where a trivial argument becomes a window into controlling and abusive behaviour — and what survivors say they wish they'd recognised earlier.",
        ['Relationship Safety', 'Warning Signs', 'Abuse Patterns', 'Survivor Accounts', 'Escalation Triggers']
    ),
    'housing-lie.html': (
        "Who actually benefits from unaffordable housing? We follow the credit expansion, the corporate buying programmes, and the lobbying trail to map the structural forces keeping first-time buyers permanently locked out.",
        ['Housing Market', 'Corporate Landlords', 'Credit Expansion', 'Policy Analysis', 'First-Time Buyers']
    ),
    'billionaire-marriage-delusion.html': (
        "Online communities have a peculiar obsession with billionaire romantic lives. We analyse what the discourse reveals about society's beliefs around wealth, love, and hypergamy — and the psychological toll of aspirational fantasy.",
        ['Wealth & Relationships', 'Social Psychology', 'Aspiration Traps', 'Status & Dating']
    ),
    'goodbye-decision.html': (
        "Thousands of people discuss the moment they decided to leave — a job, a relationship, a city, a religion. This report maps the tipping points, the language people use, and what finally makes someone take irreversible action.",
        ['Decision Points', 'Life Transitions', 'Regret Analysis', 'Leaving Patterns']
    ),
    'landlord-can-see-you.html': (
        "Modern rental technology has given landlords unprecedented surveillance capabilities: smart locks, noise sensors, package tracking, and facial recognition entry. We analyse what tenants are discovering — and what they're doing about it.",
        ['Tenant Privacy', 'PropTech Surveillance', 'Renter Rights', 'Smart Home Risk']
    ),
    'bilingual-backstab.html': (
        "The experience of being spoken about in a language others assume you don't understand — at work, in relationships, with family. We map the emotional and professional damage and what communities are saying about code-switching as a form of exclusion.",
        ['Language & Power', 'Workplace Inclusion', 'Code-Switching', 'Cultural Identity']
    ),
    'you-dont-own-anything.html': (
        "Software licenses, streaming rights, subscription hardware, DRM'd ebooks — the shift from ownership to access is accelerating. This report analyses the backlash: what people are actually losing and the emerging counter-movement toward ownership.",
        ['Subscription Economy', 'Digital Ownership', 'Consumer Rights', 'DRM Backlash']
    ),
    'side-hustle-trap.html': (
        "The side hustle economy promised financial freedom. Instead, we find: most side hustles earn below minimum wage once costs are factored in, gig platforms extract increasing cuts, and the emotional labour is rarely accounted for.",
        ['Gig Economy', 'Side Hustle Reality', 'Platform Economics', 'Financial Freedom Myths']
    ),
    'idea-goldmine.html': (
        "We mined online communities for the highest-signal product and business ideas hiding in plain sight — the underserved problems people mention repeatedly, the tools people are building themselves, and the gaps the market hasn't filled yet.",
        ['Product Ideas', 'Market Gaps', 'Founder Opportunities', 'Underserved Problems']
    ),
    'poor-mindset.html': (
        "Is 'poor mindset' a real psychological phenomenon or a narrative used to blame individuals for structural problems? We analyse thousands of first-person accounts to map the actual cognitive patterns associated with financial scarcity — and how they form.",
        ['Wealth Psychology', 'Scarcity Mindset', 'Financial Behaviour', 'Class & Belief']
    ),
    '5am-lie.html': (
        "The 5am productivity cult is one of the biggest myths in self-improvement culture. We trace the science, the influencer economy behind it, and what real accounts of chronobiology say about who it actually works for — and who it harms.",
        ['Productivity Myths', 'Sleep Science', 'Self-Help Culture', 'Chronobiology']
    ),
    'gift-rejected.html': (
        "Gift rejection is one of the most emotionally charged relationship experiences. We analyse the full spectrum — from well-intentioned failures to deliberate power plays — and map what the gift dynamic reveals about relationship health.",
        ['Relationship Dynamics', 'Gift Psychology', 'Social Rejection', 'Power & Giving']
    ),
    'ungrateful-economy.html': (
        "Why does society feel less reciprocal than it used to? We map the structural and psychological forces behind the perception that effort, generosity, and contribution go unrewarded — and what communities are doing in response.",
        ['Reciprocity', 'Social Contracts', 'Gratitude & Recognition', 'Community Trust']
    ),
    'sponge-paradox.html': (
        "Highly empathic people describe absorbing the emotions of everyone around them — crowds, coworkers, family — to the point of exhaustion. We analyse the spectrum from healthy empathy to emotional dysregulation and what actually helps.",
        ['Empathy & Burnout', 'Emotional Regulation', 'HSP Traits', 'Social Exhaustion']
    ),
    'ai-slop-vs-human.html': (
        "The internet is filling with AI-generated content that's technically correct but emotionally hollow. We analyse the growing backlash: what people actually miss about human-written content, and whether authenticity can be preserved.",
        ['AI Content', 'Creative Authenticity', 'Content Quality', 'Human vs AI Writing']
    ),
    'viral-hooks-lab.html': (
        "We dissected hundreds of high-performing content hooks across platforms to extract the structural patterns that drive shares, saves, and emotional response — distilled into actionable frameworks any creator can apply.",
        ['Content Strategy', 'Hook Formulas', 'Viral Mechanics', 'Emotional Triggers', 'Copywriting']
    ),
    'pregnant-betrayal.html': (
        "Pregnancy is supposed to be protected time. Instead, communities document a pattern of betrayal that disproportionately occurs during pregnancy and early parenthood. We map the emotional, financial, and relational patterns.",
        ['Relationship Betrayal', 'Pregnancy & Trust', 'Vulnerability Windows', 'Survivor Stories']
    ),
    'competitor-gaps.html': (
        "Every product category has a dominant player and a set of vocal complaints that never get addressed. We mapped the gap between what customers loudly want and what competitors refuse to build — the highest-confidence product opportunities available.",
        ['Competitive Analysis', 'Product Gaps', 'Customer Complaints', 'Market Opportunity']
    ),
    'celebrity-encounters.html': (
        "Thousands of people have shared the moment they met a famous person and what it revealed about fame, performance, and the gap between public persona and private reality. The data paints a fascinating portrait of celebrity psychology.",
        ['Fame & Reality', 'Celebrity Psychology', 'Public vs Private', 'Parasocial Relationships']
    ),
    'speakerphone-crisis.html': (
        "Why do some people insist on conducting private conversations at full volume in public? We analyse the etiquette collapse, the social power dynamics behind public speakerphone use, and what communities are doing to cope.",
        ['Social Norms', 'Public Etiquette', 'Phone Culture', 'Noise Pollution', 'Boundaries']
    ),
    'dropshippers-ruined-etsy.html': (
        "Etsy's handmade marketplace has been systematically infiltrated by mass-produced dropshippers, destroying the platform's core value proposition. We trace how it happened, who profited, and whether anything can be done.",
        ['Platform Decay', 'Etsy Economics', 'Dropshipping', 'Handmade vs Mass-Produced', 'Marketplace Trust']
    ),
    'icu-ptsd-hidden-toll.html': (
        "ICU survival comes with an invisible aftermath: PTSD, cognitive impairment, phantom pain, and a healthcare system with no protocol for long-term psychological recovery. We analyse survivor and family accounts of what happens after discharge.",
        ['Medical Trauma', 'ICU Survivor Syndrome', 'Healthcare Gaps', 'PTSD & Recovery']
    ),
    'conspiracy-family-rupture.html': (
        "Radicalization doesn't just change minds — it destroys families. We map the specific patterns in which a family member's adoption of extreme beliefs unfolds, escalates, and becomes irreconcilable, with accounts from people on both sides.",
        ['Family Estrangement', 'Radicalization Patterns', 'Belief & Relationships', 'Conspiracy & Community']
    ),
    'sobriety-journey.html': (
        "Early sobriety is widely misrepresented. We analyse first-person accounts of what the first year actually looks like — the unexpected grief, the relationship changes, the identity shifts, and the moments that almost break the streak.",
        ['Recovery & Sobriety', 'Addiction', 'Identity Change', 'Relationship Dynamics']
    ),
    'ocd-trivialization.html': (
        "OCD is one of the most trivialised mental health conditions — used casually as a synonym for tidiness. We map the impact of cultural misrepresentation on those living with actual OCD and the barriers it creates to diagnosis and treatment.",
        ['Mental Health', 'OCD Awareness', 'Stigma & Trivialisation', 'Diagnosis Barriers']
    ),
    'dating-nightmare.html': (
        "Modern dating has industrialised rejection and commodified connection. We analyse the specific experiences people describe as the most damaging — ghosting mechanics, parasocial infatuation, algorithm-driven anxiety — and what they're doing differently.",
        ['Dating Apps', 'Ghosting', 'Modern Romance', 'Algorithm & Intimacy']
    ),
    'viral-hooks-2.html': (
        "Volume 2 of our viral hooks analysis, focusing on long-form content, comment-bait patterns, narrative tension builders, and the specific emotional arcs that drive platform-native sharing behaviour across TikTok, YouTube, and Twitter/X.",
        ['Viral Content', 'Long-Form Hooks', 'Emotional Arcs', 'Platform Strategy', 'Content Creation']
    ),
    'startup-opportunities.html': (
        "We extracted the highest-signal startup ideas from hundreds of thousands of community conversations — filtering by pain intensity, willingness to pay signals, frequency of mention, and absence of existing solutions.",
        ['Startup Ideas', 'Market Validation', 'Pain-Point Mapping', 'Founder Research', 'Unmet Needs']
    ),
}

generated = 0
for card in cards:
    if not card['is_stub']:
        continue
    slug = card['slug']
    meta = STUB_META.get(slug, (
        f"A deep analysis of online conversations around this topic — mapping the pain points, emotional patterns, and underserved opportunities that the data reveals.",
        ['Community Research', 'Sentiment Analysis', 'Behaviour Patterns']
    ))
    preview_desc, topics = meta
    topic_pills = ' '.join(f'<span class="topic-pill">{t}</span>' for t in topics)
    # clean title of html tags/breaks
    clean_title = re.sub(r'<[^>]+>', ' ', card['title']).strip()
    clean_excerpt = re.sub(r'<[^>]+>', '', card['excerpt']).strip()
    page = COMING_SOON_TEMPLATE.format(
        title=clean_title,
        number=card['number'],
        category=card['category'] or 'Research',
        excerpt=clean_excerpt,
        preview_desc=preview_desc,
        topic_pills=topic_pills,
    )
    path = f'reports/{slug}'
    with open(path, 'w', encoding='utf-8') as f:
        f.write(page)
    generated += 1
    print(f'  Generated: {slug}')

print(f'\nDone — {generated} coming-soon pages written.')
