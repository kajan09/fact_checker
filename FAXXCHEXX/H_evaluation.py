from __future__ import annotations
import json, re, time
from pathlib import Path
from typing import Dict, Any
import openai


def H_evaluation(
    filename: str | Path,
    model_name: str = "meditron:70b",
    temperature: float = 0.1,
) -> None:
    """
    One-stop function that opens the given JSON file, sends every statement
    (with all PubMed evidence summaries) to an LLM, extracts VERDICT and
    FINALSCORE, fills them back into the JSON, and overwrites the file.

    Parameters
    ----------
    json_path : str | Path
        Path to the JSON file that follows the structure in the example.
    model_name : str
        Name/alias of the model to call on the local server.
    temperature : float
        Sampling temperature for the chat completion.
    """
    base = Path(__file__).parent
    FILE_PATH = base / filename
    json_path = Path(FILE_PATH)

    # -------- initialise client once --------
    client = openai.OpenAI(
        base_url="http://localhost:11434/v1",
        api_key="ollama",   # any placeholder works for Ollama
    )

    # -------- open JSON --------
    if not json_path.exists():
        raise FileNotFoundError(f"{json_path!s} does not exist")

    with json_path.open("r", encoding="utf-8") as fh:
        data: Dict[str, Any] = json.load(fh)

    # -------- iterate over statements --------
    for stmt in data.get("statements", []):
        claim_text: str = stmt.get("text", "").strip()
        evidences   = stmt.get("evidence", [])

        # build evidence block (summaries only)
        evidence_lines = []
        for ev in evidences:
            pmid = ev.get("pubmed_id") or "N/A"
            summary = (ev.get("summary") or "").strip().replace("\n", " ")
            evidence_lines.append(f"- PMID {pmid}: {summary}")
        evidence_block = "\n".join(evidence_lines) or "No evidence provided."

        # final prompt
        prompt = (
            "You are a professional biomedical fact-checker.\n"
            "Decide whether the scientific abstracts collectively SUPPORT, "
            "REFUTE or leave UNCERTAIN the claim.\n\n"
            f"CLAIM:\n{claim_text}\n\n"
            f"EVIDENCE:\n{evidence_block}\n\n"
            "Respond with *exactly* two lines:\n"
            "VERDICT: true|false|uncertain\n"
            "FINALSCORE: <number between 0.00 and 1.00>\n"
            "Only those two lines, nothing else."
        )

        # call model
        try:
            start = time.time()
            res = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
            )
            reply: str = res.choices[0].message.content.strip()
        except Exception as exc:
            # fall back to uncertain if model call fails
            stmt["verdict"]    = "uncertain"
            stmt["confidence"] = 0.0
            stmt["rationale"]  = f"Model call failed: {exc}"
            continue

        # -------- parse reply --------
        verdict_match = re.search(r"VERDICT:\s*(true|false|uncertain)", reply, re.I)
        print(f"Model output:\n{reply}")
        score_match   = re.search(r"FINALSCORE:\s*([0-1](?:\.\d+)?)", reply, re.I)
        print(f"Parsed verdict: {verdict_match.group(1) if verdict_match else 'N/A'}")

        if verdict_match and score_match:
            print(f"Parsed score: {score_match.group(1)}")
            stmt["verdict"]    = verdict_match.group(1).lower()
            stmt["confidence"] = float(score_match.group(1))
            # keep the raw model reply for transparency
            stmt["rationale"]  = reply
        else:
            # model did not follow instructions → mark as uncertain
            print(f"Unparsable model output:\n{reply}")
            stmt["verdict"]    = "uncertain"
            stmt["confidence"] = 0.0
            stmt["rationale"]  = f"Unparsable model output:\n{reply}"

        elapsed = time.time() - start
        print(f"Statement {stmt.get('id')} done in {elapsed:4.1f}s")

    # -------- save JSON back --------
    with json_path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


# ---- example call ----
H_evaluation("H_state_dummy.json")
