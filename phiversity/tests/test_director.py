import pytest

from phiversity.director import (ALL_TRANSITIONS, CUT_TRANSITIONS,
                                  DEFAULT_CARD_VISUAL, EFFECT_PLAYBOOK,
                                  SELECTION_RULES, VISUAL_PLAN_SCHEMA,
                                  XFADE_MAP, describe_plan,
                                  is_cut, normalize_transition,
                                  normalize_visual_plan, suggest_transition,
                                  transition_howto, verify_effects)

ZOOM_CODE = """from manim import *


class Segment0(MovingCameraScene):
    def construct(self):
        tracker = ValueTracker(3.0)
        dot = graph_point(axes, f, tracker, color=T.graph_point)
        sec = secant_line(axes, f, x0, tracker, color=T.graph_secant)
        zoom_to(self, disc)
        pan_to(self, graph)
        camera_reset(self)
        emphasize(self, term)
"""


class TestNormalizePlan:
    def test_defaults(self):
        plan = normalize_visual_plan(None)
        assert plan["camera_movement"] == "static"
        assert plan["three_d"] is False
        assert plan["transition"] == "none"
        assert plan["dynamic"] == []

    def test_fields_and_clamping(self):
        plan = normalize_visual_plan({
            "objective": "show the tangent",
            "transition": "slide-up",
            "camera_movement": "pan",
            "camera_movement_bad": "teleport",
            "zoom_target": "discriminant",
            "highlight": ["b", "c"],
            "dynamic": ["secant follows points"],
            "three_d": True,
            "color_roles": {"curve": "graph_function"},
        })
        assert plan["objective"] == "show the tangent"
        assert plan["transition"] == "slide-up"
        assert plan["camera_movement"] == "pan"
        assert plan["zoom_target"] == "discriminant"
        assert plan["highlight"] == ["b", "c"]
        assert plan["dynamic"] == ["secant follows points"]
        assert plan["three_d"] is True
        assert plan["color_roles"] == {"curve": "graph_function"}

    def test_unknown_enums_fall_back(self):
        plan = normalize_visual_plan({"camera_movement": "spin",
                                      "diagram": "hologram",
                                      "transition": "star-wipe"})
        assert plan["camera_movement"] == "static"
        assert plan["diagram"] == "none"
        assert plan["transition"] == "carry-over"

    def test_describe_plan_mentions_beats(self):
        plan = normalize_visual_plan(
            {"objective": "x", "animation_beats": ["draw", "zoom"],
             "highlight": ["b"], "camera_movement": "pan"})
        text = describe_plan(plan)
        assert "objective: x" in text
        assert "- draw" in text and "- zoom" in text
        assert "camera movement: pan" in text
        assert "highlight in narration order: b" in text


class TestTransitions:
    @pytest.mark.parametrize("value,expected", [
        ("carry", "carry-over"), ("continuous", "carry-over"),
        ("Slide Up", "slide-up"), ("reveal", "answer-reveal"),
        ("topic", "new-topic"), ("fade", "fade"),
        (None, "none"), ("", "none"), ("nonsense", "carry-over"),
    ])
    def test_normalize(self, value, expected):
        assert normalize_transition(value) == expected

    def test_cut_vs_xfade_types(self):
        assert is_cut("carry-over") and is_cut("slide-up")
        assert is_cut("answer-reveal") and is_cut(None)
        assert not is_cut("fade") and not is_cut("wipe")
        assert set(XFADE_MAP) | CUT_TRANSITIONS >= set(ALL_TRANSITIONS)

    def test_suggest_question_to_solution(self):
        card = normalize_visual_plan(DEFAULT_CARD_VISUAL, kind="question")
        first = normalize_visual_plan({"objective": "begin solving"})
        assert suggest_transition(card, first) == "slide-up"

    def test_suggest_2d_to_3d(self):
        flat = normalize_visual_plan({"objective": "flat drawing"})
        solid = normalize_visual_plan({"objective": "3D model",
                                       "three_d": True})
        assert suggest_transition(flat, solid) == "carry-over"

    def test_howto_instructions(self):
        assert "TOP" in transition_howto("slide-up")
        assert "SurroundingRectangle" in transition_howto("answer-reveal")
        assert "crossfades" in transition_howto("fade")


class TestVerifyEffects:
    def test_missing_effects_are_flagged(self):
        plan = normalize_visual_plan(
            {"camera_movement": "pan", "zoom_target": "disc",
             "highlight": ["b"], "dynamic": ["secant"],
             "color_roles": {"curve": "graph_function"},
             "three_d": True})
        warnings = verify_effects("from manim import *", plan)
        # camera movement, zoom, highlight, dynamic, 3D model, colors
        assert len(warnings) == 6

    def test_kit_helpers_satisfy_checks(self):
        plan = normalize_visual_plan(
            {"camera_movement": "pan", "zoom_target": "disc",
             "highlight": ["term"], "dynamic": ["secant"],
             "color_roles": {"curve": "graph_function"}})
        assert verify_effects(ZOOM_CODE, plan) == []

    def test_3d_needs_real_3d_objects(self):
        plan = normalize_visual_plan({"three_d": True})
        assert verify_effects("from manim import *\nclass S(ThreeDScene):\n"
                              "    pass", plan)
        ok = ("from manim import *\n"
              "class S(ThreeDScene):\n"
              "    m = Sphere()")
        assert verify_effects(ok, plan) == []

    def test_static_plan_needs_nothing(self):
        plan = normalize_visual_plan({"objective": "plain text scene"})
        assert verify_effects("from manim import *", plan) == []


class TestPlaybookContent:
    def test_playbook_covers_required_capabilities(self):
        for snippet in ["TRANSITIONS", "CAMERA MOVEMENT", "ZOOMING",
                       "VISUAL HIGHLIGHTING", "THREE-DIMENSIONAL",
                       "DIAGRAM GENERATION", "CONTINUOUS MATHEMATICAL",
                       "DYNAMIC GEOMETRY", "MULTI-SCALE", "SEMANTIC COLOR",
                       "dim_except"]:
            assert snippet in EFFECT_PLAYBOOK
        for snippet in ["Never add an effect", "Prefer static"]:
            assert snippet in SELECTION_RULES
        for snippet in ["transition", "preset", "camera_movement",
                        "zoom_target", "highlight", "dynamic",
                        "three_d", "color_roles", "animation_beats",
                        "outcome"]:
            assert snippet in VISUAL_PLAN_SCHEMA
