"""Replay the frozen questions through the implemented public reference API."""
import argparse
import contextlib
import hashlib
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    root, output = args.root.resolve(), args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("output must be empty so previous files cannot change the totals")
    sys.path.insert(0, str(root / ".agents/ask"))
    from workflow_refs.benchmark import (EXPECTED_BASELINE_SOURCE, MANIFEST_PATH,
        _git_blob, _projection_for_path, _tokenizer, capture_baseline)
    from workflow_refs.cli import main as refs
    from workflow_refs.store import initialize_catalog, register_revision

    def write(path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def json_bytes(value):
        return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode()

    baseline = capture_baseline(root)
    manifest = json.loads((root / MANIFEST_PATH).read_text())
    encoding = _tokenizer(manifest)
    originals = {row["path"]: _git_blob(root, EXPECTED_BASELINE_SOURCE, row["path"])
                 for row in manifest["files"]}
    source_texts = {path: raw.decode("utf-8") for path, raw in originals.items()}
    candidate_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    journeys, lookup_map, responses = [], {}, {}
    with tempfile.TemporaryDirectory(prefix="refs-savings-") as temp:
        candidate = Path(temp)
        def git(*argv):
            return subprocess.check_output(["git", *argv], cwd=candidate, stderr=subprocess.PIPE)
        git("init", "-q", "-b", "benchmark")
        git("config", "user.name", "Frozen reference replay")
        git("config", "user.email", "replay@example.test")
        objects = subprocess.check_output(["git", "rev-parse", "--git-path", "objects"],
                                          cwd=root, text=True).strip()
        write(candidate / ".git/objects/info/alternates",
              (str((root / objects).resolve()) + "\n").encode())
        git("update-ref", "refs/heads/benchmark", EXPECTED_BASELINE_SOURCE)
        owners = set()
        for number, (path, raw) in enumerate(originals.items(), 1):
            owner = path.split("/")[1] if path.startswith("work/") else Path(path).stem
            catalog = candidate / "work" / owner / "references/integrity.json"
            if owner not in owners:
                initialize_catalog(catalog, owner)
                owners.add(owner)
            entry = register_revision(catalog, owner, f"{owner}/snapshot/{number}",
                {"commit": EXPECTED_BASELINE_SOURCE, "path": path}, path, "prose-item/1", raw)
            reference = entry["reference"]
            lookup_map[path] = reference
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = refs(["show", reference], root=candidate)
            if code:
                raise RuntimeError(f"public lookup failed: {path}: {stream.getvalue()}")
            responses[path] = stream.getvalue()
            write(output / "candidate/generated/responses" / (path + ".json"),
                  responses[path].encode())
            for side in ("baseline", "candidate"):
                write(output / side / "legacy-inputs" / path, raw)
            if next(row for row in manifest["files"] if row["path"] == path)["metadata"]:
                write(output / "baseline/generated" / path, raw)
        for owner in sorted(owners):
            path = Path("work") / owner / "references/integrity.json"
            write(output / "candidate/generated" / path, (candidate / path).read_bytes())
        write(output / "candidate/generated/lookup-index.json", json_bytes(lookup_map))

        for before in baseline["journeys"]:
            parts = ["Question:\n" + before["question"]]
            equivalent = True
            selected = {source["path"]: lookup_map[source["path"]] for source in before["source_inputs"]}
            parts.append("Lookup index:\n" + json_bytes(selected).decode())
            for source in before["source_inputs"]:
                path = source["path"]
                payload = json.loads(responses[path])["payload"]
                text = json.dumps(payload, ensure_ascii=False) if not isinstance(payload, str) else payload
                equivalent &= _projection_for_path(before["id"], path, text, source_texts) == source["text"]
                parts.append(f"Request: refs show {lookup_map[path]}\nResponse:\n{responses[path]}")
            transcript = "\n\n".join(parts)
            write(output / "transcripts" / (before["id"] + "-baseline.txt"), before["transcript"].encode())
            write(output / "transcripts" / (before["id"] + "-candidate.txt"), transcript.encode())
            tokens = len(encoding.encode_ordinary(transcript))
            journeys.append({"id": before["id"], "equivalent_evidence": bool(equivalent),
                "baseline_tokens": before["input_tokens"], "candidate_tokens": tokens,
                "token_regression": tokens > before["input_tokens"]})

    files, totals = {}, {}
    for side in ("baseline", "candidate"):
        files[side] = [{"path": str(path.relative_to(output / side)), "bytes": path.stat().st_size,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                       for path in sorted((output / side).rglob("*.json"))]
        totals[side] = {"agent_input_tokens": sum(j[side + "_tokens"] for j in journeys),
                        "metadata_bytes": sum(row["bytes"] for row in files[side])}
    passed = (all(j["equivalent_evidence"] for j in journeys) and
              all(totals["candidate"][unit] < totals["baseline"][unit]
                  for unit in ("agent_input_tokens", "metadata_bytes")))
    report = {"schema": "ask-reference-savings/v1", "status": "pass" if passed else "fail",
        "candidate_sha": candidate_sha, "baseline_source": EXPECTED_BASELINE_SOURCE,
        "workload_version": baseline["workload_version"], "tokenizer": baseline["tokenizer"],
        "journeys": journeys, "totals": totals, "metadata_files": files,
        "scope": "Historical whole-file reference lookups; original outcomes and source identities preserved.",
        "full_value_exceptions": ["Immutable legacy originals, catalog digests and exact source commits remain full values."],
        "accounting": "Every public response and lookup-index input is counted. Equal immutable JSON archives are included on both sides; generated catalogs and response JSON are included once per output path. Prose and logs remain in the raw transcripts."}
    write(output / "report.json", json_bytes(report))
    print(json.dumps({key: report[key] for key in ("status", "journeys", "totals")}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
