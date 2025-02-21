import subprocess
import logging
from parsers import string

def download(url, target, force=False):
    if target.exists() and not force:
        logging.info(f"Skipping download of {target}. File already exists.")
        return
    logging.info(f"Downloading {url} to {target}.")
    subprocess.run(["wget", "-q", "-O", target, url])

def parse(input_file, output_file, parser, force=False):
    logging.info(f"Parsing {input_file} to {output_file}.")
    if output_file.exists() and not force:
        logging.info(f"Skipping parsing of {output_file}. File already exists.")
        return
    
    g = None
    match parser:
        case "string":
            g = string.parse(input_file)
        case _:
            raise ValueError(f"Unknown parser: {parser}")
    g.save(str(output_file))
    

