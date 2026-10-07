# Codex integration

Run `./ask sync` after changing canonical stage contracts or local overlays.
The generator writes eleven Codex repository skills under `.agents/skills/`
and custom agents under `.codex/agents/`. Stage bodies come from
`.agents/ask/stages/`; overlays come from `.agents/ask.local/stages/` with the
existing legacy overlay fallback. Cursor uses the same stage bodies.

Invoke a Codex skill explicitly with `$kit-00-explore`, `$kit-01-grill`, and
so on through `$kit-10-accept`. Cursor stage commands use `/00-explore`
through `/10-accept`. Stage gates and artifacts apply in either runtime.

## Ownership

Direct child names `kit-*` in `.agents/skills/` are reserved for generated ASK
stages. Commit these generated files with canonical changes. Community Skills
use other names and remain ignored. `./ask prepare` rejects reserved names
before invoking an installer. Install and upgrade migrate the kit's blanket
ignore rule to selective rules and regenerate projections, including when
`--skip-prepare` skips dependency installation.

Install and upgrade ask Git whether generated skills can be tracked. If a
consumer rule such as `.agents/` still blocks them, the command fails with the
blocking rule's location. Adjust that consumer rule explicitly and retry;
kit migration preserves unrelated ignore rules.

Sync preserves unrelated skills. It cleans stale marked ASK stage directories,
and refuses unmarked reserved directories, symlinks and unexpected extra
contents in generated directories. Relocate a consumer skill out of the
reserved namespace before retrying. Edit canonical stage files or overlays to
change a generated stage skill.

## Migrating a consumer installed before Codex stage skills

Check out the desired kit tag or SHA in a separate directory. From that kit
checkout, run its upgrader against the existing consumer repository:

```bash
bash _ask/scripts/upgrade-kit.sh --target /absolute/path/to/consumer \
  --version '<tag-or-sha>' --source '<kit-git-url>' --skip-prepare
```

Use the same version for the checkout and `--version`. The target version's
script runs the migration, preserving the consumer manifest, Community Skills,
overlays and verification config. `--skip-prepare` skips dependency installation;
projections and ignore migration still run. Omit it to prepare dependencies.

An older installed `./ask upgrade` executes its old script, which may skip the
new migration even after replacing kit files. Use the target-checkout entrypoint
for this first migration. Subsequent upgrades can use the updated consumer's
`./ask upgrade` normally.

## Validation and manual check

`_ask/tests/test-codex-skill-parity.sh` checks all eleven stages, overlay parity,
repeat generation, ownership protection, preparation namespace validation,
Git trackability and isolated install/upgrade flows.

In a Codex session that has refreshed repository skills, inspect the skill
selector and invoke `$kit-00-explore`. Check that it loads the generated
contract and follows its artifact and human-decision gates. Live UI discovery
and custom-agent spawning remain manual checks; shell tests cover generated
files and CLI behavior.

The handoff records official documentation consulted on 2026-10-07:
[skills](https://learn.chatgpt.com/docs/build-skills),
[subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents), and
[slash commands](https://learn.chatgpt.com/docs/reference/slash-commands).
A refresh attempt during implementation failed because network connections
were unavailable. Discovery and invocation guidance uses that previously
recorded interface; live behavior was not verified in this run.
