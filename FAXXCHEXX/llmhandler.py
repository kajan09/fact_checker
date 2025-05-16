"""
LLM Handler – orchestrates a multi‑agent fact‑checking flow for Instagram audio posts.

Incoming  : raw transcript string (English).
Outgoing  : JSON‑serialisable dict that conforms to the FactCheckResult schema (see README).

Each agent lives in *agents/<special>_agent.py* and must implement BaseAgent.process.
The handler wires them together and guarantees that all communication between
agents is JSON only.
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

    def __init__(self, model) -> None:
        self.llm_client = llm_client
        self.agents = [agent_cls(llm_client) for agent_cls in AGENT_CHAIN]



# Convenience wrapper ---------------------------------------------------------

def handle(fulltext: str, llm_client: "LLMClient") -> str:
    """Return a pretty‑printed JSON string for CLI usage."""
    return json.dumps(LLMHandler(llm_client)(fulltext), indent=2, ensure_ascii=False)

