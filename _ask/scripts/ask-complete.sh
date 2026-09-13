#!/usr/bin/env bash
# Print completion candidates for ./ask and askit. One candidate per line.
# Usage: ask-complete.sh <cword-index> <word0> <word1> ...
set -euo pipefail

ASK_COMMANDS=(
  check-clean
  start-work
  check-workstream
  status
  verify
  record-result
  record-run
  sync
  install
  upgrade
  prepare
  setup
  help
  completion
)

ask_complete_flags_for() {
  case "$1" in
    check-workstream|check) printf '%s\n' --allow-dirty ;;
    status) printf '%s\n' --work-id --json ;;
    record-result|record) printf '%s\n' --work-id --commit-sha --result --notes ;;
    record-run) printf '%s\n' --run-id --commit-sha --metric --notes --out ;;
    install|install-kit) printf '%s\n' --dry-run --force --skip-prepare ;;
    upgrade|upgrade-kit) printf '%s\n' --version --skip-prepare --source ;;
    setup) printf '%s\n' --help ;;
    completion) printf '%s\n' bash zsh ;;
  esac
}

ask_print_completions() {
  local cword="${1:-1}"
  shift || true
  local -a words=()
  if [[ $# -gt 0 ]]; then
    words=("$@")
  fi
  local cur=""
  if [[ "$cword" -ge 0 && "$cword" -lt ${#words[@]} ]]; then
    cur="${words[$cword]}"
  fi

  if [[ "$cword" -le 1 ]]; then
    printf '%s\n' "${ASK_COMMANDS[@]}" -h --help
    return 0
  fi

  local sub="${words[1]:-}"
  case "$sub" in
    completion)
      printf '%s\n' bash zsh
      ;;
    *)
      ask_complete_flags_for "$sub"
      ;;
  esac
  # unused: $cur is for callers that filter; we print the full set
  : "$cur"
}

if [[ "${BASH_SOURCE[0]:-}" == "$0" ]]; then
  ask_print_completions "$@"
fi
