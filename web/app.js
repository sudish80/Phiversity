// Configuration
const API_URL = window.location.origin; // Auto-detect for cloud deployment
// For local development, you can override:
// const API_URL = 'http://localhost:8000';

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

function setStatus(html) {
  statusEl.innerHTML = html;
}

// Initialize video box with last video (if any)
/*
try {
  const lastVideo = localStorage.getItem('lastVideoUrl');
  if (lastVideo) {
    videoBoxPlayer.src = lastVideo;
    videoBoxInfo.innerHTML = `Last video loaded. <a href="${lastVideo}" target="_blank" rel="noopener">Open in new tab</a>`;
  } else {
    videoBoxInfo.innerHTML = 'No video yet. Run a job to populate.';
  }
} catch (e) {
  // ignore localStorage errors
}
*/

// Sample test button fills the form with a default prompt
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
    setStatus('Sample filled — click Run to start.');
  });
}

// LLM key status loader
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
      // voice: prefer elevenlabs if pass; else pyttsx3 if pass
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
    // Removed legacy summary line
  } catch (e) {
    statusList.innerHTML = `<div class="status">Error loading status: ${escapeHtml(String(e))}</div>`;
  }
}

if (refreshBtn) {
  // refreshBtn.addEventListener('click', () => loadLlmKeyStatus());
}
// Initial load
// loadLlmKeyStatus();

async function pollJob(jobId) {
  setStatus(`Job <code>${jobId}</code> running…`);
  videoSection.classList.add('hidden');
  
  // Show loading animation
  const loadingAnimation = document.getElementById('loading-animation');
  const loadingStatus = document.getElementById('loading-status');
  if (loadingAnimation) {
    loadingAnimation.classList.remove('hidden');
  }

  let delay = 1500; // start with 1.5s, back off up to 5s
  for (;;) {
    const res = await fetch(`${API_URL}/api/jobs/${jobId}`);
    if (!res.ok) {
      setStatus(`Error fetching status (HTTP ${res.status})`);
      if (loadingAnimation) {
        loadingAnimation.classList.add('hidden');
      }
      return;
    }
    const data = await res.json();
    const logHtml = `<pre class="log">${escapeHtml(data.log || '')}</pre>`;

    // Update loading status with latest log
    if (loadingStatus) {
      const logLines = (data.log || '').split('\n').filter(l => l.trim());
      const lastLine = logLines[logLines.length - 1] || 'Processing...';
      loadingStatus.textContent = lastLine.substring(0, 60);
    }

    if (data.status === 'done') {
      // Hide loading animation
      if (loadingAnimation) {
        loadingAnimation.classList.add('hidden');
      }
      
      setStatus(`Job <code>${jobId}</code> finished.` + logHtml);
      if (data.video_url) {
        videoEl.src = data.video_url;
        videoSection.classList.remove('hidden');
        try {
          localStorage.setItem('lastVideoUrl', data.video_url);
          videoBoxPlayer.src = data.video_url;
          videoBoxInfo.innerHTML = `Latest video loaded. <a href="${data.video_url}" target="_blank" rel="noopener">Open in new tab</a>`;
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
      return;
    }

    if (data.status === 'error') {
      // Hide loading animation on error
      const loadingAnimation = document.getElementById('loading-animation');
      if (loadingAnimation) {
        loadingAnimation.classList.add('hidden');
      }
      
      setStatus(`Job <code>${jobId}</code> failed.` + logHtml);
      return;
    }

    setStatus(`Job <code>${jobId}</code> ${data.status}…` + logHtml);
    await new Promise(r => setTimeout(r, delay));
    delay = Math.min(Math.floor(delay * 1.3), 5000);
  }
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.innerText = text;
  return div.innerHTML;
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  const problem = document.getElementById('problem').value.trim();
  const orchestrate = document.getElementById('orchestrate').checked;
  const voiceFirst = document.getElementById('voice-first').checked;
  const elementAudio = document.getElementById('element-audio').checked;
  const customPrompt = document.getElementById('custom-prompt').value.trim();

  if (!problem) {
    setStatus('Please enter a problem or plan path.');
    return;
  }

  setStatus('Submitting job…');

  // Show loading animation
  const loadingAnimation = document.getElementById('loading-animation');
  if (loadingAnimation) {
    loadingAnimation.classList.remove('hidden');
  }
  const videoSection = document.getElementById('video-section');
  if (videoSection) {
    videoSection.classList.add('hidden');
  }

  try {
    const res = await fetch(`${API_URL}/api/run`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ problem, orchestrate, voice_first: voiceFirst, element_audio: elementAudio, custom_prompt: customPrompt || null }),
    });
    if (!res.ok) {
      setStatus(`Request failed (HTTP ${res.status})`);
      return;
    }
    const data = await res.json();
    const jobId = data.job_id;
    await pollJob(jobId);
  } catch (err) {
    console.error(err);
    setStatus('Request failed — see console for details.');
  }
});

/* Authentication Logic */
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
  }

  function updateUserDisplay(user) {
    const statusEl = document.getElementById('cornerStatus');
    if (statusEl) {
      statusEl.classList.remove('hidden');
      const name = user.name || user.email || 'Guest';
      // Append user info to corner status
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
      // Simulate Google Auth
      alert('Note: In a production environment, this would redirect to Google OAuth.\n\nLogging you in as "Google User" for demonstration.');
      login({ type: 'google', name: 'Google User', email: 'user@gmail.com' });
    });
  }

  if (btnFacebook) {
    btnFacebook.addEventListener('click', () => {
      // Simulate Facebook Auth
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

  // Close video box button
  if (closeVideoBtn) {
    closeVideoBtn.addEventListener('click', () => {
      videoSection.classList.add('hidden');
    });
  }

  // Download video button
  if (downloadVideoBtn) {
    downloadVideoBtn.addEventListener('click', () => {
      if (videoEl.src) {
        const link = document.createElement('a');
        link.href = videoEl.src;
        link.download = 'phiversity-video.mp4';
        link.click();
      }
    });
  }

  // Share video button
  if (shareVideoBtn) {
    shareVideoBtn.addEventListener('click', () => {
      if (navigator.share && videoEl.src) {
        navigator.share({
          title: 'Phiversity - Generated Video',
          text: 'Check out this physics animation created by Phiversity!',
          url: window.location.href
        }).catch(err => console.log('Share failed:', err));
      } else {
        // Fallback: copy URL to clipboard
        navigator.clipboard.writeText(window.location.href).then(() => {
          alert('Video URL copied to clipboard!');
        }).catch(() => {
          alert('Video URL: ' + window.location.href);
        });
      }
    });
  }
});

