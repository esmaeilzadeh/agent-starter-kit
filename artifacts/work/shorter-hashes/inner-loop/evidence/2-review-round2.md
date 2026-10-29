# Task 2 independent review — round 2

Reviewer: `/root/cont_review`, independent Codex Sol reviewer as assigned.
Runtime: Codex. Exact inherited model and parent model identifiers not supplied.
Base: `eb39360ebe9d6609991a11b92981c62df3f8d62e`.
Candidate: `f1857159a3b3d479a9c03ab3ae7c09ab1e5ab7c3`.
Accepted inventory base: `02ad31b6e5ef5130986a920f943788cbbe970631`.

## Scope and boundary

Fresh review inspected the complete implementations and tests, prior rejection list, accepted Task 2 scope and cases 2/1–2/9, current TaskResult and immutable Red/Green evidence. The seven base-to-candidate changed paths are four workflow_refs package modules and the three declared test modules. All match owned_paths; boundary **ok**. Task 2 remains current writer.

## Prior corrections confirmed

- R1 resolved: only declared auxiliary kinds use the generic path, preventing reserved hierarchical parent bypass. New malformed-reference assertions exercise the failure.
- R3 resolved: immutable snapshot commit/path identities now live once in a shared catalog table; entries use snapshot_id. Tests append run evidence sharing a snapshot and preserve old contract entries and accepted-tests authority.
- R4 resolved to the task's current interface scope: explicit move mapping now returns old/new qualified targets while retaining dependencies; published-revision overwrite assertions use valid pinned bytes; interrupted-state readers observe refusal before advancement and full recovery afterward; actual unreachable source object removal is exercised without checkout fallback; persisted byte roundtrips cover spec/part, plan/item, task and test. Byte savings compares typed and full references with the same compact serialization.
- R5 resolved: full commit identity is checked against actual repository object format and exact commit resolution. Git authority initialization uses the correct zero-ID width. A real SHA-256 fixture rejects a 40-character prefix, with targeted behavior Red and exact-candidate Green.
- Unsupported API arguments removed: register_revision no longer swallows arbitrary kwargs; resolve_version no longer accepts ignored payload/semantics parameters.

## Remaining R2 — existing-spec behavior defect: finite-number validation still differs by ingress

Location: `.agents/ask/workflow_refs/codec.py:79`, text decode branch; task criterion SH-09, case 2/6.

Rejecting NaN/Infinity tokens via parse_constant fixes the prior literal-token bypass but not floating-point exponent overflow. Direct independent probe: a valid wrapper with payload `{"value":1e999}` is accepted by decode_envelope and produces Python `inf` (math.isfinite returns False). Equivalent dictionary/encoder input with inf is rejected by allow_nan=False. Normalization can therefore still return a nonfinite payload that cannot be persisted under the writer's supported finite-JSON contract.

Required fix: enforce finite parsed float values, either through a finite-checking parse_float hook or a complete post-parse JSON-value validation shared by both ingress forms. Add a genuine behavior-assertion regression for positive and negative exponent overflow, retain NaN/Infinity and blank-schema refusals, and run fresh exact-candidate Green and independent review. This remains the same R2 ingress-consistency defect, not a new scope or design change.

## Assertion inventory and TDD

Initial nine-case assertion Red remains retained. Broad correction Red run `508b5e1013ac4a30aa9b43105981ed94`, source `01eaba25c768de392749860935cbedf528e398c3`, records genuine behavior failures for 2/1, 2/2, 2/4 and 2/6. Targeted SHA-256 Red `a4974e5a0ba84812b8f945f0b40d8fd5`, source `d2c4d26e06b179a975b824338b4078f69b2c6ce5`, records 2/4 behavior_assertion failure while other cases pass. Final Green `d818facb6c394363b7128a3e9cb06783` binds exactly to f185715 and all nine mapped cases pass. All runners collect successfully and all inspected runner log digests match bytes. No test-source assertions were weakened from targeted Red to current Green.

The extra unmapped test_snapshot_identity_requires_full_object_id duplicates the malformed-length checks now contained in mapped 2/4. It is explained as redundant direct-suite coverage in structured inventory exclusions; it supplies no separate accepted obligation or independent TDD claim.

No full test suite was independently rerun by reviewer; the overflow decoder probe was executed directly without source mutation. Passing mapped tests does not resolve the missing overflow regression.

## Other classifications and verdict

No further local suggestion, broader refactor, required redesign or withdrawn finding. No parked handoffs. Original rejection files remain intact.

**REJECTED** for `f1857159a3b3d479a9c03ab3ae7c09ab1e5ab7c3`.
Boundary: **ok**. Only blocking finding: **R2 finite-number ingress overflow**.
