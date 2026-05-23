/* ============================================================
   FIRE NOC SYSTEM - Sidebar Builder
   ============================================================ */

function buildSidebar(role) {
  const navItems = {
    admin: [
      { label:'Dashboard',      icon:'fas fa-tachometer-alt', href:'admin-dashboard.html' },
      { label:'Applications',   icon:'fas fa-file-alt',       href:'inspection-management.html' },
      { label:'Inspections',    icon:'fas fa-search',         href:'inspection-management.html' },
      { label:'Follow-ups',     icon:'fas fa-redo',           href:'followup-management.html' },
      { label:'NOC Management', icon:'fas fa-certificate',    href:'noc-management.html' },
      { label:'Reports',        icon:'fas fa-chart-bar',      href:'reports.html' },
      { label:'Notifications',  icon:'fas fa-bell',           href:'notifications.html' },
      { label:'Profile',        icon:'fas fa-user',           href:'profile.html' },
    ],
    inspector: [
      { label:'Dashboard',      icon:'fas fa-tachometer-alt', href:'inspector-dashboard.html' },
      { label:'My Inspections', icon:'fas fa-search',         href:'inspection-management.html' },
      { label:'Follow-ups',     icon:'fas fa-redo',           href:'followup-management.html' },
      { label:'Applications',   icon:'fas fa-file-alt',       href:'application-status.html' },
      { label:'Notifications',  icon:'fas fa-bell',           href:'notifications.html' },
      { label:'Profile',        icon:'fas fa-user',           href:'profile.html' },
    ],
    applicant: [
      { label:'Dashboard',      icon:'fas fa-tachometer-alt', href:'applicant-dashboard.html' },
      { label:'New Application',icon:'fas fa-plus-circle',    href:'application-form.html' },
      { label:'My Applications',icon:'fas fa-file-alt',       href:'application-status.html' },
      { label:'My Documents',   icon:'fas fa-folder',         href:'application-status.html' },
      { label:'NOC Status',     icon:'fas fa-certificate',    href:'noc-management.html' },
      { label:'Notifications',  icon:'fas fa-bell',           href:'notifications.html' },
      { label:'Profile',        icon:'fas fa-user',           href:'profile.html' },
    ]
  };

  const items = navItems[role] || navItems['applicant'];
  const current = window.location.pathname.split('/').pop();

  return `
  <aside class="sidebar" id="sidebar">
    <div class="sidebar-brand">
      <span style="font-size:2rem">🔥</span>
      <span>Fire NOC <small>Management System</small></span>
    </div>
    <nav class="sidebar-nav">
      <div class="nav-label">Main Menu</div>
      ${items.map(item => `
        <a href="${item.href}" class="${current === item.href ? 'active' : ''}">
          <i class="${item.icon}"></i> ${item.label}
        </a>
      `).join('')}
    </nav>
    <div class="sidebar-footer">
      <div class="user-info">
        <div class="avatar" id="sidebarAvatar">A</div>
        <div>
          <div class="user-name" id="sidebarUserName">Loading...</div>
          <div class="user-role" id="sidebarUserRole">${role}</div>
        </div>
      </div>
      <button class="btn-logout" onclick="logout()">
        <i class="fas fa-sign-out-alt"></i> Logout
      </button>
    </div>
  </aside>`;
}

function injectLayout(role, pageTitle) {
  // Build and inject sidebar + navbar
  document.body.insertAdjacentHTML('afterbegin', buildSidebar(role));

  const navbar = `
  <nav class="top-navbar">
    <div style="display:flex;align-items:center;gap:12px">
      <button class="btn-menu" onclick="document.getElementById('sidebar').classList.toggle('open')">
        <i class="fas fa-bars"></i>
      </button>
      <span class="page-title">${pageTitle}</span>
    </div>
    <div class="nav-actions">
      <button class="notif-bell" onclick="window.location.href='notifications.html'">
        <i class="fas fa-bell"></i>
        <span class="badge" id="notifBadge" style="display:none">0</span>
      </button>
      <div style="font-size:.82rem;color:#666">
        <i class="fas fa-circle" style="color:#28a745;font-size:.5rem;margin-right:4px"></i>Online
      </div>
    </div>
  </nav>`;

  document.querySelector('.main-content').insertAdjacentHTML('afterbegin', navbar);

  // Inject loading overlay + toast container
  document.body.insertAdjacentHTML('beforeend', `
    <div id="loadingOverlay" class="loading-overlay">
      <div class="spinner"></div>
      <p style="margin-top:12px;color:#666;font-size:.88rem">Loading...</p>
    </div>
    <div id="toastContainer" class="toast-container"></div>
  `);

  populateSidebarUser();
  loadNotifCount();
}
