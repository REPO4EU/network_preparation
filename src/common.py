import subprocess
import logging

def download(url, target, force=False):
    if target.exists() and not force:
        logging.info(f"Skipping download of {target}. File already exists.")
        return
    logging.info(f"Downloading {url} to {target}.")
    subprocess.run(["wget", "-q", "-O", target, url])
