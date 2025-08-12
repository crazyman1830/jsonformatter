"""
Utility functions and validators for the JSON Formatter application.

This package provides reusable utility functions for input validation,
data processing, and common operations with comprehensive type hints
and error handling.
"""

from .validators import (
    create_safe_filename,
    extract_json_error_line,
    get_json_type_name,
    is_empty_or_whitespace,
    is_valid_json_type,
    normalize_line_endings,
    safe_int_conversion,
    sanitize_error_message,
    truncate_string,
    validate_boolean_parameter,
    validate_content_length,
    validate_email_format,
    validate_http_method,
    validate_indent_value,
    validate_json_string,
    validate_session_id,
    validate_url,
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
