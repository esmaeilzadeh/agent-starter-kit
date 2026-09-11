# part-engineering

Portable AI Engineering Starter Kit protocol root (branded; not a generic `engineering/` folder).

## Layout (skeleton)

```text
part-engineering/
├── guide/          # modular Guide (kit-owned)
├── spec/           # modular Build Spec (kit-owned)
├── agents/         # stage contracts 00 Explore … 10 Accept
├── policies/       # delegation, risk, verification
├── decisions/      # kit-level decision records (optional)
├── skills/         # Skill Manifest + prepare-skills.sh
└── templates/      # explore-map, intent, spec, plan, …

Also at repo root (siblings of this tree):
├── specs/          # product/workstream specifications
├── work/           # workstream artifacts (explore-map, intent, …)
├── scripts/        # kit guardrail / install / sync scripts
└── .agents/skills/ # prepared Community Skill bodies (gitignored)
```

Prepared Community Skills are installed under `.agents/skills/` and are **not** vendored into git — regenerate via `part-engineering/skills/prepare-skills.sh` once that script exists.
