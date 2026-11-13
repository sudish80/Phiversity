/* PHV core: canvas-texture glyph + equation sprites */
(function () {
  'use strict';
  var PHV = window.PHV = window.PHV || {};
  var T = window.THREE;

  var cache = {};

  function makeTexture(draw, w, h) {
    var c = document.createElement('canvas');
    c.width = w; c.height = h;
    var ctx = c.getContext('2d');
    draw(ctx, w, h);
    var tex = new T.CanvasTexture(c);
    tex.anisotropy = 2;
    return tex;
  }

  /* single math glyph (∑ ∫ π √ ∞ Δ ∇ λ) */
  function glyphTexture(ch, color) {
    var key = 'g:' + ch + ':' + color;
    if (cache[key]) return cache[key];
    var tex = makeTexture(function (ctx, w, h) {
      ctx.clearRect(0, 0, w, h);
      ctx.font = '500 150px "Space Grotesk","IBM Plex Mono",serif';
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillStyle = color || '#c9d2ff';
      ctx.shadowColor = color || '#8b5cf6';
      ctx.shadowBlur = 22;
      ctx.fillText(ch, w / 2, h / 2 + 6);
      ctx.fillText(ch, w / 2, h / 2 + 6);
    }, 192, 192);
    cache[key] = tex;
    return tex;
  }

  /* equation strip, e.g. "e^{iπ} + 1 = 0" (plain text, keep short) */
  function equationTexture(text, opts) {
    opts = opts || {};
    var key = 'e:' + text + ':' + (opts.color || '');
    if (cache[key]) return cache[key];
    var pad = 28;
    var measure = document.createElement('canvas').getContext('2d');
    measure.font = '500 54px "IBM Plex Mono",monospace';
    var tw = Math.ceil(measure.measureText(text).width) + pad * 2;
    var tex = makeTexture(function (ctx, w, h) {
      ctx.clearRect(0, 0, w, h);
      ctx.font = '500 54px "IBM Plex Mono",monospace';
      ctx.textBaseline = 'middle';
      ctx.textAlign = 'left';
      ctx.shadowColor = opts.glow || '#7c5cff';
      ctx.shadowBlur = 18;
      ctx.fillStyle = opts.color || '#dfe3ff';
      ctx.fillText(text, pad, h / 2);
      ctx.fillText(text, pad, h / 2);
    }, Math.min(tw, 1024), 96);
    cache[key] = tex;
    return tex;
  }

  /* sprite from a texture, worldSize in scene units */
  function sprite(tex, worldSize) {
    var m = new T.SpriteMaterial({ map: tex, transparent: true, depthWrite: false, opacity: 1 });
    var s = new T.Sprite(m);
    var ratio = tex.image.height / tex.image.width;
    s.scale.set(worldSize, worldSize * ratio, 1);
    return s;
  }

  /* floating glyph field + invisible hit spheres for cursor labels */
  function makeGlyphField(chars, opts) {
    opts = opts || {};
    var grp = new T.Group();
    var rnd = PHV.utils.seedRandom(opts.seed || 33);
    var hits = [];
    var span = opts.span || { x: 22, y: 9, z: 16 };
    chars.forEach(function (ch, i) {
      var col = i % 3 === 0 ? '#8b5cf6' : i % 3 === 1 ? '#7dd3fc' : '#c9d2ff';
      var sp = sprite(glyphTexture(ch, col), opts.size || (0.9 + rnd() * 1.1));
      sp.position.set(
        (rnd() - 0.5) * span.x,
        (rnd() - 0.35) * span.y,
        -2 - rnd() * span.z
      );
      sp.userData = {
        baseY: sp.position.y,
        phase: rnd() * Math.PI * 2,
        speed: 0.2 + rnd() * 0.4,
        label: opts.labels ? opts.labels[i % opts.labels.length] : null,
        drift: 0.15 + rnd() * 0.3
      };
      grp.add(sp);

      if (sp.userData.label) {
        var hit = new T.Mesh(
          new T.SphereGeometry(1.05, 8, 6),
          new T.MeshBasicMaterial({ visible: false })
        );
        hit.position.copy(sp.position);
        hit.userData = { label: sp.userData.label, sprite: sp };
        grp.add(hit);
        hits.push(hit);
      }
    });
    grp.userData = {
      sprites: grp.children.filter(function (c) { return c.isSprite; }),
      hits: hits,
      update: function (t) {
        grp.userData.sprites.forEach(function (sp) {
          sp.position.y = sp.userData.baseY + Math.sin(t * sp.userData.speed + sp.userData.phase) * sp.userData.drift;
          var m = sp.material;
        });
        for (var i = 0; i < hits.length; i++) hits[i].position.copy(hits[i].userData.sprite.position);
      }
    };
    return grp;
  }

  PHV.symbols = {
    glyphTexture: glyphTexture,
    equationTexture: equationTexture,
    sprite: sprite,
    makeGlyphField: makeGlyphField
  };
})();
