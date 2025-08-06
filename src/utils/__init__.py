"""
Utility functions and validators for the JSON Formatter application.

This package provides reusable utility functions for input validation,
data processing, and common operations with comprehensive type hints
and error handling.
"""

from .validators import (
    # JSON validation utilities
    validate_json_string,
    validate_indent_value,
    validate_boolean_parameter,
    validate_content_length,
    # Session and security utilities
    validate_session_id,
    sanitize_error_message,
    # JSON processing helpers
    extract_json_error_line,
    normalize_line_endings,
    is_valid_json_type,
    get_json_type_name,
    # General validation utilities
    validate_url,
    validate_http_method,
    validate_email_format,
    # String and data utilities
    create_safe_filename,
    truncate_string,
    is_empty_or_whitespace,
    safe_int_conversion,
)

__all__ = [
    # JSON validation utilities
    "validate_json_string",
    "validate_indent_value",
    "validate_boolean_parameter",
    "validate_content_length",
    # Session and security utilities
    "validate_session_id",
    "sanitize_error_message",
    # JSON processing helpers
    "extract_json_error_line",
    "normalize_line_endings",
    "is_valid_json_type",
    "get_json_type_name",
    # General validation utilities
    "validate_url",
    "validate_http_method",
    "validate_email_format",
    # String and data utilities
    "create_safe_filename",
    "truncate_string",
    "is_empty_or_whitespace",
    "safe_int_conversion",
]
