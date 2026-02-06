import argparse
import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from .prompt_orchestrator import orchestrate_solution, generate_local_fallback_plan


def main():
    parser = argparse.ArgumentParser(description="Run two-stage LLM orchestration: ChatGPT prompt -> DeepSeek solution JSON")
    parser.add_argument("question", nargs="?", help="User question/problem to solve")
    parser.add_argument("--out", dest="out", default=None, help="Optional output JSON path (default: media/texts/solution_plan.json)")
    parser.add_argument("--prompt", dest="prompt", default=None, help="Override solver prompt; the entered question will be appended to this prompt.")
    parser.add_argument("--prompt-file", dest="prompt_file", default=None, help="Path to a file containing the solver prompt. Takes precedence over --prompt.")
    args = parser.parse_args()

    question = args.question
    if not question:
        print("Enter your question, then Ctrl+Z + Enter (Windows) or Ctrl+D (Unix):\n")
        question = "".join(iter(input, None))  # type: ignore

    prompt_override = None
    if args.prompt_file:
        pf = Path(args.prompt_file)
        if not pf.exists():
            raise SystemExit(f"--prompt-file not found: {pf}")
        prompt_override = pf.read_text(encoding="utf-8", errors="ignore")
    else:
        prompt_override = args.prompt

    try:
        result = orchestrate_solution(user_question=question, override_solver_prompt=prompt_override)
        default_out = Path("media") / "texts" / "solution_plan.json"
        out_path = Path(args.out) if args.out else default_out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)
        print(f"Saved structured JSON to: {out_path}")
    except Exception as e:
        default_out = Path("media") / "texts" / "solution_plan.json"
        out_path = Path(args.out) if args.out else default_out
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if os.getenv("ORCHESTRATOR_DISABLE_LOCAL_FALLBACK"):
            out_path.write_text("false", encoding="utf-8")
            print(f"Orchestration failed; wrote 'false' to: {out_path}. Error: {e}")
            raise SystemExit(1)
        # Generate a local minimal valid plan to allow pipeline to continue
        print(f"[orchestrator] Using local fallback plan due to error: {e}")
        fallback = generate_local_fallback_plan(question)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(fallback.model_dump(), f, ensure_ascii=False, indent=2)
        print(f"Saved local fallback JSON to: {out_path}")
        # Exit success so server proceeds to pipeline
        return


if __name__ == "__main__":
    main()
