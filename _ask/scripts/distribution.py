#!/usr/bin/env python3
"""Validate pinned skill sources and prepare them only after user approval."""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

PINS_SHA256 = "8b08246a80fd26530481faf3f919fe0bcfa4eb7b1839de162277bf2eff9b3ba7"

SHA = re.compile(r"^[0-9a-f]{40}$")
SKILL_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]*$")


class DistributionError(ValueError):
    pass


def read_manifest(path: Path) -> list[dict]:
    entries: list[dict] = []
    current: dict | None = None
    allowed = {"source", "revision", "skill", "role", "required"}
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#") or line.strip() == "skills:":
            continue
        item = re.fullmatch(r"  ([A-Za-z0-9_-]+):\s*", line)
        field = re.fullmatch(r"    ([a-z_-]+):\s*(.*?)\s*", line)
        if item:
            if current is not None:
                entries.append(current)
            current = {"id": item.group(1)}
        elif field and current is not None:
            key, value = field.groups()
            if key not in allowed or key in current:
                raise DistributionError(f"{path}:{number}: unexpected or duplicate field")
            value = value.strip().strip("\"'")
            if key == "required":
                if value.lower() not in {"true", "false", "yes", "no", "1", "0"}:
                    raise DistributionError(f"{path}:{number}: invalid required flag")
                current[key] = value.lower() in {"true", "yes", "1"}
            else:
                current[key] = value
        else:
            raise DistributionError(f"{path}:{number}: unsupported manifest syntax")
    if current is not None:
        entries.append(current)
    if not entries:
        raise DistributionError(f"{path}: no skills entries found")

    seen: set[str] = set()
    for entry in entries:
        skill = entry.get("skill", entry["id"])
        source = entry.get("source", "")
        revision = entry.get("revision", "")
        tag = revision.removeprefix("refs/tags/")
        if not SHA.fullmatch(revision) and (tag.lower() == "latest" or subprocess.run(
                ["git", "check-ref-format", f"refs/tags/{tag}"], capture_output=True).returncode):
            raise DistributionError(
                f"invalid revision for skill {entry['id']}: expected a Git tag or full commit SHA, got {revision!r}")
        if (entry["id"] in seen or not SKILL_ID.fullmatch(skill) or skill.startswith("kit-")
                or not source or source.startswith("-") or "#" in source
                or re.search(r"[\s\x00-\x1f]", source)):
            raise DistributionError(f"invalid source identity for skill {entry['id']}")
        entry["skill"] = skill
        seen.add(entry["id"])
    return entries


def read_pins(path: Path) -> dict:
    try:
        raw = path.read_bytes()
        pins = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise DistributionError(f"cannot read dependency pins: {exc}") from exc
    if hashlib.sha256(raw).hexdigest() != PINS_SHA256:
        raise DistributionError("dependency pin record does not match this installed release")
    if not isinstance(pins, dict) or pins.get("schema") != "ask-dependency-pins/v1":
        raise DistributionError("unsupported dependency pin schema")
    packages = pins.get("packages")
    if not isinstance(packages, dict):
        raise DistributionError("dependency package pins are missing")
    cli, tracker = packages.get("skills"), packages.get("mcp-atlassian")
    if not isinstance(cli, dict) or not isinstance(tracker, dict):
        raise DistributionError("dependency package pins are missing")
    if (not re.fullmatch(r"\d+\.\d+\.\d+", str(cli.get("version", "")))
            or not SHA.fullmatch(str(cli.get("source_commit", "")))
            or cli.get("node") != ">=18"
            or not re.fullmatch(r"sha512-[A-Za-z0-9+/]+={0,2}", str(cli.get("integrity", "")))
            or cli.get("tarball") != f"https://registry.npmjs.org/skills/-/skills-{cli.get('version')}.tgz"
            or not re.fullmatch(r"\d+\.\d+\.\d+", str(tracker.get("version", "")))
            or not SHA.fullmatch(str(tracker.get("source_commit", "")))
            or not SHA.fullmatch(str(tracker.get("source_tree", "")))
            or not re.fullmatch(r"[0-9a-f]{64}", str(tracker.get("wheel_sha256", "")))):
        raise DistributionError("dependency pin lacks an exact source or artifact identity")
    skills = pins.get("skills")
    if not isinstance(skills, dict) or not skills:
        raise DistributionError("skill source identities are missing")
    for name, item in skills.items():
        if (not isinstance(item, dict) or item.get("skill") != name
                or not SHA.fullmatch(str(item.get("commit", "")))
                or not SHA.fullmatch(str(item.get("tree", "")))
                or not re.fullmatch(r"[0-9a-f]{64}", str(item.get("skill_sha256", "")))
                or not isinstance(item.get("path"), str)
                or not item["path"].endswith("SKILL.md")):
            raise DistributionError(f"invalid pinned skill identity: {name}")
    return pins


def approval_path(root: Path) -> Path:
    config = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config").expanduser().absolute()
    if config == root or root in config.parents or any(
            part.is_symlink() for part in (config, *config.parents) if part != part.parent):
        raise DistributionError("skill approvals must use a nonsymlink path outside the project")
    config = config.resolve()
    if config == root or root in config.parents:
        raise DistributionError("skill approvals must be stored outside the project")
    return config / "askit" / "skill-source-approvals.json"


def validate_approval_dir(directory: Path, *, create: bool = False) -> None:
    if create:
        directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    if directory.is_symlink() or not directory.is_dir():
        raise DistributionError("skill approval directory must be a regular directory")
    info = directory.stat()
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
        raise DistributionError("skill approval directory must be private and owned by the current user")


def load_approvals(path: Path) -> list[dict]:
    if path.parent.exists():
        validate_approval_dir(path.parent)
    if not path.exists():
        return []
    if path.is_symlink() or not path.is_file():
        raise DistributionError("skill approval record must be a regular user-owned file")
    info = path.stat()
    if info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) & 0o077:
        raise DistributionError("skill approval record must be private and owned by the current user")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DistributionError(f"cannot read skill approval record: {exc}") from exc
    if (not isinstance(data, dict) or data.get("schema") != "askit-skill-source-approvals/v1"
            or not isinstance(data.get("approvals"), list)):
        raise DistributionError("invalid skill approval record")
    return data["approvals"]


def save_approvals(path: Path, approvals: list[dict]) -> None:
    validate_approval_dir(path.parent, create=True)
    if path.exists() and (path.is_symlink() or not path.is_file()):
        raise DistributionError("skill approval record must be a regular file")
    content = json.dumps({"schema": "askit-skill-source-approvals/v1", "approvals": approvals},
                         indent=2).encode() + b"\n"
    fd, name = tempfile.mkstemp(prefix=".approvals-", dir=path.parent)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def source_url(source: str) -> str:
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", source):
        return f"https://github.com/{source}.git"
    if source.startswith(("/", "./", "../", "~")):
        return str(Path(source).expanduser())
    return source


def git(args: list[str], *, cwd: Path | None = None) -> str:
    result = subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True)
    if result.returncode:
        raise DistributionError(result.stderr.strip() or "git source resolution failed")
    return result.stdout.strip()


def resolve_tag(source: str, tag: str) -> str:
    ref = f"refs/tags/{tag}"
    peeled = ref + "^{}"
    output = git(["ls-remote", "--tags", "--", source_url(source), ref, peeled])
    refs = {name: sha for sha, name in (line.split("\t", 1) for line in output.splitlines())}
    commit = refs.get(peeled, refs.get(ref, ""))
    if not SHA.fullmatch(commit):
        raise DistributionError(f"tag {tag!r} was not found at {source}")
    return commit


def verified_source(entry: dict, pins: dict, path: Path) -> Path:
    git(["clone", "--no-checkout", "--no-tags", source_url(entry["source"]), str(path)])
    git(["fetch", "--no-tags", "origin", entry["revision"]], cwd=path)
    git(["checkout", "--detach", entry["revision"]], cwd=path)
    actual = git(["rev-parse", "--verify", "HEAD"], cwd=path)
    if actual != entry["revision"] or git(["status", "--porcelain", "--untracked-files=all"], cwd=path):
        raise DistributionError(f"skill source did not resolve cleanly to {entry['revision']}")
    pin = pins["skills"].get(entry["id"])
    if pin and (entry["source"], entry["revision"], entry["skill"]) == (
            pin["source"], pin["commit"], pin["skill"]):
        tree = git(["rev-parse", "HEAD^{tree}"], cwd=path)
        skill = path / pin["path"]
        if (tree != pin["tree"] or not skill.is_file()
                or hashlib.sha256(skill.read_bytes()).hexdigest() != pin["skill_sha256"]):
            raise DistributionError(f"reviewed skill content mismatch for {entry['id']}")
    return path


def trusted_executable(name: str, root: Path) -> Path:
    for directory in os.environ.get("PATH", os.defpath).split(os.pathsep):
        candidate = Path(directory or ".") / name
        if not candidate.is_file() or not os.access(candidate, os.X_OK):
            continue
        resolved = candidate.resolve()
        if resolved == root or root in resolved.parents:
            continue
        return resolved
    raise DistributionError(f"{name} executable not found outside the project")


def install_skills_cli(pins: dict, root: Path, directory: Path) -> tuple[Path, Path, dict[str, str]]:
    cli = pins["packages"]["skills"]
    directory.mkdir(mode=0o700, parents=True)
    with urllib.request.urlopen(cli["tarball"], timeout=60) as response:
        if urllib.parse.urlparse(response.geturl()).hostname != "registry.npmjs.org":
            raise DistributionError("skills CLI download redirected outside the npm registry")
        archive = response.read()
    if base64.b64encode(hashlib.sha512(archive).digest()).decode() != cli["integrity"].removeprefix("sha512-"):
        raise DistributionError("skills CLI artifact integrity mismatch")

    tarball = directory / f"skills-{cli['version']}.tgz"
    tarball.write_bytes(archive)
    (directory / "package.json").write_text("{}\n", encoding="utf-8")
    user_config = directory / "user.npmrc"
    global_config = directory / "global.npmrc"
    user_config.write_text("\n", encoding="utf-8")
    global_config.write_text("\n", encoding="utf-8")
    env = {key: value for key, value in os.environ.items()
           if not key.upper().startswith("NPM_CONFIG_") and key != "NODE_OPTIONS"}
    env["PATH"] = os.pathsep.join(
        part for part in env.get("PATH", os.defpath).split(os.pathsep)
        if (Path(part or ".").resolve() != root and root not in Path(part or ".").resolve().parents)
    )
    npm = trusted_executable("npm", root)
    result = subprocess.run(
        [str(npm), "install", "--ignore-scripts", "--no-save", "--package-lock=false",
         "--no-audit", "--no-fund", "--registry=https://registry.npmjs.org",
         f"--userconfig={user_config}", f"--globalconfig={global_config}", str(tarball)],
        cwd=directory, env=env, text=True, capture_output=True,
    )
    if result.returncode:
        raise DistributionError("could not install the verified skills CLI artifact")
    package = directory / "node_modules/skills"
    metadata = json.loads((package / "package.json").read_text(encoding="utf-8"))
    command = metadata.get("bin", {}).get("skills") if isinstance(metadata.get("bin"), dict) else metadata.get("bin")
    if metadata.get("version") != cli["version"] or not isinstance(command, str):
        raise DistributionError("installed skills CLI does not match its reviewed package pin")
    executable = (package / command).resolve()
    if package.resolve() not in executable.parents or not executable.is_file():
        raise DistributionError("skills CLI entry point escapes its verified package")
    return trusted_executable("node", root), executable, env


def confirm_source(prompt: str) -> None:
    if not sys.stdin.isatty():
        raise DistributionError("new skill source or revision requires interactive approval")
    try:
        answer = input(prompt).strip().lower()
    except EOFError:
        answer = ""
    if answer not in {"y", "yes"}:
        raise DistributionError("skill source was not approved")


def approve_sources(entries: list[dict], pins: dict, root: Path, *, validate_only: bool) -> list[dict]:
    path = approval_path(root)
    approvals = load_approvals(path)
    known_sources = {record.get("source") for record in [*pins["skills"].values(), *approvals]}
    resolved_tags: dict[tuple[str, str], str] = {}
    resolved_entries = []
    for entry in entries:
        source, revision, skill = (entry[key] for key in ("source", "revision", "skill"))
        tag = None
        if not SHA.fullmatch(revision):
            if validate_only:
                resolved_entries.append(entry)
                continue
            tag = revision.removeprefix("refs/tags/")
            if source not in known_sources:
                print(f"New skill source for tag lookup: {source} @ {tag}")
                confirm_source("Approve contacting this source? [y/N] ")
                known_sources.add(source)
            key = (source, tag)
            if key not in resolved_tags:
                resolved_tags[key] = resolve_tag(source, tag)
            revision = resolved_tags[key]

        identity = {"source": source, "revision": revision, "skill": skill}
        pinned = pins["skills"].get(entry["id"])
        bundled = pinned and (source, revision, skill) == (pinned["source"], pinned["commit"], pinned["skill"])
        approved = bundled or any(all(record.get(key) == value for key, value in identity.items())
                                  for record in approvals)
        previous = next((record for record in approvals if tag is not None
                         and (record.get("source"), record.get("tag"), record.get("skill")) == (source, tag, skill)), None)
        moved = previous is not None and previous["revision"] != revision
        if moved:
            print(f"Skill tag moved: {source} @ {tag} from {previous['revision']} to {revision} --skill {skill}")
        elif not approved:
            print(f"New skill source fetch: {source} @ {revision} --skill {skill}")
        if moved or not approved:
            confirm_source("Approve this source and commit? [y/N] ")

        if tag is not None and (previous is None or moved):
            if previous is not None:
                approvals.remove(previous)
            approvals.append(dict(identity, tag=tag))
            save_approvals(path, approvals)
        elif not approved:
            approvals.append(identity)
            save_approvals(path, approvals)
        known_sources.add(source)
        resolved_entries.append(dict(entry, revision=revision))
    return resolved_entries


def apply_tdd_override(root: Path) -> None:
    start, end = "<!-- ASK TDD OVERRIDE START -->", "<!-- ASK TDD OVERRIDE END -->"
    override = root / "_ask/skills/tdd-override.md"
    if not override.is_file():
        raise DistributionError(f"missing repository TDD override: {override}")
    block = f"{start}\n{override.read_text(encoding='utf-8').strip()}\n{end}"
    views = [root / ".agents/skills/tdd/SKILL.md"]
    cursor_view = root / ".cursor/skills/tdd/SKILL.md"
    if cursor_view.exists():
        views.append(cursor_view)
    for path in views:
        if not path.is_file():
            raise DistributionError(f"missing prepared TDD skill view: {path}")
        content = path.read_text(encoding="utf-8")
        starts, ends = content.count(start), content.count(end)
        if starts != ends or starts > 1:
            raise DistributionError(f"malformed or duplicate TDD override markers in {path}")
        if starts:
            content = re.sub(re.escape(start) + r".*?" + re.escape(end), "", content,
                             count=1, flags=re.S).rstrip()
        updated = content.rstrip() + "\n\n" + block + "\n"
        if updated != path.read_text(encoding="utf-8"):
            path.write_text(updated, encoding="utf-8")


def prepare(root: Path, manifest: Path, pin_path: Path, installer=None, source_resolver=None) -> int:
    pins = read_pins(pin_path)
    entries = read_manifest(manifest)
    bundled = read_manifest(root / "_ask/skills/manifest.yaml")
    if set(pins["skills"]) != {entry["id"] for entry in bundled}:
        raise DistributionError("bundled manifest and reviewed skill identities do not match")
    for entry in entries:
        for destination in (
            root / ".agents/skills" / entry["skill"],
            root / ".cursor/skills" / entry["skill"],
        ):
            if any(path.is_symlink() for path in (
                    destination.parents[1], destination.parent, destination,
                    destination / "SKILL.md")):
                raise DistributionError(f"skill destination cannot contain symlinks: {destination}")
    validate_only = os.environ.get("SKIP_INSTALL") == "1"
    entries = approve_sources(entries, pins, root, validate_only=validate_only)
    if validate_only:
        for entry in entries:
            print(f"prepare-skills: validated {entry['id']} @ {entry['revision']}")
        return 0

    from client_ignores import BEGIN, update
    ignore = root / ".gitignore"
    if ignore.is_file() and BEGIN in ignore.read_bytes().splitlines():
        update(root, root)

    failed = False
    with tempfile.TemporaryDirectory(prefix="askit-skills-") as temporary:
        temporary = Path(temporary)
        cli = None if installer else install_skills_cli(pins, root, temporary / "cli")
        sources: dict[tuple[str, str], Path] = {}
        for entry in entries:
            key = (entry["source"], entry["revision"])
            try:
                source = sources.get(key)
                if source is None:
                    resolve = source_resolver or verified_source
                    source = resolve(entry, pins, temporary / f"source-{len(sources)}")
                    sources[key] = source
                if installer:
                    result = installer(entry, source)
                else:
                    node, executable, env = cli
                    command = [str(node), str(executable), "add", str(source),
                               "--skill", entry["skill"], "--agent", "cursor", "--yes"]
                    print("prepare-skills:", " ".join(command))
                    result = subprocess.run(command, cwd=root, env=env)
            except (OSError, DistributionError) as exc:
                print(f"prepare-skills: {exc}", file=sys.stderr)
                failed |= entry.get("required", False)
                continue
            primary = root / ".agents/skills" / entry["skill"] / "SKILL.md"
            if result.returncode:
                print(f"prepare-skills: installer failed for {entry['id']} (exit {result.returncode})",
                      file=sys.stderr)
                failed |= entry.get("required", False)
                continue
            if entry.get("required", False) and not primary.is_file():
                print(f"prepare-skills: missing required primary skill output for {entry['id']}",
                      file=sys.stderr)
                failed = True
                continue
            if entry["skill"] == "tdd":
                try:
                    apply_tdd_override(root)
                except (OSError, DistributionError) as exc:
                    print(f"prepare-skills: {exc}", file=sys.stderr)
                    failed = True
                    continue
            print(f"prepare-skills: ok {entry['skill']} @ {entry['revision']}")
    if failed:
        return 1
    print("prepare-skills: summary complete")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--pins", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        return prepare(args.root.resolve(), args.manifest.resolve(), args.pins.resolve())
    except (OSError, DistributionError) as exc:
        print(f"prepare-skills: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
