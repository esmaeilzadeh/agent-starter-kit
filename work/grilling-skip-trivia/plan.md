# Plan

## Specification

`specs/current/grilling-skip-trivia.md`

## Approach

Amend kit contracts and ADR. Do not edit the pinned Community grilling SKILL.md.

## Work breakdown

1. Intent/spec/challenge (this)
2. `01-grill.md`, `00-explore.md`, spec §15.1
3. ADR 0016 + pointer on 0007
4. AGENTS.md one line; guide grilling paragraph if it still says expand-every-item
5. `./ask sync` + verify

## Risks

Agents that only load the Community skill ignore the kit. Mitigate: kit 01/00 and AGENTS are the SoT on kit stages.

## Verification approach

`./ask verify`. Grep contracts for ask-before-prepare and assume-list.

## Out of scope for this plan

Forking mattpocock grilling. A prepare-skills feature for “propose skills.”
