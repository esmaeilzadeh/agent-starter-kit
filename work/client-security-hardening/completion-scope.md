# Authorized completion scope

## Human directions

The current request is: “continue untill implementation plan is ready then
stop to switch back to luna coordinator.” The human clarified that both
recovery and milestone evidence are needed for the current task, added
“also plan for laddered escalation too,” and required checking that the
changes preserve existing behavior and are fully verified at completion.

These directions supersede the earlier sequence that deferred milestone
evidence until after CSH-10 and the parked status of recovery tooling. All
three outcomes belong to this completion plan on
`agent/client-security-hardening`. Planning is authorized now; this turn ends
when the reviewed implementation plan is ready. Implementation waits for the
human's Luna coordinator handoff and continuation.

## Outcomes and route

1. **Recovery validator bug:** preserve valid model-state publications and
   completion projections while retaining immutable execution evidence.
   Reproduction is recorded in
   `inner-loop/evidence/recovery-reconciliation-proposal.md`: the frozen
   read-only reconcile rejects changed `model-state/current.json` and new
   projection files, although all 77 checkpoint ledger rows remain an exact
   prefix of the current 80-row ledger.
2. **Recovery transition feature:** provide an independently reviewed,
   stale-safe transition for CSH-10's pending state with no recorded attempt.
   Preserve earlier results, reviews, accepted pins, chronology, and failed
   runs; start a new attempt honestly rather than inventing a past attempt.
3. **Milestone evidence feature and clean-gate consistency:** commit compact
   meaningful progress and review history on the work branch, preserve source
   candidate identities, and backfill current evidence. Keep raw outputs in
   private recovery storage. The old archived draft is design input only.
4. **Laddered escalation completion:** assess existing commit `e8414c4`, close
   operational and verification gaps, and consult available native model rungs
   before interrupting the human for uncertainty within authorized scope.
   Preserve the strict above-90% threshold and human authority boundaries.
5. **Security closeout:** finish CSH-10 and final workstream regression checks,
   candidate review, result recording, and human acceptance. A plan-ready
   outcome is not product completion or a verification pass.

## Operating boundary

Under the highest-priority self-development rule in root `AGENTS.md`, conduct
this planning and the later kit maintenance with dogfooding disabled. Reuse
tests and independent review. The frozen runner at commit
`98f3c09d958a75c6e78181f196f313a99b4c0379`, location
`/tmp/askit-security-csh06.98f3c09.frozen`, stays unchanged as historical
verification evidence; it cannot govern installation of its own recovery fix.
Plan a supported maintenance transition rather than bypassing its refusal or
upgrading the frozen copy mid-task.

Sol-high drafts this plan. Luna remains the requested implementation
coordinator, and Sol-medium remains the requested independent reviewer.
Consultation does not switch the coordinator or approve product completion.

The original accepted security intent, specifications, test plan, TaskGraph,
and accepted-test pin remain unchanged during planning. Companion completion
artifacts specify the separately authorized kit maintenance and its regression
checks without rewriting historical contracts.

## Planning preimages

Starting HEAD: `72c7e4d`. State revision: 108. CSH-10: pending, attempt 0.
Checkpoint: `c8ebe82a55f40fca95036c0555e5280bbe605add`.
Accepted-test authority: `768d42f27894017c109213285aede23e89105e7c`.

| File | SHA-256 |
| --- | --- |
| `intent.md` | `38106bb1ca9437cc0da5044e0fb5f0c7a5bf4e2835d743f7873fa1b2c5147115` |
| `specs/current/client-security-hardening.md` | `f091c0bc398c77ae9e24d82223586011595396d93e077028d4d4a97dc79a60dc` |
| `specs/current/client-security-hardening.json` | `2bbcb3ccc08d5969020dba809b90eb9d22dbc1e5317a71933c672579bf79203f` |
| `test-plan.json` | `192d96e721b3001d72138ecfd699552b56103c7492174b0c780438151aa94a40` |
| `inner-loop/tasks.yaml` | `0477e6a223eb87ad2e4d345acf6ea9346f84d8cde8a5a20ce60939922e51fe39` |
| `traceability-accepted.json` | `26bfc14bad4cd40dc71afa5d2b2dbdb8efdcc84f43576434773131ad0fb71a52` |
| `inner-loop/state.json` | `c05a4f9478cf1888a2d721b8e84bb606c331537152dba736a865f1211cc57dc3` |

Relative file names in this table are inside `work/client-security-hardening/`
except the two explicit `specs/current/` paths. Restore private raw logs from
the archive documented in the reconciliation proposal when needed; their
digests belong in public progress records, their contents remain private.
