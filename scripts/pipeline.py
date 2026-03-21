import argparse
import json
import os
import uuid
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

from .orchestrator.prompt_orchestrator import orchestrate_solution
from . import manim_adapter
from .voiceover import (
    synthesize_scene_wise,
    get_audio_durations,
    synthesize_element_wise,
    flatten_audio,
    get_element_durations,
)
from .av_sync import combine_video_with_audio

# Minimum video duration in seconds (10 minutes)
MIN_VIDEO_DURATION_SECONDS = int(os.getenv("MIN_VIDEO_DURATION", "600"))


def _load_intro_voiceover() -> str:
    """Load intro narration from text file when configured, else use default."""
    default_text = "Welcome to Phiversity. Where Education is made simple."
    intro_file = os.getenv("INTRO_TEXT_FILE", "intro.txt")
    p = Path(intro_file)
    if not p.exists():
        return default_text
    try:
        text = p.read_text(encoding="utf-8").strip()
        return text or default_text
    except Exception as e:
        print(f"[pipeline] WARNING: Could not read intro text file {p}: {e}")
        return default_text


class PipelineTimeoutError(Exception):
    """Raised when pipeline execution exceeds timeout"""
    pass


def run_pipeline(
    question: Optional[str],
    json_in: Optional[str],
    workdir: Path,
    voice_first: bool = True,
    element_audio: bool = False,
    override_prompt: Optional[str] = None,
) -> Path:
    workdir.mkdir(parents=True, exist_ok=True)

    # Step 1: Get structured JSON (either orchestrate or read input)
    print("[pipeline] Step 1/5: Getting solution plan...")
    if json_in:
        data = json.loads(Path(json_in).read_text(encoding="utf-8"))
    else:
        if not question:
            raise ValueError("Provide either --question or --json")
        result = orchestrate_solution(question, override_solver_prompt=override_prompt)
        data = result.model_dump()
    json_path = workdir / "solution_plan.json"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Validate duration — warn early if plan is too short for 10-min video
    manim_adapter.validate_duration(data)

    # Check complexity and warn if too high
    scenes = data.get("animation_plan", {}).get("scenes", [])
    total_elements = sum(len(sc.get("elements", [])) for sc in scenes)
    print(f"[pipeline] Plan has {len(scenes)} scenes with {total_elements} total elements")
    if len(scenes) > 10:
        print(f"[pipeline] WARNING: High scene count ({len(scenes)}) may cause slow rendering")
    if total_elements > 50:
        print(f"[pipeline] WARNING: High element count ({total_elements}) may cause slow rendering")

    def _write_generated_script(content: str) -> Path:
        g_dir = Path(__file__).resolve().parent / "_generated"
        g_dir.mkdir(parents=True, exist_ok=True)
        s_path = g_dir / f"generated_scene_{uuid.uuid4().hex[:8]}.py"
        s_path.write_text(content, encoding="utf-8")
        return s_path

    # ── Intro source selection ──────────────────────────────────────────────
    # Prefer external intro video when enabled; otherwise inject synthetic intro scene.
    intro_enabled = os.getenv("INTRO_ENABLED", "true").lower() != "false"
    intro_video_path = Path(os.getenv("INTRO_VIDEO_PATH", "intro.mp4"))
    use_intro_video = intro_enabled and intro_video_path.exists()

    _scenes = data.get("animation_plan", {}).get("scenes", [])
    has_intro_scene = bool(_scenes) and _scenes[0].get("description", "").lower() == "intro"

    if use_intro_video:
        if has_intro_scene:
            data.get("animation_plan", {}).get("scenes", []).pop(0)
            print("[pipeline] Removed synthetic intro scene (using INTRO_VIDEO_PATH instead)")
        else:
            print("[pipeline] Using intro.mp4 as intro source")
    else:
        if not has_intro_scene:
            intro_voiceover = _load_intro_voiceover()
            _intro = {
                "id": "intro",
                "description": "intro",
                "voiceover": intro_voiceover,
                "elements": [],
            }
            data.setdefault("animation_plan", {}).setdefault("scenes", []).insert(0, _intro)
            print("[pipeline] Injected intro scene for audio-video alignment")

    # Voice-first mode: generate audio first to time scenes to audio durations
    audio_dir = workdir / "voice"
    if voice_first:
        if element_audio:
            print("[pipeline] Step 2/5: Generating element-wise audio (this may take time)...")
            nested_paths = synthesize_element_wise(data, audio_dir)
            element_durs = get_element_durations(nested_paths)
            print("[pipeline] Step 3/5: Generating Manim script...")
            gen_script = manim_adapter.generate_scene_script(
                data, scene_durations=[sum(x) for x in element_durs], element_durations=element_durs
            )
            script_path = _write_generated_script(gen_script)
            print("[pipeline] Step 4/5: Rendering video with Manim (this may take several minutes)...")
            silent_video = manim_adapter.render_with_manim(
                script_path, "GeneratedScene", out_path=workdir / "silent.mp4", quality=os.getenv("MANIM_QUALITY", "medium")
            )
            print("[pipeline] Step 5/5: Combining video with audio...")
            final_path = workdir / "final.mp4"
            combine_video_with_audio(silent_video, flatten_audio(nested_paths), final_path)
        else:
            print("[pipeline] Step 2/5: Generating scene-wise audio...")
            audio_paths = synthesize_scene_wise(data, audio_dir)
            durations = get_audio_durations(audio_paths)
            print("[pipeline] Step 3/5: Generating Manim script...")
            gen_script = manim_adapter.generate_scene_script(data, scene_durations=durations)
            script_path = _write_generated_script(gen_script)
            print("[pipeline] Step 4/5: Rendering video with Manim (this may take several minutes)...")
            silent_video = manim_adapter.render_with_manim(
                script_path, "GeneratedScene", out_path=workdir / "silent.mp4", quality=os.getenv("MANIM_QUALITY", "medium")
            )
            print("[pipeline] Step 5/5: Combining video with audio...")
            final_path = workdir / "final.mp4"
            combine_video_with_audio(silent_video, audio_paths, final_path)
    else:
        # Video-first (previous behavior): render silent video, then synthesize and overlay audio
        print("[pipeline] Step 2/5: Generating Manim script...")
        gen_script = manim_adapter.generate_scene_script(data)
        script_path = _write_generated_script(gen_script)
        print("[pipeline] Step 3/5: Rendering video with Manim (this may take several minutes)...")
        silent_video = manim_adapter.render_with_manim(
            script_path, "GeneratedScene", out_path=workdir / "silent.mp4", quality=os.getenv("MANIM_QUALITY", "medium")
        )
        print("[pipeline] Step 4/5: Generating audio...")
        if element_audio:
            nested_paths = synthesize_element_wise(data, audio_dir)
            audio_paths = flatten_audio(nested_paths)
        else:
            audio_paths = synthesize_scene_wise(data, audio_dir)
        print("[pipeline] Step 5/5: Combining video with audio...")
        final_path = workdir / "final.mp4"
        combine_video_with_audio(silent_video, audio_paths, final_path)

    # ── Post-render duration check ──────────────────────────────────────────
    _check_minimum_duration(final_path, MIN_VIDEO_DURATION_SECONDS)

    print(f"[pipeline] Pipeline complete! Output: {final_path}")
    return final_path


def _check_minimum_duration(video_path: Path, min_seconds: int) -> None:
    """Warn (but don't fail) if the final video is shorter than the minimum."""
    try:
        try:
            from moviepy.editor import VideoFileClip  # type: ignore
        except Exception:
            from moviepy import VideoFileClip  # type: ignore
        with VideoFileClip(str(video_path)) as clip:
            duration = clip.duration or 0.0
        minutes = duration / 60.0
        print(f"[pipeline] Final video duration: {duration:.1f}s ({minutes:.1f} min)")
        if duration < min_seconds:
            deficit = min_seconds - duration
            print(f"[pipeline] WARNING: Video is {deficit:.0f}s shorter than {min_seconds}s minimum ({min_seconds/60:.0f} min)")
            print(f"[pipeline] TIP: To reach {min_seconds/60:.0f} min, add more scenes or lower VOICE_RATE in .env")
        else:
            print(f"[pipeline] [OK] Video meets {min_seconds/60:.0f}-minute minimum requirement")
    except Exception as e:
        print(f"[pipeline] Could not check video duration: {e}")


def main():
    parser = argparse.ArgumentParser(description="Phiversity video generation pipeline")
    parser.add_argument("--question", "-q", help="User question to orchestrate and render")
    parser.add_argument("--json", dest="json_in", help="Path to existing solution_plan JSON")
    parser.add_argument("--out-dir", dest="out_dir", default="media/videos/output", help="Output directory for rendered video")
    parser.add_argument("--voice-first", action="store_true", default=True, help="Generate audio before video (default)")
    parser.add_argument("--element-audio", action="store_true", default=False, help="Element-wise audio synthesis")
    parser.add_argument("--prompt", dest="override_prompt", default=None, help="Override solver prompt")
    args = parser.parse_args()

    if not args.question and not args.json_in:
        parser.error("Provide either --question or --json")

    final_path = run_pipeline(
        question=args.question,
        json_in=args.json_in,
        workdir=Path(args.out_dir),
        voice_first=args.voice_first,
        element_audio=args.element_audio,
        override_prompt=args.override_prompt,
    )
    print(f"[pipeline] Final output: {final_path}")


if __name__ == "__main__":
    main()
