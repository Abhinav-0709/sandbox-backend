import json
from unittest.mock import patch, MagicMock
import httpx

from app.evaluators.ai_assisted import (
    AiRubricEvaluator,
    evaluate_rubric_questions,
)
from app.evaluators.finance import QUESTION_RUBRICS, _build_finance_evaluation_result
from app.evaluators.hr import HR_QUESTION_RUBRICS, _build_hr_evaluation_result
from app.evaluators.sde import SDE_QUESTION_RUBRICS, _build_sde_evaluation_result


SAMPLE_RUBRIC = {
    "id": "q_sample",
    "field": "sample_field",
    "question": "Explain internal control separation of duties.",
    "keywords": ["segregation", "authorization", "reconciliation", "custody", "audit"],
    "required_keywords": 3,
    "min_word_count": 30,
    "max_score": 10.0,
}


def test_ai_evaluator_empty_response():
    evaluator = AiRubricEvaluator(provider="mock")
    res = evaluator.evaluate_answer(
        question=SAMPLE_RUBRIC["question"],
        answer_text="   ",
        rubric=SAMPLE_RUBRIC,
    )
    assert res.score == 0.0
    assert res.max_score == 10.0
    assert res.confidence == "high"
    assert res.is_ai_generated is False


def test_ai_evaluator_deterministic_fallback():
    evaluator = AiRubricEvaluator(provider="gemini", api_key="", enabled=True)
    res = evaluator.evaluate_answer(
        question=SAMPLE_RUBRIC["question"],
        answer_text=(
            "Segregation of duties ensures authorization and reconciliation remain separate "
            "from physical asset custody to prevent fraud and ensure audit compliance across departments."
        ),
        rubric=SAMPLE_RUBRIC,
    )
    assert res.score >= 8.0
    assert res.max_score == 10.0
    assert "segregation" in [k.lower() for k in res.matched_criteria]
    assert res.is_ai_generated is False


def test_ai_evaluator_mock_mode():
    evaluator = AiRubricEvaluator(provider="mock")
    answer = (
        "We implement strict segregation of duties where authorization is distinct from reconciliation. "
        "Asset custody must be verified through regular internal audit procedures."
    )
    res = evaluator.evaluate_answer(
        question=SAMPLE_RUBRIC["question"],
        answer_text=answer,
        rubric=SAMPLE_RUBRIC,
    )
    assert res.score >= 7.0
    assert res.max_score == 10.0
    assert res.is_ai_generated is True
    assert len(res.matched_criteria) >= 2
    assert "rationale" in res.model_dump()


def test_prompt_generation():
    evaluator = AiRubricEvaluator(provider="gemini")
    prompt = evaluator._build_evaluation_prompt(
        question=SAMPLE_RUBRIC["question"],
        answer_text="Sample candidate answer text here.",
        rubric=SAMPLE_RUBRIC,
        context="Finance Audit Simulation",
    )
    assert "Finance Audit Simulation" in prompt
    assert SAMPLE_RUBRIC["question"] in prompt
    assert "Maximum Points: 10.0" in prompt
    assert "segregation" in prompt


def test_response_parser_handles_fenced_json():
    evaluator = AiRubricEvaluator()
    fenced_json = """```json
    {
        "score": 9.5,
        "max_score": 10.0,
        "matched_criteria": ["segregation", "authorization"],
        "missing_criteria": ["custody"],
        "rationale": "Clear and concise explanation of control separation.",
        "feedback": "Strong answer. Consider explicitly mentioning asset custody.",
        "confidence": "high"
    }
    ```"""
    res = evaluator._parse_and_validate_response(fenced_json, max_score=10.0)
    assert res.score == 9.5
    assert res.matched_criteria == ["segregation", "authorization"]
    assert res.is_ai_generated is True


def test_response_parser_clamps_scores():
    evaluator = AiRubricEvaluator()
    over_scored_json = json.dumps({
        "score": 15.0,
        "max_score": 10.0,
        "matched_criteria": [],
        "missing_criteria": [],
        "rationale": "Over generous score.",
        "feedback": "Good job.",
        "confidence": "high",
    })
    res = evaluator._parse_and_validate_response(over_scored_json, max_score=10.0)
    assert res.score == 10.0


def test_network_failure_falls_back_gracefully():
    evaluator = AiRubricEvaluator(provider="gemini", api_key="test-dummy-key")
    answer = "Segregation of duties between authorization and reconciliation ensures safety."

    with patch("httpx.Client.post", side_effect=httpx.ConnectTimeout("Connection timed out")):
        res = evaluator.evaluate_answer(
            question=SAMPLE_RUBRIC["question"],
            answer_text=answer,
            rubric=SAMPLE_RUBRIC,
        )
        assert res is not None
        assert res.is_ai_generated is False
        assert res.score > 0.0


def test_gemini_api_adapter_mocked():
    evaluator = AiRubricEvaluator(provider="gemini", api_key="valid-test-key")
    mock_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {
                            "text": json.dumps({
                                "score": 8.5,
                                "max_score": 10.0,
                                "matched_criteria": ["authorization", "reconciliation"],
                                "missing_criteria": ["custody"],
                                "rationale": "Solid understanding demonstrated.",
                                "feedback": "Well explained.",
                                "confidence": "high",
                            })
                        }
                    ]
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_payload
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.Client.post", return_value=mock_resp):
        res = evaluator.evaluate_answer(
            question=SAMPLE_RUBRIC["question"],
            answer_text="Authorization must always be segregated from reconciliation to prevent internal collusion.",
            rubric=SAMPLE_RUBRIC,
        )
        assert res.score == 8.5
        assert res.is_ai_generated is True
        assert res.matched_criteria == ["authorization", "reconciliation"]


def test_openai_api_adapter_mocked():
    evaluator = AiRubricEvaluator(provider="openai", api_key="valid-openai-key")
    mock_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "score": 9.0,
                        "max_score": 10.0,
                        "matched_criteria": ["segregation", "audit", "authorization"],
                        "missing_criteria": [],
                        "rationale": "Superb answer referencing all key pillars.",
                        "feedback": "Outstanding clarity.",
                        "confidence": "high",
                    })
                }
            }
        ]
    }

    mock_resp = MagicMock()
    mock_resp.json.return_value = mock_payload
    mock_resp.raise_for_status = MagicMock()

    with patch("httpx.Client.post", return_value=mock_resp):
        res = evaluator.evaluate_answer(
            question=SAMPLE_RUBRIC["question"],
            answer_text="Segregation and authorization are audited constantly.",
            rubric=SAMPLE_RUBRIC,
        )
        assert res.score == 9.0
        assert res.is_ai_generated is True


def test_evaluate_rubric_questions_batch():
    evaluator = AiRubricEvaluator(provider="mock")
    rubrics = [SAMPLE_RUBRIC]
    answers = {"sample_field": "Segregation of duties authorization and reconciliation."}
    q_evals, total_pts, max_pts, any_ai = evaluate_rubric_questions(
        rubrics=rubrics,
        answers=answers,
        evaluator=evaluator,
    )
    assert len(q_evals) == 1
    assert total_pts >= 6
    assert max_pts == 10
    assert any_ai is True
    assert q_evals[0]["is_ai_evaluated"] is True


def test_evaluate_finance_submission_with_ai():
    mock_ai = AiRubricEvaluator(provider="mock")
    answers = {
        "q1DecisionsReasoning": "Identified freight charge price mismatch on Vertex INV-8821 where shipping billed higher than contracted.",
        "q2DiscountAnalysis": "Sigma INV-8829 has 2/10 net 30 payment terms saving 2% cash discount if approved within early pay window.",
        "q3DiscrepancyInformation": "Duplicate invoice INV-8826 indicates missing ERP uniqueness constraints; recommend automated 3-way check.",
        "q4ControlRecommendations": "Hold payment on Zenith INV-8832 due to bank change fraud risk and verify with CFO via callback.",
        "q5DeadlinePressure": "Document receiving slip bill of lading and signed purchase order in audit trail log under deadline pressure.",
        "supplierEmailDraft": "Dear Supplier, We noticed a pricing mismatch on INV-8821. Please issue a revised credit memo.",
    }

    q_evals, total_q, max_q, any_ai = evaluate_rubric_questions(
        QUESTION_RUBRICS, answers, evaluator=mock_ai
    )
    result = _build_finance_evaluation_result(
        task_evaluations=[],
        question_evaluations=q_evals,
        total_invoice_points=60,
        max_invoice_points=60,
        total_question_points=total_q,
        max_question_points=max_q,
        answers=answers,
        integrity_flags={"pasteCount": 0},
        evaluation_method="hybrid_ai" if any_ai else "deterministic",
    )
    assert result["overall_score"] >= 70
    assert result["passed"] is True
    assert result["evaluation_method"] == "hybrid_ai"
    assert result["score_breakdown"]["ai_assisted"] is True


def test_evaluate_hr_submission_with_ai():
    mock_ai = AiRubricEvaluator(provider="mock")
    answers = {
        "q1ShortlistRanking": "Shortlisting Elena Rostova, Aisha Bello, Chloe Dupont, and Zoe Chen based on proven React portfolio and essential criteria evidence.",
        "q2ExperienceVsProjects": "Demonstrated practical code on GitHub and live verified repositories outweigh unverified commercial years with solid evidence.",
        "q3OverclaimedFullStack": "Inspecting repository commit history showed static boilerplate templates rather than dynamic backend integration.",
        "q4ManagerBiasResponse": "Maintained objective benchmark criteria and fairness standards despite informal preference, declining candidate Samira due to non-responsive code.",
        "recruitmentSummaryDraft": "Memo to David: Recommending our top shortlist of engineers who met all technical benchmark criteria and interview requirements.",
    }
    q_evals, total_q, max_q, any_ai = evaluate_rubric_questions(
        HR_QUESTION_RUBRICS, answers, evaluator=mock_ai
    )
    result = _build_hr_evaluation_result(
        task_evaluations=[],
        question_evaluations=q_evals,
        total_candidate_points=100,
        max_candidate_points=100,
        total_question_points=total_q,
        max_question_points=max_q,
        answers=answers,
        integrity_flags={"pasteCount": 0},
        evaluation_method="hybrid_ai" if any_ai else "rubric",
    )
    assert result["overall_score"] >= 80
    assert result["passed"] is True
    assert result["score_breakdown"]["ai_assisted"] is True


def test_evaluate_sde_submission_with_ai():
    mock_ai = AiRubricEvaluator(provider="mock")
    answers = {
        "q1RootCauses": "Issue 1 was a race condition lacking idempotency. Issue 2 lacked database transaction rollback. Issue 3 had mass assignment allowing BOLA authorization tampering.",
        "q2DuplicatePrevention": "Apply atomic database locks, unique constraint indices, debouncing, and idempotency keys.",
        "q3OptimisticUiTradeoffs": "Design idempotent message processing with distributed locks in Redis or Postgres advisory locks with rollback.",
        "q4OwnershipSecurityRisks": "Enforce strict schema validation and DTO field filtering before updating entities in the ORM to prevent privilege escalation.",
        "q5LayerResponsibilities": "Frontend handles optimistic feedback and debouncing while backend enforces authorization and atomic database transactions.",
        "q6TestingStrategy": "Implement concurrent integration tests and automated regression suites simulating simultaneous requests and transaction rollback.",
    }
    q_evals, total_q, max_q, any_ai = evaluate_rubric_questions(
        SDE_QUESTION_RUBRICS, answers, evaluator=mock_ai
    )
    result = _build_sde_evaluation_result(
        task_evaluations=[],
        question_evaluations=q_evals,
        diagnostics_score=30,
        total_question_points=total_q,
        max_question_points=max_q,
        answers=answers,
        integrity_flags={"pasteCount": 0},
        evaluation_method="hybrid_ai" if any_ai else "deterministic",
    )
    assert result["overall_score"] >= 75
    assert result["passed"] is True
    assert result["score_breakdown"]["ai_assisted"] is True
