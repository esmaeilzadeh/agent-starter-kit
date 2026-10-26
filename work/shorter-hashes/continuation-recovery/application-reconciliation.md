# Continuation recovery application reconciliation

Date: 2026-10-26  
Workstream: `shorter-hashes`  
Prior coordinator: `0c4dfcbbfa4d68e1ce2c0b6cd6c8b879c4a9b610` (state revision 11)  
Reviewed recovery candidate: `5129baf59fbe005bd8a7155eeb0842d036f76cb3`  
Accepted continuation-recovery integration: `725b6af` (`agent/continuation-recovery`, also the shorter-hashes parent)

## Authorization and scope

The user authorized a temporary, recorded exception on 2026-10-26. The scope is to adopt the already accepted continuation-recovery source changes into the shorter-hashes coordinator baseline. The continuation authorization is recorded in `continuation-authorization.md`; prior reconciliation review and user merge authorization are in `reconciliation-review.md` and the accepted continuation-recovery workstream artifacts.

This step advances only `coordinator_sha` and its tree snapshot. It preserves task statuses, all attempts, the Task 1 integration receipt, and Task 2's registered regression classification and blocker record. It does not mark any task complete or schedule work.

## Exact task-owned source postimages

The recovery audit named these paths as changed after the prior coordinator. SHA-1 values below are Git blob identities at the reviewed candidate; SHA-256 can be recomputed from each file when applying.

| Path | Git blob |
|---|---|
| `.agents/ask/verification/traceability/adapters.py` | `9a06336fd05f35812a48c6de90157a8b0f3528e5` |
| `.agents/ask/verification/traceability/cli.py` | `ab85395ffa51d2a16f11bacb35370dd9d80d61dd` |
| `.agents/ask/verification/traceability/completion.py` | `6abe5975706a36a94ac8769795f5c5989c528739` |
| `.agents/ask/verification/traceability/coverage.py` | `8510b86358371ccd47642d93344749aa20dc1cd8` |
| `.agents/ask/verification/traceability/evidence.py` | `2c2fe15dd1c63c7cfc8aaadd0dc819f0d35824ab` |
| `.agents/ask/verification/traceability/service.py` | `fc7a00ff339496fe47c68195df5cd991e12d4ecc` |
| `_ask/scripts/inner_loop/__main__.py` | `89cd8864c9eb4394f5672d94b2391cfd767365d7` |
| `_ask/scripts/inner_loop/attempts.py` | `70b9a3188ef3cbf0948ff6cef465ed0aa8c37ba1` |
| `_ask/scripts/inner_loop/checkpoint.py` | `901f0c9c6d35776325c33cc4753fbd644de45f9c` |
| `_ask/scripts/inner_loop/driver.py` | `579b9d25deaa7a7895f397322c8b1fb9ecf4306f` |
| `_ask/scripts/inner_loop/evidence.py` | `934d6b80cdbfa4521a7625713b3ae304281e3d46` |
| `_ask/scripts/inner_loop/recovery.py` | `82ae73797b93376e46f2b2129006858e4188785d` |
| `_ask/scripts/inner_loop/state.py` | `9384a92cbacd156d1100d70a6b110f6773d0dd15` |
| `_ask/scripts/start-work.sh` | `9fef4b17af1d5c00ce779e682e64fe378774aae6` |
| `_ask/tests/test-start-work-from-develop.sh` | `aade7523827b60b688f2d0c07e8241e682e8d990` |
| `_ask/tests/test-start-work-no-explore-map.sh` | `5dca9e8820a5a4fbb6c5d0f29184b385ea2990e3` |
| `ask` | `7638414330dc25f55b70ae89ae13c06effbec0ef` |

## Application result

Pending application through a state transaction whose validator permits exactly the paths above. After application, record the resulting state revision and checkpoint ref here. If any listed postimage changes before application, abort and regenerate this record and its review.
