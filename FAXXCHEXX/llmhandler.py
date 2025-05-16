"""
LLMHandler
Incoming  : raw transcript string (English).
Outgoing  : JSON‑serialisable dict that conforms to the FactCheckResult schema (see README).
"""


from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Type

import json, pathlib, datetime as dt

path = pathlib.Path("state.json")


state = load_state()
state["transcript"] = None      # Add
state["generated_at"] = dt.datetime.utcnow().isoformat(timespec="seconds") + "Z"

save_state(state)

for i, stmt in enumerate(llm_splitter(state["transcript"]), start=1):
    add_statement(stmt, i)

save_state(state)




BASE_PROMPT_TMPL = (
    "You are a professional fact‑checker. "
    "You will receive a transcript of spoken English. "
)

STATEMENT_PROMPT = (
    "You will receive a transcript of spoken English. "
    "Extract concise, fact‑checkable statements. "
    "Return ONLY valid JSON: {\n  \"statements\": [\n    {\"id\": <int>, \"text\": <string>}\n  ]\n}"
)

CHECK_PROMPT_TMPL = (
    "You are a professional fact‑checker. Classify the statement as true, false, or uncertain. "
    "Return ONLY valid JSON of the form: {\n  \"verdict\": \"true|false|uncertain\",\n  \"rationale\": <string>,\n  \"confidence\": <float between 0 and 1>\n} \n\nSTATEMENT:\n{statement}"
)

ANALYSE_PROMPT_TMPL = (
    "You will receive a biomedical statement and a list of PubMed abstracts. "
    "For EACH abstract decide whether it supports, refutes, or is irrelevant to the statement. "
    "Return ONLY valid JSON list under key 'evidence': [\n  {\n    \"pubmed_id\": <string>,\n    \"title\": <string>,\n    \"verdict\": \"support|refute|irrelevant\",\n    \"snippet\": <string>\n  }\n]"
)

SUMMARY_PROMPT = (
    "Compose a brief fact‑check summary for end users based on the JSON below. "
    "Return ONLY valid JSON with keys: headline, body (40‑80 words), and optional call_to_action."
)


class LLMHandler:
    """Central orchestrator that streams JSON payload through every agent."""

    def __init__(self, high_model, low_model):
        self.low_model = low_model
        self.high_model = high_model


def run(self, transcript: str, oneshot, lowonly,highonly, pubmed, reasoning):
    if oneshot:
        # Run the high model once
        result = self.low_model_exchange(transcript, )
        if result is not None:
            return result
    return None

def low_model_exchange(self, transcript: str, agent):
    return None

def high_model_exchange(self, transcript: str, agent):
    return None




def load_state() -> dict:
    if path.exists():
        return json.loads(path.read_text())
    else:
        # start from fresh skeleton
        return {
            "transcript": None,
            "statements": [],
            "summary": {"headline": None, "body": None, "call_to_action": None},
            "overall_truthiness": None,
            "generated_at": None,
        }

def add_statement(text: str, idx: int) -> None:
    state["statements"].append({
        "id": idx,
        "text": text,
        "verdict": None,
        "rationale": None,
        "confidence": None,
        "evidence": [],
        "metadata": []
    })

    