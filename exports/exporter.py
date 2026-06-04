import csv
import os
from datetime import datetime

def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def export_txt(result: dict, workflow: str, directory: str = ".") -> str:
    filename = os.path.join(directory, f"result_{workflow}_{_timestamp()}.txt")
    lines = [f"Workflow: {workflow}", f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ""]

    summary = result.get("summary")
    if isinstance(summary, list):
        points = [p.strip() for p in summary if isinstance(p, str) and p.strip()]
        if points:
            lines += ["=== SUMMARY ==="]
            for p in points:
                lines += [f"  • {p}", ""]
    elif isinstance(summary, str) and summary.strip():
        lines += ["=== SUMMARY ===", summary.strip(), ""]
    if result.get("key_insights"):
        lines += ["=== INSIGHTS ==="]
        lines += [f"  • {i}" for i in result["key_insights"]]
        lines.append("")
    if result.get("action_items"):
        lines += ["=== TASKS ==="]
        for task in result["action_items"]:
            lines.append(f"  • {task['task']}")
            lines.append(f"    Priority: {task.get('priority','N/A')}   Deadline: {task.get('deadline','N/A')}")
        lines.append("")

    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return filename

def export_csv(result: dict, workflow: str, directory: str = ".") -> str:
    filename = os.path.join(directory, f"result_{workflow}_{_timestamp()}.csv")

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if workflow == "tasks" and result.get("action_items"):
            writer.writerow(["Task", "Priority", "Deadline"])
            for task in result["action_items"]:
                writer.writerow([task.get("task", ""), task.get("priority", "N/A"), task.get("deadline", "N/A")])
        elif result.get("key_insights"):
            writer.writerow(["Insight"])
            for insight in result["key_insights"]:
                writer.writerow([insight])
        elif "summary" in result:
            writer.writerow(["Field", "Value"])
            summary = result.get("summary")
            if isinstance(summary, list):
                for i, point in enumerate(summary, 1):
                    if isinstance(point, str) and point.strip():
                        writer.writerow([f"Summary point {i}", point.strip()])
            elif isinstance(summary, str) and summary.strip():
                writer.writerow(["Summary", summary.strip()])
            for i, insight in enumerate(result.get("key_insights", []), 1):
                writer.writerow([f"Insight {i}", insight])

    return filename
