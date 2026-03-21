import json
import os
from pathlib import Path
from typing import Dict, Any, List

from .llm_clients import get_chatgpt_client, get_deepseek_client, get_ollama_client, get_gemini_model, get_nvidia_client
from .schemas import SolverOutput
from ..server.utils.retries import retry_with_backoff
from ..server.utils.circuit_breaker import get_breaker

# Content Maximizer — enriches prompts with real MIT lecture transcripts
try:
    from ..content_maximizer import maximize_content as _maximize_content
except ImportError:
    _maximize_content = None  # graceful degradation

# Educational Content Generator — prerequisite analysis & section builder
try:
    from ..edu_content_generator import build_educational_prompt as _build_educational_prompt
except ImportError:
    _build_educational_prompt = None


SYSTEM_PROMPT_FOR_PROMPTER = """
You are a prompt engineer. Your job: given a user's question, write a single, clear, rigorous prompt for a subject-expert LLM to produce a machine-parseable JSON object with:
1) solution steps (with brief explanations and optional LaTeX), and
2) a comprehensive animation plan for Manim,
under the exact JSON schema described below.

FIRST, CLASSIFY THE QUESTION TYPE to select the best teaching approach:
- DERIVATION: Asks to prove, derive, or show something from first principles
  → Lead with the target result, then show 2+ derivation methods, verify with limiting cases
- CONCEPTUAL: Asks "what is", "explain", "why does"
  → Lead with intuitive analogy/example, formal definition, multiple representations, misconceptions
- NUMERICAL PROBLEM: Asks to calculate, solve, find a number
  → Given/Find/Plan/Execute/Verify framework, show unit cancellation, alternative solution methods
- COMPARISON: Asks to compare, contrast, differentiate between concepts
  → Side-by-side tables, Venn diagrams, same-scenario worked examples using both concepts
- APPLICATION: Asks about real-world uses
  → Start with compelling scenario, theory bridge, 4+ domain examples, detailed walkthrough
- GRAPHICAL: Involves graphs, plots, diagrams, geometry
  → Set up axes, qualitative sketch first, annotate features, parameter sensitivity animation

For EVERY question, the solver prompt must instruct: step-by-step transparency (never skip steps),
metacognitive narration ("why I chose this approach"), pattern recognition cues, and error awareness.

CRITICAL: OBEY MODE-SPECIFIC DURATION AND CONTENT REQUIREMENTS (NON-NEGOTIABLE).
- QUESTION_SOLVING mode:
  - Total lesson length must be 2 to 5 minutes (120 to 300 seconds).
  - Solve ONLY one question end-to-end with no chapter expansion.
  - Show full step-by-step working, checks, and final verification.
- LECTURE mode:
  - Total lesson length must be 30 to 60 minutes (1800 to 3600 seconds).
  - Teach the full lesson/chapter flow like a teacher: concepts, intuition, derivations, examples, and exercises for each topic.
  - Include structured teaching progression from basics to applications.
- REVISION mode:
  - Total lesson length must be 10 to 15 minutes (600 to 900 seconds).
  - Create a last-hour quick revision focused on tiny lesson topics.
  - Include 4 to 5 solved questions and derivation steps when relevant.

Rules:
- The solver LLM must respond with ONLY JSON, no prose.
- The JSON must conform to the schema and be valid.
- Scenes must be detailed and comprehensive — not just solving, but teaching.
- Include: hook, detailed background theory with historical context, exhaustive formula derivation
  from first principles using multiple approaches, unit analysis with worked examples,
  25+ solving steps, multiple common mistakes scenes, three to four worked examples,
  extensive real-world applications with actual data, edge cases and limiting cases,
  comprehensive summary with 8-12 takeaways, and 5-8 practice problems.
- Each scene must have extensive visual elements (text, latex, shapes, graphs, highlights, arrows)
- Pack each scene with maximum visual density and informational content.
- Prefer high-clarity LaTeX where it helps.
- Provide detailed, flowing explanations in voiceover for each concept.

EDUCATIONAL STRUCTURE — MANDATORY:
- If a topic requires prerequisite knowledge, identify and teach ALL prerequisites first.
- Structure content into sections: A (concepts), B (derivations), D (MCQs & short answers), E (practice problems).
- MAIN formula: full detailed derivation (12-20 steps). Supporting formulas: short derivation (5-8 steps).
- Include 12+ MCQs (4 options each with answers and detailed explanations) and 8+ short-answer questions with model answers.
- Include 5+ practice problems with complete step-by-step solutions of increasing difficulty.
- Add cross-references connecting concepts across sections with visual concept maps.
- End with summary (section highlights, concept map, exam tips) and additional practice exercises with answer keys.
- The JSON solution object should also include: prerequisite_topics, mcq_questions, short_answer_questions, practice_problems, cross_references.

JSON Schema (types and keys):
{
  "solution": {
    "topic": string,
    "difficulty": "beginner" | "intermediate" | "advanced",
    "subject": "physics" | "chemistry" | "mathematics" | "economics",
    "summary": string,
    "duration_estimate_minutes": number (must satisfy selected mode duration range),
    "prerequisite_topics": [string] | null,
    "steps": [
      { "title": string, "explanation": string, "latex": string | null }
    ],
    "final_answer": string,
    "mcq_questions": [
      { "question": string, "topic": string | null, "difficulty": "easy" | "medium" | "hard",
        "option_a": string, "option_b": string, "option_c": string, "option_d": string,
        "correct_answer": "A" | "B" | "C" | "D", "explanation": string }
    ] | null,
    "short_answer_questions": [
      { "question": string, "topic": string | null, "model_answer": string }
    ] | null,
    "practice_problems": [
      { "problem": string, "difficulty": string, "concepts_needed": [string],
        "steps": [{ "title": string, "explanation": string, "latex": string | null }],
        "final_answer": string }
    ] | null,
    "cross_references": [
      { "concept_a": string, "concept_b": string, "relationship": string }
    ] | null
  },
  "animation_plan": {
    "overview": string | null,
    "total_scenes": integer (must satisfy selected mode scope and pacing),
    "estimated_duration_seconds": integer (must satisfy selected mode duration range),
    "scenes": [
      {
        "id": string (snake_case),
        "description": string (max 8 words),
        "voiceover": string (150-300 words of teacher narration),
        "duration_seconds": integer (50-120),
        "elements": [
          { 
            "type": "Text" | "Latex" | "MathTex" | "Circle" | "Rectangle" | "Polygon" | "Annulus" | "Axes" | "Graph" | "highlight" | "arrow" | "Line" | "Arrow" | "DashedLine" | "Vector",
            "content": string, 
            "position": string | null, 
            "style": object | null 
          }
        ]
      }
    ]
  }
}

Element Instructions:
- "Latex"/"MathTex": Use for all math expressions. content="E = mc^2".
- "Polygon": content="[(0,0), (2,0), (0,2)]".
- "Circle": content="radius label" (optional).
- "Annulus": content="label" (optional). inner/outer radius handled by logic.
- "Rectangle": content="label" (optional). dimensions handled by logic.
- "Axes": content="" (empty). style={"x_range": [-5,5], "y_range": [-3,3]}.
- "highlight": content="" to highlight last object, or specific text to find.
- "Line"/"Arrow"/"DashedLine"/"Vector": Use for lines and arrows in diagrams.
- Each scene MUST have 5-10 visual elements for maximum visual density and engagement.

Write only the solver prompt. Do not include example JSON or any extra commentary.
""".strip()


def _mode_guidance(mode: str | None) -> str:
  m = (mode or "question_solving").strip().lower()
  if m == "lecture":
    return (
      "OVERRIDE RULE: The following mode constraints are mandatory and override any conflicting duration or scope instruction in other prompt text. "
      "MODE: LECTURE. Duration target is 30-60 minutes total. Teach as a full teacher-led chapter lesson: "
      "all key concepts, intuition, definitions, derivations, worked examples, and exercises topic-by-topic. "
      "Cover the lesson comprehensively with classroom sequencing from fundamentals to applications."
    )
  if m == "revision":
    return (
      "OVERRIDE RULE: The following mode constraints are mandatory and override any conflicting duration or scope instruction in other prompt text. "
      "MODE: REVISION. Duration target is 10-15 minutes total. Build a last-hour quick revision on tiny topics of the lesson. "
      "Include 4-5 solved questions, key formulas, derivation if applicable, quick mistakes review, and rapid recap checkpoints."
    )
  return (
    "OVERRIDE RULE: The following mode constraints are mandatory and override any conflicting duration or scope instruction in other prompt text. "
    "MODE: QUESTION_SOLVING. Duration target is 2-5 minutes total. Solve only one question end-to-end with explicit step-by-step derivation, "
    "substitution, unit checks, and final answer verification. Do not expand into full chapter teaching."
  )


def _local_solver_prompt(user_question: str) -> str:
  # Local fallback prompt with explicit schema and 60-minute minimum requirements
  # STRONGLY ENCOURAGE MAXIMUM LENGTH AND DENSITY
  schema = """
{
  "solution": {
    "topic": "string",
    "difficulty": "beginner | intermediate | advanced",
    "subject": "physics | chemistry | mathematics | economics",
    "summary": "2-3 sentence plain-English answer",
    "duration_estimate_minutes": "number, must satisfy selected mode duration range",
    "prerequisite_topics": ["string — list of prerequisite topics taught before the main topic"],
    "steps": [
      { "title": "string", "explanation": "string", "latex": "string | null" }
    ],
    "final_answer": "string",
    "mcq_questions": [
      {
        "question": "string",
        "topic": "string | null",
        "difficulty": "easy | medium | hard",
        "option_a": "string",
        "option_b": "string",
        "option_c": "string",
        "option_d": "string",
        "correct_answer": "A | B | C | D",
        "explanation": "string"
      }
    ],
    "short_answer_questions": [
      {
        "question": "string",
        "topic": "string | null",
        "model_answer": "string (2-3 sentences)"
      }
    ],
    "practice_problems": [
      {
        "problem": "string",
        "difficulty": "easy | medium | hard | challenge",
        "concepts_needed": ["string"],
        "steps": [{ "title": "string", "explanation": "string", "latex": "string | null" }],
        "final_answer": "string"
      }
    ],
    "cross_references": [
      {
        "concept_a": "string",
        "concept_b": "string",
        "relationship": "string — how they connect"
      }
    ]
  },
  "animation_plan": {
    "overview": "string | null",
    "total_scenes": "integer, must match selected mode scope",
    "estimated_duration_seconds": "integer, must satisfy selected mode duration range",
    "scenes": [
      {
        "id": "string (snake_case)",
        "description": "string (scene header, max 8 words)",
        "voiceover": "string (150-300 words of teacher narration)",
        "duration_seconds": "integer (50-120)",
        "elements": [
          { 
            "type": "Text | Latex | MathTex | Circle | Rectangle | Polygon | Annulus | Axes | Graph | highlight | arrow | Line | Arrow | DashedLine | Vector", 
            "content": "string", 
            "position": "[x, y, z] string e.g. '[0, 0, 0]' or 'center'", 
            "style": { "color": "string", "fill_opacity": 0.5 } 
          }
        ]
      }
    ]
  }
}
"""
  return (
    "You are a world-class STEM educator producing structured, DEEPLY DETAILED, COMPREHENSIVE "
    "animation scripts for YouTube-style lesson videos of UNPARALLELED DEPTH and LENGTH.\n\n"
    "Your output must be the MOST THOROUGH, DETAILED educational content the user has ever seen.\n\n"
    "## ADAPTIVE APPROACH — CLASSIFY FIRST, THEN TEACH:\n"
    "Before generating content, identify the QUESTION TYPE and adapt your approach:\n"
    "• DERIVATION → State target result upfront, show 2+ methods, verify with dimensional analysis + limiting cases\n"
    "• CONCEPTUAL → Lead with intuitive analogy, then formal definition, 3 representations (verbal, math, visual), address 3-5 misconceptions\n"
    "• NUMERICAL → Given/Find/Plan/Execute/Verify framework, show unit cancellation explicitly, solve 2 different ways\n"
    "• COMPARISON → Define each separately, then side-by-side table, shared roots, key differences, decision rules, same-scenario example\n"
    "• APPLICATION → Compelling real scenario opener, theory bridge, 4-5 domain examples, one detailed walkthrough\n"
    "• GRAPHICAL → Set up axes, qualitative sketch first, annotate all features, parameter sensitivity, connect graph to equation\n\n"
    "For EVERY question regardless of type:\n"
    "• Show your THINKING PROCESS: 'Why did I choose this formula? What cues showed me this approach?'\n"
    "• PATTERN RECOGNITION: Teach students to identify when to use each technique\n"
    "• NEVER SKIP STEPS: Show every algebraic manipulation as a human would on a whiteboard\n"
    "• ERROR AWARENESS: At every key step, mention what could go wrong and why\n"
    "• BUILD from simple→complex, concrete→abstract\n\n"
    "## MODE REQUIREMENTS (NON-NEGOTIABLE):\n"
    "- QUESTION_SOLVING: 2-5 minutes total (120-300s), exactly one question solved end-to-end.\n"
    "- LECTURE: 30-60 minutes total (1800-3600s), teacher-style full lesson/chapter with exercises by topic.\n"
    "- REVISION: 10-15 minutes total (600-900s), last-hour quick revision with 4-5 solved questions and derivation if relevant.\n"
    "- Ensure duration_estimate_minutes and estimated_duration_seconds strictly match the selected mode.\n\n"
    "## DEPTH REQUIREMENTS:\n"
    "- Go DEEP into each concept with multiple examples and approaches\n"
    "- Include 20+ derivation steps for main formulas, showing every algebraic manipulation\n"
    "- 15+ MCQ questions with detailed explanations for correct AND incorrect answers\n"
    "- 10+ short answer questions with comprehensive model answers\n"
    "- 6+ practice problems with full solutions of increasing complexity\n"
    "- Multiple real-world applications with actual data and measurements\n"
    "- Common mistakes: list 5-8 specific errors with corrections\n"
    "- Edge cases, limiting cases, and boundary conditions\n"
    "- Multiple derivation approaches for the same result\n"
    "- Historical context including key experiments and timeline\n\n"
    "EDUCATIONAL STRUCTURE (MANDATORY):\n"
    "If the question requires prerequisite knowledge, identify and teach ALL prerequisites first.\n"
    "List all prerequisite_topics in the solution object.\n\n"
    "SECTION A — Prerequisite concept explanations, then main topic concepts (MULTIPLE examples per concept)\n"
    "SECTION B — Short derivation (5-8 steps) for prereqs, FULL derivation (15-25 steps) for main formula using 2+ approaches\n"
    "MAIN SOLVE — Full step-by-step solution with EVERY algebraic step shown and explained\n"
    "SECTION D — MCQs (15+, 4 options each) with detailed explanations and short-answer questions (10+)\n"
    "SECTION E — 6+ practice problems with complete step-by-step solutions of increasing difficulty\n"
    "CROSS-REFS — Concept map linking related ideas across sections with visual diagrams\n"
    "SUMMARY — Key takeaways from each section, exam tips, common pitfalls, memory aids\n\n"
    "MANDATORY SCENES (in order, ADD MORE if needed for depth):\n"
    "1. hook — real-world opening with engagement (250+ words voiceover)\n"
    "2. problem_statement — full problem read aloud with context and motivation (200+ words)\n"
    "3-12. section_a_* — prerequisite concepts, then main topic with multiple examples (200+ words each)\n"
    "13-28. section_b_* — derivations: thorough for prereqs, exhaustive for main using 2+ approaches (200+ words each)\n"
    "29. given_values — every given value explained with units and physical significance (200+ words)\n"
    "30-60. step_1 through step_30 — solving steps with EVERY algebraic manipulation explained (180+ words each)\n"
    "61-62. common_mistakes — 5-8 common errors with detailed corrections (200+ words each)\n"
    "63. final_answer — result + physical interpretation + units + verification + significance (200+ words)\n"
    "64-75. second_example through fifth_example — variation problems with full solutions (200+ words each)\n"
    "76-95. section_d_* — MCQs and short-answer questions with reveals and explanations (200+ words each)\n"
    "96-110. section_e_* — practice problems with full step-by-step solutions (200+ words each)\n"
    "111. cross_reference_map — concept map connecting all topics with visual diagram (200+ words)\n"
    "112-118. summary — section-by-section highlights + exam tips + pitfalls + memory aids (200+ words each)\n"
    "119+. extra_practice_* — additional exercises + answer keys (200+ words each)\n\n"
    "## REMEMBER: MORE SCENES = MORE DEPTH = BETTER EDUCATION\n\n"
    "CRITICAL GUIDELINES:\n"
    "1. Respond with ONLY valid JSON, no prose, no markdown, no code fences.\n"
    "2. For Math, use type='MathTex' or 'Latex' and proper LaTeX syntax with double-escaped backslashes.\n"
    "3. For Shapes (Circle, Rectangle, Annulus), 'content' is the label text (or empty).\n"
    "4. For 'Polygon', 'content' must be a list of tuples: '[(0,0), (1,0), (0,1)]'.\n"
    "5. 'position' must be a string like '[2.0, -1.0, 0]'.\n"
    "6. Write complete, flowing voiceover sentences — not bullet fragments.\n"
    "7. Spell out all symbols verbally in voiceover.\n"
    "8. Include at least one visual element (axes/graph/shape) in each scene.\n"
    "9. All numbers, formulas, and explanations MUST be accurate.\n"
    "10. Each scene MUST have 5-10 visual elements for maximum visual complexity.\n"
    "11. Include mcq_questions, short_answer_questions, practice_problems, and cross_references in solution.\n\n"
    f"JSON Schema:\n{schema}\n\n"
    f"User question: {user_question.strip()}\n"
  )


@retry_with_backoff(retries=2, backoff_in_seconds=1)
def craft_solver_prompt(user_question: str, chatgpt_model: str | None = None, mode: str | None = None) -> str:
  if os.getenv("ORCHESTRATOR_OFFLINE"):
    print("[orchestrator] ORCHESTRATOR_OFFLINE set — using local prompt fallback.")
    return _local_solver_prompt(user_question) + "\n" + _mode_guidance(mode)

  # Try Ollama for prompt crafting when available and no OpenAI key
  if (os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_OPENAI_BASE_URL")) and not os.getenv("OPENAI_API_KEY"):
    try:
      client = get_ollama_client()
      model = os.getenv("OLLAMA_MODEL", "llama3")
      print(f"[orchestrator] Crafting solver prompt via Ollama model: {model}")
      messages = [
        {"role": "system", "content": SYSTEM_PROMPT_FOR_PROMPTER},
        {"role": "user", "content": user_question.strip() + "\n\n" + _mode_guidance(mode)},
      ]
      resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.3,
      )
      print("[orchestrator] Prompt crafted successfully via Ollama.")
      return resp.choices[0].message.content.strip()
    except Exception as e:
      print(f"[orchestrator] Ollama prompt crafting failed — using local fallback. Error: {e}")
      return _local_solver_prompt(user_question) + "\n" + _mode_guidance(mode)

  # Skip OpenAI for prompting when only Gemini key is set
  if os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
      print("[orchestrator] Gemini-only mode: Skipping OpenAI prompt crafting, using local template.")
      return _local_solver_prompt(user_question) + "\n" + _mode_guidance(mode)

  try:
    client = get_chatgpt_client()
    model = chatgpt_model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    print(f"[orchestrator] Crafting solver prompt via OpenAI model: {model}")
    messages = [
      {"role": "system", "content": SYSTEM_PROMPT_FOR_PROMPTER},
      {"role": "user", "content": user_question.strip() + "\n\n" + _mode_guidance(mode)},
    ]
    resp = client.chat.completions.create(
      model=model,
      messages=messages,
      temperature=0.3,
    )
    print("[orchestrator] Prompt crafted successfully.")
    return resp.choices[0].message.content.strip()
  except Exception as e:
    # Fallback: local prompt when OpenAI auth/config fails
    if os.getenv("ORCHESTRATOR_DISABLE_FALLBACK"):
      print(f"[orchestrator] OpenAI prompt crafting failed and fallback disabled. Error: {e}")
      raise
    print(f"[orchestrator] OpenAI prompt crafting failed — using local fallback. Error: {e}")
    return _local_solver_prompt(user_question) + "\n" + _mode_guidance(mode)


# Placeholder output removed: orchestration will not fabricate fallback content.


@retry_with_backoff(retries=2, backoff_in_seconds=1)
def call_deepseek_solver(solver_prompt: str, deepseek_model: str | None = None, context_question: str | None = None) -> Dict[str, Any]:
  breaker = get_breaker("deepseek")
  return breaker.call(_call_deepseek_solver_raw, solver_prompt, deepseek_model, context_question)

def _call_deepseek_solver_raw(solver_prompt: str, deepseek_model: str | None = None, context_question: str | None = None) -> Dict[str, Any]:
  if os.getenv("ORCHESTRATOR_OFFLINE"):
    # Offline mode: do not fabricate output; surface as error
    raise RuntimeError("ORCHESTRATOR_OFFLINE is set; DeepSeek solver disabled")
  try:
    client = get_deepseek_client()
    model = deepseek_model or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    print(f"[orchestrator] Calling DeepSeek solver via model: {model}")

    messages = [
      {
        "role": "system",
        "content": (
          "You are a rigorous subject-expert. Respond ONLY with a single JSON object that strictly matches the requested schema. "
          "No prose, no markdown, no code fences."
        ),
      },
      {"role": "user", "content": solver_prompt},
    ]

    resp = client.chat.completions.create(
      model=model,
      messages=messages,
      temperature=0.2,
    )
    content = resp.choices[0].message.content.strip()
    print(f"[orchestrator] Solver responded with {len(content)} chars.")

    try:
      data = json.loads(content)
    except json.JSONDecodeError:
      start = content.find("{")
      end = content.rfind("}")
      if start != -1 and end != -1 and end > start:
        data = json.loads(content[start : end + 1])
      else:
        raise
    return data
  except Exception as e:
    # Surface the error; orchestrate_solution handles the fallback chain.
    print(f"[orchestrator] DeepSeek solver failed. Error: {e}")
    raise


@retry_with_backoff(retries=2, backoff_in_seconds=1)
def call_openai_solver(solver_prompt: str, openai_model: str | None = None, context_question: str | None = None) -> Dict[str, Any]:
  """Call OpenAI as the solver to produce the final JSON plan.

  This uses the already-crafted `solver_prompt` and requests a strict JSON-only response.
  """
  if os.getenv("ORCHESTRATOR_OFFLINE"):
    raise RuntimeError("ORCHESTRATOR_OFFLINE is set; OpenAI solver disabled")
  client = get_chatgpt_client()
  model = openai_model or os.getenv("OPENAI_SOLVER_MODEL", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
  print(f"[orchestrator] Calling OpenAI solver via model: {model}")
  messages = [
    {
      "role": "system",
      "content": (
        "You are a rigorous subject-expert. Respond ONLY with a single JSON object that strictly matches the requested schema. "
        "No prose, no markdown, no code fences."
      ),
    },
    {"role": "user", "content": solver_prompt},
  ]
  resp = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=0.2,
  )
  content = resp.choices[0].message.content.strip()
  print(f"[orchestrator] OpenAI solver responded with {len(content)} chars.")
  try:
    return json.loads(content)
  except json.JSONDecodeError:
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
      return json.loads(content[start : end + 1])
    raise


@retry_with_backoff(retries=2, backoff_in_seconds=30)
def call_gemini_solver(solver_prompt: str, gemini_model: str | None = None, context_question: str | None = None) -> Dict[str, Any]:
  """Call Gemini as the solver to produce the final JSON plan.

  Uses google-generativeai with response_mime_type set to application/json when available.
  """
  if os.getenv("ORCHESTRATOR_OFFLINE"):
    raise RuntimeError("ORCHESTRATOR_OFFLINE is set; Gemini solver disabled")
  # Use pro model for longer, denser output - flash is too limited
  model_name = gemini_model or os.getenv("GEMINI_MODEL", "gemini-2.0-pro")
  model = get_gemini_model(model_name=model_name)
  print(f"[orchestrator] Calling Gemini solver via model: {model_name}")
  # Large prompts with 50+ scenes can take several minutes to generate
  timeout = int(os.getenv("GEMINI_TIMEOUT", "900"))
  try:
    generation_config = {
      "temperature": 0.2, 
      "response_mime_type": "application/json",
      "max_output_tokens": 200000,  # Allow very long output for dense plans
      "top_p": 0.95,
      "top_k": 40
    }
    resp = model.generate_content(solver_prompt, generation_config=generation_config, request_options={"timeout": timeout})
  except TypeError:
    # Fallback for older API versions
    resp = model.generate_content(solver_prompt, request_options={"timeout": timeout})
  content = (getattr(resp, "text", None) or "").strip()
  print(f"[orchestrator] Gemini solver responded with {len(content)} chars.")
  try:
    return json.loads(content)
  except json.JSONDecodeError:
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
      return json.loads(content[start : end + 1])
    raise


@retry_with_backoff(retries=4, backoff_in_seconds=10)
def call_ollama_solver(solver_prompt: str, ollama_model: str | None = None, context_question: str | None = None) -> Dict[str, Any]:
  """Call Ollama (local OpenAI-compatible API) as the solver to produce the final JSON plan."""
  if os.getenv("ORCHESTRATOR_OFFLINE"):
    raise RuntimeError("ORCHESTRATOR_OFFLINE is set; Ollama solver disabled")
  client = get_ollama_client()
  model = ollama_model or os.getenv("OLLAMA_MODEL", "llama3")
  print(f"[orchestrator] Calling Ollama solver via model: {model}")
  messages = [
    {
      "role": "system",
      "content": (
        "You are a rigorous subject-expert. Respond ONLY with a single JSON object that strictly matches the requested schema. "
        "No prose, no markdown, no code fences."
      ),
    },
    {"role": "user", "content": solver_prompt},
  ]
  resp = client.chat.completions.create(
    model=model,
    messages=messages,
    temperature=0.2,
  )
  content = resp.choices[0].message.content.strip()
  print(f"[orchestrator] Ollama solver responded with {len(content)} chars.")
  try:
    return json.loads(content)
  except json.JSONDecodeError:
    start = content.find("{")
    end = content.rfind("}")
    if start != -1 and end != -1 and end > start:
      return json.loads(content[start : end + 1])
    raise


@retry_with_backoff(retries=2, backoff_in_seconds=1)
def call_nvidia_solver(solver_prompt: str, nvidia_model: str | None = None, context_question: str | None = None) -> Dict[str, Any]:
  """Call NVIDIA AI Foundation Endpoints as the solver to produce the final JSON plan.
  
  Uses the NVIDIA NIM API with OpenAI compatibility.
  """
  if os.getenv("ORCHESTRATOR_OFFLINE"):
    raise RuntimeError("ORCHESTRATOR_OFFLINE is set; NVIDIA solver disabled")
  try:
    client = get_nvidia_client()
    model = nvidia_model or os.getenv("NVIDIA_MODEL", "nvidia/llama-3.1-nemotron-70b-instruct")
    print(f"[orchestrator] Calling NVIDIA solver via model: {model}")
    messages = [
      {
        "role": "system",
        "content": (
          "You are a rigorous subject-expert. Respond ONLY with a single JSON object that strictly matches the requested schema. "
          "No prose, no markdown, no code fences."
        ),
      },
      {"role": "user", "content": solver_prompt},
    ]
    resp = client.chat.completions.create(
      model=model,
      messages=messages,
      temperature=0.2,
    )
    content = resp.choices[0].message.content.strip()
    print(f"[orchestrator] NVIDIA solver responded with {len(content)} chars.")
    try:
      return json.loads(content)
    except json.JSONDecodeError:
      start = content.find("{")
      end = content.rfind("}")
      if start != -1 and end != -1 and end > start:
        return json.loads(content[start : end + 1])
      raise
  except Exception as e:
    # On NVIDIA failure, try other backends
    if os.getenv("ORCHESTRATOR_DISABLE_FALLBACK"):
      print(f"[orchestrator] NVIDIA solver failed and fallback disabled. Error: {e}")
      raise
    print(f"[orchestrator] NVIDIA solver failed — attempting other backends. Error: {e}")
    raise


def _load_default_prompt() -> str | None:
  """Auto-load Prompt.txt from project root — the comprehensive 10-min prompt."""
  try:
    root = Path(__file__).resolve().parents[2]
    prompt_path = root / "Prompt.txt"
    if prompt_path.exists():
      text = prompt_path.read_text(encoding="utf-8", errors="ignore").strip()
      if text:
        print(f"[orchestrator] Loaded default 10-min prompt from {prompt_path} ({len(text)} chars)")
        return text
  except Exception as e:
    print(f"[orchestrator] WARNING: Could not load Prompt.txt: {e}")
  return None


def _normalize_solver_response(raw: Dict[str, Any] | List[Any]) -> Dict[str, Any]:
  """Repair common LLM response issues before Pydantic validation.

  Handles cases where the LLM omits or renames required fields like
  solution.steps / solution.final_answer, or nests data differently.
  """
  # Handle case where LLM returns a list directly instead of a dict
  if isinstance(raw, list):
    # Check if list contains scene-like objects
    if raw and isinstance(raw[0], dict) and 'scene_number' in raw[0]:
      # Wrap the scenes in the expected structure
      print("[orchestrator] Normalizing: wrapping list response in solution structure")
      return {
        "solution": {
          "topic": "",
          "steps": raw,
          "final_answer": "See generated scenes"
        }
      }
    return {
      "solution": {
        "topic": "",
        "steps": raw,
        "final_answer": ""
      }
    }

  if not isinstance(raw, dict):
    return {
      "solution": {
        "topic": "",
        "steps": [],
        "final_answer": str(raw) if raw else ""
      }
    }

  sol = raw.get("solution")
  if not isinstance(sol, dict):
    return raw

  # If 'steps' is missing, try common alternative key names
  if "steps" not in sol:
    for alt_key in ("sections", "solution_steps", "content", "derivation_steps",
                     "explanation_steps", "procedure"):
      if alt_key in sol and isinstance(sol[alt_key], list):
        sol["steps"] = sol.pop(alt_key)
        print(f"[orchestrator] Normalized: renamed solution.{alt_key} -> solution.steps")
        break

  # If 'final_answer' is missing, try alternatives or derive a default
  if "final_answer" not in sol:
    for alt_key in ("answer", "conclusion", "result", "final_result", "summary_answer"):
      if alt_key in sol and isinstance(sol[alt_key], str):
        sol["final_answer"] = sol.pop(alt_key)
        print(f"[orchestrator] Normalized: renamed solution.{alt_key} -> solution.final_answer")
        break

  # Ensure each step has an 'explanation' field (required by SolutionStep schema).
  # LLMs sometimes return 'narration', 'description', 'voiceover', or 'content' instead.
  steps = sol.get("steps")
  if isinstance(steps, list):
    for step in steps:
      if isinstance(step, dict) and "explanation" not in step:
        for alt in ("narration", "description", "voiceover", "content", "text", "body"):
          if alt in step and isinstance(step[alt], str):
            step["explanation"] = step[alt]
            break
        else:
          # Last resort: synthesize from title
          step["explanation"] = step.get("title", "")

  # Ensure top-level 'animation_plan' exists (required by SolverOutput schema).
  if "animation_plan" not in raw:
    # Try to build one from scenes embedded in the solution steps
    scenes = []
    if isinstance(steps, list):
      for i, step in enumerate(steps if isinstance(steps, list) else []):
        if isinstance(step, dict) and "scene_number" in step:
          scenes.append({
            "id": f"scene{step.get('scene_number', i + 1)}",
            "description": step.get("title", f"Scene {i + 1}"),
            "voiceover": step.get("narration") or step.get("voiceover") or step.get("explanation", ""),
            "elements": step.get("elements", [
              {"type": "Text", "content": step.get("title", f"Scene {i + 1}"), "position": "[0, 2, 0]", "style": {"color": "#ffffff"}}
            ]),
          })
    if not scenes:
      scenes = [{"id": "scene1", "description": "Introduction", "voiceover": "", "elements": [
        {"type": "Text", "content": sol.get("topic", ""), "position": "[0, 2, 0]", "style": {"color": "#ffffff"}}
      ]}]
    raw["animation_plan"] = {
      "overview": sol.get("topic", "Generated animation"),
      "scenes": scenes,
    }
    print(f"[orchestrator] Normalized: synthesized animation_plan with {len(scenes)} scenes")

  return raw


def orchestrate_solution(user_question: str, override_solver_prompt: str | None = None, mode: str | None = None) -> SolverOutput:
  try:
    if override_solver_prompt and override_solver_prompt.strip():
      # Use the provided prompt directly, and ensure the user's question is included.
      solver_prompt = _mode_guidance(mode) + "\n\n" + override_solver_prompt.strip() + "\n\n" + f"User question: {user_question.strip()}"
    else:
      # Auto-load the comprehensive 10-min Prompt.txt as default
      default_prompt = _load_default_prompt()
      if default_prompt:
        solver_prompt = _mode_guidance(mode) + "\n\n" + default_prompt + "\n\n" + f"User question: {user_question.strip()}"
      else:
        solver_prompt = craft_solver_prompt(user_question, mode=mode)

    # ── Educational Content Generator — inject prerequisite analysis & section structure ──
    if _build_educational_prompt is not None:
        try:
            edu_block = _build_educational_prompt(user_question.strip())
            if edu_block:
                solver_prompt = solver_prompt + "\n" + edu_block
                print(f"[orchestrator] Edu Content Generator injected {len(edu_block)} chars of educational structure")
        except Exception as edu_err:
            print(f"[orchestrator] Edu Content Generator error (non-fatal): {edu_err}")
    else:
        print("[orchestrator] Edu Content Generator not available — using Prompt.txt educational sections only")

    # ── Content Maximizer — inject MIT lecture transcripts ──────────────
    if _maximize_content is not None:
        try:
            transcript_block = _maximize_content(user_question.strip())
            if transcript_block:
                solver_prompt = solver_prompt + "\n" + transcript_block
                print(f"[orchestrator] Content Maximizer injected {len(transcript_block)} chars of reference material")
            else:
                print("[orchestrator] Content Maximizer returned no transcripts — continuing without")
        except Exception as cm_err:
            print(f"[orchestrator] Content Maximizer error (non-fatal): {cm_err}")
    else:
        print("[orchestrator] Content Maximizer not available — continuing without transcript enrichment")

    # Smart routing based on available keys
    # Priority: Ollama > Gemini > DeepSeek > OpenAI > NVIDIA
    last_error = None

    if os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_OPENAI_BASE_URL"):
        print("[orchestrator] Trying Ollama solver...")
        try:
            raw = call_ollama_solver(solver_prompt, context_question=user_question)
            raw = _normalize_solver_response(raw)
            return SolverOutput.model_validate(raw)
        except Exception as e:
            last_error = e
            print(f"[orchestrator] Ollama solver failed: {e}")

    if os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"):
        print("[orchestrator] Trying Gemini solver...")
        try:
            raw = call_gemini_solver(solver_prompt, context_question=user_question)
            raw = _normalize_solver_response(raw)
            return SolverOutput.model_validate(raw)
        except Exception as e:
            last_error = e
            print(f"[orchestrator] Gemini solver failed: {e}")

    if os.getenv("DEEPSEEK_API_KEY"):
        print("[orchestrator] Trying DeepSeek solver...")
        try:
            raw = call_deepseek_solver(solver_prompt, context_question=user_question)
            raw = _normalize_solver_response(raw)
            return SolverOutput.model_validate(raw)
        except Exception as e:
            last_error = e
            print(f"[orchestrator] DeepSeek solver failed: {e}")

    if os.getenv("OPENAI_API_KEY"):
        print("[orchestrator] Trying OpenAI solver...")
        try:
            raw = call_openai_solver(solver_prompt, context_question=user_question)
            raw = _normalize_solver_response(raw)
            return SolverOutput.model_validate(raw)
        except Exception as e:
            last_error = e
            print(f"[orchestrator] OpenAI solver failed: {e}")

    if os.getenv("NVIDIA_API_KEY"):
        print("[orchestrator] Trying NVIDIA solver...")
        try:
            raw = call_nvidia_solver(solver_prompt, context_question=user_question)
            raw = _normalize_solver_response(raw)
            return SolverOutput.model_validate(raw)
        except Exception as e:
            last_error = e
            print(f"[orchestrator] NVIDIA solver failed: {e}")

    raise RuntimeError(f"All LLM backends failed. Last error: {last_error}")
  except Exception as e:
    print(f"[orchestrator] Orchestration failed. Error: {e}")
    raise


def generate_local_fallback_plan(user_question: str, mode: str | None = None) -> SolverOutput:
  """Generate a structured, visual SolverOutput when remote solvers fail.

  This keeps the pipeline usable even during backend outages by producing
  multiple visual scenes (not a single lecture-only slide).
  """
  uq = (user_question or "").strip() or "Concept explanation"
  short_q = uq[:80]
  m = (mode or "question_solving").strip().lower()
  mode_label = "Question Solving" if m == "question_solving" else ("Lecture" if m == "lecture" else "Revision")
  data = {
    "solution": {
      "topic": short_q,
      "difficulty": "beginner",
      "subject": "physics",
      "summary": f"Fallback structured {mode_label.lower()} lesson generated because online LLM backends were unavailable.",
      "duration_estimate_minutes": 3,
      "steps": [
        {
          "title": "Question Breakdown",
          "explanation": f"Restate and split the prompt into knowns, unknowns, and required outputs: {uq}",
          "latex": None
        },
        {
          "title": "Core Principle",
          "explanation": "Present the governing relationship and explain each variable before substitution.",
          "latex": r"F = m a"
        },
        {
          "title": "Solve Numerically",
          "explanation": "Compute the requested values step-by-step and verify unit consistency.",
          "latex": r"a = \frac{F}{m}"
        },
        {
          "title": "Interpretation",
          "explanation": "Explain how changing mass changes acceleration for fixed force.",
          "latex": None
        }
      ],
      "final_answer": "This is a fallback educational plan. Retry with an available LLM backend for a full-length custom lesson."
    },
    "animation_plan": {
      "overview": f"Fallback visual {mode_label.lower()} lesson for: {uq}",
      "total_scenes": 4,
      "estimated_duration_seconds": 180,
      "scenes": [
        {
          "id": "scene1_problem",
          "description": "State the problem clearly",
          "voiceover": f"We are solving: {uq}. First, identify the known values and what must be computed.",
          "duration_seconds": 45,
          "elements": [
            {
              "type": "Title",
              "content": short_q,
              "position": "[0, 2, 0]",
              "style": {"color": "#ffffff"}
            },
            {
              "type": "Text",
              "content": "Knowns, unknowns, and target equation",
              "position": "[0, 0.8, 0]",
              "style": {"color": "#6ec1ff"}
            },
            {
              "type": "Rectangle",
              "content": "",
              "position": "[0, -0.6, 0]",
              "style": {"color": "#cccccc", "stroke_width": 2}
            }
          ]
        },
        {
          "id": "scene2_formula",
          "description": "Show governing formula",
          "voiceover": (
            "Use Newton's second law. Force equals mass times acceleration. Rearranging gives acceleration equals force over mass."
            if m != "revision" else
            "Revision checkpoint: remember the core law F equals m a and quick rearrangement a equals F by m."
          ),
          "duration_seconds": 45,
          "elements": [
            {
              "type": "Title",
              "content": "Core Law",
              "position": "[0, 2, 0]",
              "style": {"color": "#ffffff"}
            },
            {
              "type": "MathTex",
              "content": r"F = m a",
              "position": "[0, 0.7, 0]",
              "style": {"color": "#f1c40f"}
            },
            {
              "type": "MathTex",
              "content": r"a = \frac{F}{m}",
              "position": "[0, -0.6, 0]",
              "style": {"color": "#2ecc71"}
            }
          ]
        },
        {
          "id": "scene3_steps",
          "description": "Compute values stepwise",
          "voiceover": (
            "Substitute numbers carefully, compute acceleration and velocity, and keep SI units throughout the calculation."
            if m != "lecture" else
            "In lecture mode, pause on each substitution and explain why each quantity enters the equation in this order."
          ),
          "duration_seconds": 45,
          "elements": [
            {
              "type": "Title",
              "content": "Numerical Steps",
              "position": "[0, 2, 0]",
              "style": {"color": "#ffffff"}
            },
            {
              "type": "Text",
              "content": "1) a = F/m",
              "position": "[-3.2, 0.9, 0]",
              "style": {"color": "#ffffff"}
            },
            {
              "type": "Text",
              "content": "2) v = u + at",
              "position": "[-3.2, 0.1, 0]",
              "style": {"color": "#ffffff"}
            },
            {
              "type": "Arrow",
              "content": "",
              "position": "[0, -0.7, 0]",
              "style": {"color": "#6ec1ff"}
            }
          ]
        },
        {
          "id": "scene4_summary",
          "description": "Summarize and compare",
          "voiceover": (
            "If mass doubles while force stays constant, acceleration halves. This inverse relationship is the key takeaway."
            if m != "question_solving" else
            "Final answer check: for fixed force, doubling mass halves acceleration, matching the relation a equals F over m."
          ),
          "duration_seconds": 45,
          "elements": [
            {
              "type": "Title",
              "content": "Key Takeaway",
              "position": "[0, 2, 0]",
              "style": {"color": "#ffffff"}
            },
            {
              "type": "MathTex",
              "content": r"a \propto \frac{1}{m}\;\text{for fixed}\;F",
              "position": "[0, 0.5, 0]",
              "style": {"color": "#2ecc71"}
            },
            {
              "type": "Text",
              "content": "Backend unavailable: showing structured fallback lesson.",
              "position": "[0, -1.0, 0]",
              "style": {"color": "#ffb347"}
            }
          ]
        }
      ]
    }
  }
  return SolverOutput.model_validate(data)
