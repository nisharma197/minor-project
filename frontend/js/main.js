/* ============================================================
   FIRE NOC SYSTEM - Main JavaScript Utilities
   ============================================================ */

const API = (window.location.origin && window.location.origin !== 'null')
  ? `${window.location.origin}/api`
  : 'http://localhost:5000/api';

/* ── Token helpers ─────────────────────────────────────────── */
function getToken() { return localStorage.getItem('fire_noc_token'); }
function getUser() { const u = localStorage.getItem('fire_noc_user'); return u ? JSON.parse(u) : null; }
function setAuth(token, user) {
  localStorage.setItem('fire_noc_token', token);
  localStorage.setItem('fire_noc_user', JSON.stringify(user));
}
function clearAuth() { localStorage.removeItem('fire_noc_token'); localStorage.removeItem('fire_noc_user'); }

/* ── Redirect if not logged in ─────────────────────────────── */
function requireAuth(role) {
  const token = getToken();
  const user = getUser();
  if (!token || !user) { window.location.href = '/pages/login.html'; return false; }
  if (role && user.role !== role) {
    // redirect to correct dashboard
    redirectByRole(user.role);
    return false;
  }
  return true;
}

function redirectByRole(role) {
  const map = { admin: 'admin-dashboard.html', inspector: 'inspector-dashboard.html', applicant: 'applicant-dashboard.html' };
  window.location.href = '/pages/' + (map[role] || 'login.html');
}

/* ── API fetch wrapper ─────────────────────────────────────── */
async function apiFetch(path, options = {}) {
  const token = getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = 'Bearer ' + token;

  showLoading();
  try {
    const res = await fetch(API + path, { ...options, headers, credentials: 'same-origin' });
    let data = null;
    try {
      data = await res.json();
    } catch (jsonError) {
      data = { error: 'Invalid JSON response from server' };
    }
    if (res.status === 401 || res.status === 422) {
      clearAuth();
      window.location.href = '/pages/login.html';
    }
    if (!res.ok && data?.error) showToast(data.error, 'error');
    return { ok: res.ok, status: res.status, data };
  } catch (e) {
    showToast('Network error. Is the backend running?', 'error');
    return { ok: false, data: { error: 'Network error. Is the backend running?' } };
  } finally {
    hideLoading();
  }
}

/* ── Form data upload (multipart) ─────────────────────────── */
async function apiUpload(path, formData) {
  const token = getToken();
  showLoading();
  try {
    const headers = token ? { 'Authorization': 'Bearer ' + token } : {};
    const res = await fetch(API + path, {
      method: 'POST',
      headers,
      credentials: 'same-origin',
      body: formData
    });
    let data = null;
    try {
      data = await res.json();
    } catch (jsonError) {
      data = { error: 'Invalid JSON response from server' };
    }
    hideLoading();
    if (res.status === 401 || res.status === 422) { clearAuth(); window.location.href = '/pages/login.html'; }
    if (!res.ok && data?.error) showToast(data.error, 'error');
    return { ok: res.ok, status: res.status, data };
  } catch (e) {
    hideLoading();
    showToast('Network error', 'error');
    return { ok: false, data: { error: 'Network error' } };
  }
}

/* ── Toast notifications ───────────────────────────────────── */
function showToast(message, type = 'info') {
  const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
  const container = document.getElementById('toastContainer') || createToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<span class="toast-icon">${icons[type]}</span><span class="toast-msg">${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => toast.classList.add('show'), 10);
  setTimeout(() => { toast.classList.remove('show'); setTimeout(() => toast.remove(), 400); }, 3500);
}
function createToastContainer() {
  const c = document.createElement('div');
  c.id = 'toastContainer'; c.className = 'toast-container';
  document.body.appendChild(c); return c;
}

/* ── Loading overlay ───────────────────────────────────────── */
function showLoading() { const el = document.getElementById('loadingOverlay'); if (el) el.classList.add('show'); }
function hideLoading() { const el = document.getElementById('loadingOverlay'); if (el) el.classList.remove('show'); }

/* ── Modal helpers ─────────────────────────────────────────── */
function openModal(id) { document.getElementById(id)?.classList.add('show'); }
function closeModal(id) { document.getElementById(id)?.classList.remove('show'); }

/* ── Status badge ──────────────────────────────────────────── */
function statusBadge(status) {
  const map = {
    'Pending': 'badge-pending',
    'Under Inspection': 'badge-inspection',
    'Follow-up Required': 'badge-followup',
    'Approved': 'badge-approved',
    'Rejected': 'badge-rejected',
    'Scheduled': 'badge-scheduled',
    'In Progress': 'badge-inprogress',
    'Completed': 'badge-completed',
    'Failed': 'badge-failed',
    'Unread': 'badge-unread',
    'Read': 'badge-read',
    'High': 'badge-high',
    'Medium': 'badge-medium',
    'Low': 'badge-low',
  };
  return `<span class="badge ${map[status] || ''}">${status}</span>`;
}

/* ── Format date ───────────────────────────────────────────── */
function fmtDate(dt) {
  if (!dt || dt === 'None' || dt === 'null') return '—';
  const d = new Date(dt);
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

/* ── Sidebar toggle ────────────────────────────────────────── */
function initSidebar() {
  const btn = document.querySelector('.btn-menu');
  const sidebar = document.querySelector('.sidebar');
  if (btn && sidebar) {
    btn.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', e => {
      if (!sidebar.contains(e.target) && !btn.contains(e.target)) sidebar.classList.remove('open');
    });
  }
}

/* ── Populate sidebar user info ────────────────────────────── */
function populateSidebarUser() {
  const user = getUser();
  if (!user) return;
  const nameEl = document.getElementById('sidebarUserName');
  const roleEl = document.getElementById('sidebarUserRole');
  const avatarEl = document.getElementById('sidebarAvatar');
  if (nameEl) nameEl.textContent = user.full_name;
  if (roleEl) roleEl.textContent = user.role;
  if (avatarEl) avatarEl.textContent = user.full_name?.charAt(0).toUpperCase();
}

/* ── Load unread notifications count ──────────────────────── */
async function loadNotifCount() {
  const user = getUser();
  if (!user) return;
  const res = await apiFetch('/notifications/' + user.id);
  if (res.ok) {
    const unread = res.data.filter(n => n.status === 'Unread').length;
    const badge = document.getElementById('notifBadge');
    if (badge) { badge.textContent = unread; badge.style.display = unread > 0 ? 'flex' : 'none'; }
  }
}

/* ── Logout ────────────────────────────────────────────────── */
function logout() {
  clearAuth();
  window.location.href = '/pages/login.html';
}

/* ── Search filter for tables ──────────────────────────────── */
function filterTable(inputId, tableId) {
  const input = document.getElementById(inputId);
  const table = document.getElementById(tableId);
  if (!input || !table) return;
  input.addEventListener('keyup', function () {
    const q = this.value.toLowerCase();
    Array.from(table.querySelectorAll('tbody tr')).forEach(row => {
      row.style.display = row.textContent.toLowerCase().includes(q) ? '' : 'none';
    });
  });
}

/* ── Simple form validation ────────────────────────────────── */
function validateForm(formId) {
  const form = document.getElementById(formId);
  if (!form) return true;
  let valid = true;
  form.querySelectorAll('[required]').forEach(el => {
    const errEl = el.parentElement.querySelector('.form-error');
    if (!el.value.trim()) {
      valid = false;
      if (errEl) errEl.classList.add('show');
      el.style.borderColor = '#dc3545';
    } else {
      if (errEl) errEl.classList.remove('show');
      el.style.borderColor = '';
    }
  });
  return valid;
}

/* ── On DOM ready ──────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initSidebar();
  populateSidebarUser();
  loadNotifCount();

  // Mark active nav link
  const current = window.location.pathname.split('/').pop();
  document.querySelectorAll('.sidebar-nav a').forEach(a => {
    if (a.getAttribute('href') === current) a.classList.add('active');
  });

  // Close modal on overlay click
  document.querySelectorAll('.modal-overlay').forEach(m => {
    m.addEventListener('click', e => { if (e.target === m) m.classList.remove('show'); });
  });
});
