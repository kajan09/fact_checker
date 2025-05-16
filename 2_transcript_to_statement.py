#!/usr/bin/env python3
"""
TRANSCRIPT → MEDICAL-STATEMENTS
──────────────────────────────
• Reads a FAXXCHEXX-style JSON file that contains a "transcript".
• Asks a local LLM to extract ONLY medically-relevant factual claims.
• Replaces/creates the "statements" list; each entry has the usual
  skeleton (id, text, verdict=None, …).
• No PubMed / evidence handling.
• Writes the updated JSON to the output path and stamps generated_at.
"""

import argparse
import datetime as dt
import json
import re
import sys
from typing import Any, Dict, List

import openai

# ────────────────────────────────────────────────────────────────────
# Configuration
# ────────────────────────────────────────────────────────────────────
client = openai.OpenAI(
    base_url="http://localhost:11434/v1",  # Ollama / LM-Studio
    api_key="ollama",
)

MODEL = "deepseek-r1:1.5b"  # gemma3:27b, dongheechoi/meerkat:latest

TRAILING_COMMAS_RE = re.compile(r",\s*(?=[\]}])")

PROMPT_TMPL = """
You are a medical‐domain statement extractor.

**Task**  
From the transcript below, list ONLY the distinct, self-contained
factual claims *related to medicine or human health*.  A claim is
medically relevant if it concerns:
• diseases, diagnoses, risk factors
• pharmaceuticals, supplements, or treatments
• nutrition, exercise effects on health
• physiology or pathophysiology
• clinical study results

Ignore:
• greetings, rhetorical questions, jokes
• motivational or moral advice
• claims not tied to health/medicine

**Output format (strict)**  
A valid JSON array of strings.  No other text.

TRANSCRIPT
----------
{transcript}
----------
"""


# ────────────────────────────────────────────────────────────────────
# Helper functions
# ────────────────────────────────────────────────────────────────────
def load_json_relaxed(path: str) -> Any:
    raw = open(path, "r", encoding="utf-8").read()
    return json.loads(TRAILING_COMMAS_RE.sub("", raw))


def split_into_medical_statements(transcript: str) -> List[str]:
    """LLM → JSON array of medically-relevant claims."""
    prompt = PROMPT_TMPL.format(transcript=transcript.strip())
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        content = resp.choices[0].message.content.strip()
        return json.loads(content)
    except Exception:
        # Fallback: naïve sentence split; real pipeline should re-prompt or log
        rough = re.split(r"[.!?]\s+", transcript)
        return [s.strip() for s in rough if s.strip()]


def statement_skeleton(text: str, idx: int) -> Dict[str, Any]:
    return {
        "id": idx,
        "text": text,
        "verdict": None,
        "rationale": None,
        "confidence": None,
        "query": None,
        "evidence": []
    }


# ────────────────────────────────────────────────────────────────────
# Core
# ────────────────────────────────────────────────────────────────────
def process_file(in_path: str, out_path: str) -> None:
    try:
        data: Dict[str, Any] = load_json_relaxed(in_path)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    transcript: str = data.get("transcript", "")
    if not transcript.strip():
        print("Input JSON has no transcript text.", file=sys.stderr)
        sys.exit(1)

    claims = split_into_medical_statements(transcript)
    data["statements"] = [
        statement_skeleton(text, i) for i, text in enumerate(claims, 1)
    ]

    data["generated_at"] = (
        dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    )

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Extracted {len(claims)} medical statements → {out_path}")


# ────────────────────────────────────────────────────────────────────
# CLI
# ────────────────────────────────────────────────────────────────────
def main() -> None:
    p = argparse.ArgumentParser(
        description="Extract medically relevant statements from transcript"
    )
    p.add_argument("input_json", help="Path to input JSON")
    p.add_argument("output_json", help="Path to output JSON")
    args = p.parse_args()
    process_file(args.input_json, args.output_json)


# Uncomment if you prefer CLI usage; otherwise, call `process_file(...)`
# from another module.
# if __name__ == "__main__":
#     main()

# Direct call example (remove or adapt in production)
process_file("json_example_2.json", "json_example_3.json")
