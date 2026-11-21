from __future__ import annotations

import uuid
from typing import Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime, timezone
from sqlalchemy import String, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import UUIDPrimaryKeyMixin, GUID

if TYPE_CHECKING:
    from app.models.session import SandboxSession


class SandboxActivityEvent(Base, UUIDPrimaryKeyMixin):
    """
    Append-only telemetry and activity events for evidence, anti-cheat, and audit trails.
    """
    __tablename__ = "sandbox_activity_events"

    session_id: Mapped[uuid.UUID] = mapped_column(
        GUID(),
        ForeignKey("sandbox_sessions.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_data: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    client_timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    server_timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    sequence_no: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    session: Mapped[SandboxSession] = relationship("SandboxSession", back_populates="events")
