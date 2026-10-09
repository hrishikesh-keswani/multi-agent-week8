"""Standalone agent tests against local Ollama."""

import pytest

from underwriting.agents import (
    enrichment_agent,
    intake_agent,
    recommendation_agent,
    risk_scoring_agent,
)
from underwriting.state import CaseRecord

CLEAN_APPLICATION = {
    "submission": (
        "Hi, I'm Maya Chen, 29, software engineer in Ohio. I rent an apartment "
        "and want $100,000 of renters insurance. No prior claims. Single household. "
        "SSN 900-01-0001."
    ),
}

KNOWN_INTAKE = {
    "ssn": "900-01-0001",
    "full_name": "Maya Chen",
    "age": 29,
    "occupation": "software engineer",
    "coverage_type": "renters",
    "coverage_amount": 100000,
    "state": "OH",
    "household": "single",
    "notes": "No prior claims.",
}

KNOWN_ENRICHMENT = {
    "ssn": "900-01-0001",
    "bureau": {
        "found": True,
        "prior_claims": 0,
        "credit_band": "excellent",
        "occupation_class": "low",
        "flood_zone": False,
    },
    "summary": "Clean renters application.",
    "red_flags": [],
    "missing_fields": [],
    "risk_notes": "Low risk bureau record.",
}

KNOWN_RISK = {
    "score": 22,
    "band": "low",
    "factors": ["no prior claims", "low occupation class"],
}


@pytest.mark.live
def test_intake_agent(live_llm):
    case = intake_agent(CaseRecord.from_application(CLEAN_APPLICATION), live_llm)
    assert case.intake["ssn"] == "900-01-0001"
    assert isinstance(case.intake["full_name"], str) and case.intake["full_name"]
    assert case.intake["coverage_type"]
    assert case.last_usage["prompt_tokens"] + case.last_usage["completion_tokens"] > 0


@pytest.mark.live
def test_enrichment_agent(live_llm):
    case = CaseRecord.from_application(CLEAN_APPLICATION)
    case.intake = dict(KNOWN_INTAKE)
    case = enrichment_agent(case, live_llm)
    assert case.enrichment["bureau"]["found"] is True
    assert case.enrichment["bureau"]["prior_claims"] == 0
    assert isinstance(case.enrichment["summary"], str) and case.enrichment["summary"]
    assert isinstance(case.enrichment["red_flags"], list)
    assert case.last_usage["prompt_tokens"] + case.last_usage["completion_tokens"] > 0


@pytest.mark.live
def test_risk_scoring_agent(live_llm):
    case = CaseRecord.from_application(CLEAN_APPLICATION)
    case.intake = dict(KNOWN_INTAKE)
    case.enrichment = dict(KNOWN_ENRICHMENT)
    case = risk_scoring_agent(case, live_llm)
    risk = case.risk
    assert risk["deterministic_score"] == 20
    assert risk["deterministic_band"] == "low"
    assert risk["llm_band"] in {"low", "medium", "high"}
    assert isinstance(risk["factors"], list)
    assert case.last_usage["prompt_tokens"] + case.last_usage["completion_tokens"] > 0
    if risk["agreed"]:
        assert risk["band"] == "low"
        assert isinstance(risk["score"], int)
        assert 0 <= risk["score"] <= 100
    else:
        assert risk["score"] is None
        assert risk["band"] is None
        assert case.status == "escalated"
        assert case.recommendation["source"] == "escalation"


@pytest.mark.live
def test_recommendation_agent(live_llm):
    case = CaseRecord.from_application(CLEAN_APPLICATION)
    case.intake = dict(KNOWN_INTAKE)
    case.enrichment = dict(KNOWN_ENRICHMENT)
    case.risk = dict(KNOWN_RISK)
    case = recommendation_agent(case, live_llm)
    recommendation = case.recommendation
    assert recommendation["decision"] in {"approve", "deny", "refer"}
    assert recommendation["source"] == "model"
    assert recommendation["model_decision"] in {"approve", "deny", "refer"}
    assert recommendation["final_decision"] == recommendation["decision"]
    if recommendation["model_decision"] == recommendation["final_decision"]:
        assert recommendation["guard_reason"] is None
    else:
        assert recommendation["guard_reason"]
    assert case.last_usage["prompt_tokens"] + case.last_usage["completion_tokens"] > 0
