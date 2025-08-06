"""Request logging middleware for Flask applications."""

import time
import logging
from typing import Optional, TYPE_CHECKING
from flask import Flask, request, g

if TYPE_CHECKING:
    from flask import Response

from core.logging import RequestLogger


class RequestLoggingMiddleware:
    """Middleware for logging HTTP requests and responses."""

    def __init__(
        self, app: Optional[Flask] = None, logger: Optional[logging.Logger] = None
    ):
        """Initialize the request logging middleware.

        Args:
            app: Flask application instance (optional)
            logger: Logger instance (optional)
        """
        self.request_logger = RequestLogger(logger)

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize the middleware with a Flask application.

        Args:
            app: Flask application instance
        """
        app.before_request(self._before_request)
        app.after_request(self._after_request)
        app.teardown_request(self._teardown_request)

    def _before_request(self) -> None:
        """Handle request start logging."""
        g.start_time = time.time()

        # Log request start
        self.request_logger.log_request_start(
            method=request.method,
            path=request.path,
            remote_addr=request.remote_addr or "unknown",
        )

    def _after_request(self, response: "Response") -> "Response":
        """Handle request completion logging.

        Args:
            response: Flask response object

        Returns:
            Flask response object
        """
        # Calculate duration
        duration_ms = (
            (time.time() - g.start_time) * 1000 if hasattr(g, "start_time") else 0
        )

        # Log request completion
        self.request_logger.log_request_end(
            method=request.method,
            path=request.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )

        return response

    def _teardown_request(self, exception: Optional[BaseException]) -> None:
        """Handle request teardown and error logging.

        Args:
            exception: Exception that occurred during request processing (if any)
        """
        if exception is not None:
            self.request_logger.log_request_error(
                method=request.method,
                path=request.path,
                error=(
                    exception
                    if isinstance(exception, Exception)
                    else Exception(str(exception))
                ),
            )
