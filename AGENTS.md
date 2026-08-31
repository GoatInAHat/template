# Project

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
