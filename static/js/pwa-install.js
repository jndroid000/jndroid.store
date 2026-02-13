// PWA Install Prompt Handler
let deferredPrompt;
let installPromptShown = false;

// Detect install prompt availability
window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  console.log('📦 App installable - prompt available');
  
  // Show custom install banner after 3 seconds (not immediately)
  if (!installPromptShown) {
    showInstallPrompt();
  }
});

// Show custom install prompt banner
function showInstallPrompt() {
  const isMobile = /iPhone|iPad|iPod|Android/i.test(navigator.userAgent);
  const banner = document.getElementById('pwa-install-banner');
  
  if (!banner || installPromptShown || !isMobile) {
    return;
  }
  
  installPromptShown = true;
  
  // Show banner with animation
  setTimeout(() => {
    banner.classList.add('show');
    
    // Auto-hide after 10 seconds
    setTimeout(() => {
      banner.classList.remove('show');
    }, 10000);
  }, 2000);
}

// Handle install button click
document.addEventListener('DOMContentLoaded', () => {
  const installBtn = document.getElementById('pwa-install-btn');
  const closeBannerBtn = document.getElementById('pwa-banner-close');
  
  if (installBtn) {
    installBtn.addEventListener('click', async () => {
      if (!deferredPrompt) {
        console.log('Install prompt not available');
        return;
      }
      
      // Show the install dialog
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      
      if (outcome === 'accepted') {
        console.log('✅ User accepted install');
        deferredPrompt = null;
      } else {
        console.log('❌ User declined install');
      }
    });
  }
  
  if (closeBannerBtn) {
    closeBannerBtn.addEventListener('click', () => {
      const banner = document.getElementById('pwa-install-banner');
      banner.classList.remove('show');
      installPromptShown = true; // Don't show again this session
    });
  }
});

// Notify when app is installed
window.addEventListener('appinstalled', () => {
  console.log('✅ App installed successfully!');
  const banner = document.getElementById('pwa-install-banner');
  if (banner) {
    banner.classList.add('installed');
  }
  deferredPrompt = null;
});

// PWA Install Status Check
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/service-worker.js', { scope: '/' })
      .then((registration) => {
        console.log('✅ Service Worker registered');
        
        // Check for updates every 5 minutes
        setInterval(() => {
          registration.update();
        }, 300000);
        
        // Cache popular apps immediately
        if (registration.active) {
          registration.active.postMessage({ type: 'CACHE_POPULAR_APPS' });
        }
      })
      .catch((error) => {
        console.warn('⚠️ Service Worker registration failed:', error);
      });
  });
}

// Offline detection
window.addEventListener('offline', () => {
  console.log('📡 You are now offline');
  showOfflineNotification();
});

window.addEventListener('online', () => {
  console.log('📡 You are back online');
});

// Show offline notification
function showOfflineNotification() {
  const notification = document.createElement('div');
  notification.className = 'offline-notification';
  notification.innerHTML = `
    <span>📡 আপনি অফলাইন আছেন - অ্যাপ ব্যবহার করতে পারবেন অফলাইন ফিচার সহ!</span>
  `;
  document.body.appendChild(notification);
  
  setTimeout(() => {
    notification.remove();
  }, 5000);
}
