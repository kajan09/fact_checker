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

# --- import the agent classes -------------------------------------------------
# The AGENT_CHAIN order defines the pipeline.
from agents.statement_agent import StatementAgent
from agents.claim_check_agent import ClaimCheckAgent
from agents.pubmed_search_agent import PubMedSearchAgent
from agents.synthesis_agent import SynthesisAgent

AGENT_CHAIN: List[Type] = [
    StatementAgent,
    ClaimCheckAgent,
    PubMedSearchAgent,
    SynthesisAgent,
]


class LLMHandler:
    """Central orchestrator that streams JSON payload through every agent."""

    def __init__(self, llm_client: "LLMClient") -> None:
        self.llm_client = llm_client
        self.agents = [agent_cls(llm_client) for agent_cls in AGENT_CHAIN]

    # ---------------------------------------------------------------------
    # Public API
    # ---------------------------------------------------------------------
    def __call__(self, fulltext: str) -> Dict[str, Any]:
        """Run the entire pipeline and return a JSON‑serialisable dict."""
        payload: Dict[str, Any] = {"transcript": fulltext}

        for agent in self.agents:
            payload = agent.process(payload)
            # Always round‑trip through json to guarantee serialisability
            payload = json.loads(json.dumps(payload, ensure_ascii=False))

        payload["generated_at"] = datetime.now(timezone.utc).isoformat()
        return payload


# Convenience wrapper ---------------------------------------------------------

def handle(fulltext: str, llm_client: "LLMClient") -> str:
    """Return a pretty‑printed JSON string for CLI usage."""
    return json.dumps(LLMHandler(llm_client)(fulltext), indent=2, ensure_ascii=False)


if __name__ == "__main__":
    import sys
    from utils.llm_client import LocalLLMClient

    transcript_text = sys.stdin.read().strip()
    client = LocalLLMClient()
    print(handle(transcript_text, client))
