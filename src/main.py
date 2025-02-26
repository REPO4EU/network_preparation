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
                logger.info(f"Downloading {file[0]}...")
                download(url, target)
            else:
                logger.info(f"Skipping download of {file[0]}. File already exists")
                logger.debug(f"{target=}")

    for source in config["sources"].items():
        for file in source[1].items():
            input_file = Path(os.path.join(config["download_dir"], file[1]["filename"])).resolve()
            output_file = Path(os.path.join(config["network_dir"], f"{file[0]}.{file[1]["id_space"]}.gt")).resolve()
            if not output_file.exists() or args.force:
                logger.info(f"Parsing {file[0]}...")
                parse(input_file, output_file, source[0])
            else:
                logger.info(f"Skipping parsing of {file[0]}. File already exists")
                logger.debug(f"{output_file=}")


if __name__ == "__main__":
    sys.exit(main())