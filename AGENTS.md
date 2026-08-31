# <Project>

<One paragraph: what this project is, what the agent should treat as the source
of truth, and what it must not touch.>

## Repository layout

| Path | Purpose |
|---|---|
| `.agents/` | The one canonical agent folder: shared skills, MCP definitions, hook scripts, setup scripts, and the `setup` entry shim. Everything agent-related is edited here and only here. |
| `.github/workflows/` | CI enforcement of the rules below. Nothing harness-specific is committed anywhere in this repository: every file a harness reads (`CLAUDE.md`, `.claude/`, `.cursor/`, `.gemini/`, …) is generated from `.agents/` and gitignored — never edit or commit one. |
| `.devcontainer/` | Container definition for Codespaces, Ona, and local devcontainers. |

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

Concretely, in `Workflow` scripts set `model:` per `agent()` call — omitting it
inherits the session's strongest tier for every step, which is exactly the
failure mode. A deliberately single-tier workflow states why in a
`// single-tier: <reason>` comment; a committed Claude Code hook
(`.agents/hooks/workflow-model-mix.py`) blocks multi-agent scripts that do
neither.

## Skills and MCP

- No skills ship with this template. Add one under `.agents/skills/<name>/` or
  install a third party's with `npx skills add <repo>@<skill> -y`, then re-run
  `.agents/scripts/sync.py` and `.agents/scripts/check-skills.py --update`.
- **Context7** is registered for library documentation: `resolve-library-id`
  then `query-docs`, rather than recalling an API from memory. It works
  unauthenticated at a lower rate limit; set `CONTEXT7_API_KEY` and add the
  `Authorization: Bearer` header for your harness to raise it.

## Agent configuration

- Run `.agents/scripts/bootstrap.sh` once per fresh checkout — nothing a
  harness reads exists until you do. It is idempotent, and every environment
  invokes this one line: from `.devcontainer/`, from `.agents/setup`, or from
  the setup-script field in a cloud harness's own settings. See the
  environments table in `.agents/README.md`.
- Edit shared skills only in `.agents/skills/`; edit MCP servers only in
  `.agents/mcp/servers.json`; edit hook scripts only in `.agents/hooks/`; then
  run `.agents/scripts/sync.py`. It renders gitignored adapters for the
  harnesses detected on this machine (`--all` for every harness, `list` for the
  full table of who gets what). Instructions and skills ride the standards:
  harnesses read `AGENTS.md` (Claude Code through the generated `CLAUDE.md`
  pointer, Gemini through a generated `context.fileName`) and `.agents/skills/`
  (Claude Code and CodeBuddy through generated symlinks). The rest is MCP
  config for tools with a project-level MCP surface; dsh has none (user-level
  `$DSH_HOME` config only).
- Every renderer output must be listed in `.gitignore`'s generated-adapters
  block. `.agents/scripts/sync.py check` fails if one is unignored or tracked,
  and CI fails if a bootstrap run leaves an untracked file behind. Local,
  uncommitted Claude Code settings belong in `.claude/settings.local.json`,
  which the generator never touches.
- Codex loads a repo-local `.codex/config.toml` only for trusted projects; run
  `.agents/scripts/sync.py install-codex` only when the user wants this repo's
  MCP servers in their user-level Codex config instead.
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
.agents/scripts/sync.py check
.agents/scripts/check-skills.py
git diff --check
pre-commit run --all-files
```

Verify that every generated skill symlink resolves and review the final diff
before committing. Use
focused, imperative commit messages and avoid combining
unrelated changes. GitHub Actions runs the same agent-configuration checks on
pull requests and pushes to `main`; treat that workflow as the enforcement
layer. Don't leave work finished but unsynced with the remote, and don't leave
stale worktrees or branches behind.
