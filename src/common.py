import subprocess
import logging
from parsers import string, hippie, biogrid, iid, nedrex
from downloaders  import nedrex as nedrex_downloader
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
    
    # creating new vertex property "name" to match property name when reading from csv
    names = g.new_vertex_property("string")

    # Copy the values from the old property to the new one
    for v in g.vertices():
        names[v] = g.vp["ids"][v]

    # Remove the old property (optional)
    del g.vertex_properties["ids"]

    # Assign the new property to the graph
    g.vertex_properties["name"] = names
    g.save(str(output_file))

def map_to_uniprot_ac(input_file, output_file, id_space, mapper):
    input_g = gt.load_graph(str(input_file))
    input_nodes = g2nodes(input_g)
    input_edges = g2tuples(input_g)
    
    match id_space:
        case "Ensembl_PRO":
            mapping = mapper.ensembl_pro_to_uniprot_ac
        case "UniProtKB-ID":
            mapping = mapper.uniprot_id_to_uniprot_ac
        case _:
            raise ValueError(f"Unknown id space: {id_space}")
        
    print(len([node for node in input_nodes if node in mapping.keys()]))
    print(len(input_nodes))
    

