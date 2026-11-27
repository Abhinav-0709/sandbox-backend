import pytest
from app.evaluators import evaluate_submission
from app.evaluators.finance_business_performance import evaluate_business_performance_submission
from app.evaluators.finance_cash_flow_forecast import evaluate_cash_flow_submission


def test_business_performance_evaluator_pass():
    workspace = {
        "metrics": [
            {"id": "m-rev", "metric": "Revenue", "marchActual": 4800000, "aprilBudget": 5500000, "aprilActual": 5100000, "varBudgetAbs": -400000, "varBudgetPct": -7.27, "varMarchAbs": 300000, "varMarchPct": 6.25},
            {"id": "m-cogs", "metric": "Cost of Goods Sold (COGS)", "marchActual": 2700000, "aprilBudget": 3000000, "aprilActual": 3150000, "varBudgetAbs": 150000, "varBudgetPct": 5.00, "varMarchAbs": 450000, "varMarchPct": 16.67},
            {"id": "m-emp", "metric": "Employee Expenses", "marchActual": 800000, "aprilBudget": 850000, "aprilActual": 920000, "varBudgetAbs": 70000, "varBudgetPct": 8.24, "varMarchAbs": 120000, "varMarchPct": 15.00},
            {"id": "m-mkt", "metric": "Marketing Expenses", "marchActual": 300000, "aprilBudget": 400000, "aprilActual": 520000, "varBudgetAbs": 120000, "varBudgetPct": 30.00, "varMarchAbs": 220000, "varMarchPct": 73.33},
            {"id": "m-oth", "metric": "Other Operating Expenses", "marchActual": 400000, "aprilBudget": 450000, "aprilActual": 480000, "varBudgetAbs": 30000, "varBudgetPct": 6.67, "varMarchAbs": 80000, "varMarchPct": 20.00},
        ],
        "profitabilitySummary": {
            "grossProfitActual": 1950000,
            "grossMarginActualPct": 38.24,
            "operatingProfitActual": 30000,
            "operatingMarginActualPct": 0.59,
        },
        "oneTimeCostsIdentified": {
            "marketingAgencySetup": True,
            "storeHvacRepair": True,
        },
    }
    answers = {
        "revenueTargetGap": "Revenue grew by +3,00,000 or +6.25% month-on-month compared to March, but failed to reach the ambitious budget of 55,00,000, missing by -4,00,000. The shortfall was driven primarily by Apparel (-3,00,000) due to summer shipment delays and Footwear (-1,80,000) due to warehouse stockouts in core sizes.",
        "expensePriority": "Management should investigate COGS first. COGS expanded by +1,50,000 against budget and +4,50,000 or +16.67% over March, compressing gross margin from 45.45% down to 38.24%. This structural inflation in packaging and freight erodes profitability on every transaction across the business.",
        "marketingEffectiveness": "We cannot immediately conclude marketing was ineffective. Marketing included an 80,000 one-time setup retainer for the summer campaign that began late in April. Customer acquisition and promotional conversion pipelines exhibit a natural timing lag that will monetize in May and June.",
        "oneTimeVsRecurring": "Distinguish one-time expenses by reviewing underlying vendor contracts and maintenance logs. The 80,000 agency fee and 25,000 HVAC compressor repair are non-recurring isolated events. Normalizing these costs increases ongoing run-rate operating profit from 30,000 to 1,35,000.",
        "costReductionStrategy": "To reduce opex by 10%, audit discretionary expenses first rather than cutting core commercial operations. Eliminate warehouse overtime by re-aligning staff shifts, renegotiate shipping freight tariffs, and preserve revenue-generating digital marketing channels to prevent damaging top-line sales.",
    }
    result = evaluate_business_performance_submission(workspace, answers, {})
    assert result["passed"] is True
    assert result["overall_score"] >= 75
    assert len(result["task_evaluations"]) == 6


def test_cash_flow_forecast_evaluator_pass():
    workspace = {
        "openingCashBalance": 1200000,
        "stressFactors": {
            "zenithMartDelayApplied": True,
            "zenithDisputedAmount": 200000,
            "unbudgetedInventoryIncluded": True,
        },
        "mitigationPlan": {
            "supplierTermsNegotiated": True,
            "supplierExtensionAmount": 400000,
            "inventoryDeliveryPhased": True,
            "inventoryPhase1June": 250000,
            "inventoryPhase2July": 350000,
            "mitigatedJuneClosingCash": 400000,
        },
    }
    answers = {
        "profitableYetIlliquid": "A profitable business can experience severe cash shortages because accounting profit is recorded on an accrual basis when revenue is billed, whereas cash depends on actual collections. Rapid sales expansion ties up cash in customer receivables and inventory before payments are received.",
        "latePayingCustomer": "For a customer like Zenith Mart with a history of delinquent payments and active invoice disputes, the forecast must discount prompt payment. We shift the expected 6,00,000 inflow from June into July and prepare a cautious stress-scenario to evaluate liquidity downside.",
        "paymentPriorityTradeoffs": "Employee salaries represent statutory and non-negotiable obligations that cause severe legal breach and morale damage if delayed. In contrast, supplier payables can be commercially negotiated for 30-day extensions on non-critical materials without jeopardizing business continuity.",
        "dualScenarioUtility": "Dual scenario modeling provides essential sensitivity analysis. The expected-case provides operational guidance, while the conservative stress forecast establishes downside liquidity thresholds, contingency triggers, and working capital buffers needed to avoid insolvency.",
        "deficitEscalationProtocol": "Before presenting solutions, provide management with the exact timing of the cash trough (-50,000 in June), breakdown of unavoidable disbursements versus deferrable payables, aged receivables status, and concrete proposals such as inventory phasing and supplier term extensions.",
    }
    result = evaluate_cash_flow_submission(workspace, answers, {})
    assert result["passed"] is True
    assert result["overall_score"] >= 75
    assert len(result["task_evaluations"]) == 5


def test_subrole3_dispatcher():
    # Dispatch business performance
    perf_res = evaluate_submission(
        category="finance",
        workspace_snapshot={
            "oneTimeCostsIdentified": {"marketingAgencySetup": True, "storeHvacRepair": True}
        },
        answers={"revenueTargetGap": "valid answer here with sufficient words to pass length checks"},
        integrity_flags={},
        environment_slug="finance-business-performance",
    )
    assert "pnl_variance_analysis" in perf_res["score_breakdown"]

    # Dispatch cash flow forecast
    cf_res = evaluate_submission(
        category="finance",
        workspace_snapshot={
            "openingCashBalance": 1200000,
            "stressFactors": {"zenithMartDelayApplied": True},
        },
        answers={"profitableYetIlliquid": "valid answer here with sufficient words to pass length checks"},
        integrity_flags={},
        environment_slug="finance-cash-flow-forecast",
    )
    assert "cash_flow_modeling" in cf_res["score_breakdown"]
