from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel


class EvaluationResultResponse(BaseModel):
    id: uuid.UUID
    session_id: uuid.UUID
    submission_id: uuid.UUID
    overall_score: int
    passed: bool
    evaluation_method: str
    score_breakdown: Dict[str, Any]
    task_evaluations: List[Dict[str, Any]]
    question_evaluations: List[Dict[str, Any]]
    integrity_audit: Dict[str, Any]
    feedback_summary: Optional[str] = None
    evaluated_at: datetime
