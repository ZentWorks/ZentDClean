const CACHE_PREFIX = "zentdclean-static-";
const CACHE_NAME = `${CACHE_PREFIX}7`;
const PRECACHE = [
  "/static/app.css?v=7",
  "/static/app.js?v=7",
  "/static/favicon.ico?v=7",
  "/static/icons/icon-64.png?v=7",
  "/static/icons/icon-192.png?v=7",
  "/static/icons/icon-512.png?v=7",
  "/static/icons/icon-maskable-192.png?v=7",
  "/static/icons/icon-maskable-512.png?v=7",
  "/static/icons/apple-touch-icon.png?v=7",
  "/manifest.webmanifest?v=7"
];

self.addEventListener("install", event => {
  event.waitUntil(caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE)));
  self.skipWaiting();
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(key => key.startsWith(CACHE_PREFIX) && key !== CACHE_NAME).map(key => caches.delete(key))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const request = event.request;
  if (request.method !== "GET") return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // Never cache pages or API responses. Authentication and Docker state must
  // always come from the live application.
  if (url.pathname.startsWith("/api/") || url.pathname === "/" || request.mode === "navigate") return;

  const cacheable = url.pathname.startsWith("/static/") || url.pathname === "/manifest.webmanifest";
  if (!cacheable) return;

  event.respondWith(
    caches.match(request).then(cached => cached || fetch(request).then(response => {
      if (response.ok) {
        const copy = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(request, copy));
      }
      return response;
    }))
  );
});
