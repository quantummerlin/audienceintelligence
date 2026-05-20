/**
 * share.js — Aether Intel universal share UI
 * Runs on every page after main.js. Auto-injects a share button into <article>
 * or <main>. On mobile triggers the native Web Share API. On desktop opens a
 * blurred-backdrop modal with six share targets:
 *   Copy link · X · LinkedIn · Reddit · Facebook · Telegram
 *
 * Reads share data from existing OG meta tags so it works site-wide without
 * any per-page wiring.
 */

(function () {
  'use strict';

  // ---------------------------------------------------------------------------
  // ICONS — inline SVG, no emoji, no external deps
  // ---------------------------------------------------------------------------
  const I = {
    share:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><line x1="8.59" y1="13.51" x2="15.42" y2="17.49"/><line x1="15.41" y1="6.51" x2="8.59" y2="10.49"/></svg>',
    copy:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>',
    check:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"/></svg>',
    x:
      '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
    linkedin:
      '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.852 3.37-1.852 3.601 0 4.267 2.37 4.267 5.455v6.288zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.063 2.063 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>',
    reddit:
      '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0zm5.01 4.744c.688 0 1.25.561 1.25 1.249a1.25 1.25 0 01-2.498.056l-2.597-.547-.8 3.747c1.824.07 3.48.632 4.674 1.488.308-.309.73-.491 1.207-.491.968 0 1.754.786 1.754 1.754 0 .716-.435 1.333-1.01 1.614a3.111 3.111 0 01.042.52c0 2.694-3.13 4.87-7.004 4.87-3.874 0-7.004-2.176-7.004-4.87 0-.183.015-.366.043-.534A1.748 1.748 0 014.028 12c0-.968.786-1.754 1.754-1.754.463 0 .898.196 1.207.49 1.207-.883 2.878-1.43 4.744-1.487l.885-4.182a.342.342 0 01.14-.197.35.35 0 01.238-.042l2.906.617a1.214 1.214 0 011.108-.701zM9.25 12C8.561 12 8 12.562 8 13.25c0 .687.561 1.248 1.25 1.248.687 0 1.248-.561 1.248-1.249 0-.688-.561-1.249-1.249-1.249zm5.5 0c-.687 0-1.248.561-1.248 1.25 0 .687.561 1.248 1.249 1.248.688 0 1.249-.561 1.249-1.249 0-.687-.562-1.249-1.25-1.249zm-5.466 3.99a.327.327 0 00-.231.094.33.33 0 000 .463c.842.842 2.484.913 2.961.913.477 0 2.105-.056 2.961-.913a.361.361 0 00.029-.463.33.33 0 00-.464 0c-.547.533-1.684.73-2.512.73-.828 0-1.979-.196-2.512-.73a.326.326 0 00-.232-.095z"/></svg>',
    facebook:
      '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>',
    telegram:
      '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M11.944 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0a12 12 0 00-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 01.171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/></svg>',
    close:
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="6"/></svg>',
  };

  // ---------------------------------------------------------------------------
  // Read share payload from OG meta tags (with sensible fallbacks)
  // ---------------------------------------------------------------------------
  function meta(name) {
    var el =
      document.querySelector('meta[property="' + name + '"]') ||
      document.querySelector('meta[name="' + name + '"]');
    return el ? el.getAttribute('content') : '';
  }

  function getShareData() {
    var title = meta('og:title') || document.title || 'Aether Intel';
    var text =
      meta('og:description') || meta('description') || '';
    var url = meta('og:url') || location.href;
    var image = meta('og:image') || '';
    return { title: title, text: text, url: url, image: image };
  }

  // ---------------------------------------------------------------------------
  // Share target URL builders
  // ---------------------------------------------------------------------------
  function targetUrl(kind, d) {
    var t = encodeURIComponent(d.title);
    var u = encodeURIComponent(d.url);
    var x = encodeURIComponent(d.text);
    switch (kind) {
      case 'x':
        return 'https://twitter.com/intent/tweet?text=' + t + '&url=' + u;
      case 'linkedin':
        return (
          'https://www.linkedin.com/sharing/share-offsite/?url=' + u
        );
      case 'reddit':
        return 'https://www.reddit.com/submit?url=' + u + '&title=' + t;
      case 'facebook':
        return 'https://www.facebook.com/sharer/sharer.php?u=' + u;
      case 'telegram':
        return 'https://t.me/share/url?url=' + u + '&text=' + t;
    }
    return '';
  }

  // ---------------------------------------------------------------------------
  // Copy link with toast
  // ---------------------------------------------------------------------------
  function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
      return navigator.clipboard.writeText(text);
    }
    return new Promise(function (resolve, reject) {
      try {
        var ta = document.createElement('textarea');
        ta.value = text;
        ta.style.position = 'fixed';
        ta.style.opacity = '0';
        document.body.appendChild(ta);
        ta.select();
        document.execCommand('copy');
        document.body.removeChild(ta);
        resolve();
      } catch (e) {
        reject(e);
      }
    });
  }

  function showToast(msg) {
    var toast = document.createElement('div');
    toast.className = 'ae-share-toast';
    toast.innerHTML =
      '<span class="ae-share-toast-icon">' + I.check + '</span>' +
      '<span>' + msg + '</span>';
    document.body.appendChild(toast);
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        toast.classList.add('is-visible');
      });
    });
    setTimeout(function () {
      toast.classList.remove('is-visible');
      setTimeout(function () {
        if (toast.parentNode) toast.parentNode.removeChild(toast);
      }, 240);
    }, 1800);
  }

  // ---------------------------------------------------------------------------
  // Modal
  // ---------------------------------------------------------------------------
  var modalEl = null;
  var lastFocus = null;

  function buildModal(d) {
    var imgHtml = d.image
      ? '<div class="ae-share-preview-img" style="background-image:url(\'' +
        d.image.replace(/'/g, "%27") +
        '\')"></div>'
      : '<div class="ae-share-preview-img is-empty"></div>';

    var targets = [
      { k: 'copy',     label: 'Copy link', icon: I.copy },
      { k: 'x',        label: 'X',         icon: I.x },
      { k: 'linkedin', label: 'LinkedIn',  icon: I.linkedin },
      { k: 'reddit',   label: 'Reddit',    icon: I.reddit },
      { k: 'facebook', label: 'Facebook',  icon: I.facebook },
      { k: 'telegram', label: 'Telegram',  icon: I.telegram },
    ];

    var grid = targets
      .map(function (t) {
        return (
          '<button class="ae-share-target" data-target="' + t.k + '" type="button" aria-label="Share to ' + t.label + '">' +
            '<span class="ae-share-target-icon ae-icon-' + t.k + '">' + t.icon + '</span>' +
            '<span class="ae-share-target-label">' + t.label + '</span>' +
          '</button>'
        );
      })
      .join('');

    var html =
      '<div class="ae-share-backdrop" data-share-close="1"></div>' +
      '<div class="ae-share-modal" role="dialog" aria-modal="true" aria-labelledby="ae-share-title">' +
        '<button class="ae-share-close" type="button" aria-label="Close share dialog" data-share-close="1">' + I.close + '</button>' +
        '<div class="ae-share-modal-head">' +
          '<span class="ae-share-eyebrow">Share signal</span>' +
          '<h2 id="ae-share-title" class="ae-share-modal-title">' + escapeHtml(d.title) + '</h2>' +
        '</div>' +
        '<div class="ae-share-preview">' +
          imgHtml +
          '<div class="ae-share-preview-url">' + escapeHtml(d.url) + '</div>' +
        '</div>' +
        '<div class="ae-share-grid">' + grid + '</div>' +
      '</div>';

    var wrap = document.createElement('div');
    wrap.className = 'ae-share-root';
    wrap.innerHTML = html;
    return wrap;
  }

  function escapeHtml(s) {
    return String(s)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function openModal() {
    if (modalEl) return;
    var d = getShareData();
    lastFocus = document.activeElement;
    modalEl = buildModal(d);
    document.body.appendChild(modalEl);
    document.body.classList.add('ae-share-open');

    // animate in
    requestAnimationFrame(function () {
      requestAnimationFrame(function () {
        modalEl.classList.add('is-visible');
      });
    });

    // wire up close
    modalEl.addEventListener('click', function (e) {
      if (e.target.closest('[data-share-close]')) closeModal();
    });

    // wire targets
    modalEl.addEventListener('click', function (e) {
      var btn = e.target.closest('.ae-share-target');
      if (!btn) return;
      var kind = btn.getAttribute('data-target');
      if (kind === 'copy') {
        copyToClipboard(d.url).then(
          function () {
            closeModal();
            showToast('Link copied');
          },
          function () { showToast('Copy failed'); }
        );
        return;
      }
      var url = targetUrl(kind, d);
      if (url) {
        window.open(url, '_blank', 'noopener,noreferrer');
      }
    });

    document.addEventListener('keydown', onKeydown);
  }

  function closeModal() {
    if (!modalEl) return;
    modalEl.classList.remove('is-visible');
    document.body.classList.remove('ae-share-open');
    document.removeEventListener('keydown', onKeydown);
    var el = modalEl;
    modalEl = null;
    setTimeout(function () {
      if (el && el.parentNode) el.parentNode.removeChild(el);
      if (lastFocus && lastFocus.focus) lastFocus.focus();
    }, 240);
  }

  function onKeydown(e) {
    if (e.key === 'Escape') closeModal();
  }

  // ---------------------------------------------------------------------------
  // Trigger — public API
  // ---------------------------------------------------------------------------
  function isMobile() {
    return (
      typeof navigator !== 'undefined' &&
      typeof navigator.share === 'function' &&
      /android|iphone|ipad|ipod|mobile/i.test(navigator.userAgent || '')
    );
  }

  function triggerShare() {
    var d = getShareData();
    if (isMobile()) {
      navigator
        .share({ title: d.title, text: d.text, url: d.url })
        .catch(function () { openModal(); });
      return;
    }
    openModal();
  }

  // ---------------------------------------------------------------------------
  // Auto-inject the share button
  // ---------------------------------------------------------------------------
  function shareButtonHtml() {
    return (
      '<div class="ae-share-row" role="group" aria-label="Share this page">' +
        '<div class="ae-share-row-label">' +
          '<span class="ae-share-row-dot" aria-hidden="true"></span>' +
          '<span>Share this signal</span>' +
        '</div>' +
        '<button type="button" class="ae-share-trigger" data-share-open="1">' +
          '<span class="ae-share-trigger-icon">' + I.share + '</span>' +
          '<span class="ae-share-trigger-label">Share</span>' +
        '</button>' +
      '</div>'
    );
  }

  function injectShareButton() {
    // Skip on pages that already have one
    if (document.querySelector('.ae-share-row')) return;

    var row = document.createElement('div');
    row.innerHTML = shareButtonHtml();
    var node = row.firstElementChild;

    // Prefer inside the article (article pages)
    var article = document.querySelector('article');
    if (article) {
      article.appendChild(node);
    } else {
      // Otherwise drop into <main> as the last meaningful element
      var main = document.querySelector('main, .main-content > section:last-of-type, .main-content');
      if (main) {
        main.appendChild(node);
      } else {
        return;
      }
    }

    node.addEventListener('click', function (e) {
      if (e.target.closest('[data-share-open]')) {
        triggerShare();
      }
    });
  }

  // Public API for any inline triggers added by other scripts
  window.AetherShare = {
    open: triggerShare,
    close: closeModal,
  };

  // Wire up after main.js shell injection completes
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectShareButton);
  } else {
    injectShareButton();
  }
})();
