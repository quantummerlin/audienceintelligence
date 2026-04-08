// Service Worker for Video Downloader PWA
// Caches the app shell for offline support and fast load.

const CACHE_NAME = 'viddown-v1';
const SHELL = [
  '/downloader.html',
  '/style.css',
  '/downloader-manifest.json',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(SHELL))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  // Only cache GET requests for the app shell; pass API calls straight through
  const url = new URL(event.request.url);
  const isShell = SHELL.some(path => url.pathname === path);

  if (event.request.method !== 'GET' || url.pathname.startsWith('/api/')) {
    return; // let the network handle it
  }

  event.respondWith(
    caches.match(event.request).then(cached => {
      const networkFetch = fetch(event.request).then(response => {
        if (isShell && response.ok) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(c => c.put(event.request, clone));
        }
        return response;
      });
      return cached || networkFetch;
    })
  );
});
