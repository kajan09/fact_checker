import json
import subprocess
import sys

def is_related(statement_text: str, evidence_summary: str) -> bool:
    """Use Ollama+Gemma3 to judge whether evidence summary is relevant to the statement text."""
    prompt = (
        f"Statement text: {statement_text}\n"
        f"Evidence summary: {evidence_summary}\n"
        "Question: Does the evidence summary support or relate to the statement text? "
        "Answer 'yes' or 'no'."
    )
    proc = subprocess.run(
        ["ollama", "run", "gemma3:27b"],
        input=prompt,
        capture_output=True,
        text=True
    )
    if proc.returncode != 0:
        raise RuntimeError(f"Ollama call failed: {proc.stderr.strip()}")
    response = proc.stdout.strip().lower()
    return response.startswith("yes")


def reduce_to_evidence(input_file: str, output_file: str):
    # Load JSON data
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Iterate through statements
    for stmt in data.get("statements", []):
        filtered = []
        statement_text = stmt.get("text", "")

        for ev in stmt.get("evidence", []):
            summary_text = ev.get("summary", "").strip()
            # If there's a summary, only keep if related; if summary is empty, retain for manual review
            if summary_text:
                if is_related(statement_text, summary_text):
                    filtered.append(ev)
            else:
                filtered.append(ev)

        stmt["evidence"] = filtered

    # Write filtered JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


reduce_to_evidence("json_example_4.json", "json_example_4.json")
