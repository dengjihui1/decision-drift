# Release checklist

## Product

- [x] Scope is a decision-drift detector, not a task manager or autonomous decision-maker.
- [x] Public demo uses fictional data only.
- [x] README shows a reproducible end-to-end run.
- [x] Research claims are framed as hypotheses.

## Protocol

- [x] Missing facts remain `UNOBSERVED`.
- [x] Status transitions are monotonic.
- [x] `REPLACED` decisions do not reactivate.
- [x] Future events are excluded from as-of replay.
- [x] Trigger output retains source provenance.

## Engineering

- [x] Python 3.9+ and standard library only.
- [x] Unit and end-to-end CLI tests pass.
- [x] JSON inputs receive structural and referential validation.
- [x] Demo outputs are regenerated from committed inputs.
- [x] GitHub Actions tests supported Python versions.

## Distribution

- [ ] Skill structure passes `quick_validate.py`.
- [ ] Release ZIP contains no `.git`, cache, bytecode, or nested ZIP.
- [ ] Tests pass after extracting the ZIP to a clean directory.
- [ ] Exactly one final ZIP remains in the project folder.
- [ ] Repository and portfolio index are pushed.
