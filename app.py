"""
JSON Formatter Web Application
Main Flask application entry point with improved structure and error handling.

This module serves as the main entry point for the JSON Formatter application,
utilizing the Flask application factory pattern with proper configuration management,
logging, and error handling.
"""

import sys
import os
from typing import NoReturn

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from core.config import AppConfig
from core.exceptions import ConfigurationError
from core.logging import LoggerFactory
from web.app import create_app


def main() -> NoReturn:
    """
    Main application entry point with comprehensive error handling.

    This function initializes the application configuration, sets up logging,
    creates the Flask application using the factory pattern, and starts the server.

    Raises:
        SystemExit: On configuration or application errors
    """
    try:
        # Load configuration from environment
        config = AppConfig.from_env()

        # Set up basic logging before creating the app
        LoggerFactory._setup_root_logger(config)
        logger = LoggerFactory.create_logger(__name__, config)

        logger.info("Initializing JSON Formatter Application")
        logger.info(f"Environment: {config.environment.value}")
        logger.info(f"Debug mode: {config.debug}")
        logger.info(f"Log level: {config.log_level}")

        # Create app with configuration
        app = create_app(config)

        # Display startup information
        print("=" * 60)
        print("JSON Formatter Application Starting")
        print("=" * 60)
        print(f"Environment: {config.environment.value}")
        print(f"Host: {config.host}")
        print(f"Port: {config.port}")
        print(f"Debug: {config.debug}")
        print(f"Log Level: {config.log_level}")
        print("=" * 60)

        logger.info(f"Starting server on {config.host}:{config.port}")

        # Run the application
        app.run(
            debug=config.debug,
            host=config.host,
            port=config.port,
            use_reloader=config.debug,
            reloader_type="stat",  # Use 'stat' reloader to avoid issues with Python 3.13+
        )

    except ConfigurationError as e:
        error_msg = f"Configuration Error: {e}"
        print(f"ERROR: {error_msg}")

        # Try to log the error if logging is available
        try:
            logger = LoggerFactory.create_logger(__name__)
            logger.critical(error_msg)
        except Exception:  # nosec B110
            pass  # Logging might not be available yet

        sys.exit(1)

    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        try:
            logger = LoggerFactory.create_logger(__name__)
            logger.info("Application interrupted by user")
        except Exception:  # nosec B110
            pass
        sys.exit(0)

    except Exception as e:
        error_msg = f"Unexpected Application Error: {e}"
        print(f"ERROR: {error_msg}")

        # Try to log the error if logging is available
        try:
            logger = LoggerFactory.create_logger(__name__)
            logger.critical(error_msg, exc_info=True)
        except Exception:  # nosec B110
            pass  # Logging might not be available yet

        sys.exit(1)


def create_wsgi_app():
    """
    Create a WSGI application for production deployment.

    This function creates a Flask application configured for production use
    with WSGI servers like Gunicorn or uWSGI.

    Returns:
        Flask: Configured Flask application for WSGI deployment

    Raises:
        ConfigurationError: If production configuration is invalid
    """
    try:
        # Ensure we're in production mode
        os.environ.setdefault("FLASK_ENV", "production")
        os.environ.setdefault("FLASK_DEBUG", "false")

        # Load configuration
        config = AppConfig.from_env()

        # Set up logging
        LoggerFactory._setup_root_logger(config)
        logger = LoggerFactory.create_logger(__name__, config)

        logger.info("Creating WSGI application for production")

        # Create and return the app
        app = create_app(config)

        logger.info("WSGI application created successfully")
        return app

    except Exception as e:
        print(f"Failed to create WSGI application: {e}")
        raise


# WSGI application instance for production deployment
application = create_wsgi_app()


if __name__ == "__main__":
    main()
