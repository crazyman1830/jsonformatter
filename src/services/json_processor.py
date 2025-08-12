"""
JSON processing service with comprehensive error handling and logging.

This service provides a clean interface for JSON validation, parsing, and formatting
operations with integrated logging and dependency injection support.
"""

import logging
from typing import Any, Optional

from core.exceptions import ProcessingError, ValidationError

from models.json_data import JSONData, JSONFormatResult, JSONValidationResult


class JSONProcessorService:
    """
    Service for processing JSON data with validation, formatting, and analysis.

    This service encapsulates all JSON processing logic with comprehensive
    error handling, logging, and a clean interface for dependency injection.
    """

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize the JSON processor service.

        Args:
            logger: Optional logger instance for dependency injection
        """
        self.logger = logger or logging.getLogger(__name__)
        self.logger.debug("JSONProcessorService initialized")

    def _validate_raw_json_input(self, raw_json: Any) -> None:
        """
        Validate raw JSON input to ensure it's a non-empty string.

        Args:
            raw_json: The raw input to validate.

        Raises:
            ValidationError: If the input is invalid.
        """
        if raw_json is None:
            error_msg = "Input cannot be None"
            self.logger.error(f"Validation failed: {error_msg}")
            raise ValidationError(error_msg)

        if not isinstance(raw_json, str):
            error_msg = "Input must be a string"
            self.logger.error(f"Validation failed: {error_msg}")
            raise ValidationError(error_msg)

        if not raw_json.strip():
            error_msg = "Input cannot be empty"
            self.logger.error(f"Validation failed: {error_msg}")
            raise ValidationError(error_msg)

    def format_json(
        self, raw_json: Any, indent: int = 2, sort_keys: bool = True
    ) -> JSONFormatResult:
        """
        Format JSON data with specified indentation and options.

        Args:
            raw_json: Raw JSON string to format
            indent: Number of spaces for indentation (default: 2)
            sort_keys: Whether to sort object keys (default: True)

        Returns:
            JSONFormatResult: Formatting result with formatted JSON or error details

        Raises:
            ValidationError: If input validation fails
            ProcessingError: If formatting process fails
        """
        self.logger.info(f"Formatting JSON with indent={indent}, sort_keys={sort_keys}")
        self._validate_raw_json_input(raw_json)

        try:
            # Create JSON data model and format
            json_data = JSONData(raw_json)
            format_result = json_data.format(indent=indent, sort_keys=sort_keys)

            if format_result.success:
                self.logger.info(
                    f"JSON formatted successfully, {format_result.line_count} lines"
                )
            else:
                self.logger.warning(
                    f"JSON formatting failed: {format_result.error_message}"
                )
                # For invalid JSON, raise ValidationError instead of returning failed result
                raise ValidationError(
                    format_result.error_message or "JSON formatting failed"
                )

            return format_result

        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            error_msg = f"Unexpected error during formatting: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ProcessingError(error_msg) from e

    def validate_json(self, raw_json: Any) -> JSONValidationResult:
        """
        Validate JSON input with comprehensive error reporting.

        Args:
            raw_json: Raw JSON string to validate

        Returns:
            JSONValidationResult: Validation result with error details if invalid

        Raises:
            ValidationError: If input validation fails
        """
        self.logger.debug("Validating JSON input")
        self._validate_raw_json_input(raw_json)

        try:
            # Create JSON data model and validate
            json_data = JSONData(raw_json)
            validation_result = json_data.validate()

            if validation_result.is_valid:
                self.logger.debug("JSON validation successful")
            else:
                self.logger.info(
                    f"JSON validation failed: {validation_result.error_message}"
                )

            return validation_result

        except Exception as e:
            error_msg = f"Unexpected error during validation: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ProcessingError(error_msg) from e
