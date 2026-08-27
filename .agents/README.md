# Agent configuration

This directory is the canonical home for portable agent assets. Shared skills
follow the Agent Skills standard and are read from `.agents/skills/` natively
by most harnesses (symlinked into the few that still want their own
directory); MCP definitions are rendered into each tool's configuration
format. Rendered adapters are gitignored and recreated per checkout.

## Commands

```bash
# Install development tooling and refresh agent configuration
.agents/scripts/bootstrap.sh

# Render adapters for the harnesses detected on this machine
.agents/scripts/sync.py

# Render adapters for every known harness / a specific one
.agents/scripts/sync.py --all
.agents/scripts/sync.py windsurf

# Show the harness table: detection state and what each gets
.agents/scripts/sync.py list

# Fail if a managed key in a committed seed file is stale
.agents/scripts/sync.py check

# Explicitly install this repo's managed MCP block in the user Codex config
.agents/scripts/sync.py install-codex

# Verify skills-lock.json against the skills on disk (--update to re-lock)
.agents/scripts/check-skills.py
```

## Environments

Every environment runs the same `bootstrap.sh`. Nothing is
environment-specific except the hook that calls it:

| Environment | Entry point |
|---|---|
| Local | `.agents/scripts/bootstrap.sh`, once per checkout |
| Claude Code (web/cloud) | `SessionStart` hook → `.claude/hooks/session-start.sh` |
| GitHub Codespaces / devcontainers / Ona | `.devcontainer/devcontainer.json` `postCreateCommand` |
| GitHub Copilot coding agent | `.github/workflows/copilot-setup-steps.yml` (devcontainers are not honored there) |
| Cursor cloud agents | `.cursor/environment.json` `install` |
| Amp orbs | `.agents/setup` |
| Codex cloud | No in-repo hook — put `.agents/scripts/bootstrap.sh` in the environment's Setup script field (chatgpt.com/codex/settings/environments) |
| Jules / Devin / Factory | No in-repo hook — same one-liner in their UI setup/snapshot configuration |
| CI | `.github/workflows/agent-config.yml` |

To add another environment, call `bash .agents/scripts/bootstrap.sh` from its
native setup hook. Do not fork the setup logic. Bootstrap must stay
idempotent, non-interactive, fast when there is nothing to do, and free of
secrets at setup time (Codex cloud strips them before the agent phase).

## Generated files

`sync.py` renders adapters from `.agents/mcp/servers.json` and links
`.agents/skills/` for harnesses that don't read it natively — by default only
for harnesses it detects on the machine (CLI on PATH, config directory, or
environment variable; CI renders all). All of it is gitignored; the
`Validate agent configuration` workflow fails if a rendered file ever shows up
untracked. The two committed exceptions, `.claude/settings.json` and
`.gemini/settings.json`, are hand-owned apart from one managed key each
(`enabledMcpjsonServers`, `mcpServers`), which `sync.py check` keeps honest.
