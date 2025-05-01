// Service Worker for offline capabilities
const CACHE_NAME = 'credit-risk-app-v1';
const urlsToCache = [
    '/',
    '/static/css/custom.css',
    '/static/js/scripts.js',
    '/static/js/validation.js',
    '/static/js/charts.js',
    '/login',
    '/register',
    '/forgot_password',
    'https://cdn.replit.com/agent/bootstrap-agent-dark-theme.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'https://cdn.jsdelivr.net/npm/chart.js',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js'
];

// Install event - cache all initial resources
self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - serve from cache first, then network
self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Cache hit - return response
                if (response) {
                    return response;
                }

                // Clone the request because it's a one-time use
                const fetchRequest = event.request.clone();

                return fetch(fetchRequest)
                    .then(function(response) {
                        // Check if we received a valid response
                        if (!response || response.status !== 200 || response.type !== 'basic') {
                            return response;
                        }

                        // Clone the response because it's a one-time use
                        const responseToCache = response.clone();

                        // Open the cache and put the new response in it
                        caches.open(CACHE_NAME)
                            .then(function(cache) {
                                // Skip caching API responses
                                if (!event.request.url.includes('/api/')) {
                                    cache.put(event.request, responseToCache);
                                }
                            });

                        return response;
                    })
                    .catch(function(err) {
                        // For navigation requests, serve index page as fallback
                        if (event.request.mode === 'navigate') {
                            return caches.match('/');
                        }
                        
                        console.log('Fetch error:', err);
                        // For failed image requests, could serve a default image
                        // For failed API requests, could return default data
                    });
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', function(event) {
    const cacheWhitelist = [CACHE_NAME];

    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.map(function(cacheName) {
                    if (cacheWhitelist.indexOf(cacheName) === -1) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Handle offline page requests
self.addEventListener('fetch', function(event) {
    // Serve offline page for navigations when offline
    if (event.request.mode === 'navigate' && !navigator.onLine) {
        event.respondWith(
            caches.match('/')
                .then(function(response) {
                    return response || fetch(event.request);
                })
        );
    }
});

// Listen for messages from the main thread
self.addEventListener('message', function(event) {
    if (event.data.action === 'skipWaiting') {
        self.skipWaiting();
    }
});
