# Task 6 binding decision

On 2026-10-29 the user delegated implementor decisions to the coordinator:

> decides on what implementor agent needs if you can more than 90 confident else escalate

This supersedes the pending human-choice stop in `handoff.md` for the proposed
Task 6 source-binding amendment. The coordinator approves that amendment with
confidence above 90%: `checkpoint.py` and `recovery.py` read and validate persisted
state, and `attempts.py` controls task-attempt identity. Omitting those consumers
would permit changes to the tested behavior outside its recorded source identity.

Add `_ask/scripts/inner_loop/checkpoint.py` and `recovery.py` to cases `6/1` and
`6/2`, and `attempts.py` to `6/1` only. The specification, scenarios, assertions,
criteria, classifications, runners, task order, owned paths, and approved intent
are unchanged. Preserve the v1 state projection consumed by later-task readers.

Independent exact-revision review and renewed accepted-plan registration remain
required before implementation. Decisions with confidence at or below 90%,
changed What/Why or acceptance criteria, and material unresolved contradictions
must be escalated. This delegation does not supply final acceptance evidence.
