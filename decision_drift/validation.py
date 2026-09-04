"""Structural and referential validation for Decision Drift inputs."""

from __future__ import annotations

from datetime import date
from typing import Any


SUPPORTED_OPERATORS = {
    "eq",
    "ne",
    "gt",
    "gte",
    "lt",
    "lte",
    "contains",
    "not_contains",
    "in",
    "not_in",
    "changed_from",
    "exists",
}
STATUSES = {"ACTIVE", "AT_RISK", "STALE", "REPLACED"}
SEVERITIES = {"warning", "invalidate"}


def _is_date(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def _require_text(errors: list[str], value: Any, path: str) -> None:
    if not isinstance(value, str) or not value.strip():
        errors.append(f"{path} must be a non-empty string")


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def validate_ledger(ledger: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(ledger, dict):
        return ["ledger must be a JSON object"]
    if ledger.get("schema_version") != "0.1.0":
        errors.append("schema_version must be 0.1.0")
    project = ledger.get("project")
    if not isinstance(project, dict):
        errors.append("project must be an object")
    else:
        _require_text(errors, project.get("id"), "project.id")
        _require_text(errors, project.get("name"), "project.name")
    if not _is_date(ledger.get("review_date")):
        errors.append("review_date must be an ISO date")

    decisions = ledger.get("decisions")
    if not isinstance(decisions, list) or not decisions:
        errors.append("decisions must be a non-empty array")
        return errors

    decision_ids = [d.get("id") for d in decisions if isinstance(d, dict) and isinstance(d.get("id"), str)]
    for duplicate in sorted(_duplicates(decision_ids)):
        errors.append(f"duplicate decision id: {duplicate}")

    for index, decision in enumerate(decisions):
        path = f"decisions[{index}]"
        if not isinstance(decision, dict):
            errors.append(f"{path} must be an object")
            continue
        for field in ("id", "title", "choice", "rationale"):
            _require_text(errors, decision.get(field), f"{path}.{field}")
        if not _is_date(decision.get("made_at")):
            errors.append(f"{path}.made_at must be an ISO date")
        if decision.get("status") not in STATUSES:
            errors.append(f"{path}.status must be one of {sorted(STATUSES)}")
        if decision.get("reversibility") not in {"easy", "medium", "hard", "irreversible"}:
            errors.append(f"{path}.reversibility is invalid")
        if "next_review_at" in decision and not _is_date(decision.get("next_review_at")):
            errors.append(f"{path}.next_review_at must be an ISO date")

        assumptions = decision.get("assumptions")
        if not isinstance(assumptions, list):
            errors.append(f"{path}.assumptions must be an array")
            assumptions = []
        assumption_ids = [a.get("id") for a in assumptions if isinstance(a, dict) and isinstance(a.get("id"), str)]
        for duplicate in sorted(_duplicates(assumption_ids)):
            errors.append(f"{path} duplicate assumption id: {duplicate}")
        for a_index, assumption in enumerate(assumptions):
            a_path = f"{path}.assumptions[{a_index}]"
            if not isinstance(assumption, dict):
                errors.append(f"{a_path} must be an object")
                continue
            _require_text(errors, assumption.get("id"), f"{a_path}.id")
            _require_text(errors, assumption.get("statement"), f"{a_path}.statement")
            if assumption.get("source") not in {"explicit", "inferred"}:
                errors.append(f"{a_path}.source must be explicit or inferred")
            if assumption.get("confidence") not in {"low", "medium", "high"}:
                errors.append(f"{a_path}.confidence is invalid")
            if assumption.get("state") not in {"unknown", "holding", "challenged", "invalidated"}:
                errors.append(f"{a_path}.state is invalid")

        rules = decision.get("rules")
        if not isinstance(rules, list):
            errors.append(f"{path}.rules must be an array")
            rules = []
        rule_ids = [r.get("id") for r in rules if isinstance(r, dict) and isinstance(r.get("id"), str)]
        for duplicate in sorted(_duplicates(rule_ids)):
            errors.append(f"{path} duplicate rule id: {duplicate}")
        for r_index, rule in enumerate(rules):
            r_path = f"{path}.rules[{r_index}]"
            if not isinstance(rule, dict):
                errors.append(f"{r_path} must be an object")
                continue
            for field in ("id", "assumption_id", "fact", "message"):
                _require_text(errors, rule.get(field), f"{r_path}.{field}")
            if rule.get("assumption_id") not in assumption_ids:
                errors.append(f"{r_path}.assumption_id references an unknown assumption")
            if rule.get("operator") not in SUPPORTED_OPERATORS:
                errors.append(f"{r_path}.operator is unsupported")
            if rule.get("operator") != "exists" and "value" not in rule:
                errors.append(f"{r_path}.value is required for {rule.get('operator')}")
            if rule.get("severity") not in SEVERITIES:
                errors.append(f"{r_path}.severity must be warning or invalidate")

        evidence = decision.get("evidence")
        if not isinstance(evidence, list):
            errors.append(f"{path}.evidence must be an array")
            evidence = []
        evidence_ids = [e.get("id") for e in evidence if isinstance(e, dict) and isinstance(e.get("id"), str)]
        for duplicate in sorted(_duplicates(evidence_ids)):
            errors.append(f"{path} duplicate evidence id: {duplicate}")
        for e_index, item in enumerate(evidence):
            e_path = f"{path}.evidence[{e_index}]"
            if not isinstance(item, dict):
                errors.append(f"{e_path} must be an object")
                continue
            for field in ("id", "kind", "source"):
                _require_text(errors, item.get(field), f"{e_path}.{field}")
            if not _is_date(item.get("observed_at")):
                errors.append(f"{e_path}.observed_at must be an ISO date")
            expiry = item.get("expires_after_days")
            if expiry is not None and (not isinstance(expiry, int) or expiry < 1):
                errors.append(f"{e_path}.expires_after_days must be a positive integer")
            supports = item.get("supports")
            if not isinstance(supports, list):
                errors.append(f"{e_path}.supports must be an array")
            else:
                for assumption_id in supports:
                    if assumption_id not in assumption_ids:
                        errors.append(f"{e_path}.supports references unknown assumption {assumption_id}")

        alternatives = decision.get("alternatives")
        if not isinstance(alternatives, list):
            errors.append(f"{path}.alternatives must be an array")
            alternatives = []
        alternative_ids = [a.get("id") for a in alternatives if isinstance(a, dict) and isinstance(a.get("id"), str)]
        for duplicate in sorted(_duplicates(alternative_ids)):
            errors.append(f"{path} duplicate alternative id: {duplicate}")
        for alt_index, alternative in enumerate(alternatives):
            alt_path = f"{path}.alternatives[{alt_index}]"
            if not isinstance(alternative, dict):
                errors.append(f"{alt_path} must be an object")
                continue
            for field in ("id", "label", "rejected_because"):
                _require_text(errors, alternative.get(field), f"{alt_path}.{field}")
            reopen_when = alternative.get("reopen_when")
            if not isinstance(reopen_when, list):
                errors.append(f"{alt_path}.reopen_when must be an array")
            else:
                for rule_id in reopen_when:
                    if rule_id not in rule_ids:
                        errors.append(f"{alt_path}.reopen_when references unknown rule {rule_id}")

        predictions = decision.get("predictions")
        if not isinstance(predictions, list):
            errors.append(f"{path}.predictions must be an array")
            predictions = []
        prediction_ids = [p.get("id") for p in predictions if isinstance(p, dict) and isinstance(p.get("id"), str)]
        for duplicate in sorted(_duplicates(prediction_ids)):
            errors.append(f"{path} duplicate prediction id: {duplicate}")
        for p_index, prediction in enumerate(predictions):
            p_path = f"{path}.predictions[{p_index}]"
            if not isinstance(prediction, dict):
                errors.append(f"{p_path} must be an object")
                continue
            _require_text(errors, prediction.get("id"), f"{p_path}.id")
            _require_text(errors, prediction.get("metric"), f"{p_path}.metric")
            _require_text(errors, prediction.get("unit"), f"{p_path}.unit")
            lower, upper = prediction.get("lower"), prediction.get("upper")
            if not isinstance(lower, (int, float)) or not isinstance(upper, (int, float)):
                errors.append(f"{p_path}.lower and upper must be numbers")
            elif lower > upper:
                errors.append(f"{p_path}.lower must not exceed upper")
            if "actual" in prediction and not isinstance(prediction.get("actual"), (int, float)):
                errors.append(f"{p_path}.actual must be a number")
            for date_field in ("due_at", "actual_observed_at"):
                if date_field in prediction and not _is_date(prediction.get(date_field)):
                    errors.append(f"{p_path}.{date_field} must be an ISO date")

    return errors


def validate_events(events_document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(events_document, dict):
        return ["events document must be a JSON object"]
    events = events_document.get("events")
    if not isinstance(events, list):
        return ["events must be an array"]
    ids: list[str] = []
    for index, event in enumerate(events):
        path = f"events[{index}]"
        if not isinstance(event, dict):
            errors.append(f"{path} must be an object")
            continue
        _require_text(errors, event.get("id"), f"{path}.id")
        if isinstance(event.get("id"), str):
            ids.append(event["id"])
        if not _is_date(event.get("observed_at")):
            errors.append(f"{path}.observed_at must be an ISO date")
        _require_text(errors, event.get("source"), f"{path}.source")
        if not isinstance(event.get("facts"), dict):
            errors.append(f"{path}.facts must be an object")
    for duplicate in sorted(_duplicates(ids)):
        errors.append(f"duplicate event id: {duplicate}")
    return errors
