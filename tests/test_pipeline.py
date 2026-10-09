"""Pipeline wiring, traces, and the recommendation guard."""

import json

import pytest

from underwriting.agents import apply_guard
from underwriting.llm import LLMError
from underwriting.paths import DATA_DIR
from underwriting.pipeline import run_pipeline
from underwriting.ssn import extract_ssn
from underwriting.state import CaseRecord
from tests.fakes import FakeLLM


DEMO_APPLICATIONS = [
    {
        "submission": "Hi, I'm Maya Chen, 29, software engineer in Ohio. I rent an apartment and want $100,000 of renters insurance. No prior claims. Non-smoker, single household. SSN 900-01-0001.",
    },
    {
        "submission": "Robert Hale, age 58, commercial fisherman, wants $1,200,000 homeowners on a beach house in Florida. Two water claims in the last three years. Property is in a flood zone. SSN 900-01-0009.",
    },
    {
        "submission": "Applicant Jordan Lee is asking for coverage. Occupation might be roofing. State not provided. Coverage amount left blank. Age unknown. SSN 900-01-0015.",
    },
]


def _complete_intake():
    return {
        "ssn": "900-01-0001",
        "full_name": "Maya Chen",
        "age": 29,
        "occupation": "software engineer",
        "coverage_type": "renters",
        "coverage_amount": 100000,
        "state": "OH",
        "household": "single",
        "notes": "",
    }


def test_ssn_missing_from_bureau_goes_to_human_review():
    fake = FakeLLM()
    case = run_pipeline(
        {"submission": "New applicant Nora Kim, 33, teacher in Maine. SSN 900-99-9999."},
        fake,
        backoff_s=(0, 0),
    )
    assert case.status == "escalated"
    assert case.case_id == "900-99-9999"
    assert case.recommendation["decision"] == "refer"
    assert case.recommendation["source"] == "escalation"
    assert case.intake is None
    assert fake.calls == []
    assert case.trace[0]["agent"] == "bureau_lookup"
    assert case.trace[0]["status"] == "escalated"


def test_submission_without_an_ssn_is_rejected():
    with pytest.raises(ValueError, match="SSN"):
        CaseRecord.from_application({"submission": "Maya Chen needs renters insurance."})


def test_batch_file_has_twenty_applications_with_bureau_rows():
    applications = json.loads((DATA_DIR / "applications.json").read_text(encoding="utf-8"))
    bureau = json.loads((DATA_DIR / "bureau.json").read_text(encoding="utf-8"))
    assert len(applications) == 20
    ssns = [extract_ssn(row["submission"]) for row in applications]
    assert ssns == ["900-01-{0:04d}".format(number) for number in range(1, 21)]
    assert all(ssn in bureau for ssn in ssns)
    assert all("applicant_id" not in row for row in applications)


def test_three_applications_complete_with_traces():
    cases = [run_pipeline(raw, FakeLLM(), backoff_s=(0, 0)) for raw in DEMO_APPLICATIONS]
    by_id = {case.case_id: case for case in cases}
    assert set(by_id) == {"900-01-0001", "900-01-0009", "900-01-0015"}

    clean_risk = by_id["900-01-0001"].risk
    assert clean_risk["agreed"] is True
    assert clean_risk["llm_score"] == 18
    assert clean_risk["deterministic_score"] == 20
    assert clean_risk["band"] == "low"
    assert clean_risk["score"] == 20

    clean = by_id["900-01-0001"].recommendation
    assert clean["model_decision"] == "approve"
    assert clean["final_decision"] == "approve"
    assert clean["guard_reason"] is None
    assert clean["source"] == "model"

    coast = by_id["900-01-0009"].recommendation
    assert coast["model_decision"] == "approve"
    assert coast["final_decision"] == "refer"
    assert coast["decision"] == "refer"
    assert coast["guard_reason"] == "high score"
    assert coast["source"] == "model"

    thin = by_id["900-01-0015"].recommendation
    assert thin["decision"] == "refer"
    assert thin["guard_reason"] is None
    assert thin["source"] == "model"

    for case in cases:
        assert case.status == "completed"
        assert [span["agent"] for span in case.trace] == [
            "intake",
            "enrichment",
            "risk_scoring",
            "recommendation",
        ]
        for span in case.trace:
            assert span["attempt"] == 1
            assert span["status"] == "ok"
            assert span["started_at"]
            assert span["ended_at"]
            assert span["duration_ms"] >= 0
            assert "input" in span and "output" in span
            assert span["token_usage"] == {"prompt_tokens": 100, "completion_tokens": 40}
        recommendation_span = case.trace[-1]
        assert recommendation_span["model_decision"] == case.recommendation["model_decision"]
        assert recommendation_span["final_decision"] == case.recommendation["final_decision"]
        assert recommendation_span["guard_reason"] == case.recommendation["guard_reason"]
        assert "900-10-0099" not in json.dumps(case.to_document())


def test_band_disagreement_refers_without_another_try():
    class HighScoreOnClean(FakeLLM):
        def complete(self, *, agent, system, user):
            response = super(HighScoreOnClean, self).complete(agent=agent, system=system, user=user)
            if agent == "risk_scoring":
                response.content["score"] = 90
            return response

    fake = HighScoreOnClean()
    case = run_pipeline(DEMO_APPLICATIONS[0], fake, backoff_s=(0, 0))
    assert case.status == "escalated"
    assert case.risk["agreed"] is False
    assert case.risk["llm_band"] == "high"
    assert case.risk["deterministic_band"] == "low"
    assert case.risk["score"] is None
    assert case.risk["band"] is None
    assert case.recommendation["decision"] == "refer"
    assert case.recommendation["source"] == "escalation"
    assert case.recommendation["rationale"] == "risk bands disagree: llm=high deterministic=low"
    assert fake.calls == ["intake", "enrichment", "risk_scoring"]
    risk_spans = [span for span in case.trace if span["agent"] == "risk_scoring"]
    assert len(risk_spans) == 1
    assert risk_spans[0]["status"] == "ok"


def test_guard_blocks_high_score_and_missing_sections():
    case = CaseRecord.from_application({"submission": "Maya Chen. SSN 900-01-0001."})
    case.intake = _complete_intake()
    case.risk = {"score": 80, "band": "high", "factors": []}
    decision, reason = apply_guard("approve", case)
    assert decision == "refer"
    assert reason == "high score"

    case.intake["age"] = None
    decision, reason = apply_guard("approve", case)
    assert decision == "refer"
    assert reason == "high score; missing sections"

    case.risk["score"] = 10
    decision, reason = apply_guard("deny", case)
    assert decision == "deny"
    assert reason is None


def test_failed_repair_tokens_stay_on_the_error_span():
    class BrokenJSON:
        def complete(self, *, agent, system, user):
            del agent, system, user
            raise LLMError(
                "model returned invalid JSON after repair",
                prompt_tokens=14,
                completion_tokens=5,
            )

    case = run_pipeline(
        {"submission": "Maya Chen. SSN 900-01-0001."},
        BrokenJSON(),
        max_attempts=1,
        backoff_s=(0,),
    )
    assert case.status == "escalated"
    assert case.trace[0]["token_usage"] == {"prompt_tokens": 14, "completion_tokens": 5}
    assert case.trace[0]["status"] == "error"


def test_guard_leaves_a_clean_approval_unchanged():
    case = CaseRecord.from_application({"submission": "Maya Chen. SSN 900-01-0001."})
    case.intake = _complete_intake()
    case.risk = {"score": 18, "band": "low", "factors": []}
    decision, reason = apply_guard("approve", case)
    assert decision == "approve"
    assert reason is None
