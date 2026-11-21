"""
Tests for the 4 newly added HR Benchmark Evaluators:
- hr-employee-onboarding (Nova Technologies - Operational onboarding, laptop allocation, RBAC security)
- hr-complaint-investigation (BrightEdge Solutions - Workplace investigation, confidentiality, non-retaliation)
- hr-performance-review (Vertex Solutions - Customer ops quarterly review, quality vs volume, IDPs)
- hr-training-planning (Orbit Business Solutions - CRM rollout, competency regrouping, shift SLA coverage)
"""

import pytest
from app.evaluators import evaluate_submission, evaluate_submission_async
from app.evaluators.hr_onboarding import evaluate_onboarding_submission, evaluate_onboarding_submission_async
from app.evaluators.hr_complaints import evaluate_complaint_submission, evaluate_complaint_submission_async
from app.evaluators.hr_performance import evaluate_performance_submission, evaluate_performance_submission_async
from app.evaluators.hr_training import evaluate_training_submission, evaluate_training_submission_async


# ==============================================================================
# HR Scenario 2: Employee Onboarding Tests
# ==============================================================================

def test_onboarding_evaluator_high_score():
    workspace = {
        "tracker": {
            "laptopResolution": "Reassign unutilized laptop from postponed joiner to Ananya",
            "crmAccessDecision": "Reject admin access; provision standard role-based marketing permissions under RBAC",
            "scheduleConflictResolution": "Reschedule client meeting to afternoon; prioritize morning HR orientation 9:30-11:30",
            "unverifiedIdSafeguards": "Restrict live customer data and production CRM database access until ID verified",
            "preJoiningTriage": "Triage complete: verify ID, reallocate laptop, provision corporate email credentials",
        }
    }
    answers = {
        "q1PreVsPostJoining": (
            "Critical pre-joining dependencies include formal identity verification, background screening, "
            "hardware workstation laptop provisioning, enterprise email creation, and role-based CRM access setup. "
            "Non-blocking post-joining items include submitting physical bank cancelled cheques for payroll, "
            "attending general company-wide culture orientation, and deep tool workflow walkthroughs."
        ),
        "q2LaptopAllocationResolution": (
            "IT has one laptop allocated to an employee whose start date was postponed. I will coordinate "
            "with IT Asset Management to formally reassign and re-tag this device for Ananya, update the asset inventory "
            "records, and re-image it with standard corporate security profiles to eliminate unnecessary joining delays."
        ),
        "q3AdminAccessGovernance": (
            "I will firmly reject the manager's request for administrator CRM privileges. Under corporate "
            "least privilege and role-based access control (RBAC) policies, marketing executives only require standard "
            "marketing user permissions. Administrator access exposes system configuration and sensitive enterprise data "
            "to unnecessary risk."
        ),
        "q4UnverifiedIdentityRestrictions": (
            "If Ananya joins prior to completing ID verification, she must be placed on provisional access. "
            "We must restrict production CRM database access, export permissions, and sensitive customer PII access. "
            "She can proceed with general orientation and internal marketing collateral review while an urgent 24-hour "
            "ID submission deadline is enforced."
        ),
        "q5ScheduleConflictResolution": (
            "To resolve the overlap between HR orientation (9:30-11:30 AM) and the client meeting (10:00-12:00 PM), "
            "I will coordinate with the reporting manager to bifurcate onboarding: complete core administrative orientation "
            "early at 9:00 AM, allow her to shadow the client meeting with defined observer status, and conduct the "
            "remaining orientation modules in the afternoon."
        ),
        "q6AlternativeHardwareContingency": (
            "If no corporate laptop is available, I will request an IT temporary loaner or pool device with enterprise "
            "MDM installed, or configure secure Virtual Desktop Infrastructure (VDI) access with multi-factor authentication, "
            "while expediting emergency hardware procurement."
        ),
        "q7RiskEscalationHierarchy": (
            "Immediate escalation to the HR Manager is required for manager pushback on RBAC security policy breaches, "
            "failure to clear legal background screening, or total hardware unavailability. Operational tasks such as "
            "meeting rescheduling, standard asset re-tagging, and checklist tracking will be handled directly."
        ),
        "onboardingReadinessReportDraft": (
            "EXECUTIVE ONBOARDING READINESS MEMO\n"
            "Candidate: Ananya Sharma | Role: Marketing Executive | Joining Date: 23 November\n"
            "Summary of Operational Status:\n"
            "- Laptop Provisioning: Reassigned idle unit from deferred joiner; asset log updated.\n"
            "- System Permissions: Standard RBAC marketing access approved; admin request denied in compliance with info-sec.\n"
            "- Day One Coordination: Deconflicted orientation schedule with client observation window.\n"
            "- Compliance: Provisional ID access protocol active; mandatory completion within 24 hours.\n"
            "Readiness Status: Conditionally Ready for Day One Launch."
        )
    }

    result = evaluate_onboarding_submission(workspace, answers, {"pasteCount": 0})
    assert result["overall_score"] >= 80, f"Expected score >= 80, got {result['overall_score']}"
    assert result["passed"] is True
    assert result["score_breakdown"]["operational_execution_score"] == 100
    assert result["score_breakdown"]["hr_governance_score"] >= 80


def test_onboarding_evaluator_penalizes_admin_grant():
    workspace = {
        "tracker": {
            "crmAccessDecision": "Approved administrator access as demanded by department manager",
        }
    }
    result = evaluate_onboarding_submission(workspace, {}, {"pasteCount": 0})
    crm_task = next((t for t in result["task_evaluations"] if t["id"] == "task-crm-access-policy"), None)
    assert crm_task is not None
    assert crm_task["is_correct"] is False
    assert crm_task["points_earned"] == 0


# ==============================================================================
# HR Scenario 3: Employee Complaint Tests
# ==============================================================================

def test_complaints_evaluator_high_score():
    workspace = {
        "analysis": {
            "workloadAssessment": "Contextualized project volume: elevated tickets reflected temporary coverage for absent peers and higher case complexity",
            "disclosureDecision": "Refuse full unredacted complaint sharing; provide neutral summary of concerns only to protect confidentiality",
            "retaliationSafeguards": "Issue formal interim warning against retaliation; monitor meeting invites and reinstate team communication access",
            "evidenceSynthesis": "Differentiated corroborated audit logs and substantiated timestamps from uncorroborated interpersonal opinions",
        }
    }
    answers = {
        "q1WorkloadMetricsSufficiency": (
            "Workload metrics alone do not prove unfair treatment. We must evaluate operational context, project complexity, "
            "temporary coverage during peer absence, and experience seniority. A senior associate may handle higher volume "
            "or complex tickets by design rather than as an act of discriminatory or unfair delegation."
        ),
        "q2AmbiguousWitnessInvestigation": (
            "When the primary witness cannot confirm specific verbal exchanges, the investigator must gather indirect "
            "evidence: examine the room context, review contemporaneous meeting notes and timestamps, interview other "
            "team members regarding general interactions, and look for behavioral patterns rather than relying on one uncorroborated account."
        ),
        "q3UnrecordedVerbalRequests": (
            "To investigate unrecorded verbal requests for workload relief, I will review calendar 1-on-1 meeting records, "
            "search corporate chat messages across Slack and Teams, inspect manager check-in notes, and review quarterly "
            "performance feedback logs to triangulate whether concerns were raised informally."
        ),
        "q4ManagerDisclosureConfidentiality": (
            "I will refuse to disclose Rahul's full unredacted complaint to the manager. Disclosing the raw document violates "
            "investigation confidentiality and risks witness intimidation or retaliation. Instead, I will provide a clear, neutral "
            "summary of the specific behavioral allegations and workload concerns so the manager has a fair opportunity to respond."
        ),
        "q5RetaliatoryExclusionHandling": (
            "If Rahul is excluded from essential team meetings post-complaint, HR must immediately issue an interim non-retaliation "
            "safeguard directive to the manager. We must document the meeting exclusions, provide independent oversight over project "
            "assignments, and enforce strict zero-tolerance policies against subtle retaliation."
        ),
        "q6FormalVsInformalThreshold": (
            "Formal escalation is required when allegations involve unlawful discrimination, sexual harassment, retaliatory conduct, "
            "systemic abuse of power, or bad-faith policy violations. Informal mediation is reserved strictly for minor interpersonal "
            "misunderstandings where both parties voluntarily seek coaching."
        ),
        "q7BalancedFindingsPresentation": (
            "When findings are mixed, the report must present evidence with objective neutrality: clearly state which claims were "
            "substantiated by corroborated data logs (e.g. meeting removals), distinguish unsubstantiated verbal claims, and provide "
            "balanced organizational recommendations without sensationalizing findings."
        ),
        "investigationSummaryDraft": (
            "CONFIDENTIAL WORKPLACE INVESTIGATION REPORT\n"
            "Organization: BrightEdge Solutions | Complainant: Rahul | Respondent: Vikram\n"
            "Summary of Allegations & Findings:\n"
            "1. Workload Disparity: Corroborated higher ticket volume, but contextualized by peer coverage.\n"
            "2. Retaliatory Exclusion: Substantiated removal from team meetings post-grievance; non-retaliation warning enforced.\n"
            "3. Confidentiality Safeguards: Protected complainant anonymity; shared neutral allegations summary only.\n"
            "Recommendations: Workplace mediation, client account rebalancing, and managerial leadership coaching."
        )
    }

    result = evaluate_complaint_submission(workspace, answers, {"pasteCount": 0})
    assert result["overall_score"] >= 80, f"Expected score >= 80, got {result['overall_score']}"
    assert result["passed"] is True
    assert result["score_breakdown"]["investigation_rigor_score"] == 100


def test_complaints_evaluator_penalizes_full_complaint_sharing():
    workspace = {
        "analysis": {
            "disclosureDecision": "Granted full copy of Rahul's complaint letter to manager so he can see every detail",
        }
    }
    result = evaluate_complaint_submission(workspace, {}, {"pasteCount": 0})
    conf_task = next((t for t in result["task_evaluations"] if t["id"] == "task-confidentiality-defense"), None)
    assert conf_task is not None
    assert conf_task["is_correct"] is False
    assert conf_task["points_earned"] == 0


# ==============================================================================
# HR Scenario 4: Employee Performance Review Tests
# ==============================================================================

def test_performance_evaluator_high_score():
    workspace = {
        "employees": [
            {
                "id": "perf-rahul",
                "employee": "Rahul",
                "target": 100,
                "actual": 115,
                "achievementPct": 115.0,
                "quality_score": 92.0,
                "recommendation": "Recognition + Workload Delegation Coaching"
            },
            {
                "id": "perf-priya",
                "employee": "Priya",
                "target": 100,
                "actual": 88,
                "achievementPct": 88.0,
                "quality_score": 97.0,
                "recommendation": "Protect from Negative Rating / Clarify Priority Shifts"
            },
            {
                "id": "perf-aman",
                "employee": "Aman",
                "target": 100,
                "actual": 96,
                "achievementPct": 96.0,
                "quality_score": 90.0,
                "recommendation": "Solid Performer / Handover Communication Coaching"
            },
            {
                "id": "perf-neha",
                "employee": "Neha",
                "target": 100,
                "actual": 72,
                "achievementPct": 72.0,
                "quality_score": 94.0,
                "recommendation": "Structured Enablement & System Training Before PIP"
            },
            {
                "id": "perf-karan",
                "employee": "Karan",
                "target": 100,
                "actual": 105,
                "achievementPct": 105.0,
                "quality_score": 78.0,
                "recommendation": "Quality Intervention / Formal Customer Defect Review"
            },
            {
                "id": "perf-meera",
                "employee": "Meera",
                "target": 100,
                "actual": 91,
                "achievementPct": 91.0,
                "quality_score": 96.0,
                "recommendation": "Positive Appraisal / Recognize Complex Case Resolution"
            }
        ]
    }
    answers = {
        "q1VolumeVsTotalPerformance": (
            "Exceeding volume target by 15% does not automatically warrant the highest rating. We must evaluate holistic "
            "performance including team collaboration, delegation, work sustainability, burnout risk, and mentoring newer peers "
            "rather than focusing narrowly on raw transactional speed."
        ),
        "q2PriyaQualityVsVolumeFairness": (
            "Priya achieved exceptional 95% quality while 20% of her working hours were officially redirected to cross-departmental "
            "reporting duties. A fair evaluation requires adjusting her primary target pro-rata to 400 tickets, recognizing "
            "her strong analytical reporting contributions and high quality without penalizing overall rating."
        ),
        "q3KaranQualityVsVolumeAction": (
            "Karan should not receive uncritical recognition. While his volume was 112%, his quality fell to 88% with rising "
            "customer complaints and churn risk. He requires targeted quality coaching, resolution guardrails, and sample "
            "audit reviews to re-align with organizational quality standards."
        ),
        "q4NehaSkillVsSupportDistinction": (
            "Neha's lower volume reflects a transition to a new CRM system without formal onboarding or requested training, "
            "rather than a skill gap. Her 93% quality demonstrates strong diligence. HR must provide structured software enablement, "
            "job aids, and a temporary ramp-up grace period."
        ),
        "q5MeeraTrajectoryAndComplexity": (
            "Meera achieved 90% target with elite 97% quality while handling the department's most complex escalations. Her "
            "consistent upward trajectory and mastery of difficult multi-party cases warrant a positive appraisal and "
            "complexity-weighted KPI calibration."
        ),
        "q6DevelopmentInterventionPriority": (
            "Prioritize IDP interventions for Neha (software transition training and mentoring), Karan (defect reduction coaching "
            "and customer empathy guardrails), and Priya (formalizing hybrid workload balance and analytics career pathways)."
        ),
        "q7DefendingAssessmentAgainstManager": (
            "To defend this assessment against managerial pushback, I will present objective performance data: quality metrics, "
            "customer churn correlations, cross-functional project hours, and calibration benchmarks to ensure fair, consistent "
            "evaluations across all teams."
        ),
        "performanceSynthesisDraft": (
            "QUARTERLY CUSTOMER OPERATIONS PERFORMANCE SYNTHESIS\n"
            "Organization: Vertex Solutions | Department: Customer Operations\n"
            "Key Evaluation Highlights:\n"
            "- Overall team quality remains high at 93.8%.\n"
            "- Volume disconnects addressed: Karan coaching for quality defect reduction; Priya target adjusted for reporting duties.\n"
            "- Neha supported with CRM transition training; Meera commended for high-complexity resolution.\n"
            "Action Plan: Implement complexity-weighted scorecards and customized Individual Development Plans."
        )
    }

    result = evaluate_performance_submission(workspace, answers, {"pasteCount": 0})
    assert result["overall_score"] >= 80, f"Expected score >= 80, got {result['overall_score']}"
    assert result["passed"] is True
    assert result["score_breakdown"]["performance_analytics_score"] == 100


# ==============================================================================
# HR Scenario 5: Employee Training Tests
# ==============================================================================

def test_training_evaluator_high_score():
    workspace = {
        "plan": {
            "groupingDecision": "Reorganize Group C: enforce prerequisites based on baseline assessment scores",
            "operationalScheduling": "Stagger training into 2 rotational cohorts: guarantee >=80% support coverage and <=3 sales reps per batch",
            "internalTrainerStrategy": "Deploy 2 internal champions for basic navigation modules and peer coaching",
            "totalBudgetCost": 28500,
        }
    }
    answers = {
        "q1ReorganizeVsOriginalGroups": (
            "We must reorganise employees based on individual diagnostic assessment scores rather than following the original "
            "groupings. Placing employees without core fundamentals into advanced Group C creates cognitive overload, high failure "
            "rates, and wastes training investments. Prerequisite mastery is essential."
        ),
        "q2AdvancedReadinessCriteria": (
            "Readiness for advanced training requires clearing formal prerequisite benchmarks: passing a diagnostic skills "
            "assessment, demonstrating hands-on sandbox test simulation accuracy, and error-free record management in core workflows."
        ),
        "q3InternalTrainerTradeoffs": (
            "Deploying internal champions generates significant cost savings and fosters peer trust, while ensuring practical domain "
            "expertise. The trade-offs include curriculum preparation time and opportunity cost away from day-to-day operations, "
            "which can be balanced through a hybrid trainer model."
        ),
        "q4SupportCapacityScheduling": (
            "To safeguard customer service SLAs, we schedule training across staggered rotational cohorts: maintaining at least "
            "80% active staffing on the support helpdesk at all times, staggering peak hours, and capping sales attendance at 3 reps per batch."
        ),
        "q5BudgetCriticalContingency": (
            "If the budget faces a 20% cut to ₹24,000, we will retain core hands-on classroom modules for advanced users, internalize "
            "basic navigation using internal champions and digital microlearning, and defer non-essential external vendor add-ons."
        ),
        "q6MeasuringActualProficiency": (
            "To measure actual CRM proficiency beyond satisfaction surveys, we will implement Kirkpatrick level 2 and 3 evaluations: "
            "timed sandbox simulation tasks, system completion rates, audit error rate tracking, and 30-day workflow adoption metrics."
        ),
        "q7PostRolloutRemediation": (
            "If errors persist post-rollout, provide targeted remediation: dedicated internal champion floor support and office hours, "
            "searchable microlearning job aids, peer shadowing clinics, and root-cause analysis of interface process friction."
        ),
        "trainingProposalDraft": (
            "ENTERPRISE CRM TRAINING & ENABLEMENT PROPOSAL\n"
            "Organization: Orbit Business Solutions | Target: 20 Employees | Budget: ₹28,500 (Within ₹30,000 Limit)\n"
            "Key Strategy Elements:\n"
            "1. Group Reorganization: Competency-based grouping with enforced prerequisite assessments.\n"
            "2. Operational SLAs: Staggered cohort schedule protecting >=80% support desk coverage.\n"
            "3. Internal Champions: Deployed 2 super-users for basic modules and continuous floor coaching.\n"
            "4. Measurement & Governance: Kirkpatrick proficiency metrics and 20% budget reduction contingency."
        )
    }

    result = evaluate_training_submission(workspace, answers, {"pasteCount": 0})
    assert result["overall_score"] >= 80, f"Expected score >= 80, got {result['overall_score']}"
    assert result["passed"] is True
    assert result["score_breakdown"]["instructional_design_score"] == 100


def test_training_evaluator_penalizes_budget_overrun():
    workspace = {
        "plan": {
            "totalBudgetCost": 38000,
        }
    }
    result = evaluate_training_submission(workspace, {}, {"pasteCount": 0})
    cost_task = next((t for t in result["task_evaluations"] if t["id"] == "task-budget-governance"), None)
    assert cost_task is not None
    assert cost_task["is_correct"] is False
    assert cost_task["points_earned"] == 0


# ==============================================================================
# Dispatcher Integration Tests
# ==============================================================================

def test_unified_evaluate_submission_dispatches_new_hr_scenarios():
    onboarding_res = evaluate_submission(
        category="hr",
        workspace_snapshot={},
        answers={"q1PreVsPostJoining": "test"},
        integrity_flags={"pasteCount": 0},
        environment_slug="hr-employee-onboarding",
    )
    assert "score_breakdown" in onboarding_res

    complaints_res = evaluate_submission(
        category="hr",
        workspace_snapshot={},
        answers={"q1WorkloadMetricsSufficiency": "test"},
        integrity_flags={"pasteCount": 0},
        environment_slug="hr-complaint-investigation",
    )
    assert "score_breakdown" in complaints_res

    perf_res = evaluate_submission(
        category="hr",
        workspace_snapshot={},
        answers={"q1VolumeVsTotalPerformance": "test"},
        integrity_flags={"pasteCount": 0},
        environment_slug="hr-performance-review",
    )
    assert "score_breakdown" in perf_res

    training_res = evaluate_submission(
        category="hr",
        workspace_snapshot={},
        answers={"q1ReorganizeVsOriginalGroups": "test"},
        integrity_flags={"pasteCount": 0},
        environment_slug="hr-training-planning",
    )
    assert "score_breakdown" in training_res
