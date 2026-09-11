#!/usr/bin/env bash
# Refresh kit-owned files from an explicit kit version tag/sha.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
VERSION=""
SKIP_PREPARE=0
SOURCE_REPO="${KIT_SOURCE_REPO:-https://github.com/esmaeilzadeh/agent-starter-kit.git}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --version) VERSION="$2"; shift 2 ;;
    --skip-prepare) SKIP_PREPARE=1; shift ;;
    --source) SOURCE_REPO="$2"; shift 2 ;;
    *) echo "usage: upgrade-kit.sh --version <tag-or-sha> [--skip-prepare] [--source <git-url>]" >&2; exit 2 ;;
  esac
done
if [[ -z "$VERSION" ]]; then
  echo "upgrade-kit: --version required (never blind main)" >&2
  exit 2
fi

TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
git clone --depth 1 --branch "$VERSION" "$SOURCE_REPO" "$TMP/kit" 2>/dev/null \
  || git clone "$SOURCE_REPO" "$TMP/kit" && git -C "$TMP/kit" checkout "$VERSION"

# Consumer-owned paths to preserve
preserve=(
  part-engineering/skills/manifest.yaml
)
for p in "${preserve[@]}"; do
  if [[ -f "$ROOT/$p" ]]; then
    mkdir -p "$TMP/preserve/$(dirname "$p")"
    cp -a "$ROOT/$p" "$TMP/preserve/$p"
  fi
done

# Refresh kit-owned trees
for rel in part-engineering/guide part-engineering/spec part-engineering/agents part-engineering/templates part-engineering/scripts part-engineering/tests part-engineering/docs .cursor \
           ai-agent-engineering-guide.md ai-agent-starter-kit-spec.md part-engineering/OWNED-PATHS.md part-engineering/MAPPING.md part-engineering/README.md; do
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
done < <(find "$ROOT/part-engineering/agents" -name '*.local.md' -print0 2>/dev/null || true)

if [[ "$SKIP_PREPARE" -eq 0 ]]; then
  SKIP_INSTALL="${SKIP_INSTALL:-0}" "$ROOT/part-engineering/skills/prepare-skills.sh" || true
  "$ROOT/part-engineering/scripts/sync-cursor-binding.sh"
fi
echo "upgrade-kit: refreshed kit-owned paths from $VERSION"
