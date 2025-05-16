"""
SynthesisAgent – turns the enriched payload into a concise, user‑facing overlay
summary and computes an overall truthiness score.
"""
from __future__ import annotations

import json
import statistics
from typing import Any, Dict, List

from .base_agent import BaseAgent

SUMMARY_PROMPT = (
    "Compose a brief fact‑check summary for end users based on the JSON below. "
    "Return ONLY valid JSON with keys: headline, body (40‑80 words), and optional call_to_action."
)


class SynthesisAgent(BaseAgent):
    name = "synthesis_agent"

    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        prompt = SUMMARY_PROMPT + "\nDATA:\n" + json.dumps(data, ensure_ascii=False)
        summary_json = self.llm(prompt=prompt, temperature=0.0, max_tokens=512)
        summary = summary_json if isinstance(summary_json, dict) else json.loads(summary_json)
        data["summary"] = summary

        confidences = [s.get("confidence", 0.5) for s in data.get("statements", [])]
        if confidences:
            data["overall_truthiness"] = statistics.mean(confidences)
        return data
