from typing import Dict, Any, Optional
from app.evaluators.finance import evaluate_finance_submission, evaluate_finance_submission_async
from app.evaluators.finance_expenses import evaluate_expense_submission, evaluate_expense_submission_async
from app.evaluators.finance_purchase import evaluate_purchase_submission, evaluate_purchase_submission_async
from app.evaluators.finance_budget import evaluate_budget_submission, evaluate_budget_submission_async
from app.evaluators.finance_payments import evaluate_payments_submission, evaluate_payments_submission_async
from app.evaluators.hr import evaluate_hr_submission, evaluate_hr_submission_async
from app.evaluators.hr_onboarding import evaluate_onboarding_submission, evaluate_onboarding_submission_async
from app.evaluators.hr_complaints import evaluate_complaint_submission, evaluate_complaint_submission_async
from app.evaluators.hr_performance import evaluate_performance_submission, evaluate_performance_submission_async
from app.evaluators.hr_training import evaluate_training_submission, evaluate_training_submission_async
from app.evaluators.sde import evaluate_sde_submission, evaluate_sde_submission_async
from app.evaluators.anti_cheat import evaluate_integrity, detect_ai_markers
from app.evaluators.ai_assisted import (
    AiRubricEvaluator,
    AiEvaluationResult,
    evaluate_rubric_questions,
    evaluate_rubric_questions_async,
)


def evaluate_submission(
    category: str,
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    environment_slug: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Synchronously dispatches submission evaluation to the appropriate calibrated evaluator
    based on the environment category and slug using deterministic rubrics.
    """
    cat = (category or "").lower()
    slug = (environment_slug or "").lower()

    # Finance Scenarios
    if slug == "finance-expense-review":
        return evaluate_expense_submission(workspace_snapshot, answers, integrity_flags)
    elif slug == "finance-purchase-planning":
        return evaluate_purchase_submission(workspace_snapshot, answers, integrity_flags)
    elif slug == "finance-budget-review":
        return evaluate_budget_submission(workspace_snapshot, answers, integrity_flags)
    elif slug == "finance-supplier-payments":
        return evaluate_payments_submission(workspace_snapshot, answers, integrity_flags)
    elif cat == "finance" or slug == "finance-ap-reconciliation":
        return evaluate_finance_submission(workspace_snapshot, answers, integrity_flags)

    # HR Scenarios
    elif slug == "hr-employee-onboarding":
        return evaluate_onboarding_submission(workspace_snapshot, answers, integrity_flags)
    elif slug == "hr-complaint-investigation":
        return evaluate_complaint_submission(workspace_snapshot, answers, integrity_flags)
    elif slug == "hr-performance-review":
        return evaluate_performance_submission(workspace_snapshot, answers, integrity_flags)
    elif slug == "hr-training-planning":
        return evaluate_training_submission(workspace_snapshot, answers, integrity_flags)
    elif cat == "hr" or slug == "hr-candidate-screening":
        return evaluate_hr_submission(workspace_snapshot, answers, integrity_flags)

    # SDE Scenarios
    elif cat in ["sde", "software_engineering", "engineering"]:
        return evaluate_sde_submission(workspace_snapshot, answers, integrity_flags)
    else:
        integrity = evaluate_integrity(answers)
        return {
            "overall_score": 75,
            "passed": True,
            "evaluation_method": "generic",
            "score_breakdown": {"completed": 100},
            "task_evaluations": [],
            "question_evaluations": [],
            "integrity_audit": integrity,
            "feedback_summary": "Submission recorded and evaluated.",
        }


async def evaluate_submission_async(
    category: str,
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    environment_slug: Optional[str] = None,
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    """
    Asynchronously dispatches submission evaluation with AI-assisted qualitative scoring
    and automatic deterministic fallback.
    """
    cat = (category or "").lower()
    slug = (environment_slug or "").lower()

    # Finance Scenarios
    if slug == "finance-expense-review":
        return await evaluate_expense_submission_async(
            workspace_snapshot, answers, integrity_flags, ai_evaluator=ai_evaluator
        )
    elif slug == "finance-purchase-planning":
        return await evaluate_purchase_submission_async(
            workspace_snapshot, answers, integrity_flags, ai_evaluator=ai_evaluator
        )
    elif slug == "finance-budget-review":
        return await evaluate_budget_submission_async(
            workspace_snapshot, answers, integrity_flags, ai_evaluator=ai_evaluator
        )
    elif slug == "finance-supplier-payments":
        return await evaluate_payments_submission_async(
            workspace_snapshot, answers, integrity_flags, ai_evaluator=ai_evaluator
        )
    elif cat == "finance" or slug == "finance-ap-reconciliation":
        return await evaluate_finance_submission_async(
            workspace_snapshot, answers, integrity_flags, ai_evaluator=ai_evaluator
        )

    # HR Scenarios
    elif slug == "hr-employee-onboarding":
        return await evaluate_onboarding_submission_async(
            workspace_snapshot, answers, integrity_flags, ai_evaluator=ai_evaluator
        )
    elif slug == "hr-complaint-investigation":
        return await evaluate_complaint_submission_async(
            workspace_snapshot, answers, integrity_flags, ai_evaluator=ai_evaluator
        )
    elif slug == "hr-performance-review":
        return await evaluate_performance_submission_async(
            workspace_snapshot, answers, integrity_flags, ai_evaluator=ai_evaluator
        )
    elif slug == "hr-training-planning":
        return await evaluate_training_submission_async(
            workspace_snapshot, answers, integrity_flags, ai_evaluator=ai_evaluator
        )
    elif cat == "hr" or slug == "hr-candidate-screening":
        return await evaluate_hr_submission_async(
            workspace_snapshot, answers, integrity_flags, ai_evaluator=ai_evaluator
        )

    # SDE Scenarios
    elif cat in ["sde", "software_engineering", "engineering"]:
        return await evaluate_sde_submission_async(
            workspace_snapshot, answers, integrity_flags, ai_evaluator=ai_evaluator
        )
    else:
        integrity = evaluate_integrity(answers)
        return {
            "overall_score": 75,
            "passed": True,
            "evaluation_method": "generic",
            "score_breakdown": {"completed": 100},
            "task_evaluations": [],
            "question_evaluations": [],
            "integrity_audit": integrity,
            "feedback_summary": "Submission recorded and evaluated.",
        }


__all__ = [
    "evaluate_submission",
    "evaluate_submission_async",
    "evaluate_finance_submission",
    "evaluate_finance_submission_async",
    "evaluate_expense_submission",
    "evaluate_expense_submission_async",
    "evaluate_purchase_submission",
    "evaluate_purchase_submission_async",
    "evaluate_budget_submission",
    "evaluate_budget_submission_async",
    "evaluate_payments_submission",
    "evaluate_payments_submission_async",
    "evaluate_hr_submission",
    "evaluate_hr_submission_async",
    "evaluate_onboarding_submission",
    "evaluate_onboarding_submission_async",
    "evaluate_complaint_submission",
    "evaluate_complaint_submission_async",
    "evaluate_performance_submission",
    "evaluate_performance_submission_async",
    "evaluate_training_submission",
    "evaluate_training_submission_async",
    "evaluate_sde_submission",
    "evaluate_sde_submission_async",
    "evaluate_integrity",
    "detect_ai_markers",
    "AiRubricEvaluator",
    "AiEvaluationResult",
    "evaluate_rubric_questions",
    "evaluate_rubric_questions_async",
]

