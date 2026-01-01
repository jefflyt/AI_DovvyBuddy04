from typing import List

from pydantic import AnyUrl, BaseSettings


class Settings(BaseSettings):
    environment: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: List[str] = ["http://localhost:3000"]
    database_url: AnyUrl

    class Config:
        env_file = ".env"


settings = Settings()
