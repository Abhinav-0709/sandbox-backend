"""
AI-Assisted Evaluation Module for Vivoki Sandbox Assessments.

Provides structured, rubric-guided evaluation of written/qualitative answers
using LLMs (Google Gemini, OpenAI, Groq, or Mock/Offline mode) with automatic
deterministic fallback.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional
import httpx
from pydantic import BaseModel, Field

from app.config import get_settings

logger = logging.getLogger(__name__)


class AiEvaluationResult(BaseModel):
    score: float = Field(..., description="Awarded score bounded between 0 and max_score")
    max_score: float = Field(..., description="Maximum possible points")
    matched_criteria: List[str] = Field(default_factory=list, description="Criteria successfully addressed")
    missing_criteria: List[str] = Field(default_factory=list, description="Criteria omitted or insufficiently addressed")
    rationale: str = Field(..., description="Detailed analytical justification of the score")
    feedback: str = Field(..., description="Constructive, actionable feedback for the candidate")
    confidence: str = Field(default="high", description="Evaluator confidence: high, medium, low")
    is_ai_generated: bool = Field(default=True, description="True if scored via LLM, False if deterministic fallback")


class AiRubricEvaluator:
    """
    Evaluates free-form written assessment answers against formal rubrics.
    Supports Gemini, OpenAI/Groq REST APIs, and a mock/offline mode.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        timeout_seconds: Optional[float] = None,
        base_url: Optional[str] = None,
        enabled: Optional[bool] = None,
    ):
        settings = get_settings()
        self.enabled = enabled if enabled is not None else settings.AI_EVALUATION_ENABLED
        self.provider = (provider or settings.AI_PROVIDER).lower()
        self.api_key = api_key or settings.AI_API_KEY
        self.model = model or settings.AI_MODEL
        self.timeout = timeout_seconds or settings.AI_TIMEOUT_SECONDS
        self.base_url = base_url or settings.AI_BASE_URL

    def evaluate_answer(
        self,
        question: str,
        answer_text: str,
        rubric: Dict[str, Any],
        context: Optional[str] = None,
    ) -> AiEvaluationResult:
        """
        Synchronously evaluate a single written response against a calibrated rubric.
        Falls back seamlessly to deterministic keyword evaluation if disabled,
        unconfigured, or on API error.
        """
        max_score = float(rubric.get("max_score", 10.0))
        cleaned_answer = (answer_text or "").strip()

        # If answer is empty or trivially short, return immediate zero score
        if len(cleaned_answer.split()) < 3:
            return AiEvaluationResult(
                score=0.0,
                max_score=max_score,
                matched_criteria=[],
                missing_criteria=rubric.get("keywords", [])[:3],
                rationale="Candidate provided no substantial response or under 3 words.",
                feedback="Response was empty or insufficiently developed. Please provide complete analysis.",
                confidence="high",
                is_ai_generated=False,
            )

        # Fallback if AI evaluation is not enabled or credentials missing
        if not self.enabled or (not self.api_key and self.provider != "mock"):
            return self._deterministic_fallback(rubric, cleaned_answer)

        prompt = self._build_evaluation_prompt(question, cleaned_answer, rubric, context)

        try:
            if self.provider == "mock":
                raw_json = self._call_mock_sync(cleaned_answer, rubric)
            elif self.provider in ["gemini", "google"]:
                raw_json = self._call_gemini_sync(prompt)
            elif self.provider in ["openai", "groq", "custom"]:
                raw_json = self._call_openai_compatible_sync(prompt)
            else:
                logger.warning(f"Unknown AI provider '{self.provider}', falling back to deterministic.")
                return self._deterministic_fallback(rubric, cleaned_answer)

            return self._parse_and_validate_response(raw_json, max_score)
        except Exception as e:
            logger.warning(f"AI evaluation failed ({type(e).__name__}: {e}). Using deterministic fallback.")
            return self._deterministic_fallback(rubric, cleaned_answer)

    async def evaluate_answer_async(
        self,
        question: str,
        answer_text: str,
        rubric: Dict[str, Any],
        context: Optional[str] = None,
    ) -> AiEvaluationResult:
        """
        Asynchronously evaluate a single written response against a calibrated rubric.
        """
        max_score = float(rubric.get("max_score", 10.0))
        cleaned_answer = (answer_text or "").strip()

        if len(cleaned_answer.split()) < 3:
            return AiEvaluationResult(
                score=0.0,
                max_score=max_score,
                matched_criteria=[],
                missing_criteria=rubric.get("keywords", [])[:3],
                rationale="Candidate provided no substantial response or under 3 words.",
                feedback="Response was empty or insufficiently developed. Please provide complete analysis.",
                confidence="high",
                is_ai_generated=False,
            )

        if not self.enabled or (not self.api_key and self.provider != "mock"):
            return self._deterministic_fallback(rubric, cleaned_answer)

        prompt = self._build_evaluation_prompt(question, cleaned_answer, rubric, context)

        try:
            if self.provider == "mock":
                raw_json = self._call_mock_sync(cleaned_answer, rubric)
            elif self.provider in ["gemini", "google"]:
                raw_json = await self._call_gemini(prompt)
            elif self.provider in ["openai", "groq", "custom"]:
                raw_json = await self._call_openai_compatible(prompt)
            else:
                return self._deterministic_fallback(rubric, cleaned_answer)

            return self._parse_and_validate_response(raw_json, max_score)
        except Exception as e:
            logger.warning(f"AI evaluation failed ({type(e).__name__}: {e}). Using deterministic fallback.")
            return self._deterministic_fallback(rubric, cleaned_answer)

    def _build_evaluation_prompt(
        self,
        question: str,
        answer_text: str,
        rubric: Dict[str, Any],
        context: Optional[str] = None,
    ) -> str:
        max_score = rubric.get("max_score", 10)
        keywords = rubric.get("keywords", [])
        min_words = rubric.get("min_word_count", 30)

        prompt = f"""You are a calibrated senior executive assessor evaluating a candidate's workplace simulation submission.
Evaluate the candidate's answer with rigorous, objective standards against the provided rubric.

### CONTEXT & SCENARIO:
{context or 'Enterprise Workplace Simulation Assessment'}

### QUESTION:
{question}

### RUBRIC CRITERIA:
- Maximum Points: {max_score}
- Expected Concepts & Keywords: {', '.join(keywords)}
- Minimum Target Word Count: {min_words} words

### CANDIDATE'S RESPONSE:
\"\"\"{answer_text}\"\"\"

### SCORING GUIDELINES:
- Grade proportionally from 0 to {max_score}.
- High Score ({max_score * 0.8:.1f} - {max_score:.1f}): Demonstrates thorough domain comprehension, practical reasoning, concrete evidence, and addresses core principles.
- Medium Score ({max_score * 0.5:.1f} - {max_score * 0.79:.1f}): Identifies main issues but misses subtle trade-offs, procedural completeness, or quantitative specifics.
- Low Score (0 - {max_score * 0.49:.1f}): Superficial, generic, evasive, or incorrect reasoning.

You MUST respond strictly with valid JSON conforming exactly to this schema:
{{
  "score": <float between 0 and {max_score}>,
  "max_score": {max_score},
  "matched_criteria": [<string>, ...],
  "missing_criteria": [<string>, ...],
  "rationale": "<Detailed explanation of why this score was awarded based on evidence provided>",
  "feedback": "<Constructive, professional feedback addressing how to improve>",
  "confidence": "<high|medium|low>"
}}
Do NOT include markdown formatting or commentary outside the JSON object.
"""
        return prompt

    def _call_gemini_sync(self, prompt: str) -> str:
        model = self.model or "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json",
            },
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("No response candidates returned by Gemini API")
            part = candidates[0].get("content", {}).get("parts", [{}])[0]
            return part.get("text", "")

    def _call_openai_compatible_sync(self, prompt: str) -> str:
        base_url = self.base_url.rstrip("/") if self.base_url else (
            "https://api.groq.com/openai/v1" if self.provider == "groq" else "https://api.openai.com/v1"
        )
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model or ("gpt-4o-mini" if self.provider == "openai" else "llama-3.1-8b-instant"),
            "messages": [
                {"role": "system", "content": "You are a professional assessment evaluator. Always output valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    def _call_mock_sync(self, answer_text: str, rubric: Dict[str, Any]) -> str:
        """Deterministic mock for offline CI/test environments."""
        max_score = float(rubric.get("max_score", 10))
        keywords = rubric.get("keywords", [])
        lower = answer_text.lower()
        matched = [k for k in keywords if k.lower() in lower]
        missing = [k for k in keywords if k.lower() not in lower]

        ratio = len(matched) / max(len(keywords), 1)
        score = round(max_score * min(1.0, 0.4 + (ratio * 0.6)), 1)
        mock_data = {
            "score": score,
            "max_score": max_score,
            "matched_criteria": matched,
            "missing_criteria": missing[:3],
            "rationale": f"Candidate demonstrated understanding by referencing {len(matched)} key domain criteria.",
            "feedback": (
                "Well articulated. Excellent alignment with industry assessment standards."
                if score >= max_score * 0.8
                else f"Good start. Strengthen your argument by incorporating: {', '.join(missing[:2])}."
            ),
            "confidence": "high",
        }
        return json.dumps(mock_data)

    async def _call_gemini(self, prompt: str) -> str:
        model = self.model or "gemini-1.5-flash"
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.1,
                "response_mime_type": "application/json",
            },
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                raise ValueError("No response candidates returned by Gemini API")
            part = candidates[0].get("content", {}).get("parts", [{}])[0]
            return part.get("text", "")

    async def _call_openai_compatible(self, prompt: str) -> str:
        base_url = self.base_url.rstrip("/") if self.base_url else (
            "https://api.groq.com/openai/v1" if self.provider == "groq" else "https://api.openai.com/v1"
        )
        url = f"{base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model or ("gpt-4o-mini" if self.provider == "openai" else "llama-3.1-8b-instant"),
            "messages": [
                {"role": "system", "content": "You are a professional assessment evaluator. Always output valid JSON."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"]

    async def _call_mock(self, answer_text: str, rubric: Dict[str, Any]) -> str:
        """Deterministic mock for offline CI/test environments."""
        max_score = float(rubric.get("max_score", 10))
        keywords = rubric.get("keywords", [])
        lower = answer_text.lower()
        matched = [k for k in keywords if k.lower() in lower]
        missing = [k for k in keywords if k.lower() not in lower]

        ratio = len(matched) / max(len(keywords), 1)
        score = round(max_score * min(1.0, 0.4 + (ratio * 0.6)), 1)
        mock_data = {
            "score": score,
            "max_score": max_score,
            "matched_criteria": matched,
            "missing_criteria": missing[:3],
            "rationale": f"Candidate demonstrated understanding by referencing {len(matched)} key domain criteria.",
            "feedback": (
                "Well articulated. Excellent alignment with industry assessment standards."
                if score >= max_score * 0.8
                else f"Good start. Strengthen your argument by incorporating: {', '.join(missing[:2])}."
            ),
            "confidence": "high",
        }
        return json.dumps(mock_data)

    def _parse_and_validate_response(self, raw_text: str, max_score: float) -> AiEvaluationResult:
        # Strip code fences if present
        text = raw_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text)
            text = re.sub(r"\s*```$", "", text)

        data = json.loads(text)
        score = float(data.get("score", 0.0))
        bounded_score = max(0.0, min(max_score, score))

        return AiEvaluationResult(
            score=round(bounded_score, 1),
            max_score=max_score,
            matched_criteria=data.get("matched_criteria", []),
            missing_criteria=data.get("missing_criteria", []),
            rationale=data.get("rationale", "Evaluation completed via AI rubric assessment."),
            feedback=data.get("feedback", "No specific feedback provided."),
            confidence=data.get("confidence", "high"),
            is_ai_generated=True,
        )

    def _deterministic_fallback(self, rubric: Dict[str, Any], answer_text: str) -> AiEvaluationResult:
        max_score = float(rubric.get("max_score", 10.0))
        keywords = rubric.get("keywords", [])
        required_kw = rubric.get("required_keywords", max(1, len(keywords) // 2))
        min_words = rubric.get("min_word_count", 30)

        lower = answer_text.lower()
        matched = [kw for kw in keywords if kw.lower() in lower]
        missing = [kw for kw in keywords if kw.lower() not in lower]
        word_count = len(answer_text.strip().split())

        if word_count >= min_words and len(matched) >= required_kw:
            score = max_score
        elif word_count >= 10 and len(matched) >= 1:
            score = min(
                max_score - 2,
                round((len(matched) / max(1, required_kw)) * (max_score * 0.75), 1),
            )
        elif word_count > 5:
            score = round(max_score * 0.2, 1)
        else:
            score = 0.0

        feedback = (
            "Excellent answer. Thorough coverage of essential principles and procedural requirements."
            if score >= max_score * 0.8
            else f"Good attempt. Strengthen by incorporating: {', '.join(missing[:3])}."
            if score > 3
            else "Under-developed response. Needs specific evidence and procedural detail."
        )

        return AiEvaluationResult(
            score=round(score, 1),
            max_score=max_score,
            matched_criteria=matched,
            missing_criteria=missing[:4],
            rationale=f"Evaluated via keyword rubric: {len(matched)}/{required_kw} concepts matched across {word_count} words.",
            feedback=feedback,
            confidence="medium",
            is_ai_generated=False,
        )


def evaluate_rubric_questions(
    rubrics: List[Dict[str, Any]],
    answers: Dict[str, Any],
    evaluator: Optional[AiRubricEvaluator] = None,
    context: Optional[str] = None,
) -> tuple[List[Dict[str, Any]], int, int, bool]:
    """
    Synchronously evaluates a batch of question rubrics.
    Returns: (question_evaluations, total_question_points, max_question_points, any_ai_used)
    """
    ai = evaluator or AiRubricEvaluator()
    question_evaluations: List[Dict[str, Any]] = []
    total_points = 0
    max_points = 0
    any_ai = False

    for rubric in rubrics:
        max_points += rubric["max_score"]
        answer_text = str(answers.get(rubric["field"], "") or "")
        res = ai.evaluate_answer(
            question=rubric["question"],
            answer_text=answer_text,
            rubric=rubric,
            context=context,
        )
        score_val = int(round(res.score))
        total_points += score_val
        if res.is_ai_generated:
            any_ai = True

        question_evaluations.append({
            "id": rubric["id"],
            "question": rubric["question"],
            "answer_length": len(answer_text.strip().split()),
            "matched_keywords": res.matched_criteria,
            "missing_keywords": res.missing_criteria,
            "score": score_val,
            "max_score": rubric["max_score"],
            "feedback": res.feedback,
            "rationale": res.rationale,
            "confidence": res.confidence,
            "is_ai_evaluated": res.is_ai_generated,
        })

    return question_evaluations, total_points, max_points, any_ai


async def evaluate_rubric_questions_async(
    rubrics: List[Dict[str, Any]],
    answers: Dict[str, Any],
    evaluator: Optional[AiRubricEvaluator] = None,
    context: Optional[str] = None,
) -> tuple[List[Dict[str, Any]], int, int, bool]:
    """
    Evaluates a batch of question rubrics concurrently using AI or deterministic fallback.
    Returns: (question_evaluations, total_question_points, max_question_points, any_ai_used)
    """
    ai = evaluator or AiRubricEvaluator()
    import asyncio

    tasks = []
    for rubric in rubrics:
        answer_text = str(answers.get(rubric["field"], "") or "")
        tasks.append(
            ai.evaluate_answer_async(
                question=rubric["question"],
                answer_text=answer_text,
                rubric=rubric,
                context=context,
            )
        )

    results: List[AiEvaluationResult] = await asyncio.gather(*tasks)

    question_evaluations: List[Dict[str, Any]] = []
    total_points = 0
    max_points = 0
    any_ai = False

    for rubric, res in zip(rubrics, results):
        max_points += rubric["max_score"]
        score_val = int(round(res.score))
        total_points += score_val
        if res.is_ai_generated:
            any_ai = True

        answer_text = str(answers.get(rubric["field"], "") or "")
        question_evaluations.append({
            "id": rubric["id"],
            "question": rubric["question"],
            "answer_length": len(answer_text.strip().split()),
            "matched_keywords": res.matched_criteria,
            "missing_keywords": res.missing_criteria,
            "score": score_val,
            "max_score": rubric["max_score"],
            "feedback": res.feedback,
            "rationale": res.rationale,
            "confidence": res.confidence,
            "is_ai_evaluated": res.is_ai_generated,
        })

    return question_evaluations, total_points, max_points, any_ai

