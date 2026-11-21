import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.responses import ApiResponse
from app.core.auth import AuthenticatedUser, get_current_user_or_guest
from app.services.event_service import EventService
from app.schemas.event import BatchEventsRequest, BatchEventsResponse

router = APIRouter(prefix="/sessions", tags=["events"])


@router.post("/{session_id}/events", response_model=ApiResponse[BatchEventsResponse])
async def ingest_activity_events(
    session_id: uuid.UUID,
    body: BatchEventsRequest,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user_or_guest),
):
    service = EventService(db)
    res = await service.ingest_batch(session_id=session_id, events=body.events)
    return ApiResponse(data=res)
