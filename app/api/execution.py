import uuid
from typing import List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from app.database import get_db
from app.core.responses import ApiResponse
from app.core.auth import AuthenticatedUser, get_current_user_or_guest
from app.core.exceptions import NotFoundException, ConflictException
from app.models.session import SandboxSession
from app.models.execution import ExecutionJob
from app.execution import default_execution_engine
from app.schemas.execution import ExecuteCommandRequest, ExecutionJobResponse

router = APIRouter(prefix="/sessions", tags=["execution"])


@router.post("/{session_id}/execute", response_model=ApiResponse[ExecutionJobResponse], status_code=status.HTTP_200_OK)
async def execute_command_in_sandbox(
    session_id: uuid.UUID,
    body: ExecuteCommandRequest,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user_or_guest),
):
    stmt = select(SandboxSession).where(SandboxSession.id == session_id)
    res = await db.execute(stmt)
    session = res.scalar_one_or_none()
    if not session:
        raise NotFoundException(f"Sandbox session '{session_id}' not found.")

    if session.status in ["COMPLETED", "TERMINATED"]:
        raise ConflictException(f"Cannot execute commands in session with terminal status '{session.status}'.")

    # Retrieve or provision container for this session
    container_id = session.session_metadata.get("container_id")
    if not container_id:
        container_info = default_execution_engine.provision_container(
            session_id=str(session.id),
            limits=body.resource_limits,
        )
        container_id = container_info.container_id
        session.session_metadata["container_id"] = container_id
        await db.flush()

    now = datetime.now(timezone.utc)
    job = ExecutionJob(
        session_id=session.id,
        job_type="command",
        command=body.command,
        status="running",
        started_at=now,
    )
    db.add(job)
    await db.flush()

    # Execute isolated command via execution engine
    exec_res = default_execution_engine.execute_command(
        container_id=container_id,
        command=body.command,
        timeout_seconds=body.timeout_seconds,
    )

    completed_at = datetime.now(timezone.utc)
    job.status = "timed_out" if exec_res.timed_out else "completed" if exec_res.exit_code == 0 else "failed"
    job.exit_code = exec_res.exit_code
    job.stdout = exec_res.stdout
    job.stderr = exec_res.stderr
    job.duration_ms = exec_res.duration_ms
    job.completed_at = completed_at

    await db.flush()
    await db.refresh(job)

    return ApiResponse(
        data=ExecutionJobResponse(
            id=job.id,
            session_id=job.session_id,
            job_type=job.job_type,
            command=job.command,
            status=job.status,
            exit_code=job.exit_code,
            stdout=job.stdout,
            stderr=job.stderr,
            duration_ms=job.duration_ms,
            started_at=job.started_at,
            completed_at=job.completed_at,
        )
    )


@router.get("/{session_id}/jobs", response_model=ApiResponse[List[ExecutionJobResponse]])
async def list_session_jobs(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user_or_guest),
):
    stmt = (
        select(ExecutionJob)
        .where(ExecutionJob.session_id == session_id)
        .order_by(desc(ExecutionJob.created_at))
    )
    res = await db.execute(stmt)
    jobs = list(res.scalars().all())

    return ApiResponse(
        data=[
            ExecutionJobResponse(
                id=j.id,
                session_id=j.session_id,
                job_type=j.job_type,
                command=j.command,
                status=j.status,
                exit_code=j.exit_code,
                stdout=j.stdout,
                stderr=j.stderr,
                duration_ms=j.duration_ms,
                started_at=j.started_at,
                completed_at=j.completed_at,
            )
            for j in jobs
        ]
    )
