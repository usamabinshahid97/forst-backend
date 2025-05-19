import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import matplotlib.pyplot as plt
import networkx as nx

# Import models
from app.models.category import Category
from app.models.product import Product
from app.models.inventory import Inventory
from app.models.sale import Sale

def generate_schema_diagram():
    """Generate a simple ER diagram for the database."""
    # Create a directed graph
    G = nx.DiGraph()
    
    # Add nodes for each table
    G.add_node("Category", shape="rectangle", style="filled", fillcolor="lightblue")
    G.add_node("Product", shape="rectangle", style="filled", fillcolor="lightgreen")
    G.add_node("Inventory", shape="rectangle", style="filled", fillcolor="lightpink")
    G.add_node("Sale", shape="rectangle", style="filled", fillcolor="lightyellow")
    
    # Add edges (relationships)
    G.add_edge("Product", "Category", label="belongs to")
    G.add_edge("Inventory", "Product", label="tracks")
    G.add_edge("Sale", "Product", label="includes")
    
    # Draw the graph
    plt.figure(figsize=(12, 8))
    pos = nx.spring_layout(G, seed=42)
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=3000, node_color="skyblue", alpha=0.8)
    nx.draw_networkx_labels(G, pos, font_size=14, font_weight="bold")
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=2, arrowsize=20)
    
    # Edge labels
    edge_labels = {(u, v): d["label"] for u, v, d in G.edges(data=True)}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=12)
    
    # Add title
    plt.title("E-commerce Admin Database Schema", size=15)
    
    # Remove axes
    plt.axis("off")
    
    # Save the figure
    os.makedirs("docs", exist_ok=True)
    plt.savefig("docs/schema.png", dpi=300, bbox_inches="tight")
    plt.close()
    
    print("Schema diagram generated at docs/schema.png")

if __name__ == "__main__":
    try:
        generate_schema_diagram()
    except ImportError as e:
        print(f"Error: {e}")
        print("Make sure you have installed matplotlib and networkx:\npip install matplotlib networkx") 