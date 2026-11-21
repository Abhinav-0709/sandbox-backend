from fastapi import APIRouter
from app.database import check_db_health
from app.config import get_settings
from app.api.environments import router as environments_router
from app.api.sessions import router as sessions_router
from app.api.events import router as events_router
from app.api.submissions import router as submissions_router
from app.api.execution import router as execution_router

settings = get_settings()
router = APIRouter()


@router.api_route("/health", methods=["GET", "HEAD"], tags=["system"])
async def api_health_check():
    db_alive = await check_db_health()
    return {
        "status": "ok" if db_alive else "degraded",
        "database": "connected" if db_alive else "disconnected",
        "environment": settings.ENVIRONMENT,
    }


router.include_router(environments_router)
router.include_router(sessions_router)
router.include_router(events_router)
router.include_router(submissions_router)
router.include_router(execution_router)
