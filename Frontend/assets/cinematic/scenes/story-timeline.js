/* PHV scenes: scroll-driven choreography — one ScrollTrigger per
   camera segment writes into story.state; DOM captions, reveals and
   renderer run/pause management live here. */
(function () {
  'use strict';
  var PHV = window.PHV = window.PHV || {};
  var gsap = window.gsap;
  var ScrollTrigger = window.ScrollTrigger;

  function init(story) {
    if (!gsap || !ScrollTrigger || !story) return;
    if (PHV.env.reduced()) return; /* static page, no scroll choreography */
    gsap.registerPlugin(ScrollTrigger);
    var st = story.state;

    /* ---------- renderer economy: pause when 3D is hidden ---------- */
    var productActive = false, belowActive = false, finaleActive = false;
    function resolveRun() {
      var run = !belowActive && !(productActive && !finaleActive);
      if (run) story.stage.start(); else story.stage.pause();
      var host = document.getElementById('phv-story');
      if (host) host.classList.toggle('dim', belowActive);
    }

    /* ---------- hero → question ---------- */
    ScrollTrigger.create({
      trigger: '#question', start: 'top 95%', end: 'top 25%',
      scrub: 0.5,
      onUpdate: function (self) {
        if (self.isActive) { st.seg = 'toQuestion'; st.segT = self.progress; }
      }
    });

    /* ---------- question headline reveal ---------- */
    gsap.from('#question .qline', {
      y: 74, opacity: 0, stagger: 0.14, ease: 'power3.out', duration: 0.9,
      scrollTrigger: { trigger: '#question', start: 'top 62%', toggleActions: 'play none none reverse' }
    });
    gsap.to('#question .qmark', {
      opacity: 1, duration: 1.1,
      scrollTrigger: { trigger: '#question', start: 'top 40%', toggleActions: 'play none none reverse' }
    });

    /* ---------- question → journey entry ---------- */
    ScrollTrigger.create({
      trigger: '#journey', start: 'top 95%', end: 'top top',
      scrub: 0.5,
      onUpdate: function (self) {
        if (self.isActive) { st.seg = 'toJourney'; st.segT = self.progress; }
      }
    });

    /* ---------- the journey (sticky scrub) ---------- */
    var caps = document.querySelectorAll('#journey .cap');
    var railDots = document.querySelectorAll('#journey .rail i');
    var domTabs = document.querySelectorAll('#journey .domains span');

    var capTl = gsap.timeline({
      scrollTrigger: {
        trigger: '#journey', start: 'top top', end: 'bottom bottom', scrub: 0.6,
        onUpdate: function (self) {
          st.seg = 'journey';
          st.J = self.progress;
          var idx = Math.min(3, Math.floor(self.progress * 4 + 0.18));
          railDots.forEach(function (d, i) { d.classList.toggle('on', i === idx); });
          domTabs.forEach(function (d, i) { d.classList.toggle('on', i === idx); });
        }
      }
    });
    /* caption crossfades across the journey (timeline duration = 1) */
    capTl.fromTo(caps[0], { opacity: 0, y: 34 }, { opacity: 1, y: 0, duration: 0.05 }, 0.0)
      .to(caps[0], { opacity: 0, y: -28, duration: 0.045 }, 0.2)
      .fromTo(caps[1], { opacity: 0, y: 34 }, { opacity: 1, y: 0, duration: 0.05 }, 0.28)
      .to(caps[1], { opacity: 0, y: -28, duration: 0.045 }, 0.47)
      .fromTo(caps[2], { opacity: 0, y: 34 }, { opacity: 1, y: 0, duration: 0.05 }, 0.55)
      .to(caps[2], { opacity: 0, y: -28, duration: 0.045 }, 0.73)
      .fromTo(caps[3], { opacity: 0, y: 34 }, { opacity: 1, y: 0, duration: 0.05 }, 0.81);

    /* ---------- journey → product ---------- */
    ScrollTrigger.create({
      trigger: '#product', start: 'top 95%', end: 'top 30%',
      scrub: 0.5,
      onUpdate: function (self) {
        if (self.isActive) { st.seg = 'toProduct'; st.segT = self.progress; }
      }
    });
    ScrollTrigger.create({
      trigger: '#product', start: 'top 30%', end: 'bottom top',
      onToggle: function (self) { productActive = self.isActive; if (self.isActive) st.seg = 'product'; resolveRun(); }
    });

    /* ---------- product demo plays on entry ---------- */
    if (PHV.product) {
      var demoTl = PHV.product.buildTimeline();
      if (demoTl) {
        ScrollTrigger.create({
          trigger: '.phv-app', start: 'top 62%',
          onEnter: function () { demoTl.restart(); },
          onEnterBack: function () { demoTl.restart(); }
        });
      }
    }
    gsap.from('.phv-app', {
      y: 60, opacity: 0, duration: 1.0, ease: 'power3.out',
      scrollTrigger: { trigger: '#product', start: 'top 70%', toggleActions: 'play none none reverse' }
    });

    /* ---------- product → finale ---------- */
    ScrollTrigger.create({
      trigger: '#finale', start: 'top 92%', end: 'top 12%',
      scrub: 0.5,
      onUpdate: function (self) {
        if (self.isActive) { st.seg = 'toFinale'; st.segT = self.progress; }
      }
    });
    ScrollTrigger.create({
      trigger: '#finale', start: 'top 12%', end: 'bottom top',
      onToggle: function (self) {
        finaleActive = self.isActive;
        if (self.isActive) {
          st.seg = 'finale';
          story.gridPulse();
        }
        resolveRun();
      }
    });

    /* ---------- finale text ---------- */
    gsap.from('#finale .fline', {
      y: 60, opacity: 0, stagger: 0.12, ease: 'power3.out', duration: 0.85,
      scrollTrigger: { trigger: '#finale', start: 'top 55%', toggleActions: 'play none none reverse' }
    });
    gsap.from('#finale .btn', {
      y: 26, opacity: 0, duration: 0.7, ease: 'power2.out', delay: 0.3,
      scrollTrigger: { trigger: '#finale', start: 'top 45%', toggleActions: 'play none none reverse' }
    });

    /* ---------- below the finale: dim + rest ---------- */
    ScrollTrigger.create({
      trigger: '#pricing', start: 'top 85%',
      onToggle: function (self) { belowActive = self.isActive; resolveRun(); }
    });

    resolveRun();
  }

  PHV.storyTimeline = { init: init };
})();
