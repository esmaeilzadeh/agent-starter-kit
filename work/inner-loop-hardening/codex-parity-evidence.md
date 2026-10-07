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
