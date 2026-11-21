from fastapi import APIRouter
from app.api.environments import router as environments_router
from app.api.sessions import router as sessions_router
from app.api.events import router as events_router
from app.api.submissions import router as submissions_router
from app.api.execution import router as execution_router

router = APIRouter()

router.include_router(environments_router)
router.include_router(sessions_router)
router.include_router(events_router)
router.include_router(submissions_router)
router.include_router(execution_router)
