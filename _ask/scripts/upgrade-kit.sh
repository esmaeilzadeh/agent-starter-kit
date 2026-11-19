#!/usr/bin/env bash
# Refresh kit-owned files from an explicit kit version tag/sha.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VERSION=""
EXPECTED_COMMIT=""
SKIP_PREPARE=0
SOURCE_REPO="${KIT_SOURCE_REPO:-https://github.com/esmaeilzadeh/agent-starter-kit.git}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION="$2"; shift 2 ;;
    --expected-commit) EXPECTED_COMMIT="$2"; shift 2 ;;
    --target) ROOT="$(cd "$2" && pwd)"; shift 2 ;;
    --skip-prepare) SKIP_PREPARE=1; shift ;;
    --source) SOURCE_REPO="$2"; shift 2 ;;
    *) echo "usage: upgrade-kit.sh --version <tag-or-sha> [--target <consumer-repo>] [--skip-prepare] [--source <git-url>]" >&2; exit 2 ;;
  esac
done
if [[ -z "$VERSION" ]]; then
  echo "upgrade-kit: --version required (never blind main)" >&2
  exit 2
fi
if [[ -z "$EXPECTED_COMMIT" && "$VERSION" =~ ^[0-9a-f]{40}$ ]]; then
  EXPECTED_COMMIT="$VERSION"
fi
if [[ ! "$EXPECTED_COMMIT" =~ ^[0-9a-f]{40}$ ]]; then
  echo "upgrade-kit: a full expected commit is required (--expected-commit or a full-SHA --version)" >&2
  exit 2
fi

if [[ "$(git -C "$ROOT" rev-parse --show-toplevel 2>/dev/null || true)" != "$ROOT" ]]; then
  echo "upgrade-kit: target must be a Git repository root: $ROOT" >&2
  exit 2
fi

if [[ "${ASKIT_TRANSACTION_ACTIVE:-0}" != "1" ]]; then
  args=(python3 "$ROOT/_ask/scripts/write-transaction.py" run --root "$ROOT")
  for rel in \
    _ask/skills _ask/guide _ask/spec _ask/agents _ask/templates _ask/scripts \
    _ask/tests _ask/docs _ask/cursor-commands _ask/bindings _ask/OWNED-PATHS.md \
    _ask/MAPPING.md _ask/README.md .agents/ask .agents/ask.local .agents/skills \
    .cursor .codex/agents .claude/agents .opencode/agents .gitignore ask \
    ai-agent-engineering-guide.md ai-agent-starter-kit-spec.md; do
    args+=(--path "$rel")
  done
  args+=(-- bash "$ROOT/_ask/scripts/upgrade-kit.sh" --version "$VERSION" --target "{target}")
  [[ -z "$EXPECTED_COMMIT" ]] || args+=(--expected-commit "$EXPECTED_COMMIT")
  [[ "$SKIP_PREPARE" -eq 0 ]] || args+=(--skip-prepare)
  args+=(--source "$SOURCE_REPO")
  exec "${args[@]}"
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
if ! git clone --depth 1 --branch "$VERSION" "$SOURCE_REPO" "$TMP/kit" 2>/dev/null; then
  if ! git clone "$SOURCE_REPO" "$TMP/kit" \
    || ! git -C "$TMP/kit" checkout --detach "$VERSION"; then
    echo "upgrade-kit: unable to fetch selected source revision $VERSION" >&2
    exit 1
  fi
fi
ACTUAL_COMMIT="$(git -C "$TMP/kit" rev-parse --verify HEAD 2>/dev/null || true)"
if [[ "$ACTUAL_COMMIT" != "$EXPECTED_COMMIT" ]]; then
  echo "upgrade-kit: release revision mismatch (expected $EXPECTED_COMMIT, fetched $ACTUAL_COMMIT)" >&2
  exit 1
fi
if [[ -n "$(git -C "$TMP/kit" status --porcelain --untracked-files=all)" ]]; then
  echo "upgrade-kit: fetched release working tree is not clean" >&2
  exit 1
fi

# Copy legacy settings before refreshing the kit trees.
if [[ -f "$TMP/kit/_ask/scripts/copy-project-config.sh" ]]; then
  bash "$TMP/kit/_ask/scripts/copy-project-config.sh" "$ROOT" "$TMP/kit/_ask/skills/manifest.yaml"
fi

# Consumer-owned paths to preserve
preserve=(
  _ask/skills/manifest.yaml
  _ask/bindings/models.yaml
  .agents/verification.yaml
)
for p in "${preserve[@]}"; do
  if [[ -f "$ROOT/$p" ]]; then
    mkdir -p "$TMP/preserve/$(dirname "$p")"
    cp -a "$ROOT/$p" "$TMP/preserve/$p"
  fi
done

# Refresh kit-owned trees
for rel in _ask/skills _ask/guide _ask/spec _ask/agents _ask/templates _ask/scripts _ask/tests _ask/docs _ask/cursor-commands _ask/bindings .agents/ask .cursor \
           ai-agent-engineering-guide.md ai-agent-starter-kit-spec.md _ask/OWNED-PATHS.md _ask/MAPPING.md _ask/README.md ask; do
  if [[ -e "$TMP/kit/$rel" ]]; then
    mkdir -p "$ROOT/$(dirname "$rel")"
    rm -rf "$ROOT/$rel"
    cp -a "$TMP/kit/$rel" "$ROOT/$rel"
  fi
done

# Restore consumer-owned
for p in "${preserve[@]}"; do
  if [[ -f "$TMP/preserve/$p" ]]; then
    mkdir -p "$ROOT/$(dirname "$p")"
    cp -a "$TMP/preserve/$p" "$ROOT/$p"
  fi
done
# Keep *.local.md if any were wiped — restore from preserve if we saved agents locals
while IFS= read -r -d '' f; do
  rel="${f#"$ROOT/"}"
  :
done < <(find "$ROOT/_ask/agents" -name '*.local.md' -print0 2>/dev/null || true)

if [[ "$SKIP_PREPARE" -eq 0 ]]; then
  SKIP_INSTALL="${SKIP_INSTALL:-0}" "$ROOT/_ask/skills/prepare-skills.sh"
fi
python3 "$ROOT/_ask/scripts/sync-codex-skills.py" --update-ignore
"$ROOT/_ask/scripts/sync-cursor-binding.sh"
python3 "$ROOT/_ask/scripts/sync-codex-skills.py" --check-trackability
echo "upgrade-kit: refreshed kit-owned paths from $VERSION"
