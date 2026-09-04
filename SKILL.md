---
name: decision-drift
description: Turn important project, research, or product decisions into living contracts and detect when their assumptions, evidence, or rejected alternatives should be revisited. Use when a user wants to preserve why a decision was made, audit stale decisions after new events, resurface counterfactual options, or calibrate predictions against outcomes; do not use as a generic task manager or claim that a flagged decision is objectively wrong.
---

# Decision Drift

Decision Drift maintains memory that can become invalid. It records not only what was chosen, but the assumptions, evidence, rejected alternatives, predictions, and observable conditions that should trigger reconsideration.

## Operating boundaries

- Treat a decision contract as a review aid, not proof that a decision is correct or incorrect.
- Preserve the user's wording for facts and choices. Label inferred assumptions and ask for review before treating them as commitments.
- Never invent evidence, outcomes, dates, thresholds, owners, or rejected alternatives. Use `UNKNOWN` when a field cannot be established.
- Missing event data does not mean an assumption still holds. Report it as `UNOBSERVED`.
- Do not change code, reverse a decision, contact anyone, or trigger an external action unless the user separately authorizes that action.
- Keep private project material local by default. The deterministic engine requires no account, network access, or API key.

## Modes

### Capture

Extract a meaningful decision from project notes, commits, experiment logs, requirements, or user explanation. Record the choice, rationale, alternatives, assumptions, evidence, predictions, invalidation rules, reversibility, and review date. Separate explicit content from agent inference.

### Check

Represent a new observation as an event, run it against the ledger, and explain each rule evaluation. A triggered warning can move a contract to `AT_RISK`; a triggered invalidation rule can move it to `STALE`. Never trigger a rule when its fact is absent.

### Review

Produce a prioritized drift report showing changed premises, expired evidence, reopened alternatives, unresolved observations, and the smallest next action that could discriminate between options. Preserve `REPLACED` decisions as history.

### Calibrate

Compare recorded numerical predictions with actual outcomes when units and metrics match. Report error and direction without turning a small sample into a claim about the user's general judgment ability.

## Workflow

1. Identify consequential decisions rather than logging every action.
2. Create or update a ledger conforming to [references/protocol.md](references/protocol.md).
3. Encode only observable invalidation conditions using [references/rule-language.md](references/rule-language.md).
4. Validate the ledger before checking events.
5. Run `decision-drift check` or `scripts/decision_drift.py check` for deterministic evaluation.
6. Review triggered rules, reopened alternatives, expired evidence, and unknown facts.
7. Write the final Markdown/JSON report and keep the original ledger unchanged unless the user requests an update.

## Deliverables

- `decision-ledger.json` — living decision contracts.
- `events.json` — dated observations with source references.
- `DRIFT_REPORT.md` — prioritized, explainable review.
- `drift-report.json` — machine-readable evaluations.
- `decision-graph.mmd` — optional Mermaid dependency graph.
- `CALIBRATION_REPORT.md` — prediction-versus-outcome audit when applicable.

Use [references/protocol.md](references/protocol.md) when capturing contracts and [references/rule-language.md](references/rule-language.md) when defining or auditing triggers.
