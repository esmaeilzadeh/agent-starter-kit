# CMP-04: operational confidence consultation

The existing model-decisions CLI now deterministically returns continue,
consult with verified native model/effort, or ask-human. It binds reuse to the
material decision, evidence SHA256 and current session; rejects malformed
confidence and unverified assessments; visits permitted available rungs once;
and preserves human authority and explicit model restrictions. The consult
operation uses the existing runtime adapter, checks returned identity and
records unavailable responses before advancing. Native agent tools can execute
the same exact request and resubmit their assessment. No new resolver or model
configuration was introduced.

Sol/high's 97% scoped recommendation resolves the authority conflict by placing
the ladder in existing workflow.md and restoring delegation.md exactly to the
accepted contract bytes (SHA256 ee0c1a79fe2e2b1cd7db1897f49a90c2e8af50830646e68514eadcd43ce27e46).
Accepted pins remain unchanged. Every canonical stage/task-loop references that
central policy; sync regenerated the tracked stage skills/commands. Existing
runtime bindings remain candidates until current-session native capability proof.

Checks: 20 model/runtime/orchestrator tests passed, including six focused ladder
cases; stage wiring, runtime-agent sync and canonical-stage sync passed. The CLI
entry and additional final checks remain part of closeout. CMP-03's independent
correction review approved a403701; all 30 integration reliability and ten
milestone tests passed after correction.

Native consultation limitation: the live Sol/high policy-placement consultation
and Sol/medium component reviews were dispatched through native agent tools.
The returned agents explicitly reported that actual model/effort identity is not
exposed to them. Requested settings are routing evidence, not a claimed runtime
attestation. Such unverifiable identities are unavailable for confidence-rung
reuse; the dispatcher tests cover advancing/exhausting them. No simulated
assessment is represented as a live verified consultation.

Next: exact independent CMP-04 review, then one final live recovery proposal.
