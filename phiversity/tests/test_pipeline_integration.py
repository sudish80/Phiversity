"""Integration tests: real manim renders + full pipeline (offline demo).

These exercise the actual subprocess machinery: manim render, ffmpeg
compose, healing with a fake LLM. No network or API key required.
"""

import json
from pathlib import Path

import pytest

from phiversity.config import LLMConfig, PipelineConfig, RenderConfig, TTSConfig
from phiversity.pipeline import run_pipeline
from phiversity.render import RenderError, render_scene, render_with_healing
from phiversity.tts import ffprobe_duration

BROKEN = '''from manim import *


class Segment0(Scene):
    def construct(self):
        t = TotallyNotAManimObject()
        self.play(Write(t))
        self.wait(1)
'''

WORKING = '''from manim import *


class Segment0(Scene):
    def construct(self):
        t = Text("healed!", font_size=44)
        self.play(Write(t), run_time=0.5)
        self.wait(0.3)
'''


class FakeHealClient:
    """Duck-typed stand-in for LLMClient that returns working code."""

    def __init__(self, fixed_code: str):
        self.fixed_code = fixed_code
        self.calls = 0

    def heal_code(self, code: str, error: str) -> str:
        self.calls += 1
        return self.fixed_code


@pytest.fixture(scope="module")
def tiny_render_cfg():
    return RenderConfig(quality="l", timeout=180.0, heal_attempts=2)


class TestHealing:
    def test_broken_code_fails_without_healing(self, tmp_path, tiny_render_cfg):
        with pytest.raises(RenderError):
            render_with_healing(BROKEN, "Segment0", tmp_path / "w1",
                                tiny_render_cfg, client=None, log=lambda *_: None)

    def test_llm_heals_broken_code(self, tmp_path, tiny_render_cfg):
        client = FakeHealClient(WORKING)
        out = render_with_healing(BROKEN, "Segment0", tmp_path / "w2",
                                  tiny_render_cfg, client=client,
                                  log=lambda *_: None)
        assert client.calls == 1
        assert out.exists() and out.suffix == ".mp4"

    def test_good_code_renders_first_try(self, tmp_path, tiny_render_cfg):
        client = FakeHealClient(WORKING)
        out = render_with_healing(WORKING, "Segment0", tmp_path / "w3",
                                  tiny_render_cfg, client=client,
                                  log=lambda *_: None)
        assert client.calls == 0
        assert ffprobe_duration(out) == pytest.approx(0.8, abs=0.2)


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    cfg = PipelineConfig(
        question="", demo=True,
        out_dir=tmp_path_factory.mktemp("lectures"),
        tts=TTSConfig(engine="silence"),
        render=RenderConfig(quality="l", timeout=240.0),
    )
    return run_pipeline(cfg, log=lambda *_: None)


class TestFullDemoPipeline:

    def test_final_video_exists(self, built):
        assert built.final_video.exists()
        assert built.final_video.name == "lecture.mp4"

    def test_final_video_streams(self, built):
        import subprocess
        out = subprocess.run(
            ["ffprobe", "-v", "error", "-show_entries",
             "stream=codec_type,codec_name", "-of", "json",
             str(built.final_video)],
            capture_output=True, text=True, check=True).stdout
        streams = {s["codec_type"]: s["codec_name"]
                   for s in json.loads(out)["streams"]}
        assert streams["video"] == "h264"
        assert streams["audio"] == "aac"

    def test_final_video_duration(self, built):
        total = sum(s.audio_duration for s in built.segments)
        assert ffprobe_duration(built.final_video) == pytest.approx(
            total, abs=max(2.0, total * 0.2))

    def test_manifest(self, built):
        manifest = json.loads(
            (built.final_video.parent / "manifest.json").read_text())
        assert manifest["title"]
        assert manifest["question"] and "hypotenuse" in manifest["question"]
        assert len(manifest["segments"]) == len(built.segments)
        assert all(s["narration"] for s in manifest["segments"])

    def test_question_scene_was_built(self, built):
        scenes = [s.scene_name for s in built.segments]
        assert scenes[0] == "IntroTitle"        # no intro clip configured
        assert scenes[1] == "QuestionScene"
        assert built.segments[1].kind == "question"
        assert built.segments[1].audio_duration > 0
