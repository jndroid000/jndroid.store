// Initialize mobile menu functionality
function initHeaderFunctionality() {
  const menuBtn = document.getElementById('menuBtn');
  const closeBtn = document.getElementById('closeBtn');
  const drawer = document.getElementById('drawer');
  const drawerOverlay = document.getElementById('drawerOverlay');
  const drawerNav = document.querySelectorAll('.drawer-nav a');
  const drawerFormBtn = document.querySelectorAll('.drawer-form-btn');
  
  // Profile Dropdown Functionality
  const profileBtn = document.getElementById('profileBtn');
  const profileDropdown = document.querySelector('.profile-dropdown');
  const profileMenu = document.getElementById('profileMenu');

  if (!menuBtn || !drawer) return;

  // Open drawer
  menuBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    drawer.classList.add('show');
    document.documentElement.style.overflow = 'hidden';
    document.body.style.overflow = 'hidden';
    document.body.style.overflowX = 'hidden';
  });

  // Close drawer
  function closeDrawer() {
    drawer.classList.remove('show');
    document.documentElement.style.overflow = '';
    document.body.style.overflow = '';
    document.body.style.overflowX = '';
  }

  if (closeBtn) {
    closeBtn.addEventListener('click', closeDrawer);
  }

  // Close drawer on overlay click
  if (drawerOverlay) {
    drawerOverlay.addEventListener('click', closeDrawer);
  }

  // Close drawer when clicking on a link
  drawerNav.forEach(link => {
    link.addEventListener('click', closeDrawer);
  });

  // Close drawer when clicking on form button (logout)
  drawerFormBtn.forEach(btn => {
    btn.addEventListener('click', closeDrawer);
  });

  // Close drawer on ESC key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
      closeDrawer();
    }
  });

  // Close drawer when clicking outside drawer (on web view)
  document.addEventListener('click', (e) => {
    if (drawer.classList.contains('show') && 
        !drawer.contains(e.target) && 
        !menuBtn.contains(e.target)) {
      closeDrawer();
    }
  });

  // Profile Dropdown Click Handler
  if (profileBtn && profileDropdown && profileMenu) {
    console.log('Profile dropdown initialized:', { profileBtn, profileDropdown, profileMenu });
    
    profileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      console.log('Profile button clicked!');
      profileDropdown.classList.toggle('active');
      console.log('Active class toggle, profile dropdown now:', profileDropdown.classList.contains('active'));
    });

    // Close profile dropdown when clicking on a menu item
    const menuItems = profileMenu.querySelectorAll('.profile-menu-item, button');
    menuItems.forEach(item => {
      item.addEventListener('click', () => {
        // Only close if it's not a dropdown toggle button (theme toggle)
        if (!item.classList.contains('theme-toggle-menu')) {
          profileDropdown.classList.remove('active');
        }
      });
    });

    // Close profile dropdown when clicking outside
    document.addEventListener('click', (e) => {
      if (profileDropdown.classList.contains('active') && 
          !profileDropdown.contains(e.target)) {
        profileDropdown.classList.remove('active');
      }
    });

    // Close on ESC key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && profileDropdown.classList.contains('active')) {
        profileDropdown.classList.remove('active');
      }
    });
  }
}

// Initialize footer functionality
function initFooterFunctionality() {
  const yearSpan = document.getElementById('year');
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }
}

// Initialize theme toggle functionality
function initThemeToggle() {
  const themeToggleMenus = document.querySelectorAll('.theme-toggle-menu');
  
  themeToggleMenus.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      
      // Get the associated icon based on button ID
      const isMenu = btn.id.includes('Menu');
      const iconElement = isMenu ? btn.querySelector('.icon') : btn;
      
      // Get current theme
      const currentTheme = localStorage.getItem('theme') || 'dark';
      const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
      
      // Save to localStorage
      localStorage.setItem('theme', newTheme);
      
      // Update document
      document.documentElement.setAttribute('data-theme', newTheme);
      
      // Update icon
      if (iconElement) {
        iconElement.textContent = newTheme === 'dark' ? '☀️' : '🌙';
      }
    });
  });
}

// Load on document ready
document.addEventListener('DOMContentLoaded', function() {
  initHeaderFunctionality();
  initFooterFunctionality();
  initThemeToggle();
  initSearchModal();
});

// Initialize search modal functionality
function initSearchModal() {
  const searchBtnMobile = document.getElementById('searchBtnMobile');
  const searchModal = document.getElementById('searchModal');
  const searchModalClose = document.getElementById('searchModalClose');
  const searchInput = document.getElementById('searchInput');
  const searchForm = document.getElementById('searchForm');

  if (!searchBtnMobile || !searchModal) return;

  // Open search modal
  searchBtnMobile.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    searchModal.classList.add('active');
    document.body.style.overflow = 'hidden';
    setTimeout(() => searchInput.focus(), 100);
  });

  // Close search modal
  function closeSearchModal() {
    searchModal.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (searchModalClose) {
    searchModalClose.addEventListener('click', closeSearchModal);
  }

  // Close on ESC key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && searchModal.classList.contains('active')) {
      closeSearchModal();
    }
  });

  // Close on modal background click
  searchModal.addEventListener('click', (e) => {
    if (e.target === searchModal) {
      closeSearchModal();
    }
  });

  // Submit search form
  if (searchForm) {
    searchForm.addEventListener('submit', (e) => {
      if (!searchInput.value.trim()) {
        e.preventDefault();
      }
    });
  }

  // Close modal when search is submitted
  if (searchForm) {
    searchForm.addEventListener('submit', () => {
      closeSearchModal();
    });
  }
}
