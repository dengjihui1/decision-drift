# Evaluation plan

## Goal

Test whether the protocol catches stale reasoning more reliably than static decision records while remaining explainable and temporally correct.

## Benchmark design

Create 30 synthetic but realistic timelines across software architecture, research design, and product operations. Each timeline contains:

- one decision record;
- two to four assumptions;
- zero to three incomplete or contradictory events;
- at least one rejected alternative;
- a fixed review date;
- an author-labelled ground truth for which premises require review.

Include adversarial cases: facts omitted from all events, wrong value types, evidence expiring exactly at a boundary, events before the decision, events after the review date, duplicate identifiers, and replaced decisions.

## Conditions

Compare three conditions using the same source material:

1. **Static record**: conventional decision text with rationale.
2. **Contract only**: structured assumptions and evidence, reviewed manually.
3. **Decision Drift**: full contract, deterministic rules, counterfactual reopening, and time-safe replay.

## Primary metrics

| Metric | Definition | Desired direction |
| --- | --- | --- |
| Premise-review recall | Ground-truth challenged premises surfaced / all challenged premises | Higher |
| False reassurance rate | Missing observations reported as safe / all missing observations | Lower |
| Future leakage rate | Post-review events that affect an as-of result / supplied future events | Zero |
| Alternative recovery | Eligible rejected alternatives resurfaced / all eligible alternatives | Higher |
| Traceability | Surfaced alerts linked to rule, event, date, source, and observed value | Higher |
| Review time | Median time to reach the ground-truth review set | Lower |

## Secondary metrics

- structural validation coverage;
- report agreement between two independent operators;
- time needed to author the initial contract;
- fraction of inferred assumptions accepted, edited, or rejected by the source owner;
- prediction completion rate at the due date.

## Acceptance thresholds for v0.2

- zero future leakage in the full adversarial suite;
- zero automatic triggers for absent facts;
- every trigger contains an event source and date;
- all replaced decisions remain replaced;
- at least 90% premise-review recall on the synthetic benchmark;
- median contract capture under ten minutes for a one-page decision note.

The final two thresholds require a future study and are not claimed by v0.1.

## Reproducibility

Publish generated benchmark inputs, expected machine-readable outputs, and the exact CLI version. Keep private project material out of the benchmark. Pin each release by Git commit and execute tests on Python 3.9, 3.11, and 3.13.

## Failure analysis

For every miss, classify the cause as capture omission, ambiguous premise, unsupported rule type, incomplete event, validation gap, temporal error, or incorrect ground truth. Change the protocol only when the failure generalizes beyond one wording example.
