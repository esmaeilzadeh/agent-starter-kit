# Specification change proposal: client Git ownership and uninstall

**Status: historical draft.** This proposal was never approved. The [accepted security specification](../../specs/current/client-security-hardening.md) assigns CSH-009 and CSH-010 to model flow. A revived proposal needs new criterion IDs and approval against the current spec.

## Specification at the time of drafting

This draft used the security specification and criterion registry at `853f37d`. CSH-002 protects client settings and CSH-007 validates generated agent configuration. Neither defines the complete Git ownership boundary for installed files. See `client-git-audit.md` for the observed gaps.

## Proposed change

Git ownership: AskIt must leave every path it introduces in a client checkout either ignored as kit-owned or local state, or trackable and documented as project-owned. The ordinary install, reinstall, upgrade, and sync paths maintain this policy. No manual ignore or untracking step is required for a conflict-free installation or migration.

Use the kit's owned-file inventory to generate one managed client ignore block. Cover the installed package, protocol, dispatcher, stock docs and examples, generated skills and runtime bindings, and local state. Preserve existing client ignore entries and never ignore a whole shared editor directory. Remove the managed Codex skill exception in clients and keep those skills available locally. The source kit repository controls its own tracking policy.

Keep project-owned files trackable: project instructions, overlays, skill pins and lock, CheckPlan, public tracker metadata, custom editor definitions, specs, workstream artifacts, and deliberate evidence archives. Classify mixed files by ownership: keep a client-maintained config trackable, preserve its edits, and use a separate generated companion where the runtime supports it.

Reversible installation: provide `ask uninstall --dry-run` for one client checkout and `askit self-uninstall --dry-run` for the global installation. Both commands support applying the same previewed operation. Use the same ownership records as install and upgrade. Uninstall removes verified kit files and reverses AskIt-managed entries in shared files, preserving project settings, credentials, unrelated edits and the Git index. Global uninstall removes its verified launcher, cache and opted-in completion entries. It leaves installed client projects intact. Project uninstall does not change the global installation.

For project uninstall, a file is eligible for deletion only if AskIt can prove it owns the file and Git does not track it. Preserve project-owned files even when untracked, and report tracked kit artifacts as retained. Keep project instructions, verification settings, overlays, specs, and work records. In a shared file such as `.gitignore`, remove only the verified AskIt-managed entries and preserve all project entries. Never delete the shared file or modify the Git index.

## Migration

For existing clients, migrate legacy custom inputs stored under kit paths to trackable project paths. Preflight Git status, effective ignore rules, and ownership. If a tracked file matches a known stock revision or an output regenerated from the same installed revision and inputs, automatically remove its index entry while retaining its working copy. Match ownership and bytes, not path alone. Reject a collision, conflicting ignore rule, or staged/unstaged edit before writing when it cannot be preserved automatically. Preserve staged work outside the operation. Restore affected index entries and file changes if the migration fails. Leave resulting changes for the ordinary project upgrade commit.

For uninstall, preflight the complete operation. If a legacy artifact lacks ownership evidence, or a kit artifact has been edited, identify the affected path and stop before deleting or overwriting anything. Use the installation rollback mechanism to recover from failure or interruption. A successful uninstall can be rerun safely.

## Acceptance criteria

- After fresh install and sync, a normal Git add would include only intended project inputs. Every kit-owned or local output is ignored, including all generated Codex stage skills.
- Reinstall and upgrade converge on the same rules. They preserve custom project files and unrelated ignore entries, keep generated outputs usable, and are idempotent.
- For a legacy client with unchanged tracked stock files, upgrade untracks those files automatically and leaves their local contents intact. Ambiguous ownership or edits stop the operation without changing files or the index.
- Existing and newly created project settings remain stageable. Setup and verification keep credentials, private reports and transient files out of normal Git staging.
- The source kit repository can continue tracking its own generated stage projections.
- Install and uninstall a fresh client. The preview makes no writes, and applying it removes the kit runtime, generated outputs, and managed ignore entries. Project files and the Git index stay intact.
- Uninstall in a client with committed project settings, untracked project settings, and a tracked legacy copy of a kit file. All three remain on disk and the Git index stays unchanged. Only verified untracked kit files are deleted.
- Install, upgrade, then uninstall in a client with custom rules and settings. Project-owned files stay byte-identical. An ambiguous legacy artifact, edited kit artifact, or simulated failure leaves the client's pre-uninstall state recoverable.
- Globally install with completion enabled, then self-uninstall. Remove only the owned launcher, cache and completion entries. Preserve unrelated shell configuration and installed projects. Repeating either uninstall reports that there is nothing left to remove.

## Impact and decision

Update the canonical spec and criterion registry, engineering model, task plan and client ownership documentation after approval. Sequence this with installer ownership and rollback tasks. Keep the separate Cursor rule preservation repair scoped to its reproduced defect.
