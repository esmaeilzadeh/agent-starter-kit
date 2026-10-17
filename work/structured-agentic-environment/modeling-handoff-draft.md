# Draft handoff: define the Epic, stories, and specification links

Status: continuation draft, written 2026-10-14. This document records human feedback and proposed next steps; it does not approve amended intent, change the current specification, or certify implementation completion.

Continue work ID `structured-agentic-environment` on `agent/structured-agentic-environment` using the Ask kit. At drafting, HEAD was `24473ca42826ac397b9b1c60ec54dabbc8fa2599`; the latest UI/benchmark code change was `d21dfcc2cca1ebbacee5c7de4025b0d85e4e518a`. Recheck current state before continuing.

## Human feedback and current priority

The human inspected the running UI and could not relate to its Epic, “Make agent-assisted engineering work explicit and reviewable.” They asked:

- What is the definition of this Epic?
- Which readable specification text relates to it?
- Why are there no stories under it?
- Why are several scenarios shown without a recorded story?

Address the engineering definitions and their presentation first. Repeated latency benchmarks did not resolve these questions and frustrated the human.

## Confirmed findings

`engineering-model.json` contains one `intent` node, which the UI presents as an Epic. It has a title and lifecycle, but no description or specification reference. There are zero story nodes. Two feature nodes are recorded: `traceability-harness` and `model-validation`. Their two model scenarios are contained directly by those features.

The current schema permits feature → scenario containment. The navigator therefore displays “Scenarios without a recorded story.” The current specification explicitly permits this fallback and defines Epic as a presentation label for existing intent/feature records. The fallback exposes missing definitions honestly, but the pilot lacks the meaningful Epic → Story → Scenario breakdown the human expected.

The workstream specification exists at `specs/current/structured-agentic-environment.md`, with canonical criteria in the adjacent JSON. The displayed intent does not explicitly link to the readable specification or identify its own scope within it. The harness example references separate `harness-review` criterion/test records.

## Read before continuing

- Root `AGENTS.md` and `_ask/policies/`.
- `specs/current/structured-agentic-environment.md` and adjacent JSON.
- This work directory's `engineering-model.json`, `plan.md`, and `workbench-design.md`.
- `spec-change-workbench-redesign.md` and the current accepted contract records.
- `WB-009-handoff.md`, `workbench-validation.md`, and `inner-loop/evidence/session-evidence-correction.md`.

Older handoffs describe historical checkpoints. Verify their execution claims against current files and retained evidence.

## Resume through Ask

1. Run `./ask status`, `./ask check-clean`, and `./ask inner-loop status structured-agentic-environment`. Check for another writer. Continue this branch and workstream; do not start an overlapping branch.
2. At drafting the worktree was clean. Commit `24473ca` stopped tracking `work/structured-agentic-environment/traceability/executions.json`; the existing ignore rule covers it. Preserve local ledger entries and associated reports/logs. Their presence on another machine must be checked explicitly.
3. Assess whether the unresolved domain boundaries need Explore, announce the decision, and follow the repository's confirmation rules. Prepare and sync through `./ask prepare` and `./ask sync` as required. Never run the human-only `./ask setup` wizard.
4. Prepare a bounded scope amendment for this correction. Present the complete amended intent and assumptions and record the actual human response with `./ask confirm-intent`. This draft does not supply that confirmation.
5. Prepare the applicable Spec Change, independent review, test-plan and plan updates before implementation. Preserve canonical criterion identities and historical evidence; explicitly review and pin any required contract revision.

## Proposed correction to develop and confirm

Define an Epic with a concrete user, outcome, motivation, scope, and completion criteria. Connect it to readable specification text.

Record stories grounded in the specification, with meaningful behavior and acceptance criteria. Connect the pilot's scenarios to those stories while retaining their canonical criterion and test references. Explain how features relate to stories in this model.

Audit whether the historical harness example belongs within this Epic, needs separate context, or should remain a clearly labeled example. Preserve historical attribution; newly authored stories must not be represented as historical records.

Make the Epic and Story details expose their definitions and related specification text. The user should be able to follow purpose → promised behavior → scenario → delivery task → test → result.

Keep genuine missing-story cases visible. Decide explicitly whether story completeness applies to this curated pilot or becomes a broader validation rule. Do not assume a new Epic node type or mandatory-story schema change is necessary before reviewing the domain model.

## Existing execution state and evidence limits

WB-001–008 are recorded integrated; WB-009 remains `running`. That runtime status describes an assignment, not proof of a live worker. Earlier review/history claims were corrected in `session-evidence-correction.md`; integrated status does not remove those gaps.

The most recent WB-009 run on `d21dfcc` was interrupted during the synthetic 1,000-record structural workload, before browser measurements. It did not establish a passing latency result. Preserve existing failed and partial execution evidence.

Historical red-evidence gaps and the separately parked Verify candidate-source stability issue remain unresolved. Read the existing records and report those limits honestly.

## Run the UI and verify the correction

Use the repository launcher, `./ask ui`. A persistent local environment can be prepared with:

```sh
uv venv .venv
uv pip install --python .venv/bin/python -r _ask/ui/requirements.txt
source .venv/bin/activate
./ask ui
```

Inspect an existing environment before creating one. Browser verification additionally needs the pinned test requirements and an available browser. The previous session used a temporary environment under `/tmp`; its path is machine-local and may disappear. Check for an existing UI server before starting another. The session's UI address was `http://localhost:8501`.

Use focused checks for changed definitions, references, and navigation, then inspect the real pilot in the UI. Commit meaningful steps on the work branch. Repeat full benchmarks only when a specific change or unresolved measurement justifies them; preserve the accepted limits.

Before claiming completion, perform required independent review, `./ask verify`, and candidate-bound result recording. Report partial where evidence requirements remain unmet. Human Accept remains required. Merge and push require explicit direction.
