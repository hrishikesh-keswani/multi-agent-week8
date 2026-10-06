"""Standalone underwriting agents. Each one reads and writes the case record."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from underwriting.bureau import lookup_bureau
from underwriting.state import CaseRecord

HIGH_SCORE_APPROVE_LIMIT = 75
REQUIRED_INTAKE_FIELDS = (
    "full_name",
    "age",
    "occupation",
    "coverage_type",
    "coverage_amount",
    "state",
)
DECISIONS = ("approve", "deny", "refer")

INTAKE_SYSTEM = """You normalize an insurance application into one JSON object.
Use these keys only:
ssn (string, copied from the application),
full_name (string or null),
age (number or null),
occupation (string or null),
coverage_type (string or null, such as renters or homeowners),
coverage_amount (number or null, digits only, no currency symbol),
state (string or null),
household (string or null),
notes (string).
Use null when the application does not state a fact. Do not invent an age or a coverage amount."""

ENRICHMENT_SYSTEM = """You review an insurance intake and a bureau record.
Return one JSON object with these keys:
summary (string),
red_flags (array of short strings),
missing_fields (array of short strings),
risk_notes (string).
missing_fields lists applicant facts that are null or absent.
red_flags lists concrete risk items from the bureau or the application, such as prior claims, a flood zone, or a high-risk occupation.
Use empty arrays when there are none."""

RISK_SYSTEM = """You score insurance risk from intake and enrichment.
Return one JSON object with these keys:
score (integer from 0 to 100, higher means riskier),
band (one of low, medium, high),
factors (array of short strings).
Use low under 35, medium from 35 through 74, and high from 75 up."""

RECOMMENDATION_SYSTEM = """You are an insurance underwriter.
Return one JSON object with these keys:
decision (exactly one of approve, deny, refer),
rationale (string).
Approve only a complete, low-risk application.
Deny a clear high-risk application, such as repeated claims in a flood zone with a very high coverage amount.
Refer when information is thin or the risk is ambiguous."""


def intake_agent(case: CaseRecord, llm: Any) -> CaseRecord:
    response = llm.complete(
        agent="intake",
        system=INTAKE_SYSTEM,
        user=json.dumps(case.raw_application),
    )
    _remember_usage(case, response)
    content = response.content
    case.intake = {
        "ssn": case.case_id,
        "full_name": _text(_field(content, "full_name")),
        "age": _optional_number(_field(content, "age")),
        "occupation": _text(_field(content, "occupation")),
        "coverage_type": _text(_field(content, "coverage_type")),
        "coverage_amount": _optional_number(_field(content, "coverage_amount")),
        "state": _text(_field(content, "state")),
        "household": _text(_field(content, "household")),
        "notes": _text(_field(content, "notes")) or "",
    }
    if not case.intake["full_name"]:
        raise ValueError("intake did not produce a full name")
    return case


def enrichment_agent(case: CaseRecord, llm: Any) -> CaseRecord:
    if not case.intake:
        raise ValueError("enrichment requires intake")
    ssn = str(case.intake.get("ssn") or case.case_id)
    bureau = lookup_bureau(ssn)
    response = llm.complete(
        agent="enrichment",
        system=ENRICHMENT_SYSTEM,
        user=json.dumps({"intake": case.intake, "bureau": bureau}),
    )
    _remember_usage(case, response)
    content = response.content
    case.enrichment = {
        "ssn": ssn,
        "bureau": bureau,
        "summary": _text(_field(content, "summary")) or "",
        "red_flags": _string_list(_field(content, "red_flags")),
        "missing_fields": _string_list(_field(content, "missing_fields")),
        "risk_notes": _text(_field(content, "risk_notes")) or "",
    }
    if not case.enrichment["summary"]:
        raise ValueError("enrichment did not produce a summary")
    return case


def risk_scoring_agent(case: CaseRecord, llm: Any) -> CaseRecord:
    if not case.intake or not case.enrichment:
        raise ValueError("risk scoring requires intake and enrichment")
    response = llm.complete(
        agent="risk_scoring",
        system=RISK_SYSTEM,
        user=json.dumps({"intake": case.intake, "enrichment": case.enrichment}),
    )
    _remember_usage(case, response)
    content = response.content
    score = _optional_number(_field(content, "score"))
    if score is None or score < 0 or score > 100:
        raise ValueError("risk score must be an integer from 0 to 100")
    case.risk = {
        "score": score,
        "band": _band(score, _field(content, "band")),
        "factors": _string_list(_field(content, "factors")),
    }
    return case


def recommendation_agent(case: CaseRecord, llm: Any) -> CaseRecord:
    if not case.intake or not case.enrichment or not case.risk:
        raise ValueError("recommendation requires intake, enrichment, and risk")
    response = llm.complete(
        agent="recommendation",
        system=RECOMMENDATION_SYSTEM,
        user=json.dumps(
            {
                "intake": case.intake,
                "enrichment": case.enrichment,
                "risk": case.risk,
            }
        ),
    )
    _remember_usage(case, response)
    model_decision = _decision(_field(response.content, "decision"))
    if model_decision is None:
        raise ValueError("recommendation decision must be approve, deny, or refer")
    final_decision, guard_reason = apply_guard(model_decision, case)
    case.recommendation = {
        "decision": final_decision,
        "rationale": _text(_field(response.content, "rationale")) or "",
        "source": "model",
        "model_decision": model_decision,
        "final_decision": final_decision,
        "guard_reason": guard_reason,
    }
    return case


def apply_guard(model_decision: str, case: CaseRecord) -> Tuple[str, Optional[str]]:
    """Stop an approve when the score is high or required fields are missing."""
    if model_decision != "approve":
        return model_decision, None
    reasons: List[str] = []
    score = None if not case.risk else case.risk.get("score")
    if isinstance(score, (int, float)) and not isinstance(score, bool) and score >= HIGH_SCORE_APPROVE_LIMIT:
        reasons.append("high score")
    missing = missing_sections(case)
    if missing:
        reasons.append("missing sections")
    if not reasons:
        return model_decision, None
    return "refer", "; ".join(reasons)


def missing_sections(case: CaseRecord) -> List[str]:
    intake = case.intake or {}
    missing = []
    for field_name in REQUIRED_INTAKE_FIELDS:
        value = intake.get(field_name)
        if value is None or value == "":
            missing.append(field_name)
    return missing


def _field(content: Dict[str, Any], name: str) -> Any:
    if name in content:
        return content[name]
    lowered = {str(key).lower(): value for key, value in content.items()}
    return lowered.get(name.lower())


def _remember_usage(case: CaseRecord, response: Any) -> None:
    case.last_usage = {
        "prompt_tokens": int(response.prompt_tokens),
        "completion_tokens": int(response.completion_tokens),
    }


def _text(value: Any) -> Optional[str]:
    if value is None:
        return None
    if isinstance(value, str):
        stripped = value.strip()
        if not stripped or stripped.lower() in {"null", "none", "unknown", "n/a"}:
            return None
        return stripped
    return str(value)


def _optional_number(value: Any) -> Optional[int]:
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        cleaned = value.strip().replace(",", "").replace("$", "")
        if not cleaned or cleaned.lower() in {"null", "none", "unknown", "n/a"}:
            return None
        try:
            return int(float(cleaned))
        except ValueError:
            return None
    return None


def _string_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    items = []
    for item in value:
        text = _text(item)
        if text:
            items.append(text)
    return items


def _band(score: int, raw: Any) -> str:
    text = (_text(raw) or "").lower()
    if text in {"moderate", "med"}:
        text = "medium"
    if text in {"low", "medium", "high"}:
        return text
    if score >= HIGH_SCORE_APPROVE_LIMIT:
        return "high"
    if score >= 35:
        return "medium"
    return "low"


def _decision(value: Any) -> Optional[str]:
    text = (_text(value) or "").lower()
    if text in DECISIONS:
        return text
    if "approve" in text:
        return "approve"
    if "deny" in text or "decline" in text:
        return "deny"
    if "refer" in text:
        return "refer"
    return None
