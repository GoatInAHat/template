# <Project>

<One paragraph: what this project is, what the agent should treat as the source
of truth, and what it must not touch.>

## Repository layout

| Path | Purpose |
|---|---|
| `.agents/` | Canonical shared skills, MCP definitions, and adapter scripts. |
| `.claude/`, `.cursor/`, `.codex/`, `.gemini/`, `.github/`, `.mcp.json` | Agent adapters. Generated files must not be edited directly. |
| `.devcontainer/` | Container definition for Codespaces and local devcontainers. |

## Code quality

- Prefer correct, complete implementations over minimal ones. Complete means
  every path the requested behaviour needs actually works — not extra paths
  nobody asked for. Speculative generality is a defect, not thoroughness.
- **Never write a second implementation of something this repo already does.**
  Look for the existing helper, type, or pattern before writing a new one. If it
  doesn't fit, change it where it lives so every caller gets the fix.
- Keep machinery and abstractions as central as makes sense: one owner per
  concern, callers stay thin. An abstraction with one implementation and no
  second caller in sight is premature — inline it until a real second case
  arrives.
- Use appropriate data structures and algorithms; don't brute-force what has a
  known better solution.
- When fixing a bug, fix the root cause, not the symptom. Check every caller of
  the function you are about to change; one guard in the shared path beats a
  guard in each caller, and patching only the reported path leaves its siblings
  broken.
- If something requires or could use error handling or validation to work
  reliably, include it without asking. Never simplify away validation at trust
  boundaries, error handling that prevents data loss, security controls, or
  accessibility basics.
- For anything frontend or fullstack, do E2E testing in a real browser with live
  API keys whenever possible (Playwright, a browser MCP, or the dev
  environment — whichever is available), and keep it in the development loop
  rather than saving it for the end.

## Dispatching work

Whenever work leaves your own context — dynamic workflows, subagents, background
tasks, scheduled jobs, parallel fan-out, anything — balance the models used
across intelligence and speed rather than sending every step to one tier. Match
the model to the step: fast and cheap for mechanical scans, fan-out, and
summarisation; the strongest available for design, adversarial review, and final
synthesis. Prefer a mix over a single tier by default, and say which tier a step
is using when it matters.

## Skills and MCP

- **Ponytail is always on**, at its default `full` intensity, for every coding
  task here. Read `.agents/skills/ponytail/SKILL.md` and apply it on every
  response; keep it active unless the user explicitly changes intensity or turns
  it off. `ponytail-audit`, `ponytail-debt`, `ponytail-gain`, `ponytail-help`,
  and `ponytail-review` are pinned beside it.
- **find-skills** covers skill discovery — reach for it when a task looks like
  something an installable skill already does.
- **Context7** is registered for library documentation: `resolve-library-id`
  then `query-docs`, rather than recalling an API from memory. It works
  unauthenticated at a lower rate limit; set `CONTEXT7_API_KEY` and add the
  `Authorization: Bearer` header for your harness to raise it.

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

## Documentation

- Write `README.md` once the project has enough shape to describe honestly: what
  it is, how to run it, how to test it. Keep it clean and minimal — no feature
  tour, no roadmap, no badges. Until then, don't write a placeholder.
- Update the README in the same change that makes it wrong, not later.
- Keep this file current as the project changes, and keep it small. It loads into
  every agent's context on every session, so it pays rent: record only what
  changes an agent's behaviour, drop anything the code or `--help` already says,
  and prefer one precise line to a paragraph.

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
