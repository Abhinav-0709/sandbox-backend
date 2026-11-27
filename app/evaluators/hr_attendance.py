"""
Evaluator for Scenario 2.2: HR — Resolving Attendance and Leave Discrepancies Before Payroll
Organization: Vertex Digital Solutions
Role: HR Operations Associate
Batch: 12 Employees (November Payroll Close)
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


ATTENDANCE_CHECKS = [
    {
        "id": "chk-att-aarav-remote",
        "title": "Remote Work Regularization (Aarav Sharma)",
        "points": 15,
        "explanation": "Regularized biometric absence on 15-Nov to approved remote working day based on manager-endorsed timesheet (22 payable days).",
    },
    {
        "id": "chk-att-meera-sick-leave",
        "title": "Manager-Approved Leave Sync (Meera Kapoor)",
        "points": 15,
        "explanation": "Synced 2 days manager-approved medical leave to HRIS (21 payable days), holding 1 unapproved day for employee clarification.",
    },
    {
        "id": "chk-att-rohan-shift-waive",
        "title": "Overnight Release Shift Concession (Rohan Verma)",
        "points": 15,
        "explanation": "Waived late arrival biometric deductions based on manager timesheet confirming authorized late starts after 3:30 AM client releases (22 payable days).",
    },
    {
        "id": "chk-att-ananya-lop",
        "title": "Unapproved Leave Loss of Pay (Ananya Singh)",
        "points": 15,
        "explanation": "Corrected HRIS record: Allocated 2 days as approved paid leave and categorized rejected 3rd day as Loss of Pay (LOP / 20 payable days).",
    },
    {
        "id": "chk-att-karan-offsite-od",
        "title": "Off-Site Client Duty Regularization (Karan Mehta)",
        "points": 15,
        "explanation": "Regularized missing biometric punch on 17-Nov as On-Duty (OD) supported by signed client summit attendance certificate (22 payable days).",
    },
]

RUBRIC_QUESTIONS = [
    {
        "id": "q1",
        "field": "biometricAbsentEvidence",
        "question": "An employee claims that they were present, but the attendance system shows an absence. What evidence would you review before correcting the record?",
        "keywords": ["timesheet", "approval", "vpn", "timestamp", "login", "meeting", "manager", "evidence"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q2",
        "field": "verbalLeaveApprovalAction",
        "question": "A manager confirms an employee's leave verbally, but there is no recorded approval. Should you update the leave record? Explain.",
        "keywords": ["verbal", "written", "portal", "policy", "audit", "sign-off", "compliance", "reject"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q3",
        "field": "leaveBalanceDiscrepancyInvestigation",
        "question": "If an employee's leave balance differs between the HRIS and the spreadsheet tracker, how would you investigate the discrepancy?",
        "keywords": ["audit", "formula", "tracker", "hris", "ledger", "accrual", "carry-forward", "debit"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q4",
        "field": "unresolvedAttendancePayrollDeadline",
        "question": "The payroll deadline is approaching, and one employee's attendance issue remains unresolved. Would you delay the entire payroll submission or report the exception separately?",
        "keywords": ["exception register", "delay", "continuity", "sla", "payroll", "unresolved", "deadline"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q5",
        "field": "approvedVsPendingLeaveDistinction",
        "question": "Why is it important to distinguish approved leave from pending leave when preparing payroll data?",
        "keywords": ["approved", "pending", "lop", "loss of pay", "entitlement", "overpayment", "wage"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q6",
        "field": "recurringDiscrepanciesProcessImprovement",
        "question": "If the same attendance discrepancies occur every month, what process improvements would you recommend?",
        "keywords": ["api", "integration", "automated", "reminder", "self-service", "workflow", "elimination"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
]


def evaluate_attendance_payroll_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    register = {r.get("id"): r for r in workspace_snapshot.get("attendanceRegister", [])}

    task_score = 0
    max_task_score = sum(c["points"] for c in ATTENDANCE_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    # 1. Aarav Sharma (Remote Work)
    aarav = register.get("att-1", {})
    aarav_action = str(aarav.get("action", "")).lower()
    aarav_correct = (aarav.get("payableDays") == 22 or any(w in aarav_action for w in ["remote", "wfh", "regulariz"]))
    aarav_pts = 15 if aarav_correct else 0
    task_score += aarav_pts
    task_evaluations.append({
        "task_id": "chk-att-aarav-remote",
        "title": "Remote Work Regularization (Aarav Sharma)",
        "status": "PASS" if aarav_correct else "FAIL",
        "points_earned": aarav_pts,
        "max_points": 15,
        "feedback": (
            "Regularized: Corrected biometric absent mark to remote working day (22 payable days)."
            if aarav_correct
            else "Unresolved: Approved remote day on 15-Nov not regularized."
        ),
    })

    # 2. Meera Kapoor (Approved Sick Leave)
    meera = register.get("att-2", {})
    meera_action = str(meera.get("action", "")).lower()
    meera_correct = (meera.get("payableDays") == 21 or any(w in meera_action for w in ["medical", "sick", "sync", "approved"]))
    meera_pts = 15 if meera_correct else 0
    task_score += meera_pts
    task_evaluations.append({
        "task_id": "chk-att-meera-sick-leave",
        "title": "Manager-Approved Leave Sync (Meera Kapoor)",
        "status": "PASS" if meera_correct else "FAIL",
        "points_earned": meera_pts,
        "max_points": 15,
        "feedback": (
            "Synced: Credited 2 days manager-approved medical leave."
            if meera_correct
            else "Leave unsynced: Manager-approved sick leave not credited in HRIS."
        ),
    })

    # 3. Rohan Verma (Late Arrival Concession)
    rohan = register.get("att-3", {})
    rohan_action = str(rohan.get("action", "")).lower()
    rohan_correct = (rohan.get("payableDays") == 22 or any(w in rohan_action for w in ["waive", "night", "shift", "adjust"]))
    rohan_pts = 15 if rohan_correct else 0
    task_score += rohan_pts
    task_evaluations.append({
        "task_id": "chk-att-rohan-shift-waive",
        "title": "Overnight Release Shift Concession (Rohan Verma)",
        "status": "PASS" if rohan_correct else "FAIL",
        "points_earned": rohan_pts,
        "max_points": 15,
        "feedback": (
            "Waived: Late arrivals recognized as authorized night shift compensatory adjustments."
            if rohan_correct
            else "Improper deduction: Biometric late arrival penalties applied despite manager authorization."
        ),
    })

    # 4. Ananya Singh (LOP Unapproved Leave)
    ananya = register.get("att-4", {})
    ananya_action = str(ananya.get("action", "")).lower()
    ananya_correct = (ananya.get("payableDays") == 20 or any(w in ananya_action for w in ["lop", "loss of pay", "unapproved"]) or "exception" in str(ananya.get("payrollStatus", "")).lower())
    ananya_pts = 15 if ananya_correct else 0
    task_score += ananya_pts
    task_evaluations.append({
        "task_id": "chk-att-ananya-lop",
        "title": "Unapproved Leave Loss of Pay (Ananya Singh)",
        "status": "PASS" if ananya_correct else "FAIL",
        "points_earned": ananya_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Categorized unapproved 3rd leave day as Loss of Pay (LOP)."
            if ananya_correct
            else "Payroll risk: Unapproved leave day paid without manager authorization."
        ),
    })

    # 5. Karan Mehta (On-Duty Summit)
    karan = register.get("att-5", {})
    karan_action = str(karan.get("action", "")).lower()
    karan_correct = (karan.get("payableDays") == 22 or any(w in karan_action for w in ["on-duty", "od", "client", "summit", "offsite"]))
    karan_pts = 15 if karan_correct else 0
    task_score += karan_pts
    task_evaluations.append({
        "task_id": "chk-att-karan-offsite-od",
        "title": "Off-Site Client Duty Regularization (Karan Mehta)",
        "status": "PASS" if karan_correct else "FAIL",
        "points_earned": karan_pts,
        "max_points": 15,
        "feedback": (
            "Regularized: Applied On-Duty (OD) for client summit attendance."
            if karan_correct
            else "Absence error: Off-site client attendance treated as unexcused absence."
        ),
    })

    # Rubric evaluation
    question_evaluations, question_score, max_question_score, any_ai = evaluate_rubric_questions(
        RUBRIC_QUESTIONS, answers, evaluator=None, context="Vertex Digital Solutions: Attendance and Leave Discrepancies"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Attendance reconciliation completed with score {normalized_score}%. "
        f"Attendance regularization score: {task_score}/{max_task_score}. "
        f"Payroll principles score: {question_score}/{max_question_score}. "
        + ("Attendance records reconciled accurately and formatted for payroll submission." if passed else "Review attendance policies and leave approval workflows.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "deterministic_calibrated",
        "score_breakdown": {
            "attendance_reconciliation": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "payroll_governance": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }


async def evaluate_attendance_payroll_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    register = {r.get("id"): r for r in workspace_snapshot.get("attendanceRegister", [])}

    task_score = 0
    max_task_score = sum(c["points"] for c in ATTENDANCE_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    aarav = register.get("att-1", {})
    aarav_action = str(aarav.get("action", "")).lower()
    aarav_correct = (aarav.get("payableDays") == 22 or any(w in aarav_action for w in ["remote", "wfh", "regulariz"]))
    aarav_pts = 15 if aarav_correct else 0
    task_score += aarav_pts
    task_evaluations.append({
        "task_id": "chk-att-aarav-remote",
        "title": "Remote Work Regularization (Aarav Sharma)",
        "status": "PASS" if aarav_correct else "FAIL",
        "points_earned": aarav_pts,
        "max_points": 15,
        "feedback": (
            "Regularized: Corrected biometric absent mark to remote working day (22 payable days)."
            if aarav_correct
            else "Unresolved: Approved remote day on 15-Nov not regularized."
        ),
    })

    meera = register.get("att-2", {})
    meera_action = str(meera.get("action", "")).lower()
    meera_correct = (meera.get("payableDays") == 21 or any(w in meera_action for w in ["medical", "sick", "sync", "approved"]))
    meera_pts = 15 if meera_correct else 0
    task_score += meera_pts
    task_evaluations.append({
        "task_id": "chk-att-meera-sick-leave",
        "title": "Manager-Approved Leave Sync (Meera Kapoor)",
        "status": "PASS" if meera_correct else "FAIL",
        "points_earned": meera_pts,
        "max_points": 15,
        "feedback": (
            "Synced: Credited 2 days manager-approved medical leave."
            if meera_correct
            else "Leave unsynced: Manager-approved sick leave not credited in HRIS."
        ),
    })

    rohan = register.get("att-3", {})
    rohan_action = str(rohan.get("action", "")).lower()
    rohan_correct = (rohan.get("payableDays") == 22 or any(w in rohan_action for w in ["waive", "night", "shift", "adjust"]))
    rohan_pts = 15 if rohan_correct else 0
    task_score += rohan_pts
    task_evaluations.append({
        "task_id": "chk-att-rohan-shift-waive",
        "title": "Overnight Release Shift Concession (Rohan Verma)",
        "status": "PASS" if rohan_correct else "FAIL",
        "points_earned": rohan_pts,
        "max_points": 15,
        "feedback": (
            "Waived: Late arrivals recognized as authorized night shift compensatory adjustments."
            if rohan_correct
            else "Improper deduction: Biometric late arrival penalties applied despite manager authorization."
        ),
    })

    ananya = register.get("att-4", {})
    ananya_action = str(ananya.get("action", "")).lower()
    ananya_correct = (ananya.get("payableDays") == 20 or any(w in ananya_action for w in ["lop", "loss of pay", "unapproved"]) or "exception" in str(ananya.get("payrollStatus", "")).lower())
    ananya_pts = 15 if ananya_correct else 0
    task_score += ananya_pts
    task_evaluations.append({
        "task_id": "chk-att-ananya-lop",
        "title": "Unapproved Leave Loss of Pay (Ananya Singh)",
        "status": "PASS" if ananya_correct else "FAIL",
        "points_earned": ananya_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Categorized unapproved 3rd leave day as Loss of Pay (LOP)."
            if ananya_correct
            else "Payroll risk: Unapproved leave day paid without manager authorization."
        ),
    })

    karan = register.get("att-5", {})
    karan_action = str(karan.get("action", "")).lower()
    karan_correct = (karan.get("payableDays") == 22 or any(w in karan_action for w in ["on-duty", "od", "client", "summit", "offsite"]))
    karan_pts = 15 if karan_correct else 0
    task_score += karan_pts
    task_evaluations.append({
        "task_id": "chk-att-karan-offsite-od",
        "title": "Off-Site Client Duty Regularization (Karan Mehta)",
        "status": "PASS" if karan_correct else "FAIL",
        "points_earned": karan_pts,
        "max_points": 15,
        "feedback": (
            "Regularized: Applied On-Duty (OD) for client summit attendance."
            if karan_correct
            else "Absence error: Off-site client attendance treated as unexcused absence."
        ),
    })

    question_evaluations, question_score, max_question_score, any_ai = await evaluate_rubric_questions_async(
        RUBRIC_QUESTIONS, answers, evaluator=ai_evaluator, context="Vertex Digital Solutions: Attendance and Leave Discrepancies"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Attendance reconciliation completed with score {normalized_score}%. "
        f"Attendance regularization score: {task_score}/{max_task_score}. "
        f"Payroll principles score: {question_score}/{max_question_score}. "
        + ("Attendance records reconciled accurately and formatted for payroll submission." if passed else "Review attendance policies and leave approval workflows.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "ai_assisted" if any_ai else "deterministic_calibrated",
        "score_breakdown": {
            "attendance_reconciliation": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "payroll_governance": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }
