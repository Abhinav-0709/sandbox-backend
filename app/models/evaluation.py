from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import String, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin, GUID

if TYPE_CHECKING:
    from app.models.session import SandboxSession
    from app.models.submission import SandboxSubmission


class SandboxEvaluationResult(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Official calibrated evaluation results computed from submission evidence.
    """
    __tablename__ = "sandbox_evaluation_results"

    submission_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("sandbox_submissions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    session_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("sandbox_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)  # 0 - 100
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    evaluation_method: Mapped[str] = mapped_column(String(50), default="deterministic", nullable=False)
    score_breakdown: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    task_evaluations: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    question_evaluations: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    integrity_audit: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    feedback_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    evaluator_version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    submission: Mapped[SandboxSubmission] = relationship("SandboxSubmission", back_populates="evaluation_result")
    session: Mapped[SandboxSession] = relationship("SandboxSession", back_populates="evaluation_result")
