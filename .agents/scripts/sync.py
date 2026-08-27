#!/usr/bin/env python3
"""Render harness adapters from the canonical assets in .agents/.

Canonical sources:
  .agents/skills/            shared skills (Agent Skills standard)
  .agents/mcp/servers.json   MCP servers, Claude `mcpServers` dialect plus an
                             optional `tools` read-only allowlist per server

Committed seed files (always kept in sync, because they are committed):
  .claude/settings.json      `enabledMcpjsonServers` key only
  .gemini/settings.json      `mcpServers` key only

Generated adapters (gitignored, rendered per checkout) are produced only for
harnesses detected on this machine, so a checkout carries adapters for the
tools that actually run here and nothing else.

Usage:
  sync.py [harness ...]   sync seeds + adapters for detected (or named) harnesses
  sync.py --all           sync adapters for every known harness (CI default)
  sync.py check           verify the managed keys in committed seed files
  sync.py list            show known harnesses, detection state, and adapters
  sync.py install-codex   install this repo's MCP block into ~/.codex/config.toml

Harnesses that read AGENTS.md and .agents/skills/ natively need no adapter and
no entry here: dsh (DeepSeek Harness), Goose, Zed, Crush, Cline, Antigravity,
Jules, Devin, gsd. Copilot's cloud coding agent also reads both natively; the
`vscode` entry below covers local VS Code, which wants .vscode/mcp.json.
"""
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SKILLS_ROOT = REPO_ROOT / ".agents" / "skills"
SERVERS_PATH = REPO_ROOT / ".agents" / "mcp" / "servers.json"

# Each harness: how to detect it on this machine (env vars set, commands on
# PATH, directories under $HOME or the project), where its per-skill symlinks
# go (None = it reads .agents/skills natively), and which MCP renderer feeds it
# (None = it has no project-scoped MCP file).
HARNESSES = {
    "claude":    {"env": ["CLAUDECODE", "CLAUDE_CODE_REMOTE"], "cmd": ["claude"], "home": [".claude"], "skills": ".claude/skills", "mcp": "claude"},
    "codex":     {"cmd": ["codex"], "home": [".codex"], "skills": None, "mcp": "codex"},
    "cursor":    {"cmd": ["cursor-agent", "cursor"], "home": [".cursor"], "skills": None, "mcp": "cursor"},
    "gemini":    {"cmd": ["gemini"], "home": [".gemini"], "skills": None, "mcp": "gemini"},
    "qwen":      {"cmd": ["qwen"], "home": [".qwen"], "skills": None, "mcp": "qwen"},
    "opencode":  {"cmd": ["opencode"], "home": [".config/opencode"], "skills": None, "mcp": "opencode"},
    "vscode":    {"cmd": ["code"], "project": [".vscode"], "skills": None, "mcp": "vscode"},
    "kilo":      {"cmd": ["kilo"], "home": [".config/kilo"], "skills": None, "mcp": "kilo"},
    "factory":   {"cmd": ["droid"], "home": [".factory"], "skills": None, "mcp": "factory"},
    "amp":       {"cmd": ["amp"], "home": [".amp"], "skills": None, "mcp": "amp"},
    "windsurf":  {"home": [".codeium"], "project": [".windsurf"], "skills": ".windsurf/skills", "mcp": None},
    "hermes":    {"cmd": ["hermes"], "home": [".hermes"], "skills": ".hermes/skills", "mcp": None},
    "trae":      {"home": [".trae"], "project": [".trae"], "skills": ".trae/skills", "mcp": None},
    "augment":   {"cmd": ["auggie"], "home": [".augment"], "skills": ".augment/skills", "mcp": None},
    "codebuddy": {"cmd": ["codebuddy"], "home": [".codebuddy"], "skills": ".codebuddy/skills", "mcp": None},
}

# Read AGENTS.md and .agents/skills/ natively; listed so `list` can say so.
NATIVE = ("dsh", "goose", "zed", "crush", "cline", "antigravity", "jules", "devin", "gsd")


def detected(spec):
    return (
        any(os.environ.get(var) for var in spec.get("env", ()))
        or any(shutil.which(cmd) for cmd in spec.get("cmd", ()))
        or any((Path.home() / rel).exists() for rel in spec.get("home", ()))
        or any((REPO_ROOT / rel).exists() for rel in spec.get("project", ()))
    )


def load_servers():
    try:
        servers = json.loads(SERVERS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: cannot read {SERVERS_PATH}: {exc}")
    if not isinstance(servers, dict):
        raise SystemExit("ERROR: .agents/mcp/servers.json must contain a JSON object")
    for name, config in servers.items():
        if not isinstance(name, str) or not name:
            raise SystemExit("ERROR: every MCP server must have a non-empty string name")
        if not isinstance(config, dict):
            raise SystemExit(f"ERROR: MCP server {name!r} must contain an object")
        tools = config.get("tools")
        if tools is not None and not (
            isinstance(tools, list) and all(isinstance(tool, str) and tool for tool in tools)
        ):
            raise SystemExit(f"ERROR: MCP server {name!r} has a malformed tools allowlist")
    return servers


def json_document(value):
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def body_of(config):
    """The server config without the canonical-only `tools` allowlist."""
    return {key: value for key, value in config.items() if key != "tools"}


def is_remote(config):
    return "url" in config


# ── MCP renderers ─────────────────────────────────────────────────────────────
# Each takes the canonical servers dict and returns {relative path: content}.


def render_claude(servers):
    rendered = {}
    for name, config in servers.items():
        body = body_of(config)
        if is_remote(body):
            body.setdefault("type", "http")
        rendered[name] = body
    return {".mcp.json": json_document({"mcpServers": rendered})}


def render_cursor(servers):
    rendered = {}
    for name, config in servers.items():
        body = body_of(config)
        body.pop("type", None)
        rendered[name] = body
    return {".cursor/mcp.json": json_document({"mcpServers": rendered})}


def render_vscode(servers):
    # VS Code names the top-level key `servers` and wants an explicit type.
    rendered = {}
    for name, config in servers.items():
        body = body_of(config)
        body["type"] = "http" if is_remote(body) else "stdio"
        rendered[name] = body
    return {".vscode/mcp.json": json_document({"servers": rendered})}


def gemini_servers(servers):
    # Gemini CLI names streamable HTTP `httpUrl`, keeps `url` for SSE, and
    # spells the allowlist `includeTools`.
    rendered = {}
    for name, config in servers.items():
        body = body_of(config)
        transport = body.pop("type", None)
        if "url" in body and transport != "sse":
            body["httpUrl"] = body.pop("url")
        if config.get("tools"):
            body["includeTools"] = list(config["tools"])
        rendered[name] = body
    return rendered


def render_gemini(servers):
    # Merged into the committed .gemini/settings.json; handled as a seed.
    return {}


def render_qwen(servers):
    document = {
        "contextFileName": ["AGENTS.md", "QWEN.md"],
        "mcpServers": gemini_servers(servers),
    }
    return {".qwen/settings.json": json_document(document)}


def opencode_mcp(servers):
    rendered = {}
    for name, config in servers.items():
        if is_remote(config):
            entry = {"type": "remote", "url": config["url"]}
            if config.get("headers"):
                entry["headers"] = config["headers"]
        else:
            entry = {"type": "local", "command": [config["command"], *config.get("args", [])]}
            if config.get("env"):
                entry["environment"] = config["env"]
        rendered[name] = entry
    return rendered


def render_opencode(servers):
    return {"opencode.json": json_document({"mcp": opencode_mcp(servers)})}


def render_kilo(servers):
    return {"kilo.jsonc": json_document({"mcp": opencode_mcp(servers)})}


def render_factory(servers):
    rendered = {}
    for name, config in servers.items():
        body = body_of(config)
        body["type"] = body.get("type", "http" if is_remote(body) else "stdio")
        rendered[name] = body
    return {".factory/mcp.json": json_document({"mcpServers": rendered})}


def render_amp(servers):
    rendered = {name: body_of(config) for name, config in servers.items()}
    return {".amp/settings.json": json_document({"amp.mcpServers": rendered})}


def toml_key(value):
    if re.fullmatch(r"[A-Za-z0-9_-]+", value):
        return value
    return json.dumps(value, ensure_ascii=False)


def toml_value(value):
    if isinstance(value, str):
        # json.dumps escapes U+0000-U+001F but leaves U+007F raw, which TOML forbids.
        return json.dumps(value, ensure_ascii=False).replace("\x7f", "\\u007f")
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return repr(value)
    if isinstance(value, list):
        return "[" + ", ".join(toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        pairs = (f"{toml_key(key)} = {toml_value(item)}" for key, item in value.items())
        return "{ " + ", ".join(pairs) + " }"
    raise SystemExit(f"ERROR: unsupported TOML value in MCP config: {value!r}")


def codex_toml(servers):
    lines = ["# Generated by .agents/scripts/sync.py; do not edit."]
    for name, config in servers.items():
        lines.extend(("", f"[mcp_servers.{toml_key(name)}]"))
        for key, value in config.items():
            if key in ("type", "tools"):
                continue
            lines.append(f"{toml_key(key)} = {toml_value(value)}")
        if config.get("tools"):
            lines.append(f"enabled_tools = {toml_value(list(config['tools']))}")
    return "\n".join(lines) + "\n"


def render_codex(servers):
    # Codex loads a project .codex/config.toml only once the project is
    # trusted; `install-codex` covers the user-level config instead.
    return {".codex/config.toml": codex_toml(servers)}


MCP_RENDERERS = {
    "claude": render_claude,
    "codex": render_codex,
    "cursor": render_cursor,
    "gemini": render_gemini,
    "qwen": render_qwen,
    "opencode": render_opencode,
    "vscode": render_vscode,
    "kilo": render_kilo,
    "factory": render_factory,
    "amp": render_amp,
}


# ── Committed seeds: one managed key each, merged in place ────────────────────


def merged_document(path, key, value):
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        document = {}
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"ERROR: cannot read {path}: {exc}")
    if not isinstance(document, dict):
        raise SystemExit(f"ERROR: {path} must contain a JSON object")
    document[key] = value
    return json_document(document)


def seed_outputs(servers):
    """{path: expected content} for the committed files sync owns one key of.

    Claude Code ignores project MCP servers until they are opted into
    `enabledMcpjsonServers`; Gemini CLI keeps MCP servers inside its settings
    file. Both files are committed and hand-owned apart from that one key.
    """
    seeds = {
        REPO_ROOT / ".claude" / "settings.json": ("enabledMcpjsonServers", sorted(servers)),
        REPO_ROOT / ".gemini" / "settings.json": ("mcpServers", gemini_servers(servers)),
    }
    return {path: merged_document(path, key, value) for path, (key, value) in seeds.items()}


# ── Skill symlinks ────────────────────────────────────────────────────────────


def sync_skills(target_rel):
    target_dir = REPO_ROOT / target_rel
    target_dir.mkdir(parents=True, exist_ok=True)
    link_prefix = Path(os.path.relpath(SKILLS_ROOT, target_dir))

    for skill_dir in sorted(SKILLS_ROOT.iterdir()):
        if not skill_dir.is_dir():
            continue
        link_target = link_prefix / skill_dir.name
        link_path = target_dir / skill_dir.name
        if link_path.is_symlink():
            if os.readlink(link_path) == str(link_target):
                continue
            link_path.unlink()
        elif link_path.exists():
            raise SystemExit(f"ERROR: {link_path} exists but is not a symlink.")
        link_path.symlink_to(link_target)

    for link_path in target_dir.iterdir():
        if not link_path.is_symlink():
            continue
        resolved = Path(os.path.normpath(target_dir / os.readlink(link_path)))
        if resolved.parent == SKILLS_ROOT and not resolved.exists():
            link_path.unlink()


# ── Modes ─────────────────────────────────────────────────────────────────────


def atomic_write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(content)
        umask = os.umask(0)
        os.umask(umask)
        os.chmod(temporary, 0o666 & ~umask)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def active_harnesses(arguments):
    named = [argument for argument in arguments if not argument.startswith("-")]
    unknown = sorted(set(named) - set(HARNESSES) - set(NATIVE))
    if unknown:
        known = ", ".join([*HARNESSES, *NATIVE])
        raise SystemExit(f"ERROR: unknown harness {', '.join(unknown)}. Known: {known}")
    for name in named:
        if name in NATIVE:
            print(f"{name}: reads AGENTS.md and .agents/skills natively, nothing to generate")
    if "--all" in arguments or os.environ.get("GITHUB_ACTIONS") == "true":
        return list(HARNESSES)
    if named:
        return [name for name in named if name in HARNESSES]
    return [name for name, spec in HARNESSES.items() if detected(spec)]


def sync(arguments):
    servers = load_servers()
    for path, content in seed_outputs(servers).items():
        atomic_write(path, content)

    generated = []
    for name in active_harnesses(arguments):
        spec = HARNESSES[name]
        files = MCP_RENDERERS[spec["mcp"]](servers) if spec["mcp"] else {}
        for rel, content in files.items():
            atomic_write(REPO_ROOT / rel, content)
        if spec["skills"]:
            sync_skills(spec["skills"])
            files = {**files, spec["skills"] + "/": None}
        if files:
            generated.append(f"{name}: {', '.join(sorted(files))}")
    print("Synced committed seeds: .claude/settings.json, .gemini/settings.json")
    for line in generated:
        print(f"Generated {line}")
    if not generated and not any(not argument.startswith("-") for argument in arguments):
        print("No harnesses detected; run with --all or name one to force.")


def check():
    stale = []
    for path, expected in seed_outputs(load_servers()).items():
        try:
            current = path.read_text(encoding="utf-8")
        except OSError:
            current = None
        if current != expected:
            stale.append(path.relative_to(REPO_ROOT))
    if stale:
        print("Stale managed keys in committed seed files:", file=sys.stderr)
        for path in stale:
            print(f"  {path}", file=sys.stderr)
        print("Run .agents/scripts/sync.py to regenerate them.", file=sys.stderr)
        raise SystemExit(1)
    print("Managed keys in committed seed files are current.")


def list_harnesses():
    servers = load_servers()
    for name, spec in HARNESSES.items():
        adapters = []
        if spec["skills"]:
            adapters.append(f"skills → {spec['skills']}")
        if spec["mcp"]:
            targets = MCP_RENDERERS[spec["mcp"]](servers) or {".gemini/settings.json (seed)": None}
            adapters.append("mcp → " + ", ".join(targets))
        state = "detected" if detected(spec) else "not detected"
        print(f"{name:10} {state:13} {'; '.join(adapters)}")
    print(f"{'native':10} {'—':13} AGENTS.md + .agents/skills, no adapter: {', '.join(NATIVE)}")


def install_codex():
    repo_name = re.sub(r"[^A-Za-z0-9_-]+", "-", REPO_ROOT.name).strip("-") or "repo"
    begin = f"# BEGIN {repo_name} managed MCP"
    end = f"# END {repo_name} managed MCP"
    block = begin + "\n" + codex_toml(load_servers()) + end
    user_config = Path.home() / ".codex" / "config.toml"
    try:
        current = user_config.read_text(encoding="utf-8")
    except FileNotFoundError:
        current = ""
    pattern = re.compile(
        rf"(?ms)^[ \t]*{re.escape(begin)}\n.*?^[ \t]*{re.escape(end)}[ \t]*\n?"
    )
    current = re.sub(r"\n{3,}", "\n\n", pattern.sub("", current)).rstrip()
    merged = (current + "\n\n" if current else "") + block + "\n"
    atomic_write(user_config, merged)
    print(f"Installed managed MCP block: {user_config}")


def main(arguments):
    modes = {"check": check, "list": list_harnesses, "install-codex": install_codex}
    if arguments and arguments[0] in modes:
        if arguments[1:]:
            raise SystemExit(f"ERROR: {arguments[0]} takes no further arguments")
        modes[arguments[0]]()
    elif all(argument == "--all" or not argument.startswith("-") for argument in arguments):
        sync(arguments)
    else:
        print(__doc__, file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main(sys.argv[1:])
