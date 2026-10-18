# Acceptance

## Workstream

agent-decision-clarity

## Specification

Every required workflow confirmation is presented as selectable choices across canonical and generated Agent/Cursor bundles. The user is never required to write an approval sentence; unavailable controls use numbered options. Existing approval boundaries, conditional/negative rejection, intent digest binding, and exact action scope remain enforced. Unsolicited clear text approval, including next-action directions, remains accepted.

## Evidence

The compound approval regression failed before the parser change. The confirmation test and workstream smoke both pass. `./ask prepare` and `./ask sync` were run; the pinned `frontend-design` skill fetch failed because its configured revision is unavailable, while remaining pinned skills and runtime projections prepared successfully. Full repository verification stops before checks due the missing coordinator accepted-tests ref.

## Residual risks

Ordinary yes/no questions and important-decision alerts remain parked in `button-based-user-questions`; broader workflow nesting and conflict inventory remain parked in `agent-decision-clarity`.

## Context-engineering audit

The canonical stage contracts, workflow/delegation/worktree policies, guide/spec references, root guidance, and generated Agent/Cursor projections use selectable choices for every required confirmation and do not request written approval sentences.

## Acceptance decision

Accepted for the reported approval friction and parser defect.

## Accepted commit SHA

Pending.
