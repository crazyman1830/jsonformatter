.PHONY: help install install-dev run dev test lint format type-check security-check clean all-checks pre-commit setup-hooks

# Default target
help:
	@echo "Available commands:"
	@echo "  install      - Install production dependencies"
	@echo "  install-dev  - Install development dependencies"
	@echo "  run          - Run the application in production mode"
	@echo "  dev          - Run the application in development mode"
	@echo "  test         - Run tests"
	@echo "  lint         - Run flake8 linter"
	@echo "  format       - Format code with black"
	@echo "  type-check   - Run mypy type checker"
	@echo "  security-check - Run bandit security checker"
	@echo "  all-checks   - Run all code quality checks"
	@echo "  pre-commit   - Run pre-commit hooks"
	@echo "  setup-hooks  - Install pre-commit hooks"
	@echo "  clean        - Clean up temporary files"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

# Running the application
run:
	python app.py

dev:
	FLASK_ENV=development FLASK_DEBUG=true python app.py

# Testing
test:
	pytest

test-cov:
	pytest --cov=src --cov-report=html --cov-report=term

# Code quality checks
lint:
	flake8 src/

format:
	black src/

format-check:
	black --check src/

type-check:
	mypy src/ --config-file pyproject.toml

security-check:
	bandit -r src/ --configfile pyproject.toml

# Combined checks
all-checks: format-check lint type-check security-check
	@echo "All code quality checks completed!"

# Pre-commit
pre-commit:
	pre-commit run --all-files

setup-hooks:
	pre-commit install

# Cleanup
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name ".mypy_cache" -exec rm -rf {} +
	rm -rf build/
	rm -rf dist/
	rm -rf htmlcov/

# Development workflow
setup: install-dev setup-hooks
	@echo "Development environment setup complete!"

check: format lint type-check security-check
	@echo "Code quality checks completed!"
