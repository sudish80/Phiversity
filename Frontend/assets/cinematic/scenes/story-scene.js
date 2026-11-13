/* PHV scenes: the persistent story world — one WebGL stage behind the
   page. Camera is choreographed by scroll segments (story-timeline.js
   writes {seg, segT}); this file builds the environments and resolves
   the pose + object states every frame. */
(function () {
  'use strict';
  var PHV = window.PHV = window.PHV || {};
  var U = PHV.utils;
  var T = window.THREE;

  /* camera keyframe poses: [pos, target, fov] */
  var POSES = {
    hero: { pos: [0, 3.0, 13], target: [0, 0.8, -6], fov: 46 },
    question: { pos: [0, 2.3, 8.6], target: [0, 0.7, -10], fov: 46 },
    product: { pos: [0, 3.6, 9.5], target: [0, 1.6, -9], fov: 46 },
    finale: { pos: [0, 2.6, 13.5], target: [0, 1.1, -6], fov: 44 }
  };
  /* journey camera stops (CatmullRom) */
  var J_POS = [
    [0, 1.9, 0.8],      // mathematics
    [5.4, 2.1, -0.6],    // physics
    [0, 1.85, -10.2],    // chemistry
    [-5.4, 1.95, -4.4]   // economics
  ];
  var J_TGT = [
    [0, 1.0, -6],
    [9, 1.3, -5.5],
    [0, 1.1, -16],
    [-9, 1.2, -9.5]
  ];

  function tagOpacity(grp) {
    grp.traverse(function (o) {
      var m = o.material;
      if (m && m.userData && m.userData.baseOpacity != null) return;
      if (m) m.userData.baseOpacity = m.opacity != null ? m.opacity : 1;
    });
  }
  function setFade(grp, f) {
    grp.traverse(function (o) {
      var m = o.material;
      if (!m) return;
      if (m.userData && m.userData.baseOpacity != null) m.opacity = m.userData.baseOpacity * f;
    });
  }

  var story = null;

  function build() {
    var host = document.getElementById('phv-story');
    if (!host) return null;
    var q = PHV.env.quality();

    var stage = new PHV.Stage(host, { fog: false });
    var rig = new PHV.Rig(stage.camera);
    var scene = stage.scene;

    var amb = new T.AmbientLight(0x44445f, 0.55);
    var key = new T.PointLight(0x8b5cf6, 0.9, 80);
    key.position.set(4, 8, 2);
    var fill = new T.PointLight(0x38bdf8, 0.35, 60);
    fill.position.set(-6, 4, -10);
    scene.add(amb, key, fill);

    /* ---------- persistent world ---------- */
    var grid = PHV.geo.makeGrid({ y: -2.6, lineColor: '#262a45' });
    scene.add(grid);
    var gridU = grid.material.uniforms;

    var dust = PHV.geo.makeParticles({
      count: q === 2 ? 450 : q === 1 ? 280 : 180,
      width: 34, height: 15, depth: 48, size: 2.0,
      colorA: '#c9d4ff', colorB: '#8b5cf6'
    });
    dust.material.uniforms.uPixelRatio.value = PHV.env.dpr();
    scene.add(dust);

    /* ---------- hero environment ---------- */
    var heroGrp = new T.Group();
    scene.add(heroGrp);

    var glyphs = PHV.symbols.makeGlyphField(
      ['∑', '∫', 'π', '√', '∞', 'Δ', '∇', 'λ'],
      {
        size: 1.1, span: { x: 20, y: 8, z: 15 },
        labels: ['∑ Series', '∫ Integrals', 'π Geometry', '√ Roots', '∞ Limits', 'Δ Change', '∇ Fields', 'λ Waves']
      }
    );
    heroGrp.add(glyphs);

    var sphere = PHV.geo.makeWire('icosa', 1.5, '#7c86c2', 0.4);
    sphere.position.set(5.2, 1.7, -9);
    var sphereGlow = PHV.geo.makeGlow({ color: '#38bdf8', size: 6, intensity: 0.22 });
    sphereGlow.position.copy(sphere.position);
    sphereGlow.position.z -= 0.5;
    var octa = PHV.geo.makeWire('octa', 1.1, '#8b93c9', 0.35);
    octa.position.set(-5.6, 2.3, -11);
    var knot = new T.Mesh(
      new T.TorusKnotGeometry(0.85, 0.24, 56, 8),
      new T.MeshBasicMaterial({ color: 0x565f8f, wireframe: true, transparent: true, opacity: 0.24, depthWrite: false })
    );
    knot.position.set(-2.6, 3.6, -16);
    heroGrp.add(sphere, sphereGlow, octa, knot);
    tagOpacity(heroGrp);
    heroGrp.userData.update = function (t) {
      sphere.rotation.y = t * 0.12; sphere.rotation.x = t * 0.045;
      octa.rotation.y = -t * 0.1; octa.rotation.z = t * 0.06;
      knot.rotation.y = t * 0.08; knot.rotation.x = -t * 0.05;
      glyphs.userData.update(t);
      sphereGlow.lookAt(stage.camera.position);
    };

    /* ---------- question object ---------- */
    var questGrp = new T.Group();
    var dodeca = PHV.geo.makeWire('dodeca', 1.05, '#a78bfa', 0.5);
    dodeca.position.set(3.6, 1.5, -11.5);
    var dodecaGlow = PHV.geo.makeGlow({ color: '#8b5cf6', size: 5, intensity: 0.3 });
    dodecaGlow.position.copy(dodeca.position);
    dodecaGlow.position.z -= 0.6;
    questGrp.add(dodeca, dodecaGlow);
    tagOpacity(questGrp);
    questGrp.userData.update = function (t) {
      dodeca.rotation.y = t * 0.22; dodeca.rotation.x = t * 0.09;
      dodecaGlow.lookAt(stage.camera.position);
    };
    scene.add(questGrp);

    /* ---------- mathematics ---------- */
    var mathGrp = new T.Group();
    mathGrp.position.set(0, 1.0, -6);
    var axes = PHV.geo.makeAxes(3.1, '#5f6a94');
    mathGrp.add(axes);
    /* morphing curve: sine ⇄ gaussian bell */
    var N = 121;
    var sinArr = new Float32Array(N * 3), bellArr = new Float32Array(N * 3);
    var curveGeo = new T.BufferGeometry();
    for (var i = 0; i < N; i++) {
      var x = -2.7 + (5.4 * i) / (N - 1);
      sinArr[i * 3] = x;
      sinArr[i * 3 + 1] = Math.sin(x * 1.6) * 0.62;
      sinArr[i * 3 + 2] = 0;
      bellArr[i * 3] = x;
      bellArr[i * 3 + 1] = Math.exp(-x * x / 1.5) * 1.5 - 0.35;
      bellArr[i * 3 + 2] = 0;
    }
    curveGeo.setAttribute('position', new T.BufferAttribute(sinArr.slice(), 3));
    var curveMat = new T.LineBasicMaterial({ color: 0xa78bfa, transparent: true, opacity: 1, blending: T.AdditiveBlending, depthWrite: false });
    var curve = new T.Line(curveGeo, curveMat);
    mathGrp.add(curve);
    var morph = { t: 0 };
    mathGrp.userData.update = function (t, j) {
      axes.rotation.y = Math.sin(t * 0.2) * 0.14;
      /* draw (j 0→.1) then morph (j .1→.2 of window) */
      var w = U.window(j, -0.02, 0.16, 0.24, 0.32); // activity window
      morph.t = U.smoothstep(0.12, 0.24, j);
      var pos = curve.geometry.attributes.position.array;
      for (var k = 0; k < N * 3; k += 3) {
        pos[k + 1] = U.lerp(sinArr[k + 1], bellArr[k + 1], morph.t);
      }
      curve.geometry.attributes.position.needsUpdate = true;
      curve.geometry.setDrawRange(0, Math.round(U.clamp(U.smoothstep(-0.02, 0.12, j), 0.02, 1) * N));
    };
    tagOpacity(mathGrp);
    scene.add(mathGrp);

    /* ---------- physics ---------- */
    var physGrp = new T.Group();
    var wave = PHV.geo.makeWave({ segments: q === 0 ? 30 : 44, opacity: 0.34, wireframe: true });
    wave.position.set(9, 0.9, -5.5);
    wave.rotation.x = -Math.PI / 2.4;
    physGrp.add(wave);
    var gyro = new T.Group();
    var ring1 = new T.Mesh(
      new T.TorusGeometry(1.25, 0.045, 12, 48),
      new T.MeshBasicMaterial({ color: 0x7dd3fc, transparent: true, opacity: 0.65, depthWrite: false })
    );
    var ring2 = ring1.clone();
    ring2.rotation.x = Math.PI / 2.4;
    var axis = new T.Mesh(
      new T.CylinderGeometry(0.02, 0.02, 3.4, 8),
      new T.MeshBasicMaterial({ color: 0x5f6a94, transparent: true, opacity: 0.6, depthWrite: false })
    );
    gyro.add(ring1, ring2, axis);
    gyro.position.set(9, 1.9, -5.5);
    physGrp.add(gyro);
    var arrows = new T.Group();
    for (var a = 0; a < 3; a++) {
      var dir = new T.Vector3(Math.cos(a * 2.1), 0.7 + a * 0.15, Math.sin(a * 2.1)).normalize();
      var arrow = new T.ArrowHelper(dir, new T.Vector3(0, 0, 0), 1.5, 0x7dd3fc, 0.34, 0.18);
      arrow.position.set(9 + Math.cos(a * 2.1) * 2.4, 1.1, -5.5 + Math.sin(a * 2.1) * 2.4);
      arrows.add(arrow);
    }
    physGrp.add(arrows);
    tagOpacity(physGrp);
    physGrp.userData.update = function (t, j) {
      var amp = U.window(j, 0.2, 0.34, 0.46, 0.56);
      wave.material.uniforms.uAmp.value = amp * 1.1;
      wave.material.uniforms.uTime.value = t;
      gyro.rotation.y = t * 0.55;
      gyro.rotation.z = Math.sin(t * 0.4) * 0.2;
      arrows.rotation.y = t * 0.18;
      arrows.children.forEach(function (ar) { ar.position.y = 1.1 + Math.sin(t * 1.3 + ar.position.x) * 0.22; });
    };
    scene.add(physGrp);

    /* ---------- chemistry ---------- */
    var chemGrp = new T.Group();
    var molecule = PHV.geo.makeMolecule();
    molecule.position.set(0, 1.1, -16);
    molecule.scale.setScalar(0.92);
    chemGrp.add(molecule);
    var chemGlow = PHV.geo.makeGlow({ color: '#7c3aed', size: 7, intensity: 0.25 });
    chemGlow.position.set(0, 1.1, -16.8);
    chemGrp.add(chemGlow);
    chemGrp.userData.update = function (t, j) {
      molecule.rotation.y = t * 0.3 + Math.sin(t * 0.2) * 0.25;
      molecule.rotation.x = Math.sin(t * 0.13) * 0.18;
      molecule.userData.setProgress(U.smoothstep(0.46, 0.72, j));
      chemGlow.lookAt(stage.camera.position);
    };
    tagOpacity(chemGrp);
    /* molecule materials need per-atom control — exclude from blanket fade */
    chemGrp.traverse(function (o) {
      var m = o.material;
      if (m) m.userData.baseOpacity = 1;
    });
    scene.add(chemGrp);

    /* ---------- economics ---------- */
    var econGrp = new T.Group();
    econGrp.position.set(-9, 1.2, -9.5);
    var eAxes = PHV.geo.makeAxes(2.6, '#5f6a94');
    econGrp.add(eAxes);
    var supply = PHV.geo.makeCurve(
      PHV.geo.sampleCurve(function (x) { return 0.32 * x + 0.2; }, -2.2, 2.2, 60),
      '#7dd3fc', { opacity: 1 }
    );
    var demand = PHV.geo.makeCurve(
      PHV.geo.sampleCurve(function (x) { return -0.34 * x + 1.3; }, -2.2, 2.2, 60),
      '#a78bfa', { opacity: 1 }
    );
    econGrp.add(supply.mesh, demand.mesh);
    var crossRing = PHV.geo.makeRipple('#ffffff');
    crossRing.scale.setScalar(0.5);
    crossRing.position.set(1.67, 0.73, 0);
    econGrp.add(crossRing);
    tagOpacity(econGrp);
    econGrp.userData.update = function (t, j) {
      var drawS = U.smoothstep(0.74, 0.84, j);
      var drawD = U.smoothstep(0.8, 0.9, j);
      supply.setProgress(drawS);
      demand.setProgress(drawD);
      var ringOn = U.smoothstep(0.88, 0.93, j);
      crossRing.material.uniforms.uOpacity.value = ringOn * (0.5 + Math.sin(t * 2.4) * 0.3);
      eAxes.rotation.y = Math.sin(t * 0.16) * 0.12;
    };
    scene.add(econGrp);

    /* ---------- finale ---------- */
    var finGrp = new T.Group();
    var phi = PHV.geo.makePhi({ emissive: '#7c3aed', emissiveIntensity: 1.1 });
    phi.position.set(0, 1.15, -6);
    phi.scale.setScalar(0.001);
    var phiHalo = PHV.geo.makeGlow({ color: '#7c3aed', size: 8, intensity: 0 });
    phiHalo.position.set(0, 1.15, -6.6);
    finGrp.add(phi, phiHalo);
    tagOpacity(finGrp);
    finGrp.userData.update = function (t, f) {
      var s = U.clamp(f, 0, 1);
      phi.scale.setScalar(Math.max(0.001, U.smooth(s) * 1.55));
      phi.rotation.y = t * 0.3;
      phiHalo.lookAt(stage.camera.position);
      phiHalo.material.uniforms.uIntensity.value = s * (0.5 + Math.sin(t * 1.6) * 0.09);
    };
    scene.add(finGrp);

    /* convergence particles around the finale center */
    var convDust = PHV.geo.makeParticles({
      count: q === 2 ? 260 : 150,
      width: 22, height: 10, depth: 14, size: 1.9,
      colorA: '#d8ccff', colorB: '#38bdf8'
    });
    convDust.material.uniforms.uPixelRatio.value = PHV.env.dpr();
    convDust.material.uniforms.uOpacity.value = 0;
    convDust.position.set(0, 1.15, -6);
    scene.add(convDust);

    /* ---------- state driven by scroll segments ---------- */
    var state = { seg: 'hero', segT: 0, J: 0, fin: 0, running: true };
    var pointer = { x: 0, y: 0 };

    function resolvePose() {
      var par = 0;
      var px = pointer.x, py = pointer.y;
      if (state.seg === 'hero') {
        rig.mix(POSES.hero, POSES.hero, 0);
        rig.fov = POSES.hero.fov;
        rig.pos.x += px * 0.55;
        rig.pos.y += py * 0.3;
      } else if (state.seg === 'toQuestion') {
        rig.mix(POSES.hero, POSES.question, state.segT, 0.35);
      } else if (state.seg === 'toJourney') {
        rig.mix(POSES.question, { pos: J_POS[0], target: J_TGT[0], fov: 46 }, state.segT, 0.2);
      } else if (state.seg === 'journey') {
        rig.followPath(J_POS, J_TGT, state.J, 48);
        rig.pos.x += px * 0.25;
        rig.pos.y += py * 0.15;
      } else if (state.seg === 'toProduct') {
        var jp = { pos: J_POS[3], target: J_TGT[3], fov: 46 };
        rig.mix(jp, POSES.product, state.segT, 0);
      } else if (state.seg === 'product') {
        rig.mix(POSES.product, POSES.product, 0);
        rig.fov = POSES.product.fov;
      } else if (state.seg === 'toFinale') {
        rig.mix(POSES.product, POSES.finale, state.segT, 0.25);
      } else if (state.seg === 'finale') {
        rig.mix(POSES.finale, POSES.finale, 0);
        rig.fov = POSES.finale.fov;
        rig.pos.x += px * 0.4;
        rig.pos.y += py * 0.22;
      }
    }

    stage.addTick(function (t) {
      resolvePose();
      rig.apply();
      gridU.uTime.value = t;
      dust.material.uniforms.uTime.value = t;
      dust.position.z = stage.camera.position.z;

      var J = state.J, seg = state.seg, sT = state.segT;

      /* world element opacities per zone */
      var gridOn = seg === 'hero' ? 0.55 :
        seg === 'toQuestion' ? U.lerp(0.55, 0.42, sT) :
        seg === 'toJourney' ? U.lerp(0.42, 0.3, sT) :
        seg === 'journey' ? 0.3 :
        seg === 'toProduct' ? U.lerp(0.3, 0.0, sT) :
        seg === 'toFinale' ? U.lerp(0.0, 0.22, sT) :
        seg === 'finale' ? 0.22 : 0;
      gridU.uOpacity.value = gridOn;
      var dustOn = seg === 'product' ? 0.25 : 0.75;
      dust.material.uniforms.uOpacity.value = dustOn;

      var heroOn = seg === 'hero' ? 1 :
        seg === 'toQuestion' ? 1 - sT * 0.85 :
        seg === 'toJourney' ? 0.15 * (1 - sT) : 0;
      setFade(heroGrp, heroOn);
      heroGrp.userData.update(t);

      var questOn = seg === 'toQuestion' ? sT :
        seg === 'toJourney' ? 1 - sT : 0;
      setFade(questGrp, questOn);
      questGrp.userData.update(t);

      var mathOn = seg === 'journey' ? U.window(J, -0.06, 0.05, 0.24, 0.3) :
        seg === 'toJourney' ? sT * 0.0 : 0;
      setFade(mathGrp, mathOn);
      mathGrp.userData.update(t, J);

      var physOn = seg === 'journey' ? U.window(J, 0.2, 0.3, 0.46, 0.56) : 0;
      setFade(physGrp, physOn);
      physGrp.userData.update(t, J);

      var chemOn = seg === 'journey' ? U.window(J, 0.46, 0.56, 0.72, 0.8) : 0;
      setFade(chemGrp, chemOn * 0.4 + chemOn * 0.6);
      chemGrp.userData.update(t, J);

      var econOn = seg === 'journey' ? U.window(J, 0.74, 0.83, 0.99, 1.05) :
        seg === 'toProduct' ? 1 - sT : 0;
      setFade(econGrp, econOn);
      econGrp.userData.update(t, J);

      var finOn = seg === 'toFinale' ? U.smooth(sT) : seg === 'finale' ? 1 : 0;
      finGrp.userData.update(t, finOn);
      convDust.material.uniforms.uTime.value = t;
      convDust.material.uniforms.uConverge.value = finOn;
      convDust.material.uniforms.uOpacity.value = finOn * 0.9;
    });

    /* pointer parallax (throttled by rAF already) */
    function onPointer(e) {
      pointer.x = (e.clientX / innerWidth - 0.5) * 2;
      pointer.y = -(e.clientY / innerHeight - 0.5) * 2;
    }
    document.addEventListener('pointermove', onPointer, { passive: true });

    /* hero glyph hover labels via raycast */
    var raycaster = new T.Raycaster();
    var ndc = new T.Vector2();
    function heroHover(e) {
      if (scrollY > innerHeight * 1.25 || state.seg !== 'hero' || !PHV.cursor) return;
      ndc.x = (e.clientX / innerWidth) * 2 - 1;
      ndc.y = -(e.clientY / innerHeight) * 2 + 1;
      raycaster.setFromCamera(ndc, stage.camera);
      var hits = glyphs.userData.hits;
      var hitList = raycaster.intersectObjects(hits, false);
      if (hitList.length) PHV.cursor.setLabel(hitList[0].object.userData.label);
      else PHV.cursor.clearLabel();
    }
    document.addEventListener('pointermove', heroHover, { passive: true });

    function dispose() {
      document.removeEventListener('pointermove', onPointer);
      document.removeEventListener('pointermove', heroHover);
      stage.dispose();
    }

    return {
      stage: stage, rig: rig, state: state, dispose: dispose,
      gridPulse: function () {
        var gU = gridU;
        if (window.gsap) {
          window.gsap.fromTo(gU.uPulseR, { value: 0 }, { value: 24, duration: 1.3, ease: 'power1.out' });
          window.gsap.fromTo(gU.uPulse, { value: 0.6 }, { value: 0, duration: 1.3, ease: 'power1.out' });
        }
      }
    };
  }

  PHV.storyScene = { build: build, POSES: POSES };
})();
