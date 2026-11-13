/* PHV core: CameraRig — GSAP-choreographed camera movement.
   All movement flows through a state object; poses are applied per frame,
   so multiple scrub sources blend without fighting. */
(function () {
  'use strict';
  var PHV = window.PHV = window.PHV || {};
  var U = PHV.utils;
  var T = window.THREE;

  function Rig(camera) {
    this.camera = camera;
    /* live pose */
    this.pos = new T.Vector3(0, 2, 12);
    this.target = new T.Vector3(0, 0.5, -6);
    /* parallax offset from pointer */
    this.parallax = { x: 0, y: 0, amount: 0 };
    this.fov = camera.fov;
  }

  Rig.prototype.apply = function () {
    var p = this.pos, t = this.target;
    this.camera.position.set(
      p.x + this.parallax.x * this.parallax.amount,
      p.y + this.parallax.y * this.parallax.amount,
      p.z
    );
    this.camera.lookAt(t.x, t.y, t.z);
    if (this.camera.fov !== this.fov) {
      this.camera.fov = this.fov;
      this.camera.updateProjectionMatrix();
    }
  };

  /* tween the pose with GSAP */
  Rig.prototype.moveTo = function (to, dur, ease, delay) {
    if (!window.gsap) return;
    return window.gsap.to(this, {
      pos: to.pos,
      target: to.target,
      fov: to.fov != null ? to.fov : this.fov,
      duration: dur,
      ease: ease || 'power2.inOut',
      delay: delay || 0
    });
  };

  /* lerp between two poses by t (0..1) — used by scrubbed scroll */
  Rig.prototype.mix = function (a, b, t, parallax) {
    t = U.clamp(t, 0, 1);
    var s = U.smooth(t);
    this.pos.set(
      U.lerp(a.pos[0], b.pos[0], s),
      U.lerp(a.pos[1], b.pos[1], s),
      U.lerp(a.pos[2], b.pos[2], s)
    );
    this.target.set(
      U.lerp(a.target[0], b.target[0], s),
      U.lerp(a.target[1], b.target[1], s),
      U.lerp(a.target[2], b.target[2], s)
    );
    this.fov = U.lerp(a.fov != null ? a.fov : 46, b.fov != null ? b.fov : 46, s);
    if (parallax != null) this.parallax.amount = parallax;
  };

  /* position on a CatmullRom path (arrays of vec3) at t */
  Rig.prototype.followPath = function (posPts, tgtPts, t, fov) {
    t = U.clamp(t, 0, 1);
    if (!this._posCurve || this._posCurveKey !== posPts) {
      this._posCurveKey = posPts;
      this._posCurve = new T.CatmullRomCurve3(posPts.map(function (p) { return new T.Vector3(p[0], p[1], p[2]); }));
      this._tgtCurve = new T.CatmullRomCurve3(tgtPts.map(function (p) { return new T.Vector3(p[0], p[1], p[2]); }));
    }
    var pt = this._posCurve.getPoint(t);
    var tg = this._tgtCurve.getPoint(t);
    this.pos.copy(pt);
    this.target.copy(tg);
    if (fov != null) this.fov = fov;
  };

  /* gentle orbit around a center point, angle in radians */
  Rig.prototype.orbitPose = function (center, radius, angle, height, fov) {
    this.pos.set(
      center[0] + Math.cos(angle) * radius,
      height,
      center[2] + Math.sin(angle) * radius
    );
    this.target.set(center[0], center[1], center[2]);
    if (fov != null) this.fov = fov;
  };

  PHV.Rig = Rig;
})();
