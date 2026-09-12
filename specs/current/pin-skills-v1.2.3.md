# Specification: pin Community Skills to v1.2.3

## Status

CURRENT

## Goal

`./ask prepare` installs Explore-bound Community Skills from `mattpocock/skills#v1.2.3`.

## Non-goals

Other skill sources. `revision: latest`. skip-explore gate.

## Behavior

Manifest pins:

| skill | required |
| --- | --- |
| wayfinder | yes |
| research | no |
| prototype | no |
| grilling | yes |

All `revision: "v1.2.3"`. Lock file updated by prepare. Spec schema example uses a `--skill` name that exists at the pin.

## Acceptance criteria

- Manifest and lock say `v1.2.3` for those four skills.
- `./ask prepare` exits 0 and prints ok for each.
- `SKIP_INSTALL=1 ./ask prepare` still refuses `latest`.
- `./ask verify` passes.

## Source intent

`work/pin-skills-v1.2.3/intent.md`
