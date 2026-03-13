const CACHE_NAME = 'moodtunes-v1';

// App shell assets to cache on install
const APP_SHELL = [
    '/',
    '/static/music/css/main.css',
    '/static/music/js/player.js',
    '/static/music/manifest.json',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css'
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(APP_SHELL);
            })
    );
});

self.addEventListener('fetch', event => {
    // Skip cross-origin requests, like those for audio files if hosted externally,
    // or keep it simple and cache everything locally.

    // For HTML pages and static assets, use Network First strategy, fallback to Cache
    if (event.request.method === 'GET') {
        event.respondWith(
            fetch(event.request)
                .then(response => {
                    // Check if we received a valid response
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // Clone the response because it's a stream and can only be consumed once
                    const responseToCache = response.clone();

                    // Only cache pages and static files, skip caching large audio files
                    if (!event.request.url.includes('/media/songs/')) {
                        caches.open(CACHE_NAME)
                            .then(cache => {
                                cache.put(event.request, responseToCache);
                            });
                    }

                    return response;
                })
                .catch(() => {
                    // Network failed, try to serve from cache
                    return caches.match(event.request).then(cachedResponse => {
                        if (cachedResponse) {
                            return cachedResponse;
                        }
                        // If checking for a page and not in cache, we could return an offline.html here
                        // For API calls, return a custom JSON offline message
                        if (event.request.headers.get('accept').includes('text/html')) {
                            // Offline fallback for HTML
                            return caches.match('/'); // Return home page as fallback
                        }
                    });
                })
        );
    }
});

self.addEventListener('activate', event => {
    // Clean up old caches
    const cacheWhitelist = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheWhitelist.indexOf(cacheName) === -1) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
