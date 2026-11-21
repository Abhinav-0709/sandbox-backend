"""
Evaluator for Scenario 3: HR — Handling an Employee Complaint
Organization: BrightEdge Solutions
Role: HR Executive
Subject: Workplace grievance investigation (Rahul vs Reporting Manager)
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


COMPLAINT_INVESTIGATION_CHECKS = [
    {
        "id": "task-workload-context",
        "title": "Workload & Project Contextual Analysis",
        "expected_decision": "Contextualize Raw Metrics (Covering Absence + Seniority)",
        "acceptable_decisions": ["Contextualize Raw Metrics (Covering Absence + Seniority)", "Differentiate Complexity & Absence Coverage"],
        "points": 20,
        "explanation": "Recognized that while Rahul logged 22h overtime and 5 projects, 2 projects were temporary coverage for an absent peer, and some overtime lacked pre-approval. Raw numbers alone do not establish bad faith.",
    },
    {
        "id": "task-confidentiality-defense",
        "title": "Complainant Confidentiality & Information Disclosure",
        "expected_decision": "Deny Full Complaint / Provide Generalized Allegation Summary",
        "acceptable_decisions": ["Deny Full Complaint / Provide Generalized Allegation Summary", "Summary of Issues Only", "Redacted Allegations"],
        "points": 20,
        "explanation": "Strict compliance with HR investigation ethics: refusing to provide the manager with Rahul's full verbatim complaint to prevent retaliation and witness tampering.",
    },
    {
        "id": "task-retaliation-intervention",
        "title": "Retaliation Safeguards & Meeting Exclusion Protocol",
        "expected_decision": "Immediate Neutral Workplace Intervention",
        "acceptable_decisions": ["Immediate Neutral Workplace Intervention", "Interim Protection / Direct Manager Warning", "Prevent Meeting Exclusion"],
        "points": 20,
        "explanation": "Excluding an employee from departmental meetings post-complaint represents potential retaliation; requires immediate HR intervention and interim reporting safeguards.",
    },
    {
        "id": "task-evidence-synthesis",
        "title": "Separation of Verified Facts vs Uncorroborated Allegations",
        "expected_decision": "Differentiate Verified Metrics from Disputed Verbal Statements",
        "acceptable_decisions": ["Differentiate Verified Metrics from Disputed Verbal Statements", "Triangulate Facts and Claims"],
        "points": 20,
        "explanation": "Properly distinguished substantiated data (recorded task counts, unapproved overtime hours) from unverified claims (unrecorded verbal workload requests and meeting comments).",
    },
]

COMPLAINT_QUESTION_RUBRICS = [
    {
        "id": "q1",
        "field": "q1WorkloadMetricsSufficiency",
        "question": "Q1: Does the workload information alone establish that Rahul has been treated unfairly? Explain what else must be considered.",
        "keywords": ["context", "complexity", "absence", "seniority", "overtime", "peer", "volume", "metrics", "alone", "coverage"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "q2AmbiguousWitnessInvestigation",
        "question": "Q2: How would you investigate the disagreement between Rahul and his manager when the witness cannot confirm exactly what happened?",
        "keywords": ["witness", "context", "notes", "pattern", "tone", "evidence", "interview", "corroborate", "circumstantial"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "q3UnrecordedVerbalRequests",
        "question": "Q3: Rahul says he requested workload adjustments three times, but there are no formal records. How would you investigate this claim?",
        "keywords": ["calendar", "1-on-1", "chat", "slack", "teams", "notes", "contemporaneous", "review", "logs", "triangulate"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "q4ManagerDisclosureConfidentiality",
        "question": "Q4: The manager asks you to share Rahul's complete complaint before the investigation begins. What information would you share, and what confidentiality considerations apply?",
        "keywords": ["summary", "redacted", "deny", "verbatim", "confidentiality", "retaliation", "allegations", "protect", "due process"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "q5RetaliatoryExclusionHandling",
        "question": "Q5: What would you do if Rahul reported that his manager had started excluding him from important meetings after submitting the complaint?",
        "keywords": ["retaliation", "interim", "safeguard", "warning", "oversight", "protect", "document", "exclude", "zero tolerance"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q6",
        "field": "q6FormalVsInformalThreshold",
        "question": "Q6: At what point would you recommend formal escalation rather than informal resolution?",
        "keywords": ["harassment", "policy", "retaliation", "pattern", "systemic", "mediation", "formal", "escalation", "power"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q7",
        "field": "q7BalancedFindingsPresentation",
        "question": "Q7: If the evidence supports some allegations but not others, how would you present your findings without overstating the conclusions?",
        "keywords": ["neutral", "evidence", "substantiated", "unsubstantiated", "nuance", "corroborate", "objective", "findings"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q_summary",
        "field": "investigationSummaryDraft",
        "question": "Confidential Investigation Summary & Acknowledgment: Formal workplace grievance briefing report and response letter for the complainant.",
        "keywords": ["investigation", "summary", "brightedge", "rahul", "allegations", "interim", "neutral", "recommendations", "grievance"],
        "required_keywords": 3,
        "min_word_count": 45,
        "max_score": 15,
    },
]


def evaluate_complaint_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    task_evaluations, total_task_pts, max_task_pts = _evaluate_complaint_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = evaluate_rubric_questions(
        COMPLAINT_QUESTION_RUBRICS, answers, evaluator=None, context="BrightEdge Solutions: Workplace Complaint Investigation & Ethical Governance"
    )

    return _build_complaint_result(
        task_evaluations, q_evals, total_task_pts, max_task_pts, total_q, max_q, answers, integrity_flags, "deterministic"
    )


async def evaluate_complaint_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    task_evaluations, total_task_pts, max_task_pts = _evaluate_complaint_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = await evaluate_rubric_questions_async(
        COMPLAINT_QUESTION_RUBRICS, answers, evaluator=ai_evaluator, context="BrightEdge Solutions: Workplace Complaint Investigation & Ethical Governance"
    )

    return _build_complaint_result(
        task_evaluations, q_evals, total_task_pts, max_task_pts, total_q, max_q, answers, integrity_flags, "hybrid_ai" if any_ai else "deterministic"
    )


def _evaluate_complaint_tasks(workspace_snapshot: Dict[str, Any]) -> tuple[List[Dict[str, Any]], int, int]:
    analysis = workspace_snapshot.get("investigation", workspace_snapshot.get("analysis", workspace_snapshot.get("findings", workspace_snapshot)))
    task_evaluations = []
    total_pts = 0
    max_pts = 0

    # 1. Workload context
    max_pts += 20
    workload_eval = str(analysis.get("workloadAssessment", "")).strip().lower()
    workload_ok = any(w in workload_eval for w in ["absence", "complexity", "not conclusive", "context", "unapproved", "temporary", "senior"])
    pts_workload = 20 if workload_ok else 5
    total_pts += pts_workload
    task_evaluations.append({
        "id": "task-workload-context",
        "title": "Workload & Project Contextualization",
        "expected_decision": "Contextualize Metrics (Temporary Absence & Experience)",
        "actual_decision": analysis.get("workloadAssessment", "Analyzed"),
        "is_correct": workload_ok,
        "points_earned": pts_workload,
        "max_points": 20,
        "explanation": "Thorough analysis: correctly recognized that raw project volume reflects peer coverage and seniority rather than prima facie mistreatment." if workload_ok else "Surface-level analysis: failed to examine project complexity and temporary coverage for absent peers.",
    })

    # 2. Confidentiality
    max_pts += 20
    conf_eval = str(analysis.get("disclosureDecision", "")).strip().lower()
    conf_ok = any(w in conf_eval for w in ["deny", "refuse", "summary only", "redacted", "protect", "cannot share"])
    pts_conf = 20 if conf_ok else 0
    total_pts += pts_conf
    task_evaluations.append({
        "id": "task-confidentiality-defense",
        "title": "Complainant Confidentiality & Disclosure Protection",
        "expected_decision": "Refuse Full Document / Share Summary of Allegations Only",
        "actual_decision": analysis.get("disclosureDecision", "Omitted"),
        "is_correct": conf_ok,
        "points_earned": pts_conf,
        "max_points": 20,
        "explanation": "Protected complainant confidentiality: refused to hand over unredacted complaint to prevent retaliation." if conf_ok else "Serious confidentiality breach: sharing unredacted complaints violates investigation ethics.",
    })

    # 3. Retaliation
    max_pts += 20
    retal_eval = str(analysis.get("retaliationSafeguards", "")).strip().lower()
    retal_ok = any(w in retal_eval for w in ["interim", "re-include", "escalat", "warning", "monitor", "oversight", "neutral"])
    pts_retal = 20 if retal_ok else 5
    total_pts += pts_retal
    task_evaluations.append({
        "id": "task-retaliation-intervention",
        "title": "Retaliatory Meeting Exclusion Safeguards",
        "expected_decision": "Enforce Non-Retaliation & Reinstate Meeting Access",
        "actual_decision": analysis.get("retaliationSafeguards", "Omitted"),
        "is_correct": retal_ok,
        "points_earned": pts_retal,
        "max_points": 20,
        "explanation": "Promptly instituted non-retaliation safeguards to protect complainant's operational role during investigation." if retal_ok else "Failed to establish adequate safeguards against post-complaint retaliation.",
    })

    # 4. Evidence synthesis
    max_pts += 20
    synth_eval = str(analysis.get("evidenceSynthesis", "")).strip().lower()
    synth_ok = any(w in synth_eval for w in ["substantiated", "unsubstantiated", "disputed", "interview", "corroborat", "facts"])
    pts_synth = 20 if synth_ok else 5
    total_pts += pts_synth
    task_evaluations.append({
        "id": "task-evidence-synthesis",
        "title": "Substantiated Facts vs Disputed Verbal Claims",
        "expected_decision": "Clear Demarcation of Evidence Confidence Tiers",
        "actual_decision": analysis.get("evidenceSynthesis", "Completed"),
        "is_correct": synth_ok,
        "points_earned": pts_synth,
        "max_points": 20,
        "explanation": "Maintained rigorous impartiality by separating corroborated records from disputed interpersonal claims." if synth_ok else "Conflated uncorroborated allegations with verified evidence.",
    })

    return task_evaluations, total_pts, max_pts


def _build_complaint_result(
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
            "investigation_rigor_score": round((total_task_pts / max_task_pts) * 100) if max_task_pts else 0,
            "ethical_governance_score": round((total_q_pts / max_q_pts) * 100) if max_q_pts else 0,
            "total_points": total_pts,
            "max_points": max_pts,
            "ai_assisted": eval_method == "hybrid_ai",
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity_audit,
        "feedback_summary": (
            "Exemplary workplace investigation: upheld strict confidentiality, resisted premature conclusions, and established balanced, non-retaliatory safeguards."
            if passed
            else "Investigation breached confidentiality protocols or failed to separate facts from uncorroborated allegations."
        ),
    }


__all__ = [
    "evaluate_complaint_submission",
    "evaluate_complaint_submission_async",
    "COMPLAINT_INVESTIGATION_CHECKS",
    "COMPLAINT_QUESTION_RUBRICS",
]
