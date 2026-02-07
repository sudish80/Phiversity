import argparse
import os
import shutil
from pathlib import Path
from typing import List

# Constants for video processing
INTRO_VIDEO_NAME = "intro.mp4"

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
    from moviepy.editor import AudioFileClip, VideoFileClip, concatenate_audioclips, speedx  # type: ignore
    MOVIEPY_VERSION = 1
except Exception:
    # MoviePy 2.x exposes classes/functions at top-level
    from moviepy import AudioFileClip, VideoFileClip, concatenate_audioclips, vfx  # type: ignore
    MOVIEPY_VERSION = 2
    speedx = None  # Not needed for MoviePy 2.x


def combine_video_with_audio(video_path: Path, audio_paths: List[Path], out_path: Path) -> Path:
    """Combine video with audio ensuring perfect synchronization.
    
    This function concatenates multiple audio files and overlays them on the video
    with perfect timing. It handles duration mismatches by adjusting video speed
    or padding audio as needed.
    
    Args:
        video_path: Path to the silent video file
        audio_paths: List of audio file paths to concatenate in order
        out_path: Output path for the final video with audio
    
    Returns:
        Path to the output video
    """
    # Validate audio files before processing
    for p in audio_paths:
        if not p.exists():
            raise RuntimeError(f"Audio file missing: {p}")
        if p.stat().st_size == 0:
            raise RuntimeError(f"Audio file is empty: {p}")

    print(f"[av_sync] Loading {len(audio_paths)} audio file(s)...")
    clips = [AudioFileClip(str(p)) for p in audio_paths]
    
    # Concatenate all audio clips
    print(f"[av_sync] Concatenating audio clips...")
    final_audio = concatenate_audioclips(clips)
    audio_duration = final_audio.duration
    print(f"[av_sync] Total audio duration: {audio_duration:.3f}s")
    
    print(f"[av_sync] Loading video: {video_path}")
    video = VideoFileClip(str(video_path))
    video_duration = video.duration
    print(f"[av_sync] Video duration: {video_duration:.3f}s")
    
    # Check for duration mismatch and handle it
    duration_diff = abs(video_duration - audio_duration)
    if duration_diff > 0.1:  # More than 100ms difference
        print(f"[av_sync] WARNING: Duration mismatch detected: {duration_diff:.3f}s difference")
        
        if audio_duration > video_duration:
            # Audio is longer - speed up video to match audio duration
            speedup_factor = audio_duration / video_duration
            print(f"[av_sync] Adjusting video speed by {speedup_factor:.4f}x to match audio duration")
            try:
                # Speed up video to match audio (factor > 1 speeds up)
                if MOVIEPY_VERSION == 1:
                    video = video.fx(speedx, speedup_factor)
                else:
                    # MoviePy 2.x: use MultiplySpeed effect
                    video = video.with_effects([vfx.MultiplySpeed(speedup_factor)])
                print(f"[av_sync] Video adjusted to {video.duration:.3f}s")
            except Exception as e:
                print(f"[av_sync] WARNING: Could not adjust video speed: {e}")
                print(f"[av_sync] Video may be shorter than audio, resulting in cut-off audio")
        else:
            # Video is longer - speed up audio or pad with silence
            if duration_diff < 1.0:
                # Small difference - add silence padding to audio
                try:
                    if MOVIEPY_VERSION == 1:
                        from moviepy.audio.AudioClip import AudioClip
                    else:
                        from moviepy import AudioClip
                    
                    print(f"[av_sync] Adding {duration_diff:.3f}s of silence padding to audio")
                    # Create silence clip
                    silence = AudioClip(lambda t: 0, duration=duration_diff, fps=final_audio.fps)
                    final_audio = concatenate_audioclips([final_audio, silence])
                    audio_duration = final_audio.duration
                    print(f"[av_sync] Audio padded to {audio_duration:.3f}s")
                except Exception as e:
                    print(f"[av_sync] WARNING: Could not pad audio: {e}")
            else:
                # Large difference - trim video to match audio
                print(f"[av_sync] Trimming video to match audio duration")
                video = video.subclip(0, audio_duration)
                print(f"[av_sync] Video trimmed to {video.duration:.3f}s")
    else:
        print(f"[av_sync] ✓ Audio and video durations match (diff: {duration_diff:.3f}s)")
    
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Set audio with perfect sync (start at t=0)
        if hasattr(video, "set_audio"):
            vclip = video.set_audio(final_audio)  # MoviePy 1.x style
        else:
            vclip = video.with_audio(final_audio)  # MoviePy 2.x style
        
        # Write with optimal settings for audio-video sync
        print(f"[av_sync] Writing final video with synchronized audio...")
        vclip.write_videofile(
            str(out_path),
            codec="libx264",
            audio_codec="aac",
            fps=video.fps,  # Maintain original FPS
            audio_bitrate="192k",  # High quality audio
            bitrate="5000k",  # High quality video
            preset="medium",  # Balance between speed and quality
            threads=4,  # Use multiple threads for faster encoding
            logger=None,  # Suppress verbose output
            temp_audiofile="temp-audio.m4a",  # Use temp file for audio processing
            remove_temp=True,  # Clean up temp files
            audio_fps=44100  # Standard audio sample rate for perfect sync
        )
        print(f"[av_sync] ✓ Video with synchronized audio written to: {out_path}")
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


def prepend_intro_to_video(intro_path: Path, main_video_path: Path, out_path: Path) -> Path:
    """Prepend an intro video to the main video with perfect audio-video sync.
    
    This function concatenates an intro video with the main video, ensuring that
    both videos have matching frame rates and audio settings for perfect synchronization.
    
    Args:
        intro_path: Path to intro.mp4 video file
        main_video_path: Path to the main video (final.mp4)
        out_path: Output path for the combined video
    
    Returns:
        Path to the combined video with intro
    """
    # Check if intro exists
    if not intro_path.exists():
        print(f"[av_sync] WARNING: Intro video not found at {intro_path}")
        print(f"[av_sync] Skipping intro prepend, using main video as-is")
        # If no intro, just copy main video to output
        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(main_video_path), str(out_path))
        return out_path
    
    if not main_video_path.exists():
        raise RuntimeError(f"Main video not found: {main_video_path}")
    
    try:
        if MOVIEPY_VERSION == 1:
            from moviepy.editor import concatenate_videoclips, VideoFileClip  # type: ignore
        else:
            from moviepy import concatenate_videoclips, VideoFileClip  # type: ignore
    except Exception:
        from moviepy import concatenate_videoclips, VideoFileClip  # type: ignore
    
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"[av_sync] Loading intro video: {intro_path}")
    intro_clip = VideoFileClip(str(intro_path))
    print(f"[av_sync] Intro: {intro_clip.duration:.2f}s @ {intro_clip.fps}fps, audio: {intro_clip.audio is not None}")
    
    print(f"[av_sync] Loading main video: {main_video_path}")
    main_clip = VideoFileClip(str(main_video_path))
    print(f"[av_sync] Main: {main_clip.duration:.2f}s @ {main_clip.fps}fps, audio: {main_clip.audio is not None}")
    
    try:
        # Ensure both clips have the same FPS for smooth concatenation
        target_fps = main_clip.fps
        if abs(intro_clip.fps - main_clip.fps) > 0.1:
            print(f"[av_sync] Adjusting intro FPS from {intro_clip.fps} to {target_fps} for sync")
            intro_clip = intro_clip.set_fps(target_fps)
        
        print(f"[av_sync] Concatenating intro ({intro_clip.duration:.2f}s) + main ({main_clip.duration:.2f}s)")
        
        # Concatenate with method="compose" for better audio/video sync
        combined = concatenate_videoclips([intro_clip, main_clip], method="compose")
        total_duration = combined.duration
        print(f"[av_sync] Combined duration: {total_duration:.2f}s")
        
        # Write with optimal sync settings
        print(f"[av_sync] Writing combined video with synchronized audio to {out_path}")
        combined.write_videofile(
            str(out_path),
            codec="libx264",
            audio_codec="aac",
            fps=target_fps,  # Use consistent FPS
            audio_bitrate="192k",  # High quality audio
            bitrate="5000k",  # High quality video
            preset="medium",
            threads=4,
            logger=None,  # Suppress verbose output
            temp_audiofile="temp-audio-intro.m4a",
            remove_temp=True,
            audio_fps=44100  # Standard audio sample rate
        )
        print(f"[av_sync] ✓ Intro prepend complete: {out_path}")
    finally:
        # Close resources
        try:
            intro_clip.close()
        except Exception:
            pass
        try:
            main_clip.close()
        except Exception:
            pass
        try:
            combined.close()
        except Exception:
            pass
    
    return out_path


def add_logo_watermark(video_path: Path, output_path: Path, logo_path: Path = None, margin: int = 10, opacity: float = 0.8) -> Path:
    """Add a logo watermark to the bottom right corner of a video.
    
    Args:
        video_path: Path to input video file
        output_path: Path for output video with logo
        logo_path: Path to logo image file (PNG with transparency recommended)
                   If None, looks for logo.png in project media/assets/ directory
        margin: Pixels from bottom-right corner (default 10)
        opacity: Logo opacity 0.0-1.0 (default 0.8)
    
    Returns:
        Path to output video with logo watermark
    """
    if not video_path.exists():
        raise RuntimeError(f"Video not found: {video_path}")
    
    # Determine logo path
    if logo_path is None:
        # Look for logo in media/assets/
        root = Path(__file__).resolve().parents[1]  # scripts/av_sync.py -> project root
        logo_path = root / "media" / "assets" / "logo.png"
    
    logo_path = Path(logo_path)
    
    # If logo doesn't exist, skip watermarking
    if not logo_path.exists():
        print(f"[av_sync] Logo not found at {logo_path}, skipping watermark")
        shutil.copy2(str(video_path), str(output_path))
        return output_path
    
    try:
        if MOVIEPY_VERSION == 1:
            from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip  # type: ignore
        else:
            from moviepy import VideoFileClip, ImageClip, CompositeVideoClip  # type: ignore
    except Exception:
        from moviepy import VideoFileClip, ImageClip, CompositeVideoClip  # type: ignore
    
    try:
        print(f"[av_sync] Loading video for logo watermark: {video_path}")
        video = VideoFileClip(str(video_path))
        
        print(f"[av_sync] Loading logo: {logo_path}")
        logo = ImageClip(str(logo_path))
        
        # Scale logo to be 10% of video width but not more than 150px
        max_logo_width = min(int(video.w * 0.1), 150)
        logo_aspect = logo.w / logo.h if logo.h > 0 else 1
        logo = logo.resize(newsize=(max_logo_width, int(max_logo_width / logo_aspect)))
        
        # Set logo opacity
        logo = logo.with_opacity(opacity)
        
        # Position in bottom right corner
        logo = logo.set_position((video.w - logo.w - margin, video.h - logo.h - margin))
        
        # Set logo duration to match video
        logo = logo.set_duration(video.duration)
        
        # Composite: place logo on top of video
        print(f"[av_sync] Compositing logo onto video...")
        final = CompositeVideoClip([video, logo])
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        print(f"[av_sync] Writing video with logo watermark to {output_path}")
        final.write_videofile(str(output_path), codec="libx264", audio_codec="aac", verbose=False, logger=None)
        print(f"[av_sync] ✓ Logo watermark added: {output_path}")
        
        return output_path
    except Exception as e:
        print(f"[av_sync] ERROR adding logo watermark: {e}")
        print(f"[av_sync] Falling back: copying video without watermark")
        shutil.copy2(str(video_path), str(output_path))
        return output_path
    finally:
        # Clean up resources
        try:
            video.close()
        except Exception:
            pass
        try:
            logo.close()
        except Exception:
            pass


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
