"""Text-to-speech with multiple engines and duration probing.

Engines:
  - edge : Microsoft neural voices via edge-tts (default, needs internet)
  - gtts : Google TTS via gTTS (needs internet)
  - silence: silent placeholder audio (offline testing / mute renders)

Every engine returns an audio file whose exact duration is probed with
ffprobe, so the pipeline can time the Manim animation to the voice-over.
"""

from __future__ import annotations

import asyncio
import subprocess
from pathlib import Path

from .config import TTSConfig


class TTSError(RuntimeError):
    pass


def ffprobe_duration(path: str | Path) -> float:
    """Exact media duration in seconds via ffprobe."""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, stdin=subprocess.DEVNULL, check=True)
    try:
        return float(out.stdout.strip())
    except ValueError as exc:
        raise TTSError(f"ffprobe could not read duration of {path}") from exc


def estimate_duration(text: str, wpm: float = 145.0) -> float:
    """Rough spoken duration of a text in seconds (used for silence engine)."""
    words = max(1, len(text.split()))
    return round(max(2.5, words / wpm * 60.0), 2)


def synthesize(text: str, out_path: str | Path,
               cfg: TTSConfig) -> tuple[Path, float]:
    """Speak `text` to `out_path`; returns (path, duration_seconds).

    Falls back to silence if the preferred online engine fails, so a
    network hiccup degrades voice quality instead of killing the render.
    """
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    engine = cfg.engine.lower()
    try:
        if engine == "edge":
            _edge_tts(text, out_path, cfg)
        elif engine == "gtts":
            _gtts(text, out_path, cfg)
        elif engine == "silence":
            _silence(text, out_path)
        else:
            raise TTSError(f"Unknown TTS engine: {engine!r}")
    except Exception as exc:  # noqa: BLE001 - degrade, don't die
        if engine == "silence":
            raise
        print(f"  [warn] {engine} TTS failed ({exc}); using silence. "
              f"Voice-over for this segment will be missing.")
        _silence(text, out_path)
    return out_path, ffprobe_duration(out_path)


def _edge_tts(text: str, out_path: Path, cfg: TTSConfig) -> None:
    import edge_tts

    async def _run() -> None:
        communicate = edge_tts.Communicate(text, cfg.voice, rate=cfg.rate)
        await communicate.save(str(out_path))

    asyncio.run(_run())


def _gtts(text: str, out_path: Path, cfg: TTSConfig) -> None:
    from gtts import gTTS

    gTTS(text=text, lang=cfg.language or "en").save(str(out_path))


def _silence(text: str, out_path: Path) -> None:
    duration = estimate_duration(text)
    subprocess.run(
        ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
         "-i", "anullsrc=r=44100:cl=mono", "-t", str(duration),
         "-c:a", "pcm_s16le", str(out_path)],
        stdin=subprocess.DEVNULL, check=True)
