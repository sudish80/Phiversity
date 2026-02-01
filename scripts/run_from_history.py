import json
import sys
from pathlib import Path

# Add the root directory to sys.path so scripts module can be imported
root_dir = Path(__file__).resolve().parents[1]
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from scripts.pipeline import run_pipeline

# --- CONFIGURATION START ---
# Replace these strings with your actual data
QUESTION = "Calculate the area of a circle with radius 5."
HISTORY = "User asked about circle area formula previously."
SOLUTION = """
1. Identify the formula for the area of a circle: A = pi * r^2.
2. Substitute the given radius r = 5 into the formula.
3. Calculate the square of 5: 5^2 = 25.
4. Multiply by pi: A = 25 * pi.
"""
CONCLUSION = "The area is 25pi square units."
# --- CONFIGURATION END ---

def create_animation_plan_from_history(question, history, solution, conclusion):
    """
    Creates a JSON animation plan directly from history/solution data.
    This bypasses the LLM orchestration entirely.
    """
    plan = {
        "solution": {
            "topic": "Mathematical Problem",
            "steps": [
                {
                    "title": "Problem Statement",
                    "explanation": f"We need to solve: {question}",
                    "latex": None
                },
                {
                    "title": "Context",
                    "explanation": history,
                    "latex": None
                },
                {
                    "title": "Solution Approach",
                    "explanation": solution,
                    "latex": None
                }
            ],
            "final_answer": conclusion
        },
        "animation_plan": {
            "overview": "Visualize the mathematical problem and its solution",
            "scenes": [
                {
                    "id": "scene_intro",
                    "description": "Introduction to the problem",
                    "voiceover": f"We are solving: {question}",
                    "elements": [
                        {
                            "type": "Text",
                            "content": question,
                            "position": "[0, 2, 0]",
                            "style": {"color": "#FFFFFF", "font_size": 48},
                            "timing": {"start": 0.0, "duration_in": 1.0, "transition_in": "Write"}
                        }
                    ]
                },
                {
                    "id": "scene_solution",
                    "description": "Solution steps",
                    "voiceover": "Here is the solution",
                    "elements": [
                        {
                            "type": "Text",
                            "content": conclusion,
                            "position": "[0, 0, 0]",
                            "style": {"color": "#00FF00", "font_size": 40},
                            "timing": {"start": 0.0, "duration_in": 2.0, "transition_in": "Write"}
                        }
                    ]
                }
            ]
        }
    }
    return plan

def main():
    root = root_dir
    
    # Create animation plan from history directly (no LLM call)
    print("[1/3] Creating animation plan from historical data...")
    plan = create_animation_plan_from_history(QUESTION, HISTORY, SOLUTION, CONCLUSION)
    
    # Save the plan to a JSON file
    plan_path = root / "media" / "texts" / "history_plan.json"
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    plan_path.write_text(json.dumps(plan, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"    ✓ Animation plan saved")
    
    # Run the pipeline using the pre-made plan (skip orchestration)
    print("[2/3] Generating audio voiceover...")
    print("[3/3] Rendering animation with Manim...")
    print("      (This may take several minutes, please wait...)")
    try:
        final_video = run_pipeline(
            question=None,  # We're providing the plan directly
            json_in=str(plan_path),  # Use the JSON plan instead of orchestrating
            workdir=root / "media" / "videos" / "history_run",
            voice_first=True
        )
        print()
        print("=" * 60)
        print("✓ SUCCESS! Video generation complete!")
        print("=" * 60)
        print(f"Video saved to: {final_video}")
        print(f"Video location: {final_video.resolve()}")
        print()
        print("You can now:")
        print(f"  - Open the video: {final_video}")
        print(f"  - Edit the question/solution in this script and run again")
        print("=" * 60)
    except Exception as e:
        print(f"Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
