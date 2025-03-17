import mygene

# Initialize MyGene.info client
mg = mygene.MyGeneInfo()

# List of UniProt IDs
uniprot_ids = ["P04637", "Q96P44", "O15553", "P68431"]  # Example IDs

# Query MyGene.info
results = mg.querymany(uniprot_ids, scopes="uniprot", fields="symbol", species="human", returnall=True)

# Extract mappings
print(results)
mapped_genes = [(res["query"], res.get("symbol", None)) for res in results["out"]]

# Print results
for uniprot, hgnc_symbol in mapped_genes:
    print(f"{uniprot} -> {hgnc_symbol}")