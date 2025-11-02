const CACHE_NAME = 'seyma-sor-v1';
const urlsToCache = [
    '/seyma-sor/',
    '/static/seyma-sor-manifest.json',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
    'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;600;700&display=swap'
];

// Install event
self.addEventListener('install', event => {
    console.log('Şeyma\'ya Sor SW: Install event');
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => {
                console.log('Şeyma\'ya Sor SW: Caching files');
                return cache.addAll(urlsToCache.filter(url => !url.includes('fonts.googleapis.com')));
            })
            .catch(error => {
                console.error('Şeyma\'ya Sor SW: Cache failed', error);
            })
    );
    self.skipWaiting();
});

// Activate event
self.addEventListener('activate', event => {
    console.log('Şeyma\'ya Sor SW: Activate event');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME && cacheName.startsWith('seyma-sor-')) {
                        console.log('Şeyma\'ya Sor SW: Deleting old cache', cacheName);
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
    self.clients.claim();
});

// Fetch event
self.addEventListener('fetch', event => {
    // Sadece GET isteklerini ele al
    if (event.request.method !== 'GET') {
        return;
    }

    // API isteklerini cache'leme
    if (event.request.url.includes('/seyma-sor/') && event.request.method === 'POST') {
        return;
    }

    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Cache'den döndür veya network'ten fetch et
                if (response) {
                    return response;
                }

                return fetch(event.request).then(response => {
                    // Geçerli yanıt kontrolü
                    if (!response || response.status !== 200 || response.type !== 'basic') {
                        return response;
                    }

                    // Yanıtı klonla
                    const responseToCache = response.clone();

                    // Cache'e ekle
                    caches.open(CACHE_NAME)
                        .then(cache => {
                            cache.put(event.request, responseToCache);
                        });

                    return response;
                }).catch(() => {
                    // Network hatası durumunda offline sayfası göster
                    if (event.request.destination === 'document') {
                        return new Response(`
                            <!DOCTYPE html>
                            <html lang="tr">
                            <head>
                                <meta charset="UTF-8">
                                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                                <title>Şeyma'ya Sor - Çevrimdışı</title>
                                <style>
                                    body {
                                        font-family: Inter, sans-serif;
                                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                        color: white;
                                        display: flex;
                                        align-items: center;
                                        justify-content: center;
                                        min-height: 100vh;
                                        margin: 0;
                                        text-align: center;
                                        padding: 20px;
                                    }
                                    .offline-container {
                                        max-width: 400px;
                                        background: rgba(255, 255, 255, 0.1);
                                        padding: 40px;
                                        border-radius: 20px;
                                        backdrop-filter: blur(10px);
                                    }
                                    .offline-icon {
                                        font-size: 4rem;
                                        margin-bottom: 20px;
                                    }
                                    .offline-title {
                                        font-size: 1.5rem;
                                        margin-bottom: 15px;
                                        font-weight: 600;
                                    }
                                    .offline-message {
                                        font-size: 1rem;
                                        opacity: 0.9;
                                        line-height: 1.6;
                                        margin-bottom: 30px;
                                    }
                                    .retry-btn {
                                        background: rgba(255, 255, 255, 0.2);
                                        color: white;
                                        border: 2px solid rgba(255, 255, 255, 0.3);
                                        padding: 12px 24px;
                                        border-radius: 25px;
                                        font-size: 16px;
                                        cursor: pointer;
                                        transition: all 0.3s ease;
                                        text-decoration: none;
                                        display: inline-block;
                                    }
                                    .retry-btn:hover {
                                        background: rgba(255, 255, 255, 0.3);
                                        transform: translateY(-2px);
                                    }
                                </style>
                            </head>
                            <body>
                                <div class="offline-container">
                                    <div class="offline-icon">🤖💤</div>
                                    <h1 class="offline-title">Şeyma'ya Sor Çevrimdışı</h1>
                                    <p class="offline-message">
                                        İnternet bağlantınızı kontrol edin ve tekrar deneyin.
                                        Şeyma'ya soru sorabilmek için internete ihtiyacınız var.
                                    </p>
                                    <button class="retry-btn" onclick="window.location.reload()">
                                        🔄 Tekrar Dene
                                    </button>
                                </div>
                            </body>
                            </html>
                        `, {
                            headers: { 'Content-Type': 'text/html' }
                        });
                    }
                });
            })
    );
});

// Background Sync
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        console.log('Şeyma\'ya Sor SW: Background sync triggered');
        event.waitUntil(doBackgroundSync());
    }
});

function doBackgroundSync() {
    // Arka plan senkronizasyonu için fonksiyon
    return Promise.resolve();
}

// Message handling
self.addEventListener('message', event => {
    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }
});

// Notification handling (gelecekte kullanılabilir)
self.addEventListener('notificationclick', event => {
    console.log('Şeyma\'ya Sor SW: Notification click received.');

    event.notification.close();

    event.waitUntil(
        clients.openWindow('/seyma-sor/')
    );
});

// Push notification handling (gelecekte kullanılabilir)
self.addEventListener('push', event => {
    if (event.data) {
        const data = event.data.json();
        
        const options = {
            body: data.body || 'Şeyma\'ya yeni bir soru sorabilirsiniz!',
            icon: 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'%3E%3Ctext y=\'.9em\' font-size=\'90\'%3E🤖%3C/text%3E%3C/svg%3E',
            badge: 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'%3E%3Ctext y=\'.9em\' font-size=\'90\'%3E🤖%3C/text%3E%3C/svg%3E',
            vibrate: [200, 100, 200],
            tag: 'seyma-sor-notification',
            requireInteraction: false,
            actions: [
                {
                    action: 'open',
                    title: 'Şeyma\'ya Sor\'u Aç',
                    icon: 'data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 100 100\'%3E%3Ctext y=\'.9em\' font-size=\'90\'%3E❓%3C/text%3E%3C/svg%3E'
                }
            ]
        };

        event.waitUntil(
            self.registration.showNotification(data.title || 'Şeyma\'ya Sor', options)
        );
    }
});

console.log('Şeyma\'ya Sor Service Worker loaded successfully!');