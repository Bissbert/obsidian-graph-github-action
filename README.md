# obsidian-graph-github-action

![GitHub last commit](https://img.shields.io/github/last-commit/Bissbert/obsidian-graph-github-action)

> GitHub Action that scans a repository for Obsidian-style `[[wikilinks]]` and commits a rendered PNG graph back to the repo on every push.

## Why

Obsidian's local graph view is only visible inside the desktop app. This action makes your note graph a first-class CI artefact: every push regenerates `obsidian-graph.png` and commits it back, so the graph is always browsable on GitHub without opening Obsidian. Useful for knowledge bases, wikis, or any Markdown repo where link topology matters.

## Quick start

Create `.github/workflows/generate-graph.yml` in your target repository:

```yaml
name: Generate Obsidian Graph

on:
  push:
    branches:
      - main

permissions:
  contents: write

jobs:
  generate-graph:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Obsidian Graph
        uses: Bissbert/obsidian-graph-github-action@v1
        with:
          python-version: "3.x"   # optional, defaults to "3.x"
```

After the workflow runs, `obsidian-graph.png` appears in the root of your repository.

## How it works

The action is a composite action defined in `action.yml`:

1. Checks out the target repository (`actions/checkout`).
2. Installs Python (`actions/setup-python`) and the `graphviz` Python package plus the system `graphviz` binary via `apt-get`.
3. Copies `graph.py` from the action's own directory into the workspace.
4. `graph.py` walks all `.md` files, extracts `[[wikilink]]` references with a regex, builds a directed graph where each note is a node and each link is an edge, and renders it to `obsidian-graph.png` via the Graphviz `dot` renderer.
5. Commits and pushes `obsidian-graph.png` back to the branch using the `github-actions[bot]` identity.

Dependencies: Python 3, `graphviz` pip package, `graphviz` system package (installed automatically by the action).

## Inputs

| Name | Required | Default | Description |
|---|---|---|---|
| `python-version` | No | `3.x` | Python version passed to `actions/setup-python` |

## Outputs

None. The generated `obsidian-graph.png` is committed directly to the repository.

## Status

Stable.

## License

MIT
