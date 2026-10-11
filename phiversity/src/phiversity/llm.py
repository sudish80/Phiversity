"""LLM integration: planning lectures from a question and coding Manim scenes.

Supports any OpenAI-compatible endpoint (OpenAI, NVIDIA NIM, Ollama, vLLM,
LM Studio, ...) and the Anthropic Messages API.
"""

from __future__ import annotations

import json
import re

import requests

from .config import LLMConfig
from .director import (EFFECT_PLAYBOOK, SELECTION_RULES, VISUAL_PLAN_SCHEMA,
                       describe_plan, normalize_format,
                       normalize_transition, normalize_visual_plan,
                       transition_howto)

# --------------------------------------------------------------------------
# Prompts
# --------------------------------------------------------------------------

PLANNER_SYSTEM = """\
You are an expert educator and animation director designing a short
narrated lecture video.

Given a user's question or topic, break the explanation into a sequence of
2 to {max_segments} segments. Each segment is one beat of the lecture:
one idea, spoken as natural voice-over narration.

The video opens with a QUESTION card: the user's question, cleaned up, is
printed on screen while it is read aloud, and the situation it describes
is sketched underneath. Return it in the "question" object:
- "display": the user's question rewritten as a clean, grammatically
  correct question for display. Fix grammar and punctuation but keep the
  meaning EXACT, and typeset mathematical symbols and numbers with LaTeX
  inside $...$ (for example "$f_k = 5\\\\,\\\\mathrm{{N}}$").
- "speech": the same question written to be read aloud - no LaTeX, with
  numbers and units spelled out in words.

VISUAL PLANNING - you are also the animation director. For every segment,
attach a "visual" plan that decides when transitions, camera movement,
zooming, highlighting, diagrams, dynamic geometry, or three-dimensional
views are warranted by the CONTENT. Choose the simplest visualization
that clearly explains the concept; never order an effect the lesson does
not need. Also pick one "preset" for the whole lecture: the visual theme
"math" (algebra, calculus, geometry), "lab" (experiments, physics
apparatus), "spatial" (3D solids, molecules, fields), "data" (statistics,
charts), or "paper" (light notebook look).

SOLUTION FORMAT - also classify the lesson as one "format" so the scenes
follow the right academic template:
- "numerical" for worked physics/chemistry numericals (Given / To Find /
  Formula / Calculation / boxed Final Answer with SI units)
- "inorganic-reaction" for reaction equations (conditions above the
  arrow, catalyst below, balanced, byproducts, delta-H)
- "organic-reaction" for organic chemistry (structural formulas, reagents,
  solvents, byproducts, named reactions)
- "aromatic" for benzene and derivatives (draw rings, EAS, o/m/p directors)
- "derivation" for proofs and derivations (core law first, sequential
  algebra, diagrams, integration and cancellation visuals)
- "conceptual" when none of the above applies, or "mixed" when several do.

{visual_schema}

Narration rules:
- Conversational, clear, engaging. A real teacher speaking to a student.
- 1 to 4 sentences per segment. Short beats keep animation and voice in sync.
- The first segment continues straight from the question card by
  visualizing the situation it describes; later segments analyze, zoom
  into the interesting details, give a concrete example or result, and
  finish with a short wrap-up.
- Use plain speakable text (no markdown, no LaTeX in narration; spell math
  out in words where possible).

Respond with ONLY valid JSON, no markdown fences, in this exact shape:
{{"title": "<short lecture title>", "preset": "<math|lab|spatial|data|paper>", "format": "<numerical|inorganic-reaction|organic-reaction|aromatic|derivation|conceptual|mixed>", "question": {{"display": "<cleaned question with $...$ LaTeX>", "speech": "<read-aloud version>"}}, "segments": [{{"narration": "<text>", "visual": {{...}}}}, ...]}}\
"""

CODER_SYSTEM = """\
You are an expert Manim Community developer (manim >= 0.18, API: from manim import *).
You write clean, self-contained Manim scenes for a narrated lecture video.

For each scene you are given its exact class name, the spoken narration,
and the duration of its voice-over audio in seconds. Write one Python
module per scene containing exactly one Scene class.

Hard rules:
- First line must be: from manim import *
- NO other imports. No file, network, random, subprocess, os, or sys usage.
  No external images, SVGs, sounds, or custom assets.
- One class only, with the exact class name given. Use (Scene): normally,
  or (MovingCameraScene): when the scene must zoom in or out.
- Everything must fit and stay readable on a 16:9 frame. Keep font sizes
  >= 28 (smaller is fine inside zoomed camera frames) and positions away
  from the edges.
- Prefer built-in shapes: Text, MathTex, Tex, Axes, NumberPlane, Line,
  Circle, Polygon, Arrow, Brace, BarChart, SurroundingRectangle,
  transforms, etc.
{latex_line}
Visual richness - make it feel like a real lecture, not a slideshow:
- MODEL THE SITUATION: draw the physical objects the question describes
  (cars, roads, ramps, blocks, ropes, springs, planets) from basic shapes
  (RoundedRectangle, Circle, Line, Polygon, Arc) and animate them
  (rolling, sliding, swinging) as the narration describes them.
- GRAPHS: use Axes(...) with .plot(...) for curves such as velocity-time
  or position-time graphs; NumberPlane for coordinate geometry. Label
  the axes with short Text.
- CHARTS: use BarChart(...) when comparing quantities.
- VECTOR DIAGRAMS: draw forces and velocities as colored Arrow(...)s with
  short MathTex labels; mark angles with Arc; attach each label to its
  own arrow with .next_to.
- AXIOMS / KEY STATEMENTS: box the important formula or takeaway with
  SurroundingRectangle (or underline/brace it), centered on screen.
- ZOOM: for close-ups (a tire, a contact point, a small region) use a
  MovingCameraScene and animate self.camera.frame.animate.set(width=...)
  .move_to(...) to zoom in, and zoom back out when done.
- Color-code consistently (e.g. forces one color, velocities another)
  and use TransformMatchingTex / ReplacementTransform to evolve formulas.
- Manim version note: pass animation options to self.play(..., run_time=...,
  rate_func=...), never to .animate(...); zooming scenes use
  self.camera.frame.animate.set(width=...).move_to(...).

Layout discipline - NEVER let two things overlap:
- Position every mobject BEFORE creating a box, underline, or brace
  around it: SurroundingRectangle captures the position at creation
  time, so create it only after its target reaches its final place.
- Compose with .next_to(...), .arrange(...), .to_edge(...),
  .to_corner(...) instead of raw coordinates, and keep at least 0.5
  units of margin from the frame edges.
- NOTHING may run off screen: the frame is ~14.2 units wide. Long or
  user-entered question text MUST be split with wrap_text(text,
  font_size) into rows arranged DOWN; any single wide mobject must go
  through fit_width(mobj) before it is shown.
- When adding new content in a busy area, first FadeOut or Shift what
  is already there. Two mobjects' bounding boxes must never intersect.
- Keep any single line of text under about 12 units wide; wrap longer
  text into several rows and center them.
- Key statements, formulas, and the printed question must appear
  CENTERED on the screen.

Timing rules (critical):
- The scene's total play + wait time must be within about 1.5 seconds of the
  given audio duration. Add up run_time values and waits as you write.
- End with a final self.wait(...) so the total matches the target.
- Pace animations to the narration: write equations as they are being
  explained, transform them as the idea develops.

{playbook}

Respond with ONLY valid JSON, no markdown fences, in this exact shape:
{{"segments": [{{"index": <int>, "code": "<full python source>"}}, ...]}}\
"""

CODER_USER_TEMPLATE = """\
Lecture title: {title}
Solution format for this lesson: {format_line}

Write one Scene class per scene below. The "audio_seconds" is how long the
voice-over lasts; match the scene duration to it.

{segments_block}\
"""


def _segment_block(i: int, seg: dict) -> str:
    scene_name = (seg.get("scene_name")
                  or f"Segment{seg.get('index', i)}")
    lines = [
        f"Scene {i} (class name: {scene_name})",
        f"narration: {seg['narration']}",
        f"audio_seconds: {seg['audio_duration']:.1f}",
    ]
    if seg.get("kind") == "question":
        lines.append("kind: QUESTION CARD")
        lines.append("question_display (print this EXACT text, it is "
                     f"already grammar-checked): {seg.get('question_display', '')}")
        lines.append("This is the opening card: while the narration reads "
                     "the question aloud, print the question CENTERED near "
                     "the top (Text for words, MathTex for each $...$ "
                     "piece, arranged into centered rows), and draw the "
                     "physical situation it describes in the lower half "
                     "as it is being read. Do not answer it yet.")
    plan = seg.get("visual")
    if plan:
        plan = normalize_visual_plan(plan)
        lines.append("visual plan for this scene (follow it, including the "
                     "transition, camera, zoom, highlight and color roles):")
        lines.append(describe_plan(plan))
        lines.append(transition_howto(plan.get("transition", "none"),
                                      {"summary": seg.get("previous_summary")}))
    if seg.get("previous_summary"):
        lines.append(f"the previous scene ended with: "
                     f"{seg['previous_summary']}")
    return "\n".join(lines) + "\n\n"

HEAL_SYSTEM = """\
You are an expert Manim Community developer (manim >= 0.18, from manim import *).
A scene you wrote failed to render. Fix the code so it renders cleanly.
Keep the same class name (or its MovingCameraScene variant) and the same
educational content and pacing. If the failure was a layout problem
(overlapping or off-screen elements), fix the positioning too: position
mobjects with .next_to/.arrange before boxing them, and never let bounding
boxes intersect. Rules: only "from manim import *" as import; no external
assets or IO.

Respond with ONLY the raw fixed Python source code. No markdown fences, no prose.\
"""

HEAL_USER_TEMPLATE = """\
The following scene failed to render with manim.

ERROR (tail of output):
{error}

CODE:
{code}

Return the corrected full Python source, raw, no fences.\
"""

# --------------------------------------------------------------------------
# JSON / code extraction helpers
# --------------------------------------------------------------------------


def strip_code_fences(text: str) -> str:
    """Remove ``` / ```json fences and return the inner text."""
    text = text.strip()
    fence = re.compile(r"^```[a-zA-Z0-9_+-]*\s*\n(.*?)\n?```\s*$", re.DOTALL)
    match = fence.match(text)
    if match:
        return match.group(1).strip()
    # tolerate stray fences around otherwise-plain content
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[: text.rfind("```")]
    return text.strip()


def extract_json(text: str) -> dict:
    """Parse a JSON object from an LLM reply (tolerates fences and prose)."""
    cleaned = strip_code_fences(text)
    for candidate in (cleaned, _first_braced(cleaned)):
        if candidate:
            try:
                parsed = json.loads(candidate)
                if isinstance(parsed, dict):
                    return parsed
            except json.JSONDecodeError:
                continue
    raise ValueError(f"LLM reply is not valid JSON: {text[:300]!r}")


def _first_braced(text: str) -> str | None:
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end > start:
        return text[start : end + 1]
    return None


def extract_code(text: str) -> str:
    """Extract raw Python source from an LLM reply."""
    cleaned = strip_code_fences(text)
    return cleaned


# --------------------------------------------------------------------------
# Client
# --------------------------------------------------------------------------


class LLMError(RuntimeError):
    pass


class LLMClient:
    """Minimal chat-completion client: OpenAI-compatible or Anthropic."""

    def __init__(self, cfg: LLMConfig):
        self.cfg = cfg
        self.session = requests.Session()

    # -- public API --------------------------------------------------------

    def complete(self, system: str, user: str, temperature: float | None = None,
                 max_tokens: int = 8192) -> str:
        temperature = self.cfg.temperature if temperature is None else temperature
        if self.cfg.provider == "anthropic":
            return self._anthropic(system, user, temperature, max_tokens)
        return self._openai(system, user, temperature, max_tokens)

    def complete_json(self, system: str, user: str, temperature: float = 0.4,
                      max_tokens: int = 8192) -> dict:
        """complete() + robust JSON parsing with one retry nudge."""
        for attempt in range(2):
            text = self.complete(system, user, temperature=temperature,
                                 max_tokens=max_tokens)
            try:
                return extract_json(text)
            except ValueError:
                if attempt == 0:
                    user = (user
                            + "\n\nREMINDER: reply with ONLY the raw JSON object. "
                              "No prose, no markdown fences.")
                else:
                    raise LLMError(f"Could not parse JSON from LLM: {text[:300]!r}")
        raise LLMError("unreachable")

    # -- providers ---------------------------------------------------------

    def _openai(self, system: str, user: str, temperature: float,
                max_tokens: int) -> str:
        url = f"{self.cfg.base_url}/chat/completions"
        payload = {
            "model": self.cfg.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        headers = {"Content-Type": "application/json"}
        if self.cfg.api_key:
            headers["Authorization"] = f"Bearer {self.cfg.api_key}"
        try:
            resp = self.session.post(url, json=payload, headers=headers,
                                     timeout=self.cfg.timeout)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            raise LLMError(f"LLM request failed: {exc}") from exc
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMError(f"Unexpected LLM response shape: {data}") from exc

    def _anthropic(self, system: str, user: str, temperature: float,
                   max_tokens: int) -> str:
        url = f"{self.cfg.base_url}/v1/messages"
        headers = {
            "x-api-key": self.cfg.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.cfg.model,
            "system": system,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [{"role": "user", "content": user}],
        }
        try:
            resp = self.session.post(url, json=payload, headers=headers,
                                     timeout=self.cfg.timeout)
            resp.raise_for_status()
            data = resp.json()
        except requests.RequestException as exc:
            raise LLMError(f"LLM request failed: {exc}") from exc
        try:
            return "".join(block.get("text", "")
                           for block in data["content"]
                           if block.get("type") == "text")
        except (KeyError, TypeError) as exc:
            raise LLMError(f"Unexpected LLM response shape: {data}") from exc

    # -- high-level lecture calls -------------------------------------------

    def plan_lecture(self, question: str, max_segments: int = 5) -> dict:
        """Phase 1: question -> titled plan with visual plans per segment."""
        user = (f"User question/topic: {question.strip()}\n\n"
                f"Plan the lecture segments and their visual plans now. "
                f"Respond with only the JSON object.")
        system = PLANNER_SYSTEM.format(max_segments=max_segments,
                                       visual_schema=VISUAL_PLAN_SCHEMA)
        plan = self.complete_json(system, user, temperature=0.5)
        return _normalize_plan(plan, max_segments)

    def plan_followup(self, question: str, title: str,
                      previous: list[str], max_segments: int = 3,
                      start_index: int = 0) -> dict:
        """Plan continuation segments that pick up where the lecture ended."""
        context = "\n".join(f"- {narration}" for narration in previous)
        user = (f"The lecture so far (title: {title}) covered:\n{context}\n\n"
                f"The viewer asks: {question.strip()}\n\n"
                f"Plan 1 to {max_segments} NEW segments that answer the follow-up "
                f"question and flow naturally after the segments above. "
                f"Respond with only the JSON object.")
        system = PLANNER_SYSTEM.format(max_segments=max_segments,
                                       visual_schema=VISUAL_PLAN_SCHEMA)
        plan = self.complete_json(system, user, temperature=0.5)
        return _normalize_plan(plan, max_segments, start_index=start_index)

    def code_scenes(self, title: str, segments: list[dict],
                    latex: bool = True,
                    playbook: str = "",
                    lesson_format: str = "") -> list[str]:
        """Phase 2: narrations + visual plans -> one code string per scene."""
        system = _coder_system(latex, playbook=playbook)
        block = "".join(_segment_block(i, seg)
                        for i, seg in enumerate(segments))
        if lesson_format and lesson_format not in ("conceptual", "mixed"):
            format_line = (f"{lesson_format} - follow the matching SOLUTION "
                           f"FORMAT rules exactly (headers, arrow conditions, "
                           f"units, cancellation strikes, boxed answers)")
        else:
            format_line = "conceptual - no special template required"
        user = CODER_USER_TEMPLATE.format(title=title,
                                          format_line=format_line,
                                          segments_block=block)
        data = self.complete_json(system, user, temperature=0.3)
        codes = _normalize_codes(data, len(segments))
        return codes

    def heal_code(self, code: str, error: str) -> str:
        """Ask the LLM to fix scene code that failed to render."""
        text = self.complete(HEAL_SYSTEM,
                             HEAL_USER_TEMPLATE.format(error=error[-2000:],
                                                       code=code),
                             temperature=0.2)
        return extract_code(text)


def _coder_system(latex: bool, playbook: str = "") -> str:
    if latex:
        latex_line = ("- LaTeX IS available: you may use MathTex(...) for "
                      "equations. Keep formulas simple and compileable.")
    else:
        latex_line = ("- LaTeX is NOT available: never use Tex or MathTex. "
                      "Use Text(...) with unicode symbols instead.")
    return CODER_SYSTEM.format(latex_line=latex_line, playbook=playbook)


def _normalize_plan(plan: dict, max_segments: int,
                    start_index: int = 0) -> dict:
    from .theme import normalize_preset
    title = str(plan.get("title") or "Lecture").strip() or "Lecture"
    question = _normalize_question(plan.get("question"))
    preset = normalize_preset(plan.get("preset"))
    lesson_format = normalize_format(plan.get("format"))
    raw = plan.get("segments")
    if not isinstance(raw, list) or not raw:
        raise LLMError("LLM plan has no segments")
    segments = []
    for i, item in enumerate(raw[:max_segments]):
        visual = None
        if isinstance(item, str):
            narration = item
        elif isinstance(item, dict):
            narration = str(item.get("narration") or item.get("text") or "").strip()
            visual = item.get("visual")
        else:
            continue
        if narration:
            entry = {"index": start_index + i, "narration": narration}
            if isinstance(visual, dict) or visual:
                entry["visual"] = normalize_visual_plan(visual)
            segments.append(entry)
    if not segments:
        raise LLMError("LLM plan has no usable narrations")
    return {"title": title, "question": question, "preset": preset,
            "format": lesson_format, "segments": segments}


def _normalize_question(raw: object) -> dict | None:
    """Accept question as {display, speech}, a plain string, or absent."""
    if isinstance(raw, dict):
        display = str(raw.get("display") or "").strip()
        if not display:
            return None
        speech = str(raw.get("speech") or "").strip() or display
        return {"display": display, "speech": speech}
    if isinstance(raw, str) and raw.strip():
        text = raw.strip()
        return {"display": text, "speech": text}
    return None


def _normalize_codes(data: dict, expected: int) -> list[str]:
    raw = data.get("segments")
    if not isinstance(raw, list):
        raise LLMError("LLM code response has no segments")
    codes: dict[int, str] = {}
    for item in raw:
        if isinstance(item, dict) and item.get("code"):
            idx = item.get("index")
            if not isinstance(idx, int):
                match = re.search(r"Segment(\d+)", str(item.get("scene_name", "")))
                idx = int(match.group(1)) if match else None
            if idx is None:
                idx = len(codes)
            codes[idx] = str(item["code"]).strip()
    ordered = [codes.get(i, "") for i in range(expected)]
    if not all(ordered):
        missing = [i for i, code in enumerate(ordered) if not code]
        raise LLMError(f"LLM did not return code for segments: {missing}")
    return ordered
