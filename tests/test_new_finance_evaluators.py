import pytest
from app.evaluators.finance_expenses import evaluate_expense_submission, evaluate_expense_submission_async
from app.evaluators.finance_purchase import evaluate_purchase_submission, evaluate_purchase_submission_async
from app.evaluators.finance_budget import evaluate_budget_submission, evaluate_budget_submission_async
from app.evaluators.finance_payments import evaluate_payments_submission, evaluate_payments_submission_async
from app.evaluators import evaluate_submission, evaluate_submission_async


# =====================================================================
# Scenario 2: Finance — Reviewing Employee Expenses
# =====================================================================

def test_expense_review_evaluator_perfect_score():
    workspace = {
        "claims": [
            {"id": "claim-rahul", "employee": "Rahul Sharma", "expenseType": "Meals", "claimedAmount": 650, "reimbursableAmount": 650, "decision": "Approve Full", "discrepancyType": "None"},
            {"id": "claim-priya", "employee": "Priya Patel", "expenseType": "Local Travel", "claimedAmount": 2000, "reimbursableAmount": 1500, "decision": "Partially Approve", "discrepancyType": "Exceeds Policy Limit"},
            {"id": "claim-aman", "employee": "Aman Verma", "expenseType": "Hotel", "claimedAmount": 3500, "reimbursableAmount": 3500, "decision": "Approve Full", "discrepancyType": "None"},
            {"id": "claim-neha", "employee": "Neha Gupta", "expenseType": "Meals", "claimedAmount": 1200, "reimbursableAmount": 800, "decision": "Partially Approve", "discrepancyType": "Policy Violation / Excluded Item"},
            {"id": "claim-rohan", "employee": "Rohan Mehta", "expenseType": "Office Supplies", "claimedAmount": 4500, "reimbursableAmount": 0, "decision": "Hold / Clarification", "discrepancyType": "Split Transaction"},
            {"id": "claim-kavita", "employee": "Kavita Desai", "expenseType": "Local Travel", "claimedAmount": 1400, "reimbursableAmount": 0, "decision": "Hold / Clarification", "discrepancyType": "Missing Documentation"},
        ]
    }
    answers = {
        "q1DecisionRationales": "Approved Rahul and Aman within policy limits. Partially approved Priya up to cap with exception workflow and Neha deducting non-compliant alcohol. Held Rohan for split transaction and Kavita for missing tax receipt.",
        "q2ExceptionHandling": "Priya exceeded the local travel limit due to client site emergency. Documented business justification and routed the ₹500 balance for manager approval while reimbursing the ₹1,500 standard limit.",
        "q3FraudVsMisunderstanding": "Distinguish intent by analyzing whether employee split transactions deliberately to evade threshold controls versus first-time honest misinterpretation of per diem meal caps.",
        "q4AuditPatterns": "Audit velocity patterns: round-number expenses, weekend submissions, split invoices under approval limits, and repeated merchant charges.",
        "q5ProcessImprovement": "Implement corporate travel cards with automated policy validation, per diem allowances, and an expense submission portal with instant receipt verification.",
        "auditReportDraft": "Executive Expense Audit Summary for Nova Retail Solutions. Total claimed: ₹17,450. Reimbursable: ₹6,450. Flagged ₹11,000 in split transactions and documentation non-compliance.",
    }

    result = evaluate_expense_submission(workspace, answers, {"pasteCount": 0})
    assert result["overall_score"] >= 80
    assert result["passed"] is True
    assert result["score_breakdown"]["claims_audit_score"] >= 85


def test_expense_review_evaluator_penalizes_split_purchase_blind_approval():
    workspace = {
        "claims": [
            # Blindly approving Rohan's split purchase
            {"id": "claim-rohan", "employee": "Rohan Mehta", "expenseType": "Office Supplies", "claimedAmount": 4500, "reimbursableAmount": 4500, "decision": "Approve Full", "discrepancyType": "None"},
        ]
    }
    result = evaluate_expense_submission(workspace, {}, {"pasteCount": 0})
    rohan_eval = next((t for t in result["task_evaluations"] if t["id"] == "claim-rohan"), None)
    assert rohan_eval is not None
    assert rohan_eval["is_correct"] is False


# =====================================================================
# Scenario 3: Finance — Planning a Company Purchase
# =====================================================================

def test_purchase_planning_evaluator_perfect_score():
    workspace = {
        "calculations": {
            "startingCash": 800000,
            "expectedInflows": 400000,
            "mandatoryOutflows": 480000,
            "operatingCashBuffer": 720000,
            "recommendedVendor": "Vendor B (SysTech Enterprise Solutions)",
            "vendorTco": {
                "Vendor A": 1116000,
                "Vendor B": 1120000,
                "Vendor C": 1200000,
            },
            "solvencyRiskAssessment": "High Risk — an upfront purchase of ₹9.36L under Vendor A creates immediate insolvency risk; Net 60 terms under Vendor B protect working capital buffer.",
        }
    }
    answers = {
        "q1VendorTcoComparison": "Recommended Vendor B. Although Vendor A has a lower initial sticker price of ₹9.36L, its basic warranty introduces ₹1.8L in maintenance, bringing TCO to ₹11.16L, whereas Vendor B includes comprehensive 3-year support.",
        "q2WorkingCapitalAffordability": "BrightEdge cannot afford an immediate ₹9.36L cash outlay without risking upcoming non-discretionary commitments: salaries of ₹3,00,000, rent ₹80,000, and month-2 tax liabilities.",
        "q3DeferredPaymentImpact": "Vendor B's Net 60 payment terms allow the company to preserve its ₹7,20,000 operating cash buffer until customer receivables are collected.",
        "q4PhasedRolloutStrategy": "Recommend purchasing 10 laptops in Phase 1 for immediate joiners and 10 in Phase 2 in Month 2, smoothing cash outflow.",
        "q5SensitivityAssumptions": "Verify customer payment collection velocity, actual onboarding dates, foreign exchange sensitivity, and SLA turnaround on warranty replacements.",
        "managementProposalDraft": "Executive Capital Proposal for BrightEdge Technologies. Recommended Vendor B under Net 60 arrangement to ensure cash flow safety while providing full hardware protection.",
    }

    result = evaluate_purchase_submission(workspace, answers, {"pasteCount": 0})
    assert result["overall_score"] >= 80
    assert result["passed"] is True
    assert result["score_breakdown"]["financial_modeling_score"] >= 85


# =====================================================================
# Scenario 4: Finance — Reviewing Department Budgets
# =====================================================================

def test_budget_review_evaluator_perfect_score():
    workspace = {
        "departments": [
            {"id": "dept-marketing", "department": "Marketing", "planned": 200000, "actual": 250000, "varianceAmount": -50000, "varianceType": "Unfavorable"},
            {"id": "dept-technology", "department": "Technology", "planned": 300000, "actual": 280000, "varianceAmount": 20000, "varianceType": "Favorable"},
            {"id": "dept-hr", "department": "HR", "planned": 100000, "actual": 120000, "varianceAmount": -20000, "varianceType": "Unfavorable"},
            {"id": "dept-operations", "department": "Operations", "planned": 250000, "actual": 240000, "varianceAmount": 10000, "varianceType": "Favorable"},
            {"id": "dept-sales", "department": "Sales", "planned": 150000, "actual": 180000, "varianceAmount": -30000, "varianceType": "Unfavorable"},
        ]
    }
    answers = {
        "q1ImmediateAttention": "Marketing and HR require review due to unfavorable variances. Marketing overspent by 25% due to timing lags and expedited ads; HR overspent by 20% on recruiter fees.",
        "q2ActivityVsControlOverspending": "Sales commission variance was directly driven by 140% quota attainment generating ₹6,00,000 in top-line revenue. This is an accretive variable cost, whereas marketing represents unbudgeted timing spillover.",
        "q3InvestigateVsReduce": "Investigate revenue-generating spend such as sales commissions and high-ROI acquisition ads before imposing blanket reductions that stifle growth.",
        "q4QuarterlyForecastAdjustments": "Account for the deferred ₹15,000 database migration in Technology next month and normalize HR recruitment costs to standard baseline.",
        "q5ManagerDisagreementResponse": "Engage collaboratively using objective transaction logs to show variance drivers while working together on post-campaign ROI reviews.",
        "budgetVarianceBriefingDraft": "Executive Budget Briefing for Vertex Solutions. Total variance is -₹70,000 (-7% unfavorable). Sales overage is highly accretive, while Marketing and HR represent one-time timing and recruitment items.",
    }

    result = evaluate_budget_submission(workspace, answers, {"pasteCount": 0})
    assert result["overall_score"] >= 80
    assert result["passed"] is True
    assert result["score_breakdown"]["variance_analysis_score"] >= 85


# =====================================================================
# Scenario 5: Finance — Managing Supplier Payments
# =====================================================================

def test_supplier_payments_evaluator_perfect_score():
    workspace = {
        "payments": [
            {"id": "pay-steelpro", "supplier": "SteelPro", "amountDue": 120000, "decision": "Pay Full", "paymentAmount": 120000},
            {"id": "pay-cloudhost", "supplier": "CloudHost", "amountDue": 40000, "decision": "Pay Full", "paymentAmount": 40000},
            {"id": "pay-machinecare", "supplier": "MachineCare", "amountDue": 90000, "decision": "Pay Full", "paymentAmount": 88200},  # Taking 2% discount
            {"id": "pay-printworks", "supplier": "PrintWorks", "amountDue": 50000, "decision": "Defer", "paymentAmount": 0},
            {"id": "pay-officemart", "supplier": "OfficeMart", "amountDue": 30000, "decision": "Defer", "paymentAmount": 0},
        ]
    }
    answers = {
        "q1PrioritisationCriteria": "Prioritised SteelPro (essential raw materials, line stoppage risk) and CloudHost (hosting shutdown risk) as non-negotiable. MachineCare paid to capture 2% early discount and maintain machinery.",
        "q2SizeVsCriticality": "A smaller ₹40,000 CloudHost invoice must take priority over larger discretionary marketing bills because hosting downtime paralyses the entire business.",
        "q3DiscountsVsCashPreservation": "Captured ₹1,800 discount on MachineCare because adequate treasury cash remained (₹51,800 liquidity buffer) without risking solvency.",
        "q4CashContingencyHandling": "If cash fell to ₹2,20,000, pay SteelPro (₹1.2L) and CloudHost (₹40k) in full, and negotiate a 50% partial payment with MachineCare while freezing all others.",
        "q5SupplierCommunicationStrategy": "Proactively notified PrintWorks and OfficeMart with exact payment dates, maintaining vendor goodwill and credit terms.",
        "supplierDeferralNoticeDraft": "Dear Partner, regarding pending invoice, we are scheduling your payment for our next treasury run on Friday. Thank you for your continued partnership with Orbit Manufacturing.",
    }

    result = evaluate_payments_submission(workspace, answers, {"pasteCount": 0})
    assert result["overall_score"] >= 80
    assert result["passed"] is True
    assert result["score_breakdown"]["payment_allocation_score"] >= 85


def test_supplier_payments_evaluator_catches_budget_overrun():
    workspace = {
        "payments": [
            # Paying everything = ₹3,30,000 (breaches ₹3,00,000 ceiling!)
            {"id": "pay-steelpro", "supplier": "SteelPro", "amountDue": 120000, "decision": "Pay Full", "paymentAmount": 120000},
            {"id": "pay-cloudhost", "supplier": "CloudHost", "amountDue": 40000, "decision": "Pay Full", "paymentAmount": 40000},
            {"id": "pay-machinecare", "supplier": "MachineCare", "amountDue": 90000, "decision": "Pay Full", "paymentAmount": 90000},
            {"id": "pay-printworks", "supplier": "PrintWorks", "amountDue": 50000, "decision": "Pay Full", "paymentAmount": 50000},
            {"id": "pay-officemart", "supplier": "OfficeMart", "amountDue": 30000, "decision": "Pay Full", "paymentAmount": 30000},
        ]
    }
    result = evaluate_payments_submission(workspace, {}, {"pasteCount": 0})
    ceiling_eval = next((t for t in result["task_evaluations"] if t["id"] == "task-cash-ceiling"), None)
    assert ceiling_eval is not None
    assert ceiling_eval["is_correct"] is False
    assert ceiling_eval["points_earned"] == 0


# =====================================================================
# Unified Dispatch by Environment Slug
# =====================================================================

def test_unified_evaluate_submission_dispatches_new_scenarios():
    for slug in [
        "finance-expense-review",
        "finance-purchase-planning",
        "finance-budget-review",
        "finance-supplier-payments",
    ]:
        res = evaluate_submission(
            category="finance",
            workspace_snapshot={},
            answers={},
            integrity_flags={"pasteCount": 0},
            environment_slug=slug,
        )
        assert res is not None
        assert "overall_score" in res
        assert "task_evaluations" in res
        assert "question_evaluations" in res
