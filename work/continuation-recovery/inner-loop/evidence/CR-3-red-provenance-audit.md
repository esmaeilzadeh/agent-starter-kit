# CR-3 Red provenance audit

Date: 2026-10-23. Scope: CR-T10, CR-T11, CR-T12, CR-T13, and CR-T21.
This audit follows the request-changes review at
`CR-3-result-review-08339eb.md`. It does not change the accepted plan,
reclassify runs, or authorize integration.

## Common task lineage

Both interrupted CR-3 attempts record task base
`2c508ff4248f16a3e3121d33a0fae7297c9b378e`. Attempt 1 used accepted plan
digest `2ddca16503e68dc640b51b9a4d5ddb8dab79e75b16fd1eec04bc9de012958aa0`;
attempt 2 used `a8c13188a26489e67173333ca4f69ac572f00836a3f32e77929ee82a1ff99025`.
The latter narrowly changes CR-T11 and CR-T14 from `new` to `regression`; its
review expressly leaves CR-T12, CR-T13, and CR-T21 unchanged. Their mapped
assertion source is `_ask/tests/inner_loop_recovery.py`; task attempt history
and the append-only execution ledger are retained in `state.json` and
`traceability/executions.json`.

## Per-case ledger

| Case | Original task/slice base and assertion lineage | Registered runs and outcomes | Contract applicability and continuity | Classification |
| --- | --- | --- | --- | --- |
| CR-T10 | Base `2c508ff`. The mapped assertion's retained Red is candidate `3196a591e2ee0c75ee0bda1539a9319555273662`; the final process-exit assertions were extended later at `08339eb`. | `b50dd24e0ef04a2aacff4c4a26db4dd5`, phase `red`, outcome `failed`, failure kind `behavior_assertion`, plan `2ddca165…`. Exact-candidate Green `8683de0e005d45dbac9207a8ab034aae` passed under the same plan. Latest exact-candidate Green `861e66d1fbce42859354f5b7a5b80317` passed at `08339eb`, plan `a8c13188…`. | CR-T10 mapping and assertions are unchanged by the T11/T14 plan amendment. The retained Red proves the earlier run-finalization assertion. The later ledger-publication crash assertion was added after that Red, so byte-identical assertion continuity is not claimed for that addition. | Valid retained Red for the original assertion; new R3 assertion still needs execution in a reopened attempt. |
| CR-T11 | Base `2c508ff`. The final mapped wrapper was reviewed against the task-base helper; plan-review evidence records that the wrapper’s assertion passes at base. Current accepted plan classifies only this wrapper as `regression`. | `b50dd24e0ef04a2aacff4c4a26db4dd5`, `dab908b39596441086d57106b8c816ec`, `6b6471cfb6704129afaa5bb587f71f0d`, and `861e66d1fbce42859354f5b7a5b80317` all report `passed`; no recognized behavior Red is registered. | The approved amendment `plan-review-cr3-baseline-regressions.json` binds digest `a8c13188…`, changes only CR-T11 and CR-T14 classifications, and explicitly does not reclassify T12/T13/T21. Prior review says the baseline probe was diagnostic overlay evidence, not a registered run. | Applicable as the specifically reviewed regression case; do not claim a registered Red. |
| CR-T12 | Base `2c508ff`; the mapped crash-after-verification/FF assertion was added by the test-only commit `3196a59`. The production tree under `_ask/scripts/inner_loop` is unchanged from the task base to that candidate. | `6a96d09a0d4c4394951b47fa33a14dd7`, phase `final_green`, outcome `failed`, failure kind `behavior_assertion`, plan `2ddca165…`; it cannot count as Red. `517f864631a845e082f9a73fa888ef30` is phase `red` but all eight cases passed. The valid Red-phase runs `b50dd24e…` and `dab908b3…` also report T12 passed. Later final Green `861e66d1…` passed under plan `a8c13188…`. | The actual initial Red-phase execution at test-only candidate `3196a59` shows this mapped assertion passed with task-base production. The later failed `final_green` is preserved as a failure in its original phase. | Evidence supports a narrow `regression` classification for T12; no run is relabeled Red. |
| CR-T13 | Base `2c508ff`; mapped generic-CAS and explicit-attempt assertions are in the task test source. The behavior is associated with `attempts.py`, which CR-2 owns and CR-3 currently does not. | Retained Red-phase runs `b50dd24e…`, `517f8646…`, and `dab908b3…` all report T13 passed. Later final Green `861e66d1…` also passed. No registered T13 behavior assertion failure is present. | Current CR-T13 remains `new`. Existing runs establish Green only; they do not select a historical Red baseline. Its source ownership mismatch is separately addressed by the exact proposal in `CR-3-plan-amendment-proposal.md`. | Missing valid Red; do not infer one from passing tests or source presence. |
| CR-T21 | Base `2c508ff`; mapped old-runner handoff assertions were added by test-only commit `ae31e20`. Relevant production changes to `cli.py`, `__main__.py`, `driver.py`, and `evidence.py` occur between the task base and that assertion source. | `517f864631a845e082f9a73fa888ef30` was registered as `red`, candidate `01abc53755a86405ee814684f7b31f80440a4000`, but exited successfully and all eight cases passed. Other retained Red runs `b50dd24e…` and `dab908b3…` also report T21 passed. Latest final Green `861e66d1…` passed under plan `a8c13188…`. | The implementation lineage is new to this task, but the assertion was added after those production changes. The earlier diagnostic overlay is not an immutable registered execution. No recognized Red exists. | Missing valid Red; preserve the all-pass Red-phase record without treating it as a Red. |

## Finding

The current evidence supports retained Red for T10's earlier assertion and
the reviewed regression classification for T11. T12's mapped assertion
already passed against unchanged task-base production in its first registered
Red-phase run, so a narrow regression classification is supported; its later
failed `final_green` run remains unchanged. T13's existing assertions also
passed at the initial test-only candidate, but the newly requested repeat
interrupt/reopen behavior is not in those assertions and still requires a
fresh valid Red. T21's implementation changes landed before its assertions;
therefore neither a regression classification nor a valid Red is supported.
Current Green cannot resolve T21's evidence gap. No failures were
manufactured, and no report phase was changed.

## R3 correction prepared

In `_ask/tests/inner_loop_recovery.py`, the T10 test now reloads
`executions.json` immediately after the child exits at
`after_report_publication`, before asserting that the child run ID is absent.
This makes the assertion inspect the post-crash ledger state. The amended
assertion has not yet been run under an active reopened attempt.
