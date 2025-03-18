# PPI Network Preparation
Downloads PPI networks from multiple sources and converts them to different ID spaces. The final networks are saved as [.gt files](https://graph-tool.skewed.de/static/doc/gt_format.html).

The IDs are mapped based on the [mapping file](https://ftp.uniprot.org/pub/databases/uniprot/current_release/knowledgebase/idmapping/by_organism/HUMAN_9606_idmapping_selected.tab.gz) provided py UniProt. Gene symbols are mapped using the [mygene](https://pypi.org/project/mygene/) Python package. 

The networks are converted to different ID spaces starting from UniProtKB-AC IDs. If a network source does not provide UniProtKB-AC IDs (STRING and HIPPIE), they are mapped to UniProtKB-AC IDs first. If a source ID can be mapped to multiple target IDs, all target IDs are assumed to interact with all interaction partners of the source ID. 

Some sources (HIPPIE, STRING, NeDRex) are used generate multiple subsets based on different confidence thresholds.

All self-loops (same source and target node) and duplicate edges (e.g., A -> B and B -> A) are removed. 

## Included networks
Network sources: [STRING](https://string-db.org/cgi/download), [HIPPIE](https://cbdm-01.zdv.uni-mainz.de/~mschaefer/hippie/index.php), [BioGRID](https://thebiogrid.org/), [IID](https://iid.ophid.utoronto.ca/), [NeDRex](https://nedrex.net/index.html)

ID spaces: Entrez genes, Ensembl genes, gene symbols, UniProtKB-AC

A table of the prepared networks and their sizes can be found [here](logs/network_stats.md).
## Usage
Clone repository:
```bash
git clone https://github.com/REPO4EU/network_preparation.git
```
Install dependencies with conda:
```bash
cd network_preparation
conda env create -f environment.yml
conda activate network_preparation
```
Execute the program:
```bash
python src/main.py
```
See options:
```bash
python src/main.py --help
```
## Config
Config options can be adjusted by modifying [config.toml](config.toml).