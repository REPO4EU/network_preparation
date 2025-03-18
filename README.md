# PPI Network Preparation
Downloads PPI networks from multiple sources and converts them to different ID spaces.
The final networks are saved as .gt files.

## Included networks
Network sources: [STRING](https://string-db.org/cgi/download), [HIPPIE](https://cbdm-01.zdv.uni-mainz.de/~mschaefer/hippie/index.php), [BioGRID](https://thebiogrid.org/), [IID](https://iid.ophid.utoronto.ca/), [NeDRex](https://nedrex.net/index.html)

ID spaces: Entrez genes, Ensembl genes, gene symbols, UniProt proteins

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