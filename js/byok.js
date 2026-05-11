/**
 * byok.js — Aether Intel BYOK (Bring Your Own Key) API Key Manager
 * Runs only on tool pages. Manages API keys via localStorage.
 * Keys are NEVER sent to any server — browser-only storage.
 */

(function () {
  'use strict';

  // ---------------------------------------------------------------------------
  // KEY STORAGE — localStorage keys
  // ---------------------------------------------------------------------------

  const KEY_MAP = {
    openai:      'byok_openai',
    anthropic:   'byok_anthropic',
    google:      'byok_google',
    openrouter:  'byok_openrouter',
    stability:   'byok_stability'
  };

  // Provider display config (label, placeholder hint)
  const PROVIDERS = [
    {
      id:          'openai',
      label:       'OpenAI',
      placeholder: 'sk-...',
      hint:        'platform.openai.com → API Keys'
    },
    {
      id:          'anthropic',
      label:       'Anthropic',
      placeholder: 'sk-ant-...',
      hint:        'console.anthropic.com → API Keys'
    },
    {
      id:          'google',
      label:       'Google AI',
      placeholder: 'AIza...',
      hint:        'aistudio.google.com → Get API Key'
    },
    {
      id:          'openrouter',
      label:       'OpenRouter',
      placeholder: 'sk-or-...',
      hint:        'openrouter.ai → Keys'
    },
    {
      id:          'stability',
      label:       'Stability AI',
      placeholder: 'sk-...',
      hint:        'platform.stability.ai → API Keys'
    }
  ];

  // ---------------------------------------------------------------------------
  // MODAL STYLES — injected inline so byok.js is self-contained
  // ---------------------------------------------------------------------------

  const BYOK_STYLES = `
    /* ── BYOK Modal Overlay ── */
    #byokModal {
      display: none;
      position: fixed;
      inset: 0;
      z-index: 10000;
      align-items: center;
      justify-content: center;
      background: rgba(2, 4, 18, 0.82);
      backdrop-filter: blur(8px);
      -webkit-backdrop-filter: blur(8px);
      padding: 16px;
    }
    #byokModal.byok-open {
      display: flex;
    }

    /* ── Modal Card ── */
    #byokModal .byok-card {
      position: relative;
      width: 100%;
      max-width: 520px;
      max-height: 90vh;
      overflow-y: auto;
      background: linear-gradient(135deg, rgba(15, 17, 40, 0.97) 0%, rgba(10, 12, 30, 0.99) 100%);
      border: 1px solid rgba(99, 102, 241, 0.25);
      border-radius: 16px;
      box-shadow:
        0 0 0 1px rgba(99, 102, 241, 0.08),
        0 24px 64px rgba(0, 0, 0, 0.7),
        0 0 40px rgba(99, 102, 241, 0.06);
      font-family: 'Space Grotesk', 'Inter', system-ui, sans-serif;
      color: #e2e8f0;
      animation: byokSlideIn 0.22s cubic-bezier(0.34, 1.56, 0.64, 1) both;
    }

    @keyframes byokSlideIn {
      from { opacity: 0; transform: translateY(20px) scale(0.97); }
      to   { opacity: 1; transform: translateY(0)    scale(1);    }
    }

    /* ── Modal Header ── */
    #byokModal .byok-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 20px 24px 16px;
      border-bottom: 1px solid rgba(99, 102, 241, 0.12);
    }
    #byokModal .byok-title {
      font-size: 1.15rem;
      font-weight: 700;
      letter-spacing: -0.01em;
      color: #f1f5f9;
    }
    #byokModal .byok-close {
      background: none;
      border: none;
      cursor: pointer;
      font-size: 1.25rem;
      color: #94a3b8;
      padding: 4px 8px;
      border-radius: 6px;
      line-height: 1;
      transition: color 0.15s, background 0.15s;
    }
    #byokModal .byok-close:hover {
      color: #f1f5f9;
      background: rgba(99, 102, 241, 0.12);
    }

    /* ── Info Notice ── */
    #byokModal .byok-notice {
      display: flex;
      align-items: flex-start;
      gap: 10px;
      margin: 16px 24px;
      padding: 12px 14px;
      background: rgba(99, 102, 241, 0.08);
      border: 1px solid rgba(99, 102, 241, 0.18);
      border-radius: 10px;
      font-size: 0.82rem;
      color: #a5b4fc;
      line-height: 1.5;
    }
    #byokModal .byok-notice-icon {
      font-size: 1rem;
      flex-shrink: 0;
      margin-top: 1px;
    }

    /* ── Key Groups ── */
    #byokModal .byok-keys {
      padding: 0 24px 8px;
      display: flex;
      flex-direction: column;
      gap: 14px;
    }
    #byokModal .byok-key-group {
      display: flex;
      flex-direction: column;
      gap: 6px;
    }
    #byokModal .byok-key-row {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 6px;
    }
    #byokModal .byok-key-label {
      font-size: 0.78rem;
      font-weight: 600;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      color: #94a3b8;
      margin-bottom: 2px;
    }
    #byokModal .byok-key-status {
      font-size: 0.75rem;
      color: #64748b;
      min-height: 16px;
      transition: color 0.2s;
    }
    #byokModal .byok-key-status.saved {
      color: #4ade80;
    }

    /* ── Input ── */
    #byokModal .byok-input {
      flex: 1;
      height: 38px;
      padding: 0 12px;
      background: rgba(2, 4, 18, 0.6);
      border: 1px solid rgba(99, 102, 241, 0.2);
      border-radius: 8px;
      color: #e2e8f0;
      font-family: 'Space Mono', 'Courier New', monospace;
      font-size: 0.82rem;
      outline: none;
      transition: border-color 0.2s, box-shadow 0.2s;
      min-width: 0;
    }
    #byokModal .byok-input::placeholder {
      color: #334155;
    }
    #byokModal .byok-input:focus {
      border-color: rgba(99, 102, 241, 0.55);
      box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
    }

    /* ── Buttons ── */
    #byokModal .byok-btn-save {
      flex-shrink: 0;
      height: 38px;
      padding: 0 14px;
      background: rgba(99, 102, 241, 0.18);
      border: 1px solid rgba(99, 102, 241, 0.35);
      border-radius: 8px;
      color: #a5b4fc;
      font-family: inherit;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      transition: background 0.18s, color 0.18s, border-color 0.18s;
      white-space: nowrap;
    }
    #byokModal .byok-btn-save:hover {
      background: rgba(99, 102, 241, 0.3);
      color: #e0e7ff;
      border-color: rgba(99, 102, 241, 0.6);
    }
    #byokModal .byok-btn-clear {
      flex-shrink: 0;
      height: 38px;
      padding: 0 12px;
      background: transparent;
      border: 1px solid rgba(248, 113, 113, 0.2);
      border-radius: 8px;
      color: #f87171;
      font-family: inherit;
      font-size: 0.78rem;
      cursor: pointer;
      transition: background 0.18s, border-color 0.18s;
      white-space: nowrap;
    }
    #byokModal .byok-btn-clear:hover {
      background: rgba(248, 113, 113, 0.08);
      border-color: rgba(248, 113, 113, 0.4);
    }

    /* ── Modal Divider ── */
    #byokModal .byok-divider {
      margin: 16px 24px;
      border: none;
      border-top: 1px solid rgba(99, 102, 241, 0.1);
    }

    /* ── Modal Footer ── */
    #byokModal .byok-footer {
      padding: 10px 24px 20px;
      font-size: 0.76rem;
      color: #475569;
      text-align: center;
      line-height: 1.5;
    }

    /* ── Responsive ── */
    @media (max-width: 540px) {
      #byokModal .byok-card {
        border-radius: 12px;
      }
      #byokModal .byok-header,
      #byokModal .byok-keys,
      #byokModal .byok-notice {
        padding-left: 16px;
        padding-right: 16px;
      }
      #byokModal .byok-notice {
        margin-left: 16px;
        margin-right: 16px;
      }
      #byokModal .byok-divider {
        margin-left: 16px;
        margin-right: 16px;
      }
      #byokModal .byok-footer {
        padding-left: 16px;
        padding-right: 16px;
      }
    }
  `;

  // ---------------------------------------------------------------------------
  // INJECT STYLES
  // ---------------------------------------------------------------------------

  function injectStyles() {
    const styleEl = document.createElement('style');
    styleEl.id = 'byok-styles';
    styleEl.textContent = BYOK_STYLES;
    document.head.appendChild(styleEl);
  }

  // ---------------------------------------------------------------------------
  // BUILD MODAL DOM
  // ---------------------------------------------------------------------------

  function buildModal() {
    if (document.getElementById('byokModal')) return; // already exists

    const modal = document.createElement('div');
    modal.id = 'byokModal';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-modal', 'true');
    modal.setAttribute('aria-labelledby', 'byokModalTitle');

    // Build key group HTML for each provider
    const keyGroupsHTML = PROVIDERS.map(function (p) {
      return [
        '<div class="byok-key-group">',
        '  <div class="byok-key-label">' + p.label + '</div>',
        '  <div class="byok-key-row">',
        '    <input',
        '      type="password"',
        '      class="byok-input"',
        '      id="byok-input-' + p.id + '"',
        '      placeholder="' + p.placeholder + '"',
        '      autocomplete="off"',
        '      spellcheck="false"',
        '    />',
        '    <button class="byok-btn-save" data-byok-save="' + p.id + '">Save</button>',
        '    <button class="byok-btn-clear" data-byok-clear="' + p.id + '">Clear</button>',
        '  </div>',
        '  <div class="byok-key-status" id="byok-status-' + p.id + '">Not set</div>',
        '</div>'
      ].join('\n');
    }).join('\n');

    modal.innerHTML = [
      '<div class="byok-card">',
      '  <div class="byok-header">',
      '    <span class="byok-title" id="byokModalTitle">🔑 Your API Keys</span>',
      '    <button class="byok-close" id="byokClose" aria-label="Close">✕</button>',
      '  </div>',
      '  <div class="byok-notice">',
      '    <span class="byok-notice-icon">🛡️</span>',
      '    <span>Keys are stored in your browser only. Never sent to our servers.</span>',
      '  </div>',
      '  <div class="byok-keys">',
      keyGroupsHTML,
      '  </div>',
      '  <hr class="byok-divider">',
      '  <div class="byok-footer">Keys stay in your browser. We never store or access them.</div>',
      '</div>'
    ].join('\n');

    document.body.appendChild(modal);

    // Close button
    document.getElementById('byokClose').addEventListener('click', closeByokModal);

    // Click outside card to close
    modal.addEventListener('click', function (e) {
      if (e.target === modal) closeByokModal();
    });

    // Escape key to close
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && modal.classList.contains('byok-open')) {
        closeByokModal();
      }
    });

    // Save buttons
    modal.querySelectorAll('[data-byok-save]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const providerId = btn.getAttribute('data-byok-save');
        const input = document.getElementById('byok-input-' + providerId);
        if (input && input.value.trim()) {
          saveKey(providerId, input.value.trim());
          input.value = '';
        }
      });
    });

    // Clear buttons
    modal.querySelectorAll('[data-byok-clear]').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const providerId = btn.getAttribute('data-byok-clear');
        clearKey(providerId);
      });
    });

    // Allow saving by pressing Enter inside any input
    modal.querySelectorAll('.byok-input').forEach(function (input) {
      input.addEventListener('keydown', function (e) {
        if (e.key !== 'Enter') return;
        const providerId = input.id.replace('byok-input-', '');
        if (input.value.trim()) {
          saveKey(providerId, input.value.trim());
          input.value = '';
        }
      });
    });
  }

  // ---------------------------------------------------------------------------
  // KEY FUNCTIONS (exposed globally)
  // ---------------------------------------------------------------------------

  /**
   * Save an API key to localStorage and refresh the status indicator.
   * @param {string} provider - Provider id (e.g. 'openai').
   * @param {string} value    - The API key value.
   */
  function saveKey(provider, value) {
    const storageKey = KEY_MAP[provider];
    if (!storageKey || !value) return;
    localStorage.setItem(storageKey, value);
    refreshStatus(provider);
    updatePageKeyStatus();
  }

  /**
   * Retrieve an API key from localStorage.
   * @param {string} provider - Provider id.
   * @returns {string|null}
   */
  function getKey(provider) {
    const storageKey = KEY_MAP[provider];
    if (!storageKey) return null;
    return localStorage.getItem(storageKey) || null;
  }

  /**
   * Remove an API key from localStorage and refresh the status indicator.
   * @param {string} provider - Provider id.
   */
  function clearKey(provider) {
    const storageKey = KEY_MAP[provider];
    if (!storageKey) return;
    localStorage.removeItem(storageKey);
    refreshStatus(provider);
    updatePageKeyStatus();
  }

  /**
   * Returns true if a key is set for the given provider.
   * @param {string} provider - Provider id.
   * @returns {boolean}
   */
  function hasKey(provider) {
    return Boolean(getKey(provider));
  }

  /**
   * Returns the first available key across all providers, or null.
   * Priority order: openai → anthropic → openrouter → google → stability.
   * @returns {string|null}
   */
  function getAnyKey() {
    const order = ['openai', 'anthropic', 'openrouter', 'google', 'stability'];
    for (var i = 0; i < order.length; i++) {
      var k = getKey(order[i]);
      if (k) return k;
    }
    return null;
  }

  /**
   * Show the BYOK modal.
   */
  function openByokModal() {
    buildModal();          // idempotent — only builds once
    refreshAllStatuses();  // always reflect current state
    const modal = document.getElementById('byokModal');
    if (modal) {
      modal.classList.add('byok-open');
      // Trap focus on first input
      var firstInput = modal.querySelector('.byok-input');
      if (firstInput) setTimeout(function () { firstInput.focus(); }, 50);
    }
  }

  /**
   * Hide the BYOK modal.
   */
  function closeByokModal() {
    const modal = document.getElementById('byokModal');
    if (modal) modal.classList.remove('byok-open');
  }

  // ---------------------------------------------------------------------------
  // STATUS INDICATORS
  // ---------------------------------------------------------------------------

  /**
   * Update the in-modal status line for a single provider.
   */
  function refreshStatus(provider) {
    const statusEl = document.getElementById('byok-status-' + provider);
    if (!statusEl) return;

    if (hasKey(provider)) {
      statusEl.textContent = 'Saved ✓';
      statusEl.classList.add('saved');
    } else {
      statusEl.textContent = 'Not set';
      statusEl.classList.remove('saved');
    }
  }

  /** Refresh status indicators for all providers. */
  function refreshAllStatuses() {
    PROVIDERS.forEach(function (p) {
      refreshStatus(p.id);
    });
  }

  /**
   * Updates the page-level #keyStatus element (if it exists on a tool page).
   * Shows which provider's key is loaded, or a prompt to add a key.
   */
  function updatePageKeyStatus() {
    const statusEl = document.getElementById('keyStatus');
    if (!statusEl) return;

    // Find the first loaded key and its provider name
    var loadedProvider = null;
    for (var i = 0; i < PROVIDERS.length; i++) {
      if (hasKey(PROVIDERS[i].id)) {
        loadedProvider = PROVIDERS[i];
        break;
      }
    }

    if (loadedProvider) {
      statusEl.innerHTML =
        '<span style="color:#4ade80;font-weight:600">' +
        loadedProvider.label + ' key loaded ✓</span>';
    } else {
      statusEl.innerHTML =
        '<span style="color:#64748b">No key set — ' +
        '<button onclick="openByokModal()" style="background:none;border:none;' +
        'color:#818cf8;cursor:pointer;padding:0;font-size:inherit;' +
        'font-family:inherit;text-decoration:underline;">' +
        'add your key</button> to use this tool</span>';
    }
  }

  // ---------------------------------------------------------------------------
  // TRIGGER BUTTONS
  // ---------------------------------------------------------------------------

  /**
   * Bind all [data-byok="open"] buttons to open the modal.
   * Uses event delegation so it works on dynamically added buttons.
   */
  function bindOpenButtons() {
    document.addEventListener('click', function (e) {
      const trigger = e.target.closest('[data-byok="open"]');
      if (trigger) openByokModal();
    });
  }

  // ---------------------------------------------------------------------------
  // EXPOSE PUBLIC API
  // ---------------------------------------------------------------------------

  // Make key functions available globally for tool pages to call
  window.saveKey          = saveKey;
  window.getKey           = getKey;
  window.clearKey         = clearKey;
  window.hasKey           = hasKey;
  window.getAnyKey        = getAnyKey;
  window.openByokModal    = openByokModal;
  window.closeByokModal   = closeByokModal;

  // ---------------------------------------------------------------------------
  // INIT
  // ---------------------------------------------------------------------------

  document.addEventListener('DOMContentLoaded', function () {
    injectStyles();
    bindOpenButtons();
    updatePageKeyStatus();

    // Pre-build the modal structure immediately so first open is instant
    buildModal();
    refreshAllStatuses();
  });

}());
