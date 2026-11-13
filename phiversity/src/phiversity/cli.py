"""Phiversity command line interface."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from .config import (LLMConfig, PipelineConfig, RenderConfig, TTSConfig,
                     load_env_file)
from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="phiversity",
        description="Ask a question, get a narrated lecture video: an LLM "
                    "writes the Manim animation code, TTS adds the voice-over, "
                    "ffmpeg glues it together.",
        epilog="example: phiversity \"Explain the Pythagorean theorem\" "
               "--voice en-US-GuyNeural --captions")
    parser.add_argument("question", nargs="?", default="",
                        help="the question / topic for the lecture")
    parser.add_argument("-f", "--file", metavar="PATH",
                        help="read the question from a file instead")
    parser.add_argument("-o", "--out", default=os.environ.get("PHIVERSITY_OUT_DIR", "lectures"), metavar="DIR",
                        help="output directory (default: $PHIVERSITY_OUT_DIR or ./lectures/<slug>)")
    parser.add_argument("--demo", nargs="?", const="pythagoras",
                        metavar="TOPIC", default=None,
                        help="build a bundled offline lecture instead of using "
                             "the LLM (no API key needed). Topics: "
                             "'pythagoras' (default), 'fma' (Newton's second "
                             "law), 'car-friction' (moving car + tire zoom), "
                             "'spring-blocks' (two-block spring system with "
                             "separation). Voice needs internet; add --tts "
                             "silence offline")
    parser.add_argument("--intro-clip", metavar="PATH", default=None,
                        help="brand clip played before every lecture "
                             "(default: auto-detect ./Intro.mp4)")
    parser.add_argument("--no-intro-clip", action="store_true",
                        help="never prepend an intro clip, even if "
                             "Intro.mp4 exists in the working directory")
    parser.add_argument("--transitions", choices=["none", "flip"],
                        default="none",
                        help="transition spliced between segments: 'none' "
                             "cuts straight to the next scene (default), "
                             "'flip' adds a page-turn clip")
    parser.add_argument("--theme", default="auto", metavar="PRESET",
                        help="visual theme preset: auto (the planner picks), "
                             "math, lab, spatial (3D), data, or paper "
                             "(light notebook look). Controls the semantic "
                             "color palette, background, and grading")
    parser.add_argument("--max-segments", type=int, default=5, metavar="N",
                        help="lecture length cap in segments (default: 5)")
    parser.add_argument("--no-intro", action="store_true",
                        help="skip the intro title card")
    parser.add_argument("--captions", action="store_true",
                        help="burn the narration as subtitles")
    parser.add_argument("-i", "--interactive", action="store_true",
                        help="after building, keep asking follow-up questions "
                             "and append new narrated segments to the video")

    tts_group = parser.add_argument_group("voice-over (TTS)")
    tts_group.add_argument("--tts", choices=["edge", "gtts", "silence"],
                           default="edge", help="TTS engine (default: edge)")
    tts_group.add_argument("--voice", default="en-US-AriaNeural", metavar="NAME",
                           help="Microsoft neural voice for edge-tts "
                                "(default: en-US-AriaNeural)")
    tts_group.add_argument("--rate", default="+0%", metavar="RATE",
                           help="edge-tts speaking rate, e.g. +10%% (default: +0%%)")
    tts_group.add_argument("--lang", default="en", metavar="LANG",
                           help="gTTS language code (default: en)")

    llm_group = parser.add_argument_group("LLM")
    llm_group.add_argument("--provider", choices=["openai", "anthropic"],
                           help="LLM provider (default: $PHIVERSITY_PROVIDER "
                                "or openai; any OpenAI-compatible endpoint "
                                "counts as openai)")
    llm_group.add_argument("--model", metavar="NAME",
                           help="model name (default: $LLM_MODEL)")
    llm_group.add_argument("--api-key", metavar="KEY",
                           help="API key (default: $LLM_API_KEY)")
    llm_group.add_argument("--base-url", metavar="URL",
                           help="chat endpoint base URL (default: $LLM_BASE_URL)")
    llm_group.add_argument("--llm-timeout", type=float, default=180.0,
                           metavar="SEC", help="per-request timeout (default: 180)")

    render_group = parser.add_argument_group("rendering")
    render_group.add_argument("-q", "--quality", choices=["l", "m", "h"],
                              default="m",
                              help="manim render quality: l=480p15, m=720p30, "
                                   "h=1080p60 (default: m)")
    render_group.add_argument("--render-timeout", type=float, default=420.0,
                              metavar="SEC",
                              help="per-scene render timeout (default: 420)")
    render_group.add_argument("--max-gap", type=float, default=1.2,
                               metavar="SEC",
                               help="longest allowed freeze when the voice "
                                    "outruns the animation; beyond this the "
                                    "scene is re-rendered with a paced ending "
                                    "(default: 1.2)")
    render_group.add_argument("--heal-attempts", type=int, default=2, metavar="N",
                              help="LLM repair retries per failed scene "
                                   "(default: 2)")

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    load_env_file()

    if args.file:
        try:
            args.question = open(args.file, encoding="utf-8").read().strip()
        except OSError as exc:
            print(f"error: cannot read {args.file}: {exc}", file=sys.stderr)
            return 2
    if not args.question and not args.demo:
        print("error: provide a question (or --demo [TOPIC] for a bundled "
              "lecture, or --file PATH)", file=sys.stderr)
        return 2

    llm = LLMConfig.from_env()
    if args.provider:
        llm.provider = args.provider
    if args.model:
        llm.model = args.model
    if args.api_key:
        llm.api_key = args.api_key
    if args.base_url:
        llm.base_url = args.base_url.rstrip("/")
    llm.timeout = args.llm_timeout

    if args.no_intro_clip:
        intro_clip = ""
    elif args.intro_clip:
        intro_clip = args.intro_clip
    else:
        intro_clip = "Intro.mp4" if Path("Intro.mp4").is_file() else None

    cfg = PipelineConfig(
        question=args.question,
        out_dir=args.out,
        max_segments=args.max_segments,
        intro=not args.no_intro,
        captions=args.captions,
        interactive=args.interactive,
        demo=args.demo,
        intro_clip=intro_clip,
        transitions=args.transitions,
        theme=args.theme,
        llm=llm,
        tts=TTSConfig(engine=args.tts, voice=args.voice,
                      language=args.lang, rate=args.rate),
        render=RenderConfig(quality=args.quality,
                             timeout=args.render_timeout,
                             heal_attempts=args.heal_attempts,
                             max_gap=args.max_gap),
    )

    try:
        run_pipeline(cfg)
    except KeyboardInterrupt:
        print("\naborted", file=sys.stderr)
        return 130
    except Exception as exc:  # noqa: BLE001 - CLI boundary
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
