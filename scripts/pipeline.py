import argparse
import json
import os
import signal
import shutil
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load .env from project root
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=True)

# Consistent naming for video outputs
# All final videos should be named "final.mp4" to ensure consistency across the pipeline
FINAL_VIDEO_NAME = "final.mp4"
# Intermediate silent video (before audio synthesis)
SILENT_VIDEO_NAME = "silent.mp4"
# Intro video that gets prepended to all final videos
INTRO_VIDEO_NAME = "intro.mp4"
INTRO_VIDEO_OPTIONAL = True  # If True, skips if intro.mp4 not found; if False, fails


# Find project root and intro video path
def _get_intro_video_path() -> Path:
    """Get the path to intro.mp4 in project root"""
    # Get the root directory (parent of scripts folder)
    root = Path(__file__).resolve().parents[1]
    intro_path = root / INTRO_VIDEO_NAME
    return intro_path

from .orchestrator.prompt_orchestrator import orchestrate_solution
from . import manim_adapter
from .voiceover import (
    synthesize_scene_wise,
    get_audio_durations,
    synthesize_element_wise,
    flatten_audio,
    get_element_durations,
)
from .av_sync import combine_video_with_audio, prepend_intro_to_video, add_logo_watermark
from .pipeline_validator import validate_animation_plan
from .step_to_scene_mapper import StepToSceneMapper


class TimeoutError(Exception):
    """Raised when pipeline execution exceeds timeout"""
    pass


def run_pipeline(
    question: Optional[str],
    json_in: Optional[str],
    workdir: Path,
    voice_first: bool = False,
    element_audio: bool = False,
    override_prompt: Optional[str] = None,
) -> Path:
    workdir.mkdir(parents=True, exist_ok=True)
    
    # Check if intro.mp4 exists in project root
    intro_path = _get_intro_video_path()
    if intro_path.exists():
        print(f"[pipeline] Using intro video: {intro_path}")
    else:
        print(f"[pipeline] No intro.mp4 found at {intro_path}. Proceeding without intro.")
        print(f"[pipeline] TIP: Place intro.mp4 in project root to include it in videos.")

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
    
    # Step 1A: Ensure every solution step has a scene and fix timeline overlaps
    print("[pipeline] Step 1A/5: Mapping solution steps to scenes...")
    data, mapper_warnings = StepToSceneMapper.validate_and_fix_all(data)
    if mapper_warnings:
        for warning in mapper_warnings:
            print(f"[pipeline]   {warning}")
    
    # Save fixed JSON
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    
    # Validate animation plan for step sequencing, pacing, and redundancy
    print("[pipeline] Validating animation plan structure...")
    validation_result = validate_animation_plan(data)
    validation_path = workdir / "validation_report.json"
    validation_path.write_text(json.dumps(validation_result, indent=2), encoding="utf-8")
    
    # Report validation results
    print(f"[pipeline] Validation Status: {validation_result['overall_status']}")
    step_seq = validation_result['step_sequencing']
    print(f"[pipeline] Step Coverage: {step_seq['coverage_percentage']:.1f}% ({step_seq['covered_steps']}/{step_seq['total_steps']} steps)")
    
    if step_seq['skipped_steps']:
        print(f"[pipeline] ⚠️  WARNING: Skipped steps: {', '.join(step_seq['skipped_steps'][:3])}")
    
    if step_seq['redundant_content']:
        print(f"[pipeline] ⚠️  WARNING: Redundant content detected")
    
    pacing = validation_result['adaptive_pacing']
    print(f"[pipeline] Total Duration: {pacing['total_duration_sec']}s")
    print(f"[pipeline] Pacing Recommendations: {len(validation_result['recommendations'])} issues found")
    
    if not validation_result['overall_valid']:
        print("[pipeline] ⚠️  VALIDATION WARNINGS - continuing but review recommended")
    
    # Check complexity and warn if too high
    scenes = data.get("animation_plan", {}).get("scenes", [])
    total_elements = sum(len(sc.get("elements", [])) for sc in scenes)
    print(f"[pipeline] Plan has {len(scenes)} scenes with {total_elements} total elements")
    if len(scenes) > 10:
        print(f"[pipeline] WARNING: High scene count ({len(scenes)}) may cause slow rendering")
    if total_elements > 50:
        print(f"[pipeline] WARNING: High element count ({total_elements}) may cause slow rendering")

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
            gen_dir = Path("scripts") / "_generated"
            gen_dir.mkdir(parents=True, exist_ok=True)
            script_path = gen_dir / "generated_scene.py"
            script_path.write_text(gen_script, encoding="utf-8")
            print("[pipeline] Step 4/5: Rendering video with Manim (this may take several minutes)...")
            silent_video = manim_adapter.render_with_manim(
                script_path, "GeneratedScene", out_path=workdir / SILENT_VIDEO_NAME, quality=os.getenv("MANIM_QUALITY", "medium")
            )
            print("[pipeline] Step 5/5: Combining video with audio...")
            final_path = workdir / FINAL_VIDEO_NAME
            combine_video_with_audio(silent_video, flatten_audio(nested_paths), final_path)
            
            # Add intro to the final video
            intro_path = _get_intro_video_path()
            if intro_path.exists():
                combined_with_intro = workdir / "__temp_intro_combined.mp4"
                prepend_intro_to_video(intro_path, final_path, combined_with_intro)
                # Replace final video with intro-prepended version
                shutil.move(str(combined_with_intro), str(final_path))
                print("[pipeline] ✓ Intro prepended to video")
        else:
            print("[pipeline] Step 2/5: Generating scene-wise audio...")
            audio_paths = synthesize_scene_wise(data, audio_dir)
            durations = get_audio_durations(audio_paths)
            print("[pipeline] Step 3/5: Generating Manim script...")
            gen_script = manim_adapter.generate_scene_script(data, scene_durations=durations)
            gen_dir = Path("scripts") / "_generated"
            gen_dir.mkdir(parents=True, exist_ok=True)
            script_path = gen_dir / "generated_scene.py"
            script_path.write_text(gen_script, encoding="utf-8")
            print("[pipeline] Step 4/5: Rendering video with Manim (this may take several minutes)...")
            silent_video = manim_adapter.render_with_manim(
                script_path, "GeneratedScene", out_path=workdir / SILENT_VIDEO_NAME, quality=os.getenv("MANIM_QUALITY", "medium")
            )
            print("[pipeline] Step 5/5: Combining video with audio...")
            final_path = workdir / FINAL_VIDEO_NAME
            combine_video_with_audio(silent_video, audio_paths, final_path)
            
            # Add intro to the final video
            intro_path = _get_intro_video_path()
            if intro_path.exists():
                combined_with_intro = workdir / "__temp_intro_combined.mp4"
                prepend_intro_to_video(intro_path, final_path, combined_with_intro)
                # Replace final video with intro-prepended version
                shutil.move(str(combined_with_intro), str(final_path))
                print("[pipeline] ✓ Intro prepended to video")
    else:
        # Video-first (previous behavior): render silent video, then synthesize and overlay audio
        print("[pipeline] Step 2/5: Generating Manim script...")
        gen_script = manim_adapter.generate_scene_script(data)
        gen_dir = Path("scripts") / "_generated"
        gen_dir.mkdir(parents=True, exist_ok=True)
        script_path = gen_dir / "generated_scene.py"
        script_path.write_text(gen_script, encoding="utf-8")
        print("[pipeline] Step 3/5: Rendering video with Manim (this may take several minutes)...")
        silent_video = manim_adapter.render_with_manim(
            script_path, "GeneratedScene", out_path=workdir / SILENT_VIDEO_NAME, quality=os.getenv("MANIM_QUALITY", "medium")
        )
        print("[pipeline] Step 4/5: Generating audio...")
        if element_audio:
            nested_paths = synthesize_element_wise(data, audio_dir)
            audio_paths = flatten_audio(nested_paths)
        else:
            audio_paths = synthesize_scene_wise(data, audio_dir)
        print("[pipeline] Step 5/5: Combining video with audio...")
        final_path = workdir / FINAL_VIDEO_NAME
        combine_video_with_audio(silent_video, audio_paths, final_path)
        
        # Add intro to the final video
        intro_path = _get_intro_video_path()
        if intro_path.exists():
            combined_with_intro = workdir / "__temp_intro_combined.mp4"
            prepend_intro_to_video(intro_path, final_path, combined_with_intro)
            # Replace final video with intro-prepended version
            shutil.move(str(combined_with_intro), str(final_path))
            print("[pipeline] ✓ Intro prepended to video")
    print(f"[pipeline] ✓ Pipeline complete! Output: {final_path}")
    
    # Verify final.mp4 exists
    if not final_path.exists():
        raise RuntimeError(f"Pipeline completed but final video not found at {final_path}")
    
    print(f"[pipeline] ✓ Final video confirmed: {final_path} ({final_path.stat().st_size / 1024 / 1024:.1f} MB)")
    
    # Add logo watermark to final video
    print("[pipeline] Adding logo watermark...")
    watermarked_path = workdir / "__temp_watermarked.mp4"
    add_logo_watermark(final_path, watermarked_path)
    # Replace final video with watermarked version
    shutil.move(str(watermarked_path), str(final_path))
    print("[pipeline] ✓ Logo watermark applied to final video")
    
    return final_path


def main():
    parser = argparse.ArgumentParser(description="End-to-end pipeline: Orchestrate -> Render -> Voice -> Sync")
    parser.add_argument("--question", dest="question", default=None, help="User question to solve (if --json not provided)")
    parser.add_argument("--json", dest="json", default=None, help="Existing structured JSON to use")
    parser.add_argument("--out-dir", dest="out_dir", default="media/videos/pipeline_output", help="Output working directory")
    parser.add_argument("--voice-first", action="store_true", help="Generate audio first and time scenes exactly to audio durations")
    parser.add_argument("--element-audio", action="store_true", help="Generate per-element audio for fine-grained lip-sync")
    args = parser.parse_args()

    final = run_pipeline(
        args.question, args.json, Path(args.out_dir), voice_first=args.voice_first, element_audio=args.element_audio
    )
    print(f"Final MP4: {final}")


if __name__ == "__main__":
    main()
