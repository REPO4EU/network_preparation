import pandas as pd
import logging
import graph_tool.all as gt
from utils import filter_network_tuples

def parse(input_file):
    network_df = pd.read_csv(input_file, sep="\t", usecols=["uniprot1", "uniprot2"])

    # convert columns to tuples
    network_tuples = network_df[["uniprot1", "uniprot2"]].apply(tuple, axis=1).tolist()

    # remove duplicate edges and self-loops
    network_tuples = filter_network_tuples(network_tuples)

    g = gt.Graph(network_tuples, directed=False, hashed=True)

    return g