# Plan

## Specification

ADR-0011 + Build Spec layout tree.

## Approach

1. Record ADR and spec/owned-path contract
2. `git mv` scripts → `_ask/scripts/`; fix ROOT + callers
3. `git mv` tests → `_ask/tests/`; verify discovers them
4. `git mv` docs → `_ask/docs/`; fix links
5. install-kit copies only `_ask/` + adapter; never root `scripts/` or `docs/`
6. Run kit verify

## Verification approach

`_ask/scripts/verify.sh` (after move) — all kit tests pass; install-kit apply does not create target `scripts/` and leaves consumer `docs/` intact.
