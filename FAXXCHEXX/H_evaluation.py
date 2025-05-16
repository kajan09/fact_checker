from __future__ import annotations
import json, time
from pathlib import Path
from typing import Dict, Any, List
import openai

# ---------- configuration ----------
base = Path(__file__).parent
FILE_PATH = base / "state.json"
MODEL_NAME = "meditron:70b"
TEMPERATURE = 0.1
# -----------------------------------

client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",               # any placeholder works for local ollama
)


def build_prompt(stmt: Dict[str, Any]) -> str:
    """Create the PREPROMT_TMPL for one statement."""
    evidence_blocks: List[str] = []
    for ev in stmt.get("evidence", []):
        # keep only the relevant ones; comment out the next line to include all
        if ev.get("relevance") == "no":
            continue
        evidence_blocks.append(
            f"- PMID {ev['pubmed_id']}: {ev['summary']}"
        )

    evidence_text = "\n".join(evidence_blocks) or "No PubMed evidence found."

    return (
        "You are a professional biomedical fact-checker.\n"
        "Task: Decide whether the given scientific abstracts collectively support, "
        "refute, or leave uncertain the claim.\n\n"
        f"CLAIM:\n{stmt['text']}\n\n"
        f"EVIDENCE:\n{evidence_text}\n\n"
        "Respond ONLY with valid JSON of the form:\n"
        "{\n"
        '  "verdict": "true|false|uncertain",\n'
        '  "confidence": <float between 0 and 1>\n'
        "}"
    )


def call_model(prompt: str) -> Dict[str, Any]:
    """Send the prompt and return parsed JSON."""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
        temperature=TEMPERATURE,
    )
    # the model reply is in response.choices[0].message.content
    content = response.choices[0].message.content
    return json.loads(content)      # raises if the model returned invalid JSON


def evaluate_all_statements(path: Path = FILE_PATH) -> None:
    """Main entry––loads JSON, updates every statement, saves back."""
    if not path.exists():
        raise FileNotFoundError(f"{path} not found")

    with open(path, "r", encoding="utf-8") as f:
        state: Dict[str, Any] = json.load(f)

    for stmt in state.get("statements", []):
        prompt = build_prompt(stmt)
        try:
            result = call_model(prompt)
        except Exception as e:
            # if something goes wrong leave placeholders so you can retry later
            stmt["verdict"] = "uncertain"
            stmt["confidence"] = 0.0
            stmt["rationale"] = f"Model call failed: {e}"
            continue

        # update the JSON
        stmt["verdict"] = result.get("verdict")
        stmt["confidence"] = result.get("confidence")
        # optional: keep the rationale returned by the model if you ask for it
        if "rationale" in result:
            stmt["rationale"] = result["rationale"]

    # write everything back
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, ensure_ascii=False)



evaluate_all_statements()
