/**
 * main.js — Aether Intel AI News Site
 * Runs on every page. Handles nav injection, scroll progress, scroll reveal,
 * greeting text, ticker, card hover glow, search, newsletter, and model feed.
 */

(function () {
  'use strict';

  // ---------------------------------------------------------------------------
  // 1. NAV INJECTION
  // ---------------------------------------------------------------------------

  const SIDEBAR_HTML = `
<aside class="sidebar">
  <div class="sidebar-logo">
    <a href="/index.html" class="logo-link">
      <span class="logo-aether">AETHER</span><span class="logo-intel">INTEL</span>
    </a>
    <span class="logo-tagline">AI News · Tools · Intelligence</span>
  </div>
  <nav class="sidebar-nav">
    <span class="nav-section-label">Discover</span>
    <a href="/index.html" class="nav-item" data-page="home">Home</a>
    <a href="/articles.html" class="nav-item" data-page="articles">AI News</a>
    <a href="/ai-hub.html" class="nav-item" data-page="ai-hub">AI Hub</a>
    <a href="/ai-intelligence.html" class="nav-item" data-page="ai-intelligence">Intelligence</a>

    <span class="nav-section-label">Tools</span>
    <a href="/tools/chat.html" class="nav-item" data-page="chat">AI Chat</a>
    <a href="/tools/writer.html" class="nav-item" data-page="writer">Content Writer</a>
    <a href="/tools/image.html" class="nav-item" data-page="image">Image Gen</a>

    <span class="nav-section-label">Resources</span>
    <a href="/skills.html" class="nav-item" data-page="skills">Skills Library</a>
    <a href="/research.html" class="nav-item" data-page="research">Research Reports</a>
    <a href="/resources.html" class="nav-item" data-page="resources">Resources</a>
    <a href="/affiliates.html" class="nav-item" data-page="affiliates">Recommended Tools</a>
    <a href="/newsletter.html" class="nav-item" data-page="newsletter">Newsletter</a>
  </nav>
  <div class="sidebar-cards">
    <div class="sb-card">
      <h4>BYOK TOOLS</h4>
      <p>Bring your own API key. Zero data collected.</p>
      <a href="/tools/chat.html">Try Free →</a>
    </div>
    <div class="sb-card" style="border-color:rgba(245,158,11,0.2)">
      <h4 style="color:var(--neon-gold)">SKILLS LIBRARY</h4>
      <p>Free agent skills and prompt packs to download.</p>
      <a href="/skills.html" style="color:var(--neon-gold);background:rgba(245,158,11,0.08);border-color:rgba(245,158,11,0.3)">Browse →</a>
    </div>
  </div>
</aside>`;

  const MOBILE_HEADER_HTML = `
<div class="mobile-topbar">
  <a href="/index.html" class="mobile-topbar-logo">
    <span class="logo-aether">AETHER</span><span class="logo-intel">INTEL</span>
  </a>
  <span class="mobile-topbar-tagline">AI News · Tools · Intelligence</span>
</div>`;

  const NOW_BAR_HTML = `
<footer class="now-bar">
  <div class="now-bar-left">
    <div class="now-bar-live-pill">
      <span class="now-bar-live-pill-dot"></span>
      LIVE
    </div>
    <div class="now-bar-icon-box">⚡</div>
    <div class="now-bar-info">
      <div class="now-bar-title">AETHER INTEL</div>
      <div class="now-bar-sub">ai signal · live feed</div>
    </div>
  </div>
  <div class="now-bar-center">
    <div class="now-bar-breaking-label">AI INTELLIGENCE FEED</div>
    <div class="now-bar-ticker-wrap">
      <div class="now-bar-ticker" id="tickerTrack"></div>
    </div>
  </div>
  <div class="now-bar-right">
    <button class="now-bar-btn" id="volBtn" title="Pause feed">🔊</button>
  </div>
</footer>`;

  const MOBILE_NAV_HTML = `
<nav class="mobile-bottom-nav">
  <a href="/index.html" class="mob-nav-item" data-page="home">
    <span class="mob-nav-icon">🏠</span>
    <span class="mob-nav-label">HOME</span>
  </a>
  <a href="/articles.html" class="mob-nav-item" data-page="articles">
    <span class="mob-nav-icon">📰</span>
    <span class="mob-nav-label">NEWS</span>
  </a>
  <a href="/ai-hub.html" class="mob-nav-item" data-page="ai-hub">
    <span class="mob-nav-icon">📡</span>
    <span class="mob-nav-label">HUB</span>
  </a>
  <a href="/tools/chat.html" class="mob-nav-item" data-page="chat">
    <span class="mob-nav-icon">🛠</span>
    <span class="mob-nav-label">TOOLS</span>
  </a>
  <a href="/research.html" class="mob-nav-item" data-page="research">
    <span class="mob-nav-icon">📊</span>
    <span class="mob-nav-label">REPORTS</span>
  </a>
</nav>`;

  /**
   * Wraps the existing <main> content inside the full app shell.
   * Injects scroll-progress, sidebar, main-content wrapper, mobile nav, now-bar.
   */
  function injectAppShell() {
    const body = document.body;

    // Collect existing <main> element(s) — preserve them inside .main-content
    const existingMain = body.querySelector('main');
    const mainContent = document.createElement('div');
    mainContent.className = 'main-content';

    // Inject mobile topbar at the very top of .main-content
    const mobileHeaderWrapper = document.createElement('div');
    mobileHeaderWrapper.innerHTML = MOBILE_HEADER_HTML.trim();
    const mobileHeaderEl = mobileHeaderWrapper.firstElementChild;
    mainContent.appendChild(mobileHeaderEl);

    if (existingMain) {
      // Move the existing <main> into .main-content (after mobile header)
      body.removeChild(existingMain);
      mainContent.appendChild(existingMain);
    }

    // Build .scroll-progress bar
    const scrollProgress = document.createElement('div');
    scrollProgress.className = 'scroll-progress';
    scrollProgress.setAttribute('aria-hidden', 'true');

    // Build .app-shell
    const appShell = document.createElement('div');
    appShell.className = 'app-shell';

    // Parse sidebar HTML
    const sidebarWrapper = document.createElement('div');
    sidebarWrapper.innerHTML = SIDEBAR_HTML.trim();
    const sidebarEl = sidebarWrapper.firstElementChild;

    appShell.appendChild(sidebarEl);
    appShell.appendChild(mainContent);

    // Parse mobile nav HTML
    const mobileNavWrapper = document.createElement('div');
    mobileNavWrapper.innerHTML = MOBILE_NAV_HTML.trim();
    const mobileNavEl = mobileNavWrapper.firstElementChild;

    // Parse now-bar HTML
    const nowBarWrapper = document.createElement('div');
    nowBarWrapper.innerHTML = NOW_BAR_HTML.trim();
    const nowBarEl = nowBarWrapper.firstElementChild;

    // Inject into body
    body.prepend(scrollProgress);
    body.insertBefore(appShell, scrollProgress.nextSibling);
    body.appendChild(mobileNavEl);
    body.appendChild(nowBarEl);
  }

  // ---------------------------------------------------------------------------
  // 2. ACTIVE NAV STATE
  // ---------------------------------------------------------------------------

  /**
   * Maps pathname patterns to data-page keys.
   * Returns the matching page key or null.
   */
  function resolvePageKey(pathname) {
    // Normalise: strip trailing slash, lowercase
    const p = pathname.replace(/\/$/, '').toLowerCase();

    if (p === '' || p === '/index.html' || p === '/index') return 'home';
    if (p.includes('/articles')) return 'articles';
    if (p.includes('/ai-hub')) return 'ai-hub';
    if (p.includes('/ai-intelligence')) return 'ai-intelligence';
    if (p.includes('/tools/chat')) return 'chat';
    if (p.includes('/tools/writer')) return 'writer';
    if (p.includes('/tools/image')) return 'image';
    if (p.includes('/skills')) return 'skills';
    if (p.includes('/research')) return 'research';
    if (p.includes('/resources')) return 'resources';
    if (p.includes('/affiliates')) return 'affiliates';
    if (p.includes('/newsletter')) return 'newsletter';
    return null;
  }

  function setActiveNav() {
    const pageKey = resolvePageKey(window.location.pathname);
    if (!pageKey) return;

    document.querySelectorAll('[data-page]').forEach(function (el) {
      if (el.getAttribute('data-page') === pageKey) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });
  }

  /**
   * Applies .active to any .ql-pill whose href matches the current pathname.
   * Enables the quick-access strip to reflect current page location.
   */
  function setActivePills() {
    var p = window.location.pathname;
    document.querySelectorAll('.ql-pill').forEach(function (pill) {
      var href = pill.getAttribute('href') || '';
      // Exact match, or pathname starts with the pill's path (handles index = /)
      var isActive = href && (p === href || (href !== '/' && p.startsWith(href.replace('.html', ''))));
      pill.classList.toggle('active', isActive);
    });
  }

  // ---------------------------------------------------------------------------
  // 3. SCROLL PROGRESS BAR
  // ---------------------------------------------------------------------------

  function initScrollProgress() {
    const bar = document.querySelector('.scroll-progress');
    if (!bar) return;

    function updateBar(scrollTop, scrollHeight, clientHeight) {
      const scrollable = scrollHeight - clientHeight;
      const pct = scrollable > 0 ? (scrollTop / scrollable) * 100 : 0;
      bar.style.width = Math.min(100, Math.max(0, pct)) + '%';
    }

    // Desktop: .main-content or #contentScroll scroller
    const contentScroll = document.getElementById('contentScroll') ||
      document.querySelector('.main-content');

    if (contentScroll) {
      contentScroll.addEventListener('scroll', function () {
        updateBar(
          contentScroll.scrollTop,
          contentScroll.scrollHeight,
          contentScroll.clientHeight
        );
      }, { passive: true });
    }

    // Mobile: window scroll (always listen regardless)
    window.addEventListener('scroll', function () {
      updateBar(
        window.scrollY || document.documentElement.scrollTop,
        document.documentElement.scrollHeight,
        document.documentElement.clientHeight
      );
    }, { passive: true });
  }

  // ---------------------------------------------------------------------------
  // 4. SCROLL REVEAL
  // ---------------------------------------------------------------------------

  function initScrollReveal() {
    const revealEls = document.querySelectorAll('.reveal, .reveal-scale, .reveal-stagger');
    if (!revealEls.length) return;

    // Pre-assign stagger delays to siblings within same parent
    const staggerParents = new Set();
    document.querySelectorAll('.reveal-stagger').forEach(function (el) {
      staggerParents.add(el.parentElement);
    });

    staggerParents.forEach(function (parent) {
      if (!parent) return;
      const siblings = parent.querySelectorAll('.reveal-stagger');
      siblings.forEach(function (el, i) {
        el.style.transitionDelay = (i * 0.07) + 's';
      });
    });

    // Determine the scroll root.
    // On desktop, .main-content is the scroll container (overflow-y: auto).
    // On mobile (≤900px), body/html scroll naturally so root must be null (viewport).
    // We read computed style rather than hardcoding a breakpoint so it's resize-safe.
    var mainContent = document.querySelector('.main-content');
    var scrollRoot = null;
    if (mainContent) {
      var cs = window.getComputedStyle(mainContent);
      if (cs.overflowY === 'auto' || cs.overflowY === 'scroll') {
        scrollRoot = mainContent;
      }
    }

    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('visible');
          // Once visible, no need to keep observing
          observer.unobserve(entry.target);
        }
      });
    }, {
      root: scrollRoot,          // null → viewport (mobile); .main-content (desktop)
      threshold: 0.05,
      rootMargin: '-20px 0px'   // slightly less aggressive so top-of-page items fire
    });

    revealEls.forEach(function (el) {
      observer.observe(el);
    });
  }

  // ---------------------------------------------------------------------------
  // 5. GREETING TEXT
  // ---------------------------------------------------------------------------

  function setGreeting() {
    const greetingEl = document.getElementById('greeting-text');
    if (!greetingEl) return;

    const hour = new Date().getHours();
    let greeting;

    if (hour >= 5 && hour <= 11) {
      greeting = 'Good morning';
    } else if (hour >= 12 && hour <= 16) {
      greeting = 'Good afternoon';
    } else if (hour >= 17 && hour <= 20) {
      greeting = 'Good evening';
    } else {
      greeting = 'Welcome back';
    }

    greetingEl.textContent = greeting;
  }

  // ---------------------------------------------------------------------------
  // 6. TICKER — JSON-driven with inline fallback
  // ---------------------------------------------------------------------------

  function initTicker() {
    var volBtn = document.getElementById('volBtn');
    var tickerTrack = document.getElementById('tickerTrack');
    if (!tickerTrack) return;

    // Fallback headlines used when /data/ticker.json is unavailable
    var defaultItems = [
      { text: 'AI models now processing 10M+ token contexts — long-document analysis reaches a new capability tier', tag: '🔥' },
      { text: 'OpenAI, Anthropic and Google collectively raise $40B+ in 2026 — AI infrastructure investment accelerates' },
      { text: 'Llama 4 series achieves near-parity with GPT-4o on reasoning benchmarks — open weight models close the gap', tag: '⚡' },
      { text: 'EU AI Act Phase 2 enforcement begins — high-risk AI systems face mandatory audits and documentation requirements' },
      { text: 'GitHub Copilot repos show 40% higher secret leak rate — 2,702 real credentials extracted by independent researchers' },
      { text: 'n8n surpasses 1 million active workflows — automation platform becomes default AI pipeline infrastructure', tag: '📈' },
      { text: 'AI coding assistants now used in 78% of enterprise software teams — adoption doubled year-over-year' },
      { text: 'Claude 3.7 Sonnet ranks #1 on coding benchmarks — fastest token generation at time of launch' },
      { text: 'On-device AI reaches flagship tier — Apple, Samsung and Google ship edge inference chips in 2026 devices' },
      { text: 'AI agent operating costs drop 60% year-over-year — Sonnet-class models now viable for 80% of production tasks' },
      { text: 'Anthropic interpretability research reveals internal concept mapping — first window into model reasoning', tag: '⚡' },
      { text: 'Recursive self-improvement milestones confirmed in lab settings — AI systems measurably improve their own architecture', tag: '⚠️' }
    ];

    function buildTickerHTML(items) {
      // Duplicate content for seamless CSS loop (animation moves translateX(-50%))
      var html = '';
      for (var copy = 0; copy < 2; copy++) {
        for (var i = 0; i < items.length; i++) {
          var item = items[i];
          var tagHtml = item.tag
            ? '<strong style="color:var(--neon-gold);margin-right:6px">' + item.tag + '</strong>'
            : '';
          html += '<span class="ticker-item">' + tagHtml + item.text + '</span>';
          html += '<span class="ticker-sep">◆</span>';
        }
      }
      return html;
    }

    // Paint default items immediately — ticker is never blank
    tickerTrack.innerHTML = buildTickerHTML(defaultItems);

    // Then try to fetch fresh headlines and swap in if available
    fetch('/data/ticker.json')
      .then(function (res) {
        if (!res.ok) throw new Error('ticker.json unavailable');
        return res.json();
      })
      .then(function (data) {
        if (data.items && data.items.length) {
          tickerTrack.innerHTML = buildTickerHTML(data.items);
        }
      })
      .catch(function () { /* default already painted */ });

    // Pause / resume button
    if (volBtn) {
      var paused = false;
      volBtn.addEventListener('click', function () {
        paused = !paused;
        tickerTrack.style.animationPlayState = paused ? 'paused' : 'running';
        volBtn.textContent = paused ? '⏸' : '🔊';
        volBtn.title = paused ? 'Resume feed' : 'Pause feed';
      });
    }
  }

  // ---------------------------------------------------------------------------
  // 7. CARD HOVER GLOW
  // ---------------------------------------------------------------------------

  function initCardGlow() {
    const cardSelector = '.sp-card, .article-card, .signal-card';

    // Use event delegation on document to handle dynamically added cards too
    document.addEventListener('mousemove', function (e) {
      const card = e.target.closest(cardSelector);
      if (!card) return;

      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      card.style.background =
        'radial-gradient(circle at ' + x + 'px ' + y + 'px, rgba(129,140,248,0.12), transparent 65%)';
    });

    document.addEventListener('mouseleave', function (e) {
      const card = e.target.closest(cardSelector);
      if (!card) return;
      card.style.background = '';
    }, true);

    // Also handle direct mouseleave on each card for accuracy
    document.addEventListener('mouseover', function () {}, false);

    // Delegate mouseleave via bubbling workaround — use mouseout
    document.addEventListener('mouseout', function (e) {
      const card = e.target.closest(cardSelector);
      if (!card) return;
      // Only clear if mouse actually left the card (not just moved to a child)
      if (!card.contains(e.relatedTarget)) {
        card.style.background = '';
      }
    });
  }

  // ---------------------------------------------------------------------------
  // 8. SEARCH HANDLER
  // ---------------------------------------------------------------------------

  function initSearch() {
    const searchInput = document.getElementById('topSearch');
    if (!searchInput) return;

    searchInput.addEventListener('keydown', function (e) {
      if (e.key !== 'Enter') return;
      const query = searchInput.value.trim();
      if (!query) return;
      const url = 'https://duckduckgo.com/?q=site:ai.quantummerlin.com+' + encodeURIComponent(query);
      window.open(url, '_blank', 'noopener,noreferrer');
    });
  }

  // ---------------------------------------------------------------------------
  // 9. NEWSLETTER FORM HANDLER
  // ---------------------------------------------------------------------------

  /**
   * Generic newsletter submit handler.
   * @param {Event} e - The submit event.
   * @param {string} formId - ID of the form element.
   * @param {string} btnId - ID of the submit button element.
   * @param {string} successId - ID of the success message element.
   */
  window.handleNewsletterSubmit = function (e, formId, btnId, successId) {
    e.preventDefault();

    const form = document.getElementById(formId);
    const btn = document.getElementById(btnId);
    const success = document.getElementById(successId);

    if (!form || !btn || !success) return;

    btn.disabled = true;
    btn.textContent = 'Subscribing...';

    setTimeout(function () {
      form.classList.add('hidden');
      success.classList.remove('hidden');
    }, 900);
  };

  /** Home page newsletter shorthand. */
  window.handleHomeNLSubmit = function (e) {
    window.handleNewsletterSubmit(e, 'homeNLForm', 'homeNLBtn', 'homeNLSuccess');
  };

  /** AI Hub newsletter shorthand. */
  window.handleHubNL = function (e) {
    window.handleNewsletterSubmit(e, 'hubNLForm', 'hubNLBtn', 'hubNLSuccess');
  };

  // ---------------------------------------------------------------------------
  // 10. OPENROUTER MODELS (Home page only)
  // ---------------------------------------------------------------------------

  /**
   * Formats a raw context integer into a human-readable string (e.g. 128000 → "128K").
   */
  function formatContext(num) {
    if (!num || isNaN(num)) return '—';
    if (num >= 1000000) return Math.round(num / 1000000) + 'M';
    if (num >= 1000) return Math.round(num / 1000) + 'K';
    return String(num);
  }

  /**
   * Truncates a string to maxLen characters, appending ellipsis if needed.
   */
  function truncate(str, maxLen) {
    if (!str) return '';
    return str.length > maxLen ? str.slice(0, maxLen) + '…' : str;
  }

  /**
   * Determines badge type for a model.
   * Returns 'FREE', 'NEW', or 'PRO'.
   */
  function getModelBadge(model) {
    const id = (model.id || '').toLowerCase();
    const name = (model.name || '').toLowerCase();

    // Free if pricing is zero
    if (
      model.pricing &&
      parseFloat(model.pricing.prompt) === 0 &&
      parseFloat(model.pricing.completion) === 0
    ) {
      return 'FREE';
    }

    // NEW if created within the last 30 days
    if (model.created) {
      const ageMs = Date.now() - model.created * 1000;
      const thirtyDays = 30 * 24 * 60 * 60 * 1000;
      if (ageMs < thirtyDays) return 'NEW';
    }

    // PRO for everything else
    return 'PRO';
  }

  /**
   * Extracts a short provider name from the model id (e.g. "openai/gpt-4o" → "openai").
   */
  function extractProvider(model) {
    if (model.id && model.id.includes('/')) {
      return model.id.split('/')[0];
    }
    return model.id || 'unknown';
  }

  /**
   * Renders the top 12 models into #modelsGrid.
   */
  function renderModels(models) {
    const grid = document.getElementById('modelsGrid');
    if (!grid) return;

    // Sort by `created` descending (newest first)
    const sorted = models
      .filter(function (m) { return m && m.id; })
      .sort(function (a, b) { return (b.created || 0) - (a.created || 0); })
      .slice(0, 12);

    const badgeClasses = {
      FREE: 'badge-free',
      NEW: 'badge-new',
      PRO: 'badge-pro'
    };

    const html = sorted.map(function (model) {
      const badge = getModelBadge(model);
      const provider = extractProvider(model);
      const ctx = formatContext(model.context_length);
      const name = truncate(model.name || model.id, 24);

      return [
        '<div class="model-card reveal">',
        '  <div class="model-card-header">',
        '    <span class="model-badge ' + (badgeClasses[badge] || 'badge-pro') + '">' + badge + '</span>',
        '  </div>',
        '  <div class="model-name" title="' + (model.name || model.id) + '">' + name + '</div>',
        '  <div class="model-provider">' + provider + '</div>',
        '  <div class="model-ctx">Context: ' + ctx + '</div>',
        '</div>'
      ].join('\n');
    }).join('\n');

    grid.innerHTML = html;

    // Trigger scroll reveal on newly added cards
    initScrollReveal();
  }

  function loadOpenRouterModels() {
    const grid = document.getElementById('modelsGrid');
    if (!grid) return;

    fetch('https://openrouter.ai/api/v1/models')
      .then(function (res) {
        if (!res.ok) throw new Error('OpenRouter fetch failed: ' + res.status);
        return res.json();
      })
      .then(function (data) {
        const models = Array.isArray(data) ? data : (data.data || []);
        renderModels(models);
      })
      .catch(function (err) {
        console.warn('[AetherIntel] OpenRouter models unavailable:', err.message);
        // Show a graceful fallback message in the grid
        if (grid) {
          grid.innerHTML = '<p class="models-error">Model feed temporarily unavailable.</p>';
        }
      });
  }

  // ---------------------------------------------------------------------------
  // INIT — DOMContentLoaded
  // ---------------------------------------------------------------------------

  document.addEventListener('DOMContentLoaded', function () {
    injectAppShell();
    setActiveNav();
    setActivePills();
    initScrollProgress();
    initScrollReveal();
    setGreeting();
    initTicker();
    initCardGlow();
    initSearch();
    loadOpenRouterModels(); // No-ops if #modelsGrid not present
  });

}());
