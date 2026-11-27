"""
Unit tests for HR Subrole 2 (HR Operations Associate) scenarios:
1. Scenario 2.1: HR — Managing Employee Onboarding and Documentation (hr-employee-onboarding)
2. Scenario 2.2: HR — Resolving Attendance and Leave Discrepancies Before Payroll (hr-attendance-payroll)
"""

import pytest
from app.evaluators import evaluate_submission


def test_onboarding_batch_perfect_submission():
    workspace_snapshot = {
        "batchSummary": {
            "totalJoiners": 12,
            "verifiedJoiners": 12,
            "allocatedLaptops": 10,
            "temporaryWorkstations": 2,
        },
        "employeeRecords": [
            {
                "id": "emp-1",
                "name": "Aarav Sharma",
                "department": "Engineering",
                "docStatus": "Complete",
                "itStatus": "Allocated (Laptop #01)",
                "accessStatus": "Standard Eng Access",
                "hrisStatus": "Verified",
                "notes": "All identity and academic credentials verified.",
            },
            {
                "id": "emp-2",
                "name": "Meera Kapoor",
                "department": "Sales",
                "docStatus": "Address Discrepancy",
                "itStatus": "Temporary Desktop Workstation",
                "accessStatus": "Standard Sales Access",
                "hrisStatus": "Action Required",
                "notes": "Flagged address proof discrepancy between Mumbai form declaration and Pune electricity bill; requested updated rental agreement.",
            },
            {
                "id": "emp-3",
                "name": "Rohan Verma",
                "department": "Engineering",
                "docStatus": "Name Mismatch",
                "itStatus": "Allocated (Laptop #02)",
                "accessStatus": "Standard Eng Access",
                "hrisStatus": "Action Required",
                "notes": "Entered Rohan Varma on form. Standardize to government ID Rohan Verma per Aadhaar and Passport.",
            },
            {
                "id": "emp-4",
                "name": "Ananya Singh",
                "department": "Customer Operations",
                "docStatus": "Complete",
                "itStatus": "Allocated (Laptop #03)",
                "accessStatus": "Standard Ops Access",
                "hrisStatus": "Verified",
                "notes": "Verified.",
            },
            {
                "id": "emp-5",
                "name": "Karan Mehta",
                "department": "Sales",
                "docStatus": "Education Missing",
                "itStatus": "Allocated (Laptop #04)",
                "accessStatus": "Standard User (Admin Hold)",
                "hrisStatus": "Action Required",
                "notes": "Denied CRM Administrator escalation per RBAC policy pending degree verification; granted standard access.",
            },
            {
                "id": "emp-6",
                "name": "Priya Nair",
                "department": "Engineering",
                "docStatus": "Bank Incomplete",
                "itStatus": "Allocated (Laptop #05)",
                "accessStatus": "Standard Eng Access",
                "hrisStatus": "Action Required",
                "notes": "Direct deposit setup on hold pending submission of cancelled cheque or bank verification stamp.",
            },
            {
                "id": "emp-7",
                "name": "Vikram Malhotra",
                "department": "Engineering",
                "docStatus": "Complete",
                "itStatus": "Allocated (Laptop #06)",
                "accessStatus": "Standard Eng Access",
                "hrisStatus": "Verified",
                "notes": "Verified.",
            },
            {
                "id": "emp-8",
                "name": "Sneha Iyer",
                "department": "Customer Operations",
                "docStatus": "Date Change Req",
                "itStatus": "Allocated (Laptop #07)",
                "accessStatus": "Standard Ops Access",
                "hrisStatus": "Verified",
                "notes": "Verified.",
            },
            {
                "id": "emp-9",
                "name": "Aditya Joshi",
                "department": "Sales",
                "docStatus": "Complete",
                "itStatus": "Allocated (Laptop #08)",
                "accessStatus": "Standard Sales Access",
                "hrisStatus": "Verified",
                "notes": "Verified.",
            },
            {
                "id": "emp-10",
                "name": "Ritu Sen",
                "department": "Customer Operations",
                "docStatus": "Date Change Req",
                "itStatus": "Allocated (Laptop #09)",
                "accessStatus": "Standard Ops Access",
                "hrisStatus": "Verified",
                "notes": "Verified.",
            },
            {
                "id": "emp-11",
                "name": "Siddharth Roy",
                "department": "Engineering",
                "docStatus": "IT Shortage",
                "itStatus": "Allocated (Laptop #10)",
                "accessStatus": "Standard Eng Access",
                "hrisStatus": "Verified",
                "notes": "Verified.",
            },
            {
                "id": "emp-12",
                "name": "Neha Das",
                "department": "Customer Operations",
                "docStatus": "Software Exception",
                "itStatus": "Temporary Desktop Workstation",
                "accessStatus": "Standard Ops Access",
                "hrisStatus": "Verified",
                "notes": "Verified.",
            },
        ],
        "hardwareAllocationPlan": (
            "Allocated 10 available laptops to priority roles: 4 Engineering developers and 3 client-facing Sales field executives, "
            "plus 3 customer support leads. The remaining internal office roles are assigned temporary desktop workstations."
        ),
    }

    answers = {
        "nameDiscrepancyResolution": (
            "I would rely strictly on the government identity document (Aadhaar or Passport) to standardize the legal name "
            "in the HRIS and statutory payroll registers. I would then contact the employee to obtain written confirmation "
            "explaining the spelling variation and ensuring consistent records across all compliance filings."
        ),
        "incompleteDocSystemAccess": (
            "Under company RBAC and least privilege security policy, I would provision restricted standard user access "
            "rather than elevated administrative privileges. I would notify the department supervisor that full administrative "
            "access requires verified degree transcripts and background verification sign-off."
        ),
        "unverifiedInfoRisk": (
            "Entering unverified employee data risks serious statutory non-compliance, payroll tax calculation errors, PF "
            "and ESI penalties, and audit liabilities. Maintaining data integrity prevents organizational fraud and ensures "
            "legally defensible employment documentation."
        ),
        "itEquipmentPrioritization": (
            "I would prioritise available laptops based on role criticality: allocating systems first to client-facing Sales "
            "and active Engineering developers. For internal campus roles, I would provide temporary loaner desktop workstations "
            "until the replenishment batch arrives from IT."
        ),
        "unapprovedJoiningDateChange": (
            "Before modifying the HRIS, I must obtain written approval from the hiring manager and recruitment team. "
            "A date change impacts project staffing schedules, onboarding cohort logistics, and statutory benefits start dates, "
            "which cannot be adjusted on an unconfirmed candidate request alone."
        ),
        "documentPrivacyCompliance": (
            "All employee PII and sensitive documents must be stored in encrypted HRIS repositories with strict role-based access "
            "controls (RBAC). Physical records must be secured in locked archives, ensuring compliance with data privacy regulations "
            "and restricting viewing access only to authorized personnel."
        ),
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="hr",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="hr-employee-onboarding",
    )

    assert result["passed"] is True
    assert result["overall_score"] >= 85
    assert result["score_breakdown"]["document_verification"] == 100
    assert len(result["task_evaluations"]) == 5
    for task in result["task_evaluations"]:
        assert task["status"] == "PASS"


def test_onboarding_batch_failure():
    workspace_snapshot = {
        "employeeRecords": [
            {
                "id": "emp-3",
                "name": "Rohan Varma",
                "hrisStatus": "Pending",
                "notes": "Left as Varma as filled by candidate.",
            },
            {
                "id": "emp-5",
                "name": "Karan Mehta",
                "accessStatus": "Administrator Privileges Granted",
                "notes": "Approved CRM admin escalation per manager demand without degree.",
            },
        ],
    }

    answers = {
        "nameDiscrepancyResolution": "Whatever candidate typed.",
        "incompleteDocSystemAccess": "Give full admin access so they are happy.",
        "unverifiedInfoRisk": "Not risky at all.",
        "itEquipmentPrioritization": "First come first serve.",
        "unapprovedJoiningDateChange": "Change date immediately.",
        "documentPrivacyCompliance": "Leave papers on the desk.",
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="hr",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="hr-employee-onboarding",
    )

    assert result["passed"] is False
    assert result["overall_score"] < 50


def test_attendance_payroll_perfect_submission():
    workspace_snapshot = {
        "attendanceSummary": {
            "totalEmployees": 12,
            "standardWorkingDays": 22,
        },
        "attendanceRegister": [
            {
                "id": "att-1",
                "employee": "Aarav Sharma",
                "payableDays": 22,
                "action": "Regularize Remote Work (Manager Approved)",
                "payrollStatus": "Adjusted & Confirmed",
                "notes": "Remote day on 15-Nov verified by timesheet.",
            },
            {
                "id": "att-2",
                "employee": "Meera Kapoor",
                "payableDays": 21,
                "action": "Sync 2 Days Approved Medical Leave (1 LOP)",
                "payrollStatus": "Adjusted & Confirmed",
                "notes": "2 days approved medical leave synced; 1 day remains unapproved.",
            },
            {
                "id": "att-3",
                "employee": "Rohan Verma",
                "payableDays": 22,
                "action": "Waive Biometric Lates (Night Shift Release)",
                "payrollStatus": "Adjusted & Confirmed",
                "notes": "Manager confirmed late arrivals were approved shift adjustments.",
            },
            {
                "id": "att-4",
                "employee": "Ananya Singh",
                "payableDays": 20,
                "action": "Record 2 Days Paid Leave + 1 Day LOP",
                "payrollStatus": "Exception Flagged",
                "notes": "Manager rejected 3rd day. 1 day marked as Loss of Pay.",
            },
            {
                "id": "att-5",
                "employee": "Karan Mehta",
                "payableDays": 22,
                "action": "Regularize On-Duty (Client Summit)",
                "payrollStatus": "Adjusted & Confirmed",
                "notes": "Offsite client meeting verified by client sign-off.",
            },
            {
                "id": "att-6",
                "employee": "Priya Nair",
                "payableDays": 21,
                "action": "Reconcile Leave Tracker Formula (4 Days Balance)",
                "payrollStatus": "Adjusted & Confirmed",
                "notes": "Tracker formula error fixed. Audited balance is 4 days.",
            },
            {"id": "att-7", "employee": "Vikram Malhotra", "payableDays": 22, "action": "None (Clean Record)"},
            {"id": "att-8", "employee": "Sneha Iyer", "payableDays": 22, "action": "None (Clean Record)"},
            {"id": "att-9", "employee": "Aditya Joshi", "payableDays": 22, "action": "None (Clean Record)"},
            {"id": "att-10", "employee": "Ritu Sen", "payableDays": 22, "action": "None (Clean Record)"},
            {"id": "att-11", "employee": "Siddharth Roy", "payableDays": 22, "action": "None (Clean Record)"},
            {"id": "att-12", "employee": "Neha Das", "payableDays": 22, "action": "None (Clean Record)"},
        ],
        "payrollHandoverReport": {
            "totalPayableDays": 259,
            "totalExceptions": 1,
            "exceptionNotes": "Ananya Singh: 1 unapproved absence booked as LOP pending further manager review.",
        },
    }

    answers = {
        "biometricAbsentEvidence": (
            "Before correcting an apparent biometric absence, I would review corroborated evidence including manager-approved "
            "timesheet submissions, VPN session login timestamps, Jira activity logs, and scheduled calendar meeting participation "
            "to establish authentic remote work presence."
        ),
        "verbalLeaveApprovalAction": (
            "Under HR attendance policy, verbal approvals cannot be processed for payroll updates. I would instruct the manager "
            "and employee to submit formal written leave applications through the employee self-service portal to maintain an "
            "auditable compliance trail and avoid unauthorized salary disbursements."
        ),
        "leaveBalanceDiscrepancyInvestigation": (
            "I would perform a line-by-line audit comparing the official HRIS ledger with the spreadsheet tracker, auditing "
            "opening leave accruals, carry-forward balances, recorded leave debits, and checking for broken Excel formula links "
            "to reconcile any discrepancy."
        ),
        "unresolvedAttendancePayrollDeadline": (
            "I would not delay the entire payroll submission. Instead, I would document the pending item in an exception register, "
            "process standard payroll for all 11 verified employees to maintain SLA continuity, and apply necessary retroactive "
            "reconciliation adjustments in the subsequent payroll cycle."
        ),
        "approvedVsPendingLeaveDistinction": (
            "Distinguishing approved from pending leave is critical because unapproved absences may represent unauthorized Loss "
            "of Pay (LOP). Processing pending leave as approved risks illegal wage overpayment and clawback liabilities if "
            "subsequently rejected."
        ),
        "recurringDiscrepanciesProcessImprovement": (
            "To permanently resolve recurring discrepancies, I would recommend integrating biometric hardware directly with the HRIS "
            "via automated API synchronization, establishing self-service regularisation workflows, and scheduling automated cut-off "
            "reminder notifications prior to monthly payroll freeze."
        ),
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="hr",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="hr-attendance-payroll",
    )

    assert result["passed"] is True
    assert result["overall_score"] >= 85
    assert result["score_breakdown"]["attendance_reconciliation"] == 100
    assert len(result["task_evaluations"]) == 5
    for task in result["task_evaluations"]:
        assert task["status"] == "PASS"


def test_attendance_payroll_failure():
    workspace_snapshot = {
        "attendanceRegister": [
            {
                "id": "att-1",
                "employee": "Aarav Sharma",
                "payableDays": 21,
                "action": "Unapproved deduction",
                "notes": "Deducted LOP despite remote work.",
            },
            {
                "id": "att-4",
                "employee": "Ananya Singh",
                "payableDays": 22,
                "action": "None",
                "notes": "Ignored rejected leave and paid full month.",
            },
        ]
    }

    answers = {
        "biometricAbsentEvidence": "Biometric machine is always right.",
        "verbalLeaveApprovalAction": "Sure, verbal approval is good enough.",
        "leaveBalanceDiscrepancyInvestigation": "Just guess the number.",
        "unresolvedAttendancePayrollDeadline": "Stop the entire payroll.",
        "approvedVsPendingLeaveDistinction": "No difference.",
        "recurringDiscrepanciesProcessImprovement": "Do nothing.",
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="hr",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="hr-attendance-payroll",
    )

    assert result["passed"] is False
    assert result["overall_score"] < 50
