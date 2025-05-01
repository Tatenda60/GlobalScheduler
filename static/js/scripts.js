// Main JavaScript file for the application

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Enable Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add event listener for form validation
    const forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Handle password visibility toggle
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(function(toggle) {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            const passwordField = document.querySelector(toggle.getAttribute('data-target'));
            
            if (passwordField.type === 'password') {
                passwordField.type = 'text';
                toggle.querySelector('i').classList.remove('fa-eye');
                toggle.querySelector('i').classList.add('fa-eye-slash');
            } else {
                passwordField.type = 'password';
                toggle.querySelector('i').classList.remove('fa-eye-slash');
                toggle.querySelector('i').classList.add('fa-eye');
            }
        });
    });

    // Handle sidebar toggle on mobile
    const sidebarToggle = document.getElementById('sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function(e) {
            e.preventDefault();
            document.body.classList.toggle('sidebar-toggled');
            document.querySelector('.sidebar').classList.toggle('toggled');
        });
    }

    // Close sidebar on smaller screens when links are clicked
    const mediaQuery = window.matchMedia('(max-width: 768px)');
    if (mediaQuery.matches) {
        const sidebarLinks = document.querySelectorAll('.sidebar .nav-link');
        sidebarLinks.forEach(function(link) {
            link.addEventListener('click', function() {
                document.body.classList.remove('sidebar-toggled');
                document.querySelector('.sidebar').classList.remove('toggled');
            });
        });
    }
    
    // Initialize any active charts on the page
    initializeCharts();
});

// Function to format currency values
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2
    }).format(value);
}

// Function to format percentage values
function formatPercent(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'percent',
        minimumFractionDigits: 1,
        maximumFractionDigits: 1
    }).format(value);
}

// Function to initialize any charts
function initializeCharts() {
    // This will be implemented in charts.js
}

// Function to handle service worker registration for offline support
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/js/service-worker.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful with scope: ', registration.scope);
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed: ', error);
            });
    });
}

// Service worker for offline capabilities
const CACHE_NAME = 'credit-risk-app-v1';
const urlsToCache = [
    '/',
    '/static/css/custom.css',
    '/static/js/scripts.js',
    '/static/js/validation.js',
    '/static/js/charts.js',
    '/login',
    '/register'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request)
            .then(function(response) {
                // Cache hit - return response
                if (response) {
                    return response;
                }
                return fetch(event.request);
            })
    );
});

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
