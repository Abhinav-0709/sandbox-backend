import uuid
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.responses import ApiResponse
from app.core.auth import AuthenticatedUser, get_current_user_or_guest
from app.services.session_service import SessionService
from app.schemas.submission import SubmitAssessmentRequest
from app.schemas.evaluation import EvaluationResultResponse
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/sessions", tags=["submissions"])


@router.post("/{session_id}/submit", response_model=ApiResponse[EvaluationResultResponse])
async def submit_assessment(
    session_id: uuid.UUID,
    body: SubmitAssessmentRequest,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user_or_guest),
):
    service = SessionService(db)
    result = await service.submit_assessment(
        session_id=session_id,
        workspace_snapshot=body.workspace_snapshot,
        answers=body.answers,
        integrity_flags=body.integrity_flags,
        user=user,
    )
    return ApiResponse(
        data=EvaluationResultResponse(
            id=result.id,
            session_id=result.session_id,
            submission_id=result.submission_id,
            overall_score=result.overall_score,
            passed=result.passed,
            evaluation_method=result.evaluation_method,
            score_breakdown=result.score_breakdown,
            task_evaluations=result.task_evaluations,
            question_evaluations=result.question_evaluations,
            integrity_audit=result.integrity_audit,
            feedback_summary=result.feedback_summary,
            evaluated_at=result.evaluated_at,
        )
    )


@router.get("/{session_id}/result", response_model=ApiResponse[EvaluationResultResponse])
async def get_evaluation_result(
    session_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: AuthenticatedUser = Depends(get_current_user_or_guest),
):
    service = SessionService(db)
    session = await service.get_session(session_id, user=user)
    if not session.evaluation_result:
        raise NotFoundException("Evaluation result not ready or assessment not yet submitted.")

    res = session.evaluation_result
    return ApiResponse(
        data=EvaluationResultResponse(
            id=res.id,
            session_id=res.session_id,
            submission_id=res.submission_id,
            overall_score=res.overall_score,
            passed=res.passed,
            evaluation_method=res.evaluation_method,
            score_breakdown=res.score_breakdown,
            task_evaluations=res.task_evaluations,
            question_evaluations=res.question_evaluations,
            integrity_audit=res.integrity_audit,
            feedback_summary=res.feedback_summary,
            evaluated_at=res.evaluated_at,
        )
    )
