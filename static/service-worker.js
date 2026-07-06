const CACHE_NAME = 'car-manager-v1';

// オフライン時にキャッシュするファイル
const STATIC_ASSETS = [
  '/',
  '/static/index.html',
  '/static/manifest.json',
];

// ── インストール：静的ファイルをキャッシュ ──
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => cache.addAll(STATIC_ASSETS))
  );
  self.skipWaiting();
});

// ── アクティベート：古いキャッシュを削除 ──
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE_NAME).map((key) => caches.delete(key))
      )
    )
  );
  self.clients.claim();
});

// ── フェッチ：ネットワーク優先、失敗時はキャッシュ ──
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // APIリクエストはキャッシュしない（常にネットワーク）
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(fetch(event.request));
    return;
  }

  // 静的ファイル：ネットワーク優先、失敗時はキャッシュから返す
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // 成功したらキャッシュを更新
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return response;
      })
      .catch(() => {
        // オフライン時：キャッシュから返す
        return caches.match(event.request).then(
          (cached) => cached || caches.match('/')
        );
      })
  );
});
