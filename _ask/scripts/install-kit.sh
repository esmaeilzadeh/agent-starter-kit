#!/usr/bin/env bash
# Overlay kit into an existing git repo. Never touches consumer docs/ by default.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
TARGET=""
DRY_RUN=0
FORCE=0
SKIP_PREPARE=0

while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=1; shift ;;
    --force) FORCE=1; shift ;;
    --skip-prepare) SKIP_PREPARE=1; shift ;;
    -*) echo "unknown flag $1" >&2; exit 2 ;;
    *) TARGET="$1"; shift ;;
  esac
done

if [[ -z "$TARGET" ]]; then
  echo "usage: install-kit.sh [--dry-run] [--force] [--skip-prepare] <target-repo>" >&2
  exit 2
fi
TARGET="$(cd "$TARGET" && pwd)"
if [[ ! -d "$TARGET/.git" ]]; then
  echo "install-kit: target is not a git repo: $TARGET" >&2
  exit 1
fi

# Never touch consumer docs
if [[ -e "$TARGET/docs" ]]; then
  echo "install-kit: note — will not modify target docs/ (consumer-owned)"
fi

copy_path() {
  local rel="$1"
  local src="$ROOT/$rel"
  local dest="$TARGET/$rel"
  if [[ ! -e "$src" ]]; then
    return 0
  fi
  if [[ "$DRY_RUN" -eq 1 ]]; then
    echo "DRY-RUN: would copy $rel"
    return 0
  fi
  mkdir -p "$(dirname "$dest")"
  if [[ -d "$src" ]]; then
    mkdir -p "$dest"
    # copy contents; skip consumer-owned manifest if exists unless --force
    if [[ "$rel" == "_ask" ]]; then
      excl=(--exclude tests/)
      if [[ -f "$dest/skills/manifest.yaml" && "$FORCE" -eq 0 ]]; then
        excl+=(--exclude skills/manifest.yaml)
      fi
      rsync -a "${excl[@]}" "$src/" "$dest/"
    elif [[ "$rel" == "_ask/skills" && -f "$dest/manifest.yaml" && "$FORCE" -eq 0 ]]; then
      rsync -a --exclude manifest.yaml "$src/" "$dest/"
    else
      rsync -a "$src/" "$dest/"
    fi
  else
    if [[ -e "$dest" && "$FORCE" -eq 0 ]]; then
      echo "install-kit: skip existing $rel (use --force)"
      return 0
    fi
    cp -a "$src" "$dest"
  fi
}

# Paths to overlay
for rel in \
  _ask \
  .cursor \
  .gitignore \
  AGENTS.md \
  ask \
  ai-agent-engineering-guide.md \
  ai-agent-starter-kit-spec.md
 do
  # never overlay product-generic names
  [[ "$rel" == docs || "$rel" == scripts || "$rel" == tests ]] && continue
  copy_path "$rel"
done

# Ensure target gitignores prepared skills
if [[ "$DRY_RUN" -eq 0 ]]; then
  if ! grep -q '.agents/skills/' "$TARGET/.gitignore" 2>/dev/null; then
    echo -e '\n# Prepared Community Skills\n.agents/skills/' >> "$TARGET/.gitignore"
  fi
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "install-kit: dry-run complete (product docs/scripts/tests not overlaid)"
  exit 0
fi

if [[ "$SKIP_PREPARE" -eq 0 ]]; then
  if [[ -x "$TARGET/_ask/skills/prepare-skills.sh" ]]; then
    (cd "$TARGET" && SKIP_INSTALL="${SKIP_INSTALL:-0}" ./_ask/skills/prepare-skills.sh) || true
  fi
  if [[ -x "$TARGET/_ask/scripts/sync-cursor-binding.sh" ]]; then
    (cd "$TARGET" && ./_ask/scripts/sync-cursor-binding.sh)
  fi
fi

echo "install-kit: applied to $TARGET"
