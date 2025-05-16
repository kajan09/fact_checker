"""
BaseAgent – abstract interface every specialised agent must extend.
Guarantees that *all* inter‑agent messages are JSON‑serialisable dicts.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseAgent(ABC):
    """Shared functionality & contract for all agents."""

    name: str = "base_agent"

    def __init__(self, llm_client: "LLMClient") -> None:
        self.llm = llm_client

    # ------------------------------------------------------------------
    # Core API each agent MUST implement
    # ------------------------------------------------------------------
    @abstractmethod
    def process(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Take JSON dict; return JSON dict. Never mutate *data* in‑place."""
        raise NotImplementedError
