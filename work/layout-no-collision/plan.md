# Plan

## Specification

ADR-0011 + Build Spec layout tree.

## Approach

1. Record ADR and spec/owned-path contract
2. `git mv` scripts → `part-engineering/scripts/`; fix ROOT + callers
3. `git mv` tests → `part-engineering/tests/`; verify discovers them
4. `git mv` docs → `part-engineering/docs/`; fix links
5. install-kit copies only `part-engineering/` + adapter; never root `scripts/` or `docs/`
6. Run kit verify

## Verification approach

`part-engineering/scripts/verify.sh` (after move) — all kit tests pass; install-kit apply does not create target `scripts/` and leaves consumer `docs/` intact.
