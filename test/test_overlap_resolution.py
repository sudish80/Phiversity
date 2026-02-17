#!/usr/bin/env python
"""
Quick test to diagnose overlap resolution issues.
"""

import sys
sys.path.insert(0, 'scripts')

import numpy as np
from overlap_resolution_v3_advanced import AdvancedLayoutEngine, LayoutAnalyzer

print("\n" + "="*70)
print("OVERLAP RESOLUTION DIAGNOSTIC TEST")
print("="*70)

# Test 1: Simple 2-element overlap
print("\n[TEST 1] Simple 2-Element Overlap")
elements_simple = {
    "A": {"position": (0, 0), "size": (0.5, 0.5)},
    "B": {"position": (0.3, 0.3), "size": (0.5, 0.5)}  # Overlapping!
}

engine = AdvancedLayoutEngine()
initial_overlap = LayoutAnalyzer.calculate_overlap_score(elements_simple, 
    {k: v["position"] for k, v in elements_simple.items()})

print(f"Initial overlap: {initial_overlap:.6f}")
if initial_overlap > 0.01:
    print("  ✗ Elements OVERLAPPING (overlap > 0.01)")
else:
    print("  ✓ Elements NOT overlapping")

# Solve
positions = engine.solve_with_constraints(elements_simple, max_iterations=200)
final_overlap = LayoutAnalyzer.calculate_overlap_score(elements_simple, positions)

print(f"\nAfter solve:")
print(f"  Position A: {positions['A']}")
print(f"  Position B: {positions['B']}")
print(f"  Distance: {np.linalg.norm(np.array(positions['A']) - np.array(positions['B'])):.4f}")
print(f"  Final overlap: {final_overlap:.6f}")

if final_overlap > 0.01:
    print("  ✗ STILL OVERLAPPING - Need to fix!")
else:
    print("  ✓ OVERLAPS RESOLVED")

# Test 2: Medium complexity (10 elements)
print("\n[TEST 2] Medium Complexity (10 Elements)")
np.random.seed(42)
elements_medium = {
    f"E{i}": {
        "position": (np.random.uniform(-1, 1), np.random.uniform(-1, 1)),
        "size": (0.2, 0.2)
    }
    for i in range(10)
}

initial_overlap = LayoutAnalyzer.calculate_overlap_score(elements_medium,
    {k: v["position"] for k, v in elements_medium.items()})

print(f"Initial overlap: {initial_overlap:.6f}")

positions_medium = engine.solve_with_constraints(elements_medium, max_iterations=200)
final_overlap_medium = LayoutAnalyzer.calculate_overlap_score(elements_medium, positions_medium)

print(f"Final overlap: {final_overlap_medium:.6f}")
if final_overlap_medium > 0.01:
    print("  ✗ STILL OVERLAPPING")
else:
    print("  ✓ OVERLAPS RESOLVED")

# Test 3: Check repulsion strength
print("\n[TEST 3] Repulsion Parameters")
print(f"  Repulsion strength: {engine.optimizer.predict_best_parameters(10, 50, 0.5).repulsion_strength:.4f}")
print(f"  Min distance: {engine.optimizer.predict_best_parameters(10, 50, 0.5).min_distance:.4f}")

print("\n" + "="*70)
if final_overlap > 0.01 or final_overlap_medium > 0.01:
    print("⚠️  OVERLAP RESOLUTION NEEDS IMPROVEMENT")
    print("   Possible causes:")
    print("   1. Repulsion strength too low")
    print("   2. Not enough iterations")
    print("   3. Learning rate too high/low")
    print("   4. Min distance threshold not enforced")
else:
    print("✓ OVERLAP RESOLUTION WORKING WELL")
print("="*70)
