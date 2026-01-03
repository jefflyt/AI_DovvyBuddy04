"""
Configuration for agent system.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentConfig:
    """Configuration for agent system."""

    enable_agent_routing: bool = True
    default_agent: str = "retrieval"
    max_retries: int = 3
    timeout_seconds: int = 30
    
    # LLM settings for agents
    temperature: float = 0.7
    max_tokens: int = 2048
    
    # RAG settings
    enable_rag: bool = True
    rag_top_k: int = 5
    rag_min_similarity: float = 0.5

    @classmethod
    def from_settings(cls, settings) -> "AgentConfig":
        """
        Create AgentConfig from app settings.

        Args:
            settings: App settings object

        Returns:
            AgentConfig instance
        """
        return cls(
            enable_agent_routing=settings.enable_agent_routing,
            default_agent=settings.default_agent,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
            enable_rag=settings.enable_rag,
            rag_top_k=settings.rag_top_k,
            rag_min_similarity=settings.rag_min_similarity,
        )
