# Focus indicator review: `e7d7c19f`

- Candidate: `e7d7c19f9e34b93dc68e377f54dc1d4e4c21ba16`
- Base: `d25ce752`
- Route: reproduced bug-fix follow-up under frozen kit `0e303265ceae1fbcdc9b2261bd922b003ab68924`
- Requested/resolved reviewer model: `gpt-6-luna`
- Self-reported backend identity: unavailable
- Runtime: Codex
- Parent model: GPT-6
- Verdict: **APPROVED**

## Findings

No findings.

## Review basis

The prior hard-coded black outline could not contrast with a dark primary control. `currentColor` makes the 3 px inner outline track that control’s foreground color, which is the appropriate ring color for its adjacent fill. The teal shadow has a 7 px spread; with a 2 px outline offset and 3 px outline width, its outer 2 px extends beyond the outline, leaving a distinct band visible against the surrounding surface. Against the light app surface used by the browser flow, `#005e60` has ample contrast; the test now evaluates this outer band against the outside surface separately from the inner outline against the control fill.

The browser helper still requires a visible focus indicator and at least 3:1 contrast. It selects the computed outline for the control fill and the first nontransparent computed shadow for the outside surface. The CSS values and helper change align with the regression described in the captured d25 reproduction: the previous black ring measured 1.168:1 against the dark fill. The revised rule does not hard-code one outline color across controls, and the outer shadow remains the same teal across the tested controls.

I inspected the exact three-file delta and `git diff --check`; both were clean. I did not run browser tests or broad suites. The coordinator reported the focused browser suite and CheckPlan were starting at review time, while the older full suite remained isolated on d25. This review does not claim those checks passed. Dark-theme surfaces were not part of the supplied failing case; the fixed teal outer ring would need a different color or theme-aware rule if the app later supports a dark surrounding surface where teal falls below 3:1.
