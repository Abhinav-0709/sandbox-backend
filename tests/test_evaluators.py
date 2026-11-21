import pytest
from app.evaluators.finance import evaluate_finance_submission
from app.evaluators.hr import evaluate_hr_submission
from app.evaluators.sde import evaluate_sde_submission
from app.evaluators.anti_cheat import detect_ai_markers, evaluate_integrity


def test_anti_cheat_detects_synthetic_markers():
    synthetic_text = (
        "In conclusion, it is crucial to note that fostering innovation plays a pivotal role "
        "in navigating the complexities of modern software architectures. Furthermore, it is essential "
        "to strike a delicate balance between rapid delivery and meticulous attention to detail. "
        "Moreover, it should be noted that this serves as a reminder of our holistic approach."
    )
    res = detect_ai_markers(synthetic_text)
    assert res["is_ai_likely"] is True
    assert len(res["detected_markers"]) >= 2
    assert res["confidence"] in ["Medium", "High"]


def test_anti_cheat_accepts_authentic_human_text():
    human_text = "I checked the PO and the GRN. The warehouse only received 750 cartons so we held 250."
    res = detect_ai_markers(human_text)
    assert res["is_ai_likely"] is False
    assert res["confidence"] == "Clean"


def test_finance_evaluator_perfect_score():
    perfect_invoice_rows = [
        {"invoiceNo": "INV-8821", "decision": "Partially Approve", "verifiedAmount": 37500, "discrepancyType": "Price Mismatch"},
        {"invoiceNo": "INV-8823", "decision": "Approve Full", "verifiedAmount": 14200, "discrepancyType": "None"},
        {"invoiceNo": "INV-8825", "decision": "Partially Approve", "verifiedAmount": 21000, "discrepancyType": "Quantity Mismatch"},
        {"invoiceNo": "INV-8826", "decision": "Hold", "verifiedAmount": 0, "discrepancyType": "Duplicate Submission"},
        {"invoiceNo": "INV-8829", "decision": "Approve Full", "verifiedAmount": 128086, "discrepancyType": "Early Settlement Discount"},
        {"invoiceNo": "INV-8832", "decision": "Hold", "verifiedAmount": 0, "discrepancyType": "Missing PO/Approval"},
    ]
    answers = {
        "q1DecisionsReasoning": "We enforced strict three-way matching across purchase orders, GRN receiving records, and vendor invoices. Vertex had a $5,000 price variance, QuickPrint sent a duplicate invoice, and Zenith lacked director approval.",
        "q2DiscountAnalysis": "Taking the 2% discount saves Aster $2,614 CAD on Sigma Precision Tools, improving cash flow and working capital liquidity.",
        "q3DiscrepancyInformation": "We required a formal credit note from the carrier and proof of delivery from warehouse receiving before releasing held amounts.",
        "q4ControlRecommendations": "Recommended ERP duplicate invoice checks and authorization limit segregation of duties for future purchases.",
        "q5DeadlinePressure": "Maintained strict policy integrity and audit trail compliance despite vendor manager escalation pressure.",
        "supplierEmailDraft": "Dear QuickPrint, Invoice INV-8825 had 250 damaged cartons per GRN. Invoice INV-8826 is a duplicate submission. Please issue a credit note.",
    }

    result = evaluate_finance_submission(
        workspace_snapshot={"invoiceRows": perfect_invoice_rows},
        answers=answers,
        integrity_flags={"pasteCount": 0},
    )

    assert result["passed"] is True
    assert result["overall_score"] >= 85
    assert result["score_breakdown"]["reconciliation_score"] == 100
    assert len(result["task_evaluations"]) == 6
    assert all(t["is_correct"] for t in result["task_evaluations"])


def test_finance_evaluator_catches_unapproved_spending_and_duplicates():
    # Failing scenario: candidate approved duplicate and unapproved invoices
    bad_invoice_rows = [
        {"invoiceNo": "INV-8821", "decision": "Approve Full", "verifiedAmount": 42500, "discrepancyType": "None"},
        {"invoiceNo": "INV-8826", "decision": "Approve Full", "verifiedAmount": 28000, "discrepancyType": "None"},
        {"invoiceNo": "INV-8832", "decision": "Approve Full", "verifiedAmount": 35000, "discrepancyType": "None"},
    ]
    result = evaluate_finance_submission(
        workspace_snapshot={"invoiceRows": bad_invoice_rows},
        answers={},
        integrity_flags={"pasteCount": 0},
    )

    assert result["passed"] is False
    assert result["overall_score"] < 50
    # Duplicate check should have failed
    dup_eval = next(t for t in result["task_evaluations"] if t["invoice_ref"] == "INV-8826")
    assert dup_eval["is_correct"] is False


def test_hr_evaluator_checks_bias_resistance():
    candidate_rows = [
        {"id": "cand-01", "decision": "Reject", "candidateScore": 40, "redFlagsIdentified": "duplicate project demo"},
        {"id": "cand-02", "decision": "Shortlist", "candidateScore": 88, "redFlagsIdentified": ""},
        {"id": "cand-03", "decision": "Reject", "candidateScore": 35, "redFlagsIdentified": "no react"},
        {"id": "cand-04", "decision": "Shortlist", "candidateScore": 85, "redFlagsIdentified": ""},
        {"id": "cand-05", "decision": "Reconsider", "candidateScore": 60, "redFlagsIdentified": "unverified portfolio"},
        {"id": "cand-06", "decision": "Shortlist", "candidateScore": 90, "redFlagsIdentified": ""},
        {"id": "cand-07", "decision": "Reject", "candidateScore": 42, "redFlagsIdentified": "overclaimed skills"},
        {"id": "cand-08", "decision": "Shortlist", "candidateScore": 84, "redFlagsIdentified": ""},
        # cand-09 is the hiring manager's informal bias recommendation
        {"id": "cand-09", "decision": "Reject", "candidateScore": 45, "redFlagsIdentified": "manager informal bias without responsive standards"},
        {"id": "cand-10", "decision": "Reconsider", "candidateScore": 62, "redFlagsIdentified": "minimal team collaboration"},
        {"id": "cand-11", "decision": "Reject", "candidateScore": 45, "redFlagsIdentified": "full-stack overclaim static repo"},
        {"id": "cand-12", "decision": "Reconsider", "candidateScore": 65, "redFlagsIdentified": "borderline async state handling"},
    ]
    answers = {
        "q1ShortlistRanking": "Shortlisted Elena, Aisha, Chloe, and Zoe based on verified React criteria and practical portfolio evidence.",
        "q2ExperienceVsProjects": "Demonstrated code repositories and practical evidence outweigh unverified years of commercial tenure.",
        "q3OverclaimedFullStack": "Identified static boilerplate and lack of backend integration commits in unverified repositories.",
        "q4ManagerBiasResponse": "Resisted informal recommendation for Samira by maintaining objective scoring criteria and fairness benchmarks.",
        "recruitmentSummaryDraft": "Memo to David Sterling: Shortlist rationale grounded in objective benchmarks and job criteria.",
    }

    result = evaluate_hr_submission(
        workspace_snapshot={"candidateRows": candidate_rows},
        answers=answers,
        integrity_flags={"pasteCount": 0},
    )

    assert result["passed"] is True
    assert result["overall_score"] >= 80
    cand_09 = next(c for c in result["task_evaluations"] if c["id"] == "cand-09")
    assert cand_09["is_correct"] is True


def test_sde_evaluator_diagnostics_coverage():
    diagnostics = [
        {"issueId": "issue-1", "primaryLayer": "Architecture / Multi-Layer", "selectedFix": "Add idempotency key and debounce button", "notes": "Race condition caused duplicate tasks"},
        {"issueId": "issue-2", "primaryLayer": "Frontend", "selectedFix": "Rollback optimistic UI on rejection", "notes": "Optimistic state committed before DB transaction"},
        {"issueId": "issue-3", "primaryLayer": "Backend API", "selectedFix": "Whitelist schema DTOs", "notes": "Mass assignment allowed tenant IDOR overwrite"},
    ]
    answers = {
        "q1RootCauses": "Root causes: race condition without idempotency, optimistic state rollback gap, and mass assignment BOLA vulnerability.",
        "q2DuplicatePrevention": "Client debounce plus HTTP Idempotency-Key header verified against database unique constraint.",
        "q3OptimisticUiTradeoffs": "Temporary ID reconciliation and explicit client rollback when server state rejects transaction.",
        "q4OwnershipSecurityRisks": "Strict DTO request body whitelisting and enforcing authenticated user session context.",
        "q5LayerResponsibilities": "Frontend manages transient UX, backend API enforces authorization and idempotency, DB guarantees ACID.",
        "q6TestingStrategy": "Concurrent integration test suite with transaction rollback mocks and negative security payloads.",
    }

    result = evaluate_sde_submission(
        workspace_snapshot={"diagnostics": diagnostics},
        answers=answers,
        integrity_flags={"pasteCount": 0},
    )

    assert result["passed"] is True
    assert result["overall_score"] >= 80
    assert len(result["task_evaluations"]) == 3
    assert all(t["is_correct"] for t in result["task_evaluations"])
