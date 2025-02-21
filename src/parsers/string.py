import pandas as pd
import logging
import graph_tool.all as gt

def parse(input_file):
    network_df = pd.read_csv(input_file, compression="gzip")

    # replace "9606." prefix with empty string in protein IDs
    network_df["protein1"] = network_df["protein1"].str.replace("9606.", "")
    network_df["protein2"] = network_df["protein2"].str.replace("9606.", "")

    # convert columns to tuples
    network_tuples = network_df[["protein1", "protein2"]].apply(tuple, axis=1).tolist()

    g = gt.Graph(network_tuples, directed=False, hashed=True)

    return g

