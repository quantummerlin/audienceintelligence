(function () {
  'use strict';
  if (document.getElementById('aether-footer')) return;

  /* ── STYLES ── */
  var s = document.createElement('style');
  s.textContent = [
    // Reduced margin-top from 64px → 24px so footer doesn't feel disconnected
    '#aether-footer{background:#07070f;border-top:1px solid rgba(129,140,248,0.15);padding:32px 24px 28px;margin-top:24px;font-family:"Space Grotesk",-apple-system,BlinkMacSystemFont,sans-serif;}',
    '.af-inner{max-width:780px;margin:0 auto;text-align:center;}',
    // Brand block: centred stack
    '.af-brand{margin-bottom:20px;}',
    '.af-logo{font-family:"Orbitron",sans-serif;font-size:1.1rem;font-weight:800;background:linear-gradient(135deg,#38bdf8,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;text-decoration:none;letter-spacing:.04em;display:inline-block;margin-bottom:6px;}',
    '.af-tagline{font-size:.8rem;color:rgba(148,163,184,0.7);line-height:1.55;margin:0;}',
    // BMC button: centred
    '.af-bmc-wrap{margin:18px 0 22px;display:flex;justify-content:center;}',
    '.af-bmc-btn{display:inline-flex;align-items:center;gap:8px;background:#FFDD00;color:#000;font-size:.82rem;font-weight:700;padding:10px 20px;border-radius:8px;text-decoration:none;transition:opacity .2s,transform .15s;white-space:nowrap;border:none;cursor:pointer;}',
    '.af-bmc-btn:hover{opacity:.88;transform:translateY(-1px);}',
    '.af-hr{border:none;border-top:1px solid rgba(129,140,248,0.12);margin:0 0 16px;}',
    // Bottom block: stacked & centred (copy + links)
    '.af-bottom{display:flex;flex-direction:column;align-items:center;gap:10px;}',
    '.af-copy{font-size:.76rem;color:rgba(148,163,184,0.4);margin:0;text-align:center;}',
    '.af-links{display:flex;gap:18px;flex-wrap:wrap;justify-content:center;}',
    '.af-links a{font-size:.76rem;color:rgba(148,163,184,0.55);text-decoration:none;transition:color .2s;}',
    '.af-links a:hover{color:#22d3ee;}',
  ].join('');
  document.head.appendChild(s);

  /* ── FOOTER HTML ── */
  var f = document.createElement('footer');
  f.id = 'aether-footer';
  f.innerHTML =
    '<div class="af-inner">' +
      '<div class="af-brand">' +
        '<a href="/" class="af-logo">Æther Intel</a>' +
        '<p class="af-tagline">AI signals, decoded. No paywalls. Reader-supported.</p>' +
      '</div>' +
      '<div class="af-bmc-wrap">' +
        '<a href="https://buymeacoffee.com/quantummerlin" target="_blank" rel="noopener noreferrer" class="af-bmc-btn">' +
          '<span style="font-size:1.1em;">☕</span> Buy me a coffee' +
        '</a>' +
      '</div>' +
      '<hr class="af-hr">' +
      '<div class="af-bottom">' +
        '<p class="af-copy">&copy; 2026 Æther Intel. All rights reserved.</p>' +
        '<nav class="af-links">' +
          '<a href="/privacy.html">Privacy Policy</a>' +
          '<a href="/terms.html">Terms of Service</a>' +
          '<a href="mailto:hello@ai.quantummerlin.com">Contact</a>' +
        '</nav>' +
      '</div>' +
    '</div>';
  document.body.appendChild(f);

  /* ── BUY ME A COFFEE FLOATING WIDGET ── */
  var bmc = document.createElement('script');
  bmc.setAttribute('data-name', 'BMC-Widget');
  bmc.setAttribute('data-cfasync', 'false');
  bmc.src = 'https://cdnjs.buymeacoffee.com/1.0.0/widget.prod.min.js';
  bmc.setAttribute('data-id', 'quantummerlin');
  bmc.setAttribute('data-description', 'Support Aether Intel!');
  bmc.setAttribute('data-message', 'Æther Intel is free, no ads. A coffee keeps it that way ☕');
  bmc.setAttribute('data-color', '#22d3ee');
  bmc.setAttribute('data-position', 'Right');
  bmc.setAttribute('data-x_margin', '18');
  bmc.setAttribute('data-y_margin', '18');
  document.body.appendChild(bmc);
}());
