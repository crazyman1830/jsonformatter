"""Web routes for serving the main HTML interface and static content."""

import logging
from typing import Optional, Union, Tuple, Dict
from flask import Blueprint, send_from_directory, current_app, Response


class WebRoutes:
    """
    Class-based web routes for serving HTML templates and static content.

    This class handles the main web interface routes, template rendering,
    and static file serving with proper error handling and logging.
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize web routes.

        Args:
            logger: Logger instance (optional)
        """
        self.logger = logger or logging.getLogger(__name__)
        self.blueprint = self._create_blueprint()

        self.logger.debug("WebRoutes initialized")

    def _create_blueprint(self) -> Blueprint:
        """
        Create and configure the web blueprint with all routes.

        Returns:
            Blueprint: Configured Flask blueprint
        """
        blueprint = Blueprint("web", __name__)

        # Register route handlers
        blueprint.add_url_rule(
            "/health", "health_check", self.health_check, methods=["GET"]
        )
        blueprint.add_url_rule(
            "/static/<path:filename>",
            "static_files",
            self.serve_static,
            methods=["GET"],
        )

        self.logger.debug("Web blueprint created with all routes")
        return blueprint

    def health_check(self) -> Dict[str, str]:
        """
        Health check endpoint for monitoring and load balancers.

        Returns:
            dict: Health status information
        """
        self.logger.debug("Health check endpoint accessed")

        return {"status": "healthy", "service": "JSON Formatter", "version": "1.0.0"}

    def serve_static(
        self, filename: str
    ) -> Union[Response, Tuple[Dict[str, str], int]]:
        """
        Serve static files with proper error handling.

        Args:
            filename: Static file path

        Returns:
            Flask response for static file
        """
        self.logger.debug(f"Serving static file: {filename}")

        try:
            # Use Flask's built-in static file serving
            static_folder = current_app.static_folder
            if static_folder is None:
                raise ValueError("Static folder not configured")
            return send_from_directory(static_folder, filename)
        except Exception as e:
            self.logger.error(f"Error serving static file {filename}: {str(e)}")
            return {"error": "File not found"}, 404


def create_web_blueprint() -> Blueprint:
    """
    Create and configure the web blueprint.

    Returns:
        Blueprint: Configured web blueprint
    """
    web_routes = WebRoutes()
    return web_routes.blueprint
