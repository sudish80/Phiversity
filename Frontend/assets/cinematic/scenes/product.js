/* PHV scenes: the product workflow demo — a faithful mock of the real
   Phiversity flow (plan → explain → visualize), animated on entry.
   QUESTION → EXPLANATION → VISUALIZATION → UNDERSTANDING. */
(function () {
  'use strict';
  var PHV = window.PHV = window.PHV || {};
  var gsap = window.gsap;

  function buildTimeline() {
    var app = document.querySelector('.phv-app');
    if (!app || !gsap) return null;

    var qText = app.querySelector('.q .txt');
    var steps = [].slice.call(app.querySelectorAll('.steps .st'));
    var axes = [].slice.call(app.querySelectorAll('#px-graph .axis'));
    var curve = app.querySelector('#px-curve');
    var tangent = app.querySelector('#px-tangent');
    var point = app.querySelector('#px-point');
    var graphPanel = app.querySelector('.panel.graph');
    var vizPanel = app.querySelector('.panel.viz');
    var QUESTION = 'Why does the derivative give the slope of a curve?';

    var proxy = { n: 0 };
    function setText() {
      qText.textContent = QUESTION.slice(0, Math.round(proxy.n));
    }

    var tl = gsap.timeline({ paused: true });

    /* QUESTION — typing (caret blinks via CSS) */
    tl.set(proxy, { n: 0 }, 0);
    qText.textContent = '';
    tl.to(proxy, { n: QUESTION.length, duration: 1.7, ease: 'none', onUpdate: setText });

    /* EXPLANATION — structured steps */
    steps.slice(0, 2).forEach(function (s, i) {
      tl.to(s, { opacity: 1, y: 0, duration: 0.55, ease: 'power2.out' }, i === 0 ? '-=0.25' : '-=0.1');
    });

    /* VISUALIZATION — graph draws itself */
    tl.set([graphPanel, vizPanel], { opacity: 1 }, '-=0.3');
    axes.forEach(function (ax) {
      tl.fromTo(ax, { strokeDashoffset: 300 }, { strokeDashoffset: 0, duration: 0.5, ease: 'power2.out' }, '-=0.35');
    });
    tl.fromTo(curve, { strokeDashoffset: 620 }, { strokeDashoffset: 0, duration: 1.15, ease: 'power2.inOut' }, '-=0.25')
      .fromTo(tangent, { strokeDashoffset: 260, opacity: 0 }, { strokeDashoffset: 0, opacity: 1, duration: 0.7, ease: 'power2.out' }, '-=0.35')
      .fromTo(point, { scale: 0, opacity: 0, transformOrigin: '50% 50%' }, { scale: 1, opacity: 1, duration: 0.4, ease: 'back.out(2)' }, '-=0.3')
      .to(point, { scale: 1.35, duration: 0.5, yoyo: true, repeat: 3, ease: 'sine.inOut' });

    /* step 3 while the graph animates */
    tl.to(steps[2], { opacity: 1, y: 0, duration: 0.55, ease: 'power2.out' }, '-=1.1');
    if (vizPanel) tl.add(function () { vizPanel.classList.add('live'); }, '-=0.5');

    /* UNDERSTANDING */
    tl.to(steps[3], { opacity: 1, y: 0, duration: 0.55, ease: 'power2.out' }, '-=0.15')
      .add(function () { steps[3].classList.add('lit'); });

    return tl;
  }

  PHV.product = { buildTimeline: buildTimeline };
})();
