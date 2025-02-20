#!/usr/bin/env python

"""Provide a command line tool to parse different network file formats."""

import sys
import argparse
import logging
import toml
import os
from pathlib import Path
from common import download

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
        "--force_download",
        help="Force download of files even if they already exist.",
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

    for source in config["sources"].items():
        logger.info(f"Downloading {source[0]}...")
        for file in source[1].items():
            logger.info(f"Downloading {file[0]}...")
            download(
                file[1]["url"],
                Path(os.path.join(config["download_dir"], file[1]["filename"])).resolve(),
                args.force_download
            )



if __name__ == "__main__":
    sys.exit(main())