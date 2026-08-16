#!/usr/bin/env bash
# Point every agent's skills dir at the vendor-neutral .agents/skills store.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p .agents/skills .claude/skills
# only stale symlinks are cleared; real directories an agent owns are left alone
find .claude/skills -maxdepth 1 -type l -delete
for skill in .agents/skills/*/; do
  skill=${skill%/}
  [ -f "$skill/SKILL.md" ] || continue
  ln -s "../../$skill" ".claude/skills/$(basename "$skill")"
done
