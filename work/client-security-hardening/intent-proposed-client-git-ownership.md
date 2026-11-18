# Intent: AskIt client security hardening

## What

Make AskIt safer to install, upgrade, and use in fresh and existing client repositories.

- Require explicit trust before the global launcher delegates to project code. Keep shell completion inside the installed launcher and make changes to shell startup files opt-in.
- Check destination paths and ownership before install, upgrade, and generated output writes. Reject unsafe paths and ambiguous ownership before writing. Recover kit changes if installation fails midway.
- Move tracker credentials out of client Git worktrees, store them with owner-only permissions, and load them as data. Validate tracker URLs, require opt-in for user-wide MCP changes, and give existing clients migration and token-rotation guidance.
- Verify the selected kit revision before execution, pin external installers and bundled skills, and require explicit approval for new client skill sources.
- Preserve trusted local verification and reduce the environment inherited by local checks. Keep retained verification logs private.
- Validate generated agent configuration before publishing it and bind the workbench to loopback by default.
- Enforce Git ownership in fresh and existing clients. Keep project inputs trackable and ignore installed kit files, generated outputs and local state. Automatically migrate unchanged tracked kit copies while preserving the working files and existing client edits. Leave migration changes for the ordinary project upgrade commit.
- Make project and global installation reversible. Provide previewable uninstall commands that remove proven kit changes while preserving project configuration, credentials and unrelated edits.

## Why

Installing or using AskIt should not accidentally run untrusted repository code, expose client credentials or source, or damage client files. Existing clients need an upgrade path that preserves their project configuration and tells them when to migrate or rotate credentials.

## Non-goals

- Running tests from untrusted branches or pull requests in a managed sandbox.
- Reworking agent workflows or shipping a hosted workbench.
- Implementing, merging, or publishing code in this session. Stop after the accepted Stage 05 Plan and record that endpoint.
- Redefining the existing obligation to preserve client-owned files. Reproduce any violation and track its focused repair separately. Sequence shared installer work in the plan.

## Known assumptions

- One developer or trusted CI job runs the local commands with ordinary user privileges. No protection against a compromised host, shell, or trusted project is promised.
- A Git worktree isolates checkout state. Local verification still uses the caller's account, filesystem and network.
- Client-owned settings under `.agents/ask.local/` remain trackable. Credential values never belong in project Git.
- Keep the supported CLI entry points and existing valid local checks where compatible with the new trust boundary. Document any new opt-in and upgrade steps.
- Use disposable local fixtures and dummy tokens. Tests do not need live tracker accounts.
- Published audit and frozen kit: `88035127763fb1436775c13c941fbcba7484d581`, at `/tmp/askit-security.e0Qyvz/frozen`. Product base: `11c95e9e30833786e91caded025d84cab20ebfaa`. The audit establishes source observations, not exploit or dependency scan results.

## Open questions

Any choice that changes the approved intent or weakens a criterion goes through Spec Change. Stage 04 records its disposition even if none is needed.

## Human decisions

- Trusted local verification only.
- Follow Grill, Spec, Spec Challenge, Spec Change and Plan, then stop before implementation.

Explore skipped: destination already clear.

## E2E

Applicability: `applies` for the downstream CLI journeys. Start with temporary Git repositories for fresh install, reinstall, and upgrade of a client with custom rules and settings. Use a disposable user configuration directory and synthetic credentials. Observe trust decisions, preserved project files, safe defaults, and clear errors when setup or upgrade is rejected. Remove fixtures and reset the disposable user directory between journeys.
