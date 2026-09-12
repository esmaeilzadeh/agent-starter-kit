# Experiment results

Each run is a directory. Hyperparams live in **that** directory. Commit the config (and any trainer code change) **before** training. `./ask record-run` binds the metric to `HEAD`.

```text
results/<run-id>/
  config.yaml
  run_manifest.json   # after record-run
  summary.json
```

Index: [RUN_REGISTRY.md](RUN_REGISTRY.md). Cite **path + git_sha + metric**.
