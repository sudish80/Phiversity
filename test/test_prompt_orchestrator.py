import unittest
from unittest.mock import patch

from scripts.orchestrator.prompt_orchestrator import (
    _normalize_solver_response,
    generate_local_fallback_plan,
    orchestrate_solution,
)
from scripts.orchestrator.physics_figure_builder import build_subject_figure_scene


class PromptOrchestratorTests(unittest.TestCase):
    def test_normalize_wraps_flat_solver_payload(self):
        raw = {
            "answer": "ln|x+2| + C",
            "steps": [
                {"title": "Rewrite", "description": "Factor the denominator."},
                {"title": "Integrate", "description": "Integrate the simplified form."},
            ],
        }

        normalized = _normalize_solver_response(
            raw,
            user_question="Integrate (x+1)/(x^2+3x+2) dx",
        )

        self.assertIn("solution", normalized)
        self.assertIn("animation_plan", normalized)
        self.assertEqual(normalized["solution"]["final_answer"], "ln|x+2| + C")
        self.assertEqual(normalized["solution"]["subject"], "mathematics")
        self.assertEqual(len(normalized["solution"]["steps"]), 2)
        self.assertGreaterEqual(len(normalized["animation_plan"]["scenes"]), 2)
        self.assertEqual(
            normalized["animation_plan"]["overview"],
            "Integrate (x+1)/(x^2+3x+2) dx",
        )

        graph_scenes = [
            scene for scene in normalized["animation_plan"]["scenes"]
            if any(str((el or {}).get("type", "")).lower() in {"graph", "plot", "axes", "parametricgraph"}
                   for el in scene.get("elements", []) if isinstance(el, dict))
        ]
        self.assertTrue(graph_scenes)

        scene_blob = " ".join(
            str(scene.get("voiceover", "")) + " " + str(scene.get("description", ""))
            for scene in graph_scenes
        ).lower()
        self.assertIn("integrate", scene_blob)

    def test_fallback_plan_preserves_question_context(self):
        question = "Integrate (x+1)/(x^2+3x+2) dx"
        fallback = generate_local_fallback_plan(question, mode="question_solving")

        self.assertEqual(fallback.solution.subject, "mathematics")
        self.assertIn(question, fallback.solution.steps[0].explanation)
        self.assertIn(question, fallback.animation_plan.overview)

        combined_scene_text = " ".join(
            element.content or ""
            for scene in fallback.animation_plan.scenes
            for element in scene.elements
            if hasattr(element, "content")
        )
        self.assertIn(question, combined_scene_text)
        self.assertNotIn("F = m a", combined_scene_text)

        has_graph_scene = any(
            any(getattr(element, "type", "").lower() in {"graph", "plot", "axes", "parametricgraph"}
                for element in scene.elements)
            for scene in fallback.animation_plan.scenes
        )
        self.assertTrue(has_graph_scene)

    def test_end_to_end_question_generates_problem_graph_scene(self):
        """
        End-to-end test: Feed a plain textual question through the orchestrator pipeline
        and verify the final SolverOutput animation JSON always contains the problem-linked graph scene.
        """
        question = "Solve the differential equation: d²y/dx² + 3dy/dx + 2y = 0"
        
        # Mock a simple LLM solver response (what would come from Gemini/GPT/etc)
        mock_solver_response = {
            "answer": "y = c₁e^(-x) + c₂e^(-2x)",
            "steps": [
                {"title": "Characteristic Equation", "description": "Form r² + 3r + 2 = 0"},
                {"title": "Factor", "description": "Factor as (r+1)(r+2) = 0"},
                {"title": "Roots", "description": "Find r = -1 and r = -2"},
                {"title": "General Solution", "description": "Write y = c₁e^(-x) + c₂e^(-2x)"},
            ]
        }
        
        # Normalize the mock response as would happen in any orchestrator path
        normalized_output = _normalize_solver_response(
            mock_solver_response,
            user_question=question
        )
        
        # Validate structure
        self.assertIn("solution", normalized_output)
        self.assertIn("animation_plan", normalized_output)
        self.assertEqual(normalized_output["solution"]["final_answer"], "y = c₁e^(-x) + c₂e^(-2x)")
        self.assertEqual(normalized_output["solution"]["subject"], "mathematics")
        
        # Critical assertion: animation plan has scenes
        self.assertGreaterEqual(len(normalized_output["animation_plan"]["scenes"]), 2)
        
        # Find graph scene(s) in the animation plan
        graph_scenes = [
            scene for scene in normalized_output["animation_plan"]["scenes"]
            if any(str((el or {}).get("type", "")).lower() in {"graph", "plot", "axes", "parametricgraph"}
                   for el in scene.get("elements", []) if isinstance(el, dict))
        ]
        
        # Core requirement: At least one graph scene MUST be present
        self.assertGreater(len(graph_scenes), 0, 
                          "Animation plan must contain at least one graph/plot/axes scene")
        
        # Second requirement: Graph scene must be linked to the problem (question keywords present)
        scene_text = " ".join(
            str(scene.get("voiceover", "")) + " " + str(scene.get("description", ""))
            for scene in graph_scenes
        ).lower()
        
        # The graph scene should reference the differential equation or solution
        has_problem_linkage = any(
            keyword in scene_text for keyword in [
                "differential", "equation", "solve", "d²y", "dy/dx", "solution"
            ]
        )
        self.assertTrue(has_problem_linkage,
                       f"Graph scene must be linked to problem. Scene text: {scene_text}")
        
        # Verify overview includes the question
        self.assertIn("Solve", normalized_output["animation_plan"]["overview"])

    def test_physics_question_adds_figure_and_graph_scenes(self):
        question = "A 1000 kg car moves on a 30 degree incline with friction. Draw forces and solve acceleration."
        raw = {
            "answer": "Use Newton's second law along the incline.",
            "steps": [
                {"title": "Identify forces", "description": "Weight, normal, friction, and net force along slope."},
                {"title": "Apply Newton", "description": "Resolve forces parallel to incline and compute acceleration."},
            ],
        }

        normalized = _normalize_solver_response(raw, user_question=question)
        scenes = normalized["animation_plan"]["scenes"]

        # Must include physics figure scene and graph scene together.
        physics_scenes = [
            s for s in scenes
            if isinstance(s, dict) and str(s.get("id", "")).startswith("physics_figure_")
        ]
        graph_scenes = [
            s for s in scenes
            if any(
                str((el or {}).get("type", "")).lower() in {"graph", "plot", "axes", "parametricgraph"}
                for el in s.get("elements", []) if isinstance(el, dict)
            )
        ]
        self.assertTrue(physics_scenes, "Physics question should include a figure scene")
        self.assertTrue(graph_scenes, "Physics question should also include a graph scene")

        figure_elements = [
            el for el in physics_scenes[0].get("elements", []) if isinstance(el, dict)
        ]
        figure_types = {str(el.get("type", "")).lower() for el in figure_elements}
        figure_text = " ".join(str(el.get("content", "")) for el in figure_elements).lower()

        # Object is drawn using shape primitives.
        self.assertTrue(
            any(t in figure_types for t in {"rectangle", "circle", "polygon"}),
            "Physics figure should include at least one drawn object",
        )
        # Forces are represented with arrows.
        self.assertIn("arrow", figure_types, "Physics figure should include force arrows")
        # Dimensions from the prompt should be shown.
        self.assertTrue(
            any(token in figure_text for token in ("m =", "kg", "theta", "deg", "d =", "m")),
            "Physics figure should include extracted dimensions such as mass/angle/distance",
        )

    def test_car_rough_surface_figure_contains_force_cues(self):
        scene = build_subject_figure_scene(
            "A 1200 kg car moves to the right on a rough horizontal surface with friction force, mu = 0.3 and speed 20 m/s.",
            subject="physics",
        )
        self.assertEqual(scene["id"], "physics_figure_rough_surface")
        text_blob = " ".join(str((el or {}).get("content", "")) for el in scene["elements"] if isinstance(el, dict)).lower()
        self.assertIn("car", text_blob)
        self.assertTrue(any(token in text_blob for token in ("n", "w=mg", "f", "kg")))
        self.assertIn("motion: right", text_blob)
        self.assertIn("mu=0.3", text_blob)

        car_body = next(
            (
                el for el in scene["elements"]
                if isinstance(el, dict)
                and str(el.get("type", "")).lower() == "rectangle"
                and isinstance(el.get("style"), dict)
                and el.get("style", {}).get("fill_color") == "#3a86ff"
            ),
            None,
        )
        self.assertIsNotNone(car_body, "Car body should use updated blue color scheme")

    def test_projectile_figure_contains_trajectory_and_velocity_components(self):
        scene = build_subject_figure_scene(
            "A stone is thrown as a projectile at 20 m/s. Find trajectory.",
            subject="physics",
        )
        self.assertEqual(scene["id"], "physics_figure_projectile")
        element_types = {str((el or {}).get("type", "")).lower() for el in scene["elements"] if isinstance(el, dict)}
        text_blob = " ".join(str((el or {}).get("content", "")) for el in scene["elements"] if isinstance(el, dict)).lower()
        self.assertIn("parametricgraph", element_types)
        self.assertIn("axes", element_types)
        self.assertTrue(any(token in text_blob for token in ("v0", "vx", "vy", "trajectory")))

    def test_car_theme_switches_for_wet_road(self):
        scene = build_subject_figure_scene(
            "A car moves on a wet road at night with friction.",
            subject="physics",
        )
        self.assertEqual(scene["id"], "physics_figure_rough_surface")
        text_blob = " ".join(str((el or {}).get("content", "")) for el in scene["elements"] if isinstance(el, dict)).lower()
        self.assertIn("theme: wet", text_blob)

        car_body = next(
            (
                el for el in scene["elements"]
                if isinstance(el, dict)
                and str(el.get("type", "")).lower() == "rectangle"
                and isinstance(el.get("style"), dict)
                and el.get("style", {}).get("fill_color") == "#1d4ed8"
            ),
            None,
        )
        self.assertIsNotNone(car_body)

    def test_car_theme_switches_for_icy_surface(self):
        scene = build_subject_figure_scene(
            "A car is on an icy surface with very low friction.",
            subject="physics",
        )
        text_blob = " ".join(str((el or {}).get("content", "")) for el in scene["elements"] if isinstance(el, dict)).lower()
        self.assertIn("theme: icy", text_blob)

    def test_car_theme_switches_for_hard_difficulty_without_environment(self):
        scene = build_subject_figure_scene(
            "Hard level: solve a rough-surface car force balance problem.",
            subject="physics",
        )
        text_blob = " ".join(str((el or {}).get("content", "")) for el in scene["elements"] if isinstance(el, dict)).lower()
        self.assertIn("theme: hard", text_blob)

    def test_collision_figure_contains_before_after_momentum_vectors(self):
        scene = build_subject_figure_scene(
            "Two objects collide and move together. Find momentum before and after collision.",
            subject="physics",
        )
        self.assertEqual(scene["id"], "physics_figure_collision")
        text_blob = " ".join(str((el or {}).get("content", "")) for el in scene["elements"] if isinstance(el, dict)).lower()
        self.assertIn("before", text_blob)
        self.assertIn("after", text_blob)
        self.assertTrue(any(token in text_blob for token in ("p1_before", "p2_before", "p_after")))

    def test_non_physics_subject_figure_injection_supported(self):
        q = "Given demand and supply equations, find market equilibrium."
        normalized = _normalize_solver_response(
            {
                "answer": "Equilibrium at intersection.",
                "subject": "economics",
                "steps": [{"title": "Set D=S", "description": "Solve simultaneously."}],
            },
            user_question=q,
        )
        scenes = normalized["animation_plan"]["scenes"]
        has_econ_figure = any(str(scene.get("id", "")).startswith("economics_figure_") for scene in scenes if isinstance(scene, dict))
        self.assertTrue(has_econ_figure)

    def test_chemistry_titration_scene_selected(self):
        scene = build_subject_figure_scene(
            "In an acid-base titration, determine endpoint pH and indicator change.",
            subject="chemistry",
        )
        self.assertEqual(scene["id"], "chemistry_figure_titration_scene")
        text_blob = " ".join(str((el or {}).get("content", "")) for el in scene["elements"] if isinstance(el, dict)).lower()
        self.assertIn("endpoint", text_blob)

    def test_chemistry_liquid_filling_scene_has_required_colors_and_water_reference(self):
        scene = build_subject_figure_scene(
            "Show filling liquid in vessel and bucket with acid, base and water, plus catalyst and promoter at 35 deg C and 2 atm under sunlight.",
            subject="chemistry",
        )
        self.assertEqual(scene["id"], "chemistry_figure_liquid_fill_scene")

        elements = [el for el in scene["elements"] if isinstance(el, dict)]
        fill_colors = [
            str((el.get("style") or {}).get("fill_color", "")).lower()
            for el in elements
            if isinstance(el.get("style"), dict)
        ]

        # Required liquid palette
        self.assertIn("#22c55e", fill_colors)  # acid -> green
        self.assertIn("#ffffff", fill_colors)  # base -> white
        self.assertIn("#3b82f6", fill_colors)  # water/neutral -> blue

        # Water should be mentioned naturally in voiceover and visibly in scene text.
        self.assertIn("water", str(scene.get("voiceover", "")).lower())
        text_blob = " ".join(str(el.get("content", "")) for el in elements).lower()
        self.assertIn("water", text_blob)

        # Requested additions: catalyst, promoter, thermometer/temperature, pressure,
        # sunlight animation and liquid drop animation cues.
        self.assertIn("catalyst", text_blob)
        self.assertIn("promoter", text_blob)
        self.assertIn("thermometer", text_blob)
        self.assertIn("pressure", text_blob)
        self.assertIn("sunlight animation", text_blob)
        self.assertIn("liquid drop animation", text_blob)
        self.assertIn("thermometer module", text_blob)
        self.assertIn("pressure gauge unit", text_blob)
        self.assertIn("temp lcd", text_blob)
        self.assertIn("pres lcd", text_blob)
        self.assertIn("35", text_blob)
        self.assertIn("2", text_blob)

    def test_hydrogen_nitric_acid_mistake_correction_is_present(self):
        scene = build_subject_figure_scene(
            "In laboratory hydrogen preparation, can we use nitric acid HNO3 with zinc? show catalyst promoter temperature and pressure effects.",
            subject="chemistry",
        )
        self.assertEqual(scene["id"], "chemistry_figure_preparation_scene")

        voiceover = str(scene.get("voiceover", "")).lower()
        self.assertIn("nitric acid", voiceover)
        self.assertIn("oxidizing", voiceover)
        self.assertIn("trace", voiceover)
        self.assertIn("dilute hydrochloric acid", voiceover)
        self.assertIn("zinc", voiceover)

        text_blob = " ".join(
            str((el or {}).get("content", "")) for el in scene.get("elements", []) if isinstance(el, dict)
        ).lower()
        self.assertIn("common mistake", text_blob)
        self.assertIn("hno3", text_blob)
        self.assertIn("zinc", text_blob)
        self.assertIn("2hcl", text_blob)
        self.assertIn("catalyst", text_blob)
        self.assertIn("promoter", text_blob)
        self.assertIn("temperature", text_blob)
        self.assertIn("pressure", text_blob)

    def test_general_chemistry_preparation_routes_to_preparation_scene(self):
        scene = build_subject_figure_scene(
            "Explain the laboratory preparation of oxygen gas and show reagent handling at 40 deg C and 2 atm.",
            subject="chemistry",
        )
        self.assertEqual(scene["id"], "chemistry_figure_preparation_scene")

        voiceover = str(scene.get("voiceover", "")).lower()
        self.assertIn("preparation questions", voiceover)
        self.assertIn("practical lab workflow", voiceover)

        text_blob = " ".join(
            str((el or {}).get("content", "")) for el in scene.get("elements", []) if isinstance(el, dict)
        ).lower()
        self.assertIn("preparation workflow", text_blob)
        self.assertIn("monitor temperature and pressure", text_blob)

    def test_math_geometry_scene_selected(self):
        scene = build_subject_figure_scene(
            "A triangle has sides and angle; find area using trigonometry.",
            subject="mathematics",
        )
        self.assertEqual(scene["id"], "math_figure_geometry_scene")
        element_types = {str((el or {}).get("type", "")).lower() for el in scene["elements"] if isinstance(el, dict)}
        self.assertIn("polygon", element_types)

    def test_economics_elasticity_scene_selected(self):
        scene = build_subject_figure_scene(
            "Compute price elasticity of demand between two points.",
            subject="economics",
        )
        self.assertEqual(scene["id"], "economics_figure_elasticity_scene")
        text_blob = " ".join(str((el or {}).get("content", "")) for el in scene["elements"] if isinstance(el, dict)).lower()
        self.assertIn("elastic", text_blob)

    def test_economics_question_without_subject_infers_econ_figure(self):
        normalized = _normalize_solver_response(
            {
                "answer": "Use demand and supply intersection.",
                "steps": [{"title": "Model", "description": "Set demand equal to supply and solve."}],
            },
            user_question="Given demand and supply equations, find market equilibrium price and quantity.",
        )
        scene_ids = [str(scene.get("id", "")) for scene in normalized["animation_plan"]["scenes"] if isinstance(scene, dict)]
        self.assertTrue(any(sid.startswith("economics_figure_") for sid in scene_ids))


if __name__ == "__main__":
    unittest.main()
