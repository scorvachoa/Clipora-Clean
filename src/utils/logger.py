import logging
import os
from datetime import datetime
from src.core.config import LOGS_DIR


def _setup_logger() -> logging.Logger:
    logger = logging.getLogger("clipora_clean")
    if logger.handlers:
        return logger

    logger.setLevel(logging.DEBUG)

    log_file = os.path.join(LOGS_DIR, f"clipora_{datetime.now().strftime('%Y%m%d')}.log")
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


_logger = _setup_logger()


def log_info(message: str):
    _logger.info(message)


def log_warning(message: str):
    _logger.warning(message)


def log_error(message: str):
    _logger.error(message)


def log_debug(message: str):
    _logger.debug(message)
