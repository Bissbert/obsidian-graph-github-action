import re
from pathlib import Path
from graphviz import Digraph

# Define the output file
OUTPUT_FILE = "obsidian-graph"

# Parse Markdown files in the current directory
def parse_vault():
    edges = set()
    notes = set()
    for md_file in Path(".").glob("**/*.md"):
        content = md_file.read_text(encoding="utf-8")
        note_name = md_file.stem
        notes.add(note_name)
        # Extract [[links]] using regex
        links = re.findall(r"\[\[([^\]]+)\]\]", content)
        for link in links:
            edges.add((note_name, link))
    return notes, edges

# Generate the graph
def create_graph(notes, edges, output_file):
    dot = Digraph(format="png")
    dot.attr("graph", rankdir="LR")  # Horizontal layout
    dot.attr("node", shape="ellipse", style="filled", color="lightblue", fontname="Arial")
    dot.attr("edge", color="gray", fontname="Arial")

    # Add nodes
    for note in notes:
        dot.node(note)

    # Add edges
    for note_a, note_b in edges:
        dot.edge(note_a, note_b)

    # Render graph
    dot.render(output_file, cleanup=True)

if __name__ == "__main__":
    notes, edges = parse_vault()
    create_graph(notes, edges, OUTPUT_FILE)
    print(f"Graph saved as {OUTPUT_FILE}.png")