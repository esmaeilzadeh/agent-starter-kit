# Reviewed v1-to-v2 migration proposal

Status: reviewed migration proposal; the historical source model remains v1 and
was not rewritten. Browsing, validating, or opening this workbench does not apply
the proposal. Applying any migration requires `./ask model migrate` with the
current snapshot digest, proposed v2 document, and this review's exact bindings.

## Bound source and proposed target

The proposal uses the retained `structured-agentic-environment` v1 model only to
exercise the migration review contract. The target is a deep copy with schema
`ask-engineering-model/v2` and revision advanced by one. It preserves each node,
edge, ID, reference, lifecycle, title, description, and evidence attribution.
It is a review fixture; it does not migrate the historical workstream or grant
its approval, completion, red/green results, or evidence to `revising-workbench`.

```json
{
  "schema": "ask-engineering-migration-review/v1",
  "decision": "APPROVED",
  "reviewer": "Codex implementation review",
  "rationale": "The schema/revision-only proposal preserves all historical node fields, IDs, references, and edges; the source remains unchanged.",
  "source_digest": "7a6f3b223df36df5202e5890d870f7db23cc5a552bce7564b383d277b619a341",
  "target_digest": "74cf6e0bb282aaedf191bd969d86e7778a2c75213ca852a6eda4bf2b3e971bfc",
  "diff_digest": "9fa1e5f96eaa32b5cd8918c576ea272c56580929a4437c7fdbd9bfb5c3e813a7"
}
```

The digests use canonical UTF-8 JSON with sorted keys and compact separators.
`preservation_diff` reports no added or removed IDs, changed records, changed
references, or changed edges. A migration with a missing review, stale digest,
removed identity, changed historical field, or changed reference is refused.

## Guard and authority boundaries

The public migration entry admits the current model first, checks the explicit
review, validates any selected Task context against the exact proposed target,
stages the model through the shared action journal, validates the complete
result, and publishes through the existing generation pointer. A refused
proposal leaves the old document and publication intact. Historical v1
validators and evidence remain available after adoption; migration is not
retroactive and does not transfer accepted contracts or completion state.

The `revising-workbench` pilot has its own v2 model, promoted specification,
TaskGraph, test plan, and accepted contract. It selects the historical WB-003
spec and plan passages and inspects the retained result through existing source,
execution, and coordinator review records. The historical result remains
historical; its test pass is not workstream completion. Human comprehension is
separately recorded with a candidate-bound ten-answer record and is never
synthesized by this validator.
