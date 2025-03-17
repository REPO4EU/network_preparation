import logging
import graph_tool.all as gt

def g2tuples(g):
    source_list = []
    target_list = []
    for e in g.iter_edges():
        source_list.append(g.vp["name"][e[0]])
        target_list.append(g.vp["name"][e[1]])

    return zip(source_list, target_list)

def g2nodes(g):
    return [g.vp["name"][v] for v in g.iter_vertices()]

def ids2names(g):
    # creating new vertex property "name" to match property name when reading from csv
    names = g.new_vertex_property("string")

    # Copy the values from the old property to the new one
    for v in g.vertices():
        names[v] = g.vp["ids"][v]

    # Remove the old property (optional)
    del g.vertex_properties["ids"]

    # Assign the new property to the graph
    g.vertex_properties["name"] = names

    return g

def filter_network_tuples(network_tuples, remove_dups=True, remove_self_loops=True, directed=False):

    n = len(network_tuples)
    if remove_self_loops:
        filtered_tuples = []
        for entry in network_tuples:
            if entry[0] != entry[1]:
                filtered_tuples.append(entry)
        network_tuples = filtered_tuples

    logging.debug(f"Filtered {n - len(network_tuples)} self-loops")
    n = len(network_tuples)

    if remove_dups:
        seen_edges = set()
        filtered_tuples = []
        for entry in network_tuples:
            if not directed:
                edge_tuple = tuple(sorted([entry[0], entry[1]]))
            else:
                edge_tuple = entry
            if not (edge_tuple in seen_edges):
                filtered_tuples.append(edge_tuple)
                seen_edges.add(edge_tuple)
        network_tuples = filtered_tuples
        logging.debug(f"Filtered {n - len(network_tuples)} duplicate edges")

    return network_tuples

