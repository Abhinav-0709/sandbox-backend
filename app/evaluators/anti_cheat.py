from __future__ import annotations

import re
from typing import Dict, Any, List, Tuple


COMMON_AI_MARKERS = [
    "in conclusion",
    "it is crucial to note",
    "it is important to remember",
    "furthermore, it is essential",
    "to summarize",
    "in today's fast-paced",
    "delving into",
    "tapestry",
    "beacon",
    "pivotal role",
    "paramount importance",
    "it is worth noting that",
    "a testament to",
    "holistic approach",
    "comprehensive overview",
    "it cannot be overstated",
    "in essence",
    "serves as a reminder",
    "moreover, it should be noted",
    "as an ai language model",
    "first and foremost",
    "meticulous attention to detail",
    "navigating the complexities",
    "underscores the importance",
    "by fostering a culture of",
    "striking a delicate balance",
    "plays a vital role in ensuring",
    "sheds light on",
    "speaks volumes",
    "in the realm of",
    "harnessing the power of",
    "orchestrating a seamless",
    "at the forefront of",
    "it is paramount that",
    "fostering innovation",
]

FORMAL_TRANSITIONS = [
    "furthermore",
    "moreover",
    "consequently",
    "nonetheless",
    "imperative",
    "indispensable",
    "notably",
    "subsequently",
    "henceforth",
]


def detect_ai_markers(text: str) -> Dict[str, Any]:
    if not text or len(text.strip()) < 50:
        return {
            "is_ai_likely": False,
            "confidence": "Clean",
            "detected_markers": [],
            "explanation": "Response is concise and authentic; insufficient length to trigger synthetic markers.",
        }

    lower = text.lower()
    matched_markers = [m for m in COMMON_AI_MARKERS if m in lower]

    transition_count = sum(
        len(re.findall(rf"\b{t}\b", lower, re.IGNORECASE)) for t in FORMAL_TRANSITIONS
    )

    bullet_lines = len(re.findall(r"^[ \t]*[\*\-•][ \t]+", text, re.MULTILINE))
    bold_headers = len(re.findall(r"\*\*[^*]+\*\*:", text))

    score = 0
    if len(matched_markers) >= 2:
        score += 45
    elif len(matched_markers) == 1:
        score += 25

    if transition_count >= 4:
        score += 30
    elif transition_count >= 2:
        score += 15

    if bold_headers >= 3 and bullet_lines >= 3:
        score += 30
    elif bold_headers >= 2 or bullet_lines >= 4:
        score += 20

    # Sentence length variance check:
    # Human text has wide variance; LLM text has tight 15-22 words per sentence
    sentences = [s.strip() for s in re.split(r"[.!?]+", text) if len(s.strip()) > 5]
    if len(sentences) >= 4:
        lengths = [len(s.split()) for s in sentences]
        avg_len = sum(lengths) / len(lengths)
        variance = sum((l - avg_len) ** 2 for l in lengths) / len(lengths)
        if variance < 15 and 14 <= avg_len <= 26 and score >= 20:
            score += 15

    confidence = "Clean"
    if score >= 60:
        confidence = "High"
    elif score >= 40:
        confidence = "Medium"
    elif score >= 20:
        confidence = "Low"

    is_ai_likely = score >= 45

    return {
        "is_ai_likely": is_ai_likely,
        "confidence": confidence,
        "detected_markers": matched_markers,
        "score": score,
    }


def evaluate_integrity(answers: Dict[str, Any], paste_count: int = 0) -> Dict[str, Any]:
    per_answer_audit = []
    all_markers = set()
    flagged_count = 0
    total_score = 0

    text_answers = {k: v for k, v in answers.items() if isinstance(v, str) and len(v.strip()) > 0}

    for key, text in text_answers.items():
        res = detect_ai_markers(text)
        if res["is_ai_likely"]:
            flagged_count += 1
            for m in res["detected_markers"]:
                all_markers.add(m)

        weight = 80 if res["confidence"] == "High" else 50 if res["confidence"] == "Medium" else 25 if res["confidence"] == "Low" else 5
        total_score += weight

        per_answer_audit.append({
            "question_key": key,
            "is_ai_likely": res["is_ai_likely"],
            "confidence": res["confidence"],
            "detected_markers": res["detected_markers"],
        })

    total_audited = max(len(text_answers), 1)
    avg_ai_score = min(100, round(total_score / total_audited))
    is_ai_flagged = flagged_count >= 2 or avg_ai_score >= 45

    deduction_applied = 15 if is_ai_flagged else 0
    status = (
        "Flagged (Synthetic AI Syntax Detected)"
        if is_ai_flagged
        else "Caution (Elevated AI Patterns)"
        if flagged_count == 1 or avg_ai_score >= 25
        else "Clean (Verified Human)"
    )

    summary = (
        f"Anti-Cheat Warning: {flagged_count} of {total_audited} responses triggered high-confidence synthetic AI patterns."
        if is_ai_flagged
        else f"Clipboard Alert: {paste_count} external paste attempt(s) intercepted."
        if paste_count > 0
        else "Assessment verified as authentic human candidate output."
    )

    return {
        "paste_attempts_count": paste_count,
        "has_paste_violations": paste_count > 0,
        "ai_detection_score": avg_ai_score,
        "is_ai_flagged": is_ai_flagged,
        "overall_integrity_status": status,
        "summary": summary,
        "flagged_answers_count": flagged_count,
        "total_answers_audited": total_audited,
        "detected_markers": sorted(list(all_markers)),
        "deduction_applied": deduction_applied,
        "per_answer_audit": per_answer_audit,
    }
