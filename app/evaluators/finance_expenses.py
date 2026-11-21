"""
Evaluator for Scenario 2: Finance — Reviewing Employee Expenses
Organization: Nova Retail Solutions
Role: Finance Operations Associate
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


# Global benchmark policy limits (Nova Retail Solutions)
POLICY_LIMITS = {
    "Meals": 800,
    "Local Travel": 1500,
    "Hotel": 4000,
    "Office Supplies": 5000,
}

# Calibrated claim audit rules
CLAIM_CHECKS = [
    {
        "id": "claim-rahul",
        "employee": "Rahul Sharma",
        "expense_type": "Meals",
        "claimed_amount": 650,
        "expected_decision": "Approve Full",
        "acceptable_decisions": ["Approve Full"],
        "expected_reimbursable": 650,
        "expected_non_reimbursable": 0,
        "expected_discrepancy": "None",
        "points": 15,
        "explanation": "Compliant claim within the ₹800 daily meal cap with valid itemized client lunch receipt.",
    },
    {
        "id": "claim-priya",
        "employee": "Priya Patel",
        "expense_type": "Local Travel",
        "claimed_amount": 2000,
        "expected_decision": "Partially Approve",
        "acceptable_decisions": ["Partially Approve", "Exception Approved"],
        "expected_reimbursable": 1500,
        "expected_non_reimbursable": 500,
        "expected_discrepancy": "Exceeds Policy Limit",
        "points": 20,
        "explanation": "Local travel policy cap is ₹1,500. ₹1,500 approved immediately; ₹500 overage flagged for manager exception approval.",
    },
    {
        "id": "claim-aman",
        "employee": "Aman Verma",
        "expense_type": "Hotel",
        "claimed_amount": 3500,
        "expected_decision": "Approve Full",
        "acceptable_decisions": ["Approve Full"],
        "expected_reimbursable": 3500,
        "expected_non_reimbursable": 0,
        "expected_discrepancy": "None",
        "points": 15,
        "explanation": "Legitimate conference accommodation under the ₹4,000 nightly cap with hotel folio attached.",
    },
    {
        "id": "claim-neha",
        "employee": "Neha Gupta",
        "expense_type": "Meals",
        "claimed_amount": 1200,
        "expected_decision": "Partially Approve",
        "acceptable_decisions": ["Partially Approve"],
        "expected_reimbursable": 800,
        "expected_non_reimbursable": 400,
        "expected_discrepancy": "Policy Violation / Excluded Item",
        "points": 20,
        "explanation": "Total is ₹1,200 with ₹400 alcohol itemized. Policy caps meals at ₹800 and explicitly excludes alcohol. ₹800 approved, ₹400 disallowed.",
    },
    {
        "id": "claim-rohan",
        "employee": "Rohan Mehta",
        "expense_type": "Office Supplies",
        "claimed_amount": 4500,
        "expected_decision": "Hold / Clarification",
        "acceptable_decisions": ["Hold / Clarification", "Reject"],
        "expected_reimbursable": 0,
        "expected_non_reimbursable": 4500,
        "expected_discrepancy": "Split Transaction",
        "points": 20,
        "explanation": "Audit pattern: Split purchase detected. Two claims totaling ₹8,700 within 24 hours from same vendor to evade the ₹5,000 manager sign-off threshold.",
    },
    {
        "id": "claim-kavita",
        "employee": "Kavita Desai",
        "expense_type": "Local Travel",
        "claimed_amount": 1400,
        "expected_decision": "Hold / Clarification",
        "acceptable_decisions": ["Hold / Clarification", "Reject"],
        "expected_reimbursable": 0,
        "expected_non_reimbursable": 1400,
        "expected_discrepancy": "Missing Documentation",
        "points": 10,
        "explanation": "Missing itemized receipt (only bank SMS screenshot attached). Requires authentic tax invoice per company policy.",
    },
]

EXPENSE_QUESTION_RUBRICS = [
    {
        "id": "q1",
        "field": "q1DecisionRationales",
        "question": "Q1: Which claims should be approved, rejected or sent back for clarification? Explain your decisions.",
        "keywords": ["policy limit", "receipt", "alcohol", "split transaction", "exception", "cap", "reimbursement"],
        "required_keywords": 4,
        "min_word_count": 45,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "q2ExceptionHandling",
        "question": "Q2: An employee has exceeded the expense limit but provides a reasonable business justification. How would you handle the situation?",
        "keywords": ["manager approval", "business justification", "exception workflow", "documentation", "partial reimbursement", "pre-approval"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "q3FraudVsMisunderstanding",
        "question": "Q3: How would you distinguish an honest policy misunderstanding from deliberate misuse of company funds?",
        "keywords": ["intent", "pattern", "recurring", "first-time", "concealment", "split", "training", "audit trail"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "q4AuditPatterns",
        "question": "Q4: What patterns in the expense data would make you investigate a claim further?",
        "keywords": ["round numbers", "weekend", "split invoices", "threshold", "duplicate", "vendor collusion", "velocity"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "q5ProcessImprovement",
        "question": "Q5: What changes would you recommend to reduce unnecessary spending without making the reimbursement process unfair to employees?",
        "keywords": ["corporate card", "per diem", "automated validation", "clear policy", "portal", "turnaround", "tiers"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q_report",
        "field": "auditReportDraft",
        "question": "Expense Audit Report: Short executive report highlighting recurring issues and process recommendations for Finance Management.",
        "keywords": ["summary", "total claimed", "discrepancies", "split purchasing", "receipt compliance", "recommendations", "governance"],
        "required_keywords": 4,
        "min_word_count": 50,
        "max_score": 15,
    },
]


def evaluate_expense_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    task_evaluations, total_claim_pts, max_claim_pts = _evaluate_claim_tasks(workspace_snapshot)

    # Synchronous rubric evaluation
    q_evals, total_q, max_q, any_ai = evaluate_rubric_questions(
        EXPENSE_QUESTION_RUBRICS, answers, evaluator=None, context="Nova Retail Solutions: Employee Expense Claims Audit"
    )

    return _build_expense_result(
        task_evaluations, q_evals, total_claim_pts, max_claim_pts, total_q, max_q, answers, integrity_flags, "deterministic"
    )


async def evaluate_expense_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    task_evaluations, total_claim_pts, max_claim_pts = _evaluate_claim_tasks(workspace_snapshot)

    # Async AI-assisted rubric evaluation
    q_evals, total_q, max_q, any_ai = await evaluate_rubric_questions_async(
        EXPENSE_QUESTION_RUBRICS, answers, evaluator=ai_evaluator, context="Nova Retail Solutions: Employee Expense Claims Audit"
    )

    return _build_expense_result(
        task_evaluations, q_evals, total_claim_pts, max_claim_pts, total_q, max_q, answers, integrity_flags, "hybrid_ai" if any_ai else "deterministic"
    )


def _evaluate_claim_tasks(workspace_snapshot: Dict[str, Any]) -> tuple[List[Dict[str, Any]], int, int]:
    claim_rows = workspace_snapshot.get("rows", workspace_snapshot.get("claims", []))
    task_evaluations = []
    total_points = 0
    max_points = 0

    for rule in CLAIM_CHECKS:
        max_points += rule["points"]
        row = next((r for r in claim_rows if r.get("id") == rule["id"] or r.get("employee") == rule["employee"]), None)

        if not row:
            task_evaluations.append({
                "id": rule["id"],
                "title": f"{rule['employee']} — {rule['expense_type']}",
                "expected_decision": rule["expected_decision"],
                "actual_decision": "Missing Row",
                "is_correct": False,
                "points_earned": 0,
                "max_points": rule["points"],
                "explanation": f"Claim for {rule['employee']} was missing from the audit worksheet.",
            })
            continue

        decision = str(row.get("decision", "")).strip()
        decision_ok = decision == rule["expected_decision"] or decision in rule["acceptable_decisions"]

        reimbursable = float(row.get("reimbursableAmount", row.get("verifiedAmount", 0)) or 0)
        reimbursable_ok = abs(reimbursable - rule["expected_reimbursable"]) <= 50

        discrepancy = str(row.get("discrepancyType", "")).strip()
        discrepancy_ok = (discrepancy.lower() == rule["expected_discrepancy"].lower()) or (
            rule["expected_discrepancy"] == "None" and discrepancy in ["", "None", "Compliant"]
        )

        if decision_ok and reimbursable_ok:
            pts = rule["points"]
        elif decision_ok or reimbursable_ok or discrepancy_ok:
            pts = round(rule["points"] * 0.5)
        else:
            pts = 0

        total_points += pts
        task_evaluations.append({
            "id": rule["id"],
            "title": f"{rule['employee']} — {rule['expense_type']} (₹{rule['claimed_amount']:,})",
            "expected_decision": rule["expected_decision"],
            "actual_decision": decision,
            "is_correct": pts >= rule["points"] * 0.75,
            "points_earned": pts,
            "max_points": rule["points"],
            "explanation": rule["explanation"] if pts == rule["points"] else f"Variance: Expected {rule['expected_decision']} (₹{rule['expected_reimbursable']:,}). Actual: {decision} (₹{reimbursable:,.2f}).",
        })

    return task_evaluations, total_points, max_points


def _build_expense_result(
    task_evaluations: List[Dict[str, Any]],
    question_evaluations: List[Dict[str, Any]],
    total_claim_pts: int,
    max_claim_pts: int,
    total_q_pts: int,
    max_q_pts: int,
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    eval_method: str,
) -> Dict[str, Any]:
    paste_count = int(integrity_flags.get("pasteCount", 0))
    integrity_audit = evaluate_integrity(answers, paste_count=paste_count)

    total_pts = total_claim_pts + total_q_pts
    max_pts = max_claim_pts + max_q_pts
    overall = round((total_pts / max_pts) * 100) if max_pts else 0

    if integrity_audit["is_ai_flagged"]:
        overall = max(0, overall - 10)

    passed = overall >= 70 and not integrity_audit["is_ai_flagged"]

    return {
        "overall_score": overall,
        "passed": passed,
        "evaluation_method": eval_method,
        "score_breakdown": {
            "claims_audit_score": round((total_claim_pts / max_claim_pts) * 100) if max_claim_pts else 0,
            "policy_reasoning_score": round((total_q_pts / max_q_pts) * 100) if max_q_pts else 0,
            "total_points": total_pts,
            "max_points": max_pts,
            "ai_assisted": eval_method == "hybrid_ai",
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity_audit,
        "feedback_summary": (
            "Outstanding expense audit: successfully identified policy limits, detected split transactions, and applied balanced exception judgment."
            if passed
            else "Audit fell below benchmark threshold. Pay careful attention to receipt compliance and threshold-splitting rules."
        ),
    }


__all__ = [
    "evaluate_expense_submission",
    "evaluate_expense_submission_async",
    "CLAIM_CHECKS",
    "EXPENSE_QUESTION_RUBRICS",
    "POLICY_LIMITS",
]
