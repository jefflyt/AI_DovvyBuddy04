import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import chat
from app.api.routes import lead as lead_routes
from app.api.routes import session as session_routes
from app.core.config import settings
from app.db.session import init_db


def create_app() -> FastAPI:
    app = FastAPI(title="DovvyBuddy Backend", version="0.1.0")

    # CORS configuration for frontend integration
    # Parse CORS_ORIGINS from environment (comma-separated)
    cors_origins_env = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001")
    cors_origins = [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
    
    # Add wildcard support for Vercel preview deployments
    # Format: https://*.vercel.app or https://dovvybuddy.com
    cors_origin_regex = os.getenv("CORS_ORIGIN_REGEX", r"https://.*\.vercel\.app")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_origin_regex=cors_origin_regex if cors_origin_regex else None,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    @app.on_event("startup")
    async def startup():
        await init_db()

    app.include_router(chat.router, prefix="/api")
    app.include_router(session_routes.router, prefix="/api")
    app.include_router(lead_routes.router, prefix="/api")

    @app.get("/health")
    async def health():
        return {"status": "healthy", "version": "0.1.0"}

    return app


app = create_app()
