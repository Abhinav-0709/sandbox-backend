"""
Evaluator for Scenario 1.2: HR — Managing a Difficult Hiring Requirement
Organization: Vertex Digital Solutions
Role: Talent Acquisition Specialist
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


HIRING_REQ_CHECKS = [
    {
        "id": "chk-req-lead-split",
        "title": "Role Structure Differentiation (2 Team Leads vs 4 ICs)",
        "points": 20,
        "explanation": "Separated the 6 openings into 2 Shift Team Leads (team handling required) and 4 Customer Support ICs, aligning with the workforce blueprint.",
    },
    {
        "id": "chk-req-wave-priority",
        "title": "Phased Delivery Prioritization (Wave 1 by Day 20)",
        "points": 20,
        "explanation": "Identified that 3 positions (1 Team Lead + 2 ICs) must be filled within 20 days for Project Apex kickoff.",
    },
    {
        "id": "chk-req-salary-calib",
        "title": "Market Salary & Experience Calibration",
        "points": 20,
        "explanation": "Calibrated salary tiers: ₹3.5-3.8 LPA (1-2 yrs exp) for ICs, and ₹4.5-5.0 LPA (3-5 yrs exp) for Shift Team Leads.",
    },
    {
        "id": "chk-req-recruiter-alloc",
        "title": "Recruiter Workload & Channel Strategy",
        "points": 15,
        "explanation": "Distributed the 6 openings across the 2 available recruiters (Pooja & Amit) and leveraged employee referral sprints.",
    },
]

RUBRIC_QUESTIONS = [
    {
        "id": "q1",
        "field": "managerDisagreementResolution",
        "question": "The hiring manager insists that all six candidates must have at least three years of experience. The workforce plan suggests otherwise. How would you handle this disagreement?",
        "keywords": ["workforce plan", "data", "tenure", "experience", "retention", "lead", "ic", "disagreement", "evidence"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q2",
        "field": "budgetSalaryRecommendations",
        "question": "If the salary budget is below the market expectation, what changes could you recommend without compromising essential job requirements?",
        "keywords": ["tiered", "allocation", "salary band", "incentive", "bonus", "market", "split", "flexibility", "pool"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q3",
        "field": "essentialVsPreferredSeparation",
        "question": "Why should essential and preferred requirements be separated in a job description?",
        "keywords": ["essential", "preferred", "talent pool", "barrier", "job description", "rubric", "evaluation", "scorecard"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q4",
        "field": "recruiterCapacityPrioritization",
        "question": "You have limited recruiter capacity and six open positions. How would you prioritise the recruitment activities?",
        "keywords": ["capacity", "wave", "priority", "referral", "20 days", "recruiter", "staged", "sprint"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q5",
        "field": "unsubstantiatedRejectionHandling",
        "question": "If the hiring manager rejects a candidate who meets all agreed requirements but provides no specific reason, how would you handle the situation?",
        "keywords": ["rejection", "objective", "rubric", "scorecard", "criteria", "feedback", "governance", "arbitrary"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q6",
        "field": "recruitmentMetricMonitoring",
        "question": "How would you measure whether your recruitment plan is working before the 30-day deadline?",
        "keywords": ["metrics", "conversion", "funnel", "checkpoint", "pipeline", "velocity", "sla", "milestone"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
]


def evaluate_hiring_requirement_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    tracker = workspace_snapshot.get("positionsTracker", [])
    analysis = workspace_snapshot.get("requisitionAnalysis", {})

    task_score = 0
    max_task_score = sum(c["points"] for c in HIRING_REQ_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    # 1. Team Lead vs IC Split
    lead_count = sum(1 for p in tracker if "lead" in str(p.get("tier", "")).lower() or "lead" in str(p.get("title", "")).lower())
    ic_count = sum(1 for p in tracker if "ic" in str(p.get("tier", "")).lower() or "contributor" in str(p.get("tier", "")).lower() or "associate" in str(p.get("title", "")).lower())
    split_correct = (lead_count == 2 and ic_count >= 3) or analysis.get("teamLeadPositions") == 2
    split_pts = 20 if split_correct else 0
    task_score += split_pts
    task_evaluations.append({
        "task_id": "chk-req-lead-split",
        "title": "Role Structure Differentiation (2 Team Leads vs 4 ICs)",
        "status": "PASS" if split_correct else "FAIL",
        "points_earned": split_pts,
        "max_points": 20,
        "feedback": (
            "Accurately structured: Separated 2 Shift Team Leads from 4 Support Associates."
            if split_correct
            else f"Improper structure: Requisition must separate 2 Team Leads from 4 ICs (found {lead_count} leads)."
        ),
    })

    # 2. Wave 1 Priority (Day 20)
    wave1_count = sum(1 for p in tracker if "wave 1" in str(p.get("priority", "")).lower() or "day 20" in str(p.get("priority", "")).lower())
    wave1_correct = wave1_count >= 3
    wave1_pts = 20 if wave1_correct else 0
    task_score += wave1_pts
    task_evaluations.append({
        "task_id": "chk-req-wave-priority",
        "title": "Phased Delivery Prioritization (Wave 1 by Day 20)",
        "status": "PASS" if wave1_correct else "FAIL",
        "points_earned": wave1_pts,
        "max_points": 20,
        "feedback": (
            f"Correct: Prioritised {wave1_count} positions for urgent Wave 1 delivery (Day 20)."
            if wave1_correct
            else f"Delivery risk: At least 3 positions must be tagged for Wave 1 / Day 20 (found {wave1_count})."
        ),
    })

    # 3. Salary & Experience Calibration
    salary_correct = any("4." in str(p.get("salaryBand", "")) or "5." in str(p.get("salaryBand", "")) for p in tracker if "lead" in str(p.get("tier", "")).lower()) or "lead" in str(analysis.get("revisedLeadSalaryBand", "")).lower() or "4,50" in str(analysis.get("revisedLeadSalaryBand", ""))
    salary_pts = 20 if salary_correct else 0
    task_score += salary_pts
    task_evaluations.append({
        "task_id": "chk-req-salary-calib",
        "title": "Market Salary & Experience Calibration",
        "status": "PASS" if salary_correct else "FAIL",
        "points_earned": salary_pts,
        "max_points": 20,
        "feedback": (
            "Calibrated: Team Leads budgeted at competitive rate (₹4.5-5.0L) while ICs set at ₹3.5-3.8L."
            if salary_correct
            else "Compensation risk: Offering flat ₹3.5-4.5L will cause senior lead candidates to drop out."
        ),
    })

    # 4. Recruiter Allocation
    recruiters = set(p.get("assignedRecruiter", "") for p in tracker if p.get("assignedRecruiter"))
    recruiter_correct = len(recruiters) >= 2
    recruiter_pts = 15 if recruiter_correct else 0
    task_score += recruiter_pts
    task_evaluations.append({
        "task_id": "chk-req-recruiter-alloc",
        "title": "Recruiter Workload & Channel Strategy",
        "status": "PASS" if recruiter_correct else "FAIL",
        "points_earned": recruiter_pts,
        "max_points": 15,
        "feedback": (
            "Balanced: Distributed 6 requisitions across both available recruiters (Pooja & Amit)."
            if recruiter_correct
            else "Workload bottleneck: Roles must be divided across both team recruiters."
        ),
    })

    # 5. Rubric evaluation
    question_evaluations, question_score, max_question_score, any_ai = evaluate_rubric_questions(
        RUBRIC_QUESTIONS, answers, evaluator=None, context="Vertex Digital Solutions: Difficult Hiring Requirement"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Talent acquisition plan evaluated with score {normalized_score}%. "
        f"Workforce & tracker score: {task_score}/{max_task_score}. "
        f"Recruitment principles score: {question_score}/{max_question_score}. "
        + ("Strategic hiring plan successfully formulated and aligned with workforce blueprint." if passed else "Review role tier separation and phased delivery milestones.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "deterministic_calibrated",
        "score_breakdown": {
            "recruitment_planning": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "stakeholder_strategy": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }


async def evaluate_hiring_requirement_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    tracker = workspace_snapshot.get("positionsTracker", [])
    analysis = workspace_snapshot.get("requisitionAnalysis", {})

    task_score = 0
    max_task_score = sum(c["points"] for c in HIRING_REQ_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    lead_count = sum(1 for p in tracker if "lead" in str(p.get("tier", "")).lower() or "lead" in str(p.get("title", "")).lower())
    ic_count = sum(1 for p in tracker if "ic" in str(p.get("tier", "")).lower() or "contributor" in str(p.get("tier", "")).lower() or "associate" in str(p.get("title", "")).lower())
    split_correct = (lead_count == 2 and ic_count >= 3) or analysis.get("teamLeadPositions") == 2
    split_pts = 20 if split_correct else 0
    task_score += split_pts
    task_evaluations.append({
        "task_id": "chk-req-lead-split",
        "title": "Role Structure Differentiation (2 Team Leads vs 4 ICs)",
        "status": "PASS" if split_correct else "FAIL",
        "points_earned": split_pts,
        "max_points": 20,
        "feedback": (
            "Accurately structured: Separated 2 Shift Team Leads from 4 Support Associates."
            if split_correct
            else f"Improper structure: Requisition must separate 2 Team Leads from 4 ICs (found {lead_count} leads)."
        ),
    })

    wave1_count = sum(1 for p in tracker if "wave 1" in str(p.get("priority", "")).lower() or "day 20" in str(p.get("priority", "")).lower())
    wave1_correct = wave1_count >= 3
    wave1_pts = 20 if wave1_correct else 0
    task_score += wave1_pts
    task_evaluations.append({
        "task_id": "chk-req-wave-priority",
        "title": "Phased Delivery Prioritization (Wave 1 by Day 20)",
        "status": "PASS" if wave1_correct else "FAIL",
        "points_earned": wave1_pts,
        "max_points": 20,
        "feedback": (
            f"Correct: Prioritised {wave1_count} positions for urgent Wave 1 delivery (Day 20)."
            if wave1_correct
            else f"Delivery risk: At least 3 positions must be tagged for Wave 1 / Day 20 (found {wave1_count})."
        ),
    })

    salary_correct = any("4." in str(p.get("salaryBand", "")) or "5." in str(p.get("salaryBand", "")) for p in tracker if "lead" in str(p.get("tier", "")).lower()) or "lead" in str(analysis.get("revisedLeadSalaryBand", "")).lower() or "4,50" in str(analysis.get("revisedLeadSalaryBand", ""))
    salary_pts = 20 if salary_correct else 0
    task_score += salary_pts
    task_evaluations.append({
        "task_id": "chk-req-salary-calib",
        "title": "Market Salary & Experience Calibration",
        "status": "PASS" if salary_correct else "FAIL",
        "points_earned": salary_pts,
        "max_points": 20,
        "feedback": (
            "Calibrated: Team Leads budgeted at competitive rate (₹4.5-5.0L) while ICs set at ₹3.5-3.8L."
            if salary_correct
            else "Compensation risk: Offering flat ₹3.5-4.5L will cause senior lead candidates to drop out."
        ),
    })

    recruiters = set(p.get("assignedRecruiter", "") for p in tracker if p.get("assignedRecruiter"))
    recruiter_correct = len(recruiters) >= 2
    recruiter_pts = 15 if recruiter_correct else 0
    task_score += recruiter_pts
    task_evaluations.append({
        "task_id": "chk-req-recruiter-alloc",
        "title": "Recruiter Workload & Channel Strategy",
        "status": "PASS" if recruiter_correct else "FAIL",
        "points_earned": recruiter_pts,
        "max_points": 15,
        "feedback": (
            "Balanced: Distributed 6 requisitions across both available recruiters (Pooja & Amit)."
            if recruiter_correct
            else "Workload bottleneck: Roles must be divided across both team recruiters."
        ),
    })

    question_evaluations, question_score, max_question_score, any_ai = await evaluate_rubric_questions_async(
        RUBRIC_QUESTIONS, answers, evaluator=ai_evaluator, context="Vertex Digital Solutions: Difficult Hiring Requirement"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Talent acquisition plan evaluated with score {normalized_score}%. "
        f"Workforce & tracker score: {task_score}/{max_task_score}. "
        f"Recruitment principles score: {question_score}/{max_question_score}. "
        + ("Strategic hiring plan successfully formulated and aligned with workforce blueprint." if passed else "Review role tier separation and phased delivery milestones.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "ai_assisted" if any_ai else "deterministic_calibrated",
        "score_breakdown": {
            "recruitment_planning": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "stakeholder_strategy": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }
