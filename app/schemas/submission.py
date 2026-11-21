from __future__ import annotations

import uuid
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class SubmitAssessmentRequest(BaseModel):
    workspace_snapshot: Dict[str, Any] = Field(..., description="Final workspace state snapshot")
    answers: Dict[str, Any] = Field(..., description="Responses to written assessment questions")
    integrity_flags: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Client paste count & telemetry")


class SubmissionResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    status: str
    submitted_at: datetime
