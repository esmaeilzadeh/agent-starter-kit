# CR-2 attempt history scope amendment

The active CR-2 record was marked `running` when the user approved moving
CR-T38 to CR-2. The traceability ledger already contained two CR-2 Red runs
under the old plan digest, including one valid behavior Red. `accept-plan`
correctly refuses to change accepted obligations while any task is running.

CR-07 already requires preserving prior attempts and starting an explicitly
identified attempt after a deliberate reopen. CR-T55 adds an exact integration
case for the coordinator transition needed here: interrupt an active attempt,
retain its ID/base/accepted-plan ref and exact execution ledger entries, allow
the task queue to remain quiescent while the amendment is accepted, then start
a distinct attempt only after the accepted-plan ref changes. CR-2 owns the
attempt/state/driver/CLI implementation and the recovery test. No criterion or
product intent changes.

Interrupted attempts that already have a TaskResult file are refused for
explicit reconciliation; the transition does not discard candidate results.
