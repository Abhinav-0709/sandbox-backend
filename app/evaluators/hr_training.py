"""
Evaluator for Scenario 5: HR — Planning Employee Training
Organization: Orbit Business Solutions
Role: Learning and Development Coordinator
Subject: Enterprise CRM Rollout Training Strategy & Resource Allocation
"""

from __future__ import annotations
from typing import Dict, Any, List, Optional
from app.evaluators.anti_cheat import evaluate_integrity
from app.evaluators.ai_assisted import evaluate_rubric_questions, evaluate_rubric_questions_async, AiRubricEvaluator


TRAINING_PLAN_CHECKS = [
    {
        "id": "task-regrouping-competency",
        "title": "Skill-Based Employee Re-Grouping",
        "expected_decision": "Reorganize Groups (Remediate Premature Advanced Placement)",
        "acceptable_decisions": ["Reorganize Groups (Remediate Premature Advanced Placement)", "Re-group Based on True Competency", "Remediate Group C"],
        "points": 20,
        "explanation": "Identified that employees in Group C lacked foundational CRM operations. Reorganizing based on verified diagnostic skill assessments prevents training failure and budget waste.",
    },
    {
        "id": "task-operational-staffing",
        "title": "Customer Support (80%) & Sales (<=3) Shift Protection",
        "expected_decision": "Staggered Shift Scheduling Adhering to SLAs",
        "acceptable_decisions": ["Staggered Shift Scheduling Adhering to SLAs", "Maintain Support >=80% & Sales <=3", "Staggered Cohorts"],
        "points": 20,
        "explanation": "Constructed a staggered rotational schedule ensuring Customer Support maintains >=80% active headcount and Sales has no more than 3 representatives absent concurrently.",
    },
    {
        "id": "task-internal-trainer-leverage",
        "title": "Internal Trainer Utilization & Cost Optimization",
        "expected_decision": "Deploy 2 Internal Champions for Basic CRM / Peer Labs",
        "acceptable_decisions": ["Deploy 2 Internal Champions for Basic CRM / Peer Labs", "Hybrid Internal/External Model", "Leverage Internal SMEs"],
        "points": 20,
        "explanation": "Leveraged the 2 proficient internal employees to deliver basic module walkthroughs and peer shadowing, optimizing budget expenditure.",
    },
    {
        "id": "task-budget-governance",
        "title": "Budget Ceiling Adherence (<= ₹30,000) & 20% Cut Contingency",
        "expected_decision": "Total Cost Within ₹30,000 with Viable ₹24,000 Contingency",
        "acceptable_decisions": ["Total Cost Within ₹30,000 with Viable ₹24,000 Contingency", "Compliant Budget with Internal Offset"],
        "points": 20,
        "explanation": "Calculated total training costs strictly within the ₹30,000 allocation while formulating a viable contingency if reduced by 20% (to ₹24,000).",
    },
]

TRAINING_QUESTION_RUBRICS = [
    {
        "id": "q1",
        "field": "q1ReorganizeVsOriginalGroups",
        "question": "Q1: Would you follow the original training groups or reorganise employees based on individual skill assessments? Explain your decision.",
        "keywords": ["reorganise", "individual", "assessment", "prerequisite", "group c", "fundamental", "competency", "diagnostic"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q2",
        "field": "q2AdvancedReadinessCriteria",
        "question": "Q2: How would you determine whether an employee is ready for advanced training?",
        "keywords": ["prerequisite", "benchmark", "diagnostic", "assessment", "simulation", "accuracy", "readiness", "test"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q3",
        "field": "q3InternalTrainerTradeoffs",
        "question": "Q3: Is it financially sensible to use internal trainers instead of external providers? What costs and risks would you consider?",
        "keywords": ["opportunity", "champion", "expertise", "preparation", "savings", "peer", "internal", "trainer"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q4",
        "field": "q4SupportCapacityScheduling",
        "question": "Q4: How would you schedule training without reducing the operational capacity of Customer Support below the required level?",
        "keywords": ["80%", "rotational", "staggered", "batches", "coverage", "support", "sla", "sales"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q5",
        "field": "q5BudgetCriticalContingency",
        "question": "Q5: If the training budget were reduced by 20%, which activities would you retain, modify or postpone?",
        "keywords": ["cut", "24000", "20%", "internal", "contingency", "hybrid", "core", "budget"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q6",
        "field": "q6MeasuringActualProficiency",
        "question": "Q6: How would you measure actual CRM proficiency rather than relying only on employee satisfaction surveys?",
        "keywords": ["sandbox", "simulation", "completion", "error", "logs", "proficiency", "kirkpatrick", "assessment"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q7",
        "field": "q7PostRolloutRemediation",
        "question": "Q7: What would you recommend if employees completed the training but continued making significant errors during the CRM rollout?",
        "keywords": ["office hours", "support", "super", "microlearning", "coaching", "remediation", "champion", "clinics"],
        "required_keywords": 3,
        "min_word_count": 35,
        "max_score": 10,
    },
    {
        "id": "q_proposal",
        "field": "trainingProposalDraft",
        "question": "CRM Training & Enablement Proposal: Formal executive L&D proposal for Orbit leadership detailing schedule, budget, and business KPIs.",
        "keywords": ["crm", "training", "orbit", "budget", "staggered", "schedule", "outcomes", "proposal", "enablement"],
        "required_keywords": 3,
        "min_word_count": 45,
        "max_score": 15,
    },
]


def evaluate_training_submission(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
) -> Dict[str, Any]:
    task_evaluations, total_task_pts, max_task_pts = _evaluate_training_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = evaluate_rubric_questions(
        TRAINING_QUESTION_RUBRICS, answers, evaluator=None, context="Orbit Business Solutions: Enterprise CRM Training Strategy & Resource Allocation"
    )

    return _build_training_result(
        task_evaluations, q_evals, total_task_pts, max_task_pts, total_q, max_q, answers, integrity_flags, "deterministic"
    )


async def evaluate_training_submission_async(
    workspace_snapshot: Dict[str, Any],
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    ai_evaluator: Optional[AiRubricEvaluator] = None,
) -> Dict[str, Any]:
    task_evaluations, total_task_pts, max_task_pts = _evaluate_training_tasks(workspace_snapshot)

    q_evals, total_q, max_q, any_ai = await evaluate_rubric_questions_async(
        TRAINING_QUESTION_RUBRICS, answers, evaluator=ai_evaluator, context="Orbit Business Solutions: Enterprise CRM Training Strategy & Resource Allocation"
    )

    return _build_training_result(
        task_evaluations, q_evals, total_task_pts, max_task_pts, total_q, max_q, answers, integrity_flags, "hybrid_ai" if any_ai else "deterministic"
    )


def _evaluate_training_tasks(workspace_snapshot: Dict[str, Any]) -> tuple[List[Dict[str, Any]], int, int]:
    plan = workspace_snapshot.get("trainingPlan", workspace_snapshot.get("plan", workspace_snapshot.get("proposal", workspace_snapshot)))
    task_evaluations = []
    total_pts = 0
    max_pts = 0

    # 1. Regrouping
    max_pts += 20
    regroup_eval = str(plan.get("groupingDecision", "")).strip().lower()
    regroup_ok = any(w in regroup_eval for w in ["reorganiz", "re-group", "regroup", "assessment", "prerequisite", "individual", "actual skill"])
    pts_regroup = 20 if regroup_ok else 5
    total_pts += pts_regroup
    task_evaluations.append({
        "id": "task-regrouping-competency",
        "title": "Competency-Driven Employee Re-Grouping",
        "expected_decision": "Reorganize Groups to Enforce Prerequisites",
        "actual_decision": plan.get("groupingDecision", "Evaluated"),
        "is_correct": regroup_ok,
        "points_earned": pts_regroup,
        "max_points": 20,
        "explanation": "Correctly diagnosed that placing foundational-lacking employees into Advanced CRM modules wastes capital and damages adoption." if regroup_ok else "Missed the assessment mismatch in Group C.",
    })

    # 2. Staffing
    max_pts += 20
    staffing_eval = str(plan.get("operationalScheduling", "")).strip().lower()
    staffing_ok = any(w in staffing_eval for w in ["80%", "stagger", "rotation", "sales 3", "two batches", "coverage", "cohort"])
    pts_staffing = 20 if staffing_ok else 5
    total_pts += pts_staffing
    task_evaluations.append({
        "id": "task-operational-staffing",
        "title": "Customer Support (>=80%) & Sales (<=3) Shift Safeguards",
        "expected_decision": "Staggered Rotational Cohorts",
        "actual_decision": plan.get("operationalScheduling", "Evaluated"),
        "is_correct": staffing_ok,
        "points_earned": pts_staffing,
        "max_points": 20,
        "explanation": "Demonstrated operational rigor: scheduled training in staggered cohorts preserving SLA and coverage benchmarks." if staffing_ok else "Schedule failed to explicitly protect Support 80% coverage limits.",
    })

    # 3. Internal trainer
    max_pts += 20
    trainer_eval = str(plan.get("internalTrainerStrategy", "")).strip().lower()
    trainer_ok = any(w in trainer_eval for w in ["internal", "champion", "peer", "hybrid", "sme", "basic"])
    pts_trainer = 20 if trainer_ok else 5
    total_pts += pts_trainer
    task_evaluations.append({
        "id": "task-internal-trainer-leverage",
        "title": "Internal Champion Leverage & Cost Optimization",
        "expected_decision": "Deploy 2 Internal Champions for Basic / Shadowing Modules",
        "actual_decision": plan.get("internalTrainerStrategy", "Evaluated"),
        "is_correct": trainer_ok,
        "points_earned": pts_trainer,
        "max_points": 20,
        "explanation": "Captured organizational efficiencies by pairing internal subject matter experts with external specialized instructors." if trainer_ok else "Overlooked internal training capacity.",
    })

    # 4. Budget
    max_pts += 20
    cost_val = float(plan.get("totalBudgetCost", plan.get("totalCost", 0)) or 0)
    budget_ok = 0 < cost_val <= 30000
    pts_budget = 20 if budget_ok else 0
    total_pts += pts_budget
    task_evaluations.append({
        "id": "task-budget-governance",
        "title": "Budget Cap Adherence (Max ₹30,000)",
        "expected_decision": f"Total Cost <= ₹30,000 (Actual Proposed: ₹{cost_val:,.2f})",
        "actual_decision": f"₹{cost_val:,.2f}",
        "is_correct": budget_ok,
        "points_earned": pts_budget,
        "max_points": 20,
        "explanation": "Strict compliance with L&D budget boundaries." if budget_ok else "Budget overrun: proposed programme exceeds the allocated ₹30,000 cap.",
    })

    return task_evaluations, total_pts, max_pts


def _build_training_result(
    task_evaluations: List[Dict[str, Any]],
    question_evaluations: List[Dict[str, Any]],
    total_task_pts: int,
    max_task_pts: int,
    total_q_pts: int,
    max_q_pts: int,
    answers: Dict[str, Any],
    integrity_flags: Dict[str, Any],
    eval_method: str,
) -> Dict[str, Any]:
    paste_count = int(integrity_flags.get("pasteCount", 0))
    integrity_audit = evaluate_integrity(answers, paste_count=paste_count)

    total_pts = total_task_pts + total_q_pts
    max_pts = max_task_pts + max_q_pts
    overall = round((total_pts / max_pts) * 100) if max_pts else 0

    if integrity_audit["is_ai_flagged"]:
        overall = max(0, overall - 10)

    passed = overall >= 70 and not integrity_audit["is_ai_flagged"]

    return {
        "overall_score": overall,
        "passed": passed,
        "evaluation_method": eval_method,
        "score_breakdown": {
            "instructional_design_score": round((total_task_pts / max_task_pts) * 100) if max_task_pts else 0,
            "strategic_ld_score": round((total_q_pts / max_q_pts) * 100) if max_q_pts else 0,
            "total_points": total_pts,
            "max_points": max_pts,
            "ai_assisted": eval_method == "hybrid_ai",
        },
        "task_evaluations": task_evaluations,
        "question_evaluations": question_evaluations,
        "integrity_audit": integrity_audit,
        "feedback_summary": (
            "Exemplary L&D coordination: diagnosed competency prerequisites, respected business shift SLAs, and constructed a cost-effective enablement roadmap."
            if passed
            else "Training plan failed to protect frontline operational coverage or assigned prerequisites incorrectly."
        ),
    }


__all__ = [
    "evaluate_training_submission",
    "evaluate_training_submission_async",
    "TRAINING_PLAN_CHECKS",
    "TRAINING_QUESTION_RUBRICS",
]
