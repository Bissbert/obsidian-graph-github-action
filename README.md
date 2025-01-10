# Obsidian Graph Action

**Obsidian Graph Action** is a composite GitHub Action that scans all `.md` (Markdown) files in your repository for `[[wikilink]]` references and generates a PNG graph (named `obsidian-graph.png`) using [Graphviz](https://graphviz.org/).

## How it Works

1. **Searches for Markdown files:** All `.md` files in your repository are found (including subdirectories).
2. **Extracts `[[links]]`:** The action parses these files to identify any `[[wikilink]]` references.
3. **Builds a GraphViz diagram:** Each Markdown file becomes a node, and each `[[link]]` becomes an edge.
4. **Outputs `obsidian-graph.png`:** A PNG graph is generated and committed back to your repository.

---

## Usage

### 1. Set Up Your Repository

1. Ensure your repository contains Markdown files (`.md`) that you want to graph.
2. Make sure your repository allows GitHub Actions (in the repo settings).

### 2. Create or Update Your Workflow File

Create a new file at `.github/workflows/generate-graph.yml` in your target repository (or add a job to an existing workflow):

```yaml
name: Generate Obsidian Graph

on:
  push:
    branches:
      - main

# IMPORTANT: "contents: write" is needed so the action can commit the generated PNG.
permissions:
  contents: write

jobs:
  generate-graph:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Obsidian Graph
        uses: <bissbert/obsidian-graph-github-action>@v1
        with:
          python-version: "3.x"  # optional, defaults to "3.x"
```

optionally replace @v1 with the appropriate release tag or commit SHA.

3. Push Your Changes

Every time you push changes to the main branch, GitHub Actions will:
	1.	Check out your repository.
	2.	Install Python and graphviz.
	3.	Parse all .md files, generating a visual graph of your notes.
	4.	Commit and push obsidian-graph.png back to your repository.

## Inputs

| Name            | Description                             | Required | Default |
|-----------------|-----------------------------------------|----------|---------|
| python-version  | Python version to install (e.g. 3.9, 3.x) | No       | 3.x     |

## Outputs

None. The generated image obsidian-graph.png is committed directly to your repository.

## Example

Here’s a minimal example of how you might wire up this action:

```yaml
name: Generate Obsidian Graph

on:
  workflow_dispatch:

permissions:
  contents: write

jobs:
  generate-graph:
    runs-on: ubuntu-latest
    steps:
      - name: Generate Obsidian Graph
        uses: <bissbert/obsidian-graph-github-action>@v1
        with:
          python-version: "3.9"

```

Run it manually (using the workflow_dispatch event) or whenever you push to main if you prefer. After it completes, look for obsidian-graph.png in your repository.

## Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page.
	1.	Fork the repository
	2.	Create your feature branch (git checkout -b feature/your-feature)
	3.	Commit your changes (git commit -m 'Add your feature')
	4.	Push to the branch (git push origin feature/your-feature)
	5.	Open a Pull Request

## License

This repository is licensed under the MIT License.

Feel free to adapt the license section if you use a different licence.

Happy graphing! If you have any questions, please open an issue in this repository.
