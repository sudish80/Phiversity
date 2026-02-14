#!/usr/bin/env python3
"""
OVERLAP RESOLUTION v2.0 - INTEGRATION GUIDE
Quick examples showing how to use the enhanced algorithms
"""

# ============================================================================
# EXAMPLE 1: BASIC USAGE - AUTO EVERYTHING
# ============================================================================

def example_1_auto_everything():
    """
    Simplest usage: Let the system decide everything.
    Best for: Quick integration, letting system optimize itself
    """
    from scripts.overlap_resolution_enhanced import (
        ComplexityAnalyzer,
        AdvancedForceDirectedLayout,
        EnhancedLayoutEvaluator
    )
    
    # Example elements (you would load these from your scene)
    elements = {
        'title': LayoutElement(
            id='title',
            element_type='text',
            bounding_box=BoundingBox(0, 3, 2, 3.5),
            locked=False
        ),
        'eq1': LayoutElement(
            id='eq1',
            element_type='equation',
            bounding_box=BoundingBox(0, 1, 2, 2),
            locked=False
        ),
        'graph': LayoutElement(
            id='graph',
            element_type='graph',
            bounding_box=BoundingBox(2.5, 1, 4.5, 3),
            locked=False
        )
    }
    
    # STEP 1: Analyze complexity
    analysis = ComplexityAnalyzer.analyze_elements(elements)
    print(f"Element count: {analysis['element_count']}")
    print(f"Overlap: {analysis['overlap_percentage']:.1f}%")
    print(f"Recommended: {analysis['recommended_algorithm']}")
    
    # STEP 2: Use enhanced physics (auto-selected algorithm)
    layout = AdvancedForceDirectedLayout(
        elements,
        iterations=100,
        use_thermal_annealing=True  # Helps escape local minima
    ).layout()
    
    # STEP 3: Evaluate quality
    original_pos = {
        elem_id: elem.bounding_box.center
        for elem_id, elem in elements.items()
    }
    
    scores = EnhancedLayoutEvaluator.evaluate_layout(
        elements, layout, original_pos
    )
    
    print(f"\nLayout Quality:")
    print(f"  Overlap: {scores['overlap_score']:.3f}")
    print(f"  Displacement: {scores['displacement_score']:.3f}")
    print(f"  Boundary violations: {scores['boundary_score']:.0f}")
    print(f"  Overall score: {scores['overall_score']:.1f}")
    
    return layout


# ============================================================================
# EXAMPLE 2: FAST COLLISION DETECTION - USE QUADTREE
# ============================================================================

def example_2_fast_collision_detection():
    """
    For many elements, use spatial indexing for fast collision queries.
    Best for: Large diagrams (50+ elements)
    """
    from scripts.overlap_resolution_enhanced import QuadTree
    
    # Create quadtree for canvas
    canvas_bounds = (-4, -2.25, 4, 2.25)  # Manim canvas
    qtree = QuadTree(canvas_bounds, max_depth=8, max_elements=4)
    
    # Insert all elements
    elements_data = [
        ('text1', (-3.5, 1.5, -2.0, 2.0)),
        ('text2', (-3.2, 1.3, -2.2, 1.8)),  # Overlaps with text1
        ('graph', (0, -2, 3, 1)),
        ('eq1', (3.2, 0.5, 4, 1.5)),
    ]
    
    for elem_id, bbox in elements_data:
        qtree.insert(elem_id, bbox)
    
    # Fast query: find all elements overlapping with a target
    target_bbox = (-3.3, 1.4, -2.1, 1.9)
    collisions = qtree.query_collisions(target_bbox)
    
    print(f"Elements colliding with {target_bbox}: {collisions}")
    # Output: ['text1', 'text2'] - very fast even with hundreds of elements


# ============================================================================
# EXAMPLE 3: SMART ALGORITHM SELECTION
# ============================================================================

def example_3_smart_algorithm_selection():
    """
    Automatically choose the best algorithm for your elements.
    Best for: Don't know which algorithm to use
    """
    from scripts.overlap_resolution_enhanced import ComplexityAnalyzer
    
    # Analyze your elements
    elements = load_elements_from_scene()  # Your code
    
    analysis = ComplexityAnalyzer.analyze_elements(elements)
    
    # Decision making
    algorithm = analysis['recommended_algorithm']
    
    if algorithm == 'grid':
        print("✓ Simple layout - using GRID (fastest)")
        # Use original grid algorithm
        
    elif algorithm == 'hierarchical':
        print("✓ Has structure - using HIERARCHICAL (respects dependencies)")
        # Elements have clear dependencies → hierarchical works best
        
    elif algorithm == 'radial':
        print("✓ Clustered layout - using RADIAL (spreads elements)")
        # Elements clustered together → radial spreads them nicely
        
    elif algorithm == 'force_directed':
        print("✓ Complex overlap - using FORCE_DIRECTED (best quality)")
        # High overlap or dependencies → physics handles it well


# ============================================================================
# EXAMPLE 4: TUNED FORCE-DIRECTED FOR DENSE LAYOUTS
# ============================================================================

def example_4_tuned_physics():
    """
    Fine-tune physics parameters for your specific needs.
    Best for: Dense diagrams, specific quality requirements
    """
    from scripts.overlap_resolution_enhanced import AdvancedForceDirectedLayout
    
    elements = load_elements_from_scene()
    
    # Strong overlap? Use aggressive physics
    layout = AdvancedForceDirectedLayout(
        elements,
        iterations=150,  # Longer convergence
        use_thermal_annealing=True,
    )
    
    # Increase repulsive force
    layout.repulsion_strength = 0.8  # Default 0.5
    
    # Increase boundary protection
    layout.boundary_repulsion = 2.5  # Default 2.0
    
    # More aggressive annealing
    layout.cooling_rate = 0.90  # Default 0.95 (slower = more exploration)
    layout.thermal_noise = 0.15  # Default 0.1
    
    result = layout.layout()
    return result


# ============================================================================
# EXAMPLE 5: INTEGRATION WITH MANIM_ADAPTER
# ============================================================================

def example_5_manim_integration():
    """
    How to integrate enhancements into existing manim_adapter.py
    """
    
    # In manim_adapter.py, replace the collision detection section:
    
    from scripts.overlap_resolution_enhanced import (
        ComplexityAnalyzer,
        QuadTree,
        AdvancedForceDirectedLayout,
        EnhancedLayoutEvaluator
    )
    
    def apply_layout_and_collision_detection_enhanced(scene: Dict[str, Any]):
        """Enhanced version with v2.0 improvements"""
        elements = scene.get("elements", [])
        if not elements:
            return scene
        
        # STEP 1: Convert to LayoutElement objects
        layout_elements = {}
        for elem in elements:
            # ... conversion code ...
            layout_elements[elem_id] = layout_element
        
        # STEP 2: Analyze complexity (NEW)
        analysis = ComplexityAnalyzer.analyze_elements(layout_elements)
        print(f"Complexity: {analysis['overlap_percentage']:.1f}% overlap")
        print(f"Recommended: {analysis['recommended_algorithm']}")
        
        # STEP 3: Use spatial indexing (FASTER)
        canvas_bounds = (-4, -2.25, 4, 2.25)
        qtree = QuadTree(canvas_bounds)
        for elem_id, elem in layout_elements.items():
            bbox = (
                elem.bounding_box.x_min,
                elem.bounding_box.y_min,
                elem.bounding_box.x_max,
                elem.bounding_box.y_max
            )
            qtree.insert(elem_id, bbox)
        
        # STEP 4: Solve with enhanced physics (BETTER)
        layout = AdvancedForceDirectedLayout(
            layout_elements,
            iterations=100,
            use_thermal_annealing=True
        ).layout()
        
        # STEP 5: Evaluate quality (COMPREHENSIVE)
        original_positions = {
            elem_id: elem.bounding_box.center
            for elem_id, elem in layout_elements.items()
        }
        
        scores = EnhancedLayoutEvaluator.evaluate_layout(
            layout_elements, layout, original_positions
        )
        
        print(f"Result: {scores['overall_score']:.1f}")
        print(f"  Overlap: {scores['overlap_score']:.3f}")
        print(f"  Displacement: {scores['displacement_score']:.3f}")
        
        # STEP 6: Apply to scene (unchanged)
        for elem_id, (x, y) in layout.items():
            # Update element position
            element['_layout_position'] = (x, y)
        
        return scene


# ============================================================================
# EXAMPLE 6: PERFORMANCE COMPARISON
# ============================================================================

def example_6_performance_test():
    """
    Compare performance: original vs enhanced
    """
    import time
    from scripts.overlap_resolution_enhanced import (
        QuadTree,
        AdvancedForceDirectedLayout
    )
    
    # Create test elements (500 elements)
    num_elements = 500
    elements = {}
    for i in range(num_elements):
        x = (i % 20) * 0.4 - 4
        y = (i // 20) * 0.25 - 2
        elements[f'elem_{i}'] = LayoutElement(
            id=f'elem_{i}',
            element_type='text',
            bounding_box=BoundingBox(x, y, x+0.3, y+0.2),
            locked=False
        )
    
    # Test collision detection speed
    canvas_bounds = (-4, -2.25, 4, 2.25)
    
    print("COLLISION DETECTION SPEED TEST")
    print("=" * 50)
    
    # Naive approach (old way): O(n²)
    start = time.time()
    collisions = 0
    elem_list = list(elements.values())
    for i, elem1 in enumerate(elem_list):
        for elem2 in elem_list[i+1:]:
            if elem1.bounding_box.intersects(elem2.bounding_box):
                collisions += 1
    naive_time = time.time() - start
    print(f"Naive O(n²):  {naive_time*1000:.2f}ms  ({collisions} collisions)")
    
    # Enhanced approach: O(n log n)
    start = time.time()
    qtree = QuadTree(canvas_bounds)
    collisions = 0
    for elem_id, elem in elements.items():
        bbox = (
            elem.bounding_box.x_min,
            elem.bounding_box.y_min,
            elem.bounding_box.x_max,
            elem.bounding_box.y_max
        )
        qtree.insert(elem_id, bbox)
    
    # Query collisions
    for elem_id, elem in elements.items():
        bbox = (
            elem.bounding_box.x_min,
            elem.bounding_box.y_min,
            elem.bounding_box.x_max,
            elem.bounding_box.y_max
        )
        nearby = qtree.query_collisions(bbox)
        collisions += len(nearby) // 2  # Each collision counted twice
    
    enhanced_time = time.time() - start
    print(f"Enhanced:     {enhanced_time*1000:.2f}ms  ({collisions} collisions)")
    print(f"Speedup:      {naive_time/enhanced_time:.1f}x faster")


# ============================================================================
# EXAMPLE 7: TROUBLESHOOTING
# ============================================================================

def example_7_troubleshooting():
    """
    Common issues and solutions
    """
    
    # Issue 1: Still have overlaps
    print("TROUBLESHOOTING: Overlaps remain")
    print("-" * 50)
    print("Solution 1: Increase iterations")
    print("  layout_engine.iterations = 200  # More iterations")
    print()
    print("Solution 2: Increase repulsion")
    print("  layout_engine.repulsion_strength = 0.9  # Push harder")
    print()
    print("Solution 3: Aggressive annealing")
    print("  layout_engine.cooling_rate = 0.85  # Slower cooling")
    print()
    
    # Issue 2: Too slow
    print("\nTROUBLESHOOTING: Too slow")
    print("-" * 50)
    print("Solution 1: Reduce iterations")
    print("  layout_engine.iterations = 50  # Fewer iterations")
    print()
    print("Solution 2: Disable annealing")
    print("  use_thermal_annealing = False  # Faster convergence")
    print()
    print("Solution 3: Weaken forces")
    print("  repulsion_strength = 0.3  # Gentler forces")
    print()
    
    # Issue 3: Quality varies
    print("\nTROUBLESHOOTING: Inconsistent results")
    print("-" * 50)
    print("Solution: Enable thermal annealing")
    print("  use_thermal_annealing = True")
    print("  cooling_rate = 0.90  # Slower cooling")


# ============================================================================
# STUB CLASSES FOR EXAMPLES
# ============================================================================

from dataclasses import dataclass
from typing import Tuple, Dict, Any, Optional, List

@dataclass
class BoundingBox:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    
    @property
    def width(self):
        return self.x_max - self.x_min
    
    @property
    def height(self):
        return self.y_max - self.y_min
    
    @property
    def center(self):
        return ((self.x_min + self.x_max) / 2, (self.y_min + self.y_max) / 2)
    
    def intersects(self, other, margin=0):
        return (
            self.x_min - margin < other.x_max + margin and
            self.x_max + margin > other.x_min - margin and
            self.y_min - margin < other.y_max + margin and
            self.y_max + margin > other.y_min - margin
        )


@dataclass
class LayoutElement:
    id: str
    element_type: str
    bounding_box: BoundingBox
    locked: bool = False
    layer: int = 0
    dependencies: List[str] = None
    preferred_position: Optional[Tuple[float, float]] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []


def load_elements_from_scene():
    """Placeholder for loading elements"""
    return {
        'title': LayoutElement('title', 'text', BoundingBox(0, 3, 2, 3.5)),
        'eq': LayoutElement('eq', 'equation', BoundingBox(0, 1, 2, 2)),
    }


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("OVERLAP RESOLUTION v2.0 - INTEGRATION EXAMPLES")
    print("=" * 70)
    print()
    
    print("Example 1: Auto everything")
    print("-" * 70)
    # example_1_auto_everything()
    print("Runs auto complexity analysis and recommendations")
    print()
    
    print("Example 2: Fast collision detection")
    print("-" * 70)
    # example_2_fast_collision_detection()
    print("Uses QuadTree for O(n log n) queries")
    print()
    
    print("Example 3: Smart algorithm selection")
    print("-" * 70)
    # example_3_smart_algorithm_selection()
    print("Automatically chooses best algorithm")
    print()
    
    print("Example 4: Tuned physics")
    print("-" * 70)
    # example_4_tuned_physics()
    print("Fine-tune parameters for your needs")
    print()
    
    print("Example 5: Manim integration")
    print("-" * 70)
    print("Update manim_adapter.py to use enhancements")
    print()
    
    print("Example 6: Performance test")
    print("-" * 70)
    # example_6_performance_test()
    print("Compare original vs enhanced speed")
    print()
    
    print("Example 7: Troubleshooting")
    print("-" * 70)
    # example_7_troubleshooting()
    print("Solutions for common issues")
    print()
    
    print("=" * 70)
    print("Ready to integrate! See OVERLAP_ALGORITHM_ENHANCEMENTS.md for details")
    print("=" * 70)
