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

- Work smart, not hard. Never reinvent the wheel. Design systems using a tech stack that fits together in a way that the desired behavior is emergent and necessary mechanisms are implicit. Write as little of your own code as possible, and when you do write your own custom handling of things, there needs to be a good reason why and your implementations and abstractions must be standardized across your codebase. This applies to implementations of dependencies as well, across the tech stack there may be multiple ways do to one thing, and you should always try to standardize across the codebase with the implementation that covers all bases at once (when done properly, all of this massively reduces codebase complexity).
- As an extension of the previous dogma, no filler content. On the frontend, this means things like extra UI bloat (random static text, elements that don't need to exist, etc). On the backend, it means things like handling of edge cases that will never happen because they are implicitly handled when the design dogmas outlined above are followed, api routes and logic for features that will never exist, and specialization where generalization wins.
- Drive by refactors are ok, as long as you understand the full context of what you're doing and it's for the sake of making previously written code obey these development dogmas. Codebases evolve, and the structure of your abstractions and implementations of your tech stack must be fluid to always align with best practices. One critical design pathology is hanging on to poor design decisions that were previously made, and letting them degrade the trajectory of development by continuously working around them.
- Maintain the fewest number of tests that cover the requisite variety of the codebase. Coding agents tend to treat tests as append only, always adding more and more. In observance of the previous dogmas and avoidance of the aforementioned pathology, if you never update or consolidate your previously written tests they can lock in bad architecture decisions made previously.
- In addition to tests, agentically prove changes work the way a user would run them — a real browser for UIs,
  a real invocation for CLIs and services.
- Secrets stay in the environment or a gitignored `.env`, never in git.
- Update docs in the same change that outdates them.
- Keep this document lean and token-efficient.

## Agent config

Skills and MCP servers live once in `.agents/` — `skills/` and
`mcp/servers.json` — and sync to every harness automatically, in both
directions; `CLAUDE.md`, `GEMINI.md`, and the per-harness configs are
generated from here. Personal-only config: gitignored `.agents/local/`, same
shape. Details and commands: `.agents/README.md`.

`rtk` compresses command output; when output will be large and no hook
rewrote the command, prefix it yourself: `rtk git diff`, `rtk pytest`.
