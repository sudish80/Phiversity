/* PHV core: Stage — one WebGLRenderer/scene/camera + RAF manager.
   Handles resize, DPR adaptation, visibility pause, uniform time,
   per-frame callbacks and full disposal. */
(function () {
  'use strict';
  var PHV = window.PHV = window.PHV || {};
  var U = PHV.utils;
  var T = window.THREE;

  function Stage(host, opts) {
    opts = opts || {};
    this.host = typeof host === 'string' ? document.querySelector(host) : host;
    this.fov = opts.fov || 46;
    this.near = opts.near || 0.1;
    this.far = opts.far || 160;
    this.scene = new T.Scene();
    this.scene.fog = opts.fog ? new T.FogExp2(0x000000, opts.fogDensity || 0.028) : null;
    this.camera = new T.PerspectiveCamera(this.fov, 1, this.near, this.far);
    this.camera.position.set(0, 2, 12);
    this.renderer = new T.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    this.renderer.setPixelRatio(PHV.env.dpr());
    this.renderer.setClearColor(0x000000, 0);
    this.renderer.domElement.setAttribute('aria-hidden', 'true');
    this.host.appendChild(this.renderer.domElement);

    this._tick = [];
    this._time = 0;
    this._last = performance.now();
    this._running = false;
    this._rafc = null;
    this._onResize = this._onResize.bind(this);
    this._onVis = this._onVis.bind(this);
    this._frame = this._frame.bind(this);

    window.addEventListener('resize', this._onResize);
    document.addEventListener('visibilitychange', this._onVis);
    this._onResize();
  }

  Stage.prototype.addTick = function (fn) { this._tick.push(fn); };

  Stage.prototype._onResize = function () {
    var w = this.host.clientWidth || window.innerWidth;
    var h = this.host.clientHeight || window.innerHeight;
    this.renderer.setPixelRatio(PHV.env.dpr());
    this.renderer.setSize(w, h, false);
    this.camera.aspect = w / h;
    this.camera.updateProjectionMatrix();
    this.w = w; this.h = h;
  };

  Stage.prototype._onVis = function () {
    if (document.hidden) this.pause();
    else if (this._autoRun) this.start();
  };

  Stage.prototype.start = function () {
    this._autoRun = true;
    if (this._running || document.hidden) return;
    this._running = true;
    this._last = performance.now();
    this._rafc = requestAnimationFrame(this._frame);
  };

  Stage.prototype.pause = function () {
    this._running = false;
    if (this._rafc) cancelAnimationFrame(this._rafc);
    this._rafc = null;
  };

  Stage.prototype._frame = function (now) {
    if (!this._running) return;
    this._rafc = requestAnimationFrame(this._frame);
    var dt = Math.min((now - this._last) / 1000, 0.05);
    this._last = now;
    this._advance(dt);
  };

  /* deterministic stepping for offline/video capture:
     advances the scene by dt seconds and renders exactly one frame */
  Stage.prototype.manual = function (dt) {
    if (this.disposed) return;
    this._advance(dt != null ? dt : 1 / 30);
  };

  Stage.prototype._advance = function (dt) {
    if (!PHV.env.reduced()) this._time += dt;
    var t = this._time;
    for (var i = 0; i < this._tick.length; i++) this._tick[i](t, dt);
    this.renderer.render(this.scene, this.camera);
  };

  /* full teardown — no leaks */
  Stage.prototype.dispose = function () {
    this.pause();
    this.disposed = true;
    window.removeEventListener('resize', this._onResize);
    document.removeEventListener('visibilitychange', this._onVis);
    var kill = (function (obj) {
      obj.traverse(function (o) {
        if (o.geometry) o.geometry.dispose();
        var m = o.material;
        if (m) {
          if (Array.isArray(m)) m.forEach(function (mm) { if (mm.map) mm.map.dispose(); mm.dispose(); });
          else { if (m.map) m.map.dispose(); m.dispose(); }
        }
      });
    })(this.scene);
    this.renderer.dispose();
    if (this.renderer.domElement.parentNode) this.renderer.domElement.parentNode.removeChild(this.renderer.domElement);
    this.renderer = null; this.scene = null; this.camera = null; this._tick = null;
  };

  PHV.Stage = Stage;
})();
