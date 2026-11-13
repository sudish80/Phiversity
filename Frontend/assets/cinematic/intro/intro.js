/* PHV intro: cinematic opening — phases A (void) → B (cursor) →
   C (the click) → D (brand reveal) → continuous zoom into the website.
   Resolves with 'done' | 'skipped'. */
(function () {
  'use strict';
  var PHV = window.PHV = window.PHV || {};
  var U = PHV.utils;
  var T = window.THREE;
  var gsap = window.gsap;

  var INTRO_SEEN_KEY = 'phvIntroSeen';
  function introSeen() {
    try { return sessionStorage.getItem(INTRO_SEEN_KEY) === '1'; } catch (e) { return false; }
  }
  function markSeen() {
    try { sessionStorage.setItem(INTRO_SEEN_KEY, '1'); } catch (e) { }
  }

  /* ---------- brand environment (phase D) ---------- */
  function buildBrandEnv() {
    var g = new T.Group();
    var eqs = [
      ['e^{iπ} + 1 = 0', -5.5, 2.6, -30],
      ['F = m·a', 5.2, -1.2, -27],
      ['∇·E = ρ/ε₀', -4.4, -2.2, -21],
      ['PV = nRT', 5.8, 2.8, -33],
      ['y = A·sin(ωx)', -6.4, 0.6, -24],
      ['MC = MR', 3.6, 3.4, -22]
    ];
    var sprites = eqs.map(function (e) {
      var sp = PHV.symbols.sprite(PHV.symbols.equationTexture(e[0]), 4.4);
      sp.position.set(e[1], e[2], e[3]);
      sp.material.opacity = 0;
      sp.userData = { baseOpacity: 0.62, baseY: e[2], phase: Math.random() * 6.28 };
      g.add(sp);
      return sp;
    });

    var octa = PHV.geo.makeWire('octa', 1.6, '#6f7bb8', 0.34);
    octa.position.set(6.5, 0.6, -25);
    octa.material.userData.baseOpacity = 0.34;
    g.add(octa);

    var knot = new T.Mesh(
      new T.TorusKnotGeometry(1.15, 0.32, 64, 10),
      new T.MeshBasicMaterial({ color: 0x4c5583, wireframe: true, transparent: true, opacity: 0, depthWrite: false })
    );
    knot.material.userData.baseOpacity = 0.22;
    knot.position.set(-6.8, 1.6, -29);
    g.add(knot);

    var web = PHV.geo.makeWeb(11, 8, '#6d6fa8');
    web.position.set(0, 0.5, -24);
    web.material.userData.baseOpacity = 0.16;
    g.add(web);

    var phi = PHV.geo.makePhi({ emissive: '#7c3aed', emissiveIntensity: 1.05 });
    phi.position.set(0, 0.5, -24);
    phi.scale.setScalar(1.35);
    phi.traverse(function (o) {
      if (o.material) o.material.userData.baseOpacity = 1;
    });
    g.add(phi);

    var halo = PHV.geo.makeGlow({ color: '#7c3aed', size: 9, intensity: 0 });
    halo.position.set(0, 0.5, -24.6);
    g.add(halo);

    g.userData = {
      fade: 0, t: 0, halo: halo,
      update: function (t) {
        g.userData.t = t;
        knot.rotation.y = t * 0.14; knot.rotation.x = t * 0.07;
        octa.rotation.y = -t * 0.1; octa.rotation.z = t * 0.05;
        web.rotation.z = t * 0.016;
        phi.rotation.y = Math.sin(t * 0.24) * 0.28;
        sprites.forEach(function (sp, i) {
          sp.position.y = sp.userData.baseY + Math.sin(t * 0.35 + sp.userData.phase + i) * 0.12;
        });
      },
      applyFade: function () {
        var f = g.userData.fade, t = g.userData.t;
        halo.material.uniforms.uIntensity.value = (0.5 + Math.sin(t * 1.7) * 0.08) * f;
        g.traverse(function (o) {
          var m = o.material;
          if (!m || o === halo) return;
          if (m.userData && m.userData.baseOpacity != null) m.opacity = m.userData.baseOpacity * f;
        });
      }
    };
    return g;
  }

  function run(revealHook) {
    return new Promise(function (resolve) {
      if (PHV.env.reduced() || !PHV.env.hasWebGL() || !window.THREE || !gsap || introSeen()) {
        resolve('skipped');
        return;
      }

      var overlay = document.getElementById('phv-intro');
      var skipBtn = document.getElementById('phv-skip');
      var brandEl = document.getElementById('phv-brand');
      var actor = document.getElementById('phv-actor');
      if (!overlay || !brandEl || !actor || !skipBtn) { resolve('skipped'); return; }

      var q = PHV.env.quality();
      var isTouch = PHV.env.touch();
      var tl, stage, rafTrail = null, finished = false;
      var trail = [];
      var onKey = null;
      /* exposed for deterministic capture (video rendering) */
      PHV.intro._ctx = null;

      function finish(how) {
        if (finished) return;
        finished = true;
        markSeen();
        if (rafTrail) cancelAnimationFrame(rafTrail);
        trail.forEach(function (tr) { if (tr.parentNode) tr.remove(); });
        trail = [];
        if (onKey) document.removeEventListener('keydown', onKey);
        if (tl) tl.kill();
        gsap.killTweensOf(actor);
        gsap.to(overlay, {
          opacity: 0, duration: 0.45, ease: 'power1.out', overwrite: true,
          onComplete: function () {
            overlay.classList.remove('live');
            overlay.style.display = 'none';
            if (stage) { stage.dispose(); stage = null; }
            resolve(how);
          }
        });
      }

      try {
        stage = new PHV.Stage(overlay, { fog: false });
      } catch (e) { resolve('skipped'); return; }

      var rig = new PHV.Rig(stage.camera);
      rig.pos.set(0, 2.2, 12);
      rig.target.set(0, 0.4, -6);
      var scene = stage.scene;

      var amb = new T.AmbientLight(0x444466, 0);
      var key = new T.PointLight(0x8b5cf6, 0, 70);
      key.position.set(3, 6, 4);
      scene.add(amb, key);

      /* ---------------- void environment (A–C) ---------------- */
      var grid = PHV.geo.makeGrid({ y: -3.2, lineColor: '#2c3050' });
      scene.add(grid);
      var gridU = grid.material.uniforms;

      var dust = PHV.geo.makeParticles({
        count: q === 2 ? 520 : q === 1 ? 320 : 210,
        width: 30, height: 16, depth: 46,
        colorA: '#c9d4ff', colorB: '#8b5cf6', size: 2.2
      });
      dust.material.uniforms.uPixelRatio.value = PHV.env.dpr();
      dust.material.uniforms.uOpacity.value = 0;
      scene.add(dust);

      var horizonGlow = PHV.geo.makeGlow({ color: '#5b21b6', size: 15, intensity: 0 });
      horizonGlow.position.set(0, 0.3, -18);
      scene.add(horizonGlow);

      /* first object the cursor visits */
      var icosa = PHV.geo.makeWire('icosa', 1.15, '#8b93c9', 0.55);
      icosa.position.set(3.4, 0.9, -7);
      var icosaGlow = PHV.geo.makeGlow({ color: '#38bdf8', size: 5.4, intensity: 0 });
      icosaGlow.position.copy(icosa.position); icosaGlow.position.z -= 0.5;
      var icosaCore = new T.Mesh(
        new T.IcosahedronGeometry(0.55, 0),
        new T.MeshBasicMaterial({ color: 0x9db4ff, transparent: true, opacity: 0 })
      );
      icosaCore.position.copy(icosa.position);
      scene.add(icosa, icosaGlow, icosaCore);

      /* the luminous phi symbol — click target */
      var phiGrp = new T.Group();
      phiGrp.position.set(-0.4, 1.05, -12);
      var phi = PHV.geo.makePhi({ emissive: '#7c3aed', emissiveIntensity: 0.8 });
      phi.scale.setScalar(0.9);
      var phiHalo = PHV.geo.makeGlow({ color: '#7c3aed', size: 6, intensity: 0 });
      var phiCore = PHV.geo.makeWire('icosa', 0.62, '#c4b5fd', 0);
      phiGrp.add(phi, phiHalo, phiCore);
      var phiLight = new T.PointLight(0x8b5cf6, 0, 20);
      phiLight.position.set(-0.4, 2.4, -10.5);
      scene.add(phiGrp, phiLight);

      /* ---------------- brand environment (D) ---------------- */
      var brand = buildBrandEnv();
      scene.add(brand);

      /* ---------------- helpers ---------------- */
      function ripple3D(at, color, big) {
        var r = PHV.geo.makeRipple(color);
        r.position.copy(at);
        r.position.z -= big ? 1.4 : 0.3;
        scene.add(r);
        gsap.to(r.scale, { x: big ? 15 : 7, y: big ? 15 : 7, duration: big ? 1.25 : 0.9, ease: 'power2.out' });
        gsap.to(r.material.uniforms.uOpacity, {
          value: 0, duration: big ? 1.25 : 0.9, ease: 'power1.out',
          onComplete: function () {
            scene.remove(r);
            r.geometry.dispose();
            r.material.dispose();
          }
        });
      }
      function gridPulse(strength) {
        gsap.fromTo(gridU.uPulseR, { value: 0 }, { value: 26, duration: 1.4, ease: 'power1.out', overwrite: 'auto' });
        gsap.fromTo(gridU.uPulse, { value: strength }, { value: 0, duration: 1.4, ease: 'power1.out', overwrite: 'auto' });
      }
      function domRipple(px, py, big) {
        var r = document.createElement('div');
        r.className = 'phv-ripple';
        r.style.transform = 'translate(' + px + 'px,' + py + 'px)';
        document.body.appendChild(r);
        gsap.fromTo(r,
          { opacity: 0.9, scale: 0.2 },
          { scale: big ? 5.5 : 3.4, opacity: 0, duration: 0.8, ease: 'power2.out', onComplete: function () { r.remove(); } }
        );
      }

      /* trail dots follow the actor with lag → luminous light trail */
      if (!isTouch) {
        for (var i = 0; i < 8; i++) {
          var d = document.createElement('div');
          d.className = 'phv-trail';
          document.body.appendChild(d);
          trail.push(d);
        }
      }
      function placeTrail() {
        var b = actor.getBoundingClientRect();
        var px = b.left + b.width / 2, py = b.top + b.height / 2;
        var lastX = px, lastY = py;
        for (var i = 0; i < trail.length; i++) {
          var el = trail[i];
          var k = 0.4 - i * 0.04;
          var x = parseFloat(el.dataset.x || lastX), y = parseFloat(el.dataset.y || lastY);
          x += (lastX - x) * k;
          y += (lastY - y) * k;
          el.dataset.x = x; el.dataset.y = y;
          el.style.transform = 'translate(' + x + 'px,' + y + 'px)';
          el.style.opacity = (0.55 * (1 - i / trail.length)).toFixed(3);
          lastX = x; lastY = y;
        }
        rafTrail = requestAnimationFrame(placeTrail);
      }

      /* ---------------- per-frame ---------------- */
      stage.addTick(function (t) {
        rig.apply();
        gridU.uTime.value = t;
        dust.material.uniforms.uTime.value = t;
        icosa.rotation.y = t * 0.35; icosa.rotation.x = t * 0.12;
        phi.rotation.y = Math.sin(t * 0.5) * 0.4 + t * 0.06;
        phiCore.rotation.y = t * 0.8; phiCore.rotation.z = t * 0.4;
        horizonGlow.lookAt(stage.camera.position);
        icosaGlow.lookAt(stage.camera.position);
        phiHalo.lookAt(stage.camera.position);
        dust.position.z = stage.camera.position.z;
        amb.intensity = 0.45 + brand.userData.fade * 0.4;
        key.intensity = 0.5 + brand.userData.fade * 0.45;
        brand.userData.update(t);
        brand.userData.applyFade();
      });

      /* ---------------- DOM refs ---------------- */
      var brandMark = brandEl.querySelector('.mark');
      var brandWord = brandEl.querySelectorAll('.word b');
      var brandSub = brandEl.querySelector('.sub');
      var brandBeam = brandEl.querySelector('.beam');
      var brandSweep = brandEl.querySelector('.sweep');

      /* ---------------- go ---------------- */
      overlay.classList.add('live');
      document.body.classList.add('phv-intro-lock');
      gsap.set(actor, { x: innerWidth * 0.5, y: innerHeight * 0.6 });

      tl = gsap.timeline({ onComplete: function () { finish('done'); } });
      PHV.intro._ctx = { stage: stage, tl: tl, rig: rig, finished: function () { return finished; } };

      /* ===== PHASE A — the void wakes (0 → 1.7) ===== */
      tl.to(gridU.uOpacity, { value: 0.62, duration: 1.4, ease: 'power1.inOut' }, 0.15)
        .to(dust.material.uniforms.uOpacity, { value: 0.8, duration: 1.6, ease: 'power1.inOut' }, 0.2)
        .to(horizonGlow.material.uniforms.uIntensity, { value: 0.32, duration: 1.5, ease: 'power1.inOut' }, 0.35)
        .to(amb, { intensity: 0.45, duration: 1.6 }, 0.25)
        .to(key, { intensity: 0.5, duration: 1.6 }, 0.25)
        .to(rig.pos, { z: 8.2, y: 2.05, duration: 2.9, ease: 'power1.inOut' }, 0.1);

      /* ===== PHASE B — the cursor appears (1.7 → 3.4) ===== */
      tl.set(actor, { opacity: 1 }, 1.7)
        .fromTo(actor, { scale: 0.4 }, { scale: 1, duration: 0.55, ease: 'back.out(2.2)' }, 1.7)
        .to(actor, { x: innerWidth * 0.615, y: innerHeight * 0.42, duration: 1.05, ease: 'power2.inOut' }, 1.85)
        .call(function () { if (!isTouch) placeTrail(); }, null, 1.9)
        /* the object responds */
        .to(icosaGlow.material.uniforms.uIntensity, { value: 0.85, duration: 0.4, ease: 'power2.out' }, 2.6)
        .to(icosaCore.material, { opacity: 0.8, duration: 0.4 }, 2.6)
        .call(function () { ripple3D(icosa.position, '#38bdf8', false); gridPulse(0.45); }, null, 2.75)
        .to(rig.pos, { z: 7.0, duration: 0.9, ease: 'power2.inOut' }, 2.8);

      /* ===== PHASE C — the first click (3.4 → 5.8) ===== */
      tl.to(actor, { x: innerWidth * 0.465, y: innerHeight * 0.44, duration: 0.78, ease: 'power2.inOut' }, 3.45)
        /* pause, then click */
        .to(actor, { scale: 0.75, duration: 0.12, ease: 'power2.in' }, 4.3)
        .call(function () {
          ripple3D(phiGrp.position, '#a78bfa', true);
          domRipple(innerWidth * 0.465, innerHeight * 0.44, true);
          gridPulse(1);
        }, null, 4.42)
        .to(actor, { scale: 1, duration: 0.3, ease: 'back.out(3)' }, 4.46)
        /* the symbol opens */
        .to(phi.userData.parts.barTop.position, { y: 2.6, duration: 0.7, ease: 'power3.out' }, 4.44)
        .to(phi.userData.parts.barBottom.position, { y: -2.6, duration: 0.7, ease: 'power3.out' }, 4.44)
        .to([phi.userData.parts.barTop.material, phi.userData.parts.barBottom.material], { opacity: 0, duration: 0.55, ease: 'power1.out' }, 4.58)
        .to(phi.userData.parts.ring.scale, { x: 3.4, y: 3.4, z: 3.4, duration: 0.95, ease: 'power2.out' }, 4.44)
        .to(phi.userData.parts.ring.material, { opacity: 0, duration: 0.75, ease: 'power1.out' }, 4.6)
        .to(phiCore.scale, { x: 2.1, y: 2.1, z: 2.1, duration: 0.95, ease: 'power2.out' }, 4.44)
        .to(phiCore.material, { opacity: 0.9, duration: 0.4 }, 4.44)
        .to(phiHalo.material.uniforms.uIntensity, { value: 1.2, duration: 0.5, ease: 'power2.out' }, 4.42)
        .to(phiLight, { intensity: 3.4, duration: 0.5, ease: 'power2.out' }, 4.42)
        /* acceleration through the opened symbol — one continuous dolly */
        .to(rig.pos, { x: -3.1, y: 1.35, z: -14.8, duration: 1.3, ease: 'power2.in' }, 4.46)
        .to(rig.target, { x: 0, y: 0.5, z: -24, duration: 1.3, ease: 'power2.in' }, 4.46)
        .to(rig, { fov: 55, duration: 1.15, ease: 'power2.in' }, 4.5)
        .to(dust.material.uniforms.uRush, { value: 1, duration: 1.0, ease: 'power2.in' }, 4.5)
        .to(gridU.uFlow, { value: 10, duration: 1.15, ease: 'power2.in' }, 4.5)
        .to(gridU.uOpacity, { value: 0.95, duration: 0.45 }, 4.55)
        /* void dissolves behind us */
        .to(gridU.uOpacity, { value: 0, duration: 0.5, ease: 'power1.in' }, 5.0)
        .to(horizonGlow.material.uniforms.uIntensity, { value: 0, duration: 0.5 }, 4.95)
        .to(icosaGlow.material.uniforms.uIntensity, { value: 0, duration: 0.4 }, 4.9)
        .to(icosaCore.material, { opacity: 0, duration: 0.4 }, 4.9)
        .to(icosa.material, { opacity: 0, duration: 0.4 }, 4.9)
        .to(phiHalo.material.uniforms.uIntensity, { value: 0, duration: 0.5 }, 5.0)
        .to(phiCore.material, { opacity: 0, duration: 0.5 }, 5.0)
        .to(phiLight, { intensity: 0, duration: 0.5 }, 5.0)
        /* brand environment materializes ahead */
        .to(brand.userData, { fade: 1, duration: 1.0, ease: 'power1.out' }, 4.95);

      /* ===== PHASE D — the Phiversity reveal (5.8 → 8.4) ===== */
      tl.to(actor, { opacity: 0, duration: 0.35 }, 5.1)
        .call(function () {
          if (rafTrail) cancelAnimationFrame(rafTrail);
          rafTrail = null;
          trail.forEach(function (el) { el.remove(); });
          trail = [];
        }, null, 5.4)
        .to(rig, { fov: 46, duration: 1.0, ease: 'power2.out' }, 5.75)
        .to(dust.material.uniforms.uRush, { value: 0.12, duration: 1.6, ease: 'power1.out' }, 5.7)
        /* subtle orbit, settling dead-center */
        .to(rig.pos, { x: 0, y: 1.2, z: -15, duration: 2.1, ease: 'power1.inOut' }, 5.8)
        /* DOM reveal */
        .to(brandEl, { opacity: 1, duration: 0.35 }, 5.95)
        .to(brandBeam, { opacity: 0.9, duration: 0.25, ease: 'power1.in' }, 6.0)
        .fromTo(brandBeam, { left: '-4%' }, { left: '104%', duration: 0.8, ease: 'power2.inOut' }, 6.0)
        .to(brandBeam, { opacity: 0, duration: 0.2 }, 6.72)
        .to(brandMark, { opacity: 1, y: 0, scale: 1, duration: 0.8, ease: 'power3.out' }, 6.25)
        .fromTo(brandWord, { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.65, ease: 'power3.out', stagger: 0.05 }, 6.5)
        .to(brandSub, { opacity: 1, duration: 0.6, ease: 'power2.out' }, 7.05)
        .fromTo(brandSweep, { backgroundPosition: '120% 0' }, { backgroundPosition: '-160% 0', duration: 1.3, ease: 'power2.inOut' }, 6.85)
        /* hold the composition */
        .to({}, { duration: 1.0 }, 7.45);

      /* ===== ZOOM — into the website (8.45 → 9.9) ===== */
      tl.to(rig.pos, { x: 0, y: 0.75, z: -22.2, duration: 1.35, ease: 'power2.inOut' }, 8.45)
        .to(rig.target, { x: 0, y: 0.5, z: -24.1, duration: 1.35, ease: 'power2.inOut' }, 8.45)
        .to(rig, { fov: 40, duration: 1.35, ease: 'power2.inOut' }, 8.45)
        .to(brandEl, { scale: 3.2, duration: 1.35, ease: 'power2.in' }, 8.45)
        /* the website becomes visible BEHIND the fading overlay — no black frame */
        .call(function () {
          document.body.classList.remove('phv-intro-lock');
        }, null, 8.5)
        .call(function () {
          if (revealHook) revealHook();
        }, null, 8.85)
        .to(brandEl, { opacity: 0, duration: 0.5, ease: 'power1.in' }, 9.3)
        .to(overlay, { opacity: 0, duration: 0.7, ease: 'power1.in' }, 9.2)
        .to({}, { duration: 0.15 }, 9.9);

      /* ---------------- skip ---------------- */
      skipBtn.addEventListener('click', function () { finish('skipped'); });
      onKey = function (e) {
        if (e.key === 'Escape') {
          e.preventDefault();
          finish('skipped');
        }
      };
      document.addEventListener('keydown', onKey);
      gsap.to(skipBtn, { opacity: 1, duration: 0.6, delay: 1.1 });

      stage.start();
    });
  }

  PHV.intro = {
    run: run,
    seen: introSeen,
    reset: function () {
      try { sessionStorage.removeItem(INTRO_SEEN_KEY); } catch (e) { }
    }
  };
})();
