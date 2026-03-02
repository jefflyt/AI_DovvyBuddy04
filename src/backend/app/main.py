from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.api.routes import chat
from app.api.routes import lead as lead_routes
from app.api.routes import session as session_routes
from app.core.config import settings
from app.core.rate_limit import limiter
from app.db.session import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


def create_app() -> FastAPI:
    app = FastAPI(title="DovvyBuddy Backend", version="0.1.0", lifespan=lifespan)
    
    # Add rate limiter to app state
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=settings.cors_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    app.include_router(chat.router, prefix="/api")
    app.include_router(session_routes.router, prefix="/api")
    app.include_router(lead_routes.router, prefix="/api")

    @app.get("/health")
    async def health():
        return {"status": "healthy", "version": "0.1.0"}

    return app


app = create_app()
