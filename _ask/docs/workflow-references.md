# Workflow references

The reference interface resolves one exact immutable item revision at a time.
It never falls back to the current branch, latest revision, or a shortened Git
prefix. Numeric identities include their owner and parent context; malformed,
missing, ambiguous, unsupported, and incomplete requests return a scoped JSON
diagnostic.

```sh
./ask refs show shorter-hashes/spec/1/plan/1/task/8/test/1@1
./ask refs show shorter-hashes/spec/1/plan/1/task/8/test/1@1 --integrity
./ask refs status
./ask status --references
```

Ordinary `show` output includes the selected payload, numeric revision, owner,
type, profile, and named numeric parents. `--integrity` adds the verified
digests and shared snapshot identifier. Status reports a coherent project
inventory generation; an unsupported external ref change or missing owner
authority yields `incomplete` instead of a partial success.

Impact compares two saved complete capture objects. The candidate must still
match the live cooperating-repository inventory when assessed. Refresh its
capture after publishing decisions: decision-only metadata preserves the
approved semantic generation, while the exact ref/movement snapshot changes.
The existing decisions still apply; a fresh capture requires no new approval.

```sh
./ask refs impact --source /tmp/source-capture.json --candidate /tmp/current-capture.json
```

Decision evidence must name exact old/new revisions, context generation,
reviewer, coordinator, every examined input path, and the declared required
paths. The command checks the context and attribution and leaves unresolved
decisions at `reassess`; it never rewrites consumer pins.

## Explicit legacy migration

Migration reads `work/<owner>/references/migration.json`, whose schema is
`ask-reference-migration/v1`. Each entry must explicitly name the old reference,
new logical ID, immutable full Git commit and repository-relative source path,
stable item ID, and comparison profile. `source_sha256` may pin the source
bytes as an additional check. The original record is left untouched. Mappings
are retained inside the trusted owner catalog with source provenance. No
historical revisions, reviews, or executions are inferred.

```json
{
  "schema": "ask-reference-migration/v1",
  "owner": "demo",
  "mappings": [{
    "legacy_reference": "plan-legacy-id",
    "logical_id": "demo/spec/1/plan/1/item/2",
    "snapshot": {"commit": "<full-commit-id>", "path": "work/demo/plan.json"},
    "item_id": "plan-item-2",
    "profile": "structured-item/1"
  }]
}
```

Exports contain the trusted catalog bytes, a Git bundle for its authority ref
and immutable object closure, and checksummed metadata. Import verifies the
bundle and every catalog entry against an already registered local authority
ref. A copied bundle or manifest cannot establish or replace that authority;
source-only transfers require the coordinator's reviewed registration process.
Identical imports are no-ops. Conflicting, incomplete, or unavailable history
is refused.

## Experiment runs

`./ask record-run` retains its dirty-tree, exact-HEAD, and config checks. New
run manifests and summaries use `eval-run-meta/v2` and carry a numeric
`repository-runs/run/<n>@1` reference. Full source commit and digest bindings
live once in `results/references/integrity.json`, anchored by
`refs/ask/references/repository-runs`. Existing `eval-run-meta/v1` records and
registry rows remain readable without rewriting.

`start-work` publishes `agent/<work-id>` refs while holding the persistent
Git-common-directory `ask-locks/references.lock`, the same lock used by project
capture and catalog publication. It still branches from `develop` and refuses
dirty trees before creating a ref.
