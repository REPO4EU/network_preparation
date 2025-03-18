import logging
import datetime
import os

# Configure the logger
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

# Avoid adding handlers multiple times
def setup_logging(level="INFO", log_dir=None, filename=None):

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(filename)s:%(funcName)s - %(message)s", 
        datefmt="%d.%m.%Y %H:%M:%S"
    )

    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    # Add handlers to the logger
    logger.addHandler(console_handler)

    # Add file handler if log_dir is provided
    if log_dir is not None:

        if filename is None:
            filename = os.path.join(log_dir, datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log"))

        # File handler (logs everything)
        file_handler = logging.FileHandler(filename)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logging.getLogger("requests").setLevel(logging.WARNING)  # Requests package
    logging.getLogger("urllib3").setLevel(logging.WARNING)  # urllib3 package

    # Additional step to suppress the default logging of urllib3's connection pool
    logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)