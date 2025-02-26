import pandas as pd
import logging
import graph_tool.all as gt

def parse(input_file, config):

    cutoff = config["subset_config"]["cutoff"]
    network_df = pd.read_csv(input_file, sep="\t", header=None)

    n_rows = network_df.shape[0]
    #remove rows with NaN values in columns 0 or 2
    network_df = network_df.dropna(subset=[0, 2])
    logging.debug(f"Removed {n_rows - network_df.shape[0]} rows with NaN values in columns 0 or 2")

    n_rows = network_df.shape[0]
    network_df = network_df[network_df.iloc[:, 4] >= cutoff]
    logging.debug(f"Removed {n_rows - network_df.shape[0]} rows with score below {cutoff}")

    # convert columns to tuples
    logging.debug(f"Remaining rows: {network_df.shape[0]}")
    network_tuples = network_df[[0, 2]].apply(tuple, axis=1).tolist()



    g = gt.Graph(network_tuples, directed=False, hashed=True)

    return g