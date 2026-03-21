import argparse
import json
import os
import re
import subprocess
import sys
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
    "bg":               "#121212",   # Charcoal Black  — main background
    "bg_navy":          "#0B1C2D",   # Dark Navy       — alt background

    # ── Problem / Question ────────────────────────────────────────────────────
    "problem_title":    "#FFD700",   # Gold            — scene title / question heading
    "question_action":  "#FF6B35",   # Orange-Red      — "find", "calculate", "?", "solve"

    # ── Given / Known Data ────────────────────────────────────────────────────
    "given_label":      "#78D5E3",   # Sky Cyan        — "Given:", "Known:"
    "given_value":      "#4FC3F7",   # Light Blue      — known quantities  m = 5 kg
    "given_value_alt":  "#64B5F6",   # Sky Blue        — alternating given value

    # ── Variables & Constants ─────────────────────────────────────────────────
    "variable":         "#C792EA",   # Lavender        — algebraic variables (x, v, F …)
    "constant":         "#FF9F43",   # Warm Orange     — physical constants (g, c, π, e)

    # ── Formulas / Laws / Theorems ────────────────────────────────────────────
    "formula_title":    "#BB86FC",   # Purple          — law name: "Newton's 2nd Law"
    "formula_body":     "#E040FB",   # Bright Magenta  — the formula itself  F = ma
    "formula_alt":      "#B39DDB",   # Soft Violet     — secondary formula line
    "derivation_step":  "#B39DDB",   # Soft Violet     — derivation line alternates

    # ── Step Labels ───────────────────────────────────────────────────────────
    "step_label":       "#82AAFF",   # Periwinkle      — "Step 1:"
    "step_label_2":     "#89DDFF",   # Ice Blue        — "Step 2:"
    "step_label_3":     "#7EC8E3",   # Cornflower      — "Step 3+"
    "step_label_4":     "#A5C8E1",   # Steel Blue      — "Step 4"
    "step_label_5":     "#80CBC4",   # Teal            — "Step 5+"

    # ── Algebraic Work ────────────────────────────────────────────────────────
    "algebra":          "#FFFFFF",   # White           — general algebra lines
    "algebra_alt":      "#E0E0E0",   # Off-White       — alternating algebra line
    "substitution":     "#FFE082",   # Pale Yellow     — substituting known values in
    "intermediate":     "#A5D6A7",   # Soft Green      — intermediate results

    # ── Final Answer ──────────────────────────────────────────────────────────
    "answer_label":     "#69F0AE",   # Mint Green      — "Therefore:", "Answer:"
    "answer_value":     "#00FF6A",   # Bright Green    — the final numerical answer
    "answer_alt":       "#00E676",   # Emerald         — alternate answer accent

    # ── Units ─────────────────────────────────────────────────────────────────
    "unit":             "#90A4AE",   # Slate Gray      — m/s, kg, N, J (non-distracting)

    # ── Summary ───────────────────────────────────────────────────────────────
    "summary_bullet":   "#B2EBF2",   # Ice Blue        — summary takeaway points
    "summary_title":    "#80DEEA",   # Aqua            — "Summary" heading

    # ── New 10-min roles ──────────────────────────────────────────────────────
    "mistake_warning":  "#FF5252",   # Red             — "Common mistake:", "Watch out:"
    "real_world":       "#FFD740",   # Amber           — real-world application text
    "history_note":     "#80DEEA",   # Aqua            — historical context
    "practice_q":       "#C792EA",   # Lavender        — practice problem text

    # ── Diagrams / Shapes ─────────────────────────────────────────────────────
    "shape_primary":    "#448AFF",   # Bright Blue
    "shape_secondary":  "#40C4FF",   # Cyan
    "shape_tertiary":   "#18FFFF",   # Aqua
    "shape_fill":       "#1A237E",   # Deep Indigo

    # ── Graphs & Axes ─────────────────────────────────────────────────────────
    "axis":             "#CFD8DC",   # Light Gray
    "grid":             "#37474F",   # Dark Gray

    # ── Highlights ────────────────────────────────────────────────────────────
    "highlight":        "#FFD700",   # Gold
    "highlight_alt":    "#FF4081",   # Pink

    # ── Scene Headers ─────────────────────────────────────────────────────────
    "header_problem":   "#FFD700",
    "header_given":     "#4FC3F7",
    "header_formula":   "#BB86FC",
    "header_step":      "#82AAFF",
    "header_answer":    "#00FF6A",
    "header_summary":   "#80DEEA",
    "header_mistake":   "#FF5252",
    "header_realworld": "#FFD740",
    "header_history":   "#80DEEA",
    "header_practice":  "#C792EA",
    "header_default":   "#ECEFF1",
}

# Graph curve cycling palette — each curve on the same axes gets a unique colour
CURVE_COLORS: List[str] = [
    "#FF5252",   # Red
    "#40C4FF",   # Cyan
    "#FFD740",   # Amber
    "#69F0AE",   # Mint
    "#FF4081",   # Pink
    "#B2FF59",   # Lime
    "#EA80FC",   # Light Purple
    "#FF6D00",   # Deep Orange
]

# Shape fill colours — cycle for multiple shapes in one scene
SHAPE_FILL_COLORS: List[str] = [
    "#448AFF",   # Blue
    "#FF5252",   # Red
    "#FFD740",   # Amber
    "#69F0AE",   # Mint
    "#E040FB",   # Magenta
    "#40C4FF",   # Cyan
]

# Backward-compat alias
EDUCATION_COLORS: Dict[str, str] = {
    "background":     COLORS["bg"],
    "background_alt": COLORS["bg_navy"],
    "question":       COLORS["problem_title"],
    "question_alt":   COLORS["question_action"],
    "value":          COLORS["given_value"],
    "value_alt":      COLORS["given_value_alt"],
    "formula":        COLORS["formula_title"],
    "formula_alt":    COLORS["formula_alt"],
    "step":           COLORS["algebra"],
    "step_alt":       COLORS["intermediate"],
    "answer":         COLORS["answer_value"],
    "answer_alt":     COLORS["answer_label"],
    "unit":           COLORS["unit"],
    "accent_red":     "#FF5252",
    "accent_green":   COLORS["intermediate"],
    "accent_blue":    COLORS["shape_primary"],
    "accent_orange":  COLORS["constant"],
}

# Default seconds per scene when no explicit duration is provided.
# For 10-min videos each scene should hold for ~45 s.
DEFAULT_SCENE_WAIT: float = 45.0

# ─── Position helpers ────────────────────────────────────────────────────────

POSITION_MAP: Dict[str, str] = {
    "center":       "ORIGIN",
    "top":          "UP",
    "bottom":       "DOWN",
    "left":         "LEFT",
    "right":        "RIGHT",
    "top-left":     "UP+LEFT",
    "top-right":    "UP+RIGHT",
    "bottom-left":  "DOWN+LEFT",
    "bottom-right": "DOWN+RIGHT",
}

# ─── Element type buckets ────────────────────────────────────────────────────
_VISUAL_TYPES = frozenset({
    "axes", "graph", "vectorfield", "streamlines",
    "parametric3d", "arrow", "vector",
})
_SHAPE_TYPES = frozenset({
    "circle", "annulus", "rectangle", "polygon", "ellipse",
})
_TEXT_TYPES = frozenset({
    "text", "mathtex", "latex", "",
})


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
    estimated_minutes = total_words / 130.0   # 130 wpm natural teaching pace

    # Sum per-scene duration_seconds if present
    total_scene_seconds = sum(
        float(sc.get("duration_seconds") or DEFAULT_SCENE_WAIT)
        for sc in scenes
    )

    # Read schema-level fields
    ap              = data.get("animation_plan", {})
    schema_scenes   = ap.get("total_scenes", len(scenes))
    schema_duration = ap.get("estimated_duration_seconds", 0)
    schema_minutes  = data.get("solution", {}).get("duration_estimate_minutes", 0)

    print("-" * 60)
    print("[phiversity] Pre-render duration validation")
    print(f"  Scenes in JSON  : {len(scenes)}  (schema says {schema_scenes}, min 14)")
    print(f"  Voiceover words : {total_words}  (min 1 300)")
    print(f"  Estimated length: {estimated_minutes:.1f} min  (schema says {schema_minutes}, min 10.0)")
    print(f"  Scene total     : {total_scene_seconds:.0f} s  (schema says {schema_duration}, min 600 s)")

    if len(scenes) < 14:
        print(f"  WARNING: only {len(scenes)} scenes -- below 14-scene minimum")
    if total_words < 1300:
        print(f"  WARNING: only {total_words} voiceover words -- below 1 300-word minimum")
    if estimated_minutes < 10.0:
        print(f"  WARNING: estimated {estimated_minutes:.1f} min -- below 10-minute minimum")
    if total_scene_seconds < 600:
        print(f"  WARNING: scene total {total_scene_seconds:.0f} s -- below 600 s minimum")
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
    if any(k in key for k in ("real_world", "application", "where", "industry",
                               "lab_note", "laboratory")):
        return _q(COLORS["header_realworld"])
    if any(k in key for k in ("hook", "motivation", "why this", "why does",
                               "wonder", "imagine")):
        return _q(COLORS["header_problem"])
    if any(k in key for k in ("background", "history", "context", "origin",
                               "derivation", "proof", "justif", "where the",
                               "molecular", "stoich", "thermo", "geometric",
                               "connection", "edge_case", "special_case",
                               "market", "elasticity", "policy", "data_context")):
        return _q(COLORS["header_history"])
    if any(k in key for k in ("practice", "exercise", "try", "challenge")):
        return _q(COLORS["header_practice"])
    if any(k in key for k in ("second_example", "variation", "try this")):
        return _q(COLORS["header_answer"])
    if any(k in key for k in ("unit", "dimension", "analysis", "check")):
        return _q(COLORS["header_given"])
    if any(k in key for k in ("force_diagram", "free_body", "energy_diagram",
                               "physics_graph", "supply_demand")):
        return _q(COLORS["header_formula"])

    # Original scene types
    if any(k in key for k in ("problem", "question", "intro")):
        return _q(COLORS["header_problem"])
    if any(k in key for k in ("given", "known", "data")):
        return _q(COLORS["header_given"])
    if any(k in key for k in ("formula", "law", "theorem", "concept", "principle")):
        return _q(COLORS["header_formula"])
    if any(k in key for k in ("step", "solving", "calculation", "substitute")):
        m = re.search(r'(\d+)', key)
        n = int(m.group(1)) if m else 1
        shades = [
            COLORS["step_label"], COLORS["step_label_2"], COLORS["step_label_3"],
            COLORS["step_label_4"], COLORS["step_label_5"],
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
    cl        = (content or "").lower()
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
    if any(k in scene_key for k in ("background", "history", "context", "origin",
                                     "derivation", "proof", "justif",
                                     "where the formula")):
        if index == 1:
            return _q(COLORS["history_note"])
        return _q(COLORS["formula_title"] if index % 2 == 0 else COLORS["formula_alt"])

    # Unit / dimensional analysis
    if any(k in scene_key for k in ("unit", "dimension", "unit_analysis",
                                     "dimensional")):
        if index == 1:
            return _q(COLORS["given_label"])
        return _q(COLORS["substitution"] if index % 2 == 0 else COLORS["intermediate"])

    # Common mistakes
    if any(k in scene_key for k in ("mistake", "error", "common", "watch", "wrong")):
        return _q(COLORS["mistake_warning"])

    # Real-world application / lab note
    if any(k in scene_key for k in ("real_world", "application", "where",
                                     "industry", "lab_note", "laboratory")):
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
        return _q(COLORS["summary_bullet"] if index % 2 == 0 else COLORS["summary_title"])

    # Physics extensions
    if any(k in scene_key for k in ("force_diagram", "free_body", "energy_diagram")):
        return _q(COLORS["shape_primary"] if index % 2 == 0 else COLORS["shape_secondary"])
    if any(k in scene_key for k in ("physics_graph", "motion_graph", "wave_graph")):
        return _q(CURVE_COLORS[index % len(CURVE_COLORS)])
    if any(k in scene_key for k in ("special_case", "special case", "limit",
                                     "extreme")):
        return _q(COLORS["constant"] if index % 2 == 0 else COLORS["formula_alt"])

    # Chemistry extensions
    if any(k in scene_key for k in ("molecular", "stoich", "thermo",
                                     "reaction", "equilibrium")):
        if index == 1:
            return _q(COLORS["formula_title"])
        return _q(COLORS["formula_body"] if index % 2 == 0 else COLORS["formula_alt"])
    if any(k in scene_key for k in ("lab_note", "safety")):
        return _q(COLORS["real_world"])

    # Maths extensions
    if any(k in scene_key for k in ("proof", "theorem", "justif")):
        return _q(COLORS["formula_body"] if index % 2 == 0 else COLORS["derivation_step"])
    if any(k in scene_key for k in ("geometric", "geometric_view")):
        return _q(CURVE_COLORS[index % len(CURVE_COLORS)])
    if any(k in scene_key for k in ("edge_case", "domain", "range", "undefined")):
        return _q(COLORS["constant"])
    if any(k in scene_key for k in ("connection", "related", "branch")):
        return _q(COLORS["history_note"])

    # Economics extensions
    if any(k in scene_key for k in ("market", "supply", "demand",
                                     "equilibrium", "supply_demand")):
        if index == 1:
            return _q(COLORS["real_world"])
        return _q(CURVE_COLORS[index % len(CURVE_COLORS)])
    if any(k in scene_key for k in ("elasticity", "multiplier", "inelastic")):
        return _q(COLORS["given_value"] if index % 2 == 0 else COLORS["given_value_alt"])
    if any(k in scene_key for k in ("policy", "government", "fiscal", "monetary")):
        return _q(COLORS["real_world"] if index % 2 == 0 else COLORS["constant"])
    if any(k in scene_key for k in ("data", "empirical", "statistic", "gdp")):
        return _q(COLORS["history_note"])

    # ── 2b. Original scene-context shortcuts ─────────────────────────────────
    if any(k in scene_key for k in ("given", "known", "data")):
        if any(kw in cl for kw in ("given:", "known:", "given", "known")):
            return _q(COLORS["given_label"])
        return _q(COLORS["given_value"] if index % 2 == 0 else COLORS["given_value_alt"])

    if any(k in scene_key for k in ("formula", "law", "theorem", "concept",
                                     "principle")):
        if index == 1:
            return _q(COLORS["formula_title"])
        return _q(COLORS["formula_body"] if index % 2 == 0 else COLORS["formula_alt"])

    if any(k in scene_key for k in ("answer", "result", "final", "solution")):
        if any(kw in cl for kw in ("therefore", "answer:", "hence", "so,")):
            return _q(COLORS["answer_label"])
        return _q(COLORS["answer_value"] if index % 2 == 0 else COLORS["answer_alt"])

    if re.search(r'step[\s_]*\d', scene_key):
        if index == 1:
            m2 = re.search(r'step[\s_]*(\d+)', scene_key)
            n  = int(m2.group(1)) if m2 else index
            shades = [
                COLORS["step_label"], COLORS["step_label_2"], COLORS["step_label_3"],
                COLORS["step_label_4"], COLORS["step_label_5"],
            ]
            return _q(shades[(n - 1) % len(shades)])
        if re.search(r'=\s*[\-\d\(]', cl):
            return _q(COLORS["substitution"])
        return _q(COLORS["algebra"] if index % 2 == 0 else COLORS["algebra_alt"])

    # ── 3. Fine-grained content-keyword matching ──────────────────────────────
    if any(kw in cl for kw in ["find ", "solve", "calculate", "determine",
                                 "what is", "?"]):
        return _q(COLORS["question_action"])
    if any(kw in cl for kw in ["problem", "question", "given that",
                                 "a block", "an object"]):
        return _q(COLORS["problem_title"])
    if any(kw in cl for kw in ["given:", "known:", "given", "known"]):
        return _q(COLORS["given_label"])
    if re.search(r'[a-z_]+\s*=\s*[\d\.\-]', cl):
        return _q(COLORS["given_value"] if index % 2 == 0 else COLORS["given_value_alt"])
    if any(kw in cl for kw in ["\\pi", "pi", "\\hbar", "= 9.8", "= 9.81",
                                 "= 6.67", "planck", "boltzmann", "avogadro"]):
        return _q(COLORS["constant"])
    if any(kw in cl for kw in ["law", "theorem", "principle", "formula",
                                 "newton", "ohm", "faraday", "hooke",
                                 "conservation"]):
        return _q(COLORS["formula_title"])
    if any(kw in cl for kw in ["\\frac", "\\vec", "\\int", "\\sum",
                                 "\\sqrt", "\\Delta"]):
        return _q(COLORS["formula_body"] if index % 2 == 0 else COLORS["formula_alt"])
    if re.match(r'^step\s*\d', cl):
        step_match = re.search(r'\d+', cl)
        n   = int(step_match.group()) if step_match else 1
        shd = [COLORS["step_label"], COLORS["step_label_2"], COLORS["step_label_3"],
               COLORS["step_label_4"], COLORS["step_label_5"]]
        return _q(shd[(n - 1) % len(shd)])
    if re.search(r'=\s*[\(\-\d]', cl) and re.search(r'\d', cl):
        return _q(COLORS["substitution"])
    if "=" in cl and re.search(r'\d', cl):
        return _q(COLORS["intermediate"])
    if any(kw in cl for kw in ["therefore", "answer:", "hence,", "so,"]):
        return _q(COLORS["answer_label"])
    if any(kw in cl for kw in ["answer", "result", "solution", "final"]):
        return _q(COLORS["answer_value"])
    if any(kw in cl for kw in ["\\text{ m", "\\text{ kg", "m/s", "kg", " hz"]):
        return _q(COLORS["unit"])
    if any(kw in cl for kw in ["in summary", "key point", "remember",
                                 "note that", "recap"]):
        return _q(COLORS["summary_bullet"])
    # Mistake / warning keywords
    if any(kw in cl for kw in ["mistake", "wrong", "incorrect", "error",
                                 "watch out", "do not", "don't", "avoid",
                                 "never", "common error"]):
        return _q(COLORS["mistake_warning"])

    # ── 4. Positional fallback ────────────────────────────────────────────────
    fallback = [
        COLORS["algebra"], COLORS["algebra_alt"],
        COLORS["intermediate"], COLORS["substitution"],
    ]
    return _q(fallback[index % len(fallback)])


# ══════════════════════════════════════════════════════════════════════════════
# SAFE STRING HELPER
# ══════════════════════════════════════════════════════════════════════════════

def _safe_str(s: str) -> str:
    """Escape single quotes and soft-wrap plain text (non-LaTeX) for embedding."""
    cleaned = s.replace("'", "\\'")
    if len(cleaned) > 50:
        cleaned = "\\n".join(textwrap.wrap(cleaned, width=50))
    else:
        cleaned = cleaned.replace("\n", "\\n")
    return cleaned


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
    text_indices:   List[int] = []
    visual_indices: List[int] = []
    shape_indices:  List[int] = []
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
    has_text   = bool(scene_has_text)

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
                MEDIA_POS = ["-3.8*RIGHT + 2.3*UP", "-3.8*RIGHT + 0.0*UP", "-3.8*RIGHT + -2.3*UP"]
            else:
                MEDIA_POS = [
                    "-5.3*RIGHT + 2.1*UP", "-2.3*RIGHT + 2.1*UP",
                    "-5.3*RIGHT + -2.1*UP", "-2.3*RIGHT + -2.1*UP",
                    "-5.3*RIGHT + 0.0*UP", "-2.3*RIGHT + 0.0*UP"
                ]
        else:
            if num_media == 1:
                MEDIA_POS = ["0*RIGHT + 0.0*UP"]
            elif num_media == 2:
                MEDIA_POS = ["-3.5*RIGHT + 0.0*UP", "3.5*RIGHT + 0.0*UP"]
            elif num_media == 3:
                MEDIA_POS = ["0*RIGHT + 2.0*UP", "-3.5*RIGHT + -1.5*UP", "3.5*RIGHT + -1.5*UP"]
            else:
                MEDIA_POS = [
                    "-3.5*RIGHT +  2.2*UP", " 3.5*RIGHT +  2.2*UP",
                    "-3.5*RIGHT + -2.2*UP", " 3.5*RIGHT + -2.2*UP",
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
        " 0.0*RIGHT +  0.0*UP", " 2.5*RIGHT +  1.5*UP", "-2.5*RIGHT +  1.5*UP",
        " 2.5*RIGHT + -1.5*UP", "-2.5*RIGHT + -1.5*UP",
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

    return final_result


# ══════════════════════════════════════════════════════════════════════════════
# ANIMATION HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def _anim_in_default(etype: str) -> str:
    return "Create" if etype in {
        "axes", "graph", "vectorfield", "streamlines",
        "parametric3d", "highlight",
    } else "Write"


def _anim_out_default(etype: str) -> str:
    return "FadeOut" if etype in {"text", "mathtex", "highlight"} else "Uncreate"


def _normalize_anim(name: Optional[str], default: str) -> str:
    if not name:
        return default
    mapping = {
        "write": "Write", "fadein": "FadeIn", "create": "Create",
        "fadeout": "FadeOut", "uncreate": "Uncreate",
        "growfromcenter": "GrowFromCenter",
    }
    return mapping.get(name.strip().lower(), default)


def _rate_func(name: Optional[str]) -> Optional[str]:
    if not name:
        return None
    mapping = {
        "linear": "rf.linear", "smooth": "rf.smooth",
        "rush_from": "rf.rush_from", "rush_into": "rf.rush_into",
        "there_and_back": "rf.there_and_back",
        "ease_in_sine": "rf.ease_in_sine", "ease_out_sine": "rf.ease_out_sine",
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
    subject  = (solution.get("subject") or "physics").lower()

    needs_3d = any(
        str(el.get("type") or "").lower() == "parametric3d"
        for sc in scenes
        for el in sc.get("elements", [])
    )
    scene_cls = "ThreeDScene" if needs_3d else "Scene"

    # Inject intro scene only when external intro video is not being used.
    intro_enabled = os.getenv("INTRO_ENABLED", "true").lower() != "false"
    intro_video_path = Path(os.getenv("INTRO_VIDEO_PATH", "intro.mp4"))
    use_external_intro_video = intro_enabled and intro_video_path.exists()

    # Inject intro scene if not already present and no external intro video.
    scenes_with_intro = scenes.copy()
    if (not use_external_intro_video) and (not scenes or scenes[0].get("description", "").lower() != "intro"):
        intro_scene = {
            "id": "intro",
            "description": "intro",
            "voiceover": "Welcome to Phiversity. Where Physics Education is made simple.",
            "elements": [],
        }
        scenes_with_intro.insert(0, intro_scene)
        data.setdefault("animation_plan", {}).setdefault("scenes", []).insert(0, intro_scene)

    # Subject-specific intro tagline
    subject_taglines = {
        "physics":     "Physics Education Made Simple",
        "chemistry":   "Chemistry Education Made Simple",
        "mathematics": "Mathematics Education Made Simple",
        "economics":   "Economics Education Made Simple",
    }
    tagline = subject_taglines.get(subject, "STEM Education Made Simple")

    lines: List[str] = [
        "from manim import *",
        "from manim import rate_functions as rf",
        "",
        f"# Subject: {subject}",
        f"class GeneratedScene({scene_cls}):",
        "    def construct(self):",
        f"        self.camera.background_color = '{COLORS['bg']}'",
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
        "            \"\"\"Scale a mobject down to fit within a box (in scene units).\"\"\"",
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
    if needs_3d:
        lines.append("        self.set_camera_orientation(phi=60*DEGREES, theta=45*DEGREES)")

    for sidx, sc in enumerate(scenes_with_intro, start=1):
        desc     = sc.get("description", "")
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
        scene_title   = (_safe_str(desc[:80]) or sc.get("id", f"Scene {sidx}")).replace("'", " ")
        elements      = sc.get("elements", [])
        auto_positions = _assign_positions(elements)
        hdr_color      = _scene_header_color(scene_id, desc)

        # Layout params for this scene (used for scaling/sizing to reduce overlaps)
        element_types = [
            str(el.get("type") or "").lower()
            for el in elements
            if isinstance(el, dict)
        ]
        axes_present = any(t == "axes" for t in element_types)
        scene_has_media = any(
            (t in _VISUAL_TYPES or t in _SHAPE_TYPES) and t != "highlight"
            for t in element_types
        )
        scene_has_text = any(
            (t in _TEXT_TYPES) or (t not in _VISUAL_TYPES and t not in _SHAPE_TYPES and t != "highlight")
            for t in element_types
        )
        layout_mixed = bool(scene_has_text and scene_has_media)

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
            if (t in _TEXT_TYPES) or (t not in _VISUAL_TYPES and t not in _SHAPE_TYPES and t != "highlight")
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
            f"        # Scene {sidx}: {scene_title}",
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
        ]

        # Determine duration list safely
        dur_list: Optional[List[float]] = None
        if element_durations is not None and isinstance(element_durations, list) and len(element_durations) >= sidx:
            candidate = element_durations[sidx - 1]
            if isinstance(candidate, list):
                dur_list = [float(x) for x in candidate]
        
        acc = 0.0

        for eidx, el in enumerate(elements, start=1):
            etype       = str(el.get("type") or "").lower()
            raw_content = el.get("content") or ""
            content     = raw_content if etype in ("mathtex", "latex") else _safe_str(raw_content)
            p           = auto_positions[eidx - 1]

            style   = el.get("style") if isinstance(el, dict) else None
            color_e = _color_expr(style if isinstance(style, dict) else None)
            if not color_e:
                color_e = _get_default_color(
                    etype, content, eidx,
                    scene_id=scene_id, scene_desc=desc,
                )

            timing  = el.get("timing") if isinstance(el, dict) else None
            start   = timing.get("start")            if isinstance(timing, dict) else None
            end     = timing.get("end")              if isinstance(timing, dict) else None
            tin     = (timing.get("transition_in")   or "") if isinstance(timing, dict) else ""
            tout    = (timing.get("transition_out")  or "") if isinstance(timing, dict) else ""
            easing  = (timing.get("easing")          or "") if isinstance(timing, dict) else ""
            dur_in  = timing.get("duration_in")      if isinstance(timing, dict) else None
            dur_out = timing.get("duration_out")     if isinstance(timing, dict) else None
            el_id   = el.get("id") if isinstance(el, dict) else None

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

            var      = f"obj_{sidx}_{eidx}"
            in_anim  = _normalize_anim(tin,  _anim_in_default(etype))
            out_anim = _normalize_anim(tout, _anim_out_default(etype))
            rfname   = _rate_func(easing)

            def _extras(rt: Optional[float]) -> str:
                ex: List[str] = []
                if rfname:
                    ex.append(f"rate_func={rfname}")
                if rt is not None:
                    ex.append(f"run_time={float(rt):.3f}")
                return (", " + ", ".join(ex)) if ex else ""

            def _wait_guard(ts: float) -> str:
                return f"        if t < {ts:.3f}: self.wait({ts:.3f} - t); t = {ts:.3f}"

            # ── Emit per-type code ─────────────────────────────────────────────
            if etype in ("text", ""):
                lines.append(f"        {var} = Text('{content}').scale(_text_scale).move_to({p})")
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
                    lines.append(f"        self.play({out_anim}({var}){_extras(dur_out)})")
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype in ("mathtex", "latex"):
                lines.append("        try:")
                lines.append(f"            {var} = MathTex(r'''{content}''').scale(_math_scale).move_to({p})")
                lines.append("        except Exception:")
                lines.append(f"            {var} = Text('{_safe_str(content)}').scale(_text_scale).move_to({p})")
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
                    lines.append(f"        self.play({out_anim}({var}){_extras(dur_out)})")
                lines.append(f"        objs.append({var})")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = {var}")

            elif etype == "axes":
                xr   = style.get("x_range", [-5, 5, 1]) if isinstance(style, dict) else [-5, 5, 1]
                yr   = style.get("y_range", [-3, 3, 1]) if isinstance(style, dict) else [-3, 3, 1]
                xlab = style.get("x_label")             if isinstance(style, dict) else None
                ylab = style.get("y_label")             if isinstance(style, dict) else None
                lines.append(f"        axes = Axes(x_range={xr}, y_range={yr}, x_length=_axes_x_len, y_length=_axes_y_len).move_to({p})")
                if color_e:
                    lines.append(f"        axes.set_color({color_e})")
                lines.append("        axes.set_z_index(10)")
                lines.append("        _fit(axes, _media_max_w, _media_max_h)")
                if start is not None:
                    lines.append(_wait_guard(start))
                if xlab or ylab:
                    xl = _safe_str(xlab or "x")
                    yl = _safe_str(ylab or "y")
                    lines.append(f"        lbls = axes.get_axis_labels(MathTex(r'{xl}'), MathTex(r'{yl}'))")
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
                lines.append(f"            axes = Axes(x_range=[-5,5,1], y_range=[-3,3,1], x_length=_axes_x_len, y_length=_axes_y_len).move_to({p})")
                lines.append("            axes.set_z_index(10)")
                lines.append("            _fit(axes, _media_max_w, _media_max_h)")
                lines.append("            self.play(Create(axes))")
                lines.append("            _scene_mobjs.append(axes)")
                curves = (style.get("curves") if isinstance(style, dict) else None) or []
                single = {"content": content, **(style or {})}
                items  = curves if curves else [single]
                items_repr = str([{
                    "mode":    (cv.get("mode")    or "function") if isinstance(cv, dict) else "function",
                    "content": (cv.get("content") if isinstance(cv, dict) else None) or content,
                    "x":       (cv.get("x")       if isinstance(cv, dict) else None),
                    "y":       (cv.get("y")       if isinstance(cv, dict) else None),
                    "t_range": (cv.get("t_range") if isinstance(cv, dict) else None) or [0, 6.283],
                    "x_range": (cv.get("x_range") if isinstance(cv, dict) else None) or [-5, 5],
                    "color":   (cv.get("color")   if isinstance(cv, dict) else None),
                    "label":   (cv.get("label")   if isinstance(cv, dict) else None),
                } for cv in items])
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
                    "            if color: curve.set_color(Color(color) if str(color).startswith('#') else str(color).upper())",
                    "            else: curve.set_color(Color(_auto_cc))",
                    "            curve.set_z_index(20)",
                    "            _cv_idx += 1",
                ]
                if start is not None:
                    lines.append(_wait_guard(start))
                lines += [
                    "            self.play(Create(curve))",
                    "            _scene_mobjs.append(curve)",
                ]
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append("            self.play(Uncreate(curve))")
                lines += [
                    "            objs.append(curve)",
                    "        _legend_items = [(o, cv.get('label')) for o, cv in zip(objs[-len(" + repr(items) + "):], " + repr(items) + ") if cv.get('label')]",
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
                fx = (style.get("fx") if isinstance(style, dict) else None)
                fy = (style.get("fy") if isinstance(style, dict) else None)
                if not fx or not fy:
                    parts = content.strip().strip("[]").split(",") if content else []
                    fx, fy = (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else ("y", "-x")
                xr = style.get("x_range", [-5, 5, 1]) if isinstance(style, dict) else [-5, 5, 1]
                yr = style.get("y_range", [-3, 3, 1]) if isinstance(style, dict) else [-3, 3, 1]
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
                lines += ["        self.play(Create(vf))", "        _scene_mobjs.append(vf)"]
                if end is not None and end > start and tout:
                    lines.append(_wait_guard(end))
                    lines.append("        self.play(Uncreate(vf))")
                lines.append("        objs.append(vf)")
                if el_id:
                    lines.append(f"        idmap['{el_id}'] = vf")

            elif etype == "streamlines":
                fx = (style.get("fx") if isinstance(style, dict) else None)
                fy = (style.get("fy") if isinstance(style, dict) else None)
                if not fx or not fy:
                    parts = content.strip().strip("[]").split(",") if content else []
                    fx, fy = (parts[0].strip(), parts[1].strip()) if len(parts) == 2 else ("y", "-x")
                xr = style.get("x_range", [-5, 5, 1]) if isinstance(style, dict) else [-5, 5, 1]
                yr = style.get("y_range", [-3, 3, 1]) if isinstance(style, dict) else [-3, 3, 1]
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
                lines += ["        self.play(Create(stream))", "        _scene_mobjs.append(stream)"]
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
                tr = (style.get("t_range") if isinstance(style, dict) else None) or [0, 6.283]
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
                lines += ["        self.play(Create(curve3d))", "        _scene_mobjs.append(curve3d)"]
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
                    lines.append(f"            if t < {start:.3f}: self.wait({start:.3f} - t); t = {start:.3f}")
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
                    lines.append(f"            {var}.set_fill({color_e or 'WHITE'}, opacity={style['fill_opacity']})")
                num_sides       = style.get("sides") if isinstance(style, dict) else None
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
                    lines.append(f"        self.play(Uncreate({var}), FadeOut(_poly_lbl))")
                lines.append(f"        objs.append({var})")

            elif etype == "circle":
                radius_val = (
                    str(style.get("radius", "R"))
                    if isinstance(style, dict) and "radius" in style else "R"
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
                    if isinstance(style, dict) and "inner_radius" in style else "r"
                )
                outer_r = (
                    str(style.get("outer_radius", "r+dr"))
                    if isinstance(style, dict) and "outer_radius" in style else "r+dr"
                )
                lines += [f"        {var} = Annulus(inner_radius={inner_r}, outer_radius={outer_r}).move_to({p})"]
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                if style and "fill_opacity" in style:
                    lines.append(f"        {var}.set_fill({color_e or 'YELLOW'}, opacity={style['fill_opacity']})")
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
                    lines.append(f"        self.play(Uncreate({var}), FadeOut(_ann_inner), FadeOut(_ann_outer))")
                lines.append(f"        objs.append({var})")

            elif etype == "rectangle":
                width_val  = (
                    str(style.get("width",  "2*np.pi*r"))
                    if isinstance(style, dict) and "width"  in style else "2*np.pi*r"
                )
                height_val = (
                    str(style.get("height", "dr"))
                    if isinstance(style, dict) and "height" in style else "dr"
                )
                lines += [f"        {var} = Rectangle(width={width_val}, height={height_val}).move_to({p})"]
                if color_e:
                    lines.append(f"        {var}.set_color({color_e})")
                if style and "fill_opacity" in style:
                    lines.append(f"        {var}.set_fill({color_e or 'BLUE'}, opacity={style['fill_opacity']})")
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
                    lines.append(f"        self.play(Uncreate({var}), FadeOut(_rect_w), FadeOut(_rect_h))")
                lines.append(f"        objs.append({var})")

            else:
                # Generic fallback
                lines.append(f"        {var} = Text('{content}').scale(0.6).move_to({p})")
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

        # ── End-of-scene wait — use resolved scene duration ────────────────────
        lines.append(f"        if t < {scene_sd:.3f}: self.wait({scene_sd:.3f} - t); t = {scene_sd:.3f}")

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
        "low":        "-ql",
        "medium":     "-qm",
        "high":       "-qh",
        "production": "-qp",
    }.get((quality or os.getenv("MANIM_QUALITY", "medium")).lower(), "-qm")

    output_flag: List[str] = ["-o", out_path.name] if out_path else []
    cmd = [sys.executable, "-m", "manim", quality_flag, *output_flag,
           str(script_path), scene_name]

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
    candidates   = sorted(
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


# ══════════════════════════════════════════════════════════════════════════════
# CLI ENTRY-POINT
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate and render a Manim scene from structured JSON (10-min edition)"
    )
    parser.add_argument("json",        help="Path to structured JSON (SolverOutput)")
    parser.add_argument("--out",       dest="out",       default=None,
                        help="Output mp4 path")
    parser.add_argument("--quality",   dest="quality",   default=None,
                        help="Manim quality: low|medium|high|production")
    parser.add_argument("--durations", dest="durations", default=None,
                        help="Optional JSON file with per-scene durations (seconds)")
    parser.add_argument("--no-validate", dest="no_validate", action="store_true",
                        help="Skip 10-minute duration validation")
    args = parser.parse_args()

    data = json.loads(Path(args.json).read_text(encoding="utf-8"))

    # Run duration validation before spending time generating/rendering
    if not args.no_validate:
        validate_duration(data)

    scene_durations: Optional[List[float]] = None
    if args.durations:
        scene_durations = json.loads(
            Path(args.durations).read_text(encoding="utf-8")
        )

    script_text = generate_scene_script(data, scene_durations=scene_durations)

    gen_dir     = Path("scripts") / "_generated"
    gen_dir.mkdir(parents=True, exist_ok=True)
    script_path = gen_dir / "generated_scene.py"
    script_path.write_text(script_text, encoding="utf-8")

    out_path = Path(args.out) if args.out else None
    video    = render_with_manim(
        script_path, "GeneratedScene",
        out_path=out_path, quality=args.quality,
    )
    print(f"Rendered video: {video}")


if __name__ == "__main__":
    main()
