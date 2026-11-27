"""
Unit tests for HR Subrole 1 (Talent Acquisition Specialist) scenarios:
1. Scenario 1.2: HR — Managing a Difficult Hiring Requirement (hr-hiring-requirement)
2. Scenario 1.3: HR — Managing an Interview Pipeline and Hiring Decision (hr-interview-pipeline)
"""

import pytest
from app.evaluators import evaluate_submission


def test_hiring_requirement_perfect_submission():
    workspace_snapshot = {
        "requisitionAnalysis": {
            "totalPositions": 6,
            "teamLeadPositions": 2,
            "icPositions": 4,
            "revisedIcSalaryBand": "₹3,50,000 - ₹3,80,000",
            "revisedLeadSalaryBand": "₹4,50,000 - ₹5,00,000",
        },
        "positionsTracker": [
            {"id": "pos-1", "title": "Shift Team Lead", "tier": "Team Lead", "expRequired": "3-5 Years", "salaryBand": "₹4.5 - ₹5.0 LPA", "priority": "Wave 1 (Day 20)", "assignedRecruiter": "Pooja Rao", "status": "Sourcing Active"},
            {"id": "pos-2", "title": "Customer Support IC 1", "tier": "Individual Contributor", "expRequired": "1-2 Years", "salaryBand": "₹3.5 - ₹3.8 LPA", "priority": "Wave 1 (Day 20)", "assignedRecruiter": "Amit Sen", "status": "Sourcing Active"},
            {"id": "pos-3", "title": "Customer Support IC 2", "tier": "Individual Contributor", "expRequired": "1-2 Years", "salaryBand": "₹3.5 - ₹3.8 LPA", "priority": "Wave 1 (Day 20)", "assignedRecruiter": "Amit Sen", "status": "Sourcing Active"},
            {"id": "pos-4", "title": "Shift Team Lead", "tier": "Team Lead", "expRequired": "3-5 Years", "salaryBand": "₹4.5 - ₹5.0 LPA", "priority": "Wave 2 (Day 30)", "assignedRecruiter": "Pooja Rao", "status": "Sourcing Active"},
            {"id": "pos-5", "title": "Customer Support IC 3", "tier": "Individual Contributor", "expRequired": "1-2 Years", "salaryBand": "₹3.5 - ₹3.8 LPA", "priority": "Wave 2 (Day 30)", "assignedRecruiter": "Amit Sen", "status": "Sourcing Active"},
            {"id": "pos-6", "title": "Customer Support IC 4", "tier": "Individual Contributor", "expRequired": "1-2 Years", "salaryBand": "₹3.5 - ₹3.8 LPA", "priority": "Wave 2 (Day 30)", "assignedRecruiter": "Pooja Rao", "status": "Sourcing Active"},
        ],
    }

    answers = {
        "managerDisagreementResolution": (
            "I would present empirical workforce plan data and past retention metrics demonstrating that "
            "associates with 1-2 years experience achieve equal CSAT while staying longer. By separating the 2 "
            "team leads from the 4 IC positions, we protect delivery without creating artificial candidate shortages."
        ),
        "budgetSalaryRecommendations": (
            "I would recommend re-allocating the total compensation pool into tiered salary bands: offering ₹3.5-3.8 LPA "
            "for the 4 ICs and reserving ₹4.8-5.0 LPA for the 2 Team Leads, accompanied by quarterly performance bonuses "
            "and joining flexibility to attract top talent without inflating overall budget."
        ),
        "essentialVsPreferredSeparation": (
            "Separating essential from preferred requirements broadens the candidate talent pool, avoids artificial barrier "
            "inflation, ensures diverse applicant flow, and provides an objective rubric for interview scorecards."
        ),
        "recruiterCapacityPrioritization": (
            "With 2 recruiters, we must stage recruitment in two waves: prioritize Wave 1 (1 Lead + 2 ICs) needed in 20 days "
            "for Project Apex, assign distinct role portfolios (Pooja leads Team Leads, Amit leads ICs), and launch employee referral sprints."
        ),
        "unsubstantiatedRejectionHandling": (
            "I would arrange an alignment check-in with the hiring manager, reference agreed objective scorecard rubrics, "
            "and request specific, job-related feedback to prevent arbitrary rejections and protect candidate experience."
        ),
        "recruitmentMetricMonitoring": (
            "I would monitor leading funnel metrics weekly: sourcing-to-screen conversion, screen-to-interview pass-through velocity, "
            "and candidate drop-off rates at Day 10 and Day 15 checkpoints to course-correct before the 30-day SLA deadline."
        ),
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="hr",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="hr-hiring-requirement",
    )

    assert result["passed"] is True
    assert result["overall_score"] >= 85
    assert result["score_breakdown"]["recruitment_planning"] == 100
    assert len(result["task_evaluations"]) == 4
    for task in result["task_evaluations"]:
        assert task["status"] == "PASS"


def test_hiring_requirement_unseparated_failure():
    workspace_snapshot = {
        "requisitionAnalysis": {
            "totalPositions": 6,
            "teamLeadPositions": 6,
            "icPositions": 0,
        },
        "positionsTracker": [
            {"id": "pos-1", "title": "Customer Ops", "tier": "Team Lead", "priority": "Standard", "salaryBand": "₹3.5 LPA"},
        ],
    }

    answers = {
        "managerDisagreementResolution": "Just do what the manager says.",
        "budgetSalaryRecommendations": "Ask for more money.",
        "essentialVsPreferredSeparation": "Not important.",
        "recruiterCapacityPrioritization": "Hire more recruiters.",
        "unsubstantiatedRejectionHandling": "Accept rejection.",
        "recruitmentMetricMonitoring": "Wait for 30 days.",
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="hr",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="hr-hiring-requirement",
    )

    assert result["passed"] is False
    assert result["score_breakdown"]["recruitment_planning"] < 50


def test_interview_pipeline_perfect_submission():
    workspace_snapshot = {
        "candidateActions": [
            {"id": "cand-a", "candidate": "Candidate A", "stage": "Final Leadership", "status": "Blocked", "action": "Fast-track VP final leadership interview within 24h", "rating": 4.5},
            {"id": "cand-b", "candidate": "Candidate B", "stage": "Hiring Manager", "status": "Discrepancy", "action": "Calibration sync on objection handling ratings", "rating": 3.5},
            {"id": "cand-c", "candidate": "Candidate C", "stage": "Hiring Manager", "status": "Reschedule", "action": "Reschedule interview to Friday 3:00 PM per candidate request", "rating": 3.8},
            {"id": "cand-d", "candidate": "Candidate D", "stage": "Final Leadership", "status": "CTC Mismatch", "action": "Negotiate base ₹5.0L cap plus quarterly sales commission incentives", "rating": 4.6},
            {"id": "cand-e", "candidate": "Candidate E", "stage": "Withdrawn", "status": "Drop-off", "action": "Log root cause: Process latency", "rating": 3.9},
            {"id": "cand-f", "candidate": "Candidate F", "stage": "Hiring Manager", "status": "Overdue", "action": "Execute SLA follow-up phone sync with Suresh for missing evaluation form", "rating": 4.1},
            {"id": "cand-g", "candidate": "Candidate G", "stage": "Evaluation Review", "status": "Under-review", "action": "Review underlying 90% renewal track record; retain in backup shortlist", "rating": 3.2},
            {"id": "cand-h", "candidate": "Candidate H", "stage": "Withdrawn", "status": "Drop-off", "action": "Log root cause: Competitive offer", "rating": 4.3},
        ],
    }

    answers = {
        "conflictingFeedbackHandling": (
            "I would convene a structured 15-minute calibration session between both interviewers to examine "
            "concrete behavioral evidence regarding objection handling, rather than rejecting the candidate on uncalibrated subjective scores."
        ),
        "overBudgetCandidateManagement": (
            "For Candidate D, I would maintain base salary at the approved ₹5.0 LPA cap while structuring an "
            "incentive package with quarterly performance bonuses, bridging the compensation expectation while protecting internal equity."
        ),
        "missingFeedbackEscalation": (
            "I would initiate a quick phone sync with hiring manager Suresh, offer a verbal 3-point scorecard template, "
            "and remind them of the 24-hour SLA turnaround to prevent high-potential candidate drop-off."
        ),
        "holisticVsNumericalScoring": (
            "A single numerical score can be depressed by temporary interview anxiety. Reviewing holistic track record "
            "evidence (such as Candidate G's 90% client renewal rate) ensures proven revenue capability is not discarded."
        ),
        "reducingCandidateDropoff": (
            "To reduce candidate drop-off, enforce 48-hour interview turnaround SLAs, pre-reserve leadership interview blocks "
            "on executive calendars, and maintain proactive weekly touchpoint communications with all active candidates."
        ),
        "balancingSpeedAndRigor": (
            "To balance speed and rigor under 3-day sales pressure, fast-track scheduling for validated frontrunners (Candidate A) "
            "while upholding standardized rubric scorecards to avoid premature, unverified hiring compromises."
        ),
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="hr",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="hr-interview-pipeline",
    )

    assert result["passed"] is True
    assert result["overall_score"] >= 85
    assert result["score_breakdown"]["pipeline_resolution"] == 100
    assert len(result["task_evaluations"]) == 6
    for task in result["task_evaluations"]:
        assert task["status"] == "PASS"


def test_interview_pipeline_bottleneck_unresolved():
    workspace_snapshot = {
        "candidateActions": [
            {"id": "cand-a", "candidate": "Candidate A", "action": "Do nothing"},
            {"id": "cand-b", "candidate": "Candidate B", "action": "Reject immediately"},
            {"id": "cand-c", "candidate": "Candidate C", "action": "Cancel interview"},
            {"id": "cand-d", "candidate": "Candidate D", "action": "Pay ₹7.5 LPA"},
            {"id": "cand-f", "candidate": "Candidate F", "action": "Wait indefinitely"},
            {"id": "cand-g", "candidate": "Candidate G", "action": "Reject"},
        ],
    }

    answers = {
        "conflictingFeedbackHandling": "Just reject.",
        "overBudgetCandidateManagement": "Pay whatever.",
        "missingFeedbackEscalation": "Do not follow up.",
        "holisticVsNumericalScoring": "Numbers only.",
        "reducingCandidateDropoff": "Nothing.",
        "balancingSpeedAndRigor": "Hire immediately.",
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="hr",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="hr-interview-pipeline",
    )

    assert result["passed"] is False
    assert result["score_breakdown"]["pipeline_resolution"] < 50
