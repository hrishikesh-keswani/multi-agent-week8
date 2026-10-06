"""Pipeline wiring, traces, and the recommendation guard."""

import json

from underwriting.agents import apply_guard
from underwriting.llm import LLMError
from underwriting.paths import DATA_DIR
from underwriting.pipeline import run_pipeline
from underwriting.state import CaseRecord
from tests.fakes import FakeLLM


def _applications():
    return json.loads((DATA_DIR / "applications.json").read_text(encoding="utf-8"))


def _complete_intake():
    return {
        "applicant_id": "APP-CLEAN",
        "full_name": "Maya Chen",
        "age": 29,
        "occupation": "software engineer",
        "coverage_type": "renters",
        "coverage_amount": 100000,
        "state": "OH",
        "household": "single",
        "notes": "",
    }


def test_three_applications_complete_with_traces():
    cases = [run_pipeline(raw, FakeLLM(), backoff_s=(0, 0)) for raw in _applications()]
    by_id = {case.case_id: case for case in cases}
    assert set(by_id) == {"APP-CLEAN", "APP-COAST", "APP-THIN"}

    clean = by_id["APP-CLEAN"].recommendation
    assert clean["model_decision"] == "approve"
    assert clean["final_decision"] == "approve"
    assert clean["guard_reason"] is None
    assert clean["source"] == "model"

    coast = by_id["APP-COAST"].recommendation
    assert coast["model_decision"] == "approve"
    assert coast["final_decision"] == "refer"
    assert coast["decision"] == "refer"
    assert coast["guard_reason"] == "high score"
    assert coast["source"] == "model"

    thin = by_id["APP-THIN"].recommendation
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
        assert "APP-TIMEOUT" not in json.dumps(case.to_document())


def test_guard_blocks_high_score_and_missing_sections():
    case = CaseRecord.from_application({"applicant_id": "APP-CLEAN", "submission": "x"})
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
        {"applicant_id": "APP-CLEAN", "submission": "x"},
        BrokenJSON(),
        max_attempts=1,
        backoff_s=(0,),
    )
    assert case.status == "escalated"
    assert case.trace[0]["token_usage"] == {"prompt_tokens": 14, "completion_tokens": 5}
    assert case.trace[0]["status"] == "error"


def test_guard_leaves_a_clean_approval_unchanged():
    case = CaseRecord.from_application({"applicant_id": "APP-CLEAN", "submission": "x"})
    case.intake = _complete_intake()
    case.risk = {"score": 18, "band": "low", "factors": []}
    decision, reason = apply_guard("approve", case)
    assert decision == "approve"
    assert reason is None
