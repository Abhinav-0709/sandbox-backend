"""
Evaluator for Scenario 1.3: HR — Managing an Interview Pipeline and Hiring Decision
Organization: Vertex Digital Solutions
Role: Talent Acquisition Specialist
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


PIPELINE_CHECKS = [
    {
        "id": "chk-pipe-cand-a",
        "title": "Front-Runner Fast-Track: Candidate A",
        "points": 15,
        "explanation": "Advanced front-runner Candidate A (4.5/5 rating) to final leadership discussion with VP Sales within 24 hours.",
    },
    {
        "id": "chk-pipe-cand-b",
        "title": "Score Discrepancy Calibration: Candidate B",
        "points": 15,
        "explanation": "Addressed conflicting ratings (5/5 Communication vs 2/5 Objection Handling) via structured interviewer calibration or roleplay probe.",
    },
    {
        "id": "chk-pipe-cand-c",
        "title": "Candidate Experience & Reschedule: Candidate C",
        "points": 10,
        "explanation": "Accommodated Candidate C's professional reschedule request to Friday afternoon promptly.",
    },
    {
        "id": "chk-pipe-cand-d",
        "title": "Compensation Structuring: Candidate D",
        "points": 15,
        "explanation": "Proposed hybrid compensation model: Capped base salary at approved ₹5.0 LPA with performance-linked quarterly sales incentives.",
    },
    {
        "id": "chk-pipe-cand-f",
        "title": "Missing Feedback Form SLA Escalation: Candidate F",
        "points": 10,
        "explanation": "Followed up on hiring manager Suresh's 4-day overdue evaluation form via verbal sync to prevent candidate drop-off.",
    },
    {
        "id": "chk-pipe-cand-g",
        "title": "Holistic Evidence Evaluation: Candidate G",
        "points": 10,
        "explanation": "Recognized Candidate G's demonstrated track record (90% renewal rate) despite single-question stumble; retained in backup shortlist.",
    },
]

RUBRIC_QUESTIONS = [
    {
        "id": "q1",
        "field": "conflictingFeedbackHandling",
        "question": "Candidate B received conflicting feedback from two interviewers. Would you immediately reject the candidate, advance them, or request further evaluation? Explain your decision.",
        "keywords": ["calibration", "evidence", "objective", "panel", "probe", "roleplay", "reject", "discrepancy"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q2",
        "field": "overBudgetCandidateManagement",
        "question": "Candidate D performed very well but expects a salary above the approved range. How would you manage the situation?",
        "keywords": ["negotiation", "commission", "bonus", "incentive", "base", "cap", "upside", "structure"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q3",
        "field": "missingFeedbackEscalation",
        "question": "The hiring manager has not submitted feedback for Candidate F. How would you follow up without unnecessarily delaying the recruitment process?",
        "keywords": ["sla", "follow-up", "phone", "template", "drop-off", "verbal", "quick", "turnaround"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q4",
        "field": "holisticVsNumericalScoring",
        "question": "Candidate G has a lower numerical score but strong relevant experience. Why should you review the underlying evidence rather than relying only on the overall score?",
        "keywords": ["holistic", "evidence", "track record", "stress", "anxiety", "revenue", "retention", "renewal", "context"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q5",
        "field": "reducingCandidateDropoff",
        "question": "Two candidates withdrew because of recruitment delays. What changes would you recommend to reduce candidate drop-off?",
        "keywords": ["latency", "sla", "turnaround", "calendar", "communication", "touchpoint", "velocity", "drop-off"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q6",
        "field": "balancingSpeedAndRigor",
        "question": "If the sales department pressures you to select a candidate within three days, how would you balance speed with a fair and consistent evaluation process?",
        "keywords": ["speed", "rigor", "frontrunner", "rubric", "shortlist", "standardized", "vetting", "consistency"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
]


def evaluate_interview_pipeline_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    candidates = {c.get("id"): c for c in workspace_snapshot.get("candidateActions", [])}

    task_score = 0
    max_task_score = sum(c["points"] for c in PIPELINE_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    # 1. Candidate A action
    cand_a = candidates.get("cand-a", {})
    action_a = str(cand_a.get("action", "")).lower()
    a_correct = any(w in action_a for w in ["final", "leadership", "vp", "fast-track", "24h", "advance", "offer"]) or cand_a.get("stage") == "Final Leadership"
    a_pts = 15 if a_correct else 0
    task_score += a_pts
    task_evaluations.append({
        "task_id": "chk-pipe-cand-a",
        "title": "Front-Runner Fast-Track: Candidate A",
        "status": "PASS" if a_correct else "FAIL",
        "points_earned": a_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Fast-tracked Candidate A to final leadership round."
            if a_correct
            else "Pipeline stall: Frontrunner Candidate A must be scheduled for final leadership discussion immediately."
        ),
    })

    # 2. Candidate B action
    cand_b = candidates.get("cand-b", {})
    action_b = str(cand_b.get("action", "")).lower()
    b_correct = any(w in action_b for w in ["calibration", "probe", "sync", "objection", "roleplay", "discrepancy", "re-evaluate"])
    b_pts = 15 if b_correct else 0
    task_score += b_pts
    task_evaluations.append({
        "task_id": "chk-pipe-cand-b",
        "title": "Score Discrepancy Calibration: Candidate B",
        "status": "PASS" if b_correct else "FAIL",
        "points_earned": b_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Addressed divergent interviewer scores via calibration sync."
            if b_correct
            else "Inconsistent evaluation: Conflicting ratings on Candidate B require calibration."
        ),
    })

    # 3. Candidate C action
    cand_c = candidates.get("cand-c", {})
    action_c = str(cand_c.get("action", "")).lower()
    c_correct = any(w in action_c for w in ["reschedule", "friday", "accommodate", "timing"])
    c_pts = 10 if c_correct else 0
    task_score += c_pts
    task_evaluations.append({
        "task_id": "chk-pipe-cand-c",
        "title": "Candidate Experience & Reschedule: Candidate C",
        "status": "PASS" if c_correct else "FAIL",
        "points_earned": c_pts,
        "max_points": 10,
        "feedback": (
            "Correct: Promptly accommodated legitimate reschedule request."
            if c_correct
            else "Candidate experience risk: Must accommodate Candidate C's scheduling conflict."
        ),
    })

    # 4. Candidate D action
    cand_d = candidates.get("cand-d", {})
    action_d = str(cand_d.get("action", "")).lower()
    d_correct = any(w in action_d for w in ["incentive", "negotiat", "commission", "hybrid", "5.0", "cap", "bonus", "bonus"])
    d_pts = 15 if d_correct else 0
    task_score += d_pts
    task_evaluations.append({
        "task_id": "chk-pipe-cand-d",
        "title": "Compensation Structuring: Candidate D",
        "status": "PASS" if d_correct else "FAIL",
        "points_earned": d_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Proposed incentive restructuring to align with approved ₹5.0L budget cap."
            if d_correct
            else "Budget breach: Candidate D requires compensation restructuring with sales commissions."
        ),
    })

    # 5. Candidate F action
    cand_f = candidates.get("cand-f", {})
    action_f = str(cand_f.get("action", "")).lower()
    f_correct = any(w in action_f for w in ["sla", "follow", "phone", "sync", "suresh", "form", "missing"])
    f_pts = 10 if f_correct else 0
    task_score += f_pts
    task_evaluations.append({
        "task_id": "chk-pipe-cand-f",
        "title": "Missing Feedback Form SLA Escalation: Candidate F",
        "status": "PASS" if f_correct else "FAIL",
        "points_earned": f_pts,
        "max_points": 10,
        "feedback": (
            "Correct: Escalated missing evaluation form under 24h feedback SLA."
            if f_correct
            else "Process latency: Must follow up with HM on 4-day overdue scorecard."
        ),
    })

    # 6. Candidate G action
    cand_g = candidates.get("cand-g", {})
    action_g = str(cand_g.get("action", "")).lower()
    g_correct = any(w in action_g for w in ["backup", "metric", "domain", "track record", "review", "renewal", "underlying"])
    g_pts = 10 if g_correct else 0
    task_score += g_pts
    task_evaluations.append({
        "task_id": "chk-pipe-cand-g",
        "title": "Holistic Evidence Evaluation: Candidate G",
        "status": "PASS" if g_correct else "FAIL",
        "points_earned": g_pts,
        "max_points": 10,
        "feedback": (
            "Correct: Retained Candidate G as strong backup based on renewal track record."
            if g_correct
            else "Superficial scoring: Weigh real-world sales metrics alongside interview scores."
        ),
    })

    # 7. Rubric evaluation
    question_evaluations, question_score, max_question_score, any_ai = evaluate_rubric_questions(
        RUBRIC_QUESTIONS, answers, evaluator=None, context="Vertex Digital Solutions: Interview Pipeline & Decision"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Interview pipeline audit completed with score {normalized_score}%. "
        f"Pipeline action score: {task_score}/{max_task_score}. "
        f"Recruitment evaluation score: {question_score}/{max_question_score}. "
        + ("BDE candidate pipeline successfully unblocked and calibrated for final decision." if passed else "Review calibration procedures and SLA escalation protocols.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "deterministic_calibrated",
        "score_breakdown": {
            "pipeline_resolution": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "interview_governance": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }


async def evaluate_interview_pipeline_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    candidates = {c.get("id"): c for c in workspace_snapshot.get("candidateActions", [])}

    task_score = 0
    max_task_score = sum(c["points"] for c in PIPELINE_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    cand_a = candidates.get("cand-a", {})
    action_a = str(cand_a.get("action", "")).lower()
    a_correct = any(w in action_a for w in ["final", "leadership", "vp", "fast-track", "24h", "advance", "offer"]) or cand_a.get("stage") == "Final Leadership"
    a_pts = 15 if a_correct else 0
    task_score += a_pts
    task_evaluations.append({
        "task_id": "chk-pipe-cand-a",
        "title": "Front-Runner Fast-Track: Candidate A",
        "status": "PASS" if a_correct else "FAIL",
        "points_earned": a_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Fast-tracked Candidate A to final leadership round."
            if a_correct
            else "Pipeline stall: Frontrunner Candidate A must be scheduled for final leadership discussion immediately."
        ),
    })

    cand_b = candidates.get("cand-b", {})
    action_b = str(cand_b.get("action", "")).lower()
    b_correct = any(w in action_b for w in ["calibration", "probe", "sync", "objection", "roleplay", "discrepancy", "re-evaluate"])
    b_pts = 15 if b_correct else 0
    task_score += b_pts
    task_evaluations.append({
        "task_id": "chk-pipe-cand-b",
        "title": "Score Discrepancy Calibration: Candidate B",
        "status": "PASS" if b_correct else "FAIL",
        "points_earned": b_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Addressed divergent interviewer scores via calibration sync."
            if b_correct
            else "Inconsistent evaluation: Conflicting ratings on Candidate B require calibration."
        ),
    })

    cand_c = candidates.get("cand-c", {})
    action_c = str(cand_c.get("action", "")).lower()
    c_correct = any(w in action_c for w in ["reschedule", "friday", "accommodate", "timing"])
    c_pts = 10 if c_correct else 0
    task_score += c_pts
    task_evaluations.append({
        "task_id": "chk-pipe-cand-c",
        "title": "Candidate Experience & Reschedule: Candidate C",
        "status": "PASS" if c_correct else "FAIL",
        "points_earned": c_pts,
        "max_points": 10,
        "feedback": (
            "Correct: Promptly accommodated legitimate reschedule request."
            if c_correct
            else "Candidate experience risk: Must accommodate Candidate C's scheduling conflict."
        ),
    })

    cand_d = candidates.get("cand-d", {})
    action_d = str(cand_d.get("action", "")).lower()
    d_correct = any(w in action_d for w in ["incentive", "negotiat", "commission", "hybrid", "5.0", "cap", "bonus", "bonus"])
    d_pts = 15 if d_correct else 0
    task_score += d_pts
    task_evaluations.append({
        "task_id": "chk-pipe-cand-d",
        "title": "Compensation Structuring: Candidate D",
        "status": "PASS" if d_correct else "FAIL",
        "points_earned": d_pts,
        "max_points": 15,
        "feedback": (
            "Correct: Proposed incentive restructuring to align with approved ₹5.0L budget cap."
            if d_correct
            else "Budget breach: Candidate D requires compensation restructuring with sales commissions."
        ),
    })

    cand_f = candidates.get("cand-f", {})
    action_f = str(cand_f.get("action", "")).lower()
    f_correct = any(w in action_f for w in ["sla", "follow", "phone", "sync", "suresh", "form", "missing"])
    f_pts = 10 if f_correct else 0
    task_score += f_pts
    task_evaluations.append({
        "task_id": "chk-pipe-cand-f",
        "title": "Missing Feedback Form SLA Escalation: Candidate F",
        "status": "PASS" if f_correct else "FAIL",
        "points_earned": f_pts,
        "max_points": 10,
        "feedback": (
            "Correct: Escalated missing evaluation form under 24h feedback SLA."
            if f_correct
            else "Process latency: Must follow up with HM on 4-day overdue scorecard."
        ),
    })

    cand_g = candidates.get("cand-g", {})
    action_g = str(cand_g.get("action", "")).lower()
    g_correct = any(w in action_g for w in ["backup", "metric", "domain", "track record", "review", "renewal", "underlying"])
    g_pts = 10 if g_correct else 0
    task_score += g_pts
    task_evaluations.append({
        "task_id": "chk-pipe-cand-g",
        "title": "Holistic Evidence Evaluation: Candidate G",
        "status": "PASS" if g_correct else "FAIL",
        "points_earned": g_pts,
        "max_points": 10,
        "feedback": (
            "Correct: Retained Candidate G as strong backup based on renewal track record."
            if g_correct
            else "Superficial scoring: Weigh real-world sales metrics alongside interview scores."
        ),
    })

    question_evaluations, question_score, max_question_score, any_ai = await evaluate_rubric_questions_async(
        RUBRIC_QUESTIONS, answers, evaluator=ai_evaluator, context="Vertex Digital Solutions: Interview Pipeline & Decision"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Interview pipeline audit completed with score {normalized_score}%. "
        f"Pipeline action score: {task_score}/{max_task_score}. "
        f"Recruitment evaluation score: {question_score}/{max_question_score}. "
        + ("BDE candidate pipeline successfully unblocked and calibrated for final decision." if passed else "Review calibration procedures and SLA escalation protocols.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "ai_assisted" if any_ai else "deterministic_calibrated",
        "score_breakdown": {
            "pipeline_resolution": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "interview_governance": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }
