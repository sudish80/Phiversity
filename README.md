LLM-based Manim Question Solver with Voiceover

Overview
- Takes a natural language question, uses an LLM to generate a structured solution (summary, steps, formulas), then animates the result in Manim with a synthesized voiceover.

Setup
- Ensure the project virtual environment is active or use the included `.venv`.
- Optional: set `OPENAI_API_KEY` to enable real LLM answers. Without it, a helpful placeholder solution is used.

Install Dependencies
- Dependencies are declared in `pyproject.toml`. If needed, install using your venv:

Windows (PowerShell):
```
.venv\Scripts\pip install -U pip
.venv\Scripts\pip install -e .
```

Usage
- Quick run with a question:

Windows (PowerShell):
```
python run_animation.py "Explain angular momentum conservation in collisions"
```

- Or interactively (it will prompt for input):
```
python run_animation.py
```

Two-LLM Orchestrator (ChatGPT + DeepSeek)
- New CLI to split roles: ChatGPT crafts the solver prompt; DeepSeek returns structured JSON (solution + animation plan).

Windows (PowerShell):
```
python -m scripts.orchestrator.run_orchestrator "Explain angular momentum conservation in collisions"
```

Outputs to `media/texts/solution_plan.json` by default. Use `--out path.json` to override.

Local Web UI (Frontend)
- Start a small FastAPI server that serves a web page to run the orchestrator + pipeline and view the final video.

Windows (PowerShell):
```
# Ensure venv is active
.venv\Scripts\Activate.ps1

# Install any missing packages used by the server (first time only)
.venv\Scripts\pip install aiofiles python-dotenv

# Run the server
python -m uvicorn scripts.server.app:app --reload --port 8000
```

Then open http://127.0.0.1:8000 in your browser.
- Enter a problem statement and click Run.
- Optionally uncheck "Run Orchestrator" and provide a path to an existing JSON plan file instead.
- Toggle "Voice-first" and "Element-level Audio" as needed. The page will poll job status and show logs and the resulting video when finished.

JSON → Manim → Voice → Sync (End-to-end)
- Generate the final MP4 from a question (requires `OPENAI_API_KEY` and `DEEPSEEK_API_KEY`) or from an existing JSON file.

From a question:
```
python -m scripts.pipeline --question "Explain angular momentum conservation in collisions" --out-dir media/videos/pipeline_output
```

From an existing JSON (e.g., produced by the orchestrator):
```
python -m scripts.pipeline --json media/texts/solution_plan.json --out-dir media/videos/pipeline_output
```

The pipeline does:
- Orchestrate (optional) → `solution_plan.json`
- Render silent Manim video → `silent.mp4`
- Generate scene-wise voiceover → `voice/scene_*.mp3|wav`
- Overlay audio on video → `final.mp4`

Voice-first mode (frame-accurate):
```
python -m scripts.pipeline --question "Explain angular momentum conservation" --out-dir media/videos/pipeline_voice_first --voice-first
```
This generates audio first, measures durations, times each scene with `self.wait(duration)`, then renders and muxes audio for tight sync.

Environment Variables
- `OPENAI_API_KEY`: Enables LLM responses via OpenAI.
- `OPENAI_MODEL` (optional): Override model name (default: `gpt-4o-mini`).
- `DEEPSEEK_API_KEY`: Enables DeepSeek solver via OpenAI-compatible API.
- `DEEPSEEK_MODEL` (optional): Override model (e.g., `deepseek-chat` or `deepseek-reasoner`).
- `DEEPSEEK_BASE_URL` (optional): Override base URL (default `https://api.deepseek.com`).
- `GEMINI_API_KEY` or `GOOGLE_API_KEY`: Enables Gemini (Google Generative AI) solver fallback.
- `GEMINI_MODEL` (optional): Override model (e.g., `gemini-1.5-flash` or `gemini-1.5-pro`).
- `VOICE_ENGINE`: `gtts` (default) or `pyttsx3`.
- `MANIM_QUALITY`: `low|medium|high|production` (adapter uses `medium` default).

Supported elements in the JSON animation plan:
- `Text`: Plain text content.
- `MathTex`: LaTeX math (falls back to Text if rendering fails).
- `Axes`: Optional `style.x_range`, `style.y_range`, `style.x_label`, `style.y_label`, `style.color`.
- `Graph`: Support single or multiple curves and parametric mode:
	- Function: `content: "sin(x)"`, optional `style.x_range: [a,b]`, `style.color`.
	- Parametric: in `style`: `{ mode: "parametric", x: "cos(t)", y: "sin(t)", t_range: [0, 6.283], color: "RED" }`.
	- Multiple curves: `style.curves` = array of curve objects, each with `mode`, `content` or `x/y`, `x_range` or `t_range`, optional `color` and `label`.
	- Legend: If any curve has `label`, a small legend appears at `UR`.
- `Highlight`: Surrounds the last element (or match by exact text) with a rectangle; optional `style.color`.

Per-element timings (optional):
- Each element may include `timing` with `{ start, end, transition_in, transition_out }`.
- `transition_in`: `Write|FadeIn|Create`; `transition_out`: `FadeOut|Uncreate`.
- In voice-first mode, the scene timeline aligns to audio duration and elements respect `start/end` offsets.

Per-element audio (lip-sync):
- Add `voiceover` at element level to generate audio per element.
- Run with per-element audio:
```
python -m scripts.pipeline --json media/texts/solution_plan.json --out-dir media/videos/pipeline_el_audio --voice-first --element-audio
```
- The pipeline measures each element’s audio length and, if no explicit timings are set, assigns `start/end` automatically in order.

Easing and durations:
- Each element can specify `timing.easing` (`linear|smooth|rush_from|rush_into|there_and_back|ease_in_sine|ease_out_sine`) and `timing.duration_in`, `timing.duration_out`.

3D support:
- If any element of type `Parametric3D` or `Axes3D` is present, the scene uses `ThreeDScene` and sets a default camera orientation.

Outputs
- Generated files are stored in `outputs/`:
- `solution.json`: Question + structured solution.
- `voiceover.wav`: Synthesized narration used in the animation.

Notes
- Voiceover uses `pyttsx3` (Windows SAPI5) and saves a WAV file.
- The Manim scene (`LLMScene`) displays the problem, summary, steps, and formulas; LaTeX rendering falls back to text if an expression fails.

## PDF Q&A (Extract + Ask LLM)

Use the new CLI to extract a prompt/context from a PDF and ask a question. It supports full-text extraction or marker-delimited prompts.

Install dependency (if not already installed via editable install):

Windows (PowerShell):
```
.venv\Scripts\pip install -e .
```

Run (Module mode preferred):
```
python -m scripts.pdf_qa path\to\file.pdf -q "What are the key assumptions?"
```

With prompt markers inside the PDF (case-insensitive):
```
python -m scripts.pdf_qa path\to\file.pdf \
	--start-marker "PROMPT START" --end-marker "PROMPT END" \
	-q "Generate a concise summary"
```

Environment variables:
- `OPENAI_API_KEY`: Enables LLM responses via OpenAI. If not set, the tool runs in a dry-run mode and prints the message preview.
- `OPENAI_MODEL` (optional): Override model (default: `gpt-4o-mini`).

Tips:
- Use `--max-chars` to bound the context length (default 120k).
- If markers are not found and `--no-fallback` is not set, the tool uses the full PDF text as context.
