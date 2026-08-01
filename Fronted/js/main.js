/* ═══════════════════════════════════════════
   SHARED UI LOGIC — navbar, reveal, copy, marquee
   ═══════════════════════════════════════════ */

// Navbar scroll state
document.addEventListener('DOMContentLoaded', () => {
  const nav = document.querySelector('.navbar');
  if (nav) {
    const onScroll = () => nav.classList.toggle('scrolled', window.scrollY > 30);
    window.addEventListener('scroll', onScroll);
    onScroll();
  }

  // Scroll reveal with stagger
  const reveals = document.querySelectorAll('.reveal');
  const io = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const delay = entry.target.dataset.delay || 0;
        setTimeout(() => entry.target.classList.add('in'), delay);
        io.unobserve(entry.target);
      }
    });
  }, { threshold: 0.12 });
  reveals.forEach(el => io.observe(el));

  // Mobile menu
  const burger = document.getElementById('burger');
  const sheet = document.getElementById('mobile-sheet');
  if (burger && sheet) {
    burger.addEventListener('click', () => sheet.classList.toggle('open'));
    sheet.querySelectorAll('a').forEach(a => a.addEventListener('click', () => sheet.classList.remove('open')));
  }
});

// Copy to clipboard helper (used by docs / code blocks)
function copyCode(btn, text) {
  navigator.clipboard.writeText(text).then(() => {
    const original = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-check"></i>';
    btn.classList.add('text-green-400');
    setTimeout(() => {
      btn.innerHTML = original;
      btn.classList.remove('text-green-400');
    }, 2000);
  });
}

// ── Session-aware helpers ─────────────────────────────────────────────────────
function _getSessionUser() {
  try { return JSON.parse(sessionStorage.getItem('ach_user')) || null; }
  catch { return null; }
}

function _signOut() {
  sessionStorage.removeItem('ach_user');
  if (window._achAudioBlobs) window._achAudioBlobs = [];
  window.location.href = 'index.html';
}

// Reusable navbar HTML injector
function renderNavbar(active) {
  const user = _getSessionUser();

  const authLinks = user
    ? `<a href="download.html" class="nav-link ${active === 'docs' ? '!text-white' : ''}">My Dashboard</a>
       <button onclick="_signOut()" class="btn-ghost text-sm py-2 px-4"><i class="fa-solid fa-right-from-bracket text-xs mr-1"></i>Sign Out</button>`
    : `<a href="auth.html" class="nav-link">Sign In</a>
       <a href="auth.html" class="btn-primary text-sm py-2 px-4">Get Started <i class="fa-solid fa-arrow-right text-xs"></i></a>`;

  const authMobile = user
    ? `<a href="download.html" class="nav-link">My Dashboard</a>
       <button onclick="_signOut()" class="nav-link">Sign Out</button>`
    : `<a href="auth.html" class="nav-link">Sign In</a>
       <a href="auth.html" class="btn-primary justify-center">Get Started</a>`;

  return `
  <nav class="navbar">
    <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
      <a href="index.html" class="flex items-center gap-3">
        <div class="logo-bars"><span></span><span></span><span></span><span></span><span></span></div>
        <span class="font-semibold text-[15px] tracking-tight">Audio Classification Hub</span>
      </a>
      <div class="hidden md:flex items-center gap-7">
        <a href="download.html" class="nav-link ${active === 'docs' ? '!text-white' : ''}">Docs</a>
        <a href="download.html#core-api" class="nav-link">API</a>
        <a href="#" class="nav-link">Blog</a>
        <a href="#" class="nav-link">GitHub <i class="fa-solid fa-arrow-up-right-from-square text-[10px]"></i></a>
      </div>
      <div class="hidden md:flex items-center gap-3">
        ${authLinks}
      </div>
      <button id="burger" class="md:hidden text-2xl" aria-label="Open menu"><i class="fa-solid fa-bars"></i></button>
    </div>
    <div id="mobile-sheet" class="mobile-sheet md:hidden">
      <a href="download.html" class="nav-link">Docs</a>
      <a href="download.html#core-api" class="nav-link">API</a>
      <a href="#" class="nav-link">Blog</a>
      <a href="#" class="nav-link">GitHub</a>
      ${authMobile}
    </div>
  </nav>`;
}

function renderFooter() {
  return `
  <footer class="border-t border-white/[0.06] mt-12">
    <div class="max-w-7xl mx-auto px-6 py-16 grid grid-cols-2 md:grid-cols-4 gap-10">
      <div class="col-span-2 md:col-span-1">
        <div class="flex items-center gap-3 mb-4">
          <div class="logo-bars"><span></span><span></span><span></span><span></span><span></span></div>
          <span class="font-semibold text-sm">Audio Classification Hub</span>
        </div>
        <p class="text-sm text-secondary max-w-xs">Your Voice. Your Identity. Zero Compromise.</p>
      </div>
      <div>
        <h4 class="text-sm font-semibold mb-4">Product</h4>
        <ul class="space-y-2 text-sm text-secondary">
          <li><a href="index.html#how" class="nav-link">How it works</a></li>
          <li><a href="download.html" class="nav-link">Download</a></li>
        </ul>
      </div>
      <div>
        <h4 class="text-sm font-semibold mb-4">Developers</h4>
        <ul class="space-y-2 text-sm text-secondary">
          <li><a href="download.html" class="nav-link">Docs</a></li>
          <li><a href="download.html#core-api" class="nav-link">API Reference</a></li>
          <li><a href="#" class="nav-link">GitHub</a></li>
        </ul>
      </div>
      <div>
        <h4 class="text-sm font-semibold mb-4">Company</h4>
        <ul class="space-y-2 text-sm text-secondary">
          <li><a href="#" class="nav-link">About</a></li>
          <li><a href="#" class="nav-link">Privacy</a></li>
          <li><a href="#" class="nav-link">GDPR</a></li>
        </ul>
      </div>
    </div>
    <div class="border-t border-white/[0.06] py-6 text-center text-xs text-muted font-mono">
      Made with Python + PyTorch · ECapa-TDNN · © 2026 Audio Classification Hub
    </div>
  </footer>`;
}
