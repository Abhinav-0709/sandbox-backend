from __future__ import annotations

import uuid
from typing import Dict, Any, Optional, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin, GUID

if TYPE_CHECKING:
    from app.models.session import SandboxSession
    from app.models.evaluation import SandboxEvaluationResult


class SandboxSubmission(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Assessment deliverable snapshot upon submission.
    """
    __tablename__ = "sandbox_submissions"

    session_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("sandbox_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        index=True
    )
    workspace_snapshot: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    answers: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    integrity_flags: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # pending, completed, failed
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    session: Mapped[SandboxSession] = relationship("SandboxSession", back_populates="submission")
    evaluation_result: Mapped[Optional[SandboxEvaluationResult]] = relationship(
        "SandboxEvaluationResult", back_populates="submission", uselist=False, cascade="all, delete-orphan"
    )
