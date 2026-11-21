from __future__ import annotations

import uuid
from typing import Optional, Dict, Any, List, TYPE_CHECKING
from sqlalchemy import String, SmallInteger, Boolean, Text, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
from app.models.base import UUIDPrimaryKeyMixin, TimestampMixin, GUID

if TYPE_CHECKING:
    from app.models.session import SandboxSession


class SandboxEnvironment(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """
    Reusable environment definition for workplace sandbox assessments.
    Contains scenario metadata, initial documents/files/spreadsheets,
    and calibrated evaluation rules.
    """
    __tablename__ = "sandbox_environments"

    slug: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)  # 'finance', 'hr', 'sde'
    department: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    role_title: Mapped[str] = mapped_column(String(100), nullable=False)
    subrole_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    subrole_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    difficulty: Mapped[str] = mapped_column(String(50), default="intermediate", nullable=False)
    estimated_minutes: Mapped[int] = mapped_column(SmallInteger, default=40, nullable=False)

    # Full scenario definition: instructions, documents, candidate CVs, initial codebase, tasks
    config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    # Rules & rubrics used by deterministic & rubric evaluators
    evaluation_rules: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False, index=True)
    version: Mapped[str] = mapped_column(String(20), default="1.0.0", nullable=False)

    # Optional foreign key to external simulation definition if linked
    external_simulation_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        GUID(),
        nullable=True,
        index=True
    )

    # Relationships
    sessions: Mapped[List[SandboxSession]] = relationship(
        "SandboxSession", back_populates="environment", cascade="all, delete-orphan"
    )
