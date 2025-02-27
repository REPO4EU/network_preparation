import subprocess
import logging
from parsers import string, hippie, biogrid, iid

def download(url, target):
    logging.debug(f"Downloading {url} to {target}.")
    subprocess.run(["wget", "-q", "-O", target, url])

def parse(input_file, output_file, parser, *args, **kwargs):
    logging.debug(f"Parsing {input_file} to {output_file}.")
    
    g = None
    match parser:
        case "string":
            g = string.parse(input_file,)
        case "hippie":
            g = hippie.parse(input_file, kwargs["config"])
        case "biogrid":
            g = biogrid.parse(input_file, kwargs["config"])
        case "iid":
            g = iid.parse(input_file)
        case _:
            raise ValueError(f"Unknown parser: {parser}")
    g.save(str(output_file))
    

