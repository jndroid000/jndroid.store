// Service Worker for JnDroid Store PWA
// Supports: Offline pages, caching, background sync, push notifications

const CACHE_NAME = 'jndroid-v1';
const RUNTIME_CACHE = 'jndroid-runtime-v1';
const POPULAR_APPS_CACHE = 'jndroid-popular-apps-v1';

// ==================== PHASE 1: Installation ====================
// Cache essential files on first install
self.addEventListener('install', (event) => {
  console.log('🔧 Service Worker installing...');
  
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('📦 Caching essential files');
      return cache.addAll([
        '/',
        '/offline-error/',
        '/static/css/styles.css',
        '/static/css/pages.css',
        '/static/css/header.css',
        '/static/js/common.js',
        '/static/js/theme.js',
        '/static/images/favicon.ico',
        '/static/images/favicon-64x64.png',
        '/static/images/favicon-128x128.png',
        '/static/images/favicon-256x256.png',
        '/categories/',
        '/privacy/',
        '/terms-of-service/',
        '/community-guidelines/',
        '/support/',
      ]).catch((err) => {
        console.warn('⚠️ Some resources unavailable for caching:', err);
        // Don't fail installation if some resources are missing
        return caches.open(CACHE_NAME).then((cache) => {
          // Cache at least the most important ones
          return cache.addAll([
            '/',
            '/static/js/common.js',
            '/static/js/theme.js',
          ]);
        });
      });
    })
  );
  
  // Skip waiting - activate immediately
  self.skipWaiting();
});

// ==================== ACTIVATION ====================
// Clean up old caches
self.addEventListener('activate', (event) => {
  console.log('✅ Service Worker activated');
  
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME && 
              cacheName !== RUNTIME_CACHE && 
              cacheName !== POPULAR_APPS_CACHE) {
            console.log('🗑️ Deleting old cache:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  
  // Claim all clients immediately
  return self.clients.claim();
});

// ==================== HELPER FUNCTIONS ====================

// Create offline fallback page
function createOfflineFallbackPage(requestUrl) {
  const offlineHTML = `<!DOCTYPE html>
<html lang="bn">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>অফলাইন - জয়ড্রয়েড স্টোর</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body { height: 100%; }
    
    @media (prefers-color-scheme: dark) {
      body { background: #1a1a1a; color: #f0f0f0; }
      .card { background: #2d2d2d; border-color: #404040; }
      .link-btn { background: #0056b3; border-color: #0056b3; }
      .link-btn:hover { background: #0d47a1; }
    }
    
    body { 
      background: #ffffff; 
      color: #333333; 
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
      display: flex;
      flex-direction: column;
      min-height: 100vh;
    }
    
    .container { 
      max-width: 900px; 
      margin: 0 auto; 
      padding: 20px; 
      flex: 1;
    }
    
    .header { 
      background: linear-gradient(135deg, #ff6b6b 0%, #c92a2a 100%); 
      color: #ffffff; 
      padding: 25px 20px; 
      text-align: center; 
      border-radius: 8px; 
      margin-bottom: 25px;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    }
    
    .header h1 { 
      font-size: 24px; 
      font-weight: 600;
      margin: 0;
    }
    
    .card { 
      background: #f8f9fa; 
      border: 2px solid #ff6b6b; 
      border-radius: 8px; 
      padding: 20px; 
      margin-bottom: 20px; 
    }
    
    .card h2 { 
      color: #ff6b6b; 
      margin-bottom: 10px; 
      font-size: 18px;
    }
    
    .card p { 
      margin: 8px 0; 
      line-height: 1.6;
      color: #666666;
    }
    
    .links { 
      display: grid; 
      grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); 
      gap: 12px;
      margin-top: 15px;
    }
    
    .link-btn { 
      background: #007bff; 
      color: #ffffff; 
      padding: 12px 16px; 
      border-radius: 6px; 
      text-decoration: none; 
      text-align: center; 
      cursor: pointer; 
      border: 1px solid #007bff;
      font-size: 14px; 
      font-weight: 500;
      transition: all 0.3s ease; 
      display: inline-block;
      width: 100%;
    }
    
    .link-btn:hover { 
      background: #0056b3; 
      border-color: #0056b3;
      transform: translateY(-2px); 
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
    }
    
    .link-btn:active {
      transform: translateY(0);
    }
    
    .footer {
      text-align: center;
      padding: 20px;
      color: #999999;
      font-size: 12px;
      border-top: 1px solid #e0e0e0;
      margin-top: 30px;
    }
  </style>
</head>
<body>
  <div class="container">
    <div class="header">
      <h1>📱 আপনি অফলাইন আছেন</h1>
    </div>
    
    <div class="card">
      <h2>এই পেজটি অ্যাক্সেসযোগ্য নয়</h2>
      <p>আপনি অফলাইন মোডে আছেন এবং এই পেজটি আগে কখনো ভিজিট করেননি।</p>
      <p>তাই এটি আপনার ডিভাইসে ক্যাশ করা নেই।</p>
    </div>
    
    <div class="card">
      <h2>আপনি এই পেজগুলি দেখতে পারেন:</h2>
      <div class="links">
        <a href="/" class="link-btn">🏠 হোম</a>
        <a href="/apps/" class="link-btn">📱 অ্যাপস</a>
        <a href="/categories/" class="link-btn">📂 ক্যাটাগরি</a>
        <a href="/privacy/" class="link-btn">🔒 গোপনীয়তা</a>
      </div>
    </div>
    
    <div class="card" style="background: #e7f3ff; border-color: #007bff; text-align: center;">
      <p style="color: #0056b3; margin: 0;">
        <strong>💡 টিপস:</strong> ইন্টারনেট সংযোগ করলে এই পেজটি স্বয়ংক্রিয়ভাবে লোড হবে।
      </p>
    </div>
  </div>
  
  <div class="footer">
    📡 অফলাইন মোড - আরও সামগ্রী দেখতে ইন্টারনেট সংযোগ করুন
  </div>
</body>
</html>`;
  
  return new Response(offlineHTML, {
    status: 200,
    headers: {
      'Content-Type': 'text/html; charset=utf-8',
      'Cache-Control': 'no-cache, no-store, must-revalidate',
      'Pragma': 'no-cache'
    }
  });
}

// ==================== PHASE 2: Network Requests ====================
// Intercept fetch requests - Network First, then Cache
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    return;
  }
  
  // Strategy 1: API calls only - Network First (returns JSON/data)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(event.request));
    return;
  }
  
  // Strategy 2: Static assets - Cache First
  if (url.pathname.includes('/static/')) {
    event.respondWith(cacheFirst(event.request));
    return;
  }
  
  // Strategy 3: Pages (including /apps/, /categories/, etc) - Network First with Cache fallback
  if (event.request.method === 'GET') {
    event.respondWith(networkFirstWithCache(event.request));
    return;
  }
});

// ==================== CACHING STRATEGIES ====================

// Network First: Try network first, fallback to cache (for API calls)
async function networkFirst(request) {
  try {
    const response = await fetch(request);
    
    // Cache successful responses
    if (response && response.status === 200) {
      const clonedResponse = response.clone();
      caches.open(RUNTIME_CACHE).then((cache) => {
        cache.put(request, clonedResponse);
      });
    }
    
    return response;
  } catch (error) {
    // Network failed, try cache
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('📦 Using cached response for:', request.url);
      return cachedResponse;
    }
    
    // For navigation requests, serve offline page
    if (request.mode === 'navigate') {
      const offlinePageFromCache = await caches.match('/offline-error/');
      if (offlinePageFromCache) {
        return offlinePageFromCache;
      }
      return createOfflineFallbackPage(request.url);
    }
    
    // For API requests, return JSON error
    console.warn('❌ API call failed offline:', request.url);
    return new Response(JSON.stringify({ 
      error: 'অফলাইন - API উপলব্ধ নয়',
      offline: true 
    }), {
      status: 503,
      headers: { 'Content-Type': 'application/json; charset=utf-8' },
    });
  }
}

// Cache First: Use cache first, network as fallback
async function cacheFirst(request) {
  const cachedResponse = await caches.match(request);
  
  if (cachedResponse) {
    // Update cache in background
    fetch(request).then((response) => {
      if (response && response.status === 200) {
        caches.open(CACHE_NAME).then((cache) => {
          cache.put(request, response);
        });
      }
    }).catch(() => {
      // Network failed, already using cached version
    });
    
    return cachedResponse;
  }
  
  // Not in cache, fetch from network
  try {
    const response = await fetch(request);
    if (response && response.status === 200) {
      const clonedResponse = response.clone();
      caches.open(CACHE_NAME).then((cache) => {
        cache.put(request, clonedResponse);
      });
    }
    return response;
  } catch (error) {
    console.error('❌ Fetch failed:', error);
    return new Response('Resource not available offline');
  }
}

// Network First with Cache fallback
async function networkFirstWithCache(request) {
  try {
    const response = await fetch(request);
    
    if (response && response.status === 200) {
      const clonedResponse = response.clone();
      caches.open(RUNTIME_CACHE).then((cache) => {
        cache.put(request, clonedResponse);
      });
    }
    
    return response;
  } catch (error) {
    const cachedResponse = await caches.match(request);
    if (cachedResponse) {
      console.log('📦 Using cached response for:', request.url);
      return cachedResponse;
    }
    
    // Return offline error page for navigation requests
    if (request.mode === 'navigate') {
      // First try to get offline error page from cache
      const offlineErrorPage = await caches.match('/offline-error/');
      if (offlineErrorPage) {
        console.log('📄 Serving cached offline error page:', request.url);
        return offlineErrorPage;
      }
      
      // Fallback: use helper function to create offline page
      console.log('📄 Serving inline offline fallback page for:', request.url);
      return createOfflineFallbackPage(request.url);
    }
    
    // Fallback for non-navigation requests
    console.warn('❌ Network request failed for:', request.url);
    return new Response('অফলাইন - সংস্থান উপলব্ধ নয়', { 
      status: 503, 
      headers: { 'Content-Type': 'text/plain; charset=utf-8' } 
    });
  }
}

// ==================== PHASE 3: Background Tasks ====================
// Background sync - Pre-cache popular apps periodically
async function cachePopularApps() {
  try {
    const response = await fetch('/api/popular-apps/');
    
    if (!response || response.status !== 200) {
      console.warn('⚠️ Failed to fetch popular apps');
      return;
    }
    
    const data = await response.json();
    const cache = await caches.open(POPULAR_APPS_CACHE);
    
    // Cache the API response itself
    cache.put('/api/popular-apps/', new Response(JSON.stringify(data)));
    
    // Cache app thumbnails if available
    if (data.apps && Array.isArray(data.apps)) {
      data.apps.forEach((app) => {
        // Cache app cover images
        if (app.cover_image) {
          cacheImage(app.cover_image, cache);
        }
        
        // Cache app detail pages
        if (app.id) {
          fetch(`/apps/${app.id}/`)
            .then((response) => {
              if (response && response.status === 200) {
                cache.put(`/apps/${app.id}/`, response.clone());
              }
            })
            .catch(() => {
              // Silently fail - not critical for background task
            });
        }
      });
    }
    
    console.log('✅ Popular apps cached successfully');
  } catch (error) {
    console.error('❌ Error caching popular apps:', error);
  }
}

// Helper function to cache images
async function cacheImage(imageUrl, cache) {
  try {
    const response = await fetch(imageUrl);
    if (response && response.status === 200) {
      cache.put(imageUrl, response);
    }
  } catch (error) {
    // Silently fail for image caching
  }
}

// Trigger background caching periodically
setInterval(() => {
  console.log('🔄 Updating popular apps cache...');
  cachePopularApps();
}, 1800000); // Every 30 minutes

// Also cache on first install completion
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
  
  if (event.data && event.data.type === 'CACHE_POPULAR_APPS') {
    cachePopularApps();
  }
});

console.log('✨ JnDroid Service Worker loaded successfully!');
