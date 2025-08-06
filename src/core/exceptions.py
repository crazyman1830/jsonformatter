"""Custom exception classes for the JSON Formatter application."""

from typing import Optional, Dict, Any


class JSONFormatterError(Exception):
    """Base exception class for JSON Formatter application.

    All custom exceptions in the application should inherit from this class.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize the exception.

        Args:
            message: Error message
            details: Additional error details (optional)
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}

    @property
    def http_status_code(self) -> int:
        """Get the HTTP status code for this exception.

        Returns:
            int: HTTP status code (default: 500)
        """
        return 500

    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format.

        Returns:
            Dict[str, Any]: Exception data as dictionary
        """
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "details": self.details,
            "http_status_code": self.http_status_code,
        }


class ValidationError(JSONFormatterError):
    """Exception raised when input validation fails.

    This exception is used for client-side errors such as invalid JSON,
    missing required fields, or data that doesn't meet validation criteria.
    """

    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the validation error.

        Args:
            message: Error message
            field: Field name that failed validation (optional)
            value: Invalid value (optional)
            details: Additional error details (optional)
        """
        error_details = details or {}
        if field:
            error_details["field"] = field
        if value is not None:
            error_details["invalid_value"] = str(value)

        super().__init__(message, error_details)
        self.field = field
        self.value = value

    @property
    def http_status_code(self) -> int:
        """Get the HTTP status code for validation errors.

        Returns:
            int: HTTP status code (400 - Bad Request)
        """
        return 400


class ProcessingError(JSONFormatterError):
    """Exception raised when JSON processing fails.

    This exception is used for errors that occur during JSON parsing,
    formatting, or other processing operations.
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        line_number: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the processing error.

        Args:
            message: Error message
            operation: Operation that failed (optional)
            line_number: Line number where error occurred (optional)
            details: Additional error details (optional)
        """
        error_details = details or {}
        if operation:
            error_details["operation"] = operation
        if line_number is not None:
            error_details["line_number"] = line_number

        super().__init__(message, error_details)
        self.operation = operation
        self.line_number = line_number

    @property
    def http_status_code(self) -> int:
        """Get the HTTP status code for processing errors.

        Returns:
            int: HTTP status code (422 - Unprocessable Entity)
        """
        return 422


class ConfigurationError(JSONFormatterError):
    """Exception raised when application configuration is invalid.

    This exception is used for errors related to missing or invalid
    configuration settings, environment variables, or application setup.
    """

    def __init__(
        self,
        message: str,
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the configuration error.

        Args:
            message: Error message
            config_key: Configuration key that caused the error (optional)
            details: Additional error details (optional)
        """
        error_details = details or {}
        if config_key:
            error_details["config_key"] = config_key

        super().__init__(message, error_details)
        self.config_key = config_key

    @property
    def http_status_code(self) -> int:
        """Get the HTTP status code for configuration errors.

        Returns:
            int: HTTP status code (500 - Internal Server Error)
        """
        return 500


class ContentTooLargeError(ValidationError):
    """Exception raised when request content exceeds size limits.

    This is a specialized validation error for content size violations.
    """

    def __init__(
        self,
        message: str,
        content_size: int,
        max_size: int,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the content too large error.

        Args:
            message: Error message
            content_size: Actual content size in bytes
            max_size: Maximum allowed size in bytes
            details: Additional error details (optional)
        """
        error_details = details or {}
        error_details.update({"content_size": content_size, "max_size": max_size})

        super().__init__(message, details=error_details)
        self.content_size = content_size
        self.max_size = max_size

    @property
    def http_status_code(self) -> int:
        """Get the HTTP status code for content too large errors.

        Returns:
            int: HTTP status code (413 - Payload Too Large)
        """
        return 413


class JSONParseError(ProcessingError):
    """Exception raised when JSON parsing fails.

    This is a specialized processing error for JSON parsing issues.
    """

    def __init__(
        self,
        message: str,
        json_content: Optional[str] = None,
        line_number: Optional[int] = None,
        column: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        """Initialize the JSON parse error.

        Args:
            message: Error message
            json_content: JSON content that failed to parse (optional)
            line_number: Line number where error occurred (optional)
            column: Column number where error occurred (optional)
            details: Additional error details (optional)
        """
        error_details = details or {}
        if column is not None:
            error_details["column"] = column
        if json_content:
            # Only include a snippet of the content for security
            content_snippet = (
                json_content[:200] + "..." if len(json_content) > 200 else json_content
            )
            error_details["content_snippet"] = content_snippet

        super().__init__(
            message,
            operation="json_parse",
            line_number=line_number,
            details=error_details,
        )
        self.json_content = json_content
        self.column = column


# Exception mapping for HTTP status codes
EXCEPTION_HTTP_STATUS_MAP = {
    ValidationError: 400,
    ContentTooLargeError: 413,
    ProcessingError: 422,
    JSONParseError: 422,
    ConfigurationError: 500,
    JSONFormatterError: 500,
}


def get_http_status_code(exception: Exception) -> int:
    """Get the appropriate HTTP status code for an exception.

    Args:
        exception: Exception instance

    Returns:
        int: HTTP status code
    """
    if hasattr(exception, "http_status_code"):
        return int(exception.http_status_code)

    for exc_type, status_code in EXCEPTION_HTTP_STATUS_MAP.items():
        if isinstance(exception, exc_type):
            return status_code

    # Default to 500 for unknown exceptions
    return 500
