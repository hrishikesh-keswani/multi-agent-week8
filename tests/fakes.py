"""Deterministic stand-in for the four agent calls."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from underwriting.llm import LLMResponse

PROFILES: Dict[str, Dict[str, Any]] = {
    "APP-CLEAN": {
        "full_name": "Maya Chen",
        "age": 29,
        "occupation": "software engineer",
        "coverage_type": "renters",
        "coverage_amount": 100000,
        "state": "OH",
        "household": "single",
        "notes": "No prior claims.",
        "summary": "Complete renters application with a clean bureau record.",
        "red_flags": [],
        "missing_fields": [],
        "risk_notes": "Low occupational and credit risk.",
        "score": 18,
        "band": "low",
        "factors": ["no prior claims", "excellent credit"],
        "decision": "approve",
        "rationale": "Complete file and a low risk score.",
    },
    "APP-COAST": {
        "full_name": "Robert Hale",
        "age": 58,
        "occupation": "commercial fisherman",
        "coverage_type": "homeowners",
        "coverage_amount": 1200000,
        "state": "FL",
        "household": "not stated",
        "notes": "Two recent water claims on a flood-zone beach house.",
        "summary": "High-value coastal home with prior water claims.",
        "red_flags": ["two prior claims", "flood zone", "high coverage amount"],
        "missing_fields": [],
        "risk_notes": "Repeated water claims in a flood zone.",
        "score": 86,
        "band": "high",
        "factors": ["flood zone", "prior claims", "high coverage"],
        "decision": "approve",
        "rationale": "The model approved despite the risk factors.",
    },
    "APP-THIN": {
        "full_name": "Jordan Lee",
        "age": None,
        "occupation": "roofing",
        "coverage_type": None,
        "coverage_amount": None,
        "state": None,
        "household": None,
        "notes": "Age, state, and coverage amount were not provided.",
        "summary": "Thin file with several missing applicant facts.",
        "red_flags": ["medium-risk occupation"],
        "missing_fields": ["age", "state", "coverage amount"],
        "risk_notes": "Not enough information for a firm decision.",
        "score": 52,
        "band": "medium",
        "factors": ["missing age", "missing coverage amount"],
        "decision": "refer",
        "rationale": "The file is incomplete.",
    },
    "APP-TIMEOUT": {
        "full_name": "Alex Rivera",
        "age": 41,
        "occupation": "accountant",
        "coverage_type": "renters",
        "coverage_amount": 250000,
        "state": "IL",
        "household": "not stated",
        "notes": "No claims mentioned.",
        "summary": "Complete renters file used for the timeout drill.",
        "red_flags": [],
        "missing_fields": [],
        "risk_notes": "Ordinary risk before the scoring call fails.",
        "score": 25,
        "band": "low",
        "factors": ["no prior claims"],
        "decision": "approve",
        "rationale": "This decision must not be reached when scoring times out.",
    },
}


class FakeLLM:
    def __init__(self, prompt_tokens: int = 100, completion_tokens: int = 40) -> None:
        self.calls: List[str] = []
        self.prompt_tokens = prompt_tokens
        self.completion_tokens = completion_tokens

    def complete(self, *, agent: str, system: str, user: str) -> LLMResponse:
        del system
        self.calls.append(agent)
        applicant_id = _applicant_id(user)
        profile = PROFILES[applicant_id]
        if agent == "intake":
            content = {
                "applicant_id": applicant_id,
                "full_name": profile["full_name"],
                "age": profile["age"],
                "occupation": profile["occupation"],
                "coverage_type": profile["coverage_type"],
                "coverage_amount": profile["coverage_amount"],
                "state": profile["state"],
                "household": profile["household"],
                "notes": profile["notes"],
            }
        elif agent == "enrichment":
            content = {
                "summary": profile["summary"],
                "red_flags": profile["red_flags"],
                "missing_fields": profile["missing_fields"],
                "risk_notes": profile["risk_notes"],
            }
        elif agent == "risk_scoring":
            content = {
                "score": profile["score"],
                "band": profile["band"],
                "factors": profile["factors"],
            }
        elif agent == "recommendation":
            content = {
                "decision": profile["decision"],
                "rationale": profile["rationale"],
            }
        else:
            content = {"ready": True}
        return LLMResponse(
            content=content,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            duration_ms=1,
        )


def _applicant_id(user: str) -> str:
    payload = json.loads(user)
    found = _walk(payload)
    if not found:
        raise KeyError("fake client could not find applicant_id")
    return found


def _walk(value: Any) -> Optional[str]:
    if isinstance(value, dict):
        applicant_id = value.get("applicant_id")
        if isinstance(applicant_id, str):
            return applicant_id
        for nested in value.values():
            found = _walk(nested)
            if found:
                return found
    return None
