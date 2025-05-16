"""
ClaimCheckAgent – assigns a truthfulness verdict, rationale, and confidence
score to each statement using the LLM's general knowledge.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

from .base_agent import BaseAgent

CHECK_PROMPT_TMPL = (
    "You are a professional fact‑checker. Classify the statement as true, false, or uncertain. "
    "Return ONLY valid JSON of the form: {\n  \"verdict\": \"true|false|uncertain\",\n  \"rationale\": <string>,\n  \"confidence\": <float between 0 and 1>\n} \n\nSTATEMENT:\n{statement}"
)


class ClaimCheckAgent(BaseAgent):
    name = "claim_check_agent"

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        updated: List[Dict[str, Any]] = []
        for item in data.get("statements", []):
            prompt = CHECK_PROMPT_TMPL.format(statement=item["text"])
            result = self.llm(prompt=prompt, temperature=0.0, max_tokens=512)
            obj = result if isinstance(result, dict) else json.loads(result)
            item.update(obj)
            updated.append(item)
        data["statements"] = updated
        return data
