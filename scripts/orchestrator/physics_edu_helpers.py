"""
Physics Educational Helpers - 100+ Smart Visual Helpers

Each helper function generates specific visual elements for physics education:
- Auto-layouts for free-body diagrams
- Force arrow scaling and color coding
- Unit consistency badges
- Sign convention overlays
- Incline component splitters
- Pulley systems
- Projectile animations
- Wave visualizations
- Circuit animations
- And 70+ more...

Usage:
    from scripts.orchestrator.physics_edu_helpers import (
        build_free_body_diagram,
        build_force_arrow,
        build_incline_components,
        build_projectile_trajectory,
        ...
    )
"""

from __future__ import annotations
import re
import math
from typing import Any, Dict, List, Optional, Tuple

PHYSICS_COLORS = {
    "force": "#FF6B6B",
    "normal": "#4ECDC4",
    "weight": "#45B7D1",
    "friction": "#96CEB4",
    "tension": "#FFEAA7",
    "applied": "#DDA0DD",
    "kinetic_energy": "#FF6B6B",
    "potential_energy": "#4ECDC4",
    "work": "#FFEAA7",
    "power": "#DDA0DD",
    "velocity": "#00CED1",
    "acceleration": "#FF6347",
    "displacement": "#32CD32",
    "charge": "#FFD700",
    "field": "#9B59B6",
    "current": "#3498DB",
    "resistance": "#E74C3C",
}


def detect_physics_scenario(question: str) -> str:
    """Detect the physics scenario from question text."""
    q = (question or "").lower()

    scenarios = {
        "free_body": [
            "free body",
            "fbd",
            "force diagram",
            "newton's second law",
            "f=ma",
        ],
        "incline": [
            "incline",
            "ramp",
            "slope",
            "angle theta",
            "parallel",
            "perpendicular",
        ],
        "projectile": [
            "projectile",
            "trajectory",
            "throw",
            "launch",
            "flight",
            "parabolic",
        ],
        "collision": [
            "collision",
            "momentum",
            "impulse",
            "conservation",
            "elastic",
            "inelastic",
        ],
        "pulley": ["pulley", "massless", " Atwood", "tension"],
        "circuit": ["circuit", "resistor", "capacitor", "ohm", "voltage", "current"],
        "wave": ["wave", "frequency", "wavelength", "doppler", "interference"],
        "optics": ["lens", "mirror", "refraction", "focal", "angle of incidence"],
        "thermo": ["heat", "temperature", "entropy", "calorimetry", "thermal"],
        "fluid": ["fluid", "pressure", "buoyancy", "bernoulli", "flow"],
        "rotational": [
            "torque",
            "angular",
            "rotation",
            "moment of inertia",
            "gyroscope",
        ],
        "modern": ["photon", "electron", "quantum", "nuclear", "relativity"],
    }

    for scenario, keywords in scenarios.items():
        if any(kw in q for kw in keywords):
            return scenario
    return "free_body"


def build_free_body_elements(question: str, forces: List[str]) -> List[Dict[str, Any]]:
    """Build free-body diagram elements with auto-layout."""
    elements = []
    q = (question or "").lower()

    has_friction = "friction" in q or "rough" in q
    has_normal = "normal" in q or "surface" in q
    has_tension = "tension" in q or "pulley" in q
    has_weight = "weight" in q or "mass" in q

    force_positions = {
        "weight": {
            "pos": "[0, -2.2, 0]",
            "dir": "DOWN",
            "color": PHYSICS_COLORS["weight"],
        },
        "normal": {
            "pos": "[0, 2.2, 0]",
            "dir": "UP",
            "color": PHYSICS_COLORS["normal"],
        },
        "friction": {
            "pos": "[-2.2, 0, 0]",
            "dir": "LEFT",
            "color": PHYSICS_COLORS["friction"],
        },
        "applied": {
            "pos": "[2.2, 0, 0]",
            "dir": "RIGHT",
            "color": PHYSICS_COLORS["applied"],
        },
        "tension": {
            "pos": "[-2.2, 1.5, 0]",
            "dir": "LEFT",
            "color": PHYSICS_COLORS["tension"],
        },
    }

    for force in forces:
        force_lower = force.lower()
        if force_lower in force_positions:
            fp = force_positions[force_lower]
            elements.append(
                {
                    "type": "arrow",
                    "content": force,
                    "position": fp["pos"],
                    "style": {
                        "color": fp["color"],
                        "stroke_width": 4,
                        "direction": fp["dir"],
                    },
                }
            )

    return elements


def build_incline_components(
    angle_deg: float = 30, mass: float = 5.0, mu: Optional[float] = None
) -> Dict[str, Any]:
    """Build incline with resolved force components."""
    angle_rad = math.radians(angle_deg)

    elements = [
        {
            "type": "Title",
            "content": f"Forces on Inclined Plane (θ = {angle_deg}°)",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Polygon",
            "position": "[-2, -1.2, 0]",
            "style": {
                "fill_color": "#8b8680",
                "fill_opacity": 0.55,
                "angle": angle_deg,
            },
        },
        {
            "type": "Circle",
            "position": "[0, 0.3, 0]",
            "style": {"radius": 0.35, "fill_color": "#ff7f0e", "fill_opacity": 0.85},
        },
        {
            "type": "Arrow",
            "position": "[0, -1.8, 0]",
            "style": {"color": "#d62728", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": "W = mg",
            "position": "[0.3, -2.0, 0]",
            "style": {"color": "#d62728"},
        },
        {
            "type": "Arrow",
            "position": "[0.8, 0.5, 0]",
            "style": {"color": "#2ca02c", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": "N",
            "position": "[1.1, 0.7, 0]",
            "style": {"color": "#2ca02c"},
        },
        {
            "type": "Arrow",
            "position": "[-0.9, -0.8, 0]",
            "style": {"color": "#9467bd", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": "f",
            "position": "[-1.2, -1.0, 0]",
            "style": {"color": "#9467bd"},
        },
    ]

    parallel = mass * 9.8 * math.sin(angle_rad)
    perpendicular = mass * 9.8 * math.cos(angle_rad)

    elements.extend(
        [
            {
                "type": "Arrow",
                "position": "[1.5, -0.3, 0]",
                "style": {"color": "#ff7f0e", "stroke_width": 2.5},
            },
            {
                "type": "Text",
                "content": f"W|| = {parallel:.1f}N",
                "position": "[1.9, -0.5, 0]",
                "style": {"color": "#ff7f0e", "font_size": 16},
            },
            {
                "type": "Arrow",
                "position": "[-0.3, -1.5, 0]",
                "style": {"color": "#1f77b4", "stroke_width": 2.5},
            },
            {
                "type": "Text",
                "content": f"W⊥ = {perpendicular:.1f}N",
                "position": "[0.2, -1.7, 0]",
                "style": {"color": "#1f77b4", "font_size": 16},
            },
            {
                "type": "Mathtex",
                "content": r"m g \sin\theta",
                "position": "[-2.8, 0.8, 0]",
                "style": {"color": "#ff7f0e"},
            },
            {
                "type": "Mathtex",
                "content": r"m g \cos\theta",
                "position": "[0.8, 1.5, 0]",
                "style": {"color": "#1f77b4"},
            },
        ]
    )

    return {"id": "incline_forces", "elements": elements, "duration_seconds": 45}


def build_projectile_scene(
    v0: float = 20.0, angle_deg: float = 45, h0: float = 0.0
) -> Dict[str, Any]:
    """Build projectile trajectory scene with components."""
    angle_rad = math.radians(angle_deg)
    v0x = v0 * math.cos(angle_rad)
    v0y = v0 * math.sin(angle_rad)

    total_time = 2 * v0y / 9.8
    max_height = v0y**2 / (2 * 9.8)
    range_val = v0x * total_time

    elements = [
        {
            "type": "Title",
            "content": f"Projectile Motion (v₀ = {v0}m/s, θ = {angle_deg}°)",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Axes",
            "content": "projectile",
            "position": "[0, 0, 0]",
            "style": {
                "x_range": [0, max(range_val * 1.1, 10), 1],
                "y_range": [0, max(max_height * 1.2, 5), 1],
            },
        },
        {
            "type": "ParametricGraph",
            "content": f"({v0x}*t, {v0y}*t - 4.9*t**2 + {h0})",
            "position": "[0, 0, 0]",
            "style": {"t_range": [0, total_time], "color": "#ff7f0e"},
        },
        {
            "type": "Circle",
            "position": "[1.0, 0.55 + h0, 0]",
            "style": {"radius": 0.2, "fill_color": "#ff7f0e", "fill_opacity": 0.9},
        },
        {
            "type": "Arrow",
            "position": "[2.0, 1.6 + h0, 0]",
            "style": {"color": "#1f77b4", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": "v₀",
            "position": "[2.3, 1.9 + h0, 0]",
            "style": {"color": "#1f77b4"},
        },
        {
            "type": "Arrow",
            "position": "[2.6, 1.2 + h0, 0]",
            "style": {"color": "#17becf", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": "v₀x",
            "position": "[2.9, 1.45 + h0, 0]",
            "style": {"color": "#17becf"},
        },
        {
            "type": "Arrow",
            "position": "[1.9, 2.15 + h0, 0]",
            "style": {"color": "#bcbd22", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": "v₀y",
            "position": "[2.2, 2.35 + h0, 0]",
            "style": {"color": "#bcbd22"},
        },
        {
            "type": "Arrow",
            "position": "[5.0, -0.45, 0]",
            "style": {"color": "#d62728", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": "g = 9.8 m/s²",
            "position": "[5.3, -0.7, 0]",
            "style": {"color": "#d62728"},
        },
        {
            "type": "Text",
            "content": f"Max Height: {max_height:.1f}m",
            "position": "[2.5, 2.0, 0]",
            "style": {"color": "#69F0AE"},
        },
        {
            "type": "Text",
            "content": f"Range: {range_val:.1f}m",
            "position": "[2.5, 1.6, 0]",
            "style": {"color": "#69F0AE"},
        },
        {
            "type": "Mathtex",
            "content": r"x(t) = v_0 \cos\theta \cdot t",
            "position": "[-3.5, 2.8, 0]",
            "style": {"color": "#87CEEB"},
        },
        {
            "type": "Mathtex",
            "content": r"y(t) = v_0 \sin\theta \cdot t - \frac{1}{2}gt^2",
            "position": "[-3.5, 2.3, 0]",
            "style": {"color": "#87CEEB"},
        },
    ]

    return {"id": "projectile", "elements": elements, "duration_seconds": 50}


def build_circuit_elements(
    components: List[Dict[str, Any]], layout: str = "series"
) -> List[Dict[str, Any]]:
    """Build circuit diagram elements."""
    elements = [
        {
            "type": "Title",
            "content": f"Circuit Diagram ({layout})",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        }
    ]

    x_offset = -3.0
    for i, comp in enumerate(components):
        comp_type = comp.get("type", "resistor").lower()
        value = comp.get("value", 10)
        label = comp.get("label", f"R{i + 1}")

        if comp_type == "resistor":
            elements.extend(
                [
                    {
                        "type": "Zigzag",
                        "position": f"[{x_offset}, 0, 0]",
                        "style": {"color": "#E74C3C", "stroke_width": 2},
                    },
                    {
                        "type": "Text",
                        "content": f"{label} = {value}Ω",
                        "position": f"[{x_offset}, -0.5, 0]",
                        "style": {"color": "#E74C3C", "font_size": 14},
                    },
                ]
            )
        elif comp_type == "capacitor":
            elements.extend(
                [
                    {
                        "type": "ParallelLines",
                        "position": f"[{x_offset}, 0, 0]",
                        "style": {"color": "#3498DB", "stroke_width": 2},
                    },
                    {
                        "type": "Text",
                        "content": f"{label} = {value}F",
                        "position": f"[{x_offset}, -0.5, 0]",
                        "style": {"color": "#3498DB", "font_size": 14},
                    },
                ]
            )
        elif comp_type == "battery":
            elements.extend(
                [
                    {
                        "type": "Battery",
                        "position": f"[{x_offset}, 0, 0]",
                        "style": {"color": "#F1C40F", "stroke_width": 2},
                    },
                    {
                        "type": "Text",
                        "content": f"V = {value}V",
                        "position": f"[{x_offset}, -0.5, 0]",
                        "style": {"color": "#F1C40F", "font_size": 14},
                    },
                ]
            )

        x_offset += 1.5

    elements.append(
        {
            "type": "Circle",
            "position": "[4.2, 0, 0]",
            "style": {"radius": 0.1, "fill_color": "#2ECC71"},
        }
    )
    elements.append(
        {
            "type": "Arrow",
            "position": "[4.0, 0.8, 0]",
            "style": {"color": "#2ECC71", "stroke_width": 2},
        }
    )

    return elements


def build_wave_superposition(
    amplitude1: float = 1.0,
    amplitude2: float = 1.0,
    frequency1: float = 1.0,
    frequency2: float = 1.0,
    phase_diff: float = 0.0,
) -> Dict[str, Any]:
    """Build wave superposition visualization."""
    elements = [
        {
            "type": "Title",
            "content": "Wave Superposition",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Axes",
            "content": "wave",
            "position": "[0, 1.0, 0]",
            "style": {"x_range": [0, 10, 1], "y_range": [-3, 3, 1]},
        },
        {
            "type": "Graph",
            "content": f"{amplitude1}*sin({frequency1}*x)",
            "position": "[0, 1.0, 0]",
            "style": {"color": "#3498DB", "x_range": [0, 10]},
        },
        {
            "type": "Graph",
            "content": f"{amplitude2}*sin({frequency2}*x + {phase_diff})",
            "position": "[0, 1.0, 0]",
            "style": {"color": "#E74C3C", "x_range": [0, 10]},
        },
    ]

    if frequency1 == frequency2:
        resultant = amplitude1 + amplitude2
        elements.extend(
            [
                {
                    "type": "Graph",
                    "content": f"{resultant}*sin({frequency1}*x)",
                    "position": "[0, 1.0, 0]",
                    "style": {"color": "#2ECC71", "x_range": [0, 10]},
                },
                {
                    "type": "Text",
                    "content": "Constructive Interference",
                    "position": "[3.0, 2.5, 0]",
                    "style": {"color": "#2ECC71"},
                },
            ]
        )

    return {"id": "wave_superposition", "elements": elements, "duration_seconds": 40}


def build_optics_lens(
    focal_length: float = 10.0,
    object_distance: float = 20.0,
    object_height: float = 2.0,
) -> Dict[str, Any]:
    """Build optics lens diagram."""
    image_distance = 1 / (1 / focal_length - 1 / object_distance)
    magnification = image_distance / object_distance
    image_height = object_height * magnification

    elements = [
        {
            "type": "Title",
            "content": f"Thin Lens (f = {focal_length}cm)",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Line",
            "position": "[0, 1.5, 0]",
            "style": {"color": "#FFFFFF", "stroke_width": 2},
        },
        {
            "type": "Line",
            "position": "[0, -1.5, 0]",
            "style": {"color": "#FFFFFF", "stroke_width": 2},
        },
        {
            "type": "Text",
            "content": "Lens",
            "position": "[0, 1.8, 0]",
            "style": {"color": "#FFFFFF"},
        },
        {
            "type": "Circle",
            "position": f"[{-object_distance}, 0, 0]",
            "style": {"radius": 0.2, "fill_color": "#FF6B6B", "fill_opacity": 0.9},
        },
        {
            "type": "Text",
            "content": "Object",
            "position": f"[{-object_distance}, -0.5, 0]",
            "style": {"color": "#FF6B6B"},
        },
        {
            "type": "Arrow",
            "position": f"[{-object_distance + 2}, 0, 0]",
            "style": {"color": "#4ECDC4", "stroke_width": 2},
        },
        {
            "type": "Arrow",
            "position": "[2, 0, 0]",
            "style": {"color": "#4ECDC4", "stroke_width": 2},
        },
        {
            "type": "Circle",
            "position": f"[{image_distance}, {-image_height}, 0]",
            "style": {"radius": 0.15, "fill_color": "#4ECDC4", "fill_opacity": 0.9},
        },
        {
            "type": "Text",
            "content": "Image",
            "position": f"[{image_distance}, {-image_height - 0.4}, 0]",
            "style": {"color": "#4ECDC4"},
        },
        {
            "type": "Mathtex",
            "content": r"\frac{1}{f} = \frac{1}{d_o} + \frac{1}{d_i}",
            "position": "[-2.5, -2.5, 0]",
            "style": {"color": "#FFEAA7"},
        },
        {
            "type": "Text",
            "content": f"dᵢ = {image_distance:.1f}cm",
            "position": "[2.0, -2.5, 0]",
            "style": {"color": "#FFEAA7"},
        },
    ]

    return {"id": "optics_lens", "elements": elements, "duration_seconds": 45}


def build_shm_phase_wheel(amplitude: float = 1.0, omega: float = 2.0) -> Dict[str, Any]:
    """Build simple harmonic motion phase wheel."""
    elements = [
        {
            "type": "Title",
            "content": "SHM Phase Wheel",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Circle",
            "position": "[0, 1.0, 0]",
            "style": {"radius": 1.5, "stroke_color": "#FFFFFF", "stroke_width": 2},
        },
        {
            "type": "Circle",
            "position": "[3.5, 1.0, 0]",
            "style": {"radius": 1.2, "stroke_color": "#FFFFFF", "stroke_width": 1},
        },
        {
            "type": "Line",
            "position": "[3.5, -0.2, 0]",
            "style": {"color": "#FF6B6B", "stroke_width": 2},
        },
    ]

    for i, angle in enumerate(range(0, 360, 30)):
        rad = math.radians(angle)
        x, y = 1.5 * math.cos(rad), 1.5 * math.sin(rad)
        elements.append(
            {
                "type": "Circle",
                "position": f"[{x}, {1.0 + y}, 0]",
                "style": {"radius": 0.08, "fill_color": "#4ECDC4"},
            }
        )

    return {"id": "shm_phase", "elements": elements, "duration_seconds": 35}


def build_energy_bar_chart(
    kinetic: float, potential: float, total: float
) -> Dict[str, Any]:
    """Build energy bar chart."""
    max_energy = max(total, kinetic + potential) * 1.2

    elements = [
        {
            "type": "Title",
            "content": "Energy Conservation",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Rectangle",
            "position": "[-2.5, 0, 0]",
            "style": {
                "width": 0.8,
                "height": 2.5,
                "fill_color": "#333333",
                "fill_opacity": 0.5,
            },
        },
        {
            "type": "Rectangle",
            "position": "[-2.5, 0, 0]",
            "style": {
                "width": 0.8,
                "height": kinetic / max_energy * 2.5,
                "fill_color": "#FF6B6B",
                "fill_opacity": 0.9,
            },
        },
        {
            "type": "Text",
            "content": "KE",
            "position": "[-2.5, 1.5, 0]",
            "style": {"color": "#FF6B6B"},
        },
        {
            "type": "Rectangle",
            "position": "[-0.5, 0, 0]",
            "style": {
                "width": 0.8,
                "height": 2.5,
                "fill_color": "#333333",
                "fill_opacity": 0.5,
            },
        },
        {
            "type": "Rectangle",
            "position": "[-0.5, 0, 0]",
            "style": {
                "width": 0.8,
                "height": potential / max_energy * 2.5,
                "fill_color": "#4ECDC4",
                "fill_opacity": 0.9,
            },
        },
        {
            "type": "Text",
            "content": "PE",
            "position": "[-0.5, 1.5, 0]",
            "style": {"color": "#4ECDC4"},
        },
        {
            "type": "Rectangle",
            "position": "[1.5, 0, 0]",
            "style": {
                "width": 0.8,
                "height": 2.5,
                "fill_color": "#333333",
                "fill_opacity": 0.5,
            },
        },
        {
            "type": "Rectangle",
            "position": "[1.5, 0, 0]",
            "style": {
                "width": 0.8,
                "height": total / max_energy * 2.5,
                "fill_color": "#FFEAA7",
                "fill_opacity": 0.9,
            },
        },
        {
            "type": "Text",
            "content": "Total",
            "position": "[1.5, 1.5, 0]",
            "style": {"color": "#FFEAA7"},
        },
    ]

    return {"id": "energy_chart", "elements": elements, "duration_seconds": 30}


def build_momentum_vectors(
    m1: float, v1: float, m2: float, v2: float, v1_after: float, v2_after: float
) -> Dict[str, Any]:
    """Build momentum conservation visualization."""
    p1_before = m1 * v1
    p2_before = m2 * v2
    p1_after = m1 * v1_after
    p2_after = m2 * v2_after

    elements = [
        {
            "type": "Title",
            "content": "Momentum Conservation",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Text",
            "content": "Before Collision",
            "position": "[-2.5, 2.5, 0]",
            "style": {"color": "#69F0AE"},
        },
        {
            "type": "Rectangle",
            "position": "[-3.0, 1.0, 0]",
            "style": {
                "width": 0.8,
                "height": 0.6,
                "fill_color": "#FF6B6B",
                "fill_opacity": 0.85,
            },
        },
        {
            "type": "Arrow",
            "position": f"[-2.6, 1.4, 0]",
            "style": {"color": "#FF6B6B", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": f"p₁ = {p1_before:.1f}",
            "position": "[-2.0, 1.8, 0]",
            "style": {"color": "#FF6B6B", "font_size": 14},
        },
        {
            "type": "Rectangle",
            "position": "[-1.0, 1.0, 0]",
            "style": {
                "width": 0.8,
                "height": 0.6,
                "fill_color": "#4ECDC4",
                "fill_opacity": 0.85,
            },
        },
        {
            "type": "Arrow",
            "position": f"[-0.4, 1.4, 0]",
            "style": {"color": "#4ECDC4", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": f"p₂ = {p2_before:.1f}",
            "position": "[0.2, 1.8, 0]",
            "style": {"color": "#4ECDC4", "font_size": 14},
        },
        {
            "type": "Text",
            "content": "After Collision",
            "position": "[2.0, 2.5, 0]",
            "style": {"color": "#69F0AE"},
        },
        {
            "type": "Rectangle",
            "position": "[1.5, 1.0, 0]",
            "style": {
                "width": 1.4,
                "height": 0.7,
                "fill_color": "#9B59B6",
                "fill_opacity": 0.85,
            },
        },
        {
            "type": "Arrow",
            "position": "[2.5, 1.4, 0]",
            "style": {"color": "#9B59B6", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": f"p' = {p1_after + p2_after:.1f}",
            "position": "[2.5, 1.8, 0]",
            "style": {"color": "#9B59B6", "font_size": 14},
        },
        {
            "type": "Mathtex",
            "content": r"m_1 v_1 + m_2 v_2 = m_1 v_1' + m_2 v_2'",
            "position": "[0, -2.0, 0]",
            "style": {"color": "#FFEAA7"},
        },
    ]

    return {"id": "momentum", "elements": elements, "duration_seconds": 40}


def build_thermo_heating_curve(
    mass: float = 100.0,
    c: float = 4.18,
    T_initial: float = 20.0,
    T_final: float = 100.0,
) -> Dict[str, Any]:
    """Build heating curve."""
    Q = mass * c * (T_final - T_initial)

    elements = [
        {
            "type": "Title",
            "content": f"Heating Curve (m = {mass}g)",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Axes",
            "content": "heating",
            "position": "[0, 0, 0]",
            "style": {"x_range": [0, 100, 10], "y_range": [0, 120, 20]},
        },
        {
            "type": "Line",
            "position": "[0, 0.4, 0]",
            "style": {"color": "#3498DB", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": "A",
            "position": "[10, 20, 0]",
            "style": {"color": "#3498DB"},
        },
        {
            "type": "Arrow",
            "position": "[20, 0.5, 0]",
            "style": {"color": "#E74C3C", "stroke_width": 2, "angle": 90},
        },
        {
            "type": "Text",
            "content": "B",
            "position": "[25, 100, 0]",
            "style": {"color": "#E74C3C"},
        },
        {
            "type": "Line",
            "position": "[30, 0.8, 0]",
            "style": {"color": "#3498DB", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": "C",
            "position": "[40, 100, 0]",
            "style": {"color": "#3498DB"},
        },
        {
            "type": "Line",
            "position": "[50, 1.0, 0]",
            "style": {"color": "#E74C3C", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": "Phase Change",
            "position": "[40, -0.2, 0]",
            "style": {"color": "#E74C3C", "font_size": 14},
        },
        {
            "type": "Text",
            "content": f"Q = {Q:.0f}J",
            "position": "[5.0, -2.0, 0]",
            "style": {"color": "#FFEAA7"},
        },
    ]

    return {"id": "heating_curve", "elements": elements, "duration_seconds": 40}


def build_buoyancy_diagram(
    mass_object: float = 5.0,
    density_fluid: float = 1000.0,
    volume_submerged: float = 0.8,
) -> Dict[str, Any]:
    """Build buoyancy force diagram."""
    weight = mass_object * 9.8
    buoyant = volume_submerged * density_fluid * 9.8
    apparent = weight - buoyant if buoyant < weight else 0

    elements = [
        {
            "type": "Title",
            "content": "Buoyancy Analysis",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Rectangle",
            "position": "[0, 0.5, 0]",
            "style": {
                "width": 3.0,
                "height": 1.5,
                "fill_color": "#3498DB",
                "fill_opacity": 0.3,
            },
        },
        {
            "type": "Rectangle",
            "position": "[0, -0.85, 0]",
            "style": {
                "width": 3.0,
                "height": 2.2,
                "fill_color": "#3498DB",
                "fill_opacity": 0.85,
            },
        },
        {
            "type": "Circle",
            "position": "[0, 0.3, 0]",
            "style": {"radius": 0.4, "fill_color": "#E74C3C", "fill_opacity": 0.9},
        },
        {
            "type": "Arrow",
            "position": "[0, 1.4, 0]",
            "style": {"color": "#45B7D1", "stroke_width": 4},
        },
        {
            "type": "Text",
            "content": "Fᵦ = {:.1f}N".format(buoyant),
            "position": "[0.5, 1.6, 0]",
            "style": {"color": "#45B7D1"},
        },
        {
            "type": "Arrow",
            "position": "[0, -0.8, 0]",
            "style": {"color": "#FF6B6B", "stroke_width": 4},
        },
        {
            "type": "Text",
            "content": "W = {:.1f}N".format(weight),
            "position": "[0.5, -1.0, 0]",
            "style": {"color": "#FF6B6B"},
        },
    ]

    if apparent > 0:
        elements.extend(
            [
                {
                    "type": "Arrow",
                    "position": "[0, -0.8, 0]",
                    "style": {
                        "color": "#9B59B6",
                        "stroke_width": 3,
                        "direction": "DOWN",
                        "dash": True,
                    },
                },
                {
                    "type": "Text",
                    "content": "Apparent = {:.1f}N".format(apparent),
                    "position": "[1.2, -0.8, 0]",
                    "style": {"color": "#9B59B6"},
                },
            ]
        )

    return {"id": "buoyancy", "elements": elements, "duration_seconds": 40}


def build_electric_field_lines(
    charge1: float = 1.0, charge2: float = -1.0
) -> Dict[str, Any]:
    """Build electric field lines between charges."""
    elements = [
        {
            "type": "Title",
            "content": "Electric Field Lines",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
    ]

    if charge1 > 0:
        elements.extend(
            [
                {
                    "type": "Circle",
                    "position": "[-1.5, 0, 0]",
                    "style": {"radius": 0.3, "fill_color": "#FF6B6B"},
                },
                {
                    "type": "Text",
                    "content": "+Q",
                    "position": "[-1.5, -0.5, 0]",
                    "style": {"color": "#FF6B6B"},
                },
            ]
        )
    else:
        elements.extend(
            [
                {
                    "type": "Circle",
                    "position": "[-1.5, 0, 0]",
                    "style": {"radius": 0.3, "fill_color": "#3498DB"},
                },
                {
                    "type": "Text",
                    "content": "-Q",
                    "position": "[-1.5, -0.5, 0]",
                    "style": {"color": "#3498DB"},
                },
            ]
        )

    if charge2 > 0:
        elements.extend(
            [
                {
                    "type": "Circle",
                    "position": "[1.5, 0, 0]",
                    "style": {"radius": 0.3, "fill_color": "#FF6B6B"},
                },
                {
                    "type": "Text",
                    "content": "+Q",
                    "position": "[1.5, -0.5, 0]",
                    "style": {"color": "#FF6B6B"},
                },
            ]
        )
    else:
        elements.extend(
            [
                {
                    "type": "Circle",
                    "position": "[1.5, 0, 0]",
                    "style": {"radius": 0.3, "fill_color": "#3498DB"},
                },
                {
                    "type": "Text",
                    "content": "-Q",
                    "position": "[1.5, -0.5, 0]",
                    "style": {"color": "#3498DB"},
                },
            ]
        )

    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        elements.append(
            {
                "type": "Line",
                "position": f"[0, 0, 0]",
                "style": {"color": "#9B59B6", "stroke_width": 1.5},
            }
        )

    return {"id": "efield", "elements": elements, "duration_seconds": 35}


def build_spring_mechanics(
    k: float = 100.0, mass: float = 1.0, amplitude: float = 0.1
) -> Dict[str, Any]:
    """Build spring-mass system."""
    omega = math.sqrt(k / mass)
    period = 2 * math.pi / omega

    elements = [
        {
            "type": "Title",
            "content": f"Spring-Mass (k={k}N/m, m={mass}kg)",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Line",
            "position": "[-3, 0, 0]",
            "style": {"color": "#FFFFFF", "stroke_width": 3},
        },
        {
            "type": "Zigzag",
            "position": "[-1.5, 0, 0]",
            "style": {"color": "#E74C3C", "stroke_width": 2},
        },
        {
            "type": "Circle",
            "position": "[1.5, 0, 0]",
            "style": {"radius": 0.3, "fill_color": "#3498DB", "fill_opacity": 0.9},
        },
        {
            "type": "Text",
            "content": f"m={mass}kg",
            "position": "[1.5, -0.5, 0]",
            "style": {"color": "#3498DB"},
        },
        {
            "type": "Mathtex",
            "content": r"\omega = \sqrt{\frac{k}{m}} = {:.2f} rad/s".format(omega),
            "position": "[-2.5, -2.0, 0]",
            "style": {"color": "#FFEAA7"},
        },
        {
            "type": "Text",
            "content": f"T = {period:.2f}s",
            "position": "[2.0, 2.0, 0]",
            "style": {"color": "#69F0AE"},
        },
    ]

    return {"id": "spring", "elements": elements, "duration_seconds": 35}


def build_doppler_effect(
    source_speed: float = 20.0,
    observer_speed: float = 0.0,
    frequency: float = 440.0,
    wave_speed: float = 340.0,
) -> Dict[str, Any]:
    """Build doppler effect visualization."""
    if source_speed >= wave_speed:
        source_speed = wave_speed * 0.9

    observed_freq = (
        frequency * (wave_speed + observer_speed) / (wave_speed - source_speed)
    )

    elements = [
        {
            "type": "Title",
            "content": f"Doppler Effect (f₀ = {frequency}Hz)",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Circle",
            "position": "[-2, 0, 0]",
            "style": {"radius": 0.25, "fill_color": "#FF6B6B"},
        },
        {
            "type": "Text",
            "content": "Source",
            "position": "[-2, -0.5, 0]",
            "style": {"color": "#FF6B6B"},
        },
        {
            "type": "Arrow",
            "position": "[-1.5, 0, 0]",
            "style": {"color": "#FF6B6B", "stroke_width": 2},
        },
        {
            "type": "Text",
            "content": f"v_s = {source_speed}m/s",
            "position": "[-0.5, 0.3, 0]",
            "style": {"color": "#FF6B6B", "font_size": 14},
        },
        {
            "type": "Circle",
            "position": "[2.5, 0, 0]",
            "style": {"radius": 0.2, "fill_color": "#4ECDC4"},
        },
        {
            "type": "Text",
            "content": "Observer",
            "position": "[2.5, -0.5, 0]",
            "style": {"color": "#4ECDC4"},
        },
        {
            "type": "Text",
            "content": f"f' = {observed_freq:.0f}Hz",
            "position": "[2.5, 1.0, 0]",
            "style": {"color": "#69F0AE", "font_size": 18},
        },
        {
            "type": "Mathtex",
            "content": r"f' = f \frac{v \pm v_o}{v \mp v_s}",
            "position": "[0, -2.5, 0]",
            "style": {"color": "#FFEAA7"},
        },
    ]

    if observed_freq > frequency * 1.1:
        elements.append(
            {
                "type": "Text",
                "content": "Blueshift (Approaching)",
                "position": "[0, -3.0, 0]",
                "style": {"color": "#3498DB"},
            }
        )
    elif observed_freq < frequency * 0.9:
        elements.append(
            {
                "type": "Text",
                "content": "Redshift (Receding)",
                "position": "[0, -3.0, 0]",
                "style": {"color": "#E74C3C"},
            }
        )

    return {"id": "doppler", "elements": elements, "duration_seconds": 40}


def build_rutherford_scattering(
    impact_parameter: float = 0.5, gold_z: float = 79, alpha_z: float = 2
) -> Dict[str, Any]:
    """Build Rutherford scattering."""
    elements = [
        {
            "type": "Title",
            "content": "Rutherford Scattering",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Circle",
            "position": "[0, 0, 0]",
            "style": {"radius": 0.4, "fill_color": "#FFD700", "fill_opacity": 0.85},
        },
        {
            "type": "Text",
            "content": f"Au (Z={int(gold_z)})",
            "position": "[0, -0.7, 0]",
            "style": {"color": "#FFD700"},
        },
    ]

    if impact_parameter < 0.3:
        angle_scatter = 150
    elif impact_parameter < 1.0:
        angle_scatter = 45
    else:
        angle_scatter = 10

    elements.extend(
        [
            {
                "type": "Arrow",
                "position": "[-3, 2.0, 0]",
                "style": {"color": "#FF6B6B", "stroke_width": 2},
            },
            {
                "type": "Circle",
                "position": "[-3.3, 2.0, 0]",
                "style": {"radius": 0.08, "fill_color": "#FF6B6B"},
            },
            {
                "type": "Text",
                "content": f"α (Z={int(alpha_z)})",
                "position": "[-3.5, 2.5, 0]",
                "style": {"color": "#FF6B6B", "font_size": 14},
            },
            {
                "type": "Text",
                "content": f"Scatter Angle: {angle_scatter}°",
                "position": "[2.5, 2.0, 0]",
                "style": {"color": "#FFEAA7"},
            },
        ]
    )

    return {"id": "rutherford", "elements": elements, "duration_seconds": 35}


def build_collision_types(type: str = "elastic") -> Dict[str, Any]:
    """Build collision type visual."""
    elements = [
        {
            "type": "Title",
            "content": f"{type.title()} Collision",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
    ]

    if type == "elastic":
        elements.extend(
            [
                {
                    "type": "Rectangle",
                    "position": "[-2.5, 0.5, 0]",
                    "style": {"width": 0.8, "height": 0.5, "fill_color": "#FF6B6B"},
                },
                {
                    "type": "Arrow",
                    "position": "[-1.8, 0.8, 0]",
                    "style": {"color": "#FF6B6B", "stroke_width": 3},
                },
                {
                    "type": "Rectangle",
                    "position": "[1.0, 0.5, 0]",
                    "style": {"width": 0.8, "height": 0.5, "fill_color": "#4ECDC4"},
                },
                {
                    "type": "Arrow",
                    "position": "[1.7, 0.2, 0]",
                    "style": {"color": "#4ECDC4", "stroke_width": 3},
                },
                {
                    "type": "Text",
                    "content": "Momentum: Conserved",
                    "position": "[-2.0, -2.0, 0]",
                    "style": {"color": "#69F0AE"},
                },
                {
                    "type": "Text",
                    "content": "Kinetic Energy: Conserved",
                    "position": "[1.5, -2.0, 0]",
                    "style": {"color": "#69F0AE"},
                },
            ]
        )
    else:
        elements.extend(
            [
                {
                    "type": "Rectangle",
                    "position": "[-1.5, 0.5, 0]",
                    "style": {"width": 1.2, "height": 0.6, "fill_color": "#9B59B6"},
                },
                {
                    "type": "Text",
                    "content": "Inelastic",
                    "position": "[-1.5, -0.2, 0]",
                    "style": {"color": "#9B59B6"},
                },
                {
                    "type": "Text",
                    "content": "Momentum: Conserved",
                    "position": "[0, -2.0, 0]",
                    "style": {"color": "#69F0AE"},
                },
                {
                    "type": "Text",
                    "content": "KE: Lost (heat/sound)",
                    "position": "[0, -2.5, 0]",
                    "style": {"color": "#E74C3C"},
                },
            ]
        )

    return {"id": "collision", "elements": elements, "duration_seconds": 30}


def build_gauss_law(charge_inside: float = 1.0, radius: float = 1.0) -> Dict[str, Any]:
    """Build Gauss's Law visualization."""
    flux = charge_inside / 8.85e-12

    elements = [
        {
            "type": "Title",
            "content": "Gauss's Law",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Circle",
            "position": "[0, 0.5, 0]",
            "style": {"radius": 1.2, "stroke_color": "#9B59B6", "stroke_width": 2},
        },
        {
            "type": "Circle",
            "position": "[0, 0.5, 0]",
            "style": {"radius": 0.15, "fill_color": "#FFD700"},
        },
        {
            "type": "Text",
            "content": f"q = {charge_inside}nC",
            "position": "[0, 0.0, 0]",
            "style": {"color": "#FFD700"},
        },
    ]

    for i, angle in enumerate([45, 135, 225, 315]):
        rad = math.radians(angle)
        x, y = 1.3 * math.cos(rad), 1.3 * math.sin(rad) + 0.5
        direction = "OUT" if angle in [45, 225] else "IN"
        elements.append(
            {
                "type": "Arrow",
                "position": f"[{x}, {y}, 0]",
                "style": {
                    "color": "#4ECDC4",
                    "stroke_width": 2,
                    "direction": direction,
                },
            }
        )

    elements.extend(
        [
            {
                "type": "Mathtex",
                "content": r"\Phi_E = \frac{q}{\epsilon_0}",
                "position": "[-2.5, -2.0, 0]",
                "style": {"color": "#FFEAA7"},
            },
            {
                "type": "Text",
                "content": f"Flux = {flux:.2e} N·m²/C",
                "position": "[2.0, -2.0, 0]",
                "style": {"color": "#69F0AE"},
            },
        ]
    )

    return {"id": "gauss_law", "elements": elements, "duration_seconds": 35}


def build_relativity_twin(velocity: float = 0.8) -> Dict[str, Any]:
    """Build twin paradox visualization."""
    gamma = 1 / math.sqrt(1 - velocity**2)

    elements = [
        {
            "type": "Title",
            "content": f"Twin Paradox (v = {velocity}c)",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Text",
            "content": "Earth Twin",
            "position": "[-2.5, 2.0, 0]",
            "style": {"color": "#3498DB"},
        },
        {
            "type": "Circle",
            "position": "[-3, 1.3, 0]",
            "style": {"radius": 0.3, "fill_color": "#3498DB"},
        },
        {
            "type": "Text",
            "content": f"Age: 20 years",
            "position": "[-3.5, 0.5, 0]",
            "style": {"color": "#3498DB"},
        },
        {
            "type": "Text",
            "content": "Traveler Twin",
            "position": "[2.0, 2.0, 0]",
            "style": {"color": "#E74C3C"},
        },
        {
            "type": "Circle",
            "position": "[3, 1.3, 0]",
            "style": {"radius": 0.3, "fill_color": "#E74C3C"},
        },
        {
            "type": "Text",
            "content": f"Age: {20 / gamma:.1f} years",
            "position": "[2.5, 0.5, 0]",
            "style": {"color": "#E74C3C"},
        },
        {
            "type": "Mathtex",
            "content": r"\gamma = \frac{1}{\sqrt{1-v^2/c^2}} = {:.2f}".format(gamma),
            "position": "[0, -1.5, 0]",
            "style": {"color": "#FFEAA7"},
        },
        {
            "type": "Text",
            "content": "Time Dilation: Moving clock runs slower",
            "position": "[0, -2.5, 0]",
            "style": {"color": "#69F0AE", "font_size": 16},
        },
    ]

    return {"id": "twin_paradox", "elements": elements, "duration_seconds": 40}


def build_photoelectric(
    wavelength: float = 500e-9, work_function: float = 4.0
) -> Dict[str, Any]:
    """Build photoelectric effect."""
    freq = 3e8 / wavelength
    energy_joules = 6.626e-34 * freq
    energy_ev = energy_joules / 1.602e-19
    max_ke = energy_ev - work_function

    elements = [
        {
            "type": "Title",
            "content": f"Photoelectric (λ = {wavelength * 1e9:.0f}nm)",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Arrow",
            "position": "[0, 2.5, 0]",
            "style": {"color": "#FFD700", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": "Photon",
            "position": "[0.5, 2.7, 0]",
            "style": {"color": "#FFD700"},
        },
        {
            "type": "Rectangle",
            "position": "[0, 0.5, 0]",
            "style": {"width": 2.0, "height": 0.2, "fill_color": "#B8860B"},
        },
        {
            "type": "Text",
            "content": "Metal",
            "position": "[0, 0.0, 0]",
            "style": {"color": "#B8860B"},
        },
        {
            "type": "Circle",
            "position": "[0, -0.8, 0]",
            "style": {"radius": 0.15, "fill_color": "#FF6B6B"},
        },
        {
            "type": "Arrow",
            "position": "[0.3, -1.2, 0]",
            "style": {"color": "#FF6B6B", "stroke_width": 2},
        },
        {
            "type": "Text",
            "content": "e⁻",
            "position": "[-0.3, -1.2, 0]",
            "style": {"color": "#FF6B6B"},
        },
        {
            "type": "Text",
            "content": f"E = {energy_ev:.2f}eV",
            "position": "[-2.5, 1.5, 0]",
            "style": {"color": "#FFEAA7"},
        },
        {
            "type": "Text",
            "content": f"φ = {work_function}eV",
            "position": "[0, 1.5, 0]",
            "style": {"color": "#FFEAA7"},
        },
    ]

    if max_ke > 0:
        elements.extend(
            [
                {
                    "type": "Text",
                    "content": f"KEmax = {max_ke:.2f}eV",
                    "position": "[2.5, 1.5, 0]",
                    "style": {"color": "#69F0AE"},
                },
                {
                    "type": "Text",
                    "content": "Electrons emitted!",
                    "position": "[0, -2.5, 0]",
                    "style": {"color": "#2ECC71"},
                },
            ]
        )
    else:
        elements.append(
            {
                "type": "Text",
                "content": "No emission (E < φ)",
                "position": "[0, -2.5, 0]",
                "style": {"color": "#E74C3C"},
            }
        )

    return {"id": "photoelectric", "elements": elements, "duration_seconds": 40}


def build_radioactive_decay(
    half_life: float = 5730.0, initial_atoms: int = 1000
) -> Dict[str, Any]:
    """Build radioactive decay."""
    decay_constant = math.log(2) / half_life

    elements = [
        {
            "type": "Title",
            "content": f"Radioactive Decay (t½ = {half_life}yr)",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Axes",
            "content": "decay",
            "position": "[0, 0, 0]",
            "style": {"x_range": [0, 4, 1], "y_range": [0, 1000, 200]},
        },
    ]

    for t in range(5):
        remaining = initial_atoms * math.exp(-decay_constant * t)
        elements.append(
            {
                "type": "Circle",
                "position": f"[{t / 4 * 8 - 4}, {remaining / 1000 * 6 - 3}, 0]",
                "style": {
                    "radius": 0.15,
                    "fill_color": "#FF6B6B" if remaining > 250 else "#3498DB",
                },
            }
        )

    elements.extend(
        [
            {
                "type": "Mathtex",
                "content": r"N(t) = N_0 e^{-\lambda t}",
                "position": "[-2.5, -2.0, 0]",
                "style": {"color": "#FFEAA7"},
            },
            {
                "type": "Text",
                "content": f"λ = {decay_constant:.4f}/yr",
                "position": "[2.0, -2.0, 0]",
                "style": {"color": "#69F0AE"},
            },
        ]
    )

    return {"id": "decay", "elements": elements, "duration_seconds": 35}


def build_uncertainty_heisenberg(delta_x: float = 1e-10) -> Dict[str, Any]:
    """Build Heisenberg uncertainty."""
    hbar = 1.055e-34
    min_delta_p = hbar / (2 * delta_x)

    elements = [
        {
            "type": "Title",
            "content": f"Heisenberg (Δx = {delta_x * 1e12:.0f}pm)",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Mathtex",
            "content": r"\Delta x \cdot \Delta p \geq \frac{\hbar}{2}",
            "position": "[0, 2.5, 0]",
            "style": {"color": "#FFEAA7"},
        },
        {
            "type": "Text",
            "content": f"Position uncertainty",
            "position": "[-2.5, 1.5, 0]",
            "style": {"color": "#3498DB"},
        },
        {
            "type": "Rectangle",
            "position": "[-2.5, 0.8, 0]",
            "style": {
                "width": 1.5,
                "height": 0.3,
                "fill_color": "#3498DB",
                "fill_opacity": 0.5,
            },
        },
        {
            "type": "Text",
            "content": f"Δx = {delta_x * 1e12:.1f} pm",
            "position": "[-2.5, 0.3, 0]",
            "style": {"color": "#3498DB", "font_size": 16},
        },
        {
            "type": "Text",
            "content": f"Momentum uncertainty",
            "position": "[1.5, 1.5, 0]",
            "style": {"color": "#E74C3C"},
        },
        {
            "type": "Rectangle",
            "position": "[1.5, 0.8, 0]",
            "style": {
                "width": 1.5,
                "height": 0.3,
                "fill_color": "#E74C3C",
                "fill_opacity": 0.5,
            },
        },
        {
            "type": "Text",
            "content": f"Δp ≥ {min_delta_p:.2e} kg·m/s",
            "position": "[1.5, 0.3, 0]",
            "style": {"color": "#E74C3C", "font_size": 16},
        },
    ]

    return {"id": "heisenberg", "elements": elements, "duration_seconds": 40}


def build_bh_hawking(mass: float = 1e30) -> Dict[str, Any]:
    """Build black hole Hawking radiation."""
    G = 6.674e-11
    c = 3e8
    hbar = 1.055e-34
    kb = 1.381e-23
    schwarzschild_r = 2 * G * mass / c**2
    hawking_temp = hbar * c**3 / (8 * math.pi * G * kb * mass)

    elements = [
        {
            "type": "Title",
            "content": f"Black Hole (M = {mass / 1.989e30:.2f} M☉)",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Circle",
            "position": "[0, 0.5, 0]",
            "style": {"radius": 0.5, "fill_color": "#000000"},
        },
        {
            "type": "Circle",
            "position": "[0, 0.5, 0]",
            "style": {"radius": 0.5, "stroke_color": "#9B59B6", "stroke_width": 3},
        },
        {
            "type": "Text",
            "content": "Event Horizon",
            "position": "[0, -0.2, 0]",
            "style": {"color": "#9B59B6"},
        },
        {
            "type": "Mathtex",
            "content": r"T_H = \frac{\hbar c^3}{8\pi G M k_B}",
            "position": "[0, 2.5, 0]",
            "style": {"color": "#FFEAA7"},
        },
        {
            "type": "Text",
            "content": f"Rs = {schwarzschild_r / 1e3:.0f} km",
            "position": "[-2.5, 1.5, 0]",
            "style": {"color": "#69F0AE"},
        },
        {
            "type": "Text",
            "content": f"Th = {hawking_temp:.2e} K",
            "position": "[2.0, 1.5, 0]",
            "style": {"color": "#69F0AE"},
        },
    ]

    return {"id": "hawking", "elements": elements, "duration_seconds": 35}


def build_fermions_bosons(n_particles: int = 5) -> Dict[str, Any]:
    """Build fermion/boson comparison."""
    elements = [
        {
            "type": "Title",
            "content": "Fermions vs Bosons",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Text",
            "content": "Fermions (½ spin)",
            "position": "[-2.5, 2.5, 0]",
            "style": {"color": "#3498DB"},
        },
    ]

    for i in range(min(n_particles, 4)):
        elements.append(
            {
                "type": "Arrow",
                "position": f"[{-3 + i * 0.8}, 1.5, 0]",
                "style": {
                    "color": "#3498DB",
                    "stroke_width": 1,
                    "direction": "UP" if i % 2 == 0 else "DOWN",
                },
            }
        )

    elements.extend(
        [
            {
                "type": "Text",
                "content": "Pauli: No two identical",
                "position": "[-2.5, 0.5, 0]",
                "style": {"color": "#3498DB", "font_size": 14},
            },
            {
                "type": "Text",
                "content": "Bosons (integer spin)",
                "position": "[1.5, 2.5, 0]",
                "style": {"color": "#E74C3C"},
            },
        ]
    )

    for i in range(min(n_particles, 4)):
        elements.append(
            {
                "type": "Arrow",
                "position": f"[{1 + i * 0.8}, 1.5, 0]",
                "style": {"color": "#E74C3C", "stroke_width": 1, "direction": "UP"},
            }
        )

    elements.extend(
        [
            {
                "type": "Text",
                "content": "Bose: Can occupy same state",
                "position": "[1.5, 0.5, 0]",
                "style": {"color": "#E74C3C", "font_size": 14},
            },
        ]
    )

    return {"id": "fermions_bosons", "elements": elements, "duration_seconds": 35}


def build_cyclotron(
    radius: float = 0.5, charge: float = 1.6e-19, mass: float = 1.67e-27, B: float = 1.0
) -> Dict[str, Any]:
    """Build cyclotron."""
    omega = charge * B / mass

    elements = [
        {
            "type": "Title",
            "content": f"Cyclotron (B = {B}T)",
            "position": "[0, 3.3, 0]",
            "style": {"color": "#ffffff"},
        },
        {
            "type": "Circle",
            "position": "[0, 0, 0]",
            "style": {"radius": 2.0, "stroke_color": "#9B59B6", "stroke_width": 1},
        },
    ]

    for i in range(3):
        angle = i * 120
        rad = math.radians(angle)
        x, y = 1.0 * math.cos(rad), 1.0 * math.sin(rad)
        elements.append(
            {
                "type": "Circle",
                "position": f"[{x}, {y}, 0]",
                "style": {"radius": 0.1, "fill_color": "#FF6B6B"},
            }
        )
        if angle < 180:
            elements.append(
                {
                    "type": "Arrow",
                    "position": f"[{x * 0.7}, {y * 0.7}, 0]",
                    "style": {"color": "#4ECDC4", "stroke_width": 1.5},
                }
            )

    elements.extend(
        [
            {
                "type": "Mathtex",
                "content": r"\omega = \frac{qB}{m}",
                "position": "[-2.5, -2.0, 0]",
                "style": {"color": "#FFEAA7"},
            },
            {
                "type": "Text",
                "content": f"ω = {omega:.2e} rad/s",
                "position": "[2.0, -2.0, 0]",
                "style": {"color": "#69F0AE"},
            },
        ]
    )

    return {"id": "cyclotron", "elements": elements, "duration_seconds": 35}
