"""
Evaluator for Scenario 4: HR — Reviewing Employee Performance
Organization: Vertex Solutions
Role: HR Performance Coordinator
Subject: Customer Operations Quarterly Performance Evaluation
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


PERFORMANCE_EVALUATION_CHECKS = [
    {
        "id": "perf-rahul",
        "employee": "Rahul",
        "target": 100,
        "actual": 115,
        "quality_score": 92,
        "expected_achievement_pct": 115.0,
        "expected_recommendation": "Recognition + Workload Delegation Coaching",
        "acceptable_recommendations": ["Recognition + Workload Delegation Coaching", "Exceeds Expectations with Burnout Coaching", "Recognize & Coach"],
        "points": 15,
        "explanation": "High volume (115%) and strong quality (92%), but manager notes taking on too much. Needs coaching on boundary management and peer delegation to prevent burnout.",
    },
    {
        "id": "perf-priya",
        "employee": "Priya",
        "target": 100,
        "actual": 88,
        "quality_score": 97,
        "expected_achievement_pct": 88.0,
        "expected_recommendation": "Protect from Negative Rating / Clarify Priority Shifts",
        "acceptable_recommendations": ["Protect from Negative Rating / Clarify Priority Shifts", "Contextual Pass / Recognize Quality", "Re-evaluate Manager Rating"],
        "points": 20,
        "explanation": "Highest quality score (97%). Volume deficit (88%) was directly caused by additional reporting responsibilities and shifting managerial priorities. Manager's 'Needs improvement' is uncalibrated and unfair.",
    },
    {
        "id": "perf-aman",
        "employee": "Aman",
        "target": 100,
        "actual": 96,
        "quality_score": 90,
        "expected_achievement_pct": 96.0,
        "expected_recommendation": "Solid Performer / Handover Communication Coaching",
        "acceptable_recommendations": ["Solid Performer / Handover Communication Coaching", "On-Track / Communication Training"],
        "points": 10,
        "explanation": "Consistent performer (96% volume, 90% quality); targeted development needed on team handover communication.",
    },
    {
        "id": "perf-neha",
        "employee": "Neha",
        "target": 100,
        "actual": 72,
        "quality_score": 94,
        "expected_achievement_pct": 72.0,
        "expected_recommendation": "Structured Enablement & System Training Before PIP",
        "acceptable_recommendations": ["Structured Enablement & System Training Before PIP", "Training Support Intervention", "Managerial Support Review"],
        "points": 20,
        "explanation": "Volume lag (72%) occurred following transition to an unfamiliar reporting platform with zero requested training support. High quality (94%) proves diligence. Requires structured system enablement before any punitive PIP.",
    },
    {
        "id": "perf-karan",
        "employee": "Karan",
        "target": 100,
        "actual": 105,
        "quality_score": 78,
        "expected_achievement_pct": 105.0,
        "expected_recommendation": "Quality Intervention / Formal Customer Defect Review",
        "acceptable_recommendations": ["Quality Intervention / Formal Customer Defect Review", "Quality Coaching / Audit Complaints", "Address Quality Defects"],
        "points": 20,
        "explanation": "Exceeded volume (105%) but has an unacceptable quality score (78%) and multiple customer complaints. Volume must never be rewarded at the cost of customer satisfaction and churn.",
    },
    {
        "id": "perf-meera",
        "employee": "Meera",
        "target": 100,
        "actual": 91,
        "quality_score": 96,
        "expected_achievement_pct": 91.0,
        "expected_recommendation": "Positive Appraisal / Recognize Complex Case Resolution",
        "acceptable_recommendations": ["Positive Appraisal / Recognize Complex Case Resolution", "Upward Trajectory Recognition", "Meets Expectations with High Complexity"],
        "points": 15,
        "explanation": "Consistent two-quarter improvement trajectory and high quality (96%) while handling the department's most complex customer escalations.",
    },
]

PERFORMANCE_QUESTION_RUBRICS = [
    {
        "id": "q1",
        "field": "q1VolumeVsTotalPerformance",
        "question": "Q1: Should Rahul automatically receive the highest performance rating because he exceeded his target by 15%?",
        "keywords": ["burnout", "delegation", "holistic", "sustainability", "quality", "target", "volume", "speed", "mentorship"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "q2PriyaQualityVsVolumeFairness",
        "question": "Q2: Priya has the highest quality score but missed her target. How would you evaluate her performance fairly?",
        "keywords": ["quality", "competing", "reporting", "duties", "fairness", "adjust", "target", "priya", "pro-rata"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "q3KaranQualityVsVolumeAction",
        "question": "Q3: Karan exceeded his target, but customer complaints and quality issues raise concerns. Would you recommend recognition, coaching or a formal review?",
        "keywords": ["complaints", "quality", "churn", "review", "coaching", "standards", "karan", "defect", "guardrails"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "q4NehaSkillVsSupportDistinction",
        "question": "Q4: Neha has missed her target for two quarters. How would you distinguish a skill gap from inadequate managerial support?",
        "keywords": ["transition", "training", "support", "quality", "neha", "enablement", "onboarding", "system", "ramp-up"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "q5MeeraTrajectoryAndComplexity",
        "question": "Q5: Meera has not achieved her target but has demonstrated consistent improvement. How should this influence her assessment?",
        "keywords": ["trajectory", "improvement", "complex", "quality", "escalations", "meera", "difficulty", "calibration"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q6",
        "field": "q6DevelopmentInterventionPriority",
        "question": "Q6: Which employees should be prioritised for development interventions, and why?",
        "keywords": ["neha", "karan", "priya", "training", "quality", "idp", "prioritise", "interventions", "plans"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q7",
        "field": "q7DefendingAssessmentAgainstManager",
        "question": "Q7: If a manager disagrees with your recommendation because it could affect an employee's annual rating, how would you defend your assessment?",
        "keywords": ["objective", "data", "evidence", "calibration", "fairness", "quality", "metrics", "consistency", "advocate"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q_summary",
        "field": "performanceSynthesisDraft",
        "question": "Quarterly Performance Synthesis & IDP Draft: Comprehensive evaluation report for Customer Operations leadership with individual action plans.",
        "keywords": ["performance", "review", "vertex", "operations", "holistic", "development", "plans", "calibration", "quality"],
        "required_keywords": 3,
        "min_word_count": 45,
        "max_score": 15,
    },
]


def evaluate_performance_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    task_evaluations, total_task_pts, max_task_pts = _evaluate_performance_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = evaluate_rubric_questions(
        PERFORMANCE_QUESTION_RUBRICS, answers, evaluator=None, context="Vertex Solutions: Customer Operations Performance Analytics & Evaluation"
    )

    return _build_performance_result(
        task_evaluations, q_evals, total_task_pts, max_task_pts, total_q, max_q, answers, integrity_flags, "deterministic"
    )


async def evaluate_performance_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    task_evaluations, total_task_pts, max_task_pts = _evaluate_performance_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = await evaluate_rubric_questions_async(
        PERFORMANCE_QUESTION_RUBRICS, answers, evaluator=ai_evaluator, context="Vertex Solutions: Customer Operations Performance Analytics & Evaluation"
    )

    return _build_performance_result(
        task_evaluations, q_evals, total_task_pts, max_task_pts, total_q, max_q, answers, integrity_flags, "hybrid_ai" if any_ai else "deterministic"
    )


def _evaluate_performance_tasks(workspace_snapshot: Dict[str, Any]) -> tuple[List[Dict[str, Any]], int, int]:
    records = workspace_snapshot.get("employees", workspace_snapshot.get("reviews", []))
    task_evaluations = []
    total_pts = 0
    max_pts = 0

    for rule in PERFORMANCE_EVALUATION_CHECKS:
        max_pts += rule["points"]
        rec = next((r for r in records if r.get("id") == rule["id"] or r.get("employee") == rule["employee"]), None)

        if not rec:
            task_evaluations.append({
                "id": rule["id"],
                "title": f"{rule['employee']} Performance Evaluation",
                "expected_decision": rule["expected_recommendation"],
                "actual_decision": "Missing Record",
                "is_correct": False,
                "points_earned": 0,
                "max_points": rule["points"],
                "explanation": f"Performance evaluation for {rule['employee']} was omitted from the assessment sheet.",
            })
            continue

        recommendation = str(rec.get("recommendation", rec.get("decision", ""))).strip().lower()
        acceptable = [a.lower() for a in rule.get("acceptable_recommendations", [rule["expected_recommendation"]])]
        rec_ok = any(a in recommendation for a in acceptable) or any(w in recommendation for w in rule["expected_recommendation"].lower().split())

        # Check calculated achievement percentage
        achieved_pct = float(rec.get("achievementPct", rec.get("actual", 0)) or 0)
        pct_ok = abs(achieved_pct - rule["expected_achievement_pct"]) <= 2.0 or abs(achieved_pct - (rule["actual"] / rule["target"] * 100)) <= 2.0

        pts = 0
        if rec_ok and pct_ok:
            pts = rule["points"]
        elif rec_ok or pct_ok:
            pts = round(rule["points"] * 0.6)

        total_pts += pts
        task_evaluations.append({
            "id": rule["id"],
            "title": f"{rule['employee']} (Target: {rule['target']} | Actual: {rule['actual']} | Quality: {rule['quality_score']}%)",
            "expected_decision": rule["expected_recommendation"],
            "actual_decision": rec.get("recommendation", "Evaluated"),
            "is_correct": pts >= rule["points"] * 0.75,
            "points_earned": pts,
            "max_points": rule["points"],
            "explanation": rule["explanation"] if pts == rule["points"] else f"Variance in recommendation for {rule['employee']}. Contextualize volume vs quality.",
        })

    return task_evaluations, total_pts, max_pts


def _build_performance_result(
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
            "performance_analytics_score": round((total_task_pts / max_task_pts) * 100) if max_task_pts else 0,
            "development_reasoning_score": round((total_q_pts / max_q_pts) * 100) if max_q_pts else 0,
            "total_points": total_pts,
            "max_points": max_pts,
            "ai_assisted": eval_method == "hybrid_ai",
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity_audit,
        "feedback_summary": (
            "Exemplary performance evaluation: resisted simplistic volume bias, accounted for systemic support barriers, and crafted holistic individual development plans."
            if passed
            else "Evaluation relied too heavily on single-metric volume or failed to contextualize managerial feedback."
        ),
    }


__all__ = [
    "evaluate_performance_submission",
    "evaluate_performance_submission_async",
    "PERFORMANCE_EVALUATION_CHECKS",
    "PERFORMANCE_QUESTION_RUBRICS",
]
