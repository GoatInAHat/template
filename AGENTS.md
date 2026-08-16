# Agent Instructions

Default instructions for any coding agent working in this repo. `CLAUDE.md` and
`GEMINI.md` are symlinks to this file — edit this one.

## Code Quality

- Prefer correct, complete implementations over minimal ones.
- Use appropriate data structures and algorithms; don't brute-force what has a known better solution.
- When fixing a bug, fix the root cause, not the symptom.
- If something requires or could use error handling or validation to work reliably, include it without asking.
- For anything frontend or fullstack, do E2E testing in a real browser with live API keys whenever
  possible (Playwright, a browser MCP, or the dev environment — whichever is available), and keep it
  in the development loop rather than saving it for the end.

## Skills

Skills live in `.agents/skills/<name>/SKILL.md` — one directory per skill, no vendor prefix.
`skills-lock.json` pins each skill's upstream source and content hash.

Agent-specific skill directories are symlinks back into that store, so every agent reads the same
copy. After adding or removing a skill:

    ./link-skills.sh

## Secrets

Never commit `.env`. `.gitignore` blocks env files, keys, certs, and auth state — extend it rather
than working around it.
