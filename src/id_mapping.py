
import pandas as pd 
import logging
from pathlib import Path
import os
from collections import defaultdict

def create_ensembl_pro_to_uniprot_ac(df):

    ensembl_pro_to_uniprot_ac = defaultdict(list)

    # Iterate over rows
    logging.info("Creating mapping from Ensembl_PRO to UniProtKB-AC.")
    for _, row in df.iterrows():
        keys = row["Ensembl_PRO"]  # List of keys
        value = row["UniProtKB-AC"]
        
        for key in keys:  # Assign each key to the value
            ensembl_pro_to_uniprot_ac[key].append(value)

    # Convert defaultdict to a regular dictionary
    ensembl_pro_to_uniprot_ac = dict(ensembl_pro_to_uniprot_ac)

    no_mapping = ensembl_pro_to_uniprot_ac.pop("nan", None)
    n_unqiue = 0
    n_multiple = 0
    max_multiple = 0
    for key, value in ensembl_pro_to_uniprot_ac.items():
        if len(value)>1:
            n_multiple += 1
            if len(value)>max_multiple:
                max_multiple = len(value)   
        else:
            n_unqiue += 1

    logging.info(f"Ignored {len(no_mapping)} rows with no Ensembl_PRO ID.")
    logging.info(f"Created mapping for {len(ensembl_pro_to_uniprot_ac)} Ensembl_PRO IDs. {n_unqiue} unique, {n_multiple} multi mappings (maximum {max_multiple}).")

    return ensembl_pro_to_uniprot_ac

class id_mapper:
    def __init__(self, uniprot_file):

        uniprot_header = (
            "UniProtKB-AC",
            "UniProtKB-ID",
            "GeneID (EntrezGene)",
            "RefSeq",
            "GI",
            "PDB",
            "GO",
            "UniRef100",
            "UniRef90",
            "UniRef50",
            "UniParc",
            "PIR",
            "NCBI-taxon",
            "MIM",
            "UniGene",
            "PubMed",
            "EMBL",
            "EMBL-CDS",
            "Ensembl",
            "Ensembl_TRS",
            "Ensembl_PRO",
            "Additional PubMed",
        )

        df = pd.read_csv(
            uniprot_file,
            sep="\t",
            header=None,
            names=uniprot_header,
            compression="gzip",
        )
        
        # Make sure UniProtKB-AC and ID only contain one value
        assert not df["UniProtKB-AC"].astype(str).str.contains(";").any()
        assert not df["UniProtKB-ID"].astype(str).str.contains(";").any()

        # Make sure UniProtKB-AC and ID are unique
        assert df["UniProtKB-AC"].is_unique
        assert df["UniProtKB-ID"].is_unique

        # Split Ensembl_PRO column into lists multiple ids
        df["Ensembl_PRO"] = df["Ensembl_PRO"].astype(str).str.split("; ")

        # Trim version number
        df["Ensembl_PRO"] = df["Ensembl_PRO"].apply(lambda lst: [x.split(".")[0] for x in lst] if isinstance(lst, list) else lst)

        # Create mappings
        self.uniprot_id_to_uniprot_ac = df.set_index("UniProtKB-ID")["UniProtKB-AC"].to_dict()
        self.ensembl_pro_to_uniprot_ac = create_ensembl_pro_to_uniprot_ac(df)


