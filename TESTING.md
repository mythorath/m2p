# M2P Testing Documentation

Comprehensive testing guide for the Mining to Podium (M2P) project.

## Table of Contents

- [Overview](#overview)
- [Test Structure](#test-structure)
- [Running Tests](#running-tests)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [Load Testing](#load-testing)
- [CI/CD Integration](#cicd-integration)
- [Best Practices](#best-practices)

## Overview

The M2P project uses a comprehensive test suite with:
- **80%+ code coverage target**
- Unit tests for all components
- Integration tests for full flows
- Load tests for performance validation
- Automated CI/CD pipeline

### Test Stack

- **pytest**: Test framework
- **pytest-asyncio**: Async test support
- **pytest-flask**: Flask application testing
- **pytest-cov**: Code coverage reporting
- **responses**: HTTP request mocking
- **faker**: Test data generation
- **locust**: Load testing

## Test Structure

```
server/tests/
├── conftest.py              # Pytest fixtures and configuration
├── test_models.py           # Database model tests
├── test_api.py              # API endpoint tests
├── test_pool_poller.py      # Pool polling tests
├── test_verifier.py         # Wallet verification tests
├── test_achievements.py     # Achievement system tests
├── test_utils.py            # Test utilities and helpers
├── integration/
│   ├── __init__.py
│   └── test_full_flow.py    # End-to-end integration tests
└── load/
    ├── __init__.py
    └── locustfile.py        # Load testing configuration
```

## Running Tests

### Install Dependencies

```bash
pip install -r requirements-test.txt
```

### Run All Tests

```bash
pytest server/tests -v
```

### Run Specific Test Categories

```bash
# Unit tests only
pytest server/tests -v -m "unit"

# Integration tests only
pytest server/tests -v -m "integration"

# API tests only
pytest server/tests -v -m "api"

# Database tests only
pytest server/tests -v -m "db"

# Verification tests only
pytest server/tests -v -m "verification"

# Achievement tests only
pytest server/tests -v -m "achievements"

# Polling tests only
pytest server/tests -v -m "polling"
```

### Run Specific Test Files

```bash
# Test models only
pytest server/tests/test_models.py -v

# Test API only
pytest server/tests/test_api.py -v

# Test pool poller only
pytest server/tests/test_pool_poller.py -v
```

### Run Specific Test Classes or Functions

```bash
# Run specific test class
pytest server/tests/test_api.py::TestRegisterEndpoint -v

# Run specific test function
pytest server/tests/test_models.py::TestPlayerModel::test_create_player -v
```

### Run with Coverage

```bash
# Generate coverage report
pytest server/tests -v --cov=server --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html
```

### Run Integration Tests

```bash
pytest server/tests/integration -v
```

### Run Slow Tests

```bash
# Run tests marked as slow
pytest server/tests -v -m "slow"

# Skip slow tests
pytest server/tests -v -m "not slow"
```

## Test Coverage

### Current Coverage Goals

- **Overall**: 80%+
- **Models**: 90%+
- **API**: 85%+
- **Business Logic**: 90%+

### View Coverage Report

```bash
# Generate HTML coverage report
pytest server/tests --cov=server --cov-report=html

# Open in browser
open htmlcov/index.html
```

### Coverage Configuration

Coverage settings are defined in `pytest.ini`:

```ini
[coverage:run]
source = server
omit =
    */tests/*
    */venv/*
    */migrations/*

[coverage:report]
precision = 2
show_missing = True
```

## Writing Tests

### Test Structure Template

```python
import pytest
from unittest.mock import Mock, patch


@pytest.mark.unit
@pytest.mark.db
class TestYourFeature:
    """Test cases for your feature."""

    def test_feature_success(self, db, session):
        """Test successful feature execution."""
        # Arrange
        test_data = {...}

        # Act
        result = your_function(test_data)

        # Assert
        assert result is not None
        assert result['status'] == 'success'

    def test_feature_failure(self, db, session):
        """Test feature failure handling."""
        # Arrange
        invalid_data = {...}

        # Act & Assert
        with pytest.raises(ValueError):
            your_function(invalid_data)
```

### Using Fixtures

```python
def test_with_fixtures(sample_wallet, sample_player_data):
    """Test using predefined fixtures."""
    assert sample_wallet is not None
    assert sample_player_data['wallet_address'] == sample_wallet
```

### Available Fixtures

- `app`: Flask application instance
- `client`: Flask test client
- `db`: Database instance
- `session`: Database session
- `sample_wallet`: Sample Alephium wallet address
- `sample_player_data`: Sample player data
- `verified_player_data`: Sample verified player data
- `sample_mining_event`: Sample mining event
- `sample_pool_snapshot`: Sample pool snapshot
- `sample_achievement`: Sample achievement
- `mock_pool_response`: Mock pool API response
- `mock_blockchain_response`: Mock blockchain API response
- `multiple_players`: List of sample players
- `mock_socketio`: Mock SocketIO instance

### Mocking HTTP Requests

```python
import responses

@responses.activate
def test_api_call():
    """Test external API call."""
    responses.add(
        responses.GET,
        'https://api.example.com/endpoint',
        json={'status': 'success'},
        status=200
    )

    result = make_api_call()
    assert result['status'] == 'success'
```

### Test Markers

Available test markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.e2e`: End-to-end tests
- `@pytest.mark.slow`: Slow-running tests
- `@pytest.mark.db`: Database tests
- `@pytest.mark.api`: API tests
- `@pytest.mark.polling`: Pool polling tests
- `@pytest.mark.verification`: Verification tests
- `@pytest.mark.achievements`: Achievement tests

## Load Testing

### Using Locust

```bash
# Start Locust web interface
locust -f server/tests/load/locustfile.py --host=http://localhost:5000

# Open browser to http://localhost:8089
# Configure number of users and spawn rate
# Click "Start swarming"
```

### Headless Load Testing

```bash
# Run load test without web UI
locust -f server/tests/load/locustfile.py \
    --host=http://localhost:5000 \
    --users=100 \
    --spawn-rate=10 \
    --run-time=5m \
    --headless
```

### Load Test Patterns

The load testing suite includes:

1. **Normal Load**: Simulated typical user behavior
2. **Step Load**: Gradually increasing user count
3. **Spike Load**: Sudden traffic spikes
4. **Sustained Load**: Continuous high load

### Load Test Metrics

Key metrics to monitor:

- **Response Time**: Average, median, p95, p99
- **Throughput**: Requests per second (RPS)
- **Error Rate**: Percentage of failed requests
- **Concurrency**: Number of simultaneous users

## CI/CD Integration

### GitHub Actions Workflow

The test suite runs automatically on:

- Push to `main`, `develop`, or `claude/**` branches
- Pull requests to `main` or `develop`

### Workflow Jobs

1. **Test**: Run all tests across Python 3.9, 3.10, 3.11
2. **Test Docker**: Run tests in Docker container
3. **Security**: Run security checks (Safety, Bandit)
4. **Performance**: Run performance/benchmark tests

### View CI/CD Results

- Go to Actions tab in GitHub repository
- Select workflow run
- View test results and coverage reports

### Local CI/CD Simulation

```bash
# Run tests as CI would
pytest server/tests -v --cov=server --cov-report=xml

# Run linting
flake8 server

# Run type checking
mypy server --ignore-missing-imports

# Run security checks
safety check
bandit -r server
```

## Best Practices

### 1. Test Naming

- Use descriptive test names
- Follow pattern: `test_<what>_<condition>_<expected_result>`
- Example: `test_register_duplicate_wallet_returns_409`

### 2. Test Organization

- Group related tests in classes
- One test file per module/component
- Use clear class and function names

### 3. Test Independence

- Each test should be independent
- Don't rely on test execution order
- Use fixtures for setup/teardown

### 4. Test Coverage

- Aim for 80%+ coverage
- Test both success and failure cases
- Test edge cases and boundary conditions

### 5. Mocking

- Mock external dependencies
- Don't mock the code under test
- Use `responses` for HTTP mocking
- Use `unittest.mock` for other mocking

### 6. Assertions

- Use specific assertions
- One logical assertion per test
- Use custom assertions from `test_utils.py`

### 7. Test Data

- Use factories and fixtures
- Don't hardcode test data
- Use `faker` for realistic data
- Use test utilities from `test_utils.py`

### 8. Documentation

- Add docstrings to test functions
- Explain complex test scenarios
- Document test data requirements

## Troubleshooting

### Tests Failing Locally

```bash
# Clear pytest cache
pytest --cache-clear

# Run with verbose output
pytest server/tests -vv

# Run specific failing test
pytest server/tests/test_api.py::TestRegisterEndpoint::test_register_valid_player -vv
```

### Database Issues

```bash
# Reset test database
rm test.db
pytest server/tests -v
```

### Import Errors

```bash
# Ensure proper Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest server/tests -v
```

### Coverage Not Generated

```bash
# Install coverage plugin
pip install pytest-cov

# Generate coverage with detailed output
pytest server/tests --cov=server --cov-report=term-missing -v
```

## Additional Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-flask Documentation](https://pytest-flask.readthedocs.io/)
- [Locust Documentation](https://docs.locust.io/)
- [responses Documentation](https://github.com/getsentry/responses)

## Contributing

When adding new features:

1. Write tests first (TDD)
2. Ensure all tests pass
3. Maintain 80%+ coverage
4. Update this documentation
5. Add integration tests for new flows

## Questions?

For questions about testing:
- Check existing test files for examples
- Review this documentation
- Ask in team discussions
