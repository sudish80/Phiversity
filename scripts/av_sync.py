import argparse
import os
import shutil
from pathlib import Path
from typing import List

# Configure moviepy to use system ffmpeg (Railway has ffmpeg installed via apt)
ffmpeg_binary = os.getenv("FFMPEG_BINARY")
if ffmpeg_binary:
    # Use explicitly set ffmpeg path
    import moviepy.config
    moviepy.config.FFMPEG_BINARY = ffmpeg_binary
elif not shutil.which("ffmpeg"):
    # If no explicit path and ffmpeg not in PATH, raise early
    raise RuntimeError(
        "ffmpeg not found in system PATH and FFMPEG_BINARY not set. "
        "On Railway, ffmpeg is installed via apt. "
        "On local Windows, set FFMPEG_BINARY in .env"
    )

try:
    # MoviePy 1.x
    from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_audioclips  # type: ignore
except Exception:
    # MoviePy 2.x exposes classes/functions at top-level
    from moviepy import AudioFileClip, VideoFileClip, concatenate_audioclips  # type: ignore


def combine_video_with_audio(video_path: Path, audio_paths: List[Path], out_path: Path) -> Path:
    # Validate audio files before processing
    for p in audio_paths:
        if not p.exists():
            raise RuntimeError(f"Audio file missing: {p}")
        if p.stat().st_size == 0:
            raise RuntimeError(f"Audio file is empty: {p}")

    clips = [AudioFileClip(str(p)) for p in audio_paths]
    final_audio = concatenate_audioclips(clips)
    video = VideoFileClip(str(video_path))
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if hasattr(video, "set_audio"):
            vclip = video.set_audio(final_audio)  # MoviePy 1.x style
        else:
            vclip = video.with_audio(final_audio)  # MoviePy 2.x style
        vclip.write_videofile(str(out_path), codec="libx264", audio_codec="aac")
    finally:
        # Close resources
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
