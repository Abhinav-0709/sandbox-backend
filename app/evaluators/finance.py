from __future__ import annotations

from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions_async, AiRubricEvaluator


INVOICE_CHECKS = [
    {
        "id": "chk-vertex",
        "invoice_no": "INV-8821",
        "supplier": "Vertex Logistics Group",
        "expected_decision": "Partially Approve",
        "acceptable_decisions": ["Partially Approve"],
        "expected_verified_amount": 37500,
        "expected_financial_impact": 5000,
        "expected_discrepancy_type": "Price Mismatch",
        "points": 15,
        "explanation": "Vertex billed $8,500/container instead of contracted $7,500/container. 5 containers = $37,500 approved, $5,000 variance held.",
    },
    {
        "id": "chk-northerngrid",
        "invoice_no": "INV-8823",
        "supplier": "NorthernGrid Power Corp.",
        "expected_decision": "Approve Full",
        "acceptable_decisions": ["Approve Full"],
        "expected_verified_amount": 14200,
        "expected_financial_impact": 0,
        "expected_discrepancy_type": "None",
        "points": 10,
        "explanation": "Utility invoice matches meter readings and contract tariff. Clean approval for $14,200 CAD.",
    },
    {
        "id": "chk-quickprint-short",
        "invoice_no": "INV-8825",
        "supplier": "QuickPrint Packaging Ltd.",
        "expected_decision": "Partially Approve",
        "acceptable_decisions": ["Partially Approve"],
        "expected_verified_amount": 21000,
        "expected_financial_impact": 7000,
        "expected_discrepancy_type": "Quantity Mismatch",
        "points": 15,
        "explanation": "Billed for 1,000 cartons, but warehouse GRN-4412 confirms only 750 received intact. Approve 750 * $28 = $21,000, hold $7,000.",
    },
    {
        "id": "chk-quickprint-dup",
        "invoice_no": "INV-8826",
        "supplier": "QuickPrint Packaging Ltd.",
        "expected_decision": "Hold",
        "acceptable_decisions": ["Hold"],
        "expected_verified_amount": 0,
        "expected_financial_impact": 28000,
        "expected_discrepancy_type": "Duplicate Submission",
        "points": 15,
        "explanation": "Duplicate invoice identical to INV-8825 submitted 1 day later. Hold full $28,000 to prevent double disbursement.",
    },
    {
        "id": "chk-sigma",
        "invoice_no": "INV-8829",
        "supplier": "Sigma Precision Tools",
        "expected_decision": "Approve Full",
        "acceptable_decisions": ["Approve Full"],
        "expected_verified_amount": 128086,
        "expected_financial_impact": 2614,
        "expected_discrepancy_type": "Early Settlement Discount",
        "points": 20,
        "explanation": "2% early payment discount available if paid within 5 days. $130,700 * 0.98 = $128,086 verified payment with $2,614 savings.",
    },
    {
        "id": "chk-zenith",
        "invoice_no": "INV-8832",
        "supplier": "Zenith Advisory Partners",
        "expected_decision": "Hold",
        "acceptable_decisions": ["Hold"],
        "expected_verified_amount": 0,
        "expected_financial_impact": 35000,
        "expected_discrepancy_type": "Missing PO/Approval",
        "points": 15,
        "explanation": "Unapproved $35,000 consulting invoice without PO or Department Director signature. Hold full amount pending authorization.",
    },
]

QUESTION_RUBRICS = [
    {
        "id": "q1",
        "field": "q1DecisionsReasoning",
        "question": "Q1: Provide audit justification for your payment decisions on Vertex Logistics, QuickPrint Packaging, and Zenith Advisory.",
        "keywords": ["Vertex", "QuickPrint", "Zenith", "three-way", "purchase order", "GRN", "variance", "duplicate", "approval"],
        "required_keywords": 4,
        "min_word_count": 50,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "q2DiscountAnalysis",
        "question": "Q2: Calculate early payment discount savings for Sigma Precision Tools and explain cash flow trade-offs.",
        "keywords": ["2%", "discount", "savings", "2,614", "Sigma", "cash flow", "liquidity", "working capital"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "q3DiscrepancyInformation",
        "question": "Q3: Detail specific evidence and documentation required from suppliers before disputed amounts can be released.",
        "keywords": ["credit note", "revised invoice", "carrier", "proof of delivery", "bill of lading", "warehouse"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "q4ControlRecommendations",
        "question": "Q4: Recommend internal AP controls to prevent duplicate billing and unapproved vendor spending in future batches.",
        "keywords": ["system control", "duplicate check", "ERP", "purchase order", "authorization limit", "segregation of duties"],
        "required_keywords": 3,
        "min_word_count": 40,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "q5DeadlinePressure",
        "question": "Q5: How do you maintain audit rigor when vendor managers pressure AP to release unverified payments?",
        "keywords": ["policy", "integrity", "audit trail", "escalation", "manager", "internal control", "risk"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q_email",
        "field": "supplierEmailDraft",
        "question": "Vendor Communication Draft: Professional email to QuickPrint Packaging regarding damaged goods and duplicate invoice.",
        "keywords": ["QuickPrint", "INV-8825", "INV-8826", "damaged", "250", "credit note", "duplicate", "GRN"],
        "required_keywords": 4,
        "min_word_count": 45,
        "max_score": 15,
    },
]


def evaluate_finance_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    invoice_rows = workspace_snapshot.get("invoiceRows", [])
    task_evaluations: List[Dict[str, Any]] = []
    total_invoice_points = 0
    max_invoice_points = 0

    for rule in INVOICE_CHECKS:
        max_invoice_points += rule["points"]
        row = next((r for r in invoice_rows if r.get("invoiceNo") == rule["invoice_no"]), None)

        if not row:
            task_evaluations.append({
                "id": rule["id"],
                "title": f"{rule['invoice_no']} — {rule['supplier']}",
                "invoice_ref": rule["invoice_no"],
                "expected_decision": rule["expected_decision"],
                "actual_decision": "Missing Row",
                "is_correct": False,
                "points_earned": 0,
                "max_points": rule["points"],
                "explanation": f"Invoice row {rule['invoice_no']} was missing from the submitted reconciliation table.",
            })
            continue

        decision_acceptable = (
            row.get("decision") == rule["expected_decision"]
            or row.get("decision") in rule.get("acceptable_decisions", [])
        )
        verified_amount = float(row.get("verifiedAmount") or 0)
        amount_correct = abs(verified_amount - rule["expected_verified_amount"]) <= 100
        discrepancy_noticed = (
            row.get("discrepancyType") == "None"
            if rule["expected_discrepancy_type"] == "None"
            else row.get("discrepancyType") == rule["expected_discrepancy_type"]
        )

        if decision_acceptable and amount_correct:
            points = rule["points"]
        elif decision_acceptable or amount_correct or discrepancy_noticed:
            points = round(rule["points"] * 0.5)
        else:
            points = 0

        total_invoice_points += points

        task_evaluations.append({
            "id": rule["id"],
            "title": f"{rule['invoice_no']} — {rule['supplier']}",
            "invoice_ref": rule["invoice_no"],
            "expected_decision": rule["expected_decision"],
            "actual_decision": row.get("decision", "None"),
            "is_correct": points >= rule["points"] * 0.8,
            "points_earned": points,
            "max_points": rule["points"],
            "explanation": (
                f"Correct! Decision ({row.get('decision')}) and verified amount (${verified_amount:,.2f} CAD) matched audit criteria. {rule['explanation']}"
                if points == rule["points"]
                else f"Audit Variance: Expected {rule['expected_decision']} at ${rule['expected_verified_amount']:,.2f} CAD. Actual was {row.get('decision')} at ${verified_amount:,.2f} CAD."
            ),
        })

    # Evaluate question rubrics
    question_evaluations: List[Dict[str, Any]] = []
    total_question_points = 0
    max_question_points = 0

    for rubric in QUESTION_RUBRICS:
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

        feedback = (
            "Excellent answer. Addressed core financial principles and sound professional reasoning."
            if score >= rubric["max_score"]
            else f"Good attempt. Consider incorporating key concepts: {', '.join(missing[:3])}."
            if score > 4
            else "Under-developed response. Needs thorough evidence and procedural justification."
        )

        question_evaluations.append({
            "id": rubric["id"],
            "question": rubric["question"],
            "answer_length": word_count,
            "matched_keywords": matched,
            "missing_keywords": missing[:4],
            "score": score,
            "max_score": rubric["max_score"],
            "feedback": feedback,
        })

    return _build_finance_evaluation_result(
        task_evaluations=task_evaluations,
        question_evaluations=question_evaluations,
        total_invoice_points=total_invoice_points,
        max_invoice_points=max_invoice_points,
        total_question_points=total_question_points,
        max_question_points=max_question_points,
        answers=answers,
        integrity_flags=integrity_flags,
        evaluation_method="deterministic",
    )


async def evaluate_finance_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    """
    Asynchronously evaluates a Finance AP simulation submission with AI-assisted
    qualitative scoring and automatic fallback.
    """
    invoice_rows: List[Dict[str, Any]] = workspace_snapshot.get("rows", [])
    task_evaluations: List[Dict[str, Any]] = []
    total_invoice_points = 0
    max_invoice_points = 0

    for rule in INVOICE_CHECKS:
        max_invoice_points += rule["points"]
        row = next((r for r in invoice_rows if r.get("invoiceNo") == rule["invoice_no"]), None)

        if not row:
            task_evaluations.append({
                "id": rule["id"],
                "title": f"{rule['invoice_no']} — {rule['supplier']}",
                "invoice_ref": rule["invoice_no"],
                "expected_decision": rule["expected_decision"],
                "actual_decision": "Missing Row",
                "is_correct": False,
                "points_earned": 0,
                "max_points": rule["points"],
                "explanation": f"Invoice row {rule['invoice_no']} was missing from the submitted reconciliation table.",
            })
            continue

        decision_acceptable = (
            row.get("decision") == rule["expected_decision"]
            or row.get("decision") in rule.get("acceptable_decisions", [])
        )
        verified_amount = float(row.get("verifiedAmount") or 0)
        amount_correct = abs(verified_amount - rule["expected_verified_amount"]) <= 100
        discrepancy_noticed = (
            row.get("discrepancyType") == "None"
            if rule["expected_discrepancy_type"] == "None"
            else row.get("discrepancyType") == rule["expected_discrepancy_type"]
        )

        if decision_acceptable and amount_correct:
            points = rule["points"]
        elif decision_acceptable or amount_correct or discrepancy_noticed:
            points = round(rule["points"] * 0.5)
        else:
            points = 0

        total_invoice_points += points

        task_evaluations.append({
            "id": rule["id"],
            "title": f"{rule['invoice_no']} — {rule['supplier']}",
            "invoice_ref": rule["invoice_no"],
            "expected_decision": rule["expected_decision"],
            "actual_decision": row.get("decision", "None"),
            "is_correct": points >= rule["points"] * 0.8,
            "points_earned": points,
            "max_points": rule["points"],
            "explanation": (
                f"Correct! Decision ({row.get('decision')}) and verified amount (${verified_amount:,.2f} CAD) matched audit criteria. {rule['explanation']}"
                if points == rule["points"]
                else f"Audit Variance: Expected {rule['expected_decision']} at ${rule['expected_verified_amount']:,.2f} CAD. Actual was {row.get('decision')} at ${verified_amount:,.2f} CAD."
            ),
        })

    # Concurrently evaluate questions with AI
    question_evaluations, total_q_pts, max_q_pts, any_ai = await evaluate_rubric_questions_async(
        rubrics=QUESTION_RUBRICS,
        answers=answers,
        evaluator=ai_evaluator,
        context="Vivoki Accounts Payable Simulation: 3-way reconciliation audit, early discount trade-offs, internal control weaknesses, vendor dispute resolution.",
    )

    return _build_finance_evaluation_result(
        task_evaluations=task_evaluations,
        question_evaluations=question_evaluations,
        total_invoice_points=total_invoice_points,
        max_invoice_points=max_invoice_points,
        total_question_points=total_q_pts,
        max_question_points=max_q_pts,
        answers=answers,
        integrity_flags=integrity_flags,
        evaluation_method="hybrid_ai" if any_ai else "deterministic",
    )


def _build_finance_evaluation_result(
    task_evaluations: List[Dict[str, Any]],
    question_evaluations: List[Dict[str, Any]],
    total_invoice_points: int,
    max_invoice_points: int,
    total_question_points: int,
    max_question_points: int,
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    evaluation_method: str = "deterministic",
) -> Dict[str, Any]:
    # Anti-cheat evaluation
    paste_count = int(integrity_flags.get("pasteCount", 0))
    integrity_audit = evaluate_integrity(answers, paste_count=paste_count)

    # Competency pillar scores
    reconciliation_score = round((total_invoice_points / max_invoice_points) * 100) if max_invoice_points else 0

    sigma_res = next((t for t in task_evaluations if t["invoice_ref"] == "INV-8829"), None)
    q2_res = next((q for q in question_evaluations if q["id"] == "q2"), None)
    discount_score = round(
        (((sigma_res["points_earned"] / sigma_res["max_points"]) if sigma_res else 0)
        + ((q2_res["score"] / q2_res["max_score"]) if q2_res else 0)) / 2 * 100
    )

    qp_dup_res = next((t for t in task_evaluations if t["invoice_ref"] == "INV-8826"), None)
    zenith_res = next((t for t in task_evaluations if t["invoice_ref"] == "INV-8832"), None)
    q4_res = next((q for q in question_evaluations if q["id"] == "q4"), None)
    controls_score = round(
        (((qp_dup_res["points_earned"] / qp_dup_res["max_points"]) if qp_dup_res else 0)
        + ((zenith_res["points_earned"] / zenith_res["max_points"]) if zenith_res else 0)
        + ((q4_res["score"] / q4_res["max_score"]) if q4_res else 0)) / 3 * 100
    )

    email_res = next((q for q in question_evaluations if q["id"] == "q_email"), None)
    q1_res = next((q for q in question_evaluations if q["id"] == "q1"), None)
    communication_score = round(
        (((email_res["score"] / email_res["max_score"]) if email_res else 0)
        + ((q1_res["score"] / q1_res["max_score"]) if q1_res else 0)) / 2 * 100
    )

    vertex_res = next((t for t in task_evaluations if t["invoice_ref"] == "INV-8821"), None)
    q5_res = next((q for q in question_evaluations if q["id"] == "q5"), None)
    raw_integrity = round(
        (((vertex_res["points_earned"] / vertex_res["max_points"]) if vertex_res else 0)
        + ((q5_res["score"] / q5_res["max_score"]) if q5_res else 0)) / 2 * 100
    )
    if integrity_audit["is_ai_flagged"]:
        raw_integrity = max(20, raw_integrity - integrity_audit["deduction_applied"])

    total_points = total_invoice_points + total_question_points
    max_points = max_invoice_points + max_question_points
    overall_score = round((total_points / max_points) * 100) if max_points else 0
    if integrity_audit["is_ai_flagged"]:
        overall_score = max(0, overall_score - 10)

    passed = overall_score >= 70 and not integrity_audit["is_ai_flagged"]

    return {
        "overall_score": overall_score,
        "passed": passed,
        "evaluation_method": evaluation_method,
        "score_breakdown": {
            "reconciliation_score": reconciliation_score,
            "discount_score": discount_score,
            "controls_score": controls_score,
            "communication_score": communication_score,
            "integrity_score": raw_integrity,
            "total_points": total_points,
            "max_points": max_points,
            "ai_assisted": evaluation_method == "hybrid_ai",
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity_audit,
        "feedback_summary": (
            "Congratulations! You demonstrated rigorous three-way matching, accurate discount calculation, and strong internal control adherence."
            if passed
            else "Assessment did not meet passing threshold. Review discrepancy identification and audit documentation requirements."
        ),
    }
