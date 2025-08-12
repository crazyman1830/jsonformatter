"""Logging configuration and utilities for the JSON Formatter application."""

import logging
import sys
from typing import Optional

from .config import AppConfig


class LoggerFactory:
    """Factory class for creating and configuring loggers."""

    _configured = False

    @staticmethod
    def create_logger(name: str, config: Optional[AppConfig] = None) -> logging.Logger:
        """Create a logger with the specified name and configuration.

        Args:
            name: Logger name (typically __name__)
            config: Application configuration (optional)

        Returns:
            logging.Logger: Configured logger instance
        """
        logger = logging.getLogger(name)

        # Configure root logger if not already done
        if not LoggerFactory._configured and config:
            LoggerFactory._setup_root_logger(config)
            LoggerFactory._configured = True

        return logger

    @staticmethod
    def _setup_root_logger(config: AppConfig) -> None:
        """Set up the root logger configuration.

        Args:
            config: Application configuration
        """
        root_logger = logging.getLogger()

        # Clear existing handlers
        root_logger.handlers.clear()

        # Set log level
        log_level = getattr(logging, config.log_level.upper(), logging.INFO)
        root_logger.setLevel(log_level)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        # Create formatter
        formatter = LoggerFactory._create_formatter(config)
        console_handler.setFormatter(formatter)

        # Add handler to root logger
        root_logger.addHandler(console_handler)

        # Log initial configuration
        logger = logging.getLogger(__name__)
        logger.info(
            f"Logging configured - Level: {config.log_level}, "
            f"Environment: {config.environment.value}"
        )

    @staticmethod
    def _create_formatter(config: AppConfig) -> logging.Formatter:
        """Create a log formatter based on configuration.

        Args:
            config: Application configuration

        Returns:
            logging.Formatter: Configured formatter
        """
        if config.is_development:
            # More detailed format for development
            format_string = (
                "[%(asctime)s] %(levelname)s in %(name)s "
                "(%(filename)s:%(lineno)d): %(message)s"
            )
        else:
            # Cleaner format for production
            format_string = "[%(asctime)s] %(levelname)s in %(name)s: %(message)s"

        return logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")

    @staticmethod
    def setup_request_logging() -> None:
        """Set up request logging for Flask applications."""
        # This will be used by the middleware
        werkzeug_logger = logging.getLogger("werkzeug")

        # Reduce werkzeug verbosity in production
        if not LoggerFactory._is_development():
            werkzeug_logger.setLevel(logging.WARNING)

    @staticmethod
    def _is_development() -> bool:
        """Check if running in development mode."""
        # Simple check - in a real implementation this would use the config
        import os

        return os.getenv("FLASK_ENV", "development").lower() == "development"


class RequestLogger:
    """Utility class for logging HTTP requests."""

    def __init__(self, logger: Optional[logging.Logger] = None):
        """Initialize request logger.

        Args:
            logger: Logger instance (optional)
        """
        self.logger = logger or logging.getLogger(__name__)

    def log_request_start(self, method: str, path: str, remote_addr: str) -> None:
        """Log the start of a request.

        Args:
            method: HTTP method
            path: Request path
            remote_addr: Client IP address
        """
        self.logger.info(f"Request started: {method} {path} from {remote_addr}")

    def log_request_end(
        self, method: str, path: str, status_code: int, duration_ms: float
    ) -> None:
        """Log the end of a request.

        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            duration_ms: Request duration in milliseconds
        """
        level = logging.INFO
        if status_code >= 400:
            level = logging.WARNING
        if status_code >= 500:
            level = logging.ERROR

        self.logger.log(
            level,
            f"Request completed: {method} {path} - {status_code} ({duration_ms:.2f}ms)",
        )

    def log_request_error(self, method: str, path: str, error: Exception) -> None:
        """Log a request error.

        Args:
            method: HTTP method
            path: Request path
            error: Exception that occurred
        """
        self.logger.error(
            f"Request error: {method} {path} - {type(error).__name__}: {error}",
            exc_info=True,
        )
