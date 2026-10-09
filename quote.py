"""Run one application sentence through the pipeline and save its trace.

    python3 quote.py "Priya Shah, 31, librarian in Vermont. ... SSN 900-01-0001."
    echo "..." | python3 quote.py

There is no warm-up call, so a cold model makes the first case slower than the
batch numbers in ANALYSIS.md. The trace lands in quotes/{ssn}.json, outside the
traces/ folder that feeds the cost table.

Exit codes: 0 completed, 1 escalated, 2 bad input.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, List, Optional, Sequence

from underwriting.llm import OllamaClient
from underwriting.paths import QUOTE_DIR
from underwriting.pipeline import run_pipeline
from underwriting.tracing import format_trace

USAGE = 'usage: python3 quote.py [--no-save] "application sentence with an SSN"'


def main(
    argv: Optional[Sequence[str]] = None,
    llm: Any = None,
    quote_dir: Optional[Path] = None,
    stdin: Any = None,
) -> int:
    args: List[str] = list(sys.argv[1:] if argv is None else argv)
    save = True
    if "--no-save" in args:
        save = False
        args = [arg for arg in args if arg != "--no-save"]
    text = " ".join(args).strip()
    if not text:
        stream = sys.stdin if stdin is None else stdin
        if stream is not None and not getattr(stream, "isatty", lambda: False)():
            text = stream.read().strip()
    if not text:
        print(USAGE)
        return 2

    client = llm if llm is not None else OllamaClient()
    try:
        case = run_pipeline({"submission": text}, client)
    except ValueError as exc:
        print(str(exc))
        return 2

    print("no warm-up call: a cold model makes this slower than the batch numbers")
    print(format_trace(case))
    if save:
        folder = quote_dir or QUOTE_DIR
        folder.mkdir(parents=True, exist_ok=True)
        path = folder / "{0}.json".format(case.case_id)
        path.write_text(json.dumps(case.to_document(), indent=2) + "\n", encoding="utf-8")
        print("wrote {0}".format(path))
    print("status={0}".format(case.status))
    return 0 if case.status == "completed" else 1


if __name__ == "__main__":
    sys.exit(main())
