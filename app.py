"""
JSON Formatter Web Application
Main Flask application entry point
"""
import os
from flask import Flask, render_template

def create_app(config_name='development'):
    """Application factory function"""
    app_instance = Flask(__name__)
    
    # Load configuration from environment variables
    secret_key = os.environ.get('SECRET_KEY', 'default-dev-secret-key')

    # Configuration settings
    if config_name == 'production':
        app_instance.config.update(
            DEBUG=False,
            TESTING=False,
            SECRET_KEY=secret_key,
            JSON_SORT_KEYS=False
        )
    elif config_name == 'testing':
        app_instance.config.update(
            DEBUG=False,
            TESTING=True,
            SECRET_KEY='test-secret-key', # Keep a fixed key for tests
            JSON_SORT_KEYS=False
        )
    else:  # development
        app_instance.config.update(
            DEBUG=True,
            TESTING=False,
            SECRET_KEY=secret_key,
            JSON_SORT_KEYS=False
        )
    
    # Register Blueprints
    import views
    app_instance.register_blueprint(views.api_bp, url_prefix='/api')

    # Main route to serve the frontend
    @app_instance.route('/')
    def index():
        """Serve the main HTML interface"""
        return render_template('index.html')

    return app_instance

def main():
    """Main application entry point"""
    # Get configuration from environment
    config_name = os.environ.get('FLASK_ENV', 'development')
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))

    # Create app with specified configuration
    app = create_app(config_name)

    print("Starting JSON Formatter Application...")
    print(f"Environment: {config_name}")
    print(f"Host: {host}")
    print(f"Port: {port}")

    # Run the application
    app.run(
        debug=(config_name == 'development'),
        host=host,
        port=port,
        reloader_type='stat'  # Use 'stat' reloader to avoid issues with Python 3.13+
    )

if __name__ == '__main__':
    main()