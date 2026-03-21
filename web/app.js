// Configuration
const API_URL = window.location.origin;

// ─── DOM references ───
const form = document.getElementById('run-form');
const statusEl = document.getElementById('status');
const videoSection = document.getElementById('video-section');
const videoEl = document.getElementById('result-video');
const planLinkEl = document.getElementById('plan-link');
const cornerStatus = document.getElementById('cornerStatus');
const closeVideoBtn = document.getElementById('close-video');
const downloadVideoBtn = document.getElementById('download-video');
const shareVideoBtn = document.getElementById('share-video');
const statusList = document.getElementById('status-list');
const overallStatusEl = document.getElementById('overall-status');

// Declare elements referenced by loadLlmKeyStatus (may not exist in DOM)
const jobsListCard = document.getElementById('jobs-list-card');
const jobsList = document.getElementById('jobs-list');
const refreshJobsBtn = document.getElementById('refresh-jobs-btn');
const refreshBtn = document.getElementById('refresh-btn');

// ─── Current job abort controller ───
let currentAbortController = null;
let currentVideoUrl = null; // track latest generated video URL

// ─── Utilities ───
function getAuthHeaders() {
  const user = localStorage.getItem('manim_user');
  if (!user) return {};
  try {
    const data = JSON.parse(user);
    const token = data.token || data.access_token;
    if (token) return { 'Authorization': `Bearer ${token}` };
  } catch (e) { }
  return {};
}

/** Efficient HTML escaping without DOM element creation per call */
const _escapeMap = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' };
function escapeHtml(text) {
  return String(text).replace(/[&<>"']/g, ch => _escapeMap[ch]);
}

function setStatusHTML(html) {
  statusEl.innerHTML = html;
}

function setStatus(text) {
  statusEl.textContent = text;
}

function hideLoadingOverlay() {
  const la = document.getElementById('loading-animation');
  if (la) la.classList.add('hidden');
}

function showLoadingOverlay() {
  const la = document.getElementById('loading-animation');
  if (la) la.classList.remove('hidden');
}

function restoreCornerStatus() {
  if (cornerStatus && cornerStatus.innerHTML.trim()) {
    cornerStatus.classList.remove('hidden');
  }
}

// ─── Auto-fill sample content on page load ───
const problemInput = document.getElementById('problem');
if (problemInput && !problemInput.value) {
  problemInput.value = 'Explain angular momentum conservation in collisions';
}

// ─── LLM key status loader ───
async function loadLlmKeyStatus() {
  if (!statusList) return;
  statusList.innerHTML = '<div class="status">Loading key status…</div>';
  try {
    const res = await fetch('/media/texts/llm_key_check.json?_=' + Date.now());
    if (!res.ok) {
      statusList.innerHTML = `<div class="status">No status file found (HTTP ${res.status}). Run <code>python test/verify_llm_keys.py</code>.</div>`;
      return;
    }
    const data = await res.json();
    const items = (data.checks || []).map(c => {
      const pass = !!(c.reachable && c.auth_valid);
      const cls = pass ? 'pass' : 'fail';
      const badge = pass ? 'PASS' : 'FAIL';
      const err = c.error ? escapeHtml(c.error) : '';
      const lat = c.latency_ms != null ? `${c.latency_ms} ms` : 'n/a';
      return `
        <div class="status-item ${cls}">
          <span class="badge ${cls}">${badge}</span>
          <strong>${escapeHtml(c.service)}</strong>
          <span>latency: ${lat}</span>
          ${err ? `<span class="hint">${err}</span>` : ''}
        </div>
      `;
    });
    statusList.innerHTML = items.join('') || '<div class="status">No checks found in JSON.</div>';
    if (overallStatusEl) {
      const anyPass = !!(data.summary && data.summary.any_pass);
      const passCount = data.summary ? data.summary.pass_count : 0;
      const svcPass = data.summary ? (data.summary.services_pass || []) : [];
      overallStatusEl.className = 'status ' + (anyPass ? 'pass' : 'fail');
      overallStatusEl.innerHTML = anyPass
        ? `Overall: PASS — ${passCount} service(s): ${escapeHtml(svcPass.join(', '))}`
        : 'Overall: FAIL — no service passed';
    }

    // Corner: show only passed LLMs and voice
    if (cornerStatus && data.summary) {
      const passSvcs = data.summary.services_pass || [];
      const llmPass = passSvcs.filter(s => ['openai', 'deepseek', 'gemini', 'ollama'].includes(s));
      let voice = null;
      if (passSvcs.includes('elevenlabs')) voice = 'elevenlabs';
      else if (passSvcs.includes('pyttsx3')) voice = 'pyttsx3';
      const lines = [];
      if (llmPass.length) {
        lines.push(`<div class="line"><span class="badge">LLM</span><span>${escapeHtml(llmPass.join(', '))}</span></div>`);
      }
      if (voice) {
        lines.push(`<div class="line"><span class="badge">Voice</span><span>${escapeHtml(voice)}</span></div>`);
      }
      if (lines.length) {
        cornerStatus.classList.remove('hidden');
        cornerStatus.innerHTML = `<div class="title">Active Services</div>${lines.join('')}`;
      } else {
        cornerStatus.classList.add('hidden');
        cornerStatus.innerHTML = '';
      }
    }
  } catch (e) {
    if (statusList) {
      statusList.innerHTML = `<div class="status">Error loading status: ${escapeHtml(String(e))}</div>`;
    }
  }
}

if (refreshBtn) {
  refreshBtn.addEventListener('click', () => loadLlmKeyStatus());
}

async function loadJobs() {
  if (!jobsList || !jobsListCard) return;
  const user = localStorage.getItem('manim_user');
  if (!user) {
    jobsListCard.classList.add('hidden');
    return;
  }

  try {
    const res = await fetch(`${API_URL}/api/v1/jobs`, {
      headers: getAuthHeaders()
    });
    if (!res.ok) {
      if (res.status === 401) {
        // Token expired? Hide list.
        jobsListCard.classList.add('hidden');
        return;
      }
      throw new Error(`HTTP ${res.status}`);
    }
    const jobs = await res.json();
    jobsListCard.classList.remove('hidden');

    if (jobs.length === 0) {
      jobsList.innerHTML = '<div class="status-item">No recent jobs found.</div>';
      return;
    }

    jobsList.innerHTML = jobs.map(job => `
      <div class="status-item">
        <span class="badge ${job.status === 'done' ? 'pass' : (job.status === 'error' ? 'fail' : 'pending')}">${escapeHtml(job.status.toUpperCase())}</span>
        <code>${escapeHtml(job.job_id)}</code>
        <button type="button" class="btn" style="margin-left:auto; padding:4px 8px; font-size:12px;" onclick="window.pollJob('${escapeHtml(job.job_id)}')">View</button>
      </div>
    `).join('');
  } catch (e) {
    console.error('Failed to load jobs:', e);
  }
}

if (refreshJobsBtn) {
  refreshJobsBtn.addEventListener('click', () => loadJobs());
}
// loadLlmKeyStatus(); // uncomment to auto-load on page load

// ─── Poll Job ───
const MAX_POLL_RETRIES = 5;
const MAX_POLL_ITERATIONS = 3600; // ~90 minutes at 1.5s avg

async function pollJob(jobId, signal) {
  // Make pollJob globally accessible so the "View" button can call it
  window.pollJob = (id) => {
    if (currentAbortController) currentAbortController.abort();
    currentAbortController = new AbortController();
    pollJob(id, currentAbortController.signal);
  };

  setStatusHTML(`Job <code>${escapeHtml(jobId)}</code> running…`);
  setStatusHTML(`Job <code>${escapeHtml(jobId)}</code> running…`);
  videoSection.classList.add('hidden');
  showLoadingOverlay();

  const loadingStatus = document.getElementById('loading-status');
  let delay = 1500;
  let retries = 0;
  let iterations = 0;

  for (; ;) {
    iterations++;
    if (iterations > MAX_POLL_ITERATIONS) {
      hideLoadingOverlay();
      restoreCornerStatus();
      setStatusHTML(`Job <code>${escapeHtml(jobId)}</code> timed out — polling stopped after ${MAX_POLL_ITERATIONS} iterations.`);
      return;
    }

    // Check abort
    if (signal && signal.aborted) {
      hideLoadingOverlay();
      restoreCornerStatus();
      setStatus('Job cancelled.');
      return;
    }

    let res;
    try {
      res = await fetch(`${API_URL}/api/v1/jobs/${encodeURIComponent(jobId)}`, {
        headers: getAuthHeaders(),
        signal
      });
    } catch (err) {
      if (err.name === 'AbortError') {
        hideLoadingOverlay();
        restoreCornerStatus();
        setStatus('Job cancelled.');
        return;
      }
      retries++;
      if (retries > MAX_POLL_RETRIES) {
        hideLoadingOverlay();
        restoreCornerStatus();
        setStatus(`Network error — lost connection after ${MAX_POLL_RETRIES} retries.`);
        return;
      }
      setStatus(`Network error (retry ${retries}/${MAX_POLL_RETRIES})…`);
      await new Promise(r => setTimeout(r, delay));
      delay = Math.min(Math.floor(delay * 1.5), 8000);
      continue;
    }

    // Reset retry counter on success
    retries = 0;

    if (!res.ok) {
      hideLoadingOverlay();
      restoreCornerStatus();
      setStatus(`Error fetching status (HTTP ${res.status})`);
      return;
    }

    const data = await res.json();
    const logHtml = `<pre class="log">${escapeHtml(data.log || '')}</pre>`;

    // Update progress bar
    const progress = data.progress || 0;
    const progressBar = document.getElementById('progress-bar');
    const progressText = document.getElementById('progress-text');
    const progressPercent = document.getElementById('progress-percent');
    const progressRingCircle = document.querySelector('.progress-ring-circle');
    
    if (progressBar) progressBar.style.width = `${progress}%`;
    if (progressText) progressText.textContent = `${progress}%`;
    if (progressPercent) progressPercent.textContent = `${Math.round(progress)}`;
    
    // Update circular progress ring
    if (progressRingCircle) {
      const circumference = 2 * Math.PI * 54; // radius = 54
      const offset = circumference - (progress / 100) * circumference;
      progressRingCircle.style.strokeDashoffset = offset;
    }

    // Update loading status with latest log line
    if (loadingStatus) {
      const logLines = (data.log || '').split('\n').filter(l => l.trim());
      const lastLine = logLines[logLines.length - 1] || 'Processing...';
      loadingStatus.textContent = lastLine.substring(0, 60);
    }

    if (data.status === 'done') {
      hideLoadingOverlay();
      setStatusHTML(`Job <code>${escapeHtml(jobId)}</code> finished.` + logHtml);

      if (data.video_url) {
        currentVideoUrl = data.video_url;
        videoEl.src = data.video_url;
        videoSection.classList.remove('hidden');
        // Update download link href
        if (downloadVideoBtn) {
          downloadVideoBtn.href = data.video_url;
        }
        if (cornerStatus) cornerStatus.classList.add('hidden');
        try {
          localStorage.setItem('lastVideoUrl', data.video_url);
        } catch (e) { /* ignore localStorage errors */ }
      } else {
        // No video — restore corner status
        restoreCornerStatus();
      }

      if (data.plan_url) {
        // Use encodeURI for the href (preserves valid URL chars) and escapeHtml for display text
        const safeHref = encodeURI(data.plan_url);
        planLinkEl.innerHTML = `Plan: <a href="${safeHref}" target="_blank" rel="noopener">download</a>`;
      } else if (data.plan_path) {
        planLinkEl.innerHTML = `Plan: <code>${escapeHtml(data.plan_path)}</code>`;
      } else {
        planLinkEl.innerHTML = '';
      }

      const logLinkEl = document.getElementById('log-link');
      if (data.log_url) {
        logLinkEl.innerHTML = `Log: <a href="${escapeHtml(data.log_url)}" target="_blank" rel="noopener">download</a>`;
      } else {
        logLinkEl.innerHTML = '';
      }
      return;
    }

    if (data.status === 'error') {
      hideLoadingOverlay();
      restoreCornerStatus();
      setStatusHTML(`Job <code>${escapeHtml(jobId)}</code> failed.` + logHtml);
      return;
    }

    // Guard against unknown/unexpected status values
    const knownStatuses = ['queued', 'running', 'pending', 'processing'];
    if (!knownStatuses.includes(data.status)) {
      hideLoadingOverlay();
      restoreCornerStatus();
      setStatusHTML(`Job <code>${escapeHtml(jobId)}</code> returned unexpected status: <code>${escapeHtml(data.status)}</code>.` + logHtml);
      return;
    }

    setStatusHTML(`Job <code>${escapeHtml(jobId)}</code> ${escapeHtml(data.status)}…` + logHtml);
    await new Promise(r => setTimeout(r, delay));
    delay = Math.min(Math.floor(delay * 1.3), 5000);
  }
}

// ─── Form Submit ───
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const problem = document.getElementById('problem').value.trim();
  // These options are always enabled (hardcoded)
  const orchestrate = true;
  const voiceFirst = true;
  const elementAudio = true;
  const longVideo = true;
  const customPrompt = document.getElementById('custom-prompt').value.trim();
  const selectedModeInput = document.querySelector('input[name="learning-mode"]:checked');
  const learningMode = selectedModeInput ? selectedModeInput.value : 'question_solving';

  const modeGuidance = {
    question_solving:
      'MODE: QUESTION_SOLVING. Focus on solving the exact question step-by-step with clear derivation, substitutions, unit checks, and final answer verification.',
    lecture:
      'MODE: LECTURE. Teach concept-first as a classroom lecture with intuition, definitions, derivations, examples, and smooth explanatory flow.',
    revision:
      'MODE: REVISION. Create a concise high-yield revision format with key formulas, quick methods, common mistakes, and rapid recap checkpoints.'
  };
  const modePrompt = modeGuidance[learningMode] || modeGuidance.question_solving;
  const mergedPrompt = [modePrompt, customPrompt].filter(Boolean).join('\n\n');

  if (!problem) {
    setStatus('Please enter a problem or plan path.');
    return;
  }

  // Cancel any previous polling
  if (currentAbortController) {
    currentAbortController.abort();
  }
  currentAbortController = new AbortController();
  const signal = currentAbortController.signal;

  setStatus('Submitting job…');
  showLoadingOverlay();
  if (cornerStatus) cornerStatus.classList.add('hidden');
  videoSection.classList.add('hidden');

  try {
    const res = await fetch(`${API_URL}/api/v1/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders()
      },
      body: JSON.stringify({
        problem,
        mode: learningMode,
        orchestrate,
        voice_first: voiceFirst,
        element_audio: elementAudio,
        long_video: longVideo,
        custom_prompt: mergedPrompt || null
      }),
      signal,
    });
    if (!res.ok) {
      if (res.status === 401) {
        localStorage.removeItem('manim_user');
        setStatus('Session expired. Please log in again.');
        hideLoadingOverlay();
        restoreCornerStatus();
        const overlay = document.getElementById('login-overlay');
        if (overlay) { overlay.style.display = 'flex'; overlay.classList.remove('hidden'); }
        return;
      }
      setStatus(`Request failed (HTTP ${res.status})`);
      hideLoadingOverlay();
      restoreCornerStatus();
      return;
    }
    const data = await res.json();
    const jobId = data.job_id;
    await pollJob(jobId, signal);
    loadJobs(); // Refresh list after job finishes
  } catch (err) {
    if (err.name === 'AbortError') {
      setStatus('Job cancelled.');
    } else {
      console.error(err);
      setStatus('Request failed — see console for details.');
    }
    hideLoadingOverlay();
    restoreCornerStatus();
  } finally {
    currentAbortController = null;
  }
});

// ─── Cancel loading button ───
const cancelLoadingBtn = document.getElementById('cancel-loading');
if (cancelLoadingBtn) {
  cancelLoadingBtn.addEventListener('click', () => {
    if (currentAbortController) {
      currentAbortController.abort();
    }
    hideLoadingOverlay();
    restoreCornerStatus();
    setStatus('Generation cancelled by user.');
  });
}

// Escape key also dismisses loading overlay
document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') {
    const la = document.getElementById('loading-animation');
    if (la && !la.classList.contains('hidden')) {
      if (currentAbortController) currentAbortController.abort();
      hideLoadingOverlay();
      restoreCornerStatus();
      setStatus('Generation cancelled by user.');
    }
  }
});

// ─── Authentication Logic ───
document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('login-overlay');
  if (!overlay) return;

  function checkAuth() {
    const user = localStorage.getItem('manim_user');
    if (user) {
      try {
        const userData = JSON.parse(user);
        const token = userData.token || userData.access_token;
        if (!token) {
          // Stale guest session without a real token — force re-login
          localStorage.removeItem('manim_user');
          if (cornerStatus) cornerStatus.classList.add('hidden');
          overlay.style.display = 'flex';
          overlay.classList.remove('hidden');
          return;
        }
        if (!userData.token) {
          userData.token = token;
          localStorage.setItem('manim_user', JSON.stringify(userData));
        }
        overlay.style.display = 'none';
        overlay.classList.add('hidden');
        updateUserDisplay(userData);
        loadJobs();
      } catch (e) {
        console.error('Auth Error: Invalid user data', e);
        localStorage.removeItem('manim_user');
        if (cornerStatus) cornerStatus.classList.add('hidden');
        overlay.style.display = 'flex';
        overlay.classList.remove('hidden');
      }
    } else {
      if (cornerStatus) cornerStatus.classList.add('hidden');
      overlay.style.display = 'flex';
      overlay.classList.remove('hidden');
    }
  }

  function login(userData) {
    console.log('Logging in as:', userData);
    if (userData && !userData.token && userData.access_token) {
      userData.token = userData.access_token;
    }
    localStorage.setItem('manim_user', JSON.stringify(userData));
    checkAuth();
    loadJobs();
  }

  // ─── Inline auth message helper ───
  const authMessageEl = document.getElementById('auth-message');
  function showAuthMessage(text, type) {
    if (!authMessageEl) return;
    authMessageEl.textContent = text;
    authMessageEl.className = 'auth-message ' + (type || '');
  }
  function clearAuthMessage() {
    if (authMessageEl) { authMessageEl.textContent = ''; authMessageEl.className = 'auth-message'; }
  }

  async function handleRealLogin(email, password) {
    clearAuthMessage();
    try {
      const res = await fetch('/api/v1/auth/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        showAuthMessage(error.detail || 'Email or password is incorrect.', 'error');
        return;
      }
      const data = await res.json();
      showAuthMessage('Login successful!', 'success');
      // Delay to show success message before hiding overlay
      setTimeout(() => {
        login({ type: 'email', email: email, name: email, token: data.access_token });
      }, 1000);
    } catch (e) {
      showAuthMessage('Login error: ' + String(e), 'error');
    }
  }

  async function handleRealSignup(email, password) {
    clearAuthMessage();
    try {
      const res = await fetch('/api/v1/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      if (!res.ok) {
        const error = await res.json().catch(() => ({}));
        showAuthMessage(error.detail || 'Signup failed.', 'error');
        return;
      }
      showAuthMessage('Signup successful!', 'success');
      // Delay to show success message before auto-login
      setTimeout(async () => {
        await handleRealLogin(email, password);
      }, 1000);
    } catch (e) {
      showAuthMessage('Signup error: ' + String(e), 'error');
    }
  }

  function logout() {
    localStorage.removeItem('manim_user');
    // Reset state without full page reload
    if (cornerStatus) {
      cornerStatus.innerHTML = '';
      cornerStatus.classList.add('hidden');
    }
    overlay.style.display = 'flex';
    overlay.classList.remove('hidden');
  }

  function updateUserDisplay(user) {
    const el = document.getElementById('cornerStatus');
    if (el) {
      el.classList.remove('hidden');
      const name = user.name || user.email || 'Guest';
      const userLine = `<div class="line" style="margin-top:4px;border-top:1px solid #333;padding-top:4px"><span class="badge" style="background:#3b82f6;color:white">User</span> <span>${escapeHtml(name)}</span> <a href="#" id="logout-link" style="font-size:10px;color:#94a3b8;margin-left:auto">Sign Out</a></div>`;
      if (!el.innerHTML.includes('User</span>')) {
        el.innerHTML += userLine;
        // Use event delegation on cornerStatus to avoid race conditions
        el.addEventListener('click', (e) => {
          if (e.target && e.target.id === 'logout-link') {
            e.preventDefault();
            logout();
          }
        });
      }
    }
  }

  // ─── Overlay login/signup form handlers ───
  // New login/signup forms from jp.js
  const loginForm = document.getElementById("loginForm");
  const signupForm = document.getElementById("signupForm");
  const forgotForm = document.getElementById("forgotForm");

  // Show form function for toggling between forms
  window.showForm = function(formId) {
    document.querySelectorAll(".form").forEach(form => {
      form.classList.remove("active");
    });
    document.getElementById(formId).classList.add("active");
    clearAuthMessage();
  };

  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById("loginEmail").value;
      const password = document.getElementById("loginPassword").value;
      
      // Use existing handleRealLogin function
      await handleRealLogin(email, password);
    });
  }

  if (signupForm) {
    signupForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const email = document.getElementById("signupEmail").value;
      const password = document.getElementById("signupPassword").value;
      const confirm = document.getElementById("signupConfirm").value;
      
      // Validation
      if (password !== confirm) {
        showAuthMessage('Passwords do not match.', 'error');
        return;
      }
      
      if (password.length < 6) {
        showAuthMessage('Password must be at least 6 characters.', 'error');
        return;
      }
      
      // Use existing handleRealSignup function
      await handleRealSignup(email, password);
    });
  }

  if (forgotForm) {
    forgotForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById("forgotEmail").value;
      // In a real app, this would send a reset link
      if (email) {
        showAuthMessage('If this email exists, a reset link will be sent.', 'success');
      }
    });
  }

  // Social / skip button handlers
  const skipBtn = document.getElementById('skip-login');
  const btnGoogleCircle = document.getElementById('btn-google-circle');
  const btnFacebookCircle = document.getElementById('btn-facebook-circle');
  const btnGoogleSignup = document.getElementById('btn-google-signup');
  const btnFacebookSignup = document.getElementById('btn-facebook-signup');

  async function requestGuestToken() {
    const res = await fetch(`${API_URL}/api/v1/auth/guest`, { method: 'POST' });
    if (!res.ok) {
      let detail = '';
      try {
        const err = await res.json();
        detail = err && err.detail ? `: ${String(err.detail)}` : '';
      } catch (e) {
        // ignore parsing failures
      }
      throw new Error(`HTTP ${res.status}${detail}`);
    }
    return await res.json();
  }

  async function handleSocialLogin(providerName) {
    clearAuthMessage();
    try {
      const data = await requestGuestToken();
      showAuthMessage(`${providerName} login successful!`, 'success');
      setTimeout(() => {
        login({
          type: providerName.toLowerCase(),
          name: `${providerName} User`,
          token: data.access_token
        });
      }, 800);
    } catch (err) {
      showAuthMessage(`${providerName} login failed: ${String(err)}`, 'error');
    }
  }

  if (skipBtn) {
    skipBtn.addEventListener('click', async (e) => {
      e.preventDefault();
      clearAuthMessage();
      skipBtn.disabled = true;
      try {
        const data = await requestGuestToken();
        showAuthMessage('Guest login successful!', 'success');
        // Delay to show success message before hiding overlay
        setTimeout(() => {
          login({ type: 'guest', name: 'Guest User', token: data.access_token });
        }, 1000);
      } catch (err) {
        showAuthMessage('Guest login failed: ' + String(err), 'error');
      } finally {
        skipBtn.disabled = false;
      }
    });
  }

  if (btnGoogleCircle) {
    btnGoogleCircle.addEventListener('click', () => {
      handleSocialLogin('Google');
    });
  }

  if (btnFacebookCircle) {
    btnFacebookCircle.addEventListener('click', () => {
      handleSocialLogin('Facebook');
    });
  }

  if (btnGoogleSignup) {
    btnGoogleSignup.addEventListener('click', () => {
      handleSocialLogin('Google');
    });
  }

  if (btnFacebookSignup) {
    btnFacebookSignup.addEventListener('click', () => {
      handleSocialLogin('Facebook');
    });
  }

  // Initial auth check
  checkAuth();

  // ─── Video controls ───
  if (closeVideoBtn) {
    closeVideoBtn.addEventListener('click', () => {
      videoSection.classList.add('hidden');
      restoreCornerStatus();
    });
  }

  // Download button: update the anchor href to the actual video
  if (downloadVideoBtn) {
    downloadVideoBtn.addEventListener('click', (e) => {
      if (currentVideoUrl) {
        downloadVideoBtn.href = currentVideoUrl;
        // Allow the default <a download> behaviour to proceed
      } else {
        e.preventDefault();
        alert('No video available to download.');
      }
    });
  }

  // Share button: share the video URL, not the page URL
  if (shareVideoBtn) {
    shareVideoBtn.addEventListener('click', () => {
      const shareUrl = currentVideoUrl || window.location.href;
      if (navigator.share) {
        navigator.share({
          title: 'Phiversity - Generated Video',
          text: 'Check out this physics animation created by Phiversity!',
          url: shareUrl,
        }).catch(err => console.log('Share failed:', err));
      } else {
        navigator.clipboard.writeText(shareUrl).then(() => {
          alert('Video URL copied to clipboard!');
        }).catch(() => {
          alert('Video URL: ' + shareUrl);
        });
      }
    });
  }
});

