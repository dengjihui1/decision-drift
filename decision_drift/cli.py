"""Command-line interface for Decision Drift."""

from __future__ import annotations

import argparse
import json
import sys
from copy import deepcopy
from pathlib import Path
from typing import Any

from .engine import calibrate_ledger, check_ledger
from .reporting import render_calibration_markdown, render_drift_markdown, render_mermaid
from .validation import validate_events, validate_ledger


def _read_json(path: str) -> Any:
    with Path(path).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _print_errors(errors: list[str]) -> None:
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)


def _validated_inputs(ledger_path: str, events_path: str | None = None) -> tuple[dict[str, Any], dict[str, Any] | None] | None:
    try:
        ledger = _read_json(ledger_path)
        events = _read_json(events_path) if events_path else None
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return None
    errors = validate_ledger(ledger)
    if events is not None:
        errors.extend(validate_events(events))
    if errors:
        _print_errors(errors)
        return None
    return ledger, events


def command_validate(args: argparse.Namespace) -> int:
    validated = _validated_inputs(args.ledger, args.events)
    if validated is None:
        return 1
    print("VALID: Decision Drift inputs passed structural and reference checks")
    return 0


def command_check(args: argparse.Namespace) -> int:
    validated = _validated_inputs(args.ledger, args.events)
    if validated is None:
        return 1
    ledger, events = validated
    assert events is not None
    if args.review_date:
        candidate = deepcopy(ledger)
        candidate["review_date"] = args.review_date
        date_errors = validate_ledger(candidate)
        if date_errors:
            _print_errors(date_errors)
            return 1
        ledger = candidate
    report = check_ledger(ledger, events)
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "drift-report.json", report)
    _write_text(output_dir / "DRIFT_REPORT.md", render_drift_markdown(report))
    _write_text(output_dir / "decision-graph.mmd", render_mermaid(report))
    print(
        "CHECKED: "
        + ", ".join(f"{status}={count}" for status, count in report["summary"].items())
    )
    return 0


def command_calibrate(args: argparse.Namespace) -> int:
    validated = _validated_inputs(args.ledger)
    if validated is None:
        return 1
    ledger, _ = validated
    report = calibrate_ledger(ledger)
    output_dir = Path(args.output_dir)
    _write_json(output_dir / "calibration-report.json", report)
    _write_text(output_dir / "CALIBRATION_REPORT.md", render_calibration_markdown(report))
    print(f"CALIBRATED: predictions={report['prediction_count']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="decision-drift",
        description="Detect when the premises behind recorded decisions need review.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="validate ledger and optional events")
    validate_parser.add_argument("ledger")
    validate_parser.add_argument("events", nargs="?")
    validate_parser.set_defaults(func=command_validate)

    check_parser = subparsers.add_parser("check", help="evaluate events against a decision ledger")
    check_parser.add_argument("ledger")
    check_parser.add_argument("events")
    check_parser.add_argument("--output-dir", default="decision-drift-output")
    check_parser.add_argument("--review-date", help="override the ledger review date")
    check_parser.set_defaults(func=command_check)

    calibration_parser = subparsers.add_parser("calibrate", help="compare predictions with outcomes")
    calibration_parser.add_argument("ledger")
    calibration_parser.add_argument("--output-dir", default="decision-drift-output")
    calibration_parser.set_defaults(func=command_calibrate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
