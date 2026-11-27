"""
Evaluator for Scenario 2.3: Finance — Verifying a Supplier Bank Account Change
Organization: Nova Retail Solutions
Role: Finance Operations Associate
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


RED_FLAG_CHECKS = [
    {
        "id": "rf-domain",
        "key": "domainMismatch",
        "title": "Lookalike Domain Spoofing (@apex-office.example)",
        "points": 15,
        "explanation": "Identified lookalike phishing domain with hyphen (@apex-office.example vs verified @apexoffice.example).",
    },
    {
        "id": "rf-phone",
        "key": "phoneMismatch",
        "title": "Unregistered Mobile Telephone (+91 98200 12345)",
        "points": 15,
        "explanation": "Detected that email signature contained an unverified mobile number rather than the registered master landline (+91 22 4912 8800).",
    },
    {
        "id": "rf-entity",
        "key": "entityNameMismatch",
        "title": "Legal Entity Name Mismatch on Bank Letter",
        "points": 10,
        "explanation": "Noticed that the XYZ Bank confirmation letter specified 'Apex Office' instead of legal entity 'Apex Office Supplies Private Limited'.",
    },
    {
        "id": "rf-urgency",
        "key": "manufacturedUrgency",
        "title": "Manufactured False Urgency & Coercive Pressure",
        "points": 10,
        "explanation": "Recognized social engineering tactic threatening delivery stoppages to bypass verification procedures.",
    },
]

RUBRIC_QUESTIONS = [
    {
        "id": "q1",
        "field": "fraudRedFlags",
        "question": "What red flags indicate that this bank account change request might be fraudulent?",
        "keywords": ["domain", "spoof", "hyphen", "phone", "mobile", "landline", "entity name", "bank letter", "urgency", "pressure", "bec"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "outOfBandProtocol",
        "question": "Why must out-of-band callback verification use the contact details on the master record rather than the contact details in the email?",
        "keywords": ["out-of-band", "callback", "master record", "inbound", "phishing", "scammer", "compromise", "bec", "independent"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "handlingPressure",
        "question": "The procurement manager insists on paying the ₹2,40,000 tomorrow into the new account to avoid shipment delays. How do you respond and handle the pressure?",
        "keywords": ["pressure", "procurement", "policy", "safeguard", "hold", "existing account", "risk", "irreversible", "capital"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "requiredDocumentation",
        "question": "What documentation and verification steps are required before a corporate vendor bank account change can be safely approved?",
        "keywords": ["documentation", "bank letter", "director", "signature", "seal", "board resolution", "callback", "verification log"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "preventativeControls",
        "question": "What permanent internal controls and system safeguards should Nova Retail Solutions implement to prevent Business Email Compromise (BEC) and unauthorized vendor bank modifications?",
        "keywords": ["controls", "cooling-off", "separation of duties", "dual control", "penny test", "micro-deposit", "dmarc", "spf", "vendor portal"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
]


def evaluate_bank_change_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    red_flags = workspace_snapshot.get("redFlagsDetected", {})
    action = workspace_snapshot.get("verificationAction", {})

    task_score = 0
    max_task_score = sum(c["points"] for c in RED_FLAG_CHECKS) + 20 + 15
    task_evaluations: List[Dict[str, Any]] = []

    # 1. Red flag detection scoring (50 points)
    for check in RED_FLAG_CHECKS:
        detected = bool(red_flags.get(check["key"], False))
        points_awarded = check["points"] if detected else 0
        task_score += points_awarded

        task_evaluations.append({
            "task_id": check["id"],
            "title": check["title"],
            "status": "PASS" if detected else "FAIL",
            "points_earned": points_awarded,
            "max_points": check["points"],
            "feedback": (
                f"Identified: {check['explanation']}"
                if detected
                else f"Missed Red Flag: Did not flag {check['title']}. {check['explanation']}"
            ),
        })

    # 2. Decision on Change Request (20 points)
    decision = action.get("decision", "")
    decision_correct = decision in ["Reject Request", "Hold for Out-of-Band Callback"]
    decision_points = 20 if decision_correct else 0
    task_score += decision_points
    task_evaluations.append({
        "task_id": "vcb-decision",
        "title": "Vendor Bank Change Request Decision",
        "status": "PASS" if decision_correct else "FAIL",
        "points_earned": decision_points,
        "max_points": 20,
        "feedback": (
            f"Correct action taken: '{decision}'. High-risk modification blocked pending verification."
            if decision_correct
            else f"Unsafe decision: '{decision}'. Under POL-FIN-009, this request must be rejected or held."
        ),
    })

    # 3. Action on Pending Payment of INV-9021 (₹2,40,000) (15 points)
    payment_action = action.get("pendingPaymentAction", "")
    payment_action_correct = payment_action in [
        "Hold Payment Pending Verification",
        "Pay to Verified Existing ABC Bank Account",
    ]
    payment_points = 15 if payment_action_correct else 0
    task_score += payment_points
    task_evaluations.append({
        "task_id": "vcb-payment-action",
        "title": "Action on Pending Invoice INV-9021 (₹2,40,000)",
        "status": "PASS" if payment_action_correct else "FAIL",
        "points_earned": payment_points,
        "max_points": 15,
        "feedback": (
            f"Capital safeguarded: '{payment_action}'. Payment not disbursed to unverified account."
            if payment_action_correct
            else f"Severe Capital Risk: '{payment_action}' risks immediate loss of ₹2,40,000 to fraudsters."
        ),
    })

    # 4. Rubric evaluation
    question_evaluations, question_score, max_question_score, any_ai = evaluate_rubric_questions(
        RUBRIC_QUESTIONS, answers, evaluator=None, context="Nova Retail Solutions: Vendor Bank Account Change Verification"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))

    passed = normalized_score >= 70

    feedback_summary = (
        f"Verification completed with score {normalized_score}%. "
        f"Risk detection & action score: {task_score}/{max_task_score}. "
        f"Qualitative analysis score: {question_score}/{max_question_score}. "
        + ("BEC phishing attack successfully intercepted and capital safeguarded." if passed else "Review fraud detection indicators and vendor governance policy.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "deterministic_calibrated",
        "score_breakdown": {
            "fraud_risk_mitigation": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "qualitative_analysis": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }


async def evaluate_bank_change_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    red_flags = workspace_snapshot.get("redFlagsDetected", {})
    action = workspace_snapshot.get("verificationAction", {})

    task_score = 0
    max_task_score = sum(c["points"] for c in RED_FLAG_CHECKS) + 20 + 15
    task_evaluations: List[Dict[str, Any]] = []

    for check in RED_FLAG_CHECKS:
        detected = bool(red_flags.get(check["key"], False))
        points_awarded = check["points"] if detected else 0
        task_score += points_awarded

        task_evaluations.append({
            "task_id": check["id"],
            "title": check["title"],
            "status": "PASS" if detected else "FAIL",
            "points_earned": points_awarded,
            "max_points": check["points"],
            "feedback": (
                f"Identified: {check['explanation']}"
                if detected
                else f"Missed Red Flag: Did not flag {check['title']}. {check['explanation']}"
            ),
        })

    decision = action.get("decision", "")
    decision_correct = decision in ["Reject Request", "Hold for Out-of-Band Callback"]
    decision_points = 20 if decision_correct else 0
    task_score += decision_points
    task_evaluations.append({
        "task_id": "vcb-decision",
        "title": "Vendor Bank Change Request Decision",
        "status": "PASS" if decision_correct else "FAIL",
        "points_earned": decision_points,
        "max_points": 20,
        "feedback": (
            f"Correct action taken: '{decision}'. High-risk modification blocked pending verification."
            if decision_correct
            else f"Unsafe decision: '{decision}'. Under POL-FIN-009, this request must be rejected or held."
        ),
    })

    payment_action = action.get("pendingPaymentAction", "")
    payment_action_correct = payment_action in [
        "Hold Payment Pending Verification",
        "Pay to Verified Existing ABC Bank Account",
    ]
    payment_points = 15 if payment_action_correct else 0
    task_score += payment_points
    task_evaluations.append({
        "task_id": "vcb-payment-action",
        "title": "Action on Pending Invoice INV-9021 (₹2,40,000)",
        "status": "PASS" if payment_action_correct else "FAIL",
        "points_earned": payment_points,
        "max_points": 15,
        "feedback": (
            f"Capital safeguarded: '{payment_action}'. Payment not disbursed to unverified account."
            if payment_action_correct
            else f"Severe Capital Risk: '{payment_action}' risks immediate loss of ₹2,40,000 to fraudsters."
        ),
    })

    question_evaluations, question_score, max_question_score, any_ai = await evaluate_rubric_questions_async(
        RUBRIC_QUESTIONS, answers, evaluator=ai_evaluator, context="Nova Retail Solutions: Vendor Bank Account Change Verification"
    )

    total_earned = task_score + question_score
    total_possible = max_task_score + max_question_score
    normalized_score = round((total_earned / total_possible) * 100) if total_possible > 0 else 75

    integrity = evaluate_integrity(answers, integrity_flags.get("paste_count", 0))

    passed = normalized_score >= 70

    feedback_summary = (
        f"Verification completed with score {normalized_score}%. "
        f"Risk detection & action score: {task_score}/{max_task_score}. "
        f"Qualitative analysis score: {question_score}/{max_question_score}. "
        + ("BEC phishing attack successfully intercepted and capital safeguarded." if passed else "Review fraud detection indicators and vendor governance policy.")
    )

    return {
        "overall_score": normalized_score,
        "passed": passed,
        "evaluation_method": "ai_calibrated" if ai_evaluator else "deterministic_calibrated",
        "score_breakdown": {
            "fraud_risk_mitigation": round((task_score / max_task_score) * 100) if max_task_score else 0,
            "qualitative_analysis": round((question_score / max_question_score) * 100) if max_question_score else 0,
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity,
        "feedback_summary": feedback_summary,
    }
