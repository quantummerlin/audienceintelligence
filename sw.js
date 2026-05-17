/**
 * Aether Intel — Service Worker
 * Strategy: network-first for HTML, cache-first for static assets
 * Version: auto-stamped at build time via CACHE_VERSION
 */

const CACHE_VERSION = 'aether-v1';
const STATIC_CACHE  = `${CACHE_VERSION}-static`;
const PAGE_CACHE    = `${CACHE_VERSION}-pages`;

// Assets to pre-cache on install (app shell)
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/css/style.css',
  '/js/main.js',
  '/images/icons/icon-192.png',
  '/images/icons/icon-512.png',
  '/manifest.json',
];

// Static asset patterns → cache-first
const STATIC_PATTERNS = [
  /\.(css|js|woff2?|ttf|otf)(\?.*)?$/,
  /\.(png|jpg|jpeg|webp|avif|svg|gif|ico)(\?.*)?$/,
  /fonts\.googleapis\.com/,
  /fonts\.gstatic\.com/,
];

// Pages to exclude from caching (never stale)
const NO_CACHE_PATTERNS = [
  /\/api\//,
  /\/admin\//,
];

// ─── Install ────────────────────────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(PRECACHE_ASSETS))
      .then(() => self.skipWaiting())
      .catch(err => {
        // Don't fail install if a precache asset is missing
        console.warn('[SW] Precache partial failure:', err);
      })
  );
});

// ─── Activate ───────────────────────────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(key => key.startsWith('aether-') && key !== STATIC_CACHE && key !== PAGE_CACHE)
          .map(key => {
            console.log('[SW] Deleting old cache:', key);
            return caches.delete(key);
          })
      )
    ).then(() => self.clients.claim())
  );
});

// ─── Fetch ───────────────────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Only handle same-origin + trusted font CDNs
  const isSameOrigin   = url.origin === self.location.origin;
  const isFontCDN      = /fonts\.(googleapis|gstatic)\.com/.test(url.hostname);
  if (!isSameOrigin && !isFontCDN) return;

  // Never cache these patterns
  if (NO_CACHE_PATTERNS.some(p => p.test(url.pathname))) return;

  // Static assets → cache-first, fallback to network
  if (STATIC_PATTERNS.some(p => p.test(url.href))) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  // HTML navigation → network-first, fallback to cache
  if (request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(networkFirst(request, PAGE_CACHE));
    return;
  }

  // Everything else → network with cache fallback
  event.respondWith(networkFirst(request, STATIC_CACHE));
});

// ─── Strategies ──────────────────────────────────────────────────────────────

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('Asset unavailable offline', { status: 503 });
  }
}

async function networkFirst(request, cacheName) {
  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    const cached = await caches.match(request);
    if (cached) return cached;
    // Offline fallback for navigations
    if (request.mode === 'navigate') {
      const fallback = await caches.match('/');
      if (fallback) return fallback;
    }
    return new Response('You appear to be offline.', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// ─── Push notifications (future) ─────────────────────────────────────────────
self.addEventListener('push', event => {
  if (!event.data) return;
  const data = event.data.json();
  event.waitUntil(
    self.registration.showNotification(data.title || 'Æther Intel', {
      body: data.body || 'New AI signal detected.',
      icon: '/images/icons/icon-192.png',
      badge: '/images/icons/favicon-32.png',
      tag: 'aether-signal',
      renotify: true,
      data: { url: data.url || '/' }
    })
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  event.waitUntil(
    clients.openWindow(event.notification.data?.url || '/')
  );
});
