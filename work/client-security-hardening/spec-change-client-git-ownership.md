# Specification change proposal: enforce client Git ownership

## Current specification

The current security specification and criterion registry are at `853f37d`. CSH-002 protects client settings and CSH-007 validates generated agent configuration. Neither defines the complete Git ownership boundary for installed files. See `client-git-audit.md` for the observed gaps.

## Proposed change

Add CSH-009. AskIt must leave every path it introduces in a client checkout either ignored as kit-owned or local state, or trackable and documented as project-owned. The ordinary install, reinstall, upgrade, and sync paths maintain this policy. No manual ignore or untracking step is required for a conflict-free installation or migration.

Use the kit's owned-file inventory to generate one managed client ignore block. Cover the installed package, protocol, dispatcher, stock docs and examples, generated skills and runtime bindings, and local state. Preserve existing client ignore entries and never ignore a whole shared editor directory. Remove the managed Codex skill exception in clients and keep those skills available locally. The source kit repository controls its own tracking policy.

Keep project-owned files trackable: project instructions, overlays, skill pins and lock, CheckPlan, public tracker metadata, custom editor definitions, specs, workstream artifacts, and deliberate evidence archives. Classify mixed files by ownership: keep a client-maintained config trackable, preserve its edits, and use a separate generated companion where the runtime supports it.

## Migration

For existing clients, migrate legacy custom inputs stored under kit paths to trackable project paths. Preflight Git status, effective ignore rules, and ownership. If a tracked file matches a known stock revision or an output regenerated from the same installed revision and inputs, automatically remove its index entry while retaining its working copy. Match ownership and bytes, not path alone. Reject a collision, conflicting ignore rule, or staged/unstaged edit before writing when it cannot be preserved automatically. Preserve staged work outside the operation. Restore affected index entries and file changes if the migration fails. Leave resulting changes for the ordinary project upgrade commit.

## Acceptance criteria

- After fresh install and sync, a normal Git add would include only intended project inputs. Every kit-owned or local output is ignored, including all generated Codex stage skills.
- Reinstall and upgrade converge on the same rules. They preserve custom project files and unrelated ignore entries, keep generated outputs usable, and are idempotent.
- For a legacy client with unchanged tracked stock files, upgrade untracks those files automatically and leaves their local contents intact. Ambiguous ownership or edits stop the operation without changing files or the index.
- Existing and newly created project settings remain stageable. Setup and verification keep credentials, private reports and transient files out of normal Git staging.
- The source kit repository can continue tracking its own generated stage projections.

## Impact and decision

Update the canonical spec and criterion registry, engineering model, task plan and client ownership documentation after approval. Sequence this with installer ownership and rollback tasks. Keep the separate Cursor rule preservation repair scoped to its reproduced defect.

Status: Proposed. Stage 04 will present this proposal and the full revised intent together after the pending Spec Challenge.
