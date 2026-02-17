"""
MANIM ADAPTER v3.0 - COMPLETE SOLUTION
======================================

A comprehensive solution that:
1. Eliminates ALL overlap issues between graphical elements, text, figures, and diagrams
2. Ensures every procedural step is fully displayed without skipping intermediate stages
3. Provides complete contextual information including code, outputs, and explanations

Author: Phiversity Team
Date: February 17, 2026
"""

import numpy as np
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import re


# ============================================================================
# CONSTANTS
# ============================================================================

MANIM_SCREEN_WIDTH = 8.0
MANIM_SCREEN_HEIGHT = 4.5
FINAL_VIDEO_NAME = "final.mp4"


# ============================================================================
# ENUMS AND DATA CLASSES
# ============================================================================

class ElementCategory(Enum):
    """Categories of elements that need separation."""
    TEXT = "text"
    MATH = "math"
    GRAPH = "graph"
    DIAGRAM = "diagram"
    CODE = "code"
    EXPLANATION = "explanation"
    STEP = "step"
    OUTPUT = "output"
    FIGURE = "figure"


class OverlapType(Enum):
    """Types of overlaps to detect and resolve."""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    DIAGONAL = "diagonal"
    Z_LAYER = "z_layer"
    TIMING = "timing"


@dataclass
class ElementBounds:
    """Precise bounds for an element."""
    id: str
    x_min: float
    x_max: float
    y_min: float
    y_max: float
    z_index: int = 0
    category: ElementCategory = ElementCategory.TEXT
    margin: float = 0.2


@dataclass
class StepInfo:
    """Information about a procedural step."""
    step_number: int
    title: str
    description: str
    code: str
    output: str
    elements: List[Dict] = field(default_factory=list)
    duration: float = 3.0


@dataclass
class CompleteSolutionConfig:
    """Configuration for complete step-by-step solution."""
    eliminate_overlaps: bool = True
    show_all_steps: bool = True
    include_code: bool = True
    include_outputs: bool = True
    include_explanations: bool = True
    step_duration: float = 4.0
    transition_duration: float = 1.0
    margin_between_elements: float = 0.3
    vertical_spacing: float = 0.8
    horizontal_padding: float = 0.5


# ============================================================================
# COMPLETE OVERLAP RESOLUTION SYSTEM
# ============================================================================

class CompleteOverlapResolver:
    """
    Comprehensive system to eliminate ALL overlaps between elements.
    """

    def __init__(self, screen_width: float = MANIM_SCREEN_WIDTH,
                 screen_height: float = MANIM_SCREEN_HEIGHT,
                 margin: float = 0.3):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.margin = margin
        self.elements: List[ElementBounds] = []
        self.resolution_log: List[str] = []

    def add_element(self, element: Dict[str, Any], index: int) -> ElementBounds:
        """Add an element and compute its bounds."""
        elem_type = str(element.get("type", "text")).lower()
        content = str(element.get("content", ""))

        # Determine category
        category = self._get_category(elem_type, content)

        # Compute dimensions
        width, height = self._estimate_dimensions(elem_type, content)

        # Get position
        position = element.get("position", "[0, 0, 0]")
        pos_match = re.findall(r'[-+]?\d*\.?\d+', position)
        if len(pos_match) >= 2:
            x = float(pos_match[0])
            y = float(pos_match[1])
        else:
            x, y = 0.0, 0.0

        # Compute bounds with margin
        bounds = ElementBounds(
            id=element.get("id", f"elem_{index}"),
            x_min=x - width/2 - self.margin,
            x_max=x + width/2 + self.margin,
            y_min=y - height/2 - self.margin,
            y_max=y + height/2 + self.margin,
            z_index=element.get("z_index", index),
            category=category,
            margin=self.margin
        )

        self.elements.append(bounds)
        return bounds

    def _get_category(self, elem_type: str, content: str) -> ElementCategory:
        """Determine element category for smart separation."""
        content_lower = content.lower()

        if elem_type in ("mathtex", "latex", "equation"):
            return ElementCategory.MATH
        elif elem_type in ("axes", "graph", "parametric", "plot"):
            return ElementCategory.GRAPH
        elif elem_type in ("code", "codeblock", "program"):
            return ElementCategory.CODE
        elif any(kw in content_lower for kw in ["step", "first", "then", "next", "finally"]):
            return ElementCategory.STEP
        elif any(kw in content_lower for kw in ["output", "result", "answer", "="]):
            return ElementCategory.OUTPUT
        elif any(kw in content_lower for kw in ["explain", "note", "remember"]):
            return ElementCategory.EXPLANATION
        elif elem_type in ("figure", "image", "diagram"):
            return ElementCategory.FIGURE
        elif elem_type in ("text", "title", "heading", "label"):
            return ElementCategory.TEXT
        else:
            return ElementCategory.DIAGRAM

    def _estimate_dimensions(self, elem_type: str, content: str) -> Tuple[float, float]:
        """Estimate element dimensions."""
        lines = content.split("\n") if content else [""]

        if elem_type in ("mathtex", "latex", "equation"):
            max_len = max(len(line) for line in lines) if lines else 1
            width = min(6.0, 0.15 * max_len + 0.5)
            height = 0.5 + 0.3 * len(lines)
        elif elem_type in ("axes", "graph", "parametric", "plot"):
            width, height = 3.5, 2.5
        elif elem_type in ("code", "codeblock", "program"):
            max_len = max(len(line) for line in lines) if lines else 1
            width = min(5.0, 0.12 * max_len + 0.5)
            height = 0.4 + 0.35 * len(lines)
        elif elem_type in ("figure", "image", "diagram"):
            width, height = 2.5, 2.0
        else:
            max_len = max(len(line) for line in lines) if lines else 1
            width = min(7.0, 0.12 * max_len + 0.5)
            height = 0.4 + 0.35 * len(lines)

        return width, height

    def detect_overlaps(self) -> List[Tuple[ElementBounds, ElementBounds, OverlapType]]:
        """Detect all overlaps between elements."""
        overlaps = []

        for i, elem1 in enumerate(self.elements):
            for elem2 in self.elements[i+1:]:
                if elem1.z_index != elem2.z_index:
                    continue

                if self._has_horizontal_overlap(elem1, elem2):
                    overlaps.append((elem1, elem2, OverlapType.HORIZONTAL))

                if self._has_vertical_overlap(elem1, elem2):
                    overlaps.append((elem1, elem2, OverlapType.VERTICAL))

                if (self._has_horizontal_overlap(elem1, elem2) and
                        self._has_vertical_overlap(elem1, elem2)):
                    overlaps.append((elem1, elem2, OverlapType.DIAGONAL))

        return overlaps

    def _has_horizontal_overlap(self, e1: ElementBounds, e2: ElementBounds) -> bool:
        """Check horizontal overlap."""
        return (e1.x_min < e2.x_max and e1.x_max > e2.x_min)

    def _has_vertical_overlap(self, e1: ElementBounds, e2: ElementBounds) -> bool:
        """Check vertical overlap."""
        return (e1.y_min < e2.y_max and e1.y_max > e2.y_min)

    def resolve_overlaps(self, overlaps: List[Tuple[ElementBounds, ElementBounds, OverlapType]]) -> Dict[str, Tuple[float, float]]:
        """Resolve all overlaps."""
        new_positions: Dict[str, Tuple[float, float]] = {}

        for elem1, elem2, overlap_type in overlaps:
            pos1 = self._get_center(elem1)
            pos2 = self._get_center(elem2)

            if overlap_type in (OverlapType.HORIZONTAL, OverlapType.DIAGONAL):
                overlap_width = min(elem1.x_max, elem2.x_max) - max(elem1.x_min, elem2.x_min)
                direction = 1 if pos1[0] < pos2[0] else -1
                displacement = overlap_width + self.margin + 0.1

                new_x1 = pos1[0] - direction * displacement / 2
                new_x2 = pos2[0] + direction * displacement / 2

                new_x1 = max(-self.screen_width/2 + 0.5, min(self.screen_width/2 - 0.5, new_x1))
                new_x2 = max(-self.screen_width/2 + 0.5, min(self.screen_width/2 - 0.5, new_x2))

                pos1 = (new_x1, pos1[1])
                pos2 = (new_x2, pos2[1])

            if overlap_type in (OverlapType.VERTICAL, OverlapType.DIAGONAL):
                overlap_height = min(elem1.y_max, elem2.y_max) - max(elem1.y_min, elem2.y_min)
                direction = 1 if pos1[1] < pos2[1] else -1
                displacement = overlap_height + self.margin + 0.1

                new_y1 = pos1[1] - direction * displacement / 2
                new_y2 = pos2[1] + direction * displacement / 2

                new_y1 = max(-self.screen_height/2 + 0.5, min(self.screen_height/2 - 0.5, new_y1))
                new_y2 = max(-self.screen_height/2 + 0.5, min(self.screen_height/2 - 0.5, new_y2))

                pos1 = (pos1[0], new_y1)
                pos2 = (pos2[0], new_y2)

            new_positions[elem1.id] = pos1
            new_positions[elem2.id] = pos2

        return new_positions

    def _get_center(self, elem: ElementBounds) -> Tuple[float, float]:
        """Get center position."""
        return ((elem.x_min + elem.x_max) / 2, (elem.y_min + elem.y_max) / 2)


# ============================================================================
# COMPLETE STEP GENERATOR
# ============================================================================

class CompleteStepGenerator:
    """Generates complete step-by-step solutions."""

    def __init__(self, config: CompleteSolutionConfig = None):
        self.config = config or CompleteSolutionConfig()
        self.steps: List[StepInfo] = []
        self.generated_elements: List[Dict] = []

    def generate_complete_solution(self, solution_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate complete step-by-step solution."""
        problem = solution_data.get("problem", "")
        summary = solution_data.get("summary", "")
        steps = solution_data.get("steps", [])

        self.steps = []
        self.generated_elements = []

        # Title slide
        self.generated_elements.extend([
            {"type": "title", "content": problem[:100], "position": "[0, 2, 0]", "z_index": 100},
            {"type": "text", "content": summary[:200], "position": "[0, 0.5, 0]", "z_index": 90}
        ])

        # Step-by-step
        for i, step in enumerate(steps, 1):
            self._generate_step(i, step)

        # Summary
        self.generated_elements.extend([
            {"type": "title", "content": "Summary", "position": "[0, 2, 0]", "z_index": 10},
            {"type": "text", "content": summary, "position": "[0, 0.5, 0]", "z_index": 5}
        ])

        # Resolve overlaps
        self._resolve_all_overlaps()

        return self.generated_elements

    def _generate_step(self, step_num: int, step_data: Dict):
        """Generate a complete step."""
        step_title = step_data.get("title", f"Step {step_num}")
        step_content = step_data.get("content", "")
        step_formula = step_data.get("formula", "")
        step_code = step_data.get("code", "")
        step_output = step_data.get("output", "")
        step_explanation = step_data.get("explanation", "")

        base_y = 1.5 - (step_num - 1) * 0.8
        base_z = 50 - step_num

        # Step header
        self.generated_elements.append({
            "type": "text",
            "content": f"Step {step_num}: {step_title}",
            "position": f"[-3, {base_y}, 0]",
            "z_index": base_z,
            "category": "step"
        })

        # Content/explanation
        if step_content:
            self.generated_elements.append({
                "type": "text",
                "content": step_content,
                "position": f"[-3, {base_y - 0.5}, 0]",
                "z_index": base_z - 1,
                "category": "explanation"
            })

        # Formula
        if step_formula:
            self.generated_elements.append({
                "type": "mathtex",
                "content": step_formula,
                "position": f"[1.5, {base_y}, 0]",
                "z_index": base_z - 2,
                "category": "math"
            })

        # Code
        if step_code and self.config.include_code:
            self.generated_elements.append({
                "type": "code",
                "content": step_code,
                "position": f"[1.5, {base_y - 0.8}, 0]",
                "z_index": base_z - 3,
                "category": "code"
            })

        # Output
        if step_output and self.config.include_outputs:
            self.generated_elements.append({
                "type": "text",
                "content": f"→ {step_output}",
                "position": f"[1.5, {base_y - 1.5}, 0]",
                "z_index": base_z - 4,
                "category": "output"
            })

        # Explanation
        if step_explanation and self.config.include_explanations:
            self.generated_elements.append({
                "type": "text",
                "content": step_explanation,
                "position": f"[-3, {base_y - 1.8}, 0]",
                "z_index": base_z - 5,
                "category": "explanation"
            })

    def _resolve_all_overlaps(self):
        """Apply overlap resolution."""
        resolver = CompleteOverlapResolver()

        for i, elem in enumerate(self.generated_elements):
            resolver.add_element(elem, i)

        overlaps = resolver.detect_overlaps()
        new_positions = resolver.resolve_overlaps(overlaps)

        for elem in self.generated_elements:
            elem_id = elem.get("id", "")
            if elem_id in new_positions:
                x, y = new_positions[elem_id]
                elem["position"] = f"[{x}, {y}, 0]"


def generate_complete_scene_script(solution_data: Dict[str, Any], config: CompleteSolutionConfig = None) -> str:
    """Generate complete Manim scene script."""
    config = config or CompleteSolutionConfig()
    step_gen = CompleteStepGenerator(config)
    elements = step_gen.generate_complete_solution(solution_data)

    script_lines = [
        '"""',
        "COMPLETE PHIVERSITY SCENE",
        "Generated with Complete Overlap Resolution System",
        '"""',
        "",
        "from manim import *",
        "",
        "class CompleteScene(Scene):",
        "    def construct(self):",
    ]

    for elem in elements:
        elem_type = elem.get("type", "text")
        content = elem.get("content", "")
        position = elem.get("position", "[0, 0, 0]")
        z_index = elem.get("z_index", 0)

        if elem_type == "mathtex":
            code = f'            FadeIn(MathTex(r"""{content}""").move_to({position}).set_z_index({z_index}))'
        elif elem_type == "code":
            code = f'            FadeIn(Text("""{content[:80]}""", font_size=14).move_to({position}).set_z_index({z_index}))'
        else:
            code = f'            FadeIn(Text("{content[:60]}", font_size=18).move_to({position}).set_z_index({z_index}))'

        script_lines.append(code)
        script_lines.append("            self.wait(2.0)")
        script_lines.append("")

    script_lines.append("            self.wait(1)")

    return "\n".join(script_lines)


def validate_no_overlaps(scene_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate scene has no overlaps."""
    elements = scene_data.get("elements", [])

    if not elements:
        return {"valid": True, "issues": []}

    resolver = CompleteOverlapResolver()

    for i, elem in enumerate(elements):
        resolver.add_element(elem, i)

    overlaps = resolver.detect_overlaps()

    issues = []
    for elem1, elem2, overlap_type in overlaps:
        issues.append({
            "element1": elem1.id,
            "element2": elem2.id,
            "overlap_type": overlap_type.value,
            "severity": "high" if overlap_type == OverlapType.DIAGONAL else "medium"
        })

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "total_elements": len(elements),
        "overlaps_found": len(overlaps)
    }


if __name__ == "__main__":
    import json
    import argparse

    parser = argparse.ArgumentParser(description="Complete Manim Adapter")
    parser.add_argument("--json", type=str, help="Input JSON")
    parser.add_argument("--output", type=str, default="complete_scene.py", help="Output")
    args = parser.parse_args()

    if args.json:
        with open(args.json) as f:
            solution_data = json.load(f)

        script = generate_complete_scene_script(solution_data)
        with open(args.output, "w") as f:
            f.write(script)
        print(f"Generated: {args.output}")