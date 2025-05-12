"""
Logging utilities for the Bitcoin Repository Health Analysis Tool.

This module provides a consistent logging setup for the entire application.
"""

import logging
import sys
from typing import Optional


# Create a custom formatter with colors
class ColoredFormatter(logging.Formatter):
    """
    A custom formatter for colorful log messages.
    """

    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[91;1m",  # Bold Red
        "RESET": "\033[0m",  # Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with colors.

        Args:
            record: The log record to format

        Returns:
            Formatted log message with colors
        """
        # Check if we're on a terminal that supports colors
        if hasattr(sys.stdout, "isatty") and sys.stdout.isatty():
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
                record.msg = f"{self.COLORS[levelname]}{record.msg}{self.COLORS['RESET']}"

        return super().format(record)


def setup_logger(level: int = logging.INFO) -> logging.Logger:
    """
    Set up the application logger.

    Args:
        level: Logging level

    Returns:
        Configured logger
    """
    # Create logger
    logger = logging.getLogger("bitcoin_repo_health")
    logger.setLevel(level)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create formatter
    formatter = ColoredFormatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)

    # Add handler to logger
    logger.addHandler(console_handler)

    return logger


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: Module name

    Returns:
        Logger instance
    """
    if name:
        return logging.getLogger(f"bitcoin_repo_health.{name}")
    else:
        return logging.getLogger("bitcoin_repo_health")
