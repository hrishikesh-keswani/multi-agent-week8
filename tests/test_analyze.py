"""Analysis text from trace files."""

import json

from underwriting.analyze import load_case_traces, render_analysis, write_analysis

COMPLETED = {
    "case_id": "900-01-0001",
    "status": "completed",
    "recommendation": {"decision": "approve"},
    "spans": [
        {
            "agent": "intake",
            "duration_ms": 12000,
            "token_usage": {"prompt_tokens": 1000, "completion_tokens": 200},
        }
    ],
}

TIMEOUT = {
    "case_id": "900-10-0099",
    "status": "escalated",
    "risk": None,
    "recommendation": {
        "decision": "refer",
        "source": "escalation",
        "rationale": "risk_scoring failed after 3 attempts: simulated upstream timeout",
    },
    "spans": [
        {
            "agent": "intake",
            "status": "ok",
            "duration_ms": 5000,
            "token_usage": {"prompt_tokens": 200, "completion_tokens": 100},
        },
        {
            "agent": "risk_scoring",
            "status": "error",
            "error": "TimeoutError: simulated upstream timeout",
            "duration_ms": 0,
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0},
        },
        {
            "agent": "risk_scoring",
            "status": "error",
            "error": "TimeoutError: simulated upstream timeout",
            "duration_ms": 0,
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0},
        },
        {
            "agent": "risk_scoring",
            "status": "error",
            "error": "TimeoutError: simulated upstream timeout",
            "duration_ms": 0,
            "token_usage": {"prompt_tokens": 0, "completion_tokens": 0},
        },
    ],
}

DISAGREE = {
    "case_id": "900-01-0016",
    "status": "escalated",
    "risk": {
        "score": None,
        "band": None,
        "llm_score": 20,
        "llm_band": "low",
        "deterministic_score": 50,
        "deterministic_band": "medium",
        "agreed": False,
    },
    "recommendation": {
        "decision": "refer",
        "source": "escalation",
        "rationale": "risk bands disagree: llm=low deterministic=medium",
    },
    "spans": [
        {
            "agent": "risk_scoring",
            "status": "ok",
            "duration_ms": 3000,
            "token_usage": {"prompt_tokens": 300, "completion_tokens": 50},
        }
    ],
}


def test_completed_totals_exclude_escalated_cases(tmp_path):
    (tmp_path / "900-01-0001.json").write_text(json.dumps(COMPLETED), encoding="utf-8")
    (tmp_path / "900-10-0099.json").write_text(json.dumps(TIMEOUT), encoding="utf-8")

    text = render_analysis(load_case_traces(tmp_path))
    assert "warm-up" in text
    assert "steady-state" in text
    assert "Actual API cost is $0" in text
    assert "- Cases: 1" in text
    assert "- Total tokens: 1000 prompt, 200 completion" in text
    assert "$0.000180" in text
    assert "overnight batch" in text


def test_escalated_cases_get_their_own_section(tmp_path):
    (tmp_path / "900-01-0001.json").write_text(json.dumps(COMPLETED), encoding="utf-8")
    (tmp_path / "900-10-0099.json").write_text(json.dumps(TIMEOUT), encoding="utf-8")
    (tmp_path / "900-01-0016.json").write_text(json.dumps(DISAGREE), encoding="utf-8")

    text = render_analysis(load_case_traces(tmp_path))
    head, _, escalated = text.partition("## Escalated cases")
    assert "900-10-0099" not in head
    assert "900-01-0016" not in head
    assert "| 900-10-0099 | risk_scoring | 3 attempt(s) failed: TimeoutError: simulated upstream timeout | 5.0 s | 200 | 100 |" in escalated
    assert "| 900-01-0016 | risk_scoring | risk bands disagree: llm low (20) vs deterministic medium (50) | 3.0 s | 300 | 50 |" in escalated


def test_no_escalations_is_stated(tmp_path):
    (tmp_path / "900-01-0001.json").write_text(json.dumps(COMPLETED), encoding="utf-8")
    text = render_analysis(load_case_traces(tmp_path))
    assert "No case was escalated to human review." in text


def test_write_analysis_reads_the_failure_folder_too(tmp_path):
    traces = tmp_path / "traces"
    failures = tmp_path / "failure-traces"
    traces.mkdir()
    failures.mkdir()
    (traces / "900-01-0001.json").write_text(json.dumps(COMPLETED), encoding="utf-8")
    (failures / "900-10-0099.json").write_text(json.dumps(TIMEOUT), encoding="utf-8")
    destination = tmp_path / "ANALYSIS.md"

    write_analysis(trace_dir=traces, destination=destination, failure_dir=failures)
    text = destination.read_text(encoding="utf-8")
    assert "- Cases: 1" in text
    assert "| 900-10-0099 |" in text
