from __future__ import annotations

from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions_async, AiRubricEvaluator


HR_CANDIDATE_CHECKS = [
    {
        "id": "cand-01",
        "name": "Marcus Vance",
        "expected_decision": "Reject",
        "alternate_acceptable_decision": "Reconsider",
        "expected_score_range": (35, 55),
        "max_points": 10,
        "explanation": "Listed duplicate projects under different names; lacks substantive commercial experience.",
    },
    {
        "id": "cand-02",
        "name": "Elena Rostova",
        "expected_decision": "Shortlist",
        "alternate_acceptable_decision": None,
        "expected_score_range": (82, 94),
        "max_points": 10,
        "explanation": "Strong verified React & TypeScript projects, clear Git history, meets all essential criteria.",
    },
    {
        "id": "cand-03",
        "name": "Tariq Al-Mansoor",
        "expected_decision": "Reject",
        "alternate_acceptable_decision": None,
        "expected_score_range": (30, 48),
        "max_points": 8,
        "explanation": "Fails essential React criteria; only possesses basic HTML/CSS without component framework evidence.",
    },
    {
        "id": "cand-04",
        "name": "Chloe Bennett",
        "expected_decision": "Shortlist",
        "alternate_acceptable_decision": None,
        "expected_score_range": (80, 92),
        "max_points": 10,
        "explanation": "Verified accessible UI components, comprehensive unit tests, clear documentation.",
    },
    {
        "id": "cand-05",
        "name": "Liam Gallagher",
        "expected_decision": "Reconsider",
        "alternate_acceptable_decision": "Reject",
        "expected_score_range": (50, 68),
        "max_points": 8,
        "explanation": "Commercial experience present, but portfolio links are broken or unverified.",
    },
    {
        "id": "cand-06",
        "name": "Aisha Patel",
        "expected_decision": "Shortlist",
        "alternate_acceptable_decision": None,
        "expected_score_range": (85, 96),
        "max_points": 10,
        "explanation": "Exceptional full responsive portfolio with live deployed demos and active GitHub contributions.",
    },
    {
        "id": "cand-07",
        "name": "Devon Miller",
        "expected_decision": "Reject",
        "alternate_acceptable_decision": None,
        "expected_score_range": (35, 52),
        "max_points": 8,
        "explanation": "Overclaimed competencies without verifiable code repository.",
    },
    {
        "id": "cand-08",
        "name": "Zoe Chen",
        "expected_decision": "Shortlist",
        "alternate_acceptable_decision": "Reconsider",
        "expected_score_range": (78, 90),
        "max_points": 10,
        "explanation": "Strong algorithmic foundations and demonstrated modern state management.",
    },
    {
        "id": "cand-09",
        "name": "Samira Khan",
        "expected_decision": "Reject",
        "alternate_acceptable_decision": "Reconsider",
        "expected_score_range": (42, 60),
        "max_points": 12,
        "explanation": "Hiring manager's personal recommendation, but objectively fails responsive and framework standards. Tests bias resistance.",
    },
    {
        "id": "cand-10",
        "name": "Lucas Silva",
        "expected_decision": "Reconsider",
        "alternate_acceptable_decision": "Reject",
        "expected_score_range": (55, 70),
        "max_points": 8,
        "explanation": "Adequate frontend knowledge but minimal team collaboration evidence.",
    },
    {
        "id": "cand-11",
        "name": "Maya Lin",
        "expected_decision": "Reject",
        "alternate_acceptable_decision": None,
        "expected_score_range": (40, 58),
        "max_points": 10,
        "explanation": "Overclaimed full-stack experience; repositories show static boilerplate rather than dynamic backend integration.",
    },
    {
        "id": "cand-12",
        "name": "Jordan Taylor",
        "expected_decision": "Reconsider",
        "alternate_acceptable_decision": "Reject",
        "expected_score_range": (58, 72),
        "max_points": 8,
        "explanation": "Borderline candidate; possesses design talent but lacks complex asynchronous state handling.",
    },
]

# Alias for backwards compatibility and test imports
CANDIDATE_BENCHMARKS = HR_CANDIDATE_CHECKS

HR_QUESTION_RUBRICS = [
    {
        "id": "q1",
        "field": "q1ShortlistRanking",
        "question": "Q1: Provide shortlisting justification for your top 4 candidates.",
        "keywords": ["React", "portfolio", "essential", "criteria", "evidence", "shortlist", "Elena", "Aisha", "Chloe", "Zoe"],
        "required_keywords": 4,
        "min_word_count": 50,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "q2ExperienceVsProjects",
        "question": "Q2: Explain why verified project evidence outweighs unverified commercial years.",
        "keywords": ["evidence", "practical", "code", "GitHub", "verify", "demonstrated", "competence"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "q3OverclaimedFullStack",
        "question": "Q3: How did you identify overclaimed technical claims in candidate portfolios?",
        "keywords": ["commits", "static", "boilerplate", "repository", "discrepancy", "inspection", "audit"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "q4ManagerBiasResponse",
        "question": "Q4: How did you handle hiring manager informal preference while maintaining objective screening rigor?",
        "keywords": ["bias", "objective", "benchmark", "criteria", "fairness", "standards", "Samira"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 12,
    },
    {
        "id": "memo",
        "field": "recruitmentSummaryDraft",
        "question": "Hiring Memo: Formal recruitment briefing memo for Engineering Lead David Sterling.",
        "keywords": ["shortlist", "interview", "rationale", "criteria", "recommendation", "David", "benchmark"],
        "required_keywords": 4,
        "min_word_count": 50,
        "max_score": 15,
    },
]


def evaluate_hr_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    candidate_rows = workspace_snapshot.get("candidateRows", [])
    task_evaluations: List[Dict[str, Any]] = []
    total_candidate_points = 0
    max_candidate_points = 0

    for check in HR_CANDIDATE_CHECKS:
        max_candidate_points += check["max_points"]
        row = next((r for r in candidate_rows if r.get("id") == check["id"]), None)

        actual_decision = row.get("decision", "Pending") if row else "Missing"
        actual_score = float(row.get("candidateScore", 0)) if row else 0
        user_flags = (row.get("redFlagsIdentified", "") if row else "").lower()

        is_decision_correct = actual_decision == check["expected_decision"]
        is_acceptable = is_decision_correct or actual_decision == check.get("alternate_acceptable_decision")
        is_score_reasonable = (
            check["expected_score_range"][0] - 8 <= actual_score <= check["expected_score_range"][1] + 8
        )

        points = 0
        if is_decision_correct:
            points += round(check["max_points"] * 0.7)
        elif is_acceptable:
            points += round(check["max_points"] * 0.45)

        if is_score_reasonable:
            points += round(check["max_points"] * 0.15)

        # Red flag bonus detection
        if check["id"] == "cand-01" and any(k in user_flags for k in ["duplicate", "same", "demo"]):
            points += round(check["max_points"] * 0.15)
        elif check["id"] == "cand-09" and any(k in user_flags for k in ["bias", "recommend", "responsive", "template"]):
            points += round(check["max_points"] * 0.15)
        elif check["id"] == "cand-11" and any(k in user_flags for k in ["full-stack", "overclaim", "static"]):
            points += round(check["max_points"] * 0.15)

        points = min(points, check["max_points"])
        total_candidate_points += points

        task_evaluations.append({
            "id": check["id"],
            "name": check["name"],
            "expected_decision": check["expected_decision"],
            "actual_decision": actual_decision,
            "is_correct": points >= check["max_points"] * 0.75,
            "points_earned": points,
            "max_points": check["max_points"],
            "explanation": (
                f"Accurately assessed {check['name']}: {check['explanation']}"
                if points >= check["max_points"] * 0.75
                else f"Variance on {check['name']}: Expected {check['expected_decision']}, assigned {actual_decision}."
            ),
        })

    # Evaluate question rubrics
    question_evaluations: List[Dict[str, Any]] = []
    total_question_points = 0
    max_question_points = 0

    for rubric in HR_QUESTION_RUBRICS:
        max_question_points += rubric["max_score"]
        answer_text = answers.get(rubric["field"], "")
        lower = answer_text.lower() if isinstance(answer_text, str) else ""

        matched = [kw for kw in rubric["keywords"] if kw.lower() in lower]
        missing = [kw for kw in rubric["keywords"] if kw.lower() not in lower]
        word_count = len(answer_text.strip().split()) if isinstance(answer_text, str) else 0

        if word_count >= rubric["min_word_count"] and len(matched) >= rubric["required_keywords"]:
            score = rubric["max_score"]
        elif word_count >= 10 and len(matched) >= 1:
            score = min(
                rubric["max_score"] - 2,
                round((len(matched) / rubric["required_keywords"]) * (rubric["max_score"] * 0.75)),
            )
        elif word_count > 5:
            score = 2
        else:
            score = 0

        total_question_points += score

        question_evaluations.append({
            "id": rubric["id"],
            "question": rubric["question"],
            "answer_length": word_count,
            "matched_keywords": matched,
            "missing_keywords": missing[:4],
            "score": score,
            "max_score": rubric["max_score"],
            "feedback": (
                "Sound justification grounded in objective evidence and bias mitigation."
                if score >= rubric["max_score"]
                else f"Consider mentioning key benchmarks: {', '.join(missing[:3])}."
                if score > 4
                else "Response needs more rigorous evidence-based rationale."
            ),
        })

    return _build_hr_evaluation_result(
        task_evaluations=task_evaluations,
        question_evaluations=question_evaluations,
        total_candidate_points=total_candidate_points,
        max_candidate_points=max_candidate_points,
        total_question_points=total_question_points,
        max_question_points=max_question_points,
        answers=answers,
        integrity_flags=integrity_flags,
        evaluation_method="rubric",
    )


async def evaluate_hr_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    """
    Asynchronously evaluates an HR Talent Screening simulation with AI-assisted
    qualitative scoring and automatic fallback.
    """
    candidate_scores = workspace_snapshot.get("candidateScores", {})
    candidate_decisions = workspace_snapshot.get("candidateDecisions", {})
    candidate_red_flags = workspace_snapshot.get("candidateRedFlags", {})

    task_evaluations: List[Dict[str, Any]] = []
    total_candidate_points = 0
    max_candidate_points = 0

    for check in HR_CANDIDATE_CHECKS:
        max_candidate_points += check["max_points"]
        actual_decision = candidate_decisions.get(check["id"], "None")
        actual_score = float(candidate_scores.get(check["id"], 0))
        user_flags = candidate_red_flags.get(check["id"], [])
        if isinstance(user_flags, str):
            user_flags = [user_flags]
        user_flags = [f.lower() for f in user_flags]

        is_decision_exact = actual_decision == check["expected_decision"]
        is_decision_acceptable = is_decision_exact or (
            check["alternate_acceptable_decision"] and actual_decision == check["alternate_acceptable_decision"]
        )
        min_expected, max_expected = check["expected_score_range"]
        is_score_reasonable = (min_expected - 10) <= actual_score <= (max_expected + 10)

        points = 0
        if is_decision_exact:
            points += round(check["max_points"] * 0.70)
        elif is_decision_acceptable:
            points += round(check["max_points"] * 0.45)

        if is_score_reasonable:
            points += round(check["max_points"] * 0.15)

        if check["id"] == "cand-01" and any(k in user_flags for k in ["duplicate", "same", "demo"]):
            points += round(check["max_points"] * 0.15)
        elif check["id"] == "cand-09" and any(k in user_flags for k in ["bias", "recommend", "responsive", "template"]):
            points += round(check["max_points"] * 0.15)
        elif check["id"] == "cand-11" and any(k in user_flags for k in ["full-stack", "overclaim", "static"]):
            points += round(check["max_points"] * 0.15)

        points = min(points, check["max_points"])
        total_candidate_points += points

        task_evaluations.append({
            "id": check["id"],
            "name": check["name"],
            "expected_decision": check["expected_decision"],
            "actual_decision": actual_decision,
            "is_correct": points >= check["max_points"] * 0.75,
            "points_earned": points,
            "max_points": check["max_points"],
            "explanation": (
                f"Accurately assessed {check['name']}: {check['explanation']}"
                if points >= check["max_points"] * 0.75
                else f"Variance on {check['name']}: Expected {check['expected_decision']}, assigned {actual_decision}."
            ),
        })

    # Concurrently evaluate HR questions with AI
    question_evaluations, total_q_pts, max_q_pts, any_ai = await evaluate_rubric_questions_async(
        rubrics=HR_QUESTION_RUBRICS,
        answers=answers,
        evaluator=ai_evaluator,
        context="Vivoki HR Assessment: Frontend engineering candidate screening, portfolio code review, bias mitigation, shortlist memo.",
    )

    return _build_hr_evaluation_result(
        task_evaluations=task_evaluations,
        question_evaluations=question_evaluations,
        total_candidate_points=total_candidate_points,
        max_candidate_points=max_candidate_points,
        total_question_points=total_q_pts,
        max_question_points=max_q_pts,
        answers=answers,
        integrity_flags=integrity_flags,
        evaluation_method="hybrid_ai" if any_ai else "rubric",
    )


def _build_hr_evaluation_result(
    task_evaluations: List[Dict[str, Any]],
    question_evaluations: List[Dict[str, Any]],
    total_candidate_points: int,
    max_candidate_points: int,
    total_question_points: int,
    max_question_points: int,
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    evaluation_method: str = "rubric",
) -> Dict[str, Any]:
    paste_count = int(integrity_flags.get("pasteCount", 0))
    integrity_audit = evaluate_integrity(answers, paste_count=paste_count)

    total_points = total_candidate_points + total_question_points
    max_points = max_candidate_points + max_question_points
    overall_score = round((total_points / max_points) * 100) if max_points else 0
    if integrity_audit["is_ai_flagged"]:
        overall_score = max(0, overall_score - 10)

    passed = overall_score >= 70 and not integrity_audit["is_ai_flagged"]

    return {
        "overall_score": overall_score,
        "passed": passed,
        "evaluation_method": evaluation_method,
        "score_breakdown": {
            "candidate_screening_score": round((total_candidate_points / max_candidate_points) * 100),
            "analytical_reasoning_score": round((total_question_points / max_question_points) * 100),
            "total_points": total_points,
            "max_points": max_points,
            "ai_assisted": evaluation_method == "hybrid_ai",
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity_audit,
        "feedback_summary": (
            "Exemplary talent screening: demonstrated strong resistance to bias, spotted overclaimed skills, and produced a defensible candidate shortlist."
            if passed
            else "Did not meet shortlist validation threshold. Review bias checks and criteria scoring."
        ),
    }


__all__ = [
    "evaluate_hr_submission",
    "evaluate_hr_submission_async",
    "HR_CANDIDATE_CHECKS",
    "CANDIDATE_BENCHMARKS",
    "HR_QUESTION_RUBRICS",
    "_build_hr_evaluation_result",
]

