from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.responses import ApiResponse
from app.services.environment_service import EnvironmentService
from app.schemas.environment import (
    EnvironmentSummaryResponse,
    EnvironmentDetailResponse,
    CreateEnvironmentRequest,
    UpdateEnvironmentRequest,
    PublishEnvironmentRequest,
)

router = APIRouter(prefix="/environments", tags=["environments"])


@router.get("", response_model=ApiResponse[List[EnvironmentSummaryResponse]])
async def list_environments(
    include_inactive: bool = Query(False, description="Whether to include inactive environments"),
    db: AsyncSession = Depends(get_db),
):
    service = EnvironmentService(db)
    envs = await service.list_environments(include_inactive=include_inactive)
    return ApiResponse(
        data=[
            EnvironmentSummaryResponse(
                id=e.id,
                slug=e.slug,
                title=e.title,
                description=e.description,
                category=e.category,
                department=e.department,
                role_title=e.role_title,
                difficulty=e.difficulty,
                estimated_minutes=e.estimated_minutes,
                version=e.version,
                is_active=e.is_active,
            )
            for e in envs
        ]
    )


@router.get("/{slug}", response_model=ApiResponse[EnvironmentDetailResponse])
async def get_environment_detail(slug: str, db: AsyncSession = Depends(get_db)):
    service = EnvironmentService(db)
    e = await service.get_by_slug(slug)
    return ApiResponse(
        data=EnvironmentDetailResponse(
            id=e.id,
            slug=e.slug,
            title=e.title,
            description=e.description,
            category=e.category,
            department=e.department,
            role_title=e.role_title,
            difficulty=e.difficulty,
            estimated_minutes=e.estimated_minutes,
            config=e.config,
            evaluation_rules=e.evaluation_rules,
            version=e.version,
            is_active=e.is_active,
        )
    )


@router.post("", response_model=ApiResponse[EnvironmentDetailResponse], status_code=status.HTTP_201_CREATED)
async def create_environment(
    body: CreateEnvironmentRequest,
    db: AsyncSession = Depends(get_db),
):
    service = EnvironmentService(db)
    e = await service.create_environment(body)
    return ApiResponse(
        data=EnvironmentDetailResponse(
            id=e.id,
            slug=e.slug,
            title=e.title,
            description=e.description,
            category=e.category,
            department=e.department,
            role_title=e.role_title,
            difficulty=e.difficulty,
            estimated_minutes=e.estimated_minutes,
            config=e.config,
            evaluation_rules=e.evaluation_rules,
            version=e.version,
            is_active=e.is_active,
        )
    )


@router.put("/{slug}", response_model=ApiResponse[EnvironmentDetailResponse])
async def update_environment(
    slug: str,
    body: UpdateEnvironmentRequest,
    db: AsyncSession = Depends(get_db),
):
    service = EnvironmentService(db)
    e = await service.update_environment(slug, body)
    return ApiResponse(
        data=EnvironmentDetailResponse(
            id=e.id,
            slug=e.slug,
            title=e.title,
            description=e.description,
            category=e.category,
            department=e.department,
            role_title=e.role_title,
            difficulty=e.difficulty,
            estimated_minutes=e.estimated_minutes,
            config=e.config,
            evaluation_rules=e.evaluation_rules,
            version=e.version,
            is_active=e.is_active,
        )
    )


@router.post("/{slug}/publish", response_model=ApiResponse[EnvironmentDetailResponse])
async def publish_environment_version(
    slug: str,
    body: PublishEnvironmentRequest,
    db: AsyncSession = Depends(get_db),
):
    service = EnvironmentService(db)
    e = await service.publish_version(slug, version_bump=body.version_bump, release_notes=body.release_notes)
    return ApiResponse(
        data=EnvironmentDetailResponse(
            id=e.id,
            slug=e.slug,
            title=e.title,
            description=e.description,
            category=e.category,
            department=e.department,
            role_title=e.role_title,
            difficulty=e.difficulty,
            estimated_minutes=e.estimated_minutes,
            config=e.config,
            evaluation_rules=e.evaluation_rules,
            version=e.version,
            is_active=e.is_active,
        )
    )


@router.delete("/{slug}", response_model=ApiResponse[dict])
async def delete_environment(
    slug: str,
    hard_delete: bool = Query(False, description="Permanent deletion"),
    db: AsyncSession = Depends(get_db),
):
    service = EnvironmentService(db)
    await service.delete_environment(slug, hard_delete=hard_delete)
    return ApiResponse(data={"deleted": True, "slug": slug})
