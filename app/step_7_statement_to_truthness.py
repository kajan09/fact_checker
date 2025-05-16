from __future__ import annotations
import json, re, time
from pathlib import Path
from typing import Dict, Any
import openai

client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # any placeholder works for Ollama
)

model_name = "gemma3:27b"
temperature = 0
max_completion_tokens = 512

def statement_to_truthness( data: Dict[str, Any]) -> Dict[str, Any]:
    # -------- iterate over statements --------
    for stmt in data.get("statements", []):
        claim_text: str = stmt.get("text", "").strip()
        evidences   = stmt.get("evidence", [])

        # build evidence block (summaries only)
        evidence_lines = []
        for ev in evidences:
            pmid = ev.get("pubmed_id") or "N/A"
            summary = (ev.get("summary") or "").strip().replace("\n", " ")
            print(f"Evidence: {summary}")
            evidence_lines.append(f"- PMID {pmid}: {summary}")
        evidence_block = "\n".join(evidence_lines) or "No evidence provided."


        # final prompt
        prompt = (
            "You are a professional fact-checker.\n"
            "Decide whether the scientific abstracts collectively SUPPORT, "
            "REFUTE or leave UNCERTAIN the claim.\n\n"
            f"CLAIM:\n{claim_text}\n\n"
            f"EVIDENCE:\n{evidence_block}\n\n"
            "Respond with *exactly* two lines:\n"
            "VERDICT: true|false|uncertain\n"
            "FINALSCORE: <number between 0.00 and 1.00>\n"
            "Only those two lines, nothing else."
        )
        print(f"Prompt:\n{prompt}")
        # call model
        try:
            start = time.time()
            res = client.chat.completions.create(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=temperature,
                max_tokens=max_completion_tokens,
            )
            print(f"response: {res}")
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

    return data
