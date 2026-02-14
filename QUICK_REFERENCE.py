#!/usr/bin/env python3
"""
Quick Reference for Animation Generation

This file shows the simplest way to generate an animation from your data.
"""

# ============================================================================
# SCENARIO 1: Simplest Usage - Edit and Run
# ============================================================================

# Open: scripts/run_from_history.py
# Edit the top section:

"""
QUESTION = "Your question"
HISTORY = "Your background context"  
SOLUTION = '''
1. Step 1
2. Step 2
3. Step 3
'''
CONCLUSION = "Your final answer"
"""

# Then run:
# python scripts/run_from_history.py
# 
# Your video will be saved to:
# media/videos/history_run/final.mp4


# ============================================================================
# SCENARIO 2: Using Python Code Directly
# ============================================================================

"""
from pathlib import Path
from scripts.pipeline import run_pipeline
from scripts.run_from_history import create_animation_plan_from_history
import json

# Your data
question = "Solve: x + 5 = 12"
history = "We learned about solving linear equations"
solution = '''
1. Start with x + 5 = 12
2. Subtract 5 from both sides
3. x = 7
'''
conclusion = "The solution is x = 7"

# Create plan
plan = create_animation_plan_from_history(question, history, solution, conclusion)

# Save plan
root = Path(__file__).parent
plan_path = root / "media" / "texts" / "my_plan.json"
plan_path.parent.mkdir(parents=True, exist_ok=True)
plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")

# Generate animation
run_pipeline(
    question=None,
    json_in=str(plan_path),
    workdir=root / "media" / "videos" / "my_video",
    voice_first=True
)

print("Done! Check media/videos/my_video/final.mp4")
"""


# ============================================================================
# SCENARIO 3: Multiple Problems in Batch
# ============================================================================

"""
from pathlib import Path
from scripts.pipeline import run_pipeline
from scripts.run_from_history import create_animation_plan_from_history
import json

root = Path(__file__).parent

problems = [
    {
        "q": "What is 2 + 2?",
        "h": "Basic arithmetic",
        "s": "1. Add the numbers: 2 + 2\\n2. Result is 4",
        "c": "The answer is 4"
    },
    {
        "q": "What is the area of a 3x4 rectangle?",
        "h": "Rectangle area formula",
        "s": "1. Formula: A = length × width\\n2. A = 3 × 4 = 12",
        "c": "The area is 12 square units"
    }
]

for i, prob in enumerate(problems, 1):
    print(f"Generating problem {i}...")
    plan = create_animation_plan_from_history(prob["q"], prob["h"], prob["s"], prob["c"])
    plan_path = root / "media" / "texts" / f"plan_{i}.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
    
    run_pipeline(
        question=None,
        json_in=str(plan_path),
        workdir=root / "media" / "videos" / f"video_{i}",
        voice_first=True
    )
    print(f"  ✓ Saved to media/videos/video_{i}/final.mp4")

print("All videos generated!")
"""


# ============================================================================
# CUSTOMIZATION: Changing Colors and Layout
# ============================================================================

"""
# In scripts/run_from_history.py, edit the create_animation_plan_from_history()
# function to customize:

# Change text color (hex values):
"color": "#FF0000"    # Red
"color": "#00FF00"    # Green
"color": "#0000FF"    # Blue
"color": "#FFFF00"    # Yellow
"color": "#FFFFFF"    # White

# Change text position (coordinate system):
"[0, 3, 0]"      # Top center
"[0, 0, 0]"      # Center
"[0, -3, 0]"     # Bottom center
"[-3, 0, 0]"     # Left side
"[3, 0, 0]"      # Right side
"[-3, 3, 0]"     # Top left
"[3, -3, 0]"     # Bottom right

# Change font size:
"font_size": 24   # Small
"font_size": 48   # Normal
"font_size": 64   # Large
"font_size": 96   # Very large
"""


# ============================================================================
# COMMON PROBLEMS & SOLUTIONS
# ============================================================================

"""
Problem: "No module named 'pyttsx3'"
Solution: pip install pyttsx3

Problem: "Video generation takes forever"
Solution: This is normal. Manim rendering takes time. For faster preview, 
          edit run_from_history.py and change voice_first=False

Problem: "No audio in the output"
Solution: Check Windows TTS is enabled. Run:
          Settings → Ease of Access → Speech → Check settings

Problem: "API key errors"
Solution: You don't need API keys with scripts/run_from_history.py!
          If using other modes, set environment variables:
          - OPENAI_API_KEY=your_key (for ChatGPT mode)
          - GEMINI_API_KEY=your_key (for Gemini mode)
"""


# ============================================================================
# FILE LOCATIONS REFERENCE
# ============================================================================

"""
Generated Files Location Reference:

v01.zip
  └─ All source code (181 KB)

scripts/run_from_history.py
  └─ Main script to edit and run

Output Locations:

After running "python scripts/run_from_history.py":

media/videos/history_run/
  ├─ final.mp4           (WATCH THIS! Your final animation)
  ├─ silent.mp4          (Video without audio)
  ├─ solution_plan.json  (Animation configuration)
  └─ voice/
     ├─ scene_01.wav
     ├─ scene_02.wav
     └─ ...

media/texts/
  └─ history_plan.json   (Reference copy of plan)

scripts/_generated/
  └─ generated_scene.py  (Manim Python code)
"""


if __name__ == "__main__":
    print(__doc__)
