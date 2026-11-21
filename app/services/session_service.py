from __future__ import annotations

import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from sqlalchemy.orm import selectinload

from app.models.session import SandboxSession
from app.models.environment import SandboxEnvironment
from app.models.submission import SandboxSubmission
from app.models.evaluation import SandboxEvaluationResult
from app.core.exceptions import NotFoundException, BadRequestException, ConflictException
from app.core.auth import AuthenticatedUser
from app.evaluators import evaluate_submission, evaluate_submission_async


VALID_TRANSITIONS = {
    "CREATED": ["READY", "RUNNING", "TERMINATED"],
    "READY": ["RUNNING", "TERMINATED"],
    "RUNNING": ["PAUSED", "COMPLETED", "TERMINATED"],
    "PAUSED": ["RUNNING", "COMPLETED", "TERMINATED"],
    "COMPLETED": [],
    "TERMINATED": [],
}


class SessionService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_or_resume_session(
        self,
        environment_slug: str,
        user: AuthenticatedUser,
        session_metadata: Optional[Dict[str, Any]] = None,
    ) -> SandboxSession:
        # 1. Fetch environment
        stmt_env = select(SandboxEnvironment).where(
            and_(SandboxEnvironment.slug == environment_slug, SandboxEnvironment.is_active == True)
        )
        res_env = await self.db.execute(stmt_env)
        env = res_env.scalar_one_or_none()
        if not env:
            raise NotFoundException(f"Sandbox environment '{environment_slug}' not found or inactive.")

        # 2. Check for active uncompleted session for this user
        stmt_active = (
            select(SandboxSession)
            .where(
                and_(
                    SandboxSession.environment_id == env.id,
                    SandboxSession.user_sub == user.sub,
                    SandboxSession.status.in_(["CREATED", "READY", "RUNNING", "PAUSED"]),
                )
            )
            .order_by(SandboxSession.created_at.desc())
            .options(selectinload(SandboxSession.environment))
        )
        res_active = await self.db.execute(stmt_active)
        active_sessions = res_active.scalars().all()

        if active_sessions:
            latest = active_sessions[0]
            # If multiple active duplicate sessions exist, terminate the older ones
            if len(active_sessions) > 1:
                for old in active_sessions[1:]:
                    old.status = "TERMINATED"
                await self.db.flush()
            return latest

        # 3. Create fresh session with initial starter workspace state
        initial_state = env.config.get("starter_workspace_state", {})
        time_limit = env.estimated_minutes * 60

        now = datetime.now(timezone.utc)
        session = SandboxSession(
            environment_id=env.id,
            user_sub=user.sub,
            user_email=user.email,
            status="READY",
            workspace_state=initial_state,
            time_limit_seconds=time_limit,
            time_remaining_seconds=time_limit,
            started_at=now,
            expires_at=now + timedelta(seconds=time_limit),
            session_metadata=session_metadata or {},
        )
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        session.environment = env
        return session

    async def get_session(self, session_id: uuid.UUID, user: Optional[AuthenticatedUser] = None) -> SandboxSession:
        stmt = (
            select(SandboxSession)
            .where(SandboxSession.id == session_id)
            .options(
                selectinload(SandboxSession.environment),
                selectinload(SandboxSession.submission),
                selectinload(SandboxSession.evaluation_result),
            )
        )
        res = await self.db.execute(stmt)
        session = res.scalar_one_or_none()
        if not session:
            raise NotFoundException(f"Sandbox session '{session_id}' not found.")
        return session

    async def update_status(
        self, session_id: uuid.UUID, new_status: str, user: Optional[AuthenticatedUser] = None
    ) -> SandboxSession:
        session = await self.get_session(session_id, user)
        target = new_status.upper()

        if target not in VALID_TRANSITIONS.get(session.status, []):
            raise ConflictException(
                f"Invalid status transition from {session.status} to {target}. Allowed: {VALID_TRANSITIONS.get(session.status, [])}"
            )

        now = datetime.now(timezone.utc)
        session.status = target

        if target == "RUNNING" and not session.started_at:
            session.started_at = now
            session.expires_at = now + timedelta(seconds=session.time_remaining_seconds)
        elif target in ["COMPLETED", "TERMINATED"]:
            session.completed_at = now

        await self.db.flush()
        return session

    async def save_workspace_state(
        self,
        session_id: uuid.UUID,
        workspace_state: Dict[str, Any],
        time_remaining_seconds: Optional[int] = None,
        user: Optional[AuthenticatedUser] = None,
    ) -> SandboxSession:
        session = await self.get_session(session_id, user)

        if session.status in ["COMPLETED", "TERMINATED"]:
            raise ConflictException(f"Cannot edit session in terminal state: {session.status}")

        session.workspace_state = workspace_state
        if time_remaining_seconds is not None:
            session.time_remaining_seconds = max(0, time_remaining_seconds)

        await self.db.flush()
        return session

    async def submit_assessment(
        self,
        session_id: uuid.UUID,
        workspace_snapshot: Dict[str, Any],
        answers: Dict[str, Any],
        integrity_flags: Optional[Dict[str, Any]] = None,
        user: Optional[AuthenticatedUser] = None,
    ) -> SandboxEvaluationResult:
        session = await self.get_session(session_id, user)

        if session.status == "COMPLETED" and session.evaluation_result:
            return session.evaluation_result

        now = datetime.now(timezone.utc)
        flags = integrity_flags or {}

        # 1. Create or update submission record
        stmt_sub = select(SandboxSubmission).where(SandboxSubmission.session_id == session.id)
        res_sub = await self.db.execute(stmt_sub)
        submission = res_sub.scalar_one_or_none()

        if not submission:
            submission = SandboxSubmission(
                session_id=session.id,
                workspace_snapshot=workspace_snapshot,
                answers=answers,
                integrity_flags=flags,
                status="completed",
                submitted_at=now,
            )
            self.db.add(submission)
            await self.db.flush()
        else:
            submission.workspace_snapshot = workspace_snapshot
            submission.answers = answers
            submission.integrity_flags = flags
            submission.status = "completed"
            await self.db.flush()

        # 2. Lock session as COMPLETED
        session.status = "COMPLETED"
        session.completed_at = now
        session.workspace_state = workspace_snapshot

        # 3. Run server-side calibrated evaluation (AI-assisted with deterministic fallback)
        eval_output = await evaluate_submission_async(
            category=session.environment.category,
            workspace_snapshot=workspace_snapshot,
            answers=answers,
            integrity_flags=flags,
            environment_slug=session.environment.slug,
        )

        eval_result = SandboxEvaluationResult(
            submission_id=submission.id,
            session_id=session.id,
            overall_score=eval_output["overall_score"],
            passed=eval_output["passed"],
            evaluation_method=eval_output.get("evaluation_method", "deterministic"),
            score_breakdown=eval_output.get("score_breakdown", {}),
            task_evaluations=eval_output.get("task_evaluations", []),
            question_evaluations=eval_output.get("question_evaluations", []),
            integrity_audit=eval_output.get("integrity_audit", {}),
            feedback_summary=eval_output.get("feedback_summary"),
            evaluator_version="1.0.0",
            evaluated_at=now,
        )
        self.db.add(eval_result)
        await self.db.flush()
        await self.db.refresh(eval_result)

        return eval_result
