import argparse
import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dotenv import load_dotenv

# Load .env from project root so CLI usage sees the same config as the server.
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=True)


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


def _resolve_voice_engine() -> Tuple[str, bool]:
    engine = os.getenv("VOICE_ENGINE", "gtts").lower()
    key_present = bool(os.getenv("ELEVENLABS_API_KEY"))
    if engine == "elevenlabs" and not key_present:
        print("[voiceover] ELEVENLABS_API_KEY missing; falling back to gtts")
        engine = "gtts"
    return engine, key_present


def _clean_latex_from_voiceover(text: str) -> str:
    """Remove or convert LaTeX formulas to readable text for TTS."""
    import re
    
    # Replace common LaTeX commands with readable equivalents
    replacements = {
        r'\\frac\{([^}]+)\}\{([^}]+)\}': r'\1 over \2',
        r'\\mathbf\{([^}]+)\}': r'\1',
        r'\\mathit\{([^}]+)\}': r'\1',
        r'\\mathrm\{([^}]+)\}': r'\1',
        r'\\cdot': 'times',
        r'\\times': 'times',
        r'\\div': 'divided by',
        r'\\\{': '{',
        r'\\\}': '}',
        r'\^': 'to the power',
        r'\\Rightarrow': 'implies',
        r'\\rightarrow': 'approaches',
        r'\\approx': 'approximately equals',
        r'\\neq': 'not equal to',
        r'\\leq': 'less than or equal to',
        r'\\geq': 'greater than or equal to',
        r'\\infty': 'infinity',
        r'\\alpha': 'alpha',
        r'\\beta': 'beta',
        r'\\gamma': 'gamma',
        r'\\delta': 'delta',
        r'\\epsilon': 'epsilon',
        r'\\lambda': 'lambda',
        r'\\mu': 'mu',
        r'\\nu': 'nu',
        r'\\pi': 'pi',
        r'\\sigma': 'sigma',
        r'\\tau': 'tau',
        r'\\phi': 'phi',
        r'\\omega': 'omega',
    }
    
    result = text
    for latex_pattern, readable in replacements.items():
        result = re.sub(latex_pattern, readable, result, flags=re.IGNORECASE)
    
    # Remove any remaining backslashes and braces
    result = re.sub(r'\\[a-zA-Z]+', '', result)
    result = re.sub(r'[{}]', '', result)
    result = re.sub(r'\s+', ' ', result).strip()
    
    return result


def synthesize_scene_wise(data: Dict[str, Any], out_dir: Path) -> List[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    engine, prefer_eleven = _resolve_voice_engine()

    audio_paths: List[Path] = []
    for idx, sc in enumerate(data.get("animation_plan", {}).get("scenes", []), start=1):
        text = sc.get("voiceover") or sc.get("description") or ""
        # Clean LaTeX from voiceover for TTS
        text = _clean_latex_from_voiceover(text)
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
        # Prefer ElevenLabs first when available; otherwise always use gTTS (works in Docker)
        ap = out_dir / f"scene_{idx:02d}.mp3"
        if prefer_eleven or engine == "elevenlabs":
            try:
                _tts_elevenlabs(text, ap)
            except Exception as e:
                print(f"[voiceover] ElevenLabs failed for scene {idx}, using gTTS fallback. Error: {e}")
                _tts_gtts(text, ap)
        else:
            # Always use gtts in production (Docker-compatible)
            _tts_gtts(text, ap)
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
    engine, prefer_eleven = _resolve_voice_engine()

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
