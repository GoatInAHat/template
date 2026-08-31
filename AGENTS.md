# <Project>

<!-- setup keep=GoatInAHat/template -->
One-time bootstrap: if no environment hook ran it yet, run
`bash .agents/setup`. Its first successful run makes everything in Agent
config automatic and deletes this notice.
<!-- /setup -->

Created from a blank, stack-agnostic template. The first real task defines
the project: pick the stack that fits, set up its tooling, and replace this
paragraph with what the project is.

Record here what can't be inferred from the code: commands, layout,
conventions, decisions. Keep it small and current; drop anything that stops
being true.

## Defaults

- Reuse before reinventing; fix root causes, not symptoms.
- Build what was asked, completely: every needed path works, errors are
  handled, input is validated at trust boundaries. No speculative generality.
- Prove changes work the way a user would run them — a real browser for UIs,
  a real invocation for CLIs and services — and run the project's checks
  before handing work back.
- Secrets stay in the environment or a gitignored `.env`, never in git.
- Update docs in the same change that outdates them.

## Agent config

Skills and MCP servers live once in `.agents/` — `skills/` and
`mcp/servers.json` — and sync to every harness automatically, in both
directions; `CLAUDE.md`, `GEMINI.md`, and the per-harness configs are
generated from here. Personal-only config: gitignored `.agents/local/`, same
shape. Details and commands: `.agents/README.md`.

`rtk` compresses command output; when output will be large and no hook
rewrote the command, prefix it yourself: `rtk git diff`, `rtk pytest`.
