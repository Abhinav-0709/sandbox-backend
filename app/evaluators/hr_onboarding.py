"""
Evaluator for Scenario 2: HR — Managing Employee Onboarding
Organization: Nova Technologies
Role: HR Operations Associate
Subject: Ananya Sharma (Marketing Executive, Joining 23 Nov)
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


ONBOARDING_TASK_CHECKS = [
    {
        "id": "task-laptop-resolution",
        "title": "IT Equipment & Laptop Allocation Resolution",
        "expected_decision": "Reallocate Unused Postponed Laptop",
        "acceptable_decisions": ["Reallocate Unused Postponed Laptop", "Reassign Postponed Asset", "Temporary Loaner Laptop"],
        "points": 15,
        "explanation": "IT currently holds one unutilized laptop reserved for a postponed joiner; update IT allocation records and reassign to Ananya to ensure Day 1 readiness.",
    },
    {
        "id": "task-crm-access-policy",
        "title": "System Access Level & RBAC Policy Adherence",
        "expected_decision": "Reject Admin Access / Grant Standard User Role",
        "acceptable_decisions": ["Reject Admin Access / Grant Standard User Role", "Standard Marketing Role", "Role-Based Access (Reject Admin)"],
        "points": 20,
        "explanation": "Company access policy enforces Principle of Least Privilege and Role-Based Access Control (RBAC). Admin access is disproportionate for a Marketing Executive and presents severe data security risks.",
    },
    {
        "id": "task-first-day-schedule",
        "title": "Day 1 Schedule Conflict Resolution",
        "expected_decision": "Reschedule Client Meeting to Afternoon",
        "acceptable_decisions": ["Reschedule Client Meeting to Afternoon", "Prioritize HR Orientation 9:30-11:30", "Split Orientation & Afternoon Client Briefing"],
        "points": 15,
        "explanation": "HR Orientation (9:30-11:30 AM) covers mandatory compliance, safety, and identity verification. The reporting manager's client meeting (10:00-12:00) must be rescheduled to the afternoon post-onboarding.",
    },
    {
        "id": "task-id-verification-risk",
        "title": "Unverified Identity Safeguards",
        "expected_decision": "Restrict Customer & Production Data Access",
        "acceptable_decisions": ["Restrict Customer & Production Data Access", "Provisional Access Only", "Suspend System Access Until Verified"],
        "points": 15,
        "explanation": "Without completed identity verification, employee must be restricted to internal general training and shadow sessions; live CRM access and client interaction must be barred.",
    },
    {
        "id": "task-pre-joining-readiness",
        "title": "Pre-Joining vs Post-Joining Activity Triage",
        "expected_decision": "ID Verification & IT Assets Must Precede Day 1",
        "acceptable_decisions": ["ID Verification & IT Assets Must Precede Day 1", "Triage Completed"],
        "points": 15,
        "explanation": "Accurately separated non-negotiable pre-joining dependencies (ID, laptop setup, credentials) from post-joining tasks (bank submission, deep tool setup).",
    },
]

ONBOARDING_QUESTION_RUBRICS = [
    {
        "id": "q1",
        "field": "q1PreVsPostJoining",
        "question": "Q1: Which activities must be completed before Ananya's joining date, and which can safely be completed afterward?",
        "keywords": ["identity", "verification", "laptop", "email", "credentials", "bank", "orientation", "pre-joining", "post-joining", "screening"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "q2LaptopAllocationResolution",
        "question": "Q2: How would you handle the laptop allocation issue without creating an unnecessary delay or violating internal allocation procedures?",
        "keywords": ["it", "coordinator", "reassign", "postpone", "asset", "tracking", "ticket", "reallocation", "audit", "laptop", "image"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "q3AdminAccessGovernance",
        "question": "Q3: The manager insists that administrator access is necessary. Would you approve the request? Explain what you would do.",
        "keywords": ["rbac", "privilege", "role", "security", "reject", "standard", "policy", "least", "admin", "deny"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "q4UnverifiedIdentityRestrictions",
        "question": "Q4: Ananya joins without completing identity verification. What activities should be restricted until verification is complete?",
        "keywords": ["restrict", "crm", "customer", "data", "compliance", "provisional", "temporary", "pii", "database", "access"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "q5ScheduleConflictResolution",
        "question": "Q5: How would you resolve the conflict between the orientation programme and the client meeting?",
        "keywords": ["reschedule", "orientation", "afternoon", "alignment", "client", "meeting", "conflict", "morning", "shadow"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q6",
        "field": "q6AlternativeHardwareContingency",
        "question": "Q6: If IT confirms that no suitable laptop is available, what alternative arrangement would you recommend?",
        "keywords": ["loaner", "rental", "temporary", "desktop", "byod", "procurement", "shadowing", "contingency", "vdi", "mdm", "pool"],
        "required_keywords": 3,
        "min_word_count": 30,
        "max_score": 10,
    },
    {
        "id": "q7",
        "field": "q7RiskEscalationHierarchy",
        "question": "Q7: Which onboarding risks would you escalate to the HR manager immediately, and which would you handle yourself?",
        "keywords": ["escalate", "identity", "admin", "shortage", "resolve", "scheduling", "documentation", "manager", "policy", "breach"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q_memo",
        "field": "onboardingReadinessReportDraft",
        "question": "Onboarding Readiness Report: Executive summary memo for HR Leadership outlining operational readiness, risk mitigations, and day-one schedule.",
        "keywords": ["ananya", "readiness", "asset", "rbac", "schedule", "escalation", "nova", "onboarding", "laptop", "compliance"],
        "required_keywords": 3,
        "min_word_count": 45,
        "max_score": 15,
    },
]


def evaluate_onboarding_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    task_evaluations, total_task_pts, max_task_pts = _evaluate_onboarding_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = evaluate_rubric_questions(
        ONBOARDING_QUESTION_RUBRICS, answers, evaluator=None, context="Nova Technologies: Employee Onboarding Operations & Risk Mitigation"
    )

    return _build_onboarding_result(
        task_evaluations, q_evals, total_task_pts, max_task_pts, total_q, max_q, answers, integrity_flags, "deterministic"
    )


async def evaluate_onboarding_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    task_evaluations, total_task_pts, max_task_pts = _evaluate_onboarding_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = await evaluate_rubric_questions_async(
        ONBOARDING_QUESTION_RUBRICS, answers, evaluator=ai_evaluator, context="Nova Technologies: Employee Onboarding Operations & Risk Mitigation"
    )

    return _build_onboarding_result(
        task_evaluations, q_evals, total_task_pts, max_task_pts, total_q, max_q, answers, integrity_flags, "hybrid_ai" if any_ai else "deterministic"
    )


def _evaluate_onboarding_tasks(workspace_snapshot: Dict[str, Any]) -> tuple[List[Dict[str, Any]], int, int]:
    tracker = workspace_snapshot.get("tracker", workspace_snapshot.get("actions", workspace_snapshot))
    task_evaluations = []
    total_pts = 0
    max_pts = 0

    # 1. Laptop resolution
    max_pts += 15
    laptop_res = str(tracker.get("laptopResolution", "")).strip().lower()
    laptop_ok = any(w in laptop_res for w in ["reassign", "reallocate", "postpone", "unused", "loaner", "available laptop"])
    pts_laptop = 15 if laptop_ok else 5
    total_pts += pts_laptop
    task_evaluations.append({
        "id": "task-laptop-resolution",
        "title": "IT Equipment & Laptop Allocation Resolution",
        "expected_decision": "Reassign Unused Asset from Postponed Joiner",
        "actual_decision": tracker.get("laptopResolution", "Omitted"),
        "is_correct": laptop_ok,
        "points_earned": pts_laptop,
        "max_points": 15,
        "explanation": "Accurately identified and reassigned the unutilized laptop from the postponed joiner with updated asset logging." if laptop_ok else "Missed the available laptop reserved for the postponed joiner.",
    })

    # 2. CRM access
    max_pts += 20
    crm_res = str(tracker.get("crmAccessDecision", "")).strip().lower()
    crm_ok = any(w in crm_res for w in ["reject admin", "standard", "role-based", "rbac", "deny admin", "marketing user"])
    pts_crm = 20 if crm_ok else 0
    total_pts += pts_crm
    task_evaluations.append({
        "id": "task-crm-access-policy",
        "title": "System Access Level & RBAC Governance",
        "expected_decision": "Deny Admin Access / Provision Standard Marketing Role",
        "actual_decision": tracker.get("crmAccessDecision", "Omitted"),
        "is_correct": crm_ok,
        "points_earned": pts_crm,
        "max_points": 20,
        "explanation": "Strict compliance with RBAC: denied unauthorized admin privileges while provisioning required standard marketing permissions." if crm_ok else "Breached security policy: administrator privileges should never be provisioned without executive infosec justification.",
    })

    # 3. Schedule conflict
    max_pts += 15
    sched_res = str(tracker.get("scheduleConflictResolution", "")).strip().lower()
    sched_ok = any(w in sched_res for w in ["afternoon", "reschedule", "orientation first", "move client"])
    pts_sched = 15 if sched_ok else 5
    total_pts += pts_sched
    task_evaluations.append({
        "id": "task-first-day-schedule",
        "title": "Day 1 Schedule Conflict Resolution",
        "expected_decision": "Prioritize Orientation 9:30-11:30; Move Client Meeting to Afternoon",
        "actual_decision": tracker.get("scheduleConflictResolution", "Omitted"),
        "is_correct": sched_ok,
        "points_earned": pts_sched,
        "max_points": 15,
        "explanation": "Protected mandatory HR compliance and first-day orientation by moving the client session to the afternoon." if sched_ok else "Schedule conflict unresolved. Mandatory orientation must precede client engagements.",
    })

    # 4. Identity verification safeguards
    max_pts += 15
    id_res = str(tracker.get("unverifiedIdSafeguards", "")).strip().lower()
    id_ok = any(w in id_res for w in ["restrict", "suspend", "no customer", "no crm", "shadow", "temporary", "provisional"])
    pts_id = 15 if id_ok else 5
    total_pts += pts_id
    task_evaluations.append({
        "id": "task-id-verification-risk",
        "title": "Unverified Identity Data Safeguards",
        "expected_decision": "Restrict Customer Data & Live CRM Access",
        "actual_decision": tracker.get("unverifiedIdSafeguards", "Omitted"),
        "is_correct": id_ok,
        "points_earned": pts_id,
        "max_points": 15,
        "explanation": "Applied proper risk controls: barred live customer data access until legal identity verification is executed." if id_ok else "Data privacy vulnerability: live customer data access must be barred prior to verified identity.",
    })

    # 5. Pre-joining triage
    max_pts += 15
    triage_res = str(tracker.get("preJoiningTriage", "")).strip().lower()
    triage_ok = any(w in triage_res for w in ["id", "laptop", "email", "credentials", "triage", "complete"])
    pts_triage = 15 if triage_ok else 5
    total_pts += pts_triage
    task_evaluations.append({
        "id": "task-pre-joining-readiness",
        "title": "Operational Dependency & Pre-Joining Triage",
        "expected_decision": "Non-Negotiable IT & Compliance Checks Identified",
        "actual_decision": tracker.get("preJoiningTriage", "Completed"),
        "is_correct": triage_ok,
        "points_earned": pts_triage,
        "max_points": 15,
        "explanation": "Successfully sequenced operational dependencies across HR, IT, and Hiring Manager.",
    })

    return task_evaluations, total_pts, max_pts


def _build_onboarding_result(
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
            "operational_execution_score": round((total_task_pts / max_task_pts) * 100) if max_task_pts else 0,
            "hr_governance_score": round((total_q_pts / max_q_pts) * 100) if max_q_pts else 0,
            "total_points": total_pts,
            "max_points": max_pts,
            "ai_assisted": eval_method == "hybrid_ai",
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity_audit,
        "feedback_summary": (
            "Exemplary onboarding coordination: resolved departmental bottlenecks, enforced infosec RBAC controls, and structured a smooth Day 1 experience."
            if passed
            else "Onboarding plan had critical governance or dependency gaps. Review RBAC policy and first-day scheduling."
        ),
    }


__all__ = [
    "evaluate_onboarding_submission",
    "evaluate_onboarding_submission_async",
    "ONBOARDING_TASK_CHECKS",
    "ONBOARDING_QUESTION_RUBRICS",
]
