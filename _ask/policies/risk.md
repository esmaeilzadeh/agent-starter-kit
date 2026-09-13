# 17. Risk policy

File:

```text
_ask/policies/risk.md
```

Risk classification must consider:

```text
reversibility
blast radius
external impact
data loss
security consequences
business consequences
```

Default:

```text
LOW
  autonomous + normal checks

MEDIUM
  autonomous + stronger verification

HIGH
  proposal + human approval

CRITICAL / IRREVERSIBLE
  human authority mandatory
```

Review’s default **pool** (`cheap` vs `diverse`) follows this class. Slugs for those pools are per runtime in `_ask/bindings/runtimes/`. Unset risk is LOW.

Projects should customize this according to their domain.

Line count is not an adequate risk metric.

---
