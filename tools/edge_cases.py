#!/usr/bin/env python3
"""Run graph.py against the awkward cases and report what actually happens.

Each scenario builds a throwaway vault in a temporary directory, runs the
action's graph.py in it the way action.yml does, and records the exit code
plus one line of observed behaviour. Nothing is asserted about what *should*
happen - the point is to write down what does.

Requires the `graphviz` Python package and the Graphviz `dot` binary;
everything else is standard library.

    python3 tools/edge_cases.py
"""

import re
import struct
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def run_graph(vault: Path) -> subprocess.CompletedProcess:
    shutil.copy(REPO / "graph.py", vault / "graph.py")
    return subprocess.run(
        [sys.executable, "graph.py"], cwd=vault, capture_output=True, text=True
    )


def parsed(result: subprocess.CompletedProcess) -> tuple[int, int]:
    match = re.search(r"Total notes found: (\d+)\. Total edges found: (\d+)", result.stderr)
    return (int(match.group(1)), int(match.group(2))) if match else (-1, -1)


def png(vault: Path) -> str:
    path = vault / "obsidian-graph.png"
    if not path.exists():
        return "no PNG"
    data = path.read_bytes()
    width, height = struct.unpack(">II", data[16:24])
    return f"{len(data):,} B, {width}x{height} px"


def case(name: str, build) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        vault = Path(tmp) / "vault"
        vault.mkdir()
        build(vault)
        result = run_graph(vault)
        notes, edges = parsed(result)
        tail = result.stderr.strip().splitlines()[-1] if result.returncode else ""
        print(
            f"| {name} | {result.returncode} | "
            f"{notes if notes >= 0 else '-'} | {edges if edges >= 0 else '-'} | "
            f"{png(vault)} | {tail} |"
        )


def write(vault: Path, relative: str, body: str) -> None:
    path = vault / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body, encoding="utf-8")


def main() -> None:
    print("| Scenario | Exit | Notes | Edges | PNG | Error |")
    print("|---|---:|---:|---:|---|---|")

    case("empty vault, no Markdown at all", lambda v: None)

    case(
        "notes in hidden directories",
        lambda v: (
            write(v, "a.md", "[[b]]\n"),
            write(v, ".obsidian/plugin-notes.md", "[[hidden target]]\n"),
            write(v, ".github/PULL_REQUEST_TEMPLATE.md", "see [[Checklist]]\n"),
        ),
    )

    case(
        "same stem in two folders",
        lambda v: (
            write(v, "projects/Note.md", "[[Target]]\n"),
            write(v, "archive/Note.md", "[[Start]]\n"),
            write(v, "Target.md", ""),
            write(v, "Start.md", ""),
        ),
    )

    case(
        "note linking to itself",
        lambda v: write(v, "Ouroboros.md", "[[Ouroboros]]\n"),
    )

    case(
        "the same link twice in one note",
        lambda v: (write(v, "a.md", "[[b]] and again [[b]]\n"), write(v, "b.md", "")),
    )

    def latin1(vault: Path) -> None:
        write(vault, "ok.md", "[[b]]\n")
        (vault / "legacy.md").write_bytes("café [[b]]\n".encode("latin-1"))

    case("one file that is not UTF-8", latin1)

    case(
        "note name with a quote in it",
        lambda v: (write(v, 'He said "no".md', "[[b]]\n"), write(v, "b.md", "")),
    )


if __name__ == "__main__":
    main()
