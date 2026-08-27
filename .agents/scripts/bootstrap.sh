#!/usr/bin/env bash
# Agent-agnostic environment setup for a fresh checkout.
#
# Safe to re-run; every step is idempotent and non-interactive. Every
# environment calls this same script through its native hook — see the
# environments table in .agents/README.md.
set -euo pipefail

REPO_ROOT="$(git -C "$(dirname "$0")" rev-parse --show-toplevel)"
cd "$REPO_ROOT"

if ! command -v pre-commit >/dev/null 2>&1; then
    if command -v uv >/dev/null 2>&1; then
        uv tool install pre-commit
        export PATH="$(uv tool dir --bin):$PATH"
    else
        python3 -m pip install --user pre-commit ||
            python3 -m pip install --user --break-system-packages pre-commit
        export PATH="$(python3 -m site --user-base)/bin:$PATH"
    fi
fi

.agents/scripts/sync.py "$@"
.agents/scripts/check-skills.py
pre-commit install

# Project setup goes here (dependency install, codegen, migrations). Keep it
# idempotent and fast when there is nothing to do, so every harness can call
# this script on every session start.
