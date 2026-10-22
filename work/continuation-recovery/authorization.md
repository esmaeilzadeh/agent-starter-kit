# Planning authority and endpoint

On 2026-10-22 the user directed “apply all review changes and seal the plan and stop”.
The subsequent user direction requires urgent interrupt work to ask for its base
(current branch, develop or main), then use a separate branch and fresh context.
The user selected the recommended current branch with “rec”.

The selected base is agent/shorter-hashes at d04b3a4e515105df8cdf703f2fa0a28895f1524d.
This fresh context owns agent/continuation-recovery. This supersedes the old
same-branch/combined-contract design. The scope remains R1–R4 planning corrections,
independent exact-artifact review and formal registration of continuation-recovery
only. The original product intent, state, authority and branch ref are preserved.

STOP after sealing. No implementation, runtime bootstrap, behavior tests or
product scheduling is authorized. A generic continuation preserves this endpoint.

## Later direction

After the seal, the user explicitly directed “continue” and clarified that this
direction was given after the model changed. This supersedes the stop-after-seal
endpoint for the continuation-recovery workstream. The approved What, Why and
assumptions are unchanged; the existing `intent.md` remains byte-identical.
Continue through the recorded implementation plan under its normal admission,
TDD, review and verification gates. This does not authorize product adoption,
integration or scheduling beyond the plan's explicit handoff.

After CR-1 integration exposed failures in the required existing reliability
suite, the user selected “expand”. This authorizes the scoped CR-1 ownership and
test-source binding amendment recorded in `cr1-integration-scope-change.md`;
CR-01–CR-08, product adoption and scheduling remain unchanged.

During CR-2, the user explicitly selected “Amend CR-T38 for checkpoint replay”.
This authorizes moving CR-T38 from CR-1 to CR-2, changing its classification to
`changed`, binding it to CR-03 and CR-07, and amending its assertion to require
replay of the published post-fast-forward checkpoint after interruption before
runtime cache replacement. No other criterion or product intent changes.

The subsequent explicit “continue” authorized resolving the active-task plan
amendment gate within existing CR-07: record the active attempt and its exact
traceability runs, permit the reviewed plan revision between attempts, then
start a new attempt with a distinct ID and accepted-plan ref. CR-T55 maps this
behavior to CR-07; it does not change What, Why, or CR-01–CR-08.

After accepting Revision 7 exposed that completed-task evidence is tied to the
previous whole-plan digest, the user directed “continue” after the recommended
resolution was presented. This authorizes a scope-aware carry-forward rule:
preserve CR-1’s original result under its original contract only when the
current CR-1 obligations are unchanged members of its previously accepted
scope; CR-T38 remains a fresh CR-2 obligation. Recovery must also attribute
committed source changes to a recorded interrupted attempt before checking
overlapping dependent-task paths. No requirement, intent, or product-adoption
scope changes.
