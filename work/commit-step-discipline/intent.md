# Intent: enforce stepwise commits on work branches

## What

Strengthen kit policy so agents **must commit after each meaningful step on `agent/<work-id>` without waiting for the human to ask**. Make the safety rationale explicit: one plan → one branch isolates those commits from `main`.

## Why

Agents (and global Cursor habits) sometimes defer commits until the human says “commit,” which fights the kit’s recoverability model. Dedicated work branches remove the usual risk of proactive commits.

## Non-goals

Changing `start-work` branching defaults. Auto-committing via hooks. Touching `main` merge process.

## Human decisions

Kit protocol overrides any global “only commit when asked” habit while this policy is in force.
