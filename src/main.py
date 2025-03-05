#!/usr/bin/env python

"""Provide a command line tool to parse different network file formats."""

import sys
import argparse
import logging
import toml
import os
from pathlib import Path
from common import download, parse, map_to_uniprot_ac
from parsers import string
from id_mapping import id_mapper

logger = logging.getLogger()
config = toml.load("config.toml")


def parse_args(argv=None):
    """Define and immediately parse command line arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-l",
        "--log-level",
        help="The desired log level (default WARNING).",
        choices=("CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"),
        default="INFO",
    )
    parser.add_argument(
        "-f",
        "--force",
        help="Force download and parsing of files even if they already exist.",
        action="store_true",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Coordinate argument parsing and program execution."""
    args = parse_args(argv)

    logging.basicConfig(
        level=args.log_level, 
        format="%(asctime)s [%(levelname)s] %(filename)s:%(funcName)s - %(message)s",
        datefmt="%d.%m.%Y %H:%M:%S"
    )
    logger.info("Starting program.")
    logger.debug(f"{config=}")

    os.makedirs(Path(config["download_dir"]).resolve(), exist_ok=True)
    os.makedirs(Path(config["network_dir"]).resolve(), exist_ok=True)



    # download network files
    for source in list(config["sources"].items()):
        for file in source[1].items():
            url = file[1]["url"]
            target = Path(os.path.join(config["download_dir"], file[1]["filename"])).resolve()
            if not target.exists() or args.force:
                logger.info(f"Downloading {source[0]}.{file[0]}...")
                download(url, target, source[0])
            else:
                logger.info(f"Skipping download of {source[0]}.{file[0]}. File already exists")
                logger.debug(f"{target=}")
    
    # download files for id mapping
    uniprot_mapping_file = Path(os.path.join(config["download_dir"], config["idmapping"]["uniprot"]["filename"])).resolve()
    uniport_mapping_url = config["idmapping"]["uniprot"]["url"]
    if not uniprot_mapping_file.exists() or args.force:
            logger.info(f"Downloading uniprot id mapping...")
            download(uniport_mapping_url, uniprot_mapping_file)
    else:
        logger.info(f"Skipping download of uniprot id mapping. File already exists")
        logger.debug(f"{uniprot_mapping_file=}")



    # create entries for each network (multiple entries for multiple subsets of the same base network)
    network_configs = []

    for source in config["sources"].items():

        # iterate over different downloadable files
        for file in source[1].items():

            input_file = Path(os.path.join(config["download_dir"], file[1]["filename"])).resolve()
            # check if a single file should be split into multiple subsets
            subsets = [""] if "subsets" not in file[1].keys() else file[1]["subsets"].items()
            for subset in subsets:
                output_stem = os.path.join(config["network_dir"], f"{source[0]}.{file[0]}")
                if subset:
                    output_stem += f"_{subset[0]}"
                network_config = {}
                network_config["input_file"] = input_file
                network_config["source"] = source[0]
                network_config["file"] = file[0]
                network_config["subset"] = subset
                network_config["output_file"] = Path(f"{output_stem}.{file[1]["id_space"]}.gt").resolve()
                network_config["uniprot_file"]= Path(f"{output_stem}.UniProtKB-AC.gt").resolve()
                network_config["file_config"] = file[1]
                network_config["subset_config"] = subset[1] if subset else {}
                network_config["id_space"] = file[1]["id_space"]
                network_configs.append(network_config)
    logger.debug(f"{network_configs=}")



    # parse network files to graph-tool graphs in their native id space
    for entry in network_configs:
        if not entry["output_file"].exists() or args.force:
            logger.info(f"Parsing {entry['output_file'].name}...")
            parse(entry["input_file"], entry["output_file"], entry["source"], config=entry)
        else:
            logger.info(f"Skipping parsing of {entry['output_file'].name}. File already exists")

    # Load id mapping
    mapper = id_mapper(uniprot_mapping_file)

    for entry in network_configs:
        if entry["id_space"] != "UniProtKB-AC":
            if not entry["uniprot_file"].exists() or args.force:
                logger.info(f"Mapping {entry['output_file'].name} to UniProtKB-AC...")
                map_to_uniprot_ac(entry["output_file"], entry["uniprot_file"], entry["id_space"], mapper)
            else:
                logger.info(f"Skipping mapping of {entry['output_file'].name} to UniProtKB-AC. File already exists")
    


if __name__ == "__main__":
    sys.exit(main())