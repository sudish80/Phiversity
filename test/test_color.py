#!/usr/bin/env python
"""Test color imports in Manim."""

print("=" * 50)
print("Testing Manim color imports...")
print("=" * 50)

# Test 1: Try ManimColor
try:
    from manim.utils.color import ManimColor
    c = ManimColor('#FF0000')
    print("✓ ManimColor from manim.utils.color works!")
except Exception as e:
    print(f"✗ ManimColor failed: {e}")

# Test 2: Check what's in the __all__ of color module
try:
    from manim.utils import color
    print(f"\nAvailable in manim.utils.color: {dir(color)[:10]}...")
except Exception as e:
    print(f"✗ Can't import manim.utils.color: {e}")

# Test 3: Check if we can just use hex strings directly
try:
    from manim import Text, Scene
    # Text objects should accept color strings
    print("\n✓ Can import Text and Scene from manim")
    # Check what Text.set_color accepts
    t = Text("test")
    # Try setting color with hex string
    t.set_color("#FF0000")
    print("✓ Text.set_color('#FF0000') works with hex strings")
except Exception as e:
    print(f"✗ Text color test failed: {e}")

# Test 4: Try to import Color from different locations
try:
    from manim.utils.color.core import Color
    print("\n✓ Color from manim.utils.color.core works!")
except:
    try:
        from manim.utils.color import ManimColor as Color
        print("\n✓ Can alias ManimColor as Color!")
    except Exception as e:
        print(f"\n✗ No Color class found: {e}")

print("\n" + "=" * 50)
