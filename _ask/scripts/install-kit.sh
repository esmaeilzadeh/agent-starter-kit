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
if [[ "$(git -C "$TARGET" rev-parse --show-toplevel 2>/dev/null || true)" != "$TARGET" ]]; then
  echo "install-kit: target is not a git repo: $TARGET" >&2
  exit 1
fi

if [[ "${ASKIT_TRANSACTION_ACTIVE:-0}" != "1" && "$DRY_RUN" -eq 0 ]]; then
  args=(python3 "$ROOT/_ask/scripts/write-transaction.py" run --root "$TARGET")
  for rel in \
    _ask/agents _ask/bindings _ask/cursor-commands _ask/policies _ask/scripts \
    _ask/skills _ask/templates _ask/ui _ask/docs .agents/ask .agents/ask.local \
    .agents/skills .cursor .codex/agents .claude/agents .opencode/agents \
    .gitignore AGENTS.md ask .ask.env.example .ask; do
    args+=(--path "$rel")
  done
  args+=(-- bash "$ROOT/_ask/scripts/install-kit.sh")
  [[ "$FORCE" -eq 0 ]] || args+=(--force)
  [[ "$SKIP_PREPARE" -eq 0 ]] || args+=(--skip-prepare)
  args+=("{target}")
  exec "${args[@]}"
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
    excl=(--exclude __pycache__/ --exclude '*.pyc')
    if [[ "$rel" == "_ask/skills" && -f "$dest/manifest.yaml" && "$FORCE" -eq 0 ]]; then
      excl+=(--exclude manifest.yaml)
    elif [[ "$rel" == "_ask/bindings" && -f "$dest/models.yaml" && "$FORCE" -eq 0 ]]; then
      excl+=(--exclude models.yaml)
    fi
    rsync -a "${excl[@]}" "$src/" "$dest/"
  else
    if [[ -e "$dest" && "$FORCE" -eq 0 ]]; then
      echo "install-kit: skip existing $rel (use --force)"
      return 0
    fi
    cp -a "$src" "$dest"
  fi
}

if [[ "$DRY_RUN" -eq 0 ]]; then
  bash "$ROOT/_ask/scripts/copy-project-config.sh" "$TARGET" "$ROOT/_ask/skills/manifest.yaml"
fi

# Consumer runtime only; kit specs, tests, authoring guides and local environments stay here.
for rel in \
  _ask/agents \
  _ask/bindings \
  _ask/cursor-commands \
  _ask/policies \
  _ask/scripts \
  _ask/skills \
  _ask/templates \
  _ask/ui \
  _ask/docs/codex-integration.md \
  _ask/docs/codex-model-routing.md \
  _ask/docs/engineering-model.md \
  _ask/docs/inner-loop-evidence.md \
  _ask/docs/spec-test-traceability.md \
  _ask/docs/workflow-references.md \
  _ask/docs/adr/0016-grilling-load-bearing-and-skill-before.md \
  _ask/docs/adr/0017-humanizer-docs-specs.md \
  .agents/ask \
  .cursor \
  .gitignore \
  AGENTS.md \
  ask \
  .ask.env.example \
  .ask/README.md
 do
  # never overlay product-generic names
  [[ "$rel" == docs || "$rel" == scripts || "$rel" == tests ]] && continue
  copy_path "$rel"
done

# Ensure target gitignores the installed kit and prepared skills
if [[ "$DRY_RUN" -eq 0 ]]; then
  if ! grep -qxF '/_ask/' "$TARGET/.gitignore" 2>/dev/null; then
    printf '\n# Installed AskIt kit\n/_ask/\n' >> "$TARGET/.gitignore"
  fi
  python3 "$TARGET/_ask/scripts/sync-codex-skills.py" --update-ignore
  if ! grep -q '^\.ask\.env$' "$TARGET/.gitignore" 2>/dev/null; then
    echo -e '\n# Setup wizard secrets\n.ask.env\n.ask/tracker-context.md' >> "$TARGET/.gitignore"
  fi
fi

if [[ "$DRY_RUN" -eq 1 ]]; then
  echo "install-kit: dry-run complete (product docs/scripts/tests not overlaid)"
  exit 0
fi

if [[ "$SKIP_PREPARE" -eq 0 ]]; then
  if [[ -x "$TARGET/_ask/skills/prepare-skills.sh" ]]; then
    (cd "$TARGET" && SKIP_INSTALL="${SKIP_INSTALL:-0}" ./_ask/skills/prepare-skills.sh)
  fi
fi
if [[ -x "$TARGET/_ask/scripts/sync-cursor-binding.sh" ]]; then
  # A caller such as detached verification may export ASK_ROOT/ASK_WORK_ID for
  # itself. Generated runtime agents belong to the explicit install target.
  (cd "$TARGET" && ASK_ROOT="$TARGET" ASK_WORK_ID= ./_ask/scripts/sync-cursor-binding.sh)
fi

python3 "$TARGET/_ask/scripts/sync-codex-skills.py" --check-trackability

echo "install-kit: applied to $TARGET"
