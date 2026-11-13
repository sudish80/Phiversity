/* PHV interactions: cinematic cursor system (desktop only).
   Visual layer only — never intercepts events; system cursor hidden
   via CSS class; Escape restores it instantly. */
(function () {
  'use strict';
  var PHV = window.PHV = window.PHV || {};
  var gsap = window.gsap;

  var el, ring, label, dot;
  var x = -100, y = -100, rx = -100, ry = -100;
  var raf = null, active = false, escapeOn = false;
  var INTERACTIVE = 'a, button, input, textarea, select, summary, [data-cursor]';
  var TEXTY = 'h1, h2, h3, .big, [data-cursor="text"]';

  function loop() {
    raf = requestAnimationFrame(loop);
    rx += (x - rx) * 0.16;
    ry += (y - ry) * 0.16;
    dot.style.transform = 'translate(' + x + 'px,' + y + 'px)';
    ring.style.transform = 'translate(' + rx + 'px,' + ry + 'px)';
    label.style.transform = 'translate(' + rx + 'px,' + ry + 'px)';
  }

  function setState(cls, on) {
    if (on) el.classList.add(cls); else el.classList.remove(cls);
  }

  function onMove(e) {
    x = e.clientX; y = e.clientY;
    if (!active) {
      active = true;
      el.classList.remove('hidden');
      rx = x; ry = y;
    }
  }

  function onOver(e) {
    var t = e.target;
    if (!t || !t.closest) return;
    var hit = t.closest(INTERACTIVE);
    var text = !hit && t.closest(TEXTY);
    setState('hover', !!hit);
    setState('text', !!text);
    var lbl = hit && hit.getAttribute ? hit.getAttribute('data-cursor-label') : null;
    if (lbl) {
      label.textContent = lbl;
      setState('labeled', true);
    } else {
      setState('labeled', false);
    }
  }

  function onDown(e) {
    setState('click', true);
    var r = document.createElement('div');
    r.className = 'phv-click-ripple';
    r.style.transform = 'translate(' + e.clientX + 'px,' + e.clientY + 'px)';
    document.body.appendChild(r);
    gsap.fromTo(r, { opacity: 0.8, scale: 0.25 }, {
      scale: 1.6, opacity: 0, duration: 0.55, ease: 'power2.out',
      onComplete: function () { r.remove(); }
    });
  }
  function onUp() { setState('click', false); }

  function onLeave() {
    active = false;
    el.classList.add('hidden');
  }

  function onKey(e) {
    if (e.key === 'Escape' && !escapeOn) {
      escapeOn = true;
      document.documentElement.classList.add('escape');
    }
  }

  function init() {
    if (PHV.env.touch() || !PHV.env.finePointer() || PHV.env.reduced() || !gsap) return false;
    el = document.createElement('div');
    el.id = 'phv-cursor';
    el.className = 'hidden';
    el.setAttribute('aria-hidden', 'true');
    el.innerHTML = '<div class="ring"></div><div class="dot"></div><div class="label"></div>';
    document.body.appendChild(el);
    ring = el.querySelector('.ring');
    dot = el.querySelector('.dot');
    label = el.querySelector('.label');

    document.addEventListener('pointermove', onMove, { passive: true });
    document.addEventListener('pointerover', onOver, { passive: true });
    document.addEventListener('pointerdown', onDown, { passive: true });
    document.addEventListener('pointerup', onUp, { passive: true });
    document.addEventListener('pointerleave', onLeave);
    document.addEventListener('keydown', onKey);
    loop();
    document.documentElement.classList.add('phv-fx');
    return true;
  }

  function show() {
    if (!el) return;
    gsap.to(el, { opacity: 1, duration: 0.4 });
  }

  /* 3D scenes can push a contextual label (e.g. glyph names) */
  function setLabel(text) {
    if (!el || !text) { setState('labeled', false); return; }
    label.textContent = text;
    setState('labeled', true);
  }
  function clearLabel() { setState('labeled', false); }

  function destroy() {
    if (raf) cancelAnimationFrame(raf);
    document.documentElement.classList.remove('phv-fx', 'escape');
    document.removeEventListener('pointermove', onMove);
    document.removeEventListener('pointerover', onOver);
    document.removeEventListener('pointerdown', onDown);
    document.removeEventListener('pointerup', onUp);
    document.removeEventListener('pointerleave', onLeave);
    document.removeEventListener('keydown', onKey);
    if (el) el.remove();
  }

  PHV.cursor = { init: init, show: show, setLabel: setLabel, clearLabel: clearLabel, destroy: destroy };
})();
