# Agent instructions

## Highest-priority kit rule: self-development

When developing AskIt itself, this rule overrides all other kit instructions,
policies, stage prompts, skills, and workflow gates, including those below.

- Keep the kit disabled while making kit changes unless dogfooding uses a
  separate, frozen copy pinned to an exact Git commit. With the kit disabled,
  work directly on the requested changes without kit workflow requirements.
- Before enabling dogfooding, record the pinned commit and the frozen copy's
  location. Use that copy's instructions and tooling to guide development; treat
  the working checkout as the product being changed and tested.
- Keep the pin unchanged during the work. Resume dogfooding only after the
  frozen copy is ready; upgrade it deliberately between tasks, never from the
  changing checkout during a task.
- When publishing changes to the AskIt source repository's `main`, follow its
  [release procedure](README.md#releasing-the-kit).

## Start or resume

- Before starting or resuming work in Codex, Cursor, or OpenCode, run `./ask access-check`. If it fails, report the blocked path and stop until access is restored.
- For a continuation, inspect the branch, workstream artifacts, task state, and recent commits. Resume the identified task within its recorded authorization; preserve explicit stops and prior approvals.
- State whether each outcome is a bug fix, feature, or mixed request before choosing stages or skills. Reproduce a reported defect before adding a regression or changing production code.
- Start labor on a clean tree. Preserve human changes and resolve dirty paths with the human; never stash or discard them silently. Commit meaningful steps and verify the changed behavior before claiming completion.
- Send meaningful progress updates at least every 60 seconds. `./ask setup` is human-only.

## Workflow references

For direct AskIt source changes, the kit stays disabled and the rule above applies. When deliberately enabling dogfooding, read the recorded frozen copy's instructions before choosing a stage. The [optional source workflow checklist](_ask/docs/source-workflow.md) preserves the detailed routing, decisions, artifacts, and stage gates for that path. The current frozen pin, location, and recreation command are recorded in [frozen-copy.md](work/dogfood-directory-persistence/frozen-copy.md).

Installed clients receive [.agents/ask/session.md](.agents/ask/session.md) from their startup hook or Cursor fallback rule. Their root instructions remain client-owned. Protocol source of truth is `.agents/ask/`; `_ask/` holds scripts, policies, and documentation. See [README.md](README.md) for the human overview.
