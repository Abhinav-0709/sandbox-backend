from __future__ import annotations

import uuid
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class CreateEnvironmentRequest(BaseModel):
    slug: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-z0-9-]+$", description="URL-friendly unique identifier")
    title: str = Field(..., min_length=3, max_length=255)
    description: Optional[str] = None
    category: str = Field(..., description="Category: finance, hr, sde, sales, marketing, operations")
    department: str = Field(..., max_length=100)
    role_title: str = Field(..., max_length=100)
    subrole_id: Optional[str] = Field(None, max_length=100, description="Parent subrole identifier")
    subrole_title: Optional[str] = Field(None, max_length=100, description="Parent subrole title")
    difficulty: str = Field("intermediate", description="beginner, intermediate, advanced, expert")
    estimated_minutes: int = Field(40, ge=5, le=240)
    config: Dict[str, Any] = Field(default_factory=dict, description="Scenario tasks, starter state, documents, resources")
    evaluation_rules: Dict[str, Any] = Field(default_factory=dict, description="Deterministic rules and question rubrics")


class UpdateEnvironmentRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    department: Optional[str] = None
    role_title: Optional[str] = None
    subrole_id: Optional[str] = None
    subrole_title: Optional[str] = None
    difficulty: Optional[str] = None
    estimated_minutes: Optional[int] = None
    config: Optional[Dict[str, Any]] = None
    evaluation_rules: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class PublishEnvironmentRequest(BaseModel):
    version_bump: str = Field("minor", description="patch, minor, major")
    release_notes: Optional[str] = None


class EnvironmentSummaryResponse(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: Optional[str] = None
    category: str
    department: str
    role_title: str
    subrole_id: Optional[str] = None
    subrole_title: Optional[str] = None
    difficulty: str
    estimated_minutes: int
    version: str
    is_active: bool


class EnvironmentDetailResponse(BaseModel):
    id: uuid.UUID
    slug: str
    title: str
    description: Optional[str] = None
    category: str
    department: str
    role_title: str
    subrole_id: Optional[str] = None
    subrole_title: Optional[str] = None
    difficulty: str
    estimated_minutes: int
    config: Dict[str, Any]
    evaluation_rules: Dict[str, Any]
    version: str
    is_active: bool
