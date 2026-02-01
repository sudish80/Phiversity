import os
import time
import json
from pathlib import Path


def read_env_values() -> dict:
    """Parse the workspace .env file without modifying process environment."""
    env: dict = {}
    try:
        from dotenv import dotenv_values
        root = Path(__file__).resolve().parents[1]
        env_path = root / ".env"
        if env_path.exists():
            env = dict(dotenv_values(str(env_path)))
    except Exception:
        pass
    return env


def _result(service: str):
    return {
        "service": service,
        "reachable": False,
        "auth_valid": False,
        "model": None,
        "latency_ms": None,
        "error": None,
    }


def check_openai(env: dict) -> dict:
    res = _result("openai")
    key = env.get("OPENAI_API_KEY")
    model = env.get("OPENAI_MODEL", "gpt-4o-mini")
    if not key:
        res["error"] = "OPENAI_API_KEY not set"
        return res
    try:
        from openai import OpenAI
        t0 = time.perf_counter()
        # Do not pass organization header; use only API key from .env
        client = OpenAI(api_key=key)
        # Light-weight call: list models; falls back to trivial chat if not allowed
        try:
            _ = client.models.list()
            res["reachable"] = True
            res["auth_valid"] = True
            res["model"] = model
        except Exception:
            # Try a tiny completion to detect 401/keys issues
            _ = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": "ping"}],
                temperature=0.0,
            )
            res["reachable"] = True
            res["auth_valid"] = True
            res["model"] = model
        finally:
            res["latency_ms"] = int((time.perf_counter() - t0) * 1000)
    except Exception as e:
        res["error"] = str(e)
    return res


def check_deepseek(env: dict) -> dict:
    res = _result("deepseek")
    key = env.get("DEEPSEEK_API_KEY")
    model = env.get("DEEPSEEK_MODEL", "deepseek-chat")
    base_url = env.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    if not key:
        res["error"] = "DEEPSEEK_API_KEY not set"
        return res
    try:
        from openai import OpenAI
        t0 = time.perf_counter()
        client = OpenAI(api_key=key, base_url=base_url)
        # DeepSeek supports Chat Completions via OpenAI SDK
        _ = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "ping"}],
            temperature=0.0,
        )
        res["reachable"] = True
        res["auth_valid"] = True
        res["model"] = model
        res["latency_ms"] = int((time.perf_counter() - t0) * 1000)
    except Exception as e:
        res["error"] = str(e)
    return res


def check_ollama(env: dict) -> dict:
    res = _result("ollama")
    base = env.get("OLLAMA_BASE_URL")
    model = env.get("OLLAMA_MODEL")
    if not base:
        res["error"] = "OLLAMA_BASE_URL not set"
        return res
    try:
        import json as _json
        import urllib.request
        import urllib.error

        t0 = time.perf_counter()
        # Try multiple endpoints and hosts
        hosts = [base.rstrip("/"), "http://127.0.0.1:11434"]
        paths = ["/api/version", "/api/tags"]
        ok = False
        last_err = None
        for h in hosts:
            for p in paths:
                try:
                    req = urllib.request.Request(h + p)
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        _ = _json.loads(resp.read().decode("utf-8"))
                    ok = True
                    break
                except Exception as e:
                    last_err = e
            if ok:
                break
        if ok:
            res["reachable"] = True
            res["auth_valid"] = True  # local servers generally don't require auth
            res["model"] = model
            res["latency_ms"] = int((time.perf_counter() - t0) * 1000)
        else:
            raise last_err or Exception("Ollama not reachable")
    except Exception as e:
        res["error"] = str(e)
    return res


def check_elevenlabs(env: dict) -> dict:
    res = _result("elevenlabs")
    key = env.get("ELEVENLABS_API_KEY")
    vid = env.get("ELEVENLABS_VOICE_ID")
    if not key:
        res["error"] = "ELEVENLABS_API_KEY not set"
        return res
    try:
        import json as _json
        import urllib.request
        import urllib.error

        t0 = time.perf_counter()
        api = "https://api.elevenlabs.io/v1"
        # Lightweight validation: list voices (auth required)
        req = urllib.request.Request(api + "/voices")
        req.add_header("xi-api-key", key)
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = _json.loads(resp.read().decode("utf-8"))
        res["reachable"] = True
        res["auth_valid"] = True
        res["model"] = vid
        res["latency_ms"] = int((time.perf_counter() - t0) * 1000)
    except Exception as e:
        res["error"] = str(e)
    return res


def write_results(results: dict):
    root = Path(__file__).resolve().parents[1]  # workspace root
    out_test = root / "test" / "llm_key_check.json"
    out_webjob_dir = root / "web_jobs" / "testjobfile"
    out_webjob_dir.mkdir(parents=True, exist_ok=True)
    out_webjob = out_webjob_dir / "llm_key_check.json"
    # Also write under media/texts so the FastAPI static mount can serve it
    out_media_dir = root / "media" / "texts"
    out_media_dir.mkdir(parents=True, exist_ok=True)
    out_media = out_media_dir / "llm_key_check.json"
    payload = json.dumps(results, indent=2)
    out_test.write_text(payload, encoding="utf-8")
    out_webjob.write_text(payload, encoding="utf-8")
    out_media.write_text(payload, encoding="utf-8")
    return [out_test, out_webjob, out_media]


def main():
    env = read_env_values()
    # Optional Gemini check
    def check_gemini(env: dict) -> dict:
        res = _result("gemini")
        key = env.get("GEMINI_API_KEY") or env.get("GOOGLE_API_KEY")
        model = env.get("GEMINI_MODEL", "gemini-flash-latest")
        if not key:
            res["error"] = "GEMINI_API_KEY/GOOGLE_API_KEY not set"
            return res
        try:
            import google.generativeai as genai  # type: ignore
            t0 = time.perf_counter()
            genai.configure(api_key=key, transport='rest')
            m = genai.GenerativeModel(model)
            # Tiny probe call
            _ = m.generate_content("ping")
            res["reachable"] = True
            res["auth_valid"] = True
            res["model"] = model
            res["latency_ms"] = int((time.perf_counter() - t0) * 1000)
        except Exception as e:
            res["error"] = str(e)
        return res

    checks = [check_openai(env), check_deepseek(env), check_gemini(env), check_elevenlabs(env)]
    # Optional Ollama check if URL present
    if env.get("OLLAMA_BASE_URL"):
        checks.append(check_ollama(env))
    # Offline TTS availability (pyttsx3) — treat as voice fallback
    def check_pyttsx3() -> dict:
        res = _result("pyttsx3")
        try:
            import pyttsx3
            from tempfile import NamedTemporaryFile
            t0 = time.perf_counter()
            eng = pyttsx3.init()
            with NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                tmp_path = tmp.name
            eng.save_to_file("ping", tmp_path)
            eng.runAndWait()
            res["reachable"] = True
            res["auth_valid"] = True
            res["model"] = "offline"
            res["latency_ms"] = int((time.perf_counter() - t0) * 1000)
            try:
                Path(tmp_path).unlink(missing_ok=True)
            except Exception:
                pass
        except Exception as e:
            res["error"] = str(e)
        return res
    checks.append(check_pyttsx3())
    pass_services = [c.get("service") for c in checks if c.get("reachable") and c.get("auth_valid")]
    results = {
        "checks": checks,
        "summary": {
            "any_pass": bool(pass_services),
            "pass_count": len(pass_services),
            "services_pass": pass_services,
        },
        "timestamp": int(time.time()),
    }
    paths = write_results(results)
    for p in paths:
        print(p)
    # Console summary for quick human reading
    print("\nSummary:")
    for c in checks:
        status = "PASS" if (c.get("reachable") and c.get("auth_valid")) else "FAIL"
        svc = c.get("service")
        err = c.get("error")
        lat = c.get("latency_ms")
        if status == "PASS":
            print(f"- {svc}: PASS (latency {lat} ms)")
        else:
            print(f"- {svc}: FAIL ({err})")
    print(f"- overall: {'PASS' if results['summary']['any_pass'] else 'FAIL'} (min one service must pass; {results['summary']['pass_count']} passed: {', '.join(results['summary']['services_pass']) or 'none'})")


if __name__ == "__main__":
    main()
