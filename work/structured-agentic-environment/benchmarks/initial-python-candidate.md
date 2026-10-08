# Initial validator candidate measurements

The machine-readable detail is in `initial-python-candidate.json`. The recorded source is commit `eb80b7b1b92d05e505cd719886833c81368ec1f0`; the report also binds the validator and benchmark script by SHA-256.

## Workloads and environment

- Actual pilot: 12 nodes, 12 edges, 6 files in its referenced-file closure.
- Synthetic graphs: 100 / 1,000 / 10,000 nodes. Valid graphs have 197 / 1,997 / 19,997 edges; invalid-link and cycle variants each add one edge. Each generated model is one JSON file.
- Fifteen fresh-process repetitions per workload, plus in-process file-read, parse and validation timings. Peak resident memory is recorded per process.
- Linux 6.2, Intel Core i7-2720QM at 2.20 GHz, x86_64, Python 3.10.12, 8 logical CPUs.

## Results

| Workload | Full CLI p50 / p95 | Validation-only p50 | Peak RSS |
| --- | ---: | ---: | ---: |
| Pilot, 12 nodes | 69.6 / 78.5 ms | 6.1 ms | 11.4 MiB |
| Valid, 100 nodes | 72.9 / 80.5 ms | 2.2 ms | 11.5 MiB |
| Valid, 1,000 nodes | 104.5 / 111.1 ms | 22.8 ms | 13.7 MiB |
| Valid, 10,000 nodes | 399.8 / 407.4 ms | 270.5 ms | 36.3 MiB |
| Invalid link, 10,000 nodes | 399.8 / 425.6 ms | 284.2 ms | 36.3 MiB |
| Cycle, 10,000 nodes | 411.4 / 424.5 ms | 274.6 ms | 37.5 MiB |

At 10,000 nodes, warm stdlib JSON parsing was 32.3 ms p50; installed `orjson` parsing was 18.9 ms. The graph-validation pass dominates this candidate's time. These are local observations, not a promised latency or a comparison with a native validator. No latency budget has been agreed. `cc` is present, but no native JSON library, Rust, or Go toolchain was found in this environment. The complete pre/post action guard has not been implemented or measured.

## Decision status

Python is the first working candidate behind `./ask model validate`. The benchmark has not approved Python as the final implementation. Keep the model's tool-selection decision open until the required complete action path is measured against an agreed need; reassess whether a native parser/graph core is warranted then.
