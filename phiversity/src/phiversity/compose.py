"""ffmpeg composition: align voice-over with each rendered segment, then
stitch all segments into the final lecture video.

Per segment:
  1. probe video and audio durations
  2. if the voice runs longer than the animation, freeze the last frame
     (tpad) so visuals wait for the narration to finish
  3. if the animation outlasts the voice, pad the audio with silence (apad)
  4. re-encode to one uniform codec profile so all segments concatenate
     cleanly, optionally burning the narration as subtitles

Finally all segments are concatenated losslessly (-c copy).
"""

from __future__ import annotations

import subprocess
from pathlib import Path

from .tts import ffprobe_duration

UNIFORM = ["-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
           "-ar", "44100", "-ac", "2", "-movflags", "+faststart"]

# burned-in captions: centered at the bottom, readable over animation
CAPTION_STYLE = ("Alignment=2,FontName=DejaVu Sans,FontSize=18,"
                 "PrimaryColour=&H00FFFFFF,OutlineColour=&H80000000,"
                 "Outline=1,Shadow=1,MarginV=28")


class ComposeError(RuntimeError):
    pass


def _run(cmd: list[str]) -> None:
    proc = subprocess.run(cmd, capture_output=True, text=True,
                          stdin=subprocess.DEVNULL)
    if proc.returncode != 0:
        raise ComposeError((proc.stderr or proc.stdout)[-2000:])


def has_audio_stream(path: str | Path) -> bool:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "a",
         "-show_entries", "stream=codec_type", "-of", "csv=p=0",
         str(path)],
        capture_output=True, text=True, stdin=subprocess.DEVNULL, check=True)
    return "audio" in out.stdout


def normalize_foreign(video: str | Path, out: str | Path, width: int,
                      height: int, fps: int) -> Path:
    """Re-encode any external clip (Intro.mp4, transitions) to the uniform
    profile: scaled + letterboxed to the target frame, converted fps, and
    an audio track (kept if present, silence otherwise) so it concatenates
    cleanly with the lecture segments."""
    video, out = Path(video), Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    duration = ffprobe_duration(video)
    vf = (f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
          f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1,fps={fps}")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(video)]
    if has_audio_stream(video):
        cmd += ["-map", "0:v:0", "-map", "0:a:0",
                "-af", f"apad=whole_dur={duration:.3f}"]
    else:
        cmd += ["-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
                "-map", "0:v:0", "-map", "1:a", "-shortest"]
    cmd += ["-vf", vf, "-t", f"{duration:.3f}", *UNIFORM, str(out)]
    _run(cmd)
    return out


def align_and_mux(video: str | Path, audio: str | Path,
                  out: str | Path, srt: str | Path | None = None) -> Path:
    """Mux one segment, padding the shorter stream, optional burned subs."""
    video, audio, out = Path(video), Path(audio), Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    dv, da = ffprobe_duration(video), ffprobe_duration(audio)
    target = max(dv, da)

    filters = []
    pad = max(0.0, da - dv)
    video_chain = ""
    if pad > 0.05:
        video_chain += f"tpad=stop_mode=clone:stop_duration={pad:.3f}"
    if srt is not None and Path(srt).is_file():
        sub = (f"subtitles={_escape_filter_path(Path(srt).resolve())}:"
               f"force_style='{CAPTION_STYLE}'")
        video_chain = f"{video_chain},{sub}" if video_chain else sub
    if video_chain:
        filters.append(f"[0:v]{video_chain}[v]")
        vlabel = "[v]"
    else:
        vlabel = "0:v"

    gap = max(0.0, dv - da)
    if gap > 0.05:
        filters.append(f"[1:a]apad=whole_dur={dv:.3f}[a]")
        alabel = "[a]"
    else:
        alabel = "1:a"

    cmd = ["ffmpeg", "-y", "-v", "error", "-i", str(video), "-i", str(audio)]
    if filters:
        cmd += ["-filter_complex", ";".join(filters)]
    cmd += ["-map", vlabel, "-map", alabel, *UNIFORM, str(out)]
    _run(cmd)
    return out


def concat(parts: list[str | Path], out: str | Path) -> Path:
    """Losslessly concatenate uniformly-encoded segments."""
    if not parts:
        raise ComposeError("nothing to concatenate")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    if len(parts) == 1:
        Path(parts[0]).replace(out)
        return out
    list_file = out.parent / "concat.txt"
    with list_file.open("w", encoding="utf-8") as fh:
        for part in parts:
            # concat demuxer resolves paths relative to the list file's
            # location, so always write absolute paths
            fh.write(f"file '{Path(part).resolve().as_posix()}'\n")
    _run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
          "-i", str(list_file), "-c", "copy", "-movflags", "+faststart",
          str(out)])
    return out


def crossfade_join(clip_a: str | Path, clip_b: str | Path, kind: str,
                   out: str | Path, duration: float = 0.6) -> Path:
    """Join two uniform clips with a video xfade + audio acrossfade."""
    from .director import XFADE_MAP, normalize_transition
    transition = XFADE_MAP.get(normalize_transition(kind), "fade")
    clip_a, clip_b, out = Path(clip_a), Path(clip_b), Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    offset = max(0.0, ffprobe_duration(clip_a) - duration)
    filters = (f"[0:v][1:v]xfade=transition={transition}"
               f":duration={duration}:offset={offset:.3f}[v];"
               f"[0:a][1:a]acrossfade=d={duration}[a]")
    _run(["ffmpeg", "-y", "-v", "error", "-i", str(clip_a),
          "-i", str(clip_b), "-filter_complex", filters,
          "-map", "[v]", "-map", "[a]", *UNIFORM, str(out)])
    return out


def smart_concat(parts: list[str | Path], junctions: list[str],
                 out: str | Path, fade_duration: float = 0.6) -> Path:
    """Concatenate clips using per-junction transition types.

    Fade-type junctions ("fade", "wipe", "dissolve", topic changes) become
    ffmpeg crossfades; continuity junctions ("carry-over", "slide-up",
    "answer-reveal") stay hard cuts because the visual continuity lives
    inside the scene code itself. Clips are grouped into blocks separated
    by cuts: crossfades join clips inside a block (re-encoded to the same
    uniform profile), blocks are then concatenated losslessly.
    """
    from .director import is_cut
    if not parts:
        raise ComposeError("nothing to concatenate")
    if len(junctions) != len(parts) - 1:
        raise ComposeError(f"expected {len(parts) - 1} junctions, "
                           f"got {len(junctions)}")
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)

    blocks: list[list[Path]] = [[Path(parts[0])]]
    block_kinds: list[list[str]] = [[]]   # fade kind per join inside a block
    for clip, kind in zip(parts[1:], junctions):
        if is_cut(kind):
            blocks.append([Path(clip)])
            block_kinds.append([])
        else:
            blocks[-1].append(Path(clip))
            block_kinds[-1].append(kind)

    work = out.parent / "xfade_work"
    work.mkdir(parents=True, exist_ok=True)
    rendered: list[Path] = []
    for index, block in enumerate(blocks):
        current = block[0]
        for step, (clip, kind) in enumerate(zip(block[1:],
                                               block_kinds[index])):
            joined = work / f"block{index}_{step}.mp4"
            current = crossfade_join(current, clip, kind, joined,
                                      duration=fade_duration)
        rendered.append(current)
    if len(rendered) == 1:
        shutil_copy(rendered[0], out)
        return out
    return concat(rendered, out)


def shutil_copy(src: Path, dst: Path) -> None:
    import shutil
    shutil.copyfile(src, dst)


def write_segment_srt(narration: str, duration: float,
                      out: str | Path, caption_width: int = 42) -> Path:
    """One-cue SRT spanning the whole (padded) segment, text wrapped."""
    out = Path(out)
    out.parent.mkdir(parents=True, exist_ok=True)
    lines = _wrap(narration, caption_width)
    cues = [(0.0, duration, lines)]
    out.write_text(_format_srt(cues), encoding="utf-8")
    return out


def _escape_filter_path(path: Path) -> str:
    """Escape a path for use inside an ffmpeg filter argument."""
    text = str(path).replace("\\", "/")
    return (text.replace("\\", "\\\\")
                .replace(":", "\\:")
                .replace("'", "\\'"))


def _wrap(text: str, width: int) -> list[str]:
    words, lines, current = text.split(), [], ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = f"{current} {word}".strip()
    if current:
        lines.append(current)
    return lines


def _ts(seconds: float) -> str:
    ms = max(0, round(seconds * 1000))
    h, rem = divmod(ms, 3600000)
    m, rem = divmod(rem, 60000)
    s, ms = divmod(rem, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def _format_srt(cues: list[tuple[float, float, list[str]]]) -> str:
    blocks = []
    for i, (start, end, lines) in enumerate(cues, 1):
        body = "\n".join(lines)
        blocks.append(f"{i}\n{_ts(start)} --> {_ts(end)}\n{body}\n")
    return "\n".join(blocks)
