"""Generate a default intro.mp4 video using Manim if one doesn't exist."""

import os
from pathlib import Path


def generate_default_intro(output_path: Path) -> None:
    """Generate a default intro video using Manim.
    
    Args:
        output_path: Path where intro.mp4 should be saved
    """
    
    # Determine the project root (where the scripts folder is)
    project_root = Path(__file__).resolve().parent.parent
    
    intro_scene_code = '''
from manim import *

class IntroScene(Scene):
    """Default intro scene for Phiversity"""
    def construct(self):
        # Main title
        title = Text("Phiversity", font_size=72, color=BLUE, weight=BOLD)
        tagline = Text("Physics Education Made Simple", font_size=28, color=WHITE).next_to(title, DOWN, buff=0.5)
        
        # Create a group for animation
        intro_group = Group(title, tagline)
        
        # Animations
        self.play(FadeIn(title, scale=0.5), run_time=1)
        self.play(Write(tagline), run_time=1.5)
        
        # Hold the intro for 2 seconds
        self.wait(2)
        
        # Fade out
        self.play(FadeOut(intro_group), run_time=1)
        self.wait(0.5)
'''
    
    # Write the scene script to a temporary file (use absolute path)
    temp_script_dir = project_root / "scripts" / "_generated_intro"
    temp_script_dir.mkdir(parents=True, exist_ok=True)
    temp_script_path = temp_script_dir / "intro_scene.py"
    temp_script_path.write_text(intro_scene_code, encoding="utf-8")
    
    # Render using manim
    import subprocess
    import sys
    import shutil
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    cmd = [
        sys.executable,
        "-m",
        "manim",
        "-qm",  # medium quality
        "-o", "intro.mp4",
        str(temp_script_path),
        "IntroScene"
    ]
    
    print(f"[generate_intro] Creating default intro video at {output_path}...")
    try:
        # Run from project root so all paths work correctly
        # Explicitly configure streams to prevent initialization errors on Windows
        subprocess.run(
            cmd,
            check=True,
            cwd=str(project_root),
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Check if manim created the video in the expected location
        # Manim creates: media/videos/<script_name>/<quality>/intro.mp4 relative to CWD
        expected_video = project_root / "media" / "videos" / "intro_scene" / "1080p30" / "intro.mp4"
        if expected_video.exists():
            expected_video.replace(output_path)
            print(f"[generate_intro] ✓ Default intro created: {output_path}")
        else:
            print(f"[generate_intro] WARNING: Could not find generated intro video at {expected_video}")
            return False
        
        return True
    except subprocess.CalledProcessError as e:
        print(f"[generate_intro] ERROR: Failed to generate intro video: {e}")
        return False
    except Exception as e:
        print(f"[generate_intro] ERROR: {e}")
        return False
    finally:
        # Clean up temporary script directory and Manim's media output
        try:
            if temp_script_dir.exists():
                shutil.rmtree(temp_script_dir, ignore_errors=True)
        except Exception:
            pass
        try:
            # Clean up media directory created by Manim in project root
            media_dir = project_root / "media"
            if media_dir.exists():
                shutil.rmtree(media_dir, ignore_errors=True)
        except Exception:
            pass


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[2]
    intro_path = root / "intro.mp4"
    
    if intro_path.exists():
        print(f"[generate_intro] intro.mp4 already exists at {intro_path}")
    else:
        generate_default_intro(intro_path)
