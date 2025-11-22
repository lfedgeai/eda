import os
from pathlib import Path
from src.build_edge_data_agent import build_edge_data_agent

def load_text(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def evaluate_task(task_path):
    print(f"\n🧪 Evaluating task: {task_path.name}")
    
    # Load components
    agent_card = load_text(task_path / "agent_card.txt")
    user_input = load_text(task_path / "input.txt")

    print("📜 Agent Card:\n", agent_card[:300], "...")  # Truncate preview
    print("🔤 Input Query:\n", user_input.strip())

    # Placeholder: Run your agent or call the function
    # result = run_edge_data_agent(agent_card, user_input, additional_files=task_path)

    # For demo purposes, print mock result
    result = f"[MOCK OUTPUT] Processed input for {task_path.name}"
    print("✅ Output:\n", result)

    # Optional: Check expected_output.txt
    expected_path = task_path / "expected_output.txt"
    if expected_path.exists():
        expected = load_text(expected_path).strip()
        print("🧾 Expected:\n", expected)
        print("🎯 Match:", result.strip() == expected)
    else:
        print("⚠️ No expected_output.txt found.")

def run_all_tasks(root_path="sandbox/data"):
    for task_dir in Path(root_path).iterdir():
        if task_dir.is_dir() and (task_dir / "agent_card.txt").exists():
            evaluate_task(task_dir)

def run_one_task(task_name, root_path="sandbox/data"):
    task_path = Path(root_path) / task_name
    if task_path.exists() and (task_path / "agent_card.txt").exists():
        evaluate_task(task_path)
    else:
        print(f"❌ Task '{task_name}' not found or missing agent_card.txt.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run local evaluation for edge agents.")
    parser.add_argument("--task", type=str, help="Name of the specific task folder to run (e.g. 'finance')")
    args = parser.parse_args()

    if args.task:
        run_one_task(args.task)
    else:
        run_all_tasks()
