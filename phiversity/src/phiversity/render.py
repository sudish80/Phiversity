"""Renders LLM-generated Manim scenes safely, with self-healing on failure.

Generated code is validated against a blocklist before being executed by
manim, rendered in an isolated working directory with a hard timeout, and
if rendering fails the error is fed back to the LLM to fix its own code.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

from .config import RenderConfig
from .llm import LLMClient

QUALITY_FLAG = {"l": "-ql", "m": "-qm", "h": "-qh"}
# ffmpeg writer fps per manim quality flag
QUALITY_FPS = {"l": 15, "m": 30, "h": 60}
# frame resolution per manim quality flag
QUALITY_SIZE = {"l": (854, 480), "m": (1280, 720), "h": (1920, 1080)}

# LLM code is untrusted: forbid anything that touches the system.
DANGEROUS_PATTERNS = [
    (r"\bimport\s+os\b", "os import"),
    (r"\bfrom\s+os\b", "os import"),
    (r"\bimport\s+sys\b", "sys import"),
    (r"\bfrom\s+sys\b", "sys import"),
    (r"\bsubprocess\b", "subprocess"),
    (r"\bshutil\b", "shutil"),
    (r"\bsocket\b", "socket"),
    (r"\brequests\b", "requests"),
    (r"\burllib\b", "urllib"),
    (r"\bpathlib\b", "pathlib"),
    (r"\b__import__\b", "__import__"),
    (r"\beval\s*\(", "eval"),
    (r"\bexec\s*\(", "exec"),
    (r"\bcompile\s*\(", "compile"),
    (r"\bglobals\s*\(", "globals"),
    (r"\blocals\s*\(", "locals"),
    (r"\bgetattr\s*\(", "getattr"),
    (r"\bopen\s*\(", "open"),
    (r"\binput\s*\(", "input"),
    (r"\brandom\b", "random"),
]

# scene base classes the generated code may use (Scene plus the camera/
# vector/3D variants, so scenes can zoom, rotate, and draw diagrams)
SCENE_CLASS_RE = r"(?:MovingCameraScene|Scene|VectorScene|ZoomedScene|ThreeDScene)"


class CodeValidationError(ValueError):
    pass


class RenderError(RuntimeError):
    pass


# ---------------------------------------------------------------------------
# Timing: keep animations in step with the measured voice-over
# ---------------------------------------------------------------------------


def estimate_scene_duration(code: str) -> float:
    """Rough timeline of a scene: every self.wait(N), every run_time=N,
    plus 1s for each .play() that omits run_time."""
    waits = [float(x) for x in
             re.findall(r"self\.wait\(\s*([0-9]*\.?[0-9]+)", code)]
    run_times = [float(x) for x in
                 re.findall(r"run_time\s*=\s*([0-9]*\.?[0-9]+)", code)]
    plays = len(re.findall(r"\.play\(", code))
    implicit = max(0, plays - len(run_times))
    return sum(waits) + sum(run_times) + implicit * 1.0


def adjust_final_wait(code: str, extra_seconds: float) -> str:
    """Stretch the scene's last self.wait(N) so the animation fills the
    voice-over instead of freezing on its final frame."""
    if extra_seconds <= 0:
        return code
    pattern = re.compile(r"self\.wait\(\s*([0-9]*\.?[0-9]+)\s*\)")
    matches = list(pattern.finditer(code))
    if not matches:
        return code
    last = matches[-1]
    new_value = max(0.05, float(last.group(1)) + extra_seconds)
    return (f"{code[:last.start()]}self.wait({new_value:g})"
            f"{code[last.end():]}")


# ---------------------------------------------------------------------------
# Layout lint: catch the classic "boxed before it moved" overlap bug
# ---------------------------------------------------------------------------


def lint_layout(code: str) -> list[str]:
    """Warn when a mobject is wrapped (SurroundingRectangle/Underline/Brace)
    and THEN repositioned - boxes capture position at creation time, so the
    box would be drawn around empty space and overlap the wrong content."""
    warnings: list[str] = []
    wraps = re.finditer(
        r"(?:SurroundingRectangle|Underline|Brace)\(\s*(\w+)", code)
    for match in wraps:
        name = match.group(1)
        rest = code[match.end():]
        if re.search(rf"\b{name}\s*\.\s*animate\s*\.\s*"
                     rf"(?:move_to|shift|to_edge|to_corner|next_to|arrange)",
                     rest):
            warnings.append(
                f"'{name}' is wrapped before it is repositioned - position it "
                f"first, then create the box")
    return warnings


# ---------------------------------------------------------------------------
# Overflow detection: is anything clipped at the frame edges?
# ---------------------------------------------------------------------------


def detect_edge_clipping(video: str | Path, samples: int = 8,
                         edge_frac: float = 0.015,
                         contrast: float = 60.0,
                         text_height_frac: float = 0.025,
                         min_frames_frac: float = 0.4) -> list[str]:
    """Check sampled frames for text-like content touching the left/right
    frame edges (i.e. the question or labels going out of the screen).

    "Text-like" means a consecutive run of at least `text_height_frac` of
    the frame height in pixel rows inside the edge strip (glyph height),
    which ignores thin full-bleed design elements (roads, floors) and
    graph lines that legitimately cross the view during camera zooms. A
    side is flagged only when the clipping persists in at least
    `min_frames_frac` of the samples, so transient mid-animation crossings
    are not reported.
    """
    import tempfile

    video = Path(video)
    from .tts import ffprobe_duration
    duration = ffprobe_duration(video)
    if duration <= 0:
        return []
    times = [min(duration - 0.05, max(0.05, duration * (i + 0.5) / samples))
             for i in range(samples)]
    hits = {"left": 0, "right": 0}
    checked = 0
    with tempfile.TemporaryDirectory() as tmp:
        for i, t in enumerate(times):
            frame = Path(tmp) / f"f{i}.png"
            proc = subprocess.run(
                ["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}",
                 "-i", str(video), "-frames:v", "1", str(frame)],
                capture_output=True, text=True, stdin=subprocess.DEVNULL)
            if proc.returncode != 0 or not frame.is_file():
                continue
            try:
                from PIL import Image
                import numpy as np
                img = np.asarray(Image.open(frame).convert("L"), dtype=int)
            except Exception:  # noqa: BLE001 - PIL/numpy unavailable
                return []
            checked += 1
            h, w = img.shape
            strip = max(2, int(w * edge_frac))
            needed_rows = max(4, int(h * text_height_frac))
            for side, region in (("left", img[:, :strip]),
                                 ("right", img[:, -strip:])):
                rows = (region.max(axis=1) - region.min(axis=1)) > contrast
                if _longest_run(rows) >= needed_rows:
                    hits[side] += 1
    if checked == 0:
        return []
    needed = max(1, int(checked * min_frames_frac + 0.999))
    return [side for side in ("left", "right")
            if hits[side] >= needed]


def _longest_run(flags) -> int:
    """Longest run of consecutive True values."""
    best = current = 0
    for value in flags:
        current = current + 1 if value else 0
        best = max(best, current)
    return best


def validate_code(code: str, scene_name: str) -> str:
    """Static safety + shape check on generated scene code. Returns cleaned code."""
    if not code or not code.strip():
        raise CodeValidationError("empty code")
    if "from manim import" not in code:
        raise CodeValidationError('code must start with "from manim import *"')
    # strip accidental markdown fences
    if code.strip().startswith("```"):
        code = code.strip().strip("`")
        lines = code.splitlines()
        if lines and lines[0].strip() in ("python", "py"):
            lines = lines[1:]
        code = "\n".join(lines)
    # drop anything the blocklist catches
    for pattern, label in DANGEROUS_PATTERNS:
        if re.search(pattern, code):
            raise CodeValidationError(
                f"generated code uses forbidden module/builtin: {label}")
    # drop import lines other than manim itself
    cleaned_lines = []
    for line in code.splitlines():
        stripped = line.strip()
        if re.match(r"^(import|from)\s+", stripped) and "manim" not in stripped:
            continue
        cleaned_lines.append(line)
    code = "\n".join(cleaned_lines)
    # the required scene class must exist
    if not re.search(rf"class\s+{scene_name}\s*\(\s*{SCENE_CLASS_RE}\s*\):",
                     code):
        raise CodeValidationError(
            f'missing "class {scene_name}(Scene):" '
            f"(or MovingCameraScene for zooming)")
    if "def construct(self)" not in code:
        raise CodeValidationError('missing "def construct(self)"')
    return code


def render_scene(code: str, scene_name: str, workdir: str | Path,
                 cfg: RenderConfig, kit: str = "") -> Path:
    """Write code to workdir, render it with manim, return the mp4 path.

    `kit` is the theme preamble (semantic colors + camera/geometry/emphasis
    helpers) prepended to the scene source before rendering.
    """
    workdir = Path(workdir)
    workdir.mkdir(parents=True, exist_ok=True)
    py_file = workdir / f"{scene_name}.py"
    py_file.write_text((kit + "\n\n" if kit else "") + code, encoding="utf-8")

    media_dir = workdir / "media"
    quality = QUALITY_FLAG.get(cfg.quality, "-qm")
    cmd = [
        sys.executable, "-m", "manim", "render",
        quality, "--format", "mp4", "--disable_caching",
        "--flush_cache",
        "--media_dir", str(media_dir),
        "--output_file", f"{scene_name}.mp4",
        str(py_file), scene_name,
    ]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              stdin=subprocess.DEVNULL, timeout=cfg.timeout)
    except subprocess.TimeoutExpired as exc:
        shutil.rmtree(media_dir, ignore_errors=True)
        raise RenderError(
            f"render exceeded {cfg.timeout:.0f}s timeout") from exc
    if proc.returncode != 0:
        raise RenderError(_tail(proc.stderr or proc.stdout))
    videos = sorted((media_dir / "videos").rglob("*.mp4"),
                    key=lambda p: p.stat().st_mtime) if (media_dir / "videos").exists() else []
    if not videos:
        raise RenderError("manim finished but no .mp4 was produced")
    return videos[-1]


def render_with_healing(code: str, scene_name: str, workdir: str | Path,
                        cfg: RenderConfig,
                        client: LLMClient | None = None,
                        kit: str = "",
                        log=print) -> Path:
    """Render a scene; on failure, ask the LLM to fix its code and retry."""
    current = validate_code(code, scene_name)
    last_error = ""
    for attempt in range(cfg.heal_attempts + 1):
        try:
            return render_scene(current, scene_name, workdir, cfg, kit=kit)
        except CodeValidationError as exc:
            last_error = f"validation: {exc}"
        except RenderError as exc:
            last_error = str(exc)
        if attempt >= cfg.heal_attempts or client is None:
            break
        log(f"  [fix] {scene_name} failed ({last_error.splitlines()[-1] if last_error else ''}); "
            f"asking the LLM to repair its code (attempt {attempt + 1}/{cfg.heal_attempts})")
        try:
            current = validate_code(client.heal_code(current, last_error),
                                     scene_name)
        except Exception as exc:  # noqa: BLE001 - healing is best-effort
            log(f"  [fix] healing failed: {exc}")
            break
    raise RenderError(f"{scene_name}: {last_error or 'unknown render error'}")


def _tail(text: str, limit: int = 2000) -> str:
    text = (text or "").strip()
    return text[-limit:] if len(text) > limit else text
