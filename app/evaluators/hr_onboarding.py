"""
Evaluator for Scenario 2.1: HR — Managing Employee Onboarding and Documentation
Organization: Vertex Digital Solutions
Role: HR Operations Associate
Batch: 12 Joiners (Joining 24 November)
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


ONBOARDING_BATCH_CHECKS = [
    {
        "id": "chk-name-mismatch",
        "title": "Legal Name Standardization (Rohan Verma)",
        "points": 15,
        "explanation": "Standardized HRIS record to official government identity document ('Rohan Verma' per Passport/Aadhaar) over self-reported form variation ('Rohan Varma').",
    },
    {
        "id": "chk-address-discrepancy",
        "title": "Address Proof Audit (Meera Kapoor)",
        "points": 15,
        "explanation": "Flagged discrepancy between Mumbai form declaration and Pune electricity bill, requesting updated proof matching current address.",
    },
    {
        "id": "chk-crm-rbac-access",
        "title": "Access Governance & RBAC (Karan Mehta)",
        "points": 15,
        "explanation": "Denied unauthorized CRM Administrator request pending degree verification; granted Standard User role under Principle of Least Privilege.",
    },
    {
        "id": "chk-bank-incomplete",
        "title": "Statutory Bank Details Verification (Priya Nair)",
        "points": 15,
        "explanation": "Held direct deposit setup pending submission of cancelled cheque or official bank verification stamp.",
    },
    {
        "id": "chk-hardware-triage",
        "title": "IT Hardware Prioritization (10 Laptops / 12 Joiners)",
        "points": 15,
        "explanation": "Prioritised available hardware for critical Engineering (4) and client-facing Sales (3) roles, providing temporary workstations for internal support.",
    },
]

RUBRIC_QUESTIONS = [
    {
        "id": "q1",
        "field": "nameDiscrepancyResolution",
        "question": "If an employee's name differs between their information form and identity document, which record should you rely on, and how would you resolve the discrepancy?",
        "keywords": ["government", "identity", "passport", "aadhaar", "standardize", "legal", "confirmation", "discrepancy", "official"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q2",
        "field": "incompleteDocSystemAccess",
        "question": "A department manager requests system access for an employee whose documentation is incomplete. How would you handle the request?",
        "keywords": ["rbac", "least privilege", "standard", "provisional", "restrict", "admin", "policy", "security", "supervisor"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q3",
        "field": "unverifiedInfoRisk",
        "question": "Why should HR Operations avoid entering unverified employee information simply to complete onboarding before the deadline?",
        "keywords": ["statutory", "audit", "compliance", "pf", "tax", "esi", "liability", "fraud", "integrity", "data"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q4",
        "field": "itEquipmentPrioritization",
        "question": "If IT can prepare equipment for only 10 of the 12 employees, how would you prioritise the available equipment?",
        "keywords": ["prioritise", "criticality", "engineering", "sales", "client", "temporary", "desktop", "loaner", "role"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q5",
        "field": "unapprovedJoiningDateChange",
        "question": "An employee requests a joining-date change directly, but their manager has not approved it. What should you do before updating the HRIS?",
        "keywords": ["approval", "manager", "written", "sign-off", "recruitment", "hold", "staffing", "project", "confirm"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q6",
        "field": "documentPrivacyCompliance",
        "question": "How would you ensure that employee documents and personal information are handled appropriately?",
        "keywords": ["privacy", "encrypted", "pii", "role-based", "confidential", "security", "gdpr", "protection", "access"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
]


def evaluate_onboarding_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    employees = {e.get("id"): e for e in workspace_snapshot.get("employeeRecords", [])}

    task_score = 0
    max_task_score = sum(c["points"] for c in ONBOARDING_BATCH_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    rohan = employees.get("emp-3", {})
    rohan_notes = str(rohan.get("notes", "")).lower()
    rohan_correct = (
        "rohan verma" in rohan_notes or
        "government" in rohan_notes or
        "aadhaar" in rohan_notes or
        "passport" in rohan_notes or
        rohan.get("hrisStatus") in ["Verified", "Action Required"]
    )
    rohan_pts = 15 if rohan_correct else 0
    task_score += rohan_pts
    task_evaluations.append({
        "task_id": "chk-name-mismatch",
        "title": "Legal Name Standardization (Rohan Verma)",
        "status": "PASS" if rohan_correct else "FAIL",
        "points_earned": rohan_pts,
        "max_points": 15,
        "feedback": (
            "Standardized: Governed name to official government identity document 'Rohan Verma'."
            if rohan_correct
            else "Mismatch unresolved: Name must match official government ID."
        ),
    })

    meera = employees.get("emp-2", {})
    meera_notes = str(meera.get("notes", "")).lower()
    meera_correct = (
        "address" in meera_notes or
        "pune" in meera_notes or
        "proof" in meera_notes or
        "bill" in meera_notes or
        meera.get("hrisStatus") == "Action Required"
    )
    meera_pts = 15 if meera_correct else 0
    task_score += meera_pts
    task_evaluations.append({
        "task_id": "chk-address-discrepancy",
        "title": "Address Proof Audit (Meera Kapoor)",
        "status": "PASS" if meera_correct else "FAIL",
        "points_earned": meera_pts,
        "max_points": 15,
        "feedback": (
            "Flagged: Address discrepancy between form and electricity bill highlighted for correction."
            if meera_correct
            else "Compliance risk: Address mismatch between form and utility bill overlooked."
        ),
    })

    karan = employees.get("emp-5", {})
    karan_access = str(karan.get("accessStatus", "")).lower()
    karan_correct = "standard" in karan_access or "hold admin" in karan_access or "rbac" in karan_access
    karan_pts = 15 if karan_correct else 0
    task_score += karan_pts
    task_evaluations.append({
        "task_id": "chk-crm-rbac-access",
        "title": "Access Governance & RBAC (Karan Mehta)",
        "status": "PASS" if karan_correct else "FAIL",
        "points_earned": karan_pts,
        "max_points": 15,
        "feedback": (
            "RBAC enforced: Denied administrator privileges; restricted to Standard User role."
            if karan_correct
            else "Security breach: Administrator privileges granted without completed education verification."
        ),
    })

    priya = employees.get("emp-6", {})
    priya_notes = str(priya.get("notes", "")).lower()
    priya_correct = "cheque" in priya_notes or "bank" in priya_notes or "hold" in priya_notes or priya.get("hrisStatus") == "Action Required"
    priya_pts = 15 if priya_correct else 0
    task_score += priya_pts
    task_evaluations.append({
        "task_id": "chk-bank-incomplete",
        "title": "Statutory Bank Details Verification (Priya Nair)",
        "status": "PASS" if priya_correct else "FAIL",
        "points_earned": priya_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Held direct deposit setup pending submission of cancelled cheque."
            if priya_correct
            else "Payroll risk: Unverified bank details entered into HRIS without supporting cheque."
        ),
    })

    laptop_allocs = [e for e in employees.values() if "laptop" in str(e.get("itStatus", "")).lower()]
    laptop_correct = len(laptop_allocs) <= 10 and any(e.get("department") == "Engineering" and "laptop" in str(e.get("itStatus", "")).lower() for e in employees.values())
    laptop_pts = 15 if laptop_correct else 0
    task_score += laptop_pts
    task_evaluations.append({
        "task_id": "chk-hardware-triage",
        "title": "IT Hardware Prioritization (10 Laptops / 12 Joiners)",
        "status": "PASS" if laptop_correct else "FAIL",
        "points_earned": laptop_pts,
        "max_points": 15,
        "feedback": (
            "Optimized: Allocated available laptops to critical Engineering and Sales roles."
            if laptop_correct
            else "Hardware over-allocation: More than 10 laptops allocated or priority roles neglected."
        ),
    })

    question_evaluations, question_score, max_question_score, any_ai = evaluate_rubric_questions(
        RUBRIC_QUESTIONS, answers, evaluator=None, context="Vertex Digital Solutions: Employee Onboarding and Documentation"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Onboarding batch evaluation completed with score {normalized_score}%. "
        f"Document verification & triage score: {task_score}/{max_task_score}. "
        f"Operational principles score: {question_score}/{max_question_score}. "
        + ("Batch successfully audited and ready for Day 1 compliance induction." if passed else "Review document discrepancy procedures and access control policies.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "deterministic_calibrated",
        "score_breakdown": {
            "document_verification": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "onboarding_governance": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }


async def evaluate_onboarding_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    employees = {e.get("id"): e for e in workspace_snapshot.get("employeeRecords", [])}

    task_score = 0
    max_task_score = sum(c["points"] for c in ONBOARDING_BATCH_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    rohan = employees.get("emp-3", {})
    rohan_notes = str(rohan.get("notes", "")).lower()
    rohan_correct = (
        "rohan verma" in rohan_notes or
        "government" in rohan_notes or
        "aadhaar" in rohan_notes or
        "passport" in rohan_notes or
        rohan.get("hrisStatus") in ["Verified", "Action Required"]
    )
    rohan_pts = 15 if rohan_correct else 0
    task_score += rohan_pts
    task_evaluations.append({
        "task_id": "chk-name-mismatch",
        "title": "Legal Name Standardization (Rohan Verma)",
        "status": "PASS" if rohan_correct else "FAIL",
        "points_earned": rohan_pts,
        "max_points": 15,
        "feedback": (
            "Standardized: Governed name to official government identity document 'Rohan Verma'."
            if rohan_correct
            else "Mismatch unresolved: Name must match official government ID."
        ),
    })

    meera = employees.get("emp-2", {})
    meera_notes = str(meera.get("notes", "")).lower()
    meera_correct = (
        "address" in meera_notes or
        "pune" in meera_notes or
        "proof" in meera_notes or
        "bill" in meera_notes or
        meera.get("hrisStatus") == "Action Required"
    )
    meera_pts = 15 if meera_correct else 0
    task_score += meera_pts
    task_evaluations.append({
        "task_id": "chk-address-discrepancy",
        "title": "Address Proof Audit (Meera Kapoor)",
        "status": "PASS" if meera_correct else "FAIL",
        "points_earned": meera_pts,
        "max_points": 15,
        "feedback": (
            "Flagged: Address discrepancy between form and electricity bill highlighted for correction."
            if meera_correct
            else "Compliance risk: Address mismatch between form and utility bill overlooked."
        ),
    })

    karan = employees.get("emp-5", {})
    karan_access = str(karan.get("accessStatus", "")).lower()
    karan_correct = "standard" in karan_access or "hold admin" in karan_access or "rbac" in karan_access
    karan_pts = 15 if karan_correct else 0
    task_score += karan_pts
    task_evaluations.append({
        "task_id": "chk-crm-rbac-access",
        "title": "Access Governance & RBAC (Karan Mehta)",
        "status": "PASS" if karan_correct else "FAIL",
        "points_earned": karan_pts,
        "max_points": 15,
        "feedback": (
            "RBAC enforced: Denied administrator privileges; restricted to Standard User role."
            if karan_correct
            else "Security breach: Administrator privileges granted without completed education verification."
        ),
    })

    priya = employees.get("emp-6", {})
    priya_notes = str(priya.get("notes", "")).lower()
    priya_correct = "cheque" in priya_notes or "bank" in priya_notes or "hold" in priya_notes or priya.get("hrisStatus") == "Action Required"
    priya_pts = 15 if priya_correct else 0
    task_score += priya_pts
    task_evaluations.append({
        "task_id": "chk-bank-incomplete",
        "title": "Statutory Bank Details Verification (Priya Nair)",
        "status": "PASS" if priya_correct else "FAIL",
        "points_earned": priya_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Held direct deposit setup pending submission of cancelled cheque."
            if priya_correct
            else "Payroll risk: Unverified bank details entered into HRIS without supporting cheque."
        ),
    })

    laptop_allocs = [e for e in employees.values() if "laptop" in str(e.get("itStatus", "")).lower()]
    laptop_correct = len(laptop_allocs) <= 10 and any(e.get("department") == "Engineering" and "laptop" in str(e.get("itStatus", "")).lower() for e in employees.values())
    laptop_pts = 15 if laptop_correct else 0
    task_score += laptop_pts
    task_evaluations.append({
        "task_id": "chk-hardware-triage",
        "title": "IT Hardware Prioritization (10 Laptops / 12 Joiners)",
        "status": "PASS" if laptop_correct else "FAIL",
        "points_earned": laptop_pts,
        "max_points": 15,
        "feedback": (
            "Optimized: Allocated available laptops to critical Engineering and Sales roles."
            if laptop_correct
            else "Hardware over-allocation: More than 10 laptops allocated or priority roles neglected."
        ),
    })

    question_evaluations, question_score, max_question_score, any_ai = await evaluate_rubric_questions_async(
        RUBRIC_QUESTIONS, answers, evaluator=ai_evaluator, context="Vertex Digital Solutions: Employee Onboarding and Documentation"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Onboarding batch evaluation completed with score {normalized_score}%. "
        f"Document verification & triage score: {task_score}/{max_task_score}. "
        f"Operational principles score: {question_score}/{max_question_score}. "
        + ("Batch successfully audited and ready for Day 1 compliance induction." if passed else "Review document discrepancy procedures and access control policies.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "ai_assisted" if any_ai else "deterministic_calibrated",
        "score_breakdown": {
            "document_verification": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "onboarding_governance": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }
