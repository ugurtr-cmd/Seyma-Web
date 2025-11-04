/* Şeyma'ya Sor - AI Asistan Service Worker */
const CACHE_NAME = 'seymasor-v1.0.0';
const OFFLINE_URL = '/offline/';

// Cache'lenecek dosyalar
const urlsToCache = [
  '/arama-motoru/',
  '/offline/',
  '/static/seyma-sor-icons/android-launchericon-192-192.png',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
  'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css',
];

// Service Worker kurulum aşaması
self.addEventListener('install', (event) => {
  console.log('[Şeyma Sor SW] Service Worker kurulumu başladı');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[Şeyma Sor SW] Cache açıldı');
      return cache.addAll(urlsToCache).catch((err) => {
        console.log('[Şeyma Sor SW] Cache ekleme hatası:', err);
        return Promise.resolve();
      });
    }).then(() => {
      console.log('[Şeyma Sor SW] Kurulum tamamlandı');
      return self.skipWaiting();
    })
  );
});

// Service Worker aktifleştirme aşaması
self.addEventListener('activate', (event) => {
  console.log('[Şeyma Sor SW] Service Worker aktifleştiriliyor');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Şeyma Sor SW] Eski cache siliniyor:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    }).then(() => {
      console.log('[Şeyma Sor SW] Aktifleştirme tamamlandı');
      return self.clients.claim();
    })
  );
});

// Fetch olaylarını yakalama - Network First stratejisi
self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') {
    return;
  }

  if (event.request.url.startsWith('chrome-extension://')) {
    return;
  }

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response && response.status === 200) {
          const responseToCache = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseToCache);
          });
        }
        return response;
      })
      .catch(() => {
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          
          if (event.request.headers.get('accept').includes('text/html')) {
            return caches.match(OFFLINE_URL);
          }
        });
      })
  );
});

// Push notification desteği
self.addEventListener('push', (event) => {
  console.log('[Şeyma Sor SW] Push notification alındı');
  
  let data = {
    title: 'Şeyma\'ya Sor',
    body: 'Yeni bir bildirim var',
    icon: '/static/seyma-sor-icons/android-launchericon-192-192.png',
    badge: '/static/seyma-sor-icons/android-launchericon-192-192.png',
  };

  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: data.icon || '/static/seyma-sor-icons/android-launchericon-192-192.png',
    badge: data.badge || '/static/seyma-sor-icons/android-launchericon-192-192.png',
    vibrate: [200, 100, 200],
    tag: 'seymasor-notification',
    requireInteraction: false,
    data: data.data || {},
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Notification tıklama olayı
self.addEventListener('notificationclick', (event) => {
  console.log('[Şeyma Sor SW] Notification tıklandı');
  event.notification.close();

  event.waitUntil(
    clients.openWindow(event.notification.data.url || '/arama-motoru/')
  );
});
