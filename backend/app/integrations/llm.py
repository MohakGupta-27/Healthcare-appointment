"""LLM integration with graceful fallback."""
import json
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

PRE_VISIT_PROMPT = (
    "Analyse these symptoms and return a JSON object with exactly these fields:\n"
    '- "urgency_level": one of "Low", "Medium", "High"\n'
    '- "chief_complaint": a brief summary of the main issue\n'
    '- "suggested_questions": three suggested questions for the doctor, separated by newlines\n\n'
    "Symptoms: {symptoms}"
)

POST_VISIT_PROMPT = (
    "Convert these clinical notes into a patient-friendly summary with "
    "medication schedule and follow-up steps. Return a JSON object with:\n"
    '- "patient_summary": the patient-friendly summary\n\n'
    "Clinical notes: {notes}\n"
    "Diagnosis: {diagnosis}\n"
    "Follow-up instructions: {follow_up}"
)


def _call_llm(prompt: str) -> str:
    """Call the configured LLM provider. Raises on failure."""
    if not settings.llm_base_url or not settings.llm_api_key:
        logger.info("LLM not configured, using mock response")
        return _mock_response(prompt)

    import httpx
    response = httpx.post(
        f"{settings.llm_base_url}/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.llm_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.llm_model or "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.3,
        },
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    return data["choices"][0]["message"]["content"]


def _mock_response(prompt: str) -> str:
    """Development fallback when no LLM is configured."""
    if "urgency_level" in prompt:
        return json.dumps({
            "urgency_level": "Medium",
            "chief_complaint": "Patient symptoms require medical evaluation",
            "suggested_questions": (
                "1. How long have you been experiencing these symptoms?\n"
                "2. Have you taken any medication for this?\n"
                "3. Do you have any known allergies?"
            ),
        })
    else:
        return json.dumps({
            "patient_summary": (
                "Your doctor has reviewed your condition and provided treatment recommendations. "
                "Please follow the prescribed medication schedule and attend any follow-up appointments. "
                "Contact your doctor if symptoms worsen or if you have any concerns."
            ),
        })


def _parse_json(text: str) -> dict:
    """Extract JSON from LLM response, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"raw_response": text}


def analyze_symptoms(symptoms: str) -> dict:
    """Generate pre-visit analysis. Returns dict with urgency_level, chief_complaint, suggested_questions."""
    prompt = PRE_VISIT_PROMPT.format(symptoms=symptoms)
    raw = _call_llm(prompt)
    result = _parse_json(raw)
    result["raw_response"] = raw
    return result


def generate_patient_summary(
    notes: str, diagnosis: str | None = None, follow_up: str | None = None
) -> dict:
    """Generate post-visit patient-friendly summary."""
    prompt = POST_VISIT_PROMPT.format(
        notes=notes,
        diagnosis=diagnosis or "Not specified",
        follow_up=follow_up or "Follow up as needed",
    )
    raw = _call_llm(prompt)
    result = _parse_json(raw)
    result["raw_response"] = raw
    return result
