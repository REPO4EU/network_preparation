#!/usr/bin/env python

"""Provide a command line tool to parse different network file formats."""

import sys
import argparse
import logging
import toml
import os
from pathlib import Path
from common import download, parse
from parsers import string

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

    for source in config["sources"].items():
        for file in source[1].items():
            url = file[1]["url"]
            target = Path(os.path.join(config["download_dir"], file[1]["filename"])).resolve()
            if not target.exists() or args.force:
                logger.info(f"Downloading {source[0]}.{file[0]}...")
                download(url, target, source[0])
            else:
                logger.info(f"Skipping download of {source[0]}.{file[0]}. File already exists")
                logger.debug(f"{target=}")

        output_file_configs = []

        for source in config["sources"].items():

            # iterate over different downloadable files
            for file in source[1].items():

                input_file = Path(os.path.join(config["download_dir"], file[1]["filename"])).resolve()

                # check if a single file should be split into multiple subsets
                if "subsets" in file[1].keys():
                    for subset in file[1]["subsets"].items():
                        output_file_configs.append(
                            {
                                "input_file": input_file,
                                "source": source[0],
                                "file": file[0],
                                "subset": subset[0],
                                "output_file": Path(os.path.join(config["network_dir"], f"{source[0]}.{file[0]}_{subset[0]}.{file[1]["id_space"]}.gt")).resolve(),
                                "file_config": file[1],
                                "subset_config": subset[1],
                                "id_space": file[1]["id_space"],
                            }
                        )
                else:
                    output_file_configs.append(
                        {
                            "input_file": input_file,
                            "source": source[0],
                            "file": file[0],
                            "output_file": Path(os.path.join(config["network_dir"], f"{source[0]}.{file[0]}.{file[1]["id_space"]}.gt")).resolve(),
                            "file_config": file[1],
                            "id_space": file[1]["id_space"],
                        }
                    )

    logger.debug(f"{output_file_configs=}")


    for entry in output_file_configs:
        if not entry["output_file"].exists() or args.force:
            logger.info(f"Parsing {entry['output_file'].name}...")
            parse(entry["input_file"], entry["output_file"], entry["source"], config=entry)
        else:
            logger.info(f"Skipping parsing of {entry['output_file'].name}. File already exists")


if __name__ == "__main__":
    sys.exit(main())