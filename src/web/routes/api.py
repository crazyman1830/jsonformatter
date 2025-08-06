"""API routes for the JSON Formatter application."""

import logging
from typing import Dict, Any, Tuple, Optional
from flask import Blueprint, request, session

from services.json_processor import JSONProcessorService
from services.comment_service import CommentService
from core.exceptions import ValidationError, ProcessingError


class APIRoutes:
    """
    Class-based API routes for JSON formatting operations.

    This class encapsulates all API endpoints with proper dependency injection,
    error handling, and comprehensive logging.
    """

    def __init__(
        self,
        json_service: JSONProcessorService,
        comment_service: CommentService,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """
        Initialize API routes with service dependencies.

        Args:
            json_service: JSON processing service
            comment_service: Comment management service
            logger: Logger instance (optional)
        """
        self.json_service = json_service
        self.comment_service = comment_service
        self.logger = logger or logging.getLogger(__name__)
        self.blueprint = self._create_blueprint()

        self.logger.debug("APIRoutes initialized")

    def _create_blueprint(self) -> Blueprint:
        """
        Create and configure the API blueprint with all routes.

        Returns:
            Blueprint: Configured Flask blueprint
        """
        blueprint = Blueprint("api", __name__)

        # Register route handlers
        blueprint.add_url_rule("/", "index", self.index, methods=["GET"])
        blueprint.add_url_rule(
            "/format", "format_json", self.format_json, methods=["POST"]
        )
        blueprint.add_url_rule(
            "/validate", "validate_json", self.validate_json, methods=["POST"]
        )
        blueprint.add_url_rule(
            "/comments", "save_comments", self.save_comments, methods=["POST"]
        )
        blueprint.add_url_rule(
            "/comments", "load_comments", self.load_comments, methods=["GET"]
        )
        blueprint.add_url_rule(
            "/comments", "clear_comments", self.clear_comments, methods=["DELETE"]
        )

        self.logger.debug("API blueprint created with all routes")
        return blueprint

    def index(self) -> Dict[str, Any]:
        """
        API root endpoint providing service information.

        Returns:
            Dict[str, Any]: API information response
        """
        self.logger.debug("API index endpoint accessed")
        return {
            "success": True,
            "message": "JSON Formatter API",
            "version": "1.0.0",
            "endpoints": {
                "format": "/api/format (POST)",
                "validate": "/api/validate (POST)",
                "comments": "/api/comments (GET, POST, DELETE)",
            },
        }

    def format_json(self) -> Tuple[Dict[str, Any], int]:
        """
        Process JSON formatting requests with comprehensive error handling.

        Returns:
            Tuple[Dict[str, Any], int]: JSON response and HTTP status code
        """
        self.logger.info("JSON format request received")

        try:
            # Extract JSON data from request
            json_data = self._extract_json_data_from_request()

            # Get formatting options
            indent = self._get_indent_from_request()
            sort_keys = self._get_sort_keys_from_request()

            # Process JSON formatting
            format_result = self.json_service.format_json(
                raw_json=json_data, indent=indent, sort_keys=sort_keys
            )

            # Prepare response
            response = {
                "success": format_result.success,
                "formatted_json": format_result.formatted_json or "",
                "line_count": format_result.line_count,
                "error_message": format_result.error_message,
            }

            status_code = 200 if format_result.success else 400
            self.logger.info(
                f"JSON format request completed - Success: {format_result.success}"
            )

            return response, status_code

        except ValidationError as e:
            self.logger.warning(f"JSON format validation error: {str(e)}")
            return self._create_error_response("VALIDATION_ERROR", str(e)), 400

        except ProcessingError as e:
            self.logger.error(f"JSON format processing error: {str(e)}")
            return self._create_error_response("PROCESSING_ERROR", str(e)), 500

        except Exception as e:
            self.logger.error(
                f"Unexpected error in format_json: {str(e)}", exc_info=True
            )
            return (
                self._create_error_response(
                    "INTERNAL_ERROR", "An unexpected error occurred"
                ),
                500,
            )

    def validate_json(self) -> Tuple[Dict[str, Any], int]:
        """
        Validate JSON data without formatting.

        Returns:
            Tuple[Dict[str, Any], int]: JSON response and HTTP status code
        """
        self.logger.info("JSON validation request received")

        try:
            # Extract JSON data from request
            json_data = self._extract_json_data_from_request()

            # Validate JSON
            validation_result = self.json_service.validate_json(json_data)

            # Prepare response
            response = {
                "is_valid": validation_result.is_valid,
                "error_message": validation_result.error_message,
                "line_number": validation_result.line_number,
            }

            status_code = 200 if validation_result.is_valid else 400
            self.logger.info(
                f"JSON validation completed - Valid: {validation_result.is_valid}"
            )

            return response, status_code

        except ValidationError as e:
            self.logger.warning(f"JSON validation input error: {str(e)}")
            return {
                "is_valid": False,
                "error_message": str(e),
                "line_number": None,
            }, 400

        except ProcessingError as e:
            self.logger.error(f"JSON validation processing error: {str(e)}")
            return {
                "is_valid": False,
                "error_message": "Processing error occurred",
                "line_number": None,
            }, 500

        except Exception as e:
            self.logger.error(
                f"Unexpected error in validate_json: {str(e)}", exc_info=True
            )
            return {
                "is_valid": False,
                "error_message": "An unexpected error occurred",
                "line_number": None,
            }, 500

    def save_comments(self) -> Tuple[Dict[str, Any], int]:
        """
        Save comments for the current session.

        Returns:
            Tuple[Dict[str, Any], int]: JSON response and HTTP status code
        """
        self.logger.info("Save comments request received")

        try:
            # Validate request content type
            if not request.is_json:
                raise ValidationError("Request must be JSON")

            # Extract comments from request
            data = request.get_json()
            if not data:
                raise ValidationError("Request body cannot be empty")

            comments = data.get("comments", "")
            if not isinstance(comments, str):
                raise ValidationError("Comments must be a string")

            # Get session ID
            session_id = self._get_session_id()

            # Save comments using service
            success = self.comment_service.save_comments(session_id, comments)

            response = {
                "success": success,
                "message": (
                    "Comments saved successfully"
                    if success
                    else "Failed to save comments"
                ),
            }

            status_code = 200 if success else 500
            self.logger.info(f"Save comments completed - Success: {success}")

            return response, status_code

        except ValidationError as e:
            self.logger.warning(f"Save comments validation error: {str(e)}")
            return self._create_error_response("VALIDATION_ERROR", str(e)), 400

        except ProcessingError as e:
            self.logger.error(f"Save comments processing error: {str(e)}")
            return self._create_error_response("PROCESSING_ERROR", str(e)), 500

        except Exception as e:
            self.logger.error(
                f"Unexpected error in save_comments: {str(e)}", exc_info=True
            )
            return (
                self._create_error_response(
                    "INTERNAL_ERROR", "An unexpected error occurred"
                ),
                500,
            )

    def load_comments(self) -> Tuple[Dict[str, Any], int]:
        """
        Load comments for the current session.

        Returns:
            Tuple[Dict[str, Any], int]: JSON response and HTTP status code
        """
        self.logger.info("Load comments request received")

        try:
            # Get session ID
            session_id = self._get_session_id()

            # Load comments using service
            comments = self.comment_service.load_comments(session_id)

            response = {"success": True, "comments": comments}

            self.logger.info("Load comments completed successfully")
            return response, 200

        except ValidationError as e:
            self.logger.warning(f"Load comments validation error: {str(e)}")
            return self._create_error_response("VALIDATION_ERROR", str(e)), 400

        except ProcessingError as e:
            self.logger.error(f"Load comments processing error: {str(e)}")
            return self._create_error_response("PROCESSING_ERROR", str(e)), 500

        except Exception as e:
            self.logger.error(
                f"Unexpected error in load_comments: {str(e)}", exc_info=True
            )
            return (
                self._create_error_response(
                    "INTERNAL_ERROR", "An unexpected error occurred"
                ),
                500,
            )

    def clear_comments(self) -> Tuple[Dict[str, Any], int]:
        """
        Clear comments for the current session.

        Returns:
            Tuple[Dict[str, Any], int]: JSON response and HTTP status code
        """
        self.logger.info("Clear comments request received")

        try:
            # Get session ID
            session_id = self._get_session_id()

            # Clear comments using service
            success = self.comment_service.clear_comments(session_id)

            response = {
                "success": success,
                "message": (
                    "Comments cleared successfully"
                    if success
                    else "Failed to clear comments"
                ),
            }

            status_code = 200 if success else 500
            self.logger.info(f"Clear comments completed - Success: {success}")

            return response, status_code

        except ValidationError as e:
            self.logger.warning(f"Clear comments validation error: {str(e)}")
            return self._create_error_response("VALIDATION_ERROR", str(e)), 400

        except ProcessingError as e:
            self.logger.error(f"Clear comments processing error: {str(e)}")
            return self._create_error_response("PROCESSING_ERROR", str(e)), 500

        except Exception as e:
            self.logger.error(
                f"Unexpected error in clear_comments: {str(e)}", exc_info=True
            )
            return (
                self._create_error_response(
                    "INTERNAL_ERROR", "An unexpected error occurred"
                ),
                500,
            )

    def _extract_json_data_from_request(self) -> str:
        """
        Extract JSON data from the current request.

        Returns:
            str: JSON data string

        Raises:
            ValidationError: If JSON data is missing or invalid
        """
        if request.is_json:
            data = request.get_json()
            if not data:
                raise ValidationError("Request body cannot be empty")
            json_data = data.get("json_data", "")
        else:
            json_data = request.form.get("json_data", "")

        if not json_data:
            raise ValidationError("No JSON data provided")

        if not isinstance(json_data, str):
            raise ValidationError("JSON data must be a string")

        return json_data

    def _get_indent_from_request(self) -> int:
        """
        Get indentation value from request parameters.

        Returns:
            int: Indentation value (default: 2)
        """
        try:
            if request.is_json:
                data = request.get_json() or {}
                indent = data.get("indent", 2)
            else:
                indent = request.form.get("indent", 2)

            indent = int(indent)
            if indent < 0 or indent > 10:
                self.logger.warning(f"Invalid indent value {indent}, using default 2")
                return 2

            return indent
        except (ValueError, TypeError):
            self.logger.warning("Invalid indent parameter, using default 2")
            return 2

    def _get_sort_keys_from_request(self) -> bool:
        """
        Get sort_keys value from request parameters.

        Returns:
            bool: Whether to sort keys (default: True)
        """
        try:
            if request.is_json:
                data = request.get_json() or {}
                sort_keys = data.get("sort_keys", True)
            else:
                sort_keys = request.form.get("sort_keys", "true").lower()
                sort_keys = sort_keys in ("true", "1", "yes", "on")

            return bool(sort_keys)
        except (ValueError, TypeError):
            self.logger.warning("Invalid sort_keys parameter, using default True")
            return True

    def _get_session_id(self) -> str:
        """
        Get or create a session ID for the current request.

        Returns:
            str: Session ID
        """
        # Use Flask session ID or create a simple one
        if "session_id" not in session:
            import uuid

            session["session_id"] = str(uuid.uuid4())

        return str(session["session_id"])

    def _create_error_response(
        self, error_code: str, error_message: str
    ) -> Dict[str, Any]:
        """
        Create a standardized error response.

        Args:
            error_code: Error code identifier
            error_message: Human-readable error message

        Returns:
            Dict[str, Any]: Standardized error response
        """
        return {
            "success": False,
            "error_code": error_code,
            "error_message": error_message,
        }


def create_api_blueprint(
    json_service: JSONProcessorService, comment_service: CommentService
) -> Blueprint:
    """
    Create and configure the API blueprint with dependency injection.

    Args:
        json_service: JSON processing service
        comment_service: Comment management service

    Returns:
        Blueprint: Configured API blueprint
    """
    api_routes = APIRoutes(json_service, comment_service)
    return api_routes.blueprint
