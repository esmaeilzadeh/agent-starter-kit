# RWB-104 independent review

- Verdict: REJECTED
- Boundary: PASS (`ok`)
- Candidate: `325e20e9fa6eaf744b864035b3bc605260f64f1a`
- Base: `3ab55340bb5cc594281b211d3664065e84f50bec`
- Reviewer: independent review agent, `gpt-6.1-sol` high

## Findings

1. **P1 — Qualified aliases produce duplicate Tasks.**
   `_ask/scripts/engineering_model/workbench.py` suppresses model rows by
   comparing product node IDs with execution TaskGraph IDs. The accepted fixture
   therefore projects `(product, task)` twice: `WB-003` and `task`, both with
   execution `(product, WB-003)`. Their statuses/context differ, corrupting
   counts and routes. Deduplicate by qualified execution alias/product identity,
   while preserving distinct unrelated identities. The test only asserts
   uniqueness for `standalone`, missing its own duplicated bound Task.

2. **P1 — Scenario presentation substitutes criterion prose for the selected
   concrete flow.** `_ask/scripts/engineering_model/projection.py` copies
   Given/When/Then from the broader criterion. In the admitted fixture,
   `scenario-stale` selects canonical `WB-stale`, whose flow is
   `Same obligation / Stale route / Refuse`; JSON and Markdown instead display
   `A valid model / Admitted / Only captured sources are used`. Preserve v1
   behavior, but resolve v2 Scenario presentation from its qualified canonical
   case, including unavailable/draft limitations.

3. **P1 — Task-to-Scenario support edges disappear from contextual routes.**
   `workbench.py` projects only Story support. `related_scenarios` remains derived
   from implementation/test mappings. Adding a legal, admitted
   `standalone contributes_to scenario-stale` edge yields an empty
   `standalone.related_scenarios`. Project explicit Scenario support with its
   provenance, without implying executable test ownership.

4. **P2 — JSON/Markdown readiness parity is incomplete.** `projection.py`
   switches every nonempty workbench to a rendering that omits readiness,
   definition lifecycle and blocker detail. The fixture's JSON identifies
   `WB-003` readiness as `blocked`; its Markdown Task entry says only `planned`.
   Model-only Tasks additionally omit `readiness_status` despite declaring
   `readiness_source="engineering-model"`. Render separate named status
   authorities and blockers consistently, including model-only Tasks and
   preserved v1 behavior.

## Evidence assessment

The reported red and final-green runs exist, bind to the stated candidates, and
all execution-log digests match. Final green contains five passing assigned
cases. These passes are authentic, but their assertions miss the counterexamples
above. The reviewer reproduced findings 1–4 using temporary admitted fixtures;
original repository files were untouched.
