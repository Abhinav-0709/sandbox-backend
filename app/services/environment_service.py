from __future__ import annotations

import uuid
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.environment import SandboxEnvironment
from app.core.exceptions import NotFoundException, ConflictException, BadRequestException
from app.schemas.environment import CreateEnvironmentRequest, UpdateEnvironmentRequest


DEFAULT_ENVIRONMENTS = [
    {
        "slug": "finance-ap-reconciliation",
        "title": "Checking Supplier Invoices — Weekly Payment Run",
        "description": "Reconcile supplier invoices against purchase orders and receiving notes with 3-way matching controls.",
        "category": "finance",
        "department": "Finance & Accounts Payable",
        "role_title": "Junior Accounts Payable Specialist",
        "subrole_id": "fin-subrole-ap",
        "subrole_title": "Accounts Payable Specialist",
        "difficulty": "Intermediate",
        "estimated_minutes": 40,
        "config": {
            "company_name": "Aster Technologies Inc.",
            "currency": "CAD",
            "batch_date": "Friday, March 27, 2026",
            "manager_name": "Robert MacLeod",
            "instructions": "Audit 6 supplier invoices against PO and GRN records to safeguard capital and detect discrepancies.",
            "starter_workspace_state": {
                "selectedDocId": "doc-inv-8821",
                "invoiceRows": [
                    {
                        "id": "row-1",
                        "rowNum": 1,
                        "invoiceNo": "INV-8821",
                        "supplier": "Vertex Logistics Group",
                        "invoiceDate": "2026-03-22",
                        "poRef": "PO-9041",
                        "grnRef": "GRN-4409",
                        "poAmount": 37500,
                        "grnQuantityRatio": "5/5",
                        "billedAmount": 42500,
                        "verifiedAmount": 0,
                        "decision": "Pending",
                        "discrepancyType": "None",
                        "financialImpact": 0,
                        "reasoning": "",
                        "emailDraftNeeded": False,
                    },
                    {
                        "id": "row-2",
                        "rowNum": 2,
                        "invoiceNo": "INV-8823",
                        "supplier": "NorthernGrid Power Corp.",
                        "invoiceDate": "2026-03-23",
                        "poRef": "PO-9045",
                        "grnRef": "GRN-4410",
                        "poAmount": 14200,
                        "grnQuantityRatio": "1/1",
                        "billedAmount": 14200,
                        "verifiedAmount": 0,
                        "decision": "Pending",
                        "discrepancyType": "None",
                        "financialImpact": 0,
                        "reasoning": "",
                        "emailDraftNeeded": False,
                    },
                    {
                        "id": "row-3",
                        "rowNum": 3,
                        "invoiceNo": "INV-8825",
                        "supplier": "QuickPrint Packaging Ltd.",
                        "invoiceDate": "2026-03-24",
                        "poRef": "PO-9050",
                        "grnRef": "GRN-4412",
                        "poAmount": 28000,
                        "grnQuantityRatio": "750/1000",
                        "billedAmount": 28000,
                        "verifiedAmount": 0,
                        "decision": "Pending",
                        "discrepancyType": "None",
                        "financialImpact": 0,
                        "reasoning": "",
                        "emailDraftNeeded": True,
                    },
                    {
                        "id": "row-4",
                        "rowNum": 4,
                        "invoiceNo": "INV-8826",
                        "supplier": "QuickPrint Packaging Ltd.",
                        "invoiceDate": "2026-03-25",
                        "poRef": "PO-9050",
                        "grnRef": "GRN-4412",
                        "poAmount": 28000,
                        "grnQuantityRatio": "0/1000",
                        "billedAmount": 28000,
                        "verifiedAmount": 0,
                        "decision": "Pending",
                        "discrepancyType": "None",
                        "financialImpact": 0,
                        "reasoning": "",
                        "emailDraftNeeded": True,
                    },
                    {
                        "id": "row-5",
                        "rowNum": 5,
                        "invoiceNo": "INV-8829",
                        "supplier": "Sigma Precision Tools",
                        "invoiceDate": "2026-03-25",
                        "poRef": "PO-9055",
                        "grnRef": "GRN-4415",
                        "poAmount": 130700,
                        "grnQuantityRatio": "20/20",
                        "billedAmount": 130700,
                        "verifiedAmount": 0,
                        "decision": "Pending",
                        "discrepancyType": "None",
                        "financialImpact": 0,
                        "reasoning": "",
                        "emailDraftNeeded": False,
                    },
                    {
                        "id": "row-6",
                        "rowNum": 6,
                        "invoiceNo": "INV-8832",
                        "supplier": "Zenith Advisory Partners",
                        "invoiceDate": "2026-03-26",
                        "poRef": "None",
                        "grnRef": "None",
                        "poAmount": 0,
                        "grnQuantityRatio": "N/A",
                        "billedAmount": 35000,
                        "verifiedAmount": 0,
                        "decision": "Pending",
                        "discrepancyType": "None",
                        "financialImpact": 0,
                        "reasoning": "",
                        "emailDraftNeeded": False,
                    },
                ]
            },
        },
        "evaluation_rules": {"category": "finance", "ruleset": "finance-v1"},
    },
    {
        "slug": "hr-candidate-screening",
        "title": "Reviewing Job Applications — Junior Frontend Developer",
        "description": "Screen 12 candidate CVs and portfolios objectively against essential job requirements while resisting bias.",
        "category": "hr",
        "department": "People Operations & Talent Acquisition",
        "role_title": "Recruitment Coordinator",
        "subrole_id": "hr-subrole-talent-acquisition",
        "subrole_title": "Talent Acquisition Specialist",
        "difficulty": "Advanced",
        "estimated_minutes": 45,
        "config": {
            "company_name": "Nova Technologies",
            "manager_name": "David Sterling",
            "instructions": "Screen 12 candidates for a Junior Frontend Developer position, resist management bias, and detect overclaimed portfolios.",
            "starter_workspace_state": {
                "candidateRows": [
                    {"id": "cand-01", "candidateNo": 1, "name": "Rahul Sharma", "experienceDisplay": "1.5 years", "experienceYears": 1.5, "hasReact": "Yes", "projectsCount": 2, "hasApiIntegration": False, "hasGit": True, "hasResponsiveDesign": True, "essentialCriteriaMet": "Partial", "desirableCriteriaMet": "Yes", "redFlagsIdentified": "", "evidenceQuality": "Overclaimed", "candidateScore": 52, "decision": "Pending", "justification": "", "suggestedInterviewQuestions": ""},
                    {"id": "cand-02", "candidateNo": 2, "name": "Priya Patel", "experienceDisplay": "Fresher (0 yrs)", "experienceYears": 0, "hasReact": "Yes", "projectsCount": 4, "hasApiIntegration": True, "hasGit": True, "hasResponsiveDesign": True, "essentialCriteriaMet": "Yes", "desirableCriteriaMet": "No", "redFlagsIdentified": "", "evidenceQuality": "Verified", "candidateScore": 92, "decision": "Pending", "justification": "", "suggestedInterviewQuestions": ""},
                    {"id": "cand-03", "candidateNo": 3, "name": "Aman Verma", "experienceDisplay": "2 years", "experienceYears": 2.0, "hasReact": "No", "projectsCount": 3, "hasApiIntegration": True, "hasGit": True, "hasResponsiveDesign": True, "essentialCriteriaMet": "No", "desirableCriteriaMet": "Yes", "redFlagsIdentified": "", "evidenceQuality": "Missing", "candidateScore": 40, "decision": "Pending", "justification": "", "suggestedInterviewQuestions": ""},
                    {"id": "cand-04", "candidateNo": 4, "name": "Neha Gupta", "experienceDisplay": "Fresher (0 yrs)", "experienceYears": 0, "hasReact": "Yes", "projectsCount": 3, "hasApiIntegration": False, "hasGit": True, "hasResponsiveDesign": True, "essentialCriteriaMet": "Partial", "desirableCriteriaMet": "No", "redFlagsIdentified": "", "evidenceQuality": "Incomplete", "candidateScore": 68, "decision": "Pending", "justification": "", "suggestedInterviewQuestions": ""},
                    {"id": "cand-05", "candidateNo": 5, "name": "Karan Mehra", "experienceDisplay": "1 year", "experienceYears": 1.0, "hasReact": "Yes", "projectsCount": 2, "hasApiIntegration": False, "hasGit": False, "hasResponsiveDesign": True, "essentialCriteriaMet": "Partial", "desirableCriteriaMet": "Yes", "redFlagsIdentified": "", "evidenceQuality": "Missing", "candidateScore": 45, "decision": "Pending", "justification": "", "suggestedInterviewQuestions": ""},
                    {"id": "cand-06", "candidateNo": 6, "name": "Meera Nambiar", "experienceDisplay": "Fresher (0 yrs)", "experienceYears": 0, "hasReact": "Yes", "projectsCount": 5, "hasApiIntegration": True, "hasGit": True, "hasResponsiveDesign": True, "essentialCriteriaMet": "Yes", "desirableCriteriaMet": "No", "redFlagsIdentified": "", "evidenceQuality": "Verified", "candidateScore": 88, "decision": "Pending", "justification": "", "suggestedInterviewQuestions": ""},
                    {"id": "cand-07", "candidateNo": 7, "name": "Arjun Nair", "experienceDisplay": "2.5 years", "experienceYears": 2.5, "hasReact": "Yes", "projectsCount": 1, "hasApiIntegration": True, "hasGit": True, "hasResponsiveDesign": True, "essentialCriteriaMet": "Partial", "desirableCriteriaMet": "Yes", "redFlagsIdentified": "", "evidenceQuality": "Incomplete", "candidateScore": 70, "decision": "Pending", "justification": "", "suggestedInterviewQuestions": ""},
                    {"id": "cand-08", "candidateNo": 8, "name": "Sneha Rao", "experienceDisplay": "8 months", "experienceYears": 0.67, "hasReact": "Yes", "projectsCount": 4, "hasApiIntegration": True, "hasGit": True, "hasResponsiveDesign": True, "essentialCriteriaMet": "Yes", "desirableCriteriaMet": "No", "redFlagsIdentified": "", "evidenceQuality": "Verified", "candidateScore": 90, "decision": "Pending", "justification": "", "suggestedInterviewQuestions": ""},
                    {"id": "cand-09", "candidateNo": 9, "name": "Vikram Joshi", "experienceDisplay": "3 years", "experienceYears": 3.0, "hasReact": "No", "projectsCount": 2, "hasApiIntegration": False, "hasGit": False, "hasResponsiveDesign": False, "essentialCriteriaMet": "No", "desirableCriteriaMet": "Yes", "redFlagsIdentified": "Informal referral bias", "evidenceQuality": "Missing", "candidateScore": 38, "decision": "Pending", "justification": "", "suggestedInterviewQuestions": ""},
                    {"id": "cand-10", "candidateNo": 10, "name": "Ananya Sen", "experienceDisplay": "Fresher (0 yrs)", "experienceYears": 0, "hasReact": "Yes", "projectsCount": 3, "hasApiIntegration": True, "hasGit": True, "hasResponsiveDesign": True, "essentialCriteriaMet": "Yes", "desirableCriteriaMet": "No", "redFlagsIdentified": "", "evidenceQuality": "Verified", "candidateScore": 84, "decision": "Pending", "justification": "", "suggestedInterviewQuestions": ""},
                    {"id": "cand-11", "candidateNo": 11, "name": "Rohan Gupta", "experienceDisplay": "2 years", "experienceYears": 2.0, "hasReact": "Yes", "projectsCount": 3, "hasApiIntegration": False, "hasGit": True, "hasResponsiveDesign": False, "essentialCriteriaMet": "Partial", "desirableCriteriaMet": "Yes", "redFlagsIdentified": "Overclaimed full-stack skills", "evidenceQuality": "Overclaimed", "candidateScore": 55, "decision": "Pending", "justification": "", "suggestedInterviewQuestions": ""},
                    {"id": "cand-12", "candidateNo": 12, "name": "Divya Krishnan", "experienceDisplay": "6 months", "experienceYears": 0.5, "hasReact": "Yes", "projectsCount": 2, "hasApiIntegration": False, "hasGit": True, "hasResponsiveDesign": True, "essentialCriteriaMet": "Partial", "desirableCriteriaMet": "No", "redFlagsIdentified": "", "evidenceQuality": "Incomplete", "candidateScore": 65, "decision": "Pending", "justification": "", "suggestedInterviewQuestions": ""},
                ]
            },
        },
        "evaluation_rules": {"category": "hr", "ruleset": "hr-v1"},
    },
    {
        "slug": "hr-hiring-requirement",
        "title": "HR — Managing a Difficult Hiring Requirement",
        "description": "Review an unrealistic customer operations hiring requisition (6 roles in 30 days under a tight budget). Align expectations with the workforce plan (2 team leads vs 4 ICs), adjust experience and salary criteria, and prepare an actionable recruitment plan and priority tracker.",
        "category": "hr",
        "department": "Talent Acquisition & Customer Operations",
        "role_title": "Talent Acquisition Specialist",
        "subrole_id": "hr-subrole-talent-acquisition",
        "subrole_title": "Talent Acquisition Specialist",
        "difficulty": "Intermediate",
        "estimated_minutes": 40,
        "config": {
            "company_name": "Vertex Digital Solutions",
            "department": "Customer Operations",
            "positions_count": 6,
            "hiring_deadline_days": 30,
            "starter_workspace_state": {
                "requisitionAnalysis": {
                    "totalPositions": 6,
                    "teamLeadPositions": 2,
                    "icPositions": 4,
                    "revisedIcSalaryBand": "₹3,50,000 - ₹3,80,000",
                    "revisedLeadSalaryBand": "₹4,50,000 - ₹5,00,000",
                },
                "positionsTracker": [
                    {"id": "pos-1", "title": "Shift Team Lead (Project Apex)", "tier": "Team Lead", "expRequired": "3-5 Years", "salaryBand": "₹4.5 - ₹5.0 LPA", "priority": "Wave 1 (Day 20)", "assignedRecruiter": "Pooja Rao", "status": "Sourcing Active"},
                    {"id": "pos-2", "title": "Customer Support IC 1 (Project Apex)", "tier": "Individual Contributor", "expRequired": "1-2 Years", "salaryBand": "₹3.5 - ₹3.8 LPA", "priority": "Wave 1 (Day 20)", "assignedRecruiter": "Amit Sen", "status": "Sourcing Active"},
                    {"id": "pos-3", "title": "Customer Support IC 2 (Project Apex)", "tier": "Individual Contributor", "expRequired": "1-2 Years", "salaryBand": "₹3.5 - ₹3.8 LPA", "priority": "Wave 1 (Day 20)", "assignedRecruiter": "Amit Sen", "status": "Sourcing Active"},
                    {"id": "pos-4", "title": "Shift Team Lead (Project Blue)", "tier": "Team Lead", "expRequired": "3-5 Years", "salaryBand": "₹4.5 - ₹5.0 LPA", "priority": "Wave 2 (Day 30)", "assignedRecruiter": "Pooja Rao", "status": "Sourcing Active"},
                    {"id": "pos-5", "title": "Customer Support IC 3 (Project Blue)", "tier": "Individual Contributor", "expRequired": "1-2 Years", "salaryBand": "₹3.5 - ₹3.8 LPA", "priority": "Wave 2 (Day 30)", "assignedRecruiter": "Amit Sen", "status": "Sourcing Active"},
                    {"id": "pos-6", "title": "Customer Support IC 4 (Project Blue)", "tier": "Individual Contributor", "expRequired": "1-2 Years", "salaryBand": "₹3.5 - ₹3.8 LPA", "priority": "Wave 2 (Day 30)", "assignedRecruiter": "Pooja Rao", "status": "Sourcing Active"},
                ],
            },
        },
        "evaluation_rules": {"category": "hr", "ruleset": "hr-hiring-requirement-v1"},
    },
    {
        "slug": "hr-interview-pipeline",
        "title": "HR — Managing an Interview Pipeline and Hiring Decision",
        "description": "Audit and unblock a delayed 8-candidate interview pipeline for a Business Development Executive role. Resolve conflicting interview feedback, investigate candidate withdrawals, address over-budget salary expectations, follow up on missing evaluation forms, and build a standardized shortlist recommendation.",
        "category": "hr",
        "department": "Talent Acquisition & Business Development",
        "role_title": "Talent Acquisition Specialist",
        "subrole_id": "hr-subrole-talent-acquisition",
        "subrole_title": "Talent Acquisition Specialist",
        "difficulty": "Intermediate",
        "estimated_minutes": 40,
        "config": {
            "company_name": "Vertex Digital Solutions",
            "department": "Business Development",
            "candidates_count": 8,
            "decision_sla_days": 3,
            "starter_workspace_state": {
                "candidateActions": [
                    {"id": "cand-a", "candidate": "Candidate A", "stage": "Final Leadership", "status": "Blocked (Unscheduled)", "action": "Fast-track VP final interview within 24h", "rating": 4.5, "ctc": "₹4.8 LPA"},
                    {"id": "cand-b", "candidate": "Candidate B", "stage": "Hiring Manager", "status": "Discrepancy", "action": "Calibration sync on objection handling", "rating": 3.5, "ctc": "₹4.5 LPA"},
                    {"id": "cand-c", "candidate": "Candidate C", "stage": "Hiring Manager", "status": "Reschedule Requested", "action": "Reschedule to Friday 3:00 PM", "rating": 3.8, "ctc": "₹4.2 LPA"},
                    {"id": "cand-d", "candidate": "Candidate D", "stage": "Final Leadership", "status": "CTC Mismatch", "action": "Negotiate Base ₹5.0L + Sales Commissions", "rating": 4.6, "ctc": "₹6.5 LPA (Target: ₹5.0L)"},
                    {"id": "cand-e", "candidate": "Candidate E", "stage": "Withdrawn", "status": "Drop-off", "action": "Log root cause: Process latency (21 days)", "rating": 3.9, "ctc": "₹4.5 LPA"},
                    {"id": "cand-f", "candidate": "Candidate F", "stage": "Hiring Manager", "status": "Feedback Overdue", "action": "Execute SLA follow-up phone sync with Suresh", "rating": 4.1, "ctc": "₹4.6 LPA"},
                    {"id": "cand-g", "candidate": "Candidate G", "stage": "Evaluation Review", "status": "Under-review", "action": "Review raw deal renewal metrics; keep as backup", "rating": 3.2, "ctc": "₹4.4 LPA"},
                    {"id": "cand-h", "candidate": "Candidate H", "stage": "Withdrawn", "status": "Drop-off", "action": "Log root cause: Accepted competitor offer", "rating": 4.3, "ctc": "₹4.8 LPA"},
                ],
            },
        },
        "evaluation_rules": {"category": "hr", "ruleset": "hr-interview-pipeline-v1"},
    },
    {
        "slug": "hr-employee-onboarding",
        "title": "HR — Managing Employee Onboarding and Documentation",
        "description": "Review 12 new employee records across Engineering, Sales, and Ops, audit identity & educational credentials, resolve CRM admin privilege escalations, and manage hardware allocation.",
        "category": "hr",
        "department": "People Operations & HR Shared Services",
        "role_title": "HR Operations Associate",
        "subrole_id": "hr-subrole-onboarding-ops",
        "subrole_title": "HR Operations Associate",
        "difficulty": "Beginner to Intermediate",
        "estimated_minutes": 45,
        "config": {
            "company_name": "Vertex Digital Solutions",
            "joining_date": "2026-11-24",
            "instructions": "Audit 12 joiner files, resolve Rohan Verma name discrepancy and Meera Kapoor address verification, hold CRM admin escalation for Karan Mehta, and allocate 10 laptops.",
            "starter_workspace_state": {
                "tracker": {
                    "batchVerificationSummary": "",
                    "hardwareAllocationPlan": "",
                    "rbacAccessPlan": "",
                }
            },
        },
        "evaluation_rules": {"category": "hr", "ruleset": "hr-onboarding-v1"},
    },
    {
        "slug": "hr-attendance-payroll",
        "title": "HR — Resolving Attendance and Leave Discrepancies Before Payroll",
        "description": "Reconcile November attendance across 12 employees, investigate biometric vs remote work discrepancies, apply HR attendance policy, and finalize payroll adjustments.",
        "category": "hr",
        "department": "People Operations & HR Shared Services",
        "role_title": "HR Operations Associate",
        "subrole_id": "hr-subrole-onboarding-ops",
        "subrole_title": "HR Operations Associate",
        "difficulty": "Beginner to Intermediate",
        "estimated_minutes": 45,
        "config": {
            "company_name": "Vertex Digital Solutions",
            "payroll_month": "November 2026",
            "working_days": 22,
            "instructions": "Reconcile November attendance records, resolve biometric vs manager approvals, adjust Loss of Pay (LOP), and prepare the payroll handover memo.",
            "starter_workspace_state": {
                "attendance": {
                    "records": [],
                    "payrollAdjustments": "",
                    "lopSummary": "",
                }
            },
        },
        "evaluation_rules": {"category": "hr", "ruleset": "hr-attendance-payroll-v1"},
    },
    {
        "slug": "hr-complaint-investigation",
        "title": "HR — Investigating a Workplace Complaint",
        "description": "Investigate a formal workplace grievance filed by Priya Sharma alleging managerial criticism, short-notice work assignments, personal remarks, and project exclusion. Assess conflicting witness statements, review project deadline changes, safeguard complainant confidentiality, and recommend non-retaliation interim measures.",
        "category": "hr",
        "department": "Customer Operations & Employee Relations",
        "role_title": "Employee Relations Associate",
        "subrole_id": "hr-subrole-employee-relations",
        "subrole_title": "Employee Relations Associate",
        "difficulty": "Intermediate",
        "estimated_minutes": 45,
        "config": {
            "company_name": "Vertex Digital Solutions",
            "complainant": "Priya Sharma",
            "respondent": "Vikram Seth",
            "department": "Customer Operations",
            "instructions": "Review the 4 alleged incidents, triangulate conflicting witness accounts with email records, enforce complainant confidentiality, and prepare an initial investigation report with interim safeguards.",
            "starter_workspace_state": {
                "caseOverview": {
                    "caseId": "ER-2026-088",
                    "complainant": "Priya Sharma",
                    "respondent": "Vikram Seth",
                },
                "incidentTimeline": [],
                "interimMeasures": {},
                "investigationReportSummary": {},
            },
        },
        "evaluation_rules": {"category": "hr", "ruleset": "hr-complaints-v1"},
    },
    {
        "slug": "hr-disciplinary-investigation",
        "title": "HR — Managing a Disciplinary Case and Policy Violation",
        "description": "Investigate an information security policy violation involving Sales employee Rahul Mehta transmitting a confidential pricing sheet to an external address. Review file access logs, evaluate disputed verbal approval claims, balance mitigating factors including training deficits, resist premature termination, and draft a formal disciplinary hearing notice and handover report.",
        "category": "hr",
        "department": "Sales & Employee Relations",
        "role_title": "Employee Relations Associate",
        "subrole_id": "hr-subrole-employee-relations",
        "subrole_title": "Employee Relations Associate",
        "difficulty": "Intermediate",
        "estimated_minutes": 45,
        "config": {
            "company_name": "Vertex Digital Solutions",
            "employee_name": "Rahul Mehta",
            "department": "Sales",
            "incident_date": "2026-11-18",
            "instructions": "Review the IT security DLP report, examine email records and file access logs, investigate verbal approval claims, balance mitigating factors, and prepare a formal disciplinary hearing notice and handover report.",
            "starter_workspace_state": {
                "disciplinaryCase": {
                    "caseId": "DISC-2026-042",
                    "employee": "Rahul Mehta",
                },
                "evidenceTimeline": [],
                "mitigatingAggravatingMatrix": {},
                "hearingNoticeDraft": {},
                "handoverRecommendations": {},
            },
        },
        "evaluation_rules": {"category": "hr", "ruleset": "hr-disciplinary-v1"},
    },
    {
        "slug": "sde-bug-triage",
        "title": "Debugging a Production Issue — CloudDesk SaaS",
        "description": "Triage 3 critical production bugs in a task service: race conditions, optimistic UI disappearance, and BOLA leaks.",
        "category": "sde",
        "department": "Platform Engineering",
        "role_title": "Junior Backend / Full-Stack Engineer",
        "subrole_id": "sde-subrole-platform-sre",
        "subrole_title": "Platform & Reliability Engineer (SRE)",
        "difficulty": "Advanced",
        "estimated_minutes": 50,
        "config": {
            "company_name": "CloudDesk SaaS",
            "instructions": "Inspect backend routes, client modals, and DB schemas to diagnose concurrency, optimistic rollback, and mass assignment defects.",
            "starter_workspace_state": {"diagnostics": []},
        },
        "evaluation_rules": {"category": "sde", "ruleset": "sde-v1"},
    },
    {
        "slug": "finance-expense-review",
        "title": "Reviewing Employee Expenses — Monthly Claims Audit",
        "description": "Review employee expense claims against company policy, identify missing documentation, spot split purchases, and prepare reimbursement recommendations.",
        "category": "finance",
        "department": "Finance Operations",
        "role_title": "Finance Operations Associate",
        "subrole_id": "fin-subrole-expense-auditor",
        "subrole_title": "Finance Operations Associate",
        "difficulty": "Beginner to Intermediate",
        "estimated_minutes": 35,
        "config": {
            "company_name": "Nova Retail Solutions",
            "currency": "INR",
            "policy": {
                "Meals": 800,
                "Local Travel": 1500,
                "Hotel": 4000,
                "Office Supplies": 5000,
            },
            "instructions": "Audit 6 employee expense claims for March against company expense policy limits, verify itemized receipts, and identify split transactions.",
            "starter_workspace_state": {
                "claims": [
                    {"id": "claim-rahul", "employee": "Rahul Sharma", "expenseType": "Meals", "claimedAmount": 650, "reimbursableAmount": 0, "decision": "Pending", "discrepancyType": "None", "notes": ""},
                    {"id": "claim-priya", "employee": "Priya Patel", "expenseType": "Local Travel", "claimedAmount": 2000, "reimbursableAmount": 0, "decision": "Pending", "discrepancyType": "None", "notes": ""},
                    {"id": "claim-aman", "employee": "Aman Verma", "expenseType": "Hotel", "claimedAmount": 3500, "reimbursableAmount": 0, "decision": "Pending", "discrepancyType": "None", "notes": ""},
                    {"id": "claim-neha", "employee": "Neha Gupta", "expenseType": "Meals", "claimedAmount": 1200, "reimbursableAmount": 0, "decision": "Pending", "discrepancyType": "None", "notes": ""},
                    {"id": "claim-rohan", "employee": "Rohan Mehta", "expenseType": "Office Supplies", "claimedAmount": 4500, "reimbursableAmount": 0, "decision": "Pending", "discrepancyType": "None", "notes": ""},
                    {"id": "claim-kavita", "employee": "Kavita Desai", "expenseType": "Local Travel", "claimedAmount": 1400, "reimbursableAmount": 0, "decision": "Pending", "discrepancyType": "None", "notes": ""},
                ]
            },
        },
        "evaluation_rules": {"category": "finance", "ruleset": "finance-expenses-v1"},
    },
    {
        "slug": "finance-duplicate-payment",
        "title": "Investigating a Duplicate Supplier Payment — Reconciliation & Recovery",
        "description": "Investigate internal payment timeout failure vs. actual bank clearance for ₹1,18,000 to Apex Office Supplies (INV-7841). Reconcile supplier ledger against bank statement, trace batch logs, and structure recovery.",
        "category": "finance",
        "department": "Accounts Payable & Finance Operations",
        "role_title": "Finance Operations Associate",
        "subrole_id": "fin-subrole-expense-auditor",
        "subrole_title": "Finance Operations Associate",
        "difficulty": "Beginner to Intermediate",
        "estimated_minutes": 40,
        "config": {
            "company_name": "Nova Retail Solutions",
            "currency": "INR",
            "instructions": "Audit internal payment batch logs against the official bank statement and supplier ledger. Uncover why system timeout failures triggered a duplicate ₹1,18,000 payout, determine actual cash movements, calculate recovery balances, and structure corrective controls.",
            "starter_workspace_state": {
                "payments": [
                    {"id": "pay-001", "paymentNo": "Payment 001", "supplier": "Apex Office Supplies", "invoiceRef": "INV-7841", "amount": 118000, "date": "04-Apr-2026", "systemStatus": "Failed (Timeout 504)", "bankStatus": "Debited (CMS-HDFC-994102)", "auditDecision": "Confirmed Duplicate", "reconciledAmount": 118000},
                    {"id": "pay-002", "paymentNo": "Payment 002", "supplier": "Apex Office Supplies", "invoiceRef": "INV-7841", "amount": 118000, "date": "08-Apr-2026", "systemStatus": "Success (HTTP 200)", "bankStatus": "Debited (CMS-HDFC-995481)", "auditDecision": "Confirmed Duplicate", "reconciledAmount": 0},
                    {"id": "pay-003", "paymentNo": "Payment 003", "supplier": "Bright Logistics", "invoiceRef": "INV-2205", "amount": 76000, "date": "09-Apr-2026", "systemStatus": "Success (HTTP 200)", "bankStatus": "Debited (CMS-HDFC-996114)", "auditDecision": "Valid Payment", "reconciledAmount": 76000},
                    {"id": "pay-004", "paymentNo": "Payment 004", "supplier": "Apex Office Supplies", "invoiceRef": "INV-7890", "amount": 42000, "date": "10-Apr-2026", "systemStatus": "Success (HTTP 200)", "bankStatus": "Debited (CMS-HDFC-997230)", "auditDecision": "Valid Payment", "reconciledAmount": 42000},
                ],
                "recoveryRecommendation": "Refund",
                "correctiveActions": {
                    "supplierNotified": True,
                    "demandLetterDrafted": False,
                    "erpStatusCorrected": False,
                    "timeoutControlsLogged": False,
                },
            },
        },
        "evaluation_rules": {"category": "finance", "ruleset": "finance-duplicate-payment-v1"},
    },
    {
        "slug": "finance-bank-change-verification",
        "title": "Verifying a Supplier Bank Account Change — Anti-Fraud BEC Audit",
        "description": "Verify an urgent vendor bank account modification request for Apex Office Supplies with an impending ₹2,40,000 payment. Uncover domain spoofing, telephone mismatch, entity name discrepancy, and enforce dual-control verification.",
        "category": "finance",
        "department": "Accounts Payable & Vendor Governance",
        "role_title": "Finance Operations Associate",
        "subrole_id": "fin-subrole-expense-auditor",
        "subrole_title": "Finance Operations Associate",
        "difficulty": "Beginner to Intermediate",
        "estimated_minutes": 35,
        "config": {
            "company_name": "Nova Retail Solutions",
            "currency": "INR",
            "instructions": "Audit an urgent change-of-bank request for Apex Office Supplies. Cross-reference master vendor records against request documents, identify 4 red flags indicating Business Email Compromise (BEC), make defensible payment decisions for pending INV-9021 (₹2,40,000), and execute out-of-band verification protocols.",
            "starter_workspace_state": {
                "requestAnalysis": {
                    "vendorId": "SUP-1042",
                    "vendorName": "Apex Office Supplies Private Limited",
                    "requestedBank": "XYZ Bank Ltd",
                    "requestedAccount": "91820491829174",
                    "currentBank": "ABC Bank Ltd",
                    "currentAccount": "00921040004821",
                    "pendingInvoiceNo": "INV-9021",
                    "pendingInvoiceAmount": 240000,
                },
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
            },
        },
        "evaluation_rules": {"category": "finance", "ruleset": "finance-bank-change-v1"},
    },
    {
        "slug": "finance-purchase-planning",
        "title": "Planning a Company Purchase — Capital Allocation & Cash Flow",
        "description": "Model cash runway, evaluate multi-year Total Cost of Ownership (TCO) across 3 hardware vendors, and structure a working-capital-preserving procurement strategy for 20 laptops.",
        "category": "finance",
        "department": "Financial Planning & Analysis (FP&A)",
        "role_title": "Junior Financial Analyst",
        "subrole_id": "fin-subrole-capital-planning",
        "subrole_title": "Junior Financial Analyst",
        "difficulty": "Intermediate",
        "estimated_minutes": 45,
        "config": {
            "company_name": "BrightEdge Technologies",
            "currency": "INR",
            "bank_balance": 800000,
            "instructions": "Analyze 30-day operational cash inflows and commitments, compare 3 laptop vendor quotes by multi-year TCO, and provide an executive capital recommendation.",
            "starter_workspace_state": {
                "calculations": {
                    "startingCash": 800000,
                    "expectedInflows": 400000,
                    "mandatoryOutflows": 480000,
                    "operatingCashBuffer": 0,
                    "recommendedVendor": "",
                    "vendorTco": {"Vendor A": 0, "Vendor B": 0, "Vendor C": 0},
                    "solvencyRiskAssessment": "",
                }
            },
        },
        "evaluation_rules": {"category": "finance", "ruleset": "finance-purchase-v1"},
    },
    {
        "slug": "finance-business-performance",
        "title": "Investigating Monthly Business Performance — P&L Variance Audit",
        "description": "Review April financial performance against March actuals and budget. Calculate revenue, COGS, and opex variances, investigate category sales shortfalls, separate one-time costs, and calculate profit margins.",
        "category": "finance",
        "department": "Financial Planning & Analysis (FP&A)",
        "role_title": "Junior Financial Analyst",
        "subrole_id": "fin-subrole-capital-planning",
        "subrole_title": "Junior Financial Analyst",
        "difficulty": "Beginner to Intermediate",
        "estimated_minutes": 40,
        "config": {
            "company_name": "Nova Retail Solutions",
            "currency": "INR",
            "instructions": "Evaluate preliminary April actuals against March actuals and the April budget. Determine why revenue grew by only ₹3,00,000 while operating expenses surged by ₹4,70,000. Isolate one-time costs, examine category sales shortfalls, calculate gross/operating margins, and deliver actionable turnaround recommendations.",
            "starter_workspace_state": {
                "metrics": [
                    {"id": "m-rev", "metric": "Revenue", "marchActual": 4800000, "aprilBudget": 5500000, "aprilActual": 5100000, "varBudgetAbs": -400000, "varBudgetPct": -7.27, "varMarchAbs": 300000, "varMarchPct": 6.25, "type": "Revenue"},
                    {"id": "m-cogs", "metric": "Cost of Goods Sold (COGS)", "marchActual": 2700000, "aprilBudget": 3000000, "aprilActual": 3150000, "varBudgetAbs": 150000, "varBudgetPct": 5.00, "varMarchAbs": 450000, "varMarchPct": 16.67, "type": "Cost"},
                    {"id": "m-emp", "metric": "Employee Expenses", "marchActual": 800000, "aprilBudget": 850000, "aprilActual": 920000, "varBudgetAbs": 70000, "varBudgetPct": 8.24, "varMarchAbs": 120000, "varMarchPct": 15.00, "type": "Opex"},
                    {"id": "m-mkt", "metric": "Marketing Expenses", "marchActual": 300000, "aprilBudget": 400000, "aprilActual": 520000, "varBudgetAbs": 120000, "varBudgetPct": 30.00, "varMarchAbs": 220000, "varMarchPct": 73.33, "type": "Opex"},
                    {"id": "m-oth", "metric": "Other Operating Expenses", "marchActual": 400000, "aprilBudget": 450000, "aprilActual": 480000, "varBudgetAbs": 30000, "varBudgetPct": 6.67, "varMarchAbs": 80000, "varMarchPct": 20.00, "type": "Opex"},
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
            },
        },
        "evaluation_rules": {"category": "finance", "ruleset": "finance-business-performance-v1"},
    },
    {
        "slug": "finance-cash-flow-forecast",
        "title": "Preparing a Cash Flow Forecast — Liquidity & Working Capital",
        "description": "Prepare a 3-month rolling cash flow forecast for May, June, and July starting with ₹12,00,000 cash. Model customer collection delays, assess supplier payment schedules, stress-test working capital, and prevent liquidity deficit.",
        "category": "finance",
        "department": "Treasury & Financial Planning",
        "role_title": "Junior Financial Analyst",
        "subrole_id": "fin-subrole-capital-planning",
        "subrole_title": "Junior Financial Analyst",
        "difficulty": "Beginner to Intermediate",
        "estimated_minutes": 40,
        "config": {
            "company_name": "Nova Retail Solutions",
            "currency": "INR",
            "instructions": "Evaluate starting cash (₹12,00,000) against projected collections and operational disbursements for May, June, and July. Audit customer receivables to stress-test late paying accounts (Zenith Mart ₹6,00,000 delayed/disputed). Assess supplier schedules and planned bulk inventory expenditures, identify the impending June cash deficit, and model corrective working capital measures.",
            "starter_workspace_state": {
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
            },
        },
        "evaluation_rules": {"category": "finance", "ruleset": "finance-cash-flow-forecast-v1"},
    },
    {
        "slug": "finance-budget-review",
        "title": "Reviewing Department Budgets — Variance & Performance Analysis",
        "description": "Conduct monthly financial close variance analysis across 5 operating departments, distinguish activity-driven revenue commissions from cost-control failures, and prepare a quarterly re-forecast.",
        "category": "finance",
        "department": "Corporate FP&A",
        "role_title": "Budget Analyst",
        "subrole_id": "fin-subrole-fpa-budget",
        "subrole_title": "Corporate FP&A Associate",
        "difficulty": "Intermediate",
        "estimated_minutes": 40,
        "config": {
            "company_name": "Vertex Solutions",
            "currency": "INR",
            "instructions": "Compare planned budgets with actual expenditures across 5 departments, determine variance percentages and causes, and prepare a quarterly re-forecast.",
            "starter_workspace_state": {
                "departments": [
                    {"id": "dept-marketing", "department": "Marketing", "planned": 200000, "actual": 250000, "varianceAmount": 0, "varianceType": "Pending", "notes": ""},
                    {"id": "dept-technology", "department": "Technology", "planned": 300000, "actual": 280000, "varianceAmount": 0, "varianceType": "Pending", "notes": ""},
                    {"id": "dept-hr", "department": "HR", "planned": 100000, "actual": 120000, "varianceAmount": 0, "varianceType": "Pending", "notes": ""},
                    {"id": "dept-operations", "department": "Operations", "planned": 250000, "actual": 240000, "varianceAmount": 0, "varianceType": "Pending", "notes": ""},
                    {"id": "dept-sales", "department": "Sales", "planned": 150000, "actual": 180000, "varianceAmount": 0, "varianceType": "Pending", "notes": ""},
                ]
            },
        },
        "evaluation_rules": {"category": "finance", "ruleset": "finance-budget-v1"},
    },
    {
        "slug": "finance-supplier-payments",
        "title": "Managing Supplier Payments — Working Capital & Payment Prioritisation",
        "description": "Prioritize mission-critical supplier disbursements under a strict ₹3,00,000 treasury liquidity constraint, capture early payment discounts, and formulate partner deferral communications.",
        "category": "finance",
        "department": "Treasury & Accounts Payable",
        "role_title": "Accounts Payable Analyst",
        "subrole_id": "fin-subrole-treasury-payments",
        "subrole_title": "Treasury & AP Associate",
        "difficulty": "Intermediate to Advanced",
        "estimated_minutes": 45,
        "config": {
            "company_name": "Orbit Manufacturing Ltd.",
            "currency": "INR",
            "cash_cap": 300000,
            "instructions": "Evaluate 5 pending supplier invoices totaling ₹3,30,000 under a ₹3,00,000 cash cap, prioritize essential operational payments, and draft deferral notices.",
            "starter_workspace_state": {
                "payments": [
                    {"id": "pay-steelpro", "supplier": "SteelPro", "amountDue": 120000, "dueDate": "Today", "priority": 1, "decision": "Pending", "paymentAmount": 0, "notes": ""},
                    {"id": "pay-cloudhost", "supplier": "CloudHost", "amountDue": 40000, "dueDate": "In 2 days", "priority": 2, "decision": "Pending", "paymentAmount": 0, "notes": ""},
                    {"id": "pay-machinecare", "supplier": "MachineCare", "amountDue": 90000, "dueDate": "Tomorrow", "priority": 3, "decision": "Pending", "paymentAmount": 0, "notes": ""},
                    {"id": "pay-printworks", "supplier": "PrintWorks", "amountDue": 50000, "dueDate": "In 10 days", "priority": 4, "decision": "Pending", "paymentAmount": 0, "notes": ""},
                    {"id": "pay-officemart", "supplier": "OfficeMart", "amountDue": 30000, "dueDate": "In 7 days", "priority": 5, "decision": "Pending", "paymentAmount": 0, "notes": ""},
                ]
            },
        },
        "evaluation_rules": {"category": "finance", "ruleset": "finance-payments-v1"},
    },
    {
        "slug": "finance-statement-reconciliation",
        "title": "Finance — Reconciling Supplier Statements",
        "description": "Reconcile vendor statement of account (₹3,85,000) against company AP sub-ledger (₹2,95,000), identify payments in transit, missing invoices, unapplied credit notes, and keying errors.",
        "category": "finance",
        "department": "Accounts Payable & General Accounting",
        "role_title": "Accounts Payable Specialist",
        "subrole_id": "fin-subrole-ap",
        "subrole_title": "Accounts Payable Specialist",
        "difficulty": "Beginner to Intermediate",
        "estimated_minutes": 35,
        "config": {
            "company_name": "Nova Retail Solutions",
            "currency": "INR",
            "supplier": "Apex Office Supplies",
            "starter_workspace_state": {
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
            },
        },
        "evaluation_rules": {"category": "finance", "ruleset": "finance-statement-reconciliation-v1"},
    },
    {
        "slug": "finance-invoice-cutoff",
        "title": "Finance — Managing Invoice Processing and Month-End Cut-Off",
        "description": "Process June month-end supplier invoice batch, enforce accounting period cut-offs, 3-way matching controls, multi-period prepayment splits, and unbilled utility accruals.",
        "category": "finance",
        "department": "Accounts Payable & General Accounting",
        "role_title": "Accounts Payable Specialist",
        "subrole_id": "fin-subrole-ap",
        "subrole_title": "Accounts Payable Specialist",
        "difficulty": "Beginner to Intermediate",
        "estimated_minutes": 35,
        "config": {
            "company_name": "Nova Retail Solutions",
            "currency": "INR",
            "starter_workspace_state": {
                "invoices": [
                    {"id": "inv-3101", "supplier": "Apex Office Supplies", "ref": "INV-3101", "amount": 48000, "status": "Hold (Missing GRN)", "juneExpenseAmount": 0, "prepaidAmount": 0},
                    {"id": "inv-3102", "supplier": "Bright Logistics", "ref": "INV-3102", "amount": 72000, "status": "Ready to Post", "juneExpenseAmount": 72000, "prepaidAmount": 0},
                    {"id": "inv-3103", "supplier": "CloudServe Technologies", "ref": "INV-3103", "amount": 120000, "status": "Split Prepayment", "juneExpenseAmount": 40000, "prepaidAmount": 80000},
                    {"id": "inv-3104", "supplier": "Metro Utilities", "ref": "INV-3104", "amount": 35000, "costCentre": "401 (Facilities & Utilities)", "status": "Ready to Post", "juneExpenseAmount": 35000, "prepaidAmount": 0},
                    {"id": "inv-3105", "supplier": "Secure Facility Services", "ref": "INV-3105", "amount": 60000, "status": "Ready to Post", "juneExpenseAmount": 60000, "prepaidAmount": 0},
                ],
                "unbilledAccruals": [
                    {"id": "acc-elec", "expenseType": "Electricity Power Tariff", "meterReadingKwh": 4200, "tariffRatePerKwh": 10.0, "estimatedAccrualAmount": 42000, "costCentre": "401 (Facilities & Utilities)"},
                ],
            },
        },
        "evaluation_rules": {"category": "finance", "ruleset": "finance-invoice-cutoff-v1"},
    },
]


def bump_semver(current: str, bump: str = "minor") -> str:
    parts = current.split(".")
    try:
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0
    except (ValueError, IndexError):
        major, minor, patch = 1, 0, 0

    if bump == "major":
        return f"{major + 1}.0.0"
    elif bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    else:  # minor default
        return f"{major}.{minor + 1}.0"


class EnvironmentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_environments(self, include_inactive: bool = False) -> List[SandboxEnvironment]:
        stmt = select(SandboxEnvironment)
        if not include_inactive:
            stmt = stmt.where(SandboxEnvironment.is_active == True)
        res = await self.db.execute(stmt)
        envs = list(res.scalars().all())
        if not envs and not include_inactive:
            await self.ensure_defaults()
            res_refreshed = await self.db.execute(stmt)
            envs = list(res_refreshed.scalars().all())
        return envs

    async def get_by_slug(self, slug: str) -> SandboxEnvironment:
        stmt = select(SandboxEnvironment).where(SandboxEnvironment.slug == slug)
        res = await self.db.execute(stmt)
        env = res.scalar_one_or_none()
        if not env:
            await self.ensure_defaults()
            res_retry = await self.db.execute(stmt)
            env = res_retry.scalar_one_or_none()

        if not env:
            raise NotFoundException(f"Environment '{slug}' not found.")
        return env

    async def create_environment(self, req: CreateEnvironmentRequest) -> SandboxEnvironment:
        stmt = select(SandboxEnvironment).where(SandboxEnvironment.slug == req.slug)
        res = await self.db.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            raise ConflictException(f"Environment with slug '{req.slug}' already exists.")

        env = SandboxEnvironment(
            slug=req.slug,
            title=req.title,
            description=req.description,
            category=req.category,
            department=req.department,
            role_title=req.role_title,
            difficulty=req.difficulty,
            estimated_minutes=req.estimated_minutes,
            config=req.config,
            evaluation_rules=req.evaluation_rules,
            is_active=True,
            version="1.0.0",
        )
        self.db.add(env)
        await self.db.flush()
        await self.db.refresh(env)
        return env

    async def update_environment(self, slug: str, req: UpdateEnvironmentRequest) -> SandboxEnvironment:
        env = await self.get_by_slug(slug)
        if req.title is not None:
            env.title = req.title
        if req.description is not None:
            env.description = req.description
        if req.department is not None:
            env.department = req.department
        if req.role_title is not None:
            env.role_title = req.role_title
        if req.difficulty is not None:
            env.difficulty = req.difficulty
        if req.estimated_minutes is not None:
            env.estimated_minutes = req.estimated_minutes
        if req.config is not None:
            env.config = req.config
        if req.evaluation_rules is not None:
            env.evaluation_rules = req.evaluation_rules
        if req.is_active is not None:
            env.is_active = req.is_active

        await self.db.flush()
        await self.db.refresh(env)
        return env

    async def publish_version(self, slug: str, version_bump: str = "minor", release_notes: Optional[str] = None) -> SandboxEnvironment:
        env = await self.get_by_slug(slug)
        new_version = bump_semver(env.version, version_bump)
        env.version = new_version
        
        # Preserve release history in config metadata
        history = env.config.get("_release_history", [])
        history.append({
            "version": new_version,
            "bump": version_bump,
            "release_notes": release_notes,
        })
        env.config["_release_history"] = history

        await self.db.flush()
        await self.db.refresh(env)
        return env

    async def delete_environment(self, slug: str, hard_delete: bool = False) -> bool:
        env = await self.get_by_slug(slug)
        if hard_delete:
            await self.db.delete(env)
        else:
            env.is_active = False
        await self.db.flush()
        return True

    async def ensure_defaults(self):
        for item in DEFAULT_ENVIRONMENTS:
            stmt = select(SandboxEnvironment).where(SandboxEnvironment.slug == item["slug"])
            res = await self.db.execute(stmt)
            existing = res.scalar_one_or_none()
            if not existing:
                env = SandboxEnvironment(
                    slug=item["slug"],
                    title=item["title"],
                    description=item["description"],
                    category=item["category"],
                    department=item["department"],
                    role_title=item["role_title"],
                    subrole_id=item.get("subrole_id"),
                    subrole_title=item.get("subrole_title"),
                    difficulty=item["difficulty"],
                    estimated_minutes=item["estimated_minutes"],
                    config=item["config"],
                    evaluation_rules=item["evaluation_rules"],
                    is_active=True,
                    version="1.0.0",
                )
                self.db.add(env)
            else:
                # Keep subrole, role, and config metadata synchronized
                existing.subrole_id = item.get("subrole_id")
                existing.subrole_title = item.get("subrole_title")
                existing.role_title = item.get("role_title")
                existing.department = item.get("department")
                existing.config = item.get("config", {})
        await self.db.flush()
