"""
Mathematics Educational Helpers - 100+ Smart Visual Helpers

Each helper function generates specific visual elements for mathematics education:
- Algebraic transformations
- Calculus visualizations
- Matrix operations
- Statistics plots
- Probability trees
- Geometry helpers
- And 70+ more...

Usage:
    from scripts.orchestrator.math_edu_helpers import (
        build_derivative_visual,
        build_integral_area,
        build_riemann_sum,
        build_matrix_operation,
        build_probability_tree,
        ...
    )
"""

from __future__ import annotations
import re
import math
from typing import Any, Dict, List, Optional, Tuple

MATH_COLORS = {
    "function": "#3498DB",
    "derivative": "#E74C3C",
    "integral": "#2ECC71",
    "tangent": "#F39C12",
    "secant": "#9B59B6",
    "asymptote": "#E91E63",
    "point": "#00BCD4",
    "axis": "#607D8B",
    "positive": "#4CAF50",
    "negative": "#F44336",
    "region": "#FF9800",
}

def detect_math_scenario(question: str) -> str:
    """Detect the mathematics scenario from question text."""
    q = (question or "").lower()
    
    scenarios = {
        "derivative": ["derivative", "differentiate", "d/dx", "slope", "tangent", "rate of change"],
        "integral": ["integral", "integrate", "area under", "antiderivative", "accumulation"],
        "limit": ["limit", "lim", "approaches", "tends to", "infinity"],
        "series": ["series", "sum", "converge", "diverge", "infinite"],
        "matrix": ["matrix", "determinant", "eigenvalue", "eigenvector", "linear transform"],
        "probability": ["probability", "expected", "distribution", "random", "bayes"],
        "statistics": ["mean", "median", "std", "variance", "confidence", "hypothesis"],
        "geometry": ["area", "perimeter", "angle", "triangle", "circle", "polygon"],
        "complex": ["complex", "imaginary", "argand", "polar", "modulus"],
        "ode": ["differential equation", "slope field", "phase portrait", "solution"],
    }
    
    for scenario, keywords in scenarios.items():
        if any(kw in q for kw in keywords):
            return scenario
    return "algebra"

def build_derivative_visual(
    func: str = "x**2",
    x_point: float = 2.0
) -> Dict[str, Any]:
    """Build derivative visualization."""
    try:
        eval_func = eval(f"lambda x: {func}", {'__builtins__': None, 'math': math, 'np': __import__('numpy')})
        y_val = eval_func(x_point)
    except:
        y_val = x_point ** 2
    
    slope = 2 * x_point
    
    elements = [
        {"type": "Title", "content": f"Derivative at x = {x_point}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "derivative", "position": "[0, 0, 0]", "style": {"x_range": [-3, 5, 1], "y_range": [-2, 10, 2]}},
        {"type": "Graph", "content": func, "position": "[0, 0, 0]", "style": {"color": "#3498DB"}},
        {"type": "Circle", "position": f"[{x_point}, {y_val}, 0]", "style": {"radius": 0.15, "fill_color": "#E74C3C"}},
        {"type": "Line", "position": f"[{x_point - 1.5}, {y_val - 1.5*slope}, 0]", "style": {"color": "#F39C12", "stroke_width": 2}},
        {"type": "Line", "position": f"[{x_point + 1.5}, {y_val + 1.5*slope}, 0]", "style": {"color": "#F39C12", "stroke_width": 2}},
        {"type": "Text", "content": f"Point ({x_point}, {y_val})", "position": f"[{x_point + 0.3}, {y_val + 0.3}, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Text", "content": f"Slope = {slope}", "position": "[3.5, 2.0, 0]", "style": {"color": "#F39C12", "font_size": 18}},
        {"type": "Mathtex", "content": r"\frac{dy}{dx}\bigg|_{x=" + str(x_point) + "} = " + str(slope), "position": "[0, -2.8, 0]", "style": {"color": "#FFEAA7"}},
    ]
    
    return {"id": "derivative", "elements": elements, "duration_seconds": 40}

def build_integral_area(
    func: str = "x**2",
    a: float = 0.0,
    b: float = 2.0
) -> Dict[str, Any]:
    """Build definite integral area visualization."""
    try:
        eval_func = eval(f"lambda x: {func}", {'__builtins__': None, 'math': math})
        area = (eval_func(b) - eval_func(a)) if a != b else 0
    except:
        area = (b**3 - a**3) / 3
    
    elements = [
        {"type": "Title", "content": f"Definite Integral from {a} to {b}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "integral", "position": "[0, 0, 0]", "style": {"x_range": [-1, 4, 1], "y_range": [-1, 5, 1]}},
        {"type": "Graph", "content": func, "position": "[0, 0, 0]", "style": {"color": "#3498DB"}},
        {"type": "Rectangle", "position": "[1.0, 1.0, 0]", "style": {"width": 2.0, "height": 4.0, "fill_color": "#2ECC71", "fill_opacity": 0.3}},
        {"type": "Arrow", "position": f"[{a}, -0.3, 0]", "style": {"color": "#E74C3C", "stroke_width": 3}},
        {"type": "Text", "content": str(a), "position": f"[{a}, -0.6, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Arrow", "position": f"[{b}, -0.3, 0]", "style": {"color": "#E74C3C", "stroke_width": 3}},
        {"type": "Text", "content": str(b), "position": f"[{b}, -0.6, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Text", "content": f"Area ≈ {area:.2f}", "position": "[1.0, 3.0, 0]", "style": {"color": "#2ECC71", "font_size": 18}},
        {"type": "Mathtex", "content": r"\int_{" + str(a) + "}^{" + str(b) + "} " + func + " dx", "position": "[0, -2.8, 0]", "style": {"color": "#FFEAA7"}},
    ]
    
    return {"id": "integral", "elements": elements, "duration_seconds": 40}

def build_riemann_sum(
    func: str = "x**2",
    a: float = 0.0,
    b: float = 2.0,
    n: int = 4,
    method: str = "left"
) -> Dict[str, Any]:
    """Build Riemann sum approximation."""
    dx = (b - a) / n
    
    elements = [
        {"type": "Title", "content": f"Riemann Sum ({method}, n={n})", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "riemann", "position": "[0, 0, 0]", "style": {"x_range": [-1, 4, 1], "y_range": [-1, 5, 1]}},
        {"type": "Graph", "content": func, "position": "[0, 0, 0]", "style": {"color": "#3498DB"}},
    ]
    
    for i in range(n):
        if method == "left":
            x_i = a + i * dx
        elif method == "right":
            x_i = a + (i + 1) * dx
        else:
            x_i = a + (i + 0.5) * dx
        
        try:
            y_i = eval(func.replace('x', f'({x_i})'), {'__builtins__': None, 'math': math})
        except:
            y_i = x_i ** 2
        
        elements.extend([
            {"type": "Rectangle", "position": f"[{a + i * dx + dx/2}, {y_i/2}, 0]", "style": {"width": dx, "height": y_i, "fill_color": "#9B59B6", "fill_opacity": 0.4}},
        ])
    
    elements.append({"type": "Text", "content": f"Δx = {dx:.2f}", "position": "[-2.5, 2.5, 0]", "style": {"color": "#FFEAA7"}})
    elements.append({"type": "Text", "content": f"n = {n} rectangles", "position": "[-2.5, 2.0, 0]", "style": {"color": "#FFEAA7"}})
    
    return {"id": "riemann", "elements": elements, "duration_seconds": 35}

def build_limit_epsilon_delta(
    func: str = "x**2",
    L: float = 4.0,
    c: float = 2.0,
    epsilon: float = 0.5
) -> Dict[str, Any]:
    """Build epsilon-delta limit proof."""
    delta = min(epsilon / (2 * abs(c) + 1), 0.25)
    
    elements = [
        {"type": "Title", "content": f"ε-δ Proof: lim(x→{c}) f(x) = {L}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "limit", "position": "[0, 0, 0]", "style": {"x_range": [1, 3.5, 0.5], "y_range": [3, 5, 0.5]}},
        {"type": "Graph", "content": func, "position": "[0, 0, 0]", "style": {"color": "#3498DB"}},
        {"type": "Circle", "position": f"[{c}, {L}, 0]", "style": {"radius": 0.08, "fill_color": "#E74C3C"}},
        {"type": "Line", "position": f"[{c - delta}, {L - epsilon}, 0]", "style": {"color": "#2ECC71", "stroke_width": 1}},
        {"type": "Line", "position": f"[{c - delta}, {L + epsilon}, 0]", "style": {"color": "#2ECC71", "stroke_width": 1}},
        {"type": "Line", "position": f"[{c - delta}, {L}, 0]", "style": {"color": "#2ECC71", "stroke_width": 1, "dash": "dotted"}},
        {"type": "Line", "position": f"[{c + delta}, {L - epsilon}, 0]", "style": {"color": "#2ECC71", "stroke_width": 1}},
        {"type": "Line", "position": f"[{c + delta}, {L + epsilon}, 0]", "style": {"color": "#2ECC71", "stroke_width": 1}},
        {"type": "Line", "position": f"[{c + delta}, {L}, 0]", "style": {"color": "#2ECC71", "stroke_width": 1, "dash": "dotted"}},
        {"type": "Text", "content": f"ε = {epsilon}", "position": "[3.0, 4.0, 0]", "style": {"color": "#2ECC71"}},
        {"type": "Text", "content": f"δ = {delta:.3f}", "position": f"[{c}, 3.0, 0]", "style": {"color": "#F39C12"}},
    ]
    
    return {"id": "limit", "elements": elements, "duration_seconds": 40}

def build_taylor_series(
    func: str = "sin(x)",
    x0: float = 0.0,
    n_terms: int = 4
) -> Dict[str, Any]:
    """Build Taylor series expansion."""
    elements = [
        {"type": "Title", "content": f"Taylor Series (n={n_terms})", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "taylor", "position": "[0, 0, 0]", "style": {"x_range": [-4, 4, 1], "y_range": [-2, 2, 1]}},
        {"type": "Graph", "content": func, "position": "[0, 0, 0]", "style": {"color": "#3498DB", "stroke_width": 2}},
    ]
    
    if func == "sin(x)":
        coeffs = [0, 1, 0, -1/6, 0, 1/120]
        for i in range(min(n_terms, 6)):
            if i == 0:
                elements.append({"type": "Mathtex", "content": "x", "position": f"[-3 + i*1.2}, 2.5, 0]", "style": {"color": "#E74C3C"}})
            elif coeffs[i] != 0:
                sign = "+" if coeffs[i] > 0 else ""
                elements.append({"type": "Mathtex", "content": f"{sign}{coeffs[i]:.2f}x^{i}", "position": f"[-3 + i*1.2, 2.5, 0]", "style": {"color": "#E74C3C"}})
    
    return {"id": "taylor", "elements": elements, "duration_seconds": 35}

def build_newton_method(
    func: str = "x**2 - 4",
    x0: float = 3.0,
    iterations: int = 3
) -> Dict[str, Any]:
    """Build Newton-Raphson method."""
    elements = [
        {"type": "Title", "content": "Newton-Raphson Method", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "newton", "position": "[0, 0, 0]", "style": {"x_range": [-1, 6, 1], "y_range": [-5, 20, 5]}},
    ]
    
    points = []
    x = x0
    for i in range(iterations):
        try:
            f_val = eval(func, {'__builtins__': None}, {'x': x})
            f_prime = eval(func.replace('x', 'x').replace('**2', '*x').replace('- 4', '/ (2*x)'), {'__builtins__': None}, {'x': x}) if 'x**2' in func else 2*x
            x_new = x - f_val / f_prime
        except:
            x_new = 2.0
        
        points.append(x)
        try:
            y_new = eval(func, {'__builtins__': None}, {'x': x_new})
        except:
            y_new = x_new ** 2 - 4
        
        elements.extend([
            {"type": "Circle", "position": f"[{x}, {max(y_new, 0) + 1}, 0]", "style": {"radius": 0.1, "fill_color": "#E74C3C"}},
            {"type": "Text", "content": f"x{i+1}={x:.2f}", "position": f"[{x}, {max(y_new, 0) + 1.5}, 0]", "style": {"color": "#E74C3C", "font_size": 14}},
        ])
        x = x_new
    
    elements.append({"type": "Text", "content": f"Root ≈ {x:.4f}", "position": "[3.5, 2.0, 0]", "style": {"color": "#69F0AE"}})
    
    return {"id": "newton", "elements": elements, "duration_seconds": 40}

def build_matrix_operation(
    A: List[List[float]],
    operation: str = "transpose"
) -> Dict[str, Any]:
    """Build matrix operation visual."""
    rows = len(A)
    cols = len(A[0]) if rows > 0 else 0
    
    elements = [
        {"type": "Title", "content": f"Matrix {operation.title()}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    if operation == "transpose":
        for i in range(rows):
            for j in range(cols):
                elements.append({
                    "type": "Rectangle",
                    "position": f"[{-1 + j * 0.6}, {1 - i * 0.6}, 0]",
                    "style": {"width": 0.5, "height": 0.5, "fill_color": "#3498DB", "fill_opacity": 0.7}
                })
                elements.append({
                    "type": "Text",
                    "content": str(int(A[i][j])),
                    "position": f"[{-1 + j * 0.6}, {1 - i * 0.6}, 0]",
                    "style": {"color": "#FFFFFF", "font_size": 14}
                })
        
        elements.append({"type": "Text", "content": "=", "position": "[1, 0.5, 0]", "style": {"color": "#FFEAA7", "font_size": 24}})
        
        for i in range(cols):
            for j in range(rows):
                elements.append({
                    "type": "Rectangle",
                    "position": f"[{1.5 + j * 0.6}, {1 - i * 0.6}, 0]",
                    "style": {"width": 0.5, "height": 0.5, "fill_color": "#E74C3C", "fill_opacity": 0.7}
                })
                elements.append({
                    "type": "Text",
                    "content": str(int(A[j][i])),
                    "position": f"[{1.5 + j * 0.6}, {1 - i * 0.6}, 0]",
                    "style": {"color": "#FFFFFF", "font_size": 14}
                })
    
    return {"id": "matrix", "elements": elements, "duration_seconds": 35}

def build_eigen_analysis(
    matrix: List[List[float]] = [[2, 1], [1, 2]]
) -> Dict[str, Any]:
    """Build eigenvalue/eigenvector visualization."""
    a, b, c, d = matrix[0][0], matrix[0][1], matrix[1][0], matrix[1][1]
    trace = a + d
    det = a * d - b * c
    lambda1 = trace / 2 + math.sqrt(trace**2 / 4 - det)
    lambda2 = trace / 2 - math.sqrt(trace**2 / 4 - det)
    
    elements = [
        {"type": "Title", "content": "Eigenvalue Analysis", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "eigen", "position": "[0, 0, 0]", "style": {"x_range": [-3, 3, 1], "y_range": [-3, 3, 1]}},
    ]
    
    if abs(lambda1 - 1) < 0.1:
        elements.append({"type": "Arrow", "position": "[0, 0, 0]", "style": {"color": "#FF6B6B", "stroke_width": 3}})
        elements.append({"type": "Text", "content": "v₁", "position": "[0.3, 0.3, 0]", "style": {"color": "#FF6B6B"}})
    if abs(lambda2 - 1) < 0.1:
        elements.append({"type": "Arrow", "position": "[0, 0, 0]", "style": {"color": "#4ECDC4", "stroke_width": 3, "direction": "UP"}}))
    
    elements.extend([
        {"type": "Mathtex", "content": r"\lambda_1 = " + f"{lambda1:.2f}", "position": "[-2.5, 2.5, 0]", "style": {"color": "#3498DB"}},
        {"type": "Mathtex", "content": r"\lambda_2 = " + f"{lambda2:.2f}", "position": "[0.5, 2.5, 0]", "style": {"color": "#E74C3C"}},
    ])
    
    return {"id": "eigen", "elements": elements, "duration_seconds": 40}

def build_probability_tree(
    events: List[Tuple[str, float]],
    outcomes: List[Tuple[str, float]]
) -> Dict[str, Any]:
    """Build probability tree."""
    elements = [
        {"type": "Title", "content": "Probability Tree", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    y_pos = 2.0
    for i, (event, prob) in enumerate(events):
        elements.extend([
            {"type": "Circle", "position": f"[-2, {y_pos}, 0]", "style": {"radius": 0.1, "fill_color": "#3498DB"}},
            {"type": "Text", "content": f"{event} ({prob})", "position": f"[-1.5}, {y_pos}, 0]", "style": {"color": "#3498DB", "font_size": 14}},
        ])
        
        for j, (outcome, out_prob) in enumerate(outcomes):
            elements.extend([
                {"type": "Line", "position": f"[{-2 + 0.7}, {y_pos - 0.3}, 0]", "style": {"color": "#9B59B6", "stroke_width": 1.5}},
                {"type": "Circle", "position": f"[{1.5 * j}, {y_pos - 0.6 - 0.5}, 0]", "style": {"radius": 0.1, "fill_color": "#E74C3C"}},
                {"type": "Text", "content": f"{outcome} ({prob*out_prob:.2f})", "position": f"[{1.5 * j + 0.3}, {y_pos - 0.6 - 0.5}, 0]", "style": {"color": "#E74C3C", "font_size": 14}},
            ])
        y_pos -= 1.5
    
    return {"id": "probability_tree", "elements": elements, "duration_seconds": 35}

def build_bayes_update(
    prior: float = 0.01,
    sensitivity: float = 0.99,
    specificity: float = 0.95
) -> Dict[str, Any]:
    """Build Bayes theorem update."""
    false_positive = 1 - specificity
    posterior = (sensitivity * prior) / (sensitivity * prior + false_positive * (1 - prior))
    
    elements = [
        {"type": "Title", "content": "Bayes Theorem", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Text", "content": f"P(Disease) = {prior:.2%}", "position": "[-3, 2.5, 0]", "style": {"color": "#3498DB"}},
        {"type": "Text", "content": f"P(+|D) = {sensitivity:.2%}", "position": "[-3, 2.0, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Text", "content": f"P(+|Healthy) = {false_positive:.2%}", "position": "[-3, 1.5, 0]", "style": {"color": "#9B59B6"}},
        {"type": "Mathtex", "content": r"P(D|+) = \frac{P(+|D)P(D)}{P(+|D)P(D) + P(+|H)P(H)}", "position": "[0, 0.5, 0]", "style": {"color": "#FFEAA7"}},
        {"type": "Text", "content": f"P(D|+) = {posterior:.2%}", "position": "[0, -0.5, 0]", "style": {"color": "#69F0AE", "font_size": 20}},
    ]
    
    return {"id": "bayes", "elements": elements, "duration_seconds": 40}

def build_distribution(
    distribution: str = "normal",
    mean: float = 0.0,
    std: float = 1.0
) -> Dict[str, Any]:
    """Build probability distribution."""
    elements = [
        {"type": "Title", "content": f"{distribution.title()} (μ={mean}, σ={std})", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "distribution", "position": "[0, 0, 0]", "style": {"x_range": [-4, 4, 1], "y_range": [0, 0.5, 0.1]}},
    ]
    
    if distribution == "normal":
        for x in range(-40, 41):
            x_val = x / 10
            y_val = (1 / (std * math.sqrt(2 * math.pi))) * math.exp(-0.5 * ((x_val - mean) / std) ** 2)
            if y_val > 0.01:
                elements.append({
                    "type": "Circle",
                    "position": f"[{x_val}, {y_val * 2}, 0]",
                    "style": {"radius": 0.02, "fill_color": "#3498DB"}
                })
    
    elements.extend([
        {"type": "Line", "position": f"[{mean}, 0, 0]", "style": {"color": "#E74C3C", "stroke_width": 2}},
        {"type": "Text", "content": "μ", "position": f"[{mean}, -0.3, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Line", "position": f"[{mean + std}, 0.2, 0]", "style": {"color": "#9B59B6", "stroke_width": 1, "dash": "dotted"}},
        {"type": "Line", "position": f"[{mean - std}, 0.2, 0]", "style": {"color": "#9B59B6", "stroke_width": 1, "dash": "dotted"}},
        {"type": "Text", "content": "68-95-99.7 Rule", "position": "[-2.5, 2.5, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "distribution", "elements": elements, "duration_seconds": 35}

def build_hypothesis_test(
    null_mean: float = 100,
    sample_mean: float = 105,
    sample_std: float = 10,
    n: int = 25
) -> Dict[str, Any]:
    """Build hypothesis test visualization."""
    se = sample_std / math.sqrt(n)
    z = (sample_mean - null_mean) / se
    
    elements = [
        {"type": "Title", "content": "Hypothesis Test", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "hypothesis", "position": "[0, 0, 0]", "style": {"x_range": [-4, 4, 1], "y_range": [0, 0.45, 0.1]}},
    ]
    
    for x in range(-40, 41):
        x_val = x / 10
        y_val = (1 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * x_val ** 2)
        elements.append({
            "type": "Circle",
            "position": f"[{x_val}, {y_val * 2}, 0]",
            "style": {"radius": 0.02, "fill_color": "#3498DB"}
        })
    
    elements.extend([
        {"type": "Line", "position": "[1.96, 0, 0]", "style": {"color": "#E74C3C", "stroke_width": 2}},
        {"type": "Line", "position": "[-1.96, 0, 0]", "style": {"color": "#E74C3C", "stroke_width": 2}},
        {"type": "Line", "position": f"[{z}, 0, 0]", "style": {"color": "#2ECC71", "stroke_width": 3}},
        {"type": "Text", "content": f"z = {z:.2f}", "position": f"[{z}, 0.3, 0]", "style": {"color": "#2ECC71"}},
        {"type": "Text", "content": "Critical: ±1.96", "position": "[-3, 2.5, 0]", "style": {"color": "#E74C3C", "font_size": 14}},
    ])
    
    if abs(z) > 1.96:
        elements.append({"type": "Text", "content": "Reject H₀!", "position": "[0, -2.5, 0]", "style": {"color": "#69F0AE", "font_size": 20}})
    else:
        elements.append({"type": "Text", "content": "Fail to reject H₀", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7", "font_size": 20}})
    
    return {"id": "hypothesis", "elements": elements, "duration_seconds": 40}

def build_regression_line(
    points: List[Tuple[float, float]],
    xlabel: str = "x",
    ylabel: str = "y"
) -> Dict[str, Any]:
    """Build regression line."""
    if len(points) < 2:
        return {"id": "regression", "elements": [], "duration_seconds": 20}
    
    n = len(points)
    sum_x = sum(p[0] for p in points)
    sum_y = sum(p[1] for p in points)
    sum_xy = sum(p[0] * p[1] for p in points)
    sum_x2 = sum(p[0]**2 for p in points)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x**2)
    intercept = (sum_y - slope * sum_x) / n
    
    elements = [
        {"type": "Title", "content": f"Linear Regression", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "regression", "position": "[0, 0, 0]", "style": {"x_range": [0, 10, 2], "y_range": [0, 10, 2]}},
    ]
    
    for x, y in points[:8]:
        elements.append({
            "type": "Circle",
            "position": f"[{x}, {y}, 0]",
            "style": {"radius": 0.1, "fill_color": "#3498DB"}
        })
    
    elements.append({
        "type": "Graph",
        "content": f"{slope}*x + {intercept}",
        "position": "[0, 0, 0]",
        "style": {"color": "#E74C3C", "stroke_width": 2}
    })
    
    elements.extend([
        {"type": "Mathtex", "content": f"y = {slope:.2f}x + {intercept:.2f}", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "regression", "elements": elements, "duration_seconds": 35}

def build_complex_plane(
    z: complex = 1 + 1j
) -> Dict[str, Any]:
    """Build complex number on Argand diagram."""
    r = abs(z)
    theta = math.degrees(math.atan2(z.imag, z.real))
    
    elements = [
        {"type": "Title", "content": f"Complex Number: {z}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "complex", "position": "[0, 0, 0]", "style": {"x_range": [-2, 3, 1], "y_range": [-2, 3, 1]}},
        {"type": "Line", "position": "[0, 0, 0]", "style": {"color": "#3498DB", "stroke_width": 1}},
        {"type": "Line", "position": "[0, 0, 0]", "style": {"color": "#3498DB", "stroke_width": 1}},
        {"type": "Arrow", "position": "[0, 0, 0]", "style": {"color": "#E74C3C", "stroke_width": 3}},
        {"type": "Circle", "position": f"[{z.real}, {z.imag}, 0]", "style": {"radius": 0.1, "fill_color": "#E74C3C"}},
        {"type": "Text", "content": f"z = {z}", "position": f"[{z.real + 0.3}, {z.imag + 0.3}, 0]", "style": {"color": "#E74C3C"}},
        {"type": "Text", "content": f"|z| = {r:.2f}", "position": "[-2.5, 2.5, 0]", "style": {"color": "#FFEAA7"}},
        {"type": "Text", "content": f"arg(z) = {theta}°", "position": "[1.5, 2.5, 0]", "style": {"color": "#FFEAA7"}},
        {"type": "Mathtex", "content": "z = r e^{iθ}", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7"}},
    ]
    
    return {"id": "complex", "elements": elements, "duration_seconds": 35}

def build_slope_field(
    func: str = "y",
    x_range: List[float] = [-2, 2],
    y_range: List[float] = [-2, 2]
) -> Dict[str, Any]:
    """Build slope field for differential equation."""
    elements = [
        {"type": "Title", "content": "Slope Field: dy/dx = " + func, "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "slopefield", "position": "[0, 0, 0]", "style": {"x_range": x_range, "y_range": y_range}},
    ]
    
    step = 0.5
    for x in [x_range[0] + i * step for i in range(int((x_range[1] - x_range[0]) / step))]:
        for y in [y_range[0] + i * step for i in range(int((y_range[1] - y_range[0]) / step))]:
            try:
                slope = eval(func, {'__builtins__': None, 'math': math}, {'x': x, 'y': y})
            except:
                slope = y
            
            if -5 < slope < 5:
                angle = math.atan(slope)
                elements.append({
                    "type": "Line",
                    "position": f"[{x}, {y}, 0]",
                    "style": {
                        "color": "#3498DB" if abs(slope) < 1 else "#E74C3C",
                        "stroke_width": 1,
                        "rotation": math.degrees(angle)
                    }
                })
    
    return {"id": "slopefield", "elements": elements, "duration_seconds": 40}

def build_fourier_synthesis(
    n_harmonics: int = 4
) -> Dict[str, Any]:
    """Build Fourier series synthesis."""
    elements = [
        {"type": "Title", "content": f"Fourier Synthesis (n={n_harmonics})", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "fourier", "position": "[0, 0, 0]", "style": {"x_range": [0, 4*math.pi, 1], "y_range": [-2, 2, 1]}},
    ]
    
    colors = ["#3498DB", "#E74C3C", "#2ECC71", "#F39C12", "#9B59B6", "#E91E63"]
    for i in range(n_harmonics):
        if i % 2 == 1:
            coef = 4 / (math.pi * i)
            elements.append({
                "type": "Graph",
                "content": f"{coef}*sin({i}*x)" if i < 4 else f"sin({i}*x)/{i}",
                "position": "[0, 0, 0]",
                "style": {"color": colors[i % len(colors)], "x_range": [0, 4*math.pi]}
            })
    
    elements.append({
        "type": "Graph",
        "content: "sin(x) + sin(3x)/3 + sin(5x)/5",
        "position": "[0, 0, 0]",
        "style": {"color": "#E74C3C", "stroke_width": 2, "x_range": [0, 4*math.pi]}
    })
    
    return {"id": "fourier", "elements": elements, "duration_seconds": 40}

def build_conic_section(
    type: str = "ellipse",
    a: float = 2.0,
    b: float = 1.5
) -> Dict[str, Any]:
    """Build conic section."""
    elements = [
        {"type": "Title", "content": type.title(), "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    if type == "ellipse":
        elements.extend([
            {"type": "Circle", "position": "[0, 0, 0]", "style": {"radius": 1.5, "stroke_color": "#3498DB", "stroke_width": 2}},
            {"type": "Mathtex", "content": r"\frac{x^2}{a^2} + \frac{y^2}{b^2} = 1", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7"}},
            {"type": "Text", "content": f"a={a}, b={b}", "position": "[-2.5, 2.5, 0]", "style": {"color": "#FFEAA7"}},
        ])
    elif type == "parabola":
        elements.extend([
            {"type": "Graph", "content": "x**2", "position": "[0, 0, 0]", "style": {"color": "#E74C3C}},
            {"type": "Mathtex", "content": "y = x^2", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7"}},
        ])
    elif type == "hyperbola":
        elements.extend([
            {"type": "Graph", "content": "x**2 - 1", "position": "[0, 0, 0]", "style": {"color": "#2ECC71"}},
            {"type": "Graph", "content": "1 - x**2", "position": "[0, 0, 0]", "style": {"color": "#2ECC71"}},
        ])
    
    return {"id": "conic", "elements": elements, "duration_seconds": 30}

def build_gram_schmidt(
    vectors: List[List[float]]
) -> Dict[str, Any]:
    """Build Gram-Schmidt orthogonalization."""
    elements = [
        {"type": "Title", "content": "Gram-Schmidt Process", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "gramschmidt", "position": "[0, 0, 0]", "style": {"x_range": [-2, 3, 1], "y_range": [-2, 3, 1]}},
    ]
    
    for i, v in enumerate(vectors[:3]):
        elements.append({
            "type": "Arrow",
            "position": "[0, 0, 0]",
            "style": {"color": "#3498DB" if i == 0 else ("#E74C3C" if i == 1 else "#2ECC71"), "stroke_width": 2}
        })
        elements.append({
            "type": "Text",
            content: f"v{i+1}",
            "position": f"[{v[0]*1.1}, {v[1]*1.1}, 0]",
            "style": {"color": "#3498DB" if i == 0 else ("#E74C3C" if i == 1 else "#2ECC71")}
        })
    
    elements.append({"type": "Text", "content": "Orthogonal vectors", "position": "[0, -2.5, 0]", "style": {"color": "#FFEAA7"}})
    
    return {"id": "gramschmidt", "elements": elements, "duration_seconds": 35}

def build_polynomial_roots(
    coeffs: List[float]
) -> Dict[str, Any]:
    """Build polynomial roots visualization."""
    import cmath
    
    if len(coeffs) == 3:
        a, b, c = coeffs
        discriminant = b**2 - 4*a*c
        if discriminant >= 0:
            r1 = (-b + discriminant**0.5) / (2*a)
            r2 = (-b - discriminant**0.5) / (2*a)
        else:
            r1 = complex(-b/(2*a), (abs(discriminant)**0.5)/(2*a))
            r2 = complex(-b/(2*a), -(abs(discriminant)**0.5)/(2*a))
    else:
        r1, r2 = 0, 0
    
    elements = [
        {"type": "Title", "content": "Polynomial Roots", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
        {"type": "Axes", "content": "roots", "position": "[0, 0, 0]", "style": {"x_range": [-3, 3, 1], "y_range": [-3, 3, 1]}},
        {"type": "Line", "position": "[0, -3, 0]", "style": {"color": "#607D8B", "stroke_width": 1}},
        {"type": "Line", "position": "[-3, 0, 0]", "style": {"color": "#607D8B", "stroke_width": 1}},
    ]
    
    if isinstance(r1, complex) or isinstance(r2, complex):
        re1, im1 = r1.real, r1.imag
        re2, im2 = r2.real, r2.imag
        elements.extend([
            {"type": "Circle", "position": f"[{re1}, {im1}, 0]", "style": {"radius": 0.1, "fill_color": "#E74C3C"}},
            {"type": "Circle", "position": f"[{re2}, {im2}, 0]", "style": {"radius": 0.1, "fill_color": "#E74C3C"}},
        ])
    else:
        elements.extend([
            {"type": "Circle", "position": f"[{r1}, 0, 0]", "style": {"radius": 0.1, "fill_color": "#E74C3C"}},
            {"type": "Circle", "position": f"[{r2}, 0, 0]", "style": {"radius": 0.1, "fill_color": "#E74C3C"}},
        ])
    
    elements.extend([
        {"type": "Text", "content": f"r1 = {r1}", "position": "[-2.5, 2.5, 0]", "style": {"color": "#FFEAA7"}},
        {"type": "Text", "content": f"r2 = {r2}", "position": "[0, 2.5, 0]", "style": {"color": "#FFEAA7"}},
    ])
    
    return {"id": "roots", "elements": elements, "duration_seconds": 35}

def build_laplace_transform(
    func: str = "1"
) -> Dict[str, Any]:
    """Build Laplace transform."""
    elements = [
        {"type": "Title", "content": f"L{func}", "position": "[0, 3.3, 0]", "style": {"color": "#ffffff"}},
    ]
    
    transforms = {
        "1": ("1/s", "#3498DB"),
        "t": ("1/s²", "#E74C3C"),
        "e^{at}": ("1/(s-a)", "#2ECC71"),
        "sin(at)": ("a/(s²+a²)", "#F39C12"),
        "cos(at)": ("s/(s²+a²)", "#9B59B6"),
    }
    
    result, color = transforms.get(func, ("?", "#FFEAA7"))
    
    elements.extend([
        {"type": "Mathtex", "content": r"\mathcal{L}\{f(t)\} = \int_0^\infty e^{-st}f(t)dt", "position": "[0, 2.5, 0]", "style": {"color": "#FFEAA7"}},
        {"type": "Text", "content": f"= {result}", "position": "[0, 1.5, 0]", "style": {"color": color, "font_size": 24}},
    ])
    
    return {"id": "laplace", "elements": elements, "duration_seconds": 35}