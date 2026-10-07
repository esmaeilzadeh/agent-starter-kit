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
