import pandas as pd
import logging
import graph_tool.all as gt

def parse(input_file, config):

    cutoff = config["subset_config"]["cutoff"]
    network_df = pd.read_csv(input_file, sep="\t")

    n_rows = network_df.shape[0]
    network_df = network_df[network_df["methods_score"] >= cutoff]
    logging.debug(f"Removed {n_rows - network_df.shape[0]} rows with methods_score below {cutoff}")

    # convert columns to tuples
    logging.debug(f"Remaining rows: {network_df.shape[0]}")
    network_tuples = network_df[["memberOne","memberTwo"]].apply(tuple, axis=1).tolist()



    g = gt.Graph(network_tuples, directed=False, hashed=True)

    return g