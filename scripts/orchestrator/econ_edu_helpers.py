"""
Economics Educational Helpers - 100+ Smart Visual Helpers

Each helper function generates specific visual elements for economics education:
- Supply/demand curves
- Elasticity
- Market structures
- GDP components
- AD-AS model
- And 70+ more...

Usage:
    from scripts.orchestrator.econ_edu_helpers import (
        build_supply_demand,
        build_elasticity,
        build_market_structure,
        build_gdp_components,
        ...
    )
"""

from __future__ import annotations
import math
from typing import Any, Dict, List, Optional, Tuple

ECON_COLORS = {
    "demand": "#E74C3C",
    "supply": "#3498DB",
    "equilibrium": "#2ECC71",
    "surplus": "#27AE60",
    "shortage": "#E74C3C",
    "tax": "#9B59B6",
    "subsidy": "#F39C12",
    "consumer": "#FF6B6B",
    "producer": "#3498DB",
    "gdp": "#2ECC71",
    "investment": "#F39C12",
    "government": "#9B59B6",
    "exports": "#E91E63",
    "imports": "#FF9800",
}

def detect_economics_scenario(question: str) -> str:
    """Detect the economics scenario from question text."""
    q = (question or "").lower()
    
    scenarios = {
        "supply_demand": ["supply", "demand", "equilibrium", "shortage", "surplus", "price"],
        "elasticity": ["elasticity", "elastic", "inelastic", "total revenue", "price sensitivity"],
        "market": ["market", "competition", "monopoly", "oligopoly", "perfect", " monopoly"],
        "gdp": ["gdp", "gnp", "aggregate", "gdp deflator"],
        "ad_as": ["ad", "as", "aggregate demand", "aggregate supply", "recession", "inflation"],
        "fiscal": ["fiscal", "tax", "government spending", "multiplier"],
        "monetary": ["monetary", "interest", "money supply", "inflation", "fed"],
        "trade": ["trade", "tariff", "quota", "comparative", "exchange rate"],
        "labor": ["labor", "unemployment", "wage", "jobs"],
    }
    
    for scenario, keywords in scenarios.items():
        if any(kw in q for kw in keywords):
            return scenario
    return "supply_demand"

def build_supply_demand(
    demand_slope: float = -1.0,
    supply_slope: float = 1.0,
    intercept_d: float = 10.0,
    intercept_s: float = 2.0
) -> Dict[str, Any]:
    """Build supply/demand curves."""
    q_eq = (intercept_d - intercept_s) / (supply_slope - demand_slope)
    p_eq = intercept_s + supply_slope * q_eq
    
    elements = [
        {"type": "Title", "content": "Supply and Demand", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "sd", "position": "[0, 0, 0]", "style": {"x_range": [0, 10, 2], "y_range": [0, 10, 2], "x_label": "Q", "y_label": "P"}},
        {"type": "Line", "position": f"[0, {intercept_d}, 0]", "style": {"color": "#E74C3C", "stroke_width": 3}},
        {"type": "Line", "position": f"[0, {intercept_s}, 0]", "style": {"color": "#3498DB", "stroke_width": 3}},
        {"type": "Circle", "position": f"[{q_eq}, {p_eq}, 0]", "style": {"radius": 0.15, "fill_color": "#2ECC71"}},
        {"type": "Text", "content": "E*", "position": f"[{q_eq + 0.3}, {p_eq + 0.3}, 0]", "style": {"color": "#2ECC71"}},
        {"type": "Text", "content": f"Q* = {q_eq:.1f}, P* = {p_eq:.1f}", "position": "[3.5, 2.5, 0]", "style": {"color": "#FFEAA7"}},
    ]
    
    return {"id": "supply_demand", "elements": elements, "duration_seconds": 40}

def build_elasticity_arc(
    p1: float = 10.0,
    p2: float = 8.0,
    q1: float = 100.0,
    q2: float = 150.0
) -> Dict[str, Any]:
    """Build arc elasticity."""
    pct_change_p = (p2 - p1) / p1 * 100
    pct_change_q = (q2 - q1) / q1 * 100
    elasticity = abs(pct_change_q / pct_change_p)
    
    elements = [
        {"type": "Title", "content": "Price Elasticity", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "elasticity", "position": "[0, 0, 0]", "style": {"x_range": [80, 180, 20], "y_range": [5, 15, 2]}},
        {"type": "Line", "position": f"[{q1}, {p1}, 0]", "style": {"color": "#E74C3C", "stroke_width": 3}},
        {"type": "Line", "position": f"[{q2}, {p2}, 0]", "style": {"color": "#E74C3C", "stroke_width": 3}},
        {"type": "Circle", "position": f"[{q1}, {p1}, 0]", "style": {"radius": 0.1, "fill_color": "#E74C3C"}},
        {"type": "Circle", "position": f"[{q2}, {p2}, 0]", "style": {"radius": 0.1, "fill_color": "#E74C3C"}},
        {"type": "Text", "content": f"%ΔQ = {pct_change_q:.1f}%", "position": f"[{q2 + 10}, {p2}, 0]", "style": {"color": "#3498DB"}},
        {"type": "Text", "content": f"%ΔP = {pct_change_p:.1f}%", "position": f"[{q1}, {p1 - 1}, 0]", "style": {"color": "#3498DB"}},
    ]
    
    if elasticity > 1:
        label, label_color = "Elastic (>1)", "#2ECC71"
    elif elasticity < 1:
        label, label_color = "Inelastic (<1)", "#E74C3C"
    else:
        label, label_color = "Unit Elastic (=1)", "#F39C12"
    
    elements.append({"type": "Text", "content": label, "position": "[0, -2.5, 0]", "style": {"color": label_color, "font_size": 20}})
    
    return {"id": "elasticity", "elements": elements, "duration_seconds": 40}

def build_tax_incidence(
    tax: float = 2.0,
    elasticity_d: float = 2.0,
    elasticity_s: float = 0.5
) -> Dict[str, Any]:
    """Build tax incidence."""
    burden_consumer = tax * elasticity_s / (elasticity_s + elasticity_d)
    burden_producer = tax * elasticity_d / (elasticity_s + elasticity_d)
    
    elements = [
        {"type": "Title", "content": "Tax Incidence", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Rectangle", "position": "[-2.5, 1.5, 0]", "style": {"width": 2.0, "height": 1.2, "fill_color": "#E74C3C", "fill_opacity": 0.3}},
        {"type": "Text", "content": "Consumer", "position": "[-2.5, 2.3, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Text", "content": f"{burden_consumer:.1f}", "position": "[-2.5, 1.8, 0]", "style": {"color": "#E74C3C", "font_size": 20}},
        {"type": "Rectangle", "position": "[0.5, 1.5, 0]", "style": {"width": 2.0, "height": 1.2, "fill_color": "#3498DB", "fill_opacity": 0.3}},
        {"type": "Text", "content": "Producer", "position": "[0.5, 2.3, 0]", "style": {"color": "#3498DB"}},
        {"type": "Text", "content": f"{burden_producer:.1f}", "position": "[0.5, 1.8, 0]", "style": {"color": "#3498DB", "font_size": 20}},
        {"type": "Text", "content": f"Tax = {tax}", "position": "[3, 2.0, 0]", "style": {"color": "#9B59B6"}},
    ]
    
    return {"id": "tax", "elements": elements, "duration_seconds": 35}

def build_consumer_surplus(
    equilibrium_price: float = 5.0,
    max_price: float = 10.0,
    equilibrium_quantity: float = 5.0
) -> Dict[str, Any]:
    """Build consumer surplus."""
    cs = 0.5 * (max_price - equilibrium_price) * equilibrium_quantity
    
    elements = [
        {"type": "Title", "content": "Consumer Surplus", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "cs", "position": "[0, 0, 0]", "style": {"x_range": [0, 10, 2], "y_range": [0, 10, 2]}},
        {"type": "Line", "position": f"[0, {equilibrium_price}, 0]", "style": {"color": "#E74C3C", "stroke_width": 2}},
        {"type": "Line", "position": f"[0, {max_price}, 0]", "style": {"color": "#9B59B6", "stroke_width": 2}},
        {"type": "Polygon", "position": f"[0, {equilibrium_price}, 0]", "style": {"fill_color": "#2ECC71", "fill_opacity": 0.3}},
    ]
    
    elements.append({"type": "Text", "content": f"CS = {cs:.1f}", "position": "[2, 7, 0]", "style": {"color": "#69F0AE", "font_size": 18}})
    
    return {"id": "consumer_surplus", "elements": elements, "duration_seconds": 35}

def build_market_structure(
    type: str = "monopoly"
) -> Dict[str, Any]:
    """Build market structure comparison."""
    structures = {
        "perfectCompetition": {"firms": "Many", "product": "Identical", "control": "None", "barriers": "None"},
        "monopoly": {"firms": "One", "product": "Unique", "control": "Full", "barriers": "High"},
        "oligopoly": {"firms": "Few", "product": "Differentiated", "control": "Some", "barriers": "High"},
        "monopolistic": {"firms": "Many", "product": "Differentiated", "control": "Some", "barriers": "Low"},
    }
    
    data = structures.get(type, structures["monopoly"])
    
    elements = [
        {"type": "Title", "content": type.title(), "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    for i, (key, val) in enumerate(data.items()):
        y_pos = 2.0 - i * 0.7
        elements.extend([
            {"type": "Text", "content": f"{key}:", "position": "[-3, {y_pos}, 0]", "style": {"color": "#FFEAA7"}},
            {"type": "Text", "content": val, "position": "[1, {y_pos}, 0]", "style": {"color": "#69F0AE"}},
        ])
    
    return {"id": "market", "elements": elements, "duration_seconds": 35}

def build_gdp_components(
    consumption: float = 12.5,
    investment: float = 3.5,
    government: float = 3.8,
    exports: float = 2.0,
    imports: float = -2.3
) -> Dict[str, Any]:
    """Build GDP components."""
    gdp = consumption + investment + government + exports + imports
    
    elements = [
        {"type": "Title", "content": f"GDP = ${gdp:.1f}T", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    components = [
        ("C", consumption, "#E74C3C"),
        ("I", investment, "#3498DB"),
        ("G", government, "#9B59B6"),
        ("X", exports, "#F39C12"),
        ("IM", -imports, "#FF9800"),
    ]
    
    x_pos = -3
    for name, value, color in components:
        bar_height = value / gdp * 3
        elements.extend([
            {"type": "Rectangle", "position": f"[{x_pos}, {bar_height/2}, 0]", "style": {"width": 0.8, "height": bar_height, "fill_color": color}},
            {"type": "Text", "content": f"{name}", "position": f"[{x_pos}, {bar_height + 0.3}, 0]", "style": {"color": color, "font_size": 14}},
            {"type": "Text", "content": f"${value:.1f}T", "position": f"[{x_pos}, -0.3, 0]", "style": {"color": color, "font_size": 14}},
        ])
        x_pos += 1.5
    
    return {"id": "gdp", "elements": elements, "duration_seconds": 40}

def build_ad_as_model(
    ad_shift: float = 0,
    as_shift: float = 0
) -> Dict[str, Any]:
    """Build AD-AS model."""
    elements = [
        {"type": "Title", "content": "AD-AS Model", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "adas", "position": "[0, 0, 0]", "style": {"x_range": [0, 14, 2], "y_range": [0, 14, 2], "x_label": "GDP", "y_label": "PL"}},
    ]
    
    elements.extend([
        {"type": "Line", "position": "[0, 2, 0]", "style": {"color": "#E74C3C", "stroke_width": 3}},
        {"type": "Line", "position": "[3, 0, 0]", "style": {"color": "#3498DB", "stroke_width": 3}},
    ])
    
    if ad_shift > 0:
        elements.extend([
            {"type": "Line", "position": f"[{ad_shift}, 2 + ad_shift}, 0]", "style": {"color": "#E74C3C", "stroke_width": 2, "dash": "dotted"}},
            {"type": "Text", "content": "AD₁", "position": "[2, 11, 0]", "style": {"color": "#E74C3C"}},
        ])
    
    if as_shift > 0:
        elements.extend([
            {"type": "Line", "position": f"[3 + as_shift, 0, 0]", "style": {"color": "#3498DB", "stroke_width": 2, "dash": "dotted"}},
            {"type": "Text", "content": "AS₁", "position": "[11, 2, 0]", "style": {"color": "#3498DB"}},
        ])
    
    elements.extend([
        {"type": "Circle", "position": "[5, 5, 0]", "style": {"radius": 0.15, "fill_color": "#2ECC71"}},
        {"type": "Text", "content": "Equilibrium", "position": "[3, 3, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "adas", "elements": elements, "duration_seconds": 40}

def build_phillips_curve(
    expected_inflation: float = 2.0,
    unemployment: float = 5.0,
    sensitivity: float = 0.5
) -> Dict[str, Any]:
    """Build Phillips Curve."""
    inflation = expected_inflation - sensitivity * (4 - unemployment)
    
    elements = [
        {"type": "Title", "content": "Phillips Curve", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "phillips", "position": "[0, 0, 0]", "style": {"x_range": [0, 10, 2], "y_range": [-2, 10, 2], "x_label": "UR%", "y_label": "π%"}},
    ]
    
    for u in range(11):
        pi = expected_inflation - sensitivity * (4 - u)
        if pi > -2:
            elements.append({
                "type": "Circle",
                "position": f"[{u}, {pi}, 0]",
                "style": {"radius": 0.08, "fill_color": "#E74C3C"}
            })
    
    elements.extend([
        {"type": "Line", "position": "[0, 4, 0]", "style": {"color": "#FFEAA7", "stroke_width": 1}},
        {"type": "Text", "content": "NATUR", "position": "[0, 4.3, 0]", "style": {"color": "#FFEAA7", "font_size": 12}},
        {"type": "Circle", "position": f"[{unemployment}, {inflation}, 0]", "style": {"radius": 0.1, "fill_color": "#2ECC71"}},
    ])
    
    return {"id": "phillips", "elements": elements, "duration_seconds": 35}

def build_multiplier(
    mpc: float = 0.8,
    government_spend: float = 100
) -> Dict[str, Any]:
    """Build fiscal multiplier."""
    multiplier = 1 / (1 - mpc)
    total_impact = multiplier * government_spend
    
    elements = [
        {"type": "Title", "content": f"Fiscal Multiplier (MPC={MPC})", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    rounds = [(0, 100), (1, mpc * 100), (2, mpc**2 * 100), (3, mpc**3 * 100), (4, mpc**4 * 100)]
    
    x_pos = -3
    y_pos = 2.0
    for round_num, amount in rounds[:5]:
        elements.extend([
            {"type": "Text", "content": f"Round {round_num}", "position": f"[{x_pos}, {y_pos}, 0]", "style": {"color": "#3498DB", "font_size": 14}},
            {"type": "Text", "content": f"${amount:.0f}", "position": f"[{x_pos + 1.5}, {y_pos}, 0]", "style": {"color": "#69F0AE"}},
        ])
        y_pos -= 0.6
    
    elements.extend([
        {"type": "Text", "content": f"Multiplier = {multiplier:.1f}", "position": "[0, -2.0, 0]", "style": {"color": "#FFEAA7", "font_size": 18}},
        {"type": "Text", "content": f"Total = ${total_impact:.0f}", "position": "[2.5, -2.0, 0]", "style": {"color": "#69F0AE", "font_size": 18}},
    ])
    
    return {"id": "multiplier", "elements": elements, "duration_seconds": 40}

def build_is_lm_model(
    i_rate: float = 0.05,
    money_supply: float = 1000,
    output: float = 9
) -> Dict[str, Any]:
    """Build IS-LM model."""
    elements = [
        {"type": "Title", "content": "IS-LM Model", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "islm", "position": "[0, 0, 0]", "style": {"x_range": [0, 12, 2], "y_range": [0, 12, 2], "x_label": "Y", "y_label": "i"}},
    ]
    
    for y in range(1, 11):
        i_eq = 3 - 0.1 * y
        elements.append({
            "type": "Circle",
            "position": f"[{y}, {i_eq if i_eq > 0 else 0}, 0]",
            "style": {"radius": 0.08, "fill_color": "#E74C3C" if y < 5 else "#3498DB"}
        })
    
    elements.extend([
        {"type": "Circle", "position": f"[{output}, {i_rate * 50}, 0]", "style": {"radius": 0.15, "fill_color": "#2ECC71"}},
        {"type": "Text", "content": "IS", "position": "[3, 9, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Text", "content": "LM", "position": "[9, 4, 0]", "style": {"color": "#3498DB"}},
    ])
    
    return {"id": "islm", "elements": elements, "duration_seconds": 35}

def build_loanable_funds(
    supply: float = 100,
    demand: float = 100
) -> Dict[str, Any]:
    """Build loanable funds market."""
    elements = [
        {"type": "Title", "content": "Loanable Funds Market", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "loanable", "position": "[0, 0, 0]", "style": {"x_range": [0, 200, 40], "y_range": [0, 10, 2]}},
    ]
    
    for i in range(200, 40, -40):
        elements.append({
            "type": "Circle",
            "position": f"[{i}, {supply/50 if i <= supply else supply/50 + (i-supply)/100}, 0]",
            "style": {"radius": 0.1, "fill_color": "#3498DB" if i <= supply else "#E74C3C"}
        })
    
    elements.extend([
        {"type": "Circle", "position": f"[{100}, {4}, 0]", "style": {"radius": 0.15, "fill_color": "#2ECC71"}},
        {"type": "Text", "content": f"Equilibrium: r* = 4%", "position": "[100, 2, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "loanable", "elements": elements, "duration_seconds": 35}

def build_lorenz_curve(
    incomes: List[float] = [10, 20, 30, 40, 50]
) -> Dict[str, Any]:
    """Build Lorenz curve."""
    total_income = sum(incomes)
    n = len(incomes)
    
    elements = [
        {"type": "Title", "content": "Lorenz Curve", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "lorenz", "position": "[0, 0, 0]", "style": {"x_range": [0, 100, 20], "y_range": [0, 100, 20]}},
    ]
    
    cum_pct = [sum(incomes[:i+1]) / total_income * 100 for i in range(n)]
    
    for i, pct in enumerate(cum_pct):
        elements.append({
            "type": "Circle",
            "position": f"[{(i+1)/n*100}, {pct}, 0]",
            "style": {"radius": 0.08, "fill_color": "#E74C3C"}
        })
    
    elements.extend([
        {"type": "Line", "position": "[0, 0, 0]", "style": {"color": "#9B59B6", "stroke_width": 2}},
        {"type": "Text", "content": "Perfect Equality", "position": "[10, 90, 0]", "style": {"color": "#2ECC71", "font_size": 14}},
    ])
    
    return {"id": "lorenz", "elements": elements, "duration_seconds": 35}

def build_exchange_rate(
    base: float = 1.10,
    change: float = 0.0
) -> Dict[str, Any]:
    """Build exchange rate diagram."""
    new_rate = base * (1 + change / 100)
    
    elements = [
        {"type": "Title", "content": "Exchange Rate", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    elements.extend([
        {"type": "Axes", "content": "fx", "position": "[0, 0, 0]", "style": {"x_range": [0, 12, 2], "y_range": [0, 1.5, 0.25]}},
        {"type": "Line", "position": f"[0, {base}, 0]", "style": {"color": "#3498DB", "stroke_width": 3}},
    ])
    
    if change != 0:
        elements.append({
            "type": "Line",
            "position": f"[{new_rate}, 0, 0]",
            "style": {"color": "#E74C3C" if change < 0 else "#2ECC71", "stroke_width": 3}
        })
    
    elements.extend([
        {"type": "Text", "content": f"$1 = €{base}", "position": "[-3, {base + 0.1}, 0]", "style": {"color": "#3498DB"}},
    ])
    
    if change != 0:
        direction = "Appreciates" if change > 0 else "Depreciates"
        elements.append({
            "type": "Text",
            "content": f"{direction}: {change:+.1f}%",
            "position": "[3, 1, 0]",
            "style": {"color": "#FFEAA7", "font_size": 18}
        })
    
    return {"id": "exchange", "elements": elements, "duration_seconds": 35}

def build_money_multiplier(
    reserve_ratio: float = 0.1,
    deposit: float = 1000
) -> Dict[str, Any]:
    """Build money multiplier."""
    multiplier = 1 / reserve_ratio
    money_created = deposit * (multiplier - 1)
    
    elements = [
        {"type": "Title", "content": f"Money Multiplier (rr={reserve_ratio})", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    rounds = [deposit]
    current = deposit
    for _ in range(4):
        current = current * (1 - reserve_ratio)
        rounds.append(current * reserve_ratio)
    
    y_pos = 2.5
    labels = ["Initial", "1st loan", "2nd loan", "Reserve", "Total created"]
    for i, label in enumerate(labels[:5]):
        if i == 0:
            val = deposit
        elif i < 4:
            val = rounds[i]
        else:
            val = money_created
        
        elements.extend([
            {"type": "Text", "content": label, "position": f"[{-3}, {y_pos}, 0]", "style": {"color": "#FFEAA7", "font_size": 14}},
            {"type": "Text", "content": f"${val:.0f}", "position": f"[{1}, {y_pos}, 0]", "style": {"color": "#69F0AE", "font_size": 14}},
        ])
        y_pos -= 0.7
    
    elements.extend([
        {"type": "Text", "content": f"Multiplier: {multiplier:.1f}x", "position": "[0, -2.5, 0]", "style": {"color": "#9B59B6", "font_size": 18}},
    ])
    
    return {"id": "money_multiplier", "elements": elements, "duration_seconds": 40}

def build_cost_curves(
    fixed_cost: float = 20,
    variable_cost: float = 50
) -> Dict[str, Any]:
    """Build cost curves."""
    elements = [
        {"type": "Title", "content": "Cost Curves", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "cost", "position": "[0, 0, 0]", "style": {"x_range": [0, 10, 2], "y_range": [0, 100, 20]}},
    ]
    
    q_range = range(1, 11)
    
    for q in q_range:
        fc = fixed_cost
        vc = variable_cost * q ** 0.5
        tc = fc + vc
        mc = 0.5 * variable_cost * q ** (-0.5)
        
        elements.append({
            "type": "Circle",
            "position": f"[{q}, {fc/10}, 0]",
            "style": {"radius": 0.05, "fill_color": "#9B59B6" if q < 3 else "#E74C3C"}
        })
    
    elements.extend([
        {"type": "Text", "content": "ATC", "position": "[8, 3, 0]", "style": {"color": "#3498DB"}},
        {"type": "Text", "content": "MC", "position": "[6, 7, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Text", "content": "FC", "position": "[8, 2, 0]", "style": {"color": "#9B59B6"}},
    ])
    
    return {"id": "cost_curves", "elements": elements, "duration_seconds": 35}

def build_marginal_revenue(
    demand_slope: float = -1.0,
    quantity: float = 5.0
) -> Dict[str, Any]:
    """Build marginal revenue for monopoly."""
    price = 10 - demand_slope * quantity
    mr = 10 - 2 * demand_slope * quantity
    
    elements = [
        {"type": "Title", "content": "Monopoly: MR", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "mr", "position": "[0, 0, 0]", "style": {"x_range": [0, 10, 2], "y_range": [0, 10, 2]}},
    ]
    
    elements.extend([
        {"type": "Line", "position": "[0, 10, 0]", "style": {"color": "#E74C3C", "stroke_width": 3}},
        {"type": "Line", "position": "[0, 5, 0]", "style": {"color": "#3498DB", "stroke_width": 3}},
    ])
    
    elements.extend([
        {"type": "Circle", "position": f"[{quantity}, {price}, 0]", "style": {"radius": 0.1, "fill_color": "#E74C3C"}},
        {"type": "Circle", "position": f"[{quantity}, {mr}, 0]", "style": {"radius": 0.1, "fill_color": "#3498DB"}},
    ])
    
    elements.extend([
        {"type": "Text", "content": "Demand", "position": "[8, 9, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Text", "content": "MR", "position": "[8, 4, 0]", "style": {"color": "#3498DB"}},
        {"type": "Text", "content": f"MR = {mr:.1f}", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "marginal_revenue", "elements": elements, "duration_seconds": 35}

def build_payoff_matrix(
    p1_choices: List[str] = ["Cooperate", "Defect"],
    p2_choices: List[str] = ["Cooperate", "Defect"],
    payoff_matrix: List[List[List[int]] = [[[4, 4], [1, 6]], [[6, 1], [2, 2]]]
) -> Dict[str, Any]:
    """Build payoff matrix game."""
    elements = [
        {"type": "Title", "content": "Payoff Matrix", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    x_pos = -1.5
    y_pos = 2.0
    for i, choice in enumerate(p1_choices):
        elements.append({
            "type": "Text",
            "content": f"{choice}",
            "position": f"[{x_pos + i * 1.5 + 0.8}, 2.5, 0]",
            "style": {"color": "#3498DB", "font_size": 16}
        })
    
    for i, choice in enumerate(p2_choices):
        elements.append({
            "type": "Text",
            "content": f"{choice}",
            "position": f"[-2.5}, {y_pos - i * 0.8}, 0]",
            "style": {"color": "#E74C3C", "font_size": 16}
        })
    
    for i in range(2):
        for j in range(2):
            payoffs = payoff_matrix[i][j]
            elements.extend([
                {"type": "Rectangle",
                "position": f"[{-1.5 + j * 1.5}, {1.5 - i * 0.8}, 0]",
                "style": {"width": 1.2, "height": 0.6, "fill_color": "#607D8B" if payoffs[0] == payoffs[1] else ("#2ECC71" if payoffs[0] > payoffs[1] else "#E74C3C")}},
                {"type": "Text",
                "content": f"{payoffs[0]},{payoffs[1]}",
                "position": f"[{-1.5 + j * 1.5}, {1.5 - i * 0.8}, 0]",
                "style": {"color": "#FFFFFF", "font_size": 14}
                }
            ])
    
    return {"id": "payoff", "elements": elements, "duration_seconds": 35}

def build_opportunity_cost(
    cost_a: float = 50,
    benefit_b: float = 80
) -> Dict[str, Any]:
    """Build opportunity cost visualization."""
    oc = benefit_b - cost_a
    
    elements = [
        {"type": "Title", "content": "Opportunity Cost", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    choices = [
        ("Option A", cost_a, "#E74C3C"),
        ("Option B", benefit_b, "#3498DB"),
    ]
    
    y_pos = 2.0
    for name, value, color in choices:
        elements.extend([
            {"type": "Rectangle",
            "position": f"[{-1.5}, {y_pos}, 0]",
            "style": {"width": 1.5, "height": 0.8, "fill_color": color, "fill_opacity": 0.7}},
            {"type": "Text",
            "content": f"{name}",
            "position": f"[{-1.5}, {y_pos + 0.5}, 0]",
            "style": {"color": color}},
            {"type": "Text",
            "content": f"${value}",
            "position": f"[{-1.5}, {y_pos - 0.3}, 0]",
            "style": {"color": "#FFFFFF", "font_size": 16}
        ])
        y_pos -= 1.2
    
    elements.extend([
        {"type": "Text",
        "content": "Opportunity Cost = Benefit of best foregone option",
        "position": "[0, -1.5, 0]",
        "style": {"color": "#FFEAA7", "font_size": 16}
        }),
        {"type": "Text",
        "content": f"OC = ${oc}",
        "position": "[2, 0, 0]",
        "style": {"color": "#69F0AE", "font_size": 20}
    ])
    
    return {"id": "opportunity_cost", "elements": elements, "duration_seconds": 35}

def build_benefit_cost(
    benefits: List[float] = [100, 80, 50],
    costs: List[float] = [30, 40, 50]
) -> Dict[str, Any]:
    """Build cost-benefit analysis."""
    npv = sum(benefits) - sum(costs)
    
    elements = [
        {"type": "Title", "content": "Cost-Benefit Analysis", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    labels = ["Project 1", "Project 2", "Project 3"]
    
    y_pos = 2.0
    for i, (b, c) in enumerate(zip(benefits, costs)):
        net = b - c
        color = "#2ECC71" if net > 0 else "#E74C3C"
        elements.extend([
            {"type": "Rectangle",
            "position": f"[{-2 + i * 2}, {y_pos}, 0]",
            "style": {"width": 1.5, "height": max(net/20, 0.1), "fill_color": color}},
            {"type": "Text",
            "content": f"B=${b}, C=${c}",
            "position": f"[{-2 + i * 2}, {y_pos - 0.5}, 0]",
            "style": {"color": color, "font_size": 14}
        ])
        y_pos -= 1.0
    
    elements.append({
        "type": "Text",
        "content": f"NPV = ${npv}",
        "position": "[0, -2.5, 0]",
        "style": {"color": "#FFEAA7" if npv > 0 else "#E74C3C", "font_size": 20}
    })
    
    return {"id": "cost_benefit", "elements": elements, "duration_seconds": 35}

def build_seasonal_index(
    values: List[float] = [100, 95, 90, 85, 95, 110, 120, 115, 105, 100, 95, 90]
) -> Dict[str, Any]:
    """Build seasonal index."""
    avg = sum(values) / len(values)
    indices = [v / avg * 100 for v in values]
    
    elements = [
        {"type": "Title", "content": "Seasonal Index", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "seasonal", "position": "[0, 0, 0]", "style": {"x_range": [0, 12, 2], "y_range": [50, 150, 20]}},
    ]
    
    months = ["J", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    
    for i, idx in enumerate(indices):
        elements.append({
            "type": "Circle",
            "position": f"[{i + 0.5}, {idx}, 0]",
            "style": {"radius": 0.1, "fill_color": "#3498DB" if idx == 100 else ("#E74C3C" if idx < 100 else "#2ECC71")}
        })
        if i % 3 == 0:
            elements.append({
                "type": "Text",
                "content": months[i],
                "position": f"[{i + 0.5}, 50, 0]",
                "style": {"color": "#FFEAA7", "font_size": 12}
            })
    
    elements.append({
        "type": "Line",
        "position": "[0, 100, 0]",
        "style": {"color": "#FFD700", "stroke_width": 2}
    })
    
    return {"id": "seasonal", "elements": elements, "duration_seconds": 35}

def build_utility_max(
    bundle_x: float = 4,
    bundle_y: float = 3,
    budget: float = 20,
    px: float = 2,
    py: float = 4
) -> Dict[str, Any]:
    """Build utility maximization."""
    allocated = min(budget / px, (budget / py))
    mrs = py / px
    
    elements = [
        {"type": "Title", "content": "Utility Maximization", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "utility", "position": "[0, 0, 0]", "style": {"x_range": [0, 12, 2], "y_range": [0, 8, 2]}},
    ]
    
    elements.extend([
        {"type": "Line",
        "position": f"[0, {budget/py}, 0]",
        "style": {"color": "#9B59B6", "stroke_width": 2}},
        {"type": "Line", 
        "position": f"[{budget/px}, 0, 0]",
        "style": {"color": "#9B59B6", "stroke_width": 2}},
    ])
    
    for i in range(1, 5):
        x_val = i * 0.5
        y_val = budget / py - (px / py) * x_val
        if y_val > 0:
            elements.append({
                "type": "Circle",
                "position": f"[{x_val}, {y_val}, 0]",
                "style": {"radius": 0.05, "fill_color": "#3498DB"}
            })
    
    elements.extend([
        {"type": "Circle",
        "position": f"[{bundle_x}, {bundle_y}, 0]",
        "style": {"radius": 0.15, "fill_color": "#2ECC71"}},
        {"type": "Text",
        "content": f"Bundle ({bundle_x}, {bundle_y})",
        "position": f"[{bundle_x + 0.5}, {bundle_y + 0.5}, 0]",
        "style": {"color": "#FFEAA7"}
    ])
    
    return {"id": "utility", "elements": elements, "duration_seconds": 35}

def build_production_possible(
    capital: float = 50,
    consumer: float = 50,
    max_k: float = 100,
    max_c: float = 100
) -> Dict[str, Any]:
    """Build production possibility frontier."""
    elements = [
        {"type": "Title", "content": "Production Possibility Frontier", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "ppf", "position": "[0, 0, 0]", "style": {"x_range": [0, 100, 20], "y_range": [0, 100, 20], "x_label": "Consumer", "y_label": "Capital"}},
    ]
    
    for i in range(101):
        if i % 10 == 0:
            elements.append({
                "type": "Circle",
                "position": f"[{100 - i}, {i}, 0]",
                "style": {"radius": 0.08, "fill_color": "#3498DB" if i == 50 else "#E74C3C"}
            })
    
    elements.extend([
        {"type": "Circle",
        "position": f"[{capital}, {consumer}, 0]",
        "style": {"radius": 0.15, "fill_color": "#2ECC71"}},
        {"type": "Text",
        "content": "Current Point",
        "position": f"[{capital + 5}, {consumer + 5}, 0]",
        "style": {"color": "#FFEAA7"}
    ])
    
    elements.append({
        "type": "Text",
        "content": "Efficient",
        "position": "[30, 70, 0]",
        "style": {"color": "#2ECC71", "font_size": 14}
    })
    elements.append({
        "type": "Text",
        "content": "Inefficient",
        "position": "[70, 70, 0]",
        "style": {"color": "#FFEAA7", "font_size": 14}
    })
    elements.append({
        "type": "Text",
        "content": "Unattainable",
        "position": "[70, 30, 0]",
        "style": {"color": "#E74C3C", "font_size": 14}
    })
    
    return {"id": "ppf", "elements": elements, "duration_seconds": 40}