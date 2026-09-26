/* Тарелка — service worker: офлайн-доступ к уже открытому меню и установка как приложение.
   Стратегия: HTML — «сначала сеть» (чтобы сразу видеть обновления), с откатом на кэш офлайн.
   Остальное (иконки, манифест) — «сначала кэш» для скорости и офлайн-доступа. */
var CACHE_NAME = 'tarelka-v1';
var APP_SHELL = [
  './tarelka_telegram.html',
  './manifest.json',
  './icon-192.png',
  './icon-512.png',
  './icon-512-maskable.png'
];

self.addEventListener('install', function(event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function(cache) {
      return cache.addAll(APP_SHELL);
    }).then(function() { return self.skipWaiting(); })
  );
});

self.addEventListener('activate', function(event) {
  event.waitUntil(
    caches.keys().then(function(names) {
      return Promise.all(names.filter(function(n) { return n !== CACHE_NAME; }).map(function(n) { return caches.delete(n); }));
    }).then(function() { return self.clients.claim(); })
  );
});

self.addEventListener('fetch', function(event) {
  var req = event.request;
  if (req.method !== 'GET') return; // не трогаем запросы на магазины и прочее
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return; // внешние ссылки (магазины, шрифты) не кэшируем

  var isHTML = req.mode === 'navigate' || (req.headers.get('accept') || '').indexOf('text/html') !== -1;

  if (isHTML) {
    event.respondWith(
      fetch(req).then(function(res) {
        var copy = res.clone();
        caches.open(CACHE_NAME).then(function(cache) { cache.put(req, copy); });
        return res;
      }).catch(function() {
        return caches.match(req).then(function(cached) {
          return cached || caches.match('./tarelka_telegram.html');
        });
      })
    );
    return;
  }

  event.respondWith(
    caches.match(req).then(function(cached) {
      return cached || fetch(req).then(function(res) {
        var copy = res.clone();
        caches.open(CACHE_NAME).then(function(cache) { cache.put(req, copy); });
        return res;
      }).catch(function() { return cached; });
    })
  );
});
