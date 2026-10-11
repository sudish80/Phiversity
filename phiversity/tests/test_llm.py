import json

import pytest

from phiversity.llm import (LLMError, extract_code, extract_json,
                              strip_code_fences, _normalize_codes,
                              _normalize_plan)


class TestExtractJson:
    def test_plain_json(self):
        assert extract_json('{"a": 1}') == {"a": 1}

    def test_fenced_json(self):
        text = '```json\n{"a": 1}\n```'
        assert extract_json(text) == {"a": 1}

    def test_prose_wrapped_json(self):
        text = 'Sure! Here you go:\n{"title": "X", "segments": []}\nDone.'
        assert extract_json(text)["title"] == "X"

    def test_invalid_raises(self):
        with pytest.raises(ValueError):
            extract_json("no json here at all")


class TestExtractCode:
    def test_strips_fences(self):
        assert extract_code("```python\nprint(1)\n```") == "print(1)"

    def test_raw_passthrough(self):
        assert extract_code("print(1)") == "print(1)"


class TestStripFences:
    def test_json_fence_tag(self):
        assert strip_code_fences("```json\n{}\n```") == "{}"


class TestNormalizePlan:
    def test_happy_path(self):
        plan = _normalize_plan(
            {"title": "T", "segments": [{"narration": "hi"},
                                        {"narration": "there"}]}, 5)
        assert plan["title"] == "T"
        assert plan["question"] is None
        assert [s["index"] for s in plan["segments"]] == [0, 1]

    def test_question_object(self):
        plan = _normalize_plan(
            {"title": "T",
             "question": {"display": "What is $F = ma$?", "speech": "what is F equals m a"},
             "segments": [{"narration": "hi"}]}, 5)
        assert plan["question"] == {"display": "What is $F = ma$?",
                                    "speech": "what is F equals m a"}

    def test_question_string_falls_back_to_same_text(self):
        plan = _normalize_plan({"question": "plain question?",
                                "segments": [{"narration": "x"}]}, 5)
        assert plan["question"]["display"] == "plain question?"

    def test_question_with_empty_display_dropped(self):
        plan = _normalize_plan({"question": {"display": ""},
                                "segments": [{"narration": "x"}]}, 5)
        assert plan["question"] is None

    def test_string_segments(self):
        plan = _normalize_plan({"segments": ["one", "two"]}, 5)
        assert len(plan["segments"]) == 2

    def test_caps_segments(self):
        plan = _normalize_plan(
            {"segments": [{"narration": str(i)} for i in range(9)]}, 3)
        assert len(plan["segments"]) == 3

    def test_start_index(self):
        plan = _normalize_plan({"segments": [{"narration": "x"}]}, 3,
                               start_index=4)
        assert plan["segments"][0]["index"] == 4

    def test_empty_rejected(self):
        with pytest.raises(LLMError):
            _normalize_plan({"segments": []}, 5)
        with pytest.raises(LLMError):
            _normalize_plan({"segments": [{"narration": ""}]}, 5)


class TestNormalizeCodes:
    def test_ordered_by_index(self):
        data = {"segments": [{"index": 1, "code": "B"},
                              {"index": 0, "code": "A"}]}
        assert _normalize_codes(data, 2) == ["A", "B"]

    def test_scene_name_fallback_index(self):
        data = {"segments": [{"scene_name": "Segment1", "code": "B"},
                              {"scene_name": "Segment0", "code": "A"}]}
        assert _normalize_codes(data, 2) == ["A", "B"]

    def test_missing_code_raises(self):
        with pytest.raises(LLMError):
            _normalize_codes({"segments": [{"index": 0, "code": "A"}]}, 2)


class TestPlannerShapes:
    """The planner/coder prompts must stay valid JSON templates."""

    def test_plan_roundtrip_through_llm_parser(self):
        reply = json.dumps(
            {"title": "Gravity",
             "segments": [{"narration": "Why do things fall?"}]})
        parsed = extract_json(reply)
        assert _normalize_plan(parsed, 5)["title"] == "Gravity"


class _FakeJSONClient:
    """Duck-typed LLMClient that records prompts and replies canned JSON."""

    def __init__(self, response):
        self.response = response
        self.users = []
        self.systems = []

    def complete_json(self, system, user, temperature=0.3, max_tokens=8192):
        self.systems.append(system)
        self.users.append(user)
        return self.response


class TestHighLevelCalls:
    def test_code_scenes_keeps_real_segment_indexes(self):
        from phiversity import llm
        fake = _FakeJSONClient({"segments": [{"index": 0, "code": "A"},
                                              {"index": 1, "code": "B"}]})
        codes = llm.LLMClient.code_scenes(fake, "T", [
            {"index": 3, "narration": "n1", "audio_duration": 4.0},
            {"index": 4, "narration": "n2", "audio_duration": 5.0}])
        assert codes == ["A", "B"]
        assert "class name: Segment3" in fake.users[0]
        assert "class name: Segment4" in fake.users[0]

    def test_code_scenes_carries_visual_plans(self):
        from phiversity import llm
        fake = _FakeJSONClient({"segments": [{"index": 0, "code": "A"},
                                              {"index": 1, "code": "B"}]})
        plan = {"objective": "zoom to the discriminant",
                "transition": "slide-up",
                "camera_movement": "pan",
                "zoom_target": "the discriminant",
                "highlight": ["coefficient b"],
                "dynamic": ["secant follows both points"],
                "color_roles": {"curve": "graph_function"},
                "animation_beats": ["write equation", "zoom in"]}
        llm.LLMClient.code_scenes(fake, "T", [
            {"index": 0, "scene_name": "QuestionScene", "kind": "question",
             "question_display": "Solve $x^2 = 4$?",
             "narration": "solve it", "audio_duration": 5.0},
            {"index": 1, "scene_name": "Segment0",
             "narration": "n", "audio_duration": 6.0,
             "visual": plan, "previous_summary": "the question card"}],
            playbook="PLAYBOOK TEXT")
        prompt = fake.users[0]
        assert "objective: zoom to the discriminant" in prompt
        assert "zoom target: the discriminant" in prompt
        assert "- write equation" in prompt
        assert "the previous scene ended with: the question card" in prompt
        assert "PLAYBOOK TEXT" in fake.systems[0]
        assert "TOP" in prompt  # slide-up howto

    def test_planner_prompt_asks_for_visual_plans(self):
        from phiversity import llm
        fake = _FakeJSONClient({"title": "T", "preset": "spatial",
                                "question": {"display": "q", "speech": "q"},
                                "segments": [{"narration": "x",
                                              "visual": {"three_d": True}}]})
        plan = llm.LLMClient.plan_lecture(fake, "shapes?", 4)
        assert plan["preset"] == "spatial"
        assert plan["segments"][0]["visual"]["three_d"] is True
        system = fake.systems[0]
        assert '"visual"' in system
        assert '"preset"' in system
        assert "camera_movement" in system
        assert "three_d" in system

    def test_code_scenes_question_card_instructions(self):
        from phiversity import llm
        fake = _FakeJSONClient({"segments": [{"index": 0, "code": "A"}]})
        llm.LLMClient.code_scenes(fake, "T", [
            {"index": 0, "scene_name": "QuestionScene", "kind": "question",
             "question_display": "What is $f_k = 5\\,\\mathrm{N}$?",
             "narration": "what is the friction?", "audio_duration": 6.0}])
        prompt = fake.users[0]
        assert "class name: QuestionScene" in prompt
        assert "QUESTION CARD" in prompt
        assert "What is $f_k = 5\\,\\mathrm{N}$?" in prompt
        # the system prompt carries the rich-visual + anti-overlap rules
        system = fake.systems[0]
        for snippet in ["Axes", "BarChart", "Arrow", "MovingCameraScene",
                        "overlap", "CENTERED"]:
            assert snippet in system

    def test_planner_prompt_asks_for_question_object(self):
        from phiversity import llm
        fake = _FakeJSONClient({"title": "T",
                                "question": {"display": "q", "speech": "q"},
                                "segments": [{"narration": "x"}]})
        plan = llm.LLMClient.plan_lecture(fake, "why?", 4)
        assert plan["question"] == {"display": "q", "speech": "q"}
        assert '"display"' in fake.systems[0]
        assert '"speech"' in fake.systems[0]

    def test_code_scenes_latex_hints(self):
        from phiversity import llm
        fake = _FakeJSONClient({"segments": [{"index": 0, "code": "A"}]})
        llm.LLMClient.code_scenes(fake, "T",
                                   [{"index": 0, "narration": "n",
                                     "audio_duration": 1.0}], latex=True)
        assert "LaTeX IS available" in fake.systems[0]
        fake2 = _FakeJSONClient({"segments": [{"index": 0, "code": "A"}]})
        llm.LLMClient.code_scenes(fake2, "T",
                                  [{"index": 0, "narration": "n",
                                    "audio_duration": 1.0}], latex=False)
        assert "LaTeX is NOT available" in fake2.systems[0]

    def test_plan_followup_offsets_indexes(self):
        from phiversity import llm
        fake = _FakeJSONClient({"title": "T", "segments":
                                [{"narration": "x"}, {"narration": "y"}]})
        plan = llm.LLMClient.plan_followup(fake, "more?", "T", ["a", "b"],
                                           start_index=3)
        assert [s["index"] for s in plan["segments"]] == [3, 4]
        assert "more?" in fake.users[0]
