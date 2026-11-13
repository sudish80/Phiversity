/* PHV core: procedural geometry + material factories (three r128) */
(function () {
  'use strict';
  var PHV = window.PHV = window.PHV || {};
  var U = PHV.utils;
  var T = window.THREE;

  var geo = {};

  /* ---------- particle field ----------
     Particles live in a box [w,h,depth] and wrap toward the camera
     inside the vertex shader (uTime * speed mod uDepth). */
  geo.makeParticles = function (opts) {
    opts = opts || {};
    var count = opts.count || 400;
    var w = opts.width || 26, h = opts.height || 14, depth = opts.depth || 40;
    var positions = new Float32Array(count * 3);
    var seeds = new Float32Array(count);
    var scales = new Float32Array(count);
    var rnd = U.seedRandom(opts.seed || 7);

    for (var i = 0; i < count; i++) {
      positions[i * 3] = (rnd() - 0.5) * w;
      positions[i * 3 + 1] = (rnd() - 0.42) * h;
      positions[i * 3 + 2] = -rnd() * depth;
      seeds[i] = rnd();
      scales[i] = 0.5 + rnd() * rnd() * 2.6;
    }
    var g = new T.BufferGeometry();
    g.setAttribute('position', new T.BufferAttribute(positions, 3));
    g.setAttribute('aSeed', new T.BufferAttribute(seeds, 1));
    g.setAttribute('aScale', new T.BufferAttribute(scales, 1));

    var m = new T.ShaderMaterial({
      vertexShader: PHV.shaders.particles.vertex,
      fragmentShader: PHV.shaders.particles.fragment,
      uniforms: {
        uTime: { value: 0 },
        uDepth: { value: depth },
        uRush: { value: 0 },
        uConverge: { value: 0 },
        uSize: { value: opts.size || 2.4 },
        uPixelRatio: { value: 1 },
        uOpacity: { value: opts.opacity != null ? opts.opacity : 0.85 },
        uColorA: { value: new T.Color(opts.colorA || '#c9d4ff') },
        uColorB: { value: new T.Color(opts.colorB || '#8b5cf6') }
      },
      transparent: true,
      depthWrite: false,
      blending: T.AdditiveBlending
    });
    var pts = new T.Points(g, m);
    pts.userData.depth = depth;
    return pts;
  };

  /* ---------- perspective grid floor ---------- */
  geo.makeGrid = function (opts) {
    opts = opts || {};
    var g = new T.PlaneGeometry(opts.size || 110, opts.size || 110, 1, 1);
    var m = new T.ShaderMaterial({
      vertexShader: PHV.shaders.grid.vertex,
      fragmentShader: PHV.shaders.grid.fragment,
      uniforms: {
        uTime: { value: 0 },
        uOpacity: { value: opts.opacity != null ? opts.opacity : 0 },
        uFlow: { value: 0 },
        uPulse: { value: 0 },
        uPulseR: { value: 0 },
        uLineCol: { value: new T.Color(opts.lineColor || '#3a3f58') },
        uAccent: { value: new T.Color(opts.accent || '#8b5cf6') }
      },
      transparent: true,
      depthWrite: false,
      side: T.DoubleSide,
      extensions: { derivatives: true }
    });
    var mesh = new T.Mesh(g, m);
    mesh.rotation.x = -Math.PI / 2;
    if (opts.y != null) mesh.position.y = opts.y;
    return mesh;
  };

  /* ---------- ripple ring (pooled shockwaves) ---------- */
  geo.makeRipple = function (color) {
    var g = new T.PlaneGeometry(1, 1);
    var m = new T.ShaderMaterial({
      vertexShader: PHV.shaders.ripple.vertex,
      fragmentShader: PHV.shaders.ripple.fragment,
      uniforms: {
        uColor: { value: new T.Color(color || '#a78bfa') },
        uOpacity: { value: 1 }
      },
      transparent: true,
      depthWrite: false,
      side: T.DoubleSide,
      blending: T.AdditiveBlending
    });
    return new T.Mesh(g, m);
  };

  /* ---------- soft glow billboard ---------- */
  geo.makeGlow = function (opts) {
    opts = opts || {};
    var m = new T.ShaderMaterial({
      vertexShader: PHV.shaders.glow.vertex,
      fragmentShader: PHV.shaders.glow.fragment,
      uniforms: {
        uColor: { value: new T.Color(opts.color || '#7c5cff') },
        uIntensity: { value: opts.intensity != null ? opts.intensity : 0.55 }
      },
      transparent: true,
      depthWrite: false,
      blending: T.AdditiveBlending
    });
    var mesh = new T.Mesh(new T.PlaneGeometry(opts.size || 8, opts.size || 8), m);
    return mesh;
  };

  /* ---------- the Phi brand object (3D) ---------- */
  geo.makePhi = function (opts) {
    opts = opts || {};
    var grp = new T.Group();
    var mat = new T.MeshStandardMaterial({
      color: opts.color || 0x241a45,
      emissive: new T.Color(opts.emissive || '#7c3aed'),
      emissiveIntensity: opts.emissiveIntensity != null ? opts.emissiveIntensity : 0.85,
      metalness: 0.7,
      roughness: 0.28,
      transparent: true,
      opacity: 1
    });
    var ring = new T.Mesh(new T.TorusGeometry(1.06, 0.085, 20, 72), mat);
    var barTop = new T.Mesh(new T.BoxGeometry(0.17, 1.38, 0.17), mat);
    barTop.position.y = 0.69;
    var barBottom = new T.Mesh(new T.BoxGeometry(0.17, 1.38, 0.17), mat);
    barBottom.position.y = -0.69;
    grp.add(ring, barTop, barBottom);
    grp.userData.parts = { ring: ring, barTop: barTop, barBottom: barBottom, mat: mat };
    return grp;
  };

  /* ---------- wireframe polyhedron ---------- */
  geo.makeWire = function (kind, radius, color, opacity) {
    var g;
    if (kind === 'icosa') g = new T.IcosahedronGeometry(radius, 1);
    else if (kind === 'octa') g = new T.OctahedronGeometry(radius, 0);
    else if (kind === 'dodeca') g = new T.DodecahedronGeometry(radius, 0);
    else g = new T.IcosahedronGeometry(radius, 1);
    var m = new T.MeshBasicMaterial({
      color: new T.Color(color || '#8b93c9'),
      wireframe: true,
      transparent: true,
      opacity: opacity != null ? opacity : 0.5,
      depthWrite: false
    });
    return new T.Mesh(g, m);
  };

  /* ---------- curve as fat-ish glowing line ----------
     Returns { mesh, setProgress(p) } — reveals via drawRange. */
  geo.makeCurve = function (points, color, opts) {
    opts = opts || {};
    var g = new T.BufferGeometry().setFromPoints(points);
    var m = new T.LineBasicMaterial({
      color: new T.Color(color || '#a78bfa'),
      transparent: true,
      opacity: opts.opacity != null ? opts.opacity : 1,
      depthWrite: false,
      blending: T.AdditiveBlending
    });
    var line = new T.Line(g, m);
    var total = points.length;
    line.geometry.setDrawRange(0, 0);
    return {
      mesh: line,
      setProgress: function (p) {
        line.geometry.setDrawRange(0, Math.max(0, Math.round(U.clamp(p, 0, 1) * total)));
      },
      setOpacity: function (o) { m.opacity = o; },
      material: m
    };
  };

  /* sample points of y=f(x) on [x0,x1] */
  geo.sampleCurve = function (f, x0, x1, n) {
    var pts = [];
    for (var i = 0; i <= n; i++) {
      var x = x0 + (x1 - x0) * i / n;
      pts.push(new T.Vector3(x, f(x), 0));
    }
    return pts;
  };

  /* ---------- axes tripod ---------- */
  geo.makeAxes = function (len, color) {
    var grp = new T.Group();
    var mat = new T.LineBasicMaterial({ color: new T.Color(color || '#5f6a94'), transparent: true, opacity: 0.7, depthWrite: false });
    var mk = function (a, b) {
      var g = new T.BufferGeometry().setFromPoints([a, b]);
      return new T.Line(g, mat);
    };
    grp.add(
      mk(new T.Vector3(0, 0, 0), new T.Vector3(len, 0, 0)),
      mk(new T.Vector3(0, 0, 0), new T.Vector3(0, len, 0)),
      mk(new T.Vector3(0, 0, 0), new T.Vector3(0, 0, len))
    );
    grp.userData.mat = mat;
    return grp;
  };

  /* ---------- molecule (benzene C6H6) ----------
     atoms: [{pos, r, color}], bonds: [[i,j]] */
  geo.makeMolecule = function (opts) {
    opts = opts || {};
    var grp = new T.Group();
    var atoms = [], bonds = [];

    var atomMat = function (hex) {
      return new T.MeshStandardMaterial({
        color: 0x14141c, emissive: new T.Color(hex), emissiveIntensity: 0.55,
        metalness: 0.5, roughness: 0.4, transparent: true, opacity: 1
      });
    };
    var bondMat = new T.MeshStandardMaterial({
      color: 0x1a1a26, emissive: new T.Color('#4c5583'), emissiveIntensity: 0.4,
      metalness: 0.4, roughness: 0.5, transparent: true, opacity: 1
    });

    var cMat = atomMat('#a78bfa'), hMat = atomMat('#7dd3fc');

    var R = 1.55, i, ang;
    for (i = 0; i < 6; i++) {
      ang = (Math.PI / 3) * i + Math.PI / 6;
      atoms.push({ pos: new T.Vector3(Math.cos(ang) * R, Math.sin(ang) * R, 0), r: 0.42, mat: cMat, kind: 'C' + (i + 1) });
    }
    for (i = 0; i < 6; i++) {
      ang = (Math.PI / 3) * i + Math.PI / 6;
      var hx = Math.cos(ang) * (R + 0.95), hy = Math.sin(ang) * (R + 0.95);
      atoms.push({ pos: new T.Vector3(hx, hy, 0), r: 0.24, mat: hMat, kind: 'H' + (i + 1) });
    }
    for (i = 0; i < 6; i++) bonds.push([i, (i + 1) % 6]);
    for (i = 0; i < 6; i++) bonds.push([i, i + 6]);

    var atomMeshes = atoms.map(function (a) {
      var m = new T.Mesh(new T.SphereGeometry(a.r, 18, 14), a.mat);
      m.position.copy(a.pos);
      m.scale.setScalar(0.001);
      grp.add(m);
      return m;
    });

    var bondMeshes = bonds.map(function (pair) {
      var a = atoms[pair[0]].pos, b = atoms[pair[1]].pos;
      var dir = new T.Vector3().subVectors(b, a);
      var len = dir.length();
      var cyl = new T.Mesh(new T.CylinderGeometry(0.085, 0.085, len, 10), bondMat);
      cyl.position.copy(a).add(b).multiplyScalar(0.5);
      cyl.quaternion.setFromUnitVectors(new T.Vector3(0, 1, 0), dir.normalize());
      cyl.scale.set(1, 0.001, 1);
      grp.add(cyl);
      return cyl;
    });

    grp.userData = {
      atomMeshes: atomMeshes, bondMeshes: bondMeshes, bondMat: bondMat,
      cMat: cMat, hMat: hMat,
      /* p in 0..1 assembles molecule */
      setProgress: function (p) {
        var ap = U.clamp(p * 1.6, 0, 1);      // atoms first
        var bp = U.clamp((p - 0.42) * 1.9, 0, 1); // then bonds
        var nA = atomMeshes.length, nB = bondMeshes.length;
        for (var i = 0; i < nA; i++) {
          var t = U.clamp(ap * nA - i, 0, 1);
          atomMeshes[i].scale.setScalar(Math.max(0.001, t));
          atomMeshes[i].material.opacity = t;
        }
        for (var j = 0; j < nB; j++) {
          var tb = U.clamp(bp * nB - j, 0, 1);
          bondMeshes[j].scale.set(1, Math.max(0.001, tb), 1);
          bondMeshes[j].material.opacity = tb;
        }
      },
      setOpacity: function (o) {
        cMat.opacity = o; hMat.opacity = o; bondMat.opacity = o;
      }
    };
    return grp;
  };

  /* ---------- wave surface ---------- */
  geo.makeWave = function (opts) {
    opts = opts || {};
    var seg = opts.segments || 48;
    var g = new T.PlaneGeometry(11, 11, seg, seg);
    var m = new T.ShaderMaterial({
      vertexShader: PHV.shaders.wave.vertex,
      fragmentShader: PHV.shaders.wave.fragment,
      uniforms: {
        uTime: { value: 0 },
        uAmp: { value: opts.amp != null ? opts.amp : 0 },
        uColA: { value: new T.Color('#38bdf8') },
        uColB: { value: new T.Color('#8b5cf6') },
        uOpacity: { value: opts.opacity != null ? opts.opacity : 0.4 }
      },
      transparent: true,
      depthWrite: false,
      wireframe: !!opts.wireframe,
      side: T.DoubleSide
    });
    var mesh = new T.Mesh(g, m);
    return mesh;
  };

  /* ---------- connection lines (constellation web) ---------- */
  geo.makeWeb = function (count, radius, color) {
    var pts = [];
    var rnd = U.seedRandom(21);
    var nodes = [];
    for (var i = 0; i < count; i++) {
      nodes.push(new T.Vector3((rnd() - 0.5) * radius * 2.4, (rnd() - 0.5) * radius * 1.5, (rnd() - 0.5) * radius * 2));
    }
    for (var j = 0; j < nodes.length; j++) {
      var a = nodes[j], b = nodes[(j + 3) % nodes.length];
      pts.push(a, b);
    }
    var g = new T.BufferGeometry().setFromPoints(pts);
    var m = new T.LineBasicMaterial({
      color: new T.Color(color || '#6d6fa8'),
      transparent: true, opacity: 0.16, depthWrite: false, blending: T.AdditiveBlending
    });
    return new T.LineSegments(g, m);
  };

  PHV.geo = geo;
})();
