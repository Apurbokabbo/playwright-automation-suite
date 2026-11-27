import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler
from pathlib import Path

from config.base_config import BaseConfig

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Created once per run, so all loggers write to the same file
_RUN_TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)

    # Already configured, return as is
    if logger.handlers:
        return logger

    logger.setLevel(level)
    logger.propagate = False  # avoid duplicate logs

    formatter = logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)

    # File handler
    log_dir = Path(BaseConfig.LOGS_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)

    file_handler = RotatingFileHandler(
        log_dir / f"test_run_{_RUN_TIMESTAMP}.log",
        maxBytes=5 * 1024 * 1024,  # 5 MB
        backupCount=5,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(level)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(level)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger