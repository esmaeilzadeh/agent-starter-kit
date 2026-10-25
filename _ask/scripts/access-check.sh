#!/usr/bin/env bash
# Probe local write access without leaving files behind.
set -euo pipefail

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "access-check: not inside a Git worktree" >&2
  exit 2
fi

ROOT="$(git rev-parse --show-toplevel)"
resolve_from_root() {
  case "$1" in
    /*) printf '%s\n' "$1" ;;
    *) printf '%s/%s\n' "$ROOT" "$1" ;;
  esac
}

probe_dir() {
  local dir="$1" label="$2" probe
  if [[ ! -d "$dir" ]]; then
    echo "access-check: $label directory is missing: $dir" >&2
    return 1
  fi
  if ! probe="$(mktemp "$dir/.ask-access-check.XXXXXX" 2>/dev/null)"; then
    echo "access-check: cannot write to $label directory: $dir; restore write access and retry" >&2
    return 1
  fi
  if ! printf 'access-check\n' >"$probe"; then
    if ! rm -f -- "$probe"; then
      echo "access-check: cannot write to $label directory: $dir; leftover probe: $probe" >&2
    else
      echo "access-check: cannot write to $label directory: $dir; restore write access and retry" >&2
    fi
    return 1
  fi
  if ! rm -f -- "$probe"; then
    echo "access-check: cannot clean up probe in $label directory: $dir; leftover probe: $probe" >&2
    return 1
  fi
}

git_dir="$(resolve_from_root "$(git rev-parse --git-dir)")"
common_dir="$(resolve_from_root "$(git rev-parse --git-common-dir)")"
workspace_dir="$ROOT"
[[ -d "$ROOT/work" ]] && workspace_dir="$ROOT/work"

for item in "worktree Git metadata:$git_dir" "shared Git metadata:$common_dir" "workspace:$workspace_dir"; do
  label="${item%%:*}"
  dir="${item#*:}"
  probe_dir "$dir" "$label" || exit 1
done

echo "access-check: Git metadata and workspace are writable"
