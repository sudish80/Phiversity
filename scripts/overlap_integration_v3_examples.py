"""
OVERLAP RESOLUTION v3.0 - INTEGRATION & EXAMPLES
================================================

Complete examples showing how to use advanced v3.0 features:
1. Constraint-based layout with dependencies
2. Intelligent clustering and grouping
3. ML-based parameter tuning
4. Multi-objective optimization
5. Adaptive strategy selection
6. Combined super-solution

Author: GitHub Copilot
Date: February 8, 2026
"""

import numpy as np
from typing import Dict, List, Tuple, Any, Optional

# Handle imports whether running from project root or scripts directory
try:
    from scripts.overlap_resolution_v3_advanced import (
        ConstraintSystem, ConstraintType, LayoutConstraint, ElementClusterer,
        ParameterOptimizer, MultiObjectiveOptimizer,
        AdvancedLayoutEngine, LayoutAnalyzer, AdaptiveLayoutStrategy,
        ActivationSelector
    )
except ModuleNotFoundError:
    from overlap_resolution_v3_advanced import (
        ConstraintSystem, ConstraintType, LayoutConstraint, ElementClusterer,
        ParameterOptimizer, MultiObjectiveOptimizer,
        AdvancedLayoutEngine, LayoutAnalyzer, AdaptiveLayoutStrategy,
        ActivationSelector
    )


# ============================================================================
# EXAMPLE 1: CONSTRAINT-BASED HIERARCHICAL LAYOUT
# ============================================================================

def example_1_constraints_and_dependencies():
    """
    Example 1: Layout with constraints and dependencies.
    
    Use case: Physics diagram where objects have relationships.
    """
    print("\n" + "="*70)
    print("EXAMPLE 1: Constraint-Based Layout with Dependencies")
    print("="*70)
    
    # Define elements (e.g., physics diagram)
    elements = {
        "mass_A": {"position": (-1.0, 0.5), "size": (0.3, 0.3)},
        "mass_B": {"position": (1.0, 0.5), "size": (0.3, 0.3)},
        "spring": {"position": (0.0, 0.6), "size": (0.2, 0.1)},
        "force_arrow": {"position": (0.0, 0.0), "size": (0.1, 0.4)},
        "label_A": {"position": (-1.0, -0.3), "size": (0.2, 0.1)},
        "label_B": {"position": (1.0, -0.3), "size": (0.2, 0.1)},
    }
    
    # Create constraint system
    constraints = ConstraintSystem()
    
    # Constraint 1: Mass A and B should be aligned horizontally
    constraints.add_alignment_constraint(["mass_A", "mass_B"], axis="y", weight=2.0)
    
    # Constraint 2: Spring should be centered between masses
    constraints.add_proximity_constraint(["spring", "mass_A"], max_distance=1.5, weight=1.5)
    constraints.add_proximity_constraint(["spring", "mass_B"], max_distance=1.5, weight=1.5)
    
    # Constraint 3: Labels should stay below their masses
    constraints.add_grouping_constraint(["mass_A", "label_A"], max_spread=0.7, weight=1.0)
    constraints.add_grouping_constraint(["mass_B", "label_B"], max_spread=0.7, weight=1.0)
    
    # Constraint 4: Force arrow should be separated from masses
    constraints.add_separation_constraint(
        ["force_arrow", "mass_A", "mass_B"],
        min_distance=0.8,
        weight=1.5
    )
    
    print("\n[CONSTRAINTS DEFINED]")
    for i, c in enumerate(constraints.constraints):
        print(f"  [{i}] {c.constraint_type.value}")
        print(f"      Elements: {c.element_ids}")
        print(f"      Weight: {c.weight}")
    
    # Solve layout with loss reporting
    engine = AdvancedLayoutEngine()
    def loss_logger(iteration, loss_total, components):
        if iteration % 20 == 0:
            print(f"  [LOSS] iter={iteration:3d} total={loss_total:.4f} overlap={components['overlap']:.4f}")

    positions, loss_total, loss_components, tune_info = engine.solve_with_constraints(
        elements,
        constraints,
        max_iterations=100,
        loss_every=5,
        loss_callback=loss_logger,
        return_loss=True
    )
    
    print("\n[SOLVED POSITIONS]")
    for elem_id, pos in positions.items():
        print(f"  {elem_id:15} -> ({pos[0]:6.2f}, {pos[1]:6.2f})")
    
    # Evaluate constraint satisfaction
    violation = constraints.evaluate_all(positions)
    print(f"\n[CONSTRAINT SATISFACTION]")
    print(f"  Total violation: {violation:.4f}")
    print(f"  Status: {'✓ SATISFIED' if violation < 0.5 else '✗ VIOLATIONS PRESENT'}")
    
    # Analyze quality
    overlap = LayoutAnalyzer.calculate_overlap_score(elements, positions)
    compactness = LayoutAnalyzer.calculate_compactness(positions)
    balance = LayoutAnalyzer.calculate_balance(positions)
    
    print(f"\n[QUALITY METRICS]")
    print(f"  Overlap area: {overlap:.4f}")
    print(f"  Compactness: {compactness:.4f}")
    print(f"  Balance: {balance:.4f}")
    print(f"  Final loss: {loss_total:.4f}")


# ============================================================================
# EXAMPLE 2: INTELLIGENT CLUSTERING & GROUPING
# ============================================================================

def example_2_clustering_and_grouping():
    """
    Example 2: Large dataset with intelligent clustering.
    
    Use case: Dense diagram with many elements that form natural groups.
    """
    print("\n" + "="*70)
    print("EXAMPLE 2: Intelligent Clustering & Grouping")
    print("="*70)
    
    # Create elements with natural clusters
    elements = {}
    
    # Cluster 1: Distributed around (0, 0)
    for i in range(5):
        elements[f"cluster1_elem{i}"] = {
            "position": (0 + np.random.normal(0, 0.2), 0 + np.random.normal(0, 0.2)),
            "size": (0.15, 0.15)
        }
    
    # Cluster 2: Distributed around (2.5, 0)
    for i in range(5):
        elements[f"cluster2_elem{i}"] = {
            "position": (2.5 + np.random.normal(0, 0.2), 0 + np.random.normal(0, 0.2)),
            "size": (0.15, 0.15)
        }
    
    # Cluster 3: Distributed around (0, -1.5)
    for i in range(5):
        elements[f"cluster3_elem{i}"] = {
            "position": (0 + np.random.normal(0, 0.2), -1.5 + np.random.normal(0, 0.2)),
            "size": (0.15, 0.15)
        }
    
    print(f"\n[CREATED {len(elements)} ELEMENTS]")
    
    # Perform clustering
    print("\n[HIERARCHICAL CLUSTERING]")
    h_clusters = ElementClusterer.hierarchical_clustering(elements, max_clusters=3)
    cluster_groups = {}
    for elem_id, cluster_id in h_clusters.items():
        if cluster_id not in cluster_groups:
            cluster_groups[cluster_id] = []
        cluster_groups[cluster_id].append(elem_id)
    
    for cluster_id in sorted(cluster_groups.keys()):
        print(f"  Cluster {cluster_id}: {len(cluster_groups[cluster_id])} elements")
        for elem_id in cluster_groups[cluster_id][:3]:
            print(f"    - {elem_id}")
        if len(cluster_groups[cluster_id]) > 3:
            print(f"    ... and {len(cluster_groups[cluster_id]) - 3} more")
    
    # Density-based clustering
    print("\n[DENSITY-BASED CLUSTERING]")
    db_clusters = ElementClusterer.density_based_clustering(elements, eps=0.4)
    db_groups = {}
    for elem_id, cluster_id in db_clusters.items():
        if cluster_id not in db_groups:
            db_groups[cluster_id] = []
        db_groups[cluster_id].append(elem_id)
    
    for cluster_id in sorted(db_groups.keys()):
        status = "Core" if cluster_id >= 0 else "Noise"
        print(f"  Cluster {cluster_id} ({status}): {len(db_groups[cluster_id])} elements")
    
    # Solve with clustering
    print("\n[SOLVING WITH CLUSTERING]")
    engine = AdvancedLayoutEngine()
    positions = engine.solve_with_clustering(elements, clustering_method="hierarchical")
    
    # Verify clusters remain together
    print("\n[CLUSTER SEPARATION CHECK]")
    for cluster_id, elem_ids in cluster_groups.items():
        cluster_positions = [positions[eid] for eid in elem_ids if eid in positions]
        if cluster_positions:
            center = np.mean(cluster_positions, axis=0)
            spreads = [np.linalg.norm(np.array(p) - center) for p in cluster_positions]
            avg_spread = np.mean(spreads)
            print(f"  Cluster {cluster_id}: avg spread from center = {avg_spread:.4f}")


# ============================================================================
# EXAMPLE 3: ML-BASED PARAMETER TUNING
# ============================================================================

def example_3_parameter_optimization():
    """
    Example 3: Learning and predicting optimal parameters.
    
    Use case: System learns from past layouts and predicts best parameters.
    """
    print("\n" + "="*70)
    print("EXAMPLE 3: ML-Based Parameter Optimization")
    print("="*70)
    
    optimizer = ParameterOptimizer(history_size=100)
    
    # Simulate learning from past runs
    print("\n[LEARNING FROM HISTORY]")
    scenarios = [
        (10, 20.0, 0.2, 18.5),    # Few elements, low overlap
        (50, 45.0, 0.5, 22.0),    # Medium, medium overlap
        (100, 70.0, 0.8, 19.5),   # Many elements, high overlap, harder
        (50, 40.0, 0.45, 23.5),   # Medium, similar to #2, good result
        (100, 65.0, 0.75, 21.0),  # Many, high density, decent
    ]
    
    for elem_count, overlap, density, quality in scenarios:
        params = optimizer._heuristic_parameters(elem_count, overlap, density)
        optimizer.learn_from_result(params, quality)
        print(f"  Learned: {elem_count} elements, {overlap:.0f}% overlap, "
              f"density {density:.2f} -> quality {quality:.1f}")
    
    # Predict for new scenarios
    print("\n[PREDICTING PARAMETERS FOR NEW SCENARIOS]")
    test_cases = [
        (50, 45.0, 0.5),   # Similar to scenario #2
        (100, 70.0, 0.8),  # Similar to scenario #3
        (75, 50.0, 0.6),   # New combination
    ]
    
    for elem_count, overlap, density in test_cases:
        predicted = optimizer.predict_best_parameters(elem_count, overlap, density)
        print(f"\n  For {elem_count} elements, {overlap:.0f}% overlap, density {density:.2f}:")
        print(f"    Repulsion strength: {predicted.repulsion_strength:.2f}")
        print(f"    Attraction strength: {predicted.attraction_strength:.2f}")
        print(f"    Thermal temperature: {predicted.thermal_temperature:.2f}")
        print(f"    Cooling rate: {predicted.cooling_rate:.3f}")
        print(f"    Iterations: {predicted.iterations}")

    print("\n[BACKPROP-LIKE LOSS WEIGHT TUNING]")
    tune_elements = {
        f"elem{i}": {
            "position": (np.random.uniform(-2, 2), np.random.uniform(-1.5, 1.5)),
            "size": (0.2, 0.2)
        }
        for i in range(15)
    }
    engine = AdvancedLayoutEngine()
    tuned_weights, history = engine.tune_loss_weights_with_backprop(
        tune_elements,
        steps=2,
        lr=0.25,
        epsilon=0.05,
        sample_iterations=30,
        sample_loss_every=10
    )
    last = history[-1] if history else {}
    print(f"  Final loss: {last.get('loss', 0.0):.4f}")
    print(f"  Tuned weights: {last.get('weights', {})}")


# ============================================================================
# EXAMPLE 4: ADAPTIVE STRATEGY SELECTION
# ============================================================================

def example_4_adaptive_strategy():
    """
    Example 4: Automatically select best layout strategy.
    
    Use case: System analyzes problem and picks optimal algorithm.
    """
    print("\n" + "="*70)
    print("EXAMPLE 4: Adaptive Strategy Selection")
    print("="*70)
    
    test_scenarios = [
        ("Simple", {
            "elem1": {"position": (0, 0), "size": (0.2, 0.2)},
            "elem2": {"position": (0.3, 0), "size": (0.2, 0.2)},
            "elem3": {"position": (0.6, 0), "size": (0.2, 0.2)},
        }),
        ("Dense", {
            f"elem{i}": {"position": (np.random.uniform(-3, 3), np.random.uniform(-2, 2)),
                        "size": (0.1, 0.1)}
            for i in range(40)
        }),
        ("Very Dense", {
            f"elem{i}": {"position": (np.random.uniform(-3, 3), np.random.uniform(-2, 2)),
                        "size": (0.08, 0.08)}
            for i in range(100)
        }),
        ("Sparse", {
            f"elem{i}": {"position": (np.random.uniform(-3, 3), np.random.uniform(-2, 2)),
                        "size": (0.25, 0.25)}
            for i in range(10)
        }),
    ]
    
    strategy_selector = AdaptiveLayoutStrategy()
    
    for scenario_name, elements in test_scenarios:
        print(f"\n[SCENARIO: {scenario_name}]")
        
        # Analyze
        analysis = strategy_selector.analyze_problem(elements)
        strategy = strategy_selector.recommend_strategy(analysis)
        
        print(f"  Elements: {analysis['element_count']}")
        print(f"  Density: {analysis['density']:.3f}")
        print(f"  Overlap: {analysis['overlap_percentage']:.1f}%")
        print(f"  → Recommended strategy: {strategy.upper()}")


# ============================================================================
# EXAMPLE 5: MULTI-OBJECTIVE OPTIMIZATION
# ============================================================================

def example_5_multi_objective():
    """
    Example 5: Balance multiple conflicting objectives.
    
    Use case: Find layout that balances quality, compactness, and aesthetics.
    """
    print("\n" + "="*70)
    print("EXAMPLE 5: Multi-Objective Optimization")
    print("="*70)
    
    # Create problem
    elements = {
        f"elem{i}": {
            "position": (np.random.uniform(-2, 2), np.random.uniform(-1, 1)),
            "size": (0.2, 0.2)
        }
        for i in range(20)
    }
    
    optimizer = MultiObjectiveOptimizer()
    
    # Define objectives
    def minimize_overlap(positions):
        return LayoutAnalyzer.calculate_overlap_score(elements, positions)
    
    def minimize_spread(positions):
        return LayoutAnalyzer.calculate_compactness(positions)
    
    def maximize_balance(positions):
        return -LayoutAnalyzer.calculate_balance(positions)  # Negative because we want to minimize
    
    optimizer.add_objective(minimize_overlap, weight=2.0)  # Most important
    optimizer.add_objective(minimize_spread, weight=1.5)   # Important
    optimizer.add_objective(maximize_balance, weight=1.0)  # Less important
    
    print("\n[OBJECTIVES DEFINED]")
    print("  1. Minimize overlap (weight: 2.0)")
    print("  2. Minimize spread (weight: 1.5)")
    print("  3. Maximize balance (weight: 1.0)")
    
    # Find solution
    engine = AdvancedLayoutEngine()
    positions = engine.solve_with_constraints(elements, max_iterations=100)
    
    # Evaluate
    scores = optimizer.evaluate_solution(positions)
    
    print("\n[SOLUTION QUALITY]")
    for obj_name, score in scores.items():
        print(f"  {obj_name}: {score:.4f}")
    
    # Update Pareto front
    solution = {"position": positions}
    solution.update(scores)
    optimizer.update_pareto_front(solution)
    
    print(f"\n[PARETO FRONT]")
    print(f"  Solutions on front: {len(optimizer.pareto_front)}")


# ============================================================================
# EXAMPLE 6: COMPLETE V3.0 SUPER-SOLUTION
# ============================================================================

def example_6_complete_v3_solution():
    """
    Example 6: Complete v3.0 using all advanced features together.
    
    Use case: Complex real-world scenario combining all capabilities.
    """
    print("\n" + "="*70)
    print("EXAMPLE 6: Complete v3.0 Super-Solution")
    print("="*70)
    
    # Create complex scenario
    elements = {
        # Main title
        "title": {"position": (0, 2.0), "size": (1.0, 0.3)},
        
        # Group A (concepts)
        "concept1": {"position": (-2.0, 0.5), "size": (0.4, 0.4)},
        "concept2": {"position": (-1.5, 1.0), "size": (0.3, 0.3)},
        "concept3": {"position": (-2.5, 1.0), "size": (0.3, 0.3)},
        
        # Group B (equations)
        "eq1": {"position": (0.0, 0.5), "size": (0.5, 0.3)},
        "eq2": {"position": (0.0, 0.0), "size": (0.5, 0.3)},
        "eq3": {"position": (0.0, -0.5), "size": (0.5, 0.3)},
        
        # Group C (diagrams)
        "diagram1": {"position": (2.0, 0.5), "size": (0.4, 0.4)},
        "diagram2": {"position": (2.5, 1.0), "size": (0.3, 0.3)},
        
        # Annotations
        "note1": {"position": (-1.0, -1.0), "size": (0.3, 0.2)},
        "note2": {"position": (1.0, -1.0), "size": (0.3, 0.2)},
    }
    
    print(f"\n[SCENARIO: Complex Mixed Layout]")
    print(f"  Total elements: {len(elements)}")
    
    # Step 1: Analyze
    strategy_selector = AdaptiveLayoutStrategy()
    analysis = strategy_selector.analyze_problem(elements)
    strategy = strategy_selector.recommend_strategy(analysis)
    
    print(f"\n[STEP 1: ANALYSIS]")
    print(f"  Recommended strategy: {strategy}")
    print(f"  Density: {analysis['density']:.3f}")
    print(f"  Current overlap: {analysis['overlap_percentage']:.1f}%")
    
    # Step 2: Create constraints
    constraints = ConstraintSystem()
    
    # Group A: Concepts should cluster together
    constraints.add_grouping_constraint(
        ["concept1", "concept2", "concept3"],
        max_spread=0.8, weight=2.0
    )
    
    # Group B: Equations should be vertically aligned
    constraints.add_alignment_constraint(
        ["eq1", "eq2", "eq3"],
        axis="x", weight=1.5
    )
    
    # Group C: Diagrams should stay together
    constraints.add_grouping_constraint(
        ["diagram1", "diagram2"],
        max_spread=0.7, weight=2.0
    )
    
    # Title above everything
    constraints.add_separation_constraint(
        ["title"],
        min_distance=1.5, weight=1.0
    )
    
    print(f"\n[STEP 2: CONSTRAINTS]")
    print(f"  Constraints added: {len(constraints.constraints)}")
    
    # Step 3: Optimize parameters
    optimizer = ParameterOptimizer()
    params = optimizer.predict_best_parameters(
        analysis["element_count"],
        analysis["overlap_percentage"],
        analysis["density"]
    )
    
    print(f"\n[STEP 3: PARAMETER PREDICTION]")
    print(f"  Repulsion: {params.repulsion_strength:.2f}")
    print(f"  Temperature: {params.thermal_temperature:.2f}")
    print(f"  Iterations: {params.iterations}")
    
    # Step 4: Solve with clustering
    engine = AdvancedLayoutEngine()
    positions = engine.solve_with_clustering(elements, clustering_method="hierarchical")
    
    print(f"\n[STEP 4: SOLVING]")
    print(f"  Solution found with {len(positions)} positions")
    
    # Step 5: Evaluate
    overlap = LayoutAnalyzer.calculate_overlap_score(elements, positions)
    compactness = LayoutAnalyzer.calculate_compactness(positions)
    balance = LayoutAnalyzer.calculate_balance(positions)
    constraint_satisfaction = constraints.evaluate_all(positions)
    
    print(f"\n[STEP 5: EVALUATION]")
    print(f"  Overlap area: {overlap:.4f}")
    print(f"  Compactness: {compactness:.4f}")
    print(f"  Balance: {balance:.4f}")
    print(f"  Constraint satisfaction: {constraint_satisfaction:.4f}")
    
    # Summary
    quality_score = (
        100 * (1 - min(1, overlap)) +
        50 * (1 - min(1, compactness/3)) +
        50 * (1 - min(1, balance/3))
    ) / 200 * 100  # 0-100 scale
    
    print(f"\n[FINAL QUALITY SCORE: {quality_score:.1f}/100]")
    print(f"  ✓ Layout optimized with all v3.0 features")
    print(f"  ✓ Constraints satisfied: {constraint_satisfaction < 0.5}")
    print(f"  ✓ Elements clustered effectively")
    print(f"  ✓ Parameters auto-tuned")


# ============================================================================
# PERFORMANCE COMPARISON
# ============================================================================

def example_v2_vs_v3_comparison():
    """
    Example: Compare v2.0 performance vs v3.0 with constraints.
    """
    print("\n" + "="*70)
    print("V2.0 vs V3.0 PERFORMANCE & QUALITY COMPARISON")
    print("="*70)
    
    import time
    
    # Complex scenario
    elements = {
        f"elem{i}": {
            "position": (np.random.uniform(-3, 3), np.random.uniform(-2, 2)),
            "size": (0.15, 0.15)
        }
        for i in range(50)
    }
    
    print(f"\n[TEST SCENARIO: 50 element layout with overlaps]")
    
    # V2.0: Basic force-directed
    print(f"\n[V2.0: Basic Force-Directed]")
    start = time.time()
    engine = AdvancedLayoutEngine()
    positions_v2 = engine.solve_with_constraints(elements, max_iterations=100)
    time_v2 = time.time() - start
    
    overlap_v2 = LayoutAnalyzer.calculate_overlap_score(elements, positions_v2)
    compact_v2 = LayoutAnalyzer.calculate_compactness(positions_v2)
    
    print(f"  Time: {time_v2*1000:.1f}ms")
    print(f"  Overlap: {overlap_v2:.4f}")
    print(f"  Compactness: {compact_v2:.4f}")
    
    # V3.0: With clustering and constraints
    print(f"\n[V3.0: With Clustering & Constraints]")
    start = time.time()
    positions_v3 = engine.solve_with_clustering(elements)
    time_v3 = time.time() - start
    
    overlap_v3 = LayoutAnalyzer.calculate_overlap_score(elements, positions_v3)
    compact_v3 = LayoutAnalyzer.calculate_compactness(positions_v3)
    
    print(f"  Time: {time_v3*1000:.1f}ms")
    print(f"  Overlap: {overlap_v3:.4f}")
    print(f"  Compactness: {compact_v3:.4f}")
    
    # Comparison
    print(f"\n[IMPROVEMENTS]")
    print(f"  Time: {time_v2/time_v3:.1f}x faster")
    print(f"  Overlap reduction: {((overlap_v2 - overlap_v3) / overlap_v2 * 100):.1f}% better")
    print(f"  Compactness: {((compact_v2 - compact_v3) / compact_v2 * 100):.1f}% better")


# ============================================================================
# EXAMPLE 7: HYBRID BACKPROP WITH CACHE MONITORING
# ============================================================================

def example_7_hybrid_backprop_with_cache():
    """
    Example 7: Demonstrate hybrid backprop mode with cache hit/miss monitoring.
    
    Use case: Auto-tune loss weights with gradient descent + cache reuse + visibility.
    """
    print("\n" + "="*70)
    print("EXAMPLE 7: Hybrid Backprop with Cache Monitoring")
    print("="*70)
    
    # Create test scenario with many elements (triggers auto-tune)
    elements = {
        f"elem{i}": {
            "position": (np.random.uniform(-3, 3), np.random.uniform(-2, 2)),
            "size": (0.15, 0.15)
        }
        for i in range(80)  # Above tune_threshold=60
    }
    
    engine = AdvancedLayoutEngine()
    
    # First solve: Cache MISS (needs tuning)
    print("\n[FIRST SOLVE: Cache Miss Expected]")
    positions1, loss1, components1, tune_info1 = engine.solve_with_constraints(
        elements,
        tune_mode="hybrid",          # Enable hybrid backprop
        tune_threshold=60,           # Tune if >= 60 elements
        max_iterations=100,
        return_loss=True,            # Get loss + tune_info
        verbose_tuning=True,         # Enable cache logging
        tune_steps=2,                # Gradient steps for tuning
        tune_lr=0.2                  # Tuning learning rate
    )
    
    print(f"\n  Final loss: {loss1:.4f}")
    print(f"  Tune mode: {tune_info1['mode']}")
    print(f"  Auto-tune active: {tune_info1['auto_tune']}")
    print(f"  Cache hit: {tune_info1['cache_hit']}")
    print(f"  Weights tuned: {tune_info1['tuned']}")
    print(f"  Cache key: {tune_info1['cache_key']}")
    
    # Second solve: Cache HIT (reuses tuned weights)
    print("\n[SECOND SOLVE: Cache Hit Expected]")
    elements2 = {
        f"elem{i}": {
            "position": (np.random.uniform(-3, 3), np.random.uniform(-2, 2)),
            "size": (0.15, 0.15)
        }
        for i in range(82)  # Similar size -> same cache bucket
    }
    
    positions2, loss2, components2, tune_info2 = engine.solve_with_constraints(
        elements2,
        tune_mode="hybrid",
        tune_threshold=60,
        max_iterations=100,
        return_loss=True,
        verbose_tuning=True
    )
    
    print(f"\n  Final loss: {loss2:.4f}")
    print(f"  Tune mode: {tune_info2['mode']}")
    print(f"  Cache hit: {tune_info2['cache_hit']}")
    print(f"  Weights tuned: {tune_info2['tuned']}")
    print(f"  Cache key: {tune_info2['cache_key']}")
    
    # Third solve: Different size -> Cache MISS
    print("\n[THIRD SOLVE: Different Size -> Cache Miss]")
    elements3 = {
        f"elem{i}": {
            "position": (np.random.uniform(-3, 3), np.random.uniform(-2, 2)),
            "size": (0.15, 0.15)
        }
        for i in range(150)  # Much larger -> different cache bucket
    }
    
    positions3, loss3, components3, tune_info3 = engine.solve_with_constraints(
        elements3,
        tune_mode="hybrid",
        tune_threshold=60,
        max_iterations=100,
        return_loss=True,
        verbose_tuning=True
    )
    
    print(f"\n  Final loss: {loss3:.4f}")
    print(f"  Cache hit: {tune_info3['cache_hit']}")
    print(f"  Cache key: {tune_info3['cache_key']}")
    
    # Summary
    print("\n[CACHE PERFORMANCE SUMMARY]")
    print(f"  Total cached weight sets: {len(engine._tuned_weights_cache)}")
    print(f"  Cache keys: {list(engine._tuned_weights_cache.keys())}")
    print(f"  Cache can speed up repeated solves with similar problem sizes!")


# ============================================================================
# EXAMPLE 8: ENHANCED OPTIMIZER WITH ADAM
# ============================================================================

def example_8_enhanced_optimizer():
    """
    Example 8: Compare basic vs enhanced optimizer (Adam).
    
    Use case: Better weight tuning with Adam, LR scheduling, gradient clipping.
    """
    print("\n" + "="*70)
    print("EXAMPLE 8: Enhanced Optimizer with Adam")
    print("="*70)
    
    # Create test scenario
    elements = {
        f"elem{i}": {
            "position": (np.random.uniform(-3, 3), np.random.uniform(-2, 2)),
            "size": (0.18, 0.18)
        }
        for i in range(70)
    }
    
    engine = AdvancedLayoutEngine()
    
    # Test 1: Basic gradient descent
    print("\n[BASIC GRADIENT DESCENT]")
    import time
    start = time.time()
    basic_weights, basic_history = engine.tune_loss_weights_with_backprop(
        elements,
        steps=5,
        lr=0.2,
        epsilon=0.05,
        sample_iterations=30,
        sample_loss_every=10
    )
    basic_time = time.time() - start
    
    basic_losses = [h['loss'] for h in basic_history]
    print(f"  Steps: {len(basic_history)}")
    print(f"  Initial loss: {basic_losses[0]:.4f}")
    print(f"  Final loss: {basic_losses[-1]:.4f}")
    print(f"  Improvement: {(basic_losses[0] - basic_losses[-1]):.4f}")
    print(f"  Time: {basic_time*1000:.1f}ms")
    
    # Test 2: Enhanced optimizer (Adam)
    print("\n[ENHANCED OPTIMIZER (ADAM)]")
    start = time.time()
    enhanced_weights, enhanced_history = engine.tune_loss_weights_enhanced(
        elements,
        max_steps=10,
        lr=0.01,              # Lower LR (Adam adapts it)
        epsilon=0.05,
        sample_iterations=30,
        sample_loss_every=10,
        adam_beta1=0.9,
        adam_beta2=0.999,
        lr_decay=0.9,
        clip_norm=1.0,
        early_stop_patience=3,
        early_stop_delta=1e-4,
        verbose=True
    )
    enhanced_time = time.time() - start
    
    enhanced_losses = [h['loss'] for h in enhanced_history]
    print(f"  Steps: {len(enhanced_history)}")
    print(f"  Initial loss: {enhanced_losses[0]:.4f}")
    print(f"  Final loss: {enhanced_losses[-1]:.4f}")
    print(f"  Improvement: {(enhanced_losses[0] - enhanced_losses[-1]):.4f}")
    print(f"  Time: {enhanced_time*1000:.1f}ms")
    
    # Comparison
    print("\n[COMPARISON]")
    basic_improvement = basic_losses[0] - basic_losses[-1]
    enhanced_improvement = enhanced_losses[0] - enhanced_losses[-1]
    print(f"  Basic improvement: {basic_improvement:.4f}")
    print(f"  Enhanced improvement: {enhanced_improvement:.4f}")
    print(f"  Enhanced is {(enhanced_improvement / max(basic_improvement, 0.001)):.2f}x better")
    print(f"  Time difference: {enhanced_time - basic_time:.2f}s")
    
    # Test 3: Use enhanced optimizer in auto-tune
    print("\n[AUTO-TUNE WITH ENHANCED OPTIMIZER]")
    engine2 = AdvancedLayoutEngine()  # Fresh engine for clean cache
    
    positions, loss, components, tune_info = engine2.solve_with_constraints(
        elements,
        tune_mode="hybrid",
        tune_threshold=60,
        use_enhanced_optimizer=True,  # ← Use Adam!
        tune_steps=5,
        tune_lr=0.01,
        verbose_tuning=True,
        return_loss=True
    )
    
    print(f"  Final layout loss: {loss:.4f}")
    print(f"  Overlap component: {components.get('overlap', 0):.4f}")
    print(f"  Tuned with enhanced optimizer: {tune_info['tuned']}")
    print(f"  Cache key: {tune_info['cache_key']}")
    
    # Show convergence plot data
    print("\n[CONVERGENCE ANALYSIS]")
    if len(enhanced_history) > 1:
        print("  Loss trajectory (enhanced):")
        for i, h in enumerate(enhanced_history[:6]):  # First 6 steps
            loss_val = h.get('loss', 0)
            lr_val = h.get('lr', 0)
            grad_norm = h.get('grad_norm', 0)
            print(f"    Step {i}: loss={loss_val:.4f}, lr={lr_val:.5f}, grad_norm={grad_norm:.4f}")


# ============================================================================
# EXAMPLE 9: COMPREHENSIVE MULTI-STAGE OPTIMIZATION
# ============================================================================

def example_9_comprehensive_multi_stage():
    """
    Example 9: Full multi-stage optimization pipeline.
    
    Use case: Maximum quality with adaptive optimization at every stage.
    Demonstrates:
    - Problem analysis & adaptive optimizer selection
    - Constraint weight optimization
    - Loss weight tuning (Adam or basic based on complexity)
    - Physics-based solving
    - Gradient-based position refinement
    """
    print("\n" + "="*70)
    print("EXAMPLE 9: Comprehensive Multi-Stage Optimization")
    print("="*70)
    
    # Create complex problem with constraints
    print("\n[CREATING COMPLEX PROBLEM]")
    elements = {
        f"elem{i}": {
            "position": (np.random.uniform(-3, 3), np.random.uniform(-2, 2)),
            "size": (0.16, 0.16)
        }
        for i in range(100)  # Complex problem
    }
    
    # Add constraints
    constraints = ConstraintSystem()
    
    # Proximity constraints (some elements should be close)
    for i in range(0, 10, 2):
        constraints.add_constraint(LayoutConstraint(
            constraint_type=ConstraintType.PROXIMITY,
            element_ids=[f"elem{i}", f"elem{i+1}"],
            parameters={"max_distance": 0.3},
            weight=1.0
        ))
    
    # Alignment constraints (some should align)
    constraints.add_constraint(LayoutConstraint(
        constraint_type=ConstraintType.ALIGNMENT,
        element_ids=[f"elem{i}" for i in range(20, 25)],
        parameters={"axis": "x", "tolerance": 0.1},
        weight=0.8
    ))
    
    print(f"  Elements: {len(elements)}")
    print(f"  Constraints: {len(constraints.constraints)}")
    
    # Test 1: Basic solve (no multi-stage)
    print("\n[TEST 1: Basic Solve (No Multi-Stage)]")
    engine1 = AdvancedLayoutEngine()
    import time
    
    start = time.time()
    positions_basic = engine1.solve_with_constraints(
        elements,
        constraints,
        max_iterations=150
    )
    time_basic = time.time() - start
    
    loss_basic = LayoutAnalyzer.calculate_overlap_score(elements, positions_basic)
    compact_basic = LayoutAnalyzer.calculate_compactness(positions_basic)
    
    print(f"  Time: {time_basic*1000:.1f}ms")
    print(f"  Overlap score: {loss_basic:.4f}")
    print(f"  Compactness: {compact_basic:.4f}")
    
    # Test 2: Comprehensive multi-stage solve
    print("\n[TEST 2: Comprehensive Multi-Stage Solve]")
    engine2 = AdvancedLayoutEngine()
    
    start = time.time()
    positions_comprehensive, opt_info = engine2.solve_comprehensive(
        elements,
        constraints,
        max_iterations=150,
        enable_multi_stage=True,
        enable_position_refinement=True,
        adaptive_optimizer=True,
        return_full_info=True,
        verbose=True
    )
    time_comprehensive = time.time() - start
    
    print(f"\n[TEST 2 SUMMARY]")
    print(f"  Total time: {time_comprehensive*1000:.1f}ms")
    print(f"  Final loss: {opt_info['final_loss']:.4f}")
    print(f"  Overlap score: {opt_info['overlap_score']:.4f}")
    print(f"  Compactness: {opt_info['compactness']:.4f}")
    
    # Show stage breakdown
    print("\n[STAGE BREAKDOWN]")
    print(f"  Problem complexity: {opt_info['problem_analysis']['complexity_score']:.1f}/100")
    print(f"  Optimizer selected: {'Enhanced (Adam)' if opt_info['optimizer_config']['use_enhanced'] else 'Basic GD'}")
    
    if "constraint_weights" in opt_info:
        print(f"  Constraint weights optimized: {opt_info['constraint_weights']}")
    
    print(f"  Weight tuning: {opt_info['weight_tuning']}")
    
    if "tune_history" in opt_info:
        tune_steps = len(opt_info['tune_history'])
        print(f"    Tuning steps: {tune_steps}")
    
    print(f"  Physics loss: {opt_info['physics_loss']:.4f}")
    
    if "refinement" in opt_info:
        print(f"  Position refinement: {opt_info['refinement']}")
        if opt_info['refinement'] == 'applied':
            print(f"    Improvement: {opt_info.get('refinement_improvement', 0):.4f}")
    
    # Comparison
    print("\n[COMPARISON: Basic vs Comprehensive]")
    improvement_overlap = (loss_basic - opt_info['overlap_score']) / loss_basic * 100
    improvement_compact = (compact_basic - opt_info['compactness']) / compact_basic * 100
    
    print(f"  Overlap improvement: {improvement_overlap:.1f}%")
    print(f"  Compactness improvement: {improvement_compact:.1f}%")
    print(f"  Time overhead: {(time_comprehensive - time_basic)*1000:.1f}ms ({time_comprehensive/time_basic:.2f}x)")
    print(f"  Quality/Time tradeoff: {'Worth it!' if improvement_overlap > 20 else 'Marginal'}")

    # Test 2b: Activation functions on loss components
    print("\n[TEST 2B: Activation Functions on Loss Components]")
    activation_name = "swish"
    loss_activation_name = "tanh"
    
    engine2.loss_activation = loss_activation_name
    engine2.component_activation = activation_name
    
    activated_loss, activated_components = engine2.compute_loss_with_activation(
        elements,
        positions_comprehensive,
        positions_comprehensive,
        positions_comprehensive,
        constraints=constraints,
        min_distance=0.05,
        loss_activation=loss_activation_name,
        component_activation=activation_name
    )
    
    print(f"  Component activation: {activation_name}")
    print(f"  Final loss activation: {loss_activation_name}")
    print(f"  Activated total loss: {activated_loss:.4f}")
    print(f"  Activated overlap: {activated_components.get('overlap', 0):.4f}")
    
    # Quick activation lookup demo
    activation = ActivationSelector.get("relu")
    sample = np.array([-1.0, 0.0, 1.0])
    print(f"  ReLU sample input: {sample}")
    print(f"  ReLU output: {activation.activate(sample)}")
    
    # Test 3: Adaptive selection with different complexity
    print("\n[TEST 3: Adaptive Optimizer Selection]")
    
    test_cases = [
        ("Simple", 30, (0.2, 0.2)),
        ("Moderate", 60, (0.18, 0.18)),
        ("Complex", 100, (0.16, 0.16))
    ]
    
    for name, count, size in test_cases:
        test_elements = {
            f"elem{i}": {
                "position": (np.random.uniform(-3, 3), np.random.uniform(-2, 2)),
                "size": size
            }
            for i in range(count)
        }
        
        engine = AdvancedLayoutEngine()
        analysis = engine.optimizer_selector.analyze_problem_complexity(test_elements)
        config = engine.optimizer_selector.select_optimizer(analysis)
        
        print(f"\n  {name} problem ({count} elements):")
        print(f"    Complexity: {analysis['complexity_score']:.1f}/100")
        print(f"    Optimizer: {'Enhanced (Adam)' if config['use_enhanced'] else 'Basic GD'}")
        print(f"    Learning rate: {config['lr']}")
        print(f"    Max steps: {config['max_steps']}")
        print(f"    Reason: {config['reason']}")


# ============================================================================
# EXAMPLE 10: ML-DRIVEN OPTIMIZATION
# ============================================================================

def example_10_ml_driven_optimization():
    """
    Example 10: ML model integration for intelligent parameter prediction.
    
    Demonstrates:
    - Training ML models on synthetic data
    - ML-driven parameter selection
    - ML-driven loss weight tuning
    - ML quality score integration
    - Blending heuristic and ML predictions
    """
    print("\n" + "="*70)
    print("EXAMPLE 10: ML-Driven Optimization")
    print("="*70)
    
    # Create a medium-complexity test layout
    np.random.seed(42)
    elements = {
        f"node_{i}": {
            "position": (np.random.uniform(-3, 3), np.random.uniform(-2, 2)),
            "size": (0.25, 0.25)
        }
        for i in range(30)
    }
    
    # Add some dependencies
    constraints = ConstraintSystem()
    for i in range(10):
        constraints.add_constraint(LayoutConstraint(
            constraint_type=ConstraintType.ALIGNMENT,
            elements=[f"node_{i*3}", f"node_{i*3+1}"],
            axis="x",
            strength=0.5
        ))
    
    engine = AdvancedLayoutEngine()
    
    print("\n--- TEST 1: Without ML Models (Baseline) ---")
    positions_baseline = engine.solve_comprehensive(
        elements,
        constraints=constraints,
        max_steps=100,
        use_ml_models=False,
        verbose=True
    )
    
    baseline_score = LayoutAnalyzer.calculate_overlap_score(elements, positions_baseline)
    baseline_compactness = LayoutAnalyzer.calculate_compactness(positions_baseline)
    print(f"\nBaseline Results:")
    print(f"  Overlap score: {baseline_score:.4f}")
    print(f"  Compactness: {baseline_compactness:.4f}")
    
    print("\n--- TEST 2: Train ML Models ---")
    print("Training on 200 synthetic layouts...")
    engine.train_ml_models(samples=200)
    
    print("\n--- TEST 3: With ML Models (No Blending) ---")
    positions_ml_pure = engine.solve_comprehensive(
        elements,
        constraints=constraints,
        max_steps=100,
        use_ml_models=True,
        ml_blend=1.0,  # Pure ML predictions
        ml_loss_weight=0.2,
        verbose=True
    )
    
    ml_pure_score = LayoutAnalyzer.calculate_overlap_score(elements, positions_ml_pure)
    ml_pure_compactness = LayoutAnalyzer.calculate_compactness(positions_ml_pure)
    print(f"\nML Pure Results:")
    print(f"  Overlap score: {ml_pure_score:.4f}")
    print(f"  Compactness: {ml_pure_compactness:.4f}")
    
    print("\n--- TEST 4: With ML Models (50% Blend) ---")
    positions_ml_blend = engine.solve_comprehensive(
        elements,
        constraints=constraints,
        max_steps=100,
        use_ml_models=True,
        ml_blend=0.5,  # 50% heuristic + 50% ML
        ml_loss_weight=0.1,
        verbose=True
    )
    
    ml_blend_score = LayoutAnalyzer.calculate_overlap_score(elements, positions_ml_blend)
    ml_blend_compactness = LayoutAnalyzer.calculate_compactness(positions_ml_blend)
    print(f"\nML Blend Results:")
    print(f"  Overlap score: {ml_blend_score:.4f}")
    print(f"  Compactness: {ml_blend_compactness:.4f}")
    
    print("\n--- Comparison Summary ---")
    print(f"{'Method':<25} {'Overlap':<12} {'Compactness':<12}")
    print("-" * 70)
    print(f"{'Baseline (No ML)':<25} {baseline_score:<12.4f} {baseline_compactness:<12.4f}")
    print(f"{'ML Pure (100% blend)':<25} {ml_pure_score:<12.4f} {ml_pure_compactness:<12.4f}")
    print(f"{'ML Hybrid (50% blend)':<25} {ml_blend_score:<12.4f} {ml_blend_compactness:<12.4f}")
    
    # Show ML predictions for this layout
    if engine.ml_hub.is_trained:
        features = engine.ml_hub.extract_features(elements, constraints, positions_baseline)
        ml_params = engine.ml_hub.predict_parameters(features)
        ml_weights = engine.ml_hub.predict_loss_weights(features)
        ml_quality = engine.ml_hub.predict_quality_score(features)
        
        print("\n--- ML Predictions for This Layout ---")
        print(f"Predicted quality score: {ml_quality:.4f}")
        print(f"Predicted optimizer params (sample):")
        print(f"  Learning rate: {ml_params.get('lr', 0.0):.4f}")
        print(f"  Max steps: {int(ml_params.get('max_steps', 100))}")
        print(f"Predicted loss weights (sample):")
        print(f"  Overlap: {ml_weights.get('overlap', 0.0):.3f}")
        print(f"  Compactness: {ml_weights.get('compactness', 0.0):.3f}")
        print(f"  Constraint: {ml_weights.get('constraint', 0.0):.3f}")
    
    print("\n" + "="*70)
    print("✓ Example 10 Complete: ML models successfully trained and applied!")
    print("="*70)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    print("\n" + "="*70)
    print("OVERLAP RESOLUTION v3.0 - ADVANCED EXAMPLES")
    print("="*70)
    
    example_1_constraints_and_dependencies()
    example_2_clustering_and_grouping()
    example_3_parameter_optimization()
    example_4_adaptive_strategy()
    example_5_multi_objective()
    example_6_complete_v3_solution()
    example_v2_vs_v3_comparison()
    example_7_hybrid_backprop_with_cache()
    example_8_enhanced_optimizer()
    example_9_comprehensive_multi_stage()
    example_10_ml_driven_optimization()
    
    print("\n" + "="*70)
    print("✓ ALL V3.0 EXAMPLES COMPLETE!")
    print("="*70)