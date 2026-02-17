#!/usr/bin/env python
"""Quick test of the pipeline validator."""

import sys
import json
from pathlib import Path

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent))

from scripts.pipeline_validator import validate_animation_plan

# Test with simple example
test_plan = {
    "solution": {
        "topic": "Basic Math",
        "steps": [
            {"title": "Count first group", "explanation": "We have 2 items", "latex": None},
            {"title": "Count second group", "explanation": "We have 2 more items", "latex": None},
            {"title": "Add together", "explanation": "2 + 2 = 4", "latex": "2 + 2 = 4"}
        ],
        "final_answer": "4"
    },
    "animation_plan": {
        "overview": "Simple addition",
        "scenes": [
            {
                "id": "scene1",
                "description": "Show first group",
                "voiceover": "We have two items",
                "elements": [
                    {"type": "Circle", "content": "1", "position": "[0, 0, 0]"},
                    {"type": "Circle", "content": "2", "position": "[1, 0, 0]"}
                ]
            },
            {
                "id": "scene2",
                "description": "Show second group",
                "voiceover": "We have two more items",
                "elements": [
                    {"type": "Circle", "content": "3", "position": "[0, 1, 0]"},
                    {"type": "Circle", "content": "4", "position": "[1, 1, 0]"}
                ]
            },
            {
                "id": "scene3",
                "description": "Show result",
                "voiceover": "When we add them together, two plus two equals four",
                "elements": [
                    {"type": "Latex", "content": "2 + 2 = 4", "position": "[0, 0, 0]"}
                ]
            }
        ]
    }
}

print("=" * 60)
print("PIPELINE VALIDATOR TEST")
print("=" * 60)

results = validate_animation_plan(test_plan)

print("\n✓ VALIDATION PASSED\n")
print("Overall Status:", results['overall_status'])
print(f"Step Coverage: {results['step_sequencing']['coverage_percentage']:.1f}%")
print(f"  Total Steps: {results['step_sequencing']['total_steps']}")
print(f"  Covered Steps: {results['step_sequencing']['covered_steps']}")
print(f"\nAudio-Visual Sync:")
print(f"  Sync Error: {results['audio_visual_sync']['sync_error_sec']:.3f}s")
print(f"  Timing Precision: {results['audio_visual_sync']['timing_precision_ms']:.1f}ms")
print(f"\nAdaptive Pacing:")
print(f"  Total Duration: {results['adaptive_pacing']['total_duration_sec']:.1f}s")
print(f"  Number of Scenes: {len(results['adaptive_pacing']['scenes'])}")

if results['recommendations']:
    print(f"\nRecommendations ({len(results['recommendations'])}):")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"  {i}. {rec}")
else:
    print("\n✓ No recommendations - plan is optimal!")

print("\n" + "=" * 60)
print("Full validation report (JSON):")
print("=" * 60)
print(json.dumps(results, indent=2))
