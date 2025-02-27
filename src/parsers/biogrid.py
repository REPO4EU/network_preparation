import pandas as pd
import logging
import graph_tool.all as gt
import zipfile
from itertools import product

def split_ids(entry):
    ids = []
    if entry != "-" and entry != "":
        ids += entry.split("|")
    return ids

def parse(input_file, config):

    with zipfile.ZipFile(input_file) as z:
        with z.open(config["subset_config"]["filename"]) as f:
            network_df = pd.read_csv(f, sep="\t")

    n_rows = network_df.shape[0]

    # remove non-human proteins
    network_df = network_df[network_df["Organism Name Interactor A"]=="Homo sapiens"]
    network_df = network_df[network_df["Organism Name Interactor B"]=="Homo sapiens"]
    logging.debug(f"Removed {n_rows-network_df.shape[0]} interactions involving non-human proteins...")
    
    # split interactors into lists
    interactors_a = network_df["SWISS-PROT Accessions Interactor A"].apply(split_ids)
    interactors_b = network_df["SWISS-PROT Accessions Interactor B"].apply(split_ids)

    # convert into list of tuples
    tuples = list(zip(interactors_a, interactors_b))

    # create products for tuples with multiple interactors
    network_tuples = []
    for tuple in tuples:
        network_tuples += product(tuple[0], tuple[1])
    logging.debug(f"Number of parsed interactions: {len(network_tuples)}")
    
    g = gt.Graph(network_tuples, directed=False, hashed=True)

    return g


