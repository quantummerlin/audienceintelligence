import os
import re

# The new CTA messaging — explains the "one collection, many reports" model
# For reports (with back button)
NEW_CTA_REPORT = '''        <!-- CTA Section -->
        <section class="cta-section">
            <div class="cta-proof">
                <span class="cta-proof-label">📊 22 free reports</span>
                <span class="cta-proof-sep">·</span>
                <span class="cta-proof-label">1 intelligence collection</span>
            </div>
            <h3 class="cta-title">Want this done for your topic?</h3>
            <p class="cta-text">Every report on this site — all 22 of them — came from a single deep-dive intelligence collection. One dataset. Dozens of angles. For $69, I'll run the same process on your niche, product, or audience and hand you the raw signal.</p>
            <a href="mailto:signup@quantummerlin.com?subject=Custom%20Report%20Request" class="btn btn-primary">Commission a Custom Collection — $69</a>
            <a href="../index.html" class="btn btn-secondary">Back to All Reports</a>
        </section>'''

# For index.html (no back button, slightly different framing)
NEW_CTA_INDEX = '''        <section class="cta-section" id="custom">
            <div class="cta-proof">
                <span class="cta-proof-label">📊 22 free reports</span>
                <span class="cta-proof-sep">·</span>
                <span class="cta-proof-label">1 intelligence collection</span>
            </div>
            <h3 class="cta-title">Want this done for your topic?</h3>
            <p class="cta-text">Every report on this site — all 22 of them — came from a single deep-dive intelligence collection. One dataset. Dozens of angles. For $69, I'll run the same process on your niche, product, or audience and hand you the raw signal.</p>
            <a href="mailto:signup@quantummerlin.com?subject=Custom%20Report%20Request" class="btn btn-primary">Commission a Custom Collection — $69</a>
        </section>'''

# CSS to add for the proof badges (if not already present)
CTA_PROOF_CSS = '''
        .cta-proof {
            display: flex;
            align-items: center;
            gap: 0.75rem;
            justify-content: center;
            margin-bottom: 1.2rem;
        }
        .cta-proof-label {
            font-size: 0.8rem;
            font-weight: 600;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            opacity: 0.7;
        }
        .cta-proof-sep {
            opacity: 0.3;
            font-size: 1rem;
        }
'''

reports_dir = 'reports'
report_files = [f for f in os.listdir(reports_dir) if f.endswith('.html')]
report_files.sort()

updated = []
skipped = []

for fname in report_files:
    path = os.path.join(reports_dir, fname)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. Replace the CTA section — handle multiple patterns
    # Pattern A: standard .cta-section with various contents
    # We'll replace everything from <!-- CTA Section --> to </section> (the cta one)
    # Use a robust regex that catches the whole block
    
    # Try to find and replace the CTA section block
    # Match from comment or opening tag to closing </section>
    pattern = r'(?:<!-- CTA Section -->\s*\n\s*)?<section class="cta-section"[^>]*>.*?</section>'
    
    if re.search(pattern, content, re.DOTALL):
        content = re.sub(pattern, NEW_CTA_REPORT.strip(), content, flags=re.DOTALL)
    else:
        # Try alternate class patterns used in newer reports
        pattern2 = r'<section class="cta"[^>]*>.*?</section>'
        if re.search(pattern2, content, re.DOTALL):
            content = re.sub(pattern2, NEW_CTA_REPORT.strip(), content, flags=re.DOTALL)
        else:
            skipped.append(fname + ' (no CTA section found)')
            continue

    # 2. Add CSS for proof badges if not already present
    if '.cta-proof' not in content:
        # Insert before closing </style>
        content = content.replace('        /* CTA Section */', CTA_PROOF_CSS + '\n        /* CTA Section */', 1)
        # If that marker doesn't exist, try inserting before last </style>
        if '.cta-proof' not in content:
            content = content.replace('</style>', CTA_PROOF_CSS + '\n        </style>', 1)

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        updated.append(fname)
    else:
        skipped.append(fname + ' (no change)')

print(f"Updated {len(updated)} reports:")
for f in updated:
    print(f"  ✓ {f}")

if skipped:
    print(f"\nSkipped {len(skipped)}:")
    for f in skipped:
        print(f"  ✗ {f}")