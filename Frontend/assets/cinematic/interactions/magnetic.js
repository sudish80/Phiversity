/* PHV interactions: magnetic buttons — restrained pull toward the
   pointer, elastic release. Fine pointers only. */
(function () {
  'use strict';
  var PHV = window.PHV = window.PHV || {};
  var gsap = window.gsap;

  function init() {
    if (PHV.env.touch() || !PHV.env.finePointer() || PHV.env.reduced() || !gsap) return;

    var R = 110, MAX = 7;
    var items = [].map.call(document.querySelectorAll('.btn, nav .act a'), function (btn) {
      return { btn: btn, qx: null, qy: null };
    });

    function onMove(e) {
      for (var i = 0; i < items.length; i++) {
        var it = items[i];
        var r = it.btn.getBoundingClientRect();
        var cx = r.left + r.width / 2, cy = r.top + r.height / 2;
        var dx = e.clientX - cx, dy = e.clientY - cy;
        var d = Math.hypot(dx, dy);
        if (d < R) {
          if (!it.qx) {
            it.qx = gsap.quickTo(it.btn, 'x', { duration: 0.35, ease: 'power2.out' });
            it.qy = gsap.quickTo(it.btn, 'y', { duration: 0.35, ease: 'power2.out' });
          }
          var pull = (1 - d / R) * MAX;
          var inv = d > 0.001 ? 1 / d : 0;
          it.qx(dx * inv * pull);
          it.qy(dy * inv * pull);
        } else if (it.qx) {
          it.qx(0); it.qy(0);
        }
      }
    }
    document.addEventListener('pointermove', onMove, { passive: true });
  }

  PHV.magnetic = { init: init };
})();
