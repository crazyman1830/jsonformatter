"""Flask application factory for the JSON Formatter application."""

import logging
from typing import Optional, Union

from flask import Flask, render_template
from flasgger import Swagger
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from core.config import AppConfig
from core.exceptions import ConfigurationError
from core.logging import LoggerFactory
from services.comment_service import CommentService, SessionCommentStorage
from services.json_processor import JSONProcessorService
from web.middleware.logging import RequestLoggingMiddleware


def create_app(config: Optional[AppConfig] = None) -> Flask:
    """
    Create and configure Flask application using the factory pattern.

    Args:
        config: Application configuration (optional, will load from env if not provided)

    Returns:
        Flask: Configured Flask application instance

    Raises:
        ConfigurationError: If configuration is invalid
    """
    # Load configuration if not provided
    if config is None:
        config = AppConfig.from_env()

    # Validate configuration
    config.validate()

    # Determine paths for frontend
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    frontend_dist = os.path.join(base_dir, "frontend", "dist")
    
    if os.path.exists(frontend_dist):
        template_folder = frontend_dist
        static_folder = os.path.join(frontend_dist, "assets")
        static_url_path = "/assets"
    else:
        # Fallback for development or if build missing
        template_folder = "templates"
        static_folder = "static"
        static_url_path = "/static"

    # Create Flask application
    app = Flask(
        __name__, 
        template_folder=template_folder, 
        static_folder=static_folder,
        static_url_path=static_url_path
    )

    # Configure Flask settings
    app.config.update(
        {
            "DEBUG": config.debug,
            "TESTING": config.is_testing,
            "SECRET_KEY": config.secret_key,
            "JSON_SORT_KEYS": False,
            "MAX_CONTENT_LENGTH": config.max_content_length,
        }
    )

    # Set up logging
    LoggerFactory._setup_root_logger(config)
    logger = LoggerFactory.create_logger(__name__, config)
    logger.info(f"Creating Flask application - Environment: {config.environment.value}")

    # Initialize services with dependency injection
    json_service = JSONProcessorService(
        logger=LoggerFactory.create_logger("json_processor")
    )
    comment_storage = SessionCommentStorage()
    comment_service = CommentService(
        storage=comment_storage, logger=LoggerFactory.create_logger("comment_service")
    )

    # Store services in app context for access by routes
    app.json_service = json_service  # type: ignore[attr-defined]
    app.comment_service = comment_service  # type: ignore[attr-defined]
    app.config_obj = config  # type: ignore[attr-defined]

    # Set up request logging middleware
    RequestLoggingMiddleware(
        app=app, logger=LoggerFactory.create_logger("request_middleware")
    )

    # Initialize Swagger
    Swagger(app)

    # Configure CORS
    CORS(app)

    # Configure Rate Limiting
    Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://",
    )

    # Register blueprints
    _register_blueprints(app, json_service, comment_service)

    # Register error handlers
    _register_error_handlers(app)

    # Main route to serve the frontend
    @app.route("/")
    def index() -> str:
        """Serve the main HTML interface."""
        logger.debug("Serving main HTML interface")
        # In production with React, this serves index.html from dist
        return render_template("index.html")

    # Catch-all route for React Router (if needed in future)
    @app.route("/<path:path>")
    def catch_all(path: str) -> str:
        if path.startswith("api") or path.startswith("assets"):
            return "Not Found", 404
        return render_template("index.html")

    logger.info("Flask application created successfully")
    return app


def _register_blueprints(
    app: Flask, json_service: JSONProcessorService, comment_service: CommentService
) -> None:
    """
    Register application blueprints with dependency injection.

    Args:
        app: Flask application instance
        json_service: JSON processing service
        comment_service: Comment management service
    """
    logger = logging.getLogger(__name__)

    try:
        # Import and register API routes
        from web.routes.api import create_api_blueprint

        api_blueprint = create_api_blueprint(json_service, comment_service)
        app.register_blueprint(api_blueprint, url_prefix="/api")
        logger.debug("API blueprint registered")

        # Import and register web routes
        from web.routes.web import create_web_blueprint

        web_blueprint = create_web_blueprint()
        app.register_blueprint(web_blueprint)
        logger.debug("Web blueprint registered")

    except ImportError as e:
        logger.warning(f"Could not import blueprint: {e}")
        # Blueprints will be created in subsequent tasks


def _register_error_handlers(app: Flask) -> None:
    """
    Register application error handlers.

    Args:
        app: Flask application instance
    """
    logger = logging.getLogger(__name__)

    @app.errorhandler(404)
    def not_found_error(error: Exception) -> tuple[dict[str, Union[bool, str]], int]:
        """Handle 404 errors."""
        logger.warning(f"404 error: {error}")
        return {
            "success": False,
            "error_code": "NOT_FOUND",
            "error_message": "The requested resource was not found",
        }, 404

    @app.errorhandler(500)
    def internal_error(error: Exception) -> tuple[dict[str, Union[bool, str]], int]:
        """Handle 500 errors."""
        logger.error(f"500 error: {error}", exc_info=True)
        return {
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "error_message": "An internal server error occurred",
        }, 500

    @app.errorhandler(413)
    def request_entity_too_large(
        error: Exception,
    ) -> tuple[dict[str, Union[bool, str]], int]:
        """Handle request too large errors."""
        logger.warning(f"413 error: {error}")
        return {
            "success": False,
            "error_code": "REQUEST_TOO_LARGE",
            "error_message": "Request entity too large",
        }, 413

    logger.debug("Error handlers registered")


def create_development_app() -> Flask:
    """
    Create a Flask application configured for development.

    Returns:
        Flask: Development-configured Flask application
    """
    import os

    os.environ.setdefault("FLASK_ENV", "development")
    os.environ.setdefault("FLASK_DEBUG", "true")
    os.environ.setdefault("SECRET_KEY", "development-secret-key-change-in-production")

    return create_app()


def create_testing_app() -> Flask:
    """
    Create a Flask application configured for testing.

    Returns:
        Flask: Testing-configured Flask application
    """
    import os

    os.environ.setdefault("FLASK_ENV", "testing")
    os.environ.setdefault("FLASK_DEBUG", "false")
    os.environ.setdefault("SECRET_KEY", "testing-secret-key")
    os.environ.setdefault("LOG_LEVEL", "WARNING")

    return create_app()


def create_production_app() -> Flask:
    """
    Create a Flask application configured for production.

    Returns:
        Flask: Production-configured Flask application

    Raises:
        ConfigurationError: If production configuration is invalid
    """
    import os

    # Ensure required production environment variables are set
    if not os.getenv("SECRET_KEY"):
        raise ConfigurationError(
            "SECRET_KEY environment variable is required for production",
            config_key="SECRET_KEY",
        )

    os.environ.setdefault("FLASK_ENV", "production")
    os.environ.setdefault("FLASK_DEBUG", "false")
    os.environ.setdefault("LOG_LEVEL", "INFO")

    return create_app()
