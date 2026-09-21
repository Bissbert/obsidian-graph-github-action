#!/usr/bin/env python3
"""Write one of the demo vaults used by the documentation.

Two variants exist:

  hero        a small, tidy vault with plain [[wikilinks]] only. Rendered as
              media/sample-graph.png, the image at the top of the README.
  link-forms  a deliberately messy vault that contains every link form
              Obsidian understands. Rendered as media/link-forms.png, the
              image in docs/graph-generation.md that shows how graph.py
              treats each of them.

Standard library only.

    python3 tools/sample_vault.py <outdir> [--variant hero|link-forms]
"""

import argparse
import shutil
from pathlib import Path

HERO = {
    "index.md": """# Index

The entry point of the vault.

- [[Zettelkasten]] - the method
- [[Graph View]] - what this action renders
- [[Daily Notes]] - the journal
- [[Reading List]] - what is on the pile
""",
    "concepts/Zettelkasten.md": """# Zettelkasten

A slip box of [[Atomic Notes]] held together by [[Linking]].
Popularised by [[Luhmann]].
""",
    "concepts/Atomic Notes.md": """# Atomic Notes

One idea per note. The idea only becomes useful through [[Linking]].
""",
    "concepts/Linking.md": """# Linking

An explicit wikilink from one note to another. Reading the links backwards
gives [[Backlinks]]; reading all of them at once gives the [[Graph View]].
""",
    "concepts/Backlinks.md": """# Backlinks

Every inbound link. The [[Graph View]] is the same information drawn as a
picture.
""",
    "concepts/Graph View.md": """# Graph View

Notes as nodes, [[Linking]] as edges.
""",
    "sources/Luhmann.md": """# Luhmann

Niklas Luhmann, who filled a [[Zettelkasten]] with roughly 90,000 slips.
See the [[Reading List]].
""",
    "sources/Reading List.md": """# Reading List

- [[How to Take Smart Notes]]
- Anything about [[Luhmann]]
""",
    "sources/How to Take Smart Notes.md": """# How to Take Smart Notes

Sonke Ahrens on the [[Zettelkasten]] and why notes should be
[[Atomic Notes]].
""",
    "daily/Daily Notes.md": """# Daily Notes

A note per day. They all point back at the [[index]].
""",
    "daily/2024-05-01.md": """# 2024-05-01

Set up the vault. See [[Daily Notes]].
Started reading about the [[Zettelkasten]].
""",
    "daily/2024-05-02.md": """# 2024-05-02

See [[Daily Notes]].
Added two items to the [[Reading List]] and finally understood
[[Backlinks]].
""",
    "templates/Note Template.md": """# Title

Body. No links yet - this note is deliberately isolated.
""",
}

LINK_FORMS = {
    "Start.md": """# Start

A plain link:            [[Target]]
An alias:                [[Target|the target note]]
A heading link:          [[Target#Origins]]
A block reference:       [[Target#^a1b2c3]]
An embed:                ![[Diagram.png]]
A link to nothing:       [[Not Yet Written]]

And one inside a code span, which is not a link at all: `[[Example]]`
""",
    "Target.md": """# Target

## Origins

The note everything above points at. ^a1b2c3
""",
    "projects/Note.md": """# Note

Two files share this stem on purpose. This one links to [[Target]].
""",
    "archive/Note.md": """# Note

The second file with the stem `Note`. It links to [[Start]].
""",
}

VARIANTS = {"hero": HERO, "link-forms": LINK_FORMS}


def write_vault(outdir: Path, variant: str) -> int:
    files = VARIANTS[variant]
    if outdir.exists():
        shutil.rmtree(outdir)
    for relative, body in files.items():
        path = outdir / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding="utf-8")
    return len(files)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("outdir", type=Path)
    parser.add_argument("--variant", choices=sorted(VARIANTS), default="hero")
    args = parser.parse_args()
    count = write_vault(args.outdir, args.variant)
    print(f"wrote {count} markdown files to {args.outdir} (variant: {args.variant})")


if __name__ == "__main__":
    main()
