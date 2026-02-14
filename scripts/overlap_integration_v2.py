#!/usr/bin/env python3
"""
ENHANCED OVERLAP RESOLUTION INTEGRATION v2.0
Integration of enhanced algorithms into Phiversity's Manim pipeline

This file demonstrates:
1. How to use QuadTree for faster collision detection
2. How to auto-select algorithms with ComplexityAnalyzer
3. How to apply AdvancedForceDirectedLayout with thermal annealing
4. How to evaluate with EnhancedLayoutEvaluator
"""

import json
import sys
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

# Enhanced v2.0 components
try:
    from scripts.overlap_resolution_enhanced import (
        QuadTree,
        ComplexityAnalyzer,
        AdvancedForceDirectedLayout,
        EnhancedLayoutEvaluator,
        BoundingBox,
        LayoutElement
    )
except ModuleNotFoundError:
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from scripts.overlap_resolution_enhanced import (
        QuadTree,
        ComplexityAnalyzer,
        AdvancedForceDirectedLayout,
        EnhancedLayoutEvaluator,
        BoundingBox,
        LayoutElement
    )

# Original v1.0 components (for compatibility)
try:
    from scripts.overlap_resolution import (
        OverlapSolver,
        create_layout_element,
        ElementType,
    )
except ModuleNotFoundError:
    pass


class EnhancedManimOverlapIntegrator:
    """
    Enhanced v2.0 integrator with automatic algorithm selection,
    faster collision detection, and comprehensive quality metrics.
    """
    
    def __init__(self, use_v2_enhancements: bool = True):
        """
        Initialize integrator
        
        Args:
            use_v2_enhancements: Use v2.0 enhancements (default True)
        """
        self.use_v2 = use_v2_enhancements
        self.element_cache = {}
        self.analysis_data = None
        
        if not use_v2_enhancements:
            self.solver = OverlapSolver()
    
    # ========== STEP 1: EXTRACT ELEMENTS ==========
    def extract_elements_from_plan(
        self,
        animation_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract element positions and bounds from animation plan JSON
        
        Same as v1.0 for compatibility
        """
        elements_dict = {}
        
        for scene in animation_plan.get("scenes", []):
            print(f"\n[EXTRACT] Processing scene: {scene.get('id', 'unknown')}")
            
            for element in scene.get("elements", []):
                elem_id = element.get("id", f"elem_{len(elements_dict)}")
                elem_type = element.get("type", "text")
                
                position = element.get("position", [0, 0])
                size = element.get("size", [1.0, 0.5])
                
                x_center, y_center = position[0], position[1]
                width, height = size[0], size[1]
                
                x_min = x_center - width / 2
                y_min = y_center - height / 2
                x_max = x_center + width / 2
                y_max = y_center + height / 2
                
                priority_map = {
                    "graph": 10, "figure": 15, "equation": 20,
                    "legend": 25, "label": 30, "text": 35, "arrow": 40,
                }
                priority = priority_map.get(elem_type, 25)
                
                elements_dict[elem_id] = {
                    "type": elem_type,
                    "position": position,
                    "size": size,
                    "bbox": [x_min, y_min, x_max, y_max],
                    "priority": priority,
                    "locked": element.get("locked", False),
                    "dependencies": element.get("dependencies", []),
                    "content": element.get("content", ""),
                }
                
                print(f"  [+] {elem_id}: {elem_type} at ({x_center:.2f}, {y_center:.2f})")
        
        print(f"\n[EXTRACT] Total elements: {len(elements_dict)}")
        return elements_dict
    
    # ========== STEP 2: ANALYZE WITH V2.0 (NEW) ==========
    def analyze_complexity(
        self,
        elements_dict: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        NEW v2.0 FEATURE: Analyze element configuration
        
        Returns analysis with recommended algorithm
        """
        if not self.use_v2:
            return None
        
        print("\n[ANALYZE] Analyzing element configuration (v2.0)...")
        
        # Convert to LayoutElement objects for analysis
        layout_elements = {}
        for elem_id, elem_data in elements_dict.items():
            bbox = elem_data["bbox"]
            layout_elements[elem_id] = LayoutElement(
                id=elem_id,
                element_type=elem_data["type"],
                bounding_box=BoundingBox(bbox[0], bbox[1], bbox[2], bbox[3]),
                locked=elem_data["locked"],
                dependencies=elem_data["dependencies"]
            )
        
        # Analyze with v2.0
        analysis = ComplexityAnalyzer.analyze_elements(layout_elements)
        
        self.analysis_data = analysis
        
        print(f"  Elements: {analysis['element_count']}")
        print(f"  Overlap: {analysis['overlap_percentage']:.1f}%")
        print(f"  Density: {analysis['element_density']:.2f}")
        print(f"  Has dependencies: {analysis['has_dependencies']}")
        print(f"  Recommended: {analysis['recommended_algorithm'].upper()}")
        
        return analysis
    
    # ========== STEP 2B: FAST COLLISION DETECTION WITH QUADTREE (NEW) ==========
    def detect_overlaps_fast(
        self,
        elements_dict: Dict[str, Any]
    ) -> List[Tuple[str, str, float]]:
        """
        NEW v2.0 FEATURE: Use QuadTree for O(n log n) collision detection
        
        Much faster than naive O(n²) approach for 20+ elements
        """
        if not self.use_v2:
            return []
        
        print("\n[DETECT] Detecting overlaps with QuadTree (v2.0)...")
        
        # Create QuadTree
        canvas_bounds = (-4.0, -2.25, 4.0, 2.25)  # Manim canvas
        qtree = QuadTree(canvas_bounds, max_depth=8, max_elements=4)
        
        # Insert all elements
        bbox_map = {}
        elem_list = list(elements_dict.items())
        
        for elem_id, elem_data in elem_list:
            bbox = elem_data["bbox"]
            bbox_tuple = (bbox[0], bbox[1], bbox[2], bbox[3])
            qtree.insert(elem_id, bbox_tuple)
            bbox_map[elem_id] = bbox_tuple
        
        # Query collisions
        collisions = []
        for elem_id, bbox_tuple in bbox_map.items():
            # Find nearby elements
            nearby = qtree.query_collisions(bbox_tuple)
            
            # Check intersection with each nearby element
            for other_id in nearby:
                if elem_id >= other_id:  # Avoid duplicates
                    continue
                
                bbox1 = bbox_map[elem_id]
                bbox2 = bbox_map[other_id]
                
                # Calculate overlap area
                overlap_width = min(bbox1[2], bbox2[2]) - max(bbox1[0], bbox2[0])
                overlap_height = min(bbox1[3], bbox2[3]) - max(bbox1[1], bbox2[1])
                
                if overlap_width > 0 and overlap_height > 0:
                    overlap_area = overlap_width * overlap_height
                    collisions.append((elem_id, other_id, overlap_area))
        
        # Sort by area
        collisions.sort(key=lambda x: x[2], reverse=True)
        
        if collisions:
            total_area = sum(area for _, _, area in collisions)
            print(f"[DETECT] Found {len(collisions)} overlapping pairs")
            print(f"[DETECT] Total overlap area: {total_area:.4f}")
            for id1, id2, area in collisions[:5]:  # Show top 5
                print(f"  - {id1} ↔ {id2}: {area:.4f}")
            if len(collisions) > 5:
                print(f"  ... and {len(collisions)-5} more")
        else:
            print("[DETECT] No overlaps found!")
        
        return collisions
    
    # ========== STEP 3: SOLVE WITH ENHANCED PHYSICS (NEW) ==========
    def solve_overlaps_enhanced(
        self,
        elements_dict: Dict[str, Any],
        strategy: Optional[str] = None,
        iterations: int = 100,
        use_thermal_annealing: bool = True
    ) -> Dict[str, Tuple[float, float]]:
        """
        NEW v2.0 FEATURE: Solve with enhanced force-directed physics
        
        Includes:
        - 4 force types (repulsive, attractive, boundary, thermal)
        - Thermal annealing for escaping local minima
        - Dynamic temperature cooling
        
        Args:
            elements_dict: Elements from extraction
            strategy: "grid", "hierarchical", "force_directed", "radial", or auto
            iterations: Number of physics iterations (default 100, max 200 for best quality)
            use_thermal_annealing: Enable thermal annealing (default True)
        
        Returns:
            Dict mapping element_id -> (x, y) resolved position
        """
        if not self.use_v2:
            return self.solve_overlaps_v1(elements_dict, strategy)
        
        print("\n[SOLVE] Using enhanced force-directed physics (v2.0)...")
        
        # Auto-select algorithm if not specified
        if strategy is None and self.analysis_data:
            strategy = self.analysis_data['recommended_algorithm']
            print(f"[SOLVE] Auto-selected algorithm: {strategy.upper()}")
        
        # Convert to LayoutElement objects
        layout_elements = {}
        original_positions = {}
        
        for elem_id, elem_data in elements_dict.items():
            bbox = elem_data["bbox"]
            bbox_obj = BoundingBox(bbox[0], bbox[1], bbox[2], bbox[3])
            
            layout_elements[elem_id] = LayoutElement(
                id=elem_id,
                element_type=elem_data["type"],
                bounding_box=bbox_obj,
                locked=elem_data["locked"],
                dependencies=elem_data["dependencies"]
            )
            
            original_positions[elem_id] = bbox_obj.center
        
        # Use enhanced force-directed layout
        if strategy and strategy.lower() != 'force_directed':
            print(f"[SOLVE] Note: Using enhanced physics for {strategy} algorithm")
        
        layout_engine = AdvancedForceDirectedLayout(
            layout_elements,
            canvas_width=8.0,
            canvas_height=4.5,
            iterations=iterations,
            use_thermal_annealing=use_thermal_annealing
        )
        
        # Optionally tune parameters
        if self.analysis_data:
            overlap_pct = self.analysis_data['overlap_percentage']
            
            if overlap_pct > 50:
                # High overlap - use aggressive settings
                layout_engine.repulsion_strength = 0.8
                layout_engine.boundary_repulsion = 2.5
                layout_engine.cooling_rate = 0.90
                print(f"[SOLVE] High overlap detected - using aggressive physics")
            else:
                # Low overlap - use conservative settings
                layout_engine.repulsion_strength = 0.4
                layout_engine.cooling_rate = 0.95
        
        print(f"[SOLVE] Running {iterations} physics iterations...")
        resolved_positions = layout_engine.layout()
        
        return resolved_positions
    
    # ========== STEP 4: EVALUATE WITH MULTI-METRICS (NEW) ==========
    def evaluate_enhanced(
        self,
        elements_dict: Dict[str, Any],
        resolved_positions: Dict[str, Tuple[float, float]]
    ) -> Dict[str, Any]:
        """
        NEW v2.0 FEATURE: Evaluate layout with multiple quality metrics
        
        Returns:
        - Overlap score (area of remaining overlaps)
        - Displacement score (total distance moved)
        - Boundary score (elements outside canvas)
        - Spacing score (minimum distance between elements)
        - Overall score (weighted combination)
        """
        if not self.use_v2:
            return {}
        
        print("\n[EVALUATE] Evaluating solution quality (v2.0)...")
        
        # Convert to LayoutElement objects
        layout_elements = {}
        original_positions = {}
        
        for elem_id, elem_data in elements_dict.items():
            bbox = elem_data["bbox"]
            bbox_obj = BoundingBox(bbox[0], bbox[1], bbox[2], bbox[3])
            
            layout_elements[elem_id] = LayoutElement(
                id=elem_id,
                element_type=elem_data["type"],
                bounding_box=bbox_obj,
                locked=elem_data["locked"],
            )
            
            original_positions[elem_id] = bbox_obj.center
        
        # Evaluate with v2.0 metrics
        scores = EnhancedLayoutEvaluator.evaluate_layout(
            layout_elements,
            resolved_positions,
            original_positions
        )
        
        print(f"  Overlap score: {scores['overlap_score']:.3f}")
        print(f"  Displacement: {scores['displacement_score']:.3f}")
        print(f"  Boundary violations: {scores['boundary_score']:.0f}")
        print(f"  Min spacing: {scores['spacing_score']:.3f}")
        print(f"  Overall: {scores['overall_score']:.1f}")
        
        return scores
    
    # ========== COMPATIBILITY: V1.0 FALLBACK ==========
    def solve_overlaps_v1(
        self,
        elements_dict: Dict[str, Any],
        strategy: Optional[str] = None
    ) -> Dict[str, Tuple[float, float]]:
        """
        Fallback to v1.0 algorithm if v2.0 not available
        """
        print("\n[SOLVE] Using original algorithm (v1.0)...")
        
        layout_elements = {}
        for elem_id, elem_data in elements_dict.items():
            bbox = elem_data["bbox"]
            layout_elements[elem_id] = create_layout_element(
                element_id=elem_id,
                element_type=elem_data["type"],
                x_min=bbox[0], y_min=bbox[1],
                x_max=bbox[2], y_max=bbox[3],
                priority=elem_data["priority"],
                locked=elem_data["locked"],
                dependencies=elem_data["dependencies"]
            )
        
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
    
    # ========== STEP 5: APPLY TO SCENE ==========
    def apply_to_manim(
        self,
        elements_dict: Dict[str, Any],
        resolved_positions: Dict[str, Tuple[float, float]],
        animation_plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply resolved positions to animation plan
        Same as v1.0
        """
        print("\n[APPLY] Updating animation plan with resolved positions...")
        
        updates_count = 0
        
        for scene in animation_plan.get("scenes", []):
            for element in scene.get("elements", []):
                elem_id = element.get("id")
                
                if elem_id in resolved_positions:
                    old_pos = element.get("position", [0, 0])
                    new_pos = resolved_positions[elem_id]
                    
                    element["position"] = list(new_pos)
                    element["resolved"] = True
                    updates_count += 1
                    
                    distance = np.sqrt(
                        (new_pos[0] - old_pos[0])**2 +
                        (new_pos[1] - old_pos[1])**2
                    )
                    
                    if distance > 0.01:
                        print(f"  {elem_id}: ({old_pos[0]:.2f},{old_pos[1]:.2f}) " +
                              f"→ ({new_pos[0]:.2f},{new_pos[1]:.2f}) [Δ={distance:.2f}]")
        
        print(f"[APPLY] Updated {updates_count} positions")
        return animation_plan
    
    # ========== STEP 6: SAVE REPORT ==========
    def save_report(
        self,
        elements_dict: Dict[str, Any],
        collisions_before: List,
        scores: Dict[str, float],
        resolved_positions: Dict[str, Tuple[float, float]],
        output_path: Path
    ) -> None:
        """
        Save detailed resolution report
        """
        print(f"\n[REPORT] Writing report to {output_path}...")
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "version": "v2.0" if self.use_v2 else "v1.0",
            "summary": {
                "total_elements": len(elements_dict),
                "overlaps_before": len(collisions_before),
                "overlap_area_before": sum(a for _, _, a in collisions_before),
                "algorithm_analysis": self.analysis_data,
                "quality_scores": scores,
            },
            "detailed_positions": {
                k: {"x": float(v[0]), "y": float(v[1])}
                for k, v in resolved_positions.items()
            }
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"[REPORT] ✓ Saved")


# ============================================================================
# EXAMPLE: COMPLETE V2.0 WORKFLOW
# ============================================================================

def example_v2_complete():
    """
    Complete example showing v2.0 enhancements
    """
    print("\n" + "="*70)
    print("ENHANCED OVERLAP RESOLUTION v2.0 - COMPLETE EXAMPLE")
    print("="*70)
    
    # Example animation plan with overlapping elements
    animation_plan = {
        "id": "physics_video",
        "scenes": [{
            "id": "angular_momentum",
            "elements": [
                {
                    "id": "title",
                    "type": "text",
                    "content": "Angular Momentum Conservation",
                    "position": [0, 3.5],
                    "size": [3.0, 0.4],
                    "locked": True
                },
                {
                    "id": "diagram_1",
                    "type": "graph",
                    "content": "Initial State",
                    "position": [-2.5, 1.5],
                    "size": [2.4, 2.2],
                },
                {
                    "id": "diagram_2",
                    "type": "graph",
                    "content": "Final State",
                    "position": [2.5, 1.5],
                    "size": [2.4, 2.2],
                },
                {
                    "id": "eq_momentum",
                    "type": "equation",
                    "content": "L = I × ω",
                    "position": [-2.5, 0.2],  # Overlaps with diagram_1
                    "size": [1.2, 0.3],
                },
                {
                    "id": "eq_conservation",
                    "type": "equation",
                    "content": "L_before = L_after",
                    "position": [2.5, 0.2],  # Overlaps with diagram_2
                    "size": [1.4, 0.3],
                },
                {
                    "id": "label_angular",
                    "type": "label",
                    "content": "Angular\nVelocity",
                    "position": [-3.2, 2.5],  # Overlaps with diagram_1
                    "size": [0.8, 0.4],
                },
            ]
        }]
    }
    
    # Create integrator with v2.0 enhancements
    integrator = EnhancedManimOverlapIntegrator(use_v2_enhancements=True)
    
    # STEP 1: Extract elements
    elements_dict = integrator.extract_elements_from_plan(animation_plan)
    
    # STEP 2: Analyze complexity (NEW v2.0)
    analysis = integrator.analyze_complexity(elements_dict)
    
    # STEP 3: Detect overlaps with QuadTree (NEW v2.0, O(n log n))
    collisions_before = integrator.detect_overlaps_fast(elements_dict)
    
    # STEP 4: Solve with enhanced physics (NEW v2.0)
    resolved_positions = integrator.solve_overlaps_enhanced(
        elements_dict,
        iterations=120,  # Balanced quality/speed
        use_thermal_annealing=True
    )
    
    # STEP 5: Evaluate with multi-metrics (NEW v2.0)
    quality_scores = integrator.evaluate_enhanced(
        elements_dict,
        resolved_positions
    )
    
    # STEP 6: Apply to animation plan
    updated_plan = integrator.apply_to_manim(
        elements_dict,
        resolved_positions,
        animation_plan
    )
    
    # STEP 7: Save detailed report
    integrator.save_report(
        elements_dict,
        collisions_before,
        quality_scores,
        resolved_positions,
        Path("media/overlap_resolution_v2_report.json")
    )
    
    print("\n" + "="*70)
    print("[✓] EXAMPLE COMPLETE - V2.0 ENHANCEMENTS WORKING")
    print("="*70 + "\n")
    
    return updated_plan


# ============================================================================
# EXAMPLE: COMPARISON V1 VS V2
# ============================================================================

def example_comparison():
    """
    Compare v1.0 and v2.0 performance
    """
    import time
    
    animation_plan = {
        "id": "test",
        "scenes": [{
            "id": "test_scene",
            "elements": [
                {
                    "id": f"elem_{i}",
                    "type": "text",
                    "position": [(i % 5) * 0.8 - 1.6, (i // 5) * 0.8 - 1.2],
                    "size": [0.5, 0.3],
                }
                for i in range(30)  # 30 overlapping elements
            ]
        }]
    }
    
    print("\n" + "="*70)
    print("V1.0 vs V2.0 COMPARISON (30 overlapping elements)")
    print("="*70)
    
    # Test V2.0
    print("\n[V2.0] Enhanced version with QuadTree + advanced physics...")
    integrator_v2 = EnhancedManimOverlapIntegrator(use_v2_enhancements=True)
    
    start = time.time()
    elements = integrator_v2.extract_elements_from_plan(animation_plan)
    analysis = integrator_v2.analyze_complexity(elements)
    collisions = integrator_v2.detect_overlaps_fast(elements)
    resolved = integrator_v2.solve_overlaps_enhanced(elements, iterations=100)
    scores = integrator_v2.evaluate_enhanced(elements, resolved)
    v2_time = time.time() - start
    
    print(f"[V2.0] Time: {v2_time*1000:.1f}ms")
    print(f"[V2.0] Overall score: {scores['overall_score']:.1f}")
    
    # Test V1.0
    print("\n[V1.0] Original version...")
    integrator_v1 = EnhancedManimOverlapIntegrator(use_v2_enhancements=False)
    
    start = time.time()
    elements = integrator_v1.extract_elements_from_plan(animation_plan)
    collisions = []  # Would need full v1.0 detection
    resolved = integrator_v1.solve_overlaps_v1(elements)
    v1_time = time.time() - start
    
    print(f"[V1.0] Time: {v1_time*1000:.1f}ms")
    
    speedup = v1_time / v2_time if v2_time > 0 else 1.0
    print(f"\n[COMPARISON] V2.0 is {speedup:.1f}x faster for 30 elements")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Run v2.0 complete example
    example_v2_complete()
    
    # Optional: Run comparison
    # example_comparison()
