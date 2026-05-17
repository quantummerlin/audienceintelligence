/**
 * Aether Intel — Service Worker v11
 * Strategy: network-first for HTML (never precache HTML), cache-first for static assets
 * v11: nukes ALL caches on activate (not just aether-*), adds updateViaCache safety
 */

const CACHE_VERSION = 'aether-v12';
const STATIC_CACHE  = `${CACHE_VERSION}-static`;
const PAGE_CACHE    = `${CACHE_VERSION}-pages`;

// Static assets only — HTML is NEVER precached so it's always fresh from network
const PRECACHE_ASSETS = [
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

// Never cache these paths
const NO_CACHE_PATTERNS = [
  /\/api\//,
  /\/admin\//,
  /\/cdn-cgi\//,   // Cloudflare infrastructure (RUM, challenge, analytics)
];

// ─── Install ────────────────────────────────────────────────────────────────
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(PRECACHE_ASSETS))
      .then(() => self.skipWaiting())
      .catch(err => {
        console.warn('[SW v11] Precache partial failure:', err);
        return self.skipWaiting();
      })
  );
});

// ─── Activate ───────────────────────────────────────────────────────────────
self.addEventListener('activate', event => {
  event.waitUntil(
    // Nuclear: delete ALL caches for this origin, not just aether-* ones
    // Eliminates any stale HTML/CSS that survived previous version bumps
    caches.keys()
      .then(keys =>
        Promise.all(
          keys
            .filter(key => key !== STATIC_CACHE && key !== PAGE_CACHE)
            .map(key => {
              console.log('[SW v11] Deleting cache:', key);
              return caches.delete(key);
            })
        )
      )
      .then(() => self.clients.claim())
  );
});

// ─── Fetch ───────────────────────────────────────────────────────────────────
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // Only handle GET requests — Cache API does not support POST/PUT/etc.
  if (request.method !== 'GET') return;

  // Only handle same-origin + trusted font CDNs
  const isSameOrigin = url.origin === self.location.origin;
  const isFontCDN    = /fonts\.(googleapis|gstatic)\.com/.test(url.hostname);
  if (!isSameOrigin && !isFontCDN) return;

  // Never intercept these paths (Cloudflare CDN infra, API routes, admin)
  if (NO_CACHE_PATTERNS.some(p => p.test(url.pathname))) return;

  // Static assets → cache-first, fallback to network
  if (STATIC_PATTERNS.some(p => p.test(url.href))) {
    event.respondWith(cacheFirst(request, STATIC_CACHE));
    return;
  }

  // HTML navigation → network-first, NO cache fallback for HTML
  // We NEVER serve stale HTML — if network fails, show offline message
  if (request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(networkOnlyWithFallback(request, PAGE_CACHE));
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

// For HTML: always go to network. Cache the response for offline only.
// CRITICALLY: only cache if response is actually ok HTML (guards against Cloudflare challenge pages)
async function networkOnlyWithFallback(request, cacheName) {
  try {
    const response = await fetch(request);
    // Only cache genuine HTML responses — skip challenge pages, redirects, errors
    const ct = response.headers.get('content-type') || '';
    if (response.ok && ct.includes('text/html')) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    // Offline: try cache
    const cached = await caches.match(request);
    if (cached) return cached;
    return new Response(
      '<!DOCTYPE html><html><body style="font-family:sans-serif;padding:2rem;background:#07070f;color:#e2e8f0">' +
      '<h2>You appear to be offline.</h2><p>Reconnect to view Aether Intel.</p></body></html>',
      { status: 503, headers: { 'Content-Type': 'text/html' } }
    );
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
    return new Response('You appear to be offline.', {
      status: 503,
      headers: { 'Content-Type': 'text/plain' }
    });
  }
}

// ─── Push notifications ─────────────────────────────────────────────────────
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
