/* PHV boot: orchestrates the full experience.
   1. legacy homepage behaviors (nav, pricing, notes)
   2. fonts ready → cinematic intro (skippable)
   3. reveal sequence → story world + scroll choreography
   4. cursor + magnetic interactions
   5. cleanup */
(function () {
  'use strict';
  var PHV = window.PHV = window.PHV || {};
  var gsap = window.gsap;

  /* ---------------- legacy homepage behaviors (preserved) ---------------- */
  function legacy() {
    var nv = document.getElementById('nv');
    if (nv) {
      var onScroll = function () { nv.classList.toggle('on', scrollY > 20); };
      addEventListener('scroll', onScroll, { passive: true });
      onScroll();
    }
    document.querySelectorAll('[data-na]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault();
        var note = document.getElementById('note');
        if (note) note.textContent = 'Sign-up and app routes are not connected in this preview.';
      });
    });
    var pr = document.getElementById('pr');
    if (pr) {
      pr.innerHTML = ['Free', 'Pro', 'Team'].map(function (n) {
        return '<div><h3>' + n + '</h3><p>Price and allowance load from plan configuration.</p>' +
          '<a class="btn sec" href="app/billing/plans.html">Choose ' + n + '</a></div>';
      }).join('');
    }
  }

  /* ---------------- hero entrance after the intro ---------------- */
  function heroEntrance(instant) {
    var words = document.querySelectorAll('#hero h1 .w > span');
    var lead = document.querySelector('#hero .lead');
    var ctas = document.querySelectorAll('#hero .ctas .btn');
    var hint = document.querySelector('#hero .hint');
    if (!gsap || !words.length) {
      document.body.classList.add('phv-entered');
      return;
    }
    document.body.classList.add('phv-entered');
    if (instant || PHV.env.reduced()) return;
    /* CSS holds translateY(112%) pre-JS; normalize into GSAP's model so the
       rise actually animates (computed % becomes px, which would defeat a
       yPercent tween). */
    gsap.set(words, { yPercent: 112, y: 0 });
    var tl = gsap.timeline();
    tl.to(words, { yPercent: 0, duration: 0.9, ease: 'power3.out', stagger: 0.11 }, 0.05)
      .fromTo(lead, { opacity: 0, y: 22 }, { opacity: 1, y: 0, duration: 0.7, ease: 'power2.out' }, 0.45)
      .fromTo(ctas, { opacity: 0, y: 18 }, {
        opacity: 1, y: 0, duration: 0.6, ease: 'power2.out', stagger: 0.08, clearProps: 'transform'
      }, 0.62);
    if (hint) tl.fromTo(hint, { opacity: 0 }, { opacity: 1, duration: 0.8 }, 1.0);
  }

  function storyUp() {
    /* hint line grows once hero is in */
    var liney = document.querySelector('#hero .hint .liney');
    if (liney && gsap && !PHV.env.reduced()) {
      gsap.fromTo(liney, { scaleY: 0 }, { scaleY: 1, duration: 1.6, ease: 'power2.out', delay: 1.2 });
    }
  }

  /* ---------------- main flow ---------------- */
  var entered = false;
  function enterHero(instant) {
    if (entered) return;
    entered = true;
    heroEntrance(instant);
  }

  function main() {
    legacy();

    var willPlayIntro = !(PHV.env.reduced() || !PHV.env.hasWebGL() || !window.THREE || !gsap) && !PHV.intro.seen();
    if (willPlayIntro) {
      try { history.scrollRestoration = 'manual'; } catch (e) { }
      window.scrollTo(0, 0);
    }

    var fontsReady = (document.fonts && document.fonts.ready) ? document.fonts.ready : Promise.resolve();
    var guard = new Promise(function (r) { setTimeout(r, 2200); });
    Promise.race([fontsReady, guard])
      .then(function () {
        /* revealHook fires mid-zoom so the hero rises as the overlay fades */
        return PHV.intro.run(function () { enterHero(false); });
      })
      .then(function () {
        document.body.classList.remove('phv-intro-lock');
        enterHero(false); /* no-op when the intro already revealed it */
        storyUp();

        /* persistent story world */
        var story = null;
        var storyHost = document.getElementById('phv-story');
        if (window.THREE && gsap && !PHV.env.reduced() && PHV.env.hasWebGL() && storyHost) {
          try { story = PHV.storyScene.build(); } catch (e) { story = null; }
        }
        if (story) {
          if (PHV.storyTimeline) PHV.storyTimeline.init(story);
          storyHost.classList.add('on'); /* CSS fade-in — no pop */
          PHV._story = story; /* exposed for deterministic capture */
          addEventListener('pagehide', function () { story.dispose(); }, { once: true });
        } else {
          document.documentElement.classList.add('phv-nowebgl');
        }

        /* interactions */
        if (PHV.cursor && PHV.cursor.init()) {
          setTimeout(function () { PHV.cursor.show(); }, 500);
        }
        if (PHV.magnetic) PHV.magnetic.init();

        /* replay control */
        var replay = document.getElementById('phv-replay');
        if (replay) {
          replay.addEventListener('click', function (e) {
            e.preventDefault();
            PHV.intro.reset();
            location.reload();
          });
        }
      }).catch(function () {
        /* never leave the visitor locked out */
        document.body.classList.remove('phv-intro-lock');
        enterHero(true);
        document.documentElement.classList.add('phv-nowebgl');
        document.getElementById('phv-intro') &&
          (document.getElementById('phv-intro').style.display = 'none');
      });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', main);
  } else {
    main();
  }
})();
