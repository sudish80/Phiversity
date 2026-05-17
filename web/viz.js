/* ════════════════════════════════════════════════════════════
   PhiversityViz — Organic ambient, physics scenes, growth chart
   ════════════════════════════════════════════════════════════ */

// roundRect polyfill for older browsers
if (!CanvasRenderingContext2D.prototype.roundRect) {
  CanvasRenderingContext2D.prototype.roundRect = function (x, y, w, h, r) {
    if (r > w / 2) r = w / 2;
    if (r > h / 2) r = h / 2;
    this.moveTo(x + r, y);
    this.arcTo(x + w, y, x + w, y + h, r);
    this.arcTo(x + w, y + h, x, y + h, r);
    this.arcTo(x, y + h, x, y, r);
    this.arcTo(x, y, x + w, y, r);
    return this;
  };
}

const PhiversityViz = (() => {
  const { $, $$, el } = Phiversity;

  // ─── Perlin noise helpers ───
  const _grad = new Float32Array(512);
  (() => {
    const p = new Uint8Array(256);
    for (let i = 0; i < 256; i++) p[i] = i;
    for (let i = 255; i > 0; i--) {
      const j = (Math.random() * (i + 1)) | 0;
      const t = p[i]; p[i] = p[j]; p[j] = t;
    }
    for (let i = 0; i < 512; i++) _grad[i] = p[i & 255];
  })();
  function _fade(t) { return t * t * t * (t * (t * 6 - 15) + 10); }
  function _lerp(a, b, t) { return a + t * (b - a); }
  function _gradDot(h, x, y) { const hh = h & 3; const u = hh < 2 ? x : y; const v = hh < 2 ? y : x; return ((hh & 1) === 0 ? u : -u) + ((hh & 2) === 0 ? v : -v); }
  function noise2D(x, y) {
    const X = Math.floor(x) & 255, Y = Math.floor(y) & 255;
    const xf = x - Math.floor(x), yf = y - Math.floor(y);
    const u = _fade(xf), v = _fade(yf);
    return _lerp(_lerp(_gradDot(_grad[_grad[X] + Y], xf, yf), _gradDot(_grad[_grad[X + 1] + Y], xf - 1, yf), u), _lerp(_gradDot(_grad[_grad[X] + Y + 1], xf, yf - 1), _gradDot(_grad[_grad[X + 1] + Y + 1], xf - 1, yf - 1), u), v);
  }

  // ─── Easing ───
  function easeInOut(t) { return t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2; }
  function lerp(a, b, t) { return a + (b - a) * t; }

  // ══════════════════════════════════════════════════════════
  // SECTION 1: PROBLEM ANALYZER
  // ══════════════════════════════════════════════════════════
  const SCENE_TYPES = {
    CAR_FRICTION: 'car_friction',
    INCLINE: 'incline',
    PROJECTILE: 'projectile',
    PENDULUM: 'pendulum',
    DEFAULT: 'default',
  };

  function analyzeProblem(text) {
    const t = (text || '').toLowerCase();
    if (/\b(car|tire|tyre|road|friction|braking|skid|wheel|vehicle|automobile)\b/.test(t)) {
      return SCENE_TYPES.CAR_FRICTION;
    }
    if (/\b(incline|ramp|slope|angle of repose)\b/.test(t)) {
      return SCENE_TYPES.INCLINE;
    }
    if (/\b(projectile|launch|ball thrown|cannon)\b/.test(t)) {
      return SCENE_TYPES.PROJECTILE;
    }
    if (/\b(pendulum|oscillat|swing|simple harmonic)\b/.test(t)) {
      return SCENE_TYPES.PENDULUM;
    }
    return SCENE_TYPES.DEFAULT;
  }

  // ══════════════════════════════════════════════════════════
  // SECTION 2: PHYSICS SCENE RENDERER
  // ══════════════════════════════════════════════════════════
  class PhysicsScene {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.W = 0; this.H = 0;
      this.zoom = 1;
      this.targetZoom = 1;
      this.panX = 0; this.panY = 0;
      this.targetPanX = 0; this.targetPanY = 0;
      this.time = 0;
      this.sceneType = SCENE_TYPES.DEFAULT;
      this.props = {};
      this._animId = null;
      this._resize();
      window.addEventListener('resize', () => this._resize());
    }

    _resize() {
      this.W = this.canvas.width = window.innerWidth;
      this.H = this.canvas.height = window.innerHeight;
    }

    setScene(type, props = {}) {
      this.sceneType = type;
      this.props = props;
      this.time = 0;
    }

    zoomTo(x, y, z) {
      this.targetPanX = this.W / 2 - x * z;
      this.targetPanY = this.H / 2 - y * z;
      this.targetZoom = z;
    }

    resetView() {
      this.targetZoom = 1;
      this.targetPanX = 0;
      this.targetPanY = 0;
    }

    start() {
      if (this._animId) return;
      this._draw();
    }

    stop() {
      if (this._animId) { cancelAnimationFrame(this._animId); this._animId = null; }
    }

    _draw = () => {
      this._animId = requestAnimationFrame(this._draw);
      this.time += 0.016;

      // Smooth zoom/pan transitions
      this.zoom = lerp(this.zoom, this.targetZoom, 0.06);
      this.panX = lerp(this.panX, this.targetPanX, 0.06);
      this.panY = lerp(this.panY, this.targetPanY, 0.06);

      const ctx = this.ctx;
      const W = this.W, H = this.H;
      ctx.clearRect(0, 0, W, H);

      ctx.save();
      ctx.translate(this.panX, this.panY);
      ctx.scale(this.zoom, this.zoom);

      switch (this.sceneType) {
        case SCENE_TYPES.CAR_FRICTION: this._drawCarFriction(ctx); break;
        case SCENE_TYPES.INCLINE: this._drawIncline(ctx); break;
        case SCENE_TYPES.PROJECTILE: this._drawProjectile(ctx); break;
        case SCENE_TYPES.PENDULUM: this._drawPendulum(ctx); break;
        default: this._drawAmbient(ctx); break;
      }

      ctx.restore();
    };

    // ─── Draw helpers ───
    _arrow(ctx, x1, y1, x2, y2, color, label) {
      const angle = Math.atan2(y2 - y1, x2 - x1);
      const len = 12 / this.zoom;
      ctx.save();
      ctx.strokeStyle = color;
      ctx.fillStyle = color;
      ctx.lineWidth = 2.5 / this.zoom;
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      ctx.lineTo(x2, y2);
      ctx.stroke();
      ctx.beginPath();
      ctx.moveTo(x2, y2);
      ctx.lineTo(x2 - len * Math.cos(angle - 0.4), y2 - len * Math.sin(angle - 0.4));
      ctx.lineTo(x2 - len * Math.cos(angle + 0.4), y2 - len * Math.sin(angle + 0.4));
      ctx.closePath();
      ctx.fill();
      if (label) {
        ctx.fillStyle = color;
        ctx.font = `${Math.max(11, 14 / this.zoom)}px Inter, sans-serif`;
        ctx.textAlign = 'center';
        ctx.fillText(label, (x1 + x2) / 2, y1 - 10 / this.zoom);
      }
      ctx.restore();
    }

    _label(ctx, x, y, text, color = '#fff', size = 13) {
      ctx.save();
      ctx.fillStyle = color;
      ctx.font = `${size / this.zoom}px Inter, sans-serif`;
      ctx.textAlign = 'center';
      ctx.fillText(text, x, y);
      ctx.restore();
    }

    // ─── Scene: Car + Tire Friction ───
    _drawCarFriction(ctx) {
      const W = this.W / this.zoom;
      const H = this.H / this.zoom;
      const c = { x: W * 0.3, y: H * 0.55 }; // car center
      const t = this.time;
      const roadY = c.y + 60 / this.zoom;
      const wheelR = 28 / this.zoom;
      const wheelX1 = c.x - 50 / this.zoom;
      const wheelX2 = c.x + 50 / this.zoom;

      // Road
      ctx.fillStyle = '#333';
      ctx.fillRect(0, roadY, W, H - roadY);
      // Road markings
      ctx.strokeStyle = '#ffcc00';
      ctx.lineWidth = 3 / this.zoom;
      ctx.setLineDash([20 / this.zoom, 15 / this.zoom]);
      ctx.beginPath();
      ctx.moveTo(0, roadY + 15 / this.zoom);
      ctx.lineTo(W, roadY + 15 / this.zoom);
      ctx.stroke();
      ctx.setLineDash([]);

      // Car body
      const bodyY = c.y - 30 / this.zoom;
      ctx.fillStyle = '#2563eb';
      ctx.beginPath();
      ctx.roundRect(c.x - 80 / this.zoom, bodyY, 160 / this.zoom, 50 / this.zoom, 6 / this.zoom);
      ctx.fill();
      // Cabin
      ctx.fillStyle = '#1d4ed8';
      ctx.beginPath();
      ctx.roundRect(c.x - 35 / this.zoom, bodyY - 25 / this.zoom, 70 / this.zoom, 30 / this.zoom, 4 / this.zoom);
      ctx.fill();
      // Window
      ctx.fillStyle = 'rgba(255,255,255,0.2)';
      ctx.beginPath();
      ctx.roundRect(c.x - 28 / this.zoom, bodyY - 20 / this.zoom, 56 / this.zoom, 18 / this.zoom, 3 / this.zoom);
      ctx.fill();

      // Wheels
      const spinAngle = t * 3;
      for (const wx of [wheelX1, wheelX2]) {
        const wy = roadY - 2 / this.zoom;
        // Tire
        ctx.fillStyle = '#111';
        ctx.beginPath();
        ctx.arc(wx, wy, wheelR, 0, Math.PI * 2);
        ctx.fill();
        // Rim
        ctx.fillStyle = '#555';
        ctx.beginPath();
        ctx.arc(wx, wy, wheelR * 0.5, 0, Math.PI * 2);
        ctx.fill();
        // Spokes
        ctx.strokeStyle = '#888';
        ctx.lineWidth = 2 / this.zoom;
        for (let s = 0; s < 5; s++) {
          const a = spinAngle + (s * Math.PI * 2) / 5;
          ctx.beginPath();
          ctx.moveTo(wx, wy);
          ctx.lineTo(wx + Math.cos(a) * wheelR * 0.45, wy + Math.sin(a) * wheelR * 0.45);
          ctx.stroke();
        }
        // Tire tread marks
        ctx.strokeStyle = 'rgba(255,255,255,0.15)';
        ctx.lineWidth = 1.5 / this.zoom;
        for (let t = 0; t < 8; t++) {
          const a = spinAngle + (t * Math.PI * 2) / 8;
          ctx.beginPath();
          ctx.arc(wx, wy, wheelR * 0.85, a - 0.15, a + 0.15);
          ctx.stroke();
        }
      }

      // Force arrows (zoomed in on tire-road contact)
      // Normal force (upward) at right wheel
      const contactX = wheelX2;
      const contactY = roadY;
      this._arrow(ctx, contactX, contactY - 40 / this.zoom, contactX, contactY,
        '#22c55e', 'N (Normal)');
      // Friction force (leftward) at contact point
      this._arrow(ctx, contactX + 50 / this.zoom, contactY, contactX, contactY,
        '#ef4444', 'f (Friction)');
      // Weight downward at center
      this._arrow(ctx, c.x, roadY - 70 / this.zoom, c.x, roadY - 20 / this.zoom,
        '#f59e0b', 'mg (Weight)');
      // Motion direction
      this._arrow(ctx, c.x + 30 / this.zoom, roadY + 40 / this.zoom,
        c.x + 90 / this.zoom, roadY + 40 / this.zoom, '#3b82f6', 'v');

      // Zoom indicator box around tire-road contact
      ctx.strokeStyle = 'rgba(16, 163, 127, 0.4)';
      ctx.lineWidth = 1.5 / this.zoom;
      ctx.setLineDash([6 / this.zoom, 4 / this.zoom]);
      const zs = 80 / this.zoom;
      ctx.strokeRect(contactX - zs / 2, contactY - zs / 2, zs, zs);
      ctx.setLineDash([]);
      this._label(ctx, contactX, contactY - zs / 2 - 8 / this.zoom, '🔍 Zoom area', 'rgba(16,163,127,0.6)');

      // Title
      this._label(ctx, W / 2, 30 / this.zoom, '🛞 Tire-Road Friction Analysis', '#10a37f', 16);
    }

    // ─── Scene: Incline ───
    _drawIncline(ctx) {
      const W = this.W / this.zoom;
      const H = this.H / this.zoom;
      const angle = 30 * Math.PI / 180; // 30 deg incline
      const rampLen = Math.min(W * 0.5, 250 / this.zoom);
      const rx1 = W * 0.2, ry1 = H * 0.25;
      const rx2 = rx1 + rampLen * Math.cos(angle), ry2 = ry1 + rampLen * Math.sin(angle);
      const blockX = rx1 + rampLen * 0.6 * Math.cos(angle);
      const blockY = ry1 + rampLen * 0.6 * Math.sin(angle);

      // Ramp
      ctx.strokeStyle = '#666';
      ctx.lineWidth = 4 / this.zoom;
      ctx.beginPath();
      ctx.moveTo(rx1, ry1);
      ctx.lineTo(rx2, ry2);
      ctx.stroke();
      // Ground
      ctx.strokeStyle = '#555';
      ctx.lineWidth = 3 / this.zoom;
      ctx.beginPath();
      ctx.moveTo(rx2, ry2);
      ctx.lineTo(W, ry2);
      ctx.stroke();

      // Block
      const bs = 26 / this.zoom;
      ctx.fillStyle = '#2563eb';
      ctx.save();
      ctx.translate(blockX, blockY);
      ctx.rotate(angle);
      ctx.fillRect(-bs / 2, -bs / 2, bs, bs);
      ctx.strokeStyle = '#1d4ed8';
      ctx.lineWidth = 2 / this.zoom;
      ctx.strokeRect(-bs / 2, -bs / 2, bs, bs);
      ctx.restore();

      // Forces
      const fx = blockX, fy = blockY;
      this._arrow(ctx, fx, fy, fx, fy + 60 / this.zoom, '#f59e0b', 'mg');
      const nx = fx - Math.sin(angle) * 50 / this.zoom;
      const ny = fy - Math.cos(angle) * 50 / this.zoom;
      this._arrow(ctx, fx, fy, nx, ny, '#22c55e', 'N');
      const ffx = fx - Math.cos(angle) * 40 / this.zoom;
      const ffy = fy + Math.sin(angle) * 40 / this.zoom;
      this._arrow(ctx, fx, fy, ffx, ffy, '#ef4444', 'f');

      this._label(ctx, W / 2, 30 / this.zoom, '📐 Incline Plane Analysis', '#10a37f', 16);
      this._label(ctx, W / 2, H - 20 / this.zoom, `θ = 30°  |  μ = ${this.props.mu || '0.2'}`, '#888');
    }

    // ─── Scene: Projectile ───
    _drawProjectile(ctx) {
      const W = this.W / this.zoom;
      const H = this.H / this.zoom;
      const t = this.time;
      const g = 9.8;
      const v0 = 30; const theta = 45 * Math.PI / 180;
      const vx = v0 * Math.cos(theta);
      const vy = v0 * Math.sin(theta);
      const totalTime = 2 * vy / g;
      const curT = Math.min(t * 0.5, totalTime);
      const scale = 4 / this.zoom;

      // Ground
      ctx.fillStyle = '#333';
      ctx.fillRect(0, H - 50 / this.zoom, W, 50 / this.zoom);

      // Trajectory
      ctx.strokeStyle = 'rgba(16, 163, 127, 0.3)';
      ctx.lineWidth = 2 / this.zoom;
      ctx.setLineDash([6 / this.zoom, 4 / this.zoom]);
      ctx.beginPath();
      for (let i = 0; i <= 50; i++) {
        const tt = (i / 50) * totalTime;
        const px = tt * vx * scale;
        const py = H - 50 / this.zoom - (vy * tt - 0.5 * g * tt * tt) * scale;
        i === 0 ? ctx.moveTo(50 / this.zoom + px, py) : ctx.lineTo(50 / this.zoom + px, py);
      }
      ctx.stroke();
      ctx.setLineDash([]);

      // Ball at current position
      const bx = 50 / this.zoom + curT * vx * scale;
      const by = H - 50 / this.zoom - (vy * curT - 0.5 * g * curT * curT) * scale;
      const ballR = 8 / this.zoom;
      ctx.fillStyle = '#ef4444';
      ctx.beginPath();
      ctx.arc(bx, by, ballR, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = 'rgba(239, 68, 68, 0.3)';
      ctx.beginPath();
      ctx.arc(bx, by, ballR * 2, 0, Math.PI * 2);
      ctx.fill();

      // Velocity vector
      const curvx = vx * scale * 0.3;
      const curvy = -(vy - g * curT) * scale * 0.3;
      this._arrow(ctx, bx, by, bx + curvx, by + curvy, '#3b82f6', 'v');

      this._label(ctx, W / 2, 30 / this.zoom, '🎯 Projectile Motion', '#10a37f', 16);
      this._label(ctx, W / 2, H - 10 / this.zoom, `v₀=${v0} m/s  θ=45°  t=${curT.toFixed(1)}s`, '#888');
    }

    // ─── Scene: Pendulum ───
    _drawPendulum(ctx) {
      const W = this.W / this.zoom;
      const H = this.H / this.zoom;
      const t = this.time;
      const pivotX = W / 2, pivotY = 60 / this.zoom;
      const len = 150 / this.zoom;
      const angle = Math.sin(t * 1.5) * 0.4;
      const bobX = pivotX + len * Math.sin(angle);
      const bobY = pivotY + len * Math.cos(angle);

      // Pivot
      ctx.fillStyle = '#888';
      ctx.beginPath();
      ctx.arc(pivotX, pivotY, 6 / this.zoom, 0, Math.PI * 2);
      ctx.fill();

      // String
      ctx.strokeStyle = '#aaa';
      ctx.lineWidth = 2 / this.zoom;
      ctx.beginPath();
      ctx.moveTo(pivotX, pivotY);
      ctx.lineTo(bobX, bobY);
      ctx.stroke();

      // Bob
      const bobR = 14 / this.zoom;
      ctx.fillStyle = '#10a37f';
      ctx.beginPath();
      ctx.arc(bobX, bobY, bobR, 0, Math.PI * 2);
      ctx.fill();
      ctx.fillStyle = 'rgba(16, 163, 127, 0.2)';
      ctx.beginPath();
      ctx.arc(bobX, bobY, bobR * 2, 0, Math.PI * 2);
      ctx.fill();

      // Arc path
      ctx.strokeStyle = 'rgba(255,255,255,0.1)';
      ctx.lineWidth = 1 / this.zoom;
      ctx.beginPath();
      for (let i = -40; i <= 40; i++) {
        const a = (i / 40) * 0.6;
        const px = pivotX + len * Math.sin(a);
        const py = pivotY + len * Math.cos(a);
        i === -40 ? ctx.moveTo(px, py) : ctx.lineTo(px, py);
      }
      ctx.stroke();

      // Force
      this._arrow(ctx, bobX, bobY, bobX, bobY + 50 / this.zoom, '#f59e0b', 'mg');
      this._arrow(ctx, bobX, bobY, pivotX, pivotY, '#22c55e', 'T');

      this._label(ctx, W / 2, 30 / this.zoom, '🔮 Simple Pendulum', '#10a37f', 16);
    }

    // ─── Default: Ambient flow ───
    _drawAmbient(ctx) {
      // Handled by OrganicFlow — this is a fallback
    }
  }

  // ══════════════════════════════════════════════════════════
  // SECTION 3: ORGANIC FLOW (ambient background)
  // ══════════════════════════════════════════════════════════
  class OrganicFlow {
    constructor(canvas) {
      this.canvas = canvas;
      this.ctx = canvas.getContext('2d');
      this.W = 0; this.H = 0;
      this.particles = [];
      this.mouse = { x: 0, y: 0, active: false, down: false };
      this.time = 0;
      this.trail = [];
      this.running = false;
      this._animId = null;
      this._resize();
      this._bindMouse();
      this._spawn();
    }

    _resize = () => {
      this.W = this.canvas.width = window.innerWidth;
      this.H = this.canvas.height = window.innerHeight;
    };

    _bindMouse() {
      const c = this.canvas;
      c.addEventListener('mousemove', (e) => {
        this.mouse.x = e.clientX; this.mouse.y = e.clientY;
        this.mouse.active = true;
        this.trail.push({ x: e.clientX, y: e.clientY, life: 1 });
      });
      c.addEventListener('mouseleave', () => { this.mouse.active = false; });
      c.addEventListener('mousedown', () => { this.mouse.down = true; });
      c.addEventListener('mouseup', () => { this.mouse.down = false; });
      window.addEventListener('resize', this._resize);
    }

    start() { if (!this.running) { this.running = true; this._draw(); } }
    stop() { this.running = false; if (this._animId) { cancelAnimationFrame(this._animId); this._animId = null; } }

    _spawn() {
      const count = Math.min(100, Math.floor(this.W * 0.06));
      this.particles = [];
      for (let i = 0; i < count; i++) {
        const types = ['ambient', 'flow', 'core'];
        const type = types[Math.floor(Math.random() * types.length)];
        this.particles.push({
          x: Math.random() * this.W, y: Math.random() * this.H,
          vx: (Math.random() - 0.5) * 0.4, vy: (Math.random() - 0.5) * 0.4,
          r: type === 'core' ? 3 + Math.random() * 3 : type === 'flow' ? 2 + Math.random() * 2 : 1 + Math.random() * 1.5,
          type,
          phase: Math.random() * Math.PI * 2,
          hue: Math.random() * 60 + 150,
          sat: 60 + Math.random() * 30,
          light: 50 + Math.random() * 20,
          bondTarget: null,
        });
      }
    }

    _draw = () => {
      if (!this.running) return;
      this._animId = requestAnimationFrame(this._draw);
      this.time += 0.005;

      const ctx = this.ctx;
      ctx.clearRect(0, 0, this.W, this.H);

      for (let i = this.particles.length - 1; i >= 0; i--) {
        const p = this.particles[i];
        const n = noise2D(p.x * 0.004 + this.time * 0.3, p.y * 0.004 + this.time * 0.2);
        const angle = n * Math.PI * 2;
        const strength = p.type === 'core' ? 0.15 : p.type === 'flow' ? 0.3 : 0.5;
        p.vx += Math.cos(angle) * strength * 0.05;
        p.vy += Math.sin(angle) * strength * 0.05;

        if (this.mouse.active) {
          const dx = this.mouse.x - p.x, dy = this.mouse.y - p.y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < 200) {
            const force = (200 - dist) / 200 * 0.35;
            if (this.mouse.down) { p.vx += dx / dist * force * 0.5; p.vy += dy / dist * force * 0.5; }
            else { p.vx -= dx / dist * force; p.vy -= dy / dist * force; }
            p.vx += (-dy / dist) * force * 0.15;
            p.vy += (dx / dist) * force * 0.15;
          }
        }

        p.vx *= 0.98; p.vy *= 0.98;
        const spd = Math.sqrt(p.vx * p.vx + p.vy * p.vy);
        const maxSpd = p.type === 'core' ? 0.8 : 1.5;
        if (spd > maxSpd) { p.vx = (p.vx / spd) * maxSpd; p.vy = (p.vy / spd) * maxSpd; }
        p.x += p.vx; p.y += p.vy;
        if (p.x < -50) p.x = this.W + 50; if (p.x > this.W + 50) p.x = -50;
        if (p.y < -50) p.y = this.H + 50; if (p.y > this.H + 50) p.y = -50;

        p.hue += 0.04; if (p.hue > 360) p.hue -= 360;

        if (Math.random() < 0.008) {
          let best = null, bestD = 120;
          for (const o of this.particles) {
            if (o === p) continue;
            const d = Math.sqrt((p.x - o.x) ** 2 + (p.y - o.y) ** 2);
            if (d < bestD && (p.type !== 'ambient' || o.type !== 'ambient')) { bestD = d; best = o; }
          }
          p.bondTarget = best;
        }

        const alpha = 0.3 + Math.sin(p.phase + this.time * 1.5) * 0.2;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(${p.hue}, ${p.sat}%, ${p.light}%, ${alpha})`;
        ctx.fill();

        if (p.type === 'core') {
          ctx.beginPath();
          ctx.arc(p.x, p.y, p.r * 2.5, 0, Math.PI * 2);
          ctx.fillStyle = `hsla(${p.hue}, ${p.sat}%, ${p.light}%, 0.06)`;
          ctx.fill();
        }

        if (p.bondTarget) {
          const dx = p.x - p.bondTarget.x, dy = p.y - p.bondTarget.y;
          const d = Math.sqrt(dx * dx + dy * dy);
          if (d < 150 && d > 0) {
            const ba = (1 - d / 150) * 0.18 * (0.5 + Math.sin(p.phase + this.time * 2) * 0.5);
            ctx.beginPath();
            ctx.moveTo(p.x, p.y);
            ctx.lineTo(p.bondTarget.x, p.bondTarget.y);
            ctx.strokeStyle = `hsla(${(p.hue + p.bondTarget.hue) / 2}, 70%, 60%, ${ba})`;
            ctx.lineWidth = 0.5 + (1 - d / 150) * 1.5;
            ctx.stroke();
          }
        }
      }

      for (let i = this.trail.length - 1; i >= 0; i--) {
        const t = this.trail[i]; t.life -= 0.03;
        if (t.life <= 0) { this.trail.splice(i, 1); continue; }
        ctx.beginPath();
        ctx.arc(t.x, t.y, 2 * t.life, 0, Math.PI * 2);
        ctx.fillStyle = `hsla(160, 80%, 60%, ${t.life * 0.25})`;
        ctx.fill();
      }
      if (this.trail.length > 60) this.trail.splice(0, this.trail.length - 60);
    }

    destroy() { this.stop(); }
  }

  // ══════════════════════════════════════════════════════════
  // SECTION 4: GROWTH CHART
  // ══════════════════════════════════════════════════════════
  class GrowthChart {
    constructor(canvasId) {
      this.canvas = document.getElementById(canvasId);
      if (!this.canvas) return;
      this.ctx = this.canvas.getContext('2d');
      this.W = 0; this.H = 0;
      this.data = [];
      this.progress = 0;
      this._animId = null;
      this._generateData();
      this._resize();
      window.addEventListener('resize', () => this._resize());
      this._draw();
    }

    _generateData() {
      this.data = [];
      let val = 5 + Math.random() * 10;
      for (let i = 0; i < 30; i++) {
        val += Math.random() * 8 - 2 + Math.sin(i * 0.3) * 3;
        val = Math.max(0, val);
        this.data.push({ x: i / 29, y: val });
      }
    }

    _resize() {
      const parent = this.canvas.parentElement;
      if (parent) {
        this.W = this.canvas.width = parent.offsetWidth || 400;
        this.H = this.canvas.height = 200;
      }
    }

    updateData(newData) { if (newData) this.data = newData; this.progress = 0; }

    _draw = () => {
      this._animId = requestAnimationFrame(this._draw);
      this.progress = Math.min(1, this.progress + 0.015);

      const ctx = this.ctx, W = this.W, H = this.H;
      if (W === 0) return;
      ctx.clearRect(0, 0, W, H);

      const pad = { top: 15, right: 15, bottom: 25, left: 35 };
      const cw = W - pad.left - pad.right, ch = H - pad.top - pad.bottom;

      // Grid
      ctx.strokeStyle = 'rgba(255,255,255,0.04)';
      ctx.lineWidth = 1;
      for (let i = 0; i <= 3; i++) {
        const y = pad.top + (ch / 3) * i;
        ctx.beginPath();
        ctx.moveTo(pad.left, y);
        ctx.lineTo(W - pad.right, y);
        ctx.stroke();
      }

      if (!this.data || this.data.length < 2) return;
      const maxY = Math.max(...this.data.map(d => d.y)) * 1.15;

      // Y labels
      ctx.fillStyle = 'rgba(255,255,255,0.25)';
      ctx.font = '9px Inter, sans-serif';
      ctx.textAlign = 'right';
      for (let i = 0; i <= 3; i++) {
        ctx.fillText(Math.round(maxY - (maxY / 3) * i), pad.left - 5, pad.top + (ch / 3) * i + 3);
      }

      // Line
      const visible = Math.floor(this.data.length * this.progress);
      const slice = this.data.slice(0, Math.max(2, visible));
      if (slice.length < 2) return;

      const px = (i) => pad.left + (slice[i].x / slice[slice.length - 1].x) * cw;
      const py = (i) => pad.top + ch - (slice[i].y / maxY) * ch;

      const grad = ctx.createLinearGradient(0, pad.top, 0, H - pad.bottom);
      grad.addColorStop(0, 'rgba(16,163,127,0.2)');
      grad.addColorStop(1, 'rgba(16,163,127,0.01)');

      ctx.beginPath();
      ctx.moveTo(px(0), H - pad.bottom);
      ctx.lineTo(px(0), py(0));
      for (let i = 1; i < slice.length; i++) {
        const xc = (px(i) + px(i - 1)) / 2, yc = (py(i) + py(i - 1)) / 2;
        ctx.quadraticCurveTo(px(i - 1), py(i - 1), xc, yc);
      }
      ctx.lineTo(px(slice.length - 1), H - pad.bottom);
      ctx.closePath();
      ctx.fillStyle = grad;
      ctx.fill();

      ctx.beginPath();
      ctx.moveTo(px(0), py(0));
      for (let i = 1; i < slice.length; i++) {
        const xc = (px(i) + px(i - 1)) / 2, yc = (py(i) + py(i - 1)) / 2;
        ctx.quadraticCurveTo(px(i - 1), py(i - 1), xc, yc);
      }
      ctx.lineTo(px(slice.length - 1), py(slice.length - 1));
      ctx.strokeStyle = '#10a37f';
      ctx.lineWidth = 2;
      ctx.shadowColor = 'rgba(16,163,127,0.3)';
      ctx.shadowBlur = 6;
      ctx.stroke();
      ctx.shadowBlur = 0;

      for (let i = 0; i < slice.length; i++) {
        const pulse = 0.6 + Math.sin(this.progress * 15 + i * 0.5) * 0.4;
        ctx.beginPath();
        ctx.arc(px(i), py(i), 2.5 * pulse, 0, Math.PI * 2);
        ctx.fillStyle = '#10a37f';
        ctx.fill();
        ctx.beginPath();
        ctx.arc(px(i), py(i), 4 * pulse, 0, Math.PI * 2);
        ctx.fillStyle = 'rgba(16,163,127,0.15)';
        ctx.fill();
      }
    };

    destroy() { if (this._animId) cancelAnimationFrame(this._animId); }
  }

  // ══════════════════════════════════════════════════════════
  // SECTION 5: ZOOM CONTROLS
  // ══════════════════════════════════════════════════════════
  function addZoomControls() {
    const container = document.getElementById('particle-canvas')?.parentElement;
    if (!container || document.getElementById('zoom-controls')) return;
    const controls = el('div', { id: 'zoom-controls', class: 'zoom-controls' });
    controls.innerHTML = `
      <button class="zoom-btn" id="zoom-in" title="Zoom In">+</button>
      <button class="zoom-btn" id="zoom-out" title="Zoom Out">−</button>
      <div class="zoom-level" id="zoom-level">×1</div>
    `;
    container.appendChild(controls);
  }

  function updateZoomDisplay(z) {
    const d = $('#zoom-level');
    if (d) d.textContent = '×' + z.toFixed(1);
  }

  // ══════════════════════════════════════════════════════════
  // SECTION 6: PUBLIC INIT & API
  // ══════════════════════════════════════════════════════════
  let organicFlow = null;
  let physicsScene = null;
  let growthChart = null;
  let activeRenderer = 'ambient';

  function init() {
    addZoomControls();

    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;

    organicFlow = new OrganicFlow(canvas);
    physicsScene = new PhysicsScene(canvas);
    growthChart = new GrowthChart('growth-chart');

    // Start with ambient
    organicFlow.start();
    activeRenderer = 'ambient';

    // Wire zoom buttons
    $('#zoom-in')?.addEventListener('click', () => {
      if (physicsScene) {
        physicsScene.targetZoom = Math.min(5, physicsScene.targetZoom * 1.3);
        updateZoomDisplay(physicsScene.targetZoom);
      }
    });
    $('#zoom-out')?.addEventListener('click', () => {
      if (physicsScene) {
        physicsScene.targetZoom = Math.max(0.3, physicsScene.targetZoom * 0.7);
        updateZoomDisplay(physicsScene.targetZoom);
      }
    });

    // Ctrl+wheel zoom
    canvas.addEventListener('wheel', (e) => {
      if (!e.ctrlKey && !e.metaKey) return;
      e.preventDefault();
      if (!physicsScene) return;
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      physicsScene.targetZoom = Math.min(5, Math.max(0.3, physicsScene.targetZoom * delta));
      updateZoomDisplay(physicsScene.targetZoom);
    }, { passive: false });

    // Double-click to reset zoom
    canvas.addEventListener('dblclick', () => {
      if (physicsScene) {
        physicsScene.targetZoom = 1;
        physicsScene.targetPanX = 0;
        physicsScene.targetPanY = 0;
        updateZoomDisplay(1);
      }
    });
  }

  /**
   * Called from app.js on problem submit. Renders matching physics scene.
   */
  function showSceneForProblem(problemText) {
    if (!physicsScene || !organicFlow) return;
    const type = analyzeProblem(problemText);

    if (type === SCENE_TYPES.DEFAULT) {
      resetToAmbient();
      return;
    }

    // Stop ambient, start physics
    organicFlow.stop();
    physicsScene.setScene(type, { mu: '0.2' });
    physicsScene.targetZoom = 1;
    physicsScene.targetPanX = 0;
    physicsScene.targetPanY = 0;
    physicsScene.start();
    activeRenderer = 'physics';
    updateZoomDisplay(1);

    // Auto-zoom into tire-road contact for car friction
    if (type === SCENE_TYPES.CAR_FRICTION) {
      setTimeout(() => {
        // Zoom into right tire contact patch
        const cx = physicsScene.W / physicsScene.zoom * 0.3 + 50 / physicsScene.zoom;
        const cy = (physicsScene.H / physicsScene.zoom * 0.55 + 60 / physicsScene.zoom);
        physicsScene.zoomTo(cx, cy, 2.8);
        updateZoomDisplay(2.8);
      }, 600);
    }
  }

  function resetToAmbient() {
    if (physicsScene) { physicsScene.stop(); physicsScene.resetView(); }
    if (organicFlow) {
      organicFlow.stop();
      organicFlow._spawn(); // refresh particles
      organicFlow.start();
    }
    activeRenderer = 'ambient';
    updateZoomDisplay(1);
  }

  function updateChartData(data) {
    if (growthChart) growthChart.updateData(data);
  }

  return { init, showSceneForProblem, resetToAmbient, updateChartData };
})();

document.addEventListener('DOMContentLoaded', () => PhiversityViz.init());
