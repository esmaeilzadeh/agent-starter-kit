#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."
python3 -m unittest _ask.tests.inner_loop_recovery
