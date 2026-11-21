from __future__ import annotations

import re
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions_async, AiRubricEvaluator


SDE_QUESTION_RUBRICS = [
    {
        "id": "q1",
        "field": "q1RootCauses",
        "question": "Q1: Explain the underlying concurrency, state, and security root causes of the 3 production issues.",
        "keywords": ["race condition", "idempotency", "optimistic", "rollback", "mass assignment", "BOLA", "authorization"],
        "required_keywords": 4,
        "min_word_count": 50,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "q2DuplicatePrevention",
        "question": "Q2: Detail your architecture for preventing duplicate task creation under high latency networks.",
        "keywords": ["idempotency key", "unique constraint", "debounce", "disable button", "header", "database"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "q3OptimisticUiTradeoffs",
        "question": "Q3: What are the failure modes of optimistic UI and how should client-server reconciliation be designed?",
        "keywords": ["rollback", "reconcile", "transaction", "commit", "temporary ID", "server state"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "q4OwnershipSecurityRisks",
        "question": "Q4: Describe how mass-assignment vulnerabilities arise in REST APIs and your defense-in-depth prevention strategy.",
        "keywords": ["DTO", "whitelist", "tenant", "authorization", "request body", "validation schema"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "q5LayerResponsibilities",
        "question": "Q5: How do you partition state consistency responsibilities across frontend, API gateway, backend service, and DB?",
        "keywords": ["frontend", "API", "backend", "database", "ACID", "constraints", "idempotency"],
        "required_keywords": 4,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q6",
        "field": "q6TestingStrategy",
        "question": "Q6: Design automated regression tests to verify that these 3 bugs cannot re-occur.",
        "keywords": ["concurrent", "integration test", "mock", "transaction rollback", "security test", "e2e"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
]


def evaluate_sde_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    diagnostics = workspace_snapshot.get("diagnostics", [])
    task_evaluations: List[Dict[str, Any]] = []
    diagnostics_score = 0

    # Issue 1: Duplicate Tasks
    d1 = next((d for d in diagnostics if d.get("issueId") == "issue-1"), None)
    d1_layer_ok = d1 and d1.get("primaryLayer") in ["Architecture / Multi-Layer", "Backend API", "Frontend"]
    d1_notes = (d1.get("notes", "") + " " + d1.get("selectedFix", "")) if d1 else ""
    d1_notes_match = bool(re.search(r"idempot|debounce|disable|unique|race", d1_notes, re.IGNORECASE))
    d1_score = (5 if d1_layer_ok else 0) + (5 if d1_notes_match else 0)
    diagnostics_score += d1_score
    task_evaluations.append({
        "id": "issue-1",
        "title": "Issue 1: Duplicate Task Creation Under Concurrency",
        "is_correct": d1_score >= 8,
        "points_earned": d1_score,
        "max_points": 10,
        "explanation": (
            "Accurate multi-layer diagnosis: identified both client button debouncing and server-side idempotency keys with unique constraints."
            if d1_score >= 8
            else "Partial diagnosis: Issue 1 requires both client button disabling/debouncing and backend idempotency keys."
        ),
    })

    # Issue 2: Missing Tasks on Refresh
    d2 = next((d for d in diagnostics if d.get("issueId") == "issue-2"), None)
    d2_layer_ok = d2 and d2.get("primaryLayer") in ["Frontend", "Backend API", "Architecture / Multi-Layer"]
    d2_notes = (d2.get("notes", "") + " " + d2.get("selectedFix", "")) if d2 else ""
    d2_notes_match = bool(re.search(r"optimistic|rollback|commit|transaction|disappear", d2_notes, re.IGNORECASE))
    d2_score = (5 if d2_layer_ok else 0) + (5 if d2_notes_match else 0)
    diagnostics_score += d2_score
    task_evaluations.append({
        "id": "issue-2",
        "title": "Issue 2: Premature Optimistic UI & Transaction Rollback",
        "is_correct": d2_score >= 8,
        "points_earned": d2_score,
        "max_points": 10,
        "explanation": (
            "Accurate root cause: identified frontend premature optimistic state without rollback and backend uncommitted transaction."
            if d2_score >= 8
            else "Ensure addressing both frontend state rollback on network rejection and committing DB transaction before HTTP 201."
        ),
    })

    # Issue 3: Task Ownership Leak
    d3 = next((d for d in diagnostics if d.get("issueId") == "issue-3"), None)
    d3_layer_ok = d3 and d3.get("primaryLayer") in ["Backend API", "Architecture / Multi-Layer"]
    d3_notes = (d3.get("notes", "") + " " + d3.get("selectedFix", "")) if d3 else ""
    d3_notes_match = bool(re.search(r"mass|assign|idor|owner|whitelist|dto", d3_notes, re.IGNORECASE))
    d3_score = (5 if d3_layer_ok else 0) + (5 if d3_notes_match else 0)
    diagnostics_score += d3_score
    task_evaluations.append({
        "id": "issue-3",
        "title": "Issue 3: Mass Assignment / IDOR Ownership Vulnerability",
        "is_correct": d3_score >= 8,
        "points_earned": d3_score,
        "max_points": 10,
        "explanation": (
            "Defensive design confirmed: identified mass assignment risk and mandated DTO request whitelisting with tenant isolation."
            if d3_score >= 8
            else "Issue 3 requires strict schema whitelisting (DTOs) and enforcing authenticated user ownership on the server."
        ),
    })

    # Evaluate question rubrics
    question_evaluations: List[Dict[str, Any]] = []
    total_question_points = 0
    max_question_points = 0

    for rubric in SDE_QUESTION_RUBRICS:
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
                "Deep architectural rigor: sound analysis of concurrency, atomicity, and security boundaries."
                if score >= rubric["max_score"]
                else f"Consider addressing: {', '.join(missing[:3])}."
                if score > 4
                else "Response requires deeper systems analysis and explicit failure-mode handling."
            ),
        })

    return _build_sde_evaluation_result(
        task_evaluations=task_evaluations,
        question_evaluations=question_evaluations,
        diagnostics_score=diagnostics_score,
        total_question_points=total_question_points,
        max_question_points=max_question_points,
        answers=answers,
        integrity_flags=integrity_flags,
        evaluation_method="deterministic",
    )


async def evaluate_sde_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    """
    Asynchronously evaluates an SDE Bug Triage simulation with AI-assisted
    qualitative scoring and automatic fallback.
    """
    diagnostics = workspace_snapshot.get("diagnostics", [])
    task_evaluations: List[Dict[str, Any]] = []
    diagnostics_score = 0

    # Issue 1: Duplicate Tasks
    d1 = next((d for d in diagnostics if d.get("issueId") == "issue-1"), None)
    d1_layer_ok = d1 and d1.get("primaryLayer") in ["Architecture / Multi-Layer", "Backend API", "Frontend"]
    d1_notes = (d1.get("notes", "") + " " + d1.get("selectedFix", "")) if d1 else ""
    d1_notes_match = bool(re.search(r"idempot|debounce|disable|unique|race", d1_notes, re.IGNORECASE))
    d1_score = (5 if d1_layer_ok else 0) + (5 if d1_notes_match else 0)
    diagnostics_score += d1_score
    task_evaluations.append({
        "id": "issue-1",
        "title": "Issue 1: Duplicate Task Creation Under Concurrency",
        "is_correct": d1_score >= 8,
        "points_earned": d1_score,
        "max_points": 10,
        "explanation": (
            "Accurate multi-layer diagnosis: identified both client button debouncing and server-side idempotency keys with unique constraints."
            if d1_score >= 8
            else "Partial diagnosis: ensure addressing both UI double-clicks and server database race conditions."
        ),
    })

    # Issue 2: Silent Data Drop
    d2 = next((d for d in diagnostics if d.get("issueId") == "issue-2"), None)
    d2_layer_ok = d2 and d2.get("primaryLayer") in ["Backend API", "Architecture / Multi-Layer", "Database"]
    d2_notes = (d2.get("notes", "") + " " + d2.get("selectedFix", "")) if d2 else ""
    d2_notes_match = bool(re.search(r"transact|rollback|catch|log|atom", d2_notes, re.IGNORECASE))
    d2_score = (5 if d2_layer_ok else 0) + (5 if d2_notes_match else 0)
    diagnostics_score += d2_score
    task_evaluations.append({
        "id": "issue-2",
        "title": "Issue 2: Silent Task Deletion Failure Without Rollback",
        "is_correct": d2_score >= 8,
        "points_earned": d2_score,
        "max_points": 10,
        "explanation": (
            "Exact transactional diagnosis: wrapped subtask deletions and parent deletion in an atomic database transaction with explicit error propagation."
            if d2_score >= 8
            else "Incomplete diagnosis: critical need for atomic transactions and removing empty catch blocks."
        ),
    })

    # Issue 3: Privilege Escalation
    d3 = next((d for d in diagnostics if d.get("issueId") == "issue-3"), None)
    d3_layer_ok = d3 and d3.get("primaryLayer") in ["Backend API", "Architecture / Multi-Layer", "Security"]
    d3_notes = (d3.get("notes", "") + " " + d3.get("selectedFix", "")) if d3 else ""
    d3_notes_match = bool(re.search(r"schema|dto|allowlist|whitelist|mass|strip|perm", d3_notes, re.IGNORECASE))
    d3_score = (5 if d3_layer_ok else 0) + (5 if d3_notes_match else 0)
    diagnostics_score += d3_score
    task_evaluations.append({
        "id": "issue-3",
        "title": "Issue 3: Mass Assignment Privilege Escalation (Role Tampering)",
        "is_correct": d3_score >= 8,
        "points_earned": d3_score,
        "max_points": 10,
        "explanation": (
            "Robust security defense: implemented strict DTO schema allowlisting preventing direct client mutation of user role or organization membership."
            if d3_score >= 8
            else "Security risk remaining: must strictly validate and allowlist assignable fields in the update payload."
        ),
    })

    # Concurrently evaluate SDE architectural questions with AI
    question_evaluations, total_q_pts, max_q_pts, any_ai = await evaluate_rubric_questions_async(
        rubrics=SDE_QUESTION_RUBRICS,
        answers=answers,
        evaluator=ai_evaluator,
        context="Vivoki Software Engineering Assessment: Production defect triage, distributed race condition mitigation, atomic rollback, mass assignment defense, automated regression test strategy.",
    )

    return _build_sde_evaluation_result(
        task_evaluations=task_evaluations,
        question_evaluations=question_evaluations,
        diagnostics_score=diagnostics_score,
        total_question_points=total_q_pts,
        max_question_points=max_q_pts,
        answers=answers,
        integrity_flags=integrity_flags,
        evaluation_method="hybrid_ai" if any_ai else "deterministic",
    )


def _build_sde_evaluation_result(
    task_evaluations: List[Dict[str, Any]],
    question_evaluations: List[Dict[str, Any]],
    diagnostics_score: int,
    total_question_points: int,
    max_question_points: int,
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    evaluation_method: str = "deterministic",
) -> Dict[str, Any]:
    paste_count = int(integrity_flags.get("pasteCount", 0))
    integrity_audit = evaluate_integrity(answers, paste_count=paste_count)

    total_points = diagnostics_score + total_question_points
    max_points = 30 + max_question_points
    overall_score = round((total_points / max_points) * 100) if max_points else 0
    if integrity_audit["is_ai_flagged"]:
        overall_score = max(0, overall_score - 10)

    passed = overall_score >= 70 and not integrity_audit["is_ai_flagged"]

    return {
        "overall_score": overall_score,
        "passed": passed,
        "evaluation_method": evaluation_method,
        "score_breakdown": {
            "diagnostics_score": round((diagnostics_score / 30) * 100),
            "architecture_reasoning_score": round((total_question_points / max_question_points) * 100),
            "total_points": total_points,
            "max_points": max_points,
            "ai_assisted": evaluation_method == "hybrid_ai",
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity_audit,
        "feedback_summary": (
            "Outstanding systems engineering: correctly diagnosed all 3 production defects with robust architectural remediations."
            if passed
            else "Did not meet production diagnosis threshold. Review concurrency locking and mass-assignment defense."
        ),
    }
