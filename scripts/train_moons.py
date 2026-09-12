#!/usr/bin/env python3
"""Train a tiny sklearn MLP on make_moons. Reads results/<run-id>/config.yaml."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
    from sklearn.datasets import make_moons
    from sklearn.metrics import accuracy_score
    from sklearn.model_selection import train_test_split
    from sklearn.neural_network import MLPClassifier
except ImportError:
    sys.stderr.write("train_moons: pip install scikit-learn numpy pyyaml\n")
    sys.exit(2)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    p.add_argument("--repo", default=".")
    args = p.parse_args()
    run_dir = Path(args.repo) / "results" / args.run_id
    cfg_path = run_dir / "config.yaml"
    if not cfg_path.is_file():
        sys.stderr.write(f"train_moons: missing {cfg_path}\n")
        return 1
    cfg = yaml.safe_load(cfg_path.read_text()) or {}
    seed = int(cfg.get("seed", 0))
    n_samples = int(cfg.get("n_samples", 200))
    noise = float(cfg.get("noise", 0.25))
    hidden = cfg.get("hidden_layer_sizes", [16])
    if isinstance(hidden, int):
        hidden = (hidden,)
    else:
        hidden = tuple(int(x) for x in hidden)
    lr = float(cfg.get("learning_rate_init", 0.01))
    max_iter = int(cfg.get("max_iter", 400))
    X, y = make_moons(n_samples=n_samples, noise=noise, random_state=seed)
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=seed)
    clf = MLPClassifier(
        hidden_layer_sizes=hidden,
        learning_rate_init=lr,
        max_iter=max_iter,
        random_state=seed,
    )
    clf.fit(Xtr, ytr)
    acc = float(accuracy_score(yte, clf.predict(Xte)))
    (run_dir / "train_output.json").write_text(
        json.dumps({"accuracy": acc, "n_iter": int(getattr(clf, "n_iter_", 0))}, indent=2)
        + "\n"
    )
    print(f"{acc:.4f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
