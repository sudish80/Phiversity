"""Pipeline orchestration: question -> lecture video with voice-over.

Stages:
  1. plan    : the LLM (or a bundled lecture) produces a titled plan: a
               QUESTION card plus narration segments, each carrying a
               VISUAL PLAN (the director decides transitions, camera
               movement, zooming, highlighting, dynamic geometry, 3D,
               diagrams and semantic color roles) and a visual preset
  2. speak   : TTS narrates the question and every segment; exact audio
               durations are probed
  3. code    : the LLM writes one Manim Scene per beat following its
               visual plan, timed to the audio; a theme "kit" preamble
               (semantic colors + camera/geometry/emphasis helpers) is
               injected into every scene file
  4. render  : Manim renders each scene (with LLM self-healing); the
               rendered code is verified against the planned effects
  5. compose : ffmpeg aligns voice and animation per segment, splices the
               user's Intro.mp4 in front, applies content-aware
               transitions between scenes (crossfades where the plan
               calls for them, continuity cuts elsewhere) and stitches
               the final lecture video

Interactive mode keeps the session open so the viewer can ask follow-up
questions; each answer is rendered as new segments and appended with fresh
voice-over.
"""

from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

from .compose import (align_and_mux, concat, normalize_foreign, smart_concat,
                      write_segment_srt)
from .config import PipelineConfig, detect_latex
from .director import (DEFAULT_CARD_VISUAL, EFFECT_PLAYBOOK, SELECTION_RULES,
                       normalize_visual_plan, suggest_transition,
                       verify_effects)
from .llm import LLMClient, LLMError
from .render import (QUALITY_FPS, QUALITY_SIZE, adjust_final_wait,
                     detect_edge_clipping, estimate_scene_duration,
                     lint_layout, render_scene, render_with_healing)
from .templates import (PAGE_FLIP_CODE, bundled_topics, demo_code,
                        demo_question_code, demo_plan, intro_segment,
                        normalize_topic)
from .theme import kit_source, normalize_preset
from .tts import ffprobe_duration, synthesize


def slugify(text: str, fallback: str = "lecture") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return slug[:40] or fallback


def build_playlist(segment_finals: list[Path], intro_clip: Path | None = None,
                   flip_clip: Path | None = None) -> list[Path]:
    """Ordering of the final concat: intro, then segments with a page-flip
    transition spliced between every pair of clips."""
    parts: list[Path] = []
    prev: Path | None = None
    if intro_clip is not None:
        parts.append(intro_clip)
        prev = intro_clip
    for final in segment_finals:
        if prev is not None and flip_clip is not None:
            parts.append(flip_clip)
        parts.append(final)
        prev = final
    return parts


def build_junctions(segments: list, intro_clip: Path | None) -> list[str]:
    """Content-aware transition type for every clip boundary.

    The intro clip crossfades into the lecture; every internal boundary
    uses the visual plan of the scene being entered (with a heuristic
    fallback when the planner did not specify one).
    """
    junctions: list[str] = []
    if intro_clip is not None:
        junctions.append("fade")
    for previous, current in zip(segments, segments[1:]):
        plan = current.visual or {}
        junctions.append(plan.get("transition")
                         or suggest_transition(previous.visual, plan))
    return junctions


@dataclass
class Segment:
    index: int
    scene_name: str
    narration: str
    code: str = ""
    kind: str = "body"                    # "body" | "question"
    question_display: str = ""
    visual: dict = field(default_factory=dict)
    effect_warnings: list = field(default_factory=list)
    audio: Path | None = None
    audio_duration: float = 0.0
    video: Path | None = None
    final: Path | None = None
    pre_aligned: bool = False   # rebuilt from disk: already aligned + muxed


@dataclass
class PipelineResult:
    title: str
    final_video: Path
    segments: list[Segment] = field(default_factory=list)


class Pipeline:
    def __init__(self, cfg: PipelineConfig, client: LLMClient | None,
                 log=print):
        self.cfg = cfg
        self.client = client
        self.log = log
        self.out_dir = Path(cfg.out_dir)
        self.work_dir = self.out_dir / "work"
        self.title = "Lecture"
        self.preset = normalize_preset(cfg.theme)
        self.kit = kit_source(self.preset)
        self.lesson_format = "conceptual"

    # ------------------------------------------------------------------ run

    def run(self, question: str) -> PipelineResult:
        """Full build: plan, speak, code, render, compose."""
        plan = self._plan(question)
        self.title = plan["title"]
        self.lesson_format = plan.get("format") or "conceptual"
        self._resolve_theme(plan)
        segments = self._build_segments(plan["segments"],
                                        question=plan.get("question"))
        return self._compose(segments)

    def followup(self, question: str, built: list[Segment]) -> list[Segment]:
        """Plan + build new segments continuing an existing lecture."""
        if self.client is None:
            raise LLMError("interactive follow-up needs an LLM (--demo has none)")
        plan = self.client.plan_followup(
            question, self.title,
            [s.narration for s in built],
            max_segments=self.cfg.max_segments,
            start_index=len(built))
        new = self._build_segments(plan["segments"],
                                   start_index=len(built))
        return built + new

    # ------------------------------------------------------------- theming

    def _resolve_theme(self, plan: dict) -> None:
        """CLI override > planned preset > content heuristic."""
        if self.cfg.theme and self.cfg.theme.strip().lower() != "auto":
            preset = normalize_preset(self.cfg.theme)
        elif plan.get("preset"):
            preset = normalize_preset(plan["preset"])
        elif any((s.get("visual") or {}).get("three_d")
                 for s in plan.get("segments", [])):
            preset = "spatial"
        else:
            preset = "math"
        self.preset = preset
        self.kit = kit_source(preset)
        self.log(f"  [+] theme : preset '{preset}' "
                 f"(semantic colors + camera/geometry kit injected)")

    # -------------------------------------------------------------- planning

    def _demo_topic(self) -> str:
        """Resolve the --demo flag (True or a topic string) to a topic key."""
        if isinstance(self.cfg.demo, str) and self.cfg.demo.strip():
            try:
                return normalize_topic(self.cfg.demo)
            except ValueError:
                raise LLMError(f"unknown --demo topic {self.cfg.demo!r}; "
                               f"available: {', '.join(bundled_topics())}")
        return "pythagoras"

    def _plan(self, question: str) -> dict:
        if self.cfg.demo:
            self.log(f"[1/5] plan : using bundled '{self._demo_topic()}' "
                     f"lecture (offline, no LLM)")
            return demo_plan(self._demo_topic())
        if self.client is None:
            raise LLMError("no LLM configured: set LLM_API_KEY (+ LLM_BASE_URL/"
                           "LLM_MODEL), or run with --demo")
        self.log(f"[1/5] plan : asking the LLM to structure: {question!r}")
        return self.client.plan_lecture(question, self.cfg.max_segments)

    # ------------------------------------------------------------ building

    def _build_segments(self, planned: list[dict], start_index: int = 0,
                        question: dict | None = None) -> list[Segment]:
        segments: list[Segment] = []
        # optional intro title card; the user's own Intro.mp4 (if any)
        # replaces it as the opener
        if self.cfg.intro and start_index == 0 and not self.cfg.intro_clip:
            audio, duration = self._speak(
                f"Welcome. In this lecture: {self.title}.", "audio_intro")
            info = intro_segment(self.title, duration)
            segments.append(Segment(0, info["scene_name"], info["narration"],
                                    info["code"], audio=audio,
                                    audio_duration=duration,
                                    visual=normalize_visual_plan(
                                        DEFAULT_CARD_VISUAL)))

        # the QUESTION card: the question printed on screen (grammar-checked,
        # LaTeX typeset) while it is read aloud, with the situation sketched
        question_seg: Segment | None = None
        if start_index == 0 and question:
            audio, duration = self._speak(question["speech"],
                                          "audio_question")
            question_seg = Segment(-1, "QuestionScene", question["speech"],
                                   kind="question",
                                   question_display=question["display"],
                                   audio=audio, audio_duration=duration,
                                   visual=normalize_visual_plan(
                                       DEFAULT_CARD_VISUAL,
                                       kind="question"))

        body = []
        for i, item in enumerate(planned):
            seg = Segment(start_index + i, f"Segment{start_index + i}",
                          str(item["narration"]))
            raw_visual = item.get("visual")
            seg.visual = (raw_visual if isinstance(raw_visual, dict) and
                          raw_visual.get("kind") else
                          normalize_visual_plan(raw_visual))
            body.append(seg)
        for seg in body:
            seg.audio, seg.audio_duration = self._speak(
                seg.narration, f"audio_{seg.scene_name}")

        coding = ([question_seg] if question_seg else []) + body
        self._write_codes(coding)
        for seg in segments + coding:
            self._render_one(seg)
        segments.extend(coding)
        return segments

    def _speak(self, narration: str, stem: str) -> tuple[Path, float]:
        audio_dir = self.work_dir / "audio"
        path, duration = synthesize(narration, audio_dir / f"{stem}.wav",
                                    self.cfg.tts)
        return path, duration

    def _write_codes(self, coding: list[Segment]) -> None:
        if self.cfg.demo:
            topic = self._demo_topic()
            for seg in coding:
                if seg.kind == "question":
                    seg.code = demo_question_code(topic)
                else:
                    seg.code = demo_code(topic, seg.index)
            self.log(f"[3/5] code : using bundled '{topic}' Manim code")
            return
        assert self.client is not None
        kinds = sum(1 for s in coding if s.kind == "question")
        self.log(f"[3/5] code : LLM writing {len(coding)} Manim scene(s) "
                 f"from their visual plans ({kinds} question card, "
                 f"{len(coding) - kinds} content)")
        payload = []
        for i, s in enumerate(coding):
            entry = {"index": i, "scene_name": s.scene_name,
                     "kind": s.kind, "question_display": s.question_display,
                     "narration": s.narration,
                     "audio_duration": s.audio_duration}
            if s.visual:
                entry["visual"] = s.visual
                if i > 0:
                    entry["previous_summary"] = (
                        f"{coding[i - 1].scene_name}: "
                        f"{coding[i - 1].visual.get('objective', '')}")
            payload.append(entry)
        playbook = EFFECT_PLAYBOOK + "\n\n" + SELECTION_RULES
        for attempt in range(2):
            try:
                codes = self.client.code_scenes(self.title, payload,
                                                latex=detect_latex(),
                                                playbook=playbook,
                                                lesson_format=self.lesson_format)
                for seg, code in zip(coding, codes):
                    seg.code = code
                return
            except LLMError as exc:
                if attempt == 1:
                    raise
                self.log(f"  [retry] scene coding failed ({exc}); retrying")

    def _render_one(self, seg: Segment) -> None:
        kind = " (question card)" if seg.kind == "question" else ""
        self.log(f"[4/5] render: {seg.scene_name}{kind} "
                 f"(voice {seg.audio_duration:.1f}s)")
        seg_dir = self.work_dir / "render" / seg.scene_name

        # layout lint: warn about (and record) the classic overlap bug
        for warning in lint_layout(seg.code):
            self.log(f"  [lint] {seg.scene_name}: {warning}")
            seg.effect_warnings.append(f"layout: {warning}")

        # auto-pacing: stretch the scene toward the measured voice length
        # BEFORE rendering, so the animation fills the narration naturally
        code = seg.code
        target = seg.audio_duration
        estimate = estimate_scene_duration(code)
        if target - estimate > 1.0:
            code = adjust_final_wait(code, target - estimate)
            self.log(f"  [pace] {seg.scene_name}: animation ~{estimate:.1f}s "
                     f"vs voice {target:.1f}s - final wait stretched")

        seg.video = render_with_healing(code, seg.scene_name, seg_dir,
                                        self.cfg.render, self.client,
                                        kit=self.kit, log=self.log)

        # verify: if a visible freeze gap remains, re-render once, paced
        max_gap = self.cfg.render.max_gap
        actual = ffprobe_duration(seg.video)
        gap = target - actual
        if gap > max_gap:
            patched = adjust_final_wait(code, gap + 0.1)
            self.log(f"  [pace] {seg.scene_name}: {gap:.1f}s freeze would "
                     f"remain - re-rendering with paced ending")
            try:
                paced = render_with_healing(patched, seg.scene_name,
                                            seg_dir / "paced",
                                            self.cfg.render, self.client,
                                            kit=self.kit, log=self.log)
                if target - ffprobe_duration(paced) < gap:
                    seg.video = paced
                    seg.code = patched
            except Exception as exc:  # noqa: BLE001 - pacing is best-effort
                self.log(f"  [pace] paced re-render failed ({exc}); "
                         f"keeping the freeze-frame padding")

        # overflow check: nothing may be clipped at the frame edges
        clipped = detect_edge_clipping(seg.video)
        if clipped:
            sides = " and ".join(clipped)
            message = (f"content is cut off at the {sides} frame edge - "
                       f"the question text runs out of the screen")
            self.log(f"  [clip] {seg.scene_name}: {message}")
            seg.effect_warnings.append(f"overflow: {message}")
            if self.client is not None:
                fixed = None
                try:
                    fixed = self.client.heal_code(
                        seg.code,
                        "The rendered frames show content clipped at the "
                        f"{sides} frame edge. Rewrite the offending long "
                        "text: split it with wrap_text(text, font_size) "
                        "into shorter centered rows, or pass wide mobjects "
                        "through fit_width(). Keep the same class name, "
                        "content and pacing.")
                    from .render import validate_code
                    fixed = validate_code(fixed, seg.scene_name)
                except Exception as exc:  # noqa: BLE001 - healing is best-effort
                    self.log(f"  [clip] overflow healing failed ({exc})")
                if fixed:
                    try:
                        retry = render_with_healing(fixed, seg.scene_name,
                                                    seg_dir / "fit",
                                                    self.cfg.render,
                                                    self.client,
                                                    kit=self.kit,
                                                    log=self.log)
                        if not detect_edge_clipping(retry):
                            seg.video = retry
                            seg.code = fixed
                            seg.effect_warnings.pop()  # resolved
                            self.log(f"  [clip] {seg.scene_name}: overflow "
                                     f"fixed")
                    except Exception as exc:  # noqa: BLE001
                        self.log(f"  [clip] overflow re-render failed "
                                 f"({exc})")

        if seg.visual:
            seg.effect_warnings += verify_effects(seg.code, seg.visual)
            for warning in seg.effect_warnings:
                self.log(f"  [check] {seg.scene_name}: {warning}")

    # ------------------------------------------------------------ composing

    def _compose(self, segments: list[Segment]) -> PipelineResult:
        self.log("[5/5] compose: aligning voice with animation, stitching")
        seg_dir = self.work_dir / "segments"
        for seg in segments:
            if seg.pre_aligned and seg.final and Path(seg.final).is_file():
                continue   # reconstructed: keep the existing aligned encode
            srt = None
            if self.cfg.captions:
                video_len = ffprobe_duration(seg.video)
                total = max(video_len, seg.audio_duration)
                srt = write_segment_srt(seg.narration, total,
                                         seg_dir / f"{seg.scene_name}.srt")
            seg.final = align_and_mux(seg.video, seg.audio,
                                      seg_dir / f"{seg.scene_name}.mp4", srt)
        intro_clip = self._prepare_intro_clip()
        if self.cfg.transitions == "flip" and len(segments) > 1:
            flip_clip = self._prepare_flip_clip()
            parts = build_playlist([s.final for s in segments], intro_clip,
                                   flip_clip)
            final = concat(parts, self.out_dir / "lecture.mp4")
        else:
            junctions = build_junctions(segments, intro_clip)
            parts = ([intro_clip] if intro_clip else []) + \
                    [s.final for s in segments]
            final = smart_concat(parts, junctions,
                                 self.out_dir / "lecture.mp4")
        self._write_manifest(segments)
        total = sum(s.audio_duration for s in segments)
        self.log(f"done  : {final}  ({len(segments)} segments, "
                 f"~{total:.0f}s of narration)")
        return PipelineResult(self.title, final, segments)

    def _foreign_geometry(self) -> tuple[int, int, int]:
        size = QUALITY_SIZE.get(self.cfg.render.quality, (1280, 720))
        return size[0], size[1], QUALITY_FPS.get(self.cfg.render.quality, 30)

    def _prepare_intro_clip(self) -> Path | None:
        """Normalize the user's Intro.mp4 so it stitches in front."""
        src = self.cfg.intro_clip
        if not src:
            return None
        src = Path(src)
        if not src.is_file():
            self.log(f"  [warn] intro clip {src} not found; skipping")
            return None
        self.log(f"  [+] intro : prepending {src.name}")
        w, h, fps = self._foreign_geometry()
        return normalize_foreign(src, self.work_dir / "foreign" / "intro.mp4",
                                 w, h, fps)

    def _prepare_flip_clip(self) -> Path | None:
        """Render the page-flip once and normalize it for splicing."""
        self.log("  [+] transitions: rendering page-flip")
        w, h, fps = self._foreign_geometry()
        raw = render_scene(PAGE_FLIP_CODE, "PageFlip",
                            self.work_dir / "transitions", self.cfg.render,
                            kit=self.kit)
        return normalize_foreign(raw, self.work_dir / "transitions" / "flip.mp4",
                                 w, h, fps)

    def _write_manifest(self, segments: list[Segment]) -> None:
        question = next((s.question_display for s in segments
                         if s.kind == "question"), None)
        manifest = {
            "title": self.title,
            "video": "lecture.mp4",
            "question": question,
            "theme": {"preset": self.preset},
            "format": self.lesson_format,
            "segments": [
                {"scene": s.scene_name, "narration": s.narration,
                 "voice_seconds": round(s.audio_duration, 2),
                 "transition": (s.visual or {}).get("transition"),
                 "visual": s.visual or None,
                 "effect_warnings": s.effect_warnings or None}
                for s in segments
            ],
        }
        (self.out_dir / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8")


def run_pipeline(cfg: PipelineConfig, log=print) -> PipelineResult:
    """One-shot build from a config. Sets up the client, dirs, and demo mode."""
    client = None if cfg.demo else LLMClient(cfg.llm)
    cfg.render.latex = detect_latex()
    if not cfg.demo and not cfg.llm.api_key and "localhost" not in cfg.llm.base_url \
            and "127.0.0.1" not in cfg.llm.base_url:
        raise LLMError("no API key configured: set LLM_API_KEY (see .env.example) "
                       "or run with --demo for the offline sample lecture")
    started = time.time()
    if cfg.demo:
        try:
            slug = slugify(cfg.question or f"demo-{normalize_topic(cfg.demo)}")
        except ValueError as exc:
            raise LLMError(str(exc)) from exc
    else:
        slug = slugify(cfg.question or "lecture")
    cfg.out_dir = Path(cfg.out_dir) / slug
    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    log(f"out   : {cfg.out_dir}")
    pipeline = Pipeline(cfg, client, log=log)
    result = pipeline.run(cfg.question)
    if cfg.interactive:
        _interactive_loop(pipeline, result, log)
    log(f"total : {time.time() - started:.0f}s")
    return result


def _interactive_loop(pipeline: Pipeline, result: PipelineResult,
                      log=print) -> None:
    print("\nLecture built. Ask follow-up questions to extend it with new "
          "narrated segments (blank line to finish).\n")
    while True:
        try:
            question = input("follow-up> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question:
            break
        try:
            segments = pipeline.followup(question, result.segments)
            result = pipeline._compose(segments)
        except Exception as exc:  # noqa: BLE001 - keep the session alive
            log(f"[error] follow-up failed: {exc}")
    log("interactive session finished")
