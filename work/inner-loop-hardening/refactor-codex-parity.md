# Codex parity refactor

## Findings and resolutions

- Context-audit wording: FIX. Spec clarifies that preserved Community Skill
  bodies exclude reserved kit-* projections; independently rechecked.
- R1: FIX in 49227d1. Added target-version upgrade `--target` entrypoint,
  first-migration docs and actual previous-upgrader fixture. RED/GREEN evidence
  in `codex-parity-evidence.md`.
- R2: FIX in ab8268e. Added Git trackability validation to install/upgrade;
  consumer blocking rules are retained and reported. RED/GREEN evidence in
  `codex-parity-evidence.md`.

## Completion

Independent reviewer approved both fixes at ab8268e; targeted parity suite
passes. Outer `./ask verify` passes all 34 mandatory checks at the same SHA.
No unresolved review findings or spec changes required.
