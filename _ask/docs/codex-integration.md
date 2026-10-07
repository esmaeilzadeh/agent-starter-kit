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

Sync preserves unrelated skills. It cleans stale marked ASK stage directories,
and refuses unmarked reserved directories, symlinks and unexpected extra
contents in generated directories. Relocate a consumer skill out of the
reserved namespace before retrying. Edit canonical stage files or overlays to
change a generated stage skill.

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
