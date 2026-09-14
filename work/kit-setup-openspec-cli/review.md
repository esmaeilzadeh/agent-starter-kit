# Review

## Model

gpt-5.6-sol-medium / cursor / parent_model grok-4.6

Cursor diverse default `kimi-k3` is not spawnable in this session. Review used
GPT-5.6 Sol (different family from Implement).

## Scope

Static review of `agent/kit-setup-openspec-cli` against
`specs/current/kit-setup-openspec-cli.md`. Helper, setup wiring, tests, Build
Spec §22.10, ADR-0018, README. Child was Ask-mode; tests were not run there.

## Findings

1. MEDIUM — Pin parse accepts non-scalar YAML (`[]`, `{}`, `null`, `|`) and can
   reach npm (helper exit 1) instead of exit 2.
2. LOW — `latest` and setup fallback warnings can omit package/revision when
   those scalars exist.
3. MEDIUM — Tests omit empty revision, conflicting symlink, and observable
   timeout child kill.
4. Positive — Stage order, `set +e`, non-TTY gate, fixed-path version, prefix
   isolation, overwrite, process-group timeout, help text.

## Suggested fixes

- Reject non-scalar pin values before npm.
- Name package and revision on exit 1/2 when those scalars exist.
- Add tests for empty revision, symlink conflict, and timeout reaping.
- Run `./ask verify --work-id kit-setup-openspec-cli`.

## Residual risks

No pseudo-TTY end-to-end of the wizard. Verification pending at review time.

## Review verdict

BLOCK
