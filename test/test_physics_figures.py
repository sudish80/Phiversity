"""Tests for physics figure builder and orchestrator integration."""

import unittest

from scripts.orchestrator.physics_figure_builder import (
    is_physics_problem,
    extract_physics_objects,
    build_physics_figure_scene,
)
from scripts.orchestrator.prompt_orchestrator import (
    _normalize_solver_response,
    generate_local_fallback_plan,
    _inject_subject_figure_scene,
)


class PhysicsFigureBuilderTests(unittest.TestCase):
    """Test physics problem detection and figure scene generation."""

    def test_physics_problem_detection(self):
        """Verify physics problem detection works for various problem types."""
        physics_problems = [
            "A car slides on ice with friction coefficient 0.2. Find acceleration.",
            "A 5 kg block is pushed on an incline at 30 degrees. What is the force?",
            "Two objects collide elastically. Calculate final velocities.",
            "A spring oscillates with mass 2 kg. Find the period.",
            "A projectile is launched at 45 degrees. How far does it travel?",
            "What is the velocity of a circular motion object at radius 5m?",
        ]
        for problem in physics_problems:
            self.assertTrue(is_physics_problem(problem), f"Failed to detect: {problem}")

    def test_non_physics_problem_detection(self):
        """Verify math problems are not classified as physics."""
        non_physics = [
            "Integrate x^3 dx",
            "What is the derivative of e^x?",
            "Solve for x: 2x + 3 = 7",
            "What is the GDP of France in 2023?",
        ]
        for problem in non_physics:
            self.assertFalse(is_physics_problem(problem), f"False positive: {problem}")

    def test_extract_physics_objects_incline(self):
        """Test object extraction from incline problem."""
        question = "A 10 kg block slides on a 30 degree incline with friction."
        context = extract_physics_objects(question)
        
        self.assertEqual(context["scenario"], "incline")
        self.assertGreater(len(context["objects"]), 0)
        self.assertGreater(len(context["forces"]), 0)
        self.assertEqual(context["dimensions"].get("mass"), 10.0)
        self.assertEqual(context["dimensions"].get("angle"), 30)

    def test_extract_physics_objects_collision(self):
        """Test object extraction from collision problem."""
        question = "Two 5kg objects collide elastically. Initial velocities are 3 m/s."
        context = extract_physics_objects(question)
        
        self.assertEqual(context["scenario"], "collision")
        self.assertGreater(len(context["objects"]), 0)
        self.assertIn("collision", [context["scenario"]])

    def test_extract_physics_objects_spring(self):
        """Test object extraction from spring problem."""
        question = "A mass of 2 kg oscillates on a spring with coefficient k=50."
        context = extract_physics_objects(question)
        
        self.assertEqual(context["scenario"], "spring")
        self.assertEqual(context["dimensions"].get("mass"), 2.0)

    def test_build_free_body_diagram(self):
        """Test free-body diagram scene generation."""
        question = "A 5 kg object experiences friction and gravity."
        scene = build_physics_figure_scene(question)
        
        self.assertIsNotNone(scene)
        self.assertEqual(scene["id"], "physics_figure_free_body")
        self.assertIn("free-body", scene["description"].lower())
        self.assertIn("voiceover", scene)
        self.assertIn("elements", scene)
        self.assertGreater(len(scene["elements"]), 0)

    def test_build_incline_scene(self):
        """Test incline plane diagram scene generation."""
        question = "A 10 kg block slides down a 30 degree incline."
        scene = build_physics_figure_scene(question)
        
        self.assertIsNotNone(scene)
        self.assertEqual(scene["id"], "physics_figure_incline")
        self.assertIn("Incline", scene["description"])
        self.assertIn("30", scene["voiceover"])

    def test_build_collision_scene(self):
        """Test collision scenario diagram."""
        question = "Two masses collide. Calculate final velocities."
        scene = build_physics_figure_scene(question)
        
        self.assertIsNotNone(scene)
        self.assertEqual(scene["id"], "physics_figure_collision")
        self.assertIn("Collision", scene["description"])

    def test_build_spring_scene(self):
        """Test spring-mass system diagram."""
        question = "A 2 kg mass oscillates on a spring."
        scene = build_physics_figure_scene(question)
        
        self.assertIsNotNone(scene)
        self.assertEqual(scene["id"], "physics_figure_spring")
        self.assertIn("Spring", scene["description"])

    def test_build_circular_motion_scene(self):
        """Test circular motion diagram."""
        question = "An object moves in circular motion at radius 5m."
        scene = build_physics_figure_scene(question)
        
        self.assertIsNotNone(scene)
        self.assertEqual(scene["id"], "physics_figure_circular")
        self.assertIn("Circular", scene["description"])

    def test_build_projectile_scene(self):
        """Test projectile motion diagram."""
        question = "A ball is thrown at 45 degrees from 10m height."
        scene = build_physics_figure_scene(question)
        
        self.assertIsNotNone(scene)
        self.assertEqual(scene["id"], "physics_figure_projectile")
        self.assertIn("Projectile", scene["description"])

    def test_scene_has_voiceover_with_problem_context(self):
        """Verify scene voiceover includes educational context."""
        question = "A 5 kg object on a frictionless surface experiences 10 N force."
        scene = build_physics_figure_scene(question)
        
        voiceover = scene.get("voiceover", "").lower()
        self.assertIn("force", voiceover)
        self.assertGreater(len(scene.get("voiceover", "")), 50)

    def test_scene_elements_have_required_fields(self):
        """Verify scene elements contain required fields."""
        question = "A car accelerates on a horizontal road."
        scene = build_physics_figure_scene(question)
        
        elements = scene.get("elements", [])
        self.assertGreater(len(elements), 0)
        
        for element in elements:
            self.assertIn("type", element, "Element missing 'type' field")

    def test_orchestrator_normalizes_with_physics_figure(self):
        """Test that orchestrator injects physics figure during normalization."""
        raw = {
            "answer": "The acceleration is 2 m/s²",
            "steps": [
                {"title": "Apply Newton's law", "description": "F = ma"},
                {"title": "Solve", "description": "a = F/m = 10/5 = 2 m/s²"},
            ]
        }
        
        physics_question = "A 5 kg object experiences 10 N force. Find acceleration."
        normalized = _normalize_solver_response(raw, user_question=physics_question)
        
        # Check physics figure was injected
        scenes = normalized.get("animation_plan", {}).get("scenes", [])
        physics_scenes = [s for s in scenes if "physics_figure" in s.get("id", "")]
        self.assertGreater(len(physics_scenes), 0, "Physics figure scene not injected")

    def test_fallback_plan_includes_physics_figure(self):
        """Test that fallback plan includes physics figure for physics problems."""
        physics_question = "A 2 kg block slides on a 30 degree incline."
        fallback = generate_local_fallback_plan(physics_question, mode="question_solving")
        
        # Check scenes include physics figure
        scenes = fallback.animation_plan.scenes
        physics_scene_exists = any(
            "physics_figure" in scene.id for scene in scenes
        )
        self.assertTrue(physics_scene_exists, "Fallback should include physics figure")

    def test_inject_physics_figure_idempotent(self):
        """Verify physics figure injection doesn't duplicate scenes."""
        raw = {
            "solution": {"steps": [], "final_answer": ""},
            "animation_plan": {
                "scenes": [
                    {
                        "id": "physics_figure_free_body",
                        "description": "Free-body diagram",
                        "elements": []
                    }
                ]
            }
        }
        
        question = "A force acts on an object."
        result = _inject_subject_figure_scene(raw, question)

        # Count physics figure scenes
        physics_scenes = [
            s for s in result.get("animation_plan", {}).get("scenes", [])
            if "physics_figure" in s.get("id", "")
        ]
        self.assertEqual(len(physics_scenes), 1, "Should not duplicate physics figure")

    def test_physics_figure_non_physics_problem_skipped(self):
        """Verify physics figure is not injected for non-physics problems."""
        raw = {
            "solution": {"steps": [], "final_answer": ""},
            "animation_plan": {"scenes": []}
        }
        
        math_question = "Integrate x^3 dx"
        result = _inject_subject_figure_scene(raw, math_question)

        scenes = result.get("animation_plan", {}).get("scenes", [])
        physics_scenes = [s for s in scenes if "physics_figure" in s.get("id", "")]
        self.assertEqual(len(physics_scenes), 0, "Physics figure should not be injected for math problems")


if __name__ == "__main__":
    unittest.main()
