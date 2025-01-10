import re
import logging
from pathlib import Path
from graphviz import Digraph

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Define the output file
OUTPUT_FILE = "obsidian-graph"

# Parse Markdown files in the current directory
def parse_vault():
    logger.info("Starting to parse markdown files in the current directory...")
    edges = set()
    notes = set()
    
    for md_file in Path(".").glob("**/*.md"):
        logger.debug(f"Reading file: {md_file}")
        content = md_file.read_text(encoding="utf-8")
        note_name = md_file.stem
        notes.add(note_name)
        # Extract [[links]] using regex
        links = re.findall(r"\[\[([^\]]+)\]\]", content)
        for link in links:
            logger.debug(f"Found link from '{note_name}' to '{link}'")
            edges.add((note_name, link))
    
    logger.info(f"Finished parsing. Total notes found: {len(notes)}. Total edges found: {len(edges)}.")
    return notes, edges

# Generate the graph
def create_graph(notes, edges, output_file):
    logger.info(f"Creating GraphViz Digraph and setting layout for output file: {output_file}.")
    dot = Digraph(format="png")
    dot.attr("graph", rankdir="LR")  # Horizontal layout
    dot.attr("node", shape="ellipse", style="filled", color="lightblue", fontname="Arial")
    dot.attr("edge", color="gray", fontname="Arial")

    # Add nodes
    for note in notes:
        logger.debug(f"Adding node: {note}")
        dot.node(note)

    # Add edges
    for note_a, note_b in edges:
        logger.debug(f"Adding edge from '{note_a}' to '{note_b}'")
        dot.edge(note_a, note_b)

    # Render graph
    logger.info(f"Rendering the graph to file: {output_file}.png")
    dot.render(output_file, cleanup=True)

if __name__ == "__main__":
    notes, edges = parse_vault()
    create_graph(notes, edges, OUTPUT_FILE)
    logger.info(f"Graph saved as {OUTPUT_FILE}.png")