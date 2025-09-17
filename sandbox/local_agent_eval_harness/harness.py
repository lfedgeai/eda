import os, sys, json, glob, argparse, importlib, traceback
from typing import Any, Dict
from tasks import TASKS
from scoring import score

def json_pointer(d: Dict[str, Any], path):
    cur = d
    for p in path:
        cur = cur[p]
    return cur

def as_json(obj):
    if isinstance(obj, (dict, list, str, int, float, bool)) or obj is None:
        return obj
    return str(obj)

def maybe_parse_json(x):
    if isinstance(x, (dict, list)):
        return x
    if isinstance(x, str):
        try:
            return json.loads(x)
        except Exception:
            # try to recover simple dict-likes
            return dict(_raw=x)
    return dict(_raw=str(x))

def print_results_table(results):
    """Print a nice table of results to the command line."""
    if not results:
        print("No results to display.")
        return
    
    # Calculate column widths
    max_task_len = max(len(r["task"]) for r in results)
    max_llm_score_len = 6  # "0.00" format
    max_agent_score_len = 6  # "0.00" format
    
    # Print header
    header = f"{'Task':<{max_task_len}} | {'LLM':<{max_llm_score_len}} | {'Agent':<{max_agent_score_len}} | Status"
    separator = "-" * len(header)
    print(f"\n{separator}")
    print(header)
    print(separator)
    
    # Print each result
    for result in results:
        task_name = result["task"]
        llm_score = result["general_llm"]["score"]
        agent_score = result["local_agent"]["score"]
        
        # Determine status
        if llm_score > agent_score:
            status = "LLM wins"
        elif agent_score > llm_score:
            status = "Agent wins"
        elif llm_score == agent_score and llm_score > 0:
            status = "Tie"
        else:
            status = "Both failed"
        
        print(f"{task_name:<{max_task_len}} | {llm_score:>5.2f} | {agent_score:>5.2f} | {status}")
    
    print(separator)
    
    # Print summary
    g_avg = sum(r["general_llm"]["score"] for r in results) / len(results)
    a_avg = sum(r["local_agent"]["score"] for r in results) / len(results)
    print(f"{'AVERAGE':<{max_task_len}} | {g_avg:>5.2f} | {a_avg:>5.2f} | {'LLM wins' if g_avg > a_avg else 'Agent wins' if a_avg > g_avg else 'Tie'}")
    print(separator)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--packs", required=True, help="Directory containing the unzipped packs")
    ap.add_argument("--out", required=True, help="Path to write a JSON report")
    ap.add_argument("--runs_dir", default="runs", help="Where to save per-task outputs")
    args = ap.parse_args()

    # Load providers
    gllm = importlib.import_module("providers.general_llm")
    agent = importlib.import_module("providers.local_agent")

    os.makedirs(args.runs_dir, exist_ok=True)
    report = {"results": [], "summary": {}}

    for task in TASKS:
        name = task["name"]
        pack_matches = glob.glob(os.path.join(args.packs, task["pack_glob"]))
        if not pack_matches:
            print(f"[warn] Task {name}: no pack matched {task['pack_glob']} under {args.packs}")
            continue
        pack_dir = max(pack_matches, key=len)  # choose the longest path (most specific) if multiple
        answers_path = os.path.join(pack_dir, task["answer_path"])

        try:
            with open(answers_path, "r", encoding="utf-8") as f:
                answers_all = json.load(f)
            expected = json_pointer(answers_all, task["answer_key_path"])
        except Exception as e:
            print(f"[error] Task {name}: failed loading expected answers: {e}")
            continue

        prompt = task["prompt"]
        extractor = task.get("extractor", lambda x: x)

        # --- Run General LLM baseline ---
        try:
            g_raw = gllm.run(prompt)
            g_json = extractor(maybe_parse_json(g_raw))
            g_score, g_details = score(expected, g_json)
        except Exception as e:
            g_json, g_score, g_details = dict(_error=str(e)), 0.0, {"error": traceback.format_exc()}

        # --- Run Local Agent ---
        try:
            a_raw = agent.run(pack_dir, prompt)
            a_json = extractor(maybe_parse_json(a_raw))
            a_score, a_details = score(expected, a_json)
        except Exception as e:
            a_json, a_score, a_details = dict(_error=str(e)), 0.0, {"error": traceback.format_exc()}

        # Save artifacts
        out_dir = os.path.join(args.runs_dir, name)
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, "expected.json"), "w", encoding="utf-8") as f:
            json.dump(expected, f, indent=2, ensure_ascii=False)
        with open(os.path.join(out_dir, "general_llm.json"), "w", encoding="utf-8") as f:
            json.dump(a_json if False else g_json, f, indent=2, ensure_ascii=False)  # keep var for clarity
        with open(os.path.join(out_dir, "local_agent.json"), "w", encoding="utf-8") as f:
            json.dump(a_json, f, indent=2, ensure_ascii=False)

        report["results"].append({
            "task": name,
            "pack_dir": pack_dir,
            "prompt": prompt,
            "expected_keys": task["answer_key_path"],
            "general_llm": {"score": g_score, "details": g_details},
            "local_agent": {"score": a_score, "details": a_details},
            "artifacts_dir": out_dir
        })

        print(f"[task] {name} → LLM {g_score:.2f} | Agent {a_score:.2f}")

    # Summary
    if report["results"]:
        g_avg = sum(r["general_llm"]["score"] for r in report["results"]) / len(report["results"])
        a_avg = sum(r["local_agent"]["score"] for r in report["results"]) / len(report["results"])
    else:
        g_avg = a_avg = 0.0
    report["summary"] = {"general_llm_avg": g_avg, "local_agent_avg": a_avg, "num_tasks": len(report["results"])}

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    # Display results table
    print_results_table(report["results"])
    
    print(f"\n[done] Wrote report to {args.out}")
    print(f"General LLM avg: {g_avg:.2f} | Local Agent avg: {a_avg:.2f}")

if __name__ == "__main__":
    main()
