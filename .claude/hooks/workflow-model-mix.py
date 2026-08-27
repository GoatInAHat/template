#!/usr/bin/env python3
"""PreToolUse hook for the Workflow tool: enforce AGENTS.md's model-mix rule.

A multi-agent workflow script that never sets `model:` runs every step on the
session's strongest tier. AGENTS.md (Dispatching work) requires balancing
tiers instead, so block such scripts with feedback. Deliberate single-tier
runs opt out with a `// single-tier: <reason>` comment.
"""
import json
import re
import sys


def main():
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        return 0
    if data.get("tool_name") != "Workflow":
        return 0

    tool_input = data.get("tool_input") or {}
    if tool_input.get("resumeFromRunId"):
        # The original invocation was already checked; a resume replays it.
        return 0

    script = tool_input.get("script") or ""
    if not script and tool_input.get("scriptPath"):
        try:
            with open(tool_input["scriptPath"], encoding="utf-8") as handle:
                script = handle.read()
        except OSError:
            return 0
    if not script:
        # Named workflow; its source is not visible here.
        return 0

    agent_calls = len(re.findall(r"\bagent\s*\(", script))
    if agent_calls < 2:
        return 0
    if re.search(r"\bmodel\s*:", script) or re.search(r"//\s*single-tier:", script):
        return 0

    print(
        f"This workflow spawns {agent_calls} agent() calls and none sets `model:`, "
        "so every step inherits the strongest tier. AGENTS.md (Dispatching work) "
        "requires a mix: set model: 'haiku' or 'sonnet' on mechanical scan, "
        "fan-out, and summarisation steps, and keep the strongest tier for "
        "design, adversarial verification, and final synthesis. If one tier "
        "really fits every step, say why in a `// single-tier: <reason>` "
        "comment and re-invoke.",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
