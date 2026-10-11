"""Configuration loading: environment variables, .env files, CLI overrides."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path


def load_env_file(path: str | Path = ".env") -> dict:
    """Tiny .env loader (KEY=VALUE lines, '#' comments). Does not override."""
    env = {}
    p = Path(path)
    if not p.is_file():
        return env
    for line in p.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    for key, value in env.items():
        os.environ.setdefault(key, value)
    return env


def _first_env(*names: str, default: str | None = None) -> str | None:
    for name in names:
        value = os.environ.get(name)
        if value:
            return value
    return default


# legacy environment variable names (pre-rename), still honoured
_LEGACY_ENV = {"PHIVERSITY_PROVIDER": "LECTUREFORGE_PROVIDER",
              "PHIVERSITY_VOICE": "LECTUREFORGE_VOICE"}


def _env(name: str) -> str | None:
    return _first_env(name, _LEGACY_ENV.get(name))


@dataclass
class LLMConfig:
    provider: str = "openai"          # "openai" (any compatible) | "anthropic"
    model: str = "gpt-4o-mini"
    api_key: str = ""
    base_url: str = "https://api.openai.com/v1"
    timeout: float = 180.0
    temperature: float = 0.6

    @classmethod
    def from_env(cls) -> "LLMConfig":
        provider = (_env("PHIVERSITY_PROVIDER") or "openai").lower()
        api_key = _first_env("LLM_API_KEY", "OPENAI_API_KEY", "NVIDIA_API_KEY",
                             "ANTHROPIC_API_KEY") or ""
        base_url = _first_env("LLM_BASE_URL", "OPENAI_BASE_URL") or ""
        model = _first_env("LLM_MODEL", "OPENAI_MODEL") or ""
        if not base_url:
            if "NVIDIA_API_KEY" in os.environ and not os.environ.get("OPENAI_API_KEY"):
                base_url = "https://integrate.api.nvidia.com/v1"
            elif provider == "anthropic":
                base_url = "https://api.anthropic.com"
            else:
                base_url = "https://api.openai.com/v1"
        if not model:
            model = ("claude-sonnet-4-20250514" if provider == "anthropic"
                     else "meta/llama-3.1-70b-instruct"
                     if "nvidia" in base_url else "gpt-4o-mini")
        return cls(provider=provider, model=model, api_key=api_key,
                   base_url=base_url.rstrip("/"))


@dataclass
class TTSConfig:
    engine: str = "edge"              # edge | gtts | silence
    voice: str = "en-US-AriaNeural"   # any Microsoft neural voice name
    language: str = "en"              # gTTS language code
    rate: str = "+0%"                 # edge-tts speaking rate, e.g. "+10%"

    @classmethod
    def from_env(cls, engine: str = "edge") -> "TTSConfig":
        return cls(engine=engine,
                   voice=_env("PHIVERSITY_VOICE") or "en-US-AriaNeural")


@dataclass
class RenderConfig:
    quality: str = "m"                # manim quality: l | m | h
    timeout: float = 420.0           # seconds per scene render
    heal_attempts: int = 2           # LLM fix retries on render failure
    latex: bool = True                # whether LaTeX is available for MathTex
    max_gap: float = 1.2             # max voice/animation freeze before a
                                     # paced re-render is triggered


@dataclass
class PipelineConfig:
    question: str = ""
    out_dir: Path = Path("lectures")
    max_segments: int = 5
    intro: bool = True
    captions: bool = False
    interactive: bool = False
    demo: bool | str = False     # True/"pythagoras"/"fma"/... (offline lectures)
    intro_clip: str | None = None  # brand clip (Intro.mp4) played before every video
    transitions: str = "none"    # "flip" (page turn) | "none" (straight cut)
    theme: str = "auto"          # visual preset: auto/math/lab/spatial/data/paper
    llm: LLMConfig = field(default_factory=LLMConfig.from_env)
    tts: TTSConfig = field(default_factory=TTSConfig.from_env)
    render: RenderConfig = field(default_factory=RenderConfig)


def detect_latex() -> bool:
    from shutil import which
    return which("pdflatex") is not None
