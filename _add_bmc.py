import os

BMC_CSS = """
        /* Buy Me a Coffee float */
        .bmc-float {
            position: fixed; bottom: 24px; right: 24px; z-index: 999;
            display: flex; align-items: center; gap: 10px;
            background: #FFDD00; color: #000;
            padding: 11px 20px 11px 14px;
            border-radius: 50px;
            text-decoration: none; font-weight: 700; font-size: 0.88rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.35);
            transition: transform .2s, box-shadow .2s;
            font-family: inherit;
        }
        .bmc-float:hover { transform: translateY(-3px); box-shadow: 0 8px 28px rgba(0,0,0,0.45); }
        .bmc-float-icon { font-size: 1.15rem; line-height: 1; }
        @media(max-width: 480px) {
            .bmc-float { padding: 11px 14px; bottom: 16px; right: 16px; }
            .bmc-float-text { display: none; }
        }"""

BMC_HTML = (
    '\n    <!-- Buy Me a Coffee floating button -->\n'
    '    <a href="https://buymeacoffee.com/quantummerlin" target="_blank" rel="noopener" class="bmc-float" aria-label="Buy Me a Coffee">\n'
    '        <span class="bmc-float-icon">&#x2615;</span>\n'
    '        <span class="bmc-float-text">Buy me a coffee</span>\n'
    '    </a>'
)

files = [
    'about.html',
    'methodology.html',
    'patterns.html',
    'reports/openclaw.html',
    'reports/passive-income.html',
    'reports/surveillance-state.html',
    'reports/vibe-coding-crisis.html',
    'reports/quantum-manifestation.html',
]

count = 0
for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'bmc-float' in content:
        print('  skip (already has it): ' + path)
        continue
    content = content.replace('</style>', BMC_CSS + '\n    </style>', 1)
    content = content.replace('</body>', BMC_HTML + '\n</body>', 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    count += 1
    print('  updated: ' + path)

print('Done - ' + str(count) + ' files updated')
