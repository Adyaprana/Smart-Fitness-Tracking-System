// Main JavaScript for Smart Fitness Tracker
// Handles theme switching and navigation interactions

(function () {
  function updateThemeToggleUI(theme) {
    const isLight = theme === 'light';
    const icon = isLight ? '☀' : '🌙';
    const label = isLight ? 'Light' : 'Dark';
    const mobileLabel = isLight ? 'Light mode' : 'Dark mode';

    document.querySelectorAll('[data-theme-toggle-icon]').forEach((el) => {
      el.textContent = icon;
    });

    document.querySelectorAll('[data-theme-toggle-label]').forEach((el) => {
      if (el.closest('.theme-toggle-mobile')) {
        el.textContent = mobileLabel;
      } else {
        el.textContent = label;
      }
    });
  }

  function applyTheme(theme) {
    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
    updateThemeToggleUI(theme);
  }

  function initTheme() {
    // Always start in dark mode on load
    applyTheme('dark');
  }

  function initThemeToggle() {
    const toggles = document.querySelectorAll('[data-theme-toggle]');
    if (!toggles.length) return;

    toggles.forEach((btn) => {
      btn.addEventListener('click', () => {
        const current =
          document.documentElement.getAttribute('data-theme') || 'dark';
        const next = current === 'dark' ? 'light' : 'dark';
        applyTheme(next);
      });
    });
  }

  function initMobileNav() {
    const navToggle = document.getElementById('navToggle');
    const mobileNav = document.getElementById('mobileNav');
    const mobileClose = document.getElementById('mobileNavClose');
    const mobileBackdrop = document.getElementById('mobileNavBackdrop');

    if (!mobileNav || !navToggle) return;

    const open = () => {
      mobileNav.classList.add('is-open');
      document.body.classList.add('nav-open');
    };

    const close = () => {
      mobileNav.classList.remove('is-open');
      document.body.classList.remove('nav-open');
    };

    navToggle.addEventListener('click', () => {
      if (mobileNav.classList.contains('is-open')) {
        close();
      } else {
        open();
      }
    });

    if (mobileClose) {
      mobileClose.addEventListener('click', close);
    }
    if (mobileBackdrop) {
      mobileBackdrop.addEventListener('click', close);
    }

    // Close panel on navigation
    mobileNav.querySelectorAll('a').forEach((link) => {
      link.addEventListener('click', close);
    });
  }

  document.addEventListener('DOMContentLoaded', function () {
    initTheme();
    initThemeToggle();
    initMobileNav();
  });
})();
