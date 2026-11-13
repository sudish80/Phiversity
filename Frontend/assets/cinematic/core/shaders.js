/* PHV core: GLSL shaders (particles, grid, ripple ring, beam) */
(function () {
  'use strict';
  var PHV = window.PHV = window.PHV || {};

  PHV.shaders = {
    /* ---------- soft glowing particle field ----------
       wraps inside a depth range so particles flow past the camera */
    particles: {
      vertex: [
        'attribute float aSeed;',
        'attribute float aScale;',
        'uniform float uTime;',
        'uniform float uDepth;',
        'uniform float uRush;   /* 0 calm .. 1 hyperdrive */',
        'uniform float uSize;',
        'uniform float uPixelRatio;',
        'uniform float uConverge; /* 0 field .. 1 collapsed to origin */',
        'varying float vAlpha;',
        'void main(){',
        '  vec3 p = position;',
        '  float speed = 0.35 + aSeed * 0.65;',
        '  float z = mod(p.z + uTime * (0.6 + speed * uRush * 9.0), uDepth) - uDepth * 0.72;',
        '  p.z = z;',
        '  p.x += sin(uTime * (0.2 + aSeed) + aSeed * 40.0) * (0.4 - uConverge * 0.35);',
        '  p.y += cos(uTime * (0.16 + aSeed * 0.7) + aSeed * 31.0) * (0.4 - uConverge * 0.35);',
        '  p = mix(p, vec3(0.0), uConverge * (0.55 + aSeed * 0.45));',
        '  vec4 mv = modelViewMatrix * vec4(p, 1.0);',
        '  float dist = -mv.z;',
        '  gl_PointSize = aScale * uSize * uPixelRatio * (140.0 / max(dist, 0.6));',
        '  gl_Position = projectionMatrix * mv;',
        '  float tw = 0.55 + 0.45 * sin(uTime * (1.2 + aSeed * 2.4) + aSeed * 90.0);',
        '  vAlpha = tw * smoothstep(uDepth * 0.72, uDepth * 0.3, dist);',
        '}'
      ].join('\n'),
      fragment: [
        'precision mediump float;',
        'uniform vec3 uColorA;',
        'uniform vec3 uColorB;',
        'uniform float uOpacity;',
        'uniform float uTime;',
        'varying float vAlpha;',
        'void main(){',
        '  float d = length(gl_PointCoord - vec2(0.5));',
        '  float disc = smoothstep(0.5, 0.06, d);',
        '  vec3 col = mix(uColorA, uColorB, smoothstep(0.0, 1.0, sin(vAlpha * 3.14)));',
        '  gl_FragColor = vec4(col, disc * vAlpha * uOpacity);',
        '  if (gl_FragColor.a < 0.003) discard;',
        '}'
      ].join('\n')
    },

    /* ---------- infinite perspective grid floor ---------- */
    grid: {
      vertex: [
        'varying vec3 vWorld;',
        'void main(){',
        '  vec4 wp = modelMatrix * vec4(position, 1.0);',
        '  vWorld = wp.xyz;',
        '  gl_Position = projectionMatrix * viewMatrix * wp;',
        '}'
      ].join('\n'),
      fragment: [
        'precision mediump float;',
        'varying vec3 vWorld;',
        'uniform float uTime;',
        'uniform float uOpacity;',
        'uniform float uFlow;     /* lines streaming toward camera */',
        'uniform float uPulse;   /* 0..1 expanding interaction wave */',
        'uniform float uPulseR;',
        'uniform vec3 uLineCol;',
        'uniform vec3 uAccent;',
        'float gridLine(float coord, float width){',
        '  float g = abs(fract(coord - 0.5) - 0.5) / fwidth(coord);',
        '  return 1.0 - min(g / width, 1.0);',
        '}',
        'void main(){',
        '  vec2 c = vWorld.xz;',
        '  c.y -= uFlow;',
        '  float lx = gridLine(c.x / 1.4, 1.15);',
        '  float lz = gridLine(c.y / 1.4, 1.15);',
        '  float line = max(lx, lz);',
        '  float r = length(vWorld.xz);',
        '  float fade = 1.0 - smoothstep(6.0, 34.0, r);',
        '  /* interaction pulse ring */',
        '  float ring = 0.0;',
        '  if (uPulse > 0.001){',
        '    float pd = abs(r - uPulseR);',
        '    ring = smoothstep(2.2, 0.0, pd) * uPulse;',
        '  }',
        '  vec3 col = uLineCol * line;',
        '  col += uAccent * ring * (0.35 + line * 0.65);',
        '  float a = (line * 0.85 + ring * 0.5) * fade * uOpacity;',
        '  gl_FragColor = vec4(col, a);',
        '  if (a < 0.004) discard;',
        '}'
      ].join('\n')
    },

    /* ---------- expanding shockwave ring ---------- */
    ripple: {
      vertex: [
        'varying vec2 vUv;',
        'void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }'
      ].join('\n'),
      fragment: [
        'precision mediump float;',
        'varying vec2 vUv;',
        'uniform vec3 uColor;',
        'uniform float uOpacity;',
        'void main(){',
        '  float d = length(vUv - vec2(0.5)) * 2.0;',
        '  float ring = smoothstep(0.78, 0.94, d) * (1.0 - smoothstep(0.94, 1.0, d));',
        '  gl_FragColor = vec4(uColor, ring * uOpacity);',
        '}'
      ].join('\n')
    },

    /* ---------- volumetric-ish glow sprite ---------- */
    glow: {
      vertex: [
        'varying vec2 vUv;',
        'void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0); }'
      ].join('\n'),
      fragment: [
        'precision mediump float;',
        'varying vec2 vUv;',
        'uniform vec3 uColor;',
        'uniform float uIntensity;',
        'void main(){',
        '  float d = length(vUv - vec2(0.5)) * 2.0;',
        '  float glow = pow(max(1.0 - d, 0.0), 2.6);',
        '  gl_FragColor = vec4(uColor, glow * uIntensity);',
        '}'
      ].join('\n')
    },

    /* ---------- physics wave surface ---------- */
    wave: {
      vertex: [
        'uniform float uTime;',
        'uniform float uAmp;',
        'varying float vH;',
        'void main(){',
        '  vec3 p = position;',
        '  float x = p.x, y = p.y;',
        '  p.z = uAmp * (',
        '    0.55 * sin(0.55 * x + 0.3 * y - uTime * 1.35)',
        '    + 0.30 * sin(1.05 * y - uTime * 1.8)',
        '    + 0.22 * sin(0.85 * x - 0.6 * y + uTime * 2.1)',
        '  );',
        '  vH = p.z;',
        '  gl_Position = projectionMatrix * modelViewMatrix * vec4(p, 1.0);',
        '}'
      ].join('\n'),
      fragment: [
        'precision mediump float;',
        'uniform vec3 uColA;',
        'uniform vec3 uColB;',
        'uniform float uOpacity;',
        'varying float vH;',
        'void main(){',
        '  vec3 col = mix(uColA, uColB, clamp(vH * 0.6 + 0.5, 0.0, 1.0));',
        '  gl_FragColor = vec4(col, uOpacity);',
        '}'
      ].join('\n')
    }
  };
})();
