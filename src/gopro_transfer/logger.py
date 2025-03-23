"""Logging configuration for GoPro Transfer."""

import os
import sys
from datetime import datetime
from pathlib import Path

from loguru import logger


# Default log file location
DEFAULT_LOG_DIR = Path.home() / ".logs" / "gopro-transfer"
DEFAULT_LOG_LEVEL = "INFO"


def setup_logging(log_level=None, log_file=None):
    """Configure Loguru logger with custom settings.

    Args:
        log_level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, uses default path)
    """
    # Remove default logger
    logger.remove()

    # Set log level from environment or use default
    level = log_level or os.environ.get("GOPRO_LOG_LEVEL", DEFAULT_LOG_LEVEL)

    # Add console logger
    logger.add(
        sys.stderr,
        level=level,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        colorize=True,
    )

    # Create log directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
    else:
        log_dir = Path(os.environ.get("GOPRO_LOG_DIR", DEFAULT_LOG_DIR))
        log_dir.mkdir(parents=True, exist_ok=True)

        # Create log file with timestamp in name
        timestamp = datetime.now().strftime("%Y%m%d")
        log_path = log_dir / f"gopro-transfer-{timestamp}.log"

    # Add file logger
    logger.add(
        str(log_path),
        level=level,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="1 month",  # Keep logs for 1 month
        compression="zip",  # Compress rotated logs
    )

    # Log initial message
    logger.info(f"Logging initialized at level {level}")
    logger.info(f"Logs will be saved to {log_path}")

    return logger


# Initialize logger with default settings
setup_logging()
