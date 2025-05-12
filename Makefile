.PHONY: format lint typecheck test clean

# Format code
format:
	isort src tests
	black src tests

# Run linting
lint:
	flake8 src tests

# Run type checking
typecheck:
	mypy src

# Run tests
test:
	pytest

# Run tests with coverage
test-cov:
	pytest --cov=src tests/

# Clean up build artifacts
clean:
	rm -rf build/ dist/ *.egg-info .pytest_cache .coverage htmlcov/

# Install project in development mode
install-dev:
	pip install -e ".[testing]"

# Install pre-commit hooks
install-hooks:
	pre-commit install

# Check all (format, lint, typecheck, test)
check:
	make format
	make lint
	make typecheck
	make test

# Full cleanup and reinstall
reset: clean install-dev 