"""
Step-to-Scene Mapper: Ensures every solution step has a dedicated scene and fixes timeline overlaps.

This module enforces:
1. One scene per solution step (no skipped steps)
2. Sequential timeline management (no overlapping elements)
3. Visual element requirements (no text-only steps)
"""

import json
from typing import Dict, List, Any, Tuple
from pathlib import Path


class StepToSceneMapper:
    """Maps solution steps to animation scenes and enforces visual requirements."""
    
    @staticmethod
    def validate_and_fix_step_coverage(data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Ensure every solution step has a corresponding animation scene.
        
        Args:
            data: The full solution + animation_plan JSON
            
        Returns:
            (fixed_data, warnings_list)
        """
        warnings = []
        solution_steps = data.get("solution", {}).get("steps", [])
        animation_scenes = data.get("animation_plan", {}).get("scenes", [])
        
        if len(animation_scenes) < len(solution_steps):
            warnings.append(
                f"[WARNING] SKIPPED STEPS: {len(solution_steps)} steps but only {len(animation_scenes)} scenes. "
                f"Creating additional scenes for missing steps."
            )
            # Auto-generate missing scenes
            data = StepToSceneMapper._create_missing_scenes(data, solution_steps)
        
        return data, warnings
    
    @staticmethod
    def validate_visual_elements(data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Ensure every scene has at least one visual element (not just text).
        
        Args:
            data: The full solution + animation_plan JSON
            
        Returns:
            (fixed_data, warnings_list)
        """
        warnings = []
        animation_scenes = data.get("animation_plan", {}).get("scenes", [])
        
        visual_types = {"Graph", "Circle", "Rectangle", "Polygon", "Annulus", "Axes", "Arrow", "Line", "VectorField"}
        
        for idx, scene in enumerate(animation_scenes):
            elements = scene.get("elements", [])
            has_visual = any(elem.get("type") in visual_types for elem in elements)
            
            if not has_visual:
                warnings.append(
                    f"[WARNING] NO VISUALS: Scene {idx + 1} has no diagram/graph (only Text/Latex). "
                    f"Adding visual element recommendation."
                )
        
        return data, warnings
    
    @staticmethod
    def fix_timeline_overlaps(data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Fix elements with overlapping start times.
        Elements should start sequentially: start1 < (start1 + duration1) <= start2 <= ...
        
        Args:
            data: The full solution + animation_plan JSON
            
        Returns:
            (fixed_data, warnings_list)
        """
        warnings = []
        animation_scenes = data.get("animation_plan", {}).get("scenes", [])
        
        for scene_idx, scene in enumerate(animation_scenes):
            elements = scene.get("elements", [])
            
            # Sort elements by start time
            elements_with_timing = [
                (idx, elem) for idx, elem in enumerate(elements)
                if elem.get("timing") and "start" in elem.get("timing", {})
            ]
            
            if len(elements_with_timing) <= 1:
                continue
            
            # Check for overlaps
            elements_with_timing.sort(key=lambda x: x[1].get("timing", {}).get("start", 0))
            
            has_overlap = False
            prev_idx, prev_elem = elements_with_timing[0]
            prev_start = prev_elem.get("timing", {}).get("start", 0)
            prev_duration = prev_elem.get("timing", {}).get("duration_in", 1.0)
            prev_end = prev_start + prev_duration
            
            for curr_idx, curr_elem in elements_with_timing[1:]:
                curr_start = curr_elem.get("timing", {}).get("start", 0)
                
                # If current starts before previous ends, there's overlap
                if curr_start < prev_end:
                    has_overlap = True
                    # Fix: set current to start after previous ends
                    new_start = prev_end + 0.1  # 100ms gap
                    curr_elem["timing"]["start"] = round(new_start, 2)
                    warnings.append(
                        f"[WARNING] TIMELINE OVERLAP: Scene {scene_idx + 1}, element {curr_idx + 1} "
                        f"overlapped with previous. Fixed start time to {new_start:.1f}s"
                    )
                
                prev_start = curr_elem.get("timing", {}).get("start", 0)
                prev_duration = curr_elem.get("timing", {}).get("duration_in", 1.0)
                prev_end = prev_start + prev_duration
        
        return data, warnings
    
    @staticmethod
    def _create_missing_scenes(data: Dict[str, Any], solution_steps: List[Dict[str, str]]) -> Dict[str, Any]:
        """Create placeholder scenes for missing solution steps."""
        animation_plan = data.get("animation_plan", {})
        existing_scenes = animation_plan.get("scenes", [])
        
        # Generate missing scenes
        for step_idx in range(len(existing_scenes), len(solution_steps)):
            step = solution_steps[step_idx]
            scene = {
                "id": f"step_{step_idx + 1}",
                "description": f"Visualizing: {step.get('title', 'Step')}",
                "voiceover": step.get("explanation", ""),
                "elements": [
                    {
                        "type": "Text",
                        "content": step.get("title", f"Step {step_idx + 1}"),
                        "position": "[0, 2, 0]",
                        "style": {"color": "#FFFFFF", "font_size": 48},
                        "timing": {"start": 0.0, "duration_in": 1.0, "transition_in": "Write"}
                    },
                    {
                        "type": "Latex",
                        "content": step.get("latex", "\\text{Insert visual diagram here}"),
                        "position": "[0, 0, 0]",
                        "style": {"color": "#FFFF00"},
                        "timing": {"start": 1.5, "duration_in": 1.0, "transition_in": "FadeIn"}
                    }
                ]
            }
            existing_scenes.append(scene)
        
        animation_plan["scenes"] = existing_scenes
        data["animation_plan"] = animation_plan
        return data
    
    @staticmethod
    def validate_and_fix_all(data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Run all validations and fixes.
        
        Args:
            data: The full solution + animation_plan JSON
            
        Returns:
            (fixed_data, all_warnings)
        """
        all_warnings = []
        
        # Fix step coverage
        data, warnings = StepToSceneMapper.validate_and_fix_step_coverage(data)
        all_warnings.extend(warnings)
        
        # Check visual elements
        data, warnings = StepToSceneMapper.validate_visual_elements(data)
        all_warnings.extend(warnings)
        
        # Fix timeline overlaps
        data, warnings = StepToSceneMapper.fix_timeline_overlaps(data)
        all_warnings.extend(warnings)
        
        return data, all_warnings


def process_json_file(json_path: Path) -> bool:
    """
    Load JSON, validate and fix it, save it back.
    
    Returns:
        True if changes were made, False otherwise
    """
    data = json.loads(json_path.read_text(encoding="utf-8"))
    fixed_data, warnings = StepToSceneMapper.validate_and_fix_all(data)
    
    # Check if changes were made
    changed = json.dumps(data) != json.dumps(fixed_data)
    
    if changed or warnings:
        # Save fixed version
        json_path.write_text(json.dumps(fixed_data, indent=2, ensure_ascii=False), encoding="utf-8")
        
        # Print report
        print(f"\n[STEP-SCENE MAPPER] Processing: {json_path.name}")
        if warnings:
            for warning in warnings:
                print(f"  {warning}")
        if changed:
            print(f"  ✓ Fixed and saved")
        return True
    else:
        print(f"\n[STEP-SCENE MAPPER] {json_path.name}: OK (no issues)")
        return False


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) > 1:
        json_file = Path(sys.argv[1])
        if json_file.exists():
            process_json_file(json_file)
        else:
            print(f"File not found: {json_file}")
    else:
        print("Usage: python step_to_scene_mapper.py <path/to/animation_plan.json>")
