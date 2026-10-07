# Codex parity evidence

## Slice 1: generation

Command: `_ask/tests/test-codex-skill-parity.sh`.
RED before generator change: `AssertionError: Missing Codex skill: kit-00-explore`.
GREEN after generator change: `PASS: eleven Codex skills match Cursor stage bodies and overlays; sync is idempotent`.
The fixture asserts eleven canonical stage bodies, selected local overlay,
required Codex agent fields and byte-identical repeat skill generation.

Preparation: full network installation stalled; stopped. Pin-only
`SKIP_INSTALL=1 ./ask prepare` passed. Existing prepared skills available.
Official docs refresh: web connection failed; HTTPS connection refused.
Live Codex discovery/invocation has not been tested.

## Slice 2: ownership and preparation

Command: `_ask/tests/test-codex-skill-parity.sh`.
RED after adding manifest namespace test: exit 1 at `test ! -e install-called`;
preparation had invoked the installer before rejecting the reserved destination.
GREEN after full-manifest namespace preflight: all generation, cleanup,
collision/symlink and preparation checks pass. The fake installer is an
external boundary sentinel; no network dependency is required.

## Slice 3: install/upgrade and Git ownership

Command: `_ask/tests/test-codex-skill-parity.sh`.
RED before ignore migration: `FAIL: generated Codex skill remains ignored`.
GREEN after migration: install/upgrade migrate ignore rules, preserve consumer
skills/config/overlays and regenerate stages. Upgrade uses a local versioned
Git fixture, including a repeat upgrade to check ignore-file idempotence.
Generated projections are now committed alongside selective root ignore rules.

## Outer Verify fixture correction

First outer Verify at c9583d7 failed only the new parity test: inherited
`ASK_ROOT` redirected runtime-agent generation out of the temporary fixture,
so its Codex TOML was missing. The fixture now clears that inherited root.
Reproduction `ASK_ROOT="$PWD" _ask/tests/test-codex-skill-parity.sh` passes;
production behavior and acceptance criteria are unchanged.

## Slice 4: upgrading preparation code

Outer Verify at 13cd060 passed all 34 checks. Subsequent targeted inspection
found that upgrade's refresh list omitted `_ask/skills/`, so an older consumer
would retain its old preparation script. Added a fixture replacing that script
with an old implementation before upgrade.
RED: `FAIL: upgrade did not refresh preparation namespace guard`.
GREEN: parity test passes after refreshing `_ask/skills/` while restoring the
consumer-owned manifest. Independent audit's wording clarification applied to
the accepted spec's upgrade paragraph (Community Skill bodies exclude kit-*).

## Review R1: target-version migration entrypoint

RED: parity test invoking the target checkout's upgrader with `--target`
against a consumer containing the actual 260ad4b upgrader exited 2 (unsupported
argument). The consumer starts without generated kit skills and with legacy
preparation code and blanket ignore rules.
GREEN: parity suite passes with `upgrade-kit.sh --target <consumer>`;
`--skip-prepare` still migrates ignores, refreshes the namespace guard,
regenerates all eleven stage skills and preserves consumer state. The previous
upgrader is retained as an isolated regression fixture. Documentation directs
first migration through the target version's checkout, not the running old
consumer upgrader.

## Review R2: verify Git trackability

RED: ancestor-ignore fixture failed with `FAIL: install succeeded despite
ignored Codex skills`.
GREEN: parity suite now passes install and upgrade rejection checks. Both
flows call Git after generation; blocking rules are reported and retained.
Generation success is no longer treated as evidence that skills are trackable.

## Final evidence — 2026-10-08

Verified commit: `ab8268e57db6fbb99577a427d660f56240889bb2`.
`./ask sync` followed by `git diff --exit-code`: pass (no generated drift).
`./ask verify`: pass, all 34 mandatory checks. Exact CheckPlan results saved in
`verification-codex-parity.json`. GPT-6.1 Sol medium independent re-review:
APPROVED, R1/R2 resolved, boundary ok. Independent context recheck: all six
required IDs pass. Human Accept remains pending. Subsequent commits only
record this evidence and acceptance preparation.
