from __future__ import annotations

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.execution.base import ResourceLimits


class ExecuteCommandRequest(BaseModel):
    command: str = Field(..., min_length=1, max_length=2000, description="Shell command to execute inside the sandbox")
    timeout_seconds: Optional[int] = Field(15, ge=1, le=120)
    resource_limits: Optional[ResourceLimits] = None


class ExecutionJobResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    job_type: str
    command: str
    status: str
    exit_code: Optional[int] = None
    stdout: Optional[str] = None
    stderr: Optional[str] = None
    duration_ms: Optional[int] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
