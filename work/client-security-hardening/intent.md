# Proposed intent: AskIt client security and model decision flow

## What

Make AskIt safer to install, upgrade, and use in fresh and existing client repositories, and make model decisions predictable through the authorized workflow.

- Require explicit trust before the global launcher delegates to project code. Keep shell completion inside the installed launcher and make changes to shell startup files opt-in.
- Check destination paths and ownership before install, upgrade, and generated output writes. Reject unsafe paths and ambiguous ownership before writing. Recover kit changes if installation fails midway.
- Move tracker credentials out of client Git worktrees, store them with owner-only permissions, and load them as data. Validate tracker URLs, require opt-in for user-wide MCP changes, and give existing clients migration and token-rotation guidance.
- Verify the selected kit revision before execution, pin external installers and bundled skills, and require explicit approval for new client skill sources.
- Preserve trusted local verification and reduce the environment inherited by local checks. Keep retained verification logs private.
- Validate generated agent configuration before publishing it and bind the workbench to loopback by default.
- Confirm the complete model plan once during Grill, accept defaults together, and collect only requested stage exceptions. Reuse the recorded choices across stages and continuation without routine model gates.
- Before authorized implementation, use the latest accessible implementor model for the active runtime unless the human chose an exact override. Switch the orchestrator automatically when supported; otherwise stop and ask the human to change it before implementation starts.

## Why

Installing or using AskIt should not accidentally run untrusted repository code, expose client credentials or source, or damage client files. Existing clients need an upgrade path that preserves their project configuration and tells them when to migrate or rotate credentials. Once the user seals the specification, the workflow should continue to its authorized endpoint without repeated model questions, except for a real escalation or a required manual orchestrator switch.

## Non-goals

- Running tests from untrusted branches or pull requests in a managed sandbox.
- Workflow changes beyond the model decision and implementation-orchestrator handoff described above.
- Shipping a hosted workbench.
- Implementing, merging, or publishing code in this session. Stop after the accepted Stage 05 Plan and record that endpoint.
- Redefining the existing obligation to preserve client-owned files. Reproduce any violation and track its focused repair separately. Sequence shared installer work in the plan.

## Known assumptions

- One developer or trusted CI job runs the local commands with ordinary user privileges. No protection against a compromised host, shell, or trusted project is promised.
- A Git worktree isolates checkout state. Local verification still uses the caller's account, filesystem and network.
- Client-owned settings under `.agents/ask.local/` remain trackable. Credential values never belong in project Git.
- Keep the supported CLI entry points and existing valid local checks where compatible with the new trust boundary. Document any new opt-in and upgrade steps.
- Use disposable local fixtures and dummy tokens. Tests do not need live tracker accounts. Model-flow tests use fake runtime catalogs and switch capabilities; paid live model calls are not required.
- Composer for Cursor and Luna for Codex are the human's current implementor-family examples. Resolve accessible runtime models rather than freezing these examples into universal version names. Unsupported automatic orchestrator switching requires a manual handoff, not a claimed switch.
- During Grill, the model confirmation includes the policy of using the latest accessible implementor at implementation entry; exact human overrides remain fixed. Changing a child model does not change the orchestrator.
- Published audit and frozen kit: `88035127763fb1436775c13c941fbcba7484d581`, at `/tmp/askit-security.e0Qyvz/frozen`. Product base: `11c95e9e30833786e91caded025d84cab20ebfaa`. The audit establishes source observations, not exploit or dependency scan results.

## Open questions

Any choice that changes the approved intent or weakens a criterion goes through Spec Change. Stage 04 records its disposition even if none is needed.

## Human decisions

- Trusted local verification only.
- Follow Grill, Spec, Spec Challenge, Spec Change and Plan, then stop before implementation.
- Human requested the model-flow extension; approval of this complete revised intent and its linked proposal is pending. The existing explicit Astra choice remains recorded.

Explore skipped: destination already clear.

## E2E

Applicability: `applies` for the downstream CLI journeys. Start with temporary Git repositories for fresh install, reinstall, and upgrade of a client with custom rules and settings. Use a disposable user configuration directory and synthetic credentials. Observe trust decisions, preserved project files, safe defaults, and clear errors when setup or upgrade is rejected. Remove fixtures and reset the disposable user directory between journeys.

## Model-flow verification

Exercise one upfront default confirmation, a specific stage exception, uninterrupted stage transitions, preserved genuine escalations, continuation, runtime availability, automatic and manual orchestrator handoff, and a plan-only stop using disposable fixtures. Keep independent review and final acceptance requirements. See `spec-change-model-flow.md` for the proposed observable criteria.
