const CACHE_NAME = 'pygame-pwa-cache-1778395042';
const PRECACHE_URLS = [
    './',
    './favicon.png',
    './index.html',
    './manifest.json',
    './pwa.apk',
    './pwa.tar.gz'
];

self.addEventListener('install', event => {
    self.skipWaiting();
    event.waitUntil(
        caches.open(CACHE_NAME).then(cache => cache.addAll(PRECACHE_URLS))
    );
});

self.addEventListener('activate', event => {
    // 2. Cache Cleanup: Delete old versions of the cache
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME && cacheName.startsWith('pygame-pwa-cache-')) {
                        return caches.delete(cacheName);
                    }
                })
            );
        }).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;

    event.respondWith(
        // 3. Cache-First Strategy
        caches.match(event.request, { ignoreSearch: true }).then(cachedResponse => {
            if (cachedResponse) {
                return cachedResponse; // Instant load from cache!
            }
            
            // Fallback to network if not in cache
            return fetch(event.request).then(response => {
                if (response && (response.status === 200 || response.type === 'opaque')) {
                    const responseClone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, responseClone);
                    });
                }
                return response;
            })
        })
    );
});
