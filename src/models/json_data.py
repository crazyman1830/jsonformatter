"""
JSON data models for validation, parsing, and formatting operations.

This module provides data classes and models for handling JSON data
with comprehensive validation and error handling capabilities.
"""

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class JSONValidationResult:
    """Result of JSON validation operation."""

    is_valid: bool
    error_message: Optional[str] = None
    line_number: Optional[int] = None

    def __bool__(self) -> bool:
        """Allow boolean evaluation of validation result."""
        return self.is_valid


@dataclass
class JSONFormatResult:
    """Result of JSON formatting operation."""

    success: bool
    formatted_json: Optional[str] = None
    error_message: Optional[str] = None
    line_count: int = 0

    def __bool__(self) -> bool:
        """Allow boolean evaluation of format result."""
        return self.success


class JSONData:
    """
    JSON data model with validation, parsing, and formatting capabilities.

    This class encapsulates JSON data and provides methods for validation,
    parsing, and formatting with comprehensive error handling.
    """

    def __init__(self, raw_data: str) -> None:
        """
        Initialize JSONData with raw JSON string.

        Args:
            raw_data: Raw JSON string to process
        """
        self.raw_data = raw_data
        self._parsed_data: Optional[Any] = None
        self._validation_result: Optional[JSONValidationResult] = None

    def validate(self) -> JSONValidationResult:
        """
        Validate the JSON data.

        Returns:
            JSONValidationResult: Validation result with error details if invalid
        """
        if self._validation_result is not None:
            return self._validation_result

        # Check for empty or None input
        if not self.raw_data or not self.raw_data.strip():
            self._validation_result = JSONValidationResult(
                is_valid=False, error_message="Input cannot be empty"
            )
            return self._validation_result

        try:
            # Use json for parsing and store the result to avoid re-parsing
            self._parsed_data = json.loads(self.raw_data)
            self._validation_result = JSONValidationResult(is_valid=True)
            return self._validation_result

        except json.JSONDecodeError as e:
            # Create a more informative error message from json's exception
            error_msg = f"Invalid JSON at line {e.lineno} column {e.colno}: {e.msg}"
            self._validation_result = JSONValidationResult(
                is_valid=False, error_message=error_msg, line_number=e.lineno
            )
            return self._validation_result

        except Exception as e:
            self._validation_result = JSONValidationResult(
                is_valid=False, error_message=f"Unexpected error: {str(e)}"
            )
            return self._validation_result

    def parse(self) -> Any:
        """
        Parse the JSON data. Ensures validation is performed.

        Returns:
            Any: Parsed JSON data

        Raises:
            ValueError: If JSON is invalid
        """
        # self.validate() will populate self._parsed_data if successful
        validation_result = self.validate()
        if not validation_result.is_valid:
            raise ValueError(validation_result.error_message)

        # The parsed data should now be available
        if self._parsed_data is not None:
            return self._parsed_data

        # This is a fallback that should not normally be reached
        try:
            return json.loads(self.raw_data)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON parsing error: {str(e)}")

    def format(self, indent: int = 2, sort_keys: bool = True) -> JSONFormatResult:
        """
        Format the JSON data with specified indentation.

        Args:
            indent: Number of spaces for indentation (default: 2)
            sort_keys: Whether to sort object keys (default: True)

        Returns:
            JSONFormatResult: Formatting result with formatted JSON or error
        """
        try:
            parsed_data = self.parse()

            formatted_json = json.dumps(
                parsed_data, indent=indent, sort_keys=sort_keys, ensure_ascii=False
            )

            # Count lines in formatted JSON
            line_count = len(formatted_json.splitlines())

            return JSONFormatResult(
                success=True, formatted_json=formatted_json, line_count=line_count
            )

        except ValueError as e:
            # This catches validation errors from self.parse()
            return JSONFormatResult(success=False, error_message=str(e))
        except Exception as e:
            return JSONFormatResult(
                success=False,
                error_message=f"Unexpected error during formatting: {str(e)}",
            )

    @property
    def is_valid(self) -> bool:
        """
        Check if the JSON data is valid.

        Returns:
            bool: True if JSON is valid, False otherwise
        """
        return self.validate().is_valid

    @property
    def parsed_data(self) -> Optional[Any]:
        """
        Get parsed JSON data if valid, None otherwise.

        Returns:
            Optional[Any]: Parsed JSON data or None if invalid
        """
        try:
            return self.parse()
        except (ValueError, Exception):
            return None

    def get_structure_info(self) -> Dict[str, Any]:
        """
        Get information about the JSON structure.

        Returns:
            Dict[str, Any]: Dictionary containing structure information
        """
        if not self.is_valid:
            return {"valid": False, "error": self.validate().error_message}

        try:
            data = self.parse()
            info = {
                "valid": True,
                "type": type(data).__name__,
                "is_object": isinstance(data, dict),
                "is_array": isinstance(data, list),
                "is_primitive": not isinstance(data, (dict, list)),
            }

            if isinstance(data, dict):
                info.update(
                    {
                        "key_count": len(data),
                        "keys": (
                            list(data.keys())
                            if len(data) <= 50
                            else list(data.keys())[:50]
                        ),
                    }
                )
            elif isinstance(data, list):
                info.update(
                    {
                        "item_count": len(data),
                        "item_types": list(
                            set(type(item).__name__ for item in data[:10])
                        ),
                    }
                )

            return info

        except Exception as e:
            return {"valid": False, "error": f"Error analyzing structure: {str(e)}"}

    def __str__(self) -> str:
        """String representation of JSONData."""
        return f"JSONData(valid={self.is_valid}, length={len(self.raw_data)})"

    def __repr__(self) -> str:
        """Detailed string representation of JSONData."""
        return f"JSONData(raw_data='{self.raw_data[:50]}...', valid={self.is_valid})"
