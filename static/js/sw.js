// Service Worker for Progressive Web App functionality
const CACHE_NAME = 'bookdine-v1.0.0';
const urlsToCache = [
    '/',
    '/static/css/custom.css',
    '/static/js/booking.js',
    '/static/images/logo.png',
    '/static/images/default-restaurant.jpg',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css'
];

// Install event - cache resources
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
    );
});

// Fetch event - serve from cache when offline
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Return cached version or fetch from network
                if (response) {
                    return response;
                }
                
                return fetch(event.request).then(response => {
                    // Check if valid response
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }
                    
                    // Clone the response
                    const responseToCache = response.clone();
                    
                    caches.open(CACHE_NAME)
                        .then(cache => {
                            cache.put(event.request, responseToCache);
                        });
                    
                    return response;
                });
            })
            .catch(() => {
                // Return offline page for navigation requests
                if (event.request.destination === 'document') {
                    return caches.match('/offline.html');
                }
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        console.log('Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});

// Background sync for offline reservations
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync-reservation') {
        event.waitUntil(syncReservations());
    }
});

async function syncReservations() {
    try {
        // Get pending reservations from IndexedDB
        const pendingReservations = await getPendingReservations();
        
        for (const reservation of pendingReservations) {
            try {
                const response = await fetch('/api/reservations/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': reservation.csrfToken
                    },
                    body: JSON.stringify(reservation.data)
                });
                
                if (response.ok) {
                    // Remove from pending list
                    await removePendingReservation(reservation.id);
                    
                    // Show success notification
                    self.registration.showNotification('Reservation Confirmed', {
                        body: 'Your reservation has been successfully created!',
                        icon: '/static/images/icon-192x192.png',
                        badge: '/static/images/badge-72x72.png'
                    });
                }
            } catch (error) {
                console.error('Failed to sync reservation:', error);
            }
        }
    } catch (error) {
        console.error('Background sync failed:', error);
    }
}

// Push notifications
self.addEventListener('push', event => {
    const options = {
        body: event.data ? event.data.text() : 'New notification',
        icon: '/static/images/icon-192x192.png',
        badge: '/static/images/badge-72x72.png',
        vibrate: [100, 50, 100],
        data: {
            dateOfArrival: Date.now(),
            primaryKey: 1
        },
        actions: [
            {
                action: 'explore',
                title: 'View Details',
                icon: '/static/images/checkmark.png'
            },
            {
                action: 'close',
                title: 'Close',
                icon: '/static/images/xmark.png'
            }
        ]
    };
    
    event.waitUntil(
        self.registration.showNotification('BookDine', options)
    );
});

// Notification click handling
self.addEventListener('notificationclick', event => {
    event.notification.close();
    
    if (event.action === 'explore') {
        event.waitUntil(
            clients.openWindow('/reservations/')
        );
    }
});

// Helper functions for IndexedDB operations
async function getPendingReservations() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('BookDineDB', 1);
        
        request.onerror = () => reject(request.error);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['pendingReservations'], 'readonly');
            const store = transaction.objectStore('pendingReservations');
            const getAllRequest = store.getAll();
            
            getAllRequest.onsuccess = () => resolve(getAllRequest.result);
            getAllRequest.onerror = () => reject(getAllRequest.error);
        };
        
        request.onupgradeneeded = () => {
            const db = request.result;
            if (!db.objectStoreNames.contains('pendingReservations')) {
                db.createObjectStore('pendingReservations', { keyPath: 'id' });
            }
        };
    });
}

async function removePendingReservation(id) {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open('BookDineDB', 1);
        
        request.onsuccess = () => {
            const db = request.result;
            const transaction = db.transaction(['pendingReservations'], 'readwrite');
            const store = transaction.objectStore('pendingReservations');
            const deleteRequest = store.delete(id);
            
            deleteRequest.onsuccess = () => resolve();
            deleteRequest.onerror = () => reject(deleteRequest.error);
        };
    });
}