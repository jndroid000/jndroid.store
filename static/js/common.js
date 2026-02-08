// Initialize mobile menu functionality
function initHeaderFunctionality() {
  const menuBtn = document.getElementById('menuBtn');
  const closeBtn = document.getElementById('closeBtn');
  const drawer = document.getElementById('drawer');
  const drawerOverlay = document.getElementById('drawerOverlay');
  const drawerNav = document.querySelectorAll('.drawer-nav a');
  const drawerFormBtn = document.querySelectorAll('.drawer-form-btn');

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
}

// Initialize footer functionality
function initFooterFunctionality() {
  const yearSpan = document.getElementById('year');
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }
}

// Load on document ready
document.addEventListener('DOMContentLoaded', function() {
  initHeaderFunctionality();
  initFooterFunctionality();
});
