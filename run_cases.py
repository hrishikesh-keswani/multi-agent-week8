"""Run the three normal applications and write their traces.

The warm-up call is not traced. It loads the local model so the case timings
are steady-state generation.
"""

from __future__ import annotations

import json
import sys

from underwriting.analyze import write_analysis
from underwriting.llm import OllamaClient
from underwriting.paths import DATA_DIR, TRACE_DIR
from underwriting.pipeline import run_pipeline
from underwriting.tracing import format_trace


def warm_up(llm: OllamaClient) -> None:
    llm.complete(
        agent="warmup",
        system="Return one small JSON object.",
        user='{"ready": true}',
    )


def main() -> int:
    applications = json.loads((DATA_DIR / "applications.json").read_text(encoding="utf-8"))
    llm = OllamaClient()
    print("warming up {0}".format(llm.model))
    warm_up(llm)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)
    failed = []
    for raw in applications:
        case = run_pipeline(raw, llm)
        path = TRACE_DIR / "{0}.json".format(case.case_id)
        path.write_text(json.dumps(case.to_document(), indent=2) + "\n", encoding="utf-8")
        print(format_trace(case))
        print("wrote {0}".format(path))
        print()
        if case.status != "completed":
            failed.append(case.case_id)
    analysis = write_analysis()
    print("wrote {0}".format(analysis))
    if failed:
        print("escalated cases: {0}".format(", ".join(failed)))
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
