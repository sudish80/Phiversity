import argparse
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple


def _tts_gtts(text: str, out_path: Path):
    from gtts import gTTS

    tts = gTTS(text=text, lang=os.getenv("GOOGLE_TTS_LANGUAGE", "en"), tld=os.getenv("GOOGLE_TTS_TLD", "com"))
    tts.save(str(out_path))


def _tts_pyttsx3(text: str, out_path: Path):
    import pyttsx3

    engine = pyttsx3.init()
    rate = int(float(os.getenv("VOICE_RATE", "160")))
    volume = float(os.getenv("VOICE_VOLUME", "0.9"))
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    engine.save_to_file(text, str(out_path))
    engine.runAndWait()


def _tts_elevenlabs(text: str, out_path: Path):
    key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")
    if not key or not voice_id:
        raise RuntimeError("ELEVENLABS_API_KEY or ELEVENLABS_VOICE_ID not set")
    import json as _json
    import urllib.request
    import urllib.error

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    payload = {"text": text}
    model_id = os.getenv("ELEVENLABS_MODEL_ID")
    if model_id:
        payload["model_id"] = model_id
    data = _json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("xi-api-key", key)
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "audio/mpeg")
    timeout = int(float(os.getenv("VOICE_TIMEOUT", "15")))
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        audio = resp.read()
    out_path.write_bytes(audio)


def synthesize_scene_wise(data: Dict[str, Any], out_dir: Path) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    engine = os.getenv("VOICE_ENGINE", "gtts").lower()
    prefer_eleven = bool(os.getenv("ELEVENLABS_API_KEY"))

    audio_paths: List[Path] = []
    for idx, sc in enumerate(data.get("animation_plan", {}).get("scenes", []), start=1):
        text = sc.get("voiceover") or sc.get("description") or ""
        if not text.strip():
            # Fallback: synthesize from solution steps if available
            steps = (data.get("solution", {}) or {}).get("steps") or []
            if steps:
                parts = ["Narration:"]
                for i, st in enumerate(steps, start=1):
                    title = st.get("title") or "Step"
                    expl = st.get("explanation") or ""
                    parts.append(f"Step {i}: {title}. {expl}")
                text = ". ".join(parts)
            else:
                text = " "
        # Prefer ElevenLabs first when available; otherwise gTTS then pyttsx3
        if prefer_eleven or engine == "elevenlabs":
            ap = out_dir / f"scene_{idx:02d}.mp3"
            try:
                _tts_elevenlabs(text, ap)
            except Exception as e:
                print("[voiceover] ElevenLabs failed; falling back to TTS for scene", idx, "error:", e)
                if engine == "pyttsx3":
                    ap = out_dir / f"scene_{idx:02d}.wav"
                    _tts_pyttsx3(text, ap)
                else:
                    try:
                        _tts_gtts(text, ap)
                    except Exception:
                        print("[voiceover] gTTS failed; falling back to pyttsx3 for scene", idx)
                        ap = out_dir / f"scene_{idx:02d}.wav"
                        _tts_pyttsx3(text, ap)
        else:
            if engine == "pyttsx3":
                ap = out_dir / f"scene_{idx:02d}.wav"
                _tts_pyttsx3(text, ap)
            else:
                ap = out_dir / f"scene_{idx:02d}.mp3"
                try:
                    _tts_gtts(text, ap)
                except Exception:
                    print("[voiceover] gTTS failed; falling back to pyttsx3 for scene", idx)
                    ap = out_dir / f"scene_{idx:02d}.wav"
                    _tts_pyttsx3(text, ap)
        audio_paths.append(ap)
    return audio_paths


def get_audio_durations(paths: List[Path]) -> List[float]:
    try:
        from moviepy.editor import AudioFileClip  # type: ignore
    except Exception:
        from moviepy import AudioFileClip  # type: ignore

    durs: List[float] = []
    for p in paths:
        if not p.exists():
            durs.append(0.0)
            continue
        with AudioFileClip(str(p)) as c:
            durs.append(float(c.duration or 0.0))
    return durs


def synthesize_element_wise(data: Dict[str, Any], out_base: Path) -> List[List[Path]]:
    """Generate audio per element for each scene. Returns list[scene][element] -> audio path."""
    out_base.mkdir(parents=True, exist_ok=True)
    engine = os.getenv("VOICE_ENGINE", "gtts").lower()
    prefer_eleven = bool(os.getenv("ELEVENLABS_API_KEY"))

    scenes = data.get("animation_plan", {}).get("scenes", [])
    all_paths: List[List[Path]] = []
    for s_idx, sc in enumerate(scenes, start=1):
        scene_dir = out_base / f"scene_{s_idx:02d}"
        scene_dir.mkdir(parents=True, exist_ok=True)
        element_paths: List[Path] = []
        for e_idx, el in enumerate(sc.get("elements", []), start=1):
            text = (el.get("voiceover") or el.get("content") or " ")
            if not text.strip():
                # Fallback: use scene voiceover or description
                text = sc.get("voiceover") or sc.get("description") or " "
            if prefer_eleven or engine == "elevenlabs":
                ap = scene_dir / f"el_{e_idx:02d}.mp3"
                try:
                    _tts_elevenlabs(text, ap)
                except Exception as e:
                    print("[voiceover] ElevenLabs failed; falling back to TTS for element", e_idx, "scene", s_idx, "error:", e)
                    if engine == "pyttsx3":
                        ap = scene_dir / f"el_{e_idx:02d}.wav"
                        _tts_pyttsx3(text, ap)
                    else:
                        try:
                            _tts_gtts(text, ap)
                        except Exception:
                            print("[voiceover] gTTS failed; falling back to pyttsx3 for element", e_idx, "scene", s_idx)
                            ap = scene_dir / f"el_{e_idx:02d}.wav"
                            _tts_pyttsx3(text, ap)
            else:
                if engine == "pyttsx3":
                    ap = scene_dir / f"el_{e_idx:02d}.wav"
                    _tts_pyttsx3(text, ap)
                else:
                    ap = scene_dir / f"el_{e_idx:02d}.mp3"
                    try:
                        _tts_gtts(text, ap)
                    except Exception:
                        print("[voiceover] gTTS failed; falling back to pyttsx3 for element", e_idx, "scene", s_idx)
                        ap = scene_dir / f"el_{e_idx:02d}.wav"
                        _tts_pyttsx3(text, ap)
            element_paths.append(ap)
        all_paths.append(element_paths)
    return all_paths


def flatten_audio(nested: List[List[Path]]) -> List[Path]:
    flat: List[Path] = []
    for inner in nested:
        flat.extend(inner)
    return flat


def get_element_durations(nested: List[List[Path]]) -> List[List[float]]:
    try:
        from moviepy.editor import AudioFileClip  # type: ignore
    except Exception:
        from moviepy import AudioFileClip  # type: ignore

    all_durs: List[List[float]] = []
    for inner in nested:
        durs: List[float] = []
        for p in inner:
            if not p.exists():
                durs.append(0.0)
                continue
            with AudioFileClip(str(p)) as c:
                durs.append(float(c.duration or 0.0))
        all_durs.append(durs)
    return all_durs


def main():
    parser = argparse.ArgumentParser(description="Generate scene-wise voiceover audio files from structured JSON")
    parser.add_argument("json", help="Path to structured JSON (SolverOutput)")
    parser.add_argument("--out-dir", dest="out_dir", default="media/texts/voice", help="Directory to save audio files")
    args = parser.parse_args()

    import json

    data = json.loads(Path(args.json).read_text(encoding="utf-8"))
    out_dir = Path(args.out_dir)
    paths = synthesize_scene_wise(data, out_dir)
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
