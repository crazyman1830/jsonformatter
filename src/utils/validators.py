"""
Utility functions for input validation and data processing.

This module provides reusable validation functions and helper utilities
that support the JSON formatter application with comprehensive type hints
and error handling.
"""

import json
import re
from typing import Any, Optional, Tuple
from urllib.parse import urlparse


def validate_json_string(data: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate that input is a non-empty string suitable for JSON processing.

    Args:
        data: Input data to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)

    Examples:
        >>> validate_json_string('{"key": "value"}')
        (True, None)
        >>> validate_json_string('')
        (False, 'Input cannot be empty')
        >>> validate_json_string(None)
        (False, 'Input cannot be None')
    """
    if data is None:
        return False, "Input cannot be None"

    if not isinstance(data, str):
        return False, f"Input must be a string, got {type(data).__name__}"

    if len(data.strip()) == 0:
        return False, "Input cannot be empty"

    return True, None


def validate_indent_value(indent: Any) -> Tuple[bool, int, Optional[str]]:
    """
    Validate and normalize indentation value for JSON formatting.

    Args:
        indent: Indentation value to validate

    Returns:
        Tuple[bool, int, Optional[str]]: (is_valid, normalized_value, error_message)

    Examples:
        >>> validate_indent_value(2)
        (True, 2, None)
        >>> validate_indent_value('4')
        (True, 4, None)
        >>> validate_indent_value(-1)
        (False, 2, 'Indent must be between 0 and 10')
    """
    default_indent = 2

    if indent is None:
        return True, default_indent, None

    try:
        indent_int = int(indent)

        if indent_int < 0 or indent_int > 10:
            return False, default_indent, "Indent must be between 0 and 10"

        return True, indent_int, None

    except (ValueError, TypeError):
        return False, default_indent, f"Invalid indent value: {indent}"


def validate_boolean_parameter(
    value: Any, default: bool = True
) -> Tuple[bool, bool, Optional[str]]:
    """
    Validate and normalize boolean parameters from various input types.

    Args:
        value: Value to validate as boolean
        default: Default value if validation fails

    Returns:
        Tuple[bool, bool, Optional[str]]: (is_valid, normalized_value, error_message)

    Examples:
        >>> validate_boolean_parameter(True)
        (True, True, None)
        >>> validate_boolean_parameter('false')
        (True, False, None)
        >>> validate_boolean_parameter('invalid')
        (False, True, 'Invalid boolean value: invalid')
    """
    if value is None:
        return True, default, None

    if isinstance(value, bool):
        return True, value, None

    if isinstance(value, str):
        lower_value = value.lower().strip()
        if lower_value in ("true", "1", "yes", "on"):
            return True, True, None
        elif lower_value in ("false", "0", "no", "off"):
            return True, False, None
        else:
            return False, default, f"Invalid boolean value: {value}"

    if isinstance(value, (int, float)):
        return True, bool(value), None

    return False, default, f"Cannot convert {type(value).__name__} to boolean"


def validate_session_id(session_id: Any) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Validate session ID format and content.

    Args:
        session_id: Session ID to validate

    Returns:
        Tuple[bool, Optional[str], Optional[str]]: (is_valid, normalized_id, error_message)

    Examples:
        >>> validate_session_id('abc123')
        (True, 'abc123', None)
        >>> validate_session_id('')
        (False, None, 'Session ID cannot be empty')
    """
    if session_id is None:
        return False, None, "Session ID cannot be None"

    if not isinstance(session_id, str):
        return (
            False,
            None,
            f"Session ID must be a string, got {type(session_id).__name__}",
        )

    session_id = session_id.strip()

    if len(session_id) == 0:
        return False, None, "Session ID cannot be empty"

    if len(session_id) > 255:
        return False, None, "Session ID too long (max 255 characters)"

    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not re.match(r"^[a-zA-Z0-9_-]+$", session_id):
        return False, None, "Session ID contains invalid characters"

    return True, session_id, None


def validate_content_length(
    content: Any, max_length: int = 1048576
) -> Tuple[bool, Optional[str]]:
    """
    Validate content length against maximum allowed size.

    Args:
        content: Content to validate
        max_length: Maximum allowed length in bytes (default: 1MB)

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)

    Examples:
        >>> validate_content_length('short content')
        (True, None)
        >>> validate_content_length('x' * 2000000)  # 2MB
        (False, 'Content too large: 2000000 bytes (max: 1048576)')
    """
    if not isinstance(content, str):
        return False, f"Content must be a string, got {type(content).__name__}"

    content_length = len(content.encode("utf-8"))

    if content_length > max_length:
        return False, f"Content too large: {content_length} bytes (max: {max_length})"

    return True, None


def sanitize_error_message(error_msg: Any, max_length: int = 500) -> str:
    """
    Sanitize error messages for safe display and logging.

    Args:
        error_msg: Error message to sanitize
        max_length: Maximum length of sanitized message

    Returns:
        str: Sanitized error message

    Examples:
        >>> sanitize_error_message('Simple error')
        'Simple error'
        >>> sanitize_error_message('Error with <script>alert("xss")</script>')
        'Error with alert("xss")'
    """
    if not isinstance(error_msg, str):
        error_msg = str(error_msg)

    # Remove HTML tags
    error_msg = re.sub(r"<[^>]+>", "", error_msg)

    # Remove control characters except newlines and tabs
    error_msg = re.sub(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]", "", error_msg)

    # Truncate if too long
    if len(error_msg) > max_length:
        error_msg = error_msg[: max_length - 3] + "..."

    return str(error_msg).strip()


def extract_json_error_line(error_msg: Any) -> Optional[int]:
    """
    Extract line number from JSON error messages.

    Args:
        error_msg: JSON error message

    Returns:
        Optional[int]: Line number if found, None otherwise

    Examples:
        >>> extract_json_error_line(
        ...     'Expecting property name enclosed in double quotes: line 5 column 1'
        ... )
        5
        >>> extract_json_error_line('Invalid JSON syntax')
        None
    """
    if not isinstance(error_msg, str):
        return None

    # Common patterns for line numbers in JSON error messages
    patterns = [
        r"line (\d+)",
        r"at line (\d+)",
        r"on line (\d+)",
        r"line:(\d+)",
        r"lineno=(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, error_msg, re.IGNORECASE)
        if match:
            try:
                return int(match.group(1))
            except (ValueError, IndexError):
                continue

    return None


def normalize_line_endings(text: Any) -> str:
    """
    Normalize line endings to Unix style (LF).

    Args:
        text: Text with potentially mixed line endings

    Returns:
        str: Text with normalized line endings

    Examples:
        >>> normalize_line_endings('line1\\r\\nline2\\rline3\\n')
        'line1\\nline2\\nline3\\n'
    """
    if not isinstance(text, str):
        return str(text)

    # Replace CRLF and CR with LF
    text = text.replace("\r\n", "\n")
    text = text.replace("\r", "\n")

    return str(text)


def is_valid_json_type(data: Any) -> bool:
    """
    Check if data type is valid for JSON serialization.

    Args:
        data: Data to check

    Returns:
        bool: True if data can be JSON serialized

    Examples:
        >>> is_valid_json_type({'key': 'value'})
        True
        >>> is_valid_json_type(set([1, 2, 3]))
        False
    """
    try:
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False


def get_json_type_name(data: Any) -> str:
    """
    Get human-readable JSON type name for data.

    Args:
        data: Data to analyze

    Returns:
        str: JSON type name

    Examples:
        >>> get_json_type_name({'key': 'value'})
        'object'
        >>> get_json_type_name([1, 2, 3])
        'array'
        >>> get_json_type_name('hello')
        'string'
    """
    if data is None:
        return "null"
    elif isinstance(data, bool):
        return "boolean"
    elif isinstance(data, int):
        return "integer"
    elif isinstance(data, float):
        return "number"
    elif isinstance(data, str):
        return "string"
    elif isinstance(data, list):
        return "array"
    elif isinstance(data, dict):
        return "object"
    else:
        return type(data).__name__


def validate_url(url: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format and basic structure.

    Args:
        url: URL string to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)

    Examples:
        >>> validate_url('https://example.com')
        (True, None)
        >>> validate_url('not-a-url')
        (False, 'Invalid URL format')
    """
    if not isinstance(url, str):
        return False, f"URL must be a string, got {type(url).__name__}"

    url = url.strip()

    if not url:
        return False, "URL cannot be empty"

    try:
        parsed = urlparse(url)

        if not parsed.scheme:
            return False, "URL must include a scheme (http, https, etc.)"

        if not parsed.netloc:
            return False, "URL must include a domain"

        if parsed.scheme not in ("http", "https", "ftp", "ftps"):
            return False, f"Unsupported URL scheme: {parsed.scheme}"

        return True, None

    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def create_safe_filename(filename: Any, max_length: int = 255) -> str:
    """
    Create a safe filename by removing/replacing invalid characters.

    Args:
        filename: Original filename
        max_length: Maximum filename length

    Returns:
        str: Safe filename

    Examples:
        >>> create_safe_filename('my file<>:"/\\|?*.json')
        'my_file.json'
        >>> create_safe_filename('very_long_filename' * 20)
        'very_long_filenamevery_long_filenamevery_long_filenamevery_long_filenamevery_long_filenamevery_long_filenamevery_long_filenamevery_long_filenamevery_long_filenamevery_long_filenamevery_long_filenamevery_long_filename...'
    """
    if not isinstance(filename, str):
        filename = str(filename)

    # Remove or replace invalid characters
    # Windows invalid characters: < > : " / \ | ? *
    # Also remove control characters
    safe_filename = re.sub(r'[<>:"/\\|?*\x00-\x1f\x7f]', "_", filename)

    # Remove leading/trailing spaces and dots
    safe_filename = safe_filename.strip(" .")

    # Ensure it's not empty
    if not safe_filename:
        safe_filename = "untitled"

    # Truncate if too long
    if len(safe_filename) > max_length:
        name, ext = (
            safe_filename.rsplit(".", 1)
            if "." in safe_filename
            else (safe_filename, "")
        )
        max_name_length = max_length - len(ext) - 1 if ext else max_length
        safe_filename = name[:max_name_length] + ("." + ext if ext else "")

    return safe_filename


def validate_http_method(method: Any) -> Tuple[bool, Optional[str]]:
    """
    Validate HTTP method name.

    Args:
        method: HTTP method to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)

    Examples:
        >>> validate_http_method('GET')
        (True, None)
        >>> validate_http_method('INVALID')
        (False, 'Invalid HTTP method: INVALID')
    """
    if not isinstance(method, str):
        return False, f"HTTP method must be a string, got {type(method).__name__}"

    method = method.upper().strip()

    valid_methods = {
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "HEAD",
        "OPTIONS",
        "TRACE",
        "CONNECT",
    }

    if method not in valid_methods:
        return False, f"Invalid HTTP method: {method}"

    return True, None


def truncate_string(text: Any, max_length: int, suffix: str = "...") -> str:
    """
    Truncate string to maximum length with optional suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating

    Returns:
        str: Truncated string

    Examples:
        >>> truncate_string('This is a long string', 10)
        'This is...'
        >>> truncate_string('Short', 10)
        'Short'
    """
    if not isinstance(text, str):
        text = str(text)

    if len(text) <= max_length:
        return str(text)

    if len(suffix) >= max_length:
        return str(text)[:max_length]

    return str(text)[: max_length - len(suffix)] + suffix


def is_empty_or_whitespace(value: Any) -> bool:
    """
    Check if value is None, empty, or contains only whitespace.

    Args:
        value: Value to check

    Returns:
        bool: True if empty or whitespace only

    Examples:
        >>> is_empty_or_whitespace('')
        True
        >>> is_empty_or_whitespace('   ')
        True
        >>> is_empty_or_whitespace('content')
        False
    """
    if value is None:
        return True

    if isinstance(value, str):
        return len(value.strip()) == 0

    if isinstance(value, (list, dict, tuple, set)):
        return len(value) == 0

    return False


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """
    Safely convert value to integer with fallback default.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        int: Converted integer or default

    Examples:
        >>> safe_int_conversion('123')
        123
        >>> safe_int_conversion('invalid')
        0
        >>> safe_int_conversion('invalid', -1)
        -1
    """
    if isinstance(value, int):
        return value

    if isinstance(value, float):
        return int(value)

    if isinstance(value, str):
        try:
            return int(value.strip())
        except (ValueError, AttributeError):
            pass

    return default


def validate_email_format(email: Any) -> Tuple[bool, Optional[str]]:
    """
    Basic email format validation.

    Args:
        email: Email address to validate

    Returns:
        Tuple[bool, Optional[str]]: (is_valid, error_message)

    Examples:
        >>> validate_email_format('user@example.com')
        (True, None)
        >>> validate_email_format('invalid-email')
        (False, 'Invalid email format')
    """
    if not isinstance(email, str):
        return False, f"Email must be a string, got {type(email).__name__}"

    email = email.strip()

    if not email:
        return False, "Email cannot be empty"

    # Basic email regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    if not re.match(pattern, email):
        return False, "Invalid email format"

    if len(email) > 254:  # RFC 5321 limit
        return False, "Email address too long"

    return True, None
