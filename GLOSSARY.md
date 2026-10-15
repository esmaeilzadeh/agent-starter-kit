# Engineering Workbench

Terms used to describe promised behavior and delivery work in the Engineering
Workbench. This glossary records the human's 2026-10-16 modeling decisions;
the proposed specification defines their observable requirements. Starter Kit
protocol vocabulary remains in `CONTEXT.md`.

## Language

**Epic**:
The overall user promise and scope of the engineering environment represented
by this pilot.
_Avoid_: unexplained title standing in for a defined promise

**Story**:
An observable outcome valuable to the developer using the environment.
_Avoid_: implementation step, interchangeable use with Task

**Scenario**:
A concrete behavioral flow or example associated with a Story when that
relationship is recorded. A missing Story relationship is permitted.
_Avoid_: implementation task, synonym for Story

**Task**:
A unit of delivery work that can support multiple Stories or Scenarios while
remaining the same work item.
_Avoid_: duplicated work item for each supported Story

**Feature**:
A capability related to Stories, rather than their exclusive ownership
container.
_Avoid_: compulsory extra level for every Story
