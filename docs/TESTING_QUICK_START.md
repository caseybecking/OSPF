# OSPF Testing - Quick Start Guide

## Setup (First Time Only)

```bash
# 1. Install test dependencies
pipenv install --dev

# 2. Create test database
psql -U security -h 192.168.1.150 -c "CREATE DATABASE ospf_test;"

# 3. Verify setup
pytest --collect-only
```

## Running Tests

### Quick Commands

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_models_user.py

# Run specific test
pytest tests/test_models_user.py::TestUserModel::test_user_creation

# Run with coverage
pytest --cov=api --cov=app --cov-report=term-missing
```

### Common Test Scenarios

```bash
# Test all models
pytest tests/test_models_*.py

# Test all API endpoints
pytest tests/test_api_*.py

# Test web controllers
pytest tests/test_web_controllers.py

# Test authentication
pytest tests/test_api_authentication.py

# Test CSV import
pytest tests/test_api_transaction.py::TestTransactionCSVImport
```

## Test Structure Overview

```
tests/
├── conftest.py                    # Fixtures and configuration
│
├── Model Tests (Database Layer)
├── test_models_user.py            # 13 tests
├── test_models_institution.py     # 17 tests
├── test_models_categories.py      # 15 tests
├── test_models_transaction.py     # 14 tests
│
├── API Tests (REST Endpoints)
├── test_api_authentication.py     # 12 tests
├── test_api_institution.py        # 13 tests
├── test_api_categories.py         # 11 tests
├── test_api_transaction.py        # 19 tests
│
└── Web Tests (UI Controllers)
    └── test_web_controllers.py    # 16 tests
```

**Total: ~130+ tests**

## Available Fixtures

```python
# Application
app                    # Flask app
client                 # Test client
authenticated_client   # Logged-in client

# Models
test_user              # User account
test_institution       # Bank/institution
test_account           # Checking account
test_categories_type   # Expense type
test_categories_group  # Groceries group
test_category          # Walmart category
test_transaction       # Sample transaction

# Utilities
tmp_path              # Temporary directory
sample_csv_file       # CSV file for testing
```

## Coverage Report

```bash
# Generate HTML coverage report
pytest --cov=api --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html     # macOS
xdg-open htmlcov/index.html # Linux
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL is running
pg_isctl status

# Verify connection
psql -U security -h 192.168.1.150 -c "SELECT 1;"
```

### Clean Test Database
```bash
psql -U security -h 192.168.1.150 -d ospf_test \
  -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

### Import Errors
```bash
# Make sure you're in project root
cd /path/to/OSPF

# Activate virtual environment
pipenv shell

# Reinstall dependencies
pipenv install --dev
```

## Writing New Tests

### Template
```python
# tests/test_my_feature.py

class TestMyFeature:
    """Test my new feature"""

    def test_success_case(self, client, test_user):
        """Test successful operation"""
        # Arrange
        data = {'key': 'value'}

        # Act
        response = client.post('/api/endpoint', json=data)

        # Assert
        assert response.status_code == 200

    def test_error_case(self, client):
        """Test error handling"""
        response = client.post('/api/endpoint', json={})
        assert response.status_code == 400
```

### Run Your New Tests
```bash
pytest tests/test_my_feature.py -v
```

## CI/CD Integration

Tests can be integrated into CI/CD pipelines:

```yaml
# .github/workflows/test.yml
- name: Run tests
  run: pipenv run pytest --cov=api --cov=app
```

## Next Steps

1. Read full documentation: `tests/README.md`
2. Explore existing tests for examples
3. Run tests before committing code
4. Maintain >90% coverage
5. Write tests for new features

## Quick Reference

| Command | Description |
|---------|-------------|
| `pytest` | Run all tests |
| `pytest -v` | Verbose output |
| `pytest -s` | Show print statements |
| `pytest -x` | Stop on first failure |
| `pytest -k "user"` | Run tests matching "user" |
| `pytest --lf` | Run last failed tests |
| `pytest --cov` | Run with coverage |
| `pytest --collect-only` | List all tests without running |

---

**Need help?** Check `tests/README.md` for detailed documentation.
