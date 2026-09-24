[← back to the overview](../README.md)

# Bugs found

Both bugs below are fixed on `main`. Each was re-checked in the `ubuntu:24.04`
container described in [How this was measured](measurement.md).

| # | Bug | Status |
|---|---|---|
| 1 | Unchanged output made the action fail | Fixed in [`fbbea03`](https://github.com/Bissbert/obsidian-graph-github-action/commit/fbbea03) |
| 2 | PNG layout depended on set iteration order | Fixed in [`ba5e711`](https://github.com/Bissbert/obsidian-graph-github-action/commit/ba5e711) |

An old quick-start example used `@v1`, a tag that does not exist. That was a
documentation error, not a code bug; the README now pins `@0.1.6`.

## 1. Unchanged output made the action fail

**Status:** fixed in [`fbbea03`](https://github.com/Bissbert/obsidian-graph-github-action/commit/fbbea03).

**Location:** `action.yml`, step "Commit and Push Graph".

**What happened:** the step staged `obsidian-graph.png` and always ran
`git commit`. When the PNG was unchanged, Git printed `nothing to commit,
working tree clean` and exited 1, and the job failed.

**What changed:** the step now checks `git diff --cached --quiet --
obsidian-graph.png` first and exits 0 when nothing changed. The commit is also
limited to the image path.

**Check:** [`tools/check_commit_step.py`](../tools/check_commit_step.py)
reads the step from `action.yml`, replaces `git push` with `echo PUSH`, and runs
it twice in a throwaway repository:

```
graph changed: exit 0
   [master f56e395] Update Obsidian graph
    1 file changed, 3 insertions(+)
    create mode 100644 obsidian-graph.png
   PUSH
graph unchanged: exit 0
   Obsidian graph is unchanged; skipping commit
commits in the throwaway repo: 2 (init + 1)
```

## 2. PNG layout depended on set iteration order

**Status:** fixed in [`ba5e711`](https://github.com/Bissbert/obsidian-graph-github-action/commit/ba5e711).

**Location:** `graph.py`, `create_graph()`.

**What happened:** notes and edges are collected in sets and were handed to
Graphviz in set iteration order. String hashing is randomized per process, so
the same vault could produce a different layout and different PNG bytes on
each run, and the action would commit a new image even when no note changed.

**What changed:** both loops now iterate `sorted(notes)` and `sorted(edges)`.

**Check:** render the demo vaults under two hash seeds and compare:

```sh
PYTHONHASHSEED=0 python3 tools/render_media.py --outdir /tmp/seed0
PYTHONHASHSEED=1 python3 tools/render_media.py --outdir /tmp/seed1
sha256sum /tmp/seed0/*.png /tmp/seed1/*.png
```

```
705cdccb0e977b6f223e929c8ae5aa19748c8a49ee16065cf037a24b6bea3bd1  seed0/link-forms.png
a284185461900f59953d86331aac876ed9d19eae2af5598b5e5ce897448c6eaa  seed0/sample-graph.png
705cdccb0e977b6f223e929c8ae5aa19748c8a49ee16065cf037a24b6bea3bd1  seed1/link-forms.png
a284185461900f59953d86331aac876ed9d19eae2af5598b5e5ce897448c6eaa  seed1/sample-graph.png
identical
```
