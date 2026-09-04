from __future__ import annotations

import json
import tempfile
import unittest
from copy import deepcopy
from pathlib import Path

from decision_drift.cli import main
from decision_drift.engine import calibrate_ledger, check_ledger, evaluate_rule
from decision_drift.reporting import render_drift_markdown
from decision_drift.validation import validate_events, validate_ledger


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


class DecisionDriftTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = load_json(ROOT / "demo" / "decision-ledger.json")
        cls.events = load_json(ROOT / "demo" / "events.json")

    def test_demo_inputs_validate(self):
        self.assertEqual(validate_ledger(self.ledger), [])
        self.assertEqual(validate_events(self.events), [])

    def test_missing_fact_is_unobserved(self):
        rule = self.ledger["decisions"][0]["rules"][0]
        event = {"id": "empty", "observed_at": "2026-06-01", "source": "synthetic", "facts": {}}
        result = evaluate_rule(rule, event)
        self.assertEqual(result["state"], "UNOBSERVED")

    def test_trigger_keeps_event_provenance(self):
        rule = self.ledger["decisions"][0]["rules"][0]
        event = self.events["events"][0]
        result = evaluate_rule(rule, event)
        self.assertEqual(result["event_source"], event["source"])

    def test_invalidation_and_counterfactual_reopening(self):
        report = check_ledger(self.ledger, self.events)
        sqlite = report["decisions"][0]
        self.assertEqual(sqlite["derived_status"], "STALE")
        self.assertEqual(sqlite["reopened_alternatives"][0]["alternative_id"], "alternative-postgresql")
        self.assertIn("rule-multiple-writers", sqlite["reopened_alternatives"][0]["triggered_by"])

    def test_expired_evidence_is_reported(self):
        report = check_ledger(self.ledger, {"events": []})
        sqlite = report["decisions"][0]
        self.assertEqual(sqlite["derived_status"], "AT_RISK")
        self.assertEqual(sqlite["expired_evidence"][0]["evidence_id"], "evidence-january-load-test")

    def test_replaced_decision_is_not_reactivated(self):
        ledger = deepcopy(self.ledger)
        ledger["decisions"][0]["status"] = "REPLACED"
        report = check_ledger(ledger, self.events)
        self.assertEqual(report["decisions"][0]["derived_status"], "REPLACED")

    def test_future_events_are_excluded_from_as_of_review(self):
        events = deepcopy(self.events)
        events["events"].append(
            {
                "id": "future-invalidation",
                "observed_at": "2027-01-01",
                "source": "synthetic://future",
                "facts": {"team": {"concurrent_writers": 100}},
            }
        )
        report = check_ledger(self.ledger, events)
        self.assertEqual(report["event_window"]["eligible_as_of_review_date"], 3)
        self.assertEqual(report["event_window"]["ignored_future_event_ids"], ["future-invalidation"])
        triggered_event_ids = {
            item["event_id"]
            for decision in report["decisions"]
            for item in decision["triggered_rules"]
        }
        self.assertNotIn("future-invalidation", triggered_event_ids)

    def test_events_before_decision_are_not_applied(self):
        events = {
            "events": [
                {
                    "id": "pre-decision",
                    "observed_at": "2025-12-01",
                    "source": "synthetic://past",
                    "facts": {"team": {"concurrent_writers": 100}},
                }
            ]
        }
        report = check_ledger(self.ledger, events)
        sqlite = report["decisions"][0]
        self.assertEqual(sqlite["triggered_rules"], [])

    def test_calibration_distinguishes_hit_and_miss(self):
        report = calibrate_ledger(self.ledger)
        self.assertEqual(report["prediction_count"], 2)
        self.assertEqual(report["range_hit_count"], 1)
        positions = {item["prediction_id"]: item["range_position"] for item in report["predictions"]}
        self.assertEqual(positions["prediction-metadata-latency"], "ABOVE")
        self.assertEqual(positions["prediction-ticket-reduction"], "INSIDE")

    def test_unknown_reference_fails_validation(self):
        ledger = deepcopy(self.ledger)
        ledger["decisions"][0]["rules"][0]["assumption_id"] = "missing-assumption"
        errors = validate_ledger(ledger)
        self.assertTrue(any("unknown assumption" in error for error in errors))

    def test_cli_writes_reviewable_outputs(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = main(
                [
                    "check",
                    str(ROOT / "demo" / "decision-ledger.json"),
                    str(ROOT / "demo" / "events.json"),
                    "--output-dir",
                    temp_dir,
                ]
            )
            self.assertEqual(result, 0)
            self.assertTrue((Path(temp_dir) / "DRIFT_REPORT.md").exists())
            self.assertTrue((Path(temp_dir) / "drift-report.json").exists())
            self.assertTrue((Path(temp_dir) / "decision-graph.mmd").exists())

    def test_markdown_keeps_interpretation_boundary(self):
        report = check_ledger(self.ledger, self.events)
        text = render_drift_markdown(report)
        self.assertIn("does not prove", text)
        self.assertIn("REOPENED", text)


if __name__ == "__main__":
    unittest.main()
