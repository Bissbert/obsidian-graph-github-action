#!/usr/bin/env python3
"""Run the "Commit and Push Graph" step of action.yml in a throwaway repo.

The step's `run:` script is read from action.yml itself, so this checks the
step as it is committed. `git push` is replaced with `echo PUSH`, because
the throwaway repository has no remote. The script then runs the step twice:
once with a new graph, once with the same graph again, and prints the exit
code and output of each.

Standard library and `git` only; nothing outside the temporary directory is
touched.

    python3 tools/check_commit_step.py
"""

import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
STEP_NAME = "Commit and Push Graph"


def read_step(action: Path) -> str:
    """The `run: |` block of the named step, dedented."""
    lines = action.read_text().splitlines()
    start = next(i for i, l in enumerate(lines) if l.strip() == f"- name: {STEP_NAME}")
    run = next(i for i in range(start, len(lines)) if lines[i].strip() == "run: |")
    body = []
    for line in lines[run + 1:]:
        if line.strip().startswith("shell:"):
            break
        body.append(line)
    indent = min(len(l) - len(l.lstrip()) for l in body if l.strip())
    return "\n".join(l[indent:] for l in body)


def run(command: str, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", "-e", "-c", command], cwd=cwd, capture_output=True, text=True
    )


def show(label: str, result: subprocess.CompletedProcess) -> None:
    print(f"{label}: exit {result.returncode}")
    out = (result.stdout.strip() + "\n" + result.stderr.strip()).strip()
    print("   " + out.replace("\n", "\n   "))


def main() -> None:
    step = read_step(REPO / "action.yml").replace("git push", "echo PUSH")
    print("step from action.yml (git push replaced with echo PUSH):")
    print("   " + step.replace("\n", "\n   "))
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        run("git init -q . && git -c user.name=t -c user.email=t@e "
            "commit -q --allow-empty -m init", repo)

        (repo / "obsidian-graph.png").write_bytes(b"\x89PNG\r\n\x1a\n first")
        show("graph changed", run(step, repo))
        show("graph unchanged", run(step, repo))
        commits = run("git rev-list --count HEAD", repo).stdout.strip()
        print(f"commits in the throwaway repo: {commits} (init + 1)")


if __name__ == "__main__":
    main()
