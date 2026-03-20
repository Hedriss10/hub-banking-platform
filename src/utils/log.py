# src/utils/log.py

import logging
from datetime import datetime

from src.database.database import db


def setup_logger(name: str):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

    return logger



logger = setup_logger('AppLogger')


def logdb(level: str, message: str):
    """
    Regista no terminal e persiste no banco (tabela Log), quando aplicável.
    """
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message)


# logdb("warning", "Not found") example
# logdb("info", "Users list is empty")
# logdb("error", "Not found")
