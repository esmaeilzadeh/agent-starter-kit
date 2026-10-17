# Handle disconnected red evidence during Git integration

- **Status:** parked (not live; no `agent/*`)
- **Found during:** `revising-workbench`
- **Start later:** new session, `./ask start-work <new-work-id>`
- **First stage:** 00 Explore if dest is foggy; else 01 Grill

## Why

During RWB-102 coordinator integration, the immutable-base CheckPlan passed its
36 shell/traceability checks but refused completion with:

```text
spec-to-test completion failed: {"errors": [""], "missing_evidence": [],
"report": "work/revising-workbench/traceability/completion.json"}
```

The failure came from a registered behavior-red run whose candidate commit was
not an ancestor of the final candidate. `traceability/service.py` gathers all
red runs for the accepted spec/plan, and `completion.py` checks each red source
with `git merge-base --is-ancestor`. Git returned exit status 1 without stderr;
the adapter converted that into an empty `Invalid`, leaving the opaque
`errors: [""]` report. The disconnected red run was
`c3092da97003426fb3e7d8abe822c222`, sourced from commit
`c140be47e5d1eb60d94b35fbc9395d59816ddf67`.

That commit was a detached duplicate of test-only commit `98b8910`: both had
tree `0c3e80ef77d94cdf8f5ca7d46c50800bccd62be2`, but only `98b8910` was on the
feature branch. The red report and source files were retained unchanged. To
meet the current ancestry gate, the exact `c140be4` commit was preserved as a
second parent in history-only merge `ec1c2d6`; the resulting tree remained
`6c3ffd57a77ab69f6cd4d392e2364151286d367d`, identical to the pre-merge feature
candidate. This made the red commit an ancestor without editing its report or
test bytes. CheckPlan has not yet been rerun against that resulting candidate.

The investigation should decide how Git/traceability integration ought to
handle disconnected red candidates. It should determine whether the evidence
ledger should reject such runs at registration, completion should classify and
retain them as rejected historical attempts, or identical source trees can
provide a safe lineage proof. Any solution must preserve failed reports and
avoid rewriting/deleting evidence merely to make completion pass. It should
also replace the empty diagnostic with a useful explanation and cover detached
worktree/red-run workflows.

## Proposed What (unapproved)

Investigate and specify reliable Git ancestry and source-identity rules for
traceability red evidence, including actionable diagnostics and tests for
detached candidate commits, duplicate trees, true non-ancestor source changes,
and retained rejected attempts. Implement only after the investigation settles
the evidence contract and ownership scope.

## Note

This card is separate from the active `revising-workbench` branch. The workstream
is currently at candidate `ec1c2d6`; the previous candidate `fcde3a4` failed
only the completion gate described above after the candidate-bound review was
recorded. No push, merge to a shared branch, or deployment occurred.
