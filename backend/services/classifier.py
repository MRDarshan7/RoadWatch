import json
import os
import re

import httpx
from fastapi import HTTPException

ALLOWED_ISSUES = {
    "Pothole",
    "Waterlogging",
    "Surface Crack",
    "Unfinished Work",
    "Shoulder Damage",
    "Signage Issue",
}
ALLOWED_SEVERITIES = {"Low", "Medium", "High", "Critical"}
SAFETY_WORDS = {"accident", "dangerous", "bus", "school", "traffic", "night", "skid", "skidding"}


class ClassifierConfigError(Exception):
    pass


def configured_key(name):
    value = (os.getenv(name) or "").strip()
    if not value or value.startswith("[") or "placeholder" in value.lower() or value.startswith("your-"):
        return None
    return value


def clean_description(description):
    return " ".join((description or "").strip().split())


def fallback_classification(description, issue_types=None):
    cleaned = clean_description(description)
    normalized = [issue for issue in (issue_types or []) if issue in ALLOWED_ISSUES] or ["Pothole"]
    lowered = cleaned.lower()
    safety_risk = any(word in lowered for word in SAFETY_WORDS)
    return {
        "normalized_issue_types": normalized,
        "severity": "Medium",
        "safety_risk": safety_risk,
        "urgency_score": 6,
        "summary_english": cleaned[:240] or "Road complaint requires inspection.",
        "reasoning": "Fallback heuristic used due to model response parsing failure.",
    }


def strip_code_fences(content):
    text = (content or "").strip()
    fence_match = re.match(r"^```(?:json)?\s*(.*?)\s*```$", text, flags=re.DOTALL | re.IGNORECASE)
    return fence_match.group(1).strip() if fence_match else text


def normalize_result(raw, description, issue_types=None):
    try:
        data = json.loads(strip_code_fences(raw))
    except (TypeError, json.JSONDecodeError):
        return fallback_classification(description, issue_types)

    issues = data.get("normalized_issue_types") or issue_types or []
    if isinstance(issues, str):
        issues = [issues]
    normalized_issues = [issue for issue in issues if issue in ALLOWED_ISSUES] or fallback_classification(
        description, issue_types
    )["normalized_issue_types"]

    severity = data.get("severity")
    if severity not in ALLOWED_SEVERITIES:
        severity = "Medium"

    try:
        urgency_score = int(data.get("urgency_score", 6))
    except (TypeError, ValueError):
        urgency_score = 6
    urgency_score = max(1, min(10, urgency_score))

    return {
        "normalized_issue_types": normalized_issues,
        "severity": severity,
        "safety_risk": bool(data.get("safety_risk", False)),
        "urgency_score": urgency_score,
        "summary_english": clean_description(data.get("summary_english") or description)[:240],
        "reasoning": clean_description(data.get("reasoning") or "Model classification completed.")[:240],
    }


def build_prompt(description, issue_types=None, road_name=None):
    selected = ", ".join(issue_types or []) or "None"
    road = road_name or "Unknown road"
    return f"""
You are a civic complaint triage assistant for Indian road infrastructure complaints.
Classify the complaint for authority routing. Preserve the user's meaning and do not invent details.

Allowed issue categories only:
- Pothole
- Waterlogging
- Surface Crack
- Unfinished Work
- Shoulder Damage
- Signage Issue

Severity must be one of: Low, Medium, High, Critical.
Classify severity based on public safety, road usability, traffic impact, and vulnerable users.
Examples:
- "Big pothole near school bus stop, kids falling" => Critical, safety_risk true
- "Minor crack on side shoulder" => Low or Medium
- "Waterlogging with potholes causing skidding" => High

Return STRICT JSON only:
{{
  "normalized_issue_types": ["Pothole", "Waterlogging"],
  "severity": "High",
  "safety_risk": true,
  "urgency_score": 8,
  "summary_english": "Large pothole and waterlogging near Korattur Main Road causing vehicles to swerve.",
  "reasoning": "Multiple road defects with traffic safety impact."
}}

Road: {road}
User selected issue types: {selected}
Complaint description: {description}
""".strip()


def classify_with_groq(prompt):
    api_key = configured_key("GROQ_API_KEY")
    if not api_key:
        raise ClassifierConfigError("No Groq key configured")

    response = httpx.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": "llama-3.1-8b-instant",
            "messages": [
                {"role": "system", "content": "Return strict JSON only. Do not include markdown."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.1,
            "response_format": {"type": "json_object"},
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["choices"][0]["message"]["content"]


def classify_with_gemini(prompt):
    api_key = configured_key("GEMINI_API_KEY")
    if not api_key:
        raise ClassifierConfigError("No Gemini key configured")

    response = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
        json={
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "responseMimeType": "application/json"},
        },
        timeout=20,
    )
    response.raise_for_status()
    return response.json()["candidates"][0]["content"]["parts"][0]["text"]


def classify_complaint(description: str, issue_types: list[str] | None = None, road_name: str | None = None) -> dict:
    groq_key = configured_key("GROQ_API_KEY")
    gemini_key = configured_key("GEMINI_API_KEY")
    if not groq_key and not gemini_key:
        raise HTTPException(status_code=503, detail="No AI provider configured. Set GROQ_API_KEY or GEMINI_API_KEY.")

    prompt = build_prompt(clean_description(description), issue_types, road_name)
    provider = "groq" if groq_key else "gemini"

    try:
        raw = classify_with_groq(prompt) if provider == "groq" else classify_with_gemini(prompt)
        result = normalize_result(raw, description, issue_types)
        result["provider_used"] = provider
        return result
    except HTTPException:
        raise
    except Exception:
        result = fallback_classification(description, issue_types)
        result["provider_used"] = "fallback"
        return result
