"""Run the timeout SSN through the real pipeline and escalate when scoring times out.

Intake and enrichment call Ollama. The risk-scoring client call raises
TimeoutError. This applicant is intentionally absent from the normal case list.
"""

from __future__ import annotations

import json
import sys

from underwriting.llm import OllamaClient, TimeoutInjectingClient
from underwriting.paths import FAILURE_TRACE_DIR
from underwriting.pipeline import run_pipeline
from underwriting.tracing import format_trace

APP_TIMEOUT = {
    "submission": (
        "Alex Rivera, 41, accountant in Illinois, requesting $250,000 renters coverage. "
        "No claims mentioned. SSN 900-10-0099."
    ),
}


def main() -> int:
    client = TimeoutInjectingClient(OllamaClient(), fail_agent="risk_scoring")
    case = run_pipeline(APP_TIMEOUT, client)
    print(format_trace(case))
    FAILURE_TRACE_DIR.mkdir(parents=True, exist_ok=True)
    path = FAILURE_TRACE_DIR / "900-10-0099.json"
    path.write_text(json.dumps(case.to_document(), indent=2) + "\n", encoding="utf-8")
    print("wrote {0}".format(path))
    print("status={0}".format(case.status))
    risk_errors = [
        span
        for span in case.trace
        if span["agent"] == "risk_scoring" and span["status"] == "error"
    ]
    if case.status != "escalated" or len(risk_errors) != 3:
        return 1
    if case.recommendation.get("source") != "escalation":
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
