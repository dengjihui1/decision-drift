"""Repository-local entry point for Decision Drift."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from decision_drift.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
