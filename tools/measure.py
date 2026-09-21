#!/usr/bin/env python3
"""Measure graph.py: what it finds, how long it takes, how big the PNG gets.

Two benchmarks:

  demo   the two vaults from tools/sample_vault.py - notes, nodes, edges and
         the size of the PNG that ends up in media/.
  scale  synthetic vaults of 10, 50, 100, 500 and 1,000 notes with three
         outgoing links each, to show how the run time and the image split
         between parsing and rendering.

Every row is produced by running the action's own graph.py, the same way
action.yml runs it. Requires the `graphviz` Python package and the Graphviz
`dot` binary; everything else is standard library.

    python3 tools/measure.py [--sizes 10,50,100,500,1000] [--repeats 3]
"""

import argparse
import importlib.util
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import sample_vault

REPO = Path(__file__).resolve().parent.parent


def load_graph_module():
    """Import the action's graph.py without running it."""
    spec = importlib.util.spec_from_file_location("action_graph", REPO / "graph.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def png_size(path: Path) -> tuple[int, int]:
    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", header[16:24])


def synthetic_vault(vault: Path, notes: int, links: int = 3) -> None:
    vault.mkdir(parents=True, exist_ok=True)
    for i in range(notes):
        targets = "\n".join(
            f"- [[note-{(i * 7 + step * 13 + 1) % notes:04d}]]"
            for step in range(links)
        )
        (vault / f"note-{i:04d}.md").write_text(
            f"# note-{i:04d}\n\n{targets}\n", encoding="utf-8"
        )


def run_graph(vault: Path) -> float:
    """Run graph.py in the vault the way action.yml does. Returns seconds."""
    shutil.copy(REPO / "graph.py", vault / "graph.py")
    start = time.perf_counter()
    subprocess.run(
        [sys.executable, "graph.py"], cwd=vault, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    return time.perf_counter() - start


def time_parse(graph_module, vault: Path, repeats: int) -> tuple[float, int, int]:
    """Time parse_vault() alone, from inside the vault."""
    cwd = Path.cwd()
    best = None
    try:
        import os

        os.chdir(vault)
        for _ in range(repeats):
            start = time.perf_counter()
            notes, edges = graph_module.parse_vault()
            taken = time.perf_counter() - start
            best = taken if best is None else min(best, taken)
    finally:
        import os

        os.chdir(cwd)
    nodes = len(notes | {b for _, b in edges})
    return best, nodes, len(edges)


def bench_demo(graph_module, repeats: int) -> None:
    print("## Demo vaults\n")
    print("| Vault | Files | Nodes | Edges | PNG | Pixels |")
    print("|---|---:|---:|---:|---:|---|")
    for variant, image in (("hero", "sample-graph.png"), ("link-forms", "link-forms.png")):
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            files = sample_vault.write_vault(vault, variant)
            _, nodes, edges = time_parse(graph_module, vault, repeats)
            run_graph(vault)
            png = vault / "obsidian-graph.png"
            width, height = png_size(png)
            print(
                f"| `{variant}` | {files} | {nodes} | {edges} | "
                f"{png.stat().st_size / 1024:.1f} KB | {width}x{height} |"
            )
    print()


def bench_scale(graph_module, sizes: list[int], repeats: int) -> None:
    print("## Synthetic vaults, three links per note\n")
    print("| Notes | Nodes | Edges | Parse | Full run | PNG | Pixels |")
    print("|---:|---:|---:|---:|---:|---:|---|")
    for size in sizes:
        with tempfile.TemporaryDirectory() as tmp:
            vault = Path(tmp) / "vault"
            synthetic_vault(vault, size)
            parse, nodes, edges = time_parse(graph_module, vault, repeats)
            run = min(run_graph(vault) for _ in range(repeats))
            png = vault / "obsidian-graph.png"
            width, height = png_size(png)
            print(
                f"| {size:,} | {nodes:,} | {edges:,} | {parse * 1000:.1f} ms | "
                f"{run:.2f} s | {png.stat().st_size / 1024:.0f} KB | {width}x{height} |"
            )
    print()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", default="10,50,100,500,1000")
    parser.add_argument("--repeats", type=int, default=3)
    args = parser.parse_args()

    dot = subprocess.run(
        ["dot", "-V"], capture_output=True, text=True, check=True
    ).stderr.strip()
    print(f"python {platform.python_version()} on {platform.platform()}")
    print(f"{dot}\n")
    print("Best of", args.repeats, "runs.\n")

    graph_module = load_graph_module()
    bench_demo(graph_module, args.repeats)
    bench_scale(graph_module, [int(s) for s in args.sizes.split(",")], args.repeats)


if __name__ == "__main__":
    main()
