"""
Structured JSON logger for CloudWatch + local development.
"""

import logging
import sys
import os
from pythonjsonlogger import jsonlogger


def get_logger(name: str) -> logging.Logger:
    """
    Return a JSON-structured logger suitable for CloudWatch Logs.
    Falls back gracefully if pythonjsonlogger is unavailable.
    """
    logger = logging.getLogger(name)

    # Avoid adding duplicate handlers on Lambda container reuse
    if logger.handlers:
        return logger

    log_level_str = os.getenv("LOG_LEVEL", "INFO").upper()
    log_level = getattr(logging, log_level_str, logging.INFO)
    logger.setLevel(log_level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(log_level)

    # JSON formatter with standard AWS Lambda fields
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        rename_fields={"levelname": "level", "asctime": "timestamp"},
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
