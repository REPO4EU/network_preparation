
import pandas as pd 
import logging
from pathlib import Path
import os
from collections import defaultdict

def create_mapping(df, source_col, target_col):
    mapping = defaultdict(list)

    # Convert column elements to lists, if not yet the case
    logging.info(f"Creating mapping from {source_col} to {target_col}.")
    source_lists = df[source_col].apply(lambda x: x if isinstance(x, list) else [x]).tolist()
    target_lists = df[target_col].apply(lambda x: x if isinstance(x, list) else [x]).tolist()
    for sources, targets in zip(source_lists, target_lists):
        for source in sources:
            for target in targets:
                mapping[source].append(target)

    # Convert defaultdict to a regular dictionary
    ensembl_pro_to_uniprot_ac = dict(mapping)

    no_mapping = mapping.pop("nan", [])
    n_unqiue = 0
    n_multiple = 0
    max_multiple = 0
    for key, value in mapping.items():
        if len(value)>1:
            n_multiple += 1
            if len(value)>max_multiple:
                max_multiple = len(value)   
        else:
            n_unqiue += 1

    logging.info(f"Ignored {len(no_mapping)} rows without a mapping to {target_col}.")
    logging.info(f"Created mapping for {len(mapping)} {source_col} ids. {n_unqiue} unique, {n_multiple} multi mappings (maximum {max_multiple}).")

    return mapping
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
        self.uniprot_id_to_uniprot_ac = create_mapping(df, "UniProtKB-ID", "UniProtKB-AC")
        self.ensembl_pro_to_uniprot_ac = create_mapping(df, "Ensembl_PRO", "UniProtKB-AC")


