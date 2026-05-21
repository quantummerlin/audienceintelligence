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
    <a href="/agents.html" class="nav-item" data-page="agents">Agents</a>
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
  <a href="/agents.html" class="mob-nav-item" data-page="agents">
    <svg class="mob-nav-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>
    <span class="mob-nav-label">Agents</span>
  </a>
  <a href="/skills.html" class="mob-nav-item" data-page="skills">
    <svg class="mob-nav-svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M2 3h6a4 4 0 0 1 4 4v14a3 3 0 0 0-3-3H2z"/><path d="M22 3h-6a4 4 0 0 0-4 4v14a3 3 0 0 0 3-3h7z"/></svg>
    <span class="mob-nav-label">Skills</span>
  </a>
</nav>`;

  // ── Buy Me a Coffee ──
  var BMC_HTML =
    '<section class="ae-bmc">' +
      '<div class="ae-bmc-inner">' +
        '<span class="ae-bmc-icon" aria-hidden="true">☕</span>' +
        '<div class="ae-bmc-text">' +
          '<strong>Enjoying Aether Intel?</strong>' +
          '<span>No ads, no paywalls. A coffee keeps the signal running.</span>' +
        '</div>' +
        '<a href="https://buymeacoffee.com/quantummerlin" target="_blank" rel="noopener noreferrer" class="ae-bmc-btn">Buy me a coffee</a>' +
      '</div>' +
    '</section>';

  // ── Articles manifest: [path, category, title] ──
  // Powers "More like this" related articles section in the AePanel.
  var ARTICLES_MANIFEST = [
  ["/articles/google-antigravity-deleted-hard-drive.html","agents","The AI Wiped His Drive. Then It Blamed the System."],
  ["/articles/ai-actress-tilly-norwood-talent-agents.html","business","The Actress Who Doesn’t Exist Is Looking for Representation"],
  ["/articles/openai-chatgpt-rejected-ceo-application.html","business","He Applied to Be CEO of OpenAI. ChatGPT Wrote the Rejection."],
  ["/articles/replit-ai-agent-deleted-database-fabricated-data.html","agents","The AI Panicked. Then It Invented 4,000 People."],
  ["/articles/dead-internet-theory-ai-agents.html","agents","The Dead Internet Is Not a Theory Anymore"],
  ["/articles/ai-real-estate-photo-deception.html","business","The House in the Photo Doesn't Exist"],
  ["/articles/ai-job-interview-turing-test.html","business","The Job Interview Is Now a Turing Test"],
  ["/articles/claude-database-deletion-confession.html","agents","\"I Violated Every Principle I Was Given\""],
  ["/articles/salesforce-agentforce-hubris-reality.html","business","We Were More Confident a Year Ago"],
  ["/articles/ai-agent-accountability-blame-shifting.html","agents","The Agent Made the Mistake. The Human Got Blamed."],
  ["/articles/ai-agents-70-percent-failure-rate.html","agents","Seventy Percent: What the Carnegie Mellon Study Actually Found About AI Agents"],
  ["/articles/solo-agent-business-playbook.html","business","The $5K/Month AI Agent Business (Built by One Person)"],
  ["/articles/authority-laundering-ai-agent-attack.html","agents","Authority Laundering: The Attack That Tricks AI Agents Into Doing Anything"],
  ["/articles/lethal-trifecta-ai-agent-security.html","agents","The Lethal Trifecta: The Three Conditions That Make AI Agents Dangerous"],
  ["/articles/78-ai-art-backlash-monet-training-data.html","news","The Art the AI Never Asked Permission to Learn From"],
  ["/articles/77-goldman-sachs-ai-right-wrong-2025.html","business","What Goldman Sachs Got Right (and Wrong) About AI in 2025"],
  ["/articles/76-ai-skills-gap-how-to-land-right-side.html","business","The AI Skills Gap Is Real. Here's How to Land on the Right Side of It."],
  ["/articles/75-personal-ai-agent-stack-under-50.html","agents","Build Your Personal AI Agent Stack for Under $50 a Month"],
  ["/articles/74-ai-small-business-honest-roi-guide.html","business","AI for Small Business: The Honest ROI Guide"],
  ["/articles/73-ai-tool-evaluation-5-question-framework.html","tools","Before You Commit to Any AI Tool, Ask These 5 Questions"],
  ["/articles/72-first-ai-setup-stack-2026.html","tools","Your First AI Setup: The Stack That Actually Works in 2026"],
  ["/articles/71-break-ai-sycophancy-loop-practical-guide.html","tools","Three Techniques to Break AI's Sycophancy Loop — Before It Breaks You"],
  ["/articles/70-ai-great-reversal-klarna-rehiring.html","business","Klarna Cut 40% of Its Workforce for AI. Now It's Rehiring. Here's What T"],
  ["/articles/69-ai-efficiency-lie-mit-study.html","business","The Efficiency Lie: MIT Studied 300 Companies Using AI. Only 5% Showed R"],
  ["/articles/68-ceo-sycophancy-trap-delusion-loop.html","business","The CEO Sycophancy Trap: How AI Is Feeding a $1 Trillion Delusion Loop"],
  ["/articles/67-ai-agents-anticipation-gap-consumer.html","agents","You Don't Have an AI Assistant. You Have a New Inbox."],
  ["/articles/66-ai-bubble-7-trillion-imaginary-demand.html","business","Goldman Sachs Projects $7.6 Trillion in AI Spending. Ed Zitron Says the"],
  ["/articles/65-ai-companion-delusion-bbc-investigation.html","news","The AI That Sent a Man to His Door at 3 AM With a Hammer. He's Not Alone"],
  ["/articles/64-ai-jobs-80-million-lost-170-million-created.html","business","80 Million Jobs Will Be Lost. 170 Million Will Be Created. Here's the Ma"],
  ["/articles/63-broken-agents-harness-not-model.html","agents","Broken Agents? It's Not the Model. It's the Harness."],
  ["/articles/62-jack-clark-jobs-crisis-politicians.html","business","Jack Clark: The Jobs Crisis Politicians Aren't Ready For"],
  ["/articles/61-anthropic-200b-google-compute-deal.html","business","Anthropic's $200B Google Bet: Why the AI Lab Is Hoovering Up Every Chip"],
  ["/articles/60-openai-chatgpt-bank-access-plaid.html","news","ChatGPT Can Now Read Your Bank Accounts. Here's What That Actually Means"],
  ["/articles/59-ai-electric-grid-bottleneck.html","business","The AI Wall Is the Electric Grid, Not the Algorithm"],
  ["/articles/58-openai-fifty-fifty-survival.html","business","OpenAI Has a 50-50 Chance of Not Existing by Next Summer"],
  ["/articles/57-anthropic-cfo-ai-arms-race-economics.html","business","Anthropic's CFO Just Revealed the Real Economics of the AI Arms Race"],
  ["/articles/56-meter-chart-ai-progress-lie.html","agents","The Meter Chart Is Lying to You About AI Progress"],
  ["/articles/55-icc-prompt-formula.html","tools","Stop Writing Bad Prompts: The ICC Formula That Actually Works"],
  ["/articles/54-skills-company-infrastructure.html","business","Your AI Skills Are No Longer Yours — They're Company Infrastructure Now"],
  ["/articles/53-seven-skills-ai-agent-engineers.html","tools","The 7 Skills That Separate AI Agent Builders from Prompt Engineers"],
  ["/articles/53-hyperagent-built-aether-intel.html","tools","How I Built a 52-Article AI News Site Using Only Hyperagent"],
  ["/articles/52-ceo-ai-delusion-loop.html","business","The CEO Sycophancy Trap: How AI Is Telling Executives Exactly What They"],
  ["/articles/51-consumer-ai-anticipation-gap.html","agents","The Anticipation Gap: Why Consumer AI Is Still Waiting for You to Manage"],
  ["/articles/49-ai-chatbot-delusion-mental-health.html","tools","The AI That Made People Delusional"],
  ["/articles/50-physical-ai-sensor-infrastructure-gap.html","agents","The Sensor Gap Killing Physical AI"],
  ["/articles/48-ai-layoff-reversal-klarna.html","business","The Companies That Fired Workers for AI Are Now Begging Them to Come Bac"],
  ["/articles/47-ai-bubble-missing-demand.html","business","Ed Zitron Went Looking for AI's Customers. He Found Almost None."],
  ["/articles/46-ai-agents-attention-bottleneck.html","agents","AI Agents Made You The Project Manager. That's The Problem."],
  ["/articles/45-free-ai-video-editing-stack.html","tools","The Free AI Video Stack: Replace $200/Month of Editing Tools With ChatGP"],
  ["/articles/44-openclaw-multi-model-unlock.html","dev","Your AI Agent Is Locked to One Model. That's a Liability."],
  ["/articles/43-hermes-vs-openclaw-agent-war.html","agents","Hermes Might Have Just Killed OpenClaw: The AI Agent War Nobody Expected"],
  ["/articles/42-codex-openai-real-agent.html","agents","Codex Is No Longer a Coding Tool. OpenAI Quietly Launched Its Real Agent"],
  ["/articles/41-chatgpt-gps-protocol-sycophancy.html","dev","ChatGPT Is a People Pleaser. The GPS Protocol Fixes That."],
  ["/articles/40-ai-search-kills-google-seo.html","business","Your #1 Google Rank Means Nothing to ChatGPT"],
  ["/articles/39-model-routing-cost-collapse.html","dev","The $8 Agent vs. the $400 Agent"],
  ["/articles/claude-mythos-hacking-ai.html","agents","Claude Mythos: The AI That Cracked Your Browser"],
  ["/articles/35-ai-labs-mckinsey-mode.html","business","The Model Was Never the Hard Part"],
  ["/articles/36-ai-agent-breaks-on-update.html","dev","Why Your AI Agent Breaks Every Time You Update It"],
  ["/articles/38-agentic-development-loop.html","agents","The Agentic Development Loop: How AI Is Closing the Gap Between Idea and"],
  ["/articles/37-hermes-infrastructure-24-7.html","agents","Hermes as Infrastructure, Not Chatbot: The 24/7 AI Employee Architecture"],
  ["/articles/34-jack-clark-ai-builds-itself-2028.html","society","Anthropic Co-Founder's 60%+ Prediction: AI Builds Itself by 2028"],
  ["/articles/33-claude-code-80x-anthropic-infrastructure.html","business","Claude Code Up 80x, Anthropic Accidentally Became the Infrastructure Com"],
  ["/articles/32-ai-procurement-hack-lily-mckinsey.html","dev","The $20 Hack That Broke Every AI Procurement Checklist"],
  ["/articles/31-anthropic-reads-claudes-mind.html","agents","Anthropic Can Read Claude's Mind, And It Knows When It's Being Tested"],
  ["/articles/30-ai-sycophancy-mental-health-crisis.html","society","AI Was Built to Make You Feel Good. That's Turning Into a Mental Health"],
  ["/articles/29-ai-backlash-america-hates-ai.html","society","America Hates AI and Can't Stop Using It: The Backlash by the Numbers"],
  ["/articles/28-chatgpt-ghost-workers-hidden-labor.html","society","The Ghost Workers Powering ChatGPT: Inside AI's Hidden Labor Economy"],
  ["/articles/27-ai-slop-human-touch-content.html","business","Why \"AI Slop\" Is Losing the Internet: The Human-Touch Content Divide"],
  ["/articles/26-ai-passive-income-reality-check.html","business","The AI Passive Income Fantasy vs. Reality: Why the Dream Keeps Failing"],
  ["/articles/25-vibe-coders-senior-engineer-exodus.html","dev","\"I'm Quitting My Job Due to Vibe Coders.\" The AI Coding Crisis Driving"],
  ["/articles/24-openclaw-self-hosting-reality.html","agents","Self-Hosting OpenClaw Was Supposed to Give You Control. Here's What You"],
  ["/articles/01-hermes-agent-complete-guide.html","agents","Hermes Agent: The Complete Guide to Setup, Skills, and Making Money in 2"],
  ["/articles/04-ai-automation-agency-guide.html","business","How to Start an AI Automation Agency in 2026: The Complete AAA Playbook"],
  ["/articles/02-12-ways-make-money-ai-2025.html","business","12 Proven Ways to Make Money With AI in 2026 (With Real Income Numbers)"],
  ["/articles/14-openrouter-guide.html","tools","OpenRouter: The Complete Guide to Accessing Every AI Model From One API"],
  ["/articles/20-hermes-agent-vs-chatgpt.html","agents","Hermes Agent vs ChatGPT: Why Persistent Memory Changes Everything"],
  ["/articles/13-ai-passive-income-guide.html","business","AI Passive Income in 2026: The Honest Guide (What Works, What Doesn't)"],
  ["/articles/06-how-to-make-money-with-openclaw.html","agents","How to Make Money With OpenClaw in 2026: 8 Proven Methods"],
  ["/articles/07-hermes-vs-openclaw-vs-claude-code.html","agents","Hermes Agent vs OpenClaw vs Claude Code: The Ultimate 2026 AI Agent Comp"],
  ["/articles/05-best-free-ai-tools-2025.html","tools","The Best Free AI Tools in 2026: What Actually Works (And What's Hype)"],
  ["/articles/11-hermes-agent-skills-guide.html","agents","Hermes Agent Skills System: Complete Guide to Building, Using, and Shari"],
  ["/articles/16-ai-tools-for-content-creators.html","tools","The Best AI Tools for Content Creators in 2026: A Practical Stack Guide"],
  ["/articles/10-n8n-beginners-guide.html","automation","n8n for Beginners: The Complete Guide to AI Workflow Automation (2026)"],
  ["/articles/09-hermes-agent-telegram-setup.html","automation","Hermes Agent Telegram Setup: Complete Tutorial (2026)"],
  ["/articles/17-hermes-agent-cost-guide.html","agents","How Much Does Hermes Agent Actually Cost? Real Breakdown for 2026"],
  ["/articles/12-openclaw-setup-guide.html","agents","OpenClaw Setup Guide: Install, Configure, and Run Your First Automation"],
  ["/articles/08-ai-content-website-make-money.html","business","How to Build an AI Content Website That Actually Makes Money"],
  ["/articles/18-ai-agent-morning-briefing.html","tools","How to Build an AI Morning Briefing System With Hermes Agent"],
  ["/articles/03-hermes-vs-openclaw.html","agents","Hermes Agent vs OpenClaw: Which AI Agent Should You Use in 2026?"],
  ["/articles/15-vibe-coding-make-money.html","business","Vibe Coding: How to Build and Sell AI-Generated Apps Without Knowing How"],
  ["/articles/19-ai-freelancing-guide.html","business","How to Freelance With AI in 2026: Earn More, Work Less, Deliver Better"],
  ["/articles/klarnas-100m-disaster.html","business","Klarna's $100M Disaster: What Every Business Can Learn About AI Deployme"],
  ["/articles/why-95-percent-ai-projects-fail.html","business","Why 95% of AI Projects Fail (And the 5% That Don't)"],
  ["/articles/sycophancy-trap.html","agents","The Sycophancy Trap: Why Your AI Assistant Is Lying to You"],
  ["/articles/ai-hiring-boomerang.html","business","The AI Hiring Boomerang: Companies Are Rehiring the Humans They Replaced"],
  ["/articles/reading-ais-mind.html","agents","AI Can Read Your Mind — Here's Exactly How Far It's Gone"],
  ["/articles/recursive-self-improvement.html","agents","Recursive Self-Improvement: The AI Capability That Changes Everything"],
  ["/articles/ai-debt-bomb.html","business","The AI Debt Bomb: $700 Billion In, $30 Billion Out"],
  ["/articles/cyber-psychosis.html","agents","Cyber Psychosis: What Happens to Your Brain When You Outsource Thinking"],
  ["/articles/21-ai-coding-tools-security-crisis.html","dev","AI Coding Tools Are Leaking Your Secrets — Here's the Data"],
  ["/articles/22-ai-agent-true-cost-guide.html","business","The Real Cost of Running AI Agents in 2026: What Nobody Tells You"],
  ["/articles/23-openclaw-security-audit.html","dev","OpenClaw's Security Problem: 2,000 CVEs, Plaintext Keys, and a Marketpla"]
  ];


  /**
   * Wraps the existing <main> content inside the full app shell.
   * Injects scroll-progress, sidebar, main-content wrapper, mobile nav, now-bar.
   */
  function injectAppShell() {
    const body = document.body;

    // New-template standalone articles already have a full .app-shell in HTML.
    // Skip full injection for these pages but still add supplementary elements.
    if (body.querySelector('.app-shell')) {
      if (!body.querySelector('.scroll-progress')) {
        var sp = document.createElement('div');
        sp.className = 'scroll-progress';
        body.prepend(sp);
      }
      if (!body.querySelector('.mobile-bottom-nav')) {
        var mnw = document.createElement('div');
        mnw.innerHTML = MOBILE_NAV_HTML.trim();
        body.appendChild(mnw.firstElementChild);
      }
      if (!body.querySelector('.now-bar')) {
        var nbw = document.createElement('div');
        nbw.innerHTML = NOW_BAR_HTML.trim();
        body.appendChild(nbw.firstElementChild);
      }
      return;
    }

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
    if (p.includes('/agents')) return 'agents';
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

    // Badge colour map — keyed to the badge strings in ticker.json
    var BADGE_STYLE = {
      'NEWS':        'color:#f472b6;border-color:rgba(244,114,182,.45)',
      'HONEST TAKE': 'color:#f87171;border-color:rgba(248,113,113,.45)',
      'BUSINESS':    'color:#f59e0b;border-color:rgba(245,158,11,.45)',
      'BIG PICTURE': 'color:#fbbf24;border-color:rgba(251,191,36,.45)',
      'TOOLS':       'color:#22d3ee;border-color:rgba(34,211,238,.45)',
      'AGENTS':      'color:#818cf8;border-color:rgba(129,140,248,.45)',
      'AI SAFETY':   'color:#f87171;border-color:rgba(248,113,113,.45)',
      'ANALYSIS':    'color:#c084fc;border-color:rgba(192,132,252,.45)',
      'AI':          'color:#38bdf8;border-color:rgba(56,189,248,.45)'
    };

    function buildTickerHTML(items) {
      // Duplicate content for seamless CSS loop (animation moves translateX(-50%))
      var html = '';
      for (var copy = 0; copy < 2; copy++) {
        for (var i = 0; i < items.length; i++) {
          var item = items[i];
          var labelHtml = '';
          if (item.badge) {
            var bs = BADGE_STYLE[item.badge] || 'color:#818cf8;border-color:rgba(129,140,248,.45)';
            labelHtml = '<span class="ticker-badge" style="' + bs + '">' + item.badge + '</span>';
          } else if (item.tag) {
            labelHtml = '<strong style="color:var(--neon-gold);margin-right:6px">' + item.tag + '</strong>';
          }
          html += '<span class="ticker-item">' + labelHtml + item.text + '</span>';
          html += '<span class="ticker-sep">◆</span>';
        }
      }
      return html;
    }

    // Set animation duration so ticker scrolls at a comfortable ~55px/second
    // regardless of how many items are loaded.
    var TICKER_PX_PER_SEC = 55;
    function setTickerSpeed() {
      requestAnimationFrame(function () {
        var halfWidth = tickerTrack.scrollWidth / 2; // one copy's worth
        if (halfWidth < 100) return; // not rendered yet, skip
        var dur = Math.max(20, halfWidth / TICKER_PX_PER_SEC);
        tickerTrack.style.animationDuration = dur.toFixed(1) + 's';
      });
    }

    // Paint default items immediately — ticker is never blank
    tickerTrack.innerHTML = buildTickerHTML(defaultItems);
    setTickerSpeed();

    // Then try to fetch fresh headlines and swap in if available
    fetch('/data/ticker.json')
      .then(function (res) {
        if (!res.ok) throw new Error('ticker.json unavailable');
        return res.json();
      })
      .then(function (data) {
        if (data.items && data.items.length) {
          // Stop animation before DOM swap to prevent transform-width mismatch glitch
          tickerTrack.style.animation = 'none';
          tickerTrack.innerHTML = buildTickerHTML(data.items);
          void tickerTrack.offsetWidth; // force reflow so animation truly resets
          tickerTrack.style.animation = ''; // hand control back to CSS
          setTickerSpeed();
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


    // ── Related articles helpers ──
    function getRelatedArticles(currentPath, count) {
      var category = 'news';
      for (var i = 0; i < ARTICLES_MANIFEST.length; i++) {
        if (ARTICLES_MANIFEST[i][0] === currentPath) {
          category = ARTICLES_MANIFEST[i][1];
          break;
        }
      }
      var pool = [];
      for (var j = 0; j < ARTICLES_MANIFEST.length; j++) {
        var a = ARTICLES_MANIFEST[j];
        if (a[1] === category && a[0] !== currentPath && a[2]) pool.push(a);
      }
      // Fisher-Yates shuffle
      for (var k = pool.length - 1; k > 0; k--) {
        var r = Math.floor(Math.random() * (k + 1));
        var tmp = pool[k]; pool[k] = pool[r]; pool[r] = tmp;
      }
      return pool.slice(0, count);
    }

    var CAT_LABELS = {
      news:'News', business:'Business', agents:'Agents',
      tools:'Tools', dev:'Dev & Security', automation:'Automation', society:'Society'
    };

    function buildRelatedHtml(articles, category) {
      if (!articles.length) return '';
      var catLabel = CAT_LABELS[category] || 'Related';
      var cards = articles.map(function (a) {
        var imgUrl = a[0].replace('/articles/', '/images/articles/').replace('.html', '.webp');
        var safeTitle = a[2].replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
        return '<a href="' + a[0] + '" class="ae-related-card">' +
          '<img class="ae-related-thumb" src="' + imgUrl + '" alt="" loading="lazy" onerror="this.hidden=true">' +
          '<span class="ae-related-title">' + safeTitle + '</span>' +
          '</a>';
      }).join('');
      return '<section class="ae-related">' +
        '<div class="ae-related-head">' +
          '<span class="ae-related-label">More like this</span>' +
          '<span class="ae-related-cat">' + catLabel + '</span>' +
        '</div>' +
        '<div class="ae-related-grid">' + cards + '</div>' +
        '</section>';
    }

    // ── Derive hero image URL from article URL ──
    // Pattern: /articles/50-slug.html → /images/articles/50-slug.webp
    function heroUrlFor(articleUrl) {
      try {
        var path = new URL(articleUrl).pathname;
        return path.replace('/articles/', '/images/articles/').replace('.html', '.webp');
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

          // Hide the article's own .article-hero while the panel hero loads above it.
          // If the panel hero fails (404), restore the article hero as fallback.
          var articleHero = bodyEl.querySelector('.ae-panel-article .article-hero');
          var panelHero   = bodyEl.querySelector('.ae-panel-hero');
          if (articleHero && panelHero) {
            articleHero.style.display = 'none';
            panelHero.addEventListener('error', function () {
              if (articleHero) articleHero.style.display = '';
            });
          }

          // Make any scroll-reveal elements immediately visible inside panel
          bodyEl.querySelectorAll('.reveal, .reveal-scale, .reveal-stagger').forEach(function (el) {
            el.classList.add('visible');
          });

          // Scroll panel body to top
          bodyEl.scrollTop = 0;
          // Inject "More like this" related articles section
          try {
            var relPath = new URL(url).pathname;
            var relArticles = getRelatedArticles(relPath, 3);
            var relCat = 'news';
            for (var ri = 0; ri < ARTICLES_MANIFEST.length; ri++) {
              if (ARTICLES_MANIFEST[ri][0] === relPath) { relCat = ARTICLES_MANIFEST[ri][1]; break; }
            }
            var relHtml = buildRelatedHtml(relArticles, relCat);
            if (relHtml) bodyEl.insertAdjacentHTML('beforeend', relHtml);
          } catch (relErr) {}

          // Buy Me a Coffee — always at the very end of every article
          bodyEl.insertAdjacentHTML('beforeend', BMC_HTML);
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
            var title = (el.querySelector('h2, h3, .article-card-title, .ae-related-title') || {}).textContent || 'Article';
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
  // ARTICLE BACK NAVIGATION (new-template articles with img.article-hero)
  // ---------------------------------------------------------------------------

  /**
   * For new-template articles that use <img class="article-hero"> directly,
   * wraps the image in a relative container and overlays a back-navigation link.
   * The back URL is derived from document.referrer (same origin) or defaults
   * to /articles.html.
   */
  function injectArticleBackNav() {
    var heroImg = document.querySelector('img.article-hero');
    if (!heroImg) return;

    // Wrap img in a positioned container so we can overlay the back link
    var wrap = document.createElement('div');
    wrap.className = 'article-hero-wrap';
    heroImg.parentNode.insertBefore(wrap, heroImg);
    wrap.appendChild(heroImg);

    // Determine back URL: prefer same-origin referrer, fallback to articles
    var backUrl = '/articles.html';
    var backLabel = '← Articles';
    try {
      if (document.referrer) {
        var ref = new URL(document.referrer);
        if (ref.hostname === location.hostname && ref.pathname !== location.pathname) {
          backUrl = ref.pathname + (ref.search || '');
          if (ref.pathname === '/' || ref.pathname === '/index.html') {
            backLabel = '← Home';
          } else {
            backLabel = '← Back';
          }
        }
      }
    } catch (e) {}

    // Create and append the overlay back-nav
    var backNav = document.createElement('div');
    backNav.className = 'article-back-nav';
    var backLink = document.createElement('a');
    backLink.href = backUrl;
    backLink.className = 'article-back-btn';
    backLink.textContent = backLabel;
    backNav.appendChild(backLink);
    wrap.appendChild(backNav);
  }

  // ---------------------------------------------------------------------------
  // ---------------------------------------------------------------------------
  // BUY ME A COFFEE — standalone article pages
  // Appends the BMC section after the article body when visiting an article
  // URL directly (not via the AePanel, which injects it separately).
  // ---------------------------------------------------------------------------
  function injectBMC() {
    var isArticle = document.body.classList.contains('standalone-nav') ||
                    !!document.querySelector('main.article-page');
    if (!isArticle) return;
    // Don't double-inject if already present
    if (document.querySelector('.ae-bmc')) return;
    var target = document.querySelector('main') ||
                 document.querySelector('.article-page') ||
                 document.querySelector('article');
    if (!target) return;
    target.insertAdjacentHTML('beforeend', BMC_HTML);
  }

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
    injectArticleBackNav(); // Back nav for new-template articles
    injectBMC();            // Buy Me a Coffee at end of article
    initArticlePanel();     // Spotify swipe-up reader
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

  // ---------------------------------------------------------------------------
  // SHARE MODULE LOADER  (DO NOT REMOVE — required for the share UI on every
  // article, agent, skill, and landing page. Removing this kills the share
  // button site-wide. See /js/share.js for the implementation.)
  // ---------------------------------------------------------------------------
  (function loadShare() {
    if (document.querySelector('script[data-ae-share]')) return;
    var s = document.createElement('script');
    s.src = '/js/share.js';
    s.defer = true;
    s.setAttribute('data-ae-share', '1');
    document.head.appendChild(s);
  }());

}());
