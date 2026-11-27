"""
Evaluator for Scenario 1.2: Finance — Reconciling Supplier Statements
Organization: Nova Retail Solutions
Role: Accounts Payable Specialist
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


RECON_CHECKS = [
    {
        "id": "chk-pit",
        "key": "paymentInTransit",
        "title": "Payment in Transit Audit (CMS-HDFC-8821 - ₹50,000)",
        "points": 15,
        "explanation": "Identified ₹50,000 payment executed on May 12 (UTR: HDFCN26132049182) that cleared Nova bank account but post-dated Apex statement cut-off.",
    },
    {
        "id": "chk-missing-inv",
        "key": "missingInvoiceInv2080",
        "title": "Unrecorded Invoice Verification (INV-2080 - ₹60,000)",
        "points": 15,
        "explanation": "Verified physical receipt of 60 cartons of thermal rolls under GRN-5510 and posted missing ₹60,000 invoice to company AP ledger.",
    },
    {
        "id": "chk-credit-note",
        "key": "unappliedCreditNoteCn104",
        "title": "Unapplied Credit Note Processing (CN-104 - ₹10,000)",
        "points": 15,
        "explanation": "Applied valid supplier credit note CN-104 of ₹10,000 for water-damaged copier paper reams to reduce AP liability.",
    },
    {
        "id": "chk-transposition",
        "key": "transpositionInv2072",
        "title": "Ledger Transposition Error Correction (INV-2072 - ₹10,000)",
        "points": 15,
        "explanation": "Detected that INV-2072 (billed at ₹70,000) was mistakenly entered into Nova AP ledger as ₹80,000 and posted ₹10,000 adjusting reduction.",
    },
]

RUBRIC_QUESTIONS = [
    {
        "id": "q1",
        "field": "timingVsPermanentDifferences",
        "question": "Why might a supplier statement show a different outstanding balance from the company's accounts payable ledger?",
        "keywords": ["timing", "permanent", "transit", "cut-off", "transposition", "error", "credit note", "lag"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 5,
    },
    {
        "id": "q2",
        "field": "unrecordedCreditNoteEffect",
        "question": "If a credit note has been received but not recorded, how does it affect the company's outstanding payable balance?",
        "keywords": ["overstate", "payable", "liability", "working capital", "overpayment", "cash outflow", "distort"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 5,
    },
    {
        "id": "q3",
        "field": "paymentInTransitVerification",
        "question": "A payment appears in the company's bank records but not in the supplier statement. What would you verify before treating the difference as resolved?",
        "keywords": ["utr", "bank", "debit", "cleared", "beneficiary", "cut-off", "statement", "timestamp"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 5,
    },
    {
        "id": "q4",
        "field": "unsupportedInvoiceHandling",
        "question": "If an invoice appears on the supplier statement but there is no corresponding goods receipt, how would you handle it?",
        "keywords": ["3-way match", "hold", "grn", "receiving", "delivery", "procurement", "investigate", "dock"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 5,
    },
    {
        "id": "q5",
        "field": "reconciliationDocumentation",
        "question": "Why should unresolved reconciliation differences be documented rather than simply adjusted to make both balances match?",
        "keywords": ["audit trail", "internal control", "fraud", "integrity", "documentation", "compliance", "governance"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 5,
    },
]


def evaluate_statement_reconciliation_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    recon = workspace_snapshot.get("reconciliationSchedule", {})
    adjustments = workspace_snapshot.get("adjustmentsIdentified", {})
    email_draft = workspace_snapshot.get("supplierEmailDraft", {})

    task_score = 0
    max_task_score = sum(c["points"] for c in RECON_CHECKS) + 15  # 60 + 15 = 75
    task_evaluations: List[Dict[str, Any]] = []

    # 1. Evaluate specific adjustment identifications (60 pts)
    for check in RECON_CHECKS:
        key = check["key"]
        is_identified = bool(adjustments.get(key, False))
        
        # Also check amounts in recon schedule as fallback
        if not is_identified:
            if key == "paymentInTransit" and recon.get("paymentInTransitAmount") == 50000:
                is_identified = True
            elif key == "missingInvoiceInv2080" and recon.get("missingInvoiceAmount") == 60000:
                is_identified = True
            elif key == "unappliedCreditNoteCn104" and recon.get("unappliedCreditNoteAmount") == 10000:
                is_identified = True
            elif key == "transpositionInv2072" and recon.get("transpositionErrorCorrection") == 10000:
                is_identified = True

        points_awarded = check["points"] if is_identified else 0
        task_score += points_awarded

        task_evaluations.append({
            "task_id": check["id"],
            "title": check["title"],
            "status": "PASS" if is_identified else "FAIL",
            "points_earned": points_awarded,
            "max_points": check["points"],
            "feedback": (
                f"Accurately resolved: {check['explanation']}"
                if is_identified
                else f"Missed item: Did not identify {check['title']}."
            ),
        })

    # 2. Evaluate Final Reconciled Position (15 pts)
    adj_stmt = recon.get("adjustedSupplierBalance", 0)
    adj_ledger = recon.get("adjustedCompanyBalance", 0)
    
    # Check if both sides match ₹3,35,000
    is_balanced = (adj_stmt == 335000 and adj_ledger == 335000) or (
        adj_stmt > 0 and adj_stmt == adj_ledger and bool(recon.get("varianceResolved", False))
    )
    balance_points = 15 if is_balanced else 0
    task_score += balance_points

    task_evaluations.append({
        "task_id": "chk-balanced-position",
        "title": "Two-Way Reconciled Position (₹3,35,000)",
        "status": "PASS" if is_balanced else "FAIL",
        "points_earned": balance_points,
        "max_points": 15,
        "feedback": (
            f"Perfect reconciliation: Supplier statement and Nova AP ledger balanced at ₹3,35,000."
            if is_balanced
            else f"Variance unresolved: Stated balance ₹{adj_stmt} != Ledger balance ₹{adj_ledger}. Target: ₹3,35,000."
        ),
    })

    # 3. Rubric evaluation (25 pts)
    question_evaluations, question_score, max_question_score, any_ai = evaluate_rubric_questions(
        RUBRIC_QUESTIONS, answers, evaluator=None, context="Nova Retail Solutions: Supplier Statement Reconciliation"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Reconciliation completed with score {normalized_score}%. "
        f"Adjustment & schedule score: {task_score}/{max_task_score}. "
        f"Accounting rubric score: {question_score}/{max_question_score}. "
        + ("Supplier statement successfully reconciled and ready for credit release." if passed else "Review reconciliation discrepancies and credit note adjustments.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "deterministic_calibrated",
        "score_breakdown": {
            "reconciliation_accuracy": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "accounting_principles": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }


async def evaluate_statement_reconciliation_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    recon = workspace_snapshot.get("reconciliationSchedule", {})
    adjustments = workspace_snapshot.get("adjustmentsIdentified", {})

    task_score = 0
    max_task_score = sum(c["points"] for c in RECON_CHECKS) + 15
    task_evaluations: List[Dict[str, Any]] = []

    for check in RECON_CHECKS:
        key = check["key"]
        is_identified = bool(adjustments.get(key, False))
        if not is_identified:
            if key == "paymentInTransit" and recon.get("paymentInTransitAmount") == 50000:
                is_identified = True
            elif key == "missingInvoiceInv2080" and recon.get("missingInvoiceAmount") == 60000:
                is_identified = True
            elif key == "unappliedCreditNoteCn104" and recon.get("unappliedCreditNoteAmount") == 10000:
                is_identified = True
            elif key == "transpositionInv2072" and recon.get("transpositionErrorCorrection") == 10000:
                is_identified = True

        points_awarded = check["points"] if is_identified else 0
        task_score += points_awarded

        task_evaluations.append({
            "task_id": check["id"],
            "title": check["title"],
            "status": "PASS" if is_identified else "FAIL",
            "points_earned": points_awarded,
            "max_points": check["points"],
            "feedback": (
                f"Accurately resolved: {check['explanation']}"
                if is_identified
                else f"Missed item: Did not identify {check['title']}."
            ),
        })

    adj_stmt = recon.get("adjustedSupplierBalance", 0)
    adj_ledger = recon.get("adjustedCompanyBalance", 0)
    is_balanced = (adj_stmt == 335000 and adj_ledger == 335000) or (
        adj_stmt > 0 and adj_stmt == adj_ledger and bool(recon.get("varianceResolved", False))
    )
    balance_points = 15 if is_balanced else 0
    task_score += balance_points

    task_evaluations.append({
        "task_id": "chk-balanced-position",
        "title": "Two-Way Reconciled Position (₹3,35,000)",
        "status": "PASS" if is_balanced else "FAIL",
        "points_earned": balance_points,
        "max_points": 15,
        "feedback": (
            f"Perfect reconciliation: Supplier statement and Nova AP ledger balanced at ₹3,35,000."
            if is_balanced
            else f"Variance unresolved: Stated balance ₹{adj_stmt} != Ledger balance ₹{adj_ledger}. Target: ₹3,35,000."
        ),
    })

    question_evaluations, question_score, max_question_score, any_ai = await evaluate_rubric_questions_async(
        RUBRIC_QUESTIONS, answers, evaluator=ai_evaluator, context="Nova Retail Solutions: Supplier Statement Reconciliation"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Reconciliation completed with score {normalized_score}%. "
        f"Adjustment & schedule score: {task_score}/{max_task_score}. "
        f"Accounting rubric score: {question_score}/{max_question_score}. "
        + ("Supplier statement successfully reconciled and ready for credit release." if passed else "Review reconciliation discrepancies and credit note adjustments.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "ai_assisted" if any_ai else "deterministic_calibrated",
        "score_breakdown": {
            "reconciliation_accuracy": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "accounting_principles": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }
