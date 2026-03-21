import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, List

# Configure moviepy to use system ffmpeg (Railway has ffmpeg installed via apt)
# NOTE: The ffmpeg check is deferred to first use so that importing this module
# in tests or non-video contexts does not raise at import time.
_ffmpeg_configured = False

def _ensure_ffmpeg():
    """Lazily configure and validate ffmpeg. Called before any video operation."""
    global _ffmpeg_configured
    if _ffmpeg_configured:
        return
    ffmpeg_binary = os.getenv("FFMPEG_BINARY")
    if ffmpeg_binary:
        import moviepy.config
        moviepy.config.FFMPEG_BINARY = ffmpeg_binary
    elif not shutil.which("ffmpeg"):
        raise RuntimeError(
            "ffmpeg not found in system PATH and FFMPEG_BINARY not set. "
            "On Railway, ffmpeg is installed via apt. "
            "On local Windows, set FFMPEG_BINARY in .env"
        )
    _ffmpeg_configured = True

def _import_moviepy():
    """Lazily import moviepy classes. Returns (AudioFileClip, VideoFileClip, concatenate_audioclips, concatenate_videoclips)."""
    # Ensure ffmpeg/ffplay/ffprobe are discoverable before moviepy tries to find them at import
    _ensure_ffmpeg()
    ffmpeg_bin = os.getenv("FFMPEG_BINARY") or shutil.which("ffmpeg")
    if ffmpeg_bin:
        bin_dir = str(Path(ffmpeg_bin).parent)
        if bin_dir not in os.environ.get("PATH", ""):
            os.environ["PATH"] = bin_dir + os.pathsep + os.environ.get("PATH", "")
        os.environ.setdefault("FFMPEG_BINARY", ffmpeg_bin)
    try:
        from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_audioclips, concatenate_videoclips  # type: ignore
    except Exception:
        from moviepy import AudioFileClip, VideoFileClip, concatenate_audioclips, concatenate_videoclips  # type: ignore
    return AudioFileClip, VideoFileClip, concatenate_audioclips, concatenate_videoclips


# Default intro video path (can be overridden via environment variable)
DEFAULT_INTRO_VIDEO = os.getenv("INTRO_VIDEO_PATH", "intro.mp4")


def prepend_intro_video(main_video_path: Path, intro_path: str = None, output_path: Path = None) -> Path:
    """
    Prepend an intro video to the main video.
    Tries moviepy first, falls back to direct FFmpeg.
    """
    intro_file = Path(intro_path) if intro_path else Path(DEFAULT_INTRO_VIDEO)

    if not intro_file.exists():
        print(f"[av_sync] Intro video not found at {intro_file}, skipping prepend")
        return main_video_path

    if not main_video_path.exists():
        raise RuntimeError(f"Main video not found: {main_video_path}")

    out_path = output_path or main_video_path
    print(f"[av_sync] Prepending intro: {intro_file} -> {main_video_path}")

    # Try moviepy first
    try:
        return _prepend_intro_via_moviepy(intro_file, main_video_path, out_path)
    except Exception as e:
        print(f"[av_sync] moviepy intro prepend failed ({e}), falling back to FFmpeg")

    # Fallback: direct FFmpeg
    return _prepend_intro_via_ffmpeg(intro_file, main_video_path, out_path)


def _prepend_intro_via_moviepy(intro_file: Path, main_video_path: Path, out_path: Path) -> Path:
    """Prepend intro using moviepy."""
    _ensure_ffmpeg()
    _, VideoFileClip, _, concatenate_videoclips = _import_moviepy()
    intro_clip = VideoFileClip(str(intro_file))
    main_clip = VideoFileClip(str(main_video_path))
    try:
        final_clip = concatenate_videoclips([intro_clip, main_clip])
        tmp_output = out_path
        is_same = (out_path.resolve() == main_video_path.resolve())
        if is_same:
            tmp_output = out_path.with_name(f"tmp_intro_{out_path.name}")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        final_clip.write_videofile(str(tmp_output), codec="libx264", audio_codec="aac")
        if is_same:
            shutil.move(str(tmp_output), str(out_path))
        print(f"[av_sync] Video with intro saved: {out_path}")
        return out_path
    finally:
        for clip in (intro_clip, main_clip):
            try:
                clip.close()
            except Exception:
                pass


def _prepend_intro_via_ffmpeg(intro_file: Path, main_video_path: Path, out_path: Path) -> Path:
    """Prepend intro using FFmpeg filter_complex (handles different resolutions)."""
    ffmpeg = _find_ffmpeg()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    is_same = (out_path.resolve() == main_video_path.resolve())
    tmp_output = out_path.with_name(f"tmp_intro_{out_path.name}") if is_same else out_path
    try:
        # Use filter_complex to scale intro to match main video and concatenate
        # Probe main video for resolution and fps
        ffprobe = str(Path(ffmpeg).parent / ("ffprobe.exe" if os.name == "nt" else "ffprobe"))
        probe_result = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "v:0",
             "-show_entries", "stream=width,height,r_frame_rate",
             "-of", "csv=p=0", str(main_video_path)],
            check=True, capture_output=True, text=True,
        )
        parts = probe_result.stdout.strip().split(",")
        width, height = parts[0], parts[1]
        # r_frame_rate is like "15/1", convert to number
        fps_parts = parts[2].split("/")
        fps = str(int(fps_parts[0]) // int(fps_parts[1])) if len(fps_parts) == 2 else parts[2]

        filter_complex = (
            f"[0:v]scale={width}:{height},fps={fps},setsar=1[v0];"
            f"[0:a]aresample=22050[a0];"
            f"[v0][a0][1:v][1:a]concat=n=2:v=1:a=1[outv][outa]"
        )
        subprocess.run(
            [ffmpeg, "-y", "-i", str(intro_file), "-i", str(main_video_path),
             "-filter_complex", filter_complex,
             "-map", "[outv]", "-map", "[outa]",
             "-c:v", "libx264", "-c:a", "aac",
             "-movflags", "+faststart", str(tmp_output)],
            check=True, capture_output=True, text=True,
        )
        if is_same:
            shutil.move(str(tmp_output), str(out_path))
        print(f"[av_sync] FFmpeg: video with intro saved to {out_path}")
    finally:
        if is_same:
            try:
                Path(tmp_output).unlink(missing_ok=True)
            except Exception:
                pass
    return out_path


def combine_video_with_audio(video_path: Path, audio_paths: List[Path], out_path: Path, prepend_intro: bool = None) -> Path:
    """Combine video with audio and optionally prepend intro video.
    
    Args:
        video_path: Path to the main video
        audio_paths: List of audio file paths to combine
        out_path: Output path for the final video
        prepend_intro: If None, uses INTRO_ENABLED env var (default: True)
    """
    # Check if intro is enabled (default True)
    if prepend_intro is None:
        prepend_intro = os.getenv("INTRO_ENABLED", "true").lower() != "false"
    
    # First combine video with audio
    result_path = _combine_video_with_audio_impl(video_path, audio_paths, out_path)
    
    # Then prepend intro if enabled
    if prepend_intro:
        intro_path = os.getenv("INTRO_VIDEO_PATH", "intro.mp4")
        result_path = prepend_intro_video(result_path, intro_path)
    
    return result_path


def _find_ffmpeg() -> str:
    """Return path to ffmpeg binary."""
    env_bin = os.getenv("FFMPEG_BINARY")
    if env_bin and os.path.isfile(env_bin):
        return env_bin
    found = shutil.which("ffmpeg")
    if found:
        return found
    raise RuntimeError("ffmpeg not found in PATH and FFMPEG_BINARY not set")


def _find_ffprobe() -> str:
    """Return path to ffprobe binary."""
    ffmpeg = _find_ffmpeg()
    candidate = str(Path(ffmpeg).parent / ("ffprobe.exe" if os.name == "nt" else "ffprobe"))
    if os.path.isfile(candidate):
        return candidate
    found = shutil.which("ffprobe")
    if found:
        return found
    raise RuntimeError("ffprobe not found in PATH and FFMPEG_BINARY sibling not found")


def _probe_duration(path: Path, stream: str = "format") -> float:
    """Probe media duration in seconds using ffprobe."""
    ffprobe = _find_ffprobe()
    if stream == "audio":
        args = [
            ffprobe, "-v", "error", "-select_streams", "a:0",
            "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)
        ]
    elif stream == "video":
        args = [
            ffprobe, "-v", "error", "-select_streams", "v:0",
            "-show_entries", "stream=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(path)
        ]
    else:
        args = [
            ffprobe, "-v", "error", "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1", str(path)
        ]
    res = subprocess.run(args, check=True, capture_output=True, text=True)
    val = (res.stdout or "").strip()
    return float(val) if val else 0.0


def _combine_via_ffmpeg(video_path: Path, audio_paths: List[Path], out_path: Path) -> Path:
    """Combine video+audio using FFmpeg directly (fallback when moviepy fails)."""
    ffmpeg = _find_ffmpeg()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    # Concatenate audio files into a single WAV
    combined_audio = out_path.parent / "combined_audio.wav"
    list_file = out_path.parent / "audio_list.txt"
    gap_file = out_path.parent / "gap_silence.wav"
    try:
        gap_seconds = max(0.0, float(os.getenv("AUDIO_SCENE_GAP_SECONDS", "0.04")))
        lines: List[str] = []
        if gap_seconds > 0 and len(audio_paths) > 1:
            # Insert a tiny silent spacer between clips to prevent audible overlap
            # and boundary smearing when source MP3s include encoder delay/padding.
            subprocess.run(
                [
                    ffmpeg, "-y", "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
                    "-t", f"{gap_seconds:.6f}", "-c:a", "pcm_s16le", str(gap_file)
                ],
                check=True, capture_output=True, text=True,
            )
            for i, p in enumerate(audio_paths):
                lines.append(f"file '{p.resolve()}'".replace("\\", "/"))
                if i < len(audio_paths) - 1:
                    lines.append(f"file '{gap_file.resolve()}'".replace("\\", "/"))
            print(f"[av_sync] FFmpeg: inserted {gap_seconds:.3f}s silence between audio clips")
        else:
            lines = [f"file '{p.resolve()}'".replace("\\", "/") for p in audio_paths]
        list_file.write_text("\n".join(lines), encoding="utf-8")

        # Re-encode to deterministic PCM to avoid timestamp drift when source clips
        # have mixed codecs/sample-rates or VBR headers.
        subprocess.run(
            [ffmpeg, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
             "-vn", "-ac", "2", "-ar", "48000", "-c:a", "pcm_s16le", str(combined_audio)],
            check=True, capture_output=True, text=True,
        )
        print(f"[av_sync] FFmpeg: concatenated {len(audio_paths)} audio files")

        # Mux video + audio with explicit duration alignment (no implicit -shortest cut).
        video_dur = _probe_duration(video_path, stream="video")
        audio_dur = _probe_duration(combined_audio, stream="audio")
        target_dur = max(audio_dur, 0.0)
        pad_dur = max(0.0, audio_dur - video_dur)

        if pad_dur > 0.02:
            vfilter = f"[0:v]tpad=stop_mode=clone:stop_duration={pad_dur:.6f},trim=duration={target_dur:.6f},setpts=PTS-STARTPTS[v]"
            print(f"[av_sync] FFmpeg: padding video by {pad_dur:.2f}s to match audio")
        else:
            vfilter = f"[0:v]trim=duration={target_dur:.6f},setpts=PTS-STARTPTS[v]"
            if video_dur - audio_dur > 0.02:
                print(f"[av_sync] FFmpeg: trimming video by {(video_dur - audio_dur):.2f}s to match audio")

        afilter = f"[1:a]atrim=duration={target_dur:.6f},asetpts=PTS-STARTPTS[a]"
        subprocess.run(
            [ffmpeg, "-y", "-i", str(video_path), "-i", str(combined_audio),
             "-filter_complex", f"{vfilter};{afilter}",
             "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac",
             "-movflags", "+faststart", str(out_path)],
            check=True, capture_output=True, text=True,
        )
        print(f"[av_sync] FFmpeg: final video saved to {out_path}")
    finally:
        for tmp in (list_file, combined_audio, gap_file):
            try:
                tmp.unlink(missing_ok=True)
            except Exception:
                pass
    return out_path


def _combine_video_with_audio_impl(video_path: Path, audio_paths: List[Path], out_path: Path) -> Path:
    """Combine video with audio. Tries moviepy first, falls back to direct FFmpeg."""
    # Validate audio files before processing
    for p in audio_paths:
        if not p.exists():
            raise RuntimeError(f"Audio file missing: {p}")
        if p.stat().st_size == 0:
            raise RuntimeError(f"Audio file is empty: {p}")

    # Optional hard switch for deterministic FFmpeg pipeline.
    if os.getenv("AVSYNC_FORCE_FFMPEG", "true").lower() == "true":
        print("[av_sync] AVSYNC_FORCE_FFMPEG=true -> using FFmpeg sync path")
        return _combine_via_ffmpeg(video_path, audio_paths, out_path)

    # Try moviepy first
    try:
        return _combine_via_moviepy(video_path, audio_paths, out_path)
    except Exception as e:
        print(f"[av_sync] moviepy failed ({e}), falling back to direct FFmpeg")

    # Fallback: direct FFmpeg
    return _combine_via_ffmpeg(video_path, audio_paths, out_path)


def _sync_video_to_audio_duration(video: Any, final_audio: Any) -> Any:
    """Ensure video duration exactly matches audio duration to prevent sync issues.

    If video is shorter than audio, pad with black frames.
    If video is longer than audio, trim the excess.
    """
    video_duration = video.duration or 0.0
    audio_duration = final_audio.duration or 0.0

    if abs(video_duration - audio_duration) < 0.1:
        # Close enough, no adjustment needed
        return video

    if video_duration < audio_duration:
        # Video is shorter - pad with black frames at the end
        padding_duration = audio_duration - video_duration
        from moviepy.video.VideoClip import ColorClip
        padding = ColorClip(size=video.size, color=(0, 0, 0), duration=padding_duration)
        from moviepy.video.compositing.concatenate import concatenate_videoclips
        video = concatenate_videoclips([video, padding])
        print(f"[av_sync] Padded video with {padding_duration:.2f}s of black to match audio")
    else:
        # Video is longer - trim the excess
        from moviepy.video.compositing.concatenate import concatenate_videoclips
        video = video.subclip(0, audio_duration)
        print(f"[av_sync] Trimmed video to match audio duration {audio_duration:.2f}s")

    return video


def _combine_via_moviepy(video_path: Path, audio_paths: List[Path], out_path: Path) -> Path:
    """Original moviepy-based combine logic."""
    _ensure_ffmpeg()
    AudioFileClip, VideoFileClip, concatenate_audioclips, _ = _import_moviepy()
    clips = [AudioFileClip(str(p)) for p in audio_paths]
    final_audio = concatenate_audioclips(clips)
    video = VideoFileClip(str(video_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Sync video duration to exactly match audio duration
        video = _sync_video_to_audio_duration(video, final_audio)

        if hasattr(video, "set_audio"):
            vclip = video.set_audio(final_audio)  # MoviePy 1.x style
        else:
            vclip = video.with_audio(final_audio)  # MoviePy 2.x style
        fps = getattr(video, "fps", None)
        if fps:
            vclip.write_videofile(str(out_path), codec="libx264", audio_codec="aac", fps=fps)
        else:
            vclip.write_videofile(str(out_path), codec="libx264", audio_codec="aac")
    finally:
        # Close resources
        try:
            if 'vclip' in locals() and hasattr(vclip, "close"):
                vclip.close()
        except Exception:
            pass
        try:
            if hasattr(final_audio, "close"):
                final_audio.close()
        except Exception:
            pass
        for c in clips:
            try:
                c.close()
            except Exception:
                pass
        try:
            video.close()
        except Exception:
            pass
    return out_path


def main():
    parser = argparse.ArgumentParser(description="Overlay concatenated scene-wise audio onto a video")
    parser.add_argument("video", help="Path to silent MP4 video")
    parser.add_argument("audios", nargs="+", help="Paths to audio files in order")
    parser.add_argument("--out", dest="out", default="media/videos/final_output.mp4", help="Output MP4 path")
    args = parser.parse_args()

    audio_paths = [Path(p) for p in args.audios]
    out = combine_video_with_audio(Path(args.video), audio_paths, Path(args.out))
    print(f"Final video: {out}")


if __name__ == "__main__":
    main()
