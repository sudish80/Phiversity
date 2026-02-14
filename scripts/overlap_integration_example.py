#!/usr/bin/env python3
"""
OVERLAP RESOLUTION INTEGRATION EXAMPLE
How to integrate the algorithm into Phiversity's Manim pipeline

This file demonstrates:
1. How to extract element information from animation plans
2. How to run the overlap solver
3. How to apply resolved positions back to Manim scenes
"""

import json
import sys
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime

# Handle imports for both direct execution and module import
try:
    from scripts.overlap_resolution import (
        OverlapSolver,
        create_layout_element,
        ElementType,
        serialize_layout
    )
except ModuleNotFoundError:
    # When run directly, add parent directory to path
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from scripts.overlap_resolution import (
        OverlapSolver,
        create_layout_element,
        ElementType,
        serialize_layout
    )


class ManimOverlapIntegrator:
    """
    Integrates overlap resolution with Manim scene generation
    """
    
    def __init__(self):
        self.solver = OverlapSolver()
        self.element_cache = {}
    
    # ========== STEP 1: EXTRACT ELEMENTS FROM ANIMATION PLAN ==========
    def extract_elements_from_plan(
        self,
        animation_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract element positions and bounds from animation plan JSON
        
        Input structure:
        {
            "scenes": [{
                "elements": [{
                    "id": "text_title",
                    "type": "text",
                    "content": "...",
                    "position": [0,0],
                    "size": [1.0, 0.5],
                    "locked": false
                }, ...],
                ...
            }],
            ...
        }
        """
        elements_dict = {}
        
        for scene in animation_plan.get("scenes", []):
            print(f"\n[EXTRACT] Processing scene: {scene.get('id', 'unknown')}")
            
            for element in scene.get("elements", []):
                elem_id = element.get("id", f"elem_{len(elements_dict)}")
                elem_type = element.get("type", "text")
                
                # STEP 1.1: Get position and size
                position = element.get("position", [0, 0])
                size = element.get("size", [1.0, 0.5])
                
                # STEP 1.2: Calculate bounding box
                x_center, y_center = position[0], position[1]
                width, height = size[0], size[1]
                
                x_min = x_center - width / 2
                y_min = y_center - height / 2
                x_max = x_center + width / 2
                y_max = y_center + height / 2
                
                # STEP 1.3: Determine priority based on type
                priority_map = {
                    "graph": 10,
                    "figure": 15,
                    "equation": 20,
                    "legend": 25,
                    "label": 30,
                    "text": 35,
                    "arrow": 40,
                }
                priority = priority_map.get(elem_type, 25)
                
                # STEP 1.4: Get constraints
                locked = element.get("locked", False)
                dependencies = element.get("dependencies", [])
                
                # STEP 1.5: Store element information
                elements_dict[elem_id] = {
                    "type": elem_type,
                    "position": position,
                    "size": size,
                    "bbox": [x_min, y_min, x_max, y_max],
                    "priority": priority,
                    "locked": locked,
                    "dependencies": dependencies,
                    "content": element.get("content", ""),
                    "manim_params": element.get("manim_params", {})
                }
                
                print(f"  [+] {elem_id}: {elem_type} at ({x_center:.2f}, {y_center:.2f})")
        
        print(f"\n[EXTRACT] Total elements: {len(elements_dict)}")
        return elements_dict
    
    # ========== STEP 2: DETECT OVERLAPS BEFORE SOLVING ==========
    def detect_overlaps_in_plan(
        self,
        elements_dict: Dict[str, Any]
    ) -> List[Tuple[str, str, float]]:
        """
        Detect which elements are overlapping BEFORE solving
        
        Returns: List of (elem_id_1, elem_id_2, overlap_area)
        """
        from scripts.overlap_resolution import CollisionDetector, BoundingBox
        
        print("\n[DETECT] Analyzing overlaps...")
        
        detector = CollisionDetector(grid_size=0.5)
        
        # Convert to LayoutElements temporarily
        temp_elements = {}
        for elem_id, elem_data in elements_dict.items():
            bbox_data = elem_data["bbox"]
            temp_elements[elem_id] = create_layout_element(
                elem_id,
                elem_data["type"],
                bbox_data[0], bbox_data[1],
                bbox_data[2], bbox_data[3],
                priority=elem_data["priority"],
                locked=elem_data["locked"],
                dependencies=elem_data["dependencies"]
            )
        
        # Detect collisions
        collisions = detector.detect_collisions(temp_elements)
        
        if collisions:
            print(f"[DETECT] Found {len(collisions)} overlapping pairs:")
            total_overlap = 0
            for id1, id2, area in collisions:
                print(f"  - {id1} <-> {id2}: {area:.4f} sq units")
                total_overlap += area
            print(f"[DETECT] Total overlap area: {total_overlap:.4f}")
        else:
            print("[DETECT] No overlaps found!")
        
        return collisions
    
    # ========== STEP 3: SOLVE OVERLAPS ==========
    def solve_overlaps(
        self,
        elements_dict: Dict[str, Any],
        strategy: str = None
    ) -> Dict[str, Tuple[float, float]]:
        """
        Solve overlapping elements using the full algorithm
        
        Args:
            elements_dict: Elements from step 1
            strategy: "grid", "hierarchical", "force_directed", "radial", or None for auto
        
        Returns:
            Dict mapping element_id -> (x, y) resolved position
        """
        print("\n[SOLVE] Preparing overlap resolution...")
        
        # STEP 3.1: Convert to LayoutElements
        layout_elements = {}
        for elem_id, elem_data in elements_dict.items():
            bbox = elem_data["bbox"]
            layout_elements[elem_id] = create_layout_element(
                element_id=elem_id,
                element_type=elem_data["type"],
                x_min=bbox[0],
                y_min=bbox[1],
                x_max=bbox[2],
                y_max=bbox[3],
                priority=elem_data["priority"],
                locked=elem_data["locked"],
                dependencies=elem_data["dependencies"]
            )
        
        # STEP 3.2: Run solver
        from scripts.overlap_resolution import LayoutStrategy
        
        layout_strategy = None
        if strategy:
            strategy_map = {
                "grid": LayoutStrategy.GRID,
                "hierarchical": LayoutStrategy.HIERARCHICAL,
                "force_directed": LayoutStrategy.FORCE_DIRECTED,
                "radial": LayoutStrategy.RADIAL,
                "optimized": LayoutStrategy.OPTIMIZED,
            }
            layout_strategy = strategy_map.get(strategy.lower())
        
        resolved_positions = self.solver.solve(
            layout_elements,
            strategy=layout_strategy,
            verbose=True
        )
        
        return resolved_positions
    
    # ========== STEP 4: VALIDATE SOLUTION ==========
    def validate_solution(
        self,
        elements_dict: Dict[str, Any],
        resolved_positions: Dict[str, Tuple[float, float]]
    ) -> Dict[str, Any]:
        """
        Validate that the solution actually fixed overlaps
        
        Returns: Validation report
        """
        from scripts.overlap_resolution import CollisionDetector, BoundingBox
        
        print("\n[VALIDATE] Checking solution...")
        
        detector = CollisionDetector(grid_size=0.5)
        
        # Create temporary elements at resolved positions
        temp_elements = {}
        for elem_id, elem_data in elements_dict.items():
            if elem_id not in resolved_positions:
                continue
            
            old_bbox = elem_data["bbox"]
            old_center = (
                (old_bbox[0] + old_bbox[2]) / 2,
                (old_bbox[1] + old_bbox[3]) / 2
            )
            
            new_center = resolved_positions[elem_id]
            dx = new_center[0] - old_center[0]
            dy = new_center[1] - old_center[1]
            
            new_bbox = BoundingBox(
                old_bbox[0] + dx,
                old_bbox[1] + dy,
                old_bbox[2] + dx,
                old_bbox[3] + dy
            )
            
            temp_elements[elem_id] = create_layout_element(
                elem_id,
                elem_data["type"],
                new_bbox.x_min, new_bbox.y_min,
                new_bbox.x_max, new_bbox.y_max,
                priority=elem_data["priority"],
                locked=elem_data["locked"],
                dependencies=elem_data["dependencies"]
            )
        
        # Check final collisions
        final_collisions = detector.detect_collisions(temp_elements)
        
        report = {
            "valid": len(final_collisions) == 0,
            "remaining_overlaps": len(final_collisions),
            "remaining_area": sum(area for _, _, area in final_collisions),
            "collisions": final_collisions
        }
        
        if report["valid"]:
            print(f"[VALIDATE] Solution is valid! No overlaps remain.")
        else:
            print(f"[VALIDATE] WARNING: {len(final_collisions)} overlaps remain.")
            print(f"[VALIDATE] Total area: {report['remaining_area']:.4f}")
        
        return report
    
    # ========== STEP 5: APPLY SOLUTION TO MANIM SCENE ==========
    def apply_to_manim(
        self,
        elements_dict: Dict[str, Any],
        resolved_positions: Dict[str, Tuple[float, float]],
        animation_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update animation plan with resolved positions
        
        Modifies animation_plan in-place and returns it
        """
        print("\n[APPLY] Updating animation plan with resolved positions...")
        
        updates_count = 0
        
        for scene in animation_plan.get("scenes", []):
            for element in scene.get("elements", []):
                elem_id = element.get("id")
                
                if elem_id in resolved_positions:
                    old_pos = element.get("position", [0, 0])
                    new_pos = resolved_positions[elem_id]
                    
                    # STEP 5.1: Update position
                    element["position"] = list(new_pos)
                    element["resolved"] = True
                    updates_count += 1
                    
                    # STEP 5.2: Log change
                    distance = np.sqrt(
                        (new_pos[0] - old_pos[0])**2 +
                        (new_pos[1] - old_pos[1])**2
                    )
                    
                    if distance > 0.01:
                        print(f"  - {elem_id}: ({old_pos[0]:.2f}, {old_pos[1]:.2f}) " +
                              f"-> ({new_pos[0]:.2f}, {new_pos[1]:.2f}) [d={distance:.2f}]")
        
        print(f"\n[APPLY] Updated {updates_count} positions")
        
        return animation_plan
    
    # ========== STEP 6: SAVE RESOLUTION REPORT ==========
    def save_resolution_report(
        self,
        elements_dict: Dict[str, Any],
        collisions_before: List[Tuple[str, str, float]],
        validation_report: Dict[str, Any],
        resolved_positions: Dict[str, Tuple[float, float]],
        output_path: Path
    ) -> None:
        """
        Save detailed report of overlap resolution process
        """
        print(f"\n[SAVE] Writing resolution report to {output_path}...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_elements": len(elements_dict),
                "overlaps_before": len(collisions_before),
                "overlap_area_before": sum(a for _, _, a in collisions_before),
                "overlaps_after": validation_report["remaining_overlaps"],
                "overlap_area_after": validation_report["remaining_area"],
                "success": validation_report["valid"]
            },
            "elements": elements_dict,
            "resolved_positions": {
                k: {"x": float(v[0]), "y": float(v[1])}
                for k, v in resolved_positions.items()
            },
            "validation": validation_report
        }
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"[SAVE] ✓ Report saved")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_usage():
    """
    Complete example showing all steps
    """
    print("\n" + "="*70)
    print("OVERLAP RESOLUTION - COMPLETE EXAMPLE")
    print("="*70)
    
    # Example animation plan with overlapping elements
    animation_plan = {
        "id": "example_scene",
        "scenes": [{
            "id": "scene_1",
            "elements": [
                {
                    "id": "title",
                    "type": "text",
                    "content": "Angular Momentum",
                    "position": [4.0, 4.0],
                    "size": [2.0, 0.4],
                    "locked": True
                },
                {
                    "id": "graph_1",
                    "type": "graph",
                    "content": "L = I × ω",
                    "position": [2.0, 2.0],
                    "size": [2.0, 2.0],
                    "priority": 10
                },
                {
                    "id": "graph_2",
                    "type": "graph",
                    "content": "Conservation",
                    "position": [6.0, 2.0],
                    "size": [2.0, 2.0],
                    "priority": 10
                },
                {
                    "id": "label_1",
                    "type": "label",
                    "content": "Initial State",
                    "position": [1.5, 1.0],  # Overlaps with graph_1
                    "size": [1.0, 0.3],
                    "dependencies": ["graph_1"]
                },
                {
                    "id": "label_2",
                    "type": "label",
                    "content": "Final State",
                    "position": [6.5, 1.0],  # Overlaps with graph_2
                    "size": [1.0, 0.3],
                    "dependencies": ["graph_2"]
                }
            ]
        }]
    }
    
    # STEP 1: Create integrator
    integrator = ManimOverlapIntegrator()
    
    # STEP 2: Extract elements
    elements_dict = integrator.extract_elements_from_plan(animation_plan)
    
    # STEP 3: Detect overlaps before solving
    collisions_before = integrator.detect_overlaps_in_plan(elements_dict)
    
    # STEP 4: Solve overlaps
    resolved_positions = integrator.solve_overlaps(elements_dict, strategy="optimized")
    
    # STEP 5: Validate solution
    validation = integrator.validate_solution(elements_dict, resolved_positions)
    
    # STEP 6: Apply to animation plan
    updated_plan = integrator.apply_to_manim(
        elements_dict,
        resolved_positions,
        animation_plan
    )
    
    # STEP 7: Save report
    integrator.save_resolution_report(
        elements_dict,
        collisions_before,
        validation,
        resolved_positions,
        Path("media/resolution_report.json")
    )
    
    print("\n" + "="*70)
    print("[OK] EXAMPLE COMPLETE")
    print("="*70 + "\n")
    
    return updated_plan


if __name__ == "__main__":
    example_usage()
