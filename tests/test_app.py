"""
Application factory and basic configuration tests.
"""

import os
from flask import Flask
from web.app import create_app
from core.config import AppConfig


def test_create_app() -> None:
    """
    Test that the create_app factory returns a Flask app instance.
    """
    # Set the environment to testing
    os.environ["FLASK_ENV"] = "testing"

    # Create a minimal config for testing
    config = AppConfig.from_env()

    # Create the app
    app = create_app(config)

    # Assert that the app is a Flask instance
    assert isinstance(app, Flask)

    # Assert that the app is in testing mode
    assert app.config["TESTING"] is True
