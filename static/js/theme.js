// Theme Management
(function() {
  // Get saved theme or default to 'dark'
  const savedTheme = localStorage.getItem('theme') || 'dark';
  
  // Apply theme immediately to prevent flash
  applyTheme(savedTheme);
  
  function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    
    // Update all theme toggle icons
    updateThemeIcons(theme);
  }
  
  function updateThemeIcons(theme) {
    const themeToggleMenus = document.querySelectorAll('.theme-toggle-menu .icon');
    const themeToggle = document.querySelector('.theme-toggle');
    
    const icon = theme === 'dark' ? '☀️' : '🌙';
    
    themeToggleMenus.forEach(el => {
      el.textContent = icon;
    });
    
    if (themeToggle) {
      themeToggle.textContent = icon;
    }
  }
  
  // Store reference for use in common.js if needed
  window.applyTheme = applyTheme;
})();