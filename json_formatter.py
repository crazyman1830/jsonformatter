"""
JSON formatter module with validation and error handling.

This module provides functions for parsing, validating, and formatting JSON data
with comprehensive error handling for invalid JSON inputs.
"""

import json


def validate_json(raw_json):
    """
    Validate if the input string is valid JSON.
    
    Args:
        raw_json: Raw JSON string to validate
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not raw_json or not raw_json.strip():
        return False, "Input cannot be empty"
    
    try:
        json.loads(raw_json)
        return True, ""
    except ValueError as e:
        error_msg = "Invalid JSON: {}".format(str(e))
        return False, error_msg
    except Exception as e:
        return False, "Unexpected error: {}".format(str(e))


def format_json(raw_json, indent=2):
    """
    Format and prettify JSON data.
    
    Args:
        raw_json: Raw JSON string to format
        indent: Number of spaces for indentation (default: 2)
        
    Returns:
        dict containing:
        - success: Whether formatting was successful
        - formatted_json: Formatted JSON string (if successful)
        - error_message: Error description (if failed)
    """
    # Validate input first
    is_valid, error_message = validate_json(raw_json)
    
    if not is_valid:
        return {
            "success": False,
            "formatted_json": "",
            "error_message": error_message
        }
    
    try:
        # Parse and format the JSON
        parsed_json = json.loads(raw_json)
        formatted_json = json.dumps(parsed_json, indent=indent, sort_keys=True)
        
        return {
            "success": True,
            "formatted_json": formatted_json,
            "error_message": ""
        }
    
    except ValueError as e:
        error_msg = "JSON parsing error: {}".format(str(e))
        return {
            "success": False,
            "formatted_json": "",
            "error_message": error_msg
        }
    except Exception as e:
        return {
            "success": False,
            "formatted_json": "",
            "error_message": "Unexpected error during formatting: {}".format(str(e))
        }


def parse_json_safely(raw_json):
    """
    Safely parse JSON string and return parsed object or error message.
    
    Args:
        raw_json: Raw JSON string to parse
        
    Returns:
        tuple: (parsed_object, error_message)
    """
    is_valid, error_message = validate_json(raw_json)
    
    if not is_valid:
        return None, error_message
    
    try:
        parsed_object = json.loads(raw_json)
        return parsed_object, ""
    except ValueError as e:
        error_msg = "JSON parsing error: {}".format(str(e))
        return None, error_msg
    except Exception as e:
        return None, "Unexpected error during parsing: {}".format(str(e))

class JSONProcessor(object):
    """
    JSON processor class with comprehensive error handling.
    
    This class provides a clean interface for JSON formatting operations
    with user-friendly error messages and consistent response format.
    """
    
    def __init__(self, default_indent=2):
        """
        Initialize the JSON processor.
        
        Args:
            default_indent: Default indentation for formatted JSON (default: 2)
        """
        self.default_indent = default_indent
    
    def format_json(self, raw_json, indent=None):
        """
        Format JSON data with comprehensive error handling.
        
        Args:
            raw_json: Raw JSON string to format
            indent: Number of spaces for indentation (uses default if None)
            
        Returns:
            dict containing:
            - success: Whether formatting was successful
            - formatted_json: Formatted JSON string (if successful)
            - error_message: User-friendly error description (if failed)
        """
        if indent is None:
            indent = self.default_indent
        
        # Input validation
        if raw_json is None:
            return {
                "success": False,
                "formatted_json": "",
                "error_message": "Input cannot be None"
            }
        
        if not isinstance(raw_json, str):
            return {
                "success": False,
                "formatted_json": "",
                "error_message": "Input must be a string"
            }
        
        # Use the existing format_json function
        return format_json(raw_json, indent)
    
    def validate_json(self, raw_json):
        """
        Validate JSON input with user-friendly error messages.
        
        Args:
            raw_json: Raw JSON string to validate
            
        Returns:
            dict containing:
            - is_valid: Whether the JSON is valid
            - error_message: User-friendly error description (if invalid)
        """
        if raw_json is None:
            return {
                "is_valid": False,
                "error_message": "Input cannot be None"
            }
        
        if not isinstance(raw_json, str):
            return {
                "is_valid": False,
                "error_message": "Input must be a string"
            }
        
        is_valid, error_message = validate_json(raw_json)
        return {
            "is_valid": is_valid,
            "error_message": error_message
        }
    
    def parse_json(self, raw_json):
        """
        Parse JSON with comprehensive error handling.
        
        Args:
            raw_json: Raw JSON string to parse
            
        Returns:
            dict containing:
            - success: Whether parsing was successful
            - data: Parsed JSON object (if successful)
            - error_message: User-friendly error description (if failed)
        """
        if raw_json is None:
            return {
                "success": False,
                "data": None,
                "error_message": "Input cannot be None"
            }
        
        if not isinstance(raw_json, str):
            return {
                "success": False,
                "data": None,
                "error_message": "Input must be a string"
            }
        
        parsed_data, error_message = parse_json_safely(raw_json)
        
        if parsed_data is not None:
            return {
                "success": True,
                "data": parsed_data,
                "error_message": ""
            }
        else:
            return {
                "success": False,
                "data": None,
                "error_message": error_message
            }
    
    def get_json_info(self, raw_json):
        """
        Get information about JSON structure.
        
        Args:
            raw_json: Raw JSON string to analyze
            
        Returns:
            dict containing:
            - success: Whether analysis was successful
            - info: Dictionary with JSON structure information
            - error_message: Error description (if failed)
        """
        parse_result = self.parse_json(raw_json)
        
        if not parse_result["success"]:
            return {
                "success": False,
                "info": {},
                "error_message": parse_result["error_message"]
            }
        
        data = parse_result["data"]
        info = {
            "type": type(data).__name__,
            "is_object": isinstance(data, dict),
            "is_array": isinstance(data, list),
            "is_primitive": not isinstance(data, (dict, list))
        }
        
        if isinstance(data, dict):
            info["key_count"] = len(data)
            info["keys"] = list(data.keys())
        elif isinstance(data, list):
            info["item_count"] = len(data)
        
        return {
            "success": True,
            "info": info,
            "error_message": ""
        }