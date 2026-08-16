# <Project>

<One paragraph: what this project is, what the agent should treat as the source
of truth, and what it must not touch.>

## Repository layout

| Path | Purpose |
|---|---|
| `.agents/` | Canonical shared skills, MCP definitions, and adapter scripts. |
| `.claude/`, `.cursor/`, `.codex/`, `.gemini/`, `.mcp.json` | Agent adapters. Generated files must not be edited directly. |

## Code quality

- Prefer correct, complete implementations over minimal ones.
- Use appropriate data structures and algorithms; don't brute-force what has a
  known better solution.
- When fixing a bug, fix the root cause, not the symptom.
- If something requires or could use error handling or validation to work
  reliably, include it without asking.
- For anything frontend or fullstack, do E2E testing in a real browser with live
  API keys whenever possible (Playwright, a browser MCP, or the dev
  environment — whichever is available), and keep it in the development loop
  rather than saving it for the end.
- When dispatching subagents or dynamic workflows, spread work sensibly across
  models by speed, intelligence, and cost. Not everything needs the most
  expensive model.

## Agent configuration

- Run `.agents/scripts/bootstrap.sh` once per fresh checkout. It is idempotent
  and is what every cloud environment runs on startup.
- Edit shared skills only in `.agents/skills/`, then run
  `.agents/scripts/link-skills.sh`.
- Edit MCP servers only in `.agents/mcp/servers.json`, then run
  `.agents/scripts/sync-mcp.sh`.
- Repo-local `.codex/config.toml` is generated for parity but is not loaded
  automatically by the Codex CLI. Run `.agents/scripts/sync-mcp.sh install-codex`
  only when the user wants this repo's MCP servers in their user config.
- Never commit credentials. Secrets come from the environment or an ignored
  `.env`; `.env.example` documents the variables.

## Validation

Run the checks relevant to the files changed:

```bash
.agents/scripts/link-skills.sh
.agents/scripts/sync-mcp.sh check
.agents/scripts/check-skills.py
git diff --check
pre-commit run --all-files
```

Verify that every committed symlink resolves and review the final diff before
committing. Use focused, imperative commit messages and avoid combining
unrelated changes. GitHub Actions runs the same agent-configuration checks on
pull requests and pushes to `main`; treat that workflow as the enforcement
layer. Don't leave work finished but unsynced with the remote, and don't leave
stale worktrees or branches behind.
