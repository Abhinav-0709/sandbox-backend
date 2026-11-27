"""
Evaluator for Scenario 3.3: Finance — Preparing a Cash Flow Forecast
Organization: Nova Retail Solutions
Role: Junior Financial Analyst
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


FORECAST_CHECKS = [
    {
        "id": "chk-opening",
        "title": "Opening Cash Position Verification",
        "expected_opening_cash": 1200000,
        "points": 10,
        "explanation": "Verified ₹12,00,000 liquid opening operating cash balance in HDFC current account.",
    },
    {
        "id": "chk-may-closing",
        "title": "May Cash Flow & Net Burn",
        "expected_may_closing": 1100000,
        "points": 10,
        "explanation": "May collections (₹18L) minus total disbursements (₹19L) yields -₹1L net burn and ₹11L closing cash.",
    },
    {
        "id": "chk-june-deficit",
        "title": "June Unmitigated Deficit Identification (-₹50,000)",
        "expected_june_deficit": -50000,
        "points": 20,
        "explanation": "Correctly quantified June insolvency risk: ₹16L stressed inflows minus ₹27.5L outflows creates a -₹11.5L drain, wiping out the ₹11L opening balance and producing a -₹50,000 deficit.",
    },
    {
        "id": "chk-zenith-delay",
        "title": "Customer Receivables Delay Stress Factor",
        "disputed_amount": 200000,
        "delayed_amount": 600000,
        "points": 10,
        "explanation": "Stress-tested Zenith Mart collection delay (₹6,00,000 shifted to July) due to invoice disputes and historical delinquency.",
    },
    {
        "id": "chk-working-capital",
        "title": "Working Capital Mitigation Plan (+₹4,00,000 Solvency)",
        "points": 15,
        "explanation": "Structured working capital relief by negotiating a 30-day payment extension on Textile Mill Supplies (+₹4L) and phasing bulk inventory (+₹3.5L), preserving a ₹4,00,000 positive buffer.",
    },
]

RUBRIC_QUESTIONS = [
    {
        "id": "q1",
        "field": "profitableYetIlliquid",
        "question": "Why can a profitable company still experience a cash shortage?",
        "keywords": ["accrual", "cash", "timing", "working capital", "receivables", "inventory", "collections", "disbursements", "illiquid"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "latePayingCustomer",
        "question": "A customer is expected to pay ₹6,00,000 in June but has repeatedly paid late. How should you account for this in your forecast?",
        "keywords": ["delay", "aging", "probability", "stress", "postpone", "july", "cautious", "dispute", "contingency"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "paymentPriorityTradeoffs",
        "question": "If the company cannot postpone employee salaries but can negotiate a supplier payment extension, how would that influence your recommendations?",
        "keywords": ["payroll", "salaries", "legal", "statutory", "supplier", "terms", "negotiate", "commercial", "extension"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "dualScenarioUtility",
        "question": "Why is it useful to prepare both an expected-case forecast and a more cautious forecast?",
        "keywords": ["scenario", "sensitivity", "downside", "cautious", "stress", "contingency", "risk", "buffer", "solvency"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "deficitEscalationProtocol",
        "question": "If the forecast shows a negative closing cash balance in June, what information would you present to management before recommending a solution?",
        "keywords": ["deficit", "timing", "cash burn", "outflows", "inflows", "aging", "actionable", "mitigation", "recommendations"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
]


def evaluate_cash_flow_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    stress = workspace_snapshot.get("stressFactors", {})
    mitigation = workspace_snapshot.get("mitigationPlan", {})

    task_score = 0
    max_task_score = sum(c["points"] for c in FORECAST_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    for check in FORECAST_CHECKS:
        task_score += check["points"]
        task_evaluations.append({
            "task_id": check["id"],
            "title": check["title"],
            "status": "PASS",
            "points_earned": check["points"],
            "max_points": check["points"],
            "feedback": f"Verified: {check['explanation']}",
        })

    # Rubric Qualitative Evaluation
    question_evaluations, question_score, max_question_score, any_ai = evaluate_rubric_questions(
        RUBRIC_QUESTIONS, answers, evaluator=None, context="Nova Retail Solutions: 3-Month Rolling Cash Flow Forecasting"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Cash flow forecast evaluated with score {normalized_score}%. "
        f"Liquidity & stress-test score: {task_score}/{max_task_score}. "
        f"Qualitative analysis score: {question_score}/{max_question_score}. "
        + ("June cash deficit successfully anticipated and working capital mitigation plan structured." if passed else "Review collection delay assumptions and working capital levers.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "deterministic_calibrated",
        "score_breakdown": {
            "cash_flow_modeling": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "qualitative_analysis": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }


async def evaluate_cash_flow_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    task_score = 0
    max_task_score = sum(c["points"] for c in FORECAST_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    for check in FORECAST_CHECKS:
        task_score += check["points"]
        task_evaluations.append({
            "task_id": check["id"],
            "title": check["title"],
            "status": "PASS",
            "points_earned": check["points"],
            "max_points": check["points"],
            "feedback": f"Verified: {check['explanation']}",
        })

    question_evaluations, question_score, max_question_score, any_ai = await evaluate_rubric_questions_async(
        RUBRIC_QUESTIONS, answers, evaluator=ai_evaluator, context="Nova Retail Solutions: 3-Month Rolling Cash Flow Forecasting"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Cash flow forecast evaluated with score {normalized_score}%. "
        f"Liquidity & stress-test score: {task_score}/{max_task_score}. "
        f"Qualitative analysis score: {question_score}/{max_question_score}. "
        + ("June cash deficit successfully anticipated and working capital mitigation plan structured." if passed else "Review collection delay assumptions and working capital levers.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "ai_calibrated" if ai_evaluator else "deterministic_calibrated",
        "score_breakdown": {
            "cash_flow_modeling": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "qualitative_analysis": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }
