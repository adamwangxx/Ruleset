#!/usr/bin/env python3
"""Rebuild DivineEngine/AI.list from RuleGo plus DivineEngine/AI.local.list."""

from pathlib import Path
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_URL = (
    "https://raw.githubusercontent.com/ConnersHua/RuleGo/refs/heads/master/"
    "Surge/Ruleset/Extra/AI.list"
)
LIST_PATH = ROOT / "DivineEngine" / "AI.list"
PIN_PATH = ROOT / "DivineEngine" / "AI.local.list"
HEADER = """# Source
# https://raw.githubusercontent.com/ConnersHua/RuleGo/refs/heads/master/Surge/Ruleset/Extra/AI.list
# https://github.com/scomper/surge-list/blob/master/openai.list
"""


def parse_rules(text):
    rules = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        rules.append(stripped)
    return rules


def fetch_upstream():
    request = urllib.request.Request(
        UPSTREAM_URL,
        headers={"User-Agent": "ruleset-sync"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        text = response.read().decode("utf-8")
    if "<html" in text[:200].lower() or not parse_rules(text):
        raise SystemExit(f"upstream did not return a ruleset: {UPSTREAM_URL}")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def render(upstream, pins):
    seen = set(parse_rules(upstream))
    local = []
    for rule in parse_rules(pins):
        if rule in seen:
            continue
        seen.add(rule)
        local.append(rule)

    parts = [HEADER.rstrip(), "", upstream.strip()]
    if local:
        parts.extend(["", "# Local", *local])
    return "\n".join(parts) + "\n"


def main():
    upstream = fetch_upstream()
    pins = PIN_PATH.read_text(encoding="utf-8")
    current = LIST_PATH.read_text(encoding="utf-8") if LIST_PATH.exists() else ""
    updated = render(upstream, pins)

    current_count = len(parse_rules(current))
    updated_count = len(parse_rules(updated))
    if current_count and updated_count < current_count * 0.5:
        raise SystemExit(
            f"refusing to shrink AI.list from {current_count} to {updated_count} rules"
        )

    if updated == current:
        print("AI.list unchanged")
        return

    LIST_PATH.write_text(updated, encoding="utf-8")
    print(f"AI.list updated ({current_count} -> {updated_count} rules)")


if __name__ == "__main__":
    main()
