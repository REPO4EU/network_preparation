import subprocess
import logging
from parsers import string, hippie, biogrid, iid, nedrex
from downloaders  import nedrex as nedrex_downloader
import graph_tool.all as gt
from itertools import product

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


def download(url, target, source=None):
    logging.debug(f"Downloading {url} to {target}.")
    match source:
        case "nedrex":
            nedrex_downloader.download(url, target)
        case _:
            subprocess.run(["wget", "-q", "-O", target, url])

def parse(input_file, output_file, parser, *args, **kwargs):
    logging.debug(f"Parsing {input_file} to {output_file}.")
    
    g = None
    match parser:
        case "string":
            g = string.parse(input_file,)
        case "hippie":
            g = hippie.parse(input_file, kwargs["config"])
        case "biogrid":
            g = biogrid.parse(input_file, kwargs["config"])
        case "iid":
            g = iid.parse(input_file)
        case "nedrex":
            g = nedrex.parse(input_file, kwargs["config"])
        case _:
            raise ValueError(f"Unknown parser: {parser}")
    
    g = ids2names(g)
    g.save(str(output_file))

def map_to_uniprot_ac(input_file, output_file, id_space, mapper):
    
    match id_space:
        case "Ensembl_PRO":
            mapping = mapper.ensembl_pro_to_uniprot_ac
        case "UniProtKB-ID":
            mapping = mapper.uniprot_id_to_uniprot_ac
        case _:
            raise ValueError(f"Unknown id space: {id_space}")
        
    input_g = gt.load_graph(str(input_file))
    input_nodes = set(g2nodes(input_g))
    input_edges = list(g2tuples(input_g))
    logging.debug(f"Loaded {len(input_nodes)} nodes and {len(input_edges)} edges from {input_file}.")
    mappable = input_nodes.intersection(mapping.keys())
    n_uniquely_mappable = len(mappable.difference(set([k for k, v in mapping.items() if len(v)>1])))
    logging.debug(f"Mapping available for {len(mappable)} ({n_uniquely_mappable} uniquely) out of {len(input_nodes)} nodes.")

    output_tuples = []
    for source, target in input_edges:
        if source in mapping.keys() and target in mapping.keys():
            source_mappings = mapping[source]
            target_mappings = mapping[target]
            output_tuples += product(source_mappings, target_mappings)
    
    output_g = gt.Graph(output_tuples, directed=False, hashed=True)
    output_g = ids2names(output_g)

    logging.debug(f"Created {output_g.num_vertices()} nodes and {output_g.num_edges()} edges in {output_file}.")
    output_g.save(str(output_file))

    

