import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.responses import ApiResponse
from app.core.auth import AuthenticatedUser, get_current_user_or_guest
from app.services.session_service import SessionService
from app.schemas.session import (
    CreateSessionRequest,
    UpdateSessionStatusRequest,
    SaveWorkspaceStateRequest,
    SessionDetailResponse,
    SessionSummaryResponse,
)

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=ApiResponse[SessionDetailResponse])
async def create_or_resume_session(
    body: CreateSessionRequest,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user_or_guest),
):
    service = SessionService(db)
    session = await service.create_or_resume_session(
        environment_slug=body.environment_slug,
        user=user,
        session_metadata=body.session_metadata,
    )
    return ApiResponse(
        data=SessionDetailResponse(
            id=session.id,
            environment_slug=session.environment.slug,
            environment_title=session.environment.title,
            category=session.environment.category,
            status=session.status,
            time_limit_seconds=session.time_limit_seconds,
            time_remaining_seconds=session.time_remaining_seconds,
            workspace_state=session.workspace_state,
            environment_config=session.environment.config,
            started_at=session.started_at,
            expires_at=session.expires_at,
            completed_at=session.completed_at,
            created_at=session.created_at,
        )
    )


@router.get("/{session_id}", response_model=ApiResponse[SessionDetailResponse])
async def get_session(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user_or_guest),
):
    service = SessionService(db)
    session = await service.get_session(session_id, user=user)
    return ApiResponse(
        data=SessionDetailResponse(
            id=session.id,
            environment_slug=session.environment.slug,
            environment_title=session.environment.title,
            category=session.environment.category,
            status=session.status,
            time_limit_seconds=session.time_limit_seconds,
            time_remaining_seconds=session.time_remaining_seconds,
            workspace_state=session.workspace_state,
            environment_config=session.environment.config,
            started_at=session.started_at,
            expires_at=session.expires_at,
            completed_at=session.completed_at,
            created_at=session.created_at,
        )
    )


@router.patch("/{session_id}/status", response_model=ApiResponse[SessionSummaryResponse])
async def update_session_status(
    session_id: uuid.UUID,
    body: UpdateSessionStatusRequest,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user_or_guest),
):
    service = SessionService(db)
    session = await service.update_status(session_id, new_status=body.status, user=user)
    return ApiResponse(
        data=SessionSummaryResponse(
            id=session.id,
            environment_slug=session.environment.slug,
            environment_title=session.environment.title,
            category=session.environment.category,
            status=session.status,
            time_limit_seconds=session.time_limit_seconds,
            time_remaining_seconds=session.time_remaining_seconds,
            started_at=session.started_at,
            expires_at=session.expires_at,
            completed_at=session.completed_at,
            created_at=session.created_at,
        )
    )


@router.patch("/{session_id}/workspace", response_model=ApiResponse[SessionSummaryResponse])
async def save_workspace_state(
    session_id: uuid.UUID,
    body: SaveWorkspaceStateRequest,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user_or_guest),
):
    service = SessionService(db)
    session = await service.save_workspace_state(
        session_id=session_id,
        workspace_state=body.workspace_state,
        time_remaining_seconds=body.time_remaining_seconds,
        user=user,
    )
    return ApiResponse(
        data=SessionSummaryResponse(
            id=session.id,
            environment_slug=session.environment.slug,
            environment_title=session.environment.title,
            category=session.environment.category,
            status=session.status,
            time_limit_seconds=session.time_limit_seconds,
            time_remaining_seconds=session.time_remaining_seconds,
            started_at=session.started_at,
            expires_at=session.expires_at,
            completed_at=session.completed_at,
            created_at=session.created_at,
        )
    )
