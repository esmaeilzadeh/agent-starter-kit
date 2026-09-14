#!/usr/bin/env bash
# Print completion candidates for ./ask and askit.
# Lines are: word<TAB>description
# Usage: ask-complete.sh <cword-index> <word0> <word1> ...
set -euo pipefail

# Primary commands (tab after ask/askit). Aliases resolve in flag lookup.
ask_complete_emit() {
  printf '%s\t%s\n' "$1" "$2"
}

ask_complete_commands() {
  ask_complete_emit check-clean "refuse dirty worktree"
  ask_complete_emit start-work "branch agent/<work-id> + seed work/<work-id>/"
  ask_complete_emit check-workstream "preconditions before implement"
  ask_complete_emit status "live/archived workstreams + later inbox"
  ask_complete_emit verify "run checks; print commit SHA; optional --work-id"
  ask_complete_emit openspec-archive "archive OpenSpec change after Accept SHA"
  ask_complete_emit record-result "workstream provenance"
  ask_complete_emit record-run "experiment provenance (SHA must be HEAD)"
  ask_complete_emit sync "regenerate .cursor projections"
  ask_complete_emit install "overlay kit onto another git repo"
  ask_complete_emit upgrade "refresh kit-owned files from a version"
  ask_complete_emit prepare "install pinned Community Skills"
  ask_complete_emit setup "tracker/MCP wizard (repo must already be ask-based)"
  ask_complete_emit help "this help text"
  ask_complete_emit completion "print bash|zsh tab-completion snippet"
  ask_complete_emit -h "help"
  ask_complete_emit --help "help"
}

# Canonical name for aliases.
ask_complete_canon() {
  case "$1" in
    start) echo start-work ;;
    check|check-workstream) echo check-workstream ;;
    record) echo record-result ;;
    install-kit) echo install ;;
    upgrade-kit) echo upgrade ;;
    prepare-skills) echo prepare ;;
    sync-cursor-binding) echo sync ;;
    check-clean-worktree) echo check-clean ;;
    *) echo "$1" ;;
  esac
}

ask_complete_flags_for() {
  case "$(ask_complete_canon "$1")" in
    check-clean)
      ask_complete_emit -h "help"
      ask_complete_emit --help "help"
      ;;
    start-work)
      ask_complete_emit -h "help"
      ask_complete_emit --help "help"
      ;;
    check-workstream)
      ask_complete_emit --allow-dirty "skip the clean-tree check"
      ask_complete_emit -h "help"
      ask_complete_emit --help "help"
      ;;
    status)
      ask_complete_emit --work-id "<id>  one workstream"
      ask_complete_emit --json "machine-readable rows"
      ask_complete_emit --later-only "parked .later/ cards only"
      ask_complete_emit --work-only "workstreams only"
      ask_complete_emit -h "help"
      ask_complete_emit --help "help"
      ;;
    verify)
      ask_complete_emit --work-id "<id>  write work/<id>/verification.json"
      ask_complete_emit -h "help"
      ask_complete_emit --help "help"
      ;;
    openspec-archive)
      ask_complete_emit -h "help"
      ask_complete_emit --help "help"
      ;;
    record-result)
      ask_complete_emit --work-id "<id>  required"
      ask_complete_emit --commit-sha "<sha>  required"
      ask_complete_emit --result "<text>  required"
      ask_complete_emit --notes "<text>"
      ;;
    record-run)
      ask_complete_emit --run-id "<id>  required"
      ask_complete_emit --commit-sha "<sha>  must be HEAD"
      ask_complete_emit --metric "<value>  required"
      ask_complete_emit --notes "<text>"
      ask_complete_emit --out "<dir>  default results/<run-id>"
      ;;
    sync)
      ask_complete_emit -h "help"
      ask_complete_emit --help "help"
      ;;
    install)
      ask_complete_emit --dry-run "print paths; copy nothing"
      ask_complete_emit --force "overwrite existing kit-owned files"
      ask_complete_emit --skip-prepare "skip prepare and sync in the target"
      ask_complete_emit -h "help"
      ask_complete_emit --help "help"
      ;;
    upgrade)
      ask_complete_emit --version "<tag-or-sha>  required"
      ask_complete_emit --skip-prepare "skip prepare + sync after refresh"
      ask_complete_emit --source "<git-url>"
      ;;
    prepare)
      ask_complete_emit -h "help"
      ask_complete_emit --help "help"
      ;;
    setup)
      ask_complete_emit --help "usage without a TTY"
      ;;
    self-install)
      ask_complete_emit --source "<git-url-or-path>"
      ask_complete_emit --ref "<branch-or-tag>"
      ask_complete_emit --prefix "<dir>  default ~/.local"
      ask_complete_emit --here "also overlay the kit into cwd"
      ask_complete_emit -h "help"
      ask_complete_emit --help "help"
      ;;
    completion)
      ask_complete_emit bash "eval this in bash"
      ask_complete_emit zsh "eval this in zsh"
      ;;
    help)
      ;;
    *)
      ask_complete_emit -h "help"
      ask_complete_emit --help "help"
      ;;
  esac
}

ask_complete_value_flags() {
  case "$(ask_complete_canon "$1")" in
    status|record-result) printf '%s\n' --work-id --commit-sha --result --notes ;;
    verify) printf '%s\n' --work-id ;;
    record-run) printf '%s\n' --run-id --commit-sha --metric --notes --out ;;
    upgrade) printf '%s\n' --version --source ;;
    self-install) printf '%s\n' --source --ref --prefix ;;
  esac
}

ask_complete_already_used() {
  local word="$1"
  shift
  local w
  for w in "$@"; do
    [[ "$w" == "$word" ]] && return 0
  done
  return 1
}

ask_print_completions() {
  local cword="${1:-1}"
  shift || true
  local -a words=()
  if [[ $# -gt 0 ]]; then
    words=("$@")
  fi

  if [[ "$cword" -le 1 ]]; then
    ask_complete_commands
    if [[ "${words[0]:-}" == *askit ]]; then
      ask_complete_emit self-install "put askit on PATH (same as curl | bash)"
    fi
    return 0
  fi

  local sub="${words[1]:-}"
  local prev=""
  if [[ "$cword" -ge 1 && $((cword - 1)) -lt ${#words[@]} ]]; then
    prev="${words[$((cword - 1))]:-}"
  fi

  local vf
  vf="$(ask_complete_value_flags "$sub" || true)"
  if [[ -n "$prev" && -n "$vf" ]] && printf '%s\n' "$vf" | grep -qx -- "$prev"; then
    case "$prev" in
      --out|--source)
        ask_complete_emit __PATH__ "path"
        ;;
      --work-id)
        local d
        if [[ -d work ]]; then
          for d in work/*/; do
            [[ -d "$d" ]] || continue
            ask_complete_emit "$(basename "${d%/}")" "workstream"
          done
        fi
        ;;
    esac
    return 0
  fi

  local line word desc
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    word="${line%%	*}"
    desc="${line#*	}"
    [[ "$word" == "$line" ]] && desc=""
    if [[ "$word" == -* ]] && ask_complete_already_used "$word" "${words[@]:2}"; then
      continue
    fi
    ask_complete_emit "$word" "$desc"
  done < <(ask_complete_flags_for "$sub")

  # install's remaining positional is a repo path
  if [[ "$(ask_complete_canon "$sub")" == install ]]; then
    ask_complete_emit __PATH__ "target git repo"
  fi
}

if [[ "${BASH_SOURCE[0]:-}" == "$0" ]]; then
  ask_print_completions "$@"
fi
