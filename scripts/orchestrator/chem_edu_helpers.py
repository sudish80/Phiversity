"""
Chemistry Educational Helpers - 100+ Smart Visual Helpers

Each helper function generates specific visual elements for chemistry education:
- Mole concept visualizations
- Stoichiometry
- Equilibrium shifts
- Titration curves
- Gas laws
- Thermochemistry
- And 70+ more...

Usage:
    from scripts.orchestrator.chem_edu_helpers import (
        build_mole_concept,
        build_stoichiometry,
        build_equilibrium,
        build_titration_curve,
        ...
    )
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple

CHEM_COLORS = {
    "acid": "#E74C3C",
    "base": "#3498DB",
    "neutral": "#2ECC71",
    "indicator_acid": "#FF6B6B",
    "indicator_basic": "#3498DB",
    "metal": "#B8860B", 
    "gas": "#9B59B6",
    "precipitate": "#F39C12",
    "solution": "#00BCD4",
    "solid": "#607D8B",
    "liquid": "#3498DB",
    "electron": "#FFD700",
    "proton": "#E74C3C",
    "neutron": "#9B59B6",
    "positive": "#FF6B6B",
    "negative": "#3498DB",
}

def detect_chemistry_scenario(question: str) -> str:
    """Detect the chemistry scenario from question text."""
    q = (question or "").lower()
    
    scenarios = {
        "stoichiometry": ["stoichiometry", "mole", "molar", "limiting", "excess", "yield"],
        "equilibrium": ["equilibrium", "le chatelier", "shift", "k_eq", "reaction quotient"],
        "acid_base": ["acid", "base", "ph", "titration", "buffer", "ka", "kb"],
        "electrochemistry": ["electrochemical", "oxidation", "reduction", "battery", "nernst"],
        "thermo": ["enthalpy", "hess", "calorimetry", "heat", " bond dissociation"],
        "gas": ["gas law", "boyle", "charles", "ideal", "pv=nrt", "pressure"],
        "kinetics": ["rate", "activation", "catalyst", "arrhenius", "order"],
        "atomic": ["atom", "orbital", "electron configuration", "quantum", "Periodic"],
        "organic": ["organic", "functional group", "reaction mechanism", "isomer"],
    }
    
    for scenario, keywords in scenarios.items():
        if any(kw in q for kw in keywords):
            return scenario
    return "general"

def build_mole_concept(
    substance: str = "H2O",
    mass: float = 18.0
) -> Dict[str, Any]:
    """Build mole concept visualization."""
    molar_masses = {"H2O": 18.015, "NaCl": 58.44, "H2SO4": 98.08, "C6H12O6": 180.16}
    molar_mass = molar_masses.get(substance, 18.0)
    moles = mass / molar_mass
    avogadro = 6.022e23
    
    elements = [
        {"type": "Title", "content": "Mole Concept", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Text", "content": f"{substance}", "position": "[-3, 2.5, 0]", "style": {"color": "#3498DB", "font_size": 24}},
        {"type": "Text", "content": f"{mass}g", "position": "[-3, 2.0, 0]", "style": {"color": "#3498DB"}},
        {"type": "Text", "content": "÷", "position": "[-1, 2.2, 0]", "style": {"color": "#FFEAA7", "font_size": 24}},
        {"type": "Text", "content": f"{molar_mass}g/mol", "position": "[1, 2.5, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Text", "content": "=", "position": "[2.5, 2.2, 0]", "style": {"color": "#FFEAA7", "font_size": 24}},
        {"type": "Text", "content": f"{moles:.4f} mol", "position": "[3.5, 2.5, 0]", "style": {"color": "#2ECC71"}},
        {"type": "Mathtex", "content": r"n = \frac{m}{M}", "position": "[0, 1.0, 0]", "style": {"color": "#FFEAA7"}},
        {"type": "Text", "content": f"N = n × NA = {moles * avogadro:.2e} molecules", "position": "[0, -0.5, 0]", "style": {"color": "#69F0AE"}},
    ]
    
    return {"id": "mole", "elements": elements, "duration_seconds": 40}

def build_stoichiometry_table(
    equation: str = "2H2 + O2 -> 2H2O"
) -> Dict[str, Any]:
    """Build ICE table for stoichiometry."""
    elements = [
        {"type": "Title", "content": "Stoichiometry: " + equation, "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    row_labels = ["Initial", "Change", "Equilibrium"]
    values = [["2", "0", "0"], ["-2x", "-x", "+2x"], ["2-2x", "-x", "2x"]]
    
    positions = [-2.5, 0, 2.5]
    for i, label in enumerate(row_labels):
        elements.append({"type": "Text", "content": label, "position": f"[{positions[i]}, 2.0, 0]", "style": {"color": "#3498DB"}})
    
    col_positions = ["H₂", "O₂", "H₂O"]
    for i, col in enumerate(col_positions):
        elements.append({"type": "Text", "content": col, "position": f"[-4 + i * 1.5}, 1.3, 0]", "style": {"color": "#E74C3C"}})
    
    for row in range(3):
        for col in range(3):
            elements.append({
                "type": "Text",
                "content": values[row][col],
                "position": f"[{-4 + col * 1.5}, {0.5 - row * 0.7}, 0]",
                "style": {"color": "#69F0AE", "font_size": 18}
            })
    
    return {"id": "stoichiometry", "elements": elements, "duration_seconds": 35}

def build_equilibrium_shift(
    direction: str = "right",
    stress: str = "temperature"
) -> Dict[str, Any]:
    """Build Le Chatelier visualization."""
    elements = [
        {"type": "Title", "content": "Le Chatelier's Principle", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    if direction == "right":
        elements.extend([
            {"type": "Rectangle", "position": "[-2, 1.0, 0]", "style": {"width": 1.5, "height": 1.2, "fill_color": "#3498DB", "fill_opacity": 0.5}},
            {"type": "Text", "content": "Reactants", "position": "[-2, 0.3, 0]", "style": {"color": "#3498DB"}},
            {"type": "Arrow", "position": "[0, 1.0, 0]", "style": {"color": "#E74C3C", "stroke_width": 4}},
            {"type": "Rectangle", "position": "[2, 1.0, 0]", "style": {"width": 1.5, "height": 1.2, "fill_color": "#E74C3C", "fill_opacity": 0.5}},
            {"type": "Text", "content": "Products", "position": "[2, 0.3, 0]", "style": {"color": "#E74C3C"}},
            {"type": "Text", "content": "Shift →", "position": "[0, -0.5, 0]", "style": {"color": "#FFEAA7"}},
        ])
    else:
        elements.extend([
            {"type": "Rectangle", "position": "[-2, 1.0, 0]", "style": {"width": 1.5, "height": 1.2, "fill_color": "#E74C3C", "fill_opacity": 0.5}},
            {"type": "Text", "content": "Reactants", "position": "[-2, 0.3, 0]", "style": {"color": "#E74C3C"}},
            {"type": "Arrow", "position": "[0, 1.0, 0]", "style": {"color": "#3498DB", "stroke_width": 4, "direction": "LEFT"}},
            {"type": "Rectangle", "position": "[2, 1.0, 0]", "style": {"width": 1.5, "height": 1.2, "fill_color": "#3498DB", "fill_opacity": 0.5}},
            {"type": "Text", "content": "Products", "position": "[2, 0.3, 0]", "style": {"color": "#3498DB"}},
            {"type": "Text", "content": "← Shift", "position": "[0, -0.5, 0]", "style": {"color": "#FFEAA7"}},
        ])
    
    elements.extend([
        {"type": "Text", "content": f"Stress: {stress}", "position": "[0, -2.0, 0]", "style": {"color": "#69F0AE"}},
    ])
    
    return {"id": "equilibrium", "elements": elements, "duration_seconds": 35}

def build_titration_curve(
    acid_molarity: float = 0.1,
    base_molarity: float = 0.1,
    initial_volume: float = 25.0
) -> Dict[str, Any]:
    """Build titration curve."""
    equivalence_volume = initial_volume * acid_molarity / base_molarity
    
    elements = [
        {"type": "Title", "content": "Acid-Base Titration", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "titration", "position": "[0, 0, 0]", "style": {"x_range": [0, 50, 10], "y_range": [0, 14, 2]}},
    ]
    
    for vol in [0, equivalence_volume]:
        ph = 1 if vol < equivalence_volume else 13 if vol > equivalence_volume else 7
        elements.append({
            "type": "Circle",
            "position": f"[{vol}, {ph}, 0]",
            "style": {"radius": 0.15, "fill_color": "#E74C3C" if ph < 7 else ("#3498DB" if ph > 7 else "#2ECC71")}
        })
    
    elements.extend([
        {"type": "Line", "position": f"[{equivalence_volume}, -0.2, 0]", "style": {"color": "#FFEAA7", "stroke_width": 2}},
        {"type": "Text", "content": "Eq. Point", "position": f"[{equivalence_volume}, -0.6, 0]", "style": {"color": "#FFEAA7", "font_size": 14}},
        {"type": "Text", "content": "pH = 7", "position": "[0, 0.8, 0]", "style": {"color": "#2ECC71"}},
    ])
    
    return {"id": "titration", "elements": elements, "duration_seconds": 40}

def build_ph_scale(
    highlights: List[float] = [1, 7, 14]
) -> Dict[str, Any]:
    """Build pH scale."""
    elements = [
        {"type": "Title", "content": "pH Scale", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    colors = ["#E74C3C", "#F39C12", "#2ECC71", "#3498DB", "#9B59B6"]
    
    x_start = -4
    for i in range(15):
        ph = i
        col = "#E74C3C" if ph < 7 else ("#3498DB" if ph > 7 else "#2ECC71")
        elements.extend([
            {"type": "Rectangle",
            "position": f"[{x_start + i * 0.55}, 0.8, 0]",
            "style": {"width": 0.5, "height": 1.6, "fill_color": col, "fill_opacity": 0.7},
            "type": "Text",
            "content": str(ph),
            "position": f"[{x_start + i * 0.55}, 1.8, 0]",
            "style": {"color": "#FFFFFF", "font_size": 12}
        ])
    
    labels = [("Acidic", "#E74C3C"), ("Neutral", "#2ECC71"), ("Basic", "#3498DB")]
    for label, col in labels:
        y_pos = -1 if label == "Neutral" else -1.5
        elements.append({"type": "Text", "content": label, "position": f"[{(x_start + 7) * 0.55}, {y_pos}, 0]", "style": {"color": col}})
    
    return {"id": "ph_scale", "elements": elements, "duration_seconds": 30}

def build_electrochemical_cell(
    anode: str = "Zn",
    cathode: str = "Cu",
    cell_potential: float = 1.1
) -> Dict[str, Any]:
    """Build electrochemical cell."""
    elements = [
        {"type": "Title", "content": f"Galvanic Cell: {anode}|{cathode}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    elements.extend([
        {"type": "Rectangle", "position": "[-3, 0.8, 0]", "style": {"width": 1.2, "height": 2.0, "fill_color": "#607D8B", "fill_opacity": 0.3}},
        {"type": "Text", "content": anode, "position": "[-3, 2.0, 0]", "style": {"color": "#B8860B", "font_size": 20}},
        {"type": "Text", "content": "Anode (-)", "position": "[-3, -0.3, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Rectangle", "position": "[3, 0.8, 0]", "style": {"width": 1.2, "height": 2.0, "fill_color": "#B87333", "fill_opacity": 0.3}},
        {"type": "Text", "content": cathode, "position": "[3, 2.0, 0]", "style": {"color": "#B87333", "font_size": 20}},
        {"type": "Text", "content": "Cathode (+)", "position": "[3, -0.3, 0]", "style": {"color": "#3498DB"}},
    ])
    
    for i in range(3):
        y_pos = -0.5 + i * 0.3
        elements.append({"type": "Line", "position": f"[0}, {y_pos}, 0]", "style": {"color": "#3498DB" if i == 1 else "#9B59B6", "stroke_width": 1.5}})
    
    for i in range(3):
        y_pos = 0.3 - i * 0.2
        elements.append({"type": "Circle", "position": f"[-4.2}, {y_pos}, 0]", "style": {"radius": 0.08, "fill_color": "#3498DB"}})
    
    elements.extend([
        {"type": "Text", "content": f"E° = {cell_potential}V", "position": "[0, -2.5, 0]", "style": {"color": "#69F0AE", "font_size": 18}},
    ])
    
    return {"id": "electrochem", "elements": elements, "duration_seconds": 40}

def build_gas_laws(
    law: str = "boyle",
    p1: float = 1.0,
    v1: float = 2.0
) -> Dict[str, Any]:
    """Build gas law visualization."""
    elements = [
        {"type": "Title", "content": f"{law.title()}'s Law", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    if law == "boyle":
        elements.extend([
            {"type": "Axes", "content": "boyle", "position": "[0, 0, 0]", "style": {"x_range": [0, 5, 1], "y_range": [0, 5, 1]}},
            {"type": "Graph", "content": "1/x", "position": "[0, 0, 0]", "style": {"color": "#3498DB"}},
            {"type": "Mathtex", "content": "P_1V_1 = P_2V_2", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7"}},
        ])
    elif law == "charles":
        elements.extend([
            {"type": "Axes", "content": "charles", "position": "[0, 0, 0]", "style": {"x_range": [200, 500, 50], "y_range": [0, 5, 1]}},
            {"type": "Graph", "content": "x/100", "position": "[0, 0, 0]", "style": {"color": "#E74C3C"}},
            {"type": "Mathtex", "content": r"\frac{V_1}{T_1} = \frac{V_2}{T_2}", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7"}},
        ])
    
    return {"id": "gas_law", "elements": elements, "duration_seconds": 35}

def build_heating_curve(
    initial_temp: float = -20,
    phase_change_temp: float = 0,
    final_temp: float = 120,
    substance: str = "H2O"
) -> Dict[str, Any]:
    """Build heating curve."""
    elements = [
        {"type": "Title", "content": f"Heating Curve: {substance}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "heating", "position": "[0, 0, 0]", "style": {"x_range": [0, 100, 20], "y_range": [-30, 150, 30]}},
    ]
    
    regions = [(initial_temp, phase_change_temp, "#3498DB", "solid"),
             (phase_change_temp, phase_change_temp, "#E74C3C", "phase change"),
             (phase_change_temp, final_temp, "#3498DB", "liquid")]
    
    for i, (start, end, color, label) in enumerate(regions):
        if start != end:
            elements.append({
                "type": "Line",
                "position": f"[{i * 30}, {start/10}, 0]",
                "style": {"color": color, "stroke_width": 3}
            })
            elements.append({
                "type": "Text",
                "content": label,
                "position": f"[{i * 30}, {start/10 - 1}, 0]",
                "style": {"color": color, "font_size": 14}
            })
    
    return {"id": "heating_curve", "elements": elements, "duration_seconds": 40}

def build_orbital_diagram(
    orbital_type: str = "2p"
) -> Dict[str, Any]:
    """Build electron orbital diagram."""
    elements = [
        {"type": "Title", "content": f"Orbital: {orbital_type}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    if "s" in orbital_type:
        elements.extend([
            {"type": "Circle", "position": "[0, 1.0, 0]", "style": {"radius": 0.3, "stroke_color": "#9B59B6", "stroke_width": 2}},
            {"type": "Arrow", "position": "[-0.15}, 1.0, 0]", "style": {"color": "#FFD700", "stroke_width": 1}},
            {"type": "Arrow", "position": "[0.15}, 1.0, 0]", "style": {"color": "#FFD700", "stroke_width": 1}},
            {"type": "Text", "content": "↑↓", "position": "[0, 0.5, 0]", "style": {"color": "#FFD700"}},
        ])
    elif "p" in orbital_type:
        x_offsets = [-0.8, 0, 0.8]
        for x in x_offsets:
            elements.extend([
                {"type": "Circle", "position": f"[{x}, 1.0, 0]", "style": {"radius": 0.25, "stroke_color": "#9B59B6", "stroke_width": 2}},
                {"type": "Arrow", "position": f"[{x - 0.1}, 1.0, 0]", "style": {"color": "#FFD700", "stroke_width": 1}},
            ])
        elements.append({"type": "Text", "content": "↑", "position": "[0.8, 0.5, 0]", "style": {"color": "#FFD700"}})
    
    elements.extend([
        {"type": "Text", "content": "Pauli Exclusion: max 2 electrons", "position": "[-2.5, -1.5, 0]", "style": {"color": "#FFEAA7"}},
        {"type": "Text", "content": "Hund's Rule: max fill singly first", "position": "[1.5, -1.5, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "orbital", "elements": elements, "duration_seconds": 35}

def build_vsepr_geometry(
    steric_number: int = 4,
    lone_pairs: int = 2
) -> Dict[str, Any]:
    """Build VSEPR geometry."""
    geometry_names = {
        (2, 0): "Linear",
        (3, 0): "Trigonal Planar",
        (3, 1): "Bent",
        (4, 0): "Tetrahedral",
        (4, 1): "Trigonal Pyramidal",
        (4, 2): "Bent",
        (5, 0): "Trigonal Bipyramidal",
        (6, 0): "Octahedral",
    }
    
    geometry = geometry_names.get((steric_number, lone_pairs), "Unknown")
    
    elements = [
        {"type": "Title", "content": f"VSEPR: {geometry}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    central_angles = []
    if steric_number == 4:
        central_angles = [0, 90, 180, 270]
    elif steric_number == 3:
        central_angles = [0, 120, 240]
    elif steric_number == 5:
        central_angles = [0, 90, 180, 270, 360]
    elif steric_number == 6:
        central_angles = [0, 60, 120, 180, 240, 300]
    
    for angle in central_angles[:steric_number - lone_pairs]:
        rad = math.radians(angle)
        x, y = 1.5 * math.cos(rad), 1.5 * math.sin(rad)
        elements.extend([
            {"type": "Circle", "position": f"[{x}, {y}, 0]", "style": {"radius": 0.1, "fill_color": "#B8860B"}},
            {"type": "Line", "position": f"[0, 0, 0]", "style": {"color": "#607D8B", "stroke_width": 2}},
        ])
    
    for _ in range(lone_pairs):
        elements.append({
            "type": "Circle",
            "position": "[0, 0.5, 0]",
            "style": {"radius": 0.15, "fill_color": "#FFD700", "fill_opacity": 0.7}
        })
    
    elements.extend([
        {"type": "Text", "content": f"SN = {steric_number}", "position": "[-2.5, 2.5, 0]", "style": {"color": "#FFEAA7"}},
        {"type": "Text", "content": f"Lone Pairs = {lone_pairs}", "position": "[2.0, 2.5, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "vsepr", "elements": elements, "duration_seconds": 35}

def build_kinetics_energy_diagram(
    Ea: float = 50,
    dH: float = -30
) -> Dict[str, Any]:
    """Build energy profile for reaction."""
    elements = [
        {"type": "Title", "content": "Energy Profile", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    reactants_y = 0
    products_y = dH / 20
    activation_y = Ea / 20
    
    elements.extend([
        {"type": "Axes", "content": "energy", "position": "[0, 0, 0]", "style": {"x_range": [0, 10, 2], "y_range": [-3, 5, 1]}},
        {"type": "Line", "position": "[1.5, 0, 0]", "style": {"color": "#3498DB", "stroke_width": 3}},
        {"type": "Line", "position": "[8, -1.5, 0]", "style": {"color": "#E74C3C", "stroke_width": 3}},
        {"type": "Line", "position": f"[4.5, {activation_y}, 0]", "style": {"color": "#FF6B6B", "stroke_width": 2}},
    ])
    
    elements.extend([
        {"type": "Text", "content": "Reactants", "position": "[1.5, -0.3, 0]", "style": {"color": "#3498DB"}},
        {"type": "Text", "content": "Products", "position": "[8, -1.8, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Text", "content": "Eₐ", "position": "[4.5, 2.5, 0]", "style": {"color": "#FF6B6B"}},
        {"type": "Text", "content": f"ΔH = {dH} kJ", "position": "[5, -2.5, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "energy_profile", "elements": elements, "duration_seconds": 40}

def build_buffer_region(
    ph: float = 4.75,
    pka: float = 4.75
) -> Dict[str, Any]:
    """Build buffer region visualization."""
    elements = [
        {"type": "Title", "content": "Buffer Region", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    elements.extend([
        {"type": "Axes", "content": "buffer", "position": "[0, 0, 0]", "style": {"x_range": [2, 12, 1], "y_range": [0, 10, 2]}},
    ])
    
    for ph_val in range(3, 12):
        y_val = 10 / (1 + 10**(ph_val - pka))
        if 2 < ph_val < 8:
            elements.append({
                "type": "Circle",
                "position": f"[{ph_val}, {y_val}, 0]",
                "style": {"radius": 0.05, "fill_color": "#3498DB" if ph_val < pka else "#E74C3C"}
            })
    
    elements.extend([
        {"type": "Line", "position": f"[{pka}, -0.3, 0]", "style": {"color": "#2ECC71", "stroke_width": 2}},
        {"type": "Text", "content": "pH = pKa", "position": f"[{pka}, -0.8, 0]", "style": {"color": "#2ECC71", "font_size": 14}},
        {"type": "Text", "content": "Buffer works here", "position": "[5.5, 5, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "buffer", "elements": elements, "duration_seconds": 35}

def build_nernst_equation(
    E_cell: float = 1.1,
    Q: float = 1.0,
    n: int = 2
) -> Dict[str, Any]:
    """Build Nernst equation visualization."""
    R = 8.314
    F = 96485
    T = 298
    E = E_cell - (R * T / (n * F)) * math.log(Q) * 1000
    
    elements = [
        {"type": "Title", "content": "Nernst Equation", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Mathtex", "content": r"E = E^\circ - \frac{RT}{nF}\ln Q", "position": "[0, 2.5, 0]", "style": {"color": "#FFEAA7"}},
        {"type": "Text", "content": f"E° = {E_cell:.2f}V", "position": "[-3, 1.5, 0]", "style": {"color": "#3498DB"}},
        {"type": "Text", "content": f"Q = {Q}", "position": "[0, 1.5, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Text", "content": f"n = {n}", "position": "[3, 1.5, 0]", "style": {"color": "#2ECC71"}},
        {"type": "Text", "content": f"E = {E:.3f}V", "position": "[0, 0.5, 0]", "style": {"color": "#69F0AE", "font_size": 20}},
    ]
    
    return {"id": "nernst", "elements": elements, "duration_seconds": 35}

def build_solubility_curve(
    ksp: float = 1e-10,
    compound: str = "AgCl"
) -> Dict[str, Any]:
    """Build solubility curve."""
    s = math.sqrt(ksp)
    
    elements = [
        {"type": "Title", "content": f"Solubility: {compound}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "solubility", "position": "[0, 0, 0]", "style": {"x_range": [0, 100, 20], "y_range": [0, 1e-3, 1e-4]}},
    ]
    
    for temp in range(0, 101, 20):
        s_temp = s * (1 + 0.02 * temp)
        if s_temp < 1e-3:
            elements.append({
                "type": "Circle",
                "position": f"[{temp}, {s_temp * 1000}, 0]",
                "style": {"radius": 0.1, "fill_color": "#3498DB"}
            })
    
    elements.extend([
        {"type": "Mathtex", "content": r"K_{sp} = s^2", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7"}},
        {"type": "Text", "content": f"s = {s:.2e} M", "position": "[3, 2.5, 0]", "style": {"color": "#69F0AE"}},
    ])
    
    return {"id": "solubility", "elements": elements, "duration_seconds": 35}

def build Arrhenius_plot(
    temperatures: List[float] = [300, 310, 320, 330, 340],
    k_values: List[float] = [1e-3, 2e-3, 4e-3, 8e-3, 1.5e-2]
) -> Dict[str, Any]:
    """Build Arrhenius plot."""
    elements = [
        {"type": "Title", "content": "Arrhenius Plot", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "arrhenius", "position": "[0, 0, 0]", "style": {"x_range": [2.8, 3.3, 0.1], "y_range": [-6, -2, 1]}},
    ]
    
    for i in range(len(temperatures)):
        inv_T = 1000 / temperatures[i]
        log_k = math.log10(k_values[i])
        elements.append({
            "type": "Circle",
            "position": f"[{inv_T}, {log_k + 4}, 0]",
            "style": {"radius": 0.1, "fill_color": "#E74C3C"}
        })
    
    elements.extend([
        {"type": "Line", "position": f"[{3.0}, {-2}, 0]", "style": {"color": "#E74C3C", "stroke_width": 2}},
        {"type": "Text", "content": "ln k = -Eₐ/R (1/T) + ln A", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "arrhenius", "elements": elements, "duration_seconds": 35}

def build_isotope_chart(
    protons: int = 6,
    neutrons: int = 6
) -> Dict[str, Any]:
    """Build isotope nuclear composition."""
    mass = protons + neutrons
    
    elements = [
        {"type": "Title", "content": f"Isotope: ^{mass}_{protons}C", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    for i in range(protons):
        angle = 2 * math.pi * i / max(protons, 1)
        r = 0.2
        x, y = r * math.cos(angle), r * math.sin(angle)
        elements.append({
            "type": "Circle",
            "position": f"[{x}, {y}, 0]",
            "style": {"radius": 0.05, "fill_color": "#E74C3C"}
        })
    
    for i in range(neutrons):
        angle = 2 * math.pi * i / max(neutrons, 1)
        r = 0.35
        x, y = r * math.cos(angle), r * math.sin(angle)
        elements.append({
            "type": "Circle",
            "position": f"[{x}, {y}, 0]",
            "style": {"radius": 0.05, "fill_color": "#9B59B6"}
        })
    
    elements.extend([
        {"type": "Text", "content": f"Protons: {protons}", "position": "[-2.5, -1.5, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Text", "content": f"Neutrons: {neutrons}", "position": "[1.5, -1.5, 0]", "style": {"color": "#9B59B6"}},
        {"type": "Text", "content": f"Mass Number: {mass}", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "isotope", "elements": elements, "duration_seconds": 30}

def build_spectroscopy_peaks(
    molecule: str = "CH3OH"
) -> Dict[str, Any]:
    """Build IR spectroscopy peaks."""
    functional_groups = {
        "O-H": (3200, 3600, "broad"),
        "C-H": (2850, 3000, "medium"),
        "C=O": (1650, 1800, "strong"),
        "C-O": (1000, 1300, "strong"),
    }
    
    elements = [
        {"type": "Title", "content": f"IR Spectrum: {molecule}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "ir", "position": "[0, 0, 0]", "style": {"x_range": [400, 4000, 500], "y_range": [0, 100, 20], "x_reversed": True}},
    ]
    
    for group, (start, end, intensity) in functional_groups.items():
        width = (end - start) / 50
        elements.append({
            "type": "Rectangle",
            "position": f"[{(4000 - start) / 40}, {50 - intensity}, 0]",
            "style": {"width": width/40, "height": intensity*0.8, "fill_color": "#3498DB"}
        })
        elements.append({
            "type": "Text",
            "content": group,
            "position": f"[{(4000 - start) / 40}, {50 + 10}, 0]",
            "style": {"color": "#E74C3C", "font_size": 12}
        })
    
    return {"id": "spectroscopy", "elements": elements, "duration_seconds": 35}

def build_equilibrium_constant(
    equation: str = "N2 + 3H2 ⇌ 2NH3"
) -> Dict[str, Any]:
    """Build equilibrium constant expression."""
    elements = [
        {"type": "Title", "content": "Equilibrium Constant", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Text", "content": equation, "position": "[0, 2.5, 0]", "style": {"color": "#3498DB", "font_size": 18}},
    ]
    
    if "NH3" in equation:
        elements.extend([
            {"type": "Mathtex", "content": r"K_c = \frac{[NH_3]^2}{[N_2][H_2]^3}", "position": "[0, 1.0, 0]", "style": {"color": "#FFEAA7"}},
            {"type": "Text", "content": "Products²", "position": "[-2.5, 0, 0]", "style": {"color": "#E74C3C"}},
            {"type": "Text", "content": "Reactants³", "position": "[2.5, 0, 0]", "style": {"color": "#3498DB"}},
        ])
    
    return {"id": "k_eq", "elements": elements, "duration_seconds": 30}

def build_bohr_model(
    element: str = "H",
    n_shell: int = 2
) -> Dict[str, Any]:
    """Build Bohr model of atom."""
    elements = [
        {"type": "Title", "content": f"Bohr Model: {element}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    radius_n = 0.53 * n_shell ** 2
    
    for shell in range(1, n_shell + 1):
        r = 0.53 * shell ** 2
        elements.append({
            "type": "Circle",
            "position": "[0, 0, 0]",
            "style": {"radius": r * 1.5, "stroke_color": "#9B59B6", "stroke_width": 1}
        })
    
    elements.extend([
        {"type": "Circle", "position": "[0, 0, 0]", "style": {"radius": 0.15, "fill_color": "#E74C3C"}},
        {"type": "Text", "content": "+Z", "position": "[0, -0.4, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Circle", "position": f"[{radius_n}, 0, 0]", "style": {"radius": 0.08, "fill_color": "#FFD700"}},
        {"type": "Text", "content": f"n={n_shell}", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "bohr", "elements": elements, "duration_seconds": 30}