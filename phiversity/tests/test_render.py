import pytest

from phiversity.render import (CodeValidationError, QUALITY_FPS,
                                 QUALITY_FLAG, _longest_run,
                                 adjust_final_wait, detect_edge_clipping,
                                 estimate_scene_duration, lint_layout,
                                 validate_code)

GOOD = '''from manim import *


class Segment0(Scene):
    def construct(self):
        t = Text("hello")
        self.play(Write(t))
        self.wait(1)
'''


class TestValidateCode:
    def test_accepts_good_code(self):
        assert "class Segment0(Scene):" in validate_code(GOOD, "Segment0")

    def test_rejects_empty(self):
        with pytest.raises(CodeValidationError):
            validate_code("", "Segment0")

    def test_requires_manim_import(self):
        with pytest.raises(CodeValidationError):
            validate_code("class Segment0(Scene):\n    pass", "Segment0")

    def test_requires_scene_class(self):
        with pytest.raises(CodeValidationError):
            validate_code(GOOD, "Segment9")

    def test_accepts_moving_camera_scene(self):
        code = GOOD.replace("class Segment0(Scene):",
                            "class Segment0(MovingCameraScene):")
        assert "MovingCameraScene" in validate_code(code, "Segment0")

    def test_accepts_vector_and_3d_scenes(self):
        for base in ("VectorScene", "ThreeDScene"):
            code = GOOD.replace("class Segment0(Scene):",
                                f"class Segment0({base}):")
            validate_code(code, "Segment0")

    @pytest.mark.parametrize("bad,label", [
        ("import os\nfrom manim import *", "os import"),
        ("from manim import *\nimport subprocess", "subprocess"),
        ("from manim import *\nx = open('/etc/passwd')", "open"),
        ("from manim import *\neval('1+1')", "eval"),
        ("from manim import *\nimport requests", "requests"),
        ("from manim import *\nimport random\n", "random"),
        ("from manim import *\n__import__('os')", "__import__"),
    ])
    def test_rejects_dangerous(self, bad, label):
        with pytest.raises(CodeValidationError, match=label):
            validate_code(bad, "Segment0")

    def test_strips_non_manim_imports(self):
        code = GOOD.replace("from manim import *",
                            "from manim import *\nimport json")
        cleaned = validate_code(code, "Segment0")
        assert "import json" not in cleaned
        assert "from manim import *" in cleaned

    def test_strips_markdown_fences(self):
        fenced = "```python\n" + GOOD + "\n```"
        cleaned = validate_code(fenced, "Segment0")
        assert cleaned.startswith("from manim import")
        assert "```" not in cleaned


class TestPacing:
    SAMPLE = """from manim import *


class Segment0(Scene):
    def construct(self):
        self.play(Write(Text("hi")))              # implicit run_time 1.0
        self.play(Write(Text("there")), run_time=1.5)
        self.wait(2.0)
        self.play(Create(Line(ORIGIN, RIGHT)), run_time=1.0)
        self.wait(1.0)
"""

    def test_estimate_sums_waits_and_run_times(self):
        # waits 2.0 + 1.0, run_times 1.5 + 1.0, plus 1.0 implicit play
        assert estimate_scene_duration(self.SAMPLE) == pytest.approx(6.5)

    def test_estimate_empty_code(self):
        assert estimate_scene_duration("from manim import *") == 0.0

    def test_adjust_extends_only_the_last_wait(self):
        paced = adjust_final_wait(self.SAMPLE, 3.0)
        assert "self.wait(4)" in paced                 # 1.0 + 3.0
        assert "self.wait(2.0)" in paced               # earlier wait untouched
        assert paced.count("self.wait(2.0)") == 1

    def test_adjust_ignores_nonpositive_delta(self):
        assert adjust_final_wait(self.SAMPLE, -1.0) == self.SAMPLE
        assert adjust_final_wait(self.SAMPLE, 0.0) == self.SAMPLE

    def test_adjust_without_waits_is_noop(self):
        code = "from manim import *\n\nclass S(Scene):\n    pass"
        assert adjust_final_wait(code, 2.0) == code


class TestLayoutLint:
    def test_flags_box_created_before_repositioning(self):
        buggy = '''from manim import *


class Segment0(Scene):
    def construct(self):
        eq = MathTex("x")
        box = SurroundingRectangle(eq, buff=0.3)
        self.play(Create(box))
        self.play(eq.animate.move_to(RIGHT * 2))
'''
        warnings = lint_layout(buggy)
        assert any("eq" in w and "wrapped before" in w for w in warnings)

    def test_clean_code_has_no_warnings(self):
        clean = '''from manim import *


class Segment0(Scene):
    def construct(self):
        eq = MathTex("x")
        eq.move_to(RIGHT * 2)
        box = SurroundingRectangle(eq, buff=0.3)
        self.play(Create(box))
'''
        assert lint_layout(clean) == []

    def test_lint_ignores_unrelated_moves(self):
        code = '''from manim import *


class Segment0(Scene):
    def construct(self):
        other = MathTex("y")
        box = SurroundingRectangle(other, buff=0.3)
        self.play(unrelated.animate.move_to(ORIGIN))
'''
        assert lint_layout(code) == []


class TestLongestRun:
    def test_runs(self):
        assert _longest_run([1, 1, 0, 1, 1, 1]) == 3
        assert _longest_run([0, 0, 0]) == 0
        assert _longest_run([1] * 25) == 25


class TestEdgeClipping:
    def make_frame_video(self, path, draw_text_at_edge, seconds=2.0):
        """Small clip with optional tall text blocks touching an edge."""
        import subprocess
        if draw_text_at_edge == "both":
            vf = ("drawtext=text='XXXXXXXXXXXXXXXX':fontsize=54:"
                  "fontcolor=white:x=0:y=60,"
                  "drawtext=text='XXXXXXXXXXXXXXXX':fontsize=54:"
                  "fontcolor=white:x=w-tw:y=60")
        elif draw_text_at_edge == "none":
            vf = ("drawtext=text='hello':fontsize=48:fontcolor=white:"
                  "x=(w-tw)/2:y=(h-th)/2")
        else:  # thin full-bleed line only (a road/floor)
            vf = "drawbox=x=0:y=ih-8:w=iw:h=4:color=white@1:t=fill"
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-f", "lavfi",
             "-i", f"color=c=0x101319:s=320x180:d={seconds}",
             "-vf", vf, "-pix_fmt", "yuv420p", "-c:v", "libx264",
             str(path)], check=True)
        return path

    def test_detects_text_at_both_edges(self, tmp_path):
        clip = self.make_frame_video(tmp_path / "clip.mp4", "both")
        assert detect_edge_clipping(clip, samples=4) == ["left", "right"]

    def test_clean_centered_text_passes(self, tmp_path):
        clip = self.make_frame_video(tmp_path / "clean.mp4", "none")
        assert detect_edge_clipping(clip, samples=4) == []

    def test_thin_full_bleed_line_is_ignored(self, tmp_path):
        clip = self.make_frame_video(tmp_path / "line.mp4", "line")
        assert detect_edge_clipping(clip, samples=4) == []


class TestQualityMaps:
    def test_flags(self):
        assert QUALITY_FLAG["l"] == "-ql"
        assert QUALITY_FLAG["m"] == "-qm"
        assert QUALITY_FLAG["h"] == "-qh"

    def test_fps(self):
        assert QUALITY_FPS["m"] == 30

    def test_sizes(self):
        from phiversity.render import QUALITY_SIZE
        assert QUALITY_SIZE["m"] == (1280, 720)
