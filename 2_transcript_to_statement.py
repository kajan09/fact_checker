#!/usr/bin/env python3
"""
TRANSCRIPT-→STATEMENTS

Takes a FAXXCHEXX-style JSON file that *only* contains a
`"transcript"` string (or an empty/placeholder `"statements"` list)
and fills / replaces `"statements"` with one skeleton entry per
stand-alone factual claim.  
No PubMed handling, no evidence, no verdict calculation.

Output keeps the original top-level shape intact and adds/updates
`generated_at`.
"""

import argparse
import datetime as dt
import json
import re
import sys
from typing import Any, Dict, List

import openai

# ----------------------------------------------------------------------
# Configuration
# ----------------------------------------------------------------------

# local OpenAI-compatible endpoint (Ollama, LM-Studio, etc.)
client = openai.OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",
)

SPLIT_MODEL = "deepseek-r1:1.5b"

TRAILING_COMMAS_RE = re.compile(r",\s*(?=[\]}])")

SPLIT_PROMPT_TMPL = """
You are a professional fact-checker.

**Task**: Extract concise, self-contained factual statements from the
transcript below. Ignore greetings, rhetorical questions, opinions that
contain no verifiable claim, and purely motivational phrases.

**Output**: ONLY a valid JSON array of strings, nothing else.

TRANSCRIPT:
\"\"\"{transcript}\"\"\"
"""


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------

def load_json_relaxed(path: str) -> Any:
    raw = open(path, "r", encoding="utf-8").read()
    return json.loads(TRAILING_COMMAS_RE.sub("", raw))


def split_into_statements(transcript: str) -> List[str]:
    """
    Ask the LLM to return a JSON list of atomic factual claims.
    Falls back to naïve sentence splitting if the model misbehaves.
    """
    prompt = SPLIT_PROMPT_TMPL.format(transcript=transcript.strip())
    try:
        resp = client.chat.completions.create(
            model=SPLIT_MODEL,
            temperature=0,
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        content = resp.choices[0].message.content.strip()
        return json.loads(content)
    except Exception:
        # fallback: split on sentence boundaries, keep non-empty strings
        rough = re.split(r"[.!?]\s+", transcript)
        return [s.strip() for s in rough if s.strip()]


def make_statement_skeleton(text: str, idx: int) -> Dict[str, Any]:
    """Return an empty skeleton with just id and text filled."""
    return {
        "id": idx,
        "text": text,
        "verdict": None,
        "rationale": None,
        "confidence": None,
        "query": None,
        "evidence": []
    }


# ----------------------------------------------------------------------
# Main processor
# ----------------------------------------------------------------------

def process_file(in_path: str, out_path: str) -> None:
    try:
        data: Dict[str, Any] = load_json_relaxed(in_path)
    except json.JSONDecodeError as e:
        print(f"JSON parse error: {e}", file=sys.stderr)
        sys.exit(1)

    transcript: str = data.get("transcript") or ""
    if not transcript.strip():
        print("Input JSON has no transcript text.", file=sys.stderr)
        sys.exit(1)

    # derive new statements
    claims = split_into_statements(transcript)
    data["statements"] = [
        make_statement_skeleton(text, i) for i, text in enumerate(claims, 1)
    ]

    # timestamp
    data["generated_at"] = dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(claims)} statements to {out_path}")


# ----------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description="Extract statements from transcript (no PubMed)")
    p.add_argument("input_json", help="Path to input JSON")
    p.add_argument("output_json", help="Path to output JSON")
    args = p.parse_args()
    process_file(args.input_json, args.output_json)


if __name__ == "__main__":
    main()
