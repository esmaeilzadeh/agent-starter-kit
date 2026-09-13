# Plan

## Specification

`specs/current/promote-kit-specs.md`

## Approach

Edit the four existing Build Spec modules in place. Then replace the promoted product specs with pointers.

## Work breakdown

1. §3 layout + §5.1 fog/routing in `01-layout-and-concepts.md`
2. Dispatcher, record-run, later-inbox, off-path remainder in `04-scripts-and-git.md`
3. AGENTS / Cursor Binding leftovers in `05-examples-and-binding.md`
4. Mapping rows in `06-phases-and-acceptance.md` and `_ask/MAPPING.md`
5. Point `specs/current/{later-inbox,ask-status,skip-explore,demo-nn-train}.md` at the Build Spec

## Risks

Duplicating text that is already in §23.4 / §34a. Mitigate by inserting only what is missing.

## Verification approach

`./ask verify`. Grep `_ask/spec/` for later-inbox, record-run, fog test, off-path source.

## Out of scope for this plan

Scripts, agents, templates, policies. Artifact-schema reconciliation.
