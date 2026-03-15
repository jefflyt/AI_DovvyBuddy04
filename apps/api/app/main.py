from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text

from app.api.routes import chat
from app.api.routes import lead as lead_routes
from app.api.routes import session as session_routes
from app.core.config import settings
from app.core.rate_limit import limiter
from app.infrastructure.db.session import get_session, init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    await init_db()
    yield


async def collect_readiness_checks() -> tuple[bool, dict[str, object]]:
    checks: dict[str, object] = {}
    ready = True

    try:
        session_factory = get_session()
        async with session_factory() as session:
            await session.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:  # pragma: no cover - exercised via endpoint tests
        checks["database"] = {"status": "error", "reason": str(exc)}
        ready = False

    if settings.gemini_api_key:
        checks["llm"] = "configured"
    else:
        checks["llm"] = "missing"
        ready = False

    lead_capture_configured = bool(settings.resend_api_key and settings.lead_email_to)
    checks["lead_capture"] = "configured" if lead_capture_configured else "missing"
    if settings.environment == "production" and not lead_capture_configured:
        ready = False

    return ready, checks


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

    @app.get("/ready")
    async def ready():
        is_ready, checks = await collect_readiness_checks()
        return JSONResponse(
            status_code=200 if is_ready else 503,
            content={
                "status": "ready" if is_ready else "not_ready",
                "version": "0.1.0",
                "checks": checks,
            },
        )

    return app


app = create_app()
