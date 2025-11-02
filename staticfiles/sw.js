const CACHE_NAME = 'seyma-v1.0.0';
const urlsToCache = [
  '/',
  '/static/mainproject/css/admin.css',
  '/static/style.css',
  '/static/pwa/icon-192x192.png',
  '/static/pwa/icon-512x512.png',
  '/giris/',
  '/admin-paneli/',
  // Offline sayfası
  '/offline/'
];

// Service Worker kurulumu
self.addEventListener('install', function(event) {
  console.log('Service Worker yükleniyor...');
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Cache açıldı');
        return cache.addAll(urlsToCache);
      })
      .catch(function(error) {
        console.log('Cache ekleme hatası:', error);
      })
  );
});

// Service Worker aktifleştirme
self.addEventListener('activate', function(event) {
  console.log('Service Worker aktifleştiriliyor...');
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            console.log('Eski cache siliniyor:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Fetch event - Cache stratejisi
self.addEventListener('fetch', function(event) {
  // Sadece GET isteklerini cache'le
  if (event.request.method !== 'GET') {
    return;
  }

  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Cache'de varsa cache'den döndür
        if (response) {
          console.log('Cache\'den döndürülüyor:', event.request.url);
          return response;
        }

        // Cache'de yoksa network'ten al
        return fetch(event.request.clone())
          .then(function(response) {
            // Geçerli response kontrolü
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }

            // Response'u cache'e ekle
            var responseToCache = response.clone();
            
            // Chrome extension URL'lerini filtrele
            if (event.request.url.startsWith('http')) {
              caches.open(CACHE_NAME)
                .then(function(cache) {
                  // Sadece belirli dosya türlerini cache'le
                  if (shouldCache(event.request.url)) {
                    cache.put(event.request, responseToCache);
                    console.log('Cache\'e eklendi:', event.request.url);
                  }
                })
                .catch(function(error) {
                  console.log('Cache put hatası (güvenle yok sayılabilir):', error);
                });
            }

            return response;
          })
          .catch(function(error) {
            console.log('Network hatası:', error);
            // Offline durumunda cache'den döndür veya offline sayfası göster
            if (event.request.headers.get('accept').includes('text/html')) {
              return caches.match('/offline/') || 
                     new Response('<h1>Offline</h1><p>İnternet bağlantınızı kontrol edin.</p>', {
                       headers: { 'Content-Type': 'text/html' }
                     });
            }
            return caches.match(event.request);
          });
      })
  );
});

// Cache'lenecek dosya türlerini belirle
function shouldCache(url) {
  const cacheableExtensions = ['.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.woff', '.woff2'];
  const cacheablePaths = ['/static/', '/media/', '/admin-paneli/', '/giris/'];
  
  return cacheableExtensions.some(ext => url.includes(ext)) || 
         cacheablePaths.some(path => url.includes(path));
}

// Background Sync (gelecekte kullanmak için)
self.addEventListener('sync', function(event) {
  console.log('Background Sync tetiklendi:', event.tag);
  
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  // Offline durumunda biriken verileri senkronize et
  return Promise.resolve();
}

// Push notification (gelecekte kullanmak için)
self.addEventListener('push', function(event) {
  console.log('Push mesajı alındı:', event);
  
  const options = {
    body: event.data ? event.data.text() : 'Yeni bir bildiriminiz var',
    icon: '/static/pwa/icon-192x192.png',
    badge: '/static/pwa/icon-72x72.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Aç',
        icon: '/static/pwa/icon-192x192.png'
      },
      {
        action: 'close',
        title: 'Kapat',
        icon: '/static/pwa/icon-192x192.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('Şeyma - Kur\'an Eğitim Sistemi', options)
  );
});

// Notification click event
self.addEventListener('notificationclick', function(event) {
  console.log('Bildirime tıklandı:', event);
  
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/')
    );
  } else if (event.action === 'close') {
    // Bildirim kapatıldı
  } else {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});