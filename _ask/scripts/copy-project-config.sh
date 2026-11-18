#!/usr/bin/env bash
# Seed the tracked project overlay from legacy files or the kit defaults.
set -euo pipefail

target="$1"
default_manifest="$2"
project="$target/.agents/ask.local"

copy_if_missing() {
  if [[ -f "$1" && ! -e "$2" && ! -L "$2" ]]; then
    mkdir -p "$(dirname "$2")"
    cp "$1" "$2"
  fi
}

copy_if_missing "$target/_ask/skills/manifest.yaml" "$project/skills/manifest.yaml"
copy_if_missing "$default_manifest" "$project/skills/manifest.yaml"
copy_if_missing "$target/_ask/bindings/models.yaml" "$project/bindings/models.yaml"
for legacy in "$target"/_ask/agents/[0-9][0-9]-*.local.md; do
  copy_if_missing "$legacy" "$project/stages/$(basename "$legacy" .local.md).md"
done
