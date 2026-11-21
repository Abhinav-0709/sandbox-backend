import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from app.config import get_settings
from app.core.logging import setup_logging
from app.core.exceptions import (
    AppException,
    app_exception_handler,
    validation_exception_handler,
    generic_exception_handler,
)
from app.database import engine, Base, AsyncSessionLocal, check_db_health
from app.api.router import router as sandbox_router
from app.services.environment_service import EnvironmentService

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    # In production or local dev, ensure schema and seed defaults
    is_test = (
        os.environ.get("ENVIRONMENT", "").lower() == "test"
        or settings.is_testing
        or os.environ.get("TESTING") == "True"
    )
    if not is_test:
        try:
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            async with AsyncSessionLocal() as session:
                env_service = EnvironmentService(session)
                await env_service.ensure_defaults()
                await session.commit()
        except Exception as e:
            import logging
            logging.getLogger("sandbox.startup").warning(f"Database bootstrap notice: {e}")
    yield


def create_app() -> FastAPI:
    current_env = os.environ.get("ENVIRONMENT", settings.ENVIRONMENT).lower()
    app = FastAPI(
        title="Vivoki Sandbox Microservice",
        description="Independent execution and assessment sandbox for Vivoki workplace simulations.",
        version="0.1.0",
        docs_url="/docs" if not settings.is_production else None,
        redoc_url="/redoc" if not settings.is_production else None,
        lifespan=lifespan if current_env != "test" else None,
    )

    # CORS Middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_origin_regex=r"^https://.*\.vercel\.app$",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Exception Handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Health & Meta endpoints
    @app.get("/", tags=["system"])
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": "0.1.0",
            "environment": settings.ENVIRONMENT,
            "status": "online",
        }

    @app.get("/health", tags=["system"], status_code=status.HTTP_200_OK)
    async def health_check():
        db_alive = await check_db_health()
        return {
            "status": "ok" if db_alive else "degraded",
            "database": "connected" if db_alive else "disconnected",
            "environment": settings.ENVIRONMENT,
        }

    # Mount Sandbox API
    app.include_router(sandbox_router, prefix=settings.API_PREFIX)

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=settings.DEBUG and not settings.is_production)
