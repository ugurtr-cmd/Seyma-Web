const CACHE_NAME = 'seyma-v2';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/admin-paneli/',
  '/offline.html',
  '/static/pwa/icon-192x192.png',
  '/static/pwa/icon-512x512.png'
];

// Service Worker yükleme
self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(function(cache) {
        console.log('Cache açıldı');
        return cache.addAll(urlsToCache);
      })
  );
});

// Cache'den serve etme
self.addEventListener('fetch', function(event) {
  event.respondWith(
    caches.match(event.request)
      .then(function(response) {
        // Cache'de varsa döndür
        if (response) {
          return response;
        }
        return fetch(event.request);
      }
    )
  );
});

// Eski cache'leri temizle
self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(cacheNames) {
      return Promise.all(
        cacheNames.map(function(cacheName) {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Push notification dinleyicisi
self.addEventListener('push', function(event) {
  if (event.data) {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: data.icon || '/static/pwa/icon-192x192.png',
      badge: data.badge || '/static/pwa/icon-72x72.png',
      tag: data.tag || 'general',
      data: data.data || {},
      actions: data.actions || [],
      requireInteraction: data.requireInteraction || false,
      timestamp: Date.now()
    };

    event.waitUntil(
      self.registration.showNotification(data.title, options)
    );
  }
});

// Bildirim tıklaması
self.addEventListener('notificationclick', function(event) {
  event.notification.close();

  const action = event.action;
  const notification = event.notification;
  const data = notification.data;

  if (action === 'view-message') {
    // Günlük mesaj görüntüle
    event.waitUntil(
      clients.openWindow('/admin-paneli/')
    );
  } else if (action === 'view-students') {
    // Öğrenci listesini görüntüle
    event.waitUntil(
      clients.openWindow('/admin-paneli/ogrenciler/')
    );
  } else {
    // Varsayılan - ana sayfaya git
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Background sync (gelecekte kullanılabilir)
self.addEventListener('sync', function(event) {
  if (event.tag === 'daily-message-sync') {
    event.waitUntil(syncDailyMessage());
  } else if (event.tag === 'weekly-report-sync') {
    event.waitUntil(syncWeeklyReport());
  }
});

// Günlük mesaj senkronizasyonu
function syncDailyMessage() {
  return fetch('/api/daily-message-notification/')
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log('Günlük mesaj bildirimi senkronize edildi');
      }
    })
    .catch(error => {
      console.error('Günlük mesaj senkronizasyon hatası:', error);
    });
}

// Haftalık rapor senkronizasyonu
function syncWeeklyReport() {
  return fetch('/api/weekly-report-notification/')
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log('Haftalık rapor bildirimi senkronize edildi');
      }
    })
    .catch(error => {
      console.error('Haftalık rapor senkronizasyon hatası:', error);
    });
}