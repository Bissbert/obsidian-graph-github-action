#!/usr/bin/env python3
"""Generate the reference tables in docs/action-reference.md from action.yml.

Standard library only, so there is no PyYAML here: the parser below understands
the small subset of YAML that action.yml actually uses - two levels of mappings
under `inputs:`, and a list of steps under `runs: steps:` where every step has a
`name` and either `uses` or `run`. It is not a general YAML parser and will
complain if action.yml grows past that shape.

    python3 tools/action_reference.py [--action action.yml]

Prints Markdown: the metadata line, the inputs table, the outputs table and the
step table.
"""

import argparse
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def top_level_blocks(text: str) -> dict[str, list[str]]:
    """Split the file into top-level keys and their indented line blocks."""
    blocks: dict[str, list[str]] = {}
    current = None
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.match(r"^(\w[\w-]*):\s*(.*)$", line)
        if match:
            current = match.group(1)
            blocks[current] = []
            if match.group(2).strip():
                blocks[current].append(match.group(2))
            continue
        if current is not None:
            blocks[current].append(line)
    return blocks


def parse_inputs(lines: list[str]) -> list[dict[str, str]]:
    inputs: list[dict[str, str]] = []
    for line in lines:
        indent = len(line) - len(line.lstrip())
        stripped = line.strip()
        if indent == 2 and stripped.endswith(":"):
            inputs.append({"name": stripped[:-1]})
        elif indent == 4 and ":" in stripped and inputs:
            key, _, value = stripped.partition(":")
            inputs[-1][key.strip()] = strip_quotes(value)
    return inputs


def parse_steps(lines: list[str]) -> list[dict[str, str]]:
    steps: list[dict[str, str]] = []
    in_run = False
    for line in lines:
        stripped = line.strip()
        indent = len(line) - len(line.lstrip())
        if stripped.startswith("- name:"):
            steps.append({"name": strip_quotes(stripped[len("- name:"):]), "run": ""})
            in_run = False
        elif not steps:
            continue
        elif stripped.startswith("uses:"):
            steps[-1]["uses"] = strip_quotes(stripped[len("uses:"):])
            in_run = False
        elif stripped in ("run: |", "run: |-"):
            in_run = True
        elif stripped.startswith("run:"):
            steps[-1]["run"] = strip_quotes(stripped[len("run:"):])
            in_run = False
        elif in_run and indent >= 8:
            steps[-1]["run"] += ("\n" if steps[-1]["run"] else "") + stripped
        elif stripped.startswith("shell:") or stripped.startswith("with:"):
            in_run = False
    return steps


def render(action: Path) -> str:
    text = action.read_text(encoding="utf-8")
    blocks = top_level_blocks(text)
    out: list[str] = []

    name = strip_quotes(blocks.get("name", [""])[0])
    description = strip_quotes(blocks.get("description", [""])[0])
    using = "unknown"
    for line in blocks.get("runs", []):
        if line.strip().startswith("using:"):
            using = strip_quotes(line.split(":", 1)[1])
    out.append(f"**{name}** - {description} Runs as a `{using}` action.\n")

    out.append("## Inputs\n")
    inputs = parse_inputs(blocks.get("inputs", []))
    if inputs:
        out.append("| Name | Description | Required | Default |")
        out.append("|---|---|:--:|---|")
        for item in inputs:
            default = item.get("default", "")
            out.append(
                f"| `{item['name']}` | {item.get('description', '')} | "
                f"{item.get('required', 'false')} | "
                f"{'`' + default + '`' if default else '-'} |"
            )
    else:
        out.append("None.")
    out.append("")

    out.append("## Outputs\n")
    outputs = parse_inputs(blocks.get("outputs", []))
    if outputs:
        out.append("| Name | Description |")
        out.append("|---|---|")
        for item in outputs:
            out.append(f"| `{item['name']}` | {item.get('description', '')} |")
    else:
        out.append(
            "None. `action.yml` declares no `outputs:` block, so nothing can be\n"
            "read with `steps.<id>.outputs.*`. The result is the committed\n"
            "`obsidian-graph.png`."
        )
    out.append("")

    out.append("## Steps\n")
    out.append("| # | Step | Runs |")
    out.append("|---:|---|---|")
    for number, step in enumerate(parse_steps(blocks.get("runs", [])), start=1):
        if "uses" in step:
            runs = f"`{step['uses']}`"
        else:
            runs = "<br/>".join(f"`{line}`" for line in step["run"].splitlines())
        out.append(f"| {number} | {step['name']} | {runs} |")
    out.append("")
    return "\n".join(out)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--action", type=Path, default=REPO / "action.yml")
    args = parser.parse_args()
    print(render(args.action))


if __name__ == "__main__":
    main()
