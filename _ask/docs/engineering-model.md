# Engineering Model pilot

The optional `work/<work-id>/engineering-model.json` sidecar organizes intent,
requirements, scenarios, decisions and work. Specifications/test plans remain
canonical for behavior/assertions; existing traceability remains authoritative
for execution and completion. A declared `done` task is not execution evidence.

## Document operations

Run `./ask model --help` and each subcommand's `--help` for arguments.

- `validate` captures the model and reference closure, checks all rules, then
  rechecks freshness. It writes no model or publication. `--full` currently
  performs the same full check; no incremental validation cache is implemented.
- `admit` validates working inputs before publishing an immutable generation.
  It can recover an interrupted managed edit. Read admission grants no workflow
  or acceptance authority.
- `show` reads admitted bytes. Invalid working definitions produce diagnostics
  and, when available, an explicitly last-validated noneditable generation.
- `edit` requires the complete displayed digest with `--expected` and a JSON
  batch. It stages, validates and publishes coordinated changes together.
- `watch` observes external saves with the optional native `watchfiles` backend.
  `--once` needs only the core dependencies. Full read/action-entry validation
  remains the fallback for missed events.

Batch shape:

```json
{
  "commands": [{
    "op": "resolve_decision",
    "id": "a-decision",
    "option_id": "an-option",
    "actor": "Developer",
    "rationale": "Reason for this choice"
  }],
  "files": {"specs/current/example.md": "# Coordinated specification\n"}
}
```

The selected workstream's spec JSON/Markdown and test plan may be staged in
`files`; Engineering Model mutations use semantic commands. Add nodes and their
required edges in one batch. IDs/types are immutable; retired definitions are
terminal. Decisions resolve/reopen/retire through attributable operations, with
prior choices/options retained in history. Other declared lifecycle transitions
may use the type's allowed states; dependency edits reopen affected resolved
decisions transitively. Only resolved decisions, confirmed assumptions and done
tasks satisfy their respective prerequisites.

## Cooperating workflow actions

`./ask model admit --work-id <id> --action <label> -- <program> <args...>`
checks documents before invoking the argv directly (no shell), checks afterward,
and returns a failure if the document state is invalid/stale. The label is
attribution, not permission. Existing worktree/coordinator/approval rules still
apply. Use guarded `edit` for canonical changes inside such an action; raw
definition writes cannot be made equivalent by a later read admission.

Verify, review/completion recording, acceptance checks and inner-loop entry
points use shared admission for adopted workstreams. Existing unadopted
workstreams keep their policy and acquire no validated-state label. Adoption
markers include the working model, tracked HEAD model and published pointer, so
deleting the working file does not bypass admission.

## Publication and failure boundaries

The publication unit is a complete captured generation selected by one atomic
pointer. Readers use its stored bytes, not partially materialized working files.
A durable journal recovers interrupted edits without replaying the semantic
action; conflicting external saves are refused and preserved.

This is a local cooperating POSIX pilot. File locks and hashed publication
history provide serialization and provenance, not authentication. Raw editors
do not honor those locks; their working files remain untrusted until validation.
Several filesystem replacements are not one distributed transaction. An
invalid external save requires explicit correction/import outside ordinary
blocked actions; the UI does not repair domain documents.

Core validation/editing uses Python standard-library JSON, hash indexes and
iterative graph traversal. Optional UI/watcher dependencies are separate. The
historical initial benchmark does not establish final full-guard performance.
