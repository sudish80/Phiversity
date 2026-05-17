/* ── Phiversity API Layer ── All backend communication ── */
const PhiversityAPI = (() => {
  const BASE = window.location.origin;

  // ── Token management ──
  function _getUser() {
    try { return JSON.parse(localStorage.getItem('manim_user') || 'null'); } catch { return null; }
  }

  function _saveUser(u) {
    localStorage.setItem('manim_user', JSON.stringify(u));
    if (u && u.access_token) localStorage.setItem('auth_token', u.access_token);
    if (!u) localStorage.removeItem('auth_token');
    Phiversity.patchState({ user: u });
  }

  function _getTokens() {
    const u = _getUser();
    return {
      access: u?.access_token || u?.token || localStorage.getItem('auth_token'),
      refresh: u?.refresh_token || u?.refreshToken,
      csrf: u?.csrf_token || u?.csrfToken,
    };
  }

  function _getAuthHeaders() {
    const { access } = _getTokens();
    return access ? { 'Authorization': 'Bearer ' + access } : {};
  }

  function _getCsrfHeader() {
    const { csrf } = _getTokens();
    return csrf ? { 'X-CSRF-Token': csrf } : {};
  }

  let refreshInFlight = null;

  async function refreshToken() {
    if (refreshInFlight) return refreshInFlight;
    refreshInFlight = (async () => {
      const { refresh } = _getTokens();
      if (!refresh) throw new Error('No refresh token');
      const res = await fetch(BASE + '/api/v1/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (!res.ok) { _saveUser(null); throw new Error('Refresh failed'); }
      const data = await res.json();
      const u = _getUser() || {};
      u.access_token = data.access_token || data.token;
      u.refresh_token = data.refresh_token || data.refreshToken;
      u.csrf_token = res.headers.get('X-CSRF-Token') || u.csrf_token;
      _saveUser(u);
      return u;
    })();
    try { return await refreshInFlight; } finally { refreshInFlight = null; }
  }

  // ── Core request ──
  async function apiFetch(path, init = {}, opts = {}) {
    const { requiresAuth = true, retry = 1 } = opts;
    const headers = { ...init.headers };
    if (requiresAuth) Object.assign(headers, _getAuthHeaders(), _getCsrfHeader());
    if (!headers['Content-Type'] && !(init.body instanceof FormData)) {
      headers['Content-Type'] = 'application/json';
    }
    let res = await fetch(BASE + path, { ...init, headers, credentials: 'include' });
    if (res.status === 401 && requiresAuth && retry > 0) {
      try {
        await refreshToken();
        const retryHeaders = { ...init.headers, ..._getAuthHeaders(), ..._getCsrfHeader() };
        res = await fetch(BASE + path, { ...init, headers: retryHeaders, credentials: 'include' });
      } catch { _saveUser(null); throw new Error('Session expired'); }
    }
    if (!res.ok) {
      let msg = `HTTP ${res.status}`;
      try { const e = await res.json(); msg = e.detail || e.message || msg; } catch {}
      throw new Error(msg);
    }
    const csrf = res.headers.get('X-CSRF-Token');
    if (csrf) {
      const u = _getUser();
      if (u) { u.csrf_token = csrf; _saveUser(u); }
    }
    return res;
  }

  async function apiGet(path) { return apiFetch(path); }
  async function apiPost(path, body) {
    return apiFetch(path, { method: 'POST', body: JSON.stringify(body) });
  }
  async function apiDelete(path) { return apiFetch(path, { method: 'DELETE' }); }
  async function apiJson(path, init, opts) {
    const res = await apiFetch(path, init, opts);
    return res.json();
  }

  // ── Auth endpoints ──
  async function login(email, password) {
    const res = await apiFetch('/api/v1/auth/token', {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    }, { requiresAuth: false });
    const data = await res.json();
    const csrf = res.headers.get('X-CSRF-Token') || '';
    const user = {
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      csrf_token: csrf,
      type: 'user',
    };
    _saveUser(user);
    return user;
  }

  async function signup(fullName, email, password) {
    await apiJson('/api/v1/auth/signup', {
      method: 'POST', body: JSON.stringify({ full_name: fullName, email, password }),
    }, { requiresAuth: false });
    return login(email, password);
  }

  async function guestLogin() {
    const res = await apiFetch('/api/v1/auth/guest', { method: 'POST' }, { requiresAuth: false });
    const data = await res.json();
    const csrf = res.headers.get('X-CSRF-Token') || '';
    const user = {
      access_token: data.access_token,
      refresh_token: data.refresh_token,
      csrf_token: csrf,
      type: 'guest',
    };
    _saveUser(user);
    return user;
  }

  async function logout() {
    try { await apiFetch('/api/v1/auth/logout', { method: 'POST' }); } catch {}
    _saveUser(null);
  }

  async function me() { return apiJson('/api/v1/auth/me'); }

  // ── Job endpoints ──
  async function submitRun(params) {
    return apiJson('/api/v1/run', { method: 'POST', body: JSON.stringify(params) });
  }

  async function getJob(jobId) { return apiJson(`/api/v1/jobs/${jobId}`); }
  async function listJobs() { return apiJson('/api/v1/jobs'); }

  // ── System endpoints ──
  async function llmKeyStatus() { return apiJson('/api/v1/system/llm-key-status?_=' + Date.now()); }

  // ── Billing endpoints ──
  async function billingTiers() { return apiJson('/api/v1/billing/tiers'); }

  async function createCheckout(provider, tier) {
    return apiJson('/api/v1/billing/checkout', {
      method: 'POST',
      body: JSON.stringify({
        provider,
        tier,
        success_url: window.location.href,
        cancel_url: window.location.href,
      }),
    });
  }

  return {
    login, signup, guestLogin, logout, me, refreshToken,
    submitRun, getJob, listJobs,
    llmKeyStatus,
    billingTiers, createCheckout,
    apiFetch, apiGet, apiPost, apiDelete, apiJson,
  };
})();
