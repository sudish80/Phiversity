#!/usr/bin/env python3
"""
Test Manim code generation to catch issues before deployment.

Run locally before pushing:
    python -m pytest test/test_manim_generation.py -v
"""
import sys
import tempfile
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.manim_adapter import generate_scene_script


def test_color_import_present():
    """Verify Color import is in generated code."""
    data = {
        "animation_plan": {
            "scenes": [
                {
                    "id": "test",
                    "description": "Test scene",
                    "elements": [
                        {
                            "type": "text",
                            "text": "Test",
                            "style": {"color": "#ffffff"}
                        }
                    ]
                }
            ]
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        code = generate_scene_script(data, f.name)
    
    # Critical checks
    assert "from manim import *" in code
    assert "from manim.utils.color import Color" in code, "Color import missing!"
    assert "Color('#ffffff')" in code, "Color usage not generated correctly"


def test_no_unsafe_symbols():
    """Ensure generated code doesn't reference undefined symbols."""
    data = {
        "animation_plan": {
            "scenes": [
                {
                    "id": "test",
                    "description": "Test",
                    "elements": [{"type": "text", "text": "Hello"}]
                }
            ]
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        code = generate_scene_script(data, f.name)
    
    # Check for common runtime errors
    unsafe_patterns = [
        "color=None",  # Should use default or omit
        ".set_color()",  # Missing argument
        "Color(None)",  # Invalid Color construction
    ]
    
    for pattern in unsafe_patterns:
        assert pattern not in code, f"Unsafe pattern found: {pattern}"


def test_generated_code_compiles():
    """Verify generated Python code compiles without syntax errors."""
    data = {
        "animation_plan": {
            "scenes": [
                {
                    "id": "test",
                    "description": "Test",
                    "elements": [
                        {"type": "text", "text": "Test", "style": {"color": "#ff0000"}},
                        {"type": "circle", "radius": 1.0, "style": {"color": "BLUE"}},
                    ]
                }
            ]
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        code = generate_scene_script(data, f.name)
    
    # Compile check (doesn't execute, just validates syntax)
    try:
        compile(code, "<generated>", "exec")
    except SyntaxError as e:
        raise AssertionError(f"Generated code has syntax errors:\n{e}\n\nCode:\n{code}")


if __name__ == "__main__":
    test_color_import_present()
    test_no_unsafe_symbols()
    test_generated_code_compiles()
    print("✅ All code generation tests passed!")
