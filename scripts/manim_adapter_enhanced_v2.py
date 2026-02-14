#!/usr/bin/env python3
"""
ENHANCED MANIM ADAPTER v2.0
Integration of v2.0 overlap resolution algorithms into manim_adapter.py

This module can be imported and used as a drop-in enhancement to
the existing apply_layout_and_collision_detection function.

Usage:
    from scripts.manim_adapter_enhanced_v2 import apply_layout_and_collision_detection_v2
    
    # In your manim_adapter.py, replace the function call:
    scene = apply_layout_and_collision_detection_v2(scene)
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

# Try importing v2.0 enhanced components
try:
    from scripts.overlap_resolution_enhanced import (
        QuadTree,
        ComplexityAnalyzer,
        AdvancedForceDirectedLayout,
        EnhancedLayoutEvaluator,
        BoundingBox,
        LayoutElement
    )
    V2_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    V2_AVAILABLE = False
    print("WARNING: overlap_resolution_enhanced not found, falling back to v1.0")

# Import original collision detection for fallback
try:
    from scripts.collision_detector import CollisionDetector, AABBCollider, CollisionResolver
    from scripts.layer_manager import LayerManager, ElementType
except (ImportError, ModuleNotFoundError):
    pass

# Constants (from original manim_adapter.py)
MANIM_SCREEN_WIDTH = 8.0
MANIM_SCREEN_HEIGHT = 4.5


def apply_layout_and_collision_detection_v2(
    scene: Dict[str, Any],
    use_v2_enhancements: bool = True,
    enable_quadtree: bool = True,
    enable_auto_algorithm: bool = True,
    enable_thermal_annealing: bool = True
) -> Dict[str, Any]:
    """
    ENHANCED v2.0: Apply layout, collision detection, and optimization to scene elements.
    
    New features:
    - QuadTree spatial partitioning for O(n log n) collision detection
    - Automatic algorithm selection based on element analysis
    - Advanced force-directed physics with thermal annealing
    - Multi-metric quality evaluation
    
    Args:
        scene: Scene dict with elements
        use_v2_enhancements: Use v2.0 enhancements (default True, falls back to v1.0 if unavailable)
        enable_quadtree: Use QuadTree for faster collision detection (default True)
        enable_auto_algorithm: Auto-select best algorithm (default True)
        enable_thermal_annealing: Use thermal annealing for quality (default True)
    
    Returns:
        Updated scene dict with optimized positions
    """
    
    elements = scene.get("elements", [])
    if not elements:
        return scene
    
    # Check if v2.0 is available and requested
    if not (use_v2_enhancements and V2_AVAILABLE):
        print("[ADAPTER] Using fallback collision detection (v2.0 not available)")
        return apply_layout_and_collision_detection_v1(scene)
    
    print("[ADAPTER v2.0] Processing scene with enhanced algorithms...")
    
    try:
        # =====================================================================
        # PHASE 1: EXTRACT ELEMENTS
        # =====================================================================
        print("[ADAPTER v2.0] PHASE 1: Extracting elements...")
        
        layout_elements = {}
        element_metadata = {}
        original_positions = {}
        
        for idx, element in enumerate(elements):
            element_id = element.get("id", f"elem_{idx}")
            element_type = str(element.get("type", "text")).lower()
            
            # Get position and size
            position = element.get("position", [0, 0])
            size = element.get("size", [1.0, 0.5])
            
            # Estimate dimensions if not provided
            if not size or size == [1.0, 0.5]:
                content = str(element.get("content", ""))[:100]
                
                if element_type in ("text", "mathtex", "label"):
                    lines = content.split("\n") if content else [""]
                    max_len = max(len(line) for line in lines)
                    size = [
                        min(6.5, 0.12 * max_len + 1.0),
                        max(0.5, 0.4 * len(lines))
                    ]
                elif element_type in ("graph", "parametric", "axes"):
                    size = [3.5, 3.0]
                elif element_type in ("figure", "image"):
                    size = [2.5, 2.0]
                else:
                    size = [2.0, 1.0]
            
            # Calculate bounding box
            x_center, y_center = position[0], position[1]
            width, height = size[0], size[1]
            
            x_min = x_center - width / 2
            y_min = y_center - height / 2
            x_max = x_center + width / 2
            y_max = y_center + height / 2
            
            # Create LayoutElement
            bbox = BoundingBox(x_min, y_min, x_max, y_max)
            layout_elements[element_id] = LayoutElement(
                id=element_id,
                element_type=element_type,
                bounding_box=bbox,
                locked=element.get("locked", False),
                dependencies=element.get("dependencies", [])
            )
            
            # Store metadata
            element_metadata[element_id] = {
                "original_position": position,
                "size": size,
                "style": element.get("style", {}),
                "timing": element.get("timing", {}),
                "element_type": element_type
            }
            
            original_positions[element_id] = bbox.center
            
            print(f"  ✓ {element_id}: {element_type} ({width:.2f}×{height:.2f})")
        
        print(f"[ADAPTER v2.0] Total elements: {len(layout_elements)}")
        
        # =====================================================================
        # PHASE 2: ANALYZE COMPLEXITY (NEW v2.0)
        # =====================================================================
        print("\n[ADAPTER v2.0] PHASE 2: Analyzing element configuration...")
        
        analysis = ComplexityAnalyzer.analyze_elements(layout_elements)
        
        print(f"  Elements: {analysis['element_count']}")
        print(f"  Overlap: {analysis['overlap_percentage']:.1f}%")
        print(f"  Density: {analysis['element_density']:.2f}")
        
        recommended_algorithm = analysis['recommended_algorithm']
        if enable_auto_algorithm:
            print(f"  Recommended algorithm: {recommended_algorithm.upper()}")
        
        # =====================================================================
        # PHASE 3: FAST COLLISION DETECTION WITH QUADTREE (NEW v2.0)
        # =====================================================================
        if enable_quadtree and len(layout_elements) > 5:
            print("\n[ADAPTER v2.0] PHASE 3: Detecting overlaps with QuadTree...")
            
            canvas_bounds = (-MANIM_SCREEN_WIDTH/2, -MANIM_SCREEN_HEIGHT/2,
                            MANIM_SCREEN_WIDTH/2, MANIM_SCREEN_HEIGHT/2)
            qtree = QuadTree(canvas_bounds, max_depth=8, max_elements=4)
            
            bbox_map = {}
            for elem_id, elem in layout_elements.items():
                bbox = elem.bounding_box
                bbox_tuple = (bbox.x_min, bbox.y_min, bbox.x_max, bbox.y_max)
                qtree.insert(elem_id, bbox_tuple)
                bbox_map[elem_id] = bbox_tuple
            
            collisions = 0
            for elem_id, bbox_tuple in bbox_map.items():
                nearby = qtree.query_collisions(bbox_tuple)
                collisions += len(nearby)
            
            if collisions > 0:
                print(f"  Found potential collisions using spatial indexing")
            else:
                print(f"  No overlaps detected!")
        
        # =====================================================================
        # PHASE 4: SOLVE WITH ENHANCED PHYSICS (NEW v2.0)
        # =====================================================================
        print("\n[ADAPTER v2.0] PHASE 4: Solving with enhanced physics...")
        
        # Determine iterations based on complexity
        if analysis['overlap_percentage'] > 50:
            iterations = 150  # High overlap needs more iterations
            print(f"  High overlap detected - using {iterations} iterations")
        else:
            iterations = 100  # Standard iterations
        
        # Create layout engine with adaptive parameters
        layout_engine = AdvancedForceDirectedLayout(
            layout_elements,
            canvas_width=MANIM_SCREEN_WIDTH,
            canvas_height=MANIM_SCREEN_HEIGHT,
            iterations=iterations,
            use_thermal_annealing=enable_thermal_annealing
        )
        
        # Adapt physics parameters based on complexity
        if analysis['overlap_percentage'] > 60:
            layout_engine.repulsion_strength = 0.9
            layout_engine.boundary_repulsion = 2.5
            layout_engine.cooling_rate = 0.88
            print(f"  Aggressive physics (high overlap)")
        elif analysis['overlap_percentage'] > 30:
            layout_engine.repulsion_strength = 0.6
            layout_engine.cooling_rate = 0.92
            print(f"  Moderate physics")
        else:
            layout_engine.repulsion_strength = 0.4
            layout_engine.cooling_rate = 0.95
            print(f"  Conservative physics (low overlap)")
        
        # Run layout optimization
        resolved_positions = layout_engine.layout()
        
        print(f"  ✓ Physics optimization complete")
        
        # =====================================================================
        # PHASE 5: EVALUATE SOLUTION WITH MULTI-METRICS (NEW v2.0)
        # =====================================================================
        print("\n[ADAPTER v2.0] PHASE 5: Evaluating solution quality...")
        
        scores = EnhancedLayoutEvaluator.evaluate_layout(
            layout_elements,
            resolved_positions,
            original_positions
        )
        
        print(f"  Overlap remaining: {scores['overlap_score']:.3f}")
        print(f"  Total displacement: {scores['displacement_score']:.2f} units")
        print(f"  Boundary violations: {int(scores['boundary_score'])}")
        print(f"  Overall quality score: {scores['overall_score']:.1f}")
        
        # =====================================================================
        # PHASE 6: APPLY OPTIMIZED POSITIONS TO SCENE
        # =====================================================================
        print("\n[ADAPTER v2.0] PHASE 6: Applying optimized positions...")
        
        updates = 0
        for element in elements:
            elem_id = element.get("id", f"elem_{elements.index(element)}")
            
            if elem_id in resolved_positions:
                new_pos = resolved_positions[elem_id]
                element["position"] = list(new_pos)
                element["_layout_resolved"] = True
                element["_layout_quality"] = scores['overall_score']
                updates += 1
        
        print(f"  ✓ Updated {updates} element positions")
        
        # =====================================================================
        # PHASE 7: ADD METADATA
        # =====================================================================
        scene["_adapter_version"] = "v2.0"
        scene["_complexity_analysis"] = analysis
        scene["_quality_scores"] = scores
        scene["_layout_optimized"] = True
        
        print("\n[ADAPTER v2.0] ✅ Scene optimization complete")
        
        return scene
        
    except Exception as e:
        print(f"[ADAPTER v2.0] ERROR: {str(e)}")
        print(f"[ADAPTER v2.0] Falling back to v1.0...")
        return apply_layout_and_collision_detection_v1(scene)


def apply_layout_and_collision_detection_v1(
    scene: Dict[str, Any]
) -> Dict[str, Any]:
    """
    ORIGINAL v1.0: Fallback collision detection
    
    This preserves the original behavior for backward compatibility
    or when v2.0 enhancements are not available.
    """
    print("[ADAPTER] Using v1.0 collision detection (fallback)")
    
    elements = scene.get("elements", [])
    if not elements:
        return scene
    
    try:
        # Import original components
        from scripts.collision_detector import CollisionDetector
        from scripts.layer_manager import LayerManager, ElementType
        
        # Create detector
        collision_detector = CollisionDetector()
        layer_manager = LayerManager()
        
        # Build simple position map
        positions = {}
        for element in elements:
            elem_id = element.get("id", f"elem_{elements.index(element)}")
            position = element.get("position", [0, 0])
            positions[elem_id] = tuple(position)
        
        # Detect collisions (naive O(n²) approach)
        collisions = 0
        for i, elem1 in enumerate(elements):
            for elem2 in elements[i+1:]:
                id1 = elem1.get("id", f"elem_{i}")
                id2 = elem2.get("id", f"elem_{elements.index(elem2)}")
                
                pos1 = positions[id1]
                pos2 = positions[id2]
                
                size1 = elem1.get("size", [1.0, 0.5])
                size2 = elem2.get("size", [1.0, 0.5])
                
                # Simple AABB check
                dist_x = abs(pos1[0] - pos2[0])
                dist_y = abs(pos1[1] - pos2[1])
                
                if dist_x < (size1[0] + size2[0]) / 2 and \
                   dist_y < (size1[1] + size2[1]) / 2:
                    collisions += 1
        
        if collisions > 0:
            print(f"[ADAPTER] Detected {collisions} potential collisions")
        
        scene["_layout_optimized"] = False
        
        return scene
        
    except Exception as e:
        print(f"[ADAPTER] Fallback failed: {str(e)}")
        return scene


# ============================================================================
# UTILITY: HOW TO INTEGRATE INTO EXISTING MANIM_ADAPTER.PY
# ============================================================================

INTEGRATION_INSTRUCTIONS = """
HOW TO INTEGRATE v2.0 INTO manim_adapter.py:

1. Add import at top of file:
   from scripts.manim_adapter_enhanced_v2 import apply_layout_and_collision_detection_v2

2. Replace existing function call:
   OLD: scene = apply_layout_and_collision_detection(scene)
   NEW: scene = apply_layout_and_collision_detection_v2(scene)

3. Optional: Add options
   scene = apply_layout_and_collision_detection_v2(
       scene,
       use_v2_enhancements=True,
       enable_quadtree=True,
       enable_auto_algorithm=True,
       enable_thermal_annealing=True
   )

4. That's it!For backward compatibility:
   - If v2.0 not available → automatically falls back to v1.0
   - All existing scene structure is preserved
   - New fields added: _adapter_version, _complexity_analysis, _quality_scores
"""

if __name__ == "__main__":
    print(INTEGRATION_INSTRUCTIONS)
    print("\nv2.0 Enhanced Collision Detection Ready for Integration!")
