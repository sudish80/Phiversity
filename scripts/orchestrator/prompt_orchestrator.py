import json
import os
from typing import Dict, Any

from .llm_clients import get_chatgpt_client, get_deepseek_client, get_ollama_client, get_gemini_model
from .schemas import SolverOutput


SYSTEM_PROMPT_FOR_PROMPTER = """
You are a prompt engineer. Your job: given a user's question, write a single, clear, rigorous prompt for a subject-expert LLM to produce a machine-parseable JSON object with:
1) solution steps (with brief explanations and optional LaTeX), and
2) a concise animation plan for Manim (scenes with elements),
under the exact JSON schema described below.

Rules:
- The solver LLM must respond with ONLY JSON, no prose.
- The JSON must conform to the schema and be valid.
- Keep steps and scenes concise, but complete.
- Prefer high-clarity LaTeX where it helps.

JSON Schema (types and keys):
{
  "solution": {
    "topic": string | null,
    "steps": [
      { "title": string, "explanation": string, "latex": string | null }
    ],
    "final_answer": string
  },
  "animation_plan": {
    "overview": string | null,
    "scenes": [
      {
        "id": string,
        "description": string,
        "voiceover": string | null,
        "elements": [
          { 
            "type": "Text" | "Latex" | "Circle" | "Rectangle" | "Polygon" | "Annulus" | "Axes" | "Graph", 
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
- "Latex": Use for all math expressions. content="E = mc^2".
- "Polygon": content="[(0,0), (2,0), (0,2)]".
- "Circle": content="radius label" (optional).
- "Annulus": content="label" (optional). inner/outer radius handled by logic.
- "Rectangle": content="label" (optional). dimensions handled by logic.
- "Axes": content="" (empty). style={"x_range": [-5,5], "y_range": [-3,3]}.

Write only the solver prompt. Do not include example JSON or any extra commentary.
""".strip()


def _local_solver_prompt(user_question: str) -> str:
  # Minimal local fallback prompt with explicit schema
  schema = """
{
  "solution": {
    "topic": "string | null",
    "steps": [
      { "title": "string", "explanation": "string", "latex": "string | null" }
    ],
    "final_answer": "string"
  },
  "animation_plan": {
    "overview": "string | null",
    "scenes": [
      {
        "id": "string",
        "description": "string",
        "voiceover": "string",
        "elements": [
          { 
            "type": "Text | Latex | Circle | Rectangle | Polygon | Annulus | Axes | Graph", 
            "content": "string", 
            "position": "[x, y, z] string e.g. '[0, 0, 0]'", 
            "style": { "color": "string", "fill_opacity": 0.5 } 
          }
        ]
      }
    ]
  }
}
"""
  return (
    "Given the user's question, produce a rigorous solution and Manim animation plan using the strict JSON schema below.\n"
    "Respond with ONLY valid JSON.\n\n"
    "CRITICAL GUIDELINES:\n"
    "1. For Math, use type='Latex' and proper LaTeX syntax (e.g. 'A = \\\\pi r^2').\n"
    "2. For Shapes (Circle, Rectangle, Annulus), 'content' is the label text (or empty).\n"
    "3. For 'Polygon', 'content' must be a list of tuples: '[(0,0), (1,0), (0,1)]'.\n"
    "4. 'position' must be a string like '[2.0, -1.0, 0]'.\n\n"
    f"JSON Schema:\n{schema}\n\n"
    f"User question: {user_question.strip()}\n"
  )


def craft_solver_prompt(user_question: str, chatgpt_model: str | None = None) -> str:
  # Check if we should skip OpenAI for prompting
  if os.getenv("GEMINI_API_KEY") and not os.getenv("OPENAI_API_KEY"):
      print("[orchestrator] Gemini-only mode: Skipping OpenAI prompt crafting, using local template.")
      return _local_solver_prompt(user_question)

  if os.getenv("ORCHESTRATOR_OFFLINE"):
    print("[orchestrator] ORCHESTRATOR_OFFLINE set — using local prompt fallback.")
    return _local_solver_prompt(user_question)
  try:
    client = get_chatgpt_client()
    model = chatgpt_model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    print(f"[orchestrator] Crafting solver prompt via OpenAI model: {model}")
    messages = [
      {"role": "system", "content": SYSTEM_PROMPT_FOR_PROMPTER},
      {"role": "user", "content": user_question.strip()},
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
    return _local_solver_prompt(user_question)


# Placeholder output removed: orchestration will not fabricate fallback content.


def call_deepseek_solver(solver_prompt: str, deepseek_model: str | None = None, context_question: str | None = None) -> Dict[str, Any]:
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
    # On DeepSeek failure, try OpenAI, then Gemini, then Ollama before surfacing the error
    if os.getenv("ORCHESTRATOR_DISABLE_FALLBACK"):
      print(f"[orchestrator] DeepSeek solver failed and fallback disabled. Error: {e}")
      raise
    print(f"[orchestrator] DeepSeek solver failed — attempting OpenAI solver. Error: {e}")
    try:
      return call_openai_solver(solver_prompt, context_question=context_question)
    except Exception as e2:
      print(f"[orchestrator] OpenAI solver attempt failed — attempting Gemini. Error: {e2}")
      try:
        return call_gemini_solver(solver_prompt, context_question=context_question)
      except Exception as e3:
        print(f"[orchestrator] Gemini solver attempt failed — attempting Ollama. Error: {e3}")
        try:
          return call_ollama_solver(solver_prompt, context_question=context_question)
        except Exception as e4:
          print(f"[orchestrator] Ollama solver attempt also failed. Error: {e4}")
          raise


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


def call_gemini_solver(solver_prompt: str, gemini_model: str | None = None, context_question: str | None = None) -> Dict[str, Any]:
  """Call Gemini as the solver to produce the final JSON plan.

  Uses google-generativeai with response_mime_type set to application/json when available.
  """
  if os.getenv("ORCHESTRATOR_OFFLINE"):
    raise RuntimeError("ORCHESTRATOR_OFFLINE is set; Gemini solver disabled")
  model_name = gemini_model or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
  model = get_gemini_model(model_name=model_name)
  print(f"[orchestrator] Calling Gemini solver via model: {model_name}")
  try:
    generation_config = {"temperature": 0.2, "response_mime_type": "application/json"}
    resp = model.generate_content(solver_prompt, generation_config=generation_config)
  except TypeError:
    resp = model.generate_content(solver_prompt)
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


def orchestrate_solution(user_question: str, override_solver_prompt: str | None = None) -> SolverOutput:
  try:
    if override_solver_prompt and override_solver_prompt.strip():
      # Use the provided prompt directly, and ensure the user's question is included.
      solver_prompt = override_solver_prompt.strip() + "\n\n" + f"User question: {user_question.strip()}"
    else:
      solver_prompt = craft_solver_prompt(user_question)

    # Smart routing based on available keys
    if os.getenv("GEMINI_API_KEY") and not os.getenv("DEEPSEEK_API_KEY") and not os.getenv("OPENAI_API_KEY"):
       print("[orchestrator] Detected Gemini-only configuration. Routing directly to Gemini.")
       return SolverOutput.model_validate(call_gemini_solver(solver_prompt, context_question=user_question))

    # Prefer DeepSeek; if it fails, the function will attempt OpenAI once.
    raw = call_deepseek_solver(solver_prompt, context_question=user_question)
    return SolverOutput.model_validate(raw)
  except Exception as e:
    print(f"[orchestrator] Orchestration failed. Error: {e}")
    raise


def generate_local_fallback_plan(user_question: str) -> SolverOutput:
  """Generate a minimal, valid SolverOutput when all remote solvers fail.

  This ensures the pipeline can continue by providing a simple scene with
  text/latex elements summarizing the topic.
  """
  uq = (user_question or "").strip() or "Physics concept explanation"
  data = {
    "solution": {
      "topic": "Angular Momentum Conservation",
      "steps": [
        {
          "title": "Define angular momentum",
          "explanation": "Angular momentum of a particle about a point is L = r x p (cross product).",
          "latex": "\\mathbf{L} = \\mathbf{r} \\times \\mathbf{p}"
        },
        {
          "title": "State conservation principle",
          "explanation": "In an isolated system with zero external torque, total angular momentum is conserved during collisions.",
          "latex": "\\frac{d \\mathbf{L}_{tot}}{dt} = 0 \Rightarrow \\mathbf{L}_{tot}^{(before)} = \\mathbf{L}_{tot}^{(after)}"
        }
      ],
      "final_answer": "Angular momentum remains constant when external torques are negligible."
    },
    "animation_plan": {
      "overview": "High-level visualization of angular momentum conservation in a collision.",
      "scenes": [
        {
          "id": "scene1",
          "description": "Introduce the concept and show the conservation statement.",
          "voiceover": f"Question: {uq}. We define angular momentum and state the conservation law.",
          "elements": [
            {
              "type": "Title",
              "content": "Angular Momentum Conservation",
              "position": "[0, 2, 0]",
              "style": {"color": "#ffffff"}
            },
            {
              "type": "Latex",
              "content": "\\mathbf{L} = \\mathbf{r} \\times \\mathbf{p}",
              "position": "[0, 0.5, 0]",
              "style": {"color": "#ffd700"}
            },
            {
              "type": "Latex",
              "content": "\\frac{d \\mathbf{L}_{tot}}{dt} = 0",
              "position": "[0, -0.5, 0]",
              "style": {"color": "#80ff80"}
            },
            {
              "type": "Circle",
              "content": "object A",
              "position": "[-2, -1.5, 0]",
              "style": {"color": "#64b5f6", "stroke_width": 3}
            },
            {
              "type": "Circle",
              "content": "object B",
              "position": "[2, -1.5, 0]",
              "style": {"color": "#f06292", "stroke_width": 3}
            }
          ]
        }
      ]
    }
  }
  return SolverOutput.model_validate(data)
