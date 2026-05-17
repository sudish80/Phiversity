/* ── Phiversity Application Layer ── Form handling, job polling, video player ── */
(function() {
  const { $, $$, el, escapeHtml, on, _emit, getState, setState, patchState } = Phiversity;
  const { login, signup, guestLogin, logout, me, submitRun, getJob, listJobs, llmKeyStatus } = PhiversityAPI;
  const { toast, openOverlay } = PhiversityUI;

  // ─── DOM refs ───
  const form = $('#run-form');
  const statusEl = $('#status');
  const videoEl = $('#result-video');
  const planLinkEl = $('#plan-link');
  const cornerStatus = $('#cornerStatus');
  const loadingStatus = $('#loading-status');
  const progressBar = $('#progress-bar');
  const progressText = $('#progress-text');
  const closeVideoBtn = $('#close-video');
  const downloadVideoBtn = $('#download-video');
  const shareVideoBtn = $('#share-video');
  const cancelBtn = $('#cancel-loading');
  const navUser = $('#nav-user');

  let activeJobId = null;
  let currentVideoObjectUrl = null;
  let currentVideoUrl = null;
  let pollTimer = null;
  let pollAbort = null;

  // ─── Status helper ───
  function setStatus(msg) {
    if (statusEl) {
      statusEl.textContent = msg;
      statusEl.style.display = msg ? '' : 'none';
    }
  }

  // ─── Recent jobs ───
  window.loadRecentJobs = async function loadRecentJobs() {
    const container = $('#recent-jobs');
    if (!container) return;
    try {
      const jobs = await PhiversityAPI.listJobs();
      if (!Array.isArray(jobs)) throw new Error('Invalid response');

      // Update video stat counter
      const statVideos = $('#stat-videos');
      if (statVideos) {
        const count = jobs.length;
        statVideos.dataset.target = count;
        statVideos.textContent = '0';
        PhiversityUI.animateCounters();
      }

      if (jobs.length === 0) {
        container.innerHTML = '<div class="job-empty">Submit a question to see your generated videos here.</div>';
        return;
      }
      container.innerHTML = jobs.slice(0, 10).map((j, idx) => {
        const status = j.status || 'unknown';
        const id = j.job_id || j.id || '';
        return `<div class="job-card" style="--stagger:${idx * 0.04}s" onclick="Phiversity._emit('loadJob','${id}')">
          <div class="job-card-top">
            <span class="job-card-id">${id.slice(0, 12)}...</span>
            <span class="job-card-status ${status}">${status}</span>
          </div>
          <div class="job-card-problem">${escapeHtml(j.problem || j.question || '')}</div>
        </div>`;
      }).join('');
    } catch {
      container.innerHTML = '<div class="job-empty">Failed to load recent jobs.</div>';
    }
  };

  // ─── Auth Init ───
  async function initAuth() {
    const user = getState('user');
    if (user && user.access_token) {
      try {
        const profile = await me();
        if (profile) {
          patchState({ user: { ...user, ...profile } });
          updateNavUser(profile);
          return;
        }
      } catch {}
    }
    // No valid user — try guest
    try {
      const guest = await PhiversityAPI.guestLogin();
      patchState({ user: guest });
      updateNavUser({ name: 'Guest', type: 'guest' });
    } catch (e) {
      setStatus('Could not create session. Please refresh.');
    }
  }

  function updateNavUser(profile) {
    if (!navUser) return;
    const name = profile?.full_name || profile?.name || profile?.email || 'Guest';
    const type = profile?.type || 'guest';
    navUser.textContent = type === 'guest' ? '👤 Guest' : `👤 ${name.slice(0, 12)}`;
    navUser.title = type === 'guest' ? 'Guest session — click for account options' : `Signed in as ${name}`;
  }

  // ─── Mode Selector ───
  document.querySelectorAll('.mode-card').forEach(card => {
    card.addEventListener('click', () => {
      $$('.mode-card').forEach(c => c.classList.remove('active'));
      card.classList.add('active');
      $('#learning-mode').value = card.dataset.mode;
    });
  });

  // ─── Form Submit ───
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    if (activeJobId) { toast('A job is already running', 'warning'); return; }

    const problem = $('#problem').value.trim();
    if (!problem) { toast('Please enter a problem', 'warning'); return; }

    // Ensure auth session
    if (!getState('user')) await initAuth();

    const payload = {
      problem,
      mode: $('#learning-mode').value || 'question_solving',
      orchestrate: $('#orchestrate').checked,
      voice_first: $('#voice-first').checked,
      element_audio: $('#element-audio').checked,
      long_video: false,
      custom_prompt: $('#custom-prompt').value.trim() || undefined,
    };

    // Toggle button state
    const submitBtn = $('#submit-btn');
    const btnText = submitBtn?.querySelector('.btn-text');
    const btnLoader = submitBtn?.querySelector('.btn-loader');
    if (submitBtn) submitBtn.disabled = true;
    if (btnText) btnText.style.display = 'none';
    if (btnLoader) btnLoader.style.display = '';

    setStatus('Submitting job...');
    PhiversityUI.openOverlay('loading');
    setLoadingProgress(0, 'Submitting...');

    try {
      const result = await PhiversityAPI.submitRun(payload);
      activeJobId = result.job_id || result.id;
      toast('Job submitted!', 'success');
      setStatus(`Job ID: ${activeJobId}`);
      startPolling(activeJobId);
    } catch (err) {
      PhiversityUI.closeOverlay('loading');
      setStatus(`Error: ${err.message}`);
      toast(`Submit failed: ${err.message}`, 'error');
      // Restore button
      if (submitBtn) submitBtn.disabled = false;
      if (btnText) btnText.style.display = '';
      if (btnLoader) btnLoader.style.display = 'none';
    }
  });

  // ─── Job Polling ───
  function startPolling(jobId) {
    pollAbort = new AbortController();
    let iterations = 0;
    const MAX_ITER = 3600;
    let backoff = 1500;

    (function poll() {
      if (pollAbort.signal.aborted || iterations >= MAX_ITER) {
        if (iterations >= MAX_ITER) {
          setStatus('Polling timed out after 90 minutes.');
          toast('Job timed out', 'error');
        }
        finishJob();
        return;
      }
      iterations++;

      PhiversityAPI.getJob(jobId).then(job => {
        const status = (job.status || '').toLowerCase();
        const progress = job.progress || 0;
        const log = job.log || '';

        setLoadingProgress(progress, log.split('\n').filter(Boolean).slice(-1)[0] || status);

        if (status === 'done') {
          finishJob();
          PhiversityUI.closeOverlay('loading');
          loadVideoResult(job);
        } else if (status === 'error') {
          finishJob();
          PhiversityUI.closeOverlay('loading');
          const errMsg = job.error || job.message || 'Unknown error';
          setStatus(`Error: ${errMsg}`);
          toast(`Error: ${errMsg}`, 'error');
        } else {
          backoff = Math.min(backoff * 1.3, 5000);
          setTimeout(poll, backoff);
        }
      }).catch(err => {
        if (pollAbort.signal.aborted) return;
        backoff = Math.min(backoff * 1.5, 8000);
        setTimeout(poll, backoff);
      });
    })();
  }

  function setLoadingProgress(pct, msg) {
    if (progressBar) progressBar.style.width = `${Math.min(pct, 100)}%`;
    if (progressText) progressText.textContent = `${Math.round(pct)}%`;
    if (loadingStatus) loadingStatus.textContent = msg || 'Processing...';
  }

  function finishJob() {
    activeJobId = null;
    pollAbort = null;
    const submitBtn = $('#submit-btn');
    const btnText = submitBtn?.querySelector('.btn-text');
    const btnLoader = submitBtn?.querySelector('.btn-loader');
    if (submitBtn) submitBtn.disabled = false;
    if (btnText) btnText.style.display = '';
    if (btnLoader) btnLoader.style.display = 'none';
  }

  // ─── Video Result ───
  async function loadVideoResult(job) {
    const videoUrl = job.video_url || job.video;
    const planUrl = job.plan_url || job.plan;
    const logUrl = job.log_url || job.log;

    // Confetti burst for completed video
    PhiversityUI.confetti(40);

    // Load protected video
    if (videoUrl) {
      try {
        await loadProtectedVideo(videoUrl);
      } catch (err) {
        toast(`Video load failed: ${err.message}`, 'error');
      }
    }

    // Show video overlay
    const speed = getState('settings').playbackSpeed;
    if (videoEl) videoEl.playbackRate = speed;
    PhiversityUI.openOverlay('video');

    // Set plan/log links
    if (planLinkEl && planUrl) {
      planLinkEl.innerHTML = `<a href="#" onclick="event.preventDefault(); downloadFile('${planUrl}', 'plan.json')">📄 Download Plan JSON</a>`;
    }
    const logLinkEl = $('#log-link');
    if (logLinkEl && logUrl) {
      logLinkEl.innerHTML = `<a href="#" onclick="event.preventDefault(); downloadFile('${logUrl}', 'job.log')">📋 Download Log</a>`;
    }

    // Set download
    if (downloadVideoBtn && currentVideoObjectUrl) {
      downloadVideoBtn.href = currentVideoObjectUrl;
      downloadVideoBtn.download = 'phiversity-video.mp4';
    }
  }

  async function loadProtectedVideo(url) {
    revokeCurrentVideoObjectUrl();
    try {
      const absolute = new URL(url, window.location.origin).toString();
      const res = await PhiversityAPI.apiFetch(absolute, {}, { requiresAuth: true });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const blob = await res.blob();
      currentVideoObjectUrl = URL.createObjectURL(blob);
      currentVideoUrl = absolute;
      if (videoEl) videoEl.src = currentVideoObjectUrl;
      if (getState('settings').autoPlay) videoEl.play().catch(() => {});
    } catch (err) {
      throw err;
    }
  }

  function revokeCurrentVideoObjectUrl() {
    if (currentVideoObjectUrl) { URL.revokeObjectURL(currentVideoObjectUrl); currentVideoObjectUrl = null; }
  }

  window.downloadFile = async function(url, name) {
    try {
      const absolute = new URL(url, window.location.origin).toString();
      const res = await PhiversityAPI.apiFetch(absolute, {}, { requiresAuth: true });
      const blob = await res.blob();
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = name;
      a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 1000);
    } catch (err) {
      toast(`Download failed: ${err.message}`, 'error');
    }
  };

  // ─── Video Controls ───
  closeVideoBtn?.addEventListener('click', () => PhiversityUI.closeOverlay('video'));
  $('#pip-video')?.addEventListener('click', () => {
    if (videoEl && document.pictureInPictureEnabled) {
      videoEl.requestPictureInPicture().catch(() => {});
    }
  });

  shareVideoBtn?.addEventListener('click', async () => {
    const url = currentVideoUrl || window.location.href;
    if (navigator.share) {
      try { await navigator.share({ title: 'Phiversity Video', url }); } catch {}
    } else {
      try {
        await navigator.clipboard.writeText(url);
        toast('Link copied!', 'success');
      } catch {
        toast('Share not available', 'warning');
      }
    }
  });

  cancelBtn?.addEventListener('click', () => {
    if (pollAbort) { pollAbort.abort(); finishJob(); }
    PhiversityUI.closeOverlay('loading');
    activeJobId = null;
    setStatus('Cancelled');
    toast('Cancelled', 'info');
  });

  // ─── Sample Button ───
  $('#sample-btn')?.addEventListener('click', () => {
    $('#problem').value = 'A 5 kg block slides on a 30 degree incline with friction coefficient 0.2. Find the acceleration.';
    $('#learning-mode').value = 'question_solving';
    $$('.mode-card').forEach(c => c.classList.remove('active'));
    document.querySelector('.mode-card[data-mode="question_solving"]')?.classList.add('active');
  });

  // ─── LLM Key Status ───
  async function loadLlmKeyStatus() {
    if (!cornerStatus) return;
    try {
      const data = await PhiversityAPI.llmKeyStatus();
      const items = data?.key_status || data?.llm_status || data || {};
      const parts = Object.entries(items).slice(0, 6).map(([k, v]) => {
        const ok = v === true || v === 'ok' || v === 'configured' || v === 'healthy';
        return `<span style="color:${ok ? '#16a34a' : '#ef4444'};font-size:11px">${ok ? '●' : '○'} ${k}</span>`;
      });
      if (parts.length) {
        cornerStatus.innerHTML = parts.join(' ');
        cornerStatus.classList.remove('hidden');
      }
    } catch {}
  }

  // ─── Auth UI handlers ───
  $('#form-login')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = $('#login-email').value;
    const password = $('#login-password').value;
    if (!email || !password) return;
    try {
      const user = await PhiversityAPI.login(email, password);
      patchState({ user });
      PhiversityUI.closeOverlay('login');
      toast('Logged in!', 'success');
      loadLlmKeyStatus();
      updateNavUser(user);
    } catch (err) { toast(`Login failed: ${err.message}`, 'error'); }
  });

  $('#form-signup')?.addEventListener('submit', async (e) => {
    e.preventDefault();
    const name = $('#signup-name').value;
    const email = $('#signup-email').value;
    const password = $('#signup-password').value;
    if (!name || !email || !password) return;
    try {
      const user = await PhiversityAPI.signup(name, email, password);
      patchState({ user });
      PhiversityUI.closeOverlay('login');
      toast('Account created!', 'success');
      loadLlmKeyStatus();
      updateNavUser(user);
    } catch (err) { toast(`Signup failed: ${err.message}`, 'error'); }
  });

  $('#guest-login')?.addEventListener('click', async () => {
    try {
      const guest = await PhiversityAPI.guestLogin();
      patchState({ user: guest });
      PhiversityUI.closeOverlay('login');
      toast('Guest session started', 'info');
      loadLlmKeyStatus();
      updateNavUser({ name: 'Guest', type: 'guest' });
    } catch (err) { toast(`Guest login failed: ${err.message}`, 'error'); }
  });

  // ─── Auth tab switching ───
  document.querySelectorAll('.auth-tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      document.querySelectorAll('.auth-form').forEach(f => f.classList.remove('active'));
      const form = document.getElementById('form-' + target);
      if (form) form.classList.add('active');
    });
  });

  // ─── Password strength indicator ───
  const pwInput = $('#signup-password');
  const pwBar = $('#pw-bar');
  const pwText = $('#pw-text');
  if (pwInput && pwBar && pwText) {
    pwInput.addEventListener('input', () => {
      const val = pwInput.value;
      let strength = 0;
      if (val.length >= 8) strength++;
      if (/[a-z]/.test(val) && /[A-Z]/.test(val)) strength++;
      if (/\d/.test(val)) strength++;
      if (/[^a-zA-Z0-9]/.test(val)) strength++;
      const pct = (strength / 4) * 100;
      const colors = ['#ef4444', '#f59e0b', '#3b82f6', '#22c55e'];
      const labels = ['Weak', 'Fair', 'Good', 'Strong'];
      pwBar.innerHTML = `<div class="pw-bar-fill" style="width:${pct}%;background:${colors[strength] || '#ef4444'}"></div>`;
      pwText.textContent = strength > 0 ? labels[strength - 1] : '';
      pwText.style.color = colors[strength] || '';
    });
  }

  // ─── Session expiry handler ───
  on('session-expired', () => {
    patchState({ user: null });
    PhiversityUI.closeOverlay('loading');
    PhiversityUI.openOverlay('login');
    toast('Session expired. Please log in again.', 'warning');
  });

  // ─── Init ───
  async function init() {
    // Initialize auth
    await initAuth();
    loadLlmKeyStatus();

    // Load LLM status periodically
    setInterval(loadLlmKeyStatus, 60000);

    // Show login overlay if no user
    if (!getState('user')) {
      setTimeout(() => PhiversityUI.openOverlay('login'), 300);
    }

    // Load recent jobs
    loadRecentJobs();

    // Refresh recent jobs after job completes
    on('overlay:close', (id) => {
      if (id === 'video') loadRecentJobs();
    });

    // Listen for job selection from history sidebar
    on('loadJob', (jobId) => {
      PhiversityUI.openOverlay('loading');
      setLoadingProgress(0, 'Loading job...');
      PhiversityAPI.getJob(jobId).then(job => {
        PhiversityUI.closeOverlay('loading');
        if (job.status === 'done') loadVideoResult(job);
        else toast(`Job status: ${job.status}`, 'info');
      }).catch(err => {
        PhiversityUI.closeOverlay('loading');
        toast(`Failed: ${err.message}`, 'error');
      });
    });

    console.log('[Phiversity] App initialized');
  }

  init();
})();
