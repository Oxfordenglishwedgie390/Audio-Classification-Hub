/* ═══════════════════════════════════════════════════════════════
   api.js  —  Centralized API client + session management
   All pages import this via <script src="js/api.js"></script>
   ═══════════════════════════════════════════════════════════════ */

const API_BASE = 'http://localhost:8000';

// ── Session helpers ───────────────────────────────────────────────────────────

const Session = {
  save(user) {
    sessionStorage.setItem('ach_user', JSON.stringify(user));
  },
  get() {
    try { return JSON.parse(sessionStorage.getItem('ach_user')) || null; }
    catch { return null; }
  },
  clear() {
    sessionStorage.removeItem('ach_user');
    sessionStorage.removeItem('ach_audio_files');
  },
  requireAuth(redirectTo = 'auth.html') {
    const u = this.get();
    if (!u) { window.location.href = redirectTo; return null; }
    return u;
  },
  saveFiles(blobs) {
    // Store file metadata (can't store Blob in sessionStorage directly, use window-level cache)
    window._achAudioBlobs = blobs;
  },
  getFiles() {
    return window._achAudioBlobs || [];
  },
};

// ── Safe JSON parser ─────────────────────────────────────────────────────────
// Reads response as text first; if JSON.parse fails returns the raw text as
// the error message instead of crashing with "Unexpected token".
async function safeJson(res) {
  const text = await res.text();
  try {
    return JSON.parse(text);
  } catch (_) {
    // Server returned non-JSON (e.g. "Internal Server Error") — wrap it
    const preview = text.slice(0, 120);
    if (!res.ok) throw new Error(`Server error ${res.status}: ${preview}`);
    throw new Error(`Invalid response: ${preview}`);
  }
}

// ── API Calls ─────────────────────────────────────────────────────────────────

async function apiRegister(name, email, password) {
  const fd = new FormData();
  fd.append('name', name);
  fd.append('email', email);
  fd.append('password', password);

  const res = await fetch(`${API_BASE}/api/register`, { method: 'POST', body: fd });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data.detail || 'Registration failed');
  return data;
}

async function apiLogin(email, password) {
  const fd = new FormData();
  fd.append('email', email);
  fd.append('password', password);

  const res = await fetch(`${API_BASE}/api/login`, { method: 'POST', body: fd });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data.detail || 'Login failed');
  return data;
}

async function apiProcess(email, audioBlobs) {
  const fd = new FormData();
  fd.append('email', email);
  audioBlobs.forEach((item, i) => {
    const name = item.name || `voice_sample_${i + 1}.wav`;
    fd.append('files', item.blob, name);
  });

  const res = await fetch(`${API_BASE}/api/process`, { method: 'POST', body: fd });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data.detail || 'Processing failed');
  return data;
}

async function apiStatus(email) {
  const res = await fetch(`${API_BASE}/api/status?email=${encodeURIComponent(email)}`);
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data.detail || 'Status check failed');
  return data;
}

function apiDownloadUrl(email) {
  return `${API_BASE}/api/download?email=${encodeURIComponent(email)}`;
}

async function apiVerify(email, audioBlob, filename) {
  const fd = new FormData();
  fd.append('email', email);
  fd.append('file', audioBlob, filename || 'verify_sample.wav');

  const res = await fetch(`${API_BASE}/api/verify`, { method: 'POST', body: fd });
  const data = await safeJson(res);
  if (!res.ok) throw new Error(data.detail || 'Verification failed');
  return data;
  // Returns: { confidence, cosine_score, label, matched, color, icon }
}

// ── UI helpers ────────────────────────────────────────────────────────────────

function showError(containerId, msg) {
  let el = document.getElementById(containerId);
  if (!el) {
    el = document.createElement('div');
    el.id = containerId;
    el.className = 'error-banner';
  }
  el.textContent = msg;
  el.style.cssText = `
    margin-top:.75rem; padding:.75rem 1rem; border-radius:.6rem;
    background:rgba(239,68,68,0.12); border:1px solid rgba(239,68,68,0.35);
    color:#FCA5A5; font-size:.875rem; text-align:center;
  `;
  return el;
}

function showSuccess(containerId, msg) {
  let el = document.getElementById(containerId);
  if (!el) {
    el = document.createElement('div');
    el.id = containerId;
  }
  el.textContent = msg;
  el.style.cssText = `
    margin-top:.75rem; padding:.75rem 1rem; border-radius:.6rem;
    background:rgba(34,197,94,0.12); border:1px solid rgba(34,197,94,0.35);
    color:#86EFAC; font-size:.875rem; text-align:center;
  `;
  return el;
}

function setLoading(btn, loading, originalText) {
  if (loading) {
    btn.disabled = true;
    btn.dataset.orig = btn.innerHTML;
    btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin mr-2"></i>Please wait…';
  } else {
    btn.disabled = false;
    btn.innerHTML = originalText || btn.dataset.orig || btn.innerHTML;
  }
}
