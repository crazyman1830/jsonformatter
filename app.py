"""
JSON Formatter Web Application
Main Flask application entry point
"""

import sys
import os

# Add src directory to Python path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from core.config import AppConfig
from core.exceptions import ConfigurationError
from web.app import create_app


def main() -> None:
    """Main application entry point"""
    try:
        # Load configuration from environment
        config = AppConfig.from_env()

        # Create app with configuration
        app = create_app(config)

        print("Starting JSON Formatter Application...")
        print(f"Environment: {config.environment.value}")
        print(f"Host: {config.host}")
        print(f"Port: {config.port}")
        print(f"Debug: {config.debug}")

        # Run the application
        app.run(
            debug=config.debug,
            host=config.host,
            port=config.port,
            use_reloader=config.debug,
            reloader_type="stat",  # Use 'stat' reloader to avoid issues with Python 3.13+
        )

    except ConfigurationError as e:
        print(f"Configuration Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Application Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
