"""
Evaluator for Scenario 5: Finance — Managing Supplier Payments
Organization: Orbit Manufacturing Ltd.
Role: Accounts Payable Analyst
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


SUPPLIER_PAYMENT_CHECKS = [
    {
        "id": "pay-steelpro",
        "supplier": "SteelPro",
        "amount_due": 120000,
        "due_date": "Today",
        "expected_decision": "Pay Full",
        "expected_priority": 1,
        "expected_payment_amount": 120000,
        "points": 20,
        "explanation": "Critical Raw Materials: Immediate line-stoppage risk and 2% daily penalty if unpaid today. Highest operational priority.",
    },
    {
        "id": "pay-cloudhost",
        "supplier": "CloudHost",
        "amount_due": 40000,
        "due_date": "In 2 days",
        "expected_decision": "Pay Full",
        "expected_priority": 2,
        "expected_payment_amount": 40000,
        "points": 20,
        "explanation": "Business-Critical Infrastructure: Automated system suspension on day 3. Relatively small outlay to protect digital operations.",
    },
    {
        "id": "pay-machinecare",
        "supplier": "MachineCare",
        "amount_due": 90000,
        "due_date": "Tomorrow",
        "expected_decision": "Pay Full",
        "acceptable_decisions": ["Pay Full", "Pay Discounted", "Negotiate Partial"],
        "expected_priority": 3,
        "expected_payment_amount": 88200,  # Or 90,000 if not taking 2% discount
        "points": 20,
        "explanation": "Strategic Maintenance: Eligible for 2% early payment discount (saves ₹1,800) and preserves heavy equipment uptime.",
    },
    {
        "id": "pay-printworks",
        "supplier": "PrintWorks",
        "amount_due": 50000,
        "due_date": "In 10 days",
        "expected_decision": "Defer",
        "expected_priority": 4,
        "expected_payment_amount": 0,
        "points": 15,
        "explanation": "Discretionary / Defer: Marketing materials not due for 10 days. Cash buffer is strictly needed for non-negotiable operational commitments.",
    },
    {
        "id": "pay-officemart",
        "supplier": "OfficeMart",
        "amount_due": 30000,
        "due_date": "In 7 days",
        "expected_decision": "Defer",
        "expected_priority": 5,
        "expected_payment_amount": 0,
        "points": 15,
        "explanation": "General Supplies: Not due for 7 days with generous grace period. Defer to next payment run without operational risk.",
    },
]

PAYMENT_QUESTION_RUBRICS = [
    {
        "id": "q1",
        "field": "q1PrioritisationCriteria",
        "question": "Q1: Which suppliers should be paid first, and what criteria did you use to prioritise them?",
        "keywords": ["steelpro", "cloudhost", "machinecare", "critical", "penalty", "operational", "hosting", "material"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "q2SizeVsCriticality",
        "question": "Q2: Would you ever prioritise a smaller invoice over a larger overdue invoice? Explain when and why.",
        "keywords": ["hosting", "cloudhost", "critical", "disrupt", "outage", "risk", "leverage", "vital"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "q3DiscountsVsCashPreservation",
        "question": "Q3: How would you balance early-payment discounts against the need to maintain sufficient cash?",
        "keywords": ["liquidity", "buffer", "discount", "working capital", "cash", "solvency", "reserve"],
        "required_keywords": 3,
        "min_word_count": 30,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "q4CashContingencyHandling",
        "question": "Q4: What would you do if the available cash decreased unexpectedly before the payment run?",
        "keywords": ["partial", "renegotiat", "freeze", "priorit", "triage", "contingency", "cfo"],
        "required_keywords": 3,
        "min_word_count": 30,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "q5SupplierCommunicationStrategy",
        "question": "Q5: How would you communicate payment delays to suppliers without damaging business relationships?",
        "keywords": ["transparen", "proactive", "date", "goodwill", "partner", "written", "notice"],
        "required_keywords": 3,
        "min_word_count": 30,
        "max_score": 10,
    },
    {
        "id": "q_email",
        "field": "supplierDeferralNoticeDraft",
        "question": "Supplier Deferral Notice: Professional email communication notifying delayed suppliers with a clear payment schedule.",
        "keywords": ["partner", "schedule", "payment", "friday", "orbit", "regard"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 15,
    },
]


def evaluate_payments_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    task_evaluations, total_task_pts, max_task_pts = _evaluate_payment_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = evaluate_rubric_questions(
        PAYMENT_QUESTION_RUBRICS, answers, evaluator=None, context="Orbit Manufacturing Ltd: Supplier Payment Prioritization & Cash Management"
    )

    return _build_payment_result(
        task_evaluations, q_evals, total_task_pts, max_task_pts, total_q, max_q, answers, integrity_flags, "deterministic"
    )


async def evaluate_payments_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    task_evaluations, total_task_pts, max_task_pts = _evaluate_payment_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = await evaluate_rubric_questions_async(
        PAYMENT_QUESTION_RUBRICS, answers, evaluator=ai_evaluator, context="Orbit Manufacturing Ltd: Supplier Payment Prioritization & Cash Management"
    )

    return _build_payment_result(
        task_evaluations, q_evals, total_task_pts, max_task_pts, total_q, max_q, answers, integrity_flags, "hybrid_ai" if any_ai else "deterministic"
    )


def _evaluate_payment_tasks(workspace_snapshot: Dict[str, Any]) -> tuple[List[Dict[str, Any]], int, int]:
    rows = workspace_snapshot.get("rows", workspace_snapshot.get("payments", []))
    task_evaluations = []
    total_pts = 0
    max_pts = 0
    total_disbursed = 0.0

    for rule in SUPPLIER_PAYMENT_CHECKS:
        max_pts += rule["points"]
        row = next((r for r in rows if r.get("id") == rule["id"] or r.get("supplier") == rule["supplier"]), None)

        if not row:
            task_evaluations.append({
                "id": rule["id"],
                "title": f"{rule['supplier']} Payment Allocation",
                "expected_decision": rule["expected_decision"],
                "actual_decision": "Missing Row",
                "is_correct": False,
                "points_earned": 0,
                "max_points": rule["points"],
                "explanation": f"Payment entry for {rule['supplier']} was omitted from the payment plan.",
            })
            continue

        decision = str(row.get("decision", "")).strip().lower()
        expected_dec = rule["expected_decision"].lower()
        acceptable = [a.lower() for a in rule.get("acceptable_decisions", [rule["expected_decision"]])]
        decision_ok = (decision in acceptable) or (expected_dec in decision)

        amount = float(row.get("paymentAmount", row.get("allocatedAmount", 0)) or 0)
        total_disbursed += amount

        if rule["expected_decision"] == "Pay Full":
            amount_ok = amount >= (rule["amount_due"] * 0.95)
        else:
            amount_ok = amount == 0

        pts = 0
        if decision_ok and amount_ok:
            pts = rule["points"]
        elif decision_ok or amount_ok:
            pts = round(rule["points"] * 0.5)

        total_pts += pts
        task_evaluations.append({
            "id": rule["id"],
            "title": f"{rule['supplier']} (Due: ₹{rule['amount_due']:,} — {rule['due_date']})",
            "expected_decision": f"{rule['expected_decision']} (₹{rule['expected_payment_amount']:,})",
            "actual_decision": f"{row.get('decision', 'None')} (₹{amount:,.2f})",
            "is_correct": pts >= rule["points"] * 0.75,
            "points_earned": pts,
            "max_points": rule["points"],
            "explanation": rule["explanation"] if pts == rule["points"] else f"Variance: Expected {rule['expected_decision']} for {rule['supplier']}.",
        })

    # Cash constraint check (Strict ₹3,00,000 ceiling)
    max_pts += 10
    budget_adhered = total_disbursed <= 300000.0
    pts_budget = 10 if budget_adhered else 0
    total_pts += pts_budget
    task_evaluations.append({
        "id": "task-cash-ceiling",
        "title": "Strict Cash Constraint Adherence (Max ₹3,00,000)",
        "expected_decision": "Total Disbursements <= ₹3,00,000",
        "actual_decision": f"Total Disbursed: ₹{total_disbursed:,.2f}",
        "is_correct": budget_adhered,
        "points_earned": pts_budget,
        "max_points": 10,
        "explanation": "Strict compliance with treasury cash cap of ₹3,00,000." if budget_adhered else f"Budget Overrun: Total disbursements (₹{total_disbursed:,.2f}) exceed the ₹3,00,000 cash limit.",
    })

    return task_evaluations, total_pts, max_pts


def _build_payment_result(
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
            "payment_allocation_score": round((total_task_pts / max_task_pts) * 100) if max_task_pts else 0,
            "commercial_judgement_score": round((total_q_pts / max_q_pts) * 100) if max_q_pts else 0,
            "total_points": total_pts,
            "max_points": max_pts,
            "ai_assisted": eval_method == "hybrid_ai",
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity_audit,
        "feedback_summary": (
            "Exemplary cash management: prioritized mission-critical suppliers, respected strict treasury constraints, and drafted professional deferral communications."
            if passed
            else "Payment plan breached treasury limits or delayed operational-critical vendors. Review supplier dependency hierarchy."
        ),
    }


__all__ = [
    "evaluate_payments_submission",
    "evaluate_payments_submission_async",
    "SUPPLIER_PAYMENT_CHECKS",
    "PAYMENT_QUESTION_RUBRICS",
]
