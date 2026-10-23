# Reviewer suggestion: verify delta-scoped Red after a contract change

Please double-check that the CR-3 contract and test plan distinguish a change
to an existing behavior from introducing an entirely new behavior.

Suppose behavior T1 was implemented and its required checks passed. The contract
is then revised to T1″. If T1″ changes an observable obligation, the new Red
should demonstrate the difference between the old and revised obligations. It
should target the changed or added assertion(s) that the current implementation
does not satisfy. It should not require the whole of T1″ to fail: unchanged
assertions may still pass because T1 already implemented them. Preserve T1's
original Red/Green history and assess its applicability to T1″ separately.

Please verify the rules cover these cases:

- **Changed behavior:** capture a test-only revision and a real failing run for
  the changed obligation against the pre-fix implementation before starting its
  Red → Green → Refactor loop. The Red is scoped to that behavioral delta; it
  does not replace or invalidate T1's historical evidence.
- **Unchanged behavior, changed test code:** assess behavioral continuity under
  TT-006. Do not demand a new Red solely because assertions were rewritten,
  strengthened as observers, or moved.
- **Revised contract already satisfied:** if the current implementation already
  meets the changed obligation, record that result; do not manufacture a Red
  or claim a code-fix TDD cycle was needed.
- **Historical applicability:** validate the original Red against its original
  contract, then separately decide which part of that evidence remains
  applicable to the revised contract. New obligations must not be presented as
  having historical Red evidence.

The reviewer should confirm whether the existing CR-05 and TT-006 language plus
the CR-3 recovery rules make this explicit. If not, recommend the smallest
clarification in the authoritative spec/test plan and identify its exact
location. This file is a review suggestion only; it does not amend or authorize
a change to the accepted contract.
