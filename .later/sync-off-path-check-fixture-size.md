# Keep the off-path test fixture small

- **Status:** resolved in v2.0.2
- **Found during:** client-workflow-hooks merged-main verification
- **Resolution:** source repair `5550dc86`; no new workstream is needed
- **Tags:** testing
- **Attribution:** verification failure at `c61ebc7b`; `_ask/tests/test-sync-off-path-command.sh`
- **Affected responsibilities:** static-check fixture setup and cleanup
- **Publication status:** released

## Reproduction and fix

The original fixture copied the complete `_ask` directory, including a 589 MB
ignored virtual environment. It exceeded a 45-second reproduction limit. The
unchanged test in a clean checkout passed in 5.21 seconds.

The fixture now uses `git archive HEAD _ask .agents/ask` to copy committed kit
files. Its projection assertions are unchanged. It passed in the original
checkout in 4.92 seconds with the virtual environment still present. The full
41-check release CheckPlan also passes at `99682327`.

See `work/client-hooks-release-repair/` for the retained reports and follow-up
checks. Raw runtime logs are not required to reproduce the verification.
