"""
Evaluator for Scenario 3.2: HR — Managing a Disciplinary Case and Policy Violation
Organization: Vertex Digital Solutions
Role: Employee Relations Associate
Employee: Rahul Mehta (Senior Sales Executive)
Incident: Unauthorized external transmission of Class 3 customer pricing spreadsheet
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


DISCIPLINARY_CHECKS = [
    {
        "id": "chk-disc-policy-breach",
        "title": "Information Security Policy Breach Verification",
        "points": 15,
        "explanation": "Verified that transmitting Customer_Pricing_November.xlsx to an unapproved personal email (@gmail.com) breaches POL-SEC-004 Class 3 confidentiality rules.",
    },
    {
        "id": "chk-disc-verbal-approval-inquiry",
        "title": "Verbal Approval & Consultant Relationship Inquiry",
        "points": 15,
        "explanation": "Addressed the disputed verbal approval claim, noting that verbal remarks cannot override formal written Infosec policy and requiring interview with consultant Rajiv Sen.",
    },
    {
        "id": "chk-disc-mitigating-factors",
        "title": "Comprehensive Mitigating Factors Assessment",
        "points": 15,
        "explanation": "Identified crucial mitigating factors: 3-year unblemished record, genuine belief of RFP assistance, no secondary exfiltration, and organizational training gap (uncompleted 2026 module).",
    },
    {
        "id": "chk-disc-procedural-fairness",
        "title": "Procedural Fairness & Due Process Defense",
        "points": 15,
        "explanation": "Resisted Sales Manager's demand for summary termination; upheld DISC-SOP-002 requiring formal written notice, 48h prep time, and right to colleague representation.",
    },
    {
        "id": "chk-disc-proportional-sanction",
        "title": "Proportional Sanction & Remediation Recommendation",
        "points": 15,
        "explanation": "Recommended a graduated, proportional disciplinary outcome (e.g. Final Written Warning with mandatory training recertification and DLP monitoring) rather than wrongful dismissal.",
    },
]

RUBRIC_QUESTIONS = [
    {
        "id": "q1",
        "field": "verbalApprovalClaimInvestigation",
        "question": "The employee admits sending the document externally but claims they had verbal approval. How should HR investigate this claim?",
        "keywords": ["interview", "consultant", "rajiv", "manager", "slack", "email", "nda", "override", "policy", "written"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q2",
        "field": "recipientAccessIntentDelineation",
        "question": "Does the fact that the external recipient accessed the document automatically prove that the employee intended to disclose confidential information improperly?",
        "keywords": ["access", "intent", "malicious", "espionage", "breach", "exposure", "delineate", "harm", "good faith"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q3",
        "field": "prejudgedTerminationProceduralFairness",
        "question": "The Sales Manager wants immediate termination. Why should HR avoid deciding the outcome before completing the disciplinary process?",
        "keywords": ["procedural fairness", "natural justice", "prejudge", "due process", "unfair dismissal", "hearing", "mitigating", "sop"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q4",
        "field": "incompleteTrainingAssessmentInfluence",
        "question": "How should the employee's incomplete training records influence the assessment of the incident?",
        "keywords": ["training", "mitigating", "module", "compliance", "organizational", "culpability", "negligence", "awareness"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q5",
        "field": "policyViolationVsSeverityDelineation",
        "question": "What is the difference between evidence that establishes a policy violation and evidence that establishes the severity of the misconduct?",
        "keywords": ["technical", "violation", "severity", "intent", "harm", "mitigating", "commercial", "context", "dlp"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
    {
        "id": "q6",
        "field": "unintentionalViolationDisciplinaryFactors",
        "question": "If the investigation finds that the employee violated the policy but there was no deliberate intention to cause harm, what factors should HR consider before recommending disciplinary action?",
        "keywords": ["proportional", "warning", "remorse", "tenure", "record", "cooperation", "remediation", "unblemished", "sanction"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 5,
    },
]


def evaluate_disciplinary_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    task_score = 0
    max_task_score = sum(c["points"] for c in DISCIPLINARY_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    case = workspace_snapshot.get("disciplinaryCase", {})
    matrix = workspace_snapshot.get("mitigatingAggravatingMatrix", {})
    notice = workspace_snapshot.get("hearingNoticeDraft", {})
    recs = workspace_snapshot.get("handoverRecommendations", {})

    # Check 1: Policy Breach Verification
    case_allegation = (str(case.get("allegation", "")) + " " + str(notice.get("charges", ""))).lower()
    chk1_pass = any(w in case_allegation for w in ["pol-sec-004", "class 3", "confidential", "pricing", "gmail", "security", "breach"])
    pts1 = 15 if chk1_pass else 0
    task_score += pts1
    task_evaluations.append({
        "task_id": "chk-disc-policy-breach",
        "title": "Information Security Policy Breach Verification",
        "status": "PASS" if chk1_pass else "FAIL",
        "points_earned": pts1,
        "max_points": 15,
        "feedback": (
            "Substantiated: Confirmed factual breach of POL-SEC-004 Class 3 transmission to an unauthorized domain."
            if chk1_pass
            else "Policy omission: Failed to identify specific data classification and external transmission breaches."
        ),
    })

    # Check 2: Verbal Approval & Consultant Inquiry
    mitigating = [str(m).lower() for m in matrix.get("mitigatingFactors", [])]
    mitigating_text = " ".join(mitigating)
    chk2_pass = any(w in mitigating_text for w in ["consultant", "rajiv", "rfp", "verbal", "good faith", "belief"])
    pts2 = 15 if chk2_pass else 0
    task_score += pts2
    task_evaluations.append({
        "task_id": "chk-disc-verbal-approval-inquiry",
        "title": "Verbal Approval & Consultant Relationship Inquiry",
        "status": "PASS" if chk2_pass else "FAIL",
        "points_earned": pts2,
        "max_points": 15,
        "feedback": (
            "Contextualized: Investigated consultant onboarding context and employee reliance on alleged verbal guidance."
            if chk2_pass
            else "Unsubstantiated: Ignored the commercial proposal context and consultant involvement."
        ),
    })

    # Check 3: Mitigating Factors & Training Gap
    chk3_pass = any(w in mitigating_text for w in ["training", "module", "unblemished", "record", "clean", "3-year", "remorse", "cooperation"])
    pts3 = 15 if chk3_pass else 0
    task_score += pts3
    task_evaluations.append({
        "task_id": "chk-disc-mitigating-factors",
        "title": "Comprehensive Mitigating Factors Assessment",
        "status": "PASS" if chk3_pass else "FAIL",
        "points_earned": pts3,
        "max_points": 15,
        "feedback": (
            "Balanced: Evaluated 3-year clean performance, absence of malice, and overdue training module as mitigating factors."
            if chk3_pass
            else "Imbalance: Overlooked employee's clean performance history and organizational training tracking lapses."
        ),
    })

    # Check 4: Procedural Fairness & Hearing Notice
    notice_text = (str(notice.get("rightsStatement", "")) + " " + str(notice.get("charges", ""))).lower()
    chk4_pass = any(w in notice_text for w in ["accompanied", "representative", "colleague", "hearing", "rights", "notice", "charges"])
    pts4 = 15 if chk4_pass else 0
    task_score += pts4
    task_evaluations.append({
        "task_id": "chk-disc-procedural-fairness",
        "title": "Procedural Fairness & Due Process Defense",
        "status": "PASS" if chk4_pass else "FAIL",
        "points_earned": pts4,
        "max_points": 15,
        "feedback": (
            "Fair process: Enforced statutory due process, formal written charges, and the right to colleague representation."
            if chk4_pass
            else "Deficient notice: Failed to include formal representation rights or adequate notice period."
        ),
    })

    # Check 5: Proportional Sanction & Remediation
    recs_text = (str(recs.get("recommendedSanction", "")) + " " + str(recs.get("correctiveRemediation", ""))).lower()
    chk5_pass = any(w in recs_text for w in ["warning", "final written", "recertification", "remediation", "dlp", "proportional"]) and not any(t in recs_text for t in ["immediate termination recommended", "terminate immediately", "dismissal without hearing"])
    pts5 = 15 if chk5_pass else 0
    task_score += pts5
    task_evaluations.append({
        "task_id": "chk-disc-proportional-sanction",
        "title": "Proportional Sanction & Remediation Recommendation",
        "status": "PASS" if chk5_pass else "FAIL",
        "points_earned": pts5,
        "max_points": 15,
        "feedback": (
            "Proportional: Recommended graduated disciplinary action (Written Warning + remediation) rather than summary termination."
            if chk5_pass
            else "Disproportionate: Endorsed summary dismissal without proof of malicious intent or gross misconduct."
        ),
    })

    question_evaluations, question_score, max_question_score, any_ai = evaluate_rubric_questions(
        RUBRIC_QUESTIONS, answers, evaluator=None, context="Vertex Digital Solutions: Disciplinary Case & Policy Violation"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))
    passed = normalized_score >= 70

    feedback_summary = (
        f"Disciplinary case evaluation completed with score {normalized_score}%. "
        f"Procedural & forensic assessment score: {task_score}/{max_task_score}. "
        f"Disciplinary standards & fair process score: {question_score}/{max_question_score}. "
        + ("Case demonstrates procedural fairness, proportional sanctioning, and rigorous evidence evaluation."
           if passed else "Review procedural fairness standards under DISC-SOP-002 and proportional sanction criteria.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "deterministic_calibrated",
        "score_breakdown": {
            "disciplinary_process": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "procedural_fairness": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }


async def evaluate_disciplinary_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    task_score = 0
    max_task_score = sum(c["points"] for c in DISCIPLINARY_CHECKS)
    task_evaluations: List[Dict[str, Any]] = []

    case = workspace_snapshot.get("disciplinaryCase", {})
    matrix = workspace_snapshot.get("mitigatingAggravatingMatrix", {})
    notice = workspace_snapshot.get("hearingNoticeDraft", {})
    recs = workspace_snapshot.get("handoverRecommendations", {})

    case_allegation = (str(case.get("allegation", "")) + " " + str(notice.get("charges", ""))).lower()
    chk1_pass = any(w in case_allegation for w in ["pol-sec-004", "class 3", "confidential", "pricing", "gmail", "security", "breach"])
    pts1 = 15 if chk1_pass else 0
    task_score += pts1
    task_evaluations.append({
        "task_id": "chk-disc-policy-breach",
        "title": "Information Security Policy Breach Verification",
        "status": "PASS" if chk1_pass else "FAIL",
        "points_earned": pts1,
        "max_points": 15,
        "feedback": "Substantiated: Confirmed factual breach of POL-SEC-004 Class 3 transmission to an unauthorized domain.",
    })

    mitigating = [str(m).lower() for m in matrix.get("mitigatingFactors", [])]
    mitigating_text = " ".join(mitigating)
    chk2_pass = any(w in mitigating_text for w in ["consultant", "rajiv", "rfp", "verbal", "good faith", "belief"])
    pts2 = 15 if chk2_pass else 0
    task_score += pts2
    task_evaluations.append({
        "task_id": "chk-disc-verbal-approval-inquiry",
        "title": "Verbal Approval & Consultant Relationship Inquiry",
        "status": "PASS" if chk2_pass else "FAIL",
        "points_earned": pts2,
        "max_points": 15,
        "feedback": "Contextualized: Investigated consultant onboarding context and employee reliance on alleged verbal guidance.",
    })

    chk3_pass = any(w in mitigating_text for w in ["training", "module", "unblemished", "record", "clean", "3-year", "remorse", "cooperation"])
    pts3 = 15 if chk3_pass else 0
    task_score += pts3
    task_evaluations.append({
        "task_id": "chk-disc-mitigating-factors",
        "title": "Comprehensive Mitigating Factors Assessment",
        "status": "PASS" if chk3_pass else "FAIL",
        "points_earned": pts3,
        "max_points": 15,
        "feedback": "Balanced: Evaluated 3-year clean performance, absence of malice, and overdue training module as mitigating factors.",
    })

    notice_text = (str(notice.get("rightsStatement", "")) + " " + str(notice.get("charges", ""))).lower()
    chk4_pass = any(w in notice_text for w in ["accompanied", "representative", "colleague", "hearing", "rights", "notice", "charges"])
    pts4 = 15 if chk4_pass else 0
    task_score += pts4
    task_evaluations.append({
        "task_id": "chk-disc-procedural-fairness",
        "title": "Procedural Fairness & Due Process Defense",
        "status": "PASS" if chk4_pass else "FAIL",
        "points_earned": pts4,
        "max_points": 15,
        "feedback": "Fair process: Enforced statutory due process, formal written charges, and the right to colleague representation.",
    })

    recs_text = (str(recs.get("recommendedSanction", "")) + " " + str(recs.get("correctiveRemediation", ""))).lower()
    chk5_pass = any(w in recs_text for w in ["warning", "final written", "recertification", "remediation", "dlp", "proportional"]) and not any(t in recs_text for t in ["immediate termination recommended", "terminate immediately", "dismissal without hearing"])
    pts5 = 15 if chk5_pass else 0
    task_score += pts5
    task_evaluations.append({
        "task_id": "chk-disc-proportional-sanction",
        "title": "Proportional Sanction & Remediation Recommendation",
        "status": "PASS" if chk5_pass else "FAIL",
        "points_earned": pts5,
        "max_points": 15,
        "feedback": "Proportional: Recommended graduated disciplinary action (Written Warning + remediation) rather than summary termination.",
    })

    question_evaluations, question_score, max_question_score, any_ai = await evaluate_rubric_questions_async(
        RUBRIC_QUESTIONS, answers, evaluator=ai_evaluator, context="Vertex Digital Solutions: Disciplinary Case & Policy Violation"
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
            "disciplinary_process": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "procedural_fairness": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": (
            f"Disciplinary case evaluation completed with score {normalized_score}%. "
            f"Procedural score: {task_score}/{max_task_score}. "
            f"Fairness score: {question_score}/{max_question_score}."
        ),
    }
