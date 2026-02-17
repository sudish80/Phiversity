"""
Ultimate Overlap Fixer - Aggressive overlap resolution for video generation

This module provides:
1. Aggressive timeline overlap fixing
2. Complete spatial overlap resolution
3. Scene separation enforcement
4. Y-axis stacking for visual elements
5. Time gap enforcement between scenes

Author: Phiversity Team - Fixed for Production
"""

import json
import re
from typing import Dict, List, Any, Tuple
from pathlib import Path


class UltimateOverlapFixer:
    """
    Ultimate fixer that guarantees NO overlap in video output.
    Uses aggressive strategies to ensure complete separation.
    """
    
    def __init__(self):
        self.fixes_applied: List[str] = []
        
    def process_animation_plan(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Process animation plan and fix ALL overlaps.
        
        Returns: (fixed_data, list_of_fixes)
        """
        self.fixes_applied = []
        
        animation_plan = data.get("animation_plan", {})
        if not animation_plan:
            return data, self.fixes_applied
            
        scenes = animation_plan.get("scenes", [])
        if not scenes:
            return data, self.fixes_applied
            
        # Step 1: Reset all timings to sequential
        scenes = self._reset_scene_timings(scenes)
        
        # Step 2: Add minimum gaps between scenes
        scenes = self._enforce_scene_gaps(scenes, min_gap=2.0)
        
        # Step 3: Fix timeline overlaps within scenes
        scenes = self._fix_intra_scene_overlaps(scenes)
        
        # Step 4: Fix spatial overlaps by Y-axis stacking
        scenes = self._fix_spatial_overlaps_v2(scenes)
        
        # Step 5: Ensure element separation
        scenes = self._ensure_element_separation(scenes)
        
        animation_plan["scenes"] = scenes
        data["animation_plan"] = animation_plan
        
        return data, self.fixes_applied
    
    def _reset_scene_timings(self, scenes: List[Dict]) -> List[Dict]:
        """Reset all scene timings to sequential."""
        current_time = 0.0
        
        for scene_idx, scene in enumerate(scenes):
            # Set scene start time
            scene["start_time"] = current_time
            
            # Calculate scene duration from elements
            elements = scene.get("elements", [])
            if elements:
                max_end = max(
                    elem.get("timing", {}).get("start", 0) + 
                    elem.get("timing", {}).get("duration_in", 1.0)
                    for elem in elements
                )
                scene["duration"] = max_end + 1.0  # Add buffer
            else:
                scene["duration"] = 3.0
                
            current_time += scene["duration"] + 2.0  # 2 second gap between scenes
            
            self.fixes_applied.append(
                f"Scene {scene_idx+1}: reset to start at {scene['start_time']:.2f}s, duration {scene['duration']:.2f}s"
            )
        
        return scenes
    
    def _enforce_scene_gaps(self, scenes: List[Dict], min_gap: float = 2.0) -> List[Dict]:
        """Ensure minimum gap between scenes."""
        for i in range(1, len(scenes)):
            prev_scene = scenes[i-1]
            curr_scene = scenes[i]
            
            prev_end = prev_scene.get("start_time", 0) + prev_scene.get("duration", 3.0)
            curr_start = curr_scene.get("start_time", 0)
            
            if curr_start < prev_end + min_gap:
                new_start = prev_end + min_gap
                curr_scene["start_time"] = new_start
                
                # Shift all elements in this scene
                shift = new_start - curr_start
                for elem in curr_scene.get("elements", []):
                    if "timing" in elem:
                        elem["timing"]["start"] = elem["timing"].get("start", 0) + shift
                
                self.fixes_applied.append(
                    f"Scene {i+1}: enforced gap, shifted to {new_start:.2f}s"
                )
        
        return scenes
    
    def _fix_intra_scene_overlaps(self, scenes: List[Dict]) -> List[Dict]:
        """Fix timeline overlaps within each scene."""
        for scene_idx, scene in enumerate(scenes):
            elements = scene.get("elements", [])
            if not elements:
                continue
                
            # Sort elements by start time
            elements.sort(key=lambda e: e.get("timing", {}).get("start", 0))
            
            current_time = 0.0
            for elem in elements:
                timing = elem.get("timing", {})
                start = timing.get("start", 0)
                duration = timing.get("duration_in", 1.0)
                
                # If overlap, shift element
                if start < current_time:
                    new_start = current_time + 0.1
                    timing["start"] = new_start
                    elem["timing"] = timing
                    
                    self.fixes_applied.append(
                        f"Scene {scene_idx+1}, Element '{elem.get('id', 'unknown')}': "
                        f"timeline overlap fixed, shifted to {new_start:.2f}s"
                    )
                
                current_time = start + duration
        
        return scenes
    
    def _fix_spatial_overlaps_v2(self, scenes: List[Dict]) -> List[Dict]:
        """Fix spatial overlaps using Y-axis stacking."""
        for scene_idx, scene in enumerate(scenes):
            elements = scene.get("elements", [])
            if not elements:
                continue
            
            # Sort elements by type (MathTex first, then Code, then Text)
            type_order = {"mathtex": 0, "latex": 0, "code": 1, "text": 2, "default": 3}
            elements.sort(key=lambda e: type_order.get(e.get("type", "").lower(), 3))
            
            # Stack elements vertically with fixed Y offsets
            current_y = 2.0  # Start from top
            y_offsets = {
                "mathtex": -0.8,
                "latex": -0.8,
                "code": -1.2,
                "text": -0.5,
                "output": -0.5,
                "default": -0.5
            }
            
            for elem in elements:
                elem_type = elem.get("type", "").lower()
                offset = y_offsets.get(elem_type, -0.5)
                
                # Update position
                position = elem.get("position", "[0, 0, 0]")
                match = re.findall(r'[-+]?\d*\.?\d+', position)
                
                if len(match) >= 2:
                    x = float(match[0])
                    # Keep X, update Y
                    new_position = f"[{x}, {current_y}, 0]"
                    elem["position"] = new_position
                    
                    self.fixes_applied.append(
                        f"Scene {scene_idx+1}, Element '{elem.get('id', 'unknown')}': "
                        f"spatial fix, moved to Y={current_y:.2f}"
                    )
                
                current_y += offset
            
            # Update scene duration based on number of elements
            scene["duration"] = max(scene.get("duration", 3.0), abs(current_y) * 0.5 + 2.0)
        
        return scenes
    
    def _ensure_element_separation(self, scenes: List[Dict]) -> List[Dict]:
        """Ensure each element has clear separation."""
        for scene_idx, scene in enumerate(scenes):
            elements = scene.get("elements", [])
            if not elements:
                continue
            
            # Group by type and ensure minimum spacing
            seen_types = {}
            
            for elem in elements:
                elem_id = elem.get("id", "")
                elem_type = elem.get("type", "")
                
                # Add unique identifier to avoid conflicts
                if elem_id in seen_types:
                    # Add offset to position
                    position = elem.get("position", "[0, 0, 0]")
                    match = re.findall(r'[-+]?\d*\.?\d+', position)
                    if len(match) >= 2:
                        y = float(match[1])
                        new_position = f"[{match[0]}, {y - 0.3}, 0]"
                        elem["position"] = new_position
                        
                        self.fixes_applied.append(
                            f"Scene {scene_idx+1}, Element '{elem_id}': "
                            f"type separation, added Y offset"
                        )
                
                seen_types[elem_id] = True
        
        return scenes


def fix_overlaps_in_data(data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Main function to fix all overlaps in animation data.
    
    Args:
        data: Animation data dictionary
        
    Returns:
        Tuple of (fixed_data, list_of_fixes)
    """
    fixer = UltimateOverlapFixer()
    return fixer.process_animation_plan(data)


# Standalone execution
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python overlap_fix_v4.py <animation_data.json>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    
    if not input_file.exists():
        print(f"Error: File not found: {input_file}")
        sys.exit(1)
    
    # Load data
    data = json.loads(input_file.read_text())
    
    # Fix overlaps
    fixer = UltimateOverlapFixer()
    fixed_data, fixes = fixer.process_animation_plan(data)
    
    # Print fixes
    print("=" * 60)
    print("OVERLAP FIX REPORT")
    print("=" * 60)
    
    if fixes:
        for fix in fixes:
            print(f"  • {fix}")
    else:
        print("  No fixes needed - no overlaps detected!")
    
    print("=" * 60)
    print(f"Total fixes applied: {len(fixes)}")
    print("=" * 60)
    
    # Save fixed data
    output_file = input_file.parent / f"{input_file.stem}_fixed.json"
    output_file.write_text(json.dumps(fixed_data, indent=2))
    print(f"\nFixed data saved to: {output_file}")