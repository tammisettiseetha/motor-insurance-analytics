import logging
from pathlib import Path


LOG_FILE = Path(__file__).resolve().parent.parent / "logs" / "pipeline.log"


def setup_logger():
    """Configure logging to write messages to the pipeline log file."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("motor_insurance_pipeline")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        file_handler.setLevel(logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def log_pipeline_step(message):
    """Record a successful pipeline step or progress update."""
    logger = setup_logger()
    logger.info(message)


def log_error(message):
    """Record an error in the pipeline log."""
    logger = setup_logger()
    logger.error(message)