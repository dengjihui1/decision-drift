"""Deterministic drift, counterfactual, freshness, and calibration engine."""

from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from typing import Any


_MISSING = object()
_STATUS_RANK = {"ACTIVE": 0, "AT_RISK": 1, "STALE": 2, "REPLACED": 3}


def _get_fact(facts: dict[str, Any], path: str) -> Any:
    if path in facts:
        return facts[path]
    current: Any = facts
    for part in path.split("."):
        if not isinstance(current, dict) or part not in current:
            return _MISSING
        current = current[part]
    return current


def _compare(operator: str, observed: Any, expected: Any) -> bool:
    if operator == "eq":
        return observed == expected
    if operator in {"ne", "changed_from"}:
        return observed != expected
    if operator == "gt":
        return observed > expected
    if operator == "gte":
        return observed >= expected
    if operator == "lt":
        return observed < expected
    if operator == "lte":
        return observed <= expected
    if operator == "contains":
        return expected in observed
    if operator == "not_contains":
        return expected not in observed
    if operator == "in":
        return observed in expected
    if operator == "not_in":
        return observed not in expected
    if operator == "exists":
        return True
    raise ValueError(f"unsupported operator: {operator}")


def evaluate_rule(rule: dict[str, Any], event: dict[str, Any]) -> dict[str, Any]:
    observed = _get_fact(event.get("facts", {}), rule["fact"])
    result = {
        "rule_id": rule["id"],
        "event_id": event["id"],
        "event_date": event["observed_at"],
        "event_source": event["source"],
        "fact": rule["fact"],
        "operator": rule["operator"],
        "expected": rule.get("value"),
        "severity": rule["severity"],
        "message": rule["message"],
    }
    if observed is _MISSING:
        return {**result, "state": "UNOBSERVED", "observed": None}
    try:
        triggered = _compare(rule["operator"], observed, rule.get("value"))
    except (TypeError, ValueError) as exc:
        return {**result, "state": "ERROR", "observed": observed, "error": str(exc)}
    return {
        **result,
        "state": "TRIGGERED" if triggered else "NOT_TRIGGERED",
        "observed": observed,
    }


def _max_status(current: str, proposed: str) -> str:
    return proposed if _STATUS_RANK[proposed] > _STATUS_RANK[current] else current


def _expired_evidence(decision: dict[str, Any], review_date: date) -> list[dict[str, Any]]:
    expired: list[dict[str, Any]] = []
    for evidence in decision.get("evidence", []):
        days = evidence.get("expires_after_days")
        if days is None:
            continue
        expiry_date = date.fromisoformat(evidence["observed_at"]) + timedelta(days=days)
        if expiry_date <= review_date:
            expired.append(
                {
                    "evidence_id": evidence["id"],
                    "source": evidence["source"],
                    "expired_at": expiry_date.isoformat(),
                    "supports": evidence.get("supports", []),
                }
            )
    return expired


def check_ledger(ledger: dict[str, Any], events_document: dict[str, Any]) -> dict[str, Any]:
    review_date = date.fromisoformat(ledger["review_date"])
    events = events_document.get("events", [])
    eligible_events = [
        event for event in events if date.fromisoformat(event["observed_at"]) <= review_date
    ]
    ignored_future_event_ids = [
        event["id"] for event in events if date.fromisoformat(event["observed_at"]) > review_date
    ]
    decision_results: list[dict[str, Any]] = []

    for decision in ledger["decisions"]:
        made_at = date.fromisoformat(decision["made_at"])
        applicable_events = [
            event
            for event in eligible_events
            if date.fromisoformat(event["observed_at"]) >= made_at
        ]
        evaluations = [
            evaluate_rule(rule, event)
            for rule in decision.get("rules", [])
            for event in applicable_events
        ]
        triggered = [item for item in evaluations if item["state"] == "TRIGGERED"]
        triggered_ids = {item["rule_id"] for item in triggered}
        errors = [item for item in evaluations if item["state"] == "ERROR"]
        observed_rule_ids = {
            item["rule_id"] for item in evaluations if item["state"] != "UNOBSERVED"
        }
        unobserved_rules = [
            rule["id"] for rule in decision.get("rules", []) if rule["id"] not in observed_rule_ids
        ]
        expired = _expired_evidence(decision, review_date)
        review_overdue = bool(
            decision.get("next_review_at")
            and date.fromisoformat(decision["next_review_at"]) < review_date
        )

        derived_status = decision["status"]
        if derived_status != "REPLACED":
            if any(item["severity"] == "invalidate" for item in triggered):
                derived_status = _max_status(derived_status, "STALE")
            elif triggered or expired or review_overdue or errors:
                derived_status = _max_status(derived_status, "AT_RISK")

        reopened = []
        for alternative in decision.get("alternatives", []):
            causes = sorted(triggered_ids.intersection(alternative.get("reopen_when", [])))
            if causes:
                reopened.append(
                    {
                        "alternative_id": alternative["id"],
                        "label": alternative["label"],
                        "rejected_because": alternative["rejected_because"],
                        "triggered_by": causes,
                        "state": "REOPENED",
                    }
                )

        decision_results.append(
            {
                "decision_id": decision["id"],
                "title": decision["title"],
                "choice": decision["choice"],
                "previous_status": decision["status"],
                "derived_status": derived_status,
                "reversibility": decision["reversibility"],
                "review_overdue": review_overdue,
                "triggered_rules": triggered,
                "expired_evidence": expired,
                "reopened_alternatives": reopened,
                "unobserved_rule_ids": unobserved_rules,
                "evaluation_errors": errors,
                "next_actions": deepcopy(decision.get("next_actions", [])),
                "evaluations": evaluations,
            }
        )

    counts = {status: 0 for status in _STATUS_RANK}
    for item in decision_results:
        counts[item["derived_status"]] += 1
    return {
        "schema_version": "0.1.0",
        "project": deepcopy(ledger["project"]),
        "review_date": ledger["review_date"],
        "event_window": {
            "supplied": len(events),
            "eligible_as_of_review_date": len(eligible_events),
            "ignored_future_event_ids": ignored_future_event_ids,
        },
        "summary": counts,
        "decisions": decision_results,
    }


def calibrate_ledger(ledger: dict[str, Any]) -> dict[str, Any]:
    review_date = date.fromisoformat(ledger["review_date"])
    results: list[dict[str, Any]] = []
    excluded_future_actual_ids: list[str] = []
    for decision in ledger["decisions"]:
        for prediction in decision.get("predictions", []):
            if "actual" not in prediction:
                continue
            actual_observed_at = date.fromisoformat(prediction["actual_observed_at"])
            if actual_observed_at > review_date:
                excluded_future_actual_ids.append(prediction["id"])
                continue
            lower = float(prediction["lower"])
            upper = float(prediction["upper"])
            actual = float(prediction["actual"])
            midpoint = (lower + upper) / 2
            if actual < lower:
                range_position = "BELOW"
                distance = lower - actual
            elif actual > upper:
                range_position = "ABOVE"
                distance = actual - upper
            else:
                range_position = "INSIDE"
                distance = 0.0
            results.append(
                {
                    "decision_id": decision["id"],
                    "decision_title": decision["title"],
                    "prediction_id": prediction["id"],
                    "metric": prediction["metric"],
                    "unit": prediction["unit"],
                    "predicted_range": [lower, upper],
                    "actual": actual,
                    "actual_observed_at": prediction["actual_observed_at"],
                    "range_position": range_position,
                    "distance_to_range": distance,
                    "signed_midpoint_error": actual - midpoint,
                    "relative_midpoint_error": None if midpoint == 0 else (actual - midpoint) / abs(midpoint),
                }
            )
    hits = sum(item["range_position"] == "INSIDE" for item in results)
    return {
        "schema_version": "0.1.0",
        "project": deepcopy(ledger["project"]),
        "prediction_count": len(results),
        "excluded_future_actual_ids": excluded_future_actual_ids,
        "range_hit_count": hits,
        "range_hit_rate": None if not results else hits / len(results),
        "predictions": results,
        "warning": "Calibration describes these recorded predictions only; it is not a global score of decision quality.",
    }
