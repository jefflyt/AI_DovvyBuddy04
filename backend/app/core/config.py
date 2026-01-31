from typing import List, Literal, Optional

from pydantic import AnyUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Configuration for Pydantic v2
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
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
    groq_api_key: str = ""
    
    # LLM Provider Configuration
    default_llm_provider: Literal["groq", "gemini"] = "groq"
    default_llm_model: str = "llama-3.3-70b-versatile"  # Groq default (fast dev)
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2048
    llm_max_retries: int = 3
    llm_retry_delay: float = 1.0
    
    # Embedding Configuration
    embedding_model: str = "text-embedding-004"  # Gemini embedding model (768 dimensions)
    embedding_batch_size: int = 100
    embedding_cache_size: int = 1000
    embedding_cache_ttl: int = 3600  # 1 hour in seconds
    embedding_max_retries: int = 3
    embedding_retry_delay: float = 1.0
    
    # RAG Configuration
    enable_rag: bool = True
    rag_top_k: int = 5
    rag_min_similarity: float = 0.5
    rag_chunk_size: int = 512
    rag_chunk_overlap: int = 50
    
    # Orchestration Configuration
    max_message_length: int = 2000
    session_expiry_hours: int = 24
    max_conversation_history: int = 20
    enable_agent_routing: bool = True
    default_agent: str = "retrieval"
    
    # Conversation Continuity (PR6.1)
    feature_conversation_followup_enabled: bool = False  # Default OFF for gradual rollout
    
    # Prompt Configuration
    system_prompt_version: str = "v1"
    include_safety_disclaimer: bool = True
    
    # Lead Capture & Delivery Configuration
    resend_api_key: str = ""
    lead_email_to: str = ""
    lead_email_from: str = "leads@dovvybuddy.com"
    lead_webhook_url: Optional[str] = None


settings = Settings()
