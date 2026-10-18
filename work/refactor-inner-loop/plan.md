# Plan: Put TDD Refactor and code review inside the task loop

## Specification

specs/current/refactor-inner-loop.md and its canonical criterion metadata
specs/current/refactor-inner-loop.json, revision 1. Risk: MEDIUM because agent
workflow changes apply across runtimes. User authorized planning only; stop
before Implement. Independent review and contract pinning are recorded separately.

## Approach

1. Establish .agents/ask/task-loop.md as the canonical lifecycle contract.
   For every behavior slice: Red -> Green -> Refactor. Then independent task
   Review; fix all valid local findings and repeat review on the changed SHA.
   Retain required candidate Verify -> Integrate and outer Verify -> Accept.
2. Classify local refactors, broader horizontal refactors, existing-contract
   corrections, and necessary redesign. Local structural changes preserve
   behavior/contracts. Behavior corrections use TDD; necessary redesign requires
   Spec Change. All valid local refactor findings must be fixed, not waived.
3. Park broader candidates as attributed later-card drafts tagged refactoring.
   Coordinator, not task writer, materializes cards only after all task candidates
   integrate and no writer/resumable candidate remains, then publishes through
   normal develop integration. Retain complete drafts and publication status in
   persisted runtime review evidence during task execution and interruptions; dedupe
   against existing cards. Do not expand the task or add a card-creation CLI.
4. Have 06 Implement, 07 Review, and 08 Refactor reference the canonical contract.
   The outer workflow contains task execution, not separate unconditional task
   Review/Refactor phases. Retain cross-task assessment and final Verify/Accept.
5. Preserve current retry CLI return values and bounded attempts. Existing
   implement/debug dispatch returns into the documented correction/TDD cycle.
   Existing candidate-bound review and checks remain the integration gate; no
   automatic semantic code-quality judge or new persistent sub-state is added.
6. Add a repository-owned TDD preparation override referencing the canonical
   contract. Explicitly supersede upstream exclusion of refactoring in both
   installed .agents and Cursor views. Make repeated preparation idempotent;
   preserve pins, unrelated skill content, and SKIP_INSTALL validation semantics.
   Do not commit generated upstream skill trees or change their upstream pins.
7. Update guide/spec/demo/root references; regenerate all runtime bundles using
   ./ask sync. Verify install/upgrade ship the canonical contract and preserve
   consumer overlays. Fixtures must exclude local virtualenvs from Git snapshots.

## Work breakdown

All tasks execute serially on agent/refactor-inner-loop. Separate tasks have
reviewable outcomes and non-overlapping owned paths; graph dependencies also
serialize the canonical source, preparation behavior, and generated projections.
The exact owned-path globs are in inner-loop/tasks.yaml.

| Task ID | Outcome / deliverable | Depends on | Owned paths | Test IDs | Completion evidence |
| --- | --- | --- | --- | --- | --- |
| RF-01 | Canonical nested TDD/review loop, finding classification, coordinator parking, stage/template references | none | .agents/ask/task-loop.md; .agents/ask/stages/**; workflow policy; inner-loop evidence doc; review/later templates | none, reviewed criteria RF-001..004 | Independent scenario walkthrough with criterion-by-criterion decisions; no implementation or state transitions claimed by text checks |
| RF-02 | Pinned TDD preparation override applied to installed views, safely and idempotently | RF-01 | _ask/skills/**; test_tdd_preparation_overlay.py | PREP-01..06 | Behavior assertion Red/Green for PREP-01/02/04; current execution for PREP-03/05/06 unchanged regressions |
| RF-03 | Consistent guides/bundles/consumer installs plus preserved integration gates | RF-01, RF-02 | root guidance; _ask/guide/**; _ask/spec/**; demo docs; generated Agent/Cursor/Claude/Codex/OpenCode paths; two new integration test modules | LOOP-01..05, BUNDLE-01..02 | Install/upgrade behavior Red/Green where changed; current integration regression execution; generated parity checks |

RF-01 deliberately has no executable test: its claims are semantic agent
instructions, not a new runner API. An independent reviewer must walk the
scenarios below. Literal string assertions would not establish those claims.
RF-02/03 use public CLI seams and temporary consumers; no tests are written or
executed in this planning stage. PREP-01/02 add overrides; PREP-04 fixes stale-file
masking of nonzero installer failure and therefore requires behavior Red/Green.
PREP-03/05/06 preserve existing dry-run/optional/missing-primary semantics and
are baseline regressions, as are LOOP tests. They require current execution, not
a manufactured Red or proof of newly changed behavior.

## Review scenarios

- Green code with duplicated local logic is refactored before task review while
  preserving behavior; an empty cleanup pass does not invent edits.
- Review requests a local structural fix: fix, recheck, and re-review; a rationale
  alone cannot waive a valid suggestion.
- Review suggests a cross-module redesign with unchanged behavior: propose a
  tagged later card; preserve a durable coordinator handoff without task-writer
  branch switches or out-of-scope changes. Do not perform the broad refactor.
- A required shared contract must change: stop for Spec Change, never label it
  optional refactoring or silently park it to claim task success.
- A behavior bug within the accepted spec gets a failing regression and another
  Red -> Green -> Refactor cycle before fresh review.
- Review changes its mistaken assessment with evidence: record withdrawal; do
  not confuse that with accepting unfinished local cleanup.
- A changed candidate attempts stale approval reuse, a candidate check fails,
  or retry limits are exhausted: existing gates refuse integration.
- Interruption before later-card publication retains its draft and publication
  status; resumption publishes once through normal integration.

## Verification approach

Before implementation: validate graph and canonical spec/test mapping; obtain
independent review for exact specification/graph/test-plan digests; pin with
./ask traceability accept-plan. Review-only criteria need attributable independent
APPROVED decisions; tests cannot be relabeled to manufacture semantic authority.

During implementation: use reviewed test IDs and task scopes. Write one behavior
test at a time, observe a behavior assertion Red, implement Green, then Refactor.
Record immutable red and final candidate execution through traceability. For
unchanged regression scenarios execute current cases and explain classification
in independent candidate review. Do not substitute planned output for evidence.

After implementation: run declared unittest integrations, existing inner-loop and
bundle parity suites, ./ask sync, and ./ask verify on committed candidate source.
Record actual result and SHA; required gate failures remain failures. Do not
repeat the prior mistake of treating a static develop verification pass as a
workstream completion pin. Semantic review and executed tests are separate.

## Risks

- Upstream TDD text conflicts with this workflow: use an explicitly authoritative
  managed override; verify both prepared views and repeat preparation.
- Owned paths are broader than task responsibility: classification is semantic,
  not a glob/file-count test. Escalate ambiguity instead of expanding scope.
- Advisory local suggestions are waived: require completion or evidence-backed
  reviewer withdrawal; existing bounded retries stop non-converging work.
- Later cards violate clean-tree/single-writer rules: the coordinator parks them
  only at the final no-writer/no-resumable-candidate workstream boundary and
  publishes through develop. Runtime drafts do not advance coordinator source HEAD
  during an interrupted or blocked task.
- Updated generated files mask stale canonical rules: inspect canonical stages,
  preparation views, install/upgrade outputs, and every runtime pointer chain.

## Escalation and Spec Change triggers

Escalate a necessary contract/behavior/meaning change, unsafe local refactoring,
ambiguous scope classification, or retry exhaustion. Return to Spec Change for
required redesign; amend and independently repin Plan if task/test scope changes.
Do not alter retry bounds, add new CLI states, or weaken evidence without a
separate explicit decision.

## Out of scope for this plan

Implementation during this session; merging/pushing this work; broader horizontal
refactor execution; changing product behavior; renumbering stages; replacing the
scheduler or evidence system; a new inbox/tracker feature.

## E2E

not_applicable to an application journey. Public prepare/install/sync/upgrade and
inner-loop integration tests use disposable local consumers and controlled
installer stubs, with no external services or production data. Independent
scenario review verifies agent semantics that execution tests cannot establish.

## Stop boundary

Stop when Spec, independent Challenge, task graph, test mapping, and Plan are
committed and validated. Do not initialize task runtime state, spawn a task writer,
write behavior tests, modify implementation/protocol production sources, or run
any implementation stage. Implementation intent confirmation remains a future
entry gate if not already valid; no approval response may be fabricated.
