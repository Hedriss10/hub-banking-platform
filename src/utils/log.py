# src/utils/log.py

import logging
from datetime import datetime

from src.database.database import db
from src.models.models import Log


# setup logger só para terminal (sem ficheiros locais)
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


# salva o log no banco de dados
def log_to_db(logger_name: str, level: str, message: str):
    try:
        log_entry = Log(
            timestamp=datetime.utcnow(),  # <-- força o valor
            logger_name=logger_name,
            level=level,
            message=message,
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        logger = setup_logger('DBLogger')
        logger.error(f'Erro ao salvar log no banco: {e}')


logger = setup_logger('AppLogger')


def logdb(level: str, message: str):
    """
    Regista no terminal e persiste no banco (tabela Log), quando aplicável.
    """
    log_func = getattr(logger, level.lower(), logger.info)
    log_func(message)
    log_to_db('AppLogger', level.upper(), message)


# logdb("warning", "Not found") example
# logdb("info", "Users list is empty")
# logdb("error", "Not found")
