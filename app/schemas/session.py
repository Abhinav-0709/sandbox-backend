from __future__ import annotations

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field


class CreateSessionRequest(BaseModel):
    environment_slug: str = Field(..., description="Slug of the sandbox environment, e.g. finance-ap-reconciliation")
    session_metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)


class UpdateSessionStatusRequest(BaseModel):
    status: str = Field(..., description="New status: READY, RUNNING, PAUSED, COMPLETED, TERMINATED")


class SaveWorkspaceStateRequest(BaseModel):
    workspace_state: Dict[str, Any] = Field(..., description="Candidate workspace state to persist")
    time_remaining_seconds: Optional[int] = Field(None, description="Remaining seconds on timer")


class SessionSummaryResponse(BaseModel):
    id: uuid.UUID
    environment_slug: str
    environment_title: str
    category: str
    status: str
    time_limit_seconds: int
    time_remaining_seconds: int
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime


class SessionDetailResponse(BaseModel):
    id: uuid.UUID
    environment_slug: str
    environment_title: str
    category: str
    status: str
    time_limit_seconds: int
    time_remaining_seconds: int
    workspace_state: Dict[str, Any]
    environment_config: Dict[str, Any]
    started_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
