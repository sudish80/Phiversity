from typing import List, Optional, Union, Literal
from pydantic import BaseModel, Field, model_validator


class SolutionStep(BaseModel):
    title: str
    explanation: str
    latex: Optional[str] = None


class MCQQuestion(BaseModel):
    """Multiple-choice question with 4 options."""
    question: str
    topic: Optional[str] = None
    difficulty: Optional[str] = Field(None, description="easy, medium, or hard")
    option_a: str
    option_b: str
    option_c: str
    option_d: str
    correct_answer: str = Field(..., description="A, B, C, or D")
    explanation: Optional[str] = None


class ShortAnswerQuestion(BaseModel):
    """Short-answer question with model answer."""
    question: str
    topic: Optional[str] = None
    model_answer: str


class PracticeProblem(BaseModel):
    """Practice problem with step-by-step solution."""
    problem: str
    difficulty: Optional[str] = Field(None, description="easy, medium, hard, or challenge")
    concepts_needed: Optional[List[str]] = None
    steps: Optional[List[SolutionStep]] = None
    final_answer: Optional[str] = None


class CrossReference(BaseModel):
    """Link between related concepts across sections."""
    concept_a: str
    concept_b: str
    relationship: str = Field(..., description="How concept_a and concept_b are connected")


class Solution(BaseModel):
    topic: Optional[str] = None
    difficulty: Optional[str] = Field(None, description="beginner, intermediate, or advanced")
    subject: Optional[str] = Field(None, description="physics, chemistry, mathematics, or economics")
    summary: Optional[str] = Field(None, description="2-3 sentence plain-English summary")
    duration_estimate_minutes: Optional[float] = Field(None, description="Estimated video length in minutes (>= 10)")
    prerequisite_topics: Optional[List[str]] = Field(None, description="List of prerequisite topics taught before the main topic")
    steps: List[SolutionStep] = Field(default_factory=list, description="Solution steps with explanations")
    final_answer: str = Field(default="", description="Concise final answer or result")
    mcq_questions: Optional[List[MCQQuestion]] = Field(None, description="Multiple-choice assessment questions")
    short_answer_questions: Optional[List[ShortAnswerQuestion]] = Field(None, description="Short-answer assessment questions")
    practice_problems: Optional[List[PracticeProblem]] = Field(None, description="Practice problems with solutions")
    cross_references: Optional[List[CrossReference]] = Field(None, description="Cross-references linking related concepts")


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
    # Lowercase aliases are normalised to canonical form via validator below
    type: Literal["Text", "Latex", "MathTex", "Code", "Paragraph", "Title", "text", "latex", "mathtex", "code", "paragraph", "title"]
    content: str = Field(..., description="The actual text or LaTeX string to render.")

    @model_validator(mode='before')
    @classmethod
    def normalise_type(cls, values):
        if isinstance(values, dict) and 'type' in values:
            values['type'] = values['type'].capitalize() if values['type'] else values['type']
        return values

# 2. Elements designed to hold Math Content (Graphs, Fields) -> REQUIRE content
class MathElement(_ElementBase):
    type: Literal["Graph", "Plot", "VectorField", "ParametricGraph", "Axes", "axes", "graph", "plot", "vectorfield", "parametricgraph"]
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
    duration_seconds: Optional[float] = Field(None, description="Scene duration in seconds (40-70 for 10-min videos)")
    elements: List[SceneElement]


class AnimationPlan(BaseModel):
    overview: Optional[str] = None
    total_scenes: Optional[int] = Field(None, description="Total number of scenes (>= 14 for 10-min)")
    estimated_duration_seconds: Optional[int] = Field(None, description="Total video duration in seconds (>= 600)")
    scenes: List[Scene]


class SolverOutput(BaseModel):
    solution: Solution
    animation_plan: AnimationPlan
