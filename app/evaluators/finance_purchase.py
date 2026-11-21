"""
Evaluator for Scenario 3: Finance — Planning a Company Purchase
Organization: BrightEdge Technologies
Role: Junior Financial Analyst
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


PURCHASE_BENCHMARK_TASKS = [
    {
        "id": "task-cash-buffer",
        "title": "30-Day Operational Cash Buffer Calculation",
        "expected_value": 720000,
        "tolerance": 5000,
        "points": 20,
        "explanation": "Starting balance (₹8,00,000) + Inflows (₹4,00,000) - Non-discretionary commitments (₹4,80,000) = ₹7,20,000 operating cash buffer.",
    },
    {
        "id": "task-vendor-tco",
        "title": "3-Year Total Cost of Ownership (TCO) Comparison",
        "expected_tco": {
            "Vendor A": 1116000,  # 9,36,000 + 1,80,000 maintenance
            "Vendor B": 1120000,  # 11,20,000 + 0 maintenance (3-yr warranty)
            "Vendor C": 1200000,  # 9,60,000 + 2,40,000 maintenance
        },
        "points": 25,
        "explanation": "Accurately calculated full 3-year TCO including warranties and post-warranty maintenance estimates.",
    },
    {
        "id": "task-vendor-selection",
        "title": "Vendor & Payment Term Recommendation",
        "recommended_vendor": "Vendor B",
        "acceptable_vendors": ["Vendor B", "Vendor B (or Phased Vendor A)"],
        "points": 20,
        "explanation": "Vendor B selected for superior working capital preservation (Net 60 terms) and comprehensive 3-year warranty protection.",
    },
    {
        "id": "task-solvency-risk",
        "title": "Immediate Upfront Purchase Solvency Risk Assessment",
        "expected_decision": "High Risk / Do Not Proceed with 100% Upfront",
        "points": 15,
        "explanation": "Recognized that an immediate ₹9.36L cash outlay (Vendor A) consumes the entire ₹7.2L operating buffer, triggering severe insolvency risk.",
    },
]

PURCHASE_QUESTION_RUBRICS = [
    {
        "id": "q1",
        "field": "q1VendorTcoComparison",
        "question": "Q1: Which vendor would you recommend, and why might the cheapest quotation not be the best choice?",
        "keywords": ["tco", "ownership", "warranty", "maintenance", "hidden", "support", "vendor b", "cash"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "q2WorkingCapitalAffordability",
        "question": "Q2: Can the company afford the purchase without putting its upcoming financial commitments at risk?",
        "keywords": ["working capital", "salaries", "rent", "buffer", "liquidity", "commitments", "cash"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "q3DeferredPaymentImpact",
        "question": "Q3: What would change in your recommendation if the vendor offered a 60-day payment period?",
        "keywords": ["net 60", "deferred", "receivables", "collection", "inflow", "preserve", "cash"],
        "required_keywords": 3,
        "min_word_count": 30,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "q4PhasedRolloutStrategy",
        "question": "Q4: Would you recommend purchasing all 20 laptops immediately or splitting the purchase into phases?",
        "keywords": ["phase", "tranche", "hiring", "onboarding", "inventory", "smooth", "laptops"],
        "required_keywords": 3,
        "min_word_count": 30,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "q5SensitivityAssumptions",
        "question": "Q5: Which assumptions in your analysis would you want management to verify before approving the purchase?",
        "keywords": ["collection", "delay", "onboarding", "default", "risk", "warranty", "exchange", "tax"],
        "required_keywords": 3,
        "min_word_count": 30,
        "max_score": 10,
    },
    {
        "id": "q_memo",
        "field": "managementProposalDraft",
        "question": "Executive Financial Proposal: Formal procurement & cash-flow recommendation memo for Executive Management.",
        "keywords": ["recommend", "cash flow", "liquidity", "vendor", "phasing", "tco", "brightedge"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 15,
    },
]


def evaluate_purchase_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    task_evaluations, total_task_pts, max_task_pts = _evaluate_purchase_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = evaluate_rubric_questions(
        PURCHASE_QUESTION_RUBRICS, answers, evaluator=None, context="BrightEdge Technologies: Laptop Purchase Capital Planning"
    )

    return _build_purchase_result(
        task_evaluations, q_evals, total_task_pts, max_task_pts, total_q, max_q, answers, integrity_flags, "deterministic"
    )


async def evaluate_purchase_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    task_evaluations, total_task_pts, max_task_pts = _evaluate_purchase_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = await evaluate_rubric_questions_async(
        PURCHASE_QUESTION_RUBRICS, answers, evaluator=ai_evaluator, context="BrightEdge Technologies: Laptop Purchase Capital Planning"
    )

    return _build_purchase_result(
        task_evaluations, q_evals, total_task_pts, max_task_pts, total_q, max_q, answers, integrity_flags, "hybrid_ai" if any_ai else "deterministic"
    )


def _evaluate_purchase_tasks(workspace_snapshot: Dict[str, Any]) -> tuple[List[Dict[str, Any]], int, int]:
    calculations = workspace_snapshot.get("calculations", workspace_snapshot)
    task_evaluations = []
    total_pts = 0
    max_pts = 0

    # 1. Cash buffer
    max_pts += 20
    calc_buffer = float(calculations.get("operatingCashBuffer", calculations.get("cashBuffer", 0)) or 0)
    buffer_ok = abs(calc_buffer - 720000) <= 25000
    pts_buffer = 20 if buffer_ok else (10 if calc_buffer > 0 else 0)
    total_pts += pts_buffer
    task_evaluations.append({
        "id": "task-cash-buffer",
        "title": "30-Day Operational Cash Buffer (₹7,20,000 Expected)",
        "expected_value": "₹7,20,000",
        "actual_value": f"₹{calc_buffer:,.2f}",
        "is_correct": buffer_ok,
        "points_earned": pts_buffer,
        "max_points": 20,
        "explanation": "Correctly determined 30-day operating cash buffer after non-discretionary commitments." if buffer_ok else "Variance in cash buffer. Remember to subtract salaries (₹3L), rent (₹80k), software (₹40k), and other (₹60k).",
    })

    # 2. TCO Comparison
    max_pts += 25
    tco_data = calculations.get("vendorTco", {})
    tco_a = float(tco_data.get("Vendor A", 0) or 0)
    tco_b = float(tco_data.get("Vendor B", 0) or 0)
    tco_c = float(tco_data.get("Vendor C", 0) or 0)
    tco_correct_count = sum([
        abs(tco_a - 1116000) <= 50000,
        abs(tco_b - 1120000) <= 50000,
        abs(tco_c - 1200000) <= 50000,
    ])
    pts_tco = round((tco_correct_count / 3) * 25)
    total_pts += pts_tco
    task_evaluations.append({
        "id": "task-vendor-tco",
        "title": "3-Year Total Cost of Ownership Modeling",
        "expected_value": "A: ₹11.16L, B: ₹11.20L, C: ₹12.00L",
        "actual_value": f"A: ₹{tco_a:,.0f}, B: ₹{tco_b:,.0f}, C: ₹{tco_c:,.0f}",
        "is_correct": tco_correct_count >= 2,
        "points_earned": pts_tco,
        "max_points": 25,
        "explanation": "Factored hardware purchase price plus extended maintenance contracts into the multi-year TCO.",
    })

    # 3. Vendor selection
    max_pts += 20
    rec_vendor = str(calculations.get("recommendedVendor", "")).strip()
    vendor_ok = "vendor b" in rec_vendor.lower() or "systech" in rec_vendor.lower()
    pts_vendor = 20 if vendor_ok else 5
    total_pts += pts_vendor
    task_evaluations.append({
        "id": "task-vendor-selection",
        "title": "Recommended Vendor & Procurement Arrangement",
        "expected_value": "Vendor B (SysTech Enterprise Solutions)",
        "actual_value": rec_vendor or "None selected",
        "is_correct": vendor_ok,
        "points_earned": pts_vendor,
        "max_points": 20,
        "explanation": "Sound commercial decision: Vendor B avoids immediate cash drain through Net 60 terms while eliminating maintenance variance.",
    })

    # 4. Solvency risk
    max_pts += 15
    solvency_eval = str(calculations.get("solvencyRiskAssessment", calculations.get("affordabilityDecision", ""))).strip()
    solvency_ok = any(w in solvency_eval.lower() for w in ["risk", "cannot", "do not", "delay", "phase", "buffer", "deficit", "strain"])
    pts_solvency = 15 if solvency_ok else 5
    total_pts += pts_solvency
    task_evaluations.append({
        "id": "task-solvency-risk",
        "title": "Upfront Purchase Cash Drain Risk Assessment",
        "expected_value": "High Risk / Phased or Deferred Payment Required",
        "actual_value": solvency_eval or "Evaluated",
        "is_correct": solvency_ok,
        "points_earned": pts_solvency,
        "max_points": 15,
        "explanation": "Correctly diagnosed that immediate 100% upfront payment jeopardizes working capital reserves.",
    })

    return task_evaluations, total_pts, max_pts


def _build_purchase_result(
    task_evaluations: List[Dict[str, Any]],
    question_evaluations: List[Dict[str, Any]],
    total_task_pts: int,
    max_task_pts: int,
    total_q_pts: int,
    max_q_pts: int,
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    eval_method: str,
) -> Dict[str, Any]:
    paste_count = int(integrity_flags.get("pasteCount", 0))
    integrity_audit = evaluate_integrity(answers, paste_count=paste_count)

    total_pts = total_task_pts + total_q_pts
    max_pts = max_task_pts + max_q_pts
    overall = round((total_pts / max_pts) * 100) if max_pts else 0

    if integrity_audit["is_ai_flagged"]:
        overall = max(0, overall - 10)

    passed = overall >= 70 and not integrity_audit["is_ai_flagged"]

    return {
        "overall_score": overall,
        "passed": passed,
        "evaluation_method": eval_method,
        "score_breakdown": {
            "financial_modeling_score": round((total_task_pts / max_task_pts) * 100) if max_task_pts else 0,
            "commercial_reasoning_score": round((total_q_pts / max_q_pts) * 100) if max_q_pts else 0,
            "total_points": total_pts,
            "max_points": max_pts,
            "ai_assisted": eval_method == "hybrid_ai",
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity_audit,
        "feedback_summary": (
            "Superb capital planning: protected enterprise runway, analyzed full multi-year TCO, and formulated an actionable procurement strategy."
            if passed
            else "Analysis overlooked liquidity boundaries or multi-year maintenance costs. Re-evaluate cash commitments and terms."
        ),
    }


__all__ = [
    "evaluate_purchase_submission",
    "evaluate_purchase_submission_async",
    "PURCHASE_BENCHMARK_TASKS",
    "PURCHASE_QUESTION_RUBRICS",
]
