# Specification: promote kit contracts into the Build Spec

## Status

CURRENT

## Goal

The Build Spec under `_ask/spec/` describes the shipped kit contracts that today live only in `specs/current/` (later-inbox, status / session-only off-path, real skip of 00, `./ask record-run`).

## Non-goals

New `_ask/spec/` modules. Changing scripts, agents, templates, or policies. Moving the moons trainer / Streamlit viewer. Fixing the earlier artifact-schema drift.

## Behavior

Insert (do not copy files) into existing modules:

| Product spec | Build Spec home |
| --- | --- |
| `skip-explore` | `01-layout-and-concepts.md` §5.1 (fog test + routing) |
| `later-inbox` | `01` §3 layout; `04-scripts-and-git.md` §30 workstream convention |
| `ask-status` | `04` §23.4 (already has status; add any missing session-off-path / skip-approvals that is not already there); `05` §34a if `/off-path` source path is incomplete |
| `demo-nn-train` (`record-run` only) | `04` §22.9 dispatcher + §25 sibling for experiment runs |

After insert, those product specs become pointers to the Build Spec (except `demo-nn-train`, which keeps trainer/viewer/demo and points `record-run` at §25).

Update §3 layout and §38 mapping so the baseline tree and Guide map include `workflow.md`, `status.sh`, `record-run.sh`, `cursor-commands/`, `later-work.md`, and `.later/`.

## Interfaces

- `_ask/spec/01-layout-and-concepts.md`
- `_ask/spec/04-scripts-and-git.md`
- `_ask/spec/05-examples-and-binding.md`
- `_ask/spec/06-phases-and-acceptance.md`
- `specs/current/{later-inbox,ask-status,skip-explore,demo-nn-train}.md`

## Constraints

No new file under `_ask/spec/`. Do not rewrite accepted What/Why of the promoted workstreams — only relocate the kit contract.

## Invariants

An agent reading only `_ask/spec/` can find later-inbox, real skip of 00, session-only `/off-path`, `./ask status`, and `./ask record-run`.

## Failure cases

- New spec module created
- Product demo (trainer/viewer) copied into the Build Spec
- Product specs left as a second full SoT

## Acceptance criteria

- The four kit contracts appear in the existing modules listed above.
- No new file under `_ask/spec/`.
- Product specs point at the Build Spec; `demo-nn-train` still owns the demo vehicle.
- `./ask verify` passes.

## Open questions

None.

## Source intent

`work/promote-kit-specs/intent.md`
