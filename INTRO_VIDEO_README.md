# Intro Video Feature for Phiversity

## Overview

Every generated video in Phiversity now automatically **prepends an intro.mp4** at the beginning. This ensures consistent branding across all generated animations.

## Using the Default Intro

The system will automatically generate a default `intro.mp4` on first run if one doesn't exist. This default includes:
- **Title**: "Phiversity" in blue
- **Tagline**: "Physics Education Made Simple" in white
- **Duration**: ~4.5 seconds (with fade in/out animations)
- **Quality**: Medium (720p30)

The intro video will be created in the project root directory.

## Creating a Custom Intro

### Option 1: Replace the Generated One

1. Create your own video file (MP4 format recommended)
2. Name it `intro.mp4`
3. Place it in the project root directory (same level as `pipeline.py`)
4. The next time videos are generated, your custom intro will be used

### Option 2: Create a Custom Intro Using Manim

Create a file like this and run it with Manim:

```python
from manim import *

class MyIntroScene(Scene):
    def construct(self):
        # Your custom intro animation here
        title = Text("My Organization", font_size=72, color=BLUE)
        self.play(FadeIn(title, scale=0.5))
        self.wait(2)
        self.play(FadeOut(title))
```

Then render it:
```bash
manim -qm your_intro_file.py MyIntroScene
```

And move the output to `intro.mp4` in the project root.

## How It Works

1. **Pipeline Start**: When `run_pipeline()` is called, it checks for `intro.mp4` in the project root
2. **Auto-Generation**: If `intro.mp4` doesn't exist, a default one is automatically generated using Manim
3. **Video Combination**: After the main video is created with audio:
   - Main video with audio → `final.mp4` (intermediate)
   - Intro + intermediate final → `final.mp4` (overwritten with intro prepended)
4. **Result**: Every output video starts with your intro, then transitions to the main content

## Technical Details

- **Function**: `prepend_intro_to_video()` in `scripts/av_sync.py`
- **Constants**: 
  - `INTRO_VIDEO_NAME = "intro.mp4"` in `av_sync.py`
  - Lookup: Project root directory
- **Fallback**: If intro generation fails, videos are created without intro (graceful degradation)
- **Video Codec**: Uses ffmpeg to concatenate videos losslessly

## Requirements

- `moviepy` (already in requirements.txt)
- `ffmpeg` (system dependency for video processing)
- Manim (for auto-generating default intro)

## Customization Options

### Disable Intro for Specific Videos

If you want to generate videos without the intro:
1. Remove `intro.mp4` from project root
2. Set the environment variable: `INTRO_VIDEO_OPTIONAL=true`
3. Videos will still be generated successfully without the intro

### Adjust Intro Duration

Edit `scripts/generate_intro.py` and modify the `self.wait()` times in the `IntroScene` class.

### Change Intro Style

Replace the `IntroScene` class in `scripts/generate_intro.py` with your own animation code and regenerate by removing the existing `intro.mp4`.

## Troubleshooting

**Q: The intro video is not appearing in my videos**
- A: Check that `intro.mp4` exists in the project root with: `ls intro.mp4` (Unix) or `dir intro.mp4` (Windows)
- A: Check the server/pipeline logs for `"Intro prepended to video"` messages

**Q: The default intro generation failed**
- A: Ensure Manim is installed: `pip install manim`
- A: Check that you have write permissions to the project root
- A: Videos will still be generated without intro if generation fails

**Q: I want to use a video longer than 5 seconds as intro**
- A: Just place your custom `intro.mp4` in the project root - any duration works!

**Q: Can I use different intros for different videos?**
- A: Currently, all videos use the same `intro.mp4` from project root. You could swap it out between pipeline runs if needed.
