/**
 * Search Expand Functionality
 * Handles the expansion and collapse of the search bar in the header
 * সার্চ বার এক্সপেন্ড এবং রিয়েলটাইম সার্চ
 */

let searchTimeout; // Debounce টাইমার

function initSearchExpandFunctionality() {
  const appSearch = document.querySelector('.app-search');
  const appSearchInput = document.querySelector('.app-search__input');
  const appSearchGo = document.querySelector('.app-search__go');
  const header = document.querySelector('header');

  if (!appSearch || !appSearchInput) {
    console.warn('Search elements not found');
    return;
  }

  // Expand search when clicking on the search bar
  appSearch.addEventListener('click', (e) => {
    e.stopPropagation();
    expandSearch();
  });

  // Expand search when focusing on input
  appSearchInput.addEventListener('focus', () => {
    expandSearch();
  });

  // রিয়েলটাইম সার্চ - ইনপুট চেঞ্জ হলে
  appSearchInput.addEventListener('input', (e) => {
    const query = e.target.value.trim();
    
    // Debounce - যাতে প্রতিটা চেঞ্জে লক্ষ লক্ষ বার এপিআই কল না হয়
    clearTimeout(searchTimeout);
    
    // আপনি যখন টাইপ করেন তখনই সার্চ শুরু
    if (query.length === 0) {
      // যদি খালি হয়ে যায় তাহলে ট্রেন্ডিং দেখাও
      loadTrendingApps();
      return;
    }
    
    // 300 মিলিসেকেন্ড পর API কল করো (ডেবাউন্স)
    searchTimeout = setTimeout(() => {
      performRealtimeSearch(query);
    }, 300);
  });

  // Handle search submission by clicking Go button
  appSearchGo.addEventListener('click', () => {
    const query = appSearchInput.value.trim();
    if (query) {
      performSearch(query);
    }
  });

  // Handle Enter key in input
  appSearchInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
      const query = appSearchInput.value.trim();
      if (query) {
        performSearch(query);
      }
    }
  });
}

/**
 * রিয়েলটাইম সার্চ API কল
 * @param {string} query - সার্চ কোয়েরি
 */
function performRealtimeSearch(query) {
  console.log('রিয়েলটাইম সার্চ করছি:', query);
  
  // ট্রেন্ডিং লুকাও, সার্চ করছি স্পিনার দেখাও
  const overlay = document.getElementById('search-results-overlay');
  if (overlay) {
    overlay.innerHTML = `
      <div>
        <div class="search-loading">
          <i class="fas fa-spinner fa-spin"></i>
          <p>ফলাফল খুঁজছি...</p>
        </div>
      </div>
    `;
    overlay.style.display = 'flex';
  }
  
  // API কল করো
  fetch(`/apps/api/search/?q=${encodeURIComponent(query)}`)
    .then(response => response.json())
    .then(data => {
      console.log('সার্চ রেজাল্ট:', data);
      if (data.success && data.apps.length > 0) {
        displayRealtimeSearchResults(data.apps, query);
      } else {
        displayNoResults(query);
      }
    })
    .catch(error => {
      console.error('সার্চ এরর:', error);
      displayNoResults(query);
    });
}

/**
 * রিয়েলটাইম সার্চ রেজাল্ট দেখাও
 * @param {array} apps - অ্যাপস অ্যারে
 * @param {string} query - সার্চ কোয়েরি
 */
function displayRealtimeSearchResults(apps, query) {
  const overlay = document.getElementById('search-results-overlay');
  if (!overlay) return;
  
  let html = `<div>
    <div class="search-results-header">
      <p><strong>${apps.length}</strong> রেজাল্ট পাওয়া গেছে "<strong>${query}</strong>" এর জন্য</p>
    </div>
    <div id="search-results-grid">`;
  
  apps.forEach(app => {
    html += `
      <div class="search-result-card" onclick="window.location.href='/apps/${app.slug}/';">
        <img src="${app.icon}" alt="${app.title}" onerror="this.src='/static/images/default-app-icon.png'">
        <div class="search-result-content">
          <h4 class="search-result-title">${app.title}</h4>
          <p class="search-result-category">${app.category}</p>
          <p class="search-result-description">${app.short_description}</p>
          <div class="search-result-meta">
            <span class="search-result-rating">⭐ ${app.rating}</span>
            <span class="search-result-downloads">📥 ${app.download_count > 1000 ? (app.download_count / 1000).toFixed(1) + 'K' : app.download_count}</span>
          </div>
        </div>
      </div>
    `;
  });
  
  html += '</div></div>';
  
  overlay.innerHTML = html;
  overlay.style.display = 'flex';
}

/**
 * কোনো রেজাল্ট না পাওয়া গেলে দেখাও
 * @param {string} query - সার্চ কোয়েরি
 */
function displayNoResults(query) {
  const overlay = document.getElementById('search-results-overlay');
  if (!overlay) return;
  
  overlay.innerHTML = `
    <div>
      <div class="no-results">
        <p class="no-results__text">
          "<strong>${query}</strong>" এর জন্য কোনো অ্যাপ পাওয়া যায়নি
        </p>
        <p class="no-results__hint">অন্য কিছু খোঁজার চেষ্টা করুন</p>
      </div>
    </div>
  `;
  overlay.style.display = 'flex';
}

/**
 * Expand the search bar
 */
function expandSearch() {
  const appSearch = document.querySelector('.app-search');
  const header = document.querySelector('header');
  const appSearchInput = document.querySelector('.app-search__input');
  const body = document.body;
  const overlay = document.getElementById('search-results-overlay');

  if (appSearch && !appSearch.classList.contains('app-search--expanded')) {
    appSearch.classList.add('app-search--expanded');
    
    if (header) {
      header.classList.add('header--search-expanded');
    }

    // Add blur to main content
    body.classList.add('search-expanded');

    // Show search results overlay with trending apps
    if (overlay) {
      overlay.style.display = 'block';
      loadTrendingApps();
    }

    // Add close button if it doesn't exist
    if (!appSearch.querySelector('.app-search__close')) {
      const closeBtn = document.createElement('button');
      closeBtn.className = 'app-search__close';
      closeBtn.innerHTML = '✕';
      closeBtn.type = 'button';
      closeBtn.setAttribute('aria-label', 'Close search');
      
      closeBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        collapseSearch();
      });
      
      appSearch.appendChild(closeBtn);
    }

    // Focus input and select all text if any
    if (appSearchInput) {
      appSearchInput.focus();
      if (appSearchInput.value) {
        appSearchInput.select();
      }
    }

    console.log('Search expanded');
  }
}

/**
 * Collapse the search bar
 */
function collapseSearch() {
  const appSearch = document.querySelector('.app-search');
  const header = document.querySelector('header');
  const appSearchInput = document.querySelector('.app-search__input');
  const closeBtn = document.querySelector('.app-search__close');
  const body = document.body;

  if (appSearch && appSearch.classList.contains('app-search--expanded')) {
    appSearch.classList.remove('app-search--expanded');
    
    if (header) {
      header.classList.remove('header--search-expanded');
    }

    // Remove blur from main content
    body.classList.remove('search-expanded');

    // Hide search results
    hideSearchResults();

    // Remove close button
    if (closeBtn) {
      closeBtn.remove();
    }

    // Clear input if desired (optional)
    // if (appSearchInput) {
    //   appSearchInput.value = '';
    // }

    console.log('Search collapsed');
  }
}

/**
 * Perform search action - সার্চ রেজাল্ট পেজে যাও
 * @param {string} query - Search query
 */
function performSearch(query) {
  console.log('সার্চ করছি:', query);
  
  if (!query || query.trim() === '') {
    console.warn('খালি কোয়েরি');
    return;
  }
  
  // সার্চ পেজে রিডিরেক্ট করো
  window.location.href = `/search/?q=${encodeURIComponent(query)}`;
}

/**
 * Load and display trending apps
 */
function loadTrendingApps() {
  const overlay = document.getElementById('search-results-overlay');
  if (!overlay) return;
  
  // লোডিং স্টেট দেখাও
  overlay.innerHTML = `
    <div>
      <div class="search-loading">
        <i class="fas fa-spinner fa-spin"></i>
        <p>ট্রেন্ডিং অ্যাপ লোড করছি...</p>
      </div>
    </div>
  `;
  overlay.style.display = 'flex';
  
  // API থেকে ট্রেন্ডিং অ্যাপ ফেচ করো
  fetch('/apps/api/popular-apps/')
    .then(response => response.json())
    .then(data => {
      console.log('ট্রেন্ডিং অ্যাপস:', data);
      
      if (data && data.apps && data.apps.length > 0) {
        displayTrendingApps(data.apps);
      } else {
        overlay.innerHTML = `
          <div>
            <div class="no-results">
              <p class="no-results__text">কোনো ট্রেন্ডিং অ্যাপ পাওয়া যায়নি</p>
            </div>
          </div>
        `;
      }
    })
    .catch(error => {
      console.error('ট্রেন্ডিং অ্যাপ লোডিং এরর:', error);
      
      // ফলব্যাক - ডিফল্ট ট্রেন্ডিং অ্যাপস দেখাও
      const defaultTrending = [
        { id: 1, title: 'WhatsApp', icon: '💬', category: 'মেসেজিং', rating: 4.8, download_count: 10000000, slug: '#' },
        { id: 2, title: 'Instagram', icon: '📷', category: 'সোশ্যাল', rating: 4.6, download_count: 5000000, slug: '#' },
        { id: 3, title: 'Facebook', icon: '👥', category: 'সোশ্যাল', rating: 4.5, download_count: 8000000, slug: '#' },
        { id: 4, title: 'YouTube', icon: '📹', category: 'ভিডিও', rating: 4.7, download_count: 12000000, slug: '#' },
        { id: 5, title: 'Telegram', icon: '✈️', category: 'মেসেজিং', rating: 4.8, download_count: 3000000, slug: '#' },
        { id: 6, title: 'Netflix', icon: '🎬', category: 'বিনোদন', rating: 4.6, download_count: 2000000, slug: '#' },
      ];
      displayTrendingApps(defaultTrending);
    });
}

/**
 * Display trending apps
 */
function displayTrendingApps(apps) {
  const overlay = document.getElementById('search-results-overlay');
  if (!overlay) return;
  
  let html = `<div>
    <div class="search-results-header" style="text-align: center;">
      <p style="margin: 0;">🔥 ট্রেন্ডিং অ্যাপস</p>
    </div>
    <div id="trending-results">`;
  
  apps.slice(0, 6).forEach(app => {
    const appIcon = app.icon || '📱';
    const appTitle = app.title || app.name || 'Unknown';
    const appCategory = app.category || 'অন্যান্য';
    const appRating = app.rating || 0;
    const appDownloads = app.download_count || 0;
    const appSlug = app.slug || '#';
    
    const isImageUrl = typeof appIcon === 'string' && appIcon.includes('/');
    
    html += `
      <div class="trending-app-card" onclick="${appSlug !== '#' ? `window.location.href='/apps/${appSlug}/'` : ''}">
        <div class="trending-app-icon">
          ${isImageUrl 
            ? `<img src="${appIcon}" alt="${appTitle}" onerror="this.src='/static/images/default-app-icon.png'">` 
            : appIcon}
        </div>
        <div class="trending-app-content">
          <h4 class="trending-app-title">${appTitle}</h4>
          <p class="trending-app-category">${appCategory}</p>
          <div class="trending-app-meta">
            <span class="trending-app-rating">⭐ ${appRating}</span>
            <span class="trending-app-downloads">📥 ${appDownloads > 1000000 ? (appDownloads / 1000000).toFixed(1) + 'M' : appDownloads > 1000 ? (appDownloads / 1000).toFixed(1) + 'K' : appDownloads}</span>
          </div>
        </div>
      </div>
    `;
  });
  
  html += '</div></div>';
  
  overlay.innerHTML = html;
  overlay.style.display = 'flex';
}

/**
 * Display search results in the results grid
 * @param {array} apps - Array of app objects
 */
function displaySearchResults(apps) {
  const resultsGrid = document.getElementById('search-results-grid');
  if (!resultsGrid) return;
  
  resultsGrid.innerHTML = '';
  
  if (!apps || apps.length === 0) {
    resultsGrid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--muted); padding: 40px;">কোনো অ্যাপ পাওয়া যায়নি</p>';
    return;
  }
  
  apps.slice(0, 6).forEach(app => {
    const appCard = document.createElement('div');
    appCard.className = 'search-result-card';
    appCard.style.cursor = 'pointer';
    
    appCard.innerHTML = `
      <div style="display: flex; gap: 12px; align-items: flex-start;">
        <img src="${app.icon}" alt="${app.title}" style="width: 40px; height: 40px; border-radius: 6px; object-fit: cover;" onerror="this.src='/static/images/default-app-icon.png'">
        <div style="flex: 1;">
          <h4 style="margin: 0 0 4px 0; font-size: 14px; font-weight: 600;">${app.title}</h4>
          <p style="margin: 0 0 4px 0; font-size: 12px; color: var(--muted);">${app.category}</p>
          <div style="display: flex; gap: 12px; font-size: 12px;">
            <span>⭐ ${app.rating}</span>
            <span>📥 ${app.download_count > 1000 ? (app.download_count / 1000).toFixed(1) + 'K' : app.download_count}</span>
          </div>
        </div>
      </div>
    `;
    
    appCard.addEventListener('click', () => {
      window.location.href = `/apps/${app.slug}/`;
    });
    
    resultsGrid.appendChild(appCard);
  });
}

/**
 * Show search results overlay
 */
function showSearchResults() {
  const overlay = document.getElementById('search-results-overlay');
  if (overlay) {
    overlay.style.display = 'block';
  }
}

/**
 * Hide search results overlay
 */
function hideSearchResults() {
  const overlay = document.getElementById('search-results-overlay');
  if (overlay) {
    overlay.style.display = 'none';
  }
}

/**
 * Initialize search functionality when DOM is ready
 */
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initSearchExpandFunctionality);
} else {
  initSearchExpandFunctionality();
}
