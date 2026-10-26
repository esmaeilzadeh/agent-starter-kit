# Current shorter-hashes history reconciliation

This report is bound to `current-audit.json` and `current-proposal.json`.
It preserves the accepted product contract and task history; it does not
rewrite `state.json`, claim missing milestones, or schedule a task.

## Product and authority preimages

- Product commit: `60d314d60dccfeb1ab335c49596be97738ec15af`.
- Runtime state: revision 11, SHA-256
  `b5fad609842013a1ca11017ec60e4ae45c042f92828cbf040c795129525b17e6`.
- Live accepted-tests ref: `refs/ask/accepted-tests/shorter-hashes` at
  `4e78fedb58dd3a69ef50a5d96fc8c1d4c46d5c28`; it matches the tracked pin.
- The current accepted contract includes the independently reviewed and
  registered Task 2 regression classification. The user separately directed
  that no failing Red be manufactured for those nine regression cases.

## Task evidence

| Task | Recorded state | Reconciliation |
| --- | --- | --- |
| 1 | `integrated` | Red and Green are available only from checkout artifacts; Refactor is missing, review is unverified, and no integration receipt exists. The integrated label is unsupported by current evidence. |
| 2 | `blocked` | Historical baseline and final-Green rows exist in the checkout ledger, but no task result, Refactor, candidate review, or integration receipt is bound in current product state. Treat the nine cases as regressions; the user waived failing Red only. |
| 3–5 | `pending` | The current 17-row checkout ledger does not expose complete task evidence. The prior CR-4 audit referenced a different checkout ledger digest, so those rows remain historical observations until their exact artifacts are revalidated against the current contract and candidate. |
| 6–10 | `pending` | No task completion evidence is adopted. |

The current scheduler preflight returns `recovery_required` for Tasks 1, 5, 6,
and 8. It identifies post-coordinator changes to task-owned source for Tasks
5, 6, and 8, plus Task 1's result bound to an older accepted contract. The
exact output is `current-scheduler-check.json`.

## Reconciliation outcome

Keep the original state and every prior attempt unchanged. Do not mark Task 1
integrated from its status label, do not mark Task 2 integrated from passing
regressions, and do not schedule Tasks 3–10 while the coordinator reports
`recovery_required`. The current adoption proposal remains non-mutating and
requires independent review; it does not authorize product-state adoption.

The next safe step is to review this exact report and proposal, then resolve
each missing milestone from attributable source/run/review/integration records
or leave it explicitly incomplete. A task may advance only after its ordinary
accepted evidence and coordinator checks pass.
