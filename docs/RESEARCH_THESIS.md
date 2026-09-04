# Research thesis

## Problem

Project memory usually preserves conclusions after the conditions that justified them have changed. Architecture decision records, lab notebooks, and meeting notes answer “what did we decide?” and sometimes “why?”, but they do not encode when that reasoning should stop being trusted.

Retrieval alone does not solve this. Finding an old rationale can make it easier to repeat, even when its evidence has expired or a rejected alternative has become viable.

## Hypothesis

A decision record becomes more useful when it is treated as a falsifiable contract rather than permanent prose. The contract should bind six elements:

1. the choice and rationale;
2. explicit and inferred assumptions;
3. dated supporting evidence with freshness limits;
4. rejected alternatives and their rejection conditions;
5. observable invalidation rules;
6. numerical predictions that can later be checked.

The project hypothesis is that this structure reduces three specific failure modes compared with static records:

- **false reassurance**: missing facts are mistaken for confirmation;
- **counterfactual amnesia**: rejected options stay forgotten after their rejection reason disappears;
- **hindsight leakage**: later events are used when reconstructing an earlier decision state.

These are hypotheses to test, not established product claims.

## Technical contribution

Decision Drift combines four mechanisms in one inspectable protocol:

- deterministic premise invalidation over supplied event facts;
- evidence expiry independent of contradictory events;
- rule-linked reopening of alternatives;
- as-of replay bounded by decision and review dates.

Prediction calibration is deliberately local. The engine reports range position and error for recorded predictions but does not infer a stable personal bias or global decision score.

## Why a protocol and a Skill

The Skill handles ambiguous source material: extracting a choice, separating stated facts from inferred premises, and proposing observable conditions for user review. The runtime handles what should not depend on prose generation: validation, date boundaries, rule execution, status monotonicity, and report rendering.

This split makes the system portable across coding agents while keeping its core claims reproducible without a model or API.

## Research questions

- Does a decision contract improve detection of invalid premises over a conventional ADR?
- Does explicit `UNOBSERVED` handling reduce false reassurance when event records are incomplete?
- Do rule-linked alternatives increase recovery of previously rejected options after context changes?
- Can independent reviewers reproduce an as-of status from the same ledger and event set?
- What capture burden is acceptable before users stop maintaining the ledger?

## Non-claims

Decision Drift does not establish causal improvement in project outcomes, diagnose cognitive bias, rank people by judgment quality, or choose a replacement action. A rule can only show that a user-recorded review condition matched supplied evidence.
