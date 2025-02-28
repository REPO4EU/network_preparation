import subprocess
import logging
from parsers import string, hippie, biogrid, iid, nedrex
import downloaders

def download(url, target, source):
    logging.debug(f"Downloading {url} to {target}.")
    match source:
        case "nedrex":
            downloaders.nedrex.download(url, target)
        case _:
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
        case "nedrex":
            g = nedrex.parse(input_file, kwargs["config"])
        case _:
            raise ValueError(f"Unknown parser: {parser}")
    g.save(str(output_file))
    

