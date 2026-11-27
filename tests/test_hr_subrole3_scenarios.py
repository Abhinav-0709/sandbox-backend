"""
Unit tests for HR Subrole 3 (Employee Relations Associate) scenarios:
1. Scenario 3.1: HR — Investigating a Workplace Complaint (hr-complaint-investigation)
2. Scenario 3.2: HR — Managing a Disciplinary Case and Policy Violation (hr-disciplinary-investigation)
"""

import pytest
from app.evaluators import evaluate_submission


def test_complaint_investigation_perfect_submission():
    workspace_snapshot = {
        "caseOverview": {
            "caseId": "ER-2026-088",
            "complainant": "Priya Sharma (Customer Operations Associate)",
            "respondent": "Vikram Seth (Team Manager)",
            "dateFiled": "17-Nov-2026",
            "status": "Active Investigation",
        },
        "incidentTimeline": [
            {
                "id": "inc-1",
                "date": "04-Nov-2026",
                "allegedIncident": "Public criticism during pipeline meeting",
                "managerPosition": "Direct feedback on data calculation errors",
                "witnessCorroboration": "Witness A confirms voice was raised; Witness B notes mutual defensiveness",
                "preliminaryAssessment": "Policy breach risk: Feedback delivered in public setting violating Sec 3.1 of Respectful Workplace policy.",
            },
            {
                "id": "inc-2",
                "date": "08-Nov-2026",
                "allegedIncident": "Short-notice assignment of 3 churn decks on Friday 16:45",
                "managerPosition": "Client Apex shifted audit deadline; all team surge",
                "witnessCorroboration": "Workload data shows team-wide surge; Priya +1.5 tickets",
                "preliminaryAssessment": "Operational justification confirmed by Apex client deadline shift; not targeted harassment.",
            },
            {
                "id": "inc-3",
                "date": "12-Nov-2026",
                "allegedIncident": "Comment on personal commitments during standup",
                "managerPosition": "General reminder on sprint accountability",
                "witnessCorroboration": "Inconclusive; Witness B recalls general focus comment",
                "preliminaryAssessment": "Requires 1-on-1 interview with Vikram to assess exact phrase used under personal boundary policy.",
            },
            {
                "id": "inc-4",
                "date": "15-Nov-2026",
                "allegedIncident": "Excluded from Apex project discussion",
                "managerPosition": "Ad-hoc backend API technical sync, not account review",
                "witnessCorroboration": "Meeting invite confirms attendees were technical roles",
                "preliminaryAssessment": "Legitimate technical meeting; poor communication by manager regarding agenda.",
            },
        ],
        "interimMeasures": {
            "reportingLine": "Temporary dotted-line reporting to Operations Lead for project submissions during investigation",
            "meetingProtocol": "All 1-on-1 performance meetings between Priya and Vikram suspended or attended by HR representative with strict confidential reporting",
            "nonRetaliationAdvisory": "Issued formal written non-retaliation advisory warning to Vikram Seth and Department Head to protect complainant",
        },
        "investigationReportSummary": {
            "confirmedFacts": "Manager raised voice in public meeting on 4-Nov; tasks assigned on 8-Nov were driven by genuine Apex deadline shift; 15-Nov meeting was technical sync.",
            "disputedStatements": "Exact words spoken regarding personal commitments on 12-Nov; whether Priya was singled out for criticism.",
            "recommendedNextSteps": "1. Conduct separate structured interviews with Priya, Vikram, and both witnesses. 2. Provide Vikram with itemized summary of allegations. 3. Maintain interim reporting safeguards. 4. Deliver formal findings to HR Director.",
        },
    }

    answers = {
        "performanceReviewComplaintValidity": (
            "Prior documented performance concerns do not invalidate a workplace grievance because workplace conduct and performance "
            "management operate under separate policy standards. Managers must deliver constructive feedback privately and professionally; "
            "poor performance does not excuse public humiliation or violations of employee dignity."
        ),
        "conflictingWitnessAccountsAssessment": (
            "To assess conflicting witness statements, HR must triangulate accounts against contemporaneous digital notes, analyze the "
            "physical positioning and potential interpersonal bias of each witness, and isolate common objective facts from subjective "
            "interpretations of tone and intent."
        ),
        "confidentialityFairInvestigationBalance": (
            "HR balances confidentiality with procedural fairness by operating under strict need-to-know principles. While natural justice "
            "requires giving the respondent notice of the substantive allegations, HR protects the complainant by redacting verbatim text "
            "and establishing anti-retaliation safeguards."
        ),
        "managerCompleteComplaintRequestHandling": (
            "Under HR-SOP-008, HR should politely withhold the raw, verbatim complaint letter to prevent retaliation. Instead, HR must "
            "provide the manager with an itemized, factual written summary of each specific allegation and incident date so they can prepare "
            "a thorough defense."
        ),
        "unprovenMisconductCommunication": (
            "If evidence does not substantiate formal misconduct, HR should communicate neutrally to both parties that allegations were "
            "unsubstantiated, while providing management coaching on communication style, conduct policy reminders, and reiterating strict "
            "non-retaliation protections."
        ),
        "operationalPressureInfluenceInvestigation": (
            "Operational delivery pressure must never compromise or truncate investigative due process. While HR can implement interim "
            "working safeguards to keep business operations on track, the investigation must remain impartial, thorough, and fair regardless "
            "of client deadlines."
        ),
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="hr",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="hr-complaint-investigation",
    )

    assert result["passed"] is True
    assert result["overall_score"] >= 85
    assert result["score_breakdown"]["grievance_investigation"] == 100
    assert len(result["task_evaluations"]) == 5
    for task in result["task_evaluations"]:
        assert task["status"] == "PASS"


def test_complaint_investigation_failure():
    workspace_snapshot = {
        "incidentTimeline": [
            {
                "id": "inc-1",
                "preliminaryAssessment": "Ignore complaint because manager was just managing performance.",
            }
        ],
        "interimMeasures": {
            "reportingLine": "No action needed.",
            "meetingProtocol": "Give full complaint letter to manager immediately.",
        },
    }

    answers = {
        "performanceReviewComplaintValidity": "Yes, poor performers cannot complain.",
        "conflictingWitnessAccountsAssessment": "Believe the manager.",
        "confidentialityFairInvestigationBalance": "Give everything to the manager.",
        "managerCompleteComplaintRequestHandling": "Hand over the full letter immediately.",
        "unprovenMisconductCommunication": "Fire the employee.",
        "operationalPressureInfluenceInvestigation": "Close case immediately for client.",
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="hr",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="hr-complaint-investigation",
    )

    assert result["passed"] is False
    assert result["overall_score"] < 50


def test_disciplinary_investigation_perfect_submission():
    workspace_snapshot = {
        "disciplinaryCase": {
            "caseId": "DISC-2026-042",
            "employee": "Rahul Mehta (Senior Sales Executive)",
            "reportingManager": "Rajesh Khanna (Sales Manager)",
            "incidentDate": "18-Nov-2026",
            "allegation": "Unauthorized external transmission of Class 3 Confidential Customer Pricing model to non-whitelisted personal Gmail address breaching POL-SEC-004",
            "itSeverity": "High DLP Trigger",
        },
        "evidenceTimeline": [
            {"id": "ev-1", "time": "16:32 IST", "activity": "User logged into SharePoint Sales Repository", "source": "SharePoint Access Log", "verified": True},
            {"id": "ev-2", "time": "16:35 IST", "activity": "Downloaded Customer_Pricing_November.xlsx", "source": "File System Audit", "verified": True},
            {"id": "ev-3", "time": "16:42 IST", "activity": "Emailed spreadsheet to rajiv.consult@gmail.com", "source": "Exchange Mail Trace", "verified": True},
            {"id": "ev-4", "time": "16:45 IST", "activity": "DLP rule violation flagged by IT Security Ops", "source": "DLP System Alert", "verified": True},
            {"id": "ev-5", "time": "17:15 IST", "activity": "External recipient opened document via link", "source": "Google Workspace Link Audit", "verified": True},
        ],
        "mitigatingAggravatingMatrix": {
            "mitigatingFactors": [
                "3-year unblemished record with zero prior disciplinary marks",
                "Believed in good faith that consultant Rajiv Sen was authorized for RFP proposal preparation",
                "No evidence of secondary dissemination, commercial leak, or competitor collusion",
                "Missed mandatory 2026 data classification training module (organizational tracking gap)",
                "Immediate admission of facts, remorse, and full cooperation with IT forensics",
            ],
            "aggravatingFactors": [
                "High sensitivity of transmitted document (Class 3 master pricing and margins)",
                "Transmission sent to an unencrypted, personal Gmail address",
                "Lack of written verification before sending sensitive company asset",
            ],
        },
        "hearingNoticeDraft": {
            "recipient": "Rahul Mehta",
            "hearingDate": "24-Nov-2026 14:00 IST",
            "location": "HR Conference Room B / Video Hybrid",
            "chairperson": "Head of Employee Relations",
            "charges": "Alleged breach of POL-SEC-004 (Section 5.1) and Code of Conduct (Section 6) for unauthorized Class 3 data transmission",
            "rightsStatement": "You are entitled to be accompanied by a workplace colleague or accredited employee representative under DISC-SOP-002.",
        },
        "handoverRecommendations": {
            "recommendedSanction": "Final Written Warning with 12-month validity (Rejects summary termination without proof of malicious intent)",
            "correctiveRemediation": "Mandatory completion of Advanced Data Classification module and 60-day DLP monitoring",
            "processImprovements": "Audit external consultant NDAs, enforce corporate email whitelisting, and block personal domains at gateway",
        },
    }

    answers = {
        "verbalApprovalClaimInvestigation": (
            "To investigate the verbal approval claim, HR must interview external consultant Rajiv Sen regarding the proposal context, "
            "inspect Slack and email communication threads, and verify whether a formal NDA was executed, while establishing that verbal "
            "guidance cannot override written information security policy."
        ),
        "recipientAccessIntentDelineation": (
            "Recipient access confirms data exposure and a policy breach, but it does not automatically establish malicious intent or "
            "corporate espionage. HR must delineate technical breach from deliberate bad faith by examining exfiltration patterns and "
            "good faith reliance on commercial proposal duties."
        ),
        "prejudgedTerminationProceduralFairness": (
            "HR must resist demands for immediate termination because pre-judging outcomes violates natural justice and procedural "
            "fairness under DISC-SOP-002. Terminating an employee without a formal hearing and opportunity to present mitigating evidence "
            "exposes the company to severe legal liability for unfair dismissal."
        ),
        "incompleteTrainingAssessmentInfluence": (
            "The employee's incomplete 2026 confidentiality training module highlights an organizational compliance tracking lapse. "
            "While it does not excuse the policy breach, it serves as a significant mitigating factor showing lack of recent instruction, "
            "which weighs heavily against classifying the act as willful gross misconduct."
        ),
        "policyViolationVsSeverityDelineation": (
            "Evidence of a policy violation establishes the technical fact of non-compliance (such as IT DLP logs proving file transmission). "
            "In contrast, severity evidence evaluates contextual intent, actual commercial harm, mitigating factors, and past conduct to "
            "determine a proportional sanction."
        ),
        "unintentionalViolationDisciplinaryFactors": (
            "When a violation lacks malicious intent, HR should consider Rahul's 3-year unblemished record, genuine remorse, full cooperation "
            "with IT, the absence of secondary data leakage, and recommend a proportional graduated sanction such as a Written Warning with "
            "mandatory training remediation."
        ),
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="hr",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="hr-disciplinary-investigation",
    )

    assert result["passed"] is True
    assert result["overall_score"] >= 85
    assert result["score_breakdown"]["disciplinary_process"] == 100
    assert len(result["task_evaluations"]) == 5
    for task in result["task_evaluations"]:
        assert task["status"] == "PASS"


def test_disciplinary_investigation_failure():
    workspace_snapshot = {
        "disciplinaryCase": {
            "caseId": "DISC-2026-042",
        },
        "mitigatingAggravatingMatrix": {
            "mitigatingFactors": [],
        },
        "hearingNoticeDraft": {
            "charges": "Fired immediately.",
            "rightsStatement": "No rights.",
        },
        "handoverRecommendations": {
            "recommendedSanction": "Immediate termination recommended without hearing.",
        },
    }

    answers = {
        "verbalApprovalClaimInvestigation": "Don't bother checking.",
        "recipientAccessIntentDelineation": "Opening means guilty of espionage.",
        "prejudgedTerminationProceduralFairness": "Fire him now.",
        "incompleteTrainingAssessmentInfluence": "Irrelevant.",
        "policyViolationVsSeverityDelineation": "No difference.",
        "unintentionalViolationDisciplinaryFactors": "Termination always.",
    }

    integrity_flags = {"paste_count": 0}

    result = evaluate_submission(
        category="hr",
        workspace_snapshot=workspace_snapshot,
        answers=answers,
        integrity_flags=integrity_flags,
        environment_slug="hr-disciplinary-investigation",
    )

    assert result["passed"] is False
    assert result["overall_score"] < 50
