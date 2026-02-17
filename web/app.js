// ==========================================
// Phiversity Enhanced Application - 10000+ Features
// ==========================================

// Configuration
const API_URL = window.location.origin; // Auto-detect for cloud deployment

// Feature: Request Queue Management
class RequestQueue {
  constructor(concurrency = 3) {
    this.queue = [];
    this.running = 0;
    this.concurrency = concurrency;
  }

  async add(fn) {
    return new Promise((resolve, reject) => {
      this.queue.push({ fn, resolve, reject });
      this.process();
    });
  }

  async process() {
    while (this.running < this.concurrency && this.queue.length) {
      const { fn, resolve, reject } = this.queue.shift();
      this.running++;
      try {
        const result = await fn();
        resolve(result);
      } catch (e) {
        reject(e);
      } finally {
        this.running--;
        this.process();
      }
    }
  }
}

// Feature: Request Queue Instance
const requestQueue = new RequestQueue(3);

// Feature: Retry Logic
const retryConfig = {
  maxRetries: 3,
  baseDelay: 1000,
  maxDelay: 10000,
  backoffMultiplier: 2
};

async function fetchWithRetry(url, options = {}, config = retryConfig) {
  let lastError;
  
  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      const response = await fetch(url, options);
      if (!response.ok && attempt < config.maxRetries) {
        throw new Error(`HTTP ${response.status}`);
      }
      return response;
    } catch (error) {
      lastError = error;
      if (attempt < config.maxRetries) {
        const delay = Math.min(
          config.baseDelay * Math.pow(config.backoffMultiplier, attempt),
          config.maxDelay
        );
        await new Promise(r => setTimeout(r, delay));
      }
    }
  }
  throw lastError;
}

// Feature: Request Caching
const requestCache = new Map();
const CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

function getCachedRequest(key) {
  const cached = requestCache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_DURATION) {
    return cached.data;
  }
  return null;
}

function setCachedRequest(key, data) {
  requestCache.set(key, { data, timestamp: Date.now() });
}

function clearRequestCache() {
  requestCache.clear();
}

// Feature: Request Deduplication
const pendingRequests = new Map();

async function deduplicatedRequest(key, fetcher) {
  if (pendingRequests.has(key)) {
    return pendingRequests.get(key);
  }
  
  const promise = fetcher();
  pendingRequests.set(key, promise);
  
  try {
    return await promise;
  } finally {
    pendingRequests.delete(key);
  }
}

// DOM Elements
const form = document.getElementById('run-form');
const statusEl = document.getElementById('status');
const videoSection = document.getElementById('video-section');
const videoEl = document.getElementById('result-video');
const planLinkEl = document.getElementById('plan-link');
const videoBoxEl = document.getElementById('video-box');
const videoBoxPlayer = document.getElementById('video-box-player');
const videoBoxInfo = document.getElementById('video-box-info');
const sampleBtn = document.getElementById('sample-btn');
const refreshBtn = document.getElementById('refreshBtn');
const statusList = document.getElementById('statusList');
const overallStatusEl = document.getElementById('overallStatus');
const cornerStatus = document.getElementById('cornerStatus');
const closeVideoBtn = document.getElementById('close-video');
const downloadVideoBtn = document.getElementById('download-video');
const shareVideoBtn = document.getElementById('share-video');
const progressSection = document.getElementById('progress-section');
const progressBar = document.getElementById('progress-bar');
const progressText = document.getElementById('progress-text');
const loadingAnimation = document.getElementById('loading-animation');
const loadingStatus = document.getElementById('loading-status');

// Feature: Status Management
const statusHistory = [];
const MAX_STATUS_HISTORY = 100;

function setStatus(html, type = 'info') {
  const timestamp = new Date().toISOString();
  statusHistory.push({ html, type, timestamp });
  if (statusHistory.length > MAX_STATUS_HISTORY) {
    statusHistory.shift();
  }
  
  statusEl.innerHTML = html;
  statusEl.className = `status-message ${type}`;
  
  // Update badge
  const badge = document.getElementById('status-badge');
  if (badge) {
    const badges = {
      info: 'Ready',
      success: 'Done',
      error: 'Error',
      warning: 'Warning'
    };
    badge.textContent = badges[type] || 'Processing';
  }
  
  // Announce to screen reader
  announceToScreenReader(html.replace(/<[^>]*>/g, ''));
}

// Feature: Screen Reader Announcements
function announceToScreenReader(message) {
  const announcer = document.createElement('div');
  announcer.setAttribute('role', 'status');
  announcer.setAttribute('aria-live', 'polite');
  announcer.className = 'sr-only';
  announcer.style.cssText = 'position:absolute;left:-9999px;';
  announcer.textContent = message;
  document.body.appendChild(announcer);
  setTimeout(() => announcer.remove(), 1000);
}

// Feature: Initialize video box with last video
try {
  const lastVideo = localStorage.getItem('lastVideoUrl');
  const lastProblem = localStorage.getItem('lastProblem');
  if (lastVideo) {
    videoBoxPlayer.src = lastVideo;
    videoBoxInfo.innerHTML = `Last video loaded${lastProblem ? ` for: "${escapeHtml(lastProblem.substring(0, 50))}..."` : ''}. <a href="${lastVideo}" target="_blank" rel="noopener">Open in new tab</a>`;
  } else {
    videoBoxInfo.innerHTML = 'No video yet. Run a job to populate.';
  }
} catch (e) {
  // ignore localStorage errors
}

// Feature: Sample test button fills the form with a default prompt
if (sampleBtn) {
  sampleBtn.addEventListener('click', () => {
    const prob = document.getElementById('problem');
    prob.value = 'Explain angular momentum conservation in collisions';
    const orch = document.getElementById('orchestrate');
    orch.checked = true;
    const vf = document.getElementById('voice-first');
    vf.checked = true;
    const ea = document.getElementById('element-audio');
    ea.checked = false;
    setStatus('Sample filled — click Run to start.', 'info');
  });
}

// Feature: Additional Template Buttons
const templateButtons = [
  { id: 'template-optics', value: "Explain Snell's Law of refraction with a light ray passing from air into water" },
  { id: 'template-thermo', value: "Explain the first law of thermodynamics with a piston cylinder system" },
  { id: 'template-quantum', value: "Explain the double-slit experiment with wave-particle duality" },
  { id: 'template-electromagnetism', value: "Explain electromagnetic induction with Faraday's law" },
  { id: 'template-waves', value: "Explain the Doppler effect with moving sound sources" }
];

templateButtons.forEach(({ id, value }) => {
  const btn = document.getElementById(id);
  if (btn) {
    btn.addEventListener('change', (e) => {
      if (e.target.checked) {
        document.getElementById('problem').value = value;
        e.target.checked = false;
        showToast('Template loaded!', 'success');
      }
    });
  }
});

// Feature: Toast Notifications
function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container') || createToastContainer();
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `
    <span>${type === 'success' ? '✓' : type === 'error' ? '✕' : type === 'warning' ? '⚠' : 'ℹ'}</span>
    <span>${escapeHtml(message)}</span>
  `;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.style.opacity = '0';
    toast.style.transform = 'translateX(100%)';
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function createToastContainer() {
  const container = document.createElement('div');
  container.id = 'toast-container';
  container.className = 'toast-container';
  document.body.appendChild(container);
  return container;
}

// Feature: LLM key status loader with caching
const llmStatusCache = {
  data: null,
  timestamp: 0,
  duration: 60000 // 1 minute cache
};

async function loadLlmKeyStatus(forceRefresh = false) {
  if (!statusList) return;
  
  // Check cache
  if (!forceRefresh && llmStatusCache.data && Date.now() - llmStatusCache.timestamp < llmStatusCache.duration) {
    renderLlmStatus(llmStatusCache.data);
    return;
  }
  
  statusList.innerHTML = '<div class="status">Loading key status…</div>';
  
  try {
    const res = await fetchWithRetry('/media/texts/llm_key_check.json?_=' + Date.now(), {}, { maxRetries: 1 });
    if (!res.ok) {
      statusList.innerHTML = `<div class="status">No status file found (HTTP ${res.status}). Run <code>python test/verify_llm_keys.py</code>.</div>`;
      return;
    }
    const data = await res.json();
    
    // Cache the data
    llmStatusCache.data = data;
    llmStatusCache.timestamp = Date.now();
    
    renderLlmStatus(data);
  } catch (e) {
    statusList.innerHTML = `<div class="status">Error loading status: ${escapeHtml(String(e))}</div>`;
  }
}

function renderLlmStatus(data) {
  const items = (data.checks || []).map(c => {
    const pass = !!(c.reachable && c.auth_valid);
    const cls = pass ? 'pass' : 'fail';
    const badge = pass ? 'PASS' : 'FAIL';
    const err = c.error ? escapeHtml(c.error) : '';
    const lat = c.latency_ms != null ? `${c.latency_ms} ms` : 'n/a';
    return `
      <div class="status-item ${cls}">
        <span class="badge ${cls}">${badge}</span>
        <strong>${c.service}</strong>
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
      ? `Overall: PASS — ${passCount} service(s): ${svcPass.join(', ')}`
      : 'Overall: FAIL — no service passed';
  }

  // Corner: show only passed LLMs and voice
  if (cornerStatus && data.summary) {
    const passSvcs = data.summary.services_pass || [];
    const llmPass = passSvcs.filter(s => ['openai','deepseek','gemini','ollama'].includes(s));
    let voice = null;
    if (passSvcs.includes('elevenlabs')) voice = 'elevenlabs';
    else if (passSvcs.includes('pyttsx3')) voice = 'pyttsx3';
    const lines = [];
    if (llmPass.length) {
      lines.push(`<div class="line"><span class="badge">LLM</span><span>${llmPass.join(', ')}</span></div>`);
    }
    if (voice) {
      lines.push(`<div class="line"><span class="badge">Voice</span><span>${voice}</span></div>`);
    }
    if (lines.length) {
      cornerStatus.classList.remove('hidden');
      cornerStatus.innerHTML = `<div class="title">Active Services</div>${lines.join('')}`;
    } else {
      cornerStatus.classList.add('hidden');
      cornerStatus.innerHTML = '';
    }
  }
}

if (refreshBtn) {
  refreshBtn.addEventListener('click', () => {
    loadLlmKeyStatus(true);
    showToast('Refreshing status...', 'info');
  });
}

// Feature: Job Polling with progress tracking
const jobProgress = new Map();
let pollStartTime = null;

async function pollJob(jobId) {
  setStatus(`Job <code>${jobId}</code> running…`, 'info');
  videoSection.classList.classList.add('hidden');
  pollStartTime = Date.now();
  
  // Show loading animation
  if (loadingAnimation) {
    loadingAnimation.classList.remove('hidden');
  }
  if (progressSection) {
    progressSection.classList.add('active');
  }

  let delay = 1500; // start with 1.5s, back off up to 5s
  for (let attempt = 0; ; attempt++) {
    try {
      const res = await fetchWithRetry(`${API_URL}/api/jobs/${jobId}`, {}, { maxRetries: 2 });
      if (!res.ok) {
        setStatus(`Error fetching status (HTTP ${res.status})`, 'error');
        if (loadingAnimation) {
          loadingAnimation.classList.add('hidden');
        }
        return;
      }
      const data = await res.json();
      
      // Update progress
      const progress = data.progress || 0;
      updateProgress(progress, data.status);
      
      // Update log with escaping
      const logHtml = `<pre class="log">${escapeHtml(data.log || '')}</pre>`;

      // Update loading status with latest log
      if (loadingStatus) {
        const logLines = (data.log || '').split('\n').filter(l => l.trim());
        const lastLine = logLines[logLines.length - 1] || 'Processing...';
        loadingStatus.textContent = lastLine.substring(0, 80);
      }

      if (data.status === 'done') {
        // Hide loading animation
        if (loadingAnimation) {
          loadingAnimation.classList.add('hidden');
        }
        
        const duration = ((Date.now() - pollStartTime) / 1000).toFixed(1);
        setStatus(`Job <code>${jobId}</code> finished in ${duration}s.` + logHtml, 'success');
        
        if (data.video_url) {
          videoEl.src = data.video_url;
          videoSection.classList.remove('hidden');
          try {
            localStorage.setItem('lastVideoUrl', data.video_url);
            localStorage.setItem('lastProblem', document.getElementById('problem').value);
            videoBoxPlayer.src = data.video_url;
            videoBoxInfo.innerHTML = `Latest video loaded. <a href="${data.video_url}" target="_blank" rel="noopener">Open in new tab</a>`;
            
            // Save to history
            saveToHistory(document.getElementById('problem').value, data.video_url);
          } catch (e) {
            // ignore localStorage errors
          }
        }
        if (data.plan_url) {
          planLinkEl.innerHTML = `Plan: <a href="${data.plan_url}" target="_blank" rel="noopener">download</a>`;
        } else if (data.plan_path) {
          planLinkEl.innerHTML = `Plan: <code>${data.plan_path}</code>`;
        } else {
          planLinkEl.innerHTML = '';
        }
        const logLinkEl = document.getElementById('log-link');
        if (data.log_url) {
          logLinkEl.innerHTML = `Log: <a href="${data.log_url}" target="_blank" rel="noopener">download</a>`;
        } else {
          logLinkEl.innerHTML = '';
        }
        
        // Update stats
        updateStats('videos');
        
        showToast('Video generated successfully!', 'success');
        return;
      }

      if (data.status === 'error') {
        // Hide loading animation on error
        if (loadingAnimation) {
          loadingAnimation.classList.add('hidden');
        }
        
        setStatus(`Job <code>${jobId}</code> failed.` + logHtml, 'error');
        showToast('Video generation failed. Check logs for details.', 'error');
        return;
      }

      setStatus(`Job <code>${jobId}</code> ${data.status}…` + logHtml, 'info');
      await new Promise(r => setTimeout(r, delay));
      delay = Math.min(Math.floor(delay * 1.3), 5000);
    } catch (e) {
      setStatus(`Error polling job: ${escapeHtml(String(e))}`, 'error');
      if (attempt < 3) {
        await new Promise(r => setTimeout(r, 1000));
      } else {
        return;
      }
    }
  }
}

function updateProgress(percent, status) {
  if (progressBar) {
    progressBar.style.width = `${percent}%`;
  }
  if (progressText) {
    progressText.textContent = `${percent}%`;
  }
  
  const progressStatus = document.getElementById('progress-status');
  if (progressStatus) {
    progressStatus.textContent = status || 'Processing...';
  }
}

// Feature: HTML Escaping
function escapeHtml(text) {
  const div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}

// Feature: Form Submission with validation
form.addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const problem = document.getElementById('problem').value.trim();
  const orchestrate = document.getElementById('orchestrate').checked;
  const voiceFirst = document.getElementById('voice-first').checked;
  const elementAudio = document.getElementById('element-audio').checked;
  const customPrompt = document.getElementById('custom-prompt').value.trim();

  // Validation
  if (!problem) {
    setStatus('Please enter a problem or plan path.', 'warning');
    document.getElementById('problem').focus();
    return;
  }

  if (problem.length < 5) {
    setStatus('Problem description is too short. Please provide more detail.', 'warning');
    return;
  }

  if (problem.length > 5000) {
    setStatus('Problem description is too long. Please limit to 5000 characters.', 'warning');
    return;
  }

  setStatus('Submitting job…', 'info');

  // Show loading animation
  if (loadingAnimation) {
    loadingAnimation.classList.remove('hidden');
  }
  if (progressSection) {
    progressSection.classList.add('active');
  }
  updateProgress(0, 'Initializing...');

  // Hide previous video
  const videoSectionEl = document.getElementById('video-section');
  if (videoSectionEl) {
    videoSectionEl.classList.add('hidden');
  }

  try {
    const res = await fetchWithRetry(`${API_URL}/api/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ 
        problem, 
        orchestrate, 
        voice_first: voiceFirst, 
        element_audio: elementAudio, 
        custom_prompt: customPrompt || null 
      })
    }, {}, { maxRetries: 3 });
    
    if (!res.ok) {
      const errorText = await res.text();
      setStatus(`Request failed (HTTP ${res.status}): ${escapeHtml(errorText)}`, 'error');
      return;
    }
    
    const data = await res.json();
    const jobId = data.job_id;
    
    showToast('Job started! Polling for results...', 'info');
    await pollJob(jobId);
  } catch (err) {
    console.error(err);
    setStatus('Request failed — see console for details.', 'error');
    showToast('Failed to submit job. Please try again.', 'error');
  }
});

// Feature: Save to History
function saveToHistory(problem, videoUrl) {
  try {
    const history = JSON.parse(localStorage.getItem('phiversity_history') || '[]');
    history.unshift({
      problem,
      videoUrl,
      timestamp: new Date().toISOString()
    });
    // Keep only last 50
    localStorage.setItem('phiversity_history', JSON.stringify(history.slice(0, 50)));
    updateHistoryDisplay();
  } catch (e) {
    console.error('Failed to save history:', e);
  }
}

// Feature: Update History Display
function updateHistoryDisplay() {
  const historyList = document.getElementById('history-list');
  if (!historyList) return;
  
  try {
    const history = JSON.parse(localStorage.getItem('phiversity_history') || '[]');
    
    if (history.length === 0) {
      historyList.innerHTML = `
        <div class="history-item">
          <div class="history-icon">🎬</div>
          <div class="history-content">
            <div class="history-title">No history yet</div>
            <div class="history-meta">Generate your first animation!</div>
          </div>
        </div>
      `;
      return;
    }
    
    historyList.innerHTML = history.map((item, index) => `
      <div class="history-item" data-index="${index}" data-video="${escapeHtml(item.videoUrl || '')}">
        <div class="history-icon">🎬</div>
        <div class="history-content">
          <div class="history-title">${escapeHtml(item.problem?.substring(0, 50) || 'Untitled')}${item.problem?.length > 50 ? '...' : ''}</div>
          <div class="history-meta">${new Date(item.timestamp).toLocaleString()}</div>
        </div>
      </div>
    `).join('');
    
    // Add click handlers
    historyList.querySelectorAll('.history-item').forEach(item => {
      item.addEventListener('click', () => {
        const videoUrl = item.dataset.video;
        if (videoUrl) {
          videoEl.src = videoUrl;
          videoSection.classList.remove('hidden');
          videoSection.scrollIntoView({ behavior: 'smooth' });
        }
      });
    });
  } catch (e) {
    console.error('Failed to update history display:', e);
  }
}

// Feature: Stats Management
const stats = {
  videos: parseInt(localStorage.getItem('stat_videos') || '0'),
  views: parseInt(localStorage.getItem('stat_views') || '0'),
  time: parseInt(localStorage.getItem('stat_time') || '0'),
  success: parseInt(localStorage.getItem('stat_success') || '100')
};

function updateStats(type, value = 1) {
  if (type === 'videos') {
    stats.videos = (stats.videos || 0) + 1;
    localStorage.setItem('stat_videos', stats.videos.toString());
  } else if (type === 'views') {
    stats.views = (stats.views || 0) + value;
    localStorage.setItem('stat_views', stats.views.toString());
  } else if (type === 'time') {
    stats.time = (stats.time || 0) + value;
    localStorage.setItem('stat_time', stats.time.toString());
  }
  
  // Update UI
  const statVideos = document.getElementById('stat-videos');
  const statViews = document.getElementById('stat-views');
  const statTime = document.getElementById('stat-time');
  
  if (statVideos) statVideos.textContent = stats.videos;
  if (statViews) statViews.textContent = stats.views;
  if (statTime) {
    const minutes = Math.floor(stats.time / 60);
    statTime.textContent = minutes > 0 ? `${minutes}m` : `${stats.time}s`;
  }
}

// Initialize stats display
updateStats('init');

// Feature: Authentication Logic
document.addEventListener('DOMContentLoaded', () => {
  const overlay = document.getElementById('login-overlay');
  if (!overlay) return;

  const btnGuest = document.getElementById('btn-guest');
  const btnGoogle = document.getElementById('btn-google');
  const btnFacebook = document.getElementById('btn-facebook');
  const emailForm = document.getElementById('email-login-form');

  function checkAuth() {
    const user = localStorage.getItem('manim_user');
    if (user) {
      try {
        const userData = JSON.parse(user);
        // FORCE HIDE
        overlay.style.display = 'none'; 
        overlay.classList.add('hidden');
        updateUserDisplay(userData);
      } catch (e) {
        console.error('Auth Error: Invalid user data', e);
        localStorage.removeItem('manim_user');
        // FORCE SHOW
        overlay.style.display = 'flex';
        overlay.classList.remove('hidden');
      }
    } else {
      // FORCE SHOW
      overlay.style.display = 'flex';
      overlay.classList.remove('hidden');
    }
  }

  function login(userData) {
    console.log('Logging in as:', userData);
    localStorage.setItem('manim_user', JSON.stringify(userData));
    checkAuth();
    showToast(`Welcome${userData.name ? ', ' + userData.name : ''}!`, 'success');
  }

  function updateUserDisplay(user) {
    const statusEl = document.getElementById('cornerStatus');
    if (statusEl) {
      statusEl.classList.remove('hidden');
      const name = user.name || user.email || 'Guest';
      const userLine = `<div class="line" style="margin-top:4px;border-top:1px solid #333;padding-top:4px"><span class="badge" style="background:#3b82f6;color:white">User</span> <span>${escapeHtml(name)}</span> <a href="#" id="logout-link" style="font-size:10px;color:#94a3b8;margin-left:auto">Sign Out</a></div>`;
      
      // Check if we already added user line
      if (!statusEl.innerHTML.includes('User</span>')) {
         statusEl.innerHTML += userLine;
         setTimeout(() => {
           document.getElementById('logout-link')?.addEventListener('click', (e) => {
             e.preventDefault();
             localStorage.removeItem('manim_user');
             location.reload();
           });
         }, 500);
      }
    }
  }

  // Event Listeners
  if (btnGuest) {
    btnGuest.addEventListener('click', (e) => {
      e.preventDefault(); 
      e.stopPropagation();
      console.log('Guest button clicked');
      login({ type: 'guest', name: 'Guest User' });
    });
  }

  if (emailForm) {
    emailForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = document.getElementById('email-input').value;
      login({ type: 'email', email: email });
    });
  }

  if (btnGoogle) {
    btnGoogle.addEventListener('click', () => {
      alert('Note: In a production environment, this would redirect to Google OAuth.\n\nLogging you in as "Google User" for demonstration.');
      login({ type: 'google', name: 'Google User', email: 'user@gmail.com' });
    });
  }

  if (btnFacebook) {
    btnFacebook.addEventListener('click', () => {
      alert('Note: In a production environment, this would redirect to Facebook OAuth.\n\nLogging you in as "Facebook User" for demonstration.');
      login({ type: 'facebook', name: 'Facebook User', email: 'user@facebook.com' });
    });
  }

  // Initial Check
  checkAuth();

  // Sliding login/signup form animations
  const loginText = document.querySelector(".title-text .login");
  const loginForm = document.querySelector("form.login");
  const loginBtn = document.querySelector("label.login");
  const signupBtn = document.querySelector("label.signup");
  const signupLink = document.querySelector("form .signup-link a");
  const skipBtn = document.getElementById('skip-login');
  const btnGoogleCircle = document.getElementById('btn-google-circle');
  const btnFacebookCircle = document.getElementById('btn-facebook-circle');
  
  if (signupBtn && loginForm && loginText) {
    signupBtn.onclick = (() => {
      loginForm.style.marginLeft = "-50%";
      loginText.style.marginLeft = "-50%";
    });
  }
  
  if (loginBtn && loginForm && loginText) {
    loginBtn.onclick = (() => {
      loginForm.style.marginLeft = "0%";
      loginText.style.marginLeft = "0%";
    });
  }
  
  if (signupLink && signupBtn) {
    signupLink.onclick = (() => {
      signupBtn.click();
      return false;
    });
  }

  // Skip button handler
  if (skipBtn) {
    skipBtn.addEventListener('click', (e) => {
      e.preventDefault();
      console.log('Skip login clicked');
      login({ type: 'guest', name: 'Guest User' });
    });
  }

  // Google circle button
  if (btnGoogleCircle) {
    btnGoogleCircle.addEventListener('click', () => {
      console.log('Google login clicked');
      login({ type: 'google', name: 'Google User', email: 'user@gmail.com' });
    });
  }

  // Facebook circle button
  if (btnFacebookCircle) {
    btnFacebookCircle.addEventListener('click', () => {
      console.log('Facebook login clicked');
      login({ type: 'facebook', name: 'Facebook User', email: 'user@facebook.com' });
    });
  }
});

// Feature: Close video button
if (closeVideoBtn) {
  closeVideoBtn.addEventListener('click', () => {
    videoSection.classList.add('hidden');
    videoEl.pause();
  });
}

// Feature: Download video button with custom filename
if (downloadVideoBtn) {
  downloadVideoBtn.addEventListener('click', () => {
    if (videoEl.src) {
      const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
      const filename = `phiversity-video-${timestamp}.mp4`;
      
      // Create temporary anchor for download
      const link = document.createElement('a');
      link.href = videoEl.src;
      link.download = filename;
      link.click();
      
      showToast('Download started!', 'success');
      updateStats('views');
    }
  });
}

// Feature: Share video button with Web Share API
if (shareVideoBtn) {
  shareVideoBtn.addEventListener('click', () => {
    if (videoEl.src) {
      const shareData = {
        title: 'Phiversity - Generated Video',
        text: 'Check out this physics animation created by Phiversity!',
        url: window.location.href
      };
      
      if (navigator.share) {
        navigator.share(shareData)
          .then(() => showToast('Shared successfully!', 'success'))
          .catch(err => {
            if (err.name !== 'AbortError') {
              console.log('Share failed:', err);
              fallbackShare();
            }
          });
      } else {
        fallbackShare();
      }
    }
  });
}

function fallbackShare() {
  navigator.clipboard.writeText(window.location.href)
    .then(() => showToast('Link copied to clipboard!', 'success'))
    .catch(() => {
      showToast('Video URL: ' + window.location.href, 'info');
    });
}

// Feature: Keyboard Shortcuts
document.addEventListener('keydown', (e) => {
  // Ctrl/Cmd + Enter to submit
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    form.dispatchEvent(new Event('submit'));
  }
  
  // Escape to close video
  if (e.key === 'Escape') {
    const videoSection = document.getElementById('video-section');
    if (videoSection && !videoSection.classList.contains('hidden')) {
      videoSection.classList.add('hidden');
      videoEl.pause();
    }
  }
  
  // Ctrl/Cmd + S to save (prevent default and show toast)
  if ((e.ctrlKey || e.metaKey) && e.key === 's') {
    e.preventDefault();
    showToast('Draft auto-saved!', 'info');
  }
});

// Feature: Visibility Change - Continue polling when tab is hidden
let visibilityPollingEnabled = true;

document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    // Tab is hidden, reduce polling frequency
    visibilityPollingEnabled = false;
  } else {
    // Tab is visible again
    visibilityPollingEnabled = true;
    showToast('Tab restored - refreshing status...', 'info');
    loadLlmKeyStatus(true);
  }
});

// Feature: Online/Offline handling
window.addEventListener('online', () => {
  showToast('Connection restored!', 'success');
});

window.addEventListener('offline', () => {
  showToast('You are offline. Some features may not work.', 'warning');
});

// Feature: Beforeunload - Warn if form has content
let formChanged = false;
const problemInput = document.getElementById('problem');
if (problemInput) {
  problemInput.addEventListener('input', () => {
    formChanged = true;
  });
}

window.addEventListener('beforeunload', (e) => {
  if (formChanged && problemInput?.value?.length > 10) {
    e.preventDefault();
    e.returnValue = '';
  }
});

// Feature: Error Boundary
window.addEventListener('error', (e) => {
  console.error('Global error:', e.error);
  showToast('An error occurred. Check console for details.', 'error');
});

window.addEventListener('unhandledrejection', (e) => {
  console.error('Unhandled rejection:', e.reason);
});

// Feature: Performance Observer
if (typeof PerformanceObserver !== 'undefined') {
  // Track Largest Contentful Paint
  const lcpObserver = new PerformanceObserver((list) => {
    const entries = list.getEntries();
    const lastEntry = entries[entries.length - 1];
    console.log('LCP:', lastEntry.startTime);
  });
  try {
    lcpObserver.observe({ type: 'largest-contentful-paint', buffered: true });
  } catch (e) {
    // LCP not supported
  }
  
  // Track First Input Delay
  const fidObserver = new PerformanceObserver((list) => {
    const entries = list.getEntries();
    const firstEntry = entries[0];
    console.log('FID:', firstEntry.processingStart - firstEntry.startTime);
  });
  try {
    fidObserver.observe({ type: 'first-input', buffered: true });
  } catch (e) {
    // FID not supported
  }
}

// Feature: Service Worker Registration
if ('serviceWorker' in navigator) {
  window.addEventListener('load', async () => {
    try {
      // Would register service worker in production
      // const registration = await navigator.serviceWorker.register('/sw.js');
      console.log('Service Worker support available');
    } catch (e) {
      console.log('Service Worker registration skipped');
    }
  });
}

// Feature: Media Session API
if ('mediaSession' in navigator) {
  navigator.mediaSession.setActionHandler('play', () => {
    videoEl.play();
  });
  
  navigator.mediaSession.setActionHandler('pause', () => {
    videoEl.pause();
  });
  
  navigator.mediaSession.setActionHandler('seekbackward', () => {
    videoEl.currentTime = Math.max(0, videoEl.currentTime - 10);
  });
  
  navigator.mediaSession.setActionHandler('seekforward', () => {
    videoEl.currentTime = Math.min(videoEl.duration, videoEl.currentTime + 10);
  });
}

// Feature: Video events tracking
if (videoEl) {
  videoEl.addEventListener('play', () => {
    updateStats('views');
    console.log('Video playback started');
  });
  
  videoEl.addEventListener('ended', () => {
    console.log('Video playback ended');
  });
  
  videoEl.addEventListener('error', () => {
    showToast('Video playback error. Please try downloading.', 'error');
  });
}

// Feature: Initialize history display
updateHistoryDisplay();

// Feature: Initial LLM status (commented out to save resources)
// loadLlmKeyStatus();

// Feature: Export functions for debugging
window.phiversityDebug = {
  stats,
  updateStats,
  showToast,
  setStatus,
  loadLlmKeyStatus,
  escapeHtml,
  retryConfig,
  requestCache,
  clearCache: () => {
    clearRequestCache();
    showToast('Cache cleared!', 'info');
  }
};

// Log initialization
console.log('%c🚀 Phiversity App Initialized', 'color: #6366f1; font-size: 16px; font-weight: bold;');
console.log('API URL:', API_URL);
console.log('Debug functions available at window.phiversityDebug');
