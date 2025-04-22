import logging
import sys
from logging import Formatter, StreamHandler

# Defines logging format.
FORMAT = "%(asctime)s,%(msecs)d - %(name)s - %(levelname)s - %(message)s"
# Defines logging date format.
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def configure_logging() -> None:
    stream_handler = StreamHandler(sys.stderr)
    stream_handler.setFormatter(Formatter(FORMAT, datefmt=DATE_FORMAT))
    logging.basicConfig(handlers=[stream_handler])
