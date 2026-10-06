"""Repository paths shared by loaders and scripts."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
TRACE_DIR = ROOT / "traces"
FAILURE_TRACE_DIR = ROOT / "failure-traces"
