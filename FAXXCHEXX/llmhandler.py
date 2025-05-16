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


BASE_PROMPT_TMPL = (
    "You are a professional fact‑checker. "
    "You will receive a transcript of spoken English. "
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

STATEMENT_PROMPT = (
    "You will receive a transcript of spoken English. "
    "Extract concise, fact‑checkable statements. "
    "Return ONLY valid JSON: {\n  \"statements\": [\n    {\"id\": <int>, \"text\": <string>}\n  ]\n}"
)

SUMMARY_PROMPT = (
    "Compose a brief fact‑check summary for end users based on the JSON below. "
    "Return ONLY valid JSON with keys: headline, body (40‑80 words), and optional call_to_action."
)


class LLMHandler:
    """Central orchestrator that streams JSON payload through every agent."""

    def __init__(self, model):
        self.model = model

def run(self):
    return None



def update_json(json_str: str, key: str, value: Any) -> str:
    """Update a JSON string with a new key-value pair."""
    json_obj = json.loads(json_str)
    json_obj[key] = value
    return json.dumps(json_obj, indent=2, ensure_ascii=False)


def get_json_value(json_str: str, key: str) -> Any:
    """Get a value from a JSON string by key."""
    json_obj = json.loads(json_str)
    return json_obj.get(key, None)


def get_json_keys(json_str: str) -> List[str]:
    """Get all keys from a JSON string."""
    json_obj = json.loads(json_str)
    return list(json_obj.keys())


def get_json_values(json_str: str) -> List[Any]:
    """Get all values from a JSON string."""
    json_obj = json.loads(json_str)
    return list(json_obj.values())


def get_json_items(json_str: str) -> List[tuple]:
    """Get all items (key-value pairs) from a JSON string."""
    json_obj = json.loads(json_str)
    return list(json_obj.items())


def get_json_length(json_str: str) -> int:
    """Get the length of a JSON string."""
    json_obj = json.loads(json_str)
    return len(json_obj)

