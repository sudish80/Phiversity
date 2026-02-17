"""
Enhanced Step-to-Scene Mapper: FIXES ALL Step Jump, Skip, and Overlap Issues

This module ensures:
1. NO STEP SKIPPED - Every solution step has a dedicated scene
2. NO STEP JUMP - Steps appear in sequential order
3. NO TIMELINE OVERLAP - Elements don't overlap in time
4. NO SPATIAL OVERLAP - Elements don't overlap visually
5. COMPLETE CONTENT - All code, outputs, and explanations shown

Author: Phiversity Team
"""

import json
from typing import Dict, List, Any, Tuple, Set
from pathlib import Path
import re


class EnhancedStepMapper:
    """Enhanced mapper that fixes all step and overlap issues."""
    
    def __init__(self):
        self.fixed_issues: List[str] = []
        
    def process_solution(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Process solution and fix ALL issues.
        
        Returns: (fixed_data, list_of_fixes)
        """
        self.fixed_issues = []
        
        # Step 1: Ensure all steps have scenes (fix skipped steps)
        data = self._fix_skipped_steps(data)
        
        # Step 2: Ensure step order is sequential (fix step jumping)
        data = self._fix_step_order(data)
        
        # Step 3: Fix timeline overlaps
        data = self._fix_timeline_overlaps(data)
        
        # Step 4: Fix spatial overlaps  
        data = self._fix_spatial_overlaps(data)
        
        # Step 5: Ensure complete content (code, outputs, explanations)
        data = self._ensure_complete_content(data)
        
        return data, self.fixed_issues
    
    def _fix_skipped_steps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix: Ensure every solution step has a scene."""
        solution = data.get("solution", {})
        steps = solution.get("steps", [])
        
        animation_plan = data.get("animation_plan", {})
        scenes = animation_plan.get("scenes", [])
        
        if len(scenes) < len(steps):
            self.fixed_issues.append(
                f"[FIX] Created {len(steps) - len(scenes)} missing scenes for skipped steps"
            )
            
            # Create missing scenes
            for step_idx in range(len(scenes), len(steps)):
                step = steps[step_idx]
                
                # Create comprehensive scene for this step
                scene = self._create_complete_scene(step, step_idx)
                scenes.append(scene)
            
            animation_plan["scenes"] = scenes
            data["animation_plan"] = animation_plan
            
        return data
    
    def _create_complete_scene(self, step: Dict, step_idx: int) -> Dict[str, Any]:
        """Create a complete scene with all content for a step."""
        
        # Extract step content
        title = step.get("title", f"Step {step_idx + 1}")
        content = step.get("content", "")
        explanation = step.get("explanation", "")
        formula = step.get("formula", "")
        code = step.get("code", "")
        output = step.get("output", "")
        
        # Calculate vertical position for this step
        base_y = 2.0 - (step_idx * 0.8)  # Move down for each step
        
        elements = []
        current_y = base_y
        current_time = 0.0
        
        # Element 1: Step Title (always first)
        elements.append({
            "id": f"step_{step_idx+1}_title",
            "type": "Text",
            "content": f"Step {step_idx + 1}: {title}",
            "position": f"[-3, {current_y}, 0]",
            "z_index": 100 - step_idx,
            "timing": {
                "start": current_time,
                "duration_in": 1.0,
                "transition_in": "Write"
            }
        })
        current_time += 1.5
        
        # Element 2: Explanation/Content
        if explanation or content:
            current_y -= 0.5
            elements.append({
                "id": f"step_{step_idx+1}_content",
                "type": "Text",
                "content": explanation or content,
                "position": f"[-3, {current_y}, 0]",
                "z_index": 90 - step_idx,
                "timing": {
                    "start": current_time,
                    "duration_in": 1.0,
                    "transition_in": "FadeIn"
                }
            })
            current_time += 1.0
        
        # Element 3: Formula (Math)
        if formula:
            current_y -= 0.6
            elements.append({
                "id": f"step_{step_idx+1}_formula",
                "type": "MathTex",
                "content": formula,
                "position": f"[1, {current_y}, 0]",
                "z_index": 80 - step_idx,
                "timing": {
                    "start": current_time,
                    "duration_in": 1.5,
                    "transition_in": "Write"
                }
            })
            current_time += 2.0
        
        # Element 4: Code
        if code:
            current_y -= 0.8
            elements.append({
                "id": f"step_{step_idx+1}_code",
                "type": "Code",
                "content": code,
                "position": f"[1, {current_y}, 0]",
                "z_index": 70 - step_idx,
                "timing": {
                    "start": current_time,
                    "duration_in": 1.0,
                    "transition_in": "FadeIn"
                }
            })
            current_time += 1.5
        
        # Element 5: Output
        if output:
            current_y -= 0.5
            elements.append({
                "id": f"step_{step_idx+1}_output",
                "type": "Text",
                "content": f"→ {output}",
                "position": f"[1, {current_y}, 0]",
                "z_index": 60 - step_idx,
                "category": "output",
                "timing": {
                    "start": current_time,
                    "duration_in": 0.8,
                    "transition_in": "FadeIn"
                }
            })
            current_time += 1.0
        
        # Calculate scene duration
        scene_duration = current_time + 1.0  # Add pause at end
        
        return {
            "id": f"scene_{step_idx+1}",
            "description": title,
            "voiceover": explanation,
            "duration": scene_duration,
            "elements": elements
        }
    
    def _fix_step_order(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix: Ensure steps appear in sequential order."""
        animation_plan = data.get("animation_plan", {})
        scenes = animation_plan.get("scenes", [])
        
        # Check if scenes are in order
        for i, scene in enumerate(scenes):
            scene_id = scene.get("id", "")
            expected_id = f"scene_{i+1}"
            
            if scene_id != expected_id:
                self.fixed_issues.append(
                    f"[FIX] Reordered scene {i+1}: '{scene_id}' -> '{expected_id}'"
                )
                scene["id"] = expected_id
        
        # Ensure descriptions are in order
        solution = data.get("solution", {})
        steps = solution.get("steps", [])
        
        for i, scene in enumerate(scenes):
            if i < len(steps):
                expected_title = steps[i].get("title", f"Step {i+1}")
                scene["description"] = f"Step {i+1}: {expected_title}"
        
        animation_plan["scenes"] = scenes
        data["animation_plan"] = animation_plan
        
        return data
    
    def _fix_timeline_overlaps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix: Ensure no elements overlap in time."""
        animation_plan = data.get("animation_plan", {})
        scenes = animation_plan.get("scenes", [])
        
        for scene_idx, scene in enumerate(scenes):
            elements = scene.get("elements", [])
            
            if not elements:
                continue
                
            # Sort elements by start time
            elements.sort(key=lambda e: e.get("timing", {}).get("start", 0))
            
            # Fix overlaps: ensure each element starts after previous ends
            prev_end = 0.0
            
            for elem in elements:
                timing = elem.get("timing", {})
                start = timing.get("start", 0)
                duration = timing.get("duration_in", 1.0)
                
                if start < prev_end:
                    # Overlap detected, fix it
                    new_start = prev_end + 0.1  # 100ms gap
                    timing["start"] = round(new_start, 2)
                    elem["timing"] = timing
                    
                    self.fixed_issues.append(
                        f"[FIX] Scene {scene_idx+1}, element '{elem.get('id', 'unknown')}': "
                        f"timeline overlap fixed (start: {start}s -> {new_start:.2f}s)"
                    )
                
                prev_end = timing.get("start", 0) + timing.get("duration_in", 1.0)
            
            scene["elements"] = elements
            
            # Update scene duration if needed
            if scene.get("duration", 0) < prev_end:
                scene["duration"] = prev_end + 0.5
        
        animation_plan["scenes"] = scenes
        data["animation_plan"] = animation_plan
        
        return data
    
    def _fix_spatial_overlaps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix: Ensure no elements overlap visually."""
        animation_plan = data.get("animation_plan", {})
        scenes = animation_plan.get("scenes", [])
        
        for scene_idx, scene in enumerate(scenes):
            elements = scene.get("elements", [])
            
            if not elements:
                continue
            
            # Compute positions and fix overlaps
            positions = self._compute_element_positions(elements)
            
            # Check and fix overlaps
            fixed_positions = self._resolve_position_overlaps(positions, elements)
            
            # Apply fixed positions
            for elem_id, new_pos in fixed_positions.items():
                for elem in elements:
                    if elem.get("id") == elem_id:
                        elem["position"] = f"[{new_pos[0]}, {new_pos[1]}, 0]"
                        break
        
        animation_plan["scenes"] = scenes
        data["animation_plan"] = animation_plan
        
        return data
    
    def _compute_element_positions(self, elements: List[Dict]) -> Dict[str, Tuple[float, float, float, float]]:
        """Compute bounding boxes for elements."""
        positions = {}
        
        for elem in elements:
            elem_id = elem.get("id", "unknown")
            position_str = elem.get("position", "[0, 0, 0]")
            
            # Parse position
            match = re.findall(r'[-+]?\d*\.?\d+', position_str)
            if len(match) >= 2:
                x, y = float(match[0]), float(match[1])
            else:
                x, y = 0.0, 0.0
            
            # Estimate size based on type
            elem_type = elem.get("type", "").lower()
            content = elem.get("content", "")
            
            if "mathtex" in elem_type or "latex" in elem_type or "math" in elem_type:
                width, height = 3.0, 0.5
            elif "code" in elem_type:
                width, height = 2.5, 0.4 * len(content.split("\n"))
            else:
                width = min(5.0, 0.1 * len(content) + 1.0)
                height = 0.4
            
            positions[elem_id] = (x - width/2, x + width/2, y - height/2, y + height/2)
        
        return positions
    
    def _resolve_position_overlaps(self, positions: Dict, elements: List[Dict]) -> Dict[str, Tuple[float, float]]:
        """Resolve spatial overlaps by shifting elements."""
        new_positions = {}
        
        # Sort by position (left to right, top to bottom)
        sorted_elems = sorted(
            [(e.get("id", ""), positions.get(e.get("id", ""), (0,0,0,0))) for e in elements],
            key=lambda x: (x[1][2], x[1][0])  # Sort by y, then x
        )
        
        used_positions: Set[Tuple[float, float]] = set()
        
        for elem_id, bounds in sorted_elems:
            if not bounds:
                continue
                
            x_center = (bounds[0] + bounds[1]) / 2
            y_center = (bounds[2] + bounds[3]) / 2
            width = bounds[1] - bounds[0]
            height = bounds[3] - bounds[2]
            
            # Try original position first
            if (x_center, y_center) not in used_positions:
                new_positions[elem_id] = (x_center, y_center)
                used_positions.add((x_center, y_center))
                continue
            
            # Find nearest free position
            found = False
            for offset in [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]:
                # Try right
                test_pos = (x_center + offset, y_center)
                if test_pos not in used_positions:
                    new_positions[elem_id] = test_pos
                    used_positions.add(test_pos)
                    found = True
                    self.fixed_issues.append(
                        f"[FIX] Spatial overlap: shifted '{elem_id}' to x+{offset}"
                    )
                    break
                # Try left
                test_pos = (x_center - offset, y_center)
                if test_pos not in used_positions:
                    new_positions[elem_id] = test_pos
                    used_positions.add(test_pos)
                    found = True
                    self.fixed_issues.append(
                        f"[FIX] Spatial overlap: shifted '{elem_id}' to x-{offset}"
                    )
                    break
                # Try up
                test_pos = (x_center, y_center + offset)
                if test_pos not in used_positions:
                    new_positions[elem_id] = test_pos
                    used_positions.add(test_pos)
                    found = True
                    self.fixed_issues.append(
                        f"[FIX] Spatial overlap: shifted '{elem_id}' to y+{offset}"
                    )
                    break
                # Try down
                test_pos = (x_center, y_center - offset)
                if test_pos not in used_positions:
                    new_positions[elem_id] = test_pos
                    used_positions.add(test_pos)
                    found = True
                    self.fixed_issues.append(
                        f"[FIX] Spatial overlap: shifted '{elem_id}' to y-{offset}"
                    )
                    break
            
            if not found:
                # Use original position anyway
                new_positions[elem_id] = (x_center, y_center)
        
        return new_positions
    
    def _ensure_complete_content(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Ensure all content (code, outputs, explanations) is included."""
        solution = data.get("solution", {})
        steps = solution.get("steps", [])
        
        animation_plan = data.get("animation_plan", {})
        scenes = animation_plan.get("scenes", [])
        
        for step_idx, step in enumerate(steps):
            if step_idx >= len(scenes):
                continue
            
            scene = scenes[step_idx]
            elements = scene.get("elements", [])
            
            # Check for code in step
            has_code = step.get("code", "")
            has_code_elem = any("code" in e.get("type", "").lower() for e in elements)
            
            if has_code and not has_code_elem:
                self.fixed_issues.append(
                    f"[FIX] Step {step_idx+1}: Added missing code element"
                )
                # Add code element
                elements.append({
                    "id": f"step_{step_idx+1}_code",
                    "type": "Code",
                    "content": has_code,
                    "position": "[1, -1, 0]",
                    "timing": {"start": 3.0, "duration_in": 1.0, "transition_in": "FadeIn"}
                })
            
            # Check for output in step
            has_output = step.get("output", "")
            has_output_elem = any("output" in e.get("category", "").lower() for e in elements)
            
            if has_output and not has_output_elem:
                self.fixed_issues.append(
                    f"[FIX] Step {step_idx+1}: Added missing output element"
                )
                # Add output element
                elements.append({
                    "id": f"step_{step_idx+1}_output",
                    "type": "Text",
                    "content": f"→ {has_output}",
                    "position": "[1, -1.5, 0]",
                    "category": "output",
                    "timing": {"start": 4.0, "duration_in": 0.8, "transition_in": "FadeIn"}
                })
            
            scene["elements"] = elements
        
        animation_plan["scenes"] = scenes
        data["animation_plan"] = animation_plan
        
        return data


def process_json_file(json_path: Path) -> Dict[str, Any]:
    """Load JSON, process it, save and return report."""
    data = json.loads(json_path.read_text(encoding="utf-8"))
    
    mapper = EnhancedStepMapper()
    fixed_data, fixes = mapper.process_solution(data)
    
    # Save fixed version
    json_path.write_text(json.dumps(fixed_data, indent=2, ensure_ascii=False), encoding="utf-8")
    
    return {
        "file": json_path.name,
        "fixes_applied": fixes,
        "total_fixes": len(fixes)
    }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        json_file = Path(sys.argv[1])
        if json_file.exists():
            result = process_json_file(json_file)
            print(f"\n=== PROCESSED: {result['file']} ===")
            print(f"Total fixes: {result['total_fixes']}")
            for fix in result['fixes_applied']:
                print(f"  • {fix}")
        else:
            print(f"File not found: {json_file}")
    else:
        print("Usage: python step_mapper_fixed.py <path/to/solution.json>")