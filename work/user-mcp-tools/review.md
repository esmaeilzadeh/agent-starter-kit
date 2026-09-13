# Review

## Scope

`specs/current/user-mcp-tools.md` vs `./ask setup`, `.ask.env.example`, gitignore, tests.

## Findings

None blocking. Non-TTY refuse, help, gitignore, and install tests are green. Interactive wizard was not run (human-only by contract).

## Suggested fixes

None.

## Residual risks

Merging `~/.cursor/mcp.json` on a live machine is untested end-to-end. Stubs use `${env:...}` only.

## Review verdict

PASS
