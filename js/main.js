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
    <a href="/index.html" class="logo-link" aria-label="Aether Intel home">
      <span class="logo-ae-mark">
        <svg viewBox="0 0 512 512" width="36" height="36" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
          <defs>
            <linearGradient id="ae-sidebar-g" x1="80" y1="256" x2="432" y2="256" gradientUnits="userSpaceOnUse">
              <stop offset="0%" stop-color="#38bdf8"/>
              <stop offset="100%" stop-color="#22d3ee"/>
            </linearGradient>
          </defs>
          <rect width="512" height="512" rx="115" fill="#07070f"/>
          <text x="256" y="384" text-anchor="middle" font-family="'Space Grotesk',Arial,sans-serif" font-weight="700" font-size="370" fill="url(#ae-sidebar-g)">&#198;</text>
        </svg>
      </span>
      <span class="sidebar-logo-wordmark">
        <span class="logo-aether">AETHER</span>
        <span class="logo-intel">INTEL</span>
      </span>
    </a>
    <span class="sidebar-tagline">AI Signal · Always On</span>
  </div>
  <nav class="sidebar-nav">
    <a href="/index.html" class="nav-item" data-page="news">News</a>
    <a href="/models.html" class="nav-item" data-page="models">Models</a>
    <a href="/tools/chat.html" class="nav-item" data-page="playground">Playground</a>
    <a href="/skills.html" class="nav-item" data-page="skills">Skills</a>
  </nav>
</aside>`;

  const NOW_BAR_HTML = `
<footer class="now-bar">
  <div class="now-bar-ticker-wrap">
    <div class="now-bar-ticker" id="tickerTrack"></div>
  </div>
</footer>`;

  const MOBILE_NAV_HTML = `
<nav class="mobile-bottom-nav">
  <a href="/index.html" class="mob-nav-item" data-page="news">
    <svg class="mob-nav-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2"/><path d="M7 8h10M7 12h10M7 16h6"/></svg>
    <span class="mob-nav-label">News</span>
  </a>
  <a href="/models.html" class="mob-nav-item" data-page="models">
    <svg class="mob-nav-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6"/><path d="M9 1v3M15 1v3M9 20v3M15 20v3M1 9h3M1 15h3M20 9h3M20 15h3"/></svg>
    <span class="mob-nav-label">Models</span>
  </a>
  <a href="/tools/chat.html" class="mob-nav-item" data-page="playground">
    <svg class="mob-nav-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
    <span class="mob-nav-label">Play</span>
  </a>
  <a href="/skills.html" class="mob-nav-item" data-page="skills">
    <svg class="mob-nav-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 0 3-3h7z"/></svg>
    <span class="mob-nav-label">Skills</span>
  </a>
</nav>`;

  /**
   * Wraps the existing <main> content inside the full app shell.
   * Injects scroll-progress, sidebar, main-content wrapper, mobile nav, now-bar.
   */
  function injectAppShell() {
    const body = document.body;

    // Article pages use a .standalone-nav + content wrapper (either .page-wrap
    // or .article-hero/.article-wrap) instead of a <main> element.
    // Collect all non-script body children, strip the standalone-nav,
    // wrap the rest in a synthetic <main> so the app-shell can adopt it.
    if (!body.querySelector('main') && body.querySelector('.standalone-nav')) {
      var syntheticMain = document.createElement('main');
      syntheticMain.className = 'article-main';

      // Move every non-SCRIPT, non-NOSCRIPT body child into the synthetic main.
      // Use a snapshot array because live HTMLCollections shift as we move nodes.
      var toMove = Array.prototype.slice.call(body.childNodes).filter(function (n) {
        return n.nodeName !== 'SCRIPT' && n.nodeName !== 'NOSCRIPT';
      });
      toMove.forEach(function (node) { syntheticMain.appendChild(node); });

      // Remove the now-nested standalone-nav — the injected sidebar replaces it.
      var navInMain = syntheticMain.querySelector('.standalone-nav');
      if (navInMain) navInMain.parentNode.removeChild(navInMain);

      // Insert the synthetic main before the first script tag (or append).
      var firstScript = body.querySelector('script');
      if (firstScript) {
        body.insertBefore(syntheticMain, firstScript);
      } else {
        body.appendChild(syntheticMain);
      }
    }

    // Collect existing <main> element(s) — preserve them inside .main-content
    const existingMain = body.querySelector('main');
    const mainContent = document.createElement('div');
    mainContent.className = 'main-content';
    if (existingMain) {
      // Move the existing <main> into .main-content
      body.removeChild(existingMain);
      mainContent.appendChild(existingMain);
    }

    // Build .scroll-progress bar
    const scrollProgress = document.createElement('div');
    scrollProgress.className = 'scroll-progress';

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

    if (p === '' || p === '/index.html' || p === '/index' || p.includes('/articles')) return 'news';
    if (p.includes('/models')) return 'models';
    if (p.includes('/tools/')) return 'playground';
    if (p.includes('/skills')) return 'skills';
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
    // Hover glow is a mouse-only effect — skip entirely on touch devices
    if (!window.matchMedia('(hover: hover) and (pointer: fine)').matches) return;

    const cardSelector = '.sp-card, .article-card, .signal-card';

    document.addEventListener('mousemove', function (e) {
      // Guard: e.target must be an Element (not a text node, document, or window)
      if (!(e.target instanceof Element)) return;
      const card = e.target.closest(cardSelector);
      if (!card) return;

      const rect = card.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;

      card.style.background =
        'radial-gradient(circle at ' + x + 'px ' + y + 'px, rgba(129,140,248,0.12), transparent 65%)';
    });

    document.addEventListener('mouseout', function (e) {
      // Guard: e.target must be an Element
      if (!(e.target instanceof Element)) return;
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
  // 11. SPOTIFY-STYLE SWIPE-UP ARTICLE PANEL
  // ---------------------------------------------------------------------------

  /**
   * AePanel — manages the slide-up article overlay.
   *
   * Flow:
   *   initArticlePanel()  registers click/touch handlers on article cards.
   *   AePanel.open(url)   fetches article HTML, injects content, slides up.
   *   AePanel.close()     slides down, pops history state.
   *
   * URL management:
   *   history.pushState({ aepanel: true }, '', articleUrl) on open.
   *   history.back() on close → triggers popstate → we just animate out.
   *   Direct visits to article URLs still render normally via the app shell.
   */
  var AePanel = (function () {
    var panelEl = null;
    var bodyEl = null;
    var isOpen = false;
    var isAnimating = false;

    // Touch-drag state
    var dragStartY = 0;
    var dragCurrentY = 0;
    var isDragging = false;
    var scrolledToTop = true;

    // ── Build DOM ──
    function buildPanel() {
      if (panelEl) return;

      panelEl = document.createElement('div');
      panelEl.id = 'ae-article-panel';
      panelEl.setAttribute('role', 'dialog');
      panelEl.setAttribute('aria-modal', 'true');
      panelEl.setAttribute('aria-label', 'Article reader');

      panelEl.innerHTML =
        '<div class="ae-panel-handle" aria-hidden="true"></div>' +
        '<button class="ae-panel-down-btn" aria-label="Close article">' +
          '<svg viewBox="0 0 24 24"><polyline points="6 9 12 15 18 9"/></svg>' +
        '</button>' +
        '<div class="ae-panel-body"></div>';

      document.body.appendChild(panelEl);
      bodyEl = panelEl.querySelector('.ae-panel-body');

      // Close button
      panelEl.querySelector('.ae-panel-down-btn').addEventListener('click', function () {
        AePanel.close();
      });

      // Touch drag-to-dismiss
      panelEl.addEventListener('touchstart', onTouchStart, { passive: true });
      panelEl.addEventListener('touchmove', onTouchMove, { passive: false });
      panelEl.addEventListener('touchend', onTouchEnd, { passive: true });

      // Keyboard: Escape
      document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && isOpen) AePanel.close();
      });

      // Browser back button
      window.addEventListener('popstate', function () {
        if (isOpen) closeVisual();
      });
    }

    // ── Derive hero image URL from article URL ──
    // Pattern: /articles/50-slug.html → /images/articles/50-slug-hero.webp
    function heroUrlFor(articleUrl) {
      try {
        var path = new URL(articleUrl).pathname;
        return path.replace('/articles/', '/images/articles/').replace('.html', '-hero.webp');
      } catch (e) { return null; }
    }

    // ── Fetch + inject article ──
    function fetchAndRender(url, heroUrl) {
      // Show hero image immediately (derived from URL — usually cached by browser
      // if the user scrolled past the card). Spinner sits below it while text loads.
      var heroHtml = heroUrl
        ? '<img class="ae-panel-hero" src="' + heroUrl + '" alt="" ' +
          'onerror="this.style.display=\'none\'">'
        : '';

      bodyEl.innerHTML =
        heroHtml +
        '<div class="ae-panel-loading"><div class="ae-spinner"></div></div>';

      fetch(url)
        .then(function (res) {
          if (!res.ok) throw new Error('fetch failed ' + res.status);
          return res.text();
        })
        .then(function (html) {
          var doc = (new DOMParser()).parseFromString(html, 'text/html');

          // Update page title
          var pt = doc.querySelector('title');
          if (pt) document.title = pt.textContent;

          // Extract inline <style> blocks from the article's <head>
          var styles = '';
          doc.querySelectorAll('head style').forEach(function (s) {
            styles += s.outerHTML;
          });

          // Extract article body content
          var main = doc.querySelector('main') ||
                     doc.querySelector('.article-page') ||
                     doc.querySelector('article') ||
                     doc.body;
          var content = main ? main.innerHTML : doc.body.innerHTML;

          // Preserve the hero image if already displayed above the spinner
          var existingHero = bodyEl.querySelector('.ae-panel-hero');
          var heroTag = existingHero ? existingHero.outerHTML : '';

          bodyEl.innerHTML = heroTag + styles +
            '<div class="ae-panel-article">' + content + '</div>';

          // Hide duplicate hero inside article body (article has its own .article-hero img)
          var articleHero = bodyEl.querySelector('.ae-panel-article .article-hero');
          if (articleHero && heroTag) articleHero.style.display = 'none';

          // Make any scroll-reveal elements immediately visible inside panel
          bodyEl.querySelectorAll('.reveal, .reveal-scale, .reveal-stagger').forEach(function (el) {
            el.classList.add('visible');
          });

          // Scroll panel body to top
          bodyEl.scrollTop = 0;
        })
        .catch(function () {
          // If fetch fails, fall back to normal navigation
          closeVisual();
          window.location.href = url;
        });
    }

    // ── Animation helpers ──
    function openVisual() {
      isOpen = true;
      isAnimating = true;
      panelEl.classList.remove('ae-panel-closing');
      panelEl.classList.add('ae-panel-open');
      panelEl.addEventListener('transitionend', function handler() {
        isAnimating = false;
        panelEl.removeEventListener('transitionend', handler);
        panelEl.focus();
      });
    }

    function closeVisual() {
      if (!isOpen) return;
      isOpen = false;
      isAnimating = true;
      panelEl.classList.remove('ae-panel-open');
      panelEl.classList.add('ae-panel-closing');
      panelEl.addEventListener('transitionend', function handler() {
        panelEl.classList.remove('ae-panel-closing');
        isAnimating = false;
        // Clear content after exit so DOM stays clean
        setTimeout(function () {
          if (!isOpen) {
            bodyEl.innerHTML = '';
            document.title = 'Aether Intel';
          }
        }, 50);
        panelEl.removeEventListener('transitionend', handler);
      });
    }

    // ── Touch drag ──
    function onTouchStart(e) {
      scrolledToTop = bodyEl.scrollTop <= 2;
      if (!scrolledToTop) return;
      dragStartY = e.touches[0].clientY;
      dragCurrentY = 0;
      isDragging = true;
    }

    function onTouchMove(e) {
      if (!isDragging) return;
      // If user started scrolling the content up, stop treating as drag
      if (bodyEl.scrollTop > 4) { isDragging = false; return; }

      var dy = e.touches[0].clientY - dragStartY;
      if (dy <= 0) { isDragging = false; return; } // swipe up = scroll content

      e.preventDefault(); // prevent page behind from scrolling
      dragCurrentY = dy;

      // Follow finger with rubber-band resistance
      var resistance = Math.pow(dy, 0.72);
      panelEl.classList.add('ae-panel-dragging');
      panelEl.style.transform = 'translateY(' + resistance + 'px)';
    }

    function onTouchEnd() {
      if (!isDragging) return;
      isDragging = false;
      panelEl.classList.remove('ae-panel-dragging');
      panelEl.style.transform = '';

      if (dragCurrentY > 90) {
        AePanel.close();
      }
    }

    // ── Public API ──
    return {
      open: function (url, titleHint) {
        buildPanel();
        if (isAnimating) return;

        document.title = titleHint || 'Aether Intel';
        history.pushState({ aepanel: true, url: url }, '', url);
        openVisual();
        fetchAndRender(url, heroUrlFor(url));
      },

      close: function () {
        if (!isOpen || isAnimating) return;
        history.back(); // → triggers popstate → closeVisual()
        closeVisual();
      }
    };
  }());

  /**
   * Wire up article card clicks to open the swipe panel instead of
   * navigating. Works for <a class="article-card"> and for regular
   * <a href="/articles/..."> links inside .article-grid-full.
   */
  function initArticlePanel() {
    // Only intercept on pages that have an article grid (home, articles list)
    // and not when we ARE already inside an article page.
    var isArticlePage = document.body.classList.contains('standalone-nav') ||
                        !!document.querySelector('main.article-page');
    if (isArticlePage) return;

    // ── Card press micro-animation (Spotify tap feel) ──
    function addPressState(e) {
      var card = (e.target instanceof Element) && e.target.closest('a.article-card, .article-card');
      if (card) card.classList.add('ae-card-pressing');
    }
    function clearPressState() {
      document.querySelectorAll('.ae-card-pressing').forEach(function (c) {
        c.classList.remove('ae-card-pressing');
      });
    }
    document.addEventListener('mousedown', addPressState);
    document.addEventListener('mouseup', clearPressState);
    document.addEventListener('touchstart', addPressState, { passive: true });
    document.addEventListener('touchend', clearPressState, { passive: true });
    document.addEventListener('touchcancel', clearPressState, { passive: true });

    document.addEventListener('click', function (e) {
      // Walk up from click target to find an article link
      var el = e.target;
      while (el && el !== document.body) {
        if (el.tagName === 'A') {
          var href = el.getAttribute('href');
          if (href && href.match(/\/articles\/[^/]+\.html$/)) {
            e.preventDefault();
            var fullUrl = new URL(href, window.location.origin).href;
            var title = (el.querySelector('h2, h3, .article-card-title') || {}).textContent || 'Article';
            // 85ms delay: lets the scale-back (press → release) animate before panel rises
            setTimeout(function () {
              clearPressState();
              AePanel.open(fullUrl, title);
            }, 85);
            return;
          }
          break; // stop walking if we hit a non-article link
        }
        el = el.parentElement;
      }
    });
  }

  // ---------------------------------------------------------------------------
  // INIT — DOMContentLoaded
  // ---------------------------------------------------------------------------

  document.addEventListener('DOMContentLoaded', function () {
    injectAppShell();
    setActiveNav();
    initScrollProgress();
    initScrollReveal();
    setGreeting();
    initTicker();
    initCardGlow();
    initSearch();
    initArticlePanel(); // Spotify swipe-up reader
    loadOpenRouterModels(); // No-ops if #modelsGrid not present
  });

  // ---------------------------------------------------------------------------
  // PWA — Service Worker Registration + Update Detection
  // Centralised here so every page that loads main.js gets identical PWA setup
  // (no duplicated inline SW registration in each HTML page).
  // ---------------------------------------------------------------------------

  (function initPWA() {
    if (!('serviceWorker' in navigator)) return;

    // ─── Inject mobile-web-app-capable meta if missing (replaces deprecated apple-* version) ───
    if (!document.querySelector('meta[name="mobile-web-app-capable"]')) {
      var meta = document.createElement('meta');
      meta.name = 'mobile-web-app-capable';
      meta.content = 'yes';
      document.head.appendChild(meta);
    }

    // ─── Register on window load to not contend with critical path ───
    window.addEventListener('load', function () {
      // Nuke stale caches once per session (defends against legacy SW caches)
      try {
        if (!sessionStorage.getItem('ae-pwa-clean-v12')) {
          if ('caches' in window) {
            caches.keys().then(function (names) {
              names.forEach(function (n) { caches.delete(n); });
            });
          }
          sessionStorage.setItem('ae-pwa-clean-v12', '1');
        }
      } catch (e) { /* sessionStorage may be unavailable in some private modes */ }

      // updateViaCache:'none' forces the browser to always byte-check sw.js,
      // bypassing the HTTP cache — critical so a CDN-cached SW never gets stuck.
      navigator.serviceWorker.register('/sw.js', { updateViaCache: 'none' }).catch(function (e) {
        console.warn('[SW]', e);
      });
    });

    // When a new SW takes control (skipWaiting fired), offer a reload
    navigator.serviceWorker.addEventListener('controllerchange', function () {
      showUpdateToast();
    });

    // Also detect via updatefound (covers first-install of updated SW)
    navigator.serviceWorker.ready.then(function (reg) {
      reg.addEventListener('updatefound', function () {
        var newWorker = reg.installing;
        if (!newWorker) return;
        newWorker.addEventListener('statechange', function () {
          // installed + there was already a controller = genuine update, not first load
          if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
            showUpdateToast();
          }
        });
      });
    });

    var toastShown = false;
    function showUpdateToast() {
      if (toastShown) return;
      toastShown = true;

      var toast = document.createElement('div');
      toast.id = 'pwa-update-toast';
      toast.setAttribute('role', 'status');
      toast.setAttribute('aria-live', 'polite');
      toast.innerHTML =
        '<span class="pwa-toast-msg">✦ Fresh signals available</span>' +
        '<button class="pwa-toast-btn" id="pwa-reload-btn">Reload</button>' +
        '<button class="pwa-toast-close" id="pwa-dismiss-btn" aria-label="Dismiss">✕</button>';

      document.body.appendChild(toast);

      // Animate in
      requestAnimationFrame(function () {
        requestAnimationFrame(function () {
          toast.classList.add('pwa-toast-visible');
        });
      });

      document.getElementById('pwa-reload-btn').addEventListener('click', function () {
        window.location.reload();
      });
      document.getElementById('pwa-dismiss-btn').addEventListener('click', function () {
        toast.classList.remove('pwa-toast-visible');
        setTimeout(function () { toast.remove(); }, 300);
      });

      // Auto-dismiss after 12 s if user ignores it
      setTimeout(function () {
        if (document.body.contains(toast)) {
          toast.classList.remove('pwa-toast-visible');
          setTimeout(function () { toast.remove(); }, 300);
        }
      }, 12000);
    }
  }());

}());
