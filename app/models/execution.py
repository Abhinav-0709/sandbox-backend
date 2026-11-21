from __future__ import annotations

import uuid
from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin, GUID


class ExecutionJob(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Tracks command execution jobs running inside isolated container sandboxes.
    """
    __tablename__ = "sandbox_execution_jobs"

    session_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("sandbox_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    job_type: Mapped[str] = mapped_column(String(50), default="command", nullable=False)  # command, test_run, file_write
    command: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="queued", nullable=False, index=True)  # queued, running, completed, failed, timed_out
    
    exit_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    stdout: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    stderr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    
    execution_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
