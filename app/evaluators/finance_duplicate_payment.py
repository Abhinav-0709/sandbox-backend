"""
Evaluator for Scenario 2.2: Finance — Investigating a Duplicate Supplier Payment
Organization: Nova Retail Solutions
Role: Finance Operations Associate
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


PAYMENT_CHECKS = [
    {
        "id": "pay-001",
        "payment_no": "Payment 001",
        "supplier": "Apex Office Supplies",
        "invoice_ref": "INV-7841",
        "amount": 118000,
        "expected_decision": "Confirmed Duplicate",
        "acceptable_decisions": ["Confirmed Duplicate", "Valid Payment"],
        "expected_reconciled_amount": 118000,
        "expected_discrepancy": "Timeout False Failure / Bank Cleared",
        "points": 15,
        "explanation": "Payment 001 timed out internally with HTTP 504 but cleared HDFC Bank under CMS-HDFC-994102. It is the initial valid payment for INV-7841.",
    },
    {
        "id": "pay-002",
        "payment_no": "Payment 002",
        "supplier": "Apex Office Supplies",
        "invoice_ref": "INV-7841",
        "amount": 118000,
        "expected_decision": "Confirmed Duplicate",
        "acceptable_decisions": ["Confirmed Duplicate"],
        "expected_reconciled_amount": 0,
        "expected_discrepancy": "Duplicate Disbursement",
        "points": 25,
        "explanation": "Payment 002 was manually re-queued without checking the bank. It represents a redundant ₹1,18,000 disbursement that must be recovered.",
    },
    {
        "id": "pay-003",
        "payment_no": "Payment 003",
        "supplier": "Bright Logistics",
        "invoice_ref": "INV-2205",
        "amount": 76000,
        "expected_decision": "Valid Payment",
        "acceptable_decisions": ["Valid Payment"],
        "expected_reconciled_amount": 76000,
        "expected_discrepancy": "None",
        "points": 10,
        "explanation": "Legitimate freight expense matching freight invoice INV-2205 and cleared bank debit CMS-HDFC-996114.",
    },
    {
        "id": "pay-004",
        "payment_no": "Payment 004",
        "supplier": "Apex Office Supplies",
        "invoice_ref": "INV-7890",
        "amount": 42000,
        "expected_decision": "Valid Payment",
        "acceptable_decisions": ["Valid Payment"],
        "expected_reconciled_amount": 42000,
        "expected_discrepancy": "None",
        "points": 10,
        "explanation": "Legitimate stationery order matching invoice INV-7890 and cleared bank debit CMS-HDFC-997230.",
    },
]

RUBRIC_QUESTIONS = [
    {
        "id": "q1",
        "field": "verificationMethod",
        "question": "How would you establish whether the second payment was genuinely duplicated rather than allocated to another outstanding invoice?",
        "keywords": ["reconciliation", "bank statement", "utr", "ledger", "invoice", "statement of account", "allocation", "credit balance"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "conflictingRecords",
        "question": "The internal payment system marks a transaction as failed, but the bank statement shows that the money was transferred. Which record would you rely on, and what additional checks would you perform?",
        "keywords": ["bank statement", "source of truth", "cleared", "timeout", "network", "bank portal", "reverse inquiry", "confirmation"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "supplierProposal",
        "question": "The supplier confirms receiving the additional payment but requests that the amount be adjusted against a future invoice instead of refunded. How would you handle this?",
        "keywords": ["refund", "netting", "policy", "sop", "credit note", "working capital", "cash flow", "agreement"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "internalControls",
        "question": "What controls would you introduce to prevent duplicate payments when payment systems experience timeouts or processing failures?",
        "keywords": ["controls", "timeout", "reverse query", "idempotency", "dual sign-off", "bank portal", "reconciliation", "api"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "disputeEvidence",
        "question": "If the supplier disputes your findings, what evidence would you present to support your investigation?",
        "keywords": ["evidence", "utr", "bank statement", "transaction reference", "invoice", "audit trail", "demand letter"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
]


def evaluate_duplicate_payment_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    payments = workspace_snapshot.get("payments", [])
    user_payments = {p.get("id"): p for p in payments}

    task_score = 0
    max_task_score = sum(c["points"] for c in PAYMENT_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    for check in PAYMENT_CHECKS:
        user_row = user_payments.get(check["id"], {})
        user_decision = user_row.get("auditDecision", "")
        is_correct = user_decision in check["acceptable_decisions"]

        points_awarded = check["points"] if is_correct else 0
        task_score += points_awarded

        task_evaluations.append({
            "task_id": check["id"],
            "title": f"{check['payment_no']} ({check['invoice_ref']})",
            "status": "PASS" if is_correct else "FAIL",
            "points_earned": points_awarded,
            "max_points": check["points"],
            "feedback": (
                f"Correctly evaluated: {check['explanation']}"
                if is_correct
                else f"Discrepancy: Expected '{check['expected_decision']}', but got '{user_decision}'. {check['explanation']}"
            ),
        })

    # Recovery method bonus
    recovery = workspace_snapshot.get("recoveryRecommendation", "Refund")
    recovery_points = 10 if recovery in ["Refund", "Netting"] else 5
    task_score += recovery_points
    max_task_score += 10

    # Rubric qualitative evaluation
    question_evaluations, question_score, max_question_score, any_ai = evaluate_rubric_questions(
        RUBRIC_QUESTIONS, answers, evaluator=None, context="Nova Retail Solutions: Duplicate Supplier Payment Investigation"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))

    passed = normalized_score >= 70

    feedback_summary = (
        f"Reconciliation completed with score {normalized_score}%. "
        f"Disbursement task score: {task_score}/{max_task_score}. "
        f"Qualitative analysis score: {question_score}/{max_question_score}. "
        + ("Duplicate disbursement correctly isolated and recovery plan structured." if passed else "Review reconciliation between ERP batch status and bank debits.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "deterministic_calibrated",
        "score_breakdown": {
            "disbursement_reconciliation": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "qualitative_analysis": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }


async def evaluate_duplicate_payment_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    payments = workspace_snapshot.get("payments", [])
    user_payments = {p.get("id"): p for p in payments}

    task_score = 0
    max_task_score = sum(c["points"] for c in PAYMENT_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    for check in PAYMENT_CHECKS:
        user_row = user_payments.get(check["id"], {})
        user_decision = user_row.get("auditDecision", "")
        is_correct = user_decision in check["acceptable_decisions"]

        points_awarded = check["points"] if is_correct else 0
        task_score += points_awarded

        task_evaluations.append({
            "task_id": check["id"],
            "title": f"{check['payment_no']} ({check['invoice_ref']})",
            "status": "PASS" if is_correct else "FAIL",
            "points_earned": points_awarded,
            "max_points": check["points"],
            "feedback": (
                f"Correctly evaluated: {check['explanation']}"
                if is_correct
                else f"Discrepancy: Expected '{check['expected_decision']}', but got '{user_decision}'. {check['explanation']}"
            ),
        })

    recovery = workspace_snapshot.get("recoveryRecommendation", "Refund")
    recovery_points = 10 if recovery in ["Refund", "Netting"] else 5
    task_score += recovery_points
    max_task_score += 10

    question_evaluations, question_score, max_question_score, any_ai = await evaluate_rubric_questions_async(
        RUBRIC_QUESTIONS, answers, evaluator=ai_evaluator, context="Nova Retail Solutions: Duplicate Supplier Payment Investigation"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))

    passed = normalized_score >= 70

    feedback_summary = (
        f"Reconciliation completed with score {normalized_score}%. "
        f"Disbursement task score: {task_score}/{max_task_score}. "
        f"Qualitative analysis score: {question_score}/{max_question_score}. "
        + ("Duplicate disbursement correctly isolated and recovery plan structured." if passed else "Review reconciliation between ERP batch status and bank debits.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "ai_calibrated" if ai_evaluator else "deterministic_calibrated",
        "score_breakdown": {
            "disbursement_reconciliation": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "qualitative_analysis": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }
