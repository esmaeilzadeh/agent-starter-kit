# Task 2 independent review

Reviewer: `/root/cont_review`, independent Codex Sol reviewer as assigned.
Runtime: Codex. Exact inherited model and parent model identifiers not supplied.
Base: `eb39360ebe9d6609991a11b92981c62df3f8d62e`.
Candidate: `cf27c0dde056028d17e9f1b9c1987e503c7a0247`.
Accepted contract/inventory base: `02ad31b6e5ef5130986a920f943788cbbe970631`.

## Scope and boundary

Reviewed complete identity/store/codec implementations, package exports, all three new test modules, accepted Task 2 plan and cases 2/1–2/9, relevant canonical SH criteria, TaskResult and immutable Red/Green reports/log digests. Task 2 is current writer. The seven changed paths are exactly the four declared workflow_refs modules and three declared test modules. All match owned_paths; boundary **ok**.

## Findings

### R1 — Existing-spec behavior defect: auxiliary fallback bypasses mandatory parent grammar

Location: `.agents/ask/workflow_refs/identity.py:121`–`123`. Task criteria SH-01/SH-02/SH-08; cases 2/1 and 2/6.

The generic two-segment auxiliary fallback accepts reserved hierarchical kinds. Direct probes returned valid references for `alpha/task/1@1`, `alpha/test/1@1`, `alpha/plan/1@1`, and `alpha/part/1@1`, all missing mandatory related parents. Such references also pass envelope full-reference validation and can be catalog-registered. This violates Task 2's exact grammar and SH-02/SH-08 sufficient-context refusal. Restrict auxiliary kinds to declared auxiliary identities and reject reserved hierarchy kinds outside their complete grammar. Add genuine failing regression assertions for every bypass family and envelope/catalog entry points as appropriate.

### R2 — Existing-spec behavior defect: text envelope decoder accepts invalid/nonfinite JSON

Location: `.agents/ask/workflow_refs/codec.py:75`–`89`. Task criterion SH-09; case 2/6.

String input uses Python's default json.loads, which accepts NaN and Infinity. A direct probe decoded a valid envelope wrapper with payload `{"value":NaN}` into a Python nan value. The equivalent dictionary/encoder input is rejected by allow_nan=False. Thus accepted text depends on ingress representation and can normalize to values that cannot be emitted as valid finite JSON, contrary to deterministic JSON normalization in SH-09. The decoder also accepts blank payload_schema while the encoder rejects it. Apply consistent JSON/value/schema validation to both ingress forms; add Red regressions for nonfinite values and blank payload schema.

### R3 — Existing-spec behavior defect: repeated snapshot identities are not shared

Location: `.agents/ask/workflow_refs/store.py:347`, entry construction in register_revision. Task criteria: SH-03; cases 2/4 and 2/8.

Each appended entry embeds the complete `snapshot: {commit, path}` again. The catalog has no shared snapshot table or reference. Publishing multiple items from the same source therefore repeats the full commit/path in every entry. The accepted plan's Integrity file decision explicitly requires full repeated snapshot identities to be shared once, implementing SH-03. The existing concurrent/recovery fixture already registers three logical items against one commit/path, which would repeat that identity three times. Deduplicate immutable snapshot identity in the separate catalog and resolve it without changing historical revision targets; test multiple entries sharing one snapshot and retained integrity verification. This is within Task 2 persistence scope, not a later optional savings cleanup.

### R4 — Local structural suggestion: several assertions do not exercise their accepted scenarios

Locations: `_ask/tests/test_workflow_refs_identity.py:42`; `_ask/tests/test_workflow_refs_store.py:30`, `:94`, `:154`; `_ask/tests/test_workflow_refs_codec.py:46`. Task criteria: SH-02 (2/2), SH-03/SH-05/SH-08 (2/4 and 2/8), SH-03/SH-08/SH-13 (2/7), SH-01/SH-02/SH-09 (2/9).

- Case 2/2 parses the exact same reference twice as old and moved. It never changes ancestor revision/source path or records an explicit historical move mapping. Identical parsing is tautological and cannot detect incorrect move handling. Exercise actual historical/new source or ownership contexts using explicit mappings; retain old targets and independent edges.
- Case 2/4 attempts an old-revision mutation with bytes that do not match its Git snapshot, so it fails the earlier source-integrity check even if published-revision protection is removed. Use valid pinned replacement bytes and assert old-revision reuse itself is rejected; also explicitly register independent run evidence and verify contract entries remain unchanged.
- Case 2/7 injects before/after authority interruption, then immediately retries a writer; it never invokes a reader in the interrupted states. Add reader observations at both cut points to establish complete old/new state, and verify old targets remain unchanged.
- Case 2/8 tampers only the working catalog, which is rejected by its trust-ref byte comparison. Add actual required pinned source/object unavailability and assert refusal without HEAD/latest fallback. This is distinct from a missing numeric revision.
- Case 2/9 is an in-memory dictionary encode/decode loop. It never persists or reloads bytes through a separate reader and omits spec parts and plan items required by its Given/Then. Persist compact envelopes to temporary storage, reload them independently, cover all six named families and assert complete normalized values. Compactness must be measured on an actual emitted representation, rather than comparing two caller-selected json.dumps whitespace settings.

Complete these task-local assertion corrections and obtain fresh review. Do not fabricate historical Red or claim unexercised scenarios from passing tests.

### R5 — Existing-spec behavior defect: snapshot IDs accept abbreviated SHA-256 commits

Location: `.agents/ask/workflow_refs/store.py:257`, _safe_snapshot regex `[0-9a-f]{40,64}`.

This accepts every length between 40 and 64, unlike identity.py's exact 40-or-64 object ID grammar. In a SHA-256 Git repository a 40-character prefix may resolve through git show and be persisted as if it were an immutable full commit identity. Validate the actual repository object format/full resolved commit identity; reject abbreviated IDs rather than storing a prefix. Add assertion coverage using a SHA-256 repository where supported, or explicit format validation with a precise supported-format outcome. Exact source identities are required by SH-01/SH-03.

## Integrity and structural assessment

Positive mechanics: persistent Git-common-directory lock serializes publication; generation check occurs inside it; CAS uses previous authority ref; pending journal and exact authority bytes drive recovery; local catalog self-assertion is refused; accepted-tests authority remains separate; source payload is matched to its declared Git blob; canonical JSON and exact bytes are distinct and full digests are verified. None of those mechanisms closes the findings above. Public APIs should not silently ignore payload/semantics arguments in resolve_version or arbitrary kwargs in register_revision; remove unsupported arguments or define/test their meaning as part of local interface cleanup.

## Red → Green → Refactor evidence

Red run `5910963e67fe4c44acbf679dfb382c72` binds source `3c7f9456565fcc180dad609c615fd13dc869f9df`. All nine mapped cases collected and failed as behavior_assertion; all three runner exits are 1. Final Green `b29f215cb2c742438757bc40319bada1` binds exactly to current candidate; all nine passed with successful collection and exit 0. All six recorded runner log digests match their bytes.

The only test-source change between Red and Green adds an exact-byte non-UTF-8 digest assertion; it does not weaken Red assertions. Existing Red is genuine, but cannot prove the unasserted scenarios in R4. The reported module separation/no-further-cleanup refactor result cannot clear required local fixes. No full test suite was rerun independently by reviewer; direct parser/decoder probes described above were executed without changing source.

## Classification and verdict

R1/R2/R3/R5: existing-spec behavior defects requiring regression Red → Green → Refactor.
R4 and unsupported-argument interface cleanup: task-local structural/test suggestions.
No broader horizontal refactor, required redesign, or withdrawn finding; no parked handoffs.

**REJECTED** for candidate `cf27c0dde056028d17e9f1b9c1987e503c7a0247`.
Boundary: **ok**. Structured review records rejection honestly; it must not be recorded as semantic approval.
