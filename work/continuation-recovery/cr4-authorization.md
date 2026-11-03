# CR-4 scoped execution direction

The human explicitly authorized completing CR-3 and CR-4, then reconciling the
system state, with a one-time exception to kit rules for those two tasks:

> you can ignore the rules of the kit, do your job and after that reconsolidate the state (the state of the system eventualy should be correct

> it is one time exception only for cr3 and cr4

The latest direction is:

> continue and finish your jub then standby

This supersedes the earlier CR-3-only endpoint and the subsequent pause. Finish
CR-4's existing bug-fix scope: legacy audit/proposal support, meaningful passing
tests, independent review, verification, and reconciliation of the repair queue.
The separately approved testing direction allows tests that already pass; do
not manufacture historical Red evidence. Preserve original reports and missing
legacy milestones honestly. Record any mechanical gate disagreement explicitly;
do not change global kit rules or claim that an unpassed gate passed.

The independent review in inner-loop/evidence/review-CR-4-874f091.md approved
the exact proposal payload b643b7c4530deb2621262e1e2bf1e0b0e2dc846288b05ea70a318a38889d7535.
The coordinator records that decision in adoption/proposal.json. Later source
review findings do not change that payload; current implementation approval is
recorded separately against the final source candidate.

Product adoption, product scheduling, and integration into agent/shorter-hashes
remain outside CR-4. The approved intent and accepted behavior are unchanged.
