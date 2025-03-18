
import pandas as pd 
import logging
from pathlib import Path
import os
from collections import defaultdict
import json
import mygene

def create_mapping(df, source_col, target_col):
    mapping = defaultdict(list)
    no_mapping_target = []

    # Convert column elements to lists, if not yet the case
    logging.info(f"Creating mapping from {source_col} to {target_col}.")
    source_lists = df[source_col].apply(lambda x: x if isinstance(x, list) else [x]).tolist()
    target_lists = df[target_col].apply(lambda x: x if isinstance(x, list) else [x]).tolist()
    for sources, targets in zip(source_lists, target_lists):
        for source in sources:
            for target in targets:
                if target != "nan":
                    mapping[source].append(target)
                else:
                    no_mapping_target.append(source)

    # Convert defaultdict to a regular dictionary
    ensembl_pro_to_uniprot_ac = dict(mapping)

    no_mapping_source = mapping.pop("nan", [])
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

    logging.info(f"Ignored {len(no_mapping_source)} with missing source ({source_col}).")
    logging.info(f"Ignored {len(no_mapping_target)} with missing target ({target_col}).")
    logging.info(f"Created mapping for {len(mapping)} {source_col} ids. {n_unqiue} unique, {n_multiple} multi mappings (maximum {max_multiple}).")

    return mapping
class id_mapper:
    def __init__(self, uniprot_file, mygene_file, force=False):

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
            dtype=str,
        )
        
        # Make sure UniProtKB-AC and ID only contain one value
        assert not df["UniProtKB-AC"].astype(str).str.contains(";").any()
        assert not df["UniProtKB-ID"].astype(str).str.contains(";").any()
        # Make sure UniProtKB-AC and ID are unique
        assert df["UniProtKB-AC"].is_unique
        assert df["UniProtKB-ID"].is_unique

        # Split column into lists multiple ids
        df["Ensembl_PRO"] = df["Ensembl_PRO"].astype(str).str.split("; ")
        df["Ensembl"] = df["Ensembl"].astype(str).str.split("; ")
        df["GeneID (EntrezGene)"] = df["GeneID (EntrezGene)"].astype(str).str.split("; ")

        # Trim version number
        df["Ensembl_PRO"] = df["Ensembl_PRO"].apply(lambda lst: [x.split(".")[0] for x in lst] if isinstance(lst, list) else lst)
        df["Ensembl"] = df["Ensembl"].apply(lambda lst: [x.split(".")[0] for x in lst] if isinstance(lst, list) else lst)
        df["GeneID (EntrezGene)"] = df["GeneID (EntrezGene)"].apply(lambda lst: [x.split(".")[0] for x in lst] if isinstance(lst, list) else lst)

        # Create mappings
        self.uniprot_id_to_uniprot_ac = create_mapping(df, "UniProtKB-ID", "UniProtKB-AC")
        self.ensembl_pro_to_uniprot_ac = create_mapping(df, "Ensembl_PRO", "UniProtKB-AC")
        self.uniprot_ac_to_ensembl = create_mapping(df, "UniProtKB-AC", "Ensembl")
        self.uniprot_ac_to_entrez = create_mapping(df, "UniProtKB-AC", "GeneID (EntrezGene)")


        logging.info("Creating mapping from UniProtKB-AC to Symbol.")
        if mygene_file.exists() and not force:
            logging.info(f"Loading existing mapping from {mygene_file}.")
            with open(mygene_file, "r") as f:
                self.uniprot_ac_to_symbol = json.load(f)
        else:
            # Initialize MyGene.info client
            logging.info("Querying MyGene.info.")

            mg = mygene.MyGeneInfo()

            # List of UniProt IDs
            uniprot_ids = df["UniProtKB-AC"].tolist()

            # Query MyGene.info
            results = mg.querymany(uniprot_ids, scopes="uniprot", fields="symbol", species="human", returnall=True)

            mapped_genes = [(res["query"], res.get("symbol", None)) for res in results["out"]]

            # Print results
            symbol_mapping = defaultdict(list)

            # Convert column elements to lists, if not yet the case
            for source, target in mapped_genes:
                if target is not None:
                    symbol_mapping[source].append(target)
            
            # Save mapping to file
            with open(mygene_file, "w") as f:
                json.dump(symbol_mapping, f)

            self.uniprot_ac_to_symbol = dict(symbol_mapping)




