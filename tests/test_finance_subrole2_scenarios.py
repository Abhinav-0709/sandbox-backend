import pytest
from app.evaluators import evaluate_submission, evaluate_submission_async
from app.evaluators.finance_duplicate_payment import (
    evaluate_duplicate_payment_submission,
    evaluate_duplicate_payment_submission_async,
)
from app.evaluators.finance_bank_change import (
    evaluate_bank_change_submission,
    evaluate_bank_change_submission_async,
)


def test_duplicate_payment_evaluator_pass():
    workspace = {
        "payments": [
            {"id": "pay-001", "auditDecision": "Confirmed Duplicate", "reconciledAmount": 118000},
            {"id": "pay-002", "auditDecision": "Confirmed Duplicate", "reconciledAmount": 0},
            {"id": "pay-003", "auditDecision": "Valid Payment", "reconciledAmount": 76000},
            {"id": "pay-004", "auditDecision": "Valid Payment", "reconciledAmount": 42000},
        ],
        "recoveryRecommendation": "Refund",
    }
    answers = {
        "verificationMethod": "We conducted a 3-way reconciliation comparing the internal payment ledger with the HDFC bank statement UTR clearing numbers CMS-HDFC-994102 and CMS-HDFC-995481. We verified against the supplier statement of account which confirms only one invoice INV-7841 for 1,18,000 exists, leaving an unallocated credit balance.",
        "conflictingRecords": "The bank statement reflects actual cash reality and must be relied upon as the authoritative financial record. The internal status of failed was caused by a gateway communication timeout HTTP 504. We verified settlement directly on the bank portal.",
        "supplierProposal": "Under AP SOP 014, duplicate payments over 50,000 must be recovered via electronic refund within 5 days to preserve corporate cash flow. If netting is agreed commercially, a formal signed credit memo and recurring purchase volume must be documented.",
        "internalControls": "Introduce automated reverse API status inquiries before allowing any batch retries, implement unique idempotency keys on payment transactions, and require dual treasury sign-off with mandatory bank portal checks.",
        "disputeEvidence": "Present the certified HDFC bank statement showing debit timestamps, UTR references CMS-HDFC-994102 and CMS-HDFC-995481, invoice INV-7841, and Apex's own statement of account reflecting the unapplied credit balance.",
    }
    result = evaluate_duplicate_payment_submission(workspace, answers, {})
    assert result["passed"] is True
    assert result["overall_score"] >= 75
    assert len(result["task_evaluations"]) == 4


def test_bank_change_evaluator_pass():
    workspace = {
        "redFlagsDetected": {
            "domainMismatch": True,
            "phoneMismatch": True,
            "entityNameMismatch": True,
            "manufacturedUrgency": True,
        },
        "verificationAction": {
            "decision": "Reject Request",
            "pendingPaymentAction": "Hold Payment Pending Verification",
            "callbackConducted": True,
            "callbackNumberUsed": "+91 22 4912 8800 (Master Record Landline)",
            "contactSpokenWith": "Rajesh Nair (Director of Finance)",
            "callbackOutcome": "Fraud Confirmed: Apex never requested bank change; ABC Bank account remains active.",
        },
    }
    answers = {
        "fraudRedFlags": "Four key red flags were detected: (1) lookalike domain spoofing with a hyphen @apex-office.example instead of @apexoffice.example, (2) an unverified personal mobile phone number in the signature, (3) legal entity name mismatch on the XYZ Bank letter stating Apex Office instead of Apex Office Supplies Private Limited, and (4) false urgency threatening shipment stoppage.",
        "outOfBandProtocol": "Out-of-band callback verification must strictly use the pre-authenticated contact numbers from the verified vendor master record. Calling the number provided in the phishing email connects directly to the fraudster. Independent verification breaks the BEC attack chain.",
        "handlingPressure": "Under company policy POL-FIN-009, payments to unverified accounts cannot be disbursed regardless of operational pressure. Electronic transfers to fraudulent accounts are irreversible. I would explain the severe fraud risk to the procurement manager and offer to disburse to the verified existing ABC Bank account or hold the invoice until verified.",
        "requiredDocumentation": "A bona fide vendor bank change requires a formal request on company letterhead signed by authorized director Rajesh Nair, a certified bank reference letter with branch seal and IFSC code, a board resolution where applicable, and a documented telephone callback verification log.",
        "preventativeControls": "Implement mandatory 14-day cooling-off holding periods for any newly added vendor bank accounts, enforce dual-control authorization in the ERP, conduct penny test micro-deposits, and configure technical email defenses like SPF, DKIM, and DMARC.",
    }
    result = evaluate_bank_change_submission(workspace, answers, {})
    assert result["passed"] is True
    assert result["overall_score"] >= 75
    assert len(result["task_evaluations"]) == 6


def test_dispatch_via_evaluate_submission():
    # Test dispatcher for duplicate payment
    dup_res = evaluate_submission(
        category="finance",
        workspace_snapshot={
            "payments": [
                {"id": "pay-001", "auditDecision": "Confirmed Duplicate", "reconciledAmount": 118000},
                {"id": "pay-002", "auditDecision": "Confirmed Duplicate", "reconciledAmount": 0},
                {"id": "pay-003", "auditDecision": "Valid Payment", "reconciledAmount": 76000},
                {"id": "pay-004", "auditDecision": "Valid Payment", "reconciledAmount": 42000},
            ],
            "recoveryRecommendation": "Refund",
        },
        answers={"verificationMethod": "test answer with enough words for the validation check to verify keywords and criteria"},
        integrity_flags={},
        environment_slug="finance-duplicate-payment",
    )
    assert "disbursement_reconciliation" in dup_res["score_breakdown"]

    # Test dispatcher for bank change
    vcb_res = evaluate_submission(
        category="finance",
        workspace_snapshot={
            "redFlagsDetected": {
                "domainMismatch": True,
                "phoneMismatch": True,
                "entityNameMismatch": True,
                "manufacturedUrgency": True,
            },
            "verificationAction": {
                "decision": "Reject Request",
                "pendingPaymentAction": "Hold Payment Pending Verification",
            },
        },
        answers={"fraudRedFlags": "test answer with enough words for the validation check to verify keywords and criteria"},
        integrity_flags={},
        environment_slug="finance-bank-change-verification",
    )
    assert "fraud_risk_mitigation" in vcb_res["score_breakdown"]
