# PHIVERSITY AD ENGINE — MASTER BUILD PROMPT

s
> It is written as a complete, self-contained specification. Read it fully before writing any code.
> Work phase by phase. Do not skip the acceptance checks. Do not invent facts about the product.

---

## TABLE OF CONTENTS

1. Role and mission
2. Product context (what Phiversity is, and what you may and may not claim)
3. What "code-to-video" means here
4. The ad format: random story, then Phiversity
5. Hard constraints and non-goals
6. Definitions and vocabulary
7. Repository layout
8. Tech stack, versions and tooling
9. Configuration files
10. CLI specification
11. The Video Spec (data contract)
12. Brand system and design tokens
13. Scene catalog
14. Deterministic timeline runtime
15. Video-slot scene (embedding rendered Manim videos)
16. Capture pipeline (Playwright)
17. Encoding pipeline (FFmpeg)
18. Audio: narration, music, sound effects, captions
19. Story engine (the "random story" generator)
20. Variation engine and posting cadence
21. Platform export specs
22. Cloud execution (Azure-first) and local-only mode
23. Quality assurance and testing
24. Accessibility, safety and content rules
25. Phased delivery plan
26. Acceptance checklist
27. Appendices (full examples)

---

## 1. ROLE AND MISSION

You are a senior creative engineer. You combine three skills:

- Motion design: you think in timing, easing, hierarchy, rhythm and restraint.
- Front-end engineering: you write clean TypeScript, HTML, CSS and GSAP.
- Video pipeline engineering: you can turn a browser animation into a frame-exact MP4.

Your mission is to build the **Phiversity Ad Engine**: a command-line tool and library that
produces short vertical marketing videos for Phiversity. Every video is authored as a web page
(HTML, CSS, SVG and GSAP), driven by a JSON spec, captured frame by frame, and encoded with FFmpeg.

The engine must be able to produce many different ads from many different specs, with no manual
editing. One command in, one finished MP4 out.

### 1.1 Why this approach

- HTML, CSS and GSAP give crisp vector type, perfect easing control and easy theming.
- A JSON spec makes every video reproducible, diffable and automatable.
- Capturing frames deterministically means the result is identical on every machine.
- Phiversity already renders educational videos (Manim). The engine must reuse those renders
  inside the ads, so the ad shows the real product, not a mock-up.

### 1.2 The reference ad you are generalizing

A 29-second, 9:16 reference ad already exists as a single HTML file. Its structure is:

1. Story scene: a student at 11:47 pm with a physics exam at nine.
2. Textbook scene: the equation s = ut + ½at² sits as dead ink.
3. Turn scene: the ink becomes a distance-time curve and a falling ball.
4. Product scene: "Type a topic. Phiversity makes the narrated animation." A frame plays
   rendered Phiversity videos. Subject chips: Physics, Chemistry, Math, Economics.
5. Close scene: the Phiversity mark, "Learn it by watching it.", "Coming soon".

Your job is to turn that one hand-built ad into a **system** that can produce hundreds of
variations with different stories, different subjects and different rendered clips.

### 1.3 Definition of done (summary)

- `phiad build specs/example-physics.json` writes `out/example-physics/final.mp4`.
- The MP4 is 1080x1920, 30 fps, H.264, yuv420p, AAC audio, under 50 MB, 15 to 45 seconds.
- Re-running the same command produces a byte-different file but a visually identical result.
- Frame hashes of golden frames match within tolerance (see section 23).
- The tool runs fully locally on a modest Windows PC and also inside a container in the cloud.

---

## 2. PRODUCT CONTEXT

### 2.1 What Phiversity is (facts you may rely on)

- Phiversity is an AI-driven educational video generation platform.
- It turns a topic into a narrated explainer animation.
- It uses Manim for the animation, LLM orchestration for planning, and text-to-speech for narration.
- It supports subject packs. Known subjects: physics, chemistry, math, economics.
- It is a SaaS product and is complete.
- It is in a pre-launch phase. The public message is "Coming soon".
- Launch marketing is free marketing across social platforms, posting many short videos.
- Marketing is run by an automation agent (Hermes Agent) that calls cloud APIs only.
- The owner is a solo developer. Budget is small. The cloud budget is a student credit.

### 2.2 What you must NOT claim

Never put any of the following in an ad unless the owner explicitly adds it to the spec:

- A website URL, domain name, app store link or handle that was not supplied.
- Prices, free-trial lengths, plan names or discounts.
- User counts, ratings, testimonials, awards, press quotes or "trusted by" claims.
- Speed promises such as "in 60 seconds" or "in minutes".
- Accuracy promises such as "always correct" or "exam-proof".
- Claims that a named university, board or exam body endorses the product.
- Claims that the product replaces teachers.

If a spec contains a claim from the list above, the validator must **warn** and require
`"claimsApproved": true` in the spec before building.

### 2.3 What you may say safely

- "Type a topic. Get a narrated animation."
- "Learn it by watching it."
- "Coming soon."
- Subject names that the product really supports.
- Descriptions of what is visible on screen, for example "a ball falling as the graph draws".

### 2.4 Audience

- Primary: students in secondary school and early university, especially science and math.
- Secondary: teachers and tutors who explain concepts to others.
- Region: global English first, with Nepal as a home market. Nepali captions are a later phase.
- Viewing context: phone, vertical, sound often off. Every ad must work muted.

### 2.5 Brand voice

- Plain, warm, specific.
- Short sentences. Active voice. Sentence case.
- No hype words: revolutionary, game-changing, cutting-edge, unlock, supercharge.
- No fake urgency.
- No emoji in on-screen text.
- A story beat should feel true to a real student, not like an advertisement.

---

## 3. WHAT "CODE-TO-VIDEO" MEANS HERE

Code-to-video means the video is a program, not a timeline in an editor.

### 3.1 The mental model

```
Spec (JSON)  ->  Scene modules (TS)  ->  Master GSAP timeline (paused)
     ->  seek(t) for every frame  ->  screenshot  ->  FFmpeg  ->  MP4
```

### 3.2 Principles

1. **Determinism.** Given the same spec and assets, every frame at time t is identical.
2. **Seekability.** Nothing depends on wall-clock time. Everything is driven by `seek(t)`.
3. **No hidden state.** No `Math.random()` without a seeded generator. No `Date.now()`.
4. **Separation.** Content lives in the spec. Look lives in tokens. Motion lives in scene modules.
5. **Composable.** A scene is a pure function from props to a GSAP timeline fragment.
6. **Observable.** The engine logs a timeline report so a human can see what happens when.

### 3.3 What you must avoid

- `setTimeout`, `setInterval`, `requestAnimationFrame` loops that advance state.
- CSS keyframe animations and CSS transitions inside scenes. (They run on the wall clock and
  cannot be seeked reliably.) Use GSAP only. The one exception is a `.static` decorative class
  that is never animated.
- Autoplaying `<video>` elements during capture. Videos are seeked, never played.
- Network requests during capture. All assets are local files.
- Web fonts loaded from the network at capture time. Fonts are bundled locally.

---

## 4. THE AD FORMAT: RANDOM STORY, THEN PHIVERSITY

### 4.1 The structure

Every ad follows a five-beat arc. Beats can be longer or shorter, but the order is fixed.

| Beat | Name | Purpose | Typical length |
|------|------|---------|----------------|
| 1 | Hook | A specific human moment in the first 2 seconds | 3 to 6 s |
| 2 | Friction | The problem: static explanation, dead ink, confusion | 3 to 5 s |
| 3 | Turn | The moment the idea starts moving | 4 to 7 s |
| 4 | Product | Show real Phiversity output | 5 to 9 s |
| 5 | Close | Mark, tagline, status line | 4 to 6 s |

### 4.2 The hook rule

The first frame must already contain something readable and human. No logo-first openings.
No blank screens. No fade-from-black longer than 0.2 seconds. The viewer decides in under two
seconds, so a clock, a name, a number or a question must be on screen by frame 6.

### 4.3 The "random story" rule

The story in beat 1 should be a small, true-feeling scene, not a pitch. Examples of shapes:

- A time and a deadline: "11:47 pm. Exam at nine."
- A question a student really asks: "Why does the moon not fall down?"
- A small failure: "Third time reading this paragraph."
- A teacher moment: "She drew it on the board. It didn't move."
- A curiosity: "A ball and a feather fall together on the moon."

The story must connect to the product through the **turn**: the exact thing that was static
in the story becomes animated in beat 3, and that animation is of the same kind Phiversity makes.

### 4.4 Connection rule

Beat 3 and beat 4 must share a visual element. In the reference ad the equation becomes a curve
and the curve is the same kind of object that appears in the product clips. Your scenes must
make it easy to carry one element across beats (see "shared elements" in section 14).

### 4.5 Length budget

| Total | Use |
|-------|-----|
| 15 to 20 s | Reels/Shorts quick hooks |
| 25 to 32 s | Default ad |
| 35 to 45 s | Story-heavy ad with narration |

The validator rejects specs under 12 s or over 60 s.

---

## 5. HARD CONSTRAINTS AND NON-GOALS

### 5.1 Hard constraints

- Language: TypeScript for all engine code. Strict mode on.
- Runtime: Node.js 20 or newer. No Python in the core path.
- Animation: GSAP 3.12.x only. No other animation library in scenes.
- Capture: Playwright with Chromium.
- Encode: FFmpeg (system binary or `ffmpeg-static` fallback).
- No paid APIs required for the core build. TTS and LLM calls are optional adapters.
- Windows 10/11 must work. Use `path.join`, never hard-coded slashes. No bash-only scripts.
- The machine may have 4 GB RAM. Capture must stream frames to disk, never hold all in memory.
- No telemetry. No network calls except explicit adapters.
- All user-visible strings come from the spec or from a copy table. None are hard-coded in scenes.

### 5.2 Non-goals

- Not a general video editor. No GUI timeline.
- Not a replacement for Manim. Manim stays the product renderer; this engine makes ads.
- No 3D engine in v1. (Three.js scene type is a documented extension point only.)
- No live streaming.
- No real-time preview server with hot reload in v1. A simple `phiad preview` page is enough.

### 5.3 Style constraints for code

- Small modules. No file over 400 lines.
- Pure functions where possible.
- Every exported function has a TSDoc comment.
- No `any`. Use `unknown` and narrow.
- Errors carry a code and a human sentence: `E_SPEC_001: scene "s3" overlaps "s4" by 0.4 s`.
- Every scene has a unit test and a golden-frame test.

---

## 6. DEFINITIONS AND VOCABULARY

Use these words consistently in code, comments and logs.

- **Spec**: the JSON file describing one ad.
- **Beat**: one of the five narrative parts (hook, friction, turn, product, close).
- **Scene**: a module that builds a timeline fragment and a DOM subtree for one part of a beat.
- **Layer**: a z-ordered container inside the stage (background, content, overlay, captions, UI).
- **Stage**: the fixed 1080x1920 logical canvas, scaled to the output size.
- **Master timeline**: the single paused GSAP timeline containing all scene fragments.
- **Seek**: setting the master timeline to an exact time and waiting until the DOM is settled.
- **Clip**: a rendered Phiversity video file used inside the product scene.
- **Slot**: a rectangle in a scene where a clip plays.
- **Shared element**: a DOM node that persists across scenes and is re-parented or morphed.
- **Token**: a named design value (color, size, easing, duration).
- **Golden frame**: a stored reference PNG for a given spec at a given time.
- **Cue**: a timestamp in a spec that audio or captions attach to.
- **Safe zone**: the region of the frame not covered by platform UI.
- **Run**: one execution of `phiad build`, with its own output folder and log.

---
## 7. REPOSITORY LAYOUT

Create exactly this structure. Do not add top-level folders without a reason written in `docs/DECISIONS.md`.

```
phiversity-ad-engine/
├─ package.json
├─ tsconfig.json
├─ tsconfig.build.json
├─ eslint.config.js
├─ .prettierrc
├─ .gitignore
├─ .env.example
├─ README.md
├─ docs/
│  ├─ DECISIONS.md          # every non-obvious choice, one paragraph each
│  ├─ SCENES.md             # generated from the scene registry
│  ├─ SPEC.md               # generated from the schema
│  └─ RUNBOOK.md            # how to run locally and in the cloud
├─ assets/
│  ├─ fonts/                # bundled .woff2 files (no network at capture time)
│  ├─ brand/                # logo svg, phi mark svg
│  ├─ clips/                # rendered Phiversity videos (mp4, 16:9 or 9:16)
│  ├─ clips.index.json      # metadata for every clip (subject, topic, duration, tags)
│  ├─ music/                # royalty-free or self-made loops (wav/mp3)
│  └─ sfx/                  # tick, whoosh, pop, chime (wav)
├─ specs/
│  ├─ example-physics.json
│  ├─ example-chemistry.json
│  ├─ example-math.json
│  ├─ example-economics.json
│  └─ schema/
│     ├─ spec.schema.json   # generated from zod
│     └─ clips.schema.json
├─ src/
│  ├─ cli/
│  │  ├─ index.ts           # command router
│  │  ├─ build.ts
│  │  ├─ preview.ts
│  │  ├─ validate.ts
│  │  ├─ batch.ts
│  │  ├─ story.ts
│  │  ├─ clips.ts
│  │  └─ doctor.ts
│  ├─ spec/
│  │  ├─ schema.ts          # zod schemas, single source of truth
│  │  ├─ load.ts
│  │  ├─ validate.ts        # semantic checks beyond the schema
│  │  ├─ claims.ts          # forbidden-claim scanner
│  │  └─ normalize.ts       # fill defaults, compute absolute times
│  ├─ tokens/
│  │  ├─ colors.ts
│  │  ├─ type.ts
│  │  ├─ motion.ts          # easings, durations
│  │  ├─ layout.ts          # safe zones, grid
│  │  └─ index.ts
│  ├─ runtime/              # runs INSIDE the browser page
│  │  ├─ main.ts            # entry, exposes window.__phiad
│  │  ├─ stage.ts
│  │  ├─ timeline.ts
│  │  ├─ registry.ts
│  │  ├─ shared.ts          # shared-element helpers
│  │  ├─ rng.ts             # seeded random
│  │  ├─ text.ts            # split, measure, fit
│  │  ├─ svg.ts             # path helpers
│  │  ├─ media.ts           # video slot seeking
│  │  ├─ captions.ts
│  │  └─ debug.ts           # timeline overlay for preview only
│  ├─ scenes/
│  │  ├─ story-clock.ts
│  │  ├─ story-line.ts
│  │  ├─ story-question.ts
│  │  ├─ dead-ink.ts
│  │  ├─ equation-morph.ts
│  │  ├─ graph-draw.ts
│  │  ├─ ball-fall.ts
│  │  ├─ orbit.ts
│  │  ├─ wave.ts
│  │  ├─ bar-grow.ts
│  │  ├─ molecule.ts
│  │  ├─ video-slot.ts
│  │  ├─ subject-chips.ts
│  │  ├─ typed-prompt.ts
│  │  ├─ cta-close.ts
│  │  └─ index.ts
│  ├─ page/
│  │  ├─ template.html      # shell with #stage and layers
│  │  └─ base.css           # reset, stage sizing, layer rules
│  ├─ capture/
│  │  ├─ browser.ts
│  │  ├─ frames.ts
│  │  ├─ workers.ts
│  │  ├─ preextract.ts      # FFmpeg frame extraction for clips
│  │  └─ verify.ts
│  ├─ encode/
│  │  ├─ ffmpeg.ts
│  │  ├─ presets.ts
│  │  ├─ audio.ts
│  │  ├─ captions-burn.ts
│  │  └─ probe.ts
│  ├─ audio/
│  │  ├─ tts.ts             # adapter interface + implementations
│  │  ├─ cues.ts
│  │  ├─ mix.ts
│  │  └─ loudness.ts
│  ├─ story/
│  │  ├─ bank.ts
│  │  ├─ generate.ts        # LLM adapter (optional)
│  │  ├─ prompts.ts
│  │  └─ lint.ts
│  ├─ variation/
│  │  ├─ plan.ts
│  │  ├─ hooks.ts
│  │  └─ schedule.ts
│  ├─ cloud/
│  │  ├─ job.ts
│  │  ├─ blob.ts
│  │  └─ queue.ts
│  └─ util/
│     ├─ log.ts
│     ├─ errors.ts
│     ├─ fs.ts
│     ├─ hash.ts
│     └─ time.ts
├─ tests/
│  ├─ unit/
│  ├─ golden/               # reference PNGs per spec per time
│  └─ e2e/
├─ docker/
│  └─ Dockerfile
└─ out/                     # build output, git-ignored
```

### 7.1 Output folder per run

```
out/<spec-id>/
├─ spec.resolved.json       # the spec after normalize(), with absolute times
├─ timeline.report.txt      # human-readable list of tweens and times
├─ frames/                  # PNG or JPEG frames (deleted after encode unless --keep-frames)
├─ audio/
│  ├─ narration.wav
│  ├─ music.wav
│  ├─ sfx.wav
│  └─ mix.wav
├─ captions.srt
├─ captions.vtt
├─ video.silent.mp4
├─ final.mp4
├─ thumbnail.png
├─ meta.json                # title, description, hashtags, alt text, durations
└─ build.log
```

---

## 8. TECH STACK, VERSIONS AND TOOLING

### 8.1 Dependencies

| Package | Version range | Role |
|---------|---------------|------|
| typescript | ^5.5 | language |
| tsx | ^4 | run TS in dev |
| esbuild | ^0.23 | bundle runtime into one browser script |
| gsap | 3.12.5 (exact) | animation |
| playwright | ^1.47 | capture |
| zod | ^3.23 | spec schema |
| zod-to-json-schema | ^3.23 | publish JSON schema |
| commander | ^12 | CLI |
| pino | ^9 | structured logging |
| pino-pretty | ^11 | dev logs |
| execa | ^9 | run FFmpeg and ffprobe |
| fast-glob | ^3 | file discovery |
| sharp | ^0.33 | thumbnails, frame hashing |
| pixelmatch | ^6 | golden frame comparison |
| pngjs | ^7 | PNG decode for pixelmatch |
| vitest | ^2 | tests |
| ffmpeg-static | ^5 | fallback FFmpeg binary |
| ffprobe-static | ^3 | fallback ffprobe |

Pin GSAP exactly. Pin Playwright's browser revision in `docs/DECISIONS.md`.

### 8.2 Do not add

- Remotion, Motion Canvas, Theatre.js, p5.js: they are separate engines in the wider Phiversity
  plan. This engine is the GSAP engine. Keep the interface (spec in, MP4 out) compatible so the
  other engines can be swapped in later.
- Any CSS framework. Tailwind, Bootstrap and similar are forbidden in the runtime page.
- Any UI component library.

### 8.3 Scripts in package.json

```json
{
  "name": "phiversity-ad-engine",
  "version": "0.1.0",
  "type": "module",
  "bin": { "phiad": "dist/cli/index.js" },
  "scripts": {
    "dev": "tsx src/cli/index.ts",
    "build:runtime": "node scripts/build-runtime.mjs",
    "build": "tsc -p tsconfig.build.json && npm run build:runtime",
    "test": "vitest run",
    "test:golden": "vitest run tests/golden",
    "lint": "eslint src tests",
    "format": "prettier --write .",
    "schema": "tsx scripts/emit-schema.ts",
    "docs": "tsx scripts/emit-docs.ts",
    "doctor": "tsx src/cli/index.ts doctor"
  }
}
```

### 8.4 tsconfig essentials

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "Bundler",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noImplicitOverride": true,
    "exactOptionalPropertyTypes": true,
    "noFallthroughCasesInSwitch": true,
    "skipLibCheck": true,
    "lib": ["ES2022", "DOM"],
    "outDir": "dist",
    "rootDir": "src",
    "sourceMap": true,
    "resolveJsonModule": true
  },
  "include": ["src"]
}
```

### 8.5 The runtime bundle

`src/runtime/**` and `src/scenes/**` run in the browser. Bundle them with esbuild into one
IIFE file `dist/runtime/phiad.runtime.js`. The page template inlines nothing; it loads that
file plus a local copy of GSAP from `node_modules/gsap/dist/gsap.min.js`. Both are served from
`file://` or a tiny local static server started by the capture step.

The bundle must not import Node modules. Keep a lint rule that fails the build if
`src/runtime` or `src/scenes` import `fs`, `path`, `os`, `child_process` or anything from `node:`.

---

## 9. CONFIGURATION FILES

### 9.1 `phiad.config.json` (project defaults)

```json
{
  "output": { "dir": "out", "keepFrames": false },
  "video": { "width": 1080, "height": 1920, "fps": 30 },
  "capture": {
    "format": "jpeg",
    "jpegQuality": 92,
    "workers": 2,
    "deviceScaleFactor": 1,
    "timeoutMsPerFrame": 20000
  },
  "encode": { "preset": "slow", "crf": 18, "pixFmt": "yuv420p", "maxMB": 50 },
  "audio": { "enabled": true, "targetLufs": -14, "truePeakDb": -1.5, "sampleRate": 48000 },
  "paths": {
    "fonts": "assets/fonts",
    "clips": "assets/clips",
    "clipsIndex": "assets/clips.index.json",
    "music": "assets/music",
    "sfx": "assets/sfx"
  },
  "cloud": { "enabled": false },
  "tts": { "provider": "none" },
  "llm": { "provider": "none" }
}
```

### 9.2 `.env.example`

```
# Only needed for optional adapters. Core build needs none of these.
GEMINI_API_KEY=
DEEPSEEK_API_KEY=
OPENROUTER_API_KEY=
NVIDIA_NIM_API_KEY=
AZURE_STORAGE_CONNECTION_STRING=
AZURE_SERVICE_BUS_CONNECTION_STRING=
PHIAD_FFMPEG_PATH=
PHIAD_FFPROBE_PATH=
PHIAD_CHROMIUM_PATH=
```

Never log secrets. Never write `.env` contents into `meta.json` or `build.log`.

### 9.3 Environment resolution order

1. CLI flag
2. Environment variable
3. `phiad.config.json`
4. Built-in default

Log the resolved value and its source for every setting at the start of a run, at debug level.

---

## 10. CLI SPECIFICATION

Binary name: `phiad`. Use commander. Every command supports `--json` (machine output) and
`--verbose`. Exit codes: 0 success, 1 user error (bad spec), 2 environment error, 3 build failure.

### 10.1 `phiad doctor`

Checks and prints a table:

- Node version >= 20
- FFmpeg found, version, has libx264 and aac encoders
- ffprobe found
- Chromium launchable via Playwright
- Fonts present in `assets/fonts`
- GSAP file present
- Free disk space >= 5 GB in the output drive
- Free RAM, warns below 2 GB
- Writable output directory

Each check returns pass, warn or fail with a one-line fix hint.

### 10.2 `phiad validate <spec>`

- Parses with zod.
- Runs semantic checks (section 11.6).
- Runs the forbidden-claim scanner.
- Prints a timeline table (scene, start, end, duration).
- Exit code 1 on any error. Warnings do not fail unless `--strict`.

### 10.3 `phiad preview <spec>`

- Builds the runtime bundle if stale.
- Starts a local static server on a random free port.
- Opens the page with `?spec=<path>&debug=1`.
- The debug overlay shows current time, active scene and a scrub slider.
- Playing in preview uses `timeline.play()`. This is the only place wall-clock playback is allowed.

### 10.4 `phiad build <spec>`

Flags:

- `--out <dir>`
- `--fps <n>`
- `--size <WxH>`
- `--preset <name>` (reels, tiktok, shorts, x, linkedin, square, landscape)
- `--no-audio`
- `--tts <provider>`
- `--keep-frames`
- `--workers <n>`
- `--range <start:end>` (seconds, for quick checks)
- `--seed <int>`
- `--dry-run` (validate and print the plan, no capture)

Pipeline:

1. load -> validate -> normalize
2. resolve clips and pre-extract frames if needed
3. generate or load audio, compute cues
4. bundle runtime if stale
5. capture frames
6. encode silent video
7. mix audio and mux
8. burn captions if requested
9. thumbnail
10. meta.json
11. verify with ffprobe and write the report

### 10.5 `phiad batch <folder|list.json>`

- Builds many specs with a concurrency limit.
- Writes `out/batch-<timestamp>/summary.json` with one row per spec: status, duration, size, warnings.
- Continues on failure. Exits 3 if any failed.

### 10.6 `phiad story <command>`

- `phiad story list` prints the story bank.
- `phiad story make --subject physics --seed 12 --out specs/gen-12.json` generates a spec from a template.
- `phiad story lint <spec>` runs the story-quality checks from section 19.

### 10.7 `phiad clips <command>`

- `phiad clips scan` walks `assets/clips`, probes each file, and updates `clips.index.json`.
- `phiad clips find --subject physics --topic projectile` prints matches.
- `phiad clips verify` flags missing files, wrong codecs, and clips without a poster frame.

---
## 11. THE VIDEO SPEC (DATA CONTRACT)

The spec is the only input that describes an ad. It is JSON. It is validated by zod. The zod
schema in `src/spec/schema.ts` is the single source of truth. Generate `spec.schema.json` and
`docs/SPEC.md` from it. Never hand-edit the generated files.

### 11.1 Top-level shape

```ts
export const SpecSchema = z.object({
  version: z.literal(1),
  id: z.string().regex(/^[a-z0-9][a-z0-9-]{2,60}$/),
  title: z.string().min(3).max(100),
  locale: z.enum(["en", "ne"]).default("en"),
  seed: z.number().int().default(1),
  claimsApproved: z.boolean().default(false),
  video: VideoSchema.default({}),
  theme: ThemeSchema.default({}),
  story: StorySchema,
  beats: z.array(BeatSchema).min(5),
  product: ProductSchema,
  close: CloseSchema,
  audio: AudioSchema.default({}),
  captions: CaptionsSchema.default({}),
  meta: MetaSchema.default({}),
});
```

### 11.2 Sub-schemas

```ts
export const VideoSchema = z.object({
  width: z.number().int().default(1080),
  height: z.number().int().default(1920),
  fps: z.union([z.literal(24), z.literal(30), z.literal(60)]).default(30),
  background: z.enum(["chalkboard", "paper", "midnight"]).default("chalkboard"),
  grid: z.boolean().default(true),
});

export const ThemeSchema = z.object({
  accent: z.enum(["blue", "green", "yellow", "red"]).default("blue"),
  typeScale: z.enum(["compact", "normal", "large"]).default("normal"),
  motion: z.enum(["calm", "normal", "snappy"]).default("normal"),
});

export const StorySchema = z.object({
  kind: z.enum(["clock", "question", "failure", "teacher", "curiosity"]),
  lines: z.array(z.object({
    text: z.string().min(1).max(90),
    role: z.enum(["display", "body", "dim"]).default("body"),
  })).min(1).max(4),
  hero: z.object({
    text: z.string().max(24),            // "11:47 pm", "Why?", "3rd time"
    style: z.enum(["serif-large", "mono-clock", "handwritten"]).default("serif-large"),
  }),
  subject: z.enum(["physics", "chemistry", "math", "economics"]),
  topic: z.string().min(2).max(60),      // "projectile motion"
});

export const BeatSchema = z.object({
  id: z.enum(["hook", "friction", "turn", "product", "close"]),
  start: z.number().min(0).optional(),   // seconds; if omitted, computed
  duration: z.number().min(1.5).max(14),
  scenes: z.array(SceneRefSchema).min(1),
});

export const SceneRefSchema = z.object({
  type: SceneTypeEnum,                    // see section 13
  id: z.string().regex(/^[a-z0-9-]+$/),
  at: z.number().min(0).default(0),       // offset inside the beat
  duration: z.number().min(0.3).optional(),
  props: z.record(z.unknown()).default({}),   // validated per scene type
  shared: z.array(z.string()).default([]),    // shared element ids this scene uses
});

export const ProductSchema = z.object({
  headline: z.string().max(80),
  clips: z.array(ClipRefSchema).min(1).max(5),
  chips: z.array(z.enum(["physics", "chemistry", "math", "economics"])).min(1).max(4),
  frameStyle: z.enum(["rounded", "phone", "browser"]).default("rounded"),
  cycleSeconds: z.number().min(1.5).max(6).default(2.6),
});

export const ClipRefSchema = z.object({
  src: z.string(),                        // relative to assets/clips or an id from clips.index.json
  in: z.number().min(0).default(0),       // start offset inside the clip
  out: z.number().min(0).optional(),
  fit: z.enum(["cover", "contain"]).default("cover"),
  caption: z.string().max(60).optional(), // small label under the frame
});

export const CloseSchema = z.object({
  tagline: z.string().max(60),
  status: z.string().max(30).default("Coming soon"),
  showMark: z.boolean().default(true),
  contact: z.string().max(60).optional(), // only shown if supplied; never invented
});

export const AudioSchema = z.object({
  narration: z.object({
    enabled: z.boolean().default(false),
    voice: z.string().optional(),
    script: z.array(z.object({ at: z.number().min(0), text: z.string() })).default([]),
  }).default({}),
  music: z.object({
    enabled: z.boolean().default(true),
    track: z.string().optional(),
    gainDb: z.number().min(-40).max(0).default(-22),
    duckDb: z.number().min(-30).max(0).default(-10),
  }).default({}),
  sfx: z.object({
    enabled: z.boolean().default(true),
    cues: z.array(z.object({ at: z.number(), name: z.string() })).default([]),
  }).default({}),
});

export const CaptionsSchema = z.object({
  mode: z.enum(["off", "burned", "sidecar", "both"]).default("burned"),
  style: z.enum(["bold-center", "lower-third", "karaoke"]).default("lower-third"),
  maxCharsPerLine: z.number().int().min(14).max(34).default(24),
});

export const MetaSchema = z.object({
  title: z.string().max(100).optional(),
  description: z.string().max(400).optional(),
  hashtags: z.array(z.string().regex(/^#[A-Za-z0-9_]+$/)).max(8).default([]),
  altText: z.string().max(300).optional(),
});
```

### 11.3 Scene type enum

```ts
export const SceneTypeEnum = z.enum([
  "story-clock", "story-line", "story-question",
  "dead-ink", "equation-morph",
  "graph-draw", "ball-fall", "orbit", "wave", "bar-grow", "molecule",
  "video-slot", "subject-chips", "typed-prompt",
  "cta-close",
]);
```

Each type has its own props schema, registered in `src/scenes/index.ts` next to the module.
`normalize()` validates `props` with the registered schema and fills defaults.

### 11.4 Normalization

`normalize(spec)` returns a `ResolvedSpec` where:

- Every beat has an absolute `start` and `end`.
- Every scene has an absolute `start` and `end` in seconds.
- Times are snapped to the frame grid: `t = Math.round(t * fps) / fps`.
- Defaults are filled.
- Clip references are resolved to absolute paths and probed durations.
- Shared elements are validated: every id used in `shared` exists in the shared registry.
- `seed` is propagated to every scene as `rngSeed = hash(seed + scene.id)`.

### 11.5 Time rules

- Beats are sequential, no gaps larger than 0.1 s, no overlaps except the cross-fade window.
- The cross-fade window is exactly `tokens.motion.sceneFade` (0.4 s by default). Scenes within a
  beat may overlap freely but must be on different layers or use shared elements.
- Total duration = last beat end + `tokens.motion.tail` (0.6 s hold on the final frame).
- The final frame is held so platforms that cut early still show the close.

### 11.6 Semantic validation (beyond the schema)

Errors (block build):

- `E_SPEC_001` beat order is not hook, friction, turn, product, close.
- `E_SPEC_002` total duration under 12 s or over 60 s.
- `E_SPEC_003` a scene starts before 0 or ends after total duration.
- `E_SPEC_004` a clip file is missing or unreadable.
- `E_SPEC_005` a clip has no video stream or is shorter than 1 s.
- `E_SPEC_006` a shared element id is used but never created.
- `E_SPEC_007` the hook has no readable text visible before 0.2 s.
- `E_SPEC_008` the product beat has no video-slot scene.
- `E_SPEC_009` the close beat has no cta-close scene.
- `E_SPEC_010` a text string exceeds the line budget for its role (section 12.4).

Warnings (print, do not block):

- `W_SPEC_101` story lines contain a hype word (list in `claims.ts`).
- `W_SPEC_102` a beat is longer than 9 s with no motion change.
- `W_SPEC_103` fewer than two distinct clips in the product beat.
- `W_SPEC_104` hashtag count above 5.
- `W_SPEC_105` narration script longer than 2.6 words per second.
- `W_SPEC_106` caption line count above 2.
- `W_SPEC_107` the same clip is used twice in a row.

### 11.7 Forbidden-claim scanner

`claims.ts` exports `scanClaims(text): Finding[]`. Rules (case-insensitive):

- URLs and domains: `/\b[a-z0-9-]+\.(com|io|ai|app|co|org|net|np)\b/`, `https?://`
- Handles: `/@[A-Za-z0-9_]{3,}/`
- Prices: `/[$€£₹]\s?\d|\bNPR\b|\bRs\.?\s?\d|\bfree\b|\bdiscount\b|\boff\b/`
- Counts and ratings: `/\b\d[\d,.]*\s?(k|m)?\+?\s?(students|users|learners|teachers)\b/`, `/\b\d(\.\d)?\s?(stars?|\/5)\b/`
- Speed: `/\bin\s+(\d+|a few|just)\s+(seconds?|minutes?)\b/`, `/\binstantly\b/`
- Absolutes: `/\b(always|never|guaranteed|100%|perfect|best)\b/`
- Endorsements: `/\b(endorsed|approved|official partner|recommended by)\b/`

Findings have `{ code, severity, text, index }`. Any finding is a warning unless
`claimsApproved` is false and the finding is in the URL, price, count, speed or endorsement
groups, in which case it is an error.

### 11.8 Full example spec (physics)

```json
{
  "version": 1,
  "id": "physics-falling-ball-01",
  "title": "Physics: the ink that moves",
  "locale": "en",
  "seed": 7,
  "video": { "fps": 30, "background": "chalkboard", "grid": true },
  "theme": { "accent": "blue", "typeScale": "normal", "motion": "normal" },
  "story": {
    "kind": "clock",
    "hero": { "text": "11:47 pm", "style": "serif-large" },
    "lines": [
      { "text": "Aarav has a physics exam at nine.", "role": "body" },
      { "text": "Chapter 4 is thirty-eight pages of this:", "role": "dim" }
    ],
    "subject": "physics",
    "topic": "motion under constant acceleration"
  },
  "beats": [
    {
      "id": "hook", "duration": 5.6,
      "scenes": [{ "type": "story-clock", "id": "s1", "props": {} }]
    },
    {
      "id": "friction", "duration": 4.2,
      "scenes": [{
        "type": "dead-ink", "id": "s2",
        "props": { "equation": "s = ut + ½at²", "line": "He reads it four times. It doesn’t move.", "stamp": "Just ink." }
      }]
    },
    {
      "id": "turn", "duration": 6.0,
      "scenes": [
        { "type": "equation-morph", "id": "s3a", "shared": ["eq"], "props": { "title": "Then the ink moves." } },
        { "type": "graph-draw", "id": "s3b", "at": 0.6, "shared": ["eq"], "props": { "curve": "quadratic", "label": "s = ½at²" } },
        { "type": "ball-fall", "id": "s3c", "at": 1.2, "props": { "followCurve": true } }
      ]
    },
    {
      "id": "product", "duration": 7.0,
      "scenes": [
        { "type": "typed-prompt", "id": "s4a", "props": { "text": "projectile motion" } },
        { "type": "video-slot", "id": "s4b", "at": 0.4, "props": {} },
        { "type": "subject-chips", "id": "s4c", "at": 1.6, "props": {} }
      ]
    },
    {
      "id": "close", "duration": 6.2,
      "scenes": [{ "type": "cta-close", "id": "s5", "props": {} }]
    }
  ],
  "product": {
    "headline": "Type a topic. Phiversity makes the narrated animation.",
    "clips": [
      { "src": "physics/projectile-motion", "in": 4, "out": 9, "caption": "Projectile motion" },
      { "src": "physics/free-fall", "in": 2, "out": 6, "caption": "Free fall" }
    ],
    "chips": ["physics", "chemistry", "math", "economics"],
    "frameStyle": "rounded",
    "cycleSeconds": 2.6
  },
  "close": { "tagline": "Learn it by watching it.", "status": "Coming soon", "showMark": true },
  "audio": {
    "narration": { "enabled": false },
    "music": { "enabled": true, "track": "soft-pulse-01", "gainDb": -22, "duckDb": -10 },
    "sfx": { "enabled": true, "cues": [
      { "at": 0.2, "name": "tick" },
      { "at": 9.9, "name": "whoosh" },
      { "at": 16.1, "name": "pop" }
    ] }
  },
  "captions": { "mode": "burned", "style": "lower-third", "maxCharsPerLine": 24 },
  "meta": {
    "description": "A student, a dead equation, and the moment it starts to move.",
    "hashtags": ["#physics", "#studytok", "#edtech"],
    "altText": "A student studies late at night. A static equation turns into a graph and a falling ball."
  }
}
```

---

## 12. BRAND SYSTEM AND DESIGN TOKENS

Tokens live in `src/tokens`. Scenes import tokens and never use raw hex values or pixel sizes.

### 12.1 Color

The palette is inspired by Manim's classic scheme because Phiversity output uses it. The ad
should feel like a still from the product.

```ts
export const color = {
  chalkboard: {
    bg: "#121821",
    bgDeep: "#0a0e13",
    grid: "rgba(88,196,221,0.07)",
    ink: "#eaf0f6",
    dim: "#7f8b99",
    deadInk: "#59636f",
    line: "#2b3644",
  },
  paper: {
    bg: "#f4f1ea",
    bgDeep: "#e9e4d8",
    grid: "rgba(40,60,90,0.08)",
    ink: "#1a2230",
    dim: "#6b7480",
    deadInk: "#a8a396",
    line: "#cfc9ba",
  },
  midnight: {
    bg: "#0b1020",
    bgDeep: "#060914",
    grid: "rgba(140,160,255,0.07)",
    ink: "#e6ebff",
    dim: "#8791b8",
    deadInk: "#4b5478",
    line: "#242c4d",
  },
  accent: {
    blue: "#58c4dd",
    green: "#83c167",
    yellow: "#f4d35e",
    red: "#fc6255",
  },
} as const;
```

Rules:

- One accent per ad as the lead. The other three appear only on chips and the product frame.
- Red is for "wrong / dead / stop" moments. Never use red for the brand mark.
- Contrast: text on background must meet 4.5:1. The validator computes it for `ink` and `dim`.
- Do not use warm cream with a terracotta accent. That combination is reserved for the paper
  theme with a blue accent only.

### 12.2 Typography

Bundle fonts locally as `.woff2`. Use two families only.

- Display: Instrument Serif (regular and italic). Large numerals, hero lines, taglines.
- Text: DM Sans (400, 500, 700). Body lines, chips, captions.
- Math: use the display italic for variables. Do not use a third font.

Type scale (in stage pixels at 1080 wide). Use a 1.25 ratio:

```ts
export const type = {
  hero:   { family: "display", size: 172, line: 1.0,  track: "-0.01em", weight: 400 },
  title:  { family: "display", size: 120, line: 1.02, track: "-0.01em", weight: 400 },
  eq:     { family: "display", size: 164, line: 1.0,  track: "0.01em",  weight: 400 },
  lead:   { family: "text",    size: 64,  line: 1.35, track: "0",       weight: 400 },
  body:   { family: "text",    size: 52,  line: 1.4,  track: "0",       weight: 400 },
  chip:   { family: "text",    size: 46,  line: 1.2,  track: "0",       weight: 500 },
  caption:{ family: "text",    size: 44,  line: 1.25, track: "0",       weight: 700 },
  small:  { family: "text",    size: 34,  line: 1.3,  track: "0",       weight: 400 },
} as const;
```

Typographic rules:

- Use real typographic punctuation in all visible text: ’ for apostrophes, “ ” for quotes,
  – for ranges, × for multiplication, − for minus in math, ½ and superscripts where Unicode exists.
- Sentence case for every line. No all-caps labels. No tracked-out eyebrows.
- Do not accent a single word in a headline with a different color or italic.
- Line length under 24 characters for display lines, under 34 for body lines on a 9:16 stage.
- Never hyphenate. Balance lines with `text-wrap: balance`.

### 12.3 Layout and safe zones

Stage logical size: 1080 x 1920.

```ts
export const layout = {
  stage: { w: 1080, h: 1920 },
  margin: 97,                 // 9% of width
  grid: 120,                  // background grid cell
  safe: {
    top: 220,                 // platform header overlays
    bottom: 420,              // caption, buttons, description
    left: 60,
    right: 140,               // like/share rail on the right
  },
  frame: { w: 886, h: 498 },  // 16:9 video frame inside the margins
} as const;
```

Rules:

- All text must sit inside `safe`. The validator renders a debug overlay and fails if any text
  bounding box crosses the safe zone (checked in the golden-frame test).
- Captions live at `y = 1920 - 420 + 40`. Nothing else may occupy that band after the hook.
- Display type is left aligned. Do not center long lines. Center only the close mark and a
  single short tagline.

### 12.4 Line budgets

| Role | Max characters | Max lines |
|------|----------------|-----------|
| hero | 14 | 1 |
| display | 24 | 2 |
| body | 34 | 3 |
| dim | 34 | 3 |
| chip | 14 | 1 |
| caption | 24 | 2 |
| tagline | 28 | 2 |

### 12.5 Motion tokens

```ts
export const motion = {
  sceneFade: 0.4,
  tail: 0.6,
  ease: {
    out: "power3.out",
    in: "power2.in",
    inOut: "power2.inOut",
    settle: "back.out(1.4)",
    linear: "none",
    draw: "power1.inOut",
    spring: "elastic.out(1, 0.6)",
  },
  dur: {
    micro: 0.25,
    short: 0.45,
    medium: 0.7,
    long: 1.1,
    draw: 2.4,
  },
  stagger: { chips: 0.22, words: 0.06, lines: 0.5 },
  profile: {
    calm:   { speed: 0.85 },
    normal: { speed: 1.0 },
    snappy: { speed: 1.2 },
  },
} as const;
```

Motion rules:

- Spend motion deliberately. One orchestrated moment per beat. Do not fade-and-slide every item.
- The turn beat carries the most motion. The friction beat carries the least.
- Prefer clip-path reveals, scale from a pivot and draw-on strokes over generic fades.
- Every element that enters must have a purpose: it shows a change or answers the story.
- Hold still frames long enough to read. Minimum read time = 0.35 s + 0.06 s per character.

### 12.6 Background and grid

- The chalkboard background has a faint number-plane grid at `layout.grid` spacing.
- The grid is a static element. It never animates, except during the turn beat, when it may
  brighten by at most 30% opacity.
- Add no gradient washes, no glow, no drop shadows.

### 12.7 The mark

- The Phiversity mark is a circle with an italic phi glyph (φ) in the display font.
- Ring stroke 7 px, color = lead accent. Glyph size 100 px inside a 140 px circle.
- Wordmark "Phiversity" in DM Sans 700, 80 px, tracking -0.01em, ink color.
- Clear space around the mark: 0.5 x the circle diameter.
- If a real brand SVG exists at `assets/brand/mark.svg`, use it and ignore the rules above.

---
## 13. SCENE CATALOG

A scene is a module that exports a descriptor. The registry maps `type` to the descriptor.

### 13.1 Scene module contract

```ts
export interface SceneContext {
  stage: HTMLElement;                 // the 1080x1920 stage
  layer: (name: LayerName) => HTMLElement;
  tokens: Tokens;
  fps: number;
  rng: () => number;                  // seeded, from rng.ts
  shared: SharedRegistry;
  media: MediaRegistry;               // clip slots
  start: number;                      // absolute seconds
  end: number;                        // absolute seconds
}

export interface SceneDescriptor<P> {
  type: SceneType;
  propsSchema: z.ZodType<P>;
  /** Build DOM into the right layer and return a gsap timeline fragment (paused, duration = end - start). */
  build(ctx: SceneContext, props: P): gsap.core.Timeline;
  /** Elements that must be visible at the very first frame of the scene (for hook validation). */
  firstFrameText?(props: P): string[];
  /** Human description for docs. */
  docs: string;
}
```

Rules for every scene:

1. `build` creates its DOM, sets initial states with `gsap.set`, and returns a timeline.
2. It must not add the timeline to the master. The runtime does that at `ctx.start`.
3. It must remove nothing from the DOM. The runtime hides scenes with `autoAlpha` at the end.
4. Everything animated is a GSAP tween on that timeline. No other timers.
5. Any randomness uses `ctx.rng()`.
6. All text goes through `text.ts` helpers so that measurement and fitting are consistent.
7. All times inside the returned timeline are relative to the scene start (0 to duration).

### 13.2 `story-clock`

Purpose: hook with a time on a clock-like numeral and one or two lines.

Props:

```ts
{ hero: string; lines: { text: string; role: "body" | "dim" }[]; revealStyle: "wipe" | "tick" }
```

Behavior:

- Hero numeral is visible at frame 0, partially revealed by a left-to-right clip-path wipe
  that is already at 18% on the first frame so the first frame is never empty.
- Wipe completes in 0.9 s with `power3.out`.
- Line 1 enters at 1.4 s, line 2 at 2.9 s. Each enters with a 20 px rise and opacity.
- If `revealStyle` is `tick`, split the hero by characters and reveal each with a 0.05 s stagger.
- Hold until the scene end. Scene fade out is handled by the runtime.

### 13.3 `story-line`

Purpose: hook or friction with plain text lines and no hero.

Props: `{ lines: { text: string; role: Role }[]; gap: number }`.

Behavior: lines enter with a 0.5 s stagger. The final line stays longest.

### 13.4 `story-question`

Purpose: a question hook. A large question mark glyph or the question text.

Props: `{ question: string; underline: boolean }`.

Behavior:

- The question types in by word using `stagger.words`.
- If `underline`, a 6 px line draws under the last word with `ease.draw`.

### 13.5 `dead-ink`

Purpose: the friction beat. Shows static, uninviting content.

Props:

```ts
{ equation: string; line: string; stamp: string; dimAfter: number }
```

Behavior:

- Equation appears in `deadInk` color at 0.3 s. It does not animate beyond its entrance.
- After `dimAfter` seconds the grid lowers to 60% opacity, which makes the scene feel flat.
- The line appears at 1.4 s.
- The stamp (for example "Just ink.") appears at 2.8 s in red with a 0.9 to 1.0 scale settle.
- Nothing else moves. Stillness is the point.

### 13.6 `equation-morph`

Purpose: the turn. The static equation becomes the seed of the animation.

Props: `{ title: string; fromShared: string; toColor: AccentName }`.

Behavior:

- Re-parents the shared `eq` node from the friction scene to this scene's layer.
- Tweens its color from `deadInk` to the lead accent over 0.6 s.
- Scales it to 0.55 and moves it to the lower-left area where the graph label will sit.
- Title "Then the ink moves." enters at the top with a clip-path wipe.

### 13.7 `graph-draw`

Purpose: draw a distance-time or similar curve.

Props:

```ts
{
  curve: "quadratic" | "linear" | "sine" | "decay" | "sigmoid";
  xLabel: string; yLabel: string; label: string;
  drawSeconds: number;
}
```

Behavior:

- Draws axes first (0.4 s), then the guide curve as a dashed faint path.
- The live trail is a polyline built from sampled points up to the current progress `p`.
- Sampling step 0.02 in parameter space. Always include the exact current point.
- Provides `progress` as a GSAP-tweened number in a proxy object so that other scenes can read it.
- Labels fade in after the trail passes 60%.

Curve definitions (parameter t in [0,1], coordinates inside a 300x290 viewBox):

```ts
quadratic: t => ({ x: 20 + 260*t, y: 30 + 220*t*t })
linear:    t => ({ x: 20 + 260*t, y: 250 - 220*t })
sine:      t => ({ x: 20 + 260*t, y: 140 - 100*Math.sin(2*Math.PI*t) })
decay:     t => ({ x: 20 + 260*t, y: 30 + 220*(1 - Math.exp(-4*t)) })
sigmoid:   t => ({ x: 20 + 260*t, y: 250 - 220/(1+Math.exp(-10*(t-0.5))) })
```

### 13.8 `ball-fall`

Purpose: a physical object moving in sync with the graph.

Props: `{ followCurve: boolean; radius: number; dropLine: boolean; rail: boolean }`.

Behavior:

- A filled yellow circle. If `followCurve`, its position equals the curve point at `progress`.
- If `dropLine`, a dotted vertical line connects the ball to the x axis.
- If `rail`, a second ball falls straight down on the right edge using the same `y(t)` so the
  viewer sees the same motion as the curve and as a falling object.
- The ball must start exactly at the first point of the curve. Check with a unit test.

### 13.9 `orbit`

Purpose: gravity and orbital motion for astronomy-flavored physics ads.

Props: `{ bodies: number; eccentricity: number; trail: boolean }`.

Behavior: a central body and an orbiting body driven by a parametric ellipse. Use a polar
parametrization, not a simulation. Trail is a faded polyline of the last 40 samples.

### 13.10 `wave`

Purpose: waves, sound, light and oscillations.

Props: `{ kind: "sine" | "standing" | "interference"; amplitude: number; cycles: number }`.

Behavior: stroke-draw a sine path; for `standing` animate amplitude with `sin(omega t)` using a
proxy number; for `interference` draw two waves and their sum in three colors.

### 13.11 `bar-grow`

Purpose: economics and data stories.

Props: `{ bars: { label: string; value: number; color: AccentName }[]; unit?: string }`.

Behavior: bars grow from zero with a 0.12 s stagger and `power3.out`. Values are shown as
integers. Labels sit under bars. No axes gridlines unless `grid` is true.

### 13.12 `molecule`

Purpose: chemistry stories.

Props: `{ molecule: "water" | "methane" | "co2" | "ammonia"; spin: boolean }`.

Behavior: draw atoms as circles with radii by element and bonds as lines. Atoms scale in with
`settle`. Optional slow rotation implemented by tweening a rotation proxy number and re-projecting
2D positions. No WebGL.

### 13.13 `typed-prompt`

Purpose: show the product input: the user types a topic.

Props: `{ text: string; placeholder: string; caret: boolean }`.

Behavior:

- A rounded input shape with a placeholder in `dim`.
- Characters appear one at a time. Typing speed is 14 characters per second plus seeded jitter
  of up to 25 ms per character from `ctx.rng()`.
- Caret blinks by toggling opacity on exact 0.5 s boundaries. It must be seek-safe, so compute
  its visibility from time rather than from a looping tween.
- After the last character a short 0.25 s "send" pulse on the frame outline in the lead accent.

### 13.14 `video-slot`

Purpose: show real Phiversity output. Full details in section 15.

### 13.15 `subject-chips`

Purpose: show supported subjects.

Props: `{ chips: Subject[]; stagger: number }`.

Behavior: chips enter one by one. Each has a colored dot: physics blue, chemistry green,
math yellow, economics red. Chips wrap on narrow widths. Use only the subjects listed in the
spec; the schema restricts the values to the supported four.

### 13.16 `cta-close`

Purpose: the close.

Props: `{ tagline: string; status: string; showMark: boolean; contact?: string }`.

Behavior:

- The mark enters first, then the tagline (clip-path wipe, 0.7 s), then the status line.
- The status line uses the yellow accent.
- `contact` is rendered only if it is present in the spec. It is never defaulted.
- Everything holds still for at least 1.6 s at the end.

### 13.17 Adding a new scene

To add a scene type:

1. Create `src/scenes/<name>.ts` with a descriptor.
2. Register it in `src/scenes/index.ts`.
3. Add it to `SceneTypeEnum`.
4. Add a unit test that builds it at `fps = 30` and asserts the duration and first-frame text.
5. Add a golden-frame test at three times: 10%, 50%, 100% of the scene.
6. Run `npm run docs` to refresh `docs/SCENES.md`.

---

## 14. DETERMINISTIC TIMELINE RUNTIME

The runtime runs in the browser page and exposes a tiny API for the capture step.

### 14.1 Page template

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=1080, initial-scale=1">
<title>phiad</title>
<link rel="stylesheet" href="./base.css">
<style id="font-faces"></style>
</head>
<body>
<div id="viewport">
  <div id="stage" data-bg="chalkboard">
    <div class="layer" data-layer="bg"></div>
    <div class="layer" data-layer="content"></div>
    <div class="layer" data-layer="overlay"></div>
    <div class="layer" data-layer="captions"></div>
    <div class="layer" data-layer="debug"></div>
  </div>
</div>
<script src="./gsap.min.js"></script>
<script src="./phiad.runtime.js"></script>
</body>
</html>
```

### 14.2 Base CSS rules

```css
html, body { margin: 0; padding: 0; background: #000; overflow: hidden; }
#viewport { width: 1080px; height: 1920px; transform-origin: 0 0; }
#stage { position: relative; width: 1080px; height: 1920px; overflow: hidden; }
.layer { position: absolute; inset: 0; pointer-events: none; }
.layer[data-layer="bg"] { z-index: 0; }
.layer[data-layer="content"] { z-index: 10; }
.layer[data-layer="overlay"] { z-index: 20; }
.layer[data-layer="captions"] { z-index: 30; }
.layer[data-layer="debug"] { z-index: 99; display: none; }
body[data-debug="1"] .layer[data-layer="debug"] { display: block; }
* { box-sizing: border-box; animation: none !important; transition: none !important; }
```

The `animation: none !important` and `transition: none !important` rule is mandatory. It
guarantees that nothing outside GSAP can move.

### 14.3 The public runtime API

```ts
declare global {
  interface Window {
    __phiad: {
      ready: Promise<void>;          // fonts loaded, media decoded, timeline built
      duration: number;              // seconds
      fps: number;
      seek(t: number): Promise<void>;// resolves when the DOM reflects time t
      report(): TimelineReport;      // for timeline.report.txt
      setDebug(on: boolean): void;
    };
  }
}
```

### 14.4 Boot sequence

1. Read the resolved spec from `window.__SPEC__` (injected by the capture step) or `?spec=`.
2. Inject `@font-face` rules pointing at local `.woff2` files.
3. `await document.fonts.load()` for every family and weight used. Then `await document.fonts.ready`.
4. Build the stage and layers. Apply theme tokens as CSS variables on `#stage`.
5. For each scene in the resolved spec, call `descriptor.build(ctx, props)` and add its
   fragment to the master timeline at `scene.start` with `master.add(fragment, scene.start)`.
6. Add scene visibility tweens: `autoAlpha 0 -> 1` at the scene start, and `1 -> 0` at the end
   minus `sceneFade`, except for the final scene which stays.
7. Pre-decode media (section 15) and resolve `ready`.
8. Create the master with `gsap.timeline({ paused: true, defaults: { overwrite: false } })`.
9. Call `master.time(0)` and render once.

### 14.5 `seek(t)` contract

```ts
async function seek(t: number): Promise<void> {
  const clamped = Math.min(Math.max(t, 0), master.duration());
  master.time(clamped, false);              // false: do not fire callbacks as a side effect
  gsap.ticker.tick();                       // force a render pass
  await media.seekAll(clamped);             // seek every active video element and wait for 'seeked'
  await nextFrame();                        // double rAF to let layout and paint settle
  await nextFrame();
}
```

Rules:

- `seek` must be idempotent. Calling `seek(t)` twice in a row produces identical pixels.
- `seek` must work in any order, forwards or backwards. The capture step may use parallel
  workers that each capture a different range.
- Never use `master.play()` in capture mode. Never rely on `onUpdate` side effects that depend
  on the previous time. If a scene uses a proxy-number tween with `onUpdate`, the update function
  must compute everything from the current proxy value only (no accumulation).
- Timeline callbacks (`call`) are forbidden in capture mode because they depend on direction.
  Replace them with state derived from time inside tweens, or with `autoAlpha` toggles.

### 14.6 Pure update functions

Every `onUpdate` must be a pure function of the proxy value:

```ts
// GOOD
const o = { t: 0 };
tl.to(o, { t: 1, duration: 2.6, ease: "none", onUpdate: () => draw(o.t) }, 1.1);

// BAD: accumulates state, breaks seeking
let last = 0;
tl.to(o, { t: 1, onUpdate: () => { d += step; last = o.t; } });
```

For trails and paths, rebuild the whole path from `0..t` on every update. At 30 fps this is cheap.

### 14.7 Shared elements

Shared elements let one node survive across scenes (the equation in the reference ad).

```ts
export interface SharedRegistry {
  create(id: string, el: HTMLElement, owner: string): void;
  adopt(id: string, intoLayer: HTMLElement): HTMLElement; // moves node, keeps styles
  get(id: string): HTMLElement;
}
```

Rules:

- The first scene that lists the id in `shared` creates it. Later scenes adopt it at their start.
- Adoption is performed at build time, not at seek time. To make the node appear in the right
  place at the right time, use a wrapper per scene and animate the wrapper's opacity. The
  actual node is moved between wrappers with a Flip-like computed transform that is tweened
  on the timeline. Do not use GSAP Flip plugin (it is a plugin; stay with core).
- Provide a helper `morphBox(from: DOMRect, to: DOMRect)` that returns `{x, y, scale}` for a tween.

### 14.8 Text helpers (`text.ts`)

- `split(el, mode)` splits text into spans by `chars`, `words` or `lines` and returns the spans.
  It preserves spaces with `white-space: pre`. It must not break ligatures in the display font.
- `fit(el, maxWidth, maxHeight, minSize)` reduces font size in 2 px steps until it fits. Used
  only at build time, never during seek.
- `measure(text, font)` uses an offscreen canvas and returns width and height.
- `balance(el)` applies `text-wrap: balance` and falls back to a manual break algorithm.
- All helpers throw `E_TEXT_001` if the final box is outside the safe zone.

### 14.9 SVG helpers (`svg.ts`)

- `pathFromPoints(points)` returns a `d` string with fixed precision (1 decimal).
- `lengthAt(path, t)` samples `getTotalLength` for stroke-draw effects.
- `drawOn(path, tl, at, duration, ease)` sets `strokeDasharray`/`strokeDashoffset` and tweens it.
- `sample(fn, n)` returns `n+1` points of a parametric function over [0,1].
- `bboxOf(points)` returns a rectangle. Used for fitting graphs into frames.
- Always set `vector-effect: non-scaling-stroke` on strokes that must keep a fixed pixel width.

### 14.10 Seeded random (`rng.ts`)

```ts
export function mulberry32(seed: number) {
  let a = seed >>> 0;
  return function () {
    a = (a + 0x6D2B79F5) >>> 0;
    let t = a;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}
export function hashString(s: string): number {
  let h = 2166136261;
  for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 16777619); }
  return h >>> 0;
}
```

Use `mulberry32(hashString(spec.seed + ":" + scene.id))` for each scene.

### 14.11 Timeline report

`report()` walks the master timeline and returns rows:

```
t=0.000  s1     tween  #clock   clipPath  0.9s  power3.out
t=1.400  s1     tween  .l1      opacity,y 0.6s  power2.out
...
```

Write it to `timeline.report.txt`. A reviewer must be able to read the report and understand
the ad without watching it.

### 14.12 Debug overlay

In `?debug=1` mode, show: current time, active scene ids, a safe-zone rectangle, a 3x3 thirds
grid, and a scrubber input that calls `seek`. This overlay is never present in capture mode.

---

## 15. VIDEO-SLOT SCENE (EMBEDDING RENDERED PHIVERSITY VIDEOS)

This is the scene that makes the ad honest: it shows the product's real output.

### 15.1 Clip sources

Clips are Phiversity-rendered MP4s (Manim output with narration or silent). They may be 16:9
(1920x1080 or 1280x720) or 9:16. They live in `assets/clips` and are indexed in
`assets/clips.index.json`:

```json
{
  "version": 1,
  "clips": [
    {
      "id": "physics/projectile-motion",
      "file": "physics/projectile-motion.mp4",
      "subject": "physics",
      "topic": "projectile motion",
      "durationSec": 62.4,
      "width": 1920,
      "height": 1080,
      "fps": 30,
      "hasAudio": true,
      "bestRanges": [{ "in": 4, "out": 9, "note": "parabola draws with velocity vectors" }],
      "tags": ["parabola", "vectors", "graph"]
    }
  ]
}
```

`phiad clips scan` generates entries with ffprobe and leaves `bestRanges` empty for a human to fill.

### 15.2 Two embedding strategies

Implement both. Choose with `product.strategy` (default `frames`).

**Strategy A: `frames` (default, most reliable).**

1. Before capture, run FFmpeg to extract the needed range of each clip into a numbered image
   sequence at the output fps, scaled to the slot size (886x498 at device scale 1).
2. In the page, the slot is a `<img>` whose `src` is set from the sequence for the exact frame
   index `round((t - slotStart) * fps) + inFrame`.
3. All images in the range are preloaded with `Image.decode()` before `ready` resolves.
4. Memory: at 886x498 JPEG quality 85 each frame is about 40 KB. A 5 s range at 30 fps is
   150 frames, about 6 MB. Fine on a 4 GB machine. Cap total preloaded frames at 900.

**Strategy B: `video` (fast to author, less exact).**

1. Use a `<video muted playsinline preload="auto">` element.
2. `seek(t)` sets `video.currentTime = in + (t - slotStart)` and awaits `seeked`.
3. Wait one more `requestVideoFrameCallback` if available, else two `requestAnimationFrame`s.
4. If `seeked` does not fire within 5 s, throw `E_MEDIA_002` with the clip id and time.
5. Chromium bundled with Playwright lacks proprietary codecs. H.264 playback may fail. If
   `video.canPlayType('video/mp4; codecs="avc1.42E01E"')` returns an empty string, the runtime
   must throw `E_MEDIA_001` and tell the user to use strategy `frames` or to install Chrome and
   set `PHIAD_CHROMIUM_PATH`.

### 15.3 Frame mapping

```ts
function clipTimeFor(t: number, slot: Slot): number {
  const local = t - slot.start;
  const loopLen = slot.out - slot.in;
  const wrapped = ((local % loopLen) + loopLen) % loopLen;   // loop
  return slot.in + wrapped;
}
```

When there are several clips, the slot cycles through them every `cycleSeconds`. The switch is
a hard cut with a 0.12 s clip-path wipe on the frame. The current clip index is
`Math.floor((t - slotStart) / cycleSeconds) % clips.length`. It is derived from time, never stored.

### 15.4 Frame styles

- `rounded`: 16:9 box, 6 px border in the lead accent, radius 28 px, 886 px wide.
- `phone`: a 9:16 rounded phone outline for vertical clips, 520 px wide. Not a photo of a phone.
- `browser`: a 16:9 box with a slim top bar with three neutral dots. No fake URL text.

For `fit: "cover"` crop to fill. For `contain`, letterbox on `bgDeep`.

### 15.5 Clip captions

If `caption` is set, render it below the frame in `small` type, `dim` color. It changes with the clip.

### 15.6 Clip audio

- Clip audio is **not** played in the browser. Audio is mixed separately in section 18.
- By default the ad uses music and SFX only. If `audio.narration.useClipAudio` is true, extract
  the audio of each clip range with FFmpeg and place it at the slot time at -6 dB, ducking music.

### 15.7 Choosing good ranges

Write `clips/pick.ts` that scores candidate ranges for each clip. The score favors ranges where:

- the frame-to-frame difference is moderate (something is clearly moving, but it is not a cut),
- there is a visible graph, equation or shape (detected by edge density),
- the range is 3 to 6 seconds,
- the range does not start or end in the middle of an on-screen text transition.

Use FFmpeg `select` with `scene` scores to find cuts. Never start a range on a black frame.

### 15.8 What if there are no clips yet

If `assets/clips` is empty, the engine must still produce a valid ad. In that case the slot
shows an animated placeholder (a drawn sine wave and the text "Your rendered videos play here").
The validator prints `W_SPEC_199: using placeholder clips` and the build adds a visible small
"placeholder" watermark in the top-left corner so a placeholder ad is never posted by accident.

---
## 16. CAPTURE PIPELINE (PLAYWRIGHT)

### 16.1 Goals

- Capture every frame exactly once, in any order, on any worker.
- Stream frames to disk as they are produced. Memory stays flat.
- Survive a crash: a rerun resumes from the last good frame.

### 16.2 Browser launch

```ts
const browser = await chromium.launch({
  executablePath: process.env.PHIAD_CHROMIUM_PATH || undefined,
  args: [
    "--disable-gpu-vsync",
    "--disable-frame-rate-limit",
    "--force-color-profile=srgb",
    "--font-render-hinting=none",
    "--disable-lcd-text",
    "--hide-scrollbars",
    "--mute-audio",
    "--autoplay-policy=no-user-gesture-required",
    "--allow-file-access-from-files",
    "--no-sandbox"                       // only inside the container
  ],
});
const context = await browser.newContext({
  viewport: { width: 1080, height: 1920 },
  deviceScaleFactor: 1,
  reducedMotion: "no-preference",
});
```

Notes:

- `--font-render-hinting=none` and `--disable-lcd-text` keep text rendering identical across
  machines. Without them, text edges differ between Windows and Linux.
- Use `deviceScaleFactor: 1` for 1080x1920 output. For a 2x supersampled look use 2 and
  downscale with FFmpeg (slower, sharper). Offer it as `--supersample`.
- Never use headed mode in the cloud.

### 16.3 Page load

1. Start a tiny static server (Node `http`) that serves `dist/runtime`, `assets` and the
   per-run folder. Bind to `127.0.0.1` on a random port. Close it at the end of the run.
2. `page.goto("http://127.0.0.1:<port>/page.html")`.
3. `await page.evaluate((spec) => { window.__SPEC__ = spec; }, resolvedSpec)` before the runtime
   boots. If boot has already started, pass the spec via `page.addInitScript`.
4. `await page.evaluate(() => window.__phiad.ready)`.
5. Read `duration` and `fps` from the page and compare with the resolved spec. If they differ
   by more than half a frame, throw `E_CAPTURE_001`.

### 16.4 The frame loop

```ts
const total = Math.ceil(duration * fps);
for (let i = startFrame; i < endFrame; i++) {
  const t = i / fps;
  await page.evaluate((tt) => window.__phiad.seek(tt), t);
  const file = path.join(framesDir, `f_${String(i).padStart(6, "0")}.${ext}`);
  await page.screenshot({
    path: file,
    type: ext === "jpeg" ? "jpeg" : "png",
    quality: ext === "jpeg" ? cfg.jpegQuality : undefined,
    omitBackground: false,
    animations: "disabled",
    caret: "hide",
    clip: { x: 0, y: 0, width: 1080, height: 1920 },
  });
  progress(i + 1, total);
}
```

Rules:

- Use `animations: "disabled"` as an extra safety. It must not be the thing that makes the output
  correct; the runtime already stops everything.
- Retry a frame up to 3 times on timeout. After 3 failures throw `E_CAPTURE_002` with the frame
  index and time.
- If a frame file already exists and is larger than 1 KB, skip it (resume support).
- Log every 30 frames: frames done, fps achieved, ETA.

### 16.5 Parallel workers

- `workers` defaults to `min(2, cpuCount - 1)` and to 1 when free RAM is under 3 GB.
- Split the frame range into contiguous chunks of equal size. One page per worker, each with its
  own `context`. All workers share the same static server.
- Each worker loads the runtime independently and calls `seek` for its own frames, which is safe
  because seek is order-independent (section 14.5).
- Aggregate progress through a single log line updated at most twice a second.
- If any worker throws, cancel the others and surface the first error.

### 16.6 Speed notes

- JPEG at quality 92 is about 4x faster than PNG and visually lossless for flat vector art with text.
  Use PNG only for golden frames and thumbnails.
- Avoid `fullPage: true`.
- Keep the DOM small. Do not render offscreen scenes: scenes outside their window use
  `visibility: hidden` (GSAP `autoAlpha: 0` already does this).
- Expect 3 to 8 frames per second per worker on a modest machine. A 30 s ad at 30 fps is 900
  frames, so plan on 2 to 6 minutes.

### 16.7 Verification after capture

`capture/verify.ts` checks:

- The number of frame files equals `total`.
- No file is smaller than 2 KB.
- First and last frames are not identical to a flat color (guards against a blank page).
- Mean absolute difference between consecutive frames is non-zero for at least 90% of pairs
  inside non-static scenes (guards against a frozen timeline).
- A sample of 10 random frames is decoded with `sharp` to confirm dimensions 1080x1920.

Failures throw `E_VERIFY_001` with the list of bad frames.

### 16.8 Pre-extraction of clip frames (strategy A)

Before capture run, for each clip range:

```
ffmpeg -y -ss <in> -t <out-in> -i <clip> \
  -vf "fps=<fps>,scale=886:498:force_original_aspect_ratio=increase,crop=886:498" \
  -q:v 4 <runDir>/clipframes/<clipId>/%05d.jpg
```

- Use `-ss` before `-i` for fast seek, accept the tiny inexactness, then align by frame count.
- For vertical clips targeting the phone frame use `scale=520:924` and crop likewise.
- Write `clipframes/<clipId>/index.json` with `{ frames, fps, width, height }`.
- Deduplicate: if two scenes use the same clip range, reuse the folder.
- Delete `clipframes` after a successful run unless `--keep-frames`.

---

## 17. ENCODING PIPELINE (FFMPEG)

### 17.1 Silent video from frames

```
ffmpeg -y -framerate 30 -start_number 0 -i frames/f_%06d.jpg \
  -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p \
  -profile:v high -level 4.1 -movflags +faststart \
  -vf "scale=1080:1920:flags=lanczos,format=yuv420p" \
  -color_primaries bt709 -color_trc bt709 -colorspace bt709 -color_range tv \
  video.silent.mp4
```

Notes:

- `-movflags +faststart` moves the index to the front so platforms process it quickly.
- Force BT.709 tags. Many players assume it for HD, but explicit tags prevent shifted colors.
- If the file is larger than `maxMB`, re-encode with a two-pass bitrate target computed as
  `targetKbps = (maxMB * 8192) / duration * 0.92 - audioKbps`.

### 17.2 Presets (`presets.ts`)

| Preset | Size | FPS | CRF | Max length | Notes |
|--------|------|-----|-----|------------|-------|
| reels | 1080x1920 | 30 | 18 | 90 s | AAC 128 kbps |
| tiktok | 1080x1920 | 30 | 18 | 60 s | keep captions above bottom 420 px |
| shorts | 1080x1920 | 30 | 18 | 60 s | |
| x | 1080x1920 | 30 | 20 | 140 s | size under 512 MB, aim for 20 MB |
| linkedin | 1080x1350 | 30 | 20 | 600 s | 4:5, re-layout required |
| square | 1080x1080 | 30 | 20 | 60 s | 1:1, re-layout required |
| landscape | 1920x1080 | 30 | 20 | 600 s | 16:9, re-layout required |

For presets that change the aspect ratio, the runtime receives `video.width` and `video.height`
and scenes must handle them through `layout.ts` functions (`layoutFor(w, h)`), not constants.
v1 only needs 9:16 to be perfect. Other ratios may use a simplified layout, but must not clip text.

### 17.3 Audio mux

```
ffmpeg -y -i video.silent.mp4 -i audio/mix.wav \
  -c:v copy -c:a aac -b:a 128k -ar 48000 -ac 2 -shortest \
  -movflags +faststart final.mp4
```

If audio is disabled, copy the silent video to `final.mp4` and still add a silent AAC track
(`-f lavfi -i anullsrc=r=48000:cl=stereo`) because some platforms reject files without audio.

### 17.4 Burned captions

Two options. Implement option A first.

**A. Burn from the DOM.** Captions are a layer in the page (section 18.5), so they are already in
the frames. This gives perfect typographic control and no libass dependency.

**B. Burn with libass.** Render `captions.ass` and apply `-vf ass=captions.ass`. Use only when
captions must be switched on or off after capture without recapturing.

### 17.5 Thumbnail

- Choose the frame at the end of the hook beat plus 0.5 s, or the `thumbnail.at` time if given.
- Save as PNG at 1080x1920 with sharp, then also a 1080x1350 center crop `thumbnail.4x5.png`.

### 17.6 Probe and report

After encoding run ffprobe and assert:

- codec h264, pix_fmt yuv420p, width/height as expected, avg_frame_rate = fps
- duration within 0.1 s of the resolved total
- audio stream present, 48 kHz, stereo
- size under `maxMB`
- first video packet is a keyframe

Write `meta.json` with: id, title, description, hashtags, altText, durationSec, sizeMB,
codec info, spec hash, engine version, build time, warnings.

---

## 18. AUDIO: NARRATION, MUSIC, SOUND EFFECTS, CAPTIONS

Every ad must work muted. Audio is a bonus layer, never the carrier of meaning.

### 18.1 Audio plan

`audio/cues.ts` creates a list of cues from the resolved spec:

```ts
interface Cue {
  kind: "narration" | "music" | "sfx" | "clip-audio";
  at: number;          // seconds
  duration?: number;
  file?: string;       // resolved audio file
  gainDb?: number;
  text?: string;       // for narration, used for captions
}
```

Automatic SFX placement rules (if the spec has none):

- `tick` at the hook start if the hero is a clock.
- `whoosh` at the turn beat start.
- `pop` on each subject chip entrance.
- `chime` softly at the close tagline.
- Never more than one SFX per 0.25 s. Never louder than -14 dB relative to the music peak.

### 18.2 Narration (optional)

The TTS layer is an adapter:

```ts
export interface TtsProvider {
  name: string;
  synthesize(text: string, opts: { voice?: string; locale: "en" | "ne"; speed?: number }):
    Promise<{ wavPath: string; durationSec: number; words?: { w: string; start: number; end: number }[] }>;
}
```

Implementations to provide:

1. `none` (default): returns nothing.
2. `file`: reads pre-recorded WAVs from `assets/narration/<spec-id>/<n>.wav`.
3. `piper`: spawns a local Piper binary (works offline on Windows). Config path via env.
4. `http`: posts text to any configured endpoint that returns WAV (so cloud TTS can be plugged in).

Do not hard-code a vendor. Keep secrets in env.

Narration timing rules:

- Speaking rate target is 2.2 to 2.6 words per second.
- A narration line must start no earlier than the scene it belongs to and must end 0.3 s before
  the next beat boundary.
- If narration is longer than its window, shorten the text (never speed up above 1.12x) or
  extend the beat. The validator warns with `W_SPEC_105`.
- If word timestamps exist, the karaoke caption style uses them. Otherwise estimate by
  character count proportional to duration.

### 18.3 Music

- Loops live in `assets/music`. Provide the engine with a `loop-to-length` function: crossfade
  the loop end into its start for 0.5 s and trim to total duration plus 1 s.
- Fade in 0.4 s, fade out the last 1.2 s.
- Default level -22 dB. When narration plays, duck music by `duckDb` using FFmpeg `sidechaincompress`
  or by a precomputed volume envelope (envelope is simpler and deterministic).
- Music must have a license note in `assets/music/LICENSES.md`. The engine refuses tracks not
  listed there (`E_AUDIO_003`). Never download music at build time.

### 18.4 Mixing and loudness

Mix with FFmpeg `amix`/`adelay`/`volume` filters, or build an `.wav` in Node by summing buffers.
Then normalize:

```
ffmpeg -i mix.raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null -
# parse the measured values, then run the second pass with measured_* parameters
ffmpeg -i mix.raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=..:measured_TP=..:measured_LRA=..:measured_thresh=..:offset=..:linear=true mix.wav
```

Assertions: integrated loudness within 1 LU of -14, true peak below -1.0 dBTP.

### 18.5 Captions

- Source: narration script if enabled, otherwise the visible on-screen story lines.
- Captions are a DOM layer in the `captions` layer, driven by the same master timeline.
- Style `lower-third`: left aligned, `caption` type, white on a 60% black rounded plate, max
  2 lines, `maxCharsPerLine` from the spec. Vertical position inside the bottom safe band.
- Style `bold-center`: center, 64 px, used for hook-only captions on silent ads.
- Style `karaoke`: the current word is highlighted with the lead accent. Use word timestamps.
- Each caption shows for at least 0.9 s and at most 5 s.
- Captions must never cover the product frame or the mark.
- Also export `captions.srt` and `captions.vtt` for platforms that accept sidecar files.

SRT builder rules:

- Times as `HH:MM:SS,mmm`.
- Lines wrapped at `maxCharsPerLine` on word boundaries.
- No overlap between consecutive cues. Minimum gap 0.04 s.

### 18.6 Alt text and descriptions

Generate `altText` automatically if missing: a single sentence naming the story kind, the
equation or topic, and what moves. Example: "A student studies late at night. A static equation
turns into a graph and a falling ball." Never describe the face or body of a person.

---

## 19. STORY ENGINE (THE "RANDOM STORY" GENERATOR)

The story engine produces the beat-1 content and the connection to the subject.

### 19.1 Story bank

`src/story/bank.ts` holds a curated list of story seeds. Each seed:

```ts
interface StorySeed {
  id: string;
  kind: "clock" | "question" | "failure" | "teacher" | "curiosity";
  subject: "physics" | "chemistry" | "math" | "economics";
  topic: string;
  hero: string;
  lines: { text: string; role: "body" | "dim" }[];
  staticThing: string;       // what looks dead in the friction beat, e.g. an equation
  movesInto: SceneType;      // what it becomes in the turn beat
  clipTags: string[];        // tags for finding product clips
  doNotUse?: string[];       // reasons or contexts to avoid
}
```

Ship at least 24 seeds: 6 per subject. Examples:

```
physics / clock / motion under constant acceleration
  hero "11:47 pm"
  lines: "Aarav has a physics exam at nine." / "Chapter 4 is thirty-eight pages of this:"
  staticThing "s = ut + ½at²"   movesInto graph-draw + ball-fall

physics / question / orbits
  hero "Why?"
  lines: "Why doesn’t the moon fall down?" / "The textbook says: balanced forces."
  staticThing "F = GMm / r²"    movesInto orbit

chemistry / failure / balancing equations
  hero "3rd try"
  lines: "Maya balances H₂ + O₂ → H₂O again." / "The atoms never seem to add up."
  staticThing "H₂ + O₂ → H₂O"   movesInto molecule

math / teacher / the unit circle
  hero "Board"
  lines: "Mr. Rai draws a circle on the board." / "It sits there. The sine wave never appears."
  staticThing "sin θ"           movesInto wave

economics / curiosity / supply and demand
  hero "Why?"
  lines: "Why did tomatoes double in price overnight?" / "The chart in the book is two straight lines."
  staticThing "S = D"           movesInto bar-grow
```

Use names that are plausible and neutral for a Nepali and global audience (Aarav, Maya, Sita,
Bikash, Anisha, Mr. Rai). Rotate them with the seed.

### 19.2 Story quality rules (`lint.ts`)

A story passes if all are true:

1. The hero is 14 characters or fewer and appears in the first frame.
2. The first line contains a concrete time, number, place or person.
3. There is exactly one problem. No lists of problems.
4. No line mentions Phiversity, "AI", "app", "platform" or "tool" before the product beat.
5. The static thing is a real, correct formula or fact (see 19.4).
6. The turn is physically or logically true: the thing that moves actually follows from the formula.
7. Reading time of all story lines combined is under 6 s at 14 characters per second.
8. No stereotypes, no mocking of students, no "lazy", "stupid", "failing" labels.
9. No real names of real people, schools, exam boards or brands.

### 19.3 LLM-assisted generation (optional adapter)

`story/generate.ts` takes `{ subject, topic, seed }` and asks an LLM for a StorySeed as JSON.
The adapter interface mirrors TTS: `LlmProvider.complete(system, user): Promise<string>`.
Providers: `none`, `http` (OpenAI-compatible endpoint, which covers OpenRouter, DeepSeek, NVIDIA NIM
and Gemini's compatible endpoint). Never import a vendor SDK in core.

System prompt to use:

```
You write the opening story for a 30-second vertical educational ad.
Return ONLY valid JSON matching the StorySeed schema. No markdown.
Rules:
- One specific human moment, true to a real student's life.
- The first line has a concrete time, number or person.
- Hero text is 14 characters or fewer.
- Exactly one static thing (a formula, diagram or fact) that looks lifeless.
- That static thing must be correct and must plausibly become an animation.
- Never mention a product, an app, AI or software.
- No hype words. No emoji. Sentence case. Use typographic apostrophes.
- Neutral names only. No real people, schools or brands.
- Maximum 4 lines of 34 characters each.
```

After generation, always run `lint`. If lint fails, retry up to 3 times with the lint errors
appended. If still failing, fall back to a bank seed chosen by the RNG.

### 19.4 Factual safety for the static thing

- Maintain `src/story/facts.ts` with a whitelist of formulas and facts per subject and topic.
- The static thing must match an entry. If the LLM proposes a formula not in the whitelist, reject.
- Start the whitelist with about 60 entries covering secondary-school physics, chemistry, math
  and economics. Each has `id`, `display`, `subject`, `topic`, `explanation`, `visualizes`.
- Never present a wrong formula even as "dead ink". Correctness is part of the brand.

### 19.5 Turn mapping

A table maps `movesInto` to scene combinations:

| movesInto | Scenes used in the turn beat |
|-----------|------------------------------|
| graph-draw | equation-morph, graph-draw, ball-fall |
| orbit | equation-morph, orbit |
| molecule | equation-morph, molecule |
| wave | equation-morph, wave |
| bar-grow | equation-morph, bar-grow |

`story make` fills the beats array from this table and sets durations from the motion profile.

---
## 20. VARIATION ENGINE AND POSTING CADENCE

Phiversity's launch plan is high volume: a teaser phase first, then roughly 3 to 6 videos a day
at random times, with an ambition of many more. The engine must make variety cheap and keep
every ad on brand.

### 20.1 Variation axes

A variation plan combines choices along these axes:

| Axis | Values |
|------|--------|
| Subject | physics, chemistry, math, economics |
| Story kind | clock, question, failure, teacher, curiosity |
| Hook text | from the seed, or an A/B alternative |
| Accent | blue, green, yellow, red (lead accent only) |
| Background | chalkboard (default), midnight; paper sparingly |
| Motion profile | calm, normal, snappy |
| Clip set | different ranges and different clips |
| Length | 18 s, 28 s, 38 s |
| Music | 3 to 5 loops |
| Captions | bold-center for silent, lower-third for narrated |

### 20.2 Constraints on variation

- Never change the mark, the wordmark, the fonts or the tagline structure.
- At most 30% of a batch may use a non-default background.
- Two consecutive ads in a schedule must differ in at least two axes.
- The same story seed must not repeat within 14 days.
- The same clip range must not appear in more than 3 ads in a 7-day window.
- Red as the lead accent is allowed only when the story is about a mistake or a misconception.

### 20.3 `variation/plan.ts`

```ts
interface PlanInput {
  count: number;
  start: string;            // ISO date
  subjects?: Subject[];
  seed: number;
  history?: HistoryRow[];   // previous posts, to enforce spacing rules
}
interface PlanRow {
  id: string;
  subject: Subject;
  seedId: string;
  accent: AccentName;
  background: Background;
  motion: MotionProfile;
  length: 18 | 28 | 38;
  clipIds: string[];
  musicId: string;
  hookVariant: "a" | "b";
}
```

The planner is a seeded, constraint-satisfying shuffle. It must be deterministic for a given
`seed` and `history`. It writes `plan.json` and one spec per row to `specs/generated/`.

### 20.4 Hook A/B variants

Each seed may have two hook variants. Example for the clock story:

- A: "11:47 pm" with "Aarav has a physics exam at nine."
- B: "9 am" with "Aarav’s physics exam starts in nine hours."

Rules: the variants must differ in the hero text or the first line only. The rest of the ad is
identical so that results can be compared.

### 20.5 Posting schedule (`variation/schedule.ts`)

The engine does not post. It produces a schedule file that the marketing agent consumes.

```json
{
  "version": 1,
  "timezone": "Asia/Kathmandu",
  "items": [
    {
      "id": "physics-falling-ball-01",
      "file": "out/physics-falling-ball-01/final.mp4",
      "thumbnail": "out/physics-falling-ball-01/thumbnail.png",
      "caption": "A static equation, then the moment it moves.",
      "hashtags": ["#physics", "#studytok"],
      "altText": "…",
      "earliest": "2026-11-15T07:40:00+05:45",
      "platforms": ["reels", "tiktok", "shorts"],
      "phase": "teaser",
      "approval": "pending"
    }
  ]
}
```

Scheduling rules:

- Random times: draw from a seeded distribution that avoids exact hour marks and avoids the
  same minute twice in a day.
- Daily count: random integer from 3 to 6 (configurable). Minimum gap between posts 70 minutes.
- Preferred windows for students: early morning, after school, late evening (local time).
  Configure as weights, not fixed hours.
- Phase `teaser`: every ad ends on "Coming soon". Phase `launch`: the close may carry a
  `contact` that the owner supplies. The engine never writes a contact by itself.
- Every item starts with `approval: "pending"`. A human flips it to `approved`. The agent must
  not post pending items. This is a hard rule, not a suggestion.

### 20.6 Caption and hashtag generation

- Caption: one or two short sentences in brand voice. No hype, no claims (run `scanClaims`).
- Hashtags: 3 to 5, lowercase, relevant: subject tag, `#studytok` or `#edutok`, one topic tag.
- Do not use banned or misleading tags. Do not use trending tags unrelated to the content.
- Provide a 3-caption set per ad for the agent to rotate across platforms.

### 20.7 History file

`out/history.jsonl` appends one line per built ad: id, date, seedId, clipIds, accent, hook variant,
spec hash. The planner reads it to enforce the spacing rules in 20.2.

---

## 21. PLATFORM EXPORT SPECS

### 21.1 Safe zones by platform

Use the union of all platforms for the default 9:16 layout. The values below are conservative.

| Zone | Distance from edge |
|------|--------------------|
| Top | 220 px |
| Bottom | 420 px |
| Right | 140 px |
| Left | 60 px |

### 21.2 Technical limits

| Platform | Ratio | Max length used | Max size used | Audio |
|----------|-------|-----------------|---------------|-------|
| Instagram Reels | 9:16 | 60 s | 100 MB | AAC |
| TikTok | 9:16 | 60 s | 100 MB | AAC |
| YouTube Shorts | 9:16 | 60 s | 100 MB | AAC |
| X | 9:16 or 16:9 | 90 s | 50 MB | AAC |
| LinkedIn | 4:5 or 1:1 | 60 s | 50 MB | AAC |
| Facebook Reels | 9:16 | 60 s | 100 MB | AAC |

These are conservative internal targets, not quotes from the platforms. Platform limits change.
Put them in `presets.ts` as data so they can be edited without touching code. Add a comment that
the owner must re-check the current limits before relying on them.

### 21.3 File naming

`<spec-id>__<preset>__<yyyymmdd>.mp4`, for example `physics-falling-ball-01__reels__20261115.mp4`.
Lowercase, ASCII only, no spaces.

### 21.4 Metadata

- Embed the title into the MP4 `title` metadata via FFmpeg `-metadata`.
- Do not embed the engine's absolute paths or the user's machine name.
- Strip other metadata with `-map_metadata -1` before adding the title.

---

## 22. CLOUD EXECUTION (AZURE-FIRST) AND LOCAL-ONLY MODE

The owner's local PC is small (4 GB RAM). The default plan is that heavy rendering runs in the
cloud and the PC only coordinates. The engine must also run fully locally when needed.

### 22.1 Two modes, one code path

```
phiad build spec.json                 # local mode: everything on this machine
phiad build spec.json --cloud         # enqueue a job, wait, download the result
phiad worker                          # cloud mode: run inside a container, pull jobs
```

The capture and encode code is identical. Only the job wrapper differs.

### 22.2 Job message

```json
{
  "jobId": "01J...",
  "specUrl": "blob://specs/physics-falling-ball-01.json",
  "clipUrls": ["blob://clips/physics/projectile-motion.mp4"],
  "preset": "reels",
  "outputPrefix": "blob://renders/physics-falling-ball-01/",
  "options": { "workers": 2, "audio": true },
  "attempt": 1
}
```

### 22.3 Azure mapping

| Need | Service |
|------|---------|
| Queue of render jobs | Service Bus queue `render-jobs` (dead-letter enabled) |
| Run a render | Container Apps Job, triggered by queue length (KEDA scaler) |
| Storage of specs, clips and results | Blob Storage, containers `specs`, `clips`, `renders` |
| Secrets | Key Vault |
| Logs and metrics | Azure Monitor / Log Analytics |
| Container image | Azure Container Registry |

### 22.4 Worker behavior

1. Receive a message with a lock. Parse and validate.
2. Download the spec and clips to `/tmp/job`.
3. Run `build` with `--workers` from the message.
4. Upload `final.mp4`, `thumbnail.png`, `meta.json`, `build.log`, `timeline.report.txt`.
5. Complete the message. On failure abandon it. After 3 attempts it dead-letters.
6. Always clean `/tmp/job`.

The worker must be idempotent: if `renders/<id>/final.mp4` exists and the spec hash matches,
complete the message without rebuilding.

### 22.5 Dockerfile outline

```dockerfile
FROM mcr.microsoft.com/playwright:v1.47.0-jammy
RUN apt-get update && apt-get install -y ffmpeg fonts-noto-core && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY dist ./dist
COPY assets/fonts ./assets/fonts
COPY assets/brand ./assets/brand
ENV NODE_ENV=production PHIAD_CHROMIUM_PATH=
USER pwuser
ENTRYPOINT ["node", "dist/cli/index.js"]
CMD ["worker"]
```

Notes: the Playwright base image includes Chromium but not proprietary H.264 decoding, which is
why strategy A (pre-extracted frames) is the default.

### 22.6 Cost control

The owner has a limited student credit. The engine must be frugal.

- Default container size: 2 vCPU, 4 GB RAM. One job at a time per container.
- Scale to zero when the queue is empty.
- Frame format JPEG, not PNG, in the cloud.
- Hard cap per job: 10 minutes wall time. Exceed it and the job fails with `E_CLOUD_001`.
- Log an estimated cost per job: `vCPU-seconds * rate`. Keep the rates in config, not in code.
- A `phiad cost report` command sums the estimated cost from `out/history.jsonl`.
- Budget guard: if the monthly estimate passes 80% of the configured budget, the CLI refuses
  new `--cloud` jobs unless `--force` is passed.
- Upload only final artifacts. Do not upload frames.
- Use Blob lifecycle rules to delete `renders` older than 30 days and temp data after 2 days.

### 22.7 Local-only mode on a 4 GB machine

- Force `workers = 1`.
- Use JPEG at quality 88.
- Lower the clip-frame cap to 600.
- Process one ad at a time. `batch` concurrency is 1.
- Close the Chromium page between ads to release memory.
- If free RAM falls below 1 GB during capture, pause for 2 seconds and continue; log a warning.
- Do not keep the frame folder. Stream frames into FFmpeg through stdin when possible:

```ts
const ff = spawn(ffmpegPath, [
  "-y", "-f", "image2pipe", "-framerate", String(fps), "-vcodec", "mjpeg", "-i", "pipe:0",
  "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p",
  "-movflags", "+faststart", outPath,
]);
// page.screenshot({ type: "jpeg" }) returns a Buffer -> ff.stdin.write(buffer)
```

  With streaming, frames must be written in order, so streaming mode uses one worker only.

### 22.8 Offline guarantee

Local mode must work with no internet after dependencies are installed. The `doctor` command
verifies that fonts, GSAP and Chromium are local. No CDN links appear in the page template.

---
## 23. QUALITY ASSURANCE AND TESTING

### 23.1 Test pyramid

| Level | Tool | What it checks | Count target |
|-------|------|----------------|--------------|
| Unit | vitest | schema, normalize, claims, srt, rng, curves, mapping | 120+ |
| Scene | vitest + jsdom/Playwright | each scene builds, duration, first-frame text | 1 per scene |
| Golden | Playwright + pixelmatch | pixels at fixed times for 4 example specs | 3 times each |
| E2E | vitest | `phiad build` on the example spec, ffprobe assertions | 4 |
| Property | fast-check (optional) | seek order independence | 3 |

### 23.2 Unit tests that must exist

1. `schema`: every example spec parses; a spec with a missing `story` fails with a clear path.
2. `normalize`: all times are on the frame grid; total = last beat end + tail.
3. `claims`: each pattern in 11.7 has a positive and a negative case.
4. `srt`: output times are monotonic with no overlap and match `HH:MM:SS,mmm`.
5. `rng`: same seed gives the same first 1000 numbers; different seeds differ.
6. `curves`: every curve starts at the documented first point and ends at the documented last.
7. `ball-fall`: ball position at progress 0 equals the curve start within 0.01 px.
8. `typed-prompt`: caret visibility is a pure function of time (call it in scrambled order).
9. `video-slot`: `clipTimeFor` wraps correctly at the loop boundary and for negative offsets.
10. `presets`: every preset has width, height, fps, crf, maxLength and a valid audio config.
11. `story lint`: each rule in 19.2 has a failing example.
12. `facts`: every whitelist entry has all fields and a non-empty explanation.

### 23.3 Seek independence test (critical)

```ts
test("seek is order independent", async () => {
  const times = [0, 5.1, 2.4, 9.9, 0.3, 14.7, 5.1];
  const shots: Record<string, string> = {};
  for (const t of times) {
    await page.evaluate((x) => window.__phiad.seek(x), t);
    const hash = sha1(await page.screenshot({ type: "png" }));
    if (shots[t]) expect(hash).toBe(shots[t]);   // same time, same pixels
    shots[t] = hash;
  }
});
```

If this test fails, the engine is broken regardless of how good it looks.

### 23.4 Golden frames

- For each example spec store PNGs at 10%, 50% and 95% of the duration in `tests/golden/<id>/`.
- Compare with pixelmatch, threshold 0.1, allow up to 0.15% differing pixels.
- Fonts must be bundled so goldens are stable across machines.
- To update goldens: `npm run test:golden -- -u` and review the diff images manually.
- Store diff images in `tests/golden/__diff__/` and git-ignore them.

### 23.5 Visual rule checks (automated)

Run inside the page after the timeline is built, at 20 sample times:

- Every visible text node's bounding box is inside the safe zone (except the debug layer).
- No two text nodes in the content layer overlap by more than 2 px unless one is a caption.
- Text contrast meets 4.5:1 against the actual computed background color at that point.
- No element has a computed font family outside the two bundled families.
- No element has `animation-name` other than `none`.
- No image is smaller than its display size by more than 10% (blurry upscale guard).

Violations produce `E_QA_xxx` and fail the build in `--strict` mode, warn otherwise.

### 23.6 Review artifacts

Every build produces a contact sheet `review.png`: a grid of 12 frames evenly spaced, with
timestamps. A human can approve an ad from that one image. Build it with sharp composite.

### 23.7 Pre-publish checklist (printed at the end of `build`)

```
[ ] First frame has readable text
[ ] Works with sound off
[ ] No unsupported claims (scanClaims clean)
[ ] Product clips are real Phiversity output, not placeholders
[ ] Formula or fact is correct (facts whitelist)
[ ] Tagline and status line correct for the current phase
[ ] Captions inside the safe zone
[ ] Loudness within target
[ ] File under size limit
[ ] Alt text present
```

---

## 24. ACCESSIBILITY, SAFETY AND CONTENT RULES

### 24.1 Accessibility

- Every ad must be understandable with sound off and with captions on.
- Minimum on-screen text size 34 px at 1080 wide.
- Contrast 4.5:1 for all text.
- No flashing faster than 3 times per second anywhere in the frame. The validator checks
  scene cuts and opacity tweens for luminance changes above 20% at more than 3 Hz.
- Avoid pure red on pure green adjacency without a shape or label difference.
- Provide alt text and captions as sidecar files for every build.
- The reduced-motion preference is not relevant to a rendered video, but `calm` motion profile
  must exist for sensitive audiences.

### 24.2 Content safety

- No claims from section 2.2 without approval.
- No health, medical, legal or financial promises.
- No content aimed at children under 13. The audience is secondary school and older.
- No exam-cheating framing ("beat the exam", "no need to study").
- No comparison with named competitors or named products.
- No use of real logos, trademarks or copyrighted characters.
- No copyrighted music or fonts without a license note.
- Names of people in stories are fictional and common. Never use a real person's name.

### 24.3 Educational accuracy

- Every formula must exist in `facts.ts`.
- Units are shown correctly with a thin space: `9.8 m/s²`.
- Sign conventions are consistent within an ad. If a ball falls downward, y increases downward,
  and the graph label says "distance fallen", not "height".
- Do not show a physically wrong animation to look good. A falling ball follows `s = ½at²`.
  An orbit follows an ellipse, not a spiral. A reaction balances atoms.
- When in doubt, simplify the visual rather than bend the science.

### 24.4 Privacy

- No personal data in specs, logs or metadata.
- No analytics, no tracking pixels in the page template.
- Cloud uploads contain only specs, clips and results.

### 24.5 Licensing

- Keep `assets/LICENSES.md` listing every font, music track and SFX with source and license.
- Fonts: Instrument Serif and DM Sans are open-licensed. Keep the license files in `assets/fonts`.
- The engine refuses to build if an asset used in a spec is not in the license list (`E_LICENSE_001`).

---

## 25. PHASED DELIVERY PLAN

Work in this order. At the end of each phase, stop, run the acceptance commands, update
`docs/DECISIONS.md`, and only then move on. Do not start a phase while the previous one fails.

### Phase 0: Skeleton (target: half a day)

- Create the repository layout (section 7).
- Add package.json, tsconfig, lint, prettier, vitest.
- Implement `util/log`, `util/errors`, `util/fs`, `util/time`.
- Implement `phiad doctor`.
- Acceptance: `npm run build` passes; `phiad doctor` prints a readable table.

### Phase 1: Spec and tokens (target: one day)

- Implement `spec/schema`, `load`, `normalize`, `validate`, `claims`.
- Implement `tokens/*`.
- Generate `spec.schema.json` and `docs/SPEC.md`.
- Add the four example specs (physics first).
- Acceptance: `phiad validate specs/example-physics.json` prints a timeline table and exits 0;
  a bad spec exits 1 with an `E_SPEC_*` message.

### Phase 2: Runtime and first scenes (target: two days)

- Build the page template, base CSS, runtime boot, `seek`, registry, rng, text, svg helpers.
- Implement scenes: `story-clock`, `dead-ink`, `equation-morph`, `graph-draw`, `ball-fall`,
  `typed-prompt`, `video-slot` (placeholder only), `subject-chips`, `cta-close`.
- Implement `preview` with the debug overlay.
- Acceptance: opening the preview shows the reference ad's five beats; scrubbing back and forth
  gives identical frames; the seek independence test passes.

### Phase 3: Capture and encode (target: one to two days)

- Implement browser launch, static server, frame loop, verify, resume.
- Implement FFmpeg encode, mux, probe, thumbnail, contact sheet.
- Acceptance: `phiad build specs/example-physics.json --no-audio` produces a playable 1080x1920
  MP4; ffprobe assertions pass; a second run resumes after killing the process midway.

### Phase 4: Real clips (target: one day)

- Implement `clips scan`, `clips.index.json`, pre-extraction (strategy A), `video-slot` with frames.
- Implement the placeholder fallback with the watermark.
- Optional: strategy B with the codec check.
- Acceptance: with two real Phiversity clips in `assets/clips`, the product beat shows them,
  cycling every 2.6 s, frame-exact when scrubbed.

### Phase 5: Audio and captions (target: one to two days)

- Implement cues, music loop, SFX, mix, loudness, SRT/VTT, DOM captions.
- Implement TTS adapters `none`, `file`, `http`, then `piper`.
- Acceptance: loudness within 1 LU of -14; captions inside the safe zone; muted playback still
  tells the whole story.

### Phase 6: Story and variation (target: two days)

- Implement the story bank (24 seeds), facts whitelist (60 entries), lint, `story make`.
- Implement the remaining scenes: `orbit`, `wave`, `bar-grow`, `molecule`, `story-question`, `story-line`.
- Implement the variation planner, schedule file, history file.
- Acceptance: `phiad story make` produces valid specs for all four subjects; `phiad batch`
  builds 8 different ads; the planner respects the spacing rules.

### Phase 7: Cloud (target: one to two days)

- Implement job message, blob upload/download, queue consumer, Dockerfile.
- Implement cost estimate and budget guard.
- Acceptance: a job enqueued from the CLI produces the same output as local mode; a failed job
  dead-letters after 3 attempts; the container exits cleanly when the queue is empty.

### Phase 8: Hardening (target: one day)

- Golden tests for all four examples, property tests, lint rules for the runtime boundary.
- README and RUNBOOK. Troubleshooting section filled from real failures.
- Acceptance: `npm test` green; a fresh clone builds an ad using only the README.

### 25.1 Reporting format after each phase

Report in this exact shape:

```
PHASE N DONE
Built: <files and features>
Commands run: <list with results>
Acceptance: <pass/fail for each bullet>
Known gaps: <honest list>
Decisions added: <titles in DECISIONS.md>
Next: <phase N+1 first step>
```

Do not claim a pass for a command you did not run.

---

## 26. ACCEPTANCE CHECKLIST (WHOLE PROJECT)

Functional:

- [ ] `phiad doctor` passes on Windows and in the container.
- [ ] `phiad validate` rejects each E_SPEC case with the right code.
- [ ] `phiad build` produces a 1080x1920, 30 fps H.264 MP4 under 50 MB.
- [ ] Output duration matches the spec within 0.1 s.
- [ ] Seeking is order independent (test passes).
- [ ] The product beat shows real clips and cycles correctly.
- [ ] Placeholder clips are visibly watermarked.
- [ ] Audio loudness is -14 LUFS within 1 LU, true peak under -1 dBTP.
- [ ] Captions are in the safe zone and also exported as SRT and VTT.
- [ ] Thumbnails, contact sheet and `meta.json` are written.
- [ ] `phiad batch` builds 8 ads with different stories.
- [ ] The planner enforces the spacing rules.
- [ ] Cloud mode matches local output.

Quality:

- [ ] First frame is readable and human.
- [ ] No unsupported claims; `scanClaims` clean on all example specs.
- [ ] Every formula is in the facts whitelist and is correct.
- [ ] Typography uses typographic punctuation and sentence case.
- [ ] No gradients, glows or shadows. One accent per ad.
- [ ] Motion is deliberate: friction is still, turn is lively.

Engineering:

- [ ] No file over 400 lines. No `any`.
- [ ] No Node imports in `src/runtime` or `src/scenes`.
- [ ] No CSS animations or transitions in the page.
- [ ] No network access during capture.
- [ ] Memory stays under 2 GB during a local build.
- [ ] All tests pass. README works from a clean clone.

---

## 27. APPENDICES

### Appendix A: `story-clock` scene skeleton

```ts
import gsap from "gsap";
import { z } from "zod";
import type { SceneDescriptor } from "../runtime/registry";
import { split } from "../runtime/text";

const Props = z.object({
  hero: z.string().max(14),
  lines: z.array(z.object({ text: z.string().max(34), role: z.enum(["body", "dim"]) })).max(3),
  revealStyle: z.enum(["wipe", "tick"]).default("wipe"),
});
type P = z.infer<typeof Props>;

export const storyClock: SceneDescriptor<P> = {
  type: "story-clock",
  propsSchema: Props,
  docs: "Hook with a large hero numeral and up to three lines.",
  firstFrameText: (p) => [p.hero],
  build(ctx, p) {
    const root = document.createElement("section");
    root.className = "scene scene--story-clock";
    root.dataset.scene = "story-clock";
    const hero = document.createElement("p");
    hero.className = "t-hero";
    hero.textContent = p.hero;
    root.appendChild(hero);
    const lineEls = p.lines.map((l) => {
      const el = document.createElement("p");
      el.className = l.role === "dim" ? "t-body t-dim" : "t-body";
      el.textContent = l.text;
      root.appendChild(el);
      return el;
    });
    ctx.layer("content").appendChild(root);

    const tl = gsap.timeline({ paused: true });
    gsap.set(root, { autoAlpha: 1 });
    if (p.revealStyle === "wipe") {
      // first frame already shows 18% of the numeral
      tl.fromTo(hero, { clipPath: "inset(0 82% 0 0)" },
        { clipPath: "inset(0 0% 0 0)", duration: 0.9, ease: ctx.tokens.motion.ease.out }, 0);
    } else {
      const chars = split(hero, "chars");
      tl.from(chars, { opacity: 0, duration: 0.01, stagger: 0.05 }, 0);
    }
    lineEls.forEach((el, i) =>
      tl.from(el, { opacity: 0, y: 20, duration: 0.6, ease: ctx.tokens.motion.ease.out }, 1.4 + i * 1.5));
    tl.to({}, { duration: ctx.end - ctx.start }, 0);   // pin the fragment length
    return tl;
  },
};
```

### Appendix B: `graph-draw` and `ball-fall` sharing a progress proxy

```ts
// shared via ctx.shared as a plain object, not a DOM node
export interface GraphState { p: number }

const state = ctx.shared.getState<GraphState>("graph", () => ({ p: 0 }));
const curve = CURVES[props.curve];

function render() {
  const pts = [];
  for (let k = 0; k <= state.p + 1e-9; k += 0.02) pts.push(curve(Math.min(k, state.p)));
  pts.push(curve(state.p));                       // always include the exact current point
  trail.setAttribute("d", pathFromPoints(pts));
  const head = curve(state.p);
  ball.setAttribute("cx", String(head.x));
  ball.setAttribute("cy", String(head.y));
  drop.setAttribute("x1", String(head.x));
  drop.setAttribute("x2", String(head.x));
  drop.setAttribute("y1", String(head.y));
}

tl.to(state, { p: 1, duration: props.drawSeconds, ease: "none", onUpdate: render }, 0.6);
tl.set(state, { p: 0 }, 0);                       // reset when seeking back before the tween
render();                                         // initial paint
```

Seek safety: because `render` is a pure function of `state.p`, any seek position paints the same
result. The `tl.set(state, {p: 0}, 0)` call makes backwards seeks land on the correct value.

### Appendix C: Typed prompt, seek-safe caret

```ts
const CPS = 14;
const jitter = Array.from({ length: text.length }, () => ctx.rng() * 0.025);
const reveal = [];
let acc = 0;
for (let i = 0; i < text.length; i++) { acc += 1 / CPS + jitter[i]; reveal.push(acc); }

const o = { t: 0 };
tl.to(o, { t: acc, duration: acc, ease: "none", onUpdate: () => {
  const n = reveal.filter((x) => x <= o.t).length;
  label.textContent = text.slice(0, n);
  caret.style.opacity = Math.floor(o.t / 0.5) % 2 === 0 ? "1" : "0";   // time-derived blink
}}, 0.2);
```

### Appendix D: Chemistry example spec (abbreviated)

```json
{
  "version": 1,
  "id": "chemistry-balance-01",
  "title": "Chemistry: atoms that finally add up",
  "seed": 11,
  "claimsApproved": false,
  "story": {
    "kind": "failure",
    "hero": { "text": "3rd try", "style": "serif-large" },
    "lines": [
      { "text": "Maya balances H₂ + O₂ → H₂O again.", "role": "body" },
      { "text": "The atoms never seem to add up.", "role": "dim" }
    ],
    "subject": "chemistry",
    "topic": "balancing equations"
  },
  "beats": [
    { "id": "hook", "duration": 5.0, "scenes": [{ "type": "story-clock", "id": "c1", "props": { "revealStyle": "tick" } }] },
    { "id": "friction", "duration": 4.0, "scenes": [{ "type": "dead-ink", "id": "c2", "props": { "equation": "H₂ + O₂ → H₂O", "line": "Two oxygen atoms in. One comes out.", "stamp": "Not balanced." } }] },
    { "id": "turn", "duration": 6.0, "scenes": [
      { "type": "equation-morph", "id": "c3a", "shared": ["eq"], "props": { "title": "Then the atoms move." } },
      { "type": "molecule", "id": "c3b", "at": 0.8, "props": { "molecule": "water", "spin": true } }
    ] },
    { "id": "product", "duration": 7.0, "scenes": [
      { "type": "typed-prompt", "id": "c4a", "props": { "text": "balancing equations" } },
      { "type": "video-slot", "id": "c4b", "at": 0.4 },
      { "type": "subject-chips", "id": "c4c", "at": 1.6 }
    ] },
    { "id": "close", "duration": 6.0, "scenes": [{ "type": "cta-close", "id": "c5" }] }
  ],
  "product": {
    "headline": "Type a topic. Phiversity makes the narrated animation.",
    "clips": [{ "src": "chemistry/balancing-equations", "in": 3, "out": 8 }],
    "chips": ["physics", "chemistry", "math", "economics"]
  },
  "close": { "tagline": "Learn it by watching it.", "status": "Coming soon" }
}
```

### Appendix E: Troubleshooting guide

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| Text looks different on two machines | Fonts not bundled or hinting differs | Bundle `.woff2`, use the Chromium flags in 16.2 |
| Frames flicker between two states | A CSS transition or animation is active | Check the global `animation: none` rule; remove stray CSS |
| Backwards seek shows wrong state | An `onUpdate` accumulates state | Make it a pure function of the proxy value; add `tl.set(proxy, ..., 0)` |
| Video frame is black | H.264 not supported by bundled Chromium | Use strategy A or set `PHIAD_CHROMIUM_PATH` to Chrome |
| `seeked` never fires | Clip has a huge GOP or is corrupt | Re-encode the clip with `-g 30` or use strategy A |
| Capture is very slow | PNG frames, `deviceScaleFactor` 2, too many DOM nodes | Use JPEG, scale 1, simplify DOM |
| Out of memory locally | Too many workers or too many preloaded clip frames | `--workers 1`, lower the clip frame cap, stream to FFmpeg |
| Colors look washed out on a phone | Missing BT.709 tags or wrong range | Apply the tags in 17.1 |
| File too large | CRF too low or long duration | Raise CRF to 21 or use the two-pass size target |
| Audio too quiet | Loudness normalization skipped | Run the two-pass `loudnorm` in 18.4 |
| Captions overlap the product frame | Caption position ignores the layout | Use the bottom safe band only; lower-third style |
| Spec fails with `E_SPEC_010` | A line exceeds its character budget | Shorten the text or change its role |

### Appendix F: Writing rules for on-screen copy (quick reference)

- Start with a concrete detail: a time, a name, a number, a place.
- One idea per line. One problem per story.
- Active voice. Plain verbs. Sentence case.
- Say what is on screen, not what the product is.
- Do not explain the joke or the metaphor.
- End the story line on a noun, not on a promise.
- The tagline is a verb phrase the viewer could repeat: "Learn it by watching it."
- The status line is a fact about timing: "Coming soon."
- If a line could appear in any ad for any product, cut it.

### Appendix G: Review questions before you call an ad finished

1. Could a stranger tell, in the first two seconds, what human moment this is?
2. Does the friction beat feel genuinely dead, so the turn feels like relief?
3. Is the thing that moves in the turn the same kind of thing the product shows?
4. Would the ad still make sense on mute, on a small phone, outdoors?
5. Is every claim something the owner can defend?
6. Is there exactly one memorable moment, and is everything else quiet?
7. Would you remove one more element if you could?

---

### Appendix H: Handoff contract with the marketing agent

The marketing automation agent (Hermes Agent, cloud APIs only) consumes the engine's output. The
engine never posts. The agent never edits videos. The contract between them is files.

Engine writes:

- `out/<id>/final.mp4`, `thumbnail.png`, `captions.srt`, `meta.json`
- `schedule.json` (section 20.5), one item per ad, all `approval: "pending"`

Agent may:

- Read `schedule.json` and the files it references.
- Rotate the three caption variants across platforms.
- Post only items whose `approval` is `approved` and whose `earliest` time has passed.
- Write `out/posted.jsonl` with `{ id, platform, postedAt, url }` after posting.

Agent must not:

- Change the video, the tagline or the status line.
- Add links, handles, prices or claims to captions.
- Post an item with `phase: "teaser"` using launch wording.
- Post more than the configured daily maximum.

Engine reads `posted.jsonl` on the next planning run to update the spacing rules.

### Appendix I: Error code reference

| Code | Meaning |
|------|---------|
| E_SPEC_001 | Beat order wrong |
| E_SPEC_002 | Total duration out of range |
| E_SPEC_003 | Scene outside the timeline |
| E_SPEC_004 | Clip file missing |
| E_SPEC_005 | Clip has no video stream or is too short |
| E_SPEC_006 | Shared element never created |
| E_SPEC_007 | Hook has no early readable text |
| E_SPEC_008 | Product beat lacks a video slot |
| E_SPEC_009 | Close beat lacks a close scene |
| E_SPEC_010 | Text exceeds its line budget |
| W_SPEC_199 | Placeholder clips in use |
| E_TEXT_001 | Text box outside the safe zone |
| E_MEDIA_001 | H.264 playback unsupported in the browser |
| E_MEDIA_002 | Video seek timed out |
| E_CAPTURE_001 | Page duration or fps differs from the spec |
| E_CAPTURE_002 | A frame failed after retries |
| E_VERIFY_001 | Captured frames failed verification |
| E_AUDIO_003 | Music track missing from the license list |
| E_CLOUD_001 | Cloud job exceeded the time cap |
| E_QA_xxx | Visual rule violation |
| E_LICENSE_001 | Asset missing from the license list |

### Appendix J: Math and economics scene hints

Math (unit circle to sine wave):

- Draw a circle of radius 110 on the left and a growing sine trace on the right.
- A point travels around the circle. Its y value is carried across by a dotted horizontal
  line to the trace at the same time. The trace is `y = sin(2πp)` with `p` the progress.
- The angle label shows θ in degrees as an integer, updated from `p`.

Economics (supply and demand):

- Two lines cross at an equilibrium point. Draw demand first, then supply.
- When the story is a price spike, shift the supply line left with a 1.2 s tween and move the
  intersection dot along the demand line. Label the new price with an integer, no currency symbol.
- Use `bar-grow` only for comparisons, not for curves.

Chemistry (molecule):

- Radii: H 18, C 30, N 28, O 28. Colors: H ink, C dim, N blue, O red (as a bond-count aid, not a claim).
- Bond length 70 for single bonds. Water angle 104.5 degrees. CO₂ is linear.
- Atoms enter with `settle` and a 0.12 s stagger. Bonds draw after both atoms are visible.

### Appendix K: Definition of a "good" turn beat

A turn beat is good when all five are true:

1. The first moving element appears within 0.4 s of the beat start.
2. The static object from the friction beat visibly becomes the moving object (shared element).
3. The motion obeys the real formula.
4. A single short title names the change in plain words.
5. The beat ends on a held frame of at least 0.6 s so the viewer sees the result.

### Appendix L: Example timeline report for the reference ad

```
t=0.000  s1   story-clock     #clock    clipPath       0.9s  power3.out
t=1.400  s1   story-clock     .l1       opacity,y      0.6s  power3.out
t=2.900  s1   story-clock     .l2       opacity,y      0.6s  power3.out
t=5.600  s2   dead-ink        #eq       opacity        0.5s  power3.out
t=7.000  s2   dead-ink        .l3       opacity        0.5s  power3.out
t=8.400  s2   dead-ink        .stamp    opacity,scale  0.4s  back.out
t=9.800  s3a  equation-morph  #eq       color,scale,x  0.6s  power2.inOut
t=10.100 s3a  equation-morph  #t3       opacity,y      0.6s  power3.out
t=11.000 s3b  graph-draw      #trail    progress 0..1  2.6s  none
t=11.000 s3c  ball-fall       #ball     progress 0..1  2.6s  none
t=13.900 s3b  graph-draw      #f3       opacity,x      0.6s  power3.out
t=15.800 s4a  typed-prompt    #prompt   text           2.0s  none
t=16.200 s4b  video-slot      #frame    frames         6.4s  none
t=17.600 s4c  subject-chips   .chip     opacity,y      0.4s  stagger 0.25
t=22.800 s5   cta-close       .mark     opacity,y      0.5s  power3.out
t=24.000 s5   cta-close       .tagline  clipPath       0.7s  power3.out
t=25.200 s5   cta-close       .status   opacity        0.5s  power3.out
t=29.000 end  hold            -         -              0.6s  -
```

---

## FINAL INSTRUCTIONS TO THE CODING AGENT

1. Read this whole document once, then restate the plan in 12 bullets before writing code.
2. Start with Phase 0. Do not skip ahead.
3. Ask the owner a question only when a decision cannot be derived from this document. When you
   must ask, ask one question and offer a recommended default.
4. Keep `docs/DECISIONS.md` current. Every deviation from this document needs a one-paragraph reason.
5. Never invent facts about Phiversity: no URLs, prices, user numbers, handles or speed claims.
6. Prefer the simplest implementation that satisfies the acceptance criteria. Cut features
   before cutting determinism.
7. If something in this document conflicts with correctness of the output video, correctness wins.
8. When all phases pass, run a final batch of 8 ads, produce contact sheets, and report.

END OF PROMPT
