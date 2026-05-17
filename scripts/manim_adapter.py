import argparse
import concurrent.futures
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path
from typing import Dict, Any, List, Optional


# ══════════════════════════════════════════════════════════════════════════════
# PHIVERSITY SEMANTIC COLOR SYSTEM  — 10-Minute Edition
# Every distinct role in a Physics / Chemistry / Maths / Economics lesson
# has its own colour.  Dark background (#121212) is assumed throughout.
# ══════════════════════════════════════════════════════════════════════════════

COLORS: Dict[str, str] = {
    # ── Backgrounds ───────────────────────────────────────────────────────────
    "bg": "#121212",  # Charcoal Black  — main background
    "bg_navy": "#0B1C2D",  # Dark Navy       — alt background
    # ── Problem / Question ────────────────────────────────────────────────────
    "problem_title": "#FFD700",  # Gold            — scene title / question heading
    "question_action": "#FF6B35",  # Orange-Red      — "find", "calculate", "?", "solve"
    # ── Given / Known Data ────────────────────────────────────────────────────
    "given_label": "#78D5E3",  # Sky Cyan        — "Given:", "Known:"
    "given_value": "#4FC3F7",  # Light Blue      — known quantities  m = 5 kg
    "given_value_alt": "#64B5F6",  # Sky Blue        — alternating given value
    # ── Variables & Constants ─────────────────────────────────────────────────
    "variable": "#C792EA",  # Lavender        — algebraic variables (x, v, F …)
    "constant": "#FF9F43",  # Warm Orange     — physical constants (g, c, π, e)
    # ── Formulas / Laws / Theorems ────────────────────────────────────────────
    "formula_title": "#BB86FC",  # Purple          — law name: "Newton's 2nd Law"
    "formula_body": "#E040FB",  # Bright Magenta  — the formula itself  F = ma
    "formula_alt": "#B39DDB",  # Soft Violet     — secondary formula line
    "derivation_step": "#B39DDB",  # Soft Violet     — derivation line alternates
    # ── Step Labels ───────────────────────────────────────────────────────────
    "step_label": "#82AAFF",  # Periwinkle      — "Step 1:"
    "step_label_2": "#89DDFF",  # Ice Blue        — "Step 2:"
    "step_label_3": "#7EC8E3",  # Cornflower      — "Step 3+"
    "step_label_4": "#A5C8E1",  # Steel Blue      — "Step 4"
    "step_label_5": "#80CBC4",  # Teal            — "Step 5+"
    # ── Algebraic Work ────────────────────────────────────────────────────────
    "algebra": "#FFFFFF",  # White           — general algebra lines
    "algebra_alt": "#E0E0E0",  # Off-White       — alternating algebra line
    "substitution": "#FFE082",  # Pale Yellow     — substituting known values in
    "intermediate": "#A5D6A7",  # Soft Green      — intermediate results
    # ── Final Answer ──────────────────────────────────────────────────────────
    "answer_label": "#69F0AE",  # Mint Green      — "Therefore:", "Answer:"
    "answer_value": "#00FF6A",  # Bright Green    — the final numerical answer
    "answer_alt": "#00E676",  # Emerald         — alternate answer accent
    # ── Units ─────────────────────────────────────────────────────────────────
    "unit": "#90A4AE",  # Slate Gray      — m/s, kg, N, J (non-distracting)
    # ── Summary ───────────────────────────────────────────────────────────────
    "summary_bullet": "#B2EBF2",  # Ice Blue        — summary takeaway points
    "summary_title": "#80DEEA",  # Aqua            — "Summary" heading
    # ── New 10-min roles ──────────────────────────────────────────────────────
    "mistake_warning": "#FF5252",  # Red             — "Common mistake:", "Watch out:"
    "real_world": "#FFD740",  # Amber           — real-world application text
    "history_note": "#80DEEA",  # Aqua            — historical context
    "practice_q": "#C792EA",  # Lavender        — practice problem text
    # ── Diagrams / Shapes ─────────────────────────────────────────────────────
    "shape_primary": "#448AFF",  # Bright Blue
    "shape_secondary": "#40C4FF",  # Cyan
    "shape_tertiary": "#18FFFF",  # Aqua
    "shape_fill": "#1A237E",  # Deep Indigo
    # ── Graphs & Axes ─────────────────────────────────────────────────────────
    "axis": "#CFD8DC",  # Light Gray
    "grid": "#37474F",  # Dark Gray
    # ── Highlights ────────────────────────────────────────────────────────────
    "highlight": "#FFD700",  # Gold
    "highlight_alt": "#FF4081",  # Pink
    # ── Scene Headers ─────────────────────────────────────────────────────────
    "header_problem": "#FFD700",
    "header_given": "#4FC3F7",
    "header_formula": "#BB86FC",
    "header_step": "#82AAFF",
    "header_answer": "#00FF6A",
    "header_summary": "#80DEEA",
    "header_mistake": "#FF5252",
    "header_realworld": "#FFD740",
    "header_history": "#80DEEA",
    "header_practice": "#C792EA",
    "header_default": "#ECEFF1",
}

# Graph curve cycling palette — each curve on the same axes gets a unique colour
CURVE_COLORS: List[str] = [
    "#FF5252",  # Red
    "#40C4FF",  # Cyan
    "#FFD740",  # Amber
    "#69F0AE",  # Mint
    "#FF4081",  # Pink
    "#B2FF59",  # Lime
    "#EA80FC",  # Light Purple
    "#FF6D00",  # Deep Orange
]

# Shape fill colours — cycle for multiple shapes in one scene
SHAPE_FILL_COLORS: List[str] = [
    "#448AFF",  # Blue
    "#FF5252",  # Red
    "#FFD740",  # Amber
    "#69F0AE",  # Mint
    "#E040FB",  # Magenta
    "#40C4FF",  # Cyan
]

VIBRANT_3D_COLORS: Dict[str, Dict[str, str]] = {
    "coin": {
        "gold": "#FFD700",
        "silver": "#C0C0C0",
        "edge": "#B8860B",
        "highlight": "#FFF8DC",
    },
    "tire": {
        "rubber": "#1a1a1a",
        "tread": "#2d2d2d",
        "rim": "#B8860B",
        "glow": "#FF4500",
    },
    "car": {
        "body": "#4169E1",
        "window": "#87CEEB",
        "headlight": "#FFD700",
        "taillight": "#FF0000",
        "wheel": "#1a1a1a",
    },
    "road": {
        "asphalt": "#3d3d3d",
        "line": "#FFFFFF",
        "marking": "#FFD700",
        "edge": "#FF6B35",
        "texture": "#4a4a4a",
    },
    "heat": {
        "low": "#FF6B35",
        "medium": "#FF4500",
        "high": "#FF0000",
        "glow": "#FFA500",
    },
    "force": {
        "normal": "#00FF7F",
        "weight": "#FF4500",
        "friction": "#9400D3",
        "applied": "#00BFFF",
    },
}

_SMART_ENV_THEMES: Dict[str, Dict[str, str]] = {
    "icy": {
        "name": "Icy",
        "car_body": "#8ecae6",
        "window": "#caf0f8",
        "wheel": "#1d3557",
        "road": "#d9edff",
        "accent": "#7bdff2",
        "text": "#ffffff",
        "sky": "#e0f4ff",
    },
    "wet": {
        "name": "Wet",
        "car_body": "#1d4ed8",
        "window": "#93c5fd",
        "wheel": "#0f172a",
        "road": "#475569",
        "accent": "#60a5fa",
        "text": "#ffffff",
        "sky": "#1e293b",
    },
    "night": {
        "name": "Night",
        "car_body": "#7c3aed",
        "window": "#c4b5fd",
        "wheel": "#111827",
        "road": "#1f2937",
        "accent": "#fde047",
        "text": "#f8fafc",
        "sky": "#0a0a1a",
    },
    "rainy": {
        "name": "Rainy",
        "car_body": "#0ea5e9",
        "window": "#7dd3fc",
        "wheel": "#164e63",
        "road": "#334155",
        "accent": "#38bdf8",
        "text": "#ffffff",
        "sky": "#1e3a5f",
    },
    "foggy": {
        "name": "Foggy",
        "car_body": "#64748b",
        "window": "#cbd5e1",
        "wheel": "#334155",
        "road": "#475569",
        "accent": "#94a3b8",
        "text": "#1e293b",
        "sky": "#94a3b8",
    },
    "sunset": {
        "name": "Sunset",
        "car_body": "#f97316",
        "window": "#fdba74",
        "wheel": "#7c2d12",
        "road": "#7f1d1d",
        "accent": "#fbbf24",
        "text": "#ffffff",
        "sky": "#7c2d12",
    },
}

_SMART_DIFFICULTY_THEMES: Dict[str, Dict[str, str]] = {
    "easy": {
        "name": "Easy",
        "car_body": "#10b981",
        "window": "#a7f3d0",
        "wheel": "#1f2937",
        "road": "#737373",
        "accent": "#34d399",
        "text": "#ffffff",
    },
    "medium": {
        "name": "Medium",
        "car_body": "#f59e0b",
        "window": "#fde68a",
        "wheel": "#1f2937",
        "road": "#737373",
        "accent": "#fbbf24",
        "text": "#ffffff",
    },
    "hard": {
        "name": "Hard",
        "car_body": "#ef4444",
        "window": "#fecaca",
        "wheel": "#1f2937",
        "road": "#6b7280",
        "accent": "#fb7185",
        "text": "#ffffff",
    },
}


def _detect_environment(question: str) -> Optional[str]:
    q = (question or "").lower()
    if any(token in q for token in ("icy", "ice", "snow", "frozen", "cold winter")):
        return "icy"
    if any(token in q for token in ("wet", "rain", "rainy", "drizzle", "puddle")):
        return "wet"
    if any(token in q for token in ("night", "dark", "midnight", "evening")):
        return "night"
    if any(token in q for token in ("rainy", "storm", "thunderstorm")):
        return "rainy"
    if any(token in q for token in ("fog", "foggy", "mist", "misty")):
        return "foggy"
    if any(
        token in q for token in ("sunset", "sunrise", "dusk", "dawn", "golden hour")
    ):
        return "sunset"
    return None


def _detect_difficulty(question: str) -> Optional[str]:
    q = (question or "").lower()
    if any(
        token in q
        for token in ("hard", "difficult", "advanced", "challenge", "complex")
    ):
        return "hard"
    if any(token in q for token in ("medium", "intermediate", "moderate")):
        return "medium"
    if any(token in q for token in ("easy", "simple", "beginner", "basic", "intro")):
        return "easy"
    return None


def _get_smart_color(theme_type: str, color_key: str, question: str) -> str:
    env = _detect_environment(question)
    if env and theme_type in ("car", "road", "tire"):
        theme = _SMART_ENV_THEMES.get(env, {})
        return theme.get(color_key, "")
    diff = _detect_difficulty(question)
    if diff and theme_type in ("car", "road"):
        theme = _SMART_DIFFICULTY_THEMES.get(diff, {})
        return theme.get(color_key, "")
    return ""


PHYSICS_MOTION_COLORS: Dict[str, str] = {
    "velocity": "#00CED1",
    "acceleration": "#FF6347",
    "force": "#FFD700",
    "friction": "#9932CC",
    "normal": "#32CD32",
    "gravity": "#DC143C",
    "tension": "#FF8C00",
    "drag": "#4169E1",
}

# Backward-compat alias
EDUCATION_COLORS: Dict[str, str] = {
    "background": COLORS["bg"],
    "background_alt": COLORS["bg_navy"],
    "question": COLORS["problem_title"],
    "question_alt": COLORS["question_action"],
    "value": COLORS["given_value"],
    "value_alt": COLORS["given_value_alt"],
    "formula": COLORS["formula_title"],
    "formula_alt": COLORS["formula_alt"],
    "step": COLORS["algebra"],
    "step_alt": COLORS["intermediate"],
    "answer": COLORS["answer_value"],
    "answer_alt": COLORS["answer_label"],
    "unit": COLORS["unit"],
    "accent_red": "#FF5252",
    "accent_green": COLORS["intermediate"],
    "accent_blue": COLORS["shape_primary"],
    "accent_orange": COLORS["constant"],
}

# Default seconds per scene when no explicit duration is provided.
# For 10-min videos each scene should hold for ~45 s.
DEFAULT_SCENE_WAIT: float = 45.0

# ─── Position helpers ────────────────────────────────────────────────────────

POSITION_MAP: Dict[str, str] = {
    "center": "ORIGIN",
    "top": "UP",
    "bottom": "DOWN",
    "left": "LEFT",
    "right": "RIGHT",
    "top-left": "UP+LEFT",
    "top-right": "UP+RIGHT",
    "bottom-left": "DOWN+LEFT",
    "bottom-right": "DOWN+RIGHT",
}

# ─── Element type buckets ────────────────────────────────────────────────────
_VISUAL_TYPES = frozenset(
    {
        "axes",
        "graph",
        "vectorfield",
        "streamlines",
        "parametric3d",
        "arrow",
        "vector",
    }
)

_VISUAL_3D_TYPES = frozenset(
    {
        "sphere3d",
        "cylinder3d",
        "box3d",
        "surface3d",
        "coin3d",
        "tire3d",
        "car3d",
        "road3d",
        "cone3d",
        "torus3d",
        "arrow3d",
    }
)

_PHYSICS_ANIMATION_TYPES = frozenset(
    {
        "car_moving",
        "friction_heat",
        "force_arrow",
        "motion_trail",
        "particle_system",
        "growth_chart",
    }
)
_SHAPE_TYPES = frozenset(
    {
        "circle",
        "annulus",
        "rectangle",
        "polygon",
        "ellipse",
    }
)
_TEXT_TYPES = frozenset(
    {
        "text",
        "mathtex",
        "latex",
        "",
    }
)


# ══════════════════════════════════════════════════════════════════════════════
# VALIDATION — warn early if the JSON plan is too short for a 10-min video
# ══════════════════════════════════════════════════════════════════════════════


def validate_duration(data: Dict[str, Any]) -> None:
    """Print warnings when the generated plan looks shorter than 10 minutes."""
    scenes = data.get("animation_plan", {}).get("scenes", [])

    # Count voiceover words across all scenes (exclude injected intro)
    total_words = sum(
        len((sc.get("voiceover") or "").split())
        for sc in scenes
        if sc.get("id") != "intro"
    )
    estimated_minutes = total_words / 130.0  # 130 wpm natural teaching pace

    # Sum per-scene duration_seconds if present
    total_scene_seconds = sum(
        float(sc.get("duration_seconds") or DEFAULT_SCENE_WAIT) for sc in scenes
    )

    # Read schema-level fields
    ap = data.get("animation_plan", {})
    schema_scenes = ap.get("total_scenes", len(scenes))
    schema_duration = ap.get("estimated_duration_seconds", 0)
    schema_minutes = data.get("solution", {}).get("duration_estimate_minutes", 0)

    print("-" * 60)
    print("[phiversity] Pre-render duration validation")
    print(f"  Scenes in JSON  : {len(scenes)}  (schema says {schema_scenes}, min 14)")
    print(f"  Voiceover words : {total_words}  (min 1 300)")
    print(
        f"  Estimated length: {estimated_minutes:.1f} min  (schema says {schema_minutes}, min 10.0)"
    )
    print(
        f"  Scene total     : {total_scene_seconds:.0f} s  (schema says {schema_duration}, min 600 s)"
    )

    if len(scenes) < 14:
        print(f"  WARNING: only {len(scenes)} scenes -- below 14-scene minimum")
    if total_words < 1300:
        print(
            f"  WARNING: only {total_words} voiceover words -- below 1 300-word minimum"
        )
    if estimated_minutes < 10.0:
        print(
            f"  WARNING: estimated {estimated_minutes:.1f} min -- below 10-minute minimum"
        )
    if total_scene_seconds < 600:
        print(
            f"  WARNING: scene total {total_scene_seconds:.0f} s -- below 600 s minimum"
        )
    print("-" * 60)


# ══════════════════════════════════════════════════════════════════════════════
# COLOR HELPERS
# ══════════════════════════════════════════════════════════════════════════════


def _q(c: str) -> str:
    """Quote a hex colour string for embedding in generated Python code."""
    return f"'{c}'" if c.startswith("#") else c


def _scene_header_color(scene_id: str, description: str) -> str:
    """Return a quoted hex colour for a scene's header based on scene type."""
    key = (scene_id + " " + description).lower()

    # 10-min new scene types — check first (more specific)
    if any(k in key for k in ("mistake", "error", "watch", "common", "wrong")):
        return _q(COLORS["header_mistake"])
    if any(
        k in key
        for k in (
            "real_world",
            "application",
            "where",
            "industry",
            "lab_note",
            "laboratory",
        )
    ):
        return _q(COLORS["header_realworld"])
    if any(
        k in key
        for k in ("hook", "motivation", "why this", "why does", "wonder", "imagine")
    ):
        return _q(COLORS["header_problem"])
    if any(
        k in key
        for k in (
            "background",
            "history",
            "context",
            "origin",
            "derivation",
            "proof",
            "justif",
            "where the",
            "molecular",
            "stoich",
            "thermo",
            "geometric",
            "connection",
            "edge_case",
            "special_case",
            "market",
            "elasticity",
            "policy",
            "data_context",
        )
    ):
        return _q(COLORS["header_history"])
    if any(k in key for k in ("practice", "exercise", "try", "challenge")):
        return _q(COLORS["header_practice"])
    if any(k in key for k in ("second_example", "variation", "try this")):
        return _q(COLORS["header_answer"])
    if any(k in key for k in ("unit", "dimension", "analysis", "check")):
        return _q(COLORS["header_given"])
    if any(
        k in key
        for k in (
            "force_diagram",
            "free_body",
            "energy_diagram",
            "physics_graph",
            "supply_demand",
        )
    ):
        return _q(COLORS["header_formula"])

    # Original scene types
    if any(k in key for k in ("problem", "question", "intro")):
        return _q(COLORS["header_problem"])
    if any(k in key for k in ("given", "known", "data")):
        return _q(COLORS["header_given"])
    if any(k in key for k in ("formula", "law", "theorem", "concept", "principle")):
        return _q(COLORS["header_formula"])
    if any(k in key for k in ("step", "solving", "calculation", "substitute")):
        m = re.search(r"(\d+)", key)
        n = int(m.group(1)) if m else 1
        shades = [
            COLORS["step_label"],
            COLORS["step_label_2"],
            COLORS["step_label_3"],
            COLORS["step_label_4"],
            COLORS["step_label_5"],
        ]
        return _q(shades[(n - 1) % len(shades)])
    if any(k in key for k in ("answer", "result", "solution", "final", "therefore")):
        return _q(COLORS["header_answer"])
    if any(k in key for k in ("summary", "recap", "takeaway", "conclusion")):
        return _q(COLORS["header_summary"])

    return _q(COLORS["header_default"])


def _color_expr(style: Optional[Dict[str, Any]]) -> Optional[str]:
    """Extract an explicit colour from a style dict, return quoted string or None."""
    if not style or not isinstance(style, dict):
        return None
    color = style.get("color")
    if not color:
        return None
    c = str(color)
    return _q(c) if c.startswith("#") else c.upper()


def _get_default_color(
    etype: str,
    content: str,
    index: int,
    scene_id: str = "",
    scene_desc: str = "",
) -> str:
    """Resolve display colour using semantic role detection.

    Priority:
      1. Element type  (shapes/graphs/highlights always win)
      2. Scene context (scene_id + description tell us the role of the scene)
      3. Content keywords
      4. Positional fallback
    """
    cl = (content or "").lower()
    scene_key = (scene_id + " " + scene_desc).lower()

    # ── 1. Type-based (always definitive) ────────────────────────────────────
    if etype == "highlight":
        return _q(COLORS["highlight"] if index % 2 == 0 else COLORS["highlight_alt"])
    if etype in ("circle", "ellipse"):
        return _q(SHAPE_FILL_COLORS[index % len(SHAPE_FILL_COLORS)])
    if etype == "annulus":
        return _q(SHAPE_FILL_COLORS[(index + 2) % len(SHAPE_FILL_COLORS)])
    if etype == "rectangle":
        return _q(SHAPE_FILL_COLORS[(index + 1) % len(SHAPE_FILL_COLORS)])
    if etype == "polygon":
        return _q(SHAPE_FILL_COLORS[(index + 3) % len(SHAPE_FILL_COLORS)])
    if etype == "axes":
        return _q(COLORS["axis"])
    if etype == "graph":
        return _q(CURVE_COLORS[index % len(CURVE_COLORS)])
    if etype in ("vectorfield", "streamlines"):
        return _q(COLORS["shape_secondary"])
    if etype == "parametric3d":
        return _q(CURVE_COLORS[(index + 1) % len(CURVE_COLORS)])
    if etype in ("arrow", "vector"):
        return _q(COLORS["constant"])

    # ── 2. Scene-context shortcuts (10-min new scene types) ──────────────────

    # Hook
    if any(k in scene_key for k in ("hook", "motivation", "why this", "why does")):
        if index == 1:
            return _q(COLORS["problem_title"])
        return _q(COLORS["real_world"] if index % 2 == 0 else COLORS["history_note"])

    # Background / history / derivation / proof
    if any(
        k in scene_key
        for k in (
            "background",
            "history",
            "context",
            "origin",
            "derivation",
            "proof",
            "justif",
            "where the formula",
        )
    ):
        if index == 1:
            return _q(COLORS["history_note"])
        return _q(COLORS["formula_title"] if index % 2 == 0 else COLORS["formula_alt"])

    # Unit / dimensional analysis
    if any(
        k in scene_key for k in ("unit", "dimension", "unit_analysis", "dimensional")
    ):
        if index == 1:
            return _q(COLORS["given_label"])
        return _q(COLORS["substitution"] if index % 2 == 0 else COLORS["intermediate"])

    # Common mistakes
    if any(k in scene_key for k in ("mistake", "error", "common", "watch", "wrong")):
        return _q(COLORS["mistake_warning"])

    # Real-world application / lab note
    if any(
        k in scene_key
        for k in (
            "real_world",
            "application",
            "where",
            "industry",
            "lab_note",
            "laboratory",
        )
    ):
        if index == 1:
            return _q(COLORS["real_world"])
        return _q(COLORS["constant"] if index % 2 == 0 else COLORS["history_note"])

    # Second example / variation
    if any(k in scene_key for k in ("second_example", "variation", "try this")):
        if index == 1:
            return _q(COLORS["problem_title"])
        return _q(COLORS["substitution"] if index % 2 == 0 else COLORS["intermediate"])

    # Practice problems
    if any(k in scene_key for k in ("practice", "exercise", "try", "challenge")):
        if index == 1:
            return _q(COLORS["practice_q"])
        return _q(COLORS["practice_q"] if index % 2 == 0 else COLORS["formula_alt"])

    # Summary
    if any(k in scene_key for k in ("summary", "recap", "takeaway", "conclusion")):
        return _q(
            COLORS["summary_bullet"] if index % 2 == 0 else COLORS["summary_title"]
        )

    # Physics extensions
    if any(k in scene_key for k in ("force_diagram", "free_body", "energy_diagram")):
        return _q(
            COLORS["shape_primary"] if index % 2 == 0 else COLORS["shape_secondary"]
        )
    if any(k in scene_key for k in ("physics_graph", "motion_graph", "wave_graph")):
        return _q(CURVE_COLORS[index % len(CURVE_COLORS)])
    if any(
        k in scene_key for k in ("special_case", "special case", "limit", "extreme")
    ):
        return _q(COLORS["constant"] if index % 2 == 0 else COLORS["formula_alt"])

    # Chemistry extensions
    if any(
        k in scene_key
        for k in ("molecular", "stoich", "thermo", "reaction", "equilibrium")
    ):
        if index == 1:
            return _q(COLORS["formula_title"])
        return _q(COLORS["formula_body"] if index % 2 == 0 else COLORS["formula_alt"])
    if any(k in scene_key for k in ("lab_note", "safety")):
        return _q(COLORS["real_world"])

    # Maths extensions
    if any(k in scene_key for k in ("proof", "theorem", "justif")):
        return _q(
            COLORS["formula_body"] if index % 2 == 0 else COLORS["derivation_step"]
        )
    if any(k in scene_key for k in ("geometric", "geometric_view")):
        return _q(CURVE_COLORS[index % len(CURVE_COLORS)])
    if any(k in scene_key for k in ("edge_case", "domain", "range", "undefined")):
        return _q(COLORS["constant"])
    if any(k in scene_key for k in ("connection", "related", "branch")):
        return _q(COLORS["history_note"])

    # Economics extensions
    if any(
        k in scene_key
        for k in ("market", "supply", "demand", "equilibrium", "supply_demand")
    ):
        if index == 1:
            return _q(COLORS["real_world"])
        return _q(CURVE_COLORS[index % len(CURVE_COLORS)])
    if any(k in scene_key for k in ("elasticity", "multiplier", "inelastic")):
        return _q(
            COLORS["given_value"] if index % 2 == 0 else COLORS["given_value_alt"]
        )
    if any(k in scene_key for k in ("policy", "government", "fiscal", "monetary")):
        return _q(COLORS["real_world"] if index % 2 == 0 else COLORS["constant"])
    if any(k in scene_key for k in ("data", "empirical", "statistic", "gdp")):
        return _q(COLORS["history_note"])

    # ── 2b. Original scene-context shortcuts ─────────────────────────────────
    if any(k in scene_key for k in ("given", "known", "data")):
        if any(kw in cl for kw in ("given:", "known:", "given", "known")):
            return _q(COLORS["given_label"])
        return _q(
            COLORS["given_value"] if index % 2 == 0 else COLORS["given_value_alt"]
        )

    if any(
        k in scene_key for k in ("formula", "law", "theorem", "concept", "principle")
    ):
        if index == 1:
            return _q(COLORS["formula_title"])
        return _q(COLORS["formula_body"] if index % 2 == 0 else COLORS["formula_alt"])

    if any(k in scene_key for k in ("answer", "result", "final", "solution")):
        if any(kw in cl for kw in ("therefore", "answer:", "hence", "so,")):
            return _q(COLORS["answer_label"])
        return _q(COLORS["answer_value"] if index % 2 == 0 else COLORS["answer_alt"])

    if re.search(r"step[\s_]*\d", scene_key):
        if index == 1:
            m2 = re.search(r"step[\s_]*(\d+)", scene_key)
            n = int(m2.group(1)) if m2 else index
            shades = [
                COLORS["step_label"],
                COLORS["step_label_2"],
                COLORS["step_label_3"],
                COLORS["step_label_4"],
                COLORS["step_label_5"],
            ]
            return _q(shades[(n - 1) % len(shades)])
        if re.search(r"=\s*[\-\d\(]", cl):
            return _q(COLORS["substitution"])
        return _q(COLORS["algebra"] if index % 2 == 0 else COLORS["algebra_alt"])

    # ── 3. Fine-grained content-keyword matching ──────────────────────────────
    if any(
        kw in cl for kw in ["find ", "solve", "calculate", "determine", "what is", "?"]
    ):
        return _q(COLORS["question_action"])
    if any(
        kw in cl for kw in ["problem", "question", "given that", "a block", "an object"]
    ):
        return _q(COLORS["problem_title"])
    if any(kw in cl for kw in ["given:", "known:", "given", "known"]):
        return _q(COLORS["given_label"])
    if re.search(r"[a-z_]+\s*=\s*[\d\.\-]", cl):
        return _q(
            COLORS["given_value"] if index % 2 == 0 else COLORS["given_value_alt"]
        )
    if any(
        kw in cl
        for kw in [
            "\\pi",
            "pi",
            "\\hbar",
            "= 9.8",
            "= 9.81",
            "= 6.67",
            "planck",
            "boltzmann",
            "avogadro",
        ]
    ):
        return _q(COLORS["constant"])
    if any(
        kw in cl
        for kw in [
            "law",
            "theorem",
            "principle",
            "formula",
            "newton",
            "ohm",
            "faraday",
            "hooke",
            "conservation",
        ]
    ):
        return _q(COLORS["formula_title"])
    if any(
        kw in cl for kw in ["\\frac", "\\vec", "\\int", "\\sum", "\\sqrt", "\\Delta"]
    ):
        return _q(COLORS["formula_body"] if index % 2 == 0 else COLORS["formula_alt"])
    if re.match(r"^step\s*\d", cl):
        step_match = re.search(r"\d+", cl)
        n = int(step_match.group()) if step_match else 1
        shd = [
            COLORS["step_label"],
            COLORS["step_label_2"],
            COLORS["step_label_3"],
            COLORS["step_label_4"],
            COLORS["step_label_5"],
        ]
        return _q(shd[(n - 1) % len(shd)])
    if re.search(r"=\s*[\(\-\d]", cl) and re.search(r"\d", cl):
        return _q(COLORS["substitution"])
    if "=" in cl and re.search(r"\d", cl):
        return _q(COLORS["intermediate"])
    if any(kw in cl for kw in ["therefore", "answer:", "hence,", "so,"]):
        return _q(COLORS["answer_label"])
    if any(kw in cl for kw in ["answer", "result", "solution", "final"]):
        return _q(COLORS["answer_value"])
    if any(kw in cl for kw in ["\\text{ m", "\\text{ kg", "m/s", "kg", " hz"]):
        return _q(COLORS["unit"])
    if any(
        kw in cl for kw in ["in summary", "key point", "remember", "note that", "recap"]
    ):
        return _q(COLORS["summary_bullet"])
    # Mistake / warning keywords
    if any(
        kw in cl
        for kw in [
            "mistake",
            "wrong",
            "incorrect",
            "error",
            "watch out",
            "do not",
            "don't",
            "avoid",
            "never",
            "common error",
        ]
    ):
        return _q(COLORS["mistake_warning"])

    # ── 4. Positional fallback ────────────────────────────────────────────────
    fallback = [
        COLORS["algebra"],
        COLORS["algebra_alt"],
        COLORS["intermediate"],
        COLORS["substitution"],
    ]
    return _q(fallback[index % len(fallback)])


# ══════════════════════════════════════════════════════════════════════════════
# SAFE STRING HELPER
# ══════════════════════════════════════════════════════════════════════════════


def _safe_str(s: str) -> str:
    """Escape backslashes and single quotes for embedding in Python string literals.

    This ensures generated code has properly escaped strings that won't cause
    SyntaxWarning or SyntaxError when parsed.
    """
    # First escape backslashes, then single quotes
    cleaned = s.replace("\\", "\\\\")  # Escape backslashes first
    cleaned = cleaned.replace("'", "\\'")  # Then escape single quotes
    cleaned = cleaned.replace("\n", "\\n")  # Escape newlines
    cleaned = cleaned.replace("\r", "\\r")  # Escape carriage returns
    cleaned = cleaned.replace("\t", "\\t")  # Escape tabs
    return cleaned


def _safe_comment(s: str) -> str:
    """Sanitize a string for use in Python comments - replaces newlines with spaces."""
    return s.replace("\n", " ").replace("\r", " ").replace("'", " ")[:80]


# ══════════════════════════════════════════════════════════════════════════════
# POSITION HELPERS
# ══════════════════════════════════════════════════════════════════════════════


def _pos_expr(p: Optional[str]) -> str:
    if not p:
        return "ORIGIN"
    p_str = str(p).strip()
    if p_str.startswith("[") and p_str.endswith("]"):
        inner = p_str.strip("[]")
        coords = inner.split(",")
        if len(coords) >= 2:
            try:
                x = float(coords[0].strip())
                y = float(coords[1].strip())
                return f"{x}*RIGHT + {y}*UP"
            except ValueError:
                pass
    return POSITION_MAP.get(p_str.lower(), "ORIGIN")


def _assign_positions(elements: List[Dict[str, Any]]) -> List[str]:
    """Compute non-overlapping positions for every element in a scene.

    Layout modes
    ────────────
    TEXT-ONLY        → vertical centre column
    MIXED            → visuals/shapes on LEFT, text stacked on RIGHT
    VISUAL/SHAPE-ONLY → full-canvas grid
    """
    n = len(elements)
    temp: List[Optional[str]] = [None]
    result: List[Optional[str]] = temp * n

    def _etype(i: int) -> str:
        try:
            return str((elements[i] or {}).get("type") or "").lower()
        except Exception:
            return ""

    def _is_text_type(t: str) -> bool:
        # Unknown types default to text (safer than placing in the media lane).
        if t in _TEXT_TYPES:
            return True
        if t in _VISUAL_TYPES or t in _SHAPE_TYPES or t == "highlight":
            return False
        return True

    def _is_media_type(t: str) -> bool:
        return t in _VISUAL_TYPES or t in _SHAPE_TYPES

    def _est_lines(i: int) -> int:
        t = _etype(i)
        if t in ("mathtex", "latex"):
            return 1
        try:
            raw = str((elements[i] or {}).get("content") or "")
        except Exception:
            return 1
        if not raw.strip():
            return 1
        if "\n" in raw:
            return max(1, raw.count("\n") + 1)
        # Mirrors _safe_str wrap width=50 (rough estimate).
        return max(1, (len(raw) + 49) // 50)

    # Honour explicit positions
    for i, el in enumerate(elements):
        pos_input = el.get("position")
        if pos_input:
            result[i] = _pos_expr(str(pos_input))

    # Axes + Graph are drawn together (graphs use the global `axes` object). Treat as one slot.
    axes_idx: Optional[int] = None
    graph_indices: List[int] = []
    for i in range(n):
        t = _etype(i)
        if t == "axes" and axes_idx is None:
            axes_idx = i
        elif t == "graph":
            graph_indices.append(i)

    if axes_idx is not None and graph_indices:
        # If either axes or graph has an explicit position, force both to share it.
        shared = result[axes_idx]
        if shared is None:
            for gi in graph_indices:
                if result[gi] is not None:
                    shared = result[gi]
                    break
        if shared is not None:
            result[axes_idx] = shared
            for gi in graph_indices:
                result[gi] = shared

    # Decide layout mode based on the full scene (not only un-positioned elements).
    scene_has_text = any(_is_text_type(_etype(i)) for i in range(n))
    scene_has_media = any(_is_media_type(_etype(i)) for i in range(n))

    # Bucket remaining elements
    text_indices: List[int] = []
    visual_indices: List[int] = []
    shape_indices: List[int] = []
    deferred_graph_indices: List[int] = []

    for i, el in enumerate(elements):
        if result[i] is not None:
            continue
        etype = str(el.get("type") or "").lower()
        if etype == "highlight":
            # SurroundingRectangle targets an existing object; don't consume layout slots.
            continue
        if axes_idx is not None and graph_indices and etype == "graph":
            # Graph uses the axes position; assign after axes has a position.
            deferred_graph_indices.append(i)
            continue
        if _is_text_type(etype):
            text_indices.append(i)
        elif etype in _VISUAL_TYPES:
            visual_indices.append(i)
        elif etype in _SHAPE_TYPES:
            shape_indices.append(i)
        else:
            text_indices.append(i)

    # Use scene-wide flags so explicitly positioned media still pushes auto-text into the text lane.
    has_visual = bool(scene_has_media)
    has_text = bool(scene_has_text)

    # Bigger vertical spacing to reduce overlaps with multi-line text.
    TEXT_Y_STEP = 1.55

    if has_text:
        if not has_visual:
            # TEXT-ONLY: centre column
            y = 2.6
            for i in text_indices:
                result[i] = f"0.0*RIGHT + {y:.2f}*UP"
                # Reserve extra space for wrapped text.
                y -= TEXT_Y_STEP + 0.45 * max(_est_lines(i) - 1, 0)
        else:
            # MIXED: text on right half
            y = 2.4
            for i in text_indices:
                result[i] = f"3.8*RIGHT + {y:.2f}*UP"
                y -= TEXT_Y_STEP + 0.45 * max(_est_lines(i) - 1, 0)

    media_indices = visual_indices + shape_indices
    num_media = len(media_indices)

    if num_media > 0:
        if has_text:
            if num_media == 1:
                MEDIA_POS = ["-3.8*RIGHT + 0.0*UP"]
            elif num_media == 2:
                # Stack media with extra separation (axes are tall).
                MEDIA_POS = ["-3.8*RIGHT + 2.1*UP", "-3.8*RIGHT + -2.1*UP"]
            elif num_media == 3:
                MEDIA_POS = [
                    "-3.8*RIGHT + 2.3*UP",
                    "-3.8*RIGHT + 0.0*UP",
                    "-3.8*RIGHT + -2.3*UP",
                ]
            else:
                MEDIA_POS = [
                    "-5.3*RIGHT + 2.1*UP",
                    "-2.3*RIGHT + 2.1*UP",
                    "-5.3*RIGHT + -2.1*UP",
                    "-2.3*RIGHT + -2.1*UP",
                    "-5.3*RIGHT + 0.0*UP",
                    "-2.3*RIGHT + 0.0*UP",
                ]
        else:
            if num_media == 1:
                MEDIA_POS = ["0*RIGHT + 0.0*UP"]
            elif num_media == 2:
                MEDIA_POS = ["-3.5*RIGHT + 0.0*UP", "3.5*RIGHT + 0.0*UP"]
            elif num_media == 3:
                MEDIA_POS = [
                    "0*RIGHT + 2.0*UP",
                    "-3.5*RIGHT + -1.5*UP",
                    "3.5*RIGHT + -1.5*UP",
                ]
            else:
                MEDIA_POS = [
                    "-3.5*RIGHT +  2.2*UP",
                    " 3.5*RIGHT +  2.2*UP",
                    "-3.5*RIGHT + -2.2*UP",
                    " 3.5*RIGHT + -2.2*UP",
                    " 0.0*RIGHT +  0.0*UP",
                ]

        for rank, i in enumerate(media_indices):
            result[i] = MEDIA_POS[rank % len(MEDIA_POS)]

    # If we have Axes+Graph, force Graph to share the final axes position.
    if axes_idx is not None and graph_indices and result[axes_idx] is not None:
        for gi in graph_indices + deferred_graph_indices:
            result[gi] = result[axes_idx]

    # Fallback
    FALLBACK = [
        " 0.0*RIGHT +  0.0*UP",
        " 2.5*RIGHT +  1.5*UP",
        "-2.5*RIGHT +  1.5*UP",
        " 2.5*RIGHT + -1.5*UP",
        "-2.5*RIGHT + -1.5*UP",
    ]
    fallback_idx = 0
    final_result: List[str] = []
    for i in range(n):
        if result[i] is None:
            idx = fallback_idx % len(FALLBACK)
            final_result.append(str(FALLBACK[idx]))
            fallback_idx += 1
        else:
            final_result.append(str(result[i]))

    # Collision resolution: estimate bounding boxes and shift overlapping items
    def _parse_vec(pos_str: str) -> tuple[float, float]:
        x, y = 0.0, 0.0
        for part in pos_str.replace("*", " ").split("+"):
            part = part.strip()
            if not part:
                continue
            if "RIGHT" in part:
                try:
                    x = float(part.split()[0])
                except ValueError:
                    x = 0.0
            elif "LEFT" in part:
                try:
                    x = -float(part.split()[0])
                except ValueError:
                    x = 0.0
            elif "UP" in part:
                try:
                    y = float(part.split()[0])
                except ValueError:
                    y = 0.0
            elif "DOWN" in part:
                try:
                    y = -float(part.split()[0])
                except ValueError:
                    y = 0.0
            elif "ORIGIN" in part:
                x, y = 0.0, 0.0
        return x, y

    parsed = [_parse_vec(p) for p in final_result]
    adjusted = list(parsed)
    used_boxes: list[tuple[float, float, float, float]] = []

    for i in range(n):
        etype = str(elements[i].get("type") or "").lower()
        content = str(elements[i].get("content") or "")
        est_w = 3.0 if etype in ("axes", "graph") else (2.5 if etype == "mathtex" else 1.0 + len(content) * 0.10)
        est_h = 2.0 if etype in ("axes", "graph") else 1.2
        bx, by = adjusted[i]
        box = (bx - est_w / 2, by - est_h / 2, bx + est_w / 2, by + est_h / 2)
        for j, ob in enumerate(used_boxes):
            if box[0] < ob[2] and box[2] > ob[0] and box[1] < ob[3] and box[3] > ob[1]:
                shift_y = ob[3] - box[1] + 0.3
                adjusted[i] = (bx, by + shift_y)
                box = (bx - est_w / 2, by + shift_y - est_h / 2, bx + est_w / 2, by + shift_y + est_h / 2)
                break
        used_boxes.append(box)
        side = "UP" if adjusted[i][1] >= 0 else "DOWN"
        x_str = f"{adjusted[i][0]:.2f}*RIGHT" if adjusted[i][0] >= 0 else f"{abs(adjusted[i][0]):.2f}*LEFT"
        y_str = f"{adjusted[i][1]:.2f}*UP" if adjusted[i][1] >= 0 else f"{abs(adjusted[i][1]):.2f}*DOWN"
        final_result[i] = f"{x_str} + {y_str}"

    return final_result


# ══════════════════════════════════════════════════════════════════════════════
# ANIMATION HELPERS
# ══════════════════════════════════════════════════════════════════════════════


def _anim_in_default(etype: str) -> str:
    return (
        "Create"
        if etype
        in {
            "axes",
            "graph",
            "vectorfield",
            "streamlines",
            "parametric3d",
            "highlight",
        }
        else "Write"
    )


def _anim_out_default(etype: str) -> str:
    return "FadeOut" if etype in {"text", "mathtex", "highlight"} else "Uncreate"


def _normalize_anim(name: Optional[str], default: str) -> str:
    if not name:
        return default
    mapping = {
        "write": "Write",
        "fadein": "FadeIn",
        "create": "Create",
        "fadeout": "FadeOut",
        "uncreate": "Uncreate",
        "growfromcenter": "GrowFromCenter",
    }
    return mapping.get(name.strip().lower(), default)


def _rate_func(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    mapping = {
        "linear": "rf.linear",
        "smooth": "rf.smooth",
        "rush_from": "rf.rush_from",
        "rush_into": "rf.rush_into",
        "there_and_back": "rf.there_and_back",
        "ease_in_sine": "rf.ease_in_sine",
        "ease_out_sine": "rf.ease_out_sine",
    }
    return mapping.get(name.strip().lower())


def _resolve_scene_duration(
    sc: Dict[str, Any],
    scene_durations: Optional[List[float]],
    sidx: int,
) -> float:
    """Return the best available scene duration in seconds.

    Priority:
      1. Per-scene ``duration_seconds`` field from the JSON (new 10-min schema)
      2. CLI-supplied ``scene_durations`` list
      3. ``DEFAULT_SCENE_WAIT`` (45 s) — appropriate for 10-min videos
    """
    sc_dur = sc.get("duration_seconds")
    if sc_dur is not None:
        val = float(sc_dur)
        if val > 0:
            return val
    if scene_durations and len(scene_durations) >= sidx:
        val = float(scene_durations[sidx - 1])
        if val > 0:
            return val
    return DEFAULT_SCENE_WAIT


def _scene_zoom_flags(scene: Dict[str, Any]) -> Dict[str, bool]:
    elements = scene.get("elements", []) if isinstance(scene, dict) else []
    etypes = {
        str(el.get("type") or "").lower() for el in elements if isinstance(el, dict)
    }
    text_parts: List[str] = [
        str(scene.get("description") or ""),
        str(scene.get("voiceover") or ""),
    ]
    for el in elements:
        if isinstance(el, dict):
            text_parts.append(str(el.get("content") or ""))
    blob = " ".join(text_parts).lower()

    has_tire_friction_focus = any(
        token in blob
        for token in (
            "friction",
            "rough surface",
            "tire",
            " tyre",
            "wheel",
            "mu =",
            "coefficient of friction",
        )
    )
    has_chem_bubble_focus = any(
        token in blob
        for token in (
            "bubble",
            "bubbles",
            "effervescence",
            "gas evolution",
            "gas release",
            "liquid drop",
        )
    )
    has_graph_focus = any(
        t in etypes
        for t in ("axes", "graph", "vectorfield", "streamlines", "parametric3d")
    ) or any(token in blob for token in ("graph", "chart", "plot", "curve", "figure"))
    has_equation_focus = (
        any(t in etypes for t in ("mathtex", "latex"))
        or any(token in blob for token in ("equation", "formula", "derive", "solve"))
        or ("=" in blob and any(ch.isalpha() for ch in blob))
    )

    has_3d_object_focus = any(
        token in blob
        for token in (
            "coin",
            "sphere",
            "tire",
            "wheel",
            "car",
            "cylinder",
            "cone",
            "torus",
            "3d",
        )
    )
    has_coin_focus = any(
        token in blob for token in ("coin", "gold", "silver", "penny", "nickel")
    )
    has_car_focus = any(
        token in blob for token in ("car", "vehicle", "driving", "automobile")
    )
    has_road_focus = any(
        token in blob for token in ("road", "surface", "highway", "asphalt", "pavement")
    )

    has_zoom_trigger = any(
        token in blob
        for token in (
            "zoom in",
            "let's zoom",
            "close up",
            "focus on",
            "look at",
            "examine",
            "inspect",
        )
    )

    has_motion_trigger = any(
        token in blob
        for token in (
            "moving",
            "driving",
            "motion",
            "speeding",
            "accelerating",
            "decelerating",
        )
    )

    has_heat_friction = any(
        token in blob
        for token in (
            "heat",
            "heating",
            "thermal",
            "warm",
            "temperature rise",
            "energy loss",
        )
    )

    has_growth_chart_focus = any(
        t in etypes for t in ("growth_chart",)
    ) or any(token in blob for token in ("growth chart", "growth", "trend", "increase over time", "data points"))

    has_particle_focus = any(
        t in etypes for t in ("particle_system", "particle")
    ) or any(token in blob for token in ("particle", "organic", "fluid", "flow", "swarm"))

    return {
        "tire": has_tire_friction_focus,
        "bubble": has_chem_bubble_focus,
        "graph": has_graph_focus,
        "equation": has_equation_focus,
        "3d_object": has_3d_object_focus,
        "coin": has_coin_focus,
        "car": has_car_focus,
        "road": has_road_focus,
        "zoom_trigger": has_zoom_trigger,
        "motion_trigger": has_motion_trigger,
        "heat_friction": has_heat_friction,
        "growth_chart": has_growth_chart_focus,
        "particle": has_particle_focus,
        "any": any(
            (
                has_tire_friction_focus,
                has_chem_bubble_focus,
                has_graph_focus,
                has_equation_focus,
                has_3d_object_focus,
                has_growth_chart_focus,
                has_particle_focus,
            )
        ),
    }

# ══════════════════════════════════════════════════════════════════════════════
# MAIN SCENE SCRIPT GENERATOR
# ══════════════════════════════════════════════════════════════════════════════


def generate_scene_script(
    data: Dict[str, Any],
    scene_durations: Optional[List[float]] = None,
    element_durations: Optional[List[List[float]]] = None,
) -> str:
    scenes: List[Dict[str, Any]] = data.get("animation_plan", {}).get("scenes", [])
    solution = data.get("solution", {})
    subject = (solution.get("subject") or "physics").lower()
    question = solution.get("question", "") or solution.get("problem", "")

    detected_env = _detect_environment(question)
    detected_difficulty = _detect_difficulty(question)

    active_theme = None
    if detected_env:
        active_theme = _SMART_ENV_THEMES.get(detected_env, {})
    elif detected_difficulty:
        active_theme = _SMART_DIFFICULTY_THEMES.get(detected_difficulty, {})

    needs_3d = any(
        str(el.get("type") or "").lower() == "parametric3d"
        for sc in scenes
        for el in sc.get("elements", [])
    )
    zoom_cues_present = any(
        _scene_zoom_flags(sc).get("any") for sc in scenes if isinstance(sc, dict)
    )
    scene_cls = (
        "ThreeDScene"
        if needs_3d
        else ("MovingCameraScene" if zoom_cues_present else "Scene")
    )

    # Inject intro scene only when external intro video is not being used.
    intro_enabled = os.getenv("INTRO_ENABLED", "true").lower() != "false"
    intro_video_path = Path(os.getenv("INTRO_VIDEO_PATH", "intro.mp4"))
    use_external_intro_video = intro_enabled and intro_video_path.exists()

    # Inject intro scene if not already present and no external intro video.
    scenes_with_intro = scenes.copy()
    if (not use_external_intro_video) and (
        not scenes or scenes[0].get("description", "").lower() != "intro"
    ):
        intro_scene = {
            "id": "intro",
            "description": "intro",
            "voiceover": "Welcome to Phiversity. Where Physics Education is made simple.",
            "elements": [],
        }
        scenes_with_intro.insert(0, intro_scene)
        data.setdefault("animation_plan", {}).setdefault("scenes", []).insert(
            0, intro_scene
        )

    # Subject-specific intro tagline
    subject_taglines = {
        "physics": "Physics Education Made Simple",
        "chemistry": "Chemistry Education Made Simple",
        "mathematics": "Mathematics Education Made Simple",
        "economics": "Economics Education Made Simple",
    }
    tagline = subject_taglines.get(subject, "STEM Education Made Simple")

    lines: List[str] = [
        "from manim import *",
        "from manim import rate_functions as rf",
        "",
        f"# Subject: {subject}",
        f"class GeneratedScene({scene_cls}):",
        "    def construct(self):",
        f"        _bg_color = '{COLORS['bg']}'",
        "        self.camera.background_color = _bg_color",
        "",
        "        # Persistent watermark — added once, never removed",
        "        watermark = Text('Phiversity', font_size=18, color=GRAY).set_opacity(0.5)",
        "        watermark.set_z_index(100)",
        "        watermark.to_corner(DR, buff=0.2)",
        "        self.add(watermark)",
        "",
        f"        # Subject badge",
        f"        subject_badge = Text('{subject.title()}', font_size=16, color=GRAY).set_opacity(0.4)",
        "        subject_badge.set_z_index(100)",
        "        subject_badge.to_corner(DL, buff=0.2)",
        "        self.add(subject_badge)",
        "",
        "        def _fit(mob, max_w=None, max_h=None):",
        '            """Scale a mobject down to fit within a box (in scene units)."""',
        "            try:",
        "                if max_w and hasattr(mob, 'width') and mob.width > max_w:",
        "                    mob.scale(max_w / mob.width)",
        "                if max_h and hasattr(mob, 'height') and mob.height > max_h:",
        "                    mob.scale(max_h / mob.height)",
        "            except Exception:",
        "                pass",
        "            return mob",
        "",
    ]
    cam_phi, cam_theta, cam_zoom = (66, -35, 1.05)
    if needs_3d:
        camera_profiles = {
            "physics": (70, -40, 1.08),
            "chemistry": (66, -35, 1.06),
            "mathematics": (64, -30, 1.04),
            "economics": (62, -28, 1.03),
        }
        cam_phi, cam_theta, cam_zoom = camera_profiles.get(subject, (66, -35, 1.05))
        lines += [
            "        # Enhanced 3D camera framing for clearer depth and better scene readability.",
            f"        self.set_camera_orientation(phi={cam_phi}*DEGREES, theta={cam_theta}*DEGREES, gamma=0*DEGREES, zoom={cam_zoom})",
        ]

    for sidx, sc in enumerate(scenes_with_intro, start=1):
        desc = sc.get("description", "")
        scene_id = sc.get("id", "")
        scene_sd = _resolve_scene_duration(sc, scene_durations, sidx)

        # ── Intro scene ───────────────────────────────────────────────────────
        if scene_id == "intro" or desc.lower() == "intro":
            lines += [
                "        # ── Intro ─────────────────────────────────────────────",
                "        t = 0.0",
                "        intro   = Text('Phiversity', font_size=72, color=BLUE)",
                f"        tagline = Text('{tagline}', font_size=28, color=WHITE)",
                "        tagline.next_to(intro, DOWN)",
                "        self.play(FadeIn(intro, scale=0.5))",
                "        t += 1.0",
                "        self.play(Write(tagline))",
                "        t += 1.0",
                "        self.play(FadeOut(intro), FadeOut(tagline))",
                "        t += 1.0",
                f"        if t < {scene_sd:.3f}: self.wait({scene_sd:.3f} - t); t = {scene_sd:.3f}",
            ]
            continue

        # ── Regular scene ─────────────────────────────────────────────────────
        scene_title_for_comment = _safe_comment(desc[:80]) or sc.get(
            "id", f"Scene {sidx}"
        )
        scene_title = (_safe_str(desc[:80]) or sc.get("id", f"Scene {sidx}")).replace(
            "'", " "
        )
        elements = sc.get("elements", [])
        auto_positions = _assign_positions(elements)
        hdr_color = _scene_header_color(scene_id, desc)

        # Layout params for this scene (used for scaling/sizing to reduce overlaps)
        element_types = [
            str(el.get("type") or "").lower() for el in elements if isinstance(el, dict)
        ]
        axes_present = any(t == "axes" for t in element_types)
        scene_has_media = any(
            (t in _VISUAL_TYPES or t in _SHAPE_TYPES) and t != "highlight"
            for t in element_types
        )
        scene_has_text = any(
            (t in _TEXT_TYPES)
            or (t not in _VISUAL_TYPES and t not in _SHAPE_TYPES and t != "highlight")
            for t in element_types
        )
        layout_mixed = bool(scene_has_text and scene_has_media)
        zoom_flags = _scene_zoom_flags(sc)

        media_slots = sum(
            1
            for t in element_types
            if (t in _VISUAL_TYPES or t in _SHAPE_TYPES)
            and t != "highlight"
            and not (axes_present and t == "graph")
        )
        text_slots = sum(
            1
            for t in element_types
            if (t in _TEXT_TYPES)
            or (t not in _VISUAL_TYPES and t not in _SHAPE_TYPES and t != "highlight")
        )

        # Conservative defaults: keep content readable while reducing collisions in mixed scenes.
        text_scale = 0.60
        math_scale = 0.80
        if layout_mixed:
            if text_slots >= 8:
                text_scale, math_scale = 0.45, 0.65
            elif text_slots >= 6:
                text_scale, math_scale = 0.50, 0.70
            elif text_slots >= 4:
                text_scale, math_scale = 0.53, 0.74
            else:
                text_scale, math_scale = 0.57, 0.78
        else:
            if text_slots >= 10:
                text_scale, math_scale = 0.50, 0.70
            elif text_slots >= 6:
                text_scale, math_scale = 0.55, 0.75

        # Lanes: right for text, left for visuals. Fit prevents large items from covering others.
        text_max_w = 6.1 if layout_mixed else 12.8
        text_max_h = 5.8
        media_max_w = 6.1 if layout_mixed else 12.8
        media_max_h = 5.6 if layout_mixed else 7.2
        if layout_mixed and media_slots >= 2:
            media_max_h = 3.9

        # Axes can be tall; shrink when multiple media items share the left lane.
        axes_x_len, axes_y_len = 6.0, 4.0
        if layout_mixed:
            if media_slots >= 3:
                axes_x_len, axes_y_len = 4.8, 2.8
            elif media_slots >= 2:
                axes_x_len, axes_y_len = 5.2, 3.0

        lines += [
            f"        # Scene {sidx}: {scene_title_for_comment}",
            f"        header = Text('{scene_title}', color={hdr_color}).scale(0.6).to_edge(UP, buff=0.15)",
            "        header.set_z_index(80)",
            "        _fit(header, 12.8, None)",
            "        self.play(FadeIn(header, shift=DOWN))",
            "        _scene_mobjs = [header]",
            "        objs  = []",
            "        idmap = {}",
            "        axes  = None",
            "        import math, numpy as np",
            "        t  = 0.0",
            "        R  = 2.0",
            "        r  = 1.0",
            "        dr = 0.2",
            f"        _layout_mixed = {layout_mixed}",
            f"        _text_scale  = {text_scale:.3f}",
            f"        _math_scale  = {math_scale:.3f}",
            f"        _text_max_w  = {text_max_w:.3f}",
            f"        _text_max_h  = {text_max_h:.3f}",
            f"        _media_max_w = {media_max_w:.3f}",
            f"        _media_max_h = {media_max_h:.3f}",
            f"        _axes_x_len  = {axes_x_len:.3f}",
            f"        _axes_y_len  = {axes_y_len:.3f}",
            "        _legend_corner = UL if _layout_mixed else UR",
            f"        _zoom_tire = {zoom_flags['tire']}",
            f"        _zoom_bubble = {zoom_flags['bubble']}",
            f"        _zoom_graph = {zoom_flags['graph']}",
            f"        _zoom_equation = {zoom_flags['equation']}",
            f"        _zoom_any = {zoom_flags['any']}",
            f"        _zoom_zoom_trigger = {zoom_flags.get('zoom_trigger', False)}",
            f"        _zoom_motion_trigger = {zoom_flags.get('motion_trigger', False)}",
            f"        _zoom_heat_friction = {zoom_flags.get('heat_friction', False)}",
            f"        _zoom_3d_object = {zoom_flags.get('3d_object', False)}",
            f"        _zoom_coin = {zoom_flags.get('coin', False)}",
            f"        _zoom_car = {zoom_flags.get('car', False)}",
            f"        _zoom_road = {zoom_flags.get('road', False)}",
            f"        _is_3d_scene = {needs_3d}",
            f"        _cam_zoom = {cam_zoom:.3f}",
            f"        _env_detected = {repr(detected_env)}",
            f"        _diff_detected = {repr(detected_difficulty)}",
            f"        _active_theme = {repr(active_theme) if active_theme else 'None'}",
        ]

        if active_theme:
            lines.extend(
                [
                    f"        _car_color = '{active_theme.get('car_body', '#4169E1')}'",
                    f"        _window_color = '{active_theme.get('window', '#87CEEB')}'",
                    f"        _wheel_color = '{active_theme.get('wheel', '#1a1a1a')}'",
                    f"        _road_color = '{active_theme.get('road', '#3d3d3d')}'",
                    f"        _accent_color = '{active_theme.get('accent', '#FBBF24')}'",
                    f"        _bg_color = '{active_theme.get('sky', COLORS['bg'])}'",
                ]
            )
        else:
            lines.extend(
                [
                    "        _car_color = '#4169E1'",
                    "        _window_color = '#87CEEB'",
                    "        _wheel_color = '#1a1a1a'",
                    "        _road_color = '#3d3d3d'",
                    "        _accent_color = '#FBBF24'",
                    f"        _bg_color = '{COLORS['bg']}'",
                ]
            )

        # Apply background color for this scene
        lines.append("        self.camera.background_color = _bg_color")

        # Determine duration list safely
        dur_list: Optional[List[float]] = None
        if (
            element_durations is not None
            and isinstance(element_durations, list)
            and len(element_durations) >= sidx
        ):
            candidate = element_durations[sidx - 1]
            if isinstance(candidate, list):
                dur_list = [float(x) for x in candidate]

        acc = 0.0

        for eidx, el in enumerate(elements, start=1):
            etype = str(el.get("type") or "").lower()
            raw_content = el.get("content") or ""
            content = (
                raw_content if etype in ("mathtex", "latex") else _safe_str(raw_content)
            )
            p = auto_positions[eidx - 1]

            style = el.get("style") if isinstance(el, dict) else None
            color_e = _color_expr(style if isinstance(style, dict) else None)
            if not color_e:
                color_e = _get_default_color(
                    etype,
                    content,
                    eidx,
                    scene_id=scene_id,
                    scene_desc=desc,
                )

            timing = el.get("timing") if isinstance(el, dict) else None
            start = timing.get("start") if isinstance(timing, dict) else None
            end = timing.get("end") if isinstance(timing, dict) else None
            tin = (
                (timing.get("transition_in") or "") if isinstance(timing, dict) else ""
            )
            tout = (
                (timing.get("transition_out") or "") if isinstance(timing, dict) else ""
            )
            easing = (timing.get("easing") or "") if isinstance(timing, dict) else ""
            dur_in = timing.get("duration_in") if isinstance(timing, dict) else None
            dur_out = timing.get("duration_out") if isinstance(timing, dict) else None
            el_id = el.get("id") if isinstance(el, dict) else None

            # Resolve start / end timing
            if start is None:
                if isinstance(dur_list, list) and len(dur_list) >= eidx:
                    elem_dur = max(float(dur_list[eidx - 1]), 1.0)
                elif dur_in and float(dur_in) > 0:
                    elem_dur = float(dur_in)
                else:
                    # For 10-min videos each element should show for a while
                    elem_dur = max(scene_sd / max(len(elements), 1), 3.0)
                start, end, acc = acc, acc + elem_dur, acc + elem_dur

            var = f"obj_{sidx}_{eidx}"
            in_anim = _normalize_anim(tin, _anim_in_default(etype))
            out_anim = _normalize_anim(tout, _anim_out_default(etype))
            rfname = _rate_func(easing)

            def _extras(rt: Optional[float]) -> str:
                ex: List[str] = []
                if rfname:
                    ex.append(f"rate_func={rfname}")
                if rt is not None:
                    ex.append(f"run_time={float(rt):.3f}")
                return (", " + ", ".join(ex)) if ex else ""

            def _wait_guard(ts: float) -> str:
                return f"        if t < {ts:.3f}: self.wait({ts:.3f} - t); t = {ts:.3f}"

            def _wait_guard_deep(ts: float) -> str:
                return f"            if t < {ts:.3f}: self.wait({ts:.3f} - t); t = {ts:.3f}"

            # ── Emit per-type code ─────────────────────────────────────────────
            if etype in ("text", ""):
                lines.append(
                    f"        {var} = Text('{content}').scale(_text_scale).move_to({p})"
                )
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                lines.append(f"        {var}.set_z_index(40)")
                lines.append(f"        _fit({var}, _text_max_w, _text_max_h)")
                if start is not None:
                    lines.append(_wait_guard(start))
                lines.append(f"        self.play({in_anim}({var}){_extras(dur_in)})")
                lines.append(f"        _scene_mobjs.append({var})")
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append(
                        f"        self.play({out_anim}({var}){_extras(dur_out)})"
                    )
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype in ("mathtex", "latex"):
                lines.append("        try:")
                lines.append(
                    f"            {var} = MathTex(r'''{content}''').scale(_math_scale).move_to({p})"
                )
                lines.append("        except Exception:")
                lines.append(
                    f"            {var} = Text('{_safe_str(content)}').scale(_text_scale).move_to({p})"
                )
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                lines.append(f"        {var}.set_z_index(40)")
                lines.append(f"        _fit({var}, _text_max_w, _text_max_h)")
                if start is not None:
                    lines.append(_wait_guard(start))
                lines.append(f"        self.play({in_anim}({var}){_extras(dur_in)})")
                lines.append(f"        _scene_mobjs.append({var})")
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append(
                        f"        self.play({out_anim}({var}){_extras(dur_out)})"
                    )
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype == "axes":
                xr = (
                    style.get("x_range", [-5, 5, 1])
                    if isinstance(style, dict)
                    else [-5, 5, 1]
                )
                yr = (
                    style.get("y_range", [-3, 3, 1])
                    if isinstance(style, dict)
                    else [-3, 3, 1]
                )
                xlab = style.get("x_label") if isinstance(style, dict) else None
                ylab = style.get("y_label") if isinstance(style, dict) else None
                lines.append(
                    f"        axes = Axes(x_range={xr}, y_range={yr}, x_length=_axes_x_len, y_length=_axes_y_len).move_to({p})"
                )
                if color_e:
                    lines.append(f"        axes.set_color({color_e})")
                lines.append("        axes.set_z_index(10)")
                lines.append("        _fit(axes, _media_max_w, _media_max_h)")
                if start is not None:
                    lines.append(_wait_guard(start))
                if xlab or ylab:
                    xl = _safe_str(xlab or "x")
                    yl = _safe_str(ylab or "y")
                    lines.append(
                        f"        lbls = axes.get_axis_labels(MathTex(r'{xl}'), MathTex(r'{yl}'))"
                    )
                    lines.append("        lbls.set_z_index(40)")
                    lines.append("        self.play(Create(axes), FadeIn(lbls))")
                    lines.append("        _scene_mobjs.extend([axes, lbls])")
                else:
                    lines.append("        self.play(Create(axes))")
                    lines.append("        _scene_mobjs.append(axes)")
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append("        self.play(Uncreate(axes))")
                lines.append("        objs.append(axes)")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = axes")

            elif etype == "graph":
                lines.append("        if axes is None:")
                lines.append(
                    f"            axes = Axes(x_range=[-5,5,1], y_range=[-3,3,1], x_length=_axes_x_len, y_length=_axes_y_len).move_to({p})"
                )
                lines.append("            axes.set_z_index(10)")
                lines.append("            _fit(axes, _media_max_w, _media_max_h)")
                lines.append("            self.play(Create(axes))")
                lines.append("            _scene_mobjs.append(axes)")
                curves = (
                    style.get("curves") if isinstance(style, dict) else None
                ) or []
                single = {"content": content, **(style or {})}
                items = curves if curves else [single]
                items_repr = str(
                    [
                        {
                            "mode": (cv.get("mode") or "function")
                            if isinstance(cv, dict)
                            else "function",
                            "content": (
                                cv.get("content") if isinstance(cv, dict) else None
                            )
                            or content,
                            "x": (cv.get("x") if isinstance(cv, dict) else None),
                            "y": (cv.get("y") if isinstance(cv, dict) else None),
                            "t_range": (
                                cv.get("t_range") if isinstance(cv, dict) else None
                            )
                            or [0, 6.283],
                            "x_range": (
                                cv.get("x_range") if isinstance(cv, dict) else None
                            )
                            or [-5, 5],
                            "color": (
                                cv.get("color") if isinstance(cv, dict) else None
                            ),
                            "label": (
                                cv.get("label") if isinstance(cv, dict) else None
                            ),
                        }
                        for cv in items
                    ]
                )
                lines.append(f"        _cv_idx = 0")
                lines.append(f"        for cv in {items_repr}:")
                lines += [
                    "            mode  = (cv.get('mode') or 'function').lower()",
                    "            color = cv.get('color')",
                    "            label = cv.get('label')",
                    f"            _auto_cc = {repr(CURVE_COLORS)}[_cv_idx % {len(CURVE_COLORS)}]",
                    "            if mode == 'parametric':",
                    "                ex = cv.get('x') or 'cos(t)'",
                    "                ey = cv.get('y') or 'sin(t)'",
                    "                tr = cv.get('t_range') or [0, 6.283]",
                    "                def _fx(t): return eval(ex, {'__builtins__': None, 'math': math, 'np': np}, {'t': t})",
                    "                def _fy(t): return eval(ey, {'__builtins__': None, 'math': math, 'np': np}, {'t': t})",
                    "                curve = axes.plot_parametric_curve(lambda t: np.array([_fx(t), _fy(t), 0]), t_range=tr)",
                    "            else:",
                    "                ex = cv.get('content') or 'sin(x)'",
                    "                xr = cv.get('x_range') or [-5, 5]",
                    "                def _f(x):",
                    "                    try:",
                    "                        return eval(ex, {'__builtins__': None, 'math': math, 'np': np, 'sin': math.sin, 'cos': math.cos, 'tan': math.tan, 'exp': math.exp, 'log': math.log, 'pi': math.pi, 'e': math.e}, {'x': x})",
                    "                    except: return math.sin(x)",
                    "                curve = axes.plot(_f, x_range=xr)",
                    "            if color: curve.set_color(color if str(color).startswith('#') else str(color).upper())",
                    "            else: curve.set_color(_auto_cc)",
                    "            curve.set_z_index(20)",
                    "            _cv_idx += 1",
                ]
                if start is not None:
                    lines.append(_wait_guard_deep(start))
                lines += [
                    "            self.play(Create(curve))",
                    "            _scene_mobjs.append(curve)",
                ]
                if end is not None and end > start and tout:
                    lines.append(_wait_guard_deep(end))
                    lines.append("            self.play(Uncreate(curve))")
                lines += [
                    "            objs.append(curve)",
                    "        _legend_items = [(o, cv.get('label')) for o, cv in zip(objs[-len("
                    + repr(items)
                    + "):], "
                    + repr(items)
                    + ") if cv.get('label')]",
                    "        if _legend_items:",
                    "            _li = []",
                    "            for _lc, _ll in _legend_items:",
                    "                _ld = Dot(color=_lc.get_color()).scale(0.7)",
                    "                _lt = Text(str(_ll)).scale(0.4)",
                    "                _li.append(VGroup(_ld, _lt).arrange(RIGHT, buff=0.2))",
                    "            _legend = VGroup(*_li).arrange(DOWN, aligned_edge=LEFT).to_corner(_legend_corner, buff=0.25)",
                    "            _legend.set_z_index(40)",
                    "            self.play(FadeIn(_legend))",
                    "            _scene_mobjs.append(_legend)",
                    "            objs.append(_legend)",
                ]
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = axes")

            elif etype == "vectorfield":
                fx = style.get("fx") if isinstance(style, dict) else None
                fy = style.get("fy") if isinstance(style, dict) else None
                if not fx or not fy:
                    parts = content.strip().strip("[]").split(",") if content else []
                    fx, fy = (
                        (parts[0].strip(), parts[1].strip())
                        if len(parts) == 2
                        else ("y", "-x")
                    )
                xr = (
                    style.get("x_range", [-5, 5, 1])
                    if isinstance(style, dict)
                    else [-5, 5, 1]
                )
                yr = (
                    style.get("y_range", [-3, 3, 1])
                    if isinstance(style, dict)
                    else [-3, 3, 1]
                )
                lines += [
                    f"        def _fx(x,y): return eval({repr(fx)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'x': x, 'y': y}})",
                    f"        def _fy(x,y): return eval({repr(fy)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'x': x, 'y': y}})",
                    f"        vf = VectorField(lambda p: np.array([_fx(p[0], p[1]), _fy(p[0], p[1]), 0]), x_range={xr}, y_range={yr}).scale(0.6).move_to({p})",
                ]
                if color_e:
                    lines.append(f"        vf.set_color({color_e})")
                lines.append("        vf.set_z_index(20)")
                lines.append("        _fit(vf, _media_max_w, _media_max_h)")
                if start is not None:
                    lines.append(_wait_guard(start))
                lines += [
                    "        self.play(Create(vf))",
                    "        _scene_mobjs.append(vf)",
                ]
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append("        self.play(Uncreate(vf))")
                lines.append("        objs.append(vf)")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = vf")

            elif etype == "streamlines":
                fx = style.get("fx") if isinstance(style, dict) else None
                fy = style.get("fy") if isinstance(style, dict) else None
                if not fx or not fy:
                    parts = content.strip().strip("[]").split(",") if content else []
                    fx, fy = (
                        (parts[0].strip(), parts[1].strip())
                        if len(parts) == 2
                        else ("y", "-x")
                    )
                xr = (
                    style.get("x_range", [-5, 5, 1])
                    if isinstance(style, dict)
                    else [-5, 5, 1]
                )
                yr = (
                    style.get("y_range", [-3, 3, 1])
                    if isinstance(style, dict)
                    else [-3, 3, 1]
                )
                lines += [
                    f"        def _fx(x,y): return eval({repr(fx)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'x': x, 'y': y}})",
                    f"        def _fy(x,y): return eval({repr(fy)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'x': x, 'y': y}})",
                    f"        stream = StreamLines(lambda p: np.array([_fx(p[0], p[1]), _fy(p[0], p[1]), 0]), x_range={xr}, y_range={yr}).scale(0.6).move_to({p})",
                ]
                if color_e:
                    lines.append(f"        stream.set_color({color_e})")
                lines.append("        stream.set_z_index(20)")
                lines.append("        _fit(stream, _media_max_w, _media_max_h)")
                if start is not None:
                    lines.append(_wait_guard(start))
                lines += [
                    "        self.play(Create(stream))",
                    "        _scene_mobjs.append(stream)",
                ]
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append("        self.play(Uncreate(stream))")
                lines.append("        objs.append(stream)")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = stream")

            elif etype == "parametric3d":
                ex = (style.get("x") if isinstance(style, dict) else None) or "cos(t)"
                ey = (style.get("y") if isinstance(style, dict) else None) or "sin(t)"
                ez = (style.get("z") if isinstance(style, dict) else None) or "0.2*t"
                tr = (style.get("t_range") if isinstance(style, dict) else None) or [
                    0,
                    6.283,
                ]
                lines += [
                    "        axes3d = ThreeDAxes(x_length=6, y_length=6, z_length=6)",
                    "        self.play(Create(axes3d))",
                    "        _scene_mobjs.append(axes3d)",
                    f"        def fx(t): return eval({repr(ex)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'t': t}})",
                    f"        def fy(t): return eval({repr(ey)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'t': t}})",
                    f"        def fz(t): return eval({repr(ez)}, {{'__builtins__': None, 'math': math, 'np': np}}, {{'t': t}})",
                    "        curve3d = ParametricFunction(lambda t: np.array([fx(t), fy(t), fz(t)]), t_range=tr, use_smoothing=False)",
                ]
                if color_e:
                    lines.append(f"        curve3d.set_color({color_e})")
                if start is not None:
                    lines.append(_wait_guard(start))
                lines += [
                    "        self.play(Create(curve3d))",
                    "        _scene_mobjs.append(curve3d)",
                ]
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append("        self.play(Uncreate(curve3d))")
                lines.append("        objs.append(curve3d)")

            elif etype == "highlight":
                lines += [
                    "        _hl_target = objs[-1] if objs else None",
                    f"        _hl_text   = {repr(content)}",
                    "        if _hl_text:",
                    "            for _o in objs:",
                    "                try:",
                    "                    if hasattr(_o, 'text') and _o.text == _hl_text:",
                    "                        _hl_target = _o; break",
                    "                except Exception: pass",
                    "        if _hl_target is not None:",
                    f"            {var} = SurroundingRectangle(_hl_target, buff=0.2)",
                ]
                if color_e:
                    lines.append(f"            {var}.set_color({color_e})")
                if start is not None:
                    lines.append(
                        f"            if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}"
                    )
                lines += [
                    f"            self.play(Create({var}))",
                    f"            _scene_mobjs.append({var})",
                ]
                if end is not None and end > start and tout:
                    lines += [
                        f"            if t < {end:.3f}: self.wait({end:.3f} - t); t = {end:.3f}",
                        f"            self.play(Uncreate({var}))",
                    ]
                lines.append(f"            objs.append({var})")
                if el_id:
                    lines.append(f"            idmap['{el_id}'] = {var}")

            elif etype == "polygon":
                sanitized = content.replace("\\pi", "np.pi")
                lines += [
                    "        try:",
                    f"            _pts = eval('{sanitized}', {{'__builtins__': None, 'np': np, 'R': R, 'r': r, 'dr': dr}})",
                    f"            {var} = Polygon(*[np.array([_x,_y,0]) for _x,_y in _pts])",
                    f"            {var}.move_to({p})",
                ]
                if color_e:
                    lines.append(f"            {var}.set_color({color_e})")
                if style and "fill_opacity" in style:
                    lines.append(
                        f"            {var}.set_fill({color_e or 'WHITE'}, opacity={style['fill_opacity']})"
                    )
                num_sides = style.get("sides") if isinstance(style, dict) else None
                side_label_text = f"'{num_sides}-sided'" if num_sides else "'polygon'"
                lines += [
                    f"            _poly_lbl = MathTex({side_label_text}).scale(0.5)",
                    f"            _poly_lbl.next_to({var}, UP, buff=0.15)",
                    "        except Exception:",
                    f"            {var}     = Text('Polygon Error')",
                    "            _poly_lbl = Text('')",
                ]
                if start is not None:
                    lines.append(_wait_guard(start))
                lines += [
                    f"        self.play(Create({var}), FadeIn(_poly_lbl))",
                    f"        _scene_mobjs.extend([{var}, _poly_lbl])",
                ]
                if el_id:
                    lines.append(f"        idmap['{el_id}_label'] = _poly_lbl")
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append(
                        f"        self.play(Uncreate({var}), FadeOut(_poly_lbl))"
                    )
                lines.append(f"        objs.append({var})")

            elif etype == "circle":
                radius_val = (
                    str(style.get("radius", "R"))
                    if isinstance(style, dict) and "radius" in style
                    else "R"
                )
                lines += [f"        {var} = Circle(radius={radius_val}).move_to({p})"]
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                lines += [
                    f"        _r_lbl = MathTex('r').scale(0.7)",
                    f"        _r_lbl.next_to({var}, RIGHT, buff=0.15)",
                ]
                if start is not None:
                    lines.append(_wait_guard(start))
                lines += [
                    f"        self.play(Create({var}), FadeIn(_r_lbl))",
                    f"        _scene_mobjs.extend([{var}, _r_lbl])",
                ]
                if el_id:
                    lines.append(f"        idmap['{el_id}_label'] = _r_lbl")
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append(f"        self.play(Uncreate({var}), FadeOut(_r_lbl))")
                lines.append(f"        objs.append({var})")

            elif etype == "annulus":
                inner_r = (
                    str(style.get("inner_radius", "r"))
                    if isinstance(style, dict) and "inner_radius" in style
                    else "r"
                )
                outer_r = (
                    str(style.get("outer_radius", "r+dr"))
                    if isinstance(style, dict) and "outer_radius" in style
                    else "r+dr"
                )
                lines += [
                    f"        {var} = Annulus(inner_radius={inner_r}, outer_radius={outer_r}).move_to({p})"
                ]
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                if style and "fill_opacity" in style:
                    lines.append(
                        f"        {var}.set_fill({color_e or 'YELLOW'}, opacity={style['fill_opacity']})"
                    )
                lines += [
                    f"        _ann_inner = MathTex('r').scale(0.6).move_to({p} + 0.3*LEFT + 0.3*UP)",
                    f"        _ann_outer = MathTex('R').scale(0.6).move_to({p} + 0.8*RIGHT + 0.5*UP)",
                ]
                if start is not None:
                    lines.append(_wait_guard(start))
                lines += [
                    f"        self.play(Create({var}), FadeIn(_ann_inner), FadeIn(_ann_outer))",
                    f"        _scene_mobjs.extend([{var}, _ann_inner, _ann_outer])",
                ]
                if el_id:
                    lines.append(f"        idmap['{el_id}_inner_label'] = _ann_inner")
                    lines.append(f"        idmap['{el_id}_outer_label'] = _ann_outer")
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append(
                        f"        self.play(Uncreate({var}), FadeOut(_ann_inner), FadeOut(_ann_outer))"
                    )
                lines.append(f"        objs.append({var})")

            elif etype == "rectangle":
                width_val = (
                    str(style.get("width", "2*np.pi*r"))
                    if isinstance(style, dict) and "width" in style
                    else "2*np.pi*r"
                )
                height_val = (
                    str(style.get("height", "dr"))
                    if isinstance(style, dict) and "height" in style
                    else "dr"
                )
                lines += [
                    f"        {var} = Rectangle(width={width_val}, height={height_val}).move_to({p})"
                ]
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                if style and "fill_opacity" in style:
                    lines.append(
                        f"        {var}.set_fill({color_e or 'BLUE'}, opacity={style['fill_opacity']})"
                    )
                lines += [
                    f"        _rect_w = MathTex('w').scale(0.6).next_to({var}, DOWN, buff=0.1)",
                    f"        _rect_h = MathTex('h').scale(0.6).next_to({var}, LEFT, buff=0.1)",
                ]
                if start is not None:
                    lines.append(_wait_guard(start))
                lines += [
                    f"        self.play(Create({var}), FadeIn(_rect_w), FadeIn(_rect_h))",
                    f"        _scene_mobjs.extend([{var}, _rect_w, _rect_h])",
                ]
                if el_id:
                    lines.append(f"        idmap['{el_id}_width_label']  = _rect_w")
                    lines.append(f"        idmap['{el_id}_height_label'] = _rect_h")
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append(
                        f"        self.play(Uncreate({var}), FadeOut(_rect_w), FadeOut(_rect_h))"
                    )
                lines.append(f"        objs.append({var})")

            elif etype in ("sphere3d", "coin3d"):
                radius = style.get("radius", 0.5) if isinstance(style, dict) else 0.5
                col = (
                    VIBRANT_3D_COLORS.get("coin", {}).get("gold", "#FFD700")
                    if etype == "coin3d"
                    else (color_e or "#FFD700")
                )
                lines += [
                    f"        {var} = Sphere(radius={radius}, resolution=(15, 15)).move_to({p})",
                    f"        {var}.set_fill({col})",
                    f"        {var}.set_reflectiveness(0.5)",
                    f"        {var}.set_shadow(0.3)",
                ]
                if start is not None:
                    lines.append(_wait_guard(start))
                lines += [
                    f"        self.play(Create({var}), run_time=1.5)",
                    f"        _scene_mobjs.append({var})",
                ]
                lines.append("        if _zoom_zoom_trigger:")

                lines.extend(
                    [
                        "            self.begin_ambient_camera_rotation(rate=0.1)",
                        "            self.wait(1.5)",
                        "            self.stop_ambient_camera_rotation()",
                    ]
                )
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype in ("cylinder3d", "tire3d"):
                radius = style.get("radius", 0.4) if isinstance(style, dict) else 0.4
                height = style.get("height", 0.25) if isinstance(style, dict) else 0.25
                tire_colors = VIBRANT_3D_COLORS.get("tire", {})
                col = (
                    tire_colors.get("rubber", "#1a1a1a")
                    if etype == "tire3d"
                    else (color_e or "#808080")
                )
                lines += [
                    f"        {var} = Cylinder(radius={radius}, height={height}, direction=UP).move_to({p})",
                    f"        {var}.set_fill({col})",
                ]
                if etype == "tire3d":
                    lines.extend(
                        [
                            f"        _tire_tread = Circle(radius={radius}).move_to({p})",
                            f"        _tire_tread.set_fill('#2d2d2d')",
                            f"        _tire_tread.set_z_index({var}.z_index - 1)",
                            f"        _rim = Circle(radius={radius * 0.6}).move_to({p} + 0.05*UP)",
                            f"        _rim.set_fill('{tire_colors.get('rim', '#B8860B')}')",
                        ]
                    )
                if start is not None:
                    lines.append(_wait_guard(start))
                lines += [
                    f"        self.play(Create({var}), run_time=1.5)",
                    f"        _scene_mobjs.append({var})",
                ]
                if etype == "tire3d":
                    lines.extend(
                        [
                            "        self.play(Create(_tire_tread), Create(_rim), run_time=0.8)",
                            "        _scene_mobjs.extend([_tire_tread, _rim])",
                        ]
                    )
                if zoom_flags.get("zoom_trigger"):
                    lines.extend(
                        [
                            f"        self.move_camera(phi=50*DEGREES, theta=-30*DEGREES, run_time=1.2)",
                            f"        self.wait(0.8)",
                            f"        self.move_camera(phi=70*DEGREES, theta=-45*DEGREES, run_time=1.0)",
                        ]
                    )
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype in ("box3d", "car3d"):
                width = style.get("width", 1.5) if isinstance(style, dict) else 1.5
                height = style.get("height", 0.6) if isinstance(style, dict) else 0.6
                depth = style.get("depth", 0.8) if isinstance(style, dict) else 0.8
                car_colors = VIBRANT_3D_COLORS.get("car", {})
                col = (
                    active_theme.get("car_body", car_colors.get("body", "#4169E1"))
                    if active_theme
                    else (
                        car_colors.get("body", "#4169E1")
                        if etype == "car3d"
                        else (color_e or "#4169E1")
                    )
                )
                window_col = (
                    active_theme.get("window", car_colors.get("window", "#87CEEB"))
                    if active_theme
                    else car_colors.get("window", "#87CEEB")
                )
                wheel_col = (
                    active_theme.get("wheel", car_colors.get("wheel", "#1a1a1a"))
                    if active_theme
                    else car_colors.get("wheel", "#1a1a1a")
                )
                lines += [
                    f"        {var} = Cube side_face_color={col}).move_to({p})",
                    f"        _car_body = _resize_to({var}, {width}, {height}, {depth})",
                ]
                if etype == "car3d":
                    car_parts = [
                        f"        _window = Rectangle(width={width * 0.6}, height={height * 0.5}).move_to({p} + 0.1*UP",
                        f"        _window.set_fill('{window_col}')",
                        f"        _wheel1 = Circle(radius=0.2).move_to({p} + 0.3*DOWN + 0.4*LEFT",
                        f"        _wheel1.set_fill('{wheel_col}')",
                        f"        _wheel2 = Circle(radius=0.2).move_to({p} + 0.3*DOWN + 0.4*RIGHT",
                        f"        _wheel2.set_fill('{wheel_col}')",
                    ]
                    lines.extend(car_parts)
                if start is not None:
                    lines.append(_wait_guard(start))
                lines += [
                    f"        self.play(Create({var}), run_time=1.2)",
                    f"        _scene_mobjs.append({var})",
                ]
                if etype == "car3d":
                    lines.extend(
                        [
                            "        self.play(Create(_window), Create(_wheel1), Create(_wheel2), run_time=1.0)",
                            "        _scene_mobjs.extend([_window, _wheel1, _wheel2])",
                        ]
                    )
                if zoom_flags.get("motion_trigger"):
                    dir_val = (
                        style.get("direction", "RIGHT")
                        if isinstance(style, dict)
                        else "RIGHT"
                    )
                    dist = style.get("distance", 2) if isinstance(style, dict) else 2
                    lines.extend(
                        [
                            f"        self.play({var}.animate.shift({dist}*{dir_val}), run_time=1.5)",
                            f"        self.wait(0.5)",
                        ]
                    )
                if zoom_flags.get("zoom_trigger"):
                    lines.extend(
                        [
                            "        self.move_camera(phi=60*DEGREES, theta=-40*DEGREES, run_time=1.0)",
                            "        self.wait(0.8)",
                        ]
                    )
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype in ("surface3d", "road3d"):
                width = style.get("width", 8) if isinstance(style, dict) else 8
                length = style.get("length", 6) if isinstance(style, dict) else 6
                road_colors = VIBRANT_3D_COLORS.get("road", {})
                road_col = (
                    active_theme.get("road", road_colors.get("asphalt", "#3d3d3d"))
                    if active_theme
                    else road_colors.get("asphalt", "#3d3d3d")
                )
                line_col = (
                    active_theme.get("line", road_colors.get("line", "#FFFFFF"))
                    if active_theme
                    else road_colors.get("line", "#FFFFFF")
                )
                edge_col = (
                    active_theme.get("accent", road_colors.get("edge", "#FF6B35"))
                    if active_theme
                    else road_colors.get("edge", "#FF6B35")
                )
                lines += [
                    f"        {var} = Rectangle(width={width}, height={length}).move_to({p})",
                    f"        {var}.set_fill({road_col})",
                    f"        {var}.set_z_index(5)",
                ]
                if etype == "road3d":
                    lines.extend(
                        [
                            f"        _center_line = Line(start={p} + {length // 2}*DOWN, end={p} + {length // 2}*UP)",
                            f"        _center_line.set_color('{line_col}')",
                            f"        _center_line.set_stroke(width=0.08)",
                            f"        _edge_lines = [Line(start={p} + {length // 2}*DOWN + 0.5*LEFT, end={p} + {length // 2}*UP + 0.5*LEFT), Line(start={p} + {length // 2}*DOWN + 0.5*RIGHT, end={p} + {length // 2}*UP + 0.5*RIGHT)]",
                            f"        for _el in _edge_lines: _el.set_color('{edge_col}')",
                        ]
                    )
                if start is not None:
                    lines.append(_wait_guard(start))
                lines.extend(
                    [
                        f"        self.play(Create({var})), run_time=1.0)",
                        f"        _scene_mobjs.append({var})",
                    ]
                )
                if etype == "road3d":
                    lines.extend(
                        [
                            "        self.play(Create(_center_line), Create(_edge_lines[0]), Create(_edge_lines[1]), run_time=0.8)",
                            "        _scene_mobjs.extend([_center_line, _edge_lines[0], _edge_lines[1])",
                        ]
                    )
                if zoom_flags.get("zoom_trigger"):
                    lines.extend(
                        [
                            "        self.move_camera(theta=-30*DEGREES, run_time=0.8)",
                        ]
                    )
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype == "cone3d":
                base_radius = (
                    style.get("radius", 0.5) if isinstance(style, dict) else 0.5
                )
                height = style.get("height", 1) if isinstance(style, dict) else 1
                lines.extend(
                    [
                        f"        {var} = Cone(base_radius={base_radius}, height={height}, direction=DOWN).move_to({p})",
                    ]
                )
                if color_e:
                    lines.append(f"        {var}.set_fill({color_e})")
                if start is not None:
                    lines.append(_wait_guard(start))
                lines.extend(
                    [
                        f"        self.play(Create({var}), run_time=1.2)",
                        f"        _scene_mobjs.append({var})",
                    ]
                )
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype == "torus3d":
                major_r = (
                    style.get("major_radius", 0.6) if isinstance(style, dict) else 0.6
                )
                minor_r = (
                    style.get("minor_radius", 0.2) if isinstance(style, dict) else 0.2
                )
                lines.extend(
                    [
                        f"        {var} = Torus(major_radius={major_r}, minor_radius={minor_r}).move_to({p})",
                    ]
                )
                if color_e:
                    lines.append(f"        {var}.set_fill({color_e})")
                if start is not None:
                    lines.append(_wait_guard(start))
                lines.extend(
                    [
                        f"        self.play(Create({var}), run_time=1.5)",
                        f"        _scene_mobjs.append({var})",
                    ]
                )
                if zoom_flags.get("zoom_trigger"):
                    lines.extend(
                        [
                            "        self.begin_ambient_camera_rotation(rate=0.15)",
                            "        self.wait(2)",
                            "        self.stop_ambient_camera_rotation()",
                        ]
                    )
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype == "arrow3d":
                start_pt = (
                    style.get("start", [0, 0, 0])
                    if isinstance(style, dict)
                    else [0, 0, 0]
                )
                end_pt = (
                    style.get("end", [1, 1, 0])
                    if isinstance(style, dict)
                    else [1, 1, 0]
                )
                thickness = (
                    style.get("thickness", 0.03) if isinstance(style, dict) else 0.03
                )
                lines.extend(
                    [
                        f"        {var} = Arrow3D(start={start_pt}, end={end_pt}, thickness={thickness}).move_to({p})",
                    ]
                )
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                if start is not None:
                    lines.append(_wait_guard(start))
                lines.extend(
                    [
                        f"        self.play(Create({var}), run_time=0.8)",
                        f"        _scene_mobjs.append({var})",
                    ]
                )
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype == "car_moving":
                direction = (
                    style.get("direction", "RIGHT")
                    if isinstance(style, dict)
                    else "RIGHT"
                )
                distance = style.get("distance", 3) if isinstance(style, dict) else 3
                duration = style.get("duration", 2) if isinstance(style, dict) else 2
                car_colors = VIBRANT_3D_COLORS.get("car", {})
                moving_car_col = (
                    active_theme.get("car_body", car_colors.get("body", "#4169E1"))
                    if active_theme
                    else car_colors.get("body", "#4169E1")
                )
                moving_wheel_col = (
                    active_theme.get("wheel", car_colors.get("wheel", "#1a1a1a"))
                    if active_theme
                    else car_colors.get("wheel", "#1a1a1a")
                )
                lines.extend(
                    [
                        f"        _car = Rectangle(width=1.2, height=0.5).move_to({p})",
                        f"        _car.set_fill('{moving_car_col}')",
                        f"        _wheel_a = Circle(radius=0.15).move_to({p} + 0.3*DOWN + 0.3*LEFT)",
                        f"        _wheel_a.set_fill('{moving_wheel_col}')",
                        f"        _wheel_b = Circle(radius=0.15).move_to({p} + 0.3*DOWN + 0.3*RIGHT)",
                        f"        _wheel_b.set_fill('{moving_wheel_col}')",
                        f"        _car_group = VGroup(_car, _wheel_a, _wheel_b)",
                    ]
                )
                if start is not None:
                    lines.append(_wait_guard(start))
                lines.extend(
                    [
                        "        self.play(FadeIn(_car_group), run_time=0.5)",
                        f"        self.play(_car_group.animate.shift({direction}*RIGHT*{distance}), run_time={duration})",
                        "        _scene_mobjs.append(_car_group)",
                        "        objs.append(_car_group)",
                    ]
                )
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = _car_group")

            elif etype == "friction_heat":
                intensity = (
                    style.get("intensity", 0.5) if isinstance(style, dict) else 0.5
                )
                heat_colors = VIBRANT_3D_COLORS.get("heat", {})
                col = heat_colors.get("medium" if intensity > 0.5 else "low", "#FF4500")
                radius = style.get("radius", 0.3) if isinstance(style, dict) else 0.3
                lines.extend(
                    [
                        f"        _heat_glow = Circle(radius={radius}).move_to({p})",
                        f"        _heat_glow.set_fill('{col}')",
                        f"        _heat_glow.set_opacity({intensity})",
                        f"        _heat_vapors = VGroup()",
                        "        for _i in range(3):",
                        "            _v = Dot().move_to({p} + 0.2*UP)",
                        "            _v.set_color('#FFA500')",
                        "            _heat_vapors.add(_v)",
                        "        _heat_vapors.arrange(UP, buff=0.15)",
                        "        _heat_vapors.move_to({p} + 0.5*UP)",
                    ]
                )
                if start is not None:
                    lines.append(_wait_guard(start))
                lines.extend(
                    [
                        "        self.play(FadeIn(_heat_glow), run_time=0.3)",
                        "        self.play(LaggedStart(*[FadeIn(v) for v in _heat_vapors]), run_time=0.8)",
                        "        _heat_glow.add_updater(lambda m, dt: m.set_opacity(max(0.1, m.opacity - 0.02)))",
                        "        for _v in _heat_vapors:",
                        "            _v.add_updater(lambda m, dt: m.shift(0.02*UP))",
                        "        self.wait(1.5)",
                        "        _heat_glow.remove_updater(_heat_glow.updaters[0])",
                        "        for _v in _heat_vapors: _v.remove_updater(_v.updaters[0])",
                        "        _scene_mobjs.extend([_heat_glow, _heat_vapors])",
                    ]
                )
                lines.append(f"        objs.append(_heat_glow)")
                if el_id:
                    lines.append(f"        idmap['{el_id}_glow'] = _heat_glow")

            elif etype == "force_arrow":
                force_type = (
                    style.get("force_type", "normal")
                    if isinstance(style, dict)
                    else "normal"
                )
                force_colors = PHYSICS_MOTION_COLORS
                col = force_colors.get(force_type, force_colors.get("force", "#FFD700"))
                arrow_len = style.get("length", 1.5) if isinstance(style, dict) else 1.5
                arrow_dir = (
                    style.get("direction", "UP") if isinstance(style, dict) else "UP"
                )
                lines.extend(
                    [
                        f"        _force_arrow = Arrow(start={p}, end={p} + {arrow_len}*{arrow_dir}, buff=0.1)",
                        f"        _force_arrow.set_color('{col}')",
                        f"        _force_arrow.set_z_index(30)",
                        f"        _force_label = MathTex(r'{force_type.title()}').scale(0.5).next_to(_force_arrow.get_end(), {arrow_dir}, buff=0.1)",
                        f"        _force_label.set_color('{col}')",
                    ]
                )
                if start is not None:
                    lines.append(_wait_guard(start))
                lines.extend(
                    [
                        "        self.play(Create(_force_arrow), Write(_force_label), run_time=0.8)",
                        "        _scene_mobjs.extend([_force_arrow, _force_label])",
                    ]
                )
                if zoom_flags.get("zoom_trigger"):
                    lines.extend(
                        [
                            "        _force_arrow.add_updater(lambda m: m.set_length(m.length * 1.05))",
                            "        self.wait(0.5)",
                            "        _force_arrow.remove_updater(_force_arrow.updaters[0])",
                        ]
                    )
                lines.append("        objs.append(_force_arrow)")
                if el_id:
                    lines.append(f"        idmap['{el_id}_arrow'] = _force_arrow")
                    lines.append(f"        idmap['{el_id}_label'] = _force_label")

            elif etype == "growth_chart":
                data_points = (
                    style.get("data_points", [[0,0],[1,2],[2,3],[3,5],[4,4],[5,6]])
                    if isinstance(style, dict) else [[0,0],[1,2],[2,3],[3,5],[4,4],[5,6]]
                )
                chart_col = color_e or "#00d2ff"
                label = (
                    style.get("label", "Growth")
                    if isinstance(style, dict) else "Growth"
                )
                lines.extend([
                    f"        _chart_axes = Axes(x_range=[0, {len(data_points)+1}, 1], y_range=[0, 8, 1], axis_config={{'include_numbers': True, 'font_size': 18}})",
                    f"        _chart_axes.scale(0.6).move_to({p})",
                    f"        _chart_axes.set_opacity(0.6)",
                    f"        _chart_label = Text('{label}', font_size=20, color='{chart_col}').next_to(_chart_axes, UP, buff=0.1)",
                    f"        _chart_pts = [",
                ])
                for dp in data_points:
                    x, y = dp[0], dp[1]
                    lines.append(f"            _chart_axes.c2p({x}, {y}),")
                lines.extend([
                    "        ]",
                    f"        _chart_curve = VMobject(stroke_color='{chart_col}', stroke_width=3, fill_color='{chart_col}', fill_opacity=0.15)",
                    "        _chart_curve.set_points_smoothly(_chart_pts)",
                    "        _chart_fill = VMobject(stroke_width=0, fill_color=_chart_curve.get_color(), fill_opacity=0.12)",
                    "        _chart_fill.set_points_as_corners([*_chart_pts, _chart_axes.c2p(_chart_pts[-1][0], 0), _chart_axes.c2p(_chart_pts[0][0], 0)])",
                    "        _chart_dots = VGroup(*[Dot(_pt, color=_chart_curve.get_color(), radius=0.06) for _pt in _chart_pts])",
                ])
                if start is not None:
                    lines.append(_wait_guard(start))
                lines.extend([
                    "        self.play(Create(_chart_axes), run_time=0.6)",
                    "        self.play(Create(_chart_curve), run_time=0.8)",
                    "        self.play(FadeIn(_chart_fill), run_time=0.4)",
                    "        self.play(LaggedStart(*[GrowFromCenter(d) for d in _chart_dots], lag_ratio=0.15), run_time=0.8)",
                    "        self.play(Write(_chart_label), run_time=0.4)",
                    "        _scene_mobjs.extend([_chart_axes, _chart_curve, _chart_fill, _chart_dots, _chart_label])",
                    "        for _d in _chart_dots:",
                    "            _d.add_updater(lambda m, dt: m.scale(1 + 0.08*math.sin(2*dt)))",
                    "        self.wait(0.5)",
                    "        for _d in _chart_dots:",
                    "            _d.remove_updater(_d.updaters[0])",
                ])
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append("        self.play(FadeOut(_chart_axes), FadeOut(_chart_curve), FadeOut(_chart_fill), FadeOut(_chart_dots), FadeOut(_chart_label))")
                lines.extend([
                    "        objs.extend([_chart_axes, _chart_curve, _chart_fill, _chart_dots, _chart_label])",
                ])
                if el_id:
                    lines.append(f"        idmap['{el_id}_curve'] = _chart_curve")

            elif etype == "particle_system":
                count = style.get("count", 30) if isinstance(style, dict) else 30
                ps_color = color_e or "#FF6B35"
                radius = style.get("radius", 3.0) if isinstance(style, dict) else 3.0
                lines.extend([
                    "        _ps_dots = VGroup()",
                    "        _ps_vx = []",
                    "        _ps_vy = []",
                    f"        for _i in range({count}):",
                    f"            _d = Dot(radius=0.04, color='{ps_color}').move_to({p} + {radius}*np.random.uniform(-1,1)*RIGHT + {radius}*np.random.uniform(-1,1)*UP)",
                    "            _d.set_opacity(0.7)",
                    "            _ps_dots.add(_d)",
                    "            _ps_vx.append(np.random.uniform(-0.3, 0.3))",
                    "            _ps_vy.append(np.random.uniform(-0.3, 0.3))",
                    "        _ps_center = np.array(" + p.replace("[", "(").replace("]", ")") + ")",
                    "        def _ps_update(mobs, dt):",
                    "            for _idx, _m in enumerate(mobs):",
                    "                _ps_vx[_idx] += np.random.uniform(-0.02, 0.02)",
                    "                _ps_vy[_idx] += np.random.uniform(-0.02, 0.02)",
                    "                _spd = math.sqrt(_ps_vx[_idx]**2 + _ps_vy[_idx]**2)",
                    "                if _spd > 0.4:",
                    "                    _ps_vx[_idx] *= 0.98",
                    "                    _ps_vy[_idx] *= 0.98",
                    "                _m.shift(_ps_vx[_idx]*dt*RIGHT + _ps_vy[_idx]*dt*UP)",
                    "                _v = _ps_center - _m.get_center()",
                    "                _dist = np.linalg.norm(_v)",
                    f"                if _dist > {radius}:",
                    "                    _m.shift(0.03 * _v / _dist)",
                    "        _ps_dots.add_updater(_ps_update)",
                    "        _ps_bonds = VGroup()",
                    f"        for _i in range(min(12, {count})):",
                    "            _j = (_i + 1) % min(12, count)",
                    "            _line = Line(_ps_dots[_i].get_center(), _ps_dots[_j].get_center(), stroke_width=0.5, stroke_opacity=0.25)",
                    f"            _line.set_color('{ps_color}')",
                    "            _line.add_updater(lambda m: m.put_start_and_end_on(_ps_dots[_i].get_center(), _ps_dots[_j].get_center()))",
                    "            _ps_bonds.add(_line)",
                ])
                if start is not None:
                    lines.append(_wait_guard(start))
                lines.extend([
                    "        self.play(LaggedStart(*[FadeIn(d) for d in _ps_dots], lag_ratio=0.05), run_time=0.8)",
                    "        self.add(_ps_bonds)",
                    "        self.wait(2.0)",
                    "        _ps_dots.remove_updater(_ps_dots.updaters[0])",
                    "        for _b in _ps_bonds:",
                    "            if _b.updaters:",
                    "                _b.remove_updater(_b.updaters[0])",
                    "        _scene_mobjs.extend(_ps_dots)",
                    "        _scene_mobjs.extend(_ps_bonds)",
                ])
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append("        self.play(FadeOut(_ps_dots), FadeOut(_ps_bonds), run_time=0.5)")
                lines.extend([
                    "        objs.append(_ps_dots)",
                    "        objs.append(_ps_bonds)",
                ])
                if el_id:
                    lines.append(f"        idmap['{el_id}_dots'] = _ps_dots")

            else:
                # Generic fallback
                lines.append(
                    f"        {var} = Text('{content}').scale(0.6).move_to({p})"
                )
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                if start is not None:
                    lines.append(_wait_guard(start))
                lines += [
                    f"        self.play(Write({var}))",
                    f"        _scene_mobjs.append({var})",
                ]
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append(f"        self.play(FadeOut({var}))")
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

        # ── Context-aware camera zoom storytelling ─────────────────────────────
        lines += [
            "        if _zoom_any:",
            "            if _is_3d_scene:",
            "                self.move_camera(zoom=_cam_zoom * 1.14, run_time=0.9)",
            "                self.move_camera(zoom=_cam_zoom, run_time=0.8)",
            "            elif hasattr(self, 'camera') and hasattr(self.camera, 'frame'):",
            "                _focus_obj = None",
            "                if _zoom_tire:",
            "                    _tire_contact_pt = ORIGIN + 0.3*DOWN",
            "                    _contact_glow = Circle(radius=0.12, color='#FF6B35', stroke_width=0)",
            "                    _contact_glow.set_fill('#FF6B35', opacity=0.5)",
            "                    _contact_glow.move_to(_tire_contact_pt)",
            "                    self.play(FadeIn(_contact_glow), run_time=0.3)",
            "                    _zoom_box = Rectangle(width=1.2, height=0.9, color='#FFD700', stroke_width=1.5)",
            "                    _zoom_box.move_to(_tire_contact_pt)",
            "                    _zoom_box_label = Text('Contact Patch', font_size=12, color='#FFD700').next_to(_zoom_box, UP, buff=0.05)",
            "                    self.play(Create(_zoom_box), Write(_zoom_box_label), run_time=0.4)",
            "                    _orig_w = self.camera.frame.width",
            "                    self.play(self.camera.frame.animate.move_to(_tire_contact_pt).set(width=1.8), run_time=1.2)",
            "                    _contact_arrow_f = Arrow(0.3*LEFT, 0.3*RIGHT, color='#FF4500', stroke_width=4, buff=0.02)",
            "                    _contact_arrow_f.move_to(_tire_contact_pt + 0.15*DOWN)",
            "                    _contact_arrow_f_label = Text('Friction', font_size=10, color='#FF4500').next_to(_contact_arrow_f, DOWN, buff=0.02)",
            "                    _contact_arrow_N = Arrow(0.3*UP, 0.15*DOWN, color='#00FF88', stroke_width=3, buff=0.02)",
            "                    _contact_arrow_N.move_to(_tire_contact_pt)",
            "                    _contact_arrow_N_label = Text('Normal', font_size=10, color='#00FF88').next_to(_contact_arrow_N, UP, buff=0.02)",
            "                    _road_texture = VGroup(*[Line(_tire_contact_pt + 0.4*LEFT + i*0.12*RIGHT, _tire_contact_pt + 0.4*LEFT + i*0.12*RIGHT + 0.06*DOWN, stroke_width=0.5, color='#888') for i in range(7)])",
            "                    self.play(FadeIn(_road_texture), Create(_contact_arrow_f), Write(_contact_arrow_f_label), Create(_contact_arrow_N), Write(_contact_arrow_N_label), run_time=0.8)",
            "                    self.wait(1.0)",
            "                    self.play(FadeOut(_road_texture), FadeOut(_contact_arrow_f), FadeOut(_contact_arrow_f_label), FadeOut(_contact_arrow_N), FadeOut(_contact_arrow_N_label), FadeOut(_contact_glow), FadeOut(_zoom_box), FadeOut(_zoom_box_label), run_time=0.5)",
            "                    self.play(self.camera.frame.animate.set(width=_orig_w).move_to(ORIGIN), run_time=0.8)",
            "                elif _zoom_bubble or _zoom_graph or _zoom_equation:",
            "                    _focus_obj = objs[-1] if objs else None",
            "                if _focus_obj is not None:",
            "                    _orig_w = self.camera.frame.width",
            "                    _base_w = float(getattr(_focus_obj, 'width', 4.0) or 4.0)",
            "                    _target_w = max(4.2, min(9.5, _base_w * 2.4))",
            "                    self.play(self.camera.frame.animate.move_to(_focus_obj).set(width=_target_w), run_time=1.0)",
            "                    self.play(self.camera.frame.animate.set(width=_orig_w).move_to(ORIGIN), run_time=0.8)",
            "        if _zoom_zoom_trigger:",
            "            if _is_3d_scene:",
            "                self.move_camera(phi=50*DEGREES, theta=-30*DEGREES, run_time=1.0)",
            "                self.wait(0.5)",
            "                self.move_camera(phi=70*DEGREES, theta=-45*DEGREES, run_time=0.8)",
            "        if _zoom_car or _zoom_road:",
            "            if _is_3d_scene:",
            "                self.set_camera_orientation(phi=75*DEGREES, theta=-30*DEGREES)",
            "                self.begin_ambient_camera_rotation(rate=0.1)",
            "                self.wait(2)",
            "                self.stop_ambient_camera_rotation()",
            "        if _zoom_heat_friction:",
            "            _heat_base = Circle(radius=0.25, color='#FF4500').move_to(ORIGIN)",
            "            _heat_base.set_fill('#FF4500', opacity=0.4)",
            "            _heat_ring = Circle(radius=0.4, color='#FF6B35', stroke_width=2, stroke_opacity=0.6).move_to(ORIGIN)",
            "            _heat_label_prefix = 'Heat from friction!' if not _zoom_tire else 'Thermal energy at tire contact!'",
            "            _heat_text = Text(_heat_label_prefix, font_size=0.35, color='#FF6B35').next_to(_heat_ring, UP, buff=0.05)",
            "            _heat_arrow = always_redraw(lambda: Arrow(ORIGIN + 0.1*LEFT, ORIGIN + 0.1*RIGHT, color='#FF4500', stroke_width=3, buff=0.05))",
            "            self.play(FadeIn(_heat_base), Create(_heat_ring), Write(_heat_text), run_time=0.6)",
            "            _heat_base.add_updater(lambda m, dt: m.set_opacity(0.3 + 0.3*math.sin(3*dt)))",
            "            _heat_ring.add_updater(lambda m, dt: m.scale(1 + 0.15*math.sin(2*dt)))",
            "            self.wait(1.2)",
            "            _heat_base.remove_updater(_heat_base.updaters[0])",
            "            _heat_ring.remove_updater(_heat_ring.updaters[0])",
            "            self.play(FadeOut(_heat_base), FadeOut(_heat_ring), FadeOut(_heat_text), run_time=0.5)",
            "        if _zoom_3d_object:",
            "            if _is_3d_scene:",
            "                self.begin_ambient_camera_rotation(rate=0.12)",
            "                self.wait(2.5)",
            "                self.stop_ambient_camera_rotation()",
            "        if _zoom_coin:",
            "            if _is_3d_scene:",
            "                _coin_spin = Sphere(radius=0.4, resolution=(20, 20)).move_to(ORIGIN)",
            "                _coin_spin.set_fill('#FFD700')",
            "                _coin_spin.set_reflectiveness(0.8)",
            "                self.play(Create(_coin_spin), run_time=1.2)",
            "                self.begin_ambient_camera_rotation(rate=0.3)",
            "                self.wait(2)",
            "                self.stop_ambient_camera_rotation()",
        ]

        # ── End-of-scene wait — use resolved scene duration ────────────────────
        lines.append(
            f"        if t < {scene_sd:.3f}: self.wait({scene_sd:.3f} - t); t = {scene_sd:.3f}"
        )

        # ── Scene wipe: keep watermark + subject badge ─────────────────────────
        lines += [
            "        _to_remove = [m for m in _scene_mobjs if m in self.mobjects]",
            "        if _to_remove:",
            "            self.play(FadeOut(Group(*_to_remove)))",
            "        self.wait(0.3)",
        ]

    lines.append("        self.wait(0.5)")
    return "\n".join(lines) + "\n"


# ══════════════════════════════════════════════════════════════════════════════
# RENDERER
# ══════════════════════════════════════════════════════════════════════════════


def render_with_manim(
    script_path: Path,
    scene_name: str,
    out_path: Optional[Path] = None,
    quality: Optional[str] = None,
) -> Path:
    ffmpeg_bin = os.getenv("FFMPEG_BINARY")
    env = os.environ.copy()
    if ffmpeg_bin and os.path.exists(ffmpeg_bin):
        ffmpeg_dir = str(Path(ffmpeg_bin).parent)
        if ffmpeg_dir not in env["PATH"]:
            env["PATH"] = ffmpeg_dir + os.pathsep + env["PATH"]

    quality_flag = {
        "low": "-ql",
        "medium": "-qm",
        "high": "-qh",
        "production": "-qp",
    }.get((quality or os.getenv("MANIM_QUALITY", "medium")).lower(), "-qm")

    output_flag: List[str] = ["-o", out_path.name] if out_path else []
    cmd = [
        sys.executable,
        "-m",
        "manim",
        quality_flag,
        *output_flag,
        str(script_path),
        scene_name,
    ]

    # Increase timeout for long 10-min renders (default 30 min)
    timeout_seconds = int(os.getenv("MANIM_TIMEOUT", "1800"))
    try:
        print(f"[manim_adapter] Starting Manim render ({timeout_seconds}s timeout)…")
        subprocess.run(cmd, check=True, env=env, timeout=timeout_seconds)
        print("[manim_adapter] Render completed successfully")
    except subprocess.TimeoutExpired:
        raise RuntimeError(
            f"Manim rendering exceeded {timeout_seconds}s timeout. "
            "Try --quality low or split into shorter segments."
        )

    produced_dir = Path("media") / "videos" / script_path.stem
    candidates = sorted(
        produced_dir.rglob("*.mp4"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if out_path:
        if candidates:
            candidates[0].replace(out_path)
        return out_path
    if not candidates:
        raise RuntimeError("Could not locate rendered video file.")
    return candidates[0]


def render_scenes_parallel(
    data: Dict[str, Any],
    workdir: Path,
    quality: Optional[str] = None,
    max_workers: int = 4,
) -> Path:
    """Render each scene as an independent Manim script, run them in parallel, then concatenate.

    Returns path to the final stitched video.
    """
    scenes = data.get("animation_plan", {}).get("scenes", [])
    if not scenes:
        raise ValueError("No scenes in animation plan")

    scene_dir = workdir / "scenes"
    scene_dir.mkdir(parents=True, exist_ok=True)
    video_dir = workdir / "scene_videos"
    video_dir.mkdir(parents=True, exist_ok=True)

    scene_paths: List[Path] = []
    for sidx, sc in enumerate(scenes, start=1):
        scene_data = {"solution": data.get("solution", {}), "animation_plan": {"scenes": [sc]}}
        script_text = generate_scene_script(scene_data)
        script_path = scene_dir / f"scene_{sidx:03d}.py"
        script_path.write_text(script_text, encoding="utf-8")
        scene_paths.append(script_path)

    def _render_one(sp: Path, idx: int) -> Path:
        out_vid = video_dir / f"scene_{idx:03d}.mp4"
        try:
            render_with_manim(sp, "GeneratedScene", out_path=out_vid, quality=quality)
            print(f"[parallel] Scene {idx} rendered -> {out_vid}")
            return out_vid
        except Exception as e:
            print(f"[parallel] Scene {idx} FAILED: {e}")
            try:
                dummy = video_dir / f"scene_{idx:03d}_blank.mp4"
                subprocess.run(
                    [
                        shutil.which("ffmpeg") or "ffmpeg", "-y", "-f", "lavfi",
                        "-i", "color=c=#121212:s=1280x720:d=5",
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", str(dummy),
                    ],
                    check=True, capture_output=True,
                )
                return dummy
            except Exception:
                raise

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        fut_map = {pool.submit(_render_one, sp, i + 1): i + 1 for i, sp in enumerate(scene_paths)}
        results = {}
        for fut in concurrent.futures.as_completed(fut_map):
            idx = fut_map[fut]
            results[idx] = fut.result()

    sorted_videos = [results[i] for i in sorted(results.keys())]
    concat_file = workdir / "concat_list.txt"
    concat_file.write_text(
        "\n".join(f"file '{v.resolve()}'".replace("\\", "/") for v in sorted_videos),
        encoding="utf-8",
    )
    stitched = workdir / "stitched.mp4"
    subprocess.run(
        [shutil.which("ffmpeg") or "ffmpeg", "-y", "-f", "concat", "-safe", "0",
         "-i", str(concat_file), "-c", "copy", str(stitched)],
        check=True, capture_output=True,
    )
    print(f"[parallel] Stitched {len(sorted_videos)} scenes -> {stitched}")
    return stitched


def generate_mcq_from_plan(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Auto-generate multiple-choice questions from a solution plan.

    Scans solution steps for key concepts and produces MCQ items with
    distractors, correct answer, and explanations.
    """
    solution = data.get("solution", {})
    steps = solution.get("steps", [])
    topic = solution.get("topic", "") or solution.get("question", "")
    mcqs: List[Dict[str, Any]] = []

    concept_register: List[str] = []
    step_texts = " ".join(
        f"{s.get('title', '')} {s.get('explanation', '')} {s.get('latex', '') or ''}"
        for s in steps if isinstance(s, dict)
    ).lower()

    key_terms = {
        "physics": [
            ("force", "Which quantity is described by mass times acceleration?",
             ["Force", "Velocity", "Momentum", "Energy"], "Force"),
            ("newton", "Newton's second law states that force equals:",
             ["mass x velocity", "mass x acceleration", "mass / acceleration", "acceleration / mass"],
             "mass x acceleration"),
            ("friction", "Friction always acts:",
             ["In the direction of motion", "Opposite to the direction of motion",
              "Perpendicular to motion", "Upward"], "Opposite to the direction of motion"),
            ("energy", "The SI unit of energy is:",
             ["Newton", "Joule", "Watt", "Pascal"], "Joule"),
            ("momentum", "Momentum is defined as:",
             ["mass x velocity", "mass x acceleration", "force x time", "energy / time"],
             "mass x velocity"),
        ],
        "chemistry": [
            ("mole", "One mole of a substance contains approximately:",
             ["6.022 x 10^23 particles", "3.14 x 10^23 particles",
              "1.0 x 10^24 particles", "6.022 x 10^22 particles"],
             "6.022 x 10^23 particles"),
            ("acid", "A substance with pH less than 7 is called:",
             ["Base", "Acid", "Salt", "Neutral"], "Acid"),
        ],
        "mathematics": [
            ("derivative", "The derivative of x^2 with respect to x is:",
             ["x", "2x", "x^2", "2"], "2x"),
            ("integral", "The integral of 2x dx is:",
             ["x^2 + C", "2x^2 + C", "x + C", "x^3/3 + C"], "x^2 + C"),
        ],
        "economics": [
            ("demand", "When price increases, quantity demanded typically:",
             ["Increases", "Decreases", "Stays the same", "Doubles"], "Decreases"),
            ("supply", "When price increases, quantity supplied typically:",
             ["Increases", "Decreases", "Stays the same", "Halves"], "Increases"),
        ],
    }

    subject = str(solution.get("subject", "physics")).lower()
    for term, (q, options, correct) in key_terms.get(subject, key_terms["physics"]):
        if term in step_texts or term in topic.lower():
            mcqs.append({
                "question": q,
                "options": options,
                "correct": correct,
                "explanation": f"This tests understanding of '{term}' from the lesson on {topic if topic else subject}.",
            })
            if len(mcqs) >= 3:
                break

    for i in range(min(2, len(steps))):
        s = steps[i] if isinstance(steps[i], dict) else {}
        title = s.get("title", "")
        explanation = s.get("explanation", "")
        if title and len(title) > 5:
            words = title.split()
            blank_q = f"In the step '{title}', what is the key concept?"
            opts = [title]
            for j in range(1, min(4, len(steps))):
                alt = steps[(i + j) % len(steps)]
                if isinstance(alt, dict):
                    opts.append(alt.get("title", f"Alternative {j}"))
            while len(opts) < 4:
                opts.append(f"Distractor {len(opts)}")
            import random; random.shuffle(opts)
            mcqs.append({
                "question": blank_q,
                "options": opts,
                "correct": title,
                "explanation": explanation or f"This step covers {title}.",
            })

    return mcqs[:5]


def add_chapter_markers(video_path: Path, data: Dict[str, Any], out_path: Optional[Path] = None) -> Path:
    """Add chapter markers to an MP4 video based on scene descriptions.

    Uses ffmpeg metadata to create named chapters for video navigation.
    """
    scenes = data.get("animation_plan", {}).get("scenes", [])
    if not scenes:
        return video_path

    out = out_path or video_path
    metadata_file = video_path.parent / "chapter_meta.txt"

    lines = [";FFMETADATA1"]
    time_sec = 0.0
    for sidx, sc in enumerate(scenes):
        desc = sc.get("description", f"Scene {sidx + 1}")[:80]
        dur = sc.get("duration_seconds", 10.0)
        ts_start = int(time_sec * 1000)
        ts_end = int((time_sec + dur) * 1000)
        lines.append("[CHAPTER]")
        lines.append(f"TIMEBASE=1/1000")
        lines.append(f"START={ts_start}")
        lines.append(f"END={ts_end}")
        lines.append(f"title={desc}")
        time_sec += dur

    metadata_file.write_text("\n".join(lines), encoding="utf-8")

    tmp_out = out.with_suffix(".tmp_chapters.mp4")
    subprocess.run(
        [shutil.which("ffmpeg") or "ffmpeg", "-y", "-i", str(video_path),
         "-i", str(metadata_file), "-map_metadata", "1",
         "-codec", "copy", str(tmp_out)],
        check=True, capture_output=True,
    )
    tmp_out.replace(out)
    print(f"[chapters] Added {len(scenes)} chapter markers -> {out}")
    return out


# ══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY-POINT
# ══════════════════════════════════════════════════════════════════════════════


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate and render a Manim scene from structured JSON (10-min edition)"
    )
    parser.add_argument("json", help="Path to structured JSON (SolverOutput)")
    parser.add_argument("--out", dest="out", default=None, help="Output mp4 path")
    parser.add_argument(
        "--quality",
        dest="quality",
        default=None,
        help="Manim quality: low|medium|high|production",
    )
    parser.add_argument(
        "--durations",
        dest="durations",
        default=None,
        help="Optional JSON file with per-scene durations (seconds)",
    )
    parser.add_argument(
        "--no-validate",
        dest="no_validate",
        action="store_true",
        help="Skip 10-minute duration validation",
    )
    args = parser.parse_args()

    data = json.loads(Path(args.json).read_text(encoding="utf-8"))

    # Run duration validation before spending time generating/rendering
    if not args.no_validate:
        validate_duration(data)

    scene_durations: Optional[List[float]] = None
    if args.durations:
        scene_durations = json.loads(Path(args.durations).read_text(encoding="utf-8"))

    script_text = generate_scene_script(data, scene_durations=scene_durations)

    gen_dir = Path("scripts") / "_generated"
    gen_dir.mkdir(parents=True, exist_ok=True)
    script_path = gen_dir / "generated_scene.py"
    script_path.write_text(script_text, encoding="utf-8")

    out_path = Path(args.out) if args.out else None
    video = render_with_manim(
        script_path,
        "GeneratedScene",
        out_path=out_path,
        quality=args.quality,
    )
    print(f"Rendered video: {video}")


if __name__ == "__main__":
    main()
