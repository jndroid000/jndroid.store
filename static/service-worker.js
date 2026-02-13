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

// ==================== PHASE 2: Network Requests ====================
// Intercept fetch requests - Network First, then Cache
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  
  // Skip cross-origin requests
  if (url.origin !== location.origin) {
    return;
  }
  
  // Strategy 1: API calls - Network First
  if (url.pathname.startsWith('/api/') || 
      url.pathname.startsWith('/apps/') ||
      url.pathname.startsWith('/categories/')) {
    event.respondWith(networkFirst(event.request));
    return;
  }
  
  // Strategy 2: Static assets - Cache First
  if (url.pathname.includes('/static/')) {
    event.respondWith(cacheFirst(event.request));
    return;
  }
  
  // Strategy 3: Pages - Network First with Cache fallback
  if (event.request.method === 'GET') {
    event.respondWith(networkFirstWithCache(event.request));
    return;
  }
});

// ==================== CACHING STRATEGIES ====================

// Network First: Try network first, fallback to cache
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
    
    // Return offline page if available
    return new Response('⚠️ You are offline and this page is not cached.', {
      status: 503,
      statusText: 'Service Unavailable',
      headers: new Headers({
        'Content-Type': 'text/plain',
      }),
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
      return cachedResponse;
    }
    
    // Return offline page
    const offlinePage = await caches.match('/');
    return offlinePage || new Response('⚠️ Offline - Page not available');
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
