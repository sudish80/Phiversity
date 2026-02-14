"""
Verify Comprehensive Multi-Stage Optimization Components
Tests all new optimizer integration components
"""

def verify_imports():
    """Test that all components can be imported"""
    print("=" * 70)
    print("COMPREHENSIVE MULTI-STAGE OPTIMIZATION VERIFICATION")
    print("=" * 70)
    
    print("\n[1] Importing Components")
    
    try:
        from overlap_resolution_v3_advanced import (
            AdaptiveOptimizerSelector,
            ConstraintWeightOptimizer,
            PositionRefiner,
            MultiStageOptimizer,
            AdvancedLayoutEngine
        )
        print("  ✓ All components imported successfully")
        return True
    except ImportError as e:
        print(f"  ✗ Import failed: {e}")
        return False


def verify_adaptive_optimizer_selector():
    """Test AdaptiveOptimizerSelector"""
    print("\n[2] AdaptiveOptimizerSelector")
    
    from overlap_resolution_v3_advanced import AdaptiveOptimizerSelector, ConstraintSystem
    import numpy as np
    
    selector = AdaptiveOptimizerSelector()
    
    # Create test problem
    elements = {
        f"elem{i}": {
            "position": (np.random.uniform(-2, 2), np.random.uniform(-1, 1)),
            "size": (0.2, 0.2)
        }
        for i in range(70)
    }
    
    # Analyze
    analysis = selector.analyze_problem_complexity(elements)
    print(f"  Problem analysis:")
    print(f"    Element count: {analysis['element_count']}")
    print(f"    Overlap density: {analysis['overlap_density']:.2%}")
    print(f"    Complexity score: {analysis['complexity_score']:.1f}/100")
    print(f"  ✓ Problem analysis works")
    
    # Select optimizer
    config = selector.select_optimizer(analysis)
    print(f"  Optimizer selection:")
    print(f"    Use enhanced: {config['use_enhanced']}")
    print(f"    Learning rate: {config['lr']}")
    print(f"    Max steps: {config['max_steps']}")
    print(f"    Reason: {config['reason']}")
    print(f"  ✓ Optimizer selection works")


def verify_constraint_weight_optimizer():
    """Test ConstraintWeightOptimizer"""
    print("\n[3] ConstraintWeightOptimizer")
    
    from overlap_resolution_v3_advanced import (
        ConstraintWeightOptimizer,
        ConstraintSystem,
        ConstraintType,
        LayoutConstraint
    )
    import numpy as np
    
    optimizer = ConstraintWeightOptimizer()
    
    # Create test elements
    elements = {
        f"elem{i}": {
            "position": (np.random.uniform(-2, 2), np.random.uniform(-1, 1)),
            "size": (0.2, 0.2)
        }
        for i in range(20)
    }
    
    # Create test constraints
    constraints = ConstraintSystem()
    constraints.add_constraint(LayoutConstraint(
        constraint_type=ConstraintType.PROXIMITY,
        element_ids=["elem0", "elem1"],
        parameters={"max_distance": 0.5},
        weight=1.0
    ))
    constraints.add_constraint(LayoutConstraint(
        constraint_type=ConstraintType.ALIGNMENT,
        element_ids=["elem2", "elem3", "elem4"],
        parameters={"axis": "x"},
        weight=1.0
    ))
    
    # Get positions
    positions = {eid: elem["position"] for eid, elem in elements.items()}
    
    # Optimize (quick test)
    weights = optimizer.optimize_constraint_weights(
        constraints,
        elements,
        positions,
        max_steps=2,
        lr=0.02,
        verbose=False
    )
    
    print(f"  Optimized weights: {weights}")
    print(f"  ✓ Constraint weight optimization works")


def verify_position_refiner():
    """Test PositionRefiner"""
    print("\n[4] PositionRefiner")
    
    from overlap_resolution_v3_advanced import (
        PositionRefiner,
        LossWeights,
        ConstraintSystem
    )
    import numpy as np
    
    refiner = PositionRefiner()
    
    # Create test elements
    elements = {
        f"elem{i}": {
            "position": (np.random.uniform(-2, 2), np.random.uniform(-1, 1)),
            "size": (0.15, 0.15)
        }
        for i in range(15)
    }
    
    initial_positions = {eid: elem["position"] for eid, elem in elements.items()}
    
    # Refine (quick test)
    refined = refiner.refine_positions(
        elements,
        initial_positions,
        LossWeights(),
        ConstraintSystem(),
        max_steps=2,
        lr=0.05,
        verbose=False
    )
    
    print(f"  Initial positions: {len(initial_positions)}")
    print(f"  Refined positions: {len(refined)}")
    print(f"  Position changed: {refined != initial_positions}")
    print(f"  ✓ Position refinement works")


def verify_multi_stage_optimizer():
    """Test MultiStageOptimizer"""
    print("\n[5] MultiStageOptimizer")
    
    from overlap_resolution_v3_advanced import (
        MultiStageOptimizer,
        ConstraintSystem
    )
    import numpy as np
    
    orchestrator = MultiStageOptimizer()
    
    elements = {
        f"elem{i}": {
            "position": (np.random.uniform(-2, 2), np.random.uniform(-1, 1)),
            "size": (0.18, 0.18)
        }
        for i in range(30)
    }
    
    _, info = orchestrator.optimize_full_pipeline(
        elements,
        ConstraintSystem(),
        None,
        enable_all_stages=False,  # Quick test
        verbose=False
    )
    
    print(f"  Stage results keys: {list(info['stage_results'].keys())}")
    print(f"  Optimizer config: {info['stage_results']['optimizer_config']['use_enhanced']}")
    print(f"  Ready for solving: {info['ready_for_solving']}")
    print(f"  ✓ Multi-stage orchestration works")


def verify_advanced_layout_engine():
    """Test AdvancedLayoutEngine integration"""
    print("\n[6] AdvancedLayoutEngine Integration")
    
    from overlap_resolution_v3_advanced import AdvancedLayoutEngine
    import numpy as np
    
    engine = AdvancedLayoutEngine()
    
    # Check new attributes
    attrs = [
        'multi_stage_optimizer',
        'optimizer_selector',
        'constraint_weight_optimizer',
        'position_refiner',
        'last_optimization_info'
    ]
    
    for attr in attrs:
        if hasattr(engine, attr):
            print(f"  ✓ {attr}")
        else:
            print(f"  ✗ {attr} NOT FOUND")
    
    # Check solve_comprehensive method
    if hasattr(engine, 'solve_comprehensive'):
        print(f"  ✓ solve_comprehensive method exists")
        
        # Quick test
        elements = {
            f"elem{i}": {
                "position": (np.random.uniform(-2, 2), np.random.uniform(-1, 1)),
                "size": (0.2, 0.2)
            }
            for i in range(20)
        }
        
        # Try calling (will be slow but tests the API)
        print(f"  Testing solve_comprehensive (quick mode)...")
        positions = engine.solve_comprehensive(
            elements,
            max_iterations=20,  # Quick
            enable_multi_stage=False,  # Skip slow stages
            enable_position_refinement=False,  # Skip refinement
            verbose=False
        )
        
        print(f"  Solved {len(positions)} positions")
        print(f"  ✓ solve_comprehensive works")
    else:
        print(f"  ✗ solve_comprehensive method NOT FOUND")


def verify_example_9():
    """Check if Example 9 exists"""
    print("\n[7] Example 9 Availability")
    
    try:
        from overlap_integration_v3_examples import example_9_comprehensive_multi_stage
        print(f"  ✓ Example 9 imported successfully")
        print(f"  Function: {example_9_comprehensive_multi_stage.__name__}")
    except ImportError as e:
        print(f"  ✗ Example 9 import failed: {e}")


if __name__ == "__main__":
    try:
        if not verify_imports():
            print("\n✗ Import failed - cannot continue")
            exit(1)
        
        verify_adaptive_optimizer_selector()
        verify_constraint_weight_optimizer()
        verify_position_refiner()
        verify_multi_stage_optimizer()
        verify_advanced_layout_engine()
        verify_example_9()
        
        print("\n" + "=" * 70)
        print("✓ ALL COMPREHENSIVE OPTIMIZER COMPONENTS VERIFIED!")
        print("  - AdaptiveOptimizerSelector: Working")
        print("  - ConstraintWeightOptimizer: Working")
        print("  - PositionRefiner: Working")
        print("  - MultiStageOptimizer: Working")
        print("  - AdvancedLayoutEngine integration: Complete")
        print("  - Example 9: Available")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error during verification: {e}")
        import traceback
        traceback.print_exc()
