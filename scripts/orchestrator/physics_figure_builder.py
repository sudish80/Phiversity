"""
Subject Figure Builder.

Builds schematic figure scenes that can be injected into the animation plan.
Includes dedicated physics diagrams and lightweight visual scenes for
mathematics, chemistry, and economics.
"""

from __future__ import annotations

import math
import re
from typing import Any, Dict, Optional


def is_physics_problem(question: str) -> bool:
    q = (question or "").lower()
    physics_keywords = {
        "force", "friction", "mass", "acceleration", "velocity", "motion",
        "object", "car", "stone", "block", "incline", "ramp", "surface",
        "solid", "substance", "body", "projectile", "trajectory", "collision",
        "impact", "momentum", "gravity", "weight", "normal force", "tension",
        "newton", "kinetic", "potential", "energy", "work", "power",
    }
    return any(token in q for token in physics_keywords)


def is_subject_figure_applicable(question: str, subject: str | None = None) -> bool:
    if question and question.strip():
        return True
    return bool(subject)


def build_subject_figure_scene(question: str, subject: str | None = None) -> Dict[str, Any]:
    resolved_subject = (subject or _infer_subject(question)).strip().lower()
    if resolved_subject == "physics":
        return build_physics_figure_scene(question)
    if resolved_subject == "chemistry":
        return _build_chemistry_figure_scene(question, _infer_chemistry_scenario(question))
    if resolved_subject == "economics":
        return _build_economics_figure_scene(question, _infer_economics_scenario(question))
    return _build_mathematics_figure_scene(question, _infer_mathematics_scenario(question))


def _infer_subject(question: str) -> str:
    q = (question or "").lower()
    if any(token in q for token in ("force", "velocity", "acceleration", "momentum", "projectile", "collision", "friction", "newton")):
        return "physics"
    if any(token in q for token in ("mole", "molar", "acid", "base", "reaction", "equilibrium", "enthalpy", "compound", "atom", "ph")):
        return "chemistry"
    if any(token in q for token in ("demand", "supply", "price", "cost", "gdp", "inflation", "elasticity", "market")):
        return "economics"
    return "mathematics"


def _infer_mathematics_scenario(question: str) -> str:
    q = (question or "").lower()
    if any(token in q for token in ("triangle", "circle", "angle", "geometry", "area", "perimeter")):
        return "geometry"
    if any(token in q for token in ("derivative", "differentiate", "integral", "slope", "tangent", "limit", "dx", "dy")):
        return "calculus"
    return "algebra"


def _infer_chemistry_scenario(question: str) -> str:
    q = (question or "").lower()
    if any(token in q for token in ("hydrogen", "h2")) and any(token in q for token in ("nitric acid", "hno3")):
        return "preparation"
    if _is_chemistry_preparation_question(q):
        return "preparation"
    if any(token in q for token in ("fill", "filling", "pour", "transfer", "vessel", "bucket", "beaker", "flask", "container", "liquid level")):
        return "liquid_fill"
    if any(token in q for token in ("titration", "ph", "indicator", "neutralization")):
        return "titration"
    if any(token in q for token in ("gas", "pressure", "volume", "temperature", "boyle", "charles", "pv=nrt")):
        return "gas_law"
    return "reaction"


def _is_chemistry_preparation_question(lowered_question: str) -> bool:
    q = lowered_question or ""
    prep_tokens = (
        "preparation",
        "prepare",
        "prepared",
        "preparing",
        "laboratory preparation",
        "lab preparation",
        "method of preparation",
        "how to produce",
        "how to make",
        "synthesis of",
    )
    chemistry_tokens = (
        "acid",
        "base",
        "salt",
        "gas",
        "solution",
        "compound",
        "reaction",
        "reagent",
        "catalyst",
        "promoter",
        "h2",
        "o2",
        "co2",
        "nh3",
        "cl2",
    )

    return any(token in q for token in prep_tokens) and any(token in q for token in chemistry_tokens)


def _infer_economics_scenario(question: str) -> str:
    q = (question or "").lower()
    if any(token in q for token in ("elasticity", "arc elasticity", "point elasticity")):
        return "elasticity"
    if any(token in q for token in ("gdp", "inflation", "unemployment", "aggregate demand", "aggregate supply")):
        return "macro"
    return "market"


def extract_physics_objects(question: str) -> Dict[str, Any]:
    q = (question or "").lower()
    result: Dict[str, Any] = {
        "objects": [],
        "scenario": "free_body",
        "forces": [],
        "dimensions": {},
    }

    if "projectile" in q or "thrown" in q or "trajectory" in q:
        result["scenario"] = "projectile"
    elif "collision" in q or "impact" in q or "collide" in q:
        result["scenario"] = "collision"
    elif "spring" in q or "oscillat" in q or "pendulum" in q:
        result["scenario"] = "spring"
    elif "circular" in q or "centripetal" in q or "radial" in q:
        result["scenario"] = "circular"
    elif "incline" in q or "ramp" in q:
        result["scenario"] = "incline"
    elif "car" in q and (
        ("friction" in q or "rough" in q) and ("surface" in q or "horizontal" in q or "road" in q)
        or any(token in q for token in ("wet road", "icy road", "night road", "wet", "icy", "rainy"))
    ):
        result["scenario"] = "rough_surface"

    object_map = {
        "car": "car",
        "stone": "stone",
        "block": "block",
        "object": "object",
        "substance": "object",
        "solid": "object",
        "body": "object",
        "ball": "ball",
        "particle": "particle",
    }
    for token, obj_type in object_map.items():
        if token in q:
            result["objects"].append({"type": obj_type, "name": token.capitalize(), "mass": extract_mass(question)})
    if not result["objects"]:
        result["objects"].append({"type": "object", "name": "Object", "mass": extract_mass(question)})

    force_map = {
        "friction": "friction",
        "normal": "normal_force",
        "weight": "gravity",
        "gravity": "gravity",
        "applied": "applied_force",
        "tension": "tension",
        "drag": "drag",
        "air resistance": "drag",
    }
    for token, ftype in force_map.items():
        if token in q:
            result["forces"].append(ftype)

    mass_match = re.search(r"(\d+\.?\d*)\s*kg", q)
    if mass_match:
        result["dimensions"]["mass"] = float(mass_match.group(1))

    angle_match = re.search(r"(\d+\.?\d*)\s*(?:degree|deg|°)", q)
    if angle_match:
        result["dimensions"]["angle"] = float(angle_match.group(1))

    speed_match = re.search(r"(\d+\.?\d*)\s*(?:m/s|ms-1)", q)
    if speed_match:
        result["dimensions"]["speed"] = float(speed_match.group(1))

    accel_match = re.search(r"(?:acceleration|a)\s*(?:is|=)?\s*(\d+\.?\d*)\s*(?:m/s\^2|m/s2|ms-2)", q)
    if accel_match:
        result["dimensions"]["acceleration"] = float(accel_match.group(1))

    mu_match = re.search(r"(?:mu|μ|coefficient\s+of\s+friction)\s*(?:is|=)?\s*(\d+\.?\d*)", q)
    if mu_match:
        result["dimensions"]["mu"] = float(mu_match.group(1))

    distance_match = re.search(r"(\d+\.?\d*)\s*(?:m|meter|metre)\b", q)
    if distance_match:
        result["dimensions"]["distance"] = float(distance_match.group(1))

    if any(token in q for token in ("left", "toward left", "to the left")):
        result["dimensions"]["motion_direction"] = "left"
    elif any(token in q for token in ("right", "toward right", "to the right", "forward")):
        result["dimensions"]["motion_direction"] = "right"

    # Smart environment and difficulty cues for adaptive color themes.
    if any(token in q for token in ("icy", "ice", "snow", "frozen")):
        result["dimensions"]["environment"] = "icy"
    elif any(token in q for token in ("wet", "rain", "rainy", "slippery")):
        result["dimensions"]["environment"] = "wet"
    elif any(token in q for token in ("night", "dark", "midnight")):
        result["dimensions"]["environment"] = "night"

    if any(token in q for token in ("hard", "difficult", "advanced", "challenge")):
        result["dimensions"]["difficulty"] = "hard"
    elif any(token in q for token in ("medium", "intermediate")):
        result["dimensions"]["difficulty"] = "medium"
    elif any(token in q for token in ("easy", "beginner", "basic")):
        result["dimensions"]["difficulty"] = "easy"

    return result


def _car_theme_from_context(context: Dict[str, Any]) -> Dict[str, str]:
    dims = context.get("dimensions", {}) if isinstance(context, dict) else {}
    environment = str(dims.get("environment", "")).lower().strip()
    difficulty = str(dims.get("difficulty", "")).lower().strip()

    # Environment-specific themes take precedence.
    if environment == "icy":
        return {
            "name": "Icy",
            "car_body": "#8ecae6",
            "window": "#caf0f8",
            "wheel": "#1d3557",
            "road": "#d9edff",
            "accent": "#7bdff2",
            "text": "#ffffff",
        }
    if environment == "wet":
        return {
            "name": "Wet",
            "car_body": "#1d4ed8",
            "window": "#93c5fd",
            "wheel": "#0f172a",
            "road": "#475569",
            "accent": "#60a5fa",
            "text": "#ffffff",
        }
    if environment == "night":
        return {
            "name": "Night",
            "car_body": "#7c3aed",
            "window": "#c4b5fd",
            "wheel": "#111827",
            "road": "#1f2937",
            "accent": "#fde047",
            "text": "#f8fafc",
        }

    # Difficulty-based fallback themes.
    if difficulty == "hard":
        return {
            "name": "Hard",
            "car_body": "#ef4444",
            "window": "#fecaca",
            "wheel": "#1f2937",
            "road": "#6b7280",
            "accent": "#fb7185",
            "text": "#ffffff",
        }
    if difficulty == "medium":
        return {
            "name": "Medium",
            "car_body": "#f59e0b",
            "window": "#fde68a",
            "wheel": "#1f2937",
            "road": "#737373",
            "accent": "#fbbf24",
            "text": "#ffffff",
        }
    if difficulty == "easy":
        return {
            "name": "Easy",
            "car_body": "#10b981",
            "window": "#a7f3d0",
            "wheel": "#1f2937",
            "road": "#737373",
            "accent": "#34d399",
            "text": "#ffffff",
        }

    # Default theme.
    return {
        "name": "Default",
        "car_body": "#3a86ff",
        "window": "#8ecae6",
        "wheel": "#1d3557",
        "road": "#6f6f6f",
        "accent": "#8ecae6",
        "text": "#ffffff",
    }


def extract_mass(question: str) -> Optional[float]:
    q = (question or "").lower()
    for pattern in (r"(\d+\.?\d*)\s*kg", r"mass\s*(?:is|=)?\s*(\d+\.?\d*)"):
        m = re.search(pattern, q)
        if m:
            return float(m.group(1))
    return None


def build_physics_figure_scene(question: str, physics_context: Dict[str, Any] | None = None) -> Dict[str, Any]:
    context = physics_context or extract_physics_objects(question)
    scenario = context.get("scenario", "free_body")

    if scenario == "rough_surface":
        return _build_rough_surface_scene(question, context)
    if scenario == "projectile":
        return _build_projectile_scene(question, context)
    if scenario == "collision":
        return _build_collision_scene(question, context)
    if scenario == "incline":
        return _build_incline_scene(question, context)
    if scenario == "spring":
        return _build_spring_scene(question, context)
    if scenario == "circular":
        return _build_circular_scene(question, context)
    return _build_free_body_scene(question, context)


def _dimension_texts(
    context: Dict[str, Any],
    start_x: float = -4.1,
    y: float = -2.9,
    exclude_keys: set[str] | None = None,
) -> list[Dict[str, Any]]:
    dims = context.get("dimensions", {}) if isinstance(context, dict) else {}
    excluded = {str(k).lower() for k in (exclude_keys or set())}
    labels: list[str] = []
    if "mass" in dims and "mass" not in excluded:
        labels.append(f"m = {dims['mass']} kg")
    if "angle" in dims and "angle" not in excluded:
        labels.append(f"theta = {dims['angle']} deg")
    if "speed" in dims and "speed" not in excluded:
        labels.append(f"v = {dims['speed']} m/s")
    if "distance" in dims and "distance" not in excluded:
        labels.append(f"d = {dims['distance']} m")
    if "mu" in dims and "mu" not in excluded:
        labels.append(f"mu = {dims['mu']}")
    if "acceleration" in dims and "acceleration" not in excluded:
        labels.append(f"a = {dims['acceleration']} m/s^2")

    out: list[Dict[str, Any]] = []
    for idx, label in enumerate(labels[:3]):
        out.append(
            {
                "type": "Text",
                "content": label,
                "position": f"[{start_x + idx * 2.8}, {y}, 0]",
                "style": {"color": "#1f77b4", "font_size": 20},
            }
        )
    return out


def _build_rough_surface_scene(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    object_name = context.get("objects", [{}])[0].get("name", "Car")
    dims = context.get("dimensions", {}) if isinstance(context, dict) else {}
    direction = str(dims.get("motion_direction", "right")).lower()
    speed = float(dims.get("speed", 0.0) or 0.0)
    mu = dims.get("mu")
    accel = dims.get("acceleration")

    applied_x = 2.0 if direction == "right" else -2.0
    friction_x = -2.6 if direction == "right" else 2.6
    arrow_strength = 3 if speed <= 0 else min(6, 3 + int(speed // 10))

    theme = _car_theme_from_context(context)
    elements: list[Dict[str, Any]] = [
        {"type": "Title", "content": "Car On Rough Surface", "position": "[0, 3.3, 0]", "style": {"color": theme["text"]}},
        {"type": "Rectangle", "position": "[0, -1.4, 0]", "style": {"width": 8.0, "height": 0.35, "fill_color": theme["road"], "fill_opacity": 0.85}},
        {"type": "Rectangle", "position": "[-0.7, -0.45, 0]", "style": {"width": 2.0, "height": 0.7, "fill_color": theme["car_body"], "fill_opacity": 0.95}},
        {"type": "Rectangle", "position": "[-0.35, -0.2, 0]", "style": {"width": 0.9, "height": 0.35, "fill_color": theme["window"], "fill_opacity": 0.85}},
        {"type": "Circle", "position": "[-1.4, -0.85, 0]", "style": {"radius": 0.2, "fill_color": theme["wheel"], "fill_opacity": 0.95}},
        {"type": "Circle", "position": "[0.0, -0.85, 0]", "style": {"radius": 0.2, "fill_color": theme["wheel"], "fill_opacity": 0.95}},
        {"type": "Text", "content": object_name, "position": "[-0.7, -0.45, 0]", "style": {"color": theme["text"]}},
        {"type": "Arrow", "position": "[-0.7, 1.25, 0]", "style": {"color": "#2ca02c", "stroke_width": 3}},
        {"type": "Text", "content": "N", "position": "[-0.35, 1.55, 0]", "style": {"color": "#2ca02c"}},
        {"type": "Arrow", "position": "[-0.7, -2.1, 0]", "style": {"color": "#d62728", "stroke_width": 3}},
        {"type": "Text", "content": "W=mg", "position": "[-0.1, -2.35, 0]", "style": {"color": "#d62728"}},
        {"type": "Arrow", "position": f"[{applied_x}, -0.45, 0]", "style": {"color": "#1f77b4", "stroke_width": arrow_strength}},
        {"type": "Text", "content": "F", "position": f"[{applied_x + (0.35 if direction == 'right' else -0.35)}, -0.15, 0]", "style": {"color": "#1f77b4"}},
        {"type": "Arrow", "position": f"[{friction_x}, -0.45, 0]", "style": {"color": "#9467bd", "stroke_width": max(2, arrow_strength - 1)}},
        {"type": "Text", "content": "f", "position": f"[{friction_x + (-0.35 if direction == 'right' else 0.35)}, -0.15, 0]", "style": {"color": "#9467bd"}},
        {"type": "Text", "content": f"Motion: {direction}", "position": "[2.9, -1.95, 0]", "style": {"color": theme["accent"]}},
        {"type": "Text", "content": f"Theme: {theme['name']}", "position": "[2.9, -1.65, 0]", "style": {"color": theme["accent"]}},
    ]

    if speed > 0:
        elements.append(
            {"type": "Text", "content": f"v = {speed} m/s", "position": "[2.9, -2.25, 0]", "style": {"color": theme["accent"]}}
        )
    if mu is not None:
        elements.append(
            {"type": "Text", "content": f"f = mu*N, mu={mu}", "position": "[2.9, -2.55, 0]", "style": {"color": "#c77dff"}}
        )
    if accel is not None:
        elements.append(
            {"type": "Text", "content": f"a = {accel} m/s^2", "position": "[2.9, -2.85, 0]", "style": {"color": "#90be6d"}}
        )

    # Keep shared given-data labels on a dedicated lower row and avoid duplicating
    # values already shown in the smart right-side panel (v, mu, a).
    elements.extend(
        _dimension_texts(
            context,
            y=-3.25,
            exclude_keys={"speed", "mu", "acceleration"},
        )
    )
    return {
        "id": "physics_figure_rough_surface",
        "description": "Car free-body on rough horizontal surface",
        "voiceover": "Draw the car as an object on a rough horizontal surface. Include normal force upward, weight downward, applied force in the direction of motion, and friction opposite to motion. Adapt force arrows using available speed and direction data, annotate friction coefficient or acceleration when given, and switch to a context-aware color theme based on environment or difficulty cues.",
        "duration_seconds": 42,
        "elements": elements,
    }


def _build_projectile_scene(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    elements: list[Dict[str, Any]] = [
        {"type": "Title", "content": "Projectile Trajectory", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "projectile reference frame", "position": "[0, -0.2, 0]", "style": {"x_range": [0, 12, 1], "y_range": [0, 7, 1], "x_label": "x", "y_label": "y"}},
        {"type": "ParametricGraph", "content": "(t, 3.5*t - 0.49*t**2)", "position": "[0, -0.2, 0]", "style": {"t_range": [0, 6], "label": "trajectory"}},
        {"type": "Circle", "position": "[1.0, 0.55, 0]", "style": {"radius": 0.16, "fill_color": "#ff7f0e", "fill_opacity": 0.9}},
        {"type": "Arrow", "position": "[2.0, 1.6, 0]", "style": {"color": "#1f77b4", "stroke_width": 3}},
        {"type": "Text", "content": "v0", "position": "[2.3, 1.9, 0]", "style": {"color": "#1f77b4"}},
        {"type": "Arrow", "position": "[2.6, 1.2, 0]", "style": {"color": "#17becf", "stroke_width": 3}},
        {"type": "Text", "content": "vx", "position": "[2.9, 1.45, 0]", "style": {"color": "#17becf"}},
        {"type": "Arrow", "position": "[1.9, 2.15, 0]", "style": {"color": "#bcbd22", "stroke_width": 3}},
        {"type": "Text", "content": "vy", "position": "[2.2, 2.35, 0]", "style": {"color": "#bcbd22"}},
        {"type": "Arrow", "position": "[5.0, -0.45, 0]", "style": {"color": "#d62728", "stroke_width": 3}},
        {"type": "Text", "content": "g", "position": "[5.3, -0.7, 0]", "style": {"color": "#d62728"}},
    ]
    elements.extend(_dimension_texts(context))
    return {
        "id": "physics_figure_projectile",
        "description": "Projectile path with decomposed velocity components",
        "voiceover": "Show the projectile trajectory on axes and decompose the launch velocity into horizontal and vertical components. The horizontal component remains nearly constant while the vertical component changes under gravity.",
        "duration_seconds": 44,
        "elements": elements,
    }


def _build_collision_scene(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    elements: list[Dict[str, Any]] = [
        {"type": "Title", "content": "Collision: Before and After", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Text", "content": "Before", "position": "[-2.9, 2.5, 0]", "style": {"color": "#6ec1ff"}},
        {"type": "Rectangle", "position": "[-3.0, 0.8, 0]", "style": {"width": 0.9, "height": 0.6, "fill_color": "#ff7f0e", "fill_opacity": 0.85}},
        {"type": "Rectangle", "position": "[-1.0, 0.8, 0]", "style": {"width": 0.9, "height": 0.6, "fill_color": "#2ca02c", "fill_opacity": 0.85}},
        {"type": "Arrow", "position": "[-2.1, 1.35, 0]", "style": {"color": "#1f77b4", "stroke_width": 3}},
        {"type": "Text", "content": "p1_before", "position": "[-1.7, 1.65, 0]", "style": {"color": "#1f77b4", "font_size": 20}},
        {"type": "Arrow", "position": "[-0.2, 0.25, 0]", "style": {"color": "#17becf", "stroke_width": 3}},
        {"type": "Text", "content": "p2_before", "position": "[0.25, 0.55, 0]", "style": {"color": "#17becf", "font_size": 20}},
        {"type": "Text", "content": "After", "position": "[2.7, 2.5, 0]", "style": {"color": "#6ec1ff"}},
        {"type": "Rectangle", "position": "[2.2, 0.8, 0]", "style": {"width": 1.6, "height": 0.7, "fill_color": "#9467bd", "fill_opacity": 0.85}},
        {"type": "Arrow", "position": "[3.4, 1.35, 0]", "style": {"color": "#d62728", "stroke_width": 3}},
        {"type": "Text", "content": "p_after", "position": "[3.8, 1.65, 0]", "style": {"color": "#d62728", "font_size": 20}},
    ]
    elements.extend(_dimension_texts(context))
    return {
        "id": "physics_figure_collision",
        "description": "Collision momentum vectors before and after",
        "voiceover": "Represent momentum vectors before collision for each body, then show the resulting momentum after collision. Use vector direction and relative magnitude to apply momentum conservation.",
        "duration_seconds": 43,
        "elements": elements,
    }


def _build_incline_scene(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    angle = context.get("dimensions", {}).get("angle", 30)
    mass = context.get("dimensions", {}).get("mass")
    mu = context.get("dimensions", {}).get("mu")
    elements: list[Dict[str, Any]] = [
        {"type": "Title", "content": "Object On Incline", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Polygon", "position": "[-1.9, -1.0, 0]", "style": {"fill_color": "#8b8680", "fill_opacity": 0.55}},
        {"type": "Circle", "position": "[-0.2, 0.2, 0]", "style": {"radius": 0.35, "fill_color": "#ff7f0e", "fill_opacity": 0.85}},
        {"type": "Arrow", "position": "[-0.2, -1.8, 0]", "style": {"color": "#d62728", "stroke_width": 3}},
        {"type": "Text", "content": "W=mg", "position": "[0.15, -2.05, 0]", "style": {"color": "#d62728"}},
        {"type": "Arrow", "position": "[0.7, 0.95, 0]", "style": {"color": "#2ca02c", "stroke_width": 3}},
        {"type": "Text", "content": "N", "position": "[1.05, 1.2, 0]", "style": {"color": "#2ca02c"}},
        {"type": "Arrow", "position": "[-1.3, -0.35, 0]", "style": {"color": "#9467bd", "stroke_width": 3}},
        {"type": "Text", "content": "f", "position": "[-1.55, -0.65, 0]", "style": {"color": "#9467bd"}},
        {"type": "Text", "content": f"theta = {angle} deg", "position": "[-1.2, -0.9, 0]", "style": {"color": "#000000"}},
        {"type": "Paragraph", "content": f"F_parallel = mg*sin({angle}) = {mass*9.81*math.sin(math.radians(angle)):.1f} N ; F_perp = mg*cos({angle}) = {mass*9.81*math.cos(math.radians(angle)):.1f} N" if mass else f"F_parallel = mg*sin(theta) ; F_perp = mg*cos(theta)", "position": "[0, -2.8, 0]", "style": {"color": "#ffd700", "font_size": 18}},
    ]
    elements.extend(_dimension_texts(context))
    return {
        "id": "physics_figure_incline",
        "description": "Incline free-body with resolved forces",
        "voiceover": f"On a {angle}-degree incline, resolve weight into components parallel and perpendicular to the surface. The parallel component mg sine theta drives motion downward, while the perpendicular component mg cosine theta equals the normal force.{f' Friction opposes motion with coefficient mu = {mu}.' if mu else ''}",
        "duration_seconds": 48,
        "elements": elements,
    }


def _build_spring_scene(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    mass = context.get("dimensions", {}).get("mass", 1.0)
    elements: list[Dict[str, Any]] = [
        {"type": "Title", "content": "Spring-Mass Oscillator", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Line", "content": "spring equilibrium", "position": "[-1.5, 0.5, 0]", "style": {"color": "#8ecae6", "stroke_width": 2}},
        {"type": "Line", "content": "spring compressed", "position": "[-1.5, -0.5, 0]", "style": {"color": "#ff7f0e", "stroke_width": 2}},
        {"type": "Line", "content": "spring extended", "position": "[-1.5, 1.5, 0]", "style": {"color": "#2ca02c", "stroke_width": 2}},
        {"type": "Text", "content": "Equilibrium", "position": "[2.0, 0.5, 0]", "style": {"color": "#8ecae6", "font_size": 18}},
        {"type": "Text", "content": "Compressed", "position": "[2.0, -0.5, 0]", "style": {"color": "#ff7f0e", "font_size": 18}},
        {"type": "Text", "content": "Extended", "position": "[2.0, 1.5, 0]", "style": {"color": "#2ca02c", "font_size": 18}},
        {"type": "Paragraph", "content": f"F = -kx (Hooke's Law);  omega = sqrt(k/m) ;  T = 2*pi*sqrt(m/k) ;  m = {mass} kg", "position": "[0, -2.5, 0]", "style": {"color": "#ffd700", "font_size": 18}},
    ]
    elements.extend(_dimension_texts(context))
    return {
        "id": "physics_figure_spring",
        "description": "Spring-mass oscillator at equilibrium, compressed, and extended positions",
        "voiceover": f"The spring-mass system oscillates with mass {mass} kg. Hooke's law gives restoring force F equals negative k x. Angular frequency omega equals sqrt k over m. Period T equals 2 pi times sqrt m over k. The system stores energy as it alternates between kinetic and elastic potential.",
        "duration_seconds": 45,
        "elements": elements,
    }


def _build_circular_scene(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    elements: list[Dict[str, Any]] = [
        {"type": "Title", "content": "Circular Motion", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Circle", "position": "[0, 0.0, 0]", "style": {"radius": 2.0, "fill_opacity": 0.0, "stroke_width": 2, "stroke_color": "#8ecae6"}},
        {"type": "Circle", "position": "[0, 2.0, 0]", "style": {"radius": 0.25, "fill_color": "#ff7f0e", "fill_opacity": 0.9}},
        {"type": "Arrow", "position": "[0, 0, 0]", "style": {"color": "#1f77b4", "stroke_width": 3}},
        {"type": "Text", "content": "r", "position": "[0.7, 0.8, 0]", "style": {"color": "#1f77b4"}},
        {"type": "Arrow", "position": "[0.25, 2.2, 0]", "style": {"color": "#2ca02c", "stroke_width": 3}},
        {"type": "Text", "content": "v (tangential)", "position": "[1.0, 2.4, 0]", "style": {"color": "#2ca02c"}},
        {"type": "Arrow", "position": "[0, 0.75, 0]", "style": {"color": "#d62728", "stroke_width": 3}},
        {"type": "Text", "content": "a_c (centripetal)", "position": "[0.75, 0.8, 0]", "style": {"color": "#d62728"}},
        {"type": "Paragraph", "content": "a_c = v^2/r = omega^2 * r ;  F_c = m*v^2/r ;  T = 2*pi*r/v", "position": "[0, -2.8, 0]", "style": {"color": "#ffd700", "font_size": 18}},
    ]
    elements.extend(_dimension_texts(context))
    return {
        "id": "physics_figure_circular",
        "description": "Circular motion with centripetal acceleration and tangential velocity",
        "voiceover": "This circular motion diagram shows an object moving along a circular path of radius r. The tangential velocity vector points along the tangent, while centripetal acceleration points inward toward the center. Centripetal force equals m v squared over r directed radially inward.",
        "duration_seconds": 44,
        "elements": elements,
    }


def _build_free_body_scene(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    object_name = context.get("objects", [{}])[0].get("name", "Object")
    mass = context.get("dimensions", {}).get("mass")
    mu = context.get("dimensions", {}).get("mu")
    dims = context.get("dimensions", {})

    equation_lines = []
    if mass:
        equation_lines.append(f"W = mg = {mass}*9.81 = {mass*9.81:.1f} N")
    if mu and mass:
        equation_lines.append(f"f = mu*N = {mu}*{mass*9.81:.1f} = {mu*mass*9.81:.1f} N")
    if not equation_lines:
        equation_lines.append("F_net = ma  (Newton's 2nd Law)")

    elements: list[Dict[str, Any]] = [
        {"type": "Title", "content": "Free-Body Diagram", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Rectangle", "position": "[0, 0.0, 0]", "style": {"width": 1.0, "height": 1.0, "fill_color": "#ff7f0e", "fill_opacity": 0.8}},
        {"type": "Text", "content": object_name, "position": "[0, 0.0, 0]", "style": {"color": "#ffffff"}},
        {"type": "Arrow", "position": "[0, 2.1, 0]", "style": {"color": "#2ca02c", "stroke_width": 3}},
        {"type": "Text", "content": "N", "position": "[0.3, 2.35, 0]", "style": {"color": "#2ca02c"}},
        {"type": "Arrow", "position": "[0, -2.2, 0]", "style": {"color": "#d62728", "stroke_width": 3}},
        {"type": "Text", "content": "W", "position": "[0.3, -2.45, 0]", "style": {"color": "#d62728"}},
        {"type": "Arrow", "position": "[2.2, 0, 0]", "style": {"color": "#1f77b4", "stroke_width": 3}},
        {"type": "Text", "content": "F", "position": "[2.45, 0.25, 0]", "style": {"color": "#1f77b4"}},
        {"type": "Arrow", "position": "[-2.2, 0, 0]", "style": {"color": "#9467bd", "stroke_width": 3}},
        {"type": "Text", "content": "f", "position": "[-2.45, 0.25, 0]", "style": {"color": "#9467bd"}},
        {"type": "Paragraph", "content": "; ".join(equation_lines), "position": "[0, -3.0, 0]", "style": {"color": "#ffd700", "font_size": 18}},
    ]
    if mass:
        elements.append({"type": "Text", "content": f"N = mg = {mass*9.81:.1f} N (vertical equilibrium)", "position": "[3.0, -1.0, 0]", "style": {"color": "#8ecae6", "font_size": 16}})
    if mu:
        elements.append({"type": "Text", "content": f"f_k = mu_k * N = {mu} * {mass*9.81:.1f if mass else 'N'}", "position": "[3.0, -1.5, 0]", "style": {"color": "#f4a261", "font_size": 16}})
    elements.extend(_dimension_texts(context))
    return {
        "id": "physics_figure_free_body",
        "description": "Object-level free-body forces with derived equations",
        "voiceover": f"Use this free-body diagram to identify all forces on {object_name}. Normal force N acts upward, weight W acts downward, applied force F acts horizontally, and friction f opposes motion. From these we derive the net force equations.",
        "duration_seconds": 48,
        "elements": elements,
    }


def _build_mathematics_figure_scene(question: str, scenario: str = "algebra") -> Dict[str, Any]:
    short = " ".join((question or "math problem").split())[:120]
    if scenario == "geometry":
        return {
            "id": "math_figure_geometry_scene",
            "description": "Geometry figure with labeled dimensions",
            "voiceover": f"Use this geometry sketch to map known sides and angles in: {short}.",
            "duration_seconds": 38,
            "elements": [
                {"type": "Title", "content": "Geometry Figure", "position": "[0, 3.2, 0]", "style": {"color": "#ffffff"}},
                {"type": "Paragraph", "content": f"Problem context: {short}", "position": "[0, 2.2, 0]", "style": {"color": "#d9e6ff"}},
                {"type": "Polygon", "position": "[-0.8, -0.3, 0]", "style": {"fill_color": "#1f77b4", "fill_opacity": 0.2}},
                {"type": "Text", "content": "a", "position": "[-1.8, -0.2, 0]", "style": {"color": "#ffcc66"}},
                {"type": "Text", "content": "b", "position": "[0.5, -1.1, 0]", "style": {"color": "#ffcc66"}},
                {"type": "Text", "content": "theta", "position": "[-1.1, -0.8, 0]", "style": {"color": "#ffcc66"}},
            ],
        }
    if scenario == "calculus":
        return {
            "id": "math_figure_calculus_scene",
            "description": "Calculus graph with tangent interpretation",
            "voiceover": f"Use the curve and tangent line to interpret derivative and accumulation behavior for: {short}.",
            "duration_seconds": 38,
            "elements": [
                {"type": "Title", "content": "Calculus Figure", "position": "[0, 3.2, 0]", "style": {"color": "#ffffff"}},
                {"type": "Paragraph", "content": f"Problem context: {short}", "position": "[0, 2.2, 0]", "style": {"color": "#d9e6ff"}},
                {"type": "Axes", "content": "calculus coordinate frame", "position": "[0, -0.2, 0]", "style": {"x_range": [-4, 4, 1], "y_range": [-4, 6, 1], "x_label": "x", "y_label": "y"}},
                {"type": "Graph", "content": "x**2 - x", "position": "[0, -0.2, 0]", "style": {"x_range": [-3, 3], "label": "f(x)"}},
                {"type": "Line", "content": "tangent approximation", "position": "[0.7, 0.5, 0]", "style": {"color": "#ff7f0e", "stroke_width": 3}},
                {"type": "Text", "content": "slope = f'(x0)", "position": "[1.5, 1.0, 0]", "style": {"color": "#ff7f0e"}},
            ],
        }
    return {
        "id": "math_figure_coordinate_scene",
        "description": "Mathematical coordinate and relation figure",
        "voiceover": f"Use this mathematical figure to visualize the relationship in the problem: {short}.",
        "duration_seconds": 38,
        "elements": [
            {"type": "Title", "content": "Math Figure", "position": "[0, 3.2, 0]", "style": {"color": "#ffffff"}},
            {"type": "Paragraph", "content": f"Problem context: {short}", "position": "[0, 2.2, 0]", "style": {"color": "#d9e6ff"}},
            {"type": "Axes", "content": "mathematical coordinate frame", "position": "[0, -0.2, 0]", "style": {"x_range": [-5, 5, 1], "y_range": [-4, 4, 1], "x_label": "x", "y_label": "y"}},
            {"type": "Graph", "content": "x**2/4 - 1", "position": "[0, -0.2, 0]", "style": {"x_range": [-4, 4], "label": "f(x)"}},
            {"type": "Arrow", "position": "[1.1, 0.8, 0]", "style": {"color": "#ff7f0e", "stroke_width": 3}},
            {"type": "Text", "content": "key point", "position": "[1.45, 1.05, 0]", "style": {"color": "#ff7f0e"}},
        ],
    }


def _build_chemistry_figure_scene(question: str, scenario: str = "reaction") -> Dict[str, Any]:
    short = " ".join((question or "chemistry problem").split())[:120]
    if scenario in ("liquid_fill", "preparation"):
        q = (question or "").lower()
        temp_match = re.search(r"(\d+\.?\d*)\s*(?:deg\s*c|°c|celsius)", q)
        pressure_match = re.search(r"(\d+\.?\d*)\s*(?:atm|bar|kpa|pa)", q)
        temp_text = f"{temp_match.group(1)} deg C" if temp_match else "25 deg C"
        pressure_text = f"{pressure_match.group(1)}" if pressure_match else "1"

        has_catalyst = any(token in q for token in ("catalyst", "cat."))
        has_promoter = any(token in q for token in ("promoter",))
        has_sunlight = any(token in q for token in ("sunlight", "light", "uv", "photo"))
        hydrogen_context = any(token in q for token in ("hydrogen", "h2"))
        nitric_context = any(token in q for token in ("nitric acid", "hno3"))
        preparation_context = scenario == "preparation" or _is_chemistry_preparation_question(q)

        voiceover_parts = [
            f"Let us fill liquids in a human, practical way for this setup: {short}.",
            "We pour water first so learners can see level changes clearly.",
            "In the scene, acid is shown in green, base is shown in white, and water or any other neutral liquid is shown in blue.",
            "This makes vessel, bucket, and chemistry equipment comparisons easy to understand at a glance.",
            f"Temperature is shown with a thermometer machine at about {temp_text}, and pressure is shown on a gauge machine around {pressure_text} atm.",
            "Liquid drop animation cues are added near the equipment to make pouring feel natural.",
        ]
        if has_catalyst:
            voiceover_parts.append("A catalyst is highlighted to show faster reaction without being consumed.")
        if has_promoter:
            voiceover_parts.append("A promoter is also highlighted to support catalyst efficiency.")
        if has_sunlight:
            voiceover_parts.append("Sunlight animation cues are included to indicate photo-driven behavior.")
        if preparation_context:
            voiceover_parts.append(
                "For chemistry preparation questions, this scene now defaults to a practical lab workflow: reagent choice, controlled addition, collection setup, and condition monitoring."
            )
            voiceover_parts.append(
                "The same visual logic keeps preparation answers appealing and consistent even when temperature or pressure terms appear in the prompt."
            )
        if hydrogen_context and nitric_context:
            voiceover_parts.append(
                "Common lab error: using nitric acid to prepare hydrogen. Nitric acid is a strong oxidizing acid, so it usually forms nitrogen oxides and water instead of releasing useful hydrogen gas."
            )
            voiceover_parts.append(
                "Correct practice: use dilute hydrochloric acid or dilute sulfuric acid with zinc, for example Zn + 2HCl gives ZnCl2 + H2."
            )
            voiceover_parts.append(
                "If nitric acid is forced into the setup, hydrogen is formed only in trace or least amount, so it is not the proper laboratory route."
            )
            voiceover_parts.append(
                "Also compare process effects: catalyst speeds reaction, promoter supports catalyst efficiency, higher temperature increases rate, and pressure mostly affects gas collection behavior in this setup."
            )

        return {
            "id": "chemistry_figure_preparation_scene" if scenario == "preparation" else "chemistry_figure_liquid_fill_scene",
            "description": "Liquid filling in vessel bucket and lab equipment",
            "voiceover": " ".join(voiceover_parts),
            "duration_seconds": 42,
            "elements": [
                {"type": "Title", "content": "Chemistry Figure: Liquid Filling", "position": "[0, 3.2, 0]", "style": {"color": "#ffffff"}},
                {"type": "Paragraph", "content": f"Problem context: {short}", "position": "[0, 2.35, 0]", "style": {"color": "#d9e6ff"}},

                {"type": "Text", "content": "Vessel", "position": "[-3.0, 1.2, 0]", "style": {"color": "#9ec5ff"}},
                {"type": "Rectangle", "position": "[-3.0, -0.1, 0]", "style": {"width": 1.25, "height": 2.4, "fill_color": "#1e293b", "fill_opacity": 0.12, "stroke_width": 2}},
                {"type": "Rectangle", "position": "[-3.0, -0.75, 0]", "style": {"width": 1.1, "height": 1.1, "fill_color": "#3b82f6", "fill_opacity": 0.85}},
                {"type": "Text", "content": "Water / Neutral (Blue)", "position": "[-3.0, -1.75, 0]", "style": {"color": "#3b82f6", "font_size": 20}},

                {"type": "Text", "content": "Bucket", "position": "[0.0, 1.2, 0]", "style": {"color": "#9ec5ff"}},
                {"type": "Rectangle", "position": "[0.0, -0.2, 0]", "style": {"width": 1.6, "height": 2.2, "fill_color": "#334155", "fill_opacity": 0.1, "stroke_width": 2}},
                {"type": "Rectangle", "position": "[0.0, -0.9, 0]", "style": {"width": 1.45, "height": 0.95, "fill_color": "#22c55e", "fill_opacity": 0.9}},
                {"type": "Text", "content": "Acid (Green)", "position": "[0.0, -1.75, 0]", "style": {"color": "#22c55e", "font_size": 20}},

                {"type": "Text", "content": "Lab Equipment (Beaker/Flask)", "position": "[3.0, 1.2, 0]", "style": {"color": "#9ec5ff", "font_size": 24}},
                {"type": "Rectangle", "position": "[3.0, -0.2, 0]", "style": {"width": 1.35, "height": 2.2, "fill_color": "#334155", "fill_opacity": 0.1, "stroke_width": 2}},
                {"type": "Rectangle", "position": "[3.0, -0.9, 0]", "style": {"width": 1.2, "height": 0.85, "fill_color": "#ffffff", "fill_opacity": 0.95}},
                {"type": "Text", "content": "Base (White)", "position": "[3.0, -1.75, 0]", "style": {"color": "#ffffff", "font_size": 20}},

                {"type": "Text", "content": "Catalyst", "position": "[1.9, 0.35, 0]", "style": {"color": "#fbbf24", "font_size": 20}},
                {"type": "Circle", "position": "[1.45, 0.05, 0]", "style": {"radius": 0.12, "fill_color": "#fbbf24", "fill_opacity": 0.9}},
                {"type": "Text", "content": "Promoter", "position": "[1.9, -0.1, 0]", "style": {"color": "#fb7185", "font_size": 20}},
                {"type": "Circle", "position": "[1.45, -0.35, 0]", "style": {"radius": 0.12, "fill_color": "#fb7185", "fill_opacity": 0.9}},

                {"type": "Rectangle", "position": "[-4.0, -0.1, 0]", "style": {"width": 0.85, "height": 2.5, "fill_color": "#111827", "fill_opacity": 0.2, "stroke_width": 2}},
                {"type": "Text", "content": "Thermometer Module", "position": "[-4.0, 1.35, 0]", "style": {"color": "#e2e8f0", "font_size": 18}},
                {"type": "Rectangle", "position": "[-4.0, 0.05, 0]", "style": {"width": 0.18, "height": 1.55, "fill_color": "#e5e7eb", "fill_opacity": 0.35, "stroke_width": 2}},
                {"type": "Rectangle", "position": "[-4.0, -0.55, 0]", "style": {"width": 0.1, "height": 0.75, "fill_color": "#ef4444", "fill_opacity": 0.92}},
                {"type": "Circle", "position": "[-4.0, -1.02, 0]", "style": {"radius": 0.14, "fill_color": "#ef4444", "fill_opacity": 0.95}},
                {"type": "Rectangle", "position": "[-3.25, -1.0, 0]", "style": {"width": 1.15, "height": 0.45, "fill_color": "#0f172a", "fill_opacity": 0.82, "stroke_width": 2}},
                {"type": "Text", "content": f"TEMP LCD: {temp_text}", "position": "[-3.25, -1.0, 0]", "style": {"color": "#22d3ee", "font_size": 18}},

                {"type": "Rectangle", "position": "[4.1, 0.1, 0]", "style": {"width": 1.55, "height": 2.25, "fill_color": "#111827", "fill_opacity": 0.2, "stroke_width": 2}},
                {"type": "Text", "content": "Pressure Gauge Unit", "position": "[4.1, 1.35, 0]", "style": {"color": "#e2e8f0", "font_size": 18}},
                {"type": "Circle", "position": "[4.1, 0.45, 0]", "style": {"radius": 0.42, "fill_color": "#0f172a", "fill_opacity": 0.18, "stroke_width": 2}},
                {"type": "Arrow", "position": "[4.2, 0.45, 0]", "style": {"color": "#f8fafc", "stroke_width": 2}},
                {"type": "Rectangle", "position": "[4.1, -0.75, 0]", "style": {"width": 1.2, "height": 0.42, "fill_color": "#0f172a", "fill_opacity": 0.86, "stroke_width": 2}},
                {"type": "Text", "content": f"PRES LCD: {pressure_text} atm", "position": "[4.1, -0.75, 0]", "style": {"color": "#a7f3d0", "font_size": 18}},

                {"type": "Line", "content": "sunlight ray 1", "position": "[-2.0, 2.6, 0]", "style": {"color": "#fde047", "stroke_width": 3}},
                {"type": "Line", "content": "sunlight ray 2", "position": "[-1.6, 2.3, 0]", "style": {"color": "#fde047", "stroke_width": 3}},
                {"type": "Text", "content": "Sunlight animation", "position": "[-1.0, 2.1, 0]", "style": {"color": "#fde047", "font_size": 20}},

                {"type": "Circle", "position": "[2.75, 0.95, 0]", "style": {"radius": 0.06, "fill_color": "#60a5fa", "fill_opacity": 0.9}},
                {"type": "Circle", "position": "[2.95, 0.65, 0]", "style": {"radius": 0.07, "fill_color": "#60a5fa", "fill_opacity": 0.9}},
                {"type": "Text", "content": "Liquid drop animation", "position": "[2.95, 0.25, 0]", "style": {"color": "#60a5fa", "font_size": 20}},

                {"type": "Arrow", "position": "[-1.55, 0.75, 0]", "style": {"color": "#60a5fa", "stroke_width": 3}},
                {"type": "Text", "content": "Pouring water", "position": "[-1.05, 1.0, 0]", "style": {"color": "#60a5fa", "font_size": 20}},
                *([
                    {"type": "Text", "content": "Preparation workflow: select reagent pair -> controlled addition -> gas/liquid collection", "position": "[0.0, -2.15, 0]", "style": {"color": "#a5f3fc", "font_size": 18}},
                    {"type": "Text", "content": "Control panel: monitor temperature and pressure, then verify product purity", "position": "[0.0, -2.4, 0]", "style": {"color": "#bfdbfe", "font_size": 18}},
                ] if preparation_context and not (hydrogen_context and nitric_context) else []),
                *([
                    {"type": "Text", "content": "Common mistake: Use of nitric acid (HNO3) for H2 prep", "position": "[0.0, -2.15, 0]", "style": {"color": "#f87171", "font_size": 20}},
                    {"type": "Text", "content": "Reason: HNO3 is oxidizing, gives NOx, hydrogen only trace/least amount", "position": "[0.0, -2.4, 0]", "style": {"color": "#fca5a5", "font_size": 18}},
                    {"type": "Text", "content": "Correct route: Zn + 2HCl -> ZnCl2 + H2 (or dilute H2SO4)", "position": "[0.0, -2.65, 0]", "style": {"color": "#86efac", "font_size": 18}},
                    {"type": "Text", "content": "Effect panel: catalyst↑ rate, promoter supports catalyst, temperature↑ rate, pressure affects gas handling", "position": "[0.0, -2.9, 0]", "style": {"color": "#93c5fd", "font_size": 17}},
                ] if hydrogen_context and nitric_context else []),
            ],
        }
    if scenario == "titration":
        return {
            "id": "chemistry_figure_titration_scene",
            "description": "Titration setup with burette and endpoint",
            "voiceover": f"Visualize the titration setup, indicator transition, and endpoint interpretation for: {short}.",
            "duration_seconds": 38,
            "elements": [
                {"type": "Title", "content": "Chemistry Figure: Titration", "position": "[0, 3.2, 0]", "style": {"color": "#ffffff"}},
                {"type": "Paragraph", "content": f"Problem context: {short}", "position": "[0, 2.2, 0]", "style": {"color": "#d9e6ff"}},
                {"type": "Rectangle", "position": "[-1.8, 0.6, 0]", "style": {"width": 0.4, "height": 2.6, "fill_color": "#8ecae6", "fill_opacity": 0.55}},
                {"type": "Text", "content": "Burette", "position": "[-1.8, -1.0, 0]", "style": {"color": "#8ecae6"}},
                {"type": "Circle", "position": "[1.1, -0.7, 0]", "style": {"radius": 0.8, "fill_color": "#f4a261", "fill_opacity": 0.35}},
                {"type": "Text", "content": "Flask", "position": "[1.1, -1.9, 0]", "style": {"color": "#f4a261"}},
                {"type": "Text", "content": "Endpoint color change", "position": "[1.1, 0.8, 0]", "style": {"color": "#ffd166"}},
            ],
        }
    if scenario == "gas_law":
        return {
            "id": "chemistry_figure_gas_law_scene",
            "description": "Gas law state variables and process path",
            "voiceover": f"Use this state-variable diagram to connect pressure, volume, and temperature changes in: {short}.",
            "duration_seconds": 38,
            "elements": [
                {"type": "Title", "content": "Chemistry Figure: Gas Laws", "position": "[0, 3.2, 0]", "style": {"color": "#ffffff"}},
                {"type": "Paragraph", "content": f"Problem context: {short}", "position": "[0, 2.2, 0]", "style": {"color": "#d9e6ff"}},
                {"type": "Axes", "content": "P-V axes", "position": "[0, -0.3, 0]", "style": {"x_range": [0, 10, 1], "y_range": [0, 10, 1], "x_label": "V", "y_label": "P"}},
                {"type": "Graph", "content": "8/x", "position": "[0, -0.3, 0]", "style": {"x_range": [1, 9], "label": "isotherm"}},
                {"type": "Text", "content": "PV = nRT", "position": "[2.2, 1.5, 0]", "style": {"color": "#ffd166"}},
            ],
        }
    return {
        "id": "chemistry_figure_reaction_scene",
        "description": "Reaction setup with species and conditions",
        "voiceover": f"Show the chemistry setup visually with species, reaction direction, and measured conditions for: {short}.",
        "duration_seconds": 38,
        "elements": [
            {"type": "Title", "content": "Chemistry Figure", "position": "[0, 3.2, 0]", "style": {"color": "#ffffff"}},
            {"type": "Paragraph", "content": f"Problem context: {short}", "position": "[0, 2.2, 0]", "style": {"color": "#d9e6ff"}},
            {"type": "Rectangle", "position": "[-1.6, -0.1, 0]", "style": {"width": 2.2, "height": 2.6, "fill_color": "#1f77b4", "fill_opacity": 0.18}},
            {"type": "Text", "content": "Reactants", "position": "[-1.6, 1.2, 0]", "style": {"color": "#6ec1ff"}},
            {"type": "Arrow", "position": "[0.2, -0.05, 0]", "style": {"color": "#f1c40f", "stroke_width": 3}},
            {"type": "Text", "content": "k(T), catalyst", "position": "[0.65, 0.3, 0]", "style": {"color": "#f1c40f"}},
            {"type": "Rectangle", "position": "[2.1, -0.1, 0]", "style": {"width": 2.2, "height": 2.6, "fill_color": "#2ca02c", "fill_opacity": 0.18}},
            {"type": "Text", "content": "Products", "position": "[2.1, 1.2, 0]", "style": {"color": "#9be39b"}},
            {"type": "Text", "content": "Concentration / pH / Temp", "position": "[0, -2.4, 0]", "style": {"color": "#ffffff"}},
        ],
    }


def _build_economics_figure_scene(question: str, scenario: str = "market") -> Dict[str, Any]:
    short = " ".join((question or "economics problem").split())[:120]
    if scenario == "elasticity":
        return {
            "id": "economics_figure_elasticity_scene",
            "description": "Elasticity comparison with demand changes",
            "voiceover": f"Compare demand response under different elasticities for: {short}.",
            "duration_seconds": 38,
            "elements": [
                {"type": "Title", "content": "Economics Figure: Elasticity", "position": "[0, 3.2, 0]", "style": {"color": "#ffffff"}},
                {"type": "Paragraph", "content": f"Problem context: {short}", "position": "[0, 2.2, 0]", "style": {"color": "#d9e6ff"}},
                {"type": "Axes", "content": "price-quantity axes", "position": "[0, -0.3, 0]", "style": {"x_range": [0, 10, 1], "y_range": [0, 10, 1], "x_label": "Q", "y_label": "P"}},
                {"type": "Graph", "content": "9 - 1.2*x", "position": "[0, -0.3, 0]", "style": {"x_range": [0, 7], "label": "Elastic D"}},
                {"type": "Graph", "content": "8 - 0.4*x", "position": "[0, -0.3, 0]", "style": {"x_range": [0, 10], "label": "Inelastic D"}},
                {"type": "Text", "content": "|E_d| = %dQ / %dP", "position": "[1.7, 1.3, 0]", "style": {"color": "#f1c40f"}},
            ],
        }
    if scenario == "macro":
        return {
            "id": "economics_figure_macro_scene",
            "description": "Macro AD-AS shift interpretation",
            "voiceover": f"Use AD-AS shifts to interpret macro effects in: {short}.",
            "duration_seconds": 38,
            "elements": [
                {"type": "Title", "content": "Economics Figure: AD-AS", "position": "[0, 3.2, 0]", "style": {"color": "#ffffff"}},
                {"type": "Paragraph", "content": f"Problem context: {short}", "position": "[0, 2.2, 0]", "style": {"color": "#d9e6ff"}},
                {"type": "Axes", "content": "price-output axes", "position": "[0, -0.3, 0]", "style": {"x_range": [0, 10, 1], "y_range": [0, 10, 1], "x_label": "Y", "y_label": "P"}},
                {"type": "Graph", "content": "9 - 0.6*x", "position": "[0, -0.3, 0]", "style": {"x_range": [0, 10], "label": "AD"}},
                {"type": "Graph", "content": "2 + 0.5*x", "position": "[0, -0.3, 0]", "style": {"x_range": [0, 10], "label": "AS"}},
                {"type": "Arrow", "position": "[1.2, 1.7, 0]", "style": {"color": "#ff7f0e", "stroke_width": 3}},
                {"type": "Text", "content": "demand shock", "position": "[1.8, 1.95, 0]", "style": {"color": "#ff7f0e"}},
            ],
        }
    return {
        "id": "economics_figure_market_scene",
        "description": "Market graph with demand and supply",
        "voiceover": f"Use a market diagram to connect price and quantity relationships for: {short}.",
        "duration_seconds": 38,
        "elements": [
            {"type": "Title", "content": "Economics Figure", "position": "[0, 3.2, 0]", "style": {"color": "#ffffff"}},
            {"type": "Paragraph", "content": f"Problem context: {short}", "position": "[0, 2.2, 0]", "style": {"color": "#d9e6ff"}},
            {"type": "Axes", "content": "price-quantity axes", "position": "[0, -0.3, 0]", "style": {"x_range": [0, 10, 1], "y_range": [0, 10, 1], "x_label": "Q", "y_label": "P"}},
            {"type": "Graph", "content": "9 - 0.7*x", "position": "[0, -0.3, 0]", "style": {"x_range": [0, 10], "label": "Demand"}},
            {"type": "Graph", "content": "1 + 0.7*x", "position": "[0, -0.3, 0]", "style": {"x_range": [0, 10], "label": "Supply"}},
            {"type": "Circle", "position": "[0, 0.2, 0]", "style": {"radius": 0.15, "fill_color": "#f1c40f", "fill_opacity": 0.9}},
            {"type": "Text", "content": "Equilibrium", "position": "[0.85, 0.5, 0]", "style": {"color": "#f1c40f"}},
        ],
    }
