const CACHE_NAME = 'pygame-pwa-cache-v4';
const PRECACHE_URLS = [
    './',
    './index.html',
    './favicon.png',
    './manifest.json',
    './favicons/favicon-192x192.png',
    './pwa.apk'
];

self.addEventListener('install', event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_URLS))
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(self.clients.claim());
});

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;

    event.respondWith(
        fetch(event.request)
            .then(response => {
                // Cache successful GET requests for offline use
                if (response && (response.status === 200 || response.type === 'opaque')) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
            .catch(() => {
                // Fallback to cache if network fails (offline mode)
                return caches.match(event.request, { ignoreSearch: true });
            })
    );
});
