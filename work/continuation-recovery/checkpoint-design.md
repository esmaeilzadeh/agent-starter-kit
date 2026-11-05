# Checkpoint retention and coordinator finalization

Normative design for CR-02–CR-05; resolves review R1 and R3.

## Reachability and publication

`_ask/scripts/inner_loop/checkpoint.py` writes a versioned manifest plus actual
required artifact blobs in a Git tree. The manifest identifies work, original
initialization anchor, attempt, contract/authority, generation, previous checkpoint,
source/runner/candidate commits and safe artifact paths/types/digests.

Each checkpoint commit parents the previous checkpoint and every required commit
not already reachable through it: original/base/Red/Green/candidate sources,
contract sources, historical authority commits and pinned runner sources. These
are real retention edges, never workflow integrations. Deduplicate parents;
never merge a checkpoint into the implementation branch or infer workflow status
from first-parent history. Artifact blobs in its tree are reachable as well.
Validate the entire required object closure before publishing the ref. Hashes
written only inside JSON never count as object retention.

The manifest separates historical authority from selected current accepted-tests
authority. Retention preserves historical provenance, not new-context acceptance.
Check object types, schemas, paths, digests and source semantics. Refuse missing
objects, traversal, escaping symlinks and unsupported records.

Under `state.lock`: validate expected generation/previous checkpoint and exact
contract/attempt; build immutable objects; verify closure; CAS-publish
`refs/ask/inner-loop/<work-id>`; atomically replace the state cache. The checkpoint
contains the post-transition state. Death before publication leaves the previous
checkpoint authoritative; death after publication replays the published state.
Unexplained newer/divergent cache requires reconciliation. Preserve the checkpoint
chain while its milestones need the retained evidence.

Public APIs acquire state lock once. Transaction-internal publishers receive the
existing context and never reacquire it. If reference publication is necessary,
acquire `state.lock` before Git-common `references.lock`; release references before
state; never call back into state while holding references alone. Execution-ledger
locks are released before checkpoint publication. Test contention/interruption.

## Transfer

Planned coordinator CLI: `inner-loop checkpoint-export <work> --out <file>` and
`checkpoint-import <work> <file>`. Export a self-contained Git bundle of the
checkpoint ref without excluded prerequisites. Parent edges cause source,
contract and authority commit closures to be transferred. Verify the manifest
and object closure; rely on neither reflogs, temporary branches, alternates nor
hard-linked clone objects.

Import into a quarantine namespace, validate the bundle/closure/schema/digests,
then CAS-publish the checkpoint ref only after reviewed owner registration.
Never automatically move accepted-tests authority, owner refs or source branches.
Current admission/contract eligibility is still required. Incomplete/source-only
transfer reports recovery/availability failure. Tests delete temporary fixture
refs, expire reflogs, prune and transfer into a separate object database before
revalidating original milestones.

## Run eligibility and interrupted finalization

Adapters and pinned verifier children produce run reports/logs and the existing
ledger only; they never acquire state lock or import checkpoint code. Preserve
the trusted snapshot boundary `.agents/ask/verification/`. CR-3 may make report
publication atomic through existing `write_json` and ledger insertion idempotent
by run ID; these adapter operations never call the coordinator.

New coordinator operation: `inner-loop checkpoint-run <work> <task> --run-id <id>`.
Validate report/log bytes, accepted contract, exact source/runner, selected
case/task/attempt and normal traceability eligibility. Red needs an actual
collected behavior-assertion failure without setup/import errors; Green needs
all mapped cases collected and passing. Phase labels or worker exit fields alone
cannot create a milestone. Keep incomplete/ineligible runs as explicit history.

If a complete validated report/log set exists but ledger insertion was interrupted,
the coordinator idempotently repairs its entry under the ledger lock, releases
that lock, then publishes the checkpoint. Conflicting entries or incomplete
reports remain diagnostic, not eligible evidence. Pending complete reports are
finalized before any new Red is scheduled. No execution is invented. Capture
the report, selected ledger entry and required output bytes in the checkpoint.

## Execution paths and lock ownership

| Path | Owner and handoff | Completion rule |
| --- | --- | --- |
| Standalone coordinator `traceability run --scope task` | Existing traceability CLI runs tests and leaves workflow admission, then invokes the coordinator finalizer with no state/ledger lock held. The coordinator module is loaded from the explicit coordinator root, never by the test adapter. | Report a recorded milestone only after validated finalization. A worker may produce run evidence but cannot publish coordinator state. Failure retains run artifacts for retry. |
| Nested `integrate_ready` verification | Parent holds state lock while its existing pinned child verifies. Child writes reports/ledger and exits. Parent consumes only run IDs referenced by that exact verification receipt, then uses its transaction-internal finalizer with the already-held lock. | No child waits for the parent lock; no candidate code is imported into the trusted verifier. Revalidate candidate/result/review before FF/integrated checkpoint. |
| Pre-hook pinned verifier | Same data-only handoff; parent consumes supported existing run/receipt schemas without requiring hooks in the child. | Missing/unsupported output is incomplete or migration_required, not success. Test the first hook-adding candidate against its old base. |

Parent records verification-complete evidence before FF, then exact resulting
HEAD/tree plus integrated checkpoint after FF. Recovery revalidates and finishes
only the missing step, never rewinds verified code or integrates an unrelated
descendant. Record Refactor and exact-candidate independent review separately.
Retain current TaskResult and traceability gates. Real nested-verifier tests use
bounded timeouts and include interruption between report, ledger and checkpoint.
