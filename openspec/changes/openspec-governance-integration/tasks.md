## 1. Baseline and pin

- [x] 1.1 Record `work/openspec-governance-integration/baseline.md`
- [x] 1.2 Add `_ask/openspec-pin.yaml` and `_ask/scripts/openspec_cli.py` with stub tests

## 2. Cutover

- [x] 2.1 `openspec init --tools none --no-animation --profile core`
- [x] 2.2 Create `openspec/changes/openspec-governance-integration/` with proposal, deltas, design, tasks
- [x] 2.3 Replace kit spec copies and `work/.../plan.md` with pointers
- [x] 2.4 Park `.later/openspec-pilot-evaluation.md`
- [x] 2.5 Targeted `openspec validate` --strict valid and status planning complete

## 3. Gates

- [ ] 3.1 `check-workstream` marked-pilot path (marker, targeted validate/status, pointers, skip_specs, archive lookup)
- [ ] 3.2 `status` checkout-scoped CLI, stage, `code-without-plan`, nextSteps strip
- [ ] 3.3 `verify --work-id` dirty refuse and `work/<id>/verification.json`
- [ ] 3.4 `./ask openspec-archive` refuse without Accept SHA; detect direct archive

## 4. Ownership and contracts

- [ ] 4.1 `_ask/OWNED-PATHS.md` lists `openspec/` consumer-owned
- [ ] 4.2 ADR-0018 for the 1.13.0 dependency and top-level path
- [ ] 4.3 `ask` help, completion, Build Spec, stage contracts
- [ ] 4.4 Existing install and smoke tests still pass
