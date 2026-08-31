# `.agents/`

Canonical agent configuration, following [AGENTS.md](https://agents.md) and
the [Agent Skills](https://agentskills.io) standard. Two tiers, nothing else:

| Tier | Contents |
|---|---|
| **Canonical**, committed | `AGENTS.md`, `skills/`, `mcp/servers.json`, `sync.py`, `setup`, and the environment hooks below |
| **Generated**, gitignored | Everything else a harness reads — MCP configs, skill symlinks, the one-line `CLAUDE.md`/`GEMINI.md` imports of `AGENTS.md` — rendered per checkout by `sync.py` for the harnesses detected on the machine |

Most harnesses — Codex cloud, Copilot's coding agent, Windsurf, Goose, Zed,
Cline, Jules, Devin, and friends — read `AGENTS.md` and `.agents/skills/`
natively and need no adapter at all. `sync.py list` shows who gets what.

The only committed harness-specific files are the hook carriers
(`.claude/settings.json`, `.cursor/environment.json`,
`copilot-setup-steps.yml`, the devcontainer): git deliberately executes
nothing from a fresh clone — a repo that could would be an attack vector —
so each harness's own committed hook format is the one place automation can
start from. Everything derivable is generated.

## Two-way sync

`python3 .agents/sync.py` converges both directions in one run:

- **Canon → harnesses**: renders MCP configs (`.mcp.json`, `.cursor/mcp.json`,
  `.codex/config.toml`, …) and skill symlinks (`.claude/skills/`,
  `.codebuddy/skills/`) from `.agents/`.
- **Harnesses → canon**: a skill directory dropped in a harness skills dir, or
  an MCP server added to any rendered config (`claude mcp add`, a hand edit),
  is adopted into `.agents/` and rendered back out to every other harness.
  Commit the changed files under `.agents/` and `skills-lock.json`.

`setup` installs native git hooks — `post-checkout` and `post-merge` re-sync
quietly after every pull or branch switch, and `pre-commit` runs `sync.py
check`, with CI running the same — so after first contact nothing needs to be
run by hand, and nothing can be committed while the two sides disagree or a
generated file is tracked. The lock records a hash per skill (the same
convention `npx skills add` writes), so vendored skills can't drift silently;
after deliberately editing one, run `sync.py lock`.

## Environments

Every environment reaches the same `.agents/setup` through its native,
committed hook — that one script is where project setup (dependencies,
codegen) goes. It also installs [rtk](https://github.com/rtk-ai/rtk),
best-effort, to compress command output agents read.

| Environment | Committed hook |
|---|---|
| Claude Code (web and local) | `SessionStart` hook in `.claude/settings.json` |
| Devcontainers: Codespaces, Ona, DevPod | `postCreateCommand` in `.devcontainer/devcontainer.json` |
| Cursor cloud agents | `install` in `.cursor/environment.json` |
| Copilot coding agent | `.github/workflows/copilot-setup-steps.yml` |
| Amp orbs | runs `.agents/setup` by convention |
| CI | `.github/workflows/agent-config.yml` |
| Codex cloud, Jules, Devin, … | no in-repo hook exists; paste `bash .agents/setup` into the environment's setup-script field. They read `AGENTS.md` and `.agents/skills/` natively, so this only matters once project setup does something. |

## Rules

- Edit skills in `.agents/skills/` and MCP servers in `mcp/servers.json`; the
  per-harness copies are generated. `mcp/servers.json` uses the Claude
  `mcpServers` dialect plus an optional `tools` read-only allowlist (rendered
  where supported: Codex `enabled_tools`, Gemini/Qwen `includeTools`).
- Credentials never go in configs — reference environment variables.
- To support a new harness, add one `HARNESSES` entry (and renderer) in
  `sync.py` and mirror its outputs in `.gitignore`'s generated block;
  `sync.py check` fails until both agree.
- Codex trusts a project `.codex/config.toml` only after you trust the
  project; `sync.py install-codex` writes the user-level config instead.
