#!/usr/bin/env python3
"""Check the packaging and the rules for what can go in this public repo."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PLUGIN = REPO / "plugins" / "stevens"
PLUGIN_PATH = "./plugins/stevens"

# Tools that exist in only one agent. Skills have to work in all of them.
AGENT_ONLY_TOOLS = re.compile(r"\b(AskUserQuestion|EnterWorktree|ExitWorktree)\b")
# This repo is public, so machine addresses stay out. Loopback addresses are fine.
IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
ALLOWED_IPS = {"127.0.0.1", "0.0.0.0"}
# Skill-relative files named in backticks, such as `dragonair.md`.
SKILL_FILE_REF = re.compile(r"`([\w-]+\.md)`")
TEXT_SUFFIXES = {".md", ".json", ".yml", ".yaml", ".sh", ".py", ".toml", ""}

failures: list[str] = []


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def frontmatter(text: str) -> dict[str, str]:
    lines = text.splitlines()
    if not lines or lines[0] != "---" or "---" not in lines[1:]:
        return {}
    fields = {}
    for line in lines[1 : lines.index("---", 1)]:
        key, separator, value = line.partition(":")
        if separator:
            fields[key.strip()] = value.strip()
    return fields


def parse_version(value: str) -> tuple[int, int, int]:
    if not re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.0", value):
        raise ValueError("version must be major.minor.0 (no patch-only releases)")
    major, minor, patch = value.split(".")
    return int(major), int(minor), int(patch)


def check_version_bump(base: str) -> None:
    manifest = "plugins/stevens/.codex-plugin/plugin.json"
    previous = json.loads(subprocess.check_output(
        ["git", "show", f"{base}:{manifest}"], cwd=REPO, text=True
    ))
    # Releases before versioned manifests used the repository's v0.1.0 tag.
    old = parse_version(previous.get("version", "0.1.0"))
    new = parse_version(load_json(REPO / manifest)["version"])
    if not (new == (old[0], old[1] + 1, 0) or new == (old[0] + 1, 0, 0)):
        failures.append(f"bump the minor or major version from {'.'.join(map(str, old))}")


def check_packaging() -> None:
    claude_market = load_json(REPO / ".claude-plugin" / "marketplace.json")
    codex_market = load_json(REPO / ".agents" / "plugins" / "marketplace.json")
    if claude_market["name"] != codex_market["name"]:
        failures.append("the Claude and Codex marketplaces must have the same name")
    if claude_market["plugins"][0]["source"] != PLUGIN_PATH:
        failures.append(f"the Claude marketplace must point at {PLUGIN_PATH}")
    if codex_market["plugins"][0]["source"]["path"] != PLUGIN_PATH:
        failures.append(f"the Codex marketplace must point at {PLUGIN_PATH}")

    for manifest in (PLUGIN / ".claude-plugin" / "plugin.json", PLUGIN / ".codex-plugin" / "plugin.json"):
        data = load_json(manifest)
        name = manifest.relative_to(REPO)
        if data.get("name") != "stevens":
            failures.append(f"{name}: the plugin must be named stevens")
        try:
            parse_version(data.get("version", ""))
        except ValueError as error:
            failures.append(f"{name}: {error}")
    claude = load_json(PLUGIN / ".claude-plugin/plugin.json")
    codex = load_json(PLUGIN / ".codex-plugin/plugin.json")
    if claude.get("version") != codex.get("version"):
        failures.append("both plugin manifests must have the same version")
    changelog = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    if not changelog.startswith(f"# Changelog\n\n## {codex.get('version')}\n"):
        failures.append("CHANGELOG.md must begin with the current version")


def check_skills() -> None:
    skill_dirs = sorted(path for path in (PLUGIN / "skills").iterdir() if path.is_dir())
    if not skill_dirs:
        failures.append("no skills found")
    for skill_dir in skill_dirs:
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            failures.append(f"{skill_dir.name}: missing SKILL.md")
            continue
        text = skill_file.read_text(encoding="utf-8")
        fields = frontmatter(text)
        if fields.get("name") != skill_dir.name:
            failures.append(f"{skill_dir.name}: frontmatter name must match its folder")
        if not fields.get("description"):
            failures.append(f"{skill_dir.name}: needs a description")
        codex_policy = skill_dir / "agents" / "openai.yaml"
        codex_manual = codex_policy.exists() and "allow_implicit_invocation: false" in codex_policy.read_text(encoding="utf-8")
        if (fields.get("disable-model-invocation") == "true") != codex_manual:
            failures.append(
                f"{skill_dir.name}: disable-model-invocation: true (Claude) and "
                "agents/openai.yaml with allow_implicit_invocation: false (Codex) must be set together"
            )
        for reference in sorted(set(SKILL_FILE_REF.findall(text))):
            if not (skill_dir / reference).exists():
                failures.append(f"{skill_dir.name}: SKILL.md names a missing file, {reference}")
        for path in skill_dir.rglob("*.md"):
            match = AGENT_ONLY_TOOLS.search(path.read_text(encoding="utf-8"))
            if match:
                failures.append(f"{path.relative_to(REPO)}: names {match.group()}, which only one agent has")


def check_public_content() -> None:
    for path in REPO.rglob("*"):
        if ".git" in path.parts or not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        for address in IPV4.findall(path.read_text(encoding="utf-8", errors="ignore")):
            if address not in ALLOWED_IPS:
                failures.append(f"{path.relative_to(REPO)}: contains the IP address {address}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="Git ref before this change; require a major/minor bump")
    args = parser.parse_args()
    check_packaging()
    if args.base:
        try:
            check_version_bump(args.base)
        except (ValueError, KeyError, subprocess.CalledProcessError) as error:
            failures.append(f"cannot validate version bump: {error}")
    check_skills()
    check_public_content()
    if failures:
        print("Validation failed:", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
