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

MODEL = "gemma3:12b"  # gemma3:27b, dongheechoi/meerkat:latest

TRAILING_COMMAS_RE = re.compile(r",\s*(?=[\]}])")

PROMPT_TMPL = """
You are a medical-domain statement extractor.

**Task**  
Check the whole input for medical statements.
Out of all medical statements take ONLY three medical statements.

**Selection rules**  
1. List **no more than three** statements. Choose the ones with the greatest clinical relevance or novelty.  
2. If there are fewer than three valid medical statements, list them all.  
3. Merge duplicates or near-duplicates into a single concise statement.  
4. Ignore greetings, rhetorical questions, jokes, motivational or moral advice, and anything not tied to medicine or human health.

**Output format (strict)**  
Return a valid JSON array containing 1–3 strings, each string being one of the extracted medical statements.  
No introductory text, no explanations.

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


def clean_json_content(content: str) -> str:
    # Remove Markdown-style code blocks if present
    return re.sub(r"^```(?:json)?\s*|\s*```$", "", content.strip(), flags=re.IGNORECASE)


def split_into_medical_statements(transcript: str) -> List[str]:
    """LLM → JSON array of medically-relevant claims."""
    prompt = PROMPT_TMPL.format(transcript=transcript.strip())
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            max_tokens=128,  # Increased from 4
            messages=[{"role": "user", "content": prompt}],
        )
        content = resp.choices[0].message.content.strip()
        cleaned = clean_json_content(content)
        print("Statements:")
        print(cleaned)
        return json.loads(cleaned)
    except Exception as e:
        print(e)
        print("FALLBACK")
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
def update_statements(data: Dict[str, Any]) -> Dict[str, Any]:
    transcript: str = data.get("transcript", "")
    if not transcript.strip():
        print("Input JSON has no transcript text.", file=sys.stderr)


    claims = split_into_medical_statements(transcript)
    data["statements"] = [
        statement_skeleton(text, i) for i, text in enumerate(claims, 1)
    ]

    data["generated_at"] = (
        dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    )

    return data
