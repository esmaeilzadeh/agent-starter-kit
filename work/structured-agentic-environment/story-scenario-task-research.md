# Story, Scenario, and Task: short research

Researched 2026-10-16 to inform the amended intent. These findings distinguish established practices from choices for this environment; they do not resolve the remaining human decisions.

## What the sources establish

**Scrum does not mandate an Epic → Feature → Story → Scenario → Task taxonomy.** Its guide defines Product Backlog items and a delivery plan, leaving decomposition to Developers. It explicitly describes other techniques as context dependent. Therefore a particular hierarchy is a tooling or modeling convention, rather than a Scrum obligation. [Scrum Guide: framework and Sprint Planning](https://scrumguides.org/scrum-guide.html)

**A user story describes a valuable functional increment.** Agile Alliance emphasizes contribution to product value and warns against mechanically creating one story per requirements-document section. A source section can explain a story without determining its boundaries. [Agile Alliance: User Stories](https://agilealliance.org/glossary/user-stories/)

**A scenario describes a concrete example of behavior, rather than implementation work.** Cucumber treats Scenario and Example as synonyms: context, event, and expected outcome. It recommends user-observable outcomes. Its vocabulary supports distinguishing a story's purpose from particular successful, alternate, or failure flows; it does not prescribe a Story entity or a minimum number of scenarios per story. [Cucumber: Gherkin reference](https://cucumber.io/docs/gherkin/reference/)

**Tasks conventionally express delivery work beneath requirements.** Azure Boards uses Epic → Feature → Requirement → Task, with different requirement names for different processes. This demonstrates an established separation between promised value and implementation work; it does not make Azure's complete hierarchy necessary here. [Microsoft: work item types](https://learn.microsoft.com/en-us/azure/devops/boards/work-items/about-work-items?view=azure-devops)

**A containment tree and shared support relationships are different mechanisms.** Azure's parent-child links allow only one parent, while other link types represent networks and dependencies. Accordingly, a task supporting multiple stories should not silently acquire multiple ownership parents or be duplicated as several tasks. [Microsoft: link types](https://learn.microsoft.com/en-us/azure/devops/boards/queries/link-type-reference?view=azure-devops)

## Recommendation for this workstream

These are proposed model choices based on the user's answers, not rules asserted by the sources:

- Keep **Epic** as the overall promise and scope, **Story** as a user outcome, **Scenario** as a particular behavioral flow/example, and **Task** as an actionable delivery unit. A story can have one scenario or several. Tasks remain visible from the stories and scenarios they support.
- Keep **Feature** as an optional capability relationship, rather than a compulsory extra navigation level. Stories and scenarios have different jobs and should not be merged merely to reduce entity count.
- Give a shared task one canonical identity and link it to every relevant story/scenario. Distinguish “supports this behavior” from “depends on this task.” The exact relationship fields and ownership policy remain specification decisions.
- Preserve optional Story membership, as requested. Explicitly show when a scenario has no linked story; do not invent one or call the whole model invalid merely to complete a tree.
- Demonstrate one representative story end to end. Show its readable definition, relevant main-spec passages, associated plan-task text, implementation tasks, and understandable tests/results. This is a limited demonstration of relationships that must work for other work Ask handles.
- Evidence should explain setup, action, expected observation, actual observation, and related scenario/task. Helper functions and fixtures are compatible with readability when their names and necessary comments expose their purpose. A bare pass badge or opaque function name does not restore context.

## Limits

This research does not establish a universal cardinality or shared-task ownership rule. It does not require adopting Scrum, Azure Boards, Cucumber, or Gherkin syntax. The user's phrase “a user story have only single story” still needs confirmation; the likely interpretation is “a story may have only one scenario.”
