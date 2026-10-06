"""Analysis text from trace files."""

import json

from underwriting.analyze import load_case_traces, render_analysis


def test_analysis_notes_warmup_and_prices_completed_cases_only(tmp_path):
    completed = {
        "case_id": "APP-CLEAN",
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
    escalated = {
        "case_id": "APP-TIMEOUT",
        "status": "escalated",
        "spans": [
            {
                "agent": "risk_scoring",
                "duration_ms": 999999,
                "token_usage": {"prompt_tokens": 5000, "completion_tokens": 5000},
            }
        ],
    }
    (tmp_path / "APP-CLEAN.json").write_text(json.dumps(completed), encoding="utf-8")
    (tmp_path / "APP-TIMEOUT.json").write_text(json.dumps(escalated), encoding="utf-8")

    text = render_analysis(load_case_traces(tmp_path))
    assert "warm-up" in text
    assert "steady-state" in text
    assert "Actual API cost is $0" in text
    assert "$0.000180" in text
    assert "999999" not in text
    assert "APP-TIMEOUT" not in text
    assert "overnight batch" in text
