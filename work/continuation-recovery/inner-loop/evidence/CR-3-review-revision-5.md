# CR-3 revision 5 review

Verdict: **REQUEST CHANGES**. Date: 2026-10-23.
Review target: `cf2f851` plus assertion-fingerprint clarification `7a3025b`.
Reviewer: `/root`. Independent read-only assessment from `/root/policy_review`
confirmed the authority ancestry finding before that agent became unavailable;
the primary reviewer completed the source/assertion review.
This is proposal review, not human scope approval or authority to reopen.

Revision 5 addresses both revision 4 findings in design: historical admission
now reaches coordinator finalization, and the inventory includes original
T10/T19 evidence alongside eligible P0 evidence. The shared validation path,
unchanged run summaries, explicit case scope and end-to-end fixture are
appropriate. Two newly explicit validation requirements would still reject
the evidence the proposal intends to carry.

## Standards / authority finding

**P1 — accepted-authority commits do not form the required ancestry chain.**
The proposal requires the original accepted-authority commit to be an ancestor
of the P1 accepted-authority commit. Current acceptance creates each authority
commit with only its contract commit as parent
(`.agents/ask/verification/traceability/evidence.py:65`). The previous authority
is used for ref compare-and-swap, not as a parent.

Observed identities:

- Original authority `14d8bbe20c5f3d24082c13ef98a29e80ac019b92` has parent
  `588c6cd9f3585eeb77d8a745abfc8d1a96b73cb6`.
- Current authority `4ad1d2de2591a672aab211df1ce019d97cb13fad` has parent
  `681d2bfebc9e07a5901c6cd0b17bf01230e3c9af`.
- The original authority is an ancestor of neither current HEAD nor current
  accepted authority. Normal proposed P0/P1 acceptance does not establish
  authority-to-authority ancestry either.

**Required amendment:** remove that unsupported authority ancestry predicate.
Validate the exact original authority object, its accepted document/review and
contract binding, the original candidate's recorded acceptance document, and
explicit current P1 authorization for that historical evidence. Keep actual
contract-to-candidate and candidate-to-task-lineage ancestry checks. Preserve
historical objects through the existing retention mechanism. Test valid
historical authority that is not a Git ancestor of the current authority,
as well as substituted/invalid authority rejection. No history rewrite or
new authority-commit merge is needed for this correction.

## Spec / assertion-continuity finding

**P1 — the proposed T10 row fails the new identical-fingerprint requirement.**
The retained log for `b50dd24e0ef04a2aacff4c4a26db4dd5` identifies T10's
failure at `_ask/tests/inner_loop_recovery.py:246` in candidate `3196a59`:

```python
self.assertTrue(
    callable(getattr(evidence, "checkpoint_run", None)),
    "coordinator must checkpoint validated standalone run milestones",
)
```

Using revision 5's exact `ast.dump` algorithm, the call fingerprint is
`56312dd9c3f4d575dba35a8d802ad76baf97266f85bf2f1ed570def0054f6398`.
There are zero identical assertion-call nodes in the current test source at
`7a3025b`. The current mapped method tests process exits and publication
boundaries. The historical report therefore cannot satisfy the proposed
identical-statement rule against that source. Later assertions in the old
method were not reached after the failing callable check; they cannot be
substituted as that run's failed statement.

**Required amendment:** compute the actual per-case fingerprints and match
results before presenting the continuity inventory as viable. For T10,
explicitly resolve the changed assertion: either establish a supported,
independently reviewed continuity mapping with precisely defined semantics,
or disclose and authorize the remaining evidence limitation. Do not describe
this removed assertion as unchanged, backdate current publication assertions,
or manufacture a product failure. A changed continuity rule must be explicit
in the proposal and mapped tests; semantic review cannot silently bypass the
proposal's identical-fingerprint requirement. The corrected observer's Green
and sensitivity evidence remain appropriate but do not resolve this separate
historical-statement mismatch.

## Handoff and validation

Retain the revision 5 architecture and correct these two evidence predicates.
Include a concrete match inventory for T10/T19/T20 rather than deferring every
fingerprint calculation to implementation. Keep original reports, receipts,
phases and summaries intact. The next review should assess those exact
corrections before the human scoped-amendment decision.

Read-only verification inspected acceptance commit parents and ancestry,
original failure logs, and immutable/current assertion ASTs. No behavioral
suite, coordinator transition, acceptance operation or aggregate verification
was run. State remains revision 27 with CR-3 interrupted. Authority refs,
contracts, state, ledger, original reports and receipts were hash-checked for
preservation before this documentation-only commit; staged whitespace check
passed. This review does not claim workstream completion.

Findings: Standards — one blocking authority ancestry assumption.
Spec — one blocking T10 assertion-continuity mismatch.
