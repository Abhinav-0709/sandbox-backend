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
        "slug": "hr-employee-onboarding",
        "title": "Managing Employee Onboarding — Operational Coordination & Infosec",
        "description": "Coordinate the onboarding of Marketing Executive Ananya Sharma on 23 Nov across HR, IT, and Manager workflows. Resolve laptop scarcity, enforce RBAC against admin escalation, and eliminate Day 1 client meeting conflicts.",
        "category": "hr",
        "department": "People Operations & HR Shared Services",
        "role_title": "HR Operations Associate",
        "subrole_id": "hr-subrole-onboarding-ops",
        "subrole_title": "HR Operations Associate",
        "difficulty": "Advanced",
        "estimated_minutes": 45,
        "config": {
            "company_name": "Nova Technologies",
            "employee_name": "Ananya Sharma",
            "joining_date": "2026-11-23",
            "role": "Marketing Executive",
            "instructions": "Review the 9-activity onboarding tracker, resolve the single-laptop allocation dispute, reject unauthorized CRM admin access under RBAC, and reschedule Day 1 conflicts.",
            "starter_workspace_state": {
                "tracker": {
                    "laptopResolution": "",
                    "crmAccessDecision": "",
                    "scheduleConflictResolution": "",
                    "unverifiedIdSafeguards": "",
                    "preJoiningTriage": "",
                }
            },
        },
        "evaluation_rules": {"category": "hr", "ruleset": "hr-onboarding-v1"},
    },
    {
        "slug": "hr-complaint-investigation",
        "title": "Handling an Employee Complaint — Workplace Investigation & Ethics",
        "description": "Investigate an employee workload, overtime, and public criticism grievance at BrightEdge Solutions. Separate verified facts from uncorroborated allegations, enforce strict complainant confidentiality, and implement non-retaliation safeguards.",
        "category": "hr",
        "department": "Employee Relations & HR Compliance",
        "role_title": "HR Executive",
        "subrole_id": "hr-subrole-employee-relations",
        "subrole_title": "HR Executive / Employee Relations",
        "difficulty": "Advanced",
        "estimated_minutes": 50,
        "config": {
            "company_name": "BrightEdge Solutions",
            "complainant": "Rahul",
            "department": "Engineering Services",
            "instructions": "Analyze team workload metrics (5 projects, 22h overtime), maintain confidentiality by withholding raw complaint copies from the manager, and establish non-retaliation meeting safeguards.",
            "starter_workspace_state": {
                "investigation": {
                    "workloadAssessment": "",
                    "disclosureDecision": "",
                    "retaliationSafeguards": "",
                    "evidenceSynthesis": "",
                }
            },
        },
        "evaluation_rules": {"category": "hr", "ruleset": "hr-complaints-v1"},
    },
    {
        "slug": "hr-performance-review",
        "title": "Reviewing Employee Performance — Contextual Analytics & Development",
        "description": "Analyze quarterly performance across 6 Customer Operations employees at Vertex Solutions. Evaluate volume vs quality metrics, contextualize shifting priorities and unguided system changes, and prepare calibrated Individual Development Plans.",
        "category": "hr",
        "department": "Talent Management & Performance",
        "role_title": "HR Performance Coordinator",
        "subrole_id": "hr-subrole-performance-management",
        "subrole_title": "HR Performance Coordinator",
        "difficulty": "Advanced",
        "estimated_minutes": 45,
        "config": {
            "company_name": "Vertex Solutions",
            "quarter": "Q1 2026",
            "department": "Customer Operations",
            "instructions": "Calculate achievement percentages, reconcile qualitative manager feedback against quality metrics (92%-97%), and formulate targeted coaching plans.",
            "starter_workspace_state": {
                "employees": [
                    {"id": "perf-rahul", "employee": "Rahul", "target": 100, "actual": 115, "qualityScore": 92, "achievementPct": 115, "recommendation": "", "notes": ""},
                    {"id": "perf-priya", "employee": "Priya", "target": 100, "actual": 88, "qualityScore": 97, "achievementPct": 88, "recommendation": "", "notes": ""},
                    {"id": "perf-aman", "employee": "Aman", "target": 100, "actual": 96, "qualityScore": 90, "achievementPct": 96, "recommendation": "", "notes": ""},
                    {"id": "perf-neha", "employee": "Neha", "target": 100, "actual": 72, "qualityScore": 94, "achievementPct": 72, "recommendation": "", "notes": ""},
                    {"id": "perf-karan", "employee": "Karan", "target": 100, "actual": 105, "qualityScore": 78, "achievementPct": 105, "recommendation": "", "notes": ""},
                    {"id": "perf-meera", "employee": "Meera", "target": 100, "actual": 91, "qualityScore": 96, "achievementPct": 91, "recommendation": "", "notes": ""},
                ]
            },
        },
        "evaluation_rules": {"category": "hr", "ruleset": "hr-performance-v1"},
    },
    {
        "slug": "hr-training-planning",
        "title": "Planning Employee Training — Competency Gaps & Resource Allocation",
        "description": "Design a 4-week CRM rollout training strategy for 20 employees under a ₹30,000 budget at Orbit Business Solutions. Reorganize skill-mismatched cohorts, leverage internal champions, and protect 80% Customer Support shift staffing.",
        "category": "hr",
        "department": "Learning & Organizational Development",
        "role_title": "Learning and Development Coordinator",
        "subrole_id": "hr-subrole-learning-development",
        "subrole_title": "Learning & Development Coordinator",
        "difficulty": "Advanced",
        "estimated_minutes": 45,
        "config": {
            "company_name": "Orbit Business Solutions",
            "total_budget": 30000,
            "crm_rollout_weeks": 4,
            "instructions": "Review 20 employee diagnostic assessments, correct premature Group C advanced placements, stagger shift cohorts preserving Support 80% SLA, and deploy internal champions.",
            "starter_workspace_state": {
                "trainingPlan": {
                    "groupingDecision": "",
                    "operationalScheduling": "",
                    "internalTrainerStrategy": "",
                    "totalBudgetCost": 28500,
                }
            },
        },
        "evaluation_rules": {"category": "hr", "ruleset": "hr-training-v1"},
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
