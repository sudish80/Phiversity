# Phiversity

**Ask a question. Get a narrated, animated lecture video.**

Phiversity turns a natural-language question — *"Explain why HBr adds to propene
to give 2-bromopropane"* — into a fully produced lecture video: an LLM plans the
lesson and writes the Manim animation code, a neural voice narrates it, and
ffmpeg assembles everything into a single MP4 with synchronized visuals,
camera work, and exam-standard formatting.

```
Intro.mp4 ─▶ QUESTION CARD (the question printed, grammar-checked, LaTeX
             typeset, read aloud while the situation is sketched)
        ─▶ the director plans each scene (transitions, camera, zoom,
            highlighting, live geometry, 3D, color roles)
        ─▶ the LLM writes one Manim scene per beat, timed to the narration
        ─▶ Manim renders (self-healing on errors; auto-pacing; overflow guard)
        ─▶ ffmpeg aligns voice with animation and stitches the final video
```

---

## Table of contents

1. [Features](#features)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Command-line usage](#command-line-usage)
6. [Web application](#web-application)
7. [REST API reference](#rest-api-reference)
8. [Visual system](#visual-system)
9. [Solution formats](#solution-formats)
10. [Quality guarantees](#quality-guarantees)
11. [Bundled sample lectures](#bundled-sample-lectures)
12. [Testing](#testing)
13. [Output layout](#output-layout)
14. [Troubleshooting](#troubleshooting)

---

## Features

**Generation pipeline**
- **Question-driven** — the user's question is printed on an opening card
  (grammar-corrected, LaTeX-typeset, centered), read aloud by TTS while the
  situation it describes is sketched, then handed off to the solution scenes
- **LLM-authored animation** — one Manim Community scene per lecture beat,
  written by any OpenAI-compatible model or Anthropic, timed to the measured
  narration duration
- **The director** — a content-aware planner attaches a *visual plan* to every
  scene (transition type, camera movement, zoom target, highlight order, live
  relationships, diagram type, 3D usage, semantic color roles, animation
  beats); a post-render verifier checks the generated code against the plan
- **Self-healing** — render failures are fed back to the LLM for repair
  (configurable retries)
- **Auto-pacing** — scenes whose animation would end before the narration are
  automatically stretched and, if needed, re-rendered so no dead freeze-frames
  appear (max-gap configurable)
- **Overflow guard** — rendered frames are inspected at the edges; clipped
  text is flagged (and healed on the LLM path), and the injected kit provides
  `wrap_text()` / `fit_width()` so questions of any length stay on screen
- **Voice-over** — Microsoft neural voices via `edge-tts` (gTTS and offline
  silence fallbacks); durations are probed with ffprobe and animations are
  aligned to them (last-frame freeze or audio padding, per segment)
- **Brand intro** — an `Intro.mp4` in the workspace is normalized and played
  before every lecture
- **Content-aware transitions** — question→solution slide-ups and
  step-to-step continuity are realized inside scene code; topic changes
  crossfade via ffmpeg `xfade`
- **Interactive follow-ups** — CLI `--interactive` appends new narrated
  segments for follow-up questions

**Web application** (local, single-user)
- Chat-first generation UI with a persistent conversation history
- Live job progress with the pipeline log streaming into the browser
- Library, recent, search, projects, notifications and sample-lecture pages,
  all driven by the REST API
- A custom video player (phi-player) with keyboard control and scrubbing

**Safety**
- Generated code is statically validated (no imports beyond Manim, no
  file/network/eval access) and rendered in an isolated directory with a
  hard timeout

---

## Architecture

```
src/phiversity/
├── cli.py        command-line interface
├── config.py     environment / .env configuration
├── server.py     local HTTP API + static frontend server (stdlib only)
├── db.py         SQLite storage: render jobs, chat threads, and the
│                 lecture index (one file: <root>/phiversity.db)
├── director.py   visual planning brain:
│                 · VISUAL_PLAN_SCHEMA  (what a scene may specify)
│                 · EFFECT_PLAYBOOK     (WHEN / WHERE / HOW / WHY for every
│                                        effect family)
│                 · SELECTION_RULES     (never add an effect without purpose)
│                 · transition mapping  (continuity cuts vs ffmpeg xfades)
│                 · verify_effects()    (post-render effect verification)
├── theme.py      semantic color registry, 5 cinematic presets (dark + light),
│                 WCAG contrast validation, and the scene "kit" injected into
│                 every render (colors T.<role>, camera framing helpers,
│                 live geometry, emphasis control, exam mechanics)
├── llm.py        LLM client (OpenAI-compatible + Anthropic), planner/coder
│                 prompts, robust JSON parsing, healing requests
├── tts.py        edge-tts / gTTS / silence engines + duration probing
├── render.py     code validation, manim subprocess rendering, self-healing,
│                 timing estimation/adjustment, layout lint, edge-clip check
├── compose.py    per-segment alignment (tpad/apad), plan-driven transitions,
│                 uniform re-encode, lossless concatenation
├── templates.py  question-card template, page-flip clip, and 12 bundled
│                 demo lectures with hand-authored visual plans
└── pipeline.py   stage orchestration, job composition, interactive mode
```

**Pipeline stages** — plan (LLM or bundled) → speak (TTS + duration probe) →
code (LLM, following the visual plan) → render (healing, pacing, linting,
verification) → compose (align, transition, stitch).

---

## Installation

Requirements: Python 3.9+, FFmpeg (with libx264 + aac), Manim ≥ 0.18
(Cairo/Pango), and LaTeX for equation typesetting.

```bash
# system dependencies (Ubuntu/Debian)
sudo apt install ffmpeg libcairo2-dev libpango1.0-dev pkg-config python3-dev
sudo apt install texlive texlive-latex-extra texlive-fonts-recommended

# python package
cd phiversity
pip install -r requirements.txt
pip install --no-build-isolation .      # installs phiversity + phiversity-serve
# (use --no-build-isolation on older pip that ships an ancient setuptools)
```

The frontend lives in `Frontend/` at the workspace root; generated videos in
`lectures/`; saved chat threads in `chats/`.

## Configuration

Copy `.env.example` to `.env`. Any OpenAI-compatible endpoint works:

| Provider | `LLM_BASE_URL` | `LLM_MODEL` example |
|----------|----------------|---------------------|
| OpenAI | `https://api.openai.com/v1` | `gpt-4o-mini` |
| NVIDIA NIM | `https://integrate.api.nvidia.com/v1` | `meta/llama-3.1-70b-instruct` |
| Ollama (local, no key) | `http://localhost:11434/v1` | `llama3.1` |
| vLLM (local, no key) | `http://localhost:8000/v1` | *your model* |
| Anthropic (`--provider anthropic`) | — | `claude-sonnet-4-20250514` |

Variables: `PHIVERSITY_PROVIDER`, `LLM_API_KEY` (also `OPENAI_API_KEY` /
`NVIDIA_API_KEY` / `ANTHROPIC_API_KEY`), `LLM_BASE_URL` (also
`OPENAI_BASE_URL`), `LLM_MODEL` (also `OPENAI_MODEL`),
`PHIVERSITY_VOICE` (default TTS voice).

Without an API key the twelve bundled sample lectures still generate
complete, narrated videos (`--demo` / the chat's sample-lecture chips).

## Command-line usage

```bash
# generate a lecture from a question (needs an LLM key)
phiversity "Explain why HBr adds to propene to give 2-bromopropane"

# read the question from a file; 1080p60 with burned-in subtitles
phiversity --file problem.md --captions -q h

# bundled sample lectures — no API key needed
phiversity --demo                      # the Pythagorean theorem
phiversity --demo hbr-propene          # Markovnikov addition (chemistry)

# interactive: follow-up questions append narrated segments
phiversity "Explain derivatives" --interactive

# serve the web application
phiversity-serve                       # http://127.0.0.1:8787
```

Key flags: `--tts edge|gtts|silence`, `--voice NAME`, `--rate "+10%"`,
`-q l|m|h` (480p15 / 720p30 / 1080p60), `--max-segments N`,
`--captions`, `--theme auto|math|lab|spatial|data|paper`,
`--intro-clip PATH` / `--no-intro-clip`, `--transitions none|flip`,
`--max-gap SEC` (auto-pacing threshold), `--heal-attempts N`,
`--render-timeout SEC`, `--provider`, `--model`, `--base-url`, `--api-key`.

## Web application

```bash
phiversity-serve               # or: --host 0.0.0.0 --port 8787 --root .
```

Open **http://127.0.0.1:8787**. The landing site routes to the app; login
(local mode, no accounts) lands in the chat.

| Page | What it does |
|------|--------------|
| `/chat.html` | the main UI: ask questions, watch live progress, play results; conversations persist and are reopenable from the recent-chats drawer (🕘) |
| `/app/library.html` | every generated lecture plus **Recent chats** — click a chat to reopen its conversation and videos |
| `/app/templates.html` | sample-lecture videos embedded directly, YouTube-style |
| `/app/generate/item.html?id=…` | live render progress: stage, progress bar, streaming pipeline log, player on completion |
| `/app/recent.html`, `/app/projects.html`, `/app/search.html` | recent videos, all lectures with delete, and full-text search |
| `/app/notifications.html` | render jobs of the current session |
| `/status.html` | live service health |

Jobs render sequentially on a worker thread; nothing leaves the machine.

## REST API reference

| Method & path | Purpose |
|---------------|---------|
| `GET /api/config` | bundled topics, themes, voices, `llm_configured` |
| `POST /api/generate` | start a job: `{question}` (LLM) or `{topic}` (bundled), plus optional `quality`, `voice`, `tts`, `theme`, `captions`, `transitions`, `max_segments` → `202 {id}` |
| `GET /api/jobs` · `GET /api/jobs/{id}` | job list · live status, stage, progress, log tail |
| `GET /api/lectures` | all generated lectures from their manifests |
| `GET /api/search?q=` | full-text search over lectures |
| `GET /api/lectures/{slug}/video` | the MP4 (HTTP Range supported) |
| `DELETE /api/lectures/{slug}` | delete a lecture |
| `GET /api/chats` | saved chat threads (newest first, with video refs) |
| `GET/POST/DELETE /api/chats/{id}` | open, save, delete a conversation |
| `GET /api/status` | service health |

## Visual system

Every scene receives a **kit** preamble with the resolved palette and
reusable helpers:

- **Semantic colors** (`T.<role>`) — variables blue, constants yellow,
  intermediate results violet, final answers green, warnings coral, force /
  velocity / acceleration / gravity vector colors, conventional element
  colors (C, H, O, N, S, Cl, P, Br), bonds, and a red `cancel_mark`.
  Roles keep their meaning across scenes; WCAG contrast is validated per
  preset.
- **Presets** — `math` (Mathematical Focus), `lab` (Scientific Laboratory),
  `spatial` (3D/molecular), `data`, and the light `paper` theme. The planner
  picks one per lesson; `--theme` overrides.
- **Camera kit** — `zoom_to`, `pan_to`, `camera_reset`, `follow`/`unfollow`
  (framing computed from the target's dimensions), `orbit_start`,
  `zoom_3d`.
- **Live geometry** — `graph_point`, `secant_line`, `tangent_line` (real
  numeric derivatives via `ValueTracker` updaters), `riemann_rectangles`,
  `scaled_bar`.
- **Emphasis** — `emphasize`, `dim_except` / `restore_emphasis`,
  `cancel_terms` (red 45° cancellation strike), `strike_through`.
- **Layout safety** — `wrap_text`, `fit_width` so long user questions never
  run off screen.

## Solution formats

The planner classifies each lesson and the coder follows the matching
academic template:

- **numerical** — Given (Data, SI-converted) → To Find (`v = ?`) → Formula →
  Calculation with visible intermediate steps and red cancellation strikes →
  boxed Final Answer **with SI units**
- **derivation** — core physical law named first, sequential one-step-per-line
  algebra with connecting phrases, sign/vector discipline, graphs and
  diagrams, integration limits explained with Riemann rectangles, proportional
  quantities shown as growing bars
- **inorganic-reaction** — balanced equations, temperature/pressure above the
  arrow, catalyst below (`\overset`/`\underset`), `\rightleftharpoons` for
  reversible, mandatory byproducts, `\Delta H` notation
- **organic-reaction** — condensed structural formulas, reagent/solvent
  placement rules, all inorganic byproducts, named-reaction media, numbered
  multi-step conversions
- **aromatic** — hexagon rings drawn (never bare `C₆H₅X`), EAS format, o/p-
  vs meta-directors with the major product marked

## Quality guarantees

1. **Static validation** — generated code may only `from manim import *`; no
   file, network, or eval access; rendered in an isolated workdir with a hard
   timeout
2. **Self-healing** — render errors return to the LLM for repair (default 2
   attempts)
3. **Auto-pacing** — timeline estimation before render, gap measurement after,
   paced re-render if the freeze would exceed `--max-gap`
4. **Layout lint** — detects "boxed before repositioned" overlap bugs
5. **Edge-clip detection** — sampled frames are checked for text-height
   clipping at the frame edges (persistent clipping only; full-bleed lines
   and zoomed graphs are ignored)
6. **Effect verification** — every planned effect (camera, zoom, highlight,
   dynamic relationship, 3D, diagram, cancellation, integration) must be
   evident in the generated code; findings are logged and recorded in the
   manifest
7. **Narration sync** — per-segment duration probing with last-frame freeze /
   audio padding at every boundary

## Bundled sample lectures

Twelve fully hand-authored lessons demonstrate every capability (usable
without any API key):

| Topic | Subject | Demonstrates |
|-------|---------|-------------|
| `pythagoras` | math | question card, worked proof |
| `fma` | physics | Newton's second law with a cart example |
| `car-friction` | physics | moving car, camera zoom to the tire, force diagram, v–t graph |
| `spring-blocks` | physics | two-block spring system, energy bar chart, SHM graph |
| `derivative` | math | secant→tangent with live trackers, multi-scale camera zoom |
| `unit-circle` | math | rotating circle driving live sin/cos projections |
| `surface3d` | math/3D | orbiting camera over a 3D surface, cross-section to 2D |
| `quadratic` | math | in-place color-graded factoring, answer reveal |
| `vectors` | physics | live resultant updating as the force angle changes |
| `methane` | chemistry | 2D drawing rebuilt as a 3D tetrahedron, 109.5° reveal |
| `hbr-propene` | chemistry | Markovnikov mechanism, energy profile, Eₐ labels, both products |
| `kinematics-numerical` | physics | full exam numerical format with cancellation strike and Riemann rectangles |

## Testing

```bash
cd phiversity
PYTHONPATH=src python3 -m pytest tests/ -q                  # full suite
PYTHONPATH=src python3 -m pytest tests/ -q -k "not integration"   # fast
PYTHONPATH=src python3 -m phiversity.cli --demo --tts silence   # smoke run
```

The suite covers: theme contrast and palettes, the director (plans,
transitions, effect verification), JSON/LLM plumbing with fake clients,
code validation and layout lint, pacing and timing, compose transitions
(xfade/cuts), TTS engines, the REST server (jobs, lectures, chats, search,
status, delete, Range streaming, static traversal guards), and full offline
integration renders.

## Output layout

```
lectures/<slug>/
├── lecture.mp4        the final narrated lecture
├── manifest.json      title, question, format, theme, per-segment
│                       narrations, transitions, and effect-verification notes
└── work/              per-segment audio, scene code, renders (reused on re-runs)
phiversity.db          SQLite database: every render job (surviving restarts),
                       all chat threads, and a searchable lecture index
Frontend/              the Phiversity web application
```

The database is created automatically on first `phiversity-serve` start (and
migrated from the earlier `chat-thread.json` / `chats/*.json` files once).
Renders that were still running when the server stopped are marked as
interrupted; completed jobs and chats survive every restart. The lecture
index is refreshed from the on-disk manifests on start and after each
completed render, so it always mirrors `lectures/`.

## Troubleshooting

- **"no API key configured"** — set `LLM_API_KEY` in `.env`, or use
  `--demo <topic>` / the sample-lecture chips
- **Robotic or missing voice** — `edge-tts`/`gTTS` need internet; the pipeline
  degrades to silence rather than failing
- **`MathTex` errors in LLM scenes** — install LaTeX; the coder prompt
  automatically switches to unicode text when LaTeX is absent
- **3D scenes render slowly** — increase `--render-timeout` (the methane
  demo needs ~10 min at 720p)
- **Old pip cannot build the package** — use
  `pip install --no-build-isolation .`
- **Server changes not visible** — static files are re-read per request;
  restart `phiversity-serve` only after Python changes
