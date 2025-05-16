"""
StatementAgent – extracts discrete factual statements from the transcript.
Output added to payload under key "statements" as a list of objects:
[{"id": 1, "text": "..."}, ...]
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from .base_agent import BaseAgent

# Prompt is deliberately minimal – everything else handled by the system prompt
STATEMENT_PROMPT = (
    "You will receive a transcript of spoken English. "
    "Extract concise, fact‑checkable statements. "
    "Return ONLY valid JSON: {\n  \"statements\": [\n    {\"id\": <int>, \"text\": <string>}\n  ]\n}"
)


class StatementAgent(BaseAgent):
    name = "statement_agent"

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        transcript: str = data["transcript"]

        llm_response = self.llm(
            prompt=f"{STATEMENT_PROMPT}\n---\nTRANSCRIPT:\n{transcript}",
            temperature=0.0,
            max_tokens=1024,
        )

        parsed = (
            llm_response
            if isinstance(llm_response, dict)
            else json.loads(llm_response)
        )
        data["statements"] = parsed["statements"]
        return data
