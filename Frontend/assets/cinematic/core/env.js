/* PHV core: namespace, device/quality detection, shared utils */
(function () {
  'use strict';
  var w = window;
  var PHV = w.PHV = w.PHV || {};

  var rmQuery = w.matchMedia ? w.matchMedia('(prefers-reduced-motion: reduce)') : { matches: false };

  var env = {
    reduced: function () { return rmQuery.matches; },
    touch: function () { return (w.matchMedia && w.matchMedia('(pointer: coarse)').matches) || 'ontouchstart' in w; },
    finePointer: function () { return w.matchMedia && w.matchMedia('(pointer: fine)').matches; },
    smallScreen: function () { return Math.min(w.innerWidth, w.innerHeight) < 700 || w.innerWidth < 700; },
    hasWebGL: function () {
      try {
        var c = document.createElement('canvas');
        return !!(w.WebGLRenderingContext && (c.getContext('webgl') || c.getContext('experimental-webgl')));
      } catch (e) { return false; }
    },
    quality: function () {
      // 2 = full desktop, 1 = tablet/small, 0 = minimal
      if (env.smallScreen()) return 0;
      if (w.innerWidth < 1100) return 1;
      return 2;
    },
    dpr: function () {
      var cap = env.quality() === 2 ? 2 : 1.5;
      return Math.min(w.devicePixelRatio || 1, cap);
    }
  };

  /* math utils */
  var utils = {
    clamp: function (v, a, b) { return v < a ? a : v > b ? b : v; },
    lerp: function (a, b, t) { return a + (b - a) * t; },
    smooth: function (t) { return t <= 0 ? 0 : t >= 1 ? 1 : t * t * (3 - 2 * t); },
    ease: function (t) { return t <= 0 ? 0 : t >= 1 ? 1 : 1 - Math.pow(1 - t, 3); },
    rand: function (a, b) { return a + Math.random() * (b - a); },
    smoothstep: function (edge0, edge1, x) {
      var t = utils.clamp((x - edge0) / (edge1 - edge0), 0, 1);
      return t * t * (3 - 2 * t);
    },
    /* window of activity: rises 0->1 across [a,b], holds, falls across [c,d] */
    window: function (x, a, b, c, d) {
      return utils.smoothstep(a, b, x) * (1 - utils.smoothstep(c, d, x));
    },
    seedRandom: function (seed) {
      var s = seed >>> 0;
      return function () {
        s = (s * 1664525 + 1013904223) >>> 0;
        return s / 4294967296;
      };
    }
  };

  PHV.env = env;
  PHV.utils = utils;
})();
