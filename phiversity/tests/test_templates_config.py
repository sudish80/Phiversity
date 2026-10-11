import pytest

from phiversity.config import LLMConfig, load_env_file, detect_latex
from phiversity.pipeline import build_playlist, slugify
from phiversity.render import validate_code
from phiversity.templates import (BUNDLED_LECTURES, bundled_topics,
                                    demo_code, demo_plan,
                                    demo_question_code, intro_segment,
                                    normalize_topic)
from pathlib import Path


class TestBundledLectures:
    def test_pythagoras_plan_shape(self):
        plan = demo_plan("pythagoras")
        assert plan["title"] == "The Pythagorean Theorem"
        assert len(plan["segments"]) == 4
        assert all(s["narration"] for s in plan["segments"])
        assert plan["question"]["display"].startswith("A right triangle")

    def test_fma_plan_shape(self):
        plan = demo_plan("f=ma")
        assert plan["title"].startswith("Newton's Second Law")
        assert len(plan["segments"]) == 4
        assert plan["question"]["display"].startswith("A net force")

    def test_car_friction_plan_shape(self):
        plan = demo_plan("car")
        assert "friction" in plan["title"].lower()
        assert len(plan["segments"]) == 3
        question = plan["question"]
        assert "car is moving along a road" in question["display"]
        assert "five newtons" in question["speech"]
        assert "$f_k" in question["display"]

    @pytest.mark.parametrize("topic", bundled_topics())
    def test_bundled_code_passes_validation(self, topic):
        lecture = BUNDLED_LECTURES[topic]
        validate_code(lecture["question_code"], "QuestionScene")
        for index in range(len(lecture["segments"])):
            validate_code(demo_code(topic, index), f"Segment{index}")

    @pytest.mark.parametrize("topic", bundled_topics())
    def test_zoom_scenes_use_moving_camera(self, topic):
        for index in range(len(BUNDLED_LECTURES[topic]["segments"])):
            code = demo_code(topic, index)
            uses_zoom = "self.camera.frame" in code
            if uses_zoom:
                assert "MovingCameraScene" in code

    def test_intro_segment_code(self):
        seg = intro_segment('The "quoted" title', 5.0)
        assert seg["scene_name"] == "IntroTitle"
        validate_code(seg["code"], "IntroTitle")
        assert '\'The "quoted" title\'' in seg["code"]

    def test_page_flip_code_valid(self):
        from phiversity.templates import PAGE_FLIP_CODE
        validate_code(PAGE_FLIP_CODE, "PageFlip")


class TestPlaylist:
    def test_no_extras(self):
        parts = build_playlist([Path("a"), Path("b")])
        assert parts == [Path("a"), Path("b")]

    def test_flip_between_all_clips(self):
        parts = build_playlist([Path("a"), Path("b"), Path("c")],
                               intro_clip=Path("in"),
                               flip_clip=Path("flip"))
        assert parts == [Path("in"), Path("flip"), Path("a"),
                         Path("flip"), Path("b"), Path("flip"), Path("c")]

    def test_intro_without_flip(self):
        parts = build_playlist([Path("a")], intro_clip=Path("in"))
        assert parts == [Path("in"), Path("a")]


class TestTopicRouting:
    def test_defaults_no_page_flip(self):
        """The flip animation is opt-in; videos cut straight by default."""
        from phiversity.config import PipelineConfig
        assert PipelineConfig().transitions == "none"

    @pytest.mark.parametrize("alias,expected", [
        ("fma", "fma"), ("F=ma", "fma"), ("f-ma", "fma"),
        ("newton", "fma"), ("Newton's second law", "fma"),
        ("pythagoras", "pythagoras"), ("Pythagorean Theorem!", "pythagoras"),
        ("car", "car-friction"), ("CAR FRICTION", "car-friction"),
        ("tire", "car-friction"), ("friction", "car-friction"),
        ("", "pythagoras"), (None, "pythagoras"), (True, "pythagoras"),
    ])
    def test_aliases(self, alias, expected):
        assert normalize_topic(alias) == expected

    def test_unknown_topic_raises(self):
        with pytest.raises(ValueError, match="no bundled lecture"):
            normalize_topic("quantum-entanglement")

    def test_all_lectures_have_title_and_segments(self):
        for topic, lecture in BUNDLED_LECTURES.items():
            assert lecture["title"]
            assert len(lecture["segments"]) >= 2


class TestSlugify:
    def test_basic(self):
        assert slugify("Explain the Pythagorean Theorem!") == \
            "explain-the-pythagorean-theorem"

    def test_fallback(self):
        assert slugify("!!!") == "lecture"

    def test_length_cap(self):
        assert len(slugify("x " * 100)) <= 40


class TestEnvConfig:
    def test_env_file_loaded(self, tmp_path, monkeypatch):
        env_file = tmp_path / ".env"
        env_file.write_text("LLM_MODEL=my-model\n# comment\nLLM_BASE_URL=http://x/v1\n")
        monkeypatch.delenv("LLM_MODEL", raising=False)
        monkeypatch.delenv("LLM_BASE_URL", raising=False)
        monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
        loaded = load_env_file(env_file)
        assert loaded["LLM_MODEL"] == "my-model"
        cfg = LLMConfig.from_env()
        assert cfg.model == "my-model"

    def test_nvidia_default_base_url(self, monkeypatch):
        monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-x")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        monkeypatch.delenv("LLM_API_KEY", raising=False)
        monkeypatch.delenv("LLM_BASE_URL", raising=False)
        monkeypatch.delenv("OPENAI_BASE_URL", raising=False)
        monkeypatch.delenv("LLM_MODEL", raising=False)
        monkeypatch.delenv("OPENAI_MODEL", raising=False)
        cfg = LLMConfig.from_env()
        assert "nvidia" in cfg.base_url
        assert cfg.model.startswith("meta/llama")


class TestLatexDetection:
    def test_bool(self):
        assert isinstance(detect_latex(), bool)
