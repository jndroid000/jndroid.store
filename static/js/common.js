// Initialize mobile menu functionality
function initHeaderFunctionality() {
  const menuBtn = document.getElementById('menuBtn');
  const closeBtn = document.getElementById('closeBtn');
  const drawer = document.getElementById('drawer');
  const drawerOverlay = document.getElementById('drawerOverlay');
  const drawerNav = document.querySelectorAll('.drawer-nav a');

  if (!menuBtn || !drawer) return;

  // Open drawer
  menuBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    drawer.classList.add('show');
    document.body.style.overflow = 'hidden';
  });

  // Close drawer
  function closeDrawer() {
    drawer.classList.remove('show');
    document.body.style.overflow = '';
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

  // Close drawer on ESC key
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
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
