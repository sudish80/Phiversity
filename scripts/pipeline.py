import argparse
import json
import os
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


def run_pipeline(
    question: Optional[str],
    json_in: Optional[str],
    workdir: Path,
    voice_first: bool = False,
    element_audio: bool = False,
    override_prompt: Optional[str] = None,
) -> Path:
    workdir.mkdir(parents=True, exist_ok=True)

    # Step 1: Get structured JSON (either orchestrate or read input)
    if json_in:
        data = json.loads(Path(json_in).read_text(encoding="utf-8"))
    else:
        if not question:
            raise ValueError("Provide either --question or --json")
        result = orchestrate_solution(question, override_solver_prompt=override_prompt)
        data = result.model_dump()
    json_path = workdir / "solution_plan.json"
    json_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # Voice-first mode: generate audio first to time scenes to audio durations
    audio_dir = workdir / "voice"
    if voice_first:
        if element_audio:
            nested_paths = synthesize_element_wise(data, audio_dir)
            element_durs = get_element_durations(nested_paths)
            gen_script = manim_adapter.generate_scene_script(
                data, scene_durations=[sum(x) for x in element_durs], element_durations=element_durs
            )
            gen_dir = Path("scripts") / "_generated"
            gen_dir.mkdir(parents=True, exist_ok=True)
            script_path = gen_dir / "generated_scene.py"
            script_path.write_text(gen_script, encoding="utf-8")
            silent_video = manim_adapter.render_with_manim(
                script_path, "GeneratedScene", out_path=workdir / "silent.mp4", quality=os.getenv("MANIM_QUALITY", "medium")
            )
            final_path = workdir / "final.mp4"
            combine_video_with_audio(silent_video, flatten_audio(nested_paths), final_path)
        else:
            audio_paths = synthesize_scene_wise(data, audio_dir)
            durations = get_audio_durations(audio_paths)
            gen_script = manim_adapter.generate_scene_script(data, scene_durations=durations)
            gen_dir = Path("scripts") / "_generated"
            gen_dir.mkdir(parents=True, exist_ok=True)
            script_path = gen_dir / "generated_scene.py"
            script_path.write_text(gen_script, encoding="utf-8")
            silent_video = manim_adapter.render_with_manim(
                script_path, "GeneratedScene", out_path=workdir / "silent.mp4", quality=os.getenv("MANIM_QUALITY", "medium")
            )
            final_path = workdir / "final.mp4"
            combine_video_with_audio(silent_video, audio_paths, final_path)
    else:
        # Video-first (previous behavior): render silent video, then synthesize and overlay audio
        gen_script = manim_adapter.generate_scene_script(data)
        gen_dir = Path("scripts") / "_generated"
        gen_dir.mkdir(parents=True, exist_ok=True)
        script_path = gen_dir / "generated_scene.py"
        script_path.write_text(gen_script, encoding="utf-8")
        silent_video = manim_adapter.render_with_manim(
            script_path, "GeneratedScene", out_path=workdir / "silent.mp4", quality=os.getenv("MANIM_QUALITY", "medium")
        )
        if element_audio:
            nested_paths = synthesize_element_wise(data, audio_dir)
            audio_paths = flatten_audio(nested_paths)
        else:
            audio_paths = synthesize_scene_wise(data, audio_dir)
        final_path = workdir / "final.mp4"
        combine_video_with_audio(silent_video, audio_paths, final_path)
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
