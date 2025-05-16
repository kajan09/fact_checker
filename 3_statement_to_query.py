#!/usr/bin/env python3
"""
STEP 3  –  STATEMENT → PUBMED QUERY
──────────────────────────────────
• Reads a FAXXCHEXX JSON that already contains *medical* statements
  produced by 2_transcript_to_statement.py
• For every statement without a "query" string, asks a local LLM to
  craft a concise, boolean-ready PubMed search query
• Adds the query to the statement
• Leaves every other field unchanged
"""

import argparse
import datetime as dt
import json
import re
import sys
from typing import Any, Dict, List

import openai

# ───────── config ─────────
OPENAI_BASE_URL = "http://localhost:11434/v1"
MODEL           = "deepseek-r1:1.5b"      # or gemma3:27b etc.
TRAILING_COMMAS_RE = re.compile(r",\s*(?=[\]}])")

QUERY_PROMPT_TMPL = """
You are an expert biomedical librarian.

TASK: Convert the claim below into a PubMed search string that captures
the core biomedical concepts.

HARD CONSTRAINTS
• Return ONE line, 4-8 terms, no line breaks.
• Type the query exactly as it should appear in PubMed.
• Do NOT wrap it in quotes, code fences, markdown, or JSON.
• First character must be a letter (A-Z or a-z).  
• After you have written the query, STOP.

CLAIM:
{claim}
"""

# ───────── helpers ─────────
def load_json(path: str) -> Dict[str, Any]:
    raw = open(path, "r", encoding="utf-8").read()
    return json.loads(TRAILING_COMMAS_RE.sub("", raw))

def write_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def make_query(claim: str, client: openai.OpenAI) -> str:
    prompt = QUERY_PROMPT_TMPL.format(claim=claim)
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            max_tokens=32,
            stop=["\n"],          # stop generation at the first newline
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.choices[0].message.content
        # keep only the first line, remove surrounding quotes/back-ticks
        query = raw.split("\n", 1)[0].strip().strip("`'\"")
        return query
    except Exception:
        # crude fallback: six deduplicated keywords joined by AND
        kws = re.findall(r"[A-Za-z']+", claim.lower())
        return " AND ".join(sorted(set(kws))[:6])


# ───────── core ─────────
def process(in_path: str, out_path: str) -> None:
    data = load_json(in_path)
    client = openai.OpenAI(base_url=OPENAI_BASE_URL, api_key="ollama")

    new_queries: List[str] = []

    for stmt in data.get("statements", []):
        if stmt.get("query"):           # already filled
            continue
        query = make_query(stmt.get("text", ""), client)
        stmt["query"] = query
        new_queries.append(query)

    # update timestamp
    data["generated_at"] = (
        dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    )

    write_json(out_path, data)
    print(f"✓ added {len(new_queries)} PubMed queries → {out_path}")

# ───────── CLI ─────────
def main() -> None:
    p = argparse.ArgumentParser(description="Generate PubMed queries for each statement")
    p.add_argument("input_json",  help="JSON produced by step 2")
    p.add_argument("output_json", help="Path for updated JSON")
    args = p.parse_args()
    process(args.input_json, args.output_json)

# if __name__ == "__main__":
#     main()
   
process("json_example_3.json", "json_example_4.json")
