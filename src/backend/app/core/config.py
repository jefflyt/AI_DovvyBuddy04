from pathlib import Path
from typing import List, Literal, Optional

from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env.local path relative to THIS file (src/backend/app/core/config.py)
# Go up 4 levels: config.py -> core/ -> app/ -> backend/ -> src/, then to project root
_ENV_FILE = Path(__file__).resolve().parent.parent.parent.parent.parent / ".env.local"


class Settings(BaseSettings):
    # Configuration for Pydantic v2
    # Read from root .env.local using absolute path
    model_config = SettingsConfigDict(env_file=str(_ENV_FILE), extra="ignore")
    
    # API Settings
    environment: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS_ORIGINS from comma-separated string to list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v
    
    # Database Settings
    database_url: Optional[str] = "postgresql+asyncpg://localhost/dovvybuddy"
    
    # API Keys
    gemini_api_key: str = ""
    groq_api_key: str = ""  # Deprecated - not used, Gemini only
    
    # LLM Provider Configuration
    default_llm_provider: Literal["groq", "gemini"] = "gemini"
    default_llm_model: str = "gemini-2.5-flash-lite"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048
    llm_max_retries: int = 3
    llm_retry_delay: float = 1.0
    
    # Embedding Configuration
    embedding_model: str = "text-embedding-004"  # Gemini embedding model (768 dimensions, standardized)
    embedding_dimension: int = 768  # Target dimension for embeddings (Matryoshka truncation)
    embedding_batch_size: int = 100
    embedding_cache_size: int = 1000
    embedding_cache_ttl: int = 3600  # 1 hour in seconds
    embedding_max_retries: int = 3
    embedding_retry_delay: float = 1.0
    
    # RAG Configuration
    enable_rag: bool = True
    rag_top_k: int = 8  # Increased to get more context for comprehensive answers
    rag_min_similarity: float = 0.5
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 50
    
    # Hybrid Search Configuration
    rag_use_hybrid: bool = True
    rag_keyword_weight: float = 0.3  # 30% keyword, 70% semantic
    
    # Orchestration Configuration
    max_message_length: int = 2000
    session_expiry_hours: int = 24
    max_conversation_history: int = 20
    enable_adk: bool = True
    adk_model: str = "gemini-2.5-flash-lite"
    enable_agent_routing: bool = True
    default_agent: str = "retrieval"
    
    # Conversation Continuity (PR6.1)
    feature_conversation_followup_enabled: bool = True  # Enabled to show contextual follow-up questions
    
    # Prompt Configuration
    system_prompt_version: str = "v1"
    include_safety_disclaimer: bool = True
    
    # Lead Capture & Delivery Configuration
    resend_api_key: str = ""
    lead_email_to: str = ""
    lead_email_from: str = "leads@dovvybuddy.com"
    lead_webhook_url: Optional[str] = None


_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get cached settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reset_settings_cache() -> None:
    """Reset cached settings instance (useful for tests)."""
    global _settings
    _settings = None


# Backward-compatible module-level accessor
settings = get_settings()
