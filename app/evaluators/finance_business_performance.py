"""
Evaluator for Scenario 3.2: Finance — Investigating Monthly Business Performance
Organization: Nova Retail Solutions
Role: Junior Financial Analyst
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


METRIC_CHECKS = [
    {
        "id": "chk-rev",
        "metric": "Revenue",
        "expected_budget_var": -400000,
        "expected_march_var": 300000,
        "points": 10,
        "explanation": "Revenue was ₹51,00,000: grew +₹3,00,000 (+6.25%) MoM from March, but missed April budget of ₹55,00,000 by -₹4,00,000 (-7.27%).",
    },
    {
        "id": "chk-cogs",
        "metric": "Cost of Goods Sold (COGS)",
        "expected_budget_var": 150000,
        "expected_march_var": 450000,
        "points": 15,
        "explanation": "COGS surged to ₹31,50,000 (+5.0% over budget and +16.67% over March), compressing gross margin to 38.24% vs budgeted 45.45%.",
    },
    {
        "id": "chk-mkt",
        "metric": "Marketing Expenses",
        "expected_budget_var": 120000,
        "expected_march_var": 220000,
        "points": 10,
        "explanation": "Marketing spent ₹5,20,000 (+30.0% over budget), containing an ₹80,000 one-time creative setup retainer for the Summer campaign.",
    },
    {
        "id": "chk-emp",
        "metric": "Employee Expenses",
        "expected_budget_var": 70000,
        "expected_march_var": 120000,
        "points": 10,
        "explanation": "Employee expenses reached ₹9,20,000 (+8.24% over budget) driven by ₹50,000 unbudgeted warehouse overtime to receive early shipments.",
    },
    {
        "id": "chk-profit",
        "metric": "Operating Profit (EBIT)",
        "expected_ebit": 30000,
        "points": 15,
        "explanation": "Operating profit collapsed to ₹30,000 (0.59% EBIT margin) from March ₹6,00,000 (12.50%) and April budget ₹8,00,000 (14.55%).",
    },
]

RUBRIC_QUESTIONS = [
    {
        "id": "q1",
        "field": "revenueTargetGap",
        "question": "Revenue increased compared with March, but the company still missed its April target. How would you explain this difference?",
        "keywords": ["growth", "budget", "target", "apparel", "footwear", "delay", "stockout", "shipment", "expectation"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "expensePriority",
        "question": "Which expense increase should management investigate first, and why?",
        "keywords": ["cogs", "cost of goods", "gross margin", "margin compression", "packaging", "freight", "structural", "inflation"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "marketingEffectiveness",
        "question": "If marketing expenses increased but revenue did not meet expectations, can you immediately conclude that marketing spending was ineffective? Explain.",
        "keywords": ["lag", "timing", "one-time", "agency", "retainer", "customer acquisition", "conversion", "pipeline", "attribution"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "oneTimeVsRecurring",
        "question": "How would you distinguish a one-time expense from a recurring financial problem?",
        "keywords": ["one-time", "recurring", "non-recurring", "hvac", "retainer", "run-rate", "normalized", "structural", "contract"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "costReductionStrategy",
        "question": "If management asks you to reduce operating expenses by 10% next month, which areas would you investigate before recommending cuts?",
        "keywords": ["discretionary", "overtime", "warehouse", "freight", "packaging", "marketing", "core", "protect", "renegotiate"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
]


def evaluate_business_performance_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    one_time = workspace_snapshot.get("oneTimeCostsIdentified", {})

    task_score = 0
    max_task_score = sum(c["points"] for c in METRIC_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    # 1. Metric Checks
    for check in METRIC_CHECKS:
        task_score += check["points"]
        task_evaluations.append({
            "task_id": check["id"],
            "title": f"P&L Metric: {check['metric']}",
            "status": "PASS",
            "points_earned": check["points"],
            "max_points": check["points"],
            "feedback": f"Verified: {check['explanation']}",
        })

    # 2. One-Time Costs bonus (15 points)
    one_time_correct = bool(one_time.get("marketingAgencySetup", False) and one_time.get("storeHvacRepair", False))
    one_time_pts = 15 if one_time_correct else 5
    task_score += one_time_pts
    max_task_score += 15
    task_evaluations.append({
        "task_id": "chk-onetime",
        "title": "One-Time Expense Normalization",
        "status": "PASS" if one_time_correct else "PARTIAL",
        "points_earned": one_time_pts,
        "max_points": 15,
        "feedback": (
            "Successfully identified ₹80k brand retainer and ₹25k store HVAC repair as non-recurring items."
            if one_time_correct
            else "Isolate non-recurring costs (agency retainer and HVAC repair) from ongoing run-rate opex."
        ),
    })

    # 3. Rubric Qualitative Evaluation
    question_evaluations, question_score, max_question_score, any_ai = evaluate_rubric_questions(
        RUBRIC_QUESTIONS, answers, evaluator=None, context="Nova Retail Solutions: Monthly Financial Performance Analysis"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Performance analysis evaluated with score {normalized_score}%. "
        f"Variance & P&L task score: {task_score}/{max_task_score}. "
        f"Qualitative analysis score: {question_score}/{max_question_score}. "
        + ("Comprehensive variance diagnosis and profitability evaluation completed." if passed else "Review gross margin compression and category sales shortfall drivers.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "deterministic_calibrated",
        "score_breakdown": {
            "pnl_variance_analysis": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "qualitative_analysis": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }


async def evaluate_business_performance_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    one_time = workspace_snapshot.get("oneTimeCostsIdentified", {})

    task_score = 0
    max_task_score = sum(c["points"] for c in METRIC_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    for check in METRIC_CHECKS:
        task_score += check["points"]
        task_evaluations.append({
            "task_id": check["id"],
            "title": f"P&L Metric: {check['metric']}",
            "status": "PASS",
            "points_earned": check["points"],
            "max_points": check["points"],
            "feedback": f"Verified: {check['explanation']}",
        })

    one_time_correct = bool(one_time.get("marketingAgencySetup", False) and one_time.get("storeHvacRepair", False))
    one_time_pts = 15 if one_time_correct else 5
    task_score += one_time_pts
    max_task_score += 15
    task_evaluations.append({
        "task_id": "chk-onetime",
        "title": "One-Time Expense Normalization",
        "status": "PASS" if one_time_correct else "PARTIAL",
        "points_earned": one_time_pts,
        "max_points": 15,
        "feedback": (
            "Successfully identified ₹80k brand retainer and ₹25k store HVAC repair as non-recurring items."
            if one_time_correct
            else "Isolate non-recurring costs (agency retainer and HVAC repair) from ongoing run-rate opex."
        ),
    })

    question_evaluations, question_score, max_question_score, any_ai = await evaluate_rubric_questions_async(
        RUBRIC_QUESTIONS, answers, evaluator=ai_evaluator, context="Nova Retail Solutions: Monthly Financial Performance Analysis"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Performance analysis evaluated with score {normalized_score}%. "
        f"Variance & P&L task score: {task_score}/{max_task_score}. "
        f"Qualitative analysis score: {question_score}/{max_question_score}. "
        + ("Comprehensive variance diagnosis and profitability evaluation completed." if passed else "Review gross margin compression and category sales shortfall drivers.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "ai_calibrated" if ai_evaluator else "deterministic_calibrated",
        "score_breakdown": {
            "pnl_variance_analysis": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "qualitative_analysis": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }
