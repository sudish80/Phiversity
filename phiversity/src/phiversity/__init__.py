"""Phiversity: ask a question, get a narrated lecture video.

The pipeline: a user question goes to an LLM which plans a lecture
(narration segments), each narration is spoken with TTS, the LLM then
writes Manim code per segment timed to the narration audio, Manim
renders each segment, and ffmpeg stitches voice + animation into one
lecture video.
"""

__version__ = "0.1.0"
