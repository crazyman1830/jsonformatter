"""
JSON processing service with comprehensive error handling and logging.

This service provides a clean interface for JSON validation, parsing, and formatting
operations with integrated logging and dependency injection support.
"""

import logging
from typing import Any, Dict, Optional

from models.json_data import JSONData, JSONValidationResult, JSONFormatResult
from core.exceptions import ValidationError, ProcessingError


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

        # Input validation
        if raw_json is None:
            error_msg = "Input cannot be None"
            self.logger.error(f"Format failed: {error_msg}")
            raise ValidationError(error_msg)

        if not isinstance(raw_json, str):
            error_msg = "Input must be a string"
            self.logger.error(f"Format failed: {error_msg}")
            raise ValidationError(error_msg)

        if len(raw_json.strip()) == 0:
            error_msg = "Input cannot be empty"
            self.logger.error(f"Format failed: {error_msg}")
            raise ValidationError(error_msg)

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

        # Input validation
        if raw_json is None:
            error_msg = "Input cannot be None"
            self.logger.error(f"Validation failed: {error_msg}")
            raise ValidationError(error_msg)

        if not isinstance(raw_json, str):
            error_msg = "Input must be a string"
            self.logger.error(f"Validation failed: {error_msg}")
            raise ValidationError(error_msg)

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

    def parse_json(self, raw_json: Any) -> Any:
        """
        Parse JSON string and return the parsed object.

        Args:
            raw_json: Raw JSON string to parse

        Returns:
            Any: Parsed JSON object

        Raises:
            ValidationError: If input validation fails or JSON is invalid
            ProcessingError: If parsing process fails
        """
        self.logger.debug("Parsing JSON input")

        # Input validation
        if raw_json is None:
            error_msg = "Input cannot be None"
            self.logger.error(f"Parse failed: {error_msg}")
            raise ValidationError(error_msg)

        if not isinstance(raw_json, str):
            error_msg = "Input must be a string"
            self.logger.error(f"Parse failed: {error_msg}")
            raise ValidationError(error_msg)

        try:
            # Create JSON data model and parse
            json_data = JSONData(raw_json)

            # Validate first
            validation_result = json_data.validate()
            if not validation_result.is_valid:
                self.logger.warning(
                    f"JSON parsing failed due to invalid JSON: {validation_result.error_message}"
                )
                raise ValidationError(
                    validation_result.error_message or "JSON validation failed"
                )

            parsed_data = json_data.parse()
            self.logger.debug("JSON parsed successfully")
            return parsed_data

        except ValidationError:
            # Re-raise validation errors
            raise
        except Exception as e:
            error_msg = f"Unexpected error during parsing: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ProcessingError(error_msg) from e

    def get_json_info(self, raw_json: Any) -> Dict[str, Any]:
        """
        Get comprehensive information about JSON structure and content.

        Args:
            raw_json: Raw JSON string to analyze

        Returns:
            Dict[str, Any]: Dictionary containing JSON structure information

        Raises:
            ValidationError: If input validation fails
            ProcessingError: If analysis process fails
        """
        self.logger.debug("Analyzing JSON structure")

        # Input validation
        if raw_json is None:
            error_msg = "Input cannot be None"
            self.logger.error(f"Analysis failed: {error_msg}")
            raise ValidationError(error_msg)

        if not isinstance(raw_json, str):
            error_msg = "Input must be a string"
            self.logger.error(f"Analysis failed: {error_msg}")
            raise ValidationError(error_msg)

        try:
            # Create JSON data model and get structure info
            json_data = JSONData(raw_json)
            structure_info = json_data.get_structure_info()

            # Add additional processing information
            structure_info.update(
                {
                    "raw_length": len(raw_json),
                    "raw_lines": len(raw_json.splitlines()),
                    "processed_by": self.__class__.__name__,
                }
            )

            if structure_info.get("valid", False):
                item_count = structure_info.get(
                    "key_count", structure_info.get("item_count", "unknown")
                )
                self.logger.debug(
                    f"JSON analysis successful: {structure_info['type']} with {item_count} items"
                )
            else:
                self.logger.info(
                    f"JSON analysis completed for invalid JSON: "
                    f"{structure_info.get('error', 'Unknown error')}"
                )

            return structure_info

        except Exception as e:
            error_msg = f"Unexpected error during analysis: {str(e)}"
            self.logger.error(error_msg, exc_info=True)
            raise ProcessingError(error_msg) from e

    def process_json_safely(
        self, raw_json: str, indent: int = 2, sort_keys: bool = True
    ) -> Dict[str, Any]:
        """
        Safely process JSON with comprehensive error handling and return structured result.

        This method combines validation, parsing, formatting, and analysis into a single
        operation with comprehensive error handling and logging.

        Args:
            raw_json: Raw JSON string to process
            indent: Number of spaces for indentation (default: 2)
            sort_keys: Whether to sort object keys (default: True)

        Returns:
            Dict[str, Any]: Comprehensive processing result with all operations
        """
        self.logger.info("Starting comprehensive JSON processing")

        result: Dict[str, Any] = {
            "success": False,
            "validation": None,
            "formatted_json": None,
            "structure_info": None,
            "error_message": None,
            "processing_steps": [],
        }

        try:
            # Step 1: Validation
            self.logger.debug("Step 1: Validating JSON")
            validation_result = self.validate_json(raw_json)
            result["validation"] = {
                "is_valid": validation_result.is_valid,
                "error_message": validation_result.error_message,
                "line_number": validation_result.line_number,
            }
            result["processing_steps"].append("validation")

            if not validation_result.is_valid:
                result["error_message"] = validation_result.error_message
                self.logger.info("JSON processing stopped at validation step")
                return result

            # Step 2: Formatting
            self.logger.debug("Step 2: Formatting JSON")
            format_result = self.format_json(
                raw_json, indent=indent, sort_keys=sort_keys
            )
            result["formatted_json"] = {
                "success": format_result.success,
                "content": format_result.formatted_json,
                "line_count": format_result.line_count,
                "error_message": format_result.error_message,
            }
            result["processing_steps"].append("formatting")

            if not format_result.success:
                result["error_message"] = format_result.error_message
                self.logger.warning("JSON processing failed at formatting step")
                return result

            # Step 3: Structure Analysis
            self.logger.debug("Step 3: Analyzing JSON structure")
            structure_info = self.get_json_info(raw_json)
            result["structure_info"] = structure_info
            result["processing_steps"].append("analysis")

            # Mark as successful
            result["success"] = True
            self.logger.info("JSON processing completed successfully")

        except ValidationError as e:
            result["error_message"] = str(e)
            self.logger.error(f"JSON processing failed with validation error: {str(e)}")
        except ProcessingError as e:
            result["error_message"] = str(e)
            self.logger.error(f"JSON processing failed with processing error: {str(e)}")
        except Exception as e:
            result["error_message"] = f"Unexpected error: {str(e)}"
            self.logger.error(
                f"JSON processing failed with unexpected error: {str(e)}", exc_info=True
            )

        return result
