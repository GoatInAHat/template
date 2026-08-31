# <Project>

Created from a blank, stack-agnostic template. The first real task defines the
project: pick the stack that fits, set up its tooling, and replace this
paragraph with what the project is.

Every coding agent reads this file — `CLAUDE.md` and `GEMINI.md` just import
it. Record here what can't be inferred from the code: commands, layout,
conventions, decisions. Keep it small and current; drop anything that stops
being true.

## Defaults

- Reuse before reinventing: look for the existing helper or pattern first. If
  it almost fits, change it where it lives so every caller benefits.
- Fix root causes, not symptoms.
- Build what was asked, completely: every needed path works, errors are
  handled, input is validated at trust boundaries. No speculative generality.
- Prove changes work the way a user would run them — a real browser for UIs, a
  real invocation for CLIs and services — and run the project's checks before
  handing work back.
- Secrets stay in the environment or a gitignored `.env`, out of git and code.
- Update docs in the same change that outdates them. Write a README once there
  is something honest to describe, not before.

## Agent config

- Skills and MCP servers are written once, in `.agents/skills/` and
  `.agents/mcp/servers.json` (both empty by default; third-party skills:
  `npx skills add <repo>@<skill> -y`). Run `python3 .agents/sync.py` after
  editing either: it renders each harness's gitignored config — never edit or
  commit those files.
- The sync is two-way. Anything installed through one harness — `claude mcp
  add`, a skill dropped in `.claude/skills/`, a server hand-added to any
  rendered config — is adopted into `.agents/` by that same command and
  rendered for every other harness. A pre-commit hook installed by
  `.agents/setup` blocks commits until converged; `python3 .agents/sync.py
  check` (CI runs it too) says what's off. Details: `.agents/README.md`.
- Every environment bootstraps through the same `.agents/setup`, reached via
  committed hooks (devcontainer, Claude Code, Cursor, Copilot, Amp); it also
  installs git hooks that re-sync on every pull and checkout. Project setup
  belongs in that script; keep it idempotent.
- `.agents/setup` installs `rtk` to compress command output. When a command
  will print a lot and no hook rewrote it, prefix it: `rtk git diff`,
  `rtk pytest`.
