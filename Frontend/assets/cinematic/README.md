# Phiversity Cinematic Experience

The homepage (`Frontend/index.html`) opens with a directed, code-only
motion experience: a cinematic intro, a custom cursor, a scroll-driven
journey through the four disciplines, and a product-flow demo — built
with **Three.js**, **GSAP + ScrollTrigger**, custom **GLSL shaders**,
**SVG** and plain HTML/CSS. No video, no pre-rendered assets.

## Run it

```bash
# from the repository root
cd phiversity
python3 -m phiversity.server --root ..
# open http://127.0.0.1:8787/
```

Any static file server works the same way — the experience is pure
frontend. Libraries are vendored under `assets/vendor/` (offline-safe).

## The experience

| Moment | What happens |
|---|---|
| **Intro** (~10 s, skippable) | Black void → grid + particles emerge → a luminous cursor drifts to an object (glow + ripple) → it clicks the φ symbol → the symbol opens, the camera accelerates through it → equations, constellation lines and the 3D φ mark materialize → `PHIVERSITY / Understand Everything.` with a light sweep → the camera zooms **into** the logo as it scales into the site |
| **Hero** | “Understand Everything.” rises word by word over a live 3D field: perspective grid, floating math glyphs (hover them — the cursor shows what they are), wireframe sphere, parallax |
| **The Question** | “Every great discovery begins with a question.” — camera glides forward |
| **The Journey** (sticky, ~4 viewports) | One continuous camera flight: **Mathematics** (curve draws itself, then morphs sine → Gaussian) → **Physics** (wave surface, vectors, gyroscope) → **Chemistry** (benzene assembles atom by atom, bonds grow, rotates) → **Economics** (supply/demand draw, equilibrium lights up) |
| **Product demo** | The real pipeline as an animated mock: question typed → structured steps → live graph draws with tangent sweep → 3D visualization spins up → Understanding |
| **Finale** | Camera pulls back; particles converge into the glowing φ mark. “Your next breakthrough starts here.” |

The intro plays once per browser session; the footer link
(*Replay intro*) resets it. **Esc** or the *Skip intro* button exits
immediately.

## Architecture

```
assets/cinematic/
  cinematic.css            all cinematic-layer styles + reduced-motion rules
  boot.js                  orchestrator: legacy behavior, fonts gate,
                           intro → reveal → story → interactions
  core/
    env.js                 device/quality detection, math utilities
    shaders.js             GLSL: particles (wrap + rush + converge),
                           grid (flow + interaction pulse), ripples, glow, wave
    geometry.js            procedural builders (phi object, molecule,
                           curves with draw-progress, grid, fields)
    symbols.js             canvas-texture equation/glyph sprites
    stage.js              one WebGLRenderer + RAF manager; DPR-adaptive,
                           pauses when hidden, full dispose (no leaks)
    rig.js                 GSAP camera rig (poses, CatmullRom paths, parallax)
  intro/intro.js           phases A–D + zoom-to-website timeline
  interactions/
    cursor.js              custom cursor: default/hover/click/text/3D-label
                           states; pointer-events: none (never blocks input);
                           Esc restores the system cursor; touch = off
    magnetic.js            restrained magnetic pull for buttons
  scenes/
    story-scene.js         the persistent 3D world + camera choreography
    story-timeline.js      ScrollTrigger segments, caption crossfades,
                           renderer run/pause economy
    product.js             the QUESTION→EXPLANATION→VISUALIZATION timeline
```

Camera work is a set of **scroll segments** (`toQuestion`, `toJourney`,
`journey`, `toProduct`, `toFinale`) whose poses line up at the seams,
so scrolling produces one continuous flight. One fixed WebGL canvas
(`#phv-story`) lives behind the whole page; it **pauses** while the
opaque product/pricing sections cover it.

## Customization

- **Brand colors** — `--phv-vio` / `--phv-blu` in `cinematic.css`; 3D
  accent colors live next to the geometry builders.
- **Logo** — the φ mark is inline SVG (`index.html`, gradient ids
  `phvgi/phvgn/phvgf`) plus `PHV.geo.makePhi()` for the 3D version.
  Replace both when an official logo exists.
- **Timing / copy** — all intro beats are labeled positions in one GSAP
  timeline (`intro/intro.js`); section copy is plain HTML.
- **Intro length** — roughly 10 s; shorten by cutting the `hold` and
  scaling the position parameters (they are absolute seconds).
- **Particle counts / quality** — derived from `PHV.env.quality()`
  (desktop / tablet / phone) in `core/env.js`.

## Accessibility & performance

- `prefers-reduced-motion`: the intro never starts, scroll choreography
  is disabled, every section renders statically with full contrast.
- No WebGL: the page falls back to a CSS grid backdrop
  (`html.phv-nowebgl`).
- The cinematic cursor is a visual layer only (`pointer-events: none`);
  it never hijacks clicks, selection, or keyboard navigation, and it is
  disabled on touch devices.
- Pixel ratio is capped (2 desktop / 1.5 mobile), geometry and particle
  counts scale down on small screens, rendering pauses when the tab is
  hidden or the canvas is covered, and every scene disposes its GPU
  resources (the intro canvas is removed entirely after it plays —
  exactly one WebGL context remains during browsing).
- *Skip intro* is keyboard-reachable (`Esc`), focus styles are preserved
  everywhere, and the flow degrades to the normal site even if the
  animation bootstrap throws.
