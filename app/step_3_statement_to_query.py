#!/usr/bin/env python3
"""
STEP 3 – STATEMENT → PUBMED QUERY
────────────────────────────────
• Reads a FAXXCHEXX JSON that already contains *medical* statements
• For every statement without a "query", asks a local LLM to create
  a concise PubMed search string (plain words, 4-8 terms, one line)
• Writes the updated JSON and time-stamp
"""

import argparse
import datetime as dt
import json
import re
import sys
from typing import Any, Dict, List

import openai

# ───────── config ─────────
OPENAI_BASE_URL   = "http://localhost:11434/v1"
MODEL             = "gemma3:27b"                 # deepseek-r1:1.5b
TRAILING_COMMAS_RE = re.compile(r",\s*(?=[\]}])")

QUERY_PROMPT_TMPL = """
You are an expert biomedical librarian.

TASK: Convert the claim below into a PubMed search string that captures
the core biomedical concepts.

HARD CONSTRAINTS
• Return ONE line, 4 words, no line breaks.
• ONLY words separated by single spaces – no AND, OR, nor parentheses.
• Do NOT wrap the query in quotes, code fences, markdown, or JSON.
• First character must be a letter (A-Z or a-z).
• After you have written the query, STOP.

CLAIM:
{claim}
"""

# first visible line that starts with a letter
QUERY_LINE_RE = re.compile(r"[A-Za-z][^\n\r]*")

# ───────── helpers ─────────
def load_json(path: str) -> Dict[str, Any]:
    raw = open(path, "r", encoding="utf-8").read()
    return json.loads(TRAILING_COMMAS_RE.sub("", raw))


def write_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def sanitise_words(words: List[str]) -> List[str]:
    """Remove Boolean operators and empty strings, keep unique order."""
    seen, out = set(), []
    for w in words:
        lw = w.lower()
        if lw in {"and", "or", ""}:
            continue
        if lw not in seen:
            seen.add(lw)
            out.append(w)
    return out


def clean_query(raw: str, fallback_source: str) -> str:
    """
    • Take the first non-empty line from the model output,
      strip quotes / back-ticks.
    • Drop AND/OR if present.
    • Ensure 4-8 words; otherwise build a crude keyword fallback.
    """
    m = QUERY_LINE_RE.search(raw)
    if m:
        q = m.group(0).strip("`'\" ")
        words = sanitise_words(q.split())
        if 4 <= len(words) <= 8:
            return " ".join(words)

    # ── fallback: deduplicate ≤8 keywords from the claim itself ──
    kws = sanitise_words(re.findall(r"[A-Za-z']+", fallback_source))
    return " ".join(kws[:8])


def make_query(claim: str, client: openai.OpenAI) -> str:
    prompt = QUERY_PROMPT_TMPL.format(claim=claim)
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            temperature=0,
            max_tokens=32,
            stop=["\n"],                         # cut at first newline
            messages=[{"role": "user", "content": prompt}],
        )
        raw = resp.choices[0].message.content
        print("Query:")
        print(raw)
        return clean_query(raw, claim)
    except Exception as e:
        print(e)
        print("FALLBACK")
        # network / model failure → crude keywords
        kws = sanitise_words(re.findall(r"[A-Za-z']+", claim))
        return " ".join(kws[:8])

# ───────── core ─────────
def update_query(data: Dict[str, Any]) -> Dict[str, Any]:
    client = openai.OpenAI(base_url=OPENAI_BASE_URL, api_key="ollama")

    new_queries: List[str] = []

    for stmt in data.get("statements", []):
        if stmt.get("query"):            # already filled
            continue
        query = make_query(stmt.get("text", ""), client)
        stmt["query"] = query
        new_queries.append(query)

    data["generated_at"] = (
        dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    )

    return data

