from typing import List, Literal, Optional

from pydantic import AnyUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Configuration for Pydantic v2
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    # API Settings
    environment: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000"]
    
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


settings = Settings()
