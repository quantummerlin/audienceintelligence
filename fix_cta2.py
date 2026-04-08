import os
import re

# New CTA for the 7 newer reports (div-based structure)
NEW_CTA_DIV = '''<div class="cta-section">
  <div class="cta-proof-row">
    <span class="cta-proof-badge">📊 22 free reports</span>
    <span class="cta-proof-sep">·</span>
    <span class="cta-proof-badge">1 intelligence collection</span>
  </div>
  <h2>Want this done for your topic?</h2>
  <p>Every report on this site — all 22 of them — came from a single deep-dive intelligence collection. One dataset. Dozens of angles. For $69, I'll run the same process on your niche, product, or audience and hand you the raw signal.</p>
  <a href="mailto:signup@quantummerlin.com?subject=Custom%20Report%20Request" class="cta-btn">Commission a Custom Collection — $69</a>
  <div class="cta-price">One-time fee · Delivered within 48 hours · No subscription</div>
</div>'''

# CSS to inject for proof badges in newer reports
PROOF_CSS = '''
  .cta-proof-row { display: flex; align-items: center; gap: 0.75rem; justify-content: center; margin-bottom: 1.2rem; }
  .cta-proof-badge { font-size: 0.75rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; opacity: 0.65; }
  .cta-proof-sep { opacity: 0.3; }'''

reports_dir = 'reports'
newer_reports = [
    'ai-slop-vs-human.html',
    'competitor-gaps.html', 
    'gift-rejected.html',
    'pregnant-betrayal.html',
    'sponge-paradox.html',
    'ungrateful-economy.html',
    'viral-hooks-lab.html',
]

updated = []

for fname in newer_reports:
    path = os.path.join(reports_dir, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Replace the div-based cta-section
    pattern = r'<div class="cta-section">.*?</div>'
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, NEW_CTA_DIV, content, flags=re.DOTALL)
    
    # Add proof badge CSS before closing </style>
    if '.cta-proof-row' not in content:
        content = content.replace('</style>', PROOF_CSS + '\n</style>', 1)

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        updated.append(fname)
        print(f"  ✓ {fname}")
    else:
        print(f"  ✗ {fname} (no change)")

print(f"\nDone. Updated {len(updated)}/7 newer reports.")

# Now update index.html
print("\nUpdating index.html CTA...")
index_path = 'index.html'
with open(index_path, 'r', encoding='utf-8') as f:
    idx = f.read()

NEW_CTA_INDEX = '''        <section class="cta-section" id="custom">
            <div class="cta-proof">
                <span class="cta-proof-label">📊 22 free reports</span>
                <span class="cta-proof-sep">·</span>
                <span class="cta-proof-label">1 intelligence collection</span>
            </div>
            <h3 class="cta-title">Want this done for your topic?</h3>
            <p class="cta-text">Every report on this site — all 22 of them — came from a single deep-dive intelligence collection. One dataset. Dozens of angles. For $69, I\'ll run the same process on your niche, product, or audience and hand you the raw signal.</p>
            <a href="mailto:signup@quantummerlin.com?subject=Custom%20Report%20Request" class="btn btn-primary">Commission a Custom Collection — $69</a>
        </section>'''

pattern_idx = r'<section class="cta-section" id="custom">.*?</section>'
if re.search(pattern_idx, idx, re.DOTALL):
    idx = re.sub(pattern_idx, NEW_CTA_INDEX, idx, flags=re.DOTALL)
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(idx)
    print("  ✓ index.html updated")
else:
    print("  ✗ index.html CTA pattern not found")