"""
Evaluator for Scenario 3.1: HR — Investigating a Workplace Complaint
Organization: Vertex Digital Solutions (~400 employees)
Role: Employee Relations Associate
Complainant: Priya Sharma (Customer Operations Associate)
Respondent: Vikram Seth (Customer Operations Team Manager)
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


COMPLAINT_INVESTIGATION_CHECKS = [
    {
        "id": "chk-complaint-respectful-conduct",
        "title": "Respectful Workplace Conduct (Incident 1 & 4 Nov)",
        "points": 15,
        "explanation": "Recognized that managerial criticism in front of colleagues breaches respectful workplace policy (Section 3.1) and is not excused by prior performance reviews.",
    },
    {
        "id": "chk-complaint-witness-assessment",
        "title": "Conflicting Witness Triangulation (Witness A vs Witness B)",
        "points": 15,
        "explanation": "Assessed conflicting witness accounts objectively, noting that Witness A corroborated voice raising while Witness B described mutual defensiveness.",
    },
    {
        "id": "chk-complaint-workload-triage",
        "title": "Workload Contextualization (Incident 2 & 8 Nov)",
        "points": 15,
        "explanation": "Contextualized short-notice tasks on 8 Nov as team-wide surge triage driven by client Apex deadline advancement rather than targeted harassment.",
    },
    {
        "id": "chk-complaint-confidentiality-defense",
        "title": "Complainant Confidentiality Defense & Structured Disclosure",
        "points": 15,
        "explanation": "Refused verbatim complaint disclosure to manager under HR-SOP-008, providing an itemized factual summary of allegations to preserve due process.",
    },
    {
        "id": "chk-complaint-interim-safeguards",
        "title": "Interim Protections & Operational Due Process",
        "points": 15,
        "explanation": "Implemented interim safeguards (reporting line adjustment, 1-on-1 meeting suspension, non-retaliation advisory) and resisted client delivery pressure.",
    },
]

RUBRIC_QUESTIONS = [
    {
        "id": "q1",
        "field": "performanceReviewComplaintValidity",
        "question": "The employee's performance review contains legitimate performance concerns. Does this automatically invalidate their workplace complaint? Explain.",
        "keywords": ["performance", "conduct", "separate", "constructive", "humiliation", "private", "policy", "dignity", "respect"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q2",
        "field": "conflictingWitnessAccountsAssessment",
        "question": "Two witnesses provide conflicting accounts of the same incident. How would you assess their statements?",
        "keywords": ["witness", "corroborate", "credibility", "bias", "facts", "digital", "notes", "context", "triangulate"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q3",
        "field": "confidentialityFairInvestigationBalance",
        "question": "The employee requests confidentiality. How would you balance their request with the need to conduct a fair investigation?",
        "keywords": ["confidentiality", "need-to-know", "natural justice", "redact", "verbatim", "due process", "retaliation", "summary"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q4",
        "field": "managerCompleteComplaintRequestHandling",
        "question": "The manager asks HR to share the employee's complete complaint immediately. How would you handle this request?",
        "keywords": ["summary", "itemized", "withhold", "verbatim", "allegations", "defense", "sop", "policy", "respond"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q5",
        "field": "unprovenMisconductCommunication",
        "question": "If the available evidence does not establish that misconduct occurred, what should HR communicate to the involved parties?",
        "keywords": ["unsubstantiated", "neutral", "coaching", "reminder", "retaliation", "support", "closure", "evidence"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q6",
        "field": "operationalPressureInfluenceInvestigation",
        "question": "The department manager wants the complaint resolved before a client deadline. Should operational pressure influence the investigation outcome?",
        "keywords": ["operational", "pressure", "compromise", "impartial", "interim", "thorough", "fairness", "deadline", "truncate"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
]


def evaluate_complaint_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    task_score = 0
    max_task_score = sum(c["points"] for c in COMPLAINT_INVESTIGATION_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    timeline = {item.get("id"): item for item in workspace_snapshot.get("incidentTimeline", [])}
    interim = workspace_snapshot.get("interimMeasures", {})
    report = workspace_snapshot.get("investigationReportSummary", {})

    # Check 1: Respectful Conduct / Incident 1
    inc1 = timeline.get("inc-1", {})
    inc1_text = (str(inc1.get("preliminaryAssessment", "")) + " " + str(inc1.get("managerPosition", ""))).lower()
    chk1_pass = any(w in inc1_text for w in ["conduct", "respect", "public", "policy", "breach", "private", "humiliat"]) or len(timeline) >= 4
    pts1 = 15 if chk1_pass else 0
    task_score += pts1
    task_evaluations.append({
        "task_id": "chk-complaint-respectful-conduct",
        "title": "Respectful Workplace Conduct (Incident 1 & 4 Nov)",
        "status": "PASS" if chk1_pass else "FAIL",
        "points_earned": pts1,
        "max_points": 15,
        "feedback": (
            "Differentiated: Public reprimands violate professional conduct standards regardless of performance review history."
            if chk1_pass
            else "Standard overlooked: Legitimate performance feedback does not justify public criticism in team meetings."
        ),
    })

    # Check 2: Conflicting Witness Assessment
    inc1_witness = str(inc1.get("witnessCorroboration", "")).lower()
    chk2_pass = any(w in inc1_witness for w in ["witness a", "witness b", "voice", "defensive", "corroborat", "triangulat", "raised"])
    pts2 = 15 if chk2_pass else 0
    task_score += pts2
    task_evaluations.append({
        "task_id": "chk-complaint-witness-assessment",
        "title": "Conflicting Witness Triangulation (Witness A vs Witness B)",
        "status": "PASS" if chk2_pass else "FAIL",
        "points_earned": pts2,
        "max_points": 15,
        "feedback": (
            "Balanced: Triangulated conflicting accounts between Witness A (voice raised) and Witness B (mutual defensiveness)."
            if chk2_pass
            else "Unilateral: Failed to balance conflicting witness observations from the 4-Nov meeting."
        ),
    })

    # Check 3: Workload Contextualization / Incident 2
    inc2 = timeline.get("inc-2", {})
    inc2_text = (str(inc2.get("preliminaryAssessment", "")) + " " + str(inc2.get("managerPosition", ""))).lower()
    chk3_pass = any(w in inc2_text for w in ["apex", "deadline", "shift", "surge", "operational", "client", "team-wide"])
    pts3 = 15 if chk3_pass else 0
    task_score += pts3
    task_evaluations.append({
        "task_id": "chk-complaint-workload-triage",
        "title": "Workload Contextualization (Incident 2 & 8 Nov)",
        "status": "PASS" if chk3_pass else "FAIL",
        "points_earned": pts3,
        "max_points": 15,
        "feedback": (
            "Substantiated: Recognized that 8-Nov task allocation was driven by client deadline advancement across the team."
            if chk3_pass
            else "Unsubstantiated: Treated client-driven surge workload as targeted personal harassment without checking project shifts."
        ),
    })

    # Check 4: Confidentiality Defense
    interim_text = (str(interim.get("meetingProtocol", "")) + " " + str(report.get("recommendedNextSteps", ""))).lower()
    chk4_pass = any(w in interim_text for w in ["summary", "redact", "withhold", "confidential", "itemized", "separate"]) or "confidential" in str(workspace_snapshot).lower()
    pts4 = 15 if chk4_pass else 0
    task_score += pts4
    task_evaluations.append({
        "task_id": "chk-complaint-confidentiality-defense",
        "title": "Complainant Confidentiality Defense & Structured Disclosure",
        "status": "PASS" if chk4_pass else "FAIL",
        "points_earned": pts4,
        "max_points": 15,
        "feedback": (
            "Compliant: Upheld confidentiality policy by withholding verbatim complaint letter while providing itemized summary."
            if chk4_pass
            else "Breach risk: Shared or considered sharing raw complaint letter containing personal statements with manager."
        ),
    })

    # Check 5: Interim Safeguards & Non-Retaliation
    safeguards_text = (str(interim.get("reportingLine", "")) + " " + str(interim.get("nonRetaliationAdvisory", ""))).lower()
    chk5_pass = any(w in safeguards_text for w in ["reporting", "retaliation", "advisory", "interim", "safeguard", "separate", "protect"])
    pts5 = 15 if chk5_pass else 0
    task_score += pts5
    task_evaluations.append({
        "task_id": "chk-complaint-interim-safeguards",
        "title": "Interim Protections & Operational Due Process",
        "status": "PASS" if chk5_pass else "FAIL",
        "points_earned": pts5,
        "max_points": 15,
        "feedback": (
            "Safeguarded: Established interim alternate reporting arrangements and explicit non-retaliation advisories."
            if chk5_pass
            else "Exposure: Left complainant vulnerable to workplace friction without interim reporting safeguards."
        ),
    })

    question_evaluations, question_score, max_question_score, any_ai = evaluate_rubric_questions(
        RUBRIC_QUESTIONS, answers, evaluator=None, context="Vertex Digital Solutions: Workplace Grievance Investigation"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Workplace complaint investigation evaluated with overall score {normalized_score}%. "
        f"Fact-finding and interim safeguards score: {task_score}/{max_task_score}. "
        f"Grievance handling principles score: {question_score}/{max_question_score}. "
        + ("Investigation demonstrates thorough fact-finding, strict confidentiality, and procedural fairness."
           if passed else "Review evidence triangulation procedures, confidentiality protocols, and non-retaliation safeguards.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "deterministic_calibrated",
        "score_breakdown": {
            "grievance_investigation": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "procedural_fairness": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }


async def evaluate_complaint_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    task_score = 0
    max_task_score = sum(c["points"] for c in COMPLAINT_INVESTIGATION_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    timeline = {item.get("id"): item for item in workspace_snapshot.get("incidentTimeline", [])}
    interim = workspace_snapshot.get("interimMeasures", {})
    report = workspace_snapshot.get("investigationReportSummary", {})

    inc1 = timeline.get("inc-1", {})
    inc1_text = (str(inc1.get("preliminaryAssessment", "")) + " " + str(inc1.get("managerPosition", ""))).lower()
    chk1_pass = any(w in inc1_text for w in ["conduct", "respect", "public", "policy", "breach", "private", "humiliat"]) or len(timeline) >= 4
    pts1 = 15 if chk1_pass else 0
    task_score += pts1
    task_evaluations.append({
        "task_id": "chk-complaint-respectful-conduct",
        "title": "Respectful Workplace Conduct (Incident 1 & 4 Nov)",
        "status": "PASS" if chk1_pass else "FAIL",
        "points_earned": pts1,
        "max_points": 15,
        "feedback": "Differentiated: Public reprimands violate professional conduct standards regardless of performance review history.",
    })

    inc1_witness = str(inc1.get("witnessCorroboration", "")).lower()
    chk2_pass = any(w in inc1_witness for w in ["witness a", "witness b", "voice", "defensive", "corroborat", "triangulat", "raised"])
    pts2 = 15 if chk2_pass else 0
    task_score += pts2
    task_evaluations.append({
        "task_id": "chk-complaint-witness-assessment",
        "title": "Conflicting Witness Triangulation (Witness A vs Witness B)",
        "status": "PASS" if chk2_pass else "FAIL",
        "points_earned": pts2,
        "max_points": 15,
        "feedback": "Balanced: Triangulated conflicting accounts between Witness A (voice raised) and Witness B (mutual defensiveness).",
    })

    inc2 = timeline.get("inc-2", {})
    inc2_text = (str(inc2.get("preliminaryAssessment", "")) + " " + str(inc2.get("managerPosition", ""))).lower()
    chk3_pass = any(w in inc2_text for w in ["apex", "deadline", "shift", "surge", "operational", "client", "team-wide"])
    pts3 = 15 if chk3_pass else 0
    task_score += pts3
    task_evaluations.append({
        "task_id": "chk-complaint-workload-triage",
        "title": "Workload Contextualization (Incident 2 & 8 Nov)",
        "status": "PASS" if chk3_pass else "FAIL",
        "points_earned": pts3,
        "max_points": 15,
        "feedback": "Substantiated: Recognized that 8-Nov task allocation was driven by client deadline advancement across the team.",
    })

    interim_text = (str(interim.get("meetingProtocol", "")) + " " + str(report.get("recommendedNextSteps", ""))).lower()
    chk4_pass = any(w in interim_text for w in ["summary", "redact", "withhold", "confidential", "itemized", "separate"]) or "confidential" in str(workspace_snapshot).lower()
    pts4 = 15 if chk4_pass else 0
    task_score += pts4
    task_evaluations.append({
        "task_id": "chk-complaint-confidentiality-defense",
        "title": "Complainant Confidentiality Defense & Structured Disclosure",
        "status": "PASS" if chk4_pass else "FAIL",
        "points_earned": pts4,
        "max_points": 15,
        "feedback": "Compliant: Upheld confidentiality policy by withholding verbatim complaint letter while providing itemized summary.",
    })

    safeguards_text = (str(interim.get("reportingLine", "")) + " " + str(interim.get("nonRetaliationAdvisory", ""))).lower()
    chk5_pass = any(w in safeguards_text for w in ["reporting", "retaliation", "advisory", "interim", "safeguard", "separate", "protect"])
    pts5 = 15 if chk5_pass else 0
    task_score += pts5
    task_evaluations.append({
        "task_id": "chk-complaint-interim-safeguards",
        "title": "Interim Protections & Operational Due Process",
        "status": "PASS" if chk5_pass else "FAIL",
        "points_earned": pts5,
        "max_points": 15,
        "feedback": "Safeguarded: Established interim alternate reporting arrangements and explicit non-retaliation advisories.",
    })

    question_evaluations, question_score, max_question_score, any_ai = await evaluate_rubric_questions_async(
        RUBRIC_QUESTIONS, answers, evaluator=ai_evaluator, context="Vertex Digital Solutions: Workplace Grievance Investigation"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "ai_assisted" if any_ai else "deterministic_fallback",
        "score_breakdown": {
            "grievance_investigation": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "procedural_fairness": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": (
            f"Workplace complaint investigation evaluated with overall score {normalized_score}%. "
            f"Fact-finding score: {task_score}/{max_task_score}. "
            f"Procedural fairness score: {question_score}/{max_question_score}."
        ),
    }
