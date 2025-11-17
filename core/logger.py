"""
Logging configuration for the document converter.
"""
import logging
import sys
from pathlib import Path
from typing import Optional


class Logger:
    """Centralized logging manager."""

    _instance: Optional[logging.Logger] = None

    @classmethod
    def setup(cls, log_file: str, log_level: str = 'INFO') -> logging.Logger:
        """
        Set up logging configuration.

        Args:
            log_file: Path to log file
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

        Returns:
            Configured logger instance
        """
        if cls._instance is not None:
            return cls._instance

        # Create logger
        logger = logging.getLogger('doc_converter')
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))

        # Remove existing handlers
        logger.handlers.clear()

        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_formatter = logging.Formatter(
            '%(levelname)s: %(message)s'
        )

        # File handler
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

        # Console handler (only WARNING and above to avoid cluttering with progress bar)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)

        cls._instance = logger
        return logger

    @classmethod
    def get(cls) -> logging.Logger:
        """
        Get logger instance.

        Returns:
            Logger instance

        Raises:
            RuntimeError: If logger not initialized
        """
        if cls._instance is None:
            raise RuntimeError("Logger not initialized. Call setup() first.")
        return cls._instance
