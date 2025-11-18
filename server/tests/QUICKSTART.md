# Test Suite Quick Start Guide

Quick reference for running M2P tests.

## Installation

```bash
pip install -r requirements-test.txt
```

## Common Commands

### Run All Tests
```bash
pytest server/tests -v
# or
make test
```

### Run Specific Test Types
```bash
# Unit tests
pytest server/tests -m unit -v

# Integration tests
pytest server/tests -m integration -v

# API tests
pytest server/tests -m api -v

# Database tests
pytest server/tests -m db -v
```

### Run Specific Files
```bash
# Test models
pytest server/tests/test_models.py -v

# Test API
pytest server/tests/test_api.py -v

# Test achievements
pytest server/tests/test_achievements.py -v
```

### Coverage
```bash
# Generate coverage report
pytest server/tests --cov=server --cov-report=html
# or
make test-cov

# View report
open htmlcov/index.html
```

### Load Testing
```bash
# Web UI
locust -f server/tests/load/locustfile.py --host=http://localhost:5000

# Headless
make load-test-headless
```

## Test Markers

- `@pytest.mark.unit` - Unit tests
- `@pytest.mark.integration` - Integration tests
- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.db` - Database tests
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.polling` - Pool polling tests
- `@pytest.mark.verification` - Wallet verification tests
- `@pytest.mark.achievements` - Achievement system tests

## Useful Options

```bash
# Verbose output
pytest server/tests -v

# Very verbose
pytest server/tests -vv

# Stop on first failure
pytest server/tests -x

# Run last failed tests
pytest server/tests --lf

# Run only failed tests
pytest server/tests --ff

# Show print statements
pytest server/tests -s

# Run in parallel
pytest server/tests -n auto
```

## Environment Variables

```bash
# Set testing mode
export TESTING=True

# Set database URI
export SQLALCHEMY_DATABASE_URI=sqlite:///test.db
```

## Quick Checks

### Before Commit
```bash
make lint
make test-cov
```

### Full CI Check
```bash
make ci
```

## Troubleshooting

### Clear Cache
```bash
pytest --cache-clear
```

### Reset Database
```bash
rm test.db
```

### Clean Build Files
```bash
make clean
```

## File Structure

```
server/tests/
├── conftest.py              # Fixtures
├── test_models.py           # Model tests (30+ tests)
├── test_api.py              # API tests (40+ tests)
├── test_pool_poller.py      # Polling tests (35+ tests)
├── test_verifier.py         # Verification tests (30+ tests)
├── test_achievements.py     # Achievement tests (35+ tests)
├── test_utils.py            # Utilities
└── integration/
    └── test_full_flow.py    # E2E tests (15+ tests)
```

## Test Count Summary

- **Unit Tests**: 150+
- **Integration Tests**: 15+
- **Total**: 165+
- **Coverage**: 80%+ target

## Need Help?

See [TESTING.md](../../TESTING.md) for comprehensive documentation.
