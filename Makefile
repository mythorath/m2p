# M2P Makefile for common tasks

.PHONY: help install test test-unit test-integration test-cov lint format clean

help:
	@echo "M2P Testing Commands:"
	@echo "  make install          - Install all dependencies"
	@echo "  make test             - Run all tests"
	@echo "  make test-unit        - Run unit tests only"
	@echo "  make test-integration - Run integration tests only"
	@echo "  make test-cov         - Run tests with coverage report"
	@echo "  make lint             - Run linting checks"
	@echo "  make format           - Format code with black"
	@echo "  make security         - Run security checks"
	@echo "  make clean            - Clean up generated files"
	@echo "  make load-test        - Run load tests"

install:
	pip install -r requirements-test.txt

test:
	pytest server/tests -v

test-unit:
	pytest server/tests -v -m "unit"

test-integration:
	pytest server/tests -v -m "integration"

test-api:
	pytest server/tests -v -m "api"

test-db:
	pytest server/tests -v -m "db"

test-cov:
	pytest server/tests -v --cov=server --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/"

test-watch:
	pytest-watch server/tests -v

lint:
	flake8 server --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 server --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics

type-check:
	mypy server --ignore-missing-imports

format:
	black server

format-check:
	black --check server

security:
	safety check
	bandit -r server -f json -o bandit-report.json

load-test:
	locust -f server/tests/load/locustfile.py --host=http://localhost:5000

load-test-headless:
	locust -f server/tests/load/locustfile.py \
		--host=http://localhost:5000 \
		--users=100 \
		--spawn-rate=10 \
		--run-time=5m \
		--headless

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.coverage" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "coverage.xml" -delete
	find . -type f -name "test.db" -delete
	find . -type f -name "bandit-report.json" -delete

ci:
	@echo "Running CI checks..."
	make lint
	make type-check
	make test-cov
	make security
	@echo "CI checks complete!"

all: clean install lint type-check test-cov

dev-setup:
	pip install -r requirements-test.txt
	pip install pytest-watch
	@echo "Development environment ready!"
