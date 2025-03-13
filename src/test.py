from graph_tool.all import Graph

# Create a directed graph
g = Graph(directed=False)

# Add vertices
v1 = g.add_vertex()
v2 = g.add_vertex()
v3 = g.add_vertex()

# Add multiple edges between the same nodes
g.add_edge(v1, v2)
g.add_edge(v1, v2)  # Duplicate edge
g.add_edge(v2, v1)
g.add_edge(v1, v2)  # Another duplicate
g.add_edge(v2, v3)

# Create a set to track unique edges
seen_edges = set()
edges_to_remove = []

# Identify duplicate edges
for e in g.edges():
    edge_tuple = tuple(sorted([e.source(), e.target()])) 
    if edge_tuple in seen_edges:
        edges_to_remove.append(e)  # Mark for removal
    else:
        seen_edges.add(edge_tuple)

# Remove duplicate edges
#for e in edges_to_remove:
#    g.remove_edge(e)

print(edges_to_remove)
print(f"Graph now has {g.num_edges()} unique edges.")
