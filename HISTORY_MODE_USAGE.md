# Animation Generation from History/Solution

## Overview

The `scripts/run_from_history.py` script allows you to generate animated videos directly from your own question, historical context, solution steps, and conclusion—**without requiring any external LLM API keys**.

## How It Works

1. **No API Required**: The script creates an animation plan directly from your provided data.
2. **Automatic Audio & Video Generation**: Uses text-to-speech (pyttsx3) and Manim for rendering.
3. **Customizable Content**: Edit the configuration variables to match your problem.

## Usage

### Step 1: Edit the Configuration

Open `scripts/run_from_history.py` and modify the top variables:

```python
QUESTION = "Your question here"
HISTORY = "Context or background about this question"
SOLUTION = """
1. First step description
2. Second step description
3. Final step description
"""
CONCLUSION = "Your final answer or conclusion"
```

### Step 2: Run the Script

```bash
python scripts/run_from_history.py
```

### Step 3: Wait for Output

The script will:
1. Create an animation plan from your data
2. Generate voiceover audio (via text-to-speech)
3. Render the animation using Manim
4. Combine audio and video

The final video will be saved at:
```
media/videos/history_run/final.mp4
```

## Example Configuration

```python
QUESTION = "Calculate the area of a circle with radius 5."
HISTORY = "The user previously learned the circle area formula."
SOLUTION = """
1. Recall the formula for circle area: A = π * r²
2. Substitute r = 5 into the formula
3. Calculate 5² = 25
4. Therefore A = 25π square units
"""
CONCLUSION = "The area of a circle with radius 5 is 25π square units."
```

## Customizing the Animation

To customize the visual appearance of scenes, edit the `create_animation_plan_from_history()` function in `scripts/run_from_history.py`:

- **Change colors**: Modify the `style` dict (e.g., `"color": "#FF0000"` for red)
- **Adjust positions**: Change values in `position` arrays (e.g., `"[0, 2, 0]"` for top, `"[0, -2, 0]"` for bottom)
- **Add more scenes**: Create additional scene objects in the `scenes` array

### Position Reference

The screen coordinates are:
- X-axis: -7.1 (left) to +7.1 (right)
- Y-axis: -4.0 (bottom) to +4.0 (top)
- Center: [0, 0, 0]

**Common positions:**
- Top center: `[0, 3.5, 0]`
- Bottom center: `[0, -3.5, 0]`
- Left side: `[-3.5, 0, 0]`
- Right side: `[3.5, 0, 0]`

## Troubleshooting

### Error: "No module named 'pyttsx3'"
Install it with:
```bash
pip install pyttsx3
```

### Video Takes a Long Time to Generate
Manim rendering can be slow depending on animation complexity. The first run may take several minutes.

### No Audio Output
Check that your system has text-to-speech enabled. On Windows, ensure Windows TTS service is available.

### Visual Quality Issues
The default quality is "medium". To improve quality, edit the pipeline call in the script:
```python
# Change voice_first=True to voice_first=False if you want faster rendering
final_video = run_pipeline(
    question=None,
    json_in=str(plan_path),
    workdir=root / "media" / "videos" / "history_run",
    voice_first=False  # Set to False for faster (lower quality) rendering
)
```

## File Output

After running, you'll find:
- **video**: `media/videos/history_run/final.mp4` - Final animation with audio
- **plan**: `media/texts/history_plan.json` - Animation plan (for reference/debugging)
- **audio**: `media/videos/history_run/voice/` - Audio files (one per scene)
- **generated script**: `scripts/_generated/generated_scene.py` - Manim scene code

## Advanced: Creating Complex Animations

For more advanced animations, you can manually create a JSON plan file and pass it to the pipeline:

```python
from scripts.pipeline import run_pipeline

run_pipeline(
    question=None,
    json_in="path/to/your/plan.json",
    workdir=Path("media/videos/custom_run"),
    voice_first=True
)
```

The JSON plan must follow the schema defined in `scripts/orchestrator/schemas.py`.

## Need Help?

Refer to:
- `GENERATION_GUIDE.txt` - Complete animation generation guide
- `Comprehensive_Prompt.txt` - LLM prompt documentation
- `scripts/orchestrator/schemas.py` - JSON plan schema definition
