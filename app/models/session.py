from __future__ import annotations

import uuid
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin, GUID

if TYPE_CHECKING:
    from app.models.environment import SandboxEnvironment
    from app.models.event import SandboxActivityEvent
    from app.models.submission import SandboxSubmission
    from app.models.evaluation import SandboxEvaluationResult


class SandboxSession(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    A single candidate's sandbox session for an assessment.
    Tracks state machine lifecycle, workspace edits, and authoritative time.
    """
    __tablename__ = "sandbox_sessions"

    environment_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("sandbox_environments.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_sub: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    user_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Lifecycle: CREATED -> READY -> RUNNING -> PAUSED -> COMPLETED -> TERMINATED
    status: Mapped[str] = mapped_column(String(50), default="CREATED", nullable=False, index=True)

    # Candidate working state (reconciliation table, screening decisions, bug fixes, draft answers)
    workspace_state: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Time limits and tracking
    time_limit_seconds: Mapped[int] = mapped_column(Integer, default=2400, nullable=False)
    time_remaining_seconds: Mapped[int] = mapped_column(Integer, default=2400, nullable=False)

    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    session_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Relationships
    environment: Mapped[SandboxEnvironment] = relationship("SandboxEnvironment", back_populates="sessions")
    events: Mapped[List[SandboxActivityEvent]] = relationship(
        "SandboxActivityEvent",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="SandboxActivityEvent.sequence_no",
    )
    submission: Mapped[Optional[SandboxSubmission]] = relationship(
        "SandboxSubmission", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
    evaluation_result: Mapped[Optional[SandboxEvaluationResult]] = relationship(
        "SandboxEvaluationResult", back_populates="session", uselist=False, cascade="all, delete-orphan"
    )
