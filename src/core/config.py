"""Configuration management for the JSON Formatter application."""

import os

from dataclasses import dataclass
from enum import Enum


def _clean_env_value(value: str) -> str:
    """Strip inline comments and whitespace from environment variable values."""
    if not value:
        return value
    # Remove inline comments (anything after #)
    if '#' in value:
        value = value.split('#')[0]
    # Strip whitespace
    return value.strip()


class Environment(Enum):
    """Application environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


@dataclass
class AppConfig:
    """Application configuration class."""

    environment: Environment
    debug: bool
    secret_key: str
    host: str
    port: int
    log_level: str
    max_content_length: int

    @classmethod
    def from_env(cls) -> "AppConfig":
        """Load configuration from environment variables.

        Returns:
            AppConfig: Configured application settings

        Raises:
            ConfigurationError: If required environment variables are missing
        """
        # Load environment variables from .env file if it exists
        try:
            from dotenv import load_dotenv

            load_dotenv()
        except ImportError:
            # python-dotenv not installed, continue with system env vars
            pass

        # Get environment
        env_str = os.getenv("FLASK_ENV", "development").lower()
        try:
            environment = Environment(env_str)
        except ValueError:
            environment = Environment.DEVELOPMENT

        # Import here to avoid circular imports
        from .exceptions import ConfigurationError

        # Validate required environment variables
        secret_key = os.getenv("SECRET_KEY")
        if not secret_key:
            raise ConfigurationError(
                "SECRET_KEY environment variable is required", config_key="SECRET_KEY"
            )

        # Get configuration values with defaults
        debug = os.getenv("FLASK_DEBUG", "false").lower() in ("true", "1", "yes", "on")
        host = os.getenv("FLASK_HOST", "127.0.0.1")

        # Parse port with validation
        try:
            port = int(os.getenv("FLASK_PORT", "5000"))
            if not (1 <= port <= 65535):
                raise ValueError("Port must be between 1 and 65535")
        except ValueError as e:
            raise ConfigurationError(
                f"Invalid FLASK_PORT: {e}", config_key="FLASK_PORT"
            )

        # Parse log level
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if log_level not in valid_log_levels:
            log_level = "INFO"

        # Parse max content length with comment/whitespace handling
        try:
            max_content_length_str = _clean_env_value(os.getenv("MAX_CONTENT_LENGTH", "1048576"))
            max_content_length = int(max_content_length_str)
            if max_content_length <= 0:
                raise ValueError("MAX_CONTENT_LENGTH must be positive")
        except ValueError as e:
            raise ConfigurationError(
                f"Invalid MAX_CONTENT_LENGTH: {e}", config_key="MAX_CONTENT_LENGTH"
            )

        return cls(
            environment=environment,
            debug=debug,
            secret_key=secret_key,
            host=host,
            port=port,
            log_level=log_level,
            max_content_length=max_content_length,
        )

    def validate(self) -> None:
        """Validate the configuration.

        Raises:
            ConfigurationError: If configuration is invalid
        """
        from .exceptions import ConfigurationError

        if not self.secret_key:
            raise ConfigurationError(
                "Secret key cannot be empty", config_key="SECRET_KEY"
            )

        if len(self.secret_key) < 16:
            raise ConfigurationError(
                "Secret key must be at least 16 characters long",
                config_key="SECRET_KEY",
            )

        if not (1 <= self.port <= 65535):
            raise ConfigurationError(
                "Port must be between 1 and 65535", config_key="FLASK_PORT"
            )

        if self.max_content_length <= 0:
            raise ConfigurationError(
                "Max content length must be positive", config_key="MAX_CONTENT_LENGTH"
            )

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.environment == Environment.TESTING

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment == Environment.PRODUCTION
