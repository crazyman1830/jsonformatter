"""
JSON Formatter Web Application
Main Flask application entry point
"""

from flask import Flask, render_template, request, jsonify
from json_formatter import JSONProcessor

def create_app(config_name='development'):
    """Application factory function"""
    app_instance = Flask(__name__)
    
    # Configuration settings
    if config_name == 'production':
        app_instance.config.update(
            DEBUG=False,
            TESTING=False,
            SECRET_KEY='your-secret-key-here',  # Should be set via environment variable
            JSON_SORT_KEYS=False
        )
    elif config_name == 'testing':
        app_instance.config.update(
            DEBUG=False,
            TESTING=True,
            SECRET_KEY='test-secret-key',
            JSON_SORT_KEYS=False
        )
    else:  # development
        app_instance.config.update(
            DEBUG=True,
            TESTING=False,
            SECRET_KEY='dev-secret-key',
            JSON_SORT_KEYS=False
        )
    
    # Initialize JSON processor
    json_processor_instance = JSONProcessor()
    
    # Register routes
    @app_instance.route('/')
    def index():
        """Serve the main HTML interface"""
        return render_template('index.html')

    @app_instance.route('/format', methods=['POST'])
    def format_json_endpoint():
        """Process JSON formatting requests"""
        try:
            # Get JSON data from request
            if request.is_json:
                data = request.get_json()
                json_data = data.get('json_data', '')
            else:
                # Handle form data
                json_data = request.form.get('json_data', '')
            
            # Validate input
            if not json_data:
                return jsonify({
                    'success': False,
                    'formatted_json': '',
                    'error_message': 'No JSON data provided'
                }), 400
            
            # Validate input type (Python 3.8+ only supports str)
            if not isinstance(json_data, str):
                return jsonify({
                    'success': False,
                    'formatted_json': '',
                    'error_message': 'JSON data must be a string'
                }), 400
            
            # Use JSON processor to format the JSON
            result = json_processor_instance.format_json(json_data)
            
            # Return appropriate HTTP status code based on success
            if result['success']:
                return jsonify(result), 200
            else:
                return jsonify(result), 400
            
        except Exception as e:
            return jsonify({
                'success': False,
                'formatted_json': '',
                'error_message': 'Server error: {}'.format(str(e))
            }), 500

    @app_instance.route('/validate', methods=['POST'])
    def validate_json_endpoint():
        """Validate JSON data without formatting"""
        try:
            # Get JSON data from request
            if request.is_json:
                data = request.get_json()
                json_data = data.get('json_data', '')
            else:
                # Handle form data
                json_data = request.form.get('json_data', '')
            
            # Validate input
            if not json_data:
                return jsonify({
                    'is_valid': False,
                    'error_message': 'No JSON data provided'
                }), 400
            
            # Validate input type (Python 3.8+ only supports str)
            if not isinstance(json_data, str):
                return jsonify({
                    'is_valid': False,
                    'error_message': 'JSON data must be a string'
                }), 400
            
            # Use JSON processor to validate the JSON
            result = json_processor_instance.validate_json(json_data)
            
            # Return appropriate HTTP status code based on validity
            if result['is_valid']:
                return jsonify(result), 200
            else:
                return jsonify(result), 400
            
        except Exception as e:
            return jsonify({
                'is_valid': False,
                'error_message': 'Server error: {}'.format(str(e))
            }), 500

    @app_instance.route('/comments', methods=['POST'])
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
            
            # Validate comments format
            if not isinstance(comments, str):
                return jsonify({
                    'success': False,
                    'error_message': 'Comments must be a string'
                }), 400
            
            # Store comments in session (in production, you might want to use a database)
            from flask import session
            session['comments'] = comments
            
            return jsonify({
                'success': True,
                'message': 'Comments saved successfully'
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error_message': 'Server error: {}'.format(str(e))
            }), 500

    @app_instance.route('/comments', methods=['GET'])
    def load_comments_endpoint():
        """Load saved comments"""
        try:
            from flask import session
            comments = session.get('comments', '')
            
            return jsonify({
                'success': True,
                'comments': comments
            }), 200
            
        except Exception as e:
            return jsonify({
                'success': False,
                'error_message': 'Server error: {}'.format(str(e))
            }), 500
    
    return app_instance

# Create the app instance
app = create_app()

def main():
    """Main application entry point"""
    import os
    
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    # Create app with specified configuration
    app_instance = create_app(config_name)
    
    print("Starting JSON Formatter Application...")
    print("Environment: {}".format(config_name))
    print("Host: {}".format(host))
    print("Port: {}".format(port))
    
    # Run the application
    app_instance.run(
        debug=(config_name == 'development'),
        host=host,
        port=port
    )

if __name__ == '__main__':
    main()