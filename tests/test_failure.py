"""Retry-then-escalate, including the deterministic APP-TIMEOUT path."""

from underwriting.llm import TimeoutInjectingClient
from underwriting.paths import DATA_DIR, ROOT
from underwriting.pipeline import run_pipeline
from tests.fakes import FakeLLM

APP_TIMEOUT = {
    "applicant_id": "APP-TIMEOUT",
    "submission": (
        "Alex Rivera, 41, accountant in Illinois, requesting $250,000 renters coverage. "
        "No claims mentioned."
    ),
}


def test_risk_timeout_retries_then_escalates():
    fake = FakeLLM()
    client = TimeoutInjectingClient(fake, fail_agent="risk_scoring")
    case = run_pipeline(APP_TIMEOUT, client, backoff_s=(0, 0))

    assert case.status == "escalated"
    assert case.risk is None
    assert case.recommendation["decision"] == "refer"
    assert case.recommendation["final_decision"] == "refer"
    assert case.recommendation["source"] == "escalation"
    assert case.recommendation["guard_reason"] is None
    assert "recommendation" not in fake.calls
    assert fake.calls == ["intake", "enrichment"]

    risk_spans = [span for span in case.trace if span["agent"] == "risk_scoring"]
    assert [span["attempt"] for span in risk_spans] == [1, 2, 3]
    assert [span["status"] for span in risk_spans] == ["error", "error", "error"]
    assert all("TimeoutError" in span["error"] for span in risk_spans)
    assert all(span["agent"] != "recommendation" for span in case.trace)


def test_failure_of_any_agent_escalates_and_stops():
    fake = FakeLLM()
    client = TimeoutInjectingClient(fake, fail_agent="intake")
    case = run_pipeline(APP_TIMEOUT, client, backoff_s=(0, 0))

    assert case.status == "escalated"
    assert case.intake is None
    assert fake.calls == []
    assert [span["agent"] for span in case.trace] == ["intake", "intake", "intake"]
    assert case.recommendation["source"] == "escalation"


def test_timeout_applicant_stays_out_of_the_normal_run():
    applications = (DATA_DIR / "applications.json").read_text(encoding="utf-8")
    run_cases = (ROOT / "run_cases.py").read_text(encoding="utf-8")
    assert "APP-TIMEOUT" not in applications
    assert "APP-TIMEOUT" not in run_cases
    assert "warm" in run_cases.lower()
