#!/usr/bin/env python3
"""Reproduce the "Commit and Push Graph" step of action.yml locally.

The step is

    git config user.name "github-actions[bot]"
    git config user.email "github-actions@github.com"
    git add obsidian-graph.png
    git commit -m "Update Obsidian graph"
    git push

with no `--allow-empty` and no guard. This script builds a throwaway
repository in a temporary directory, runs everything up to (not including)
`git push` twice - once with a changed graph, once with an unchanged one -
and prints the exit code and output of each. It proves what the step does
when a push produces no diff.

Standard library and `git` only; nothing outside the temporary directory is
touched.

    python3 tools/check_commit_step.py
"""

import subprocess
import tempfile
from pathlib import Path

STEP = """
git config user.name "github-actions[bot]"
git config user.email "github-actions@github.com"
git add obsidian-graph.png
git commit -m "Update Obsidian graph"
"""


def run(command: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "-e", "-c", command], cwd=cwd, capture_output=True, text=True
    )


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        run("git init -q . && git commit -q --allow-empty -m init "
            "--author='t <t@e>' ", repo)
        run("git config user.email t@e && git config user.name t", repo)

        (repo / "obsidian-graph.png").write_bytes(b"\x89PNG\r\n\x1a\n first")
        first = run(STEP, repo)
        print(f"graph changed:   exit {first.returncode}")
        print("   " + first.stdout.strip().replace("\n", "\n   "))

        second = run(STEP, repo)
        print(f"graph unchanged: exit {second.returncode}")
        print("   " + (second.stdout.strip() or second.stderr.strip())
              .replace("\n", "\n   "))


if __name__ == "__main__":
    main()
