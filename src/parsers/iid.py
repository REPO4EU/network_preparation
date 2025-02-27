import pandas as pd
import logging
import graph_tool.all as gt

def parse(input_file):
    network_df = pd.read_csv(input_file, sep="\t")

    # convert columns to tuples
    network_tuples = network_df[["uniprot1", "uniprot2"]].apply(tuple, axis=1).tolist()

    g = gt.Graph(network_tuples, directed=False, hashed=True)

    return g