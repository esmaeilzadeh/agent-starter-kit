#!/usr/bin/env python3
"""Manage tracker settings and private credentials without shell evaluation."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import urlsplit


PUBLIC_KEYS = {"ASK_TRACKER", "ASK_TRACKER_URL", "JIRA_URL", "ASK_EPIC", "ASK_STORY",
               "MEMORY_CHOICE", "MEMORY_CMD", "MEMORY_PATH"}
SECRET_KEYS = {"GITHUB_TOKEN", "JIRA_PERSONAL_TOKEN"}
ALL_KEYS = PUBLIC_KEYS | SECRET_KEYS
PUBLIC_JSON_KEYS = {"tracker", "url", *(key.lower() for key in PUBLIC_KEYS)}
BASE_ENV = {"PATH", "HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "LC_CTYPE", "TZ", "TMPDIR"}


class ConfigError(ValueError):
    pass


def git_root(path: Path) -> Path:
    result = subprocess.run(["git", "-C", str(path), "rev-parse", "--show-toplevel"],
                            capture_output=True, text=True)
    if result.returncode:
        raise ConfigError("project root must be a Git checkout")
    return Path(result.stdout.strip()).resolve()


def canonical_root(value: str) -> Path:
    root = Path(value).resolve(strict=True)
    if git_root(root) != root:
        raise ConfigError("project root must be a Git checkout root")
    return root


def check_components(path: Path, *, allow_missing: bool = False) -> None:
    path = Path(os.path.abspath(path))
    current = Path(path.anchor)
    for part in path.parts[1:]:
        current /= part
        try:
            info = current.lstat()
        except FileNotFoundError:
            if allow_missing:
                continue
            raise ConfigError("path does not exist") from None
        if stat.S_ISLNK(info.st_mode):
            raise ConfigError("path contains a symlink")
        if current != path and not stat.S_ISDIR(info.st_mode):
            raise ConfigError("path component is not a directory")


def validate_url(value: str) -> str:
    try:
        parsed = urlsplit(value)
        valid = (parsed.scheme == "https" and bool(parsed.hostname)
                 and parsed.username is None and parsed.password is None
                 and not any(ord(ch) < 32 for ch in value))
    except ValueError:
        valid = False
    if not valid:
        raise ConfigError("tracker URL rejected; use HTTPS without credentials")
    return value.rstrip("/")


def parse_legacy(text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for number, line in enumerate(text.splitlines(), 1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("export "):
            stripped = stripped[7:].lstrip()
        match = re.fullmatch(r"([A-Z][A-Z0-9_]*)=(.*)", stripped)
        if not match or match.group(1) not in ALL_KEYS:
            raise ConfigError(f"unsupported legacy setting at line {number}")
        key, raw = match.groups()
        if raw.startswith("'"):
            if len(raw) < 2 or raw[-1] != "'" or "'" in raw[1:-1]:
                raise ConfigError(f"unsupported legacy setting at line {number}")
            value = raw[1:-1]
        elif raw.startswith('"'):
            if len(raw) < 2 or raw[-1] != '"':
                raise ConfigError(f"unsupported legacy setting at line {number}")
            value = re.sub(r'\\([\\"])', r"\1", raw[1:-1])
            if re.search(r'(?<!\\)"', value):
                raise ConfigError(f"unsupported legacy setting at line {number}")
        else:
            if any(ch.isspace() or ch in "'\"`;&|<>\\" for ch in raw):
                raise ConfigError(f"unsupported legacy setting at line {number}")
            value = raw
        if any(ch in value for ch in "\x00\n\r"):
            raise ConfigError(f"unsupported legacy setting at line {number}")
        values[key] = value
    return values


def credential_path(root: Path) -> Path:
    config = Path(os.environ.get("XDG_CONFIG_HOME", str(Path.home() / ".config"))).expanduser()
    if not config.is_absolute():
        raise ConfigError("XDG_CONFIG_HOME must be absolute")
    check_components(config)
    if not config.is_dir() or config.stat().st_uid != os.getuid():
        raise ConfigError("XDG_CONFIG_HOME must be an owned directory")
    key = hashlib.sha256(str(root).encode()).hexdigest()
    current = config
    for part in ("askit", "projects", key):
        current = current / part
        if not current.exists():
            try:
                current.mkdir(mode=0o700)
            except FileExistsError:
                pass
        info = current.lstat()
        if (stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode)
                or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o700):
            raise ConfigError("private credential directory is unsafe")
    return current / "credentials.json"


def atomic_write(path: Path, data: bytes, mode: int) -> None:
    fd, temporary = tempfile.mkstemp(prefix=".tracker-", dir=path.parent)
    try:
        os.fchmod(fd, mode)
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        directory = os.open(path.parent, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def private_write(path: Path, data: bytes) -> None:
    if path.exists() or path.is_symlink():
        info = path.lstat()
        if (stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode)
                or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600):
            raise ConfigError("private credential file is unsafe")
    atomic_write(path, data, 0o600)


def read_credentials(root: Path) -> dict:
    path = credential_path(root)
    if not path.exists():
        raise ConfigError("tracker credentials are not configured")
    info = path.lstat()
    if (stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.getuid() or stat.S_IMODE(info.st_mode) != 0o600):
        raise ConfigError("private credential file is unsafe")
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        raise ConfigError("private credential file is invalid") from None
    if (not isinstance(data, dict) or data.get("schema") != "askit-tracker-credentials/v1"
            or not isinstance(data.get("credentials"), dict)):
        raise ConfigError("private credential file is invalid")
    return data


def project_write(root: Path, relative: str, data: bytes) -> None:
    path = root / relative
    check_components(path.parent, allow_missing=True)
    path.parent.mkdir(parents=True, exist_ok=True)
    check_components(path.parent)
    if path.exists() or path.is_symlink():
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise ConfigError("project settings path is unsafe")
        mode = stat.S_IMODE(info.st_mode)
    else:
        mode = 0o644
    atomic_write(path, data, mode)


def store(project_root: Path, credential_root: Path, record: dict) -> None:
    if not isinstance(record, dict):
        raise ConfigError("tracker settings are invalid")
    tracker = record.get("tracker")
    if tracker not in {"jira", "github", "gitlab", "none"}:
        raise ConfigError("tracker type is invalid")
    url = validate_url(record.get("url", "")) if tracker != "none" else ""
    credentials = record.get("credentials", {})
    if (not isinstance(credentials, dict)
            or any(key not in SECRET_KEYS or not isinstance(value, str)
                   for key, value in credentials.items())):
        raise ConfigError("tracker credentials are invalid")
    payload = {"schema": "askit-tracker-credentials/v1", "tracker": tracker,
               "url": url, "credentials": credentials}
    private_write(credential_path(credential_root),
                  (json.dumps(payload, sort_keys=True, indent=2) + "\n").encode())
    path = project_root / ".agents/ask.local/tracker.json"
    if path.exists() or path.is_symlink():
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
            raise ConfigError("project settings path is unsafe")
        try:
            public = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raise ConfigError("project tracker settings are invalid") from None
        if not isinstance(public, dict):
            raise ConfigError("project tracker settings are invalid")
        public = {key: value for key, value in public.items()
                  if key in PUBLIC_JSON_KEYS and isinstance(value, str)}
    else:
        public = {}
    public.update(tracker=tracker, url=url)
    settings = record.get("settings", {})
    if not isinstance(settings, dict) or any(key not in PUBLIC_KEYS or not isinstance(value, str)
                                            for key, value in settings.items()):
        raise ConfigError("tracker settings are invalid")
    public.update({key.lower(): value for key, value in settings.items()})
    project_write(project_root, ".agents/ask.local/tracker.json",
                  (json.dumps(public, sort_keys=True, indent=2) + "\n").encode())


def transactional(root: Path, outputs: list[str], inputs: list[str], command: list[str]) -> int:
    helper = root / "_ask/scripts/write-transaction.py"
    args = [sys.executable, str(helper), "run", "--root", str(root)]
    for path in outputs:
        args.extend(["--path", path])
    for path in inputs:
        args.extend(["--input-path", path])
    return subprocess.run([*args, "--", *command], cwd=root).returncode


def migrate(args: argparse.Namespace) -> int:
    if not args.yes:
        raise ConfigError("migration requires explicit --yes confirmation")
    root = canonical_root(args.root)
    legacy_path = root / ".ask.env"
    check_components(legacy_path)
    info = legacy_path.lstat()
    if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode):
        raise ConfigError("legacy settings path is unsafe")
    history_risk = (subprocess.run(["git", "-C", str(root), "ls-files", "--error-unmatch", "--", ".ask.env"],
                                   capture_output=True).returncode == 0)
    staged = subprocess.run(["git", "-C", str(root), "diff", "--cached", "--quiet", "--", ".ask.env"]).returncode == 1
    before = legacy_path.read_bytes()
    text = before.decode("utf-8")
    values = parse_legacy(text)
    tracker = values.get("ASK_TRACKER", "jira").lower()
    url = values.get("ASK_TRACKER_URL", values.get("JIRA_URL", ""))
    secrets = {key: values[key] for key in SECRET_KEYS if values.get(key)}
    store(root, root,
          {"tracker": tracker, "url": url, "credentials": secrets,
           "settings": {key: value for key, value in values.items() if key in PUBLIC_KEYS}})
    current = legacy_path.lstat()
    if (stat.S_ISLNK(current.st_mode) or not stat.S_ISREG(current.st_mode)
            or legacy_path.read_bytes() != before):
        raise ConfigError("legacy settings changed during migration; credential copy is safe, source was retained")
    cleaned = "".join(line for line in text.splitlines(keepends=True)
                      if not re.match(r"^\s*(?:export\s+)?(?:GITHUB_TOKEN|JIRA_PERSONAL_TOKEN)=", line))
    atomic_write(legacy_path, cleaned.encode("utf-8"), stat.S_IMODE(info.st_mode))
    if history_risk or staged:
        print("warning: legacy credentials may remain in Git history; credential rotation is recommended. No index or history was changed.")
    print("credentials migrated to private storage; secret assignments removed from the working file")
    return 0


def merge_mcp(path: Path, name: str, spec: dict | None) -> None:
    check_components(path.parent)
    if path.parent.stat().st_uid != os.getuid():
        raise ConfigError("MCP configuration directory is not owned by the current user")
    if path.exists() or path.is_symlink():
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode) or info.st_uid != os.getuid():
            raise ConfigError("MCP configuration path is unsafe")
        mode = stat.S_IMODE(info.st_mode)
        try:
            data = json.loads(path.read_text(encoding="utf-8") or "{}")
        except (OSError, json.JSONDecodeError):
            raise ConfigError("MCP configuration is invalid") from None
    else:
        mode, data = 0o600, {}
    if not isinstance(data, dict) or not isinstance(data.setdefault("mcpServers", {}), dict):
        raise ConfigError("MCP configuration is invalid")
    if spec is None:
        data["mcpServers"].pop(name, None)
    else:
        data["mcpServers"][name] = spec
    atomic_write(path, (json.dumps(data, sort_keys=True, indent=2) + "\n").encode(), mode)


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    url = sub.add_parser("validate-url")
    url.add_argument("value", nargs="?")
    url.add_argument("--stdin", action="store_true")
    legacy = sub.add_parser("validate-legacy")
    legacy.add_argument("file")
    save = sub.add_parser("store")
    save.add_argument("--root", required=True)
    save.add_argument("--stdin-fields", action="store_true")
    context = sub.add_parser("context")
    context.add_argument("--root", required=True)
    context.add_argument("--stdin", action="store_true")
    migration = sub.add_parser("migrate")
    migration.add_argument("--root", required=True)
    migration.add_argument("--yes", action="store_true")
    mcp = sub.add_parser("mcp")
    mcp.add_argument("--root", required=True)
    mcp.add_argument("--config", required=True)
    mcp.add_argument("--opt-in", choices={"yes", "no"}, required=True)
    merge = sub.add_parser("merge-mcp")
    merge.add_argument("--config", required=True)
    merge.add_argument("--name", required=True)
    args = parser.parse_args()
    try:
        if args.action == "validate-url":
            validate_url(sys.stdin.read() if args.stdin else (args.value or ""))
            print("valid tracker URL")
        elif args.action == "validate-legacy":
            path = Path(args.file)
            check_components(path)
            if path.is_symlink() or not path.is_file():
                raise ConfigError("legacy settings path is unsafe")
            parse_legacy(path.read_text(encoding="utf-8"))
            print("valid legacy settings")
        elif args.action == "store":
            project_root = canonical_root(args.root)
            if args.stdin_fields:
                fields = sys.stdin.buffer.read().split(b"\0")
                if len(fields) != 4 or fields[-1] != b"":
                    raise ConfigError("tracker input is invalid")
                tracker, url_value, token = (field.decode("utf-8") for field in fields[:3])
                secret_key = "GITHUB_TOKEN" if tracker == "github" else "JIRA_PERSONAL_TOKEN"
                record = {"tracker": tracker, "url": url_value,
                          "credentials": {secret_key: token} if token and tracker in {"jira", "github"} else {}}
            else:
                record = json.load(sys.stdin)
            store(project_root, project_root, record)
            print("tracker settings saved; credentials stored privately")
        elif args.action == "context":
            if os.environ.get("ASKIT_TRANSACTION_ACTIVE") != "1":
                root = canonical_root(args.root)
                return transactional(root, [".ask/tracker-context.md"], ["_ask/scripts"], [
                    sys.executable, "{target}/_ask/scripts/tracker-config.py", "context",
                    "--root", "{target}", "--stdin",
                ])
            record = json.load(sys.stdin)
            if not isinstance(record, dict):
                raise ConfigError("issue context is invalid")
            epic, story = record.get("epic", ""), record.get("story", "")
            if not isinstance(epic, str) or not isinstance(story, str):
                raise ConfigError("issue context is invalid")
            if any(ch in epic + story for ch in "\x00"):
                raise ConfigError("issue context is invalid")
            content = f"# Current issue (local; gitignored)\n\n- **epic:** {epic}\n- **story:** {story}\n"
            project_write(Path(args.root).resolve(), ".ask/tracker-context.md", content.encode())
        elif args.action == "migrate":
            return migrate(args)
        elif args.action == "mcp":
            root = canonical_root(args.root)
            if args.opt_in == "no":
                print("MCP configuration unchanged")
                return 0
            spec = {"command": "python3", "args": [str(root / "_ask/scripts/tracker-mcp.py"),
                                                              "--root", str(root)]}
            merge_mcp(Path(args.config).expanduser(), "askit-tracker", spec)
            print("tracker MCP configured without credentials in the MCP file")
        elif args.action == "merge-mcp":
            spec = json.load(sys.stdin)
            merge_mcp(Path(args.config).expanduser(), args.name, spec)
            print("MCP configuration updated")
        return 0
    except (ConfigError, OSError, ValueError, TypeError, json.JSONDecodeError) as error:
        print(f"tracker-config: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
