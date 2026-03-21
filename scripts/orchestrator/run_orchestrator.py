import argparse
import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from .prompt_orchestrator import orchestrate_solution, generate_local_fallback_plan


def main():
    parser = argparse.ArgumentParser(description="Run two-stage LLM orchestration: ChatGPT prompt -> DeepSeek solution JSON")
    parser.add_argument("question", nargs="?", help="User question/problem to solve")
    parser.add_argument("--mode", dest="mode", default="question_solving", choices=["question_solving", "lecture", "revision"], help="Learning mode")
    parser.add_argument("--out", dest="out", default=None, help="Optional output JSON path (default: media/texts/solution_plan.json)")
    parser.add_argument("--prompt", dest="prompt", default=None, help="Override solver prompt; the entered question will be appended to this prompt.")
    parser.add_argument("--prompt-file", dest="prompt_file", default=None, help="Path to a file containing the solver prompt. Takes precedence over --prompt.")
    parser.add_argument("--long-video", action="store_true", help="Tell the orchestrator to generate a long-form ~10 min video.")
    args = parser.parse_args()

    question = args.question
    if not question:
        print("Enter your question, then Ctrl+Z + Enter (Windows) or Ctrl+D (Unix):\n")
        question = sys.stdin.read().strip()

    prompt_override = None
    if args.prompt_file:
        pf = Path(args.prompt_file)
        if not pf.exists():
            raise SystemExit(f"--prompt-file not found: {pf}")
        prompt_override = pf.read_text(encoding="utf-8", errors="ignore")
    else:
        prompt_override = args.prompt

    if args.long_video:
        try:
            root_dir = Path(__file__).resolve().parents[2]
            long_prompt_path = root_dir / "Prompt_long.txt"
            if not long_prompt_path.exists():
                print(f"[orchestrator] WARNING: Prompt_long.txt not found at {long_prompt_path}. Long-video flag has no effect.")
                ext_duration_req = ""
            else:
                ext_duration_req = "\n\n" + long_prompt_path.read_text(encoding="utf-8")
        except Exception as e:
            print(f"[orchestrator] WARNING: Could not read Prompt_long.txt: {e}")
            ext_duration_req = ""

        if prompt_override:
            prompt_override += ext_duration_req
        else:
            prompt_override = ext_duration_req

    # Compute out_path once, used in both success and error branches
    out_path = Path(args.out) if args.out else Path("media") / "texts" / "solution_plan.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = orchestrate_solution(user_question=question, override_solver_prompt=prompt_override, mode=args.mode)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result.model_dump(), f, ensure_ascii=False, indent=2)
        print(f"Saved structured JSON to: {out_path}")
    except Exception as e:
        if os.getenv("ORCHESTRATOR_DISABLE_LOCAL_FALLBACK"):
            out_path.write_text("false", encoding="utf-8")
            print(f"Orchestration failed; wrote 'false' to: {out_path}. Error: {e}")
            raise SystemExit(1)
        # Generate a local minimal valid plan to allow pipeline to continue
        print(f"[orchestrator] Using local fallback plan due to error: {e}")
        fallback = generate_local_fallback_plan(question, mode=args.mode)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(fallback.model_dump(), f, ensure_ascii=False, indent=2)
        print(f"Saved local fallback JSON to: {out_path}")
        # Exit success so server proceeds to pipeline
        return


if __name__ == "__main__":
    main()
