# CSH-08 review round 1

Candidate: 269672c0768a2b5f71de5f8a2bf13cadf731a344
Reviewer: gpt-6.1-sol (medium)
Verdict: REJECTED
Boundary: ok

1. Valid model strings 1e3 and 0xabc are saved unquoted and reloaded as nonstrings. Preserve string identity through save/show/resolve.
2. The submitted risk must be applied to the work overlay before resolving the table; an old HIGH value otherwise overrides a newly submitted LOW.
3. A Codex confirmation must not mark Cursor's different model table confirmed; bind consent to its saved runtime.

Exact override precedence, legacy handling and prompt projections otherwise present. Immutable journey assertions unchanged. Reviewer ran no tests.
