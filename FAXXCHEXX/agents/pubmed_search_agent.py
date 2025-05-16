"""
PubMedSearchAgent – queries PubMed and lets the LLM decide whether returned
abstracts support or refute the claim. Evidence is attached to each statement
under key "evidence".
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from .base_agent import BaseAgent
from utils.pubmed import search_pubmed  # thin wrapper around NCBI e‑utils

ANALYSE_PROMPT_TMPL = (
    "You will receive a biomedical statement and a list of PubMed abstracts. "
    "For EACH abstract decide whether it supports, refutes, or is irrelevant to the statement. "
    "Return ONLY valid JSON list under key 'evidence': [\n  {\n    \"pubmed_id\": <string>,\n    \"title\": <string>,\n    \"verdict\": \"support|refute|irrelevant\",\n    \"snippet\": <string>\n  }\n]"
)


class PubMedSearchAgent(BaseAgent):
    name = "pubmed_search_agent"

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        for item in data.get("statements", []):
            abstracts = search_pubmed(item["text"], max_results=10)
            prompt = ANALYSE_PROMPT_TMPL + "\nSTATEMENT:\n" + item["text"] + "\nABSTRACTS:\n" + json.dumps(abstracts, ensure_ascii=False, indent=2)
            analysis = self.llm(prompt=prompt, temperature=0.0, max_tokens=1024)
            evidence = analysis if isinstance(analysis, list) else json.loads(analysis)
            item["evidence"] = evidence
        return data
