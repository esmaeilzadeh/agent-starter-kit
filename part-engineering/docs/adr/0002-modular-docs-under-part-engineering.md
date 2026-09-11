# Modular Guide/Spec live under part-engineering/ (not docs/)

Guide and Build Spec split into coarse numbered modules under `part-engineering/guide/` and `part-engineering/spec/`, with short stubs at the old monolith paths. We rejected root `docs/guide|spec` because this repository *is* the starter-kit template and may install into existing product repos that already own `docs/`. A generator-only layout could use `docs/`; install-into-existing requires a kit-namespaced tree.

## Consequences

- One layout for design repo, template clone, and overlay install
- Consumer project docs stay free of kit collisions
- `part-engineering/` holds both protocol runtime files and conceptual/spec modules
