"""
Evaluator for Scenario 1.3: Finance — Managing Invoice Processing and Month-End Cut-Off
Organization: Nova Retail Solutions
Role: Accounts Payable Specialist
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


CUTOFF_CHECKS = [
    {
        "id": "chk-cut-apex-hold",
        "title": "In-Transit Hold: Apex Office Supplies (INV-3101 - ₹48,000)",
        "points": 15,
        "explanation": "Placed INV-3101 on hold due to missing GRN (goods in transit); prevented premature ₹48,000 expense recognition in June.",
    },
    {
        "id": "chk-cut-bright-post",
        "title": "Service Verified: Bright Logistics (INV-3102 - ₹72,000)",
        "points": 10,
        "explanation": "Verified freight service completion report SCR-3301 dated June 22 and approved full ₹72,000 for June posting under Cost Centre 301.",
    },
    {
        "id": "chk-cut-cloudserve-split",
        "title": "Prepayment Split: CloudServe Technologies (INV-3103 - ₹1,20,000)",
        "points": 15,
        "explanation": "Correctly split quarterly SaaS into ₹40,000 June IT Expense (Cost Centre 501) and ₹80,000 Prepaid Asset (Account 1400).",
    },
    {
        "id": "chk-cut-metro-recode",
        "title": "Cost Centre Correction: Metro Utilities (INV-3104 - ₹35,000)",
        "points": 15,
        "explanation": "Corrected cost centre allocation from Marketing 201 to Facilities & Utilities 401 for store gas & water services.",
    },
    {
        "id": "chk-cut-secure-post",
        "title": "Security Guard Deployment: Secure Facility Services (INV-3105 - ₹60,000)",
        "points": 10,
        "explanation": "Verified SCR-3308 for June guard deployment and approved ₹60,000 under Cost Centre 101.",
    },
    {
        "id": "chk-cut-elec-accrual",
        "title": "Unbilled Electricity Accrual (4,200 kWh @ ₹10/kWh = ₹42,000)",
        "points": 10,
        "explanation": "Accurately calculated and booked unbilled June electricity accrual of ₹42,000 (Dr 401-Electricity / Cr 2100-Accrued Liabilities).",
    },
]

RUBRIC_QUESTIONS = [
    {
        "id": "q1",
        "field": "invoiceDateVsCutoff",
        "question": "Why is the invoice date alone not always sufficient to determine the accounting period in which an expense should be recorded?",
        "keywords": ["matching principle", "period", "consumed", "delivered", "timing", "accrual", "lag", "cut-off"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 5,
    },
    {
        "id": "q2",
        "field": "delayedInvoiceAccrualWorkflow",
        "question": "If a service was completed in June but the invoice arrives in July, how should the accounts payable team communicate this to the accounting team?",
        "keywords": ["accrual", "unbilled", "communication", "general ledger", "reverse", "service completion", "matching"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 5,
    },
    {
        "id": "q3",
        "field": "missingGrnAction",
        "question": "What would you do if an invoice has a valid purchase order but no goods receipt record?",
        "keywords": ["hold", "3-way match", "grn", "warehouse", "receiving", "in-transit", "procurement", "payment block"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 5,
    },
    {
        "id": "q4",
        "field": "costCentreImportance",
        "question": "Why is it important to assign the correct cost centre when processing supplier invoices?",
        "keywords": ["cost centre", "departmental", "budget", "variance", "accountability", "p&l", "reporting", "distortion"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 5,
    },
    {
        "id": "q5",
        "field": "multiPeriodPrepaymentAccounting",
        "question": "If an invoice covers June, July, and August, why should the entire amount not automatically be recorded as a June expense?",
        "keywords": ["prepayment", "prepaid asset", "distort", "profitability", "matching principle", "apportion", "subsequent periods"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 5,
    },
    {
        "id": "q6",
        "field": "missingUtilityAccrualEstimation",
        "question": "How would you handle a missing utility invoice during month-end closing without inventing an expense amount?",
        "keywords": ["meter log", "kwh", "tariff", "reading", "objective", "audit trail", "historical", "accrual"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 5,
    },
]


def evaluate_invoice_cutoff_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    invoices = {inv.get("id"): inv for inv in workspace_snapshot.get("invoices", [])}
    accruals = workspace_snapshot.get("unbilledAccruals", [])

    task_score = 0
    max_task_score = sum(c["points"] for c in CUTOFF_CHECKS)  # 75
    task_evaluations: List[Dict[str, Any]] = []

    # 1. Apex INV-3101 (Hold missing GRN)
    apex = invoices.get("inv-3101", {})
    apex_held = (
        apex.get("status") in ["Hold (Missing GRN)", "Hold"] or
        (apex.get("juneExpenseAmount") == 0 and apex.get("amount") == 48000)
    )
    apex_pts = 15 if apex_held else 0
    task_score += apex_pts
    task_evaluations.append({
        "task_id": "chk-cut-apex-hold",
        "title": "In-Transit Hold: Apex Office Supplies (INV-3101 - ₹48,000)",
        "status": "PASS" if apex_held else "FAIL",
        "points_earned": apex_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Placed INV-3101 on hold pending warehouse goods receipt note."
            if apex_held
            else "Improper cut-off: Recognized ₹48,000 for goods still in transit without GRN."
        ),
    })

    # 2. Bright Logistics INV-3102 (Post June expense)
    bright = invoices.get("inv-3102", {})
    bright_posted = (
        bright.get("status") in ["Ready to Post", "Approved"] or
        bright.get("juneExpenseAmount") == 72000
    )
    bright_pts = 10 if bright_posted else 0
    task_score += bright_pts
    task_evaluations.append({
        "task_id": "chk-cut-bright-post",
        "title": "Service Verified: Bright Logistics (INV-3102 - ₹72,000)",
        "status": "PASS" if bright_posted else "FAIL",
        "points_earned": bright_pts,
        "max_points": 10,
        "feedback": (
            "Correct: Approved freight expense supported by SCR-3301 dated June 22."
            if bright_posted
            else "Missed: Bright Logistics freight was completed in June and should be posted."
        ),
    })

    # 3. CloudServe Technologies INV-3103 (Split Prepayment 40k/80k)
    cloud = invoices.get("inv-3103", {})
    cloud_split = (
        cloud.get("status") == "Split Prepayment" or
        (cloud.get("juneExpenseAmount") == 40000 and cloud.get("prepaidAmount") == 80000)
    )
    cloud_pts = 15 if cloud_split else 0
    task_score += cloud_pts
    task_evaluations.append({
        "task_id": "chk-cut-cloudserve-split",
        "title": "Prepayment Split: CloudServe Technologies (INV-3103 - ₹1,20,000)",
        "status": "PASS" if cloud_split else "FAIL",
        "points_earned": cloud_pts,
        "max_points": 15,
        "feedback": (
            "Accurate apportionment: Split into ₹40,000 June IT expense and ₹80,000 Prepaid Asset."
            if cloud_split
            else f"Improper apportionment: Billed ₹1,20,000 was not split into 1/3 current expense and 2/3 prepaid asset."
        ),
    })

    # 4. Metro Utilities INV-3104 (Re-code to Facilities 401)
    metro = invoices.get("inv-3104", {})
    metro_cc = str(metro.get("costCentre", ""))
    metro_recoded = "401" in metro_cc or "Facilities" in metro_cc
    metro_pts = 15 if metro_recoded else 0
    task_score += metro_pts
    task_evaluations.append({
        "task_id": "chk-cut-metro-recode",
        "title": "Cost Centre Correction: Metro Utilities (INV-3104 - ₹35,000)",
        "status": "PASS" if metro_recoded else "FAIL",
        "points_earned": metro_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Re-coded water and gas utility to Cost Centre 401 (Facilities)."
            if metro_recoded
            else f"Misallocated: Remained under wrong Cost Centre '{metro_cc}'. Must be Facilities 401."
        ),
    })

    # 5. Secure Facility Services INV-3105 (Post June expense)
    secure = invoices.get("inv-3105", {})
    secure_posted = (
        secure.get("status") in ["Ready to Post", "Approved"] or
        secure.get("juneExpenseAmount") == 60000
    )
    secure_pts = 10 if secure_posted else 0
    task_score += secure_pts
    task_evaluations.append({
        "task_id": "chk-cut-secure-post",
        "title": "Security Guard Deployment: Secure Facility Services (INV-3105 - ₹60,000)",
        "status": "PASS" if secure_posted else "FAIL",
        "points_earned": secure_pts,
        "max_points": 10,
        "feedback": (
            "Correct: Approved June security services verified by SCR-3308."
            if secure_posted
            else "Missed: Security guard deployment completed in June should be posted."
        ),
    })

    # 6. Unbilled Electricity Accrual (₹42,000)
    elec_accrual = next((a for a in accruals if "elec" in a.get("id", "").lower() or "power" in a.get("expenseType", "").lower() or "elec" in a.get("expenseType", "").lower()), {})
    accrual_amt = elec_accrual.get("estimatedAccrualAmount", 0)
    if accrual_amt == 0 and "meterReadingKwh" in elec_accrual and "tariffRatePerKwh" in elec_accrual:
        accrual_amt = elec_accrual.get("meterReadingKwh", 0) * elec_accrual.get("tariffRatePerKwh", 0)

    accrual_correct = accrual_amt == 42000
    accrual_pts = 10 if accrual_correct else 0
    task_score += accrual_pts
    task_evaluations.append({
        "task_id": "chk-cut-elec-accrual",
        "title": "Unbilled Electricity Accrual (4,200 kWh @ ₹10/kWh = ₹42,000)",
        "status": "PASS" if accrual_correct else "FAIL",
        "points_earned": accrual_pts,
        "max_points": 10,
        "feedback": (
            "Accurate accrual: Booked ₹42,000 for unbilled June power consumption."
            if accrual_correct
            else f"Incorrect accrual amount: ₹{accrual_amt}. Expected 4,200 kWh * ₹10 = ₹42,000."
        ),
    })

    # 7. Rubric evaluation (30 pts)
    question_evaluations, question_score, max_question_score, any_ai = evaluate_rubric_questions(
        RUBRIC_QUESTIONS, answers, evaluator=None, context="Nova Retail Solutions: Month-End Cut-Off & Invoice Processing"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Month-end cut-off audit completed with score {normalized_score}%. "
        f"Invoice processing & accrual score: {task_score}/{max_task_score}. "
        f"Accounting principles rubric score: {question_score}/{max_question_score}. "
        + ("June AP ledger cut-off successfully enforced with compliant accruals." if passed else "Review cut-off rules, multi-period prepayments, and utility accrual methods.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "deterministic_calibrated",
        "score_breakdown": {
            "cutoff_execution": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "accounting_principles": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }


async def evaluate_invoice_cutoff_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    invoices = {inv.get("id"): inv for inv in workspace_snapshot.get("invoices", [])}
    accruals = workspace_snapshot.get("unbilledAccruals", [])

    task_score = 0
    max_task_score = sum(c["points"] for c in CUTOFF_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    # Apex INV-3101
    apex = invoices.get("inv-3101", {})
    apex_held = (
        apex.get("status") in ["Hold (Missing GRN)", "Hold"] or
        (apex.get("juneExpenseAmount") == 0 and apex.get("amount") == 48000)
    )
    apex_pts = 15 if apex_held else 0
    task_score += apex_pts
    task_evaluations.append({
        "task_id": "chk-cut-apex-hold",
        "title": "In-Transit Hold: Apex Office Supplies (INV-3101 - ₹48,000)",
        "status": "PASS" if apex_held else "FAIL",
        "points_earned": apex_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Placed INV-3101 on hold pending warehouse goods receipt note."
            if apex_held
            else "Improper cut-off: Recognized ₹48,000 for goods still in transit without GRN."
        ),
    })

    # Bright Logistics INV-3102
    bright = invoices.get("inv-3102", {})
    bright_posted = (
        bright.get("status") in ["Ready to Post", "Approved"] or
        bright.get("juneExpenseAmount") == 72000
    )
    bright_pts = 10 if bright_posted else 0
    task_score += bright_pts
    task_evaluations.append({
        "task_id": "chk-cut-bright-post",
        "title": "Service Verified: Bright Logistics (INV-3102 - ₹72,000)",
        "status": "PASS" if bright_posted else "FAIL",
        "points_earned": bright_pts,
        "max_points": 10,
        "feedback": (
            "Correct: Approved freight expense supported by SCR-3301 dated June 22."
            if bright_posted
            else "Missed: Bright Logistics freight was completed in June and should be posted."
        ),
    })

    # CloudServe Technologies INV-3103
    cloud = invoices.get("inv-3103", {})
    cloud_split = (
        cloud.get("status") == "Split Prepayment" or
        (cloud.get("juneExpenseAmount") == 40000 and cloud.get("prepaidAmount") == 80000)
    )
    cloud_pts = 15 if cloud_split else 0
    task_score += cloud_pts
    task_evaluations.append({
        "task_id": "chk-cut-cloudserve-split",
        "title": "Prepayment Split: CloudServe Technologies (INV-3103 - ₹1,20,000)",
        "status": "PASS" if cloud_split else "FAIL",
        "points_earned": cloud_pts,
        "max_points": 15,
        "feedback": (
            "Accurate apportionment: Split into ₹40,000 June IT expense and ₹80,000 Prepaid Asset."
            if cloud_split
            else f"Improper apportionment: Billed ₹1,20,000 was not split into 1/3 current expense and 2/3 prepaid asset."
        ),
    })

    # Metro Utilities INV-3104
    metro = invoices.get("inv-3104", {})
    metro_cc = str(metro.get("costCentre", ""))
    metro_recoded = "401" in metro_cc or "Facilities" in metro_cc
    metro_pts = 15 if metro_recoded else 0
    task_score += metro_pts
    task_evaluations.append({
        "task_id": "chk-cut-metro-recode",
        "title": "Cost Centre Correction: Metro Utilities (INV-3104 - ₹35,000)",
        "status": "PASS" if metro_recoded else "FAIL",
        "points_earned": metro_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Re-coded water and gas utility to Cost Centre 401 (Facilities)."
            if metro_recoded
            else f"Misallocated: Remained under wrong Cost Centre '{metro_cc}'. Must be Facilities 401."
        ),
    })

    # Secure Facility Services INV-3105
    secure = invoices.get("inv-3105", {})
    secure_posted = (
        secure.get("status") in ["Ready to Post", "Approved"] or
        secure.get("juneExpenseAmount") == 60000
    )
    secure_pts = 10 if secure_posted else 0
    task_score += secure_pts
    task_evaluations.append({
        "task_id": "chk-cut-secure-post",
        "title": "Security Guard Deployment: Secure Facility Services (INV-3105 - ₹60,000)",
        "status": "PASS" if secure_posted else "FAIL",
        "points_earned": secure_pts,
        "max_points": 10,
        "feedback": (
            "Correct: Approved June security services verified by SCR-3308."
            if secure_posted
            else "Missed: Security guard deployment completed in June should be posted."
        ),
    })

    # Unbilled Electricity Accrual
    elec_accrual = next((a for a in accruals if "elec" in a.get("id", "").lower() or "power" in a.get("expenseType", "").lower() or "elec" in a.get("expenseType", "").lower()), {})
    accrual_amt = elec_accrual.get("estimatedAccrualAmount", 0)
    if accrual_amt == 0 and "meterReadingKwh" in elec_accrual and "tariffRatePerKwh" in elec_accrual:
        accrual_amt = elec_accrual.get("meterReadingKwh", 0) * elec_accrual.get("tariffRatePerKwh", 0)

    accrual_correct = accrual_amt == 42000
    accrual_pts = 10 if accrual_correct else 0
    task_score += accrual_pts
    task_evaluations.append({
        "task_id": "chk-cut-elec-accrual",
        "title": "Unbilled Electricity Accrual (4,200 kWh @ ₹10/kWh = ₹42,000)",
        "status": "PASS" if accrual_correct else "FAIL",
        "points_earned": accrual_pts,
        "max_points": 10,
        "feedback": (
            "Accurate accrual: Booked ₹42,000 for unbilled June power consumption."
            if accrual_correct
            else f"Incorrect accrual amount: ₹{accrual_amt}. Expected 4,200 kWh * ₹10 = ₹42,000."
        ),
    })

    question_evaluations, question_score, max_question_score, any_ai = await evaluate_rubric_questions_async(
        RUBRIC_QUESTIONS, answers, evaluator=ai_evaluator, context="Nova Retail Solutions: Month-End Cut-Off & Invoice Processing"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Month-end cut-off audit completed with score {normalized_score}%. "
        f"Invoice processing & accrual score: {task_score}/{max_task_score}. "
        f"Accounting principles rubric score: {question_score}/{max_question_score}. "
        + ("June AP ledger cut-off successfully enforced with compliant accruals." if passed else "Review cut-off rules, multi-period prepayments, and utility accrual methods.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "ai_assisted" if any_ai else "deterministic_calibrated",
        "score_breakdown": {
            "cutoff_execution": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "accounting_principles": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }
