"""
Optimized Overlap Resolution - Comprehensive algorithm fix and optimization

This module fixes:
1. Timeline overlap bugs in element sequencing
2. Spatial overlap issues in element positioning  
3. Scene duration calculation errors
4. Element ordering issues
5. Performance optimization for large scenes

Author: Phiversity Team - Optimized for Production
"""

import json
import re
from typing import Dict, List, Any, Tuple, Optional
from pathlib import Path


class OptimizedOverlapFixer:
    """
    Optimized fixer with improved algorithms for guaranteed no overlaps.
    """
    
    # Constants for element positioning
    Y_POSITIONS = {
        "mathtex": 2.5,
        "latex": 2.5,
        "equation": 2.5,
        "code": 1.5,
        "text": 0.5,
        "output": -0.3,
        "default": 0.0
    }
    
    X_POSITIONS = {
        "left": -3.0,
        "center": 0.0,
        "right": 3.0,
        "default": 0.0
    }
    
    # Minimum durations per element type
    MIN_DURATIONS = {
        "mathtex": 2.0,
        "latex": 2.0,
        "code": 1.5,
        "text": 1.0,
        "output": 0.8,
        "default": 1.0
    }
    
    def __init__(self):
        self.fixes: List[str] = []
        
    def process(self, data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Process animation data with optimized algorithms.
        """
        self.fixes = []
        
        animation_plan = data.get("animation_plan", {})
        if not animation_plan:
            return data, self.fixes
            
        scenes = animation_plan.get("scenes", [])
        if not scenes:
            return data, self.fixes
            
        # Process each scene
        for scene_idx, scene in enumerate(scenes):
            scene = self._process_scene(scene, scene_idx)
            scenes[scene_idx] = scene
        
        # Calculate scene durations after processing
        scenes = self._calculate_scene_durations(scenes)
        
        animation_plan["scenes"] = scenes
        data["animation_plan"] = animation_plan
        
        return data, self.fixes
    
    def _process_scene(self, scene: Dict[str, Any], scene_idx: int) -> Dict[str, Any]:
        """Process a single scene with overlap fixes."""
        elements = scene.get("elements", [])
        
        if not elements:
            return scene
            
        # Step 1: Normalize element data
        elements = self._normalize_elements(elements)
        
        # Step 2: Sort by timing (start time)
        elements = self._sort_by_timing(elements)
        
        # Step 3: Fix timeline overlaps
        elements = self._fix_timeline(elements, scene_idx)
        
        # Step 4: Fix spatial overlaps (positioning)
        elements = self._fix_spatial(elements, scene_idx)
        
        # Apply fixed elements
        scene["elements"] = elements
        return scene
    
    def _normalize_elements(self, elements: List[Dict]) -> List[Dict]:
        """Normalize element data structures."""
        for elem in elements:
            # Ensure timing exists
            if "timing" not in elem:
                elem["timing"] = {}
            
            timing = elem["timing"]
            
            # Ensure required timing fields
            if "start" not in timing:
                timing["start"] = 0.0
            if "duration_in" not in timing:
                elem_type = elem.get("type", "").lower()
                timing["duration_in"] = self.MIN_DURATIONS.get(elem_type, 1.0)
            
            # Ensure position exists
            if "position" not in elem:
                elem["position"] = "[0, 0, 0]"
        
        return elements
    
    def _sort_by_timing(self, elements: List[Dict]) -> List[Dict]:
        """Sort elements by start time for proper sequencing."""
        return sorted(elements, key=lambda e: e.get("timing", {}).get("start", 0))
    
    def _fix_timeline(self, elements: List[Dict], scene_idx: int) -> List[Dict]:
        """Fix timeline overlaps with improved algorithm."""
        if not elements:
            return elements
            
        # Track current time position
        current_time = 0.0
        
        for i, elem in enumerate(elements):
            timing = elem.get("timing", {})
            elem_id = elem.get("id", f"element_{i}")
            elem_type = elem.get("type", "default").lower()
            
            # Get element duration (minimum based on type)
            min_duration = self.MIN_DURATIONS.get(elem_type, 1.0)
            duration = max(timing.get("duration_in", 1.0), min_duration)
            
            # Get start time
            start = timing.get("start", 0)
            
            # FIXED ALGORITHM: Ensure element starts at or after current_time
            # This guarantees no overlap with previous elements
            if start < current_time:
                new_start = current_time
                timing["start"] = round(new_start, 2)
                
                self.fixes.append(
                    f"Scene {scene_idx+1}, {elem_id}: timeline fixed "
                    f"(start {start:.2f}s → {new_start:.2f}s)"
                )
            
            # Update current_time to end of this element
            # Add small buffer (0.1s) between elements
            current_time = timing["start"] + duration + 0.1
            
            # Update duration if too short
            if timing.get("duration_in", 0) < min_duration:
                timing["duration_in"] = min_duration
                elem["timing"] = timing
                
                self.fixes.append(
                    f"Scene {scene_idx+1}, {elem_id}: duration fixed "
                    f"({timing.get('duration_in', 0):.2f}s to {min_duration:.2f}s)"
                )
        
        return elements
    
    def _fix_spatial(self, elements: List[Dict], scene_idx: int) -> List[Dict]:
        """Fix spatial overlaps with improved positioning algorithm."""
        if not elements:
            return elements
            
        # Group elements by type for better positioning
        type_groups: Dict[str, List[Dict]] = {}
        
        for elem in elements:
            elem_type = elem.get("type", "default").lower()
            if elem_type not in type_groups:
                type_groups[elem_type] = []
            type_groups[elem_type].append(elem)
        
        # Position elements based on type
        # MathTex/Latex at top, Code in middle, Text at bottom
        y_pos = 2.5  # Start from top
        
        for elem_type in ["mathtex", "latex", "equation", "code", "text", "output", "default"]:
            if elem_type not in type_groups:
                continue
                
            for i, elem in enumerate(type_groups[elem_type]):
                # Get current position
                position = elem.get("position", "[0, 0, 0]")
                match = re.findall(r'[-+]?\d*\.?\d+', position)
                
                if len(match) >= 2:
                    # Keep X position, update Y position
                    x = float(match[0])
                    new_position = f"[{x}, {y_pos}, 0]"
                    
                    if elem.get("position") != new_position:
                        elem["position"] = new_position
                        elem_id = elem.get("id", f"element_{i}")
                        self.fixes.append(
                            f"Scene {scene_idx+1}, {elem_id}: position fixed "
                            f"(Y: {float(match[1]):.2f} to {y_pos:.2f})"
                        )
                
                # Move Y position down for next element of same type
                y_pos -= self._get_element_height(elem)
        
        return elements
    
    def _get_element_height(self, elem: Dict) -> float:
        """Calculate element height for spacing."""
        elem_type = elem.get("type", "default").lower()
        content = elem.get("content", "")
        
        if "code" in elem_type:
            # Code height based on lines
            lines = len(content.split("\n"))
            return max(0.8, lines * 0.15)
        elif "mathtex" in elem_type or "latex" in elem_type:
            return 0.7
        else:
            return 0.5
    
    def _calculate_scene_durations(self, scenes: List[Dict]) -> List[Dict]:
        """Calculate accurate scene durations based on element timings."""
        for scene_idx, scene in enumerate(scenes):
            elements = scene.get("elements", [])
            
            if not elements:
                scene["duration"] = 3.0
                continue
                
            # Find the latest end time of any element
            max_end = 0.0
            
            for elem in elements:
                timing = elem.get("timing", {})
                start = timing.get("start", 0)
                duration = timing.get("duration_in", 1.0)
                end = start + duration
                
                if end > max_end:
                    max_end = end
            
            # Add buffer at end of scene
            scene_duration = max_end + 1.0
            
            if scene.get("duration", 0) != scene_duration:
                self.fixes.append(
                    f"Scene {scene_idx+1}: duration updated "
                    f"({scene.get('duration', 0):.2f}s to {scene_duration:.2f}s)"
                )
            
            scene["duration"] = scene_duration
        
        return scenes


def optimize_and_fix(data: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
    """
    Main function to optimize and fix all issues.
    
    Args:
        data: Animation data dictionary
        
    Returns:
        Tuple of (fixed_data, list_of_fixes)
    """
    fixer = OptimizedOverlapFixer()
    return fixer.process(data)