import subprocess
import logging
from parsers import string, hippie, biogrid, iid, nedrex
from downloaders  import nedrex as nedrex_downloader
import graph_tool.all as gt
from itertools import product
from utils import ids2names, g2nodes, g2tuples, filter_network_tuples

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
    
    map_graph(input_file, output_file, mapping)


def map_from_uniprot_ac(input_file, output_file, id_space, mapper):

    match id_space:
        case "Ensembl":
            mapping = mapper.uniprot_ac_to_ensembl
        case "Entrez":
            mapping = mapper.uniprot_ac_to_entrez
        case _:
            raise ValueError(f"Unknown id space: {id_space}")
    
    map_graph(input_file, output_file, mapping)


def map_graph(input_file, output_file, mapping):
    input_g = gt.load_graph(str(input_file))
    input_nodes = set(g2nodes(input_g))
    input_edges = list(g2tuples(input_g))
    logging.debug(f"Loaded {len(input_nodes)} nodes and {len(input_edges)} edges from {input_file}.")
    mappable = input_nodes.intersection(mapping.keys())
    n_uniquely_mappable = len(mappable.difference(set([k for k, v in mapping.items() if len(v)>1])))
    logging.debug(f"Mapping available for {len(mappable)} ({n_uniquely_mappable} uniquely) out of {len(input_nodes)} nodes.")

    network_tuples = []
    for source, target in input_edges:
        if source in mapping.keys() and target in mapping.keys():
            source_mappings = mapping[source]
            target_mappings = mapping[target]
            network_tuples += product(source_mappings, target_mappings)
    
    network_tuples = filter_network_tuples(network_tuples)
    output_g = gt.Graph(network_tuples, directed=False, hashed=True)
    output_g = ids2names(output_g)

    logging.debug(f"Created {output_g.num_vertices()} nodes and {output_g.num_edges()} edges in {output_file}.")
    output_g.save(str(output_file))