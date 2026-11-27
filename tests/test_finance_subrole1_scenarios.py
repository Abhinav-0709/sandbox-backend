"""
Unit tests for Finance Subrole 1 (Accounts Payable Specialist) scenarios:
1. Scenario 1.2: Finance — Reconciling Supplier Statements (finance-statement-reconciliation)
2. Scenario 1.3: Finance — Managing Invoice Processing and Month-End Cut-Off (finance-invoice-cutoff)
"""

import pytest
from app.evaluators import evaluate_submission


def test_statement_reconciliation_perfect_submission():
    workspace_snapshot = {
        "reconciliationSchedule": {
            "supplierStatementBalance": 385000,
            "paymentInTransitAmount": 50000,
            "adjustedSupplierBalance": 335000,
            "companyLedgerBalance": 295000,
            "missingInvoiceAmount": 60000,
            "unappliedCreditNoteAmount": 10000,
            "transpositionErrorCorrection": 10000,
            "adjustedCompanyBalance": 335000,
            "varianceResolved": True,
        },
        "adjustmentsIdentified": {
            "paymentInTransit": True,
            "missingInvoiceInv2080": True,
            "unappliedCreditNoteCn104": True,
            "transpositionInv2072": True,
        },
        "supplierEmailDraft": {
            "subject": "Nova Retail Solutions — Account Reconciliation & Payment Confirmation (SUP-1042)",
            "body": "Reconciliation completed with adjusted balance of ₹3,35,000.",
        },
    }

    answers = {
        "timingVsPermanentDifferences": (
            "A supplier statement might show a different outstanding balance due to timing differences "
            "such as payments in transit and invoices issued after the cut-off date, as well as permanent "
            "errors including transposition keying mistakes, unapplied credit notes, or pricing discrepancies."
        ),
        "unrecordedCreditNoteEffect": (
            "If a credit note has been received but not recorded, it causes the company's accounts payable "
            "liability to be artificially overstated in the sub-ledger, distorting working capital ratios and "
            "creating a material risk of duplicate cash outflow or overpayment to the vendor."
        ),
        "paymentInTransitVerification": (
            "Before treating the payment in transit as resolved, accounts payable must verify the cleared "
            "bank debit date on the company statement, obtain the official NEFT/RTGS UTR reference number, "
            "confirm payee beneficiary account numbers, and compare with the supplier statement cut-off timestamp."
        ),
        "unsupportedInvoiceHandling": (
            "Under 3-way matching internal controls, if an invoice appears without a corresponding goods "
            "receipt note, it must be placed on administrative hold immediately. AP must investigate warehouse "
            "receiving dock logs to verify whether goods are in-transit and notify procurement before paying."
        ),
        "reconciliationDocumentation": (
            "Unresolved differences must be formally documented on a reconciliation schedule rather than "
            "forced or plugged to maintain an auditable trail, satisfy internal financial controls, prevent "
            "unauthorized fraud, and protect statutory accounting compliance."
        ),
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="finance",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="finance-statement-reconciliation",
    )

    assert result["passed"] is True
    assert result["overall_score"] >= 85
    assert result["score_breakdown"]["reconciliation_accuracy"] == 100
    assert len(result["task_evaluations"]) == 5
    for task in result["task_evaluations"]:
        assert task["status"] == "PASS"


def test_statement_reconciliation_missing_adjustments():
    workspace_snapshot = {
        "reconciliationSchedule": {
            "supplierStatementBalance": 385000,
            "adjustedSupplierBalance": 385000,
            "companyLedgerBalance": 295000,
            "adjustedCompanyBalance": 295000,
            "varianceResolved": False,
        },
        "adjustmentsIdentified": {
            "paymentInTransit": False,
            "missingInvoiceInv2080": False,
            "unappliedCreditNoteCn104": False,
            "transpositionInv2072": False,
        },
    }

    answers = {
        "timingVsPermanentDifferences": "Not sure why balances differ.",
        "unrecordedCreditNoteEffect": "It does not matter much.",
        "paymentInTransitVerification": "Wait for next month.",
        "unsupportedInvoiceHandling": "Pay it anyway.",
        "reconciliationDocumentation": "Just adjust the numbers.",
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="finance",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="finance-statement-reconciliation",
    )

    assert result["passed"] is False
    assert result["score_breakdown"]["reconciliation_accuracy"] == 0


def test_invoice_cutoff_perfect_submission():
    workspace_snapshot = {
        "invoices": [
            {
                "id": "inv-3101",
                "supplier": "Apex Office Supplies",
                "ref": "INV-3101",
                "amount": 48000,
                "status": "Hold (Missing GRN)",
                "juneExpenseAmount": 0,
                "prepaidAmount": 0,
            },
            {
                "id": "inv-3102",
                "supplier": "Bright Logistics",
                "ref": "INV-3102",
                "amount": 72000,
                "status": "Ready to Post",
                "juneExpenseAmount": 72000,
                "prepaidAmount": 0,
            },
            {
                "id": "inv-3103",
                "supplier": "CloudServe Technologies",
                "ref": "INV-3103",
                "amount": 120000,
                "status": "Split Prepayment",
                "juneExpenseAmount": 40000,
                "prepaidAmount": 80000,
            },
            {
                "id": "inv-3104",
                "supplier": "Metro Utilities",
                "ref": "INV-3104",
                "amount": 35000,
                "costCentre": "401 (Facilities & Utilities)",
                "status": "Ready to Post",
                "juneExpenseAmount": 35000,
                "prepaidAmount": 0,
            },
            {
                "id": "inv-3105",
                "supplier": "Secure Facility Services",
                "ref": "INV-3105",
                "amount": 60000,
                "status": "Ready to Post",
                "juneExpenseAmount": 60000,
                "prepaidAmount": 0,
            },
        ],
        "unbilledAccruals": [
            {
                "id": "acc-elec",
                "expenseType": "Electricity Power Tariff",
                "meterReadingKwh": 4200,
                "tariffRatePerKwh": 10.0,
                "estimatedAccrualAmount": 42000,
                "costCentre": "401 (Facilities & Utilities)",
            },
        ],
    }

    answers = {
        "invoiceDateVsCutoff": (
            "The invoice date alone is insufficient because accounting requires recognizing expenses in "
            "the period the goods or services were consumed, adhering to the accrual matching principle. "
            "Supplier billing dates frequently lag physical delivery or cross cut-off accounting dates."
        ),
        "delayedInvoiceAccrualWorkflow": (
            "When services are finished in June but the invoice arrives in July, accounts payable coordinates "
            "with general ledger accounting to book an unbilled accrual in June supported by service completion "
            "reports, and subsequently matches and clears the accrual when the invoice is entered in July."
        ),
        "missingGrnAction": (
            "If an invoice has a valid PO but lacks a goods receipt record, accounts payable must place the "
            "invoice on administrative hold under 3-way matching rules, investigate receiving dock logs to check "
            "in-transit status, and refuse payment disbursement until physical delivery is formally certified."
        ),
        "costCentreImportance": (
            "Accurate cost centre allocation is vital for departmental budget accountability, variance tracking, "
            "and avoiding misleading management P&L reporting that distorts departmental operational cost visibility."
        ),
        "multiPeriodPrepaymentAccounting": (
            "An invoice spanning June, July, and August represents future economic benefits. Posting all ₹1,20,000 "
            "to June artificially depresses current period profitability and understates expenses in subsequent months. "
            "It must be apportioned between current expense and prepaid assets under the matching principle."
        ),
        "missingUtilityAccrualEstimation": (
            "To handle a missing utility invoice objectively without guesswork, finance inspects verified physical "
            "meter logs (e.g. 4,200 kWh consumed) and multiplies by the contracted utility tariff rate (₹10/kWh) "
            "to establish an auditable, reliable month-end accrual."
        ),
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="finance",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="finance-invoice-cutoff",
    )

    assert result["passed"] is True
    assert result["overall_score"] >= 85
    assert result["score_breakdown"]["cutoff_execution"] == 100
    assert len(result["task_evaluations"]) == 6
    for task in result["task_evaluations"]:
        assert task["status"] == "PASS"


def test_invoice_cutoff_violations():
    # Apex premature post without GRN, Metro wrong cost centre, CloudServe full post
    workspace_snapshot = {
        "invoices": [
            {
                "id": "inv-3101",
                "supplier": "Apex Office Supplies",
                "status": "Ready to Post",
                "juneExpenseAmount": 48000,
                "amount": 48000,
            },
            {
                "id": "inv-3102",
                "supplier": "Bright Logistics",
                "status": "Hold",
                "juneExpenseAmount": 0,
            },
            {
                "id": "inv-3103",
                "supplier": "CloudServe Technologies",
                "status": "Ready to Post",
                "juneExpenseAmount": 120000,
                "prepaidAmount": 0,
            },
            {
                "id": "inv-3104",
                "supplier": "Metro Utilities",
                "costCentre": "201 (Marketing)",
                "status": "Ready to Post",
                "juneExpenseAmount": 35000,
            },
        ],
        "unbilledAccruals": [],
    }

    answers = {
        "invoiceDateVsCutoff": "short answer",
        "delayedInvoiceAccrualWorkflow": "short answer",
        "missingGrnAction": "short answer",
        "costCentreImportance": "short answer",
        "multiPeriodPrepaymentAccounting": "short answer",
        "missingUtilityAccrualEstimation": "short answer",
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="finance",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="finance-invoice-cutoff",
    )

    assert result["passed"] is False
    assert result["score_breakdown"]["cutoff_execution"] < 50
