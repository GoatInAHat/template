# `.agents/`

The one canonical agent folder, following the
[Agent Skills](https://agentskills.io) open standard and
[AGENTS.md](https://agents.md) conventions.

Every piece of agent configuration is one of two things:

| Tier | Strategy |
|---|---|
| **Canonical** — the single source of truth | Lives here: `skills/`, `mcp/servers.json`, `hooks/`, `scripts/` |
| **Generated** — everything a harness reads | Rendered by `scripts/sync.py`, gitignored, recreated per checkout for the harnesses detected on that machine |

There is no committed middle tier. `CLAUDE.md`, `.claude/`, `.cursor/`, and
`.gemini/` are all generated, so a fresh clone has to run
`scripts/bootstrap.sh` before any harness-specific file exists — see the
environments table in `README.md`.

Instructions and skills need almost no adapters: `AGENTS.md` and
`.agents/skills/` are read natively by Codex, Cursor, Copilot's coding agent,
OpenCode, Amp, Factory, Windsurf, Hermes, Trae, Augment, Goose, Zed, Crush,
Kilo, Antigravity, dsh, and gsd, among others — only Claude Code and CodeBuddy
get generated skill symlinks. What `sync.py` mostly renders is MCP configs for
tools with a project-level MCP surface; `sync.py list` shows the full table.

## Layout

- `skills/` — Shared skills. Each is a directory with `SKILL.md`.
- `mcp/servers.json` — Canonical MCP server configuration (Claude `mcpServers`
  dialect, plus an optional `tools` read-only allowlist per server).
- `hooks/` — Hook scripts that generated adapters register. Harness-specific in
  what registers them, canonical in where they live.
- `scripts/` — `bootstrap.sh` (environment setup entry point), `sync.py`
  (adapter generator), `check-skills.py` (vendored-skill lock).
- `setup` — Entry shim for harnesses that execute `.agents/setup` (Amp orbs).

## Adding a skill

1. Create `.agents/skills/<name>/SKILL.md` with `name` and `description`
   frontmatter, where `name` matches the directory.
2. Run `.agents/scripts/sync.py` and `.agents/scripts/check-skills.py --update`.
3. Commit the skill directory and `skills-lock.json`. Skill symlinks are
   generated and gitignored — do not commit them.

## Installing a third-party skill

```bash
npx skills add <repo>@<skill> -y
```

It installs into `.agents/skills/` and maintains the same `skills-lock.json`.

## Adding an MCP server

1. Edit `.agents/mcp/servers.json`.
2. Run `.agents/scripts/sync.py`.
3. Commit the canonical file. Every rendered adapter is gitignored.

An optional `tools` array on a server is a read-only allowlist. It renders as
`enabled_tools` for Codex and `includeTools` for Gemini and Qwen; the other
harnesses have no equivalent and receive the server's whole tool surface.

## Rules

- Edit skills in `.agents/skills/`, never through a harness's skills directory —
  those are symlinks or native readers of this one.
- Edit MCP definitions in `.agents/mcp/servers.json`, never in a rendered
  adapter.
- To support a new harness, add one entry to the `HARNESSES` table in
  `scripts/sync.py` (detection, skills dir if it doesn't read `.agents/skills/`
  natively, renderer if it has any project-level config file) and mirror every
  new output path in `.gitignore`'s generated-adapters block. `sync.py check`
  and CI both fail if the two fall out of step.
- Nothing harness-specific is committed. If a harness format has no equivalent
  elsewhere — `.cursor/rules/*.mdc` and `.github/instructions/*.instructions.md`
  use glob scoping and conditional loading that skills cannot express — add a
  renderer for it here rather than committing the file. Knowledge every agent
  needs belongs in `AGENTS.md`.
- Keep secrets and machine-local configuration out of committed files.
- Run the pre-commit hooks or their underlying scripts before committing. GitHub
  Actions enforces the same checks for pull requests and `main`.
