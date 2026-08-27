#!/usr/bin/env bash
# Claude Code SessionStart hook: bootstrap remote sessions (Claude Code on the
# web) automatically. Local sessions skip it — run .agents/scripts/bootstrap.sh
# once per fresh checkout instead of paying for it on every session start.
#
# Always exits 0: a failing SessionStart hook kills the whole cloud session,
# and a session without generated adapters is still recoverable by hand.
set -uo pipefail

if [ "${CLAUDE_CODE_REMOTE:-}" != "true" ]; then
  exit 0
fi

project_dir="${CLAUDE_PROJECT_DIR:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)}"
"$project_dir/.agents/scripts/bootstrap.sh" ||
  echo "bootstrap failed; run .agents/scripts/bootstrap.sh manually" >&2
exit 0
