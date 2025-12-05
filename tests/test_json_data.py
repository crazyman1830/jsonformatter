"""
Unit tests for JSONData model.
"""

import pytest
from unittest.mock import patch
from models.json_data import JSONData


class TestJSONData:
    """Test cases for JSONData model."""

    def test_init(self):
        """Test initialization."""
        data = JSONData('{"key": "value"}')
        assert data.raw_data == '{"key": "value"}'
        assert data._parsed_data is None
        assert data._validation_result is None

    def test_validate_valid(self):
        """Test validation with valid JSON."""
        data = JSONData('{"key": "value"}')
        result = data.validate()
        assert result.is_valid is True
        assert result.error_message is None

    def test_validate_invalid_json(self):
        """Test validation with invalid JSON."""
        data = JSONData('{"key": "value"')
        result = data.validate()
        assert result.is_valid is False
        assert "Invalid JSON" in result.error_message
        assert result.line_number is not None

    def test_validate_empty_input(self):
        """Test validation with empty input."""
        data = JSONData("")
        result = data.validate()
        assert result.is_valid is False
        assert "Input cannot be empty" in result.error_message


    def test_parse_valid(self):
        """Test parsing valid JSON."""
        data = JSONData('{"key": "value"}')
        parsed = data.parse()
        assert parsed == {"key": "value"}
        assert data._parsed_data == {"key": "value"}

    def test_parse_invalid(self):
        """Test parsing invalid JSON."""
        data = JSONData('{"key": "value"')
        with pytest.raises(ValueError):
            data.parse()

    def test_format_valid(self):
        """Test formatting valid JSON."""
        data = JSONData('{"key": "value"}')
        result = data.format(indent=4)
        assert result.success is True
        assert result.formatted_json is not None
        assert result.line_count > 0

    def test_format_invalid(self):
        """Test formatting invalid JSON."""
        data = JSONData('{"key": "value"')
        result = data.format()
        assert result.success is False
        assert result.error_message is not None


    def test_get_structure_info_valid_object(self):
        """Test structure info for valid object."""
        data = JSONData('{"key": "value", "num": 1}')
        info = data.get_structure_info()
        assert info["valid"] is True
        assert info["is_object"] is True
        assert info["key_count"] == 2
        assert "key" in info["keys"]

    def test_get_structure_info_valid_array(self):
        """Test structure info for valid array."""
        data = JSONData('[1, "string", true]')
        info = data.get_structure_info()
        assert info["valid"] is True
        assert info["is_array"] is True
        assert info["item_count"] == 3
        assert "int" in info["item_types"]

    def test_get_structure_info_invalid(self):
        """Test structure info for invalid JSON."""
        data = JSONData('{"key": "value"')
        info = data.get_structure_info()
        assert info["valid"] is False
        assert info["error"] is not None


