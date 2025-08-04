"""
Blueprint for API endpoints.
"""

from flask import Blueprint, request, jsonify, session
from json_formatter import JSONProcessor

api_bp = Blueprint('api', __name__)

# Initialize JSON processor once for the blueprint
json_processor_instance = JSONProcessor()

@api_bp.route('/')
def index():
    """Serve the main HTML interface"""
    # Note: render_template needs access to the app's template folder.
    # This route might be better left in app.py or handled by a separate UI blueprint.
    # For simplicity, we assume it's an API endpoint returning a welcome message.
    return jsonify({"message": "Welcome to the JSON Formatter API"})

@api_bp.route('/format', methods=['POST'])
def format_json_endpoint():
    """Process JSON formatting requests"""
    try:
        if request.is_json:
            data = request.get_json()
            json_data = data.get('json_data', '')
        else:
            json_data = request.form.get('json_data', '')
        
        if not json_data:
            return jsonify({
                'success': False,
                'formatted_json': '',
                'error_message': 'No JSON data provided'
            }), 400
        
        if not isinstance(json_data, str):
            return jsonify({
                'success': False,
                'formatted_json': '',
                'error_message': 'JSON data must be a string'
            }), 400
        
        result = json_processor_instance.format_json(json_data)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({
            'success': False,
            'formatted_json': '',
            'error_message': f'Server error: {str(e)}'
        }), 500

@api_bp.route('/validate', methods=['POST'])
def validate_json_endpoint():
    """Validate JSON data without formatting"""
    try:
        if request.is_json:
            data = request.get_json()
            json_data = data.get('json_data', '')
        else:
            json_data = request.form.get('json_data', '')
        
        if not json_data:
            return jsonify({
                'is_valid': False,
                'error_message': 'No JSON data provided'
            }), 400
        
        if not isinstance(json_data, str):
            return jsonify({
                'is_valid': False,
                'error_message': 'JSON data must be a string'
            }), 400
        
        result = json_processor_instance.validate_json(json_data)
        
        if result['is_valid']:
            return jsonify(result), 200
        else:
            return jsonify(result), 400
        
    except Exception as e:
        return jsonify({
            'is_valid': False,
            'error_message': f'Server error: {str(e)}'
        }), 500

@api_bp.route('/comments', methods=['POST'])
def save_comments_endpoint():
    """Save comments for JSON"""
    try:
        if not request.is_json:
            return jsonify({
                'success': False,
                'error_message': 'Request must be JSON'
            }), 400
        
        data = request.get_json()
        comments = data.get('comments', '')
        
        if not isinstance(comments, str):
            return jsonify({
                'success': False,
                'error_message': 'Comments must be a string'
            }), 400
        
        session['comments'] = comments
        
        return jsonify({
            'success': True,
            'message': 'Comments saved successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error_message': f'Server error: {str(e)}'
        }), 500

@api_bp.route('/comments', methods=['GET'])
def load_comments_endpoint():
    """Load saved comments"""
    try:
        comments = session.get('comments', '')
        return jsonify({
            'success': True,
            'comments': comments
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error_message': f'Server error: {str(e)}'
        }), 500