# Phiversity

**Ask a question. Get a narrated, animated lecture video.**

Phiversity turns questions about mathematics, physics, chemistry and more
into fully produced lecture videos: an LLM plans the lesson and writes the
[Manim](https://www.manim.community) animation code, a neural voice narrates
it, and ffmpeg assembles the final MP4 with synchronized visuals, camera
work, and exam-standard formatting.

```
question ─▶ LLM plans the lecture ─▶ TTS speaks each beat ─▶ LLM writes
Manim scenes timed to the narration ─▶ Manim renders (self-healing,
auto-paced, overflow-guarded) ─▶ ffmpeg aligns + stitches ─▶ lecture.mp4
```

## Watch a sample lecture

**Two-Block Spring System** (physics, 2 min) — the full narrated pipeline
output: your Intro clip plays first, then the printed question is read
aloud while the setup is drawn, followed by energy conservation, the
separation of the blocks, the SHM graph, and the energy bar chart.

**▶ [Watch the full video with narration](samples/spring-blocks.mp4)**

*(animated preview below — the real video has voice-over)*

![Spring-block lecture preview](samples/spring-blocks.gif)

More sample lectures render locally with a single command — no API key
needed:

```bash
phiversity --demo derivative      # secant → tangent, live camera zoom
phiversity --demo hbr-propene     # Markovnikov mechanism (chemistry)
phiversity --demo methane         # 2D drawing → 3D tetrahedron
phiversity --demo car-friction    # camera zoom to the tire, force diagram
phiversity --demo quadratic       # color-graded factoring, answer reveal
phiversity --demo kinematics-numerical   # exam-format numerical with
                                         # cancellation strikes + Riemann sums
```

## Repository layout

| Path | What it is |
|------|------------|
| [`phiversity/`](phiversity/) | the Python project — pipeline, visual director, themes, SQLite storage, REST server, and the full documentation in [`phiversity/README.md`](phiversity/README.md) |
| [`Frontend/`](Frontend/) | the Phiversity web application: chat-first generation UI, library, sample-lecture gallery, live render progress |
| `Intro.mp4` | optional brand clip, played before every generated lecture |

## Quick start

```bash
# 1. install the Python package
cd phiversity
pip install -r requirements.txt
pip install --no-build-isolation .

# 2. (optional) add an LLM key for your own questions
cp .env.example .env        # then edit .env

# 3. generate a lecture from a bundled sample - no API key needed
phiversity --demo pythagoras

# 4. serve the web app
phiversity-serve            # http://127.0.0.1:8787
```

Full documentation — architecture, configuration, the REST API, the visual
system, solution formats, and testing — lives in
[`phiversity/README.md`](phiversity/README.md).
