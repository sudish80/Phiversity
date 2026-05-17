/* ── Phiversity UI Layer ── Overlays, toast, theme, keyboard, animations ── */
const PhiversityUI = (() => {
  const { $, $$, el, escapeHtml, getState, patchState } = Phiversity;

  // =====================================================
  // TOAST
  // =====================================================
  function toast(msg, type = 'info', duration = 4000) {
    let c = $('#toast-container');
    if (!c) {
      c = el('div', { id: 'toast-container' });
      document.body.appendChild(c);
    }
    const icons = { info: 'ℹ️', success: '✅', error: '❌', warning: '⚠️' };
    const t = el('div', { class: `toast ${type}` },
      `${icons[type] || ''} ${escapeHtml(msg)}`
    );
    c.appendChild(t);
    requestAnimationFrame(() => t.classList.add('show'));
    if (duration > 0) {
      setTimeout(() => {
        t.classList.remove('show');
        setTimeout(() => t.remove(), 400);
      }, duration);
    }
  }

  // =====================================================
  // OVERLAYS
  // =====================================================
  function openOverlay(id) {
    const el = document.getElementById(id + '-overlay');
    if (!el) return;
    el.classList.remove('overlay-hidden');
    el.classList.add('overlay-visible');
    document.body.classList.add('overlay-open');
    Phiversity._emit('overlay:open', id);
  }

  function closeOverlay(id) {
    const el = document.getElementById(id + '-overlay');
    if (!el) return;
    el.classList.remove('overlay-visible');
    el.classList.add('overlay-hidden');
    if (!document.querySelector('.overlay-visible')) {
      document.body.classList.remove('overlay-open');
    }
    Phiversity._emit('overlay:close', id);
  }

  // =====================================================
  // POPULATE SETTINGS
  // =====================================================
  function populateSettings() {
    const container = $('#speed-btns');
    if (!container || container.children.length > 0) return;
    const speeds = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0];
    const current = getState('settings').playbackSpeed || 1.0;
    speeds.forEach(s => {
      const btn = el('button', {
        class: s === current ? 'active' : '',
        onclick() {
          patchState({ settings: { ...getState('settings'), playbackSpeed: s } });
          const video = $('#result-video');
          if (video) video.playbackRate = s;
          $$('button', container).forEach(b => b.classList.remove('active'));
          btn.classList.add('active');
          toast(`Speed: ${s}x`, 'info');
        }
      }, `${s}x`);
      container.appendChild(btn);
    });
    const autoplayInput = $('#setting-autoplay');
    if (autoplayInput) {
      autoplayInput.checked = getState('settings').autoPlay;
      autoplayInput.addEventListener('change', () => {
        patchState({ settings: { ...getState('settings'), autoPlay: autoplayInput.checked } });
      });
    }
    const user = getState('user');
    const userInfo = $('#setting-user');
    const logoutBtn = $('#btn-logout');
    const loginBtn = $('#btn-show-login');
    if (userInfo && logoutBtn && loginBtn) {
      const type = user?.type || 'guest';
      userInfo.textContent = type === 'guest' ? 'Signed in as Guest' : `Signed in as ${user?.email || 'user'}`;
      if (type !== 'guest') {
        logoutBtn.style.display = '';
        loginBtn.style.display = 'none';
        logoutBtn.onclick = async () => {
          await PhiversityAPI.logout();
          closeOverlay('settings');
          toast('Logged out', 'info');
          location.reload();
        };
      } else {
        logoutBtn.style.display = 'none';
        loginBtn.style.display = '';
        loginBtn.onclick = () => { closeOverlay('settings'); openOverlay('login'); };
      }
    }
  }

  // =====================================================
  // POPULATE HISTORY
  // =====================================================
  function populateHistory() {
    const list = $('#history-list');
    if (!list) return;
    list.innerHTML = '<div class="history-empty">Loading…</div>';
    PhiversityAPI.listJobs().then(jobs => {
      if (!Array.isArray(jobs)) jobs = [];
      if (jobs.length === 0) {
        list.innerHTML = '<div class="history-empty">No jobs yet</div>';
        return;
      }
      list.innerHTML = jobs.slice(0, 20).map((j, idx) => {
        const status = j.status || 'unknown';
        return `<div class="history-item" style="--stagger:${idx * 0.04}s" onclick="Phiversity._emit('loadJob','${j.job_id || j.id}')">
          <div class="history-item-top">
            <span class="history-item-id">${(j.job_id || j.id || '').slice(0, 12)}…</span>
            <span class="history-item-status ${status}">${status}</span>
          </div>
          <div class="history-item-problem">${escapeHtml(j.problem || j.question || '')}</div>
        </div>`;
      }).join('');
    }).catch(() => {
      list.innerHTML = '<div class="history-empty">Failed to load</div>';
    });
  }

  // =====================================================
  // INTERACTIVE PARTICLE CANVAS
  // =====================================================
  function initParticles() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let W, H;
    function resize() { W = canvas.width = window.innerWidth; H = canvas.height = window.innerHeight; }
    resize();
    window.addEventListener('resize', resize);

    const count = Math.min(80, Math.floor(W * 0.06));
    const particles = [];
    const mouse = { x: W / 2, y: H / 2, active: false };

    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * W,
        y: Math.random() * H,
        vx: (Math.random() - 0.5) * 0.4,
        vy: (Math.random() - 0.5) * 0.4,
        r: Math.random() * 2 + 1,
        phase: Math.random() * Math.PI * 2,
        baseVx: (Math.random() - 0.5) * 0.4,
        baseVy: (Math.random() - 0.5) * 0.4,
      });
    }

    document.addEventListener('mousemove', (e) => {
      mouse.x = e.clientX;
      mouse.y = e.clientY;
      mouse.active = true;
    });
    document.addEventListener('mouseleave', () => { mouse.active = false; });

    function draw() {
      ctx.clearRect(0, 0, W, H);

      for (const p of particles) {
        p.x += p.baseVx;
        p.y += p.baseVy;

        if (mouse.active) {
          const dx = mouse.x - p.x;
          const dy = mouse.y - p.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 200) {
            const force = (200 - dist) / 200 * 0.3;
            p.x -= dx / dist * force;
            p.y -= dy / dist * force;
          }
        }

        if (p.x < -10) p.x = W + 10; if (p.x > W + 10) p.x = -10;
        if (p.y < -10) p.y = H + 10; if (p.y > H + 10) p.y = -10;

        const alpha = 0.3 + Math.sin(p.phase + Date.now() * 0.001) * 0.15;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(16, 163, 127, ${alpha})`;
        ctx.fill();
      }

      for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
          const dx = particles[i].x - particles[j].x;
          const dy = particles[i].y - particles[j].y;
          const dist = dx * dx + dy * dy;
          if (dist < 12000) {
            const alpha = (1 - dist / 12000) * 0.15;
            ctx.beginPath();
            ctx.moveTo(particles[i].x, particles[i].y);
            ctx.lineTo(particles[j].x, particles[j].y);
            ctx.strokeStyle = `rgba(16, 163, 127, ${alpha})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }

      requestAnimationFrame(draw);
    }
    draw();
  }

  // =====================================================
  // RIPPLE EFFECT ON BUTTONS
  // =====================================================
  function initRipples() {
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('.btn, .btn-icon, .nav-btn, .btn-social, .opt-toggle, .theme-toggle');
      if (!btn) return;
      const rect = btn.getBoundingClientRect();
      const size = Math.max(rect.width, rect.height);
      const x = e.clientX - rect.left - size / 2;
      const y = e.clientY - rect.top - size / 2;
      const ripple = el('span', {
        class: 'ripple',
        style: `width:${size}px;height:${size}px;left:${x}px;top:${y}px;`
      });
      btn.appendChild(ripple);
      setTimeout(() => ripple.remove(), 600);
    });
  }

  // =====================================================
  // TYPING EFFECT ON HERO SUBTITLE
  // =====================================================
  function initTyping() {
    const el = $('#hero-subtitle');
    if (!el) return;
    const fullText = el.textContent || el.innerText;
    el.textContent = '';
    el.style.display = 'block';
    let i = 0;
    function type() {
      if (i < fullText.length) {
        el.textContent += fullText.charAt(i);
        i++;
        setTimeout(type, 25 + Math.random() * 20);
      } else {
        el.classList.add('typing-done');
      }
    }
    setTimeout(type, 400);
  }

  // =====================================================
  // ANIMATED STAT COUNTERS
  // =====================================================
  function animateCounters() {
    $$('.stat-value[data-target]').forEach(el => {
      const target = parseInt(el.dataset.target, 10);
      const suffix = el.dataset.suffix || '';
      if (isNaN(target)) return;
      const duration = 1500;
      const start = performance.now();
      function step(now) {
        const pct = Math.min((now - start) / duration, 1);
        const eased = 1 - (1 - pct) * (1 - pct);
        el.textContent = Math.floor(eased * target) + suffix;
        if (pct < 1) requestAnimationFrame(step);
        else el.textContent = target + suffix;
      }
      requestAnimationFrame(step);
    });
  }

  // =====================================================
  // CONFETTI BURST
  // =====================================================
  function confetti(count = 30) {
    const colors = ['#10a37f', '#34d399', '#22c55e', '#3b82f6', '#f59e0b', '#ef4444', '#8b5cf6'];
    for (let i = 0; i < count; i++) {
      const piece = el('div', {
        class: 'confetti-piece',
        style: `
          left: ${Math.random() * 100}vw;
          top: -10px;
          background: ${colors[Math.floor(Math.random() * colors.length)]};
          width: ${Math.random() * 6 + 4}px;
          height: ${Math.random() * 6 + 4}px;
          border-radius: ${Math.random() > 0.5 ? '50%' : '2px'};
          animation-duration: ${Math.random() * 2 + 2}s;
          animation-delay: ${Math.random() * 0.5}s;
        `
      });
      document.body.appendChild(piece);
      setTimeout(() => piece.remove(), 4000);
    }
  }

  // =====================================================
  // 3D CARD TILT ON MOUSE MOVE
  // =====================================================
  function initTilt() {
    const selector = '.mode-card, .job-card, .stat-card, .history-item, .glass-card';
    document.addEventListener('mousemove', (e) => {
      const cards = document.querySelectorAll(selector);
      for (const card of cards) {
        const rect = card.getBoundingClientRect();
        if (e.clientX < rect.left || e.clientX > rect.right || e.clientY < rect.top || e.clientY > rect.bottom) {
          if (card.dataset.tiltReset !== 'done') {
            card.style.transform = '';
            card.dataset.tiltReset = 'done';
          }
          continue;
        }
        card.dataset.tiltReset = '';
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dx = (e.clientX - cx) / rect.width;
        const dy = (e.clientY - cy) / rect.height;
        const tiltX = dy * -6;
        const tiltY = dx * 6;
        card.style.transform = `perspective(600px) rotateX(${tiltX}deg) rotateY(${tiltY}deg) translateY(-2px)`;
        card.style.transition = 'transform 0.1s ease';
      }
    });
    document.addEventListener('mouseleave', () => {
      $$(selector).forEach(card => {
        card.style.transform = '';
      });
    });
  }

  // =====================================================
  // OBSERVER FOR SCROLL REVEAL
  // =====================================================
  function initReveal() {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.1, rootMargin: '20px' });
    $$('.reveal-section').forEach(el => observer.observe(el));
  }

  // =====================================================
  // SHORTCUTS GRID
  // =====================================================
  let shortcutsBuilt = false;
  function buildShortcuts() {
    if (shortcutsBuilt) return;
    const grid = $('.shortcuts-grid');
    if (!grid || grid.children.length > 0) return;
    const items = [
      ['H', 'History sidebar'],
      ['S', 'Settings'],
      ['?', 'Shortcuts help'],
      ['T', 'Toggle theme'],
      ['Esc', 'Close current overlay'],
      ['Enter', 'Submit form / Generate'],
    ];
    items.forEach(([key, desc]) => {
      const existing = grid.querySelector(`.shortcut-row:has(kbd)`);
      if (!existing) {
        const row = el('div', { class: 'shortcut-row' },
          el('span', {}, desc),
          el('kbd', {}, key),
        );
        grid.appendChild(row);
      }
    });
    shortcutsBuilt = true;
  }

  // =====================================================
  // INIT
  // =====================================================
  function init() {
    initParticles();
    initRipples();
    initTyping();
    initTilt();
    initReveal();
    animateCounters();
    buildShortcuts();

    ['login', 'loading', 'video', 'settings', 'history', 'shortcuts'].forEach(id => {
      Phiversity.registerLayer(id, {
        onOpen: () => {
          if (id === 'settings') populateSettings();
          if (id === 'history') populateHistory();
          openOverlay(id);
        },
        onClose: () => closeOverlay(id),
      });
    });

    document.querySelectorAll('[class$="-overlay"]').forEach(el => {
      el.addEventListener('click', function (e) {
        if (e.target === this) {
          const id = this.id.replace('-overlay', '');
          if (id !== 'loading') Phiversity.closeLayer(id);
        }
      });
    });

    document.querySelectorAll('.close-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const overlay = e.target.closest('[class$="-overlay"]');
        if (overlay) {
          const id = overlay.id.replace('-overlay', '');
          Phiversity.closeLayer(id);
        }
      });
    });

    Phiversity.on('overlay:close', () => {
      setTimeout(() => {
        $$('.reveal-section:not(.is-visible)').forEach(el => {
          const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
              if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
              }
            });
          }, { threshold: 0.1 });
          observer.observe(el);
        });
      }, 100);
    });
  }

  return {
    init, toast,
    openOverlay, closeOverlay,
    populateSettings, populateHistory,
    confetti, animateCounters,
  };
})();

document.addEventListener('DOMContentLoaded', () => PhiversityUI.init());
