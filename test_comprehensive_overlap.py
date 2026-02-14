#!/usr/bin/env python
"""
Comprehensive overlap resolution test suite.
"""

import sys
sys.path.insert(0, 'scripts')

import numpy as np
from overlap_resolution_v3_advanced import (
    AdvancedLayoutEngine, LayoutAnalyzer, ConstraintSystem, ConstraintType, LayoutConstraint
)

print("\n" + "="*70)
print("COMPREHENSIVE OVERLAP RESOLUTION TEST SUITE")
print("="*70)

engine = AdvancedLayoutEngine()
tests_passed = 0
tests_total = 0

# Test 1: Severe overlap
print("\n[TEST 1] Severe Overlap - All Elements at Same Position")
tests_total += 1
elements = {
    "A": {"position": (0, 0), "size": (0.3, 0.3)},
    "B": {"position": (0, 0), "size": (0.3, 0.3)},
    "C": {"position": (0, 0), "size": (0.3, 0.3)},
}
positions = engine.solve_with_constraints(elements, max_iterations=300)
overlap = LayoutAnalyzer.calculate_overlap_score(elements, positions)
print(f"  Final overlap: {overlap:.6f}")
if overlap < 0.001:
    print("  [PASS]")
    tests_passed += 1
else:
    print("  [FAIL]")

# Test 2: Many elements (30)
print("\n[TEST 2] Many Elements (30)")
tests_total += 1
np.random.seed(42)
elements_many = {
    f"E{i}": {
        "position": (np.random.uniform(-1, 1), np.random.uniform(-1, 1)),
        "size": (0.15, 0.15)
    }
    for i in range(30)
}
positions_many = engine.solve_with_constraints(elements_many, max_iterations=300)
overlap_many = LayoutAnalyzer.calculate_overlap_score(elements_many, positions_many)
print(f"  Final overlap: {overlap_many:.6f}")
if overlap_many < 0.001:
    print("  [PASS]")
    tests_passed += 1
else:
    print("  [FAIL]")

# Test 3: Mixed sizes
print("\n[TEST 3] Mixed Element Sizes")
tests_total += 1
elements_mixed = {
    "small1": {"position": (0, 0), "size": (0.1, 0.1)},
    "small2": {"position": (0.05, 0.05), "size": (0.1, 0.1)},
    "large1": {"position": (0, 0.5), "size": (0.5, 0.5)},
    "large2": {"position": (0, 0.6), "size": (0.5, 0.5)},
}
positions_mixed = engine.solve_with_constraints(elements_mixed, max_iterations=300)
overlap_mixed = LayoutAnalyzer.calculate_overlap_score(elements_mixed, positions_mixed)
print(f"  Final overlap: {overlap_mixed:.6f}")
if overlap_mixed < 0.001:
    print("  [PASS]")
    tests_passed += 1
else:
    print("  [FAIL]")

# Test 4: With constraints
print("\n[TEST 4] With Alignment Constraints")
tests_total += 1
elements_const = {
    "A": {"position": (0, 0), "size": (0.2, 0.2)},
    "B": {"position": (0.2, 0.2), "size": (0.2, 0.2)},
}
constraints = ConstraintSystem()
constraints.add_constraint(LayoutConstraint(
    constraint_type=ConstraintType.ALIGNMENT,
    element_ids=["A", "B"],
    parameters={"axis": "x", "tolerance": 0.3},
    weight=1.0
))
positions_const = engine.solve_with_constraints(
    elements_const,
    constraints=constraints,
    max_iterations=300
)
overlap_const = LayoutAnalyzer.calculate_overlap_score(elements_const, positions_const)
print(f"  Final overlap: {overlap_const:.6f}")
if overlap_const < 0.001:
    print("  [PASS]")
    tests_passed += 1
else:
    print("  [FAIL]")

# Test 5: Large elements
print("\n[TEST 5] Large Elements")
tests_total += 1
elements_large = {
    "L1": {"position": (-1, 0), "size": (1.0, 1.0)},
    "L2": {"position": (1, 0), "size": (1.0, 1.0)},
}
positions_large = engine.solve_with_constraints(elements_large, max_iterations=300)
overlap_large = LayoutAnalyzer.calculate_overlap_score(elements_large, positions_large)
print(f"  Final overlap: {overlap_large:.6f}")
if overlap_large < 0.001:
    print("  [PASS]")
    tests_passed += 1
else:
    print("  [FAIL]")

# Test 6: Random complex layout
print("\n[TEST 6] Random Complex Layout (50 elements)")
tests_total += 1
np.random.seed(123)
elements_complex = {
    f"E{i}": {
        "position": (np.random.uniform(-2, 2), np.random.uniform(-1.5, 1.5)),
        "size": (np.random.uniform(0.08, 0.3), np.random.uniform(0.08, 0.3))
    }
    for i in range(50)
}
positions_complex = engine.solve_with_constraints(elements_complex, max_iterations=300)
overlap_complex = LayoutAnalyzer.calculate_overlap_score(elements_complex, positions_complex)
compactness = LayoutAnalyzer.calculate_compactness(positions_complex)
print(f"  Final overlap: {overlap_complex:.6f}")
print(f"  Compactness: {compactness:.4f}")
if overlap_complex < 0.001:
    print("  [PASS]")
    tests_passed += 1
else:
    print("  [FAIL]")

# Summary
print("\n" + "="*70)
print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
print("="*70)

if tests_passed == tests_total:
    print("\n[TEST SUITE] ALL OVERLAP RESOLUTION TESTS PASSED!")
    print("   Overlaps are now completely eliminated!")
else:
    print(f"\n[TEST SUITE] {tests_total - tests_passed} test(s) failed")
    print("   Some overlap scenarios still need improvement")

print("="*70)
