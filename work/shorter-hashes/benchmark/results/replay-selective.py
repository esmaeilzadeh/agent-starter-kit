"""Replay the frozen questions through the implemented public reference API."""
import argparse
import contextlib
from decimal import Decimal
import hashlib
import io
import json
from pathlib import Path
import re
import shlex
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
        _git_blob, _tokenizer, capture_baseline)
    from workflow_refs.cli import main as refs
    from workflow_refs.store import initialize_catalog, register_revision

    def write(path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)

    def json_bytes(value):
        return (json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n").encode()

    def projection_args(path, expected_text, source_text):
        if expected_text == source_text:
            return []
        if path.endswith(".md"):
            headings = [heading for heading in ("Status and authority", "Specification", "Approach")
                        if f"## {heading}" in expected_text]
            args = [argument for heading in headings for argument in ("--section", heading)]
            rows = [line for line in expected_text.splitlines() if line.startswith("| ")
                    and not line.startswith("|---") and not line.startswith("|   ")]
            if rows:
                task_id = rows[0].split("|", 2)[1].strip()
                args.extend(("--task-row", task_id))
                if expected_text.endswith("\n\n"):
                    args.append("--blank-line")
            return args
        if path.endswith((".yaml", ".yml")):
            match = re.search(r"(?m)^  - id: (.+)$", expected_text)
            return ["--yaml-task", match.group(1)] if match else []
        if not path.endswith(".json"):
            return []
        expected, source = json.loads(expected_text), json.loads(source_text)
        if not isinstance(expected, dict) or not isinstance(source, dict):
            return []
        if expected == source:
            return []
        args = []
        for field, value in expected.items():
            if isinstance(value, list):
                for row in value:
                    keys = [key for key in ("id", "task_id", "criterion_id")
                            if isinstance(row, dict) and isinstance(row.get(key), str)]
                    if len(keys) != 1:
                        raise RuntimeError(f"cannot identify selected {field} record in {path}")
                    args.extend(("--select", f"{field}.{keys[0]}={row[keys[0]]}"))
            elif isinstance(value, dict) and value:
                for key in value:
                    args.extend(("--map-entry", f"{field}={key}"))
            else:
                args.extend(("--include", field))
        return args

    baseline = capture_baseline(root)
    manifest = json.loads((root / MANIFEST_PATH).read_text())
    encoding = _tokenizer(manifest)
    originals = {row["path"]: _git_blob(root, EXPECTED_BASELINE_SOURCE, row["path"])
                 for row in manifest["files"]}
    source_texts = {path: raw.decode("utf-8") for path, raw in originals.items()}
    candidate_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    journeys, lookup_map, responses, query_index = [], {}, {}, {}
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
            for side in ("baseline", "candidate"):
                write(output / side / "legacy-inputs" / path, raw)
            if next(row for row in manifest["files"] if row["path"] == path)["metadata"]:
                write(output / "baseline/generated" / path, raw)
        for owner in sorted(owners):
            path = Path("work") / owner / "references/integrity.json"
            write(output / "candidate/generated" / path, (candidate / path).read_bytes())

        for before in baseline["journeys"]:
            for source in before["source_inputs"]:
                path = source["path"]
                selection = projection_args(path, source["text"], source_texts[path])
                query = {"reference": lookup_map[path],
                         "arguments": [*selection, "--payload-only"]}
                previous = query_index.setdefault(path, query)
                if previous != query:
                    raise RuntimeError(f"frozen journeys require different lookups for {path}")
        write(output / "candidate/generated/lookup-index.json", json_bytes(query_index))

        for path, query in query_index.items():
            stream = io.StringIO()
            with contextlib.redirect_stdout(stream):
                code = refs(["show", query["reference"], *query["arguments"]], root=candidate)
            if code:
                raise RuntimeError(f"public lookup failed: {path}: {stream.getvalue()}")
            responses[path] = stream.getvalue()
            write(output / "candidate/generated/responses" / path,
                  responses[path].encode())

        for before in baseline["journeys"]:
            parts = ["Question:\n" + before["question"]]
            equivalent = True
            selected = {source["path"]: lookup_map[source["path"]] for source in before["source_inputs"]}
            parts.append("Lookup index:\n" + json_bytes(selected).decode())
            for source in before["source_inputs"]:
                path = source["path"]
                if path.endswith(".json"):
                    equivalent &= json.loads(responses[path], parse_float=Decimal) == json.loads(
                        source["text"], parse_float=Decimal)
                else:
                    equivalent &= responses[path] == source["text"]
                selection = projection_args(path, source["text"], source_texts[path])
                request = shlex.join(["refs", "show", lookup_map[path], *selection, "--payload-only"])
                parts.append(f"Request: {request}\nResponse:\n{responses[path]}")
            transcript = "\n\n".join(parts)
            write(output / "transcripts" / (before["id"] + "-baseline.txt"), before["transcript"].encode())
            write(output / "transcripts" / (before["id"] + "-candidate.txt"), transcript.encode())
            tokens = len(encoding.encode_ordinary(transcript))
            journeys.append({"id": before["id"], "equivalent_evidence": bool(equivalent),
                "baseline_tokens": before["input_tokens"], "candidate_tokens": tokens,
                "token_regression": tokens > before["input_tokens"]})

    files, non_json_files, totals = {}, {}, {}
    for side in ("baseline", "candidate"):
        files[side] = [{"path": str(path.relative_to(output / side)), "bytes": path.stat().st_size,
                        "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                       for path in sorted((output / side).rglob("*.json"))]
        non_json_files[side] = [{"path": str(path.relative_to(output / side)), "bytes": path.stat().st_size,
                                 "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
                                for path in sorted((output / side).rglob("*"))
                                if path.is_file() and path.suffix != ".json"]
        totals[side] = {"agent_input_tokens": sum(j[side + "_tokens"] for j in journeys),
                        "metadata_bytes": sum(row["bytes"] for row in files[side]),
                        "non_json_bytes": sum(row["bytes"] for row in non_json_files[side])}
    passed = (all(j["equivalent_evidence"] for j in journeys) and
              all(totals["candidate"][unit] < totals["baseline"][unit]
                  for unit in ("agent_input_tokens", "metadata_bytes")))
    report = {"schema": "ask-reference-savings/v1", "status": "pass" if passed else "fail",
        "candidate_sha": candidate_sha, "baseline_source": EXPECTED_BASELINE_SOURCE,
        "workload_version": baseline["workload_version"], "tokenizer": baseline["tokenizer"],
        "journeys": journeys, "totals": totals, "metadata_files": files,
        "non_json_files": non_json_files,
        "scope": "Three frozen journeys with verified source reads and selective top-level JSON item projections; original outcomes and source identities preserved.",
        "full_value_exceptions": ["Immutable legacy originals, catalog digests and exact source commits remain full values."],
        "accounting": "Every public response and lookup-index input is counted. Equal immutable JSON archives are included on both sides; generated catalogs and response JSON are included once per output path. Prose and logs remain in the raw transcripts."}
    write(output / "report.json", json_bytes(report))
    print(json.dumps({key: report[key] for key in ("status", "journeys", "totals")}, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
