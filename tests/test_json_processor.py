"""
Unit tests for JSONProcessorService.
"""

import pytest
from unittest.mock import Mock, patch
from core.exceptions import ValidationError, ProcessingError
from services.json_processor import JSONProcessorService


class TestJSONProcessorService:
    """Test cases for JSONProcessorService."""

    def setup_method(self):
        """Setup method for each test."""
        self.mock_logger = Mock()
        self.service = JSONProcessorService(logger=self.mock_logger)



    def test_format_json_success(self):
        """Test successful JSON formatting."""
        raw_json = '{"key": "value", "a": 1}'
        result = self.service.format_json(raw_json, indent=4, sort_keys=True)
        
        assert result.success is True
        assert result.formatted_json is not None
        assert '"a": 1' in result.formatted_json
        assert '"key": "value"' in result.formatted_json
        assert result.line_count > 0
        self.mock_logger.info.assert_called()

    def test_format_json_invalid_json(self):
        """Test formatting with invalid JSON."""
        raw_json = '{"key": "value"'  # Missing closing brace
        
        with pytest.raises(ValidationError):
            self.service.format_json(raw_json)
        
        self.mock_logger.warning.assert_called()


    def test_validate_json_valid(self):
        """Test validation with valid JSON."""
        raw_json = '{"key": "value"}'
        result = self.service.validate_json(raw_json)
        
        assert result.is_valid is True
        assert result.error_message is None
        self.mock_logger.debug.assert_called_with("JSON validation successful")

    def test_validate_json_invalid(self):
        """Test validation with invalid JSON."""
        raw_json = '{"key": "value"'  # Missing closing brace
        result = self.service.validate_json(raw_json)
        
        assert result.is_valid is False
        assert result.error_message is not None
        self.mock_logger.info.assert_called()

