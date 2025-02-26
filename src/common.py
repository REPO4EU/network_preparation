import subprocess
import logging
from parsers import string

def download(url, target):
    logging.debug(f"Downloading {url} to {target}.")
    subprocess.run(["wget", "-q", "-O", target, url])

def parse(input_file, output_file, parser):
    logging.debug(f"Parsing {input_file} to {output_file}.")
    
    g = None
    match parser:
        case "string":
            g = string.parse(input_file)
        case _:
            raise ValueError(f"Unknown parser: {parser}")
    g.save(str(output_file))
    

