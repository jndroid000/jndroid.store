// Initialize mobile menu functionality
function initHeaderFunctionality() {
  // Profile Dropdown Functionality
  const profileBtn = document.getElementById('profileBtn');
  const profileDropdown = document.querySelector('.profile-dropdown');
  const profileMenu = document.getElementById('profileMenu');

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

// Initialize bottom navigation menu functionality
function initBottomMenuFunctionality() {
  const moreMenuBtn = document.getElementById('moreMenuBtn');
  const bottomMenuModal = document.getElementById('bottomMenuModal');
  const bottomMenuClose = document.getElementById('bottomMenuClose');
  const bottomMenuOverlay = document.getElementById('bottomMenuOverlay');
  const bottomMenuItems = document.querySelectorAll('.bottom-menu-item');

  if (!moreMenuBtn || !bottomMenuModal) return;

  // Open bottom menu
  moreMenuBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    bottomMenuModal.classList.add('active');
    bottomMenuOverlay.classList.add('active');
  });

  // Close bottom menu
  function closeBottomMenu() {
    bottomMenuModal.classList.remove('active');
    bottomMenuOverlay.classList.remove('active');
  }

  if (bottomMenuClose) {
    bottomMenuClose.addEventListener('click', closeBottomMenu);
  }

  // Close menu on overlay click
  if (bottomMenuOverlay) {
    bottomMenuOverlay.addEventListener('click', closeBottomMenu);
  }

  // Close menu when clicking on a link/item
  bottomMenuItems.forEach(item => {
    item.addEventListener('click', closeBottomMenu);
  });

  // Also close menu when clicking form buttons in the menu
  const bottomMenuForms = document.querySelectorAll('.bottom-menu-nav form');
  bottomMenuForms.forEach(form => {
    const submitBtn = form.querySelector('button[type="submit"]');
    if (submitBtn) {
      submitBtn.addEventListener('click', closeBottomMenu);
    }
  });

  // Close menu on ESC key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && bottomMenuModal.classList.contains('active')) {
      closeBottomMenu();
    }
  });

  // Close menu when clicking outside
  document.addEventListener('click', (e) => {
    if (bottomMenuModal.classList.contains('active') && 
        !bottomMenuModal.contains(e.target) && 
        !moreMenuBtn.contains(e.target) &&
        !bottomMenuOverlay.contains(e.target)) {
      closeBottomMenu();
    }
  });
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
  const themeToggleMobile = document.getElementById('themeToggleMobile');
  
  const toggleTheme = () => {
    // Get current theme
    const currentTheme = localStorage.getItem('theme') || 'dark';
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    
    // Save to localStorage
    localStorage.setItem('theme', newTheme);
    
    // Update document
    document.documentElement.setAttribute('data-theme', newTheme);
    
    // Update desktop menu icons
    themeToggleMenus.forEach(btn => {
      const iconElement = btn.querySelector('.icon') || btn;
      if (iconElement) {
        iconElement.textContent = newTheme === 'dark' ? '☀️' : '🌙';
      }
    });
    
    // Update mobile menu icon and text
    if (themeToggleMobile) {
      const mobileIcon = document.getElementById('themeMobileIcon');
      const mobileText = document.getElementById('themeMobileText');
      if (mobileIcon) {
        mobileIcon.className = newTheme === 'dark' ? 'fas fa-sun' : 'fas fa-moon';
      }
      if (mobileText) {
        mobileText.textContent = newTheme === 'dark' ? 'Light Mode' : 'Dark Mode';
      }
    }
  };
  
  themeToggleMenus.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      toggleTheme();
    });
  });
  
  if (themeToggleMobile) {
    themeToggleMobile.addEventListener('click', (e) => {
      e.preventDefault();
      toggleTheme();
    });
  }
}

// Load on document ready
document.addEventListener('DOMContentLoaded', function() {
  initHeaderFunctionality();
  initBottomMenuFunctionality();
  initSearchModal();
  initThemeToggle();
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
