"""
Evaluator for Scenario 4: Finance — Reviewing Department Budgets
Organization: Vertex Solutions
Role: Budget Analyst
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


DEPARTMENT_BUDGET_CHECKS = [
    {
        "id": "dept-marketing",
        "department": "Marketing",
        "planned": 200000,
        "actual": 250000,
        "expected_variance": -50000,
        "expected_variance_pct": -25.0,
        "variance_type": "Unfavorable",
        "classification": "Timing Difference & One-Time Spend",
        "points": 15,
        "explanation": "₹50k unfavorable: ₹35k was a prior-quarter agency invoice delayed into April, and ₹15k was expedited launch campaign advertising.",
    },
    {
        "id": "dept-technology",
        "department": "Technology",
        "planned": 300000,
        "actual": 280000,
        "expected_variance": 20000,
        "expected_variance_pct": 6.7,
        "variance_type": "Favorable",
        "classification": "Timing Delay (Temporary)",
        "points": 15,
        "explanation": "₹20k favorable: Cloud discounts realized, but ₹15k database migration costs were deferred into May.",
    },
    {
        "id": "dept-hr",
        "department": "HR",
        "planned": 100000,
        "actual": 120000,
        "expected_variance": -20000,
        "expected_variance_pct": -20.0,
        "variance_type": "Unfavorable",
        "classification": "One-Time Authorized Capital",
        "points": 15,
        "explanation": "₹20k unfavorable: Executive search recruiter success fee for VP engineering placement (pre-approved by CEO, non-recurring).",
    },
    {
        "id": "dept-operations",
        "department": "Operations",
        "planned": 250000,
        "actual": 240000,
        "expected_variance": 10000,
        "expected_variance_pct": 4.0,
        "variance_type": "Favorable",
        "classification": "Recurring Operational Efficiency",
        "points": 10,
        "explanation": "₹10k favorable: Consistent supply chain control and travel efficiencies.",
    },
    {
        "id": "dept-sales",
        "department": "Sales",
        "planned": 150000,
        "actual": 180000,
        "expected_variance": -30000,
        "expected_variance_pct": -20.0,
        "variance_type": "Unfavorable (Revenue-Generating)",
        "classification": "Activity-Driven Variable Commission",
        "points": 20,
        "explanation": "₹30k unfavorable: Driven entirely by 140% sales quota attainment generating ₹6,00,000 in top-line revenue. Highly accretive.",
    },
]

BUDGET_QUESTION_RUBRICS = [
    {
        "id": "q1",
        "field": "q1ImmediateAttention",
        "question": "Q1: Which departments require immediate attention, and what evidence supports your conclusion?",
        "keywords": ["marketing", "hr", "sales", "unfavorable", "variance", "timing", "commission"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "q2ActivityVsControlOverspending",
        "question": "Q2: How would you distinguish between overspending caused by increased business activity and overspending caused by poor financial control?",
        "keywords": ["revenue", "sales", "commission", "variable", "activity", "control", "governance", "quota"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "q3InvestigateVsReduce",
        "question": "Q3: Which expenses should be investigated rather than automatically reduced?",
        "keywords": ["growth", "talent", "recruitment", "marketing", "acquisition", "strategic", "cut", "roi"],
        "required_keywords": 3,
        "min_word_count": 30,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "q4QuarterlyForecastAdjustments",
        "question": "Q4: Based on the available information, what changes would you make to the next quarter's budget?",
        "keywords": ["technology", "migration", "forecast", "re-forecast", "pipeline", "baseline", "accrual"],
        "required_keywords": 3,
        "min_word_count": 30,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "q5ManagerDisagreementResponse",
        "question": "Q5: A department manager disagrees with your findings and argues that the additional spending was necessary. How would you respond?",
        "keywords": ["objective", "data", "partner", "variance", "collaborat", "kpi", "roi", "evidence"],
        "required_keywords": 3,
        "min_word_count": 30,
        "max_score": 10,
    },
    {
        "id": "q_briefing",
        "field": "budgetVarianceBriefingDraft",
        "question": "Budget Variance Briefing: Formal variance explanation and re-forecast briefing for the Executive Committee.",
        "keywords": ["variance", "favorable", "unfavorable", "timing", "sales", "vertex", "recommend"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 15,
    },
]


def evaluate_budget_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    task_evaluations, total_var_pts, max_var_pts = _evaluate_budget_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = evaluate_rubric_questions(
        BUDGET_QUESTION_RUBRICS, answers, evaluator=None, context="Vertex Solutions: Department Budget Variance Analysis"
    )

    return _build_budget_result(
        task_evaluations, q_evals, total_var_pts, max_var_pts, total_q, max_q, answers, integrity_flags, "deterministic"
    )


async def evaluate_budget_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    task_evaluations, total_var_pts, max_var_pts = _evaluate_budget_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = await evaluate_rubric_questions_async(
        BUDGET_QUESTION_RUBRICS, answers, evaluator=ai_evaluator, context="Vertex Solutions: Department Budget Variance Analysis"
    )

    return _build_budget_result(
        task_evaluations, q_evals, total_var_pts, max_var_pts, total_q, max_q, answers, integrity_flags, "hybrid_ai" if any_ai else "deterministic"
    )


def _evaluate_budget_tasks(workspace_snapshot: Dict[str, Any]) -> tuple[List[Dict[str, Any]], int, int]:
    rows = workspace_snapshot.get("rows", workspace_snapshot.get("departments", []))
    task_evaluations = []
    total_pts = 0
    max_pts = 0

    for rule in DEPARTMENT_BUDGET_CHECKS:
        max_pts += rule["points"]
        row = next((r for r in rows if r.get("id") == rule["id"] or r.get("department") == rule["department"]), None)

        if not row:
            task_evaluations.append({
                "id": rule["id"],
                "title": f"{rule['department']} Variance Analysis",
                "expected_variance": f"₹{rule['expected_variance']:,}",
                "actual_variance": "Missing Row",
                "is_correct": False,
                "points_earned": 0,
                "max_points": rule["points"],
                "explanation": f"Department row for {rule['department']} was missing from the analysis sheet.",
            })
            continue

        var_val = float(row.get("varianceAmount", row.get("variance", 0)) or 0)
        var_ok = abs(abs(var_val) - abs(rule["expected_variance"])) <= 1000

        var_type = str(row.get("varianceType", "")).strip().lower()
        type_ok = rule["variance_type"].lower().startswith(var_type) if var_type else False

        pts = 0
        if var_ok and type_ok:
            pts = rule["points"]
        elif var_ok or type_ok:
            pts = round(rule["points"] * 0.6)

        total_pts += pts
        task_evaluations.append({
            "id": rule["id"],
            "title": f"{rule['department']} (Planned: ₹{rule['planned']:,} | Actual: ₹{rule['actual']:,})",
            "expected_variance": f"{rule['variance_type']} (₹{rule['expected_variance']:,})",
            "actual_variance": f"{row.get('varianceType', 'Unspecified')} (₹{var_val:,.2f})",
            "is_correct": pts >= rule["points"] * 0.75,
            "points_earned": pts,
            "max_points": rule["points"],
            "explanation": rule["explanation"] if pts == rule["points"] else f"Variance calculation difference. Expected {rule['variance_type']} of ₹{rule['expected_variance']:,}.",
        })

    return task_evaluations, total_pts, max_pts


def _build_budget_result(
    task_evaluations: List[Dict[str, Any]],
    question_evaluations: List[Dict[str, Any]],
    total_var_pts: int,
    max_var_pts: int,
    total_q_pts: int,
    max_q_pts: int,
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    eval_method: str,
) -> Dict[str, Any]:
    paste_count = int(integrity_flags.get("pasteCount", 0))
    integrity_audit = evaluate_integrity(answers, paste_count=paste_count)

    total_pts = total_var_pts + total_q_pts
    max_pts = max_var_pts + max_q_pts
    overall = round((total_pts / max_pts) * 100) if max_pts else 0

    if integrity_audit["is_ai_flagged"]:
        overall = max(0, overall - 10)

    passed = overall >= 70 and not integrity_audit["is_ai_flagged"]

    return {
        "overall_score": overall,
        "passed": passed,
        "evaluation_method": eval_method,
        "score_breakdown": {
            "variance_analysis_score": round((total_var_pts / max_var_pts) * 100) if max_var_pts else 0,
            "financial_reasoning_score": round((total_q_pts / max_q_pts) * 100) if max_q_pts else 0,
            "total_points": total_pts,
            "max_points": max_pts,
            "ai_assisted": eval_method == "hybrid_ai",
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity_audit,
        "feedback_summary": (
            "Exemplary variance analysis: clearly distinguished volume/commission growth from timing lags and communicated actionable financial recommendations."
            if passed
            else "Variance analysis missed key root causes or conflated revenue growth with operational inefficiency."
        ),
    }


__all__ = [
    "evaluate_budget_submission",
    "evaluate_budget_submission_async",
    "DEPARTMENT_BUDGET_CHECKS",
    "BUDGET_QUESTION_RUBRICS",
]
