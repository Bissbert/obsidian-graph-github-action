#!/usr/bin/env python3
"""Render the images in media/ by running the action's own graph.py.

Nothing here draws anything by hand. For each demo vault the script

  1. writes the vault with tools/sample_vault.py,
  2. copies graph.py into it, exactly as the "Copy graph.py to target
     repository" step of action.yml does,
  3. runs `python graph.py` there with the current interpreter,
  4. copies the resulting obsidian-graph.png into media/.

Requires the `graphviz` Python package and the Graphviz `dot` binary, which
are the action's own dependencies. Everything else is standard library.

    python3 tools/render_media.py [--outdir media]
"""

import argparse
import shutil
import struct
import subprocess
import sys
import tempfile
from pathlib import Path

import sample_vault

REPO = Path(__file__).resolve().parent.parent
TARGETS = [("hero", "sample-graph.png"), ("link-forms", "link-forms.png")]


def png_size(path: Path) -> tuple[int, int]:
    """Width and height from the IHDR chunk of a PNG."""
    header = path.read_bytes()[:24]
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    return struct.unpack(">II", header[16:24])


def render(variant: str, outfile: Path) -> None:
    with tempfile.TemporaryDirectory() as tmp:
        vault = Path(tmp) / "vault"
        notes = sample_vault.write_vault(vault, variant)
        shutil.copy(REPO / "graph.py", vault / "graph.py")
        subprocess.run(
            [sys.executable, "graph.py"], cwd=vault, check=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        )
        produced = vault / "obsidian-graph.png"
        outfile.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(produced, outfile)
    width, height = png_size(outfile)
    print(
        f"{outfile}: {notes} notes -> {width}x{height} px, "
        f"{outfile.stat().st_size:,} bytes"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", type=Path, default=REPO / "media")
    args = parser.parse_args()
    for variant, filename in TARGETS:
        render(variant, args.outdir / filename)


if __name__ == "__main__":
    main()
