# Initial validator candidate measurements

The machine-readable detail is in `initial-python-candidate.json`. The recorded source is commit `023e01637162734d76ddd2cd746253de7b4993e9`; the report also binds the validator and benchmark script by SHA-256. CLI timings include referenced-input snapshot hashing and a freshness reread; validation-only timings exclude them.

## Workloads and environment

- Actual pilot: 12 nodes, 12 edges, 6 files in its referenced-file closure.
- Synthetic graphs: 100 / 1,000 / 10,000 nodes. Valid graphs have 197 / 1,997 / 19,997 edges; invalid-link and cycle variants each add one edge. Each generated model is one JSON file.
- Fifteen fresh-process repetitions per workload, plus in-process file-read, parse and validation timings. Peak resident memory is recorded per process.
- Linux 6.2, Intel Core i7-2720QM at 2.20 GHz, x86_64, Python 3.10.12, 8 logical CPUs.

## Results

| Workload | Full CLI p50 / p95 | Validation-only p50 | Peak RSS |
| --- | ---: | ---: | ---: |
| Pilot, 12 nodes | 84.4 / 89.1 ms | 4.6 ms | 14.8 MiB |
| Valid, 100 nodes | 78.6 / 91.7 ms | 6.2 ms | 14.8 MiB |
| Valid, 1,000 nodes | 111.6 / 118.5 ms | 23.5 ms | 17.1 MiB |
| Valid, 10,000 nodes | 436.5 / 471.0 ms | 267.9 ms | 39.7 MiB |
| Invalid link, 10,000 nodes | 437.6 / 461.1 ms | 260.3 ms | 39.6 MiB |
| Cycle, 10,000 nodes | 438.8 / 473.7 ms | 263.4 ms | 40.8 MiB |

At 10,000 nodes, warm stdlib JSON parsing was 32.5 ms p50; installed `orjson` parsing was 18.5 ms. The graph-validation pass dominates this candidate's time. These are local observations, not a promised latency or a comparison with a native validator. No latency budget has been agreed. `cc` is present, but no native JSON library, Rust, or Go toolchain was found in this environment. The complete pre/post action guard has not been implemented or measured.

## Decision status

Python is the first working candidate behind `./ask model validate`. The benchmark has not approved Python as the final implementation. Keep the model's tool-selection decision open until the required complete action path is measured against an agreed need; reassess whether a native parser/graph core is warranted then.
