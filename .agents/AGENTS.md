# `.agents/`

The one canonical agent folder, following the
[Agent Skills](https://agentskills.io) open standard and
[AGENTS.md](https://agents.md) conventions.

Every piece of agent configuration is one of three things:

| Tier | Strategy |
|---|---|
| **Canonical** — the single source of truth | Lives here: `skills/`, `mcp/servers.json`, `scripts/` |
| **Seed** — a harness reads it straight from the clone, before any script can run | Committed in the harness's own location, kept minimal: hook and environment registrations, one managed key per settings file |
| **Generated** — everything else a harness wants | Rendered by `scripts/sync.py`, gitignored, recreated per checkout for the harnesses detected on that machine |

Most harnesses need no generated adapter at all: `AGENTS.md` and
`.agents/skills/` are read natively by Codex, Cursor, Copilot's coding agent,
OpenCode, Amp, Factory, Goose, Zed, Crush, Kilo, Antigravity, dsh, and gsd,
among others. `sync.py list` shows the full table.

## Layout

- `skills/` — Shared skills. Each is a directory with `SKILL.md`.
- `mcp/servers.json` — Canonical MCP server configuration (Claude `mcpServers`
  dialect, plus an optional `tools` read-only allowlist per server).
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
3. Commit the canonical file plus the two committed seeds it updates
   (`.claude/settings.json`, `.gemini/settings.json`). Every other rendered
   adapter is gitignored.

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
  natively, MCP renderer if it has a project-level MCP file) and mirror any new
  output path in `.gitignore`'s generated-adapters block. CI fails if the two
  fall out of step.
- Agent-specific configuration stays put. `.cursor/rules/*.mdc` and
  `.github/instructions/*.instructions.md` use glob scoping and conditional
  loading with no equivalent elsewhere — do not convert them into skills.
  Knowledge every agent needs belongs in `AGENTS.md`.
- Keep secrets and machine-local configuration out of committed files.
- Run the pre-commit hooks or their underlying scripts before committing. GitHub
  Actions enforces the same checks for pull requests and `main`.
