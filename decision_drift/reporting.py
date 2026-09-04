"""Markdown and Mermaid renderers for Decision Drift results."""

from __future__ import annotations

import re
from typing import Any


def render_drift_markdown(report: dict[str, Any]) -> str:
    project = report["project"]
    lines = [
        "# Decision Drift Report",
        "",
        f"Project: **{project['name']}**  ",
        f"Review date: **{report['review_date']}**",
        f"Eligible events as of review date: **{report['event_window']['eligible_as_of_review_date']} / {report['event_window']['supplied']}**",
        "",
        "## Status summary",
        "",
        "| ACTIVE | AT_RISK | STALE | REPLACED |",
        "| ---: | ---: | ---: | ---: |",
        "| {ACTIVE} | {AT_RISK} | {STALE} | {REPLACED} |".format(**report["summary"]),
        "",
    ]
    for decision in report["decisions"]:
        lines.extend(
            [
                f"## {decision['title']}",
                "",
                f"- Decision: `{decision['decision_id']}`",
                f"- Choice: {decision['choice']}",
                f"- Status: **{decision['previous_status']} → {decision['derived_status']}**",
                f"- Reversibility: `{decision['reversibility']}`",
            ]
        )
        if decision["review_overdue"]:
            lines.append("- Review schedule: **OVERDUE**")
        lines.extend(["", "### Triggered premises", ""])
        if decision["triggered_rules"]:
            for item in decision["triggered_rules"]:
                lines.append(
                    f"- **{item['severity'].upper()}** `{item['rule_id']}` via `{item['event_id']}`: "
                    f"`{item['fact']}` observed as `{item['observed']}`. {item['message']} "
                    f"Source: `{item['event_source']}`"
                )
        else:
            lines.append("- None observed.")

        lines.extend(["", "### Evidence freshness", ""])
        if decision["expired_evidence"]:
            for item in decision["expired_evidence"]:
                lines.append(
                    f"- `{item['evidence_id']}` expired on {item['expired_at']}: {item['source']}"
                )
        else:
            lines.append("- No dated evidence has expired.")

        lines.extend(["", "### Counterfactual alternatives", ""])
        if decision["reopened_alternatives"]:
            for item in decision["reopened_alternatives"]:
                causes = ", ".join(f"`{rule_id}`" for rule_id in item["triggered_by"])
                lines.append(f"- **REOPENED:** {item['label']} (triggered by {causes})")
                lines.append(f"  - Originally rejected because: {item['rejected_because']}")
        else:
            lines.append("- No alternative was reopened.")

        lines.extend(["", "### Unknown observations", ""])
        if decision["unobserved_rule_ids"]:
            lines.append(
                "- No supplied event observed the facts required by: "
                + ", ".join(f"`{rule_id}`" for rule_id in decision["unobserved_rule_ids"])
            )
        else:
            lines.append("- All rule fact paths were observed at least once.")

        lines.extend(["", "### Bounded next actions", ""])
        if decision["next_actions"]:
            lines.extend(f"- {action}" for action in decision["next_actions"])
        else:
            lines.append("- No next action recorded; review before changing the decision.")
        lines.append("")

    ignored_future = report["event_window"]["ignored_future_event_ids"]
    if ignored_future:
        lines.extend(
            [
                "## Time-safe replay",
                "",
                "Events dated after the review boundary were excluded: "
                + ", ".join(f"`{event_id}`" for event_id in ignored_future),
                "",
            ]
        )

    lines.extend(
        [
            "## Interpretation boundary",
            "",
            "A triggered rule means a recorded premise deserves review. It does not prove that the original decision was irrational or that a reopened alternative is now best.",
            "",
        ]
    )
    return "\n".join(lines)


def render_calibration_markdown(report: dict[str, Any]) -> str:
    rate = report["range_hit_rate"]
    rate_text = "N/A" if rate is None else f"{rate:.1%}"
    lines = [
        "# Decision Calibration Report",
        "",
        f"Project: **{report['project']['name']}**  ",
        f"Recorded predictions with outcomes: **{report['prediction_count']}**  ",
        f"Range hit rate: **{rate_text}**",
        "",
        "| Decision | Metric | Predicted | Actual | Position | Distance |",
        "| --- | --- | --- | ---: | --- | ---: |",
    ]
    for item in report["predictions"]:
        low, high = item["predicted_range"]
        lines.append(
            f"| {item['decision_title']} | {item['metric']} ({item['unit']}) | "
            f"{low:g}–{high:g} | {item['actual']:g} | {item['range_position']} | "
            f"{item['distance_to_range']:g} |"
        )
    if report["excluded_future_actual_ids"]:
        lines.extend(
            [
                "",
                "Future outcomes excluded by the review boundary: "
                + ", ".join(
                    f"`{prediction_id}`"
                    for prediction_id in report["excluded_future_actual_ids"]
                ),
            ]
        )
    lines.extend(["", f"> {report['warning']}", ""])
    return "\n".join(lines)


def _mermaid_text(value: str) -> str:
    return value.replace('"', "'").replace("\n", " ")


def _mermaid_id(prefix: str, *parts: str) -> str:
    normalized = "_".join(parts)
    normalized = re.sub(r"[^A-Za-z0-9_]", "_", normalized)
    return f"{prefix}_{normalized}"


def render_mermaid(report: dict[str, Any]) -> str:
    lines = ["flowchart LR"]
    for decision in report["decisions"]:
        decision_id = _mermaid_id("d", decision["decision_id"])
        lines.append(
            f'  {decision_id}["{_mermaid_text(decision["title"])}\\n{decision["derived_status"]}"]'
        )
        for item in decision["triggered_rules"]:
            rule_id = _mermaid_id("r", item["rule_id"], item["event_id"])
            lines.append(f'  {rule_id}["{_mermaid_text(item["fact"])} = {_mermaid_text(str(item["observed"]))}"]')
            lines.append(f"  {rule_id} -->|{item['severity']}| {decision_id}")
        for alternative in decision["reopened_alternatives"]:
            alt_id = _mermaid_id("a", alternative["alternative_id"])
            lines.append(f'  {alt_id}["Alternative: {_mermaid_text(alternative["label"])}"]')
            lines.append(f"  {decision_id} -.->|reopens| {alt_id}")
    return "\n".join(lines) + "\n"
