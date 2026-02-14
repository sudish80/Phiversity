from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, model_validator


class SolutionStep(BaseModel):
    title: str
    explanation: str
    latex: Optional[str] = None


class Solution(BaseModel):
    topic: Optional[str] = None
    steps: List[SolutionStep]
    final_answer: str = Field(..., description="Concise final answer or result")


# --- Refactored Element Models ---

class _ElementBase(BaseModel):
    """Common attributes for all animation elements."""
    id: Optional[str] = Field(None, description="Optional unique identifier (e.g., 'circle1').")
    position: Optional[str] = Field(None, description="Position array [x,y,z] or preset string.")
    style: Optional[dict] = Field(default_factory=dict, description="Styling props (color, stroke_width, etc.)")
    timing: Optional[dict] = Field(
        default=None,
        description="Timing (start, duration, transition_in, etc.)"
    )
    voiceover: Optional[str] = Field(
        default=None,
        description="Optional per-element narration."
    )

# 1. Elements designed to hold Text, Code, or Equations -> REQUIRE content
class ContentElement(_ElementBase):
    type: Literal["Text", "Latex", "MathTex", "Code", "Paragraph", "Title"]
    content: str = Field(..., description="The actual text or LaTeX string to render.")

# 2. Elements designed to hold Math Content (Graphs, Fields) -> REQUIRE content
class MathElement(_ElementBase):
    type: Literal["Graph", "Plot", "VectorField", "ParametricGraph"]
    content: str = Field(..., description="The function definition (e.g. 'sin(x)') or vector field.")

# 3. Elements that reference files -> REQUIRE content (path)
class FileElement(_ElementBase):
    type: Literal["ImageMobject", "SVG", "Video"]
    content: str = Field(..., description="File path or URL.")

# 4. Elements representing Shapes or UI components -> OPTIONAL content
#    The LLM often omits 'content' for valid reasons (defined by style/geometry).
class ShapeElement(_ElementBase):
    type: str # Open string to allow flexibility (Circle, Rectangle, Arrow, etc.)
    content: Optional[str] = Field(None, description="Optional content (e.g. Polygon vertices).")

    @model_validator(mode='after')
    def validate_type_not_reserved(self):
        """
        Ensure we don't accidentally validate a 'Text' object missing content as a generic ShapeElement.
        """
        reserved_types = {
            "Text", "Latex", "MathTex", "Code", "Paragraph", "Title",
            "Graph", "Plot", "VectorField", "ParametricGraph",
            "ImageMobject", "SVG", "Video"
        }
        if self.type in reserved_types:
            raise ValueError(
                f"Element type '{self.type}' strictly requires a 'content' field. "
                "Please provide the text, equation, or function definition in the 'content' string."
            )
        return self

# Union type for the list
SceneElement = Union[ContentElement, MathElement, FileElement, ShapeElement]


class Scene(BaseModel):
    id: str
    description: str
    voiceover: Optional[str] = None
    elements: List[SceneElement]


class AnimationPlan(BaseModel):
    overview: Optional[str] = None
    scenes: List[Scene]


class SolverOutput(BaseModel):
    solution: Solution
    animation_plan: AnimationPlan
