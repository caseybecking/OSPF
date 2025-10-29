# OSPF Test Suite

Comprehensive test suite for OSPF (Open Source Personal Finance) application.

## Table of Contents

- [Overview](#overview)
- [Setup](#setup)
- [Running Tests](#running-tests)
- [Test Structure](#test-structure)
- [Test Coverage](#test-coverage)
- [Writing Tests](#writing-tests)
- [Fixtures](#fixtures)
- [Troubleshooting](#troubleshooting)

## Overview

The OSPF test suite uses **pytest** as the testing framework and includes:

- **Unit tests** for models (database layer)
- **Integration tests** for API endpoints
- **Integration tests** for web controllers
- **Functional tests** for CSV import functionality
- **Authentication and authorization tests**

### Test Statistics

- **Total Test Files**: 9
- **Test Categories**:
  - Model tests (4 files)
  - API tests (5 files)
  - Web controller tests (1 file)
  - Authentication tests (integrated)

## Setup

### 1. Install Dependencies

```bash
# Using pipenv (recommended)
pipenv install --dev

# Or using pip
pip install -r requirements.txt
pip install pytest pytest-cov pytest-flask faker
```

### 2. Configure Test Database

The tests require a PostgreSQL test database. Update the database URL in `tests/conftest.py` if needed:

```python
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://security:security@192.168.1.150:5432/ospf_test?sslmode=disable'
```

**Important**: The test database will be created and dropped automatically. Make sure:
- The database user has CREATE/DROP permissions
- The test database name is different from your development database
- The database server is accessible

### 3. Create Test Database

```bash
# Connect to PostgreSQL
psql -U security -h 192.168.1.150

# Create test database
CREATE DATABASE ospf_test;
```

## Running Tests

### Run All Tests

```bash
# Using pytest directly
pytest

# Using pipenv
pipenv run pytest

# Verbose output
pytest -v

# With output capture disabled (see print statements)
pytest -s
```

### Run Specific Test Files

```bash
# Test a specific file
pytest tests/test_models_user.py

# Test multiple files
pytest tests/test_models_*.py
```

### Run Specific Test Classes or Functions

```bash
# Test a specific class
pytest tests/test_models_user.py::TestUserModel

# Test a specific function
pytest tests/test_models_user.py::TestUserModel::test_user_creation
```

### Run Tests by Markers

```bash
# Run only unit tests
pytest -m unit

# Run only API tests
pytest -m api

# Run only web controller tests
pytest -m web

# Skip slow tests
pytest -m "not slow"
```

### Run Tests with Coverage

```bash
# Basic coverage report
pytest --cov=api --cov=app

# Coverage with HTML report
pytest --cov=api --cov=app --cov-report=html

# Coverage with missing lines
pytest --cov=api --cov=app --cov-report=term-missing

# Open HTML coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run Tests in Parallel (faster)

```bash
# Install pytest-xdist
pip install pytest-xdist

# Run tests in parallel
pytest -n auto
```

## Test Structure

```
tests/
├── __init__.py                    # Test package initialization
├── conftest.py                    # Pytest configuration and fixtures
├── README.md                      # This file
│
├── Model Tests
├── test_models_user.py            # User model tests
├── test_models_institution.py     # Institution & Account model tests
├── test_models_categories.py      # Categories model tests
├── test_models_transaction.py     # Transaction model tests
│
├── API Tests
├── test_api_authentication.py     # Signup/Login API tests
├── test_api_institution.py        # Institution & Account API tests
├── test_api_categories.py         # Categories API tests
├── test_api_transaction.py        # Transaction & CSV import API tests
│
└── Web Controller Tests
    └── test_web_controllers.py    # Web UI controller tests
```

### Test File Naming Conventions

- **Model tests**: `test_models_*.py`
- **API tests**: `test_api_*.py`
- **Web tests**: `test_web_*.py`
- **Integration tests**: `test_integration_*.py`

### Test Function Naming Conventions

- Test functions must start with `test_`
- Use descriptive names: `test_user_creation`, `test_login_invalid_password`
- Group related tests in classes starting with `Test`

## Test Coverage

### Current Coverage Areas

#### Models (100% coverage target)
- User model (creation, authentication, API keys, uniqueness)
- Institution model (CRUD operations, relationships)
- InstitutionAccount model (all account types, status, balances)
- CategoriesType model (creation, deletion)
- CategoriesGroup model (creation, deletion)
- Categories model (hierarchy, relationships)
- Transaction model (CRUD, relationships, date handling, amounts)

#### API Endpoints
- User signup/login
- Institution CRUD
- Account CRUD with all types and classes
- Categories CRUD (Type, Group, Category)
- Transaction CRUD
- CSV import with various scenarios
- Pagination
- Error handling

#### Web Controllers
- Authentication pages (login, signup, logout)
- Dashboard
- All management pages (institutions, accounts, categories, transactions)
- CSV import page
- Authentication requirements
- API documentation

### Coverage Goals

- **Overall**: 90%+
- **Models**: 95%+
- **API Controllers**: 90%+
- **Web Controllers**: 85%+

## Fixtures

Fixtures are reusable test components defined in `conftest.py`.

### Available Fixtures

#### Application Fixtures
- `app` - Flask application instance (session scope)
- `db` - Database instance (session scope)
- `session` - Database session (function scope, auto-rollback)
- `client` - Test client for making HTTP requests
- `runner` - CLI test runner
- `authenticated_client` - Pre-authenticated test client

#### Model Fixtures
- `test_user` - Test user account
- `test_institution` - Test financial institution
- `test_account` - Test account (checking account)
- `test_categories_type` - Test category type (Expense)
- `test_categories_group` - Test category group (Groceries)
- `test_category` - Test category (Walmart)
- `test_transaction` - Test transaction

#### Utility Fixtures
- `sample_csv_file` - Sample CSV file for import testing
- `tmp_path` - Temporary directory (pytest built-in)

### Using Fixtures

```python
def test_something(test_user, test_account):
    """Test using fixtures"""
    assert test_user.id is not None
    assert test_account.user_id == test_user.id
```

### Creating New Fixtures

Add fixtures to `conftest.py`:

```python
@pytest.fixture
def my_fixture(session):
    """Create a custom fixture"""
    obj = MyModel(...)
    obj.save()
    return obj
```

## Writing Tests

### Test Structure Template

```python
class TestFeatureName:
    """Test description"""

    def test_successful_case(self, fixture1, fixture2):
        """Test the happy path"""
        # Arrange
        data = {...}

        # Act
        result = function_under_test(data)

        # Assert
        assert result.status_code == 200
        assert result.data == expected_data

    def test_error_case(self, fixture1):
        """Test error handling"""
        with pytest.raises(ExpectedException):
            function_under_test(invalid_data)
```

### Best Practices

1. **One assertion per test** (when possible)
2. **Use descriptive test names** that explain what is being tested
3. **Follow AAA pattern**: Arrange, Act, Assert
4. **Test both success and failure cases**
5. **Use fixtures to avoid code duplication**
6. **Clean up resources** (handled automatically by fixtures)
7. **Don't test implementation details**, test behavior
8. **Keep tests independent** - tests should not depend on each other

### Testing API Endpoints

```python
def test_create_resource(client, test_user):
    """Test creating a resource via API"""
    response = client.post('/api/resource', json={
        'user_id': test_user.id,
        'name': 'Test Resource'
    })

    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Resource created successfully'
```

### Testing Models

```python
def test_model_creation(session, test_user):
    """Test creating a model instance"""
    obj = MyModel(
        user_id=test_user.id,
        name='Test'
    )
    obj.save()

    assert obj.id is not None
    assert obj.name == 'Test'
```

### Testing with Authentication

```python
def test_authenticated_endpoint(authenticated_client):
    """Test endpoint requiring authentication"""
    response = authenticated_client.get('/protected-route')
    assert response.status_code == 200
```

### Testing File Uploads

```python
def test_csv_upload(authenticated_client, tmp_path):
    """Test CSV file upload"""
    csv_file = tmp_path / "test.csv"
    csv_file.write_text("header1,header2\nval1,val2")

    with open(csv_file, 'rb') as f:
        response = authenticated_client.post(
            '/api/import',
            data={'file': (f, 'test.csv')},
            content_type='multipart/form-data'
        )

    assert response.status_code == 201
```

## Troubleshooting

### Common Issues

#### 1. Database Connection Error

```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solution**:
- Verify PostgreSQL is running
- Check database credentials in `conftest.py`
- Ensure test database exists
- Verify network connectivity to database server

#### 2. Import Errors

```
ImportError: No module named 'app'
```

**Solution**:
- Run tests from project root directory
- Ensure virtual environment is activated
- Install all dependencies: `pipenv install --dev`

#### 3. Fixture Not Found

```
fixture 'test_user' not found
```

**Solution**:
- Check that fixture is defined in `conftest.py`
- Ensure `conftest.py` is in the `tests/` directory
- Verify fixture name spelling

#### 4. Tests Failing Due to Existing Data

```
IntegrityError: duplicate key value violates unique constraint
```

**Solution**:
- Tests use function-scoped sessions with auto-rollback
- If issue persists, manually clear test database:
  ```bash
  psql -U security -h 192.168.1.150 -d ospf_test -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
  ```

#### 5. Session/Authentication Issues

```
KeyError: '_user_id'
```

**Solution**:
- Use `authenticated_client` fixture for authenticated tests
- Ensure Flask-Login is properly configured in test app

### Debug Mode

Run tests with verbose output and show print statements:

```bash
pytest -vv -s
```

### Inspect Test Database

```bash
# Connect to test database
psql -U security -h 192.168.1.150 -d ospf_test

# List tables
\dt

# Query data
SELECT * FROM "user";
SELECT * FROM transaction;
```

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: security
          POSTGRES_USER: security
          POSTGRES_DB: ospf_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install pipenv
        pipenv install --dev

    - name: Run tests
      run: pipenv run pytest --cov=api --cov=app
      env:
        TEST_DATABASE_URL: postgresql://security:security@localhost:5432/ospf_test
```

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Flask Testing Documentation](https://flask.palletsprojects.com/en/stable/testing/)
- [SQLAlchemy Testing Documentation](https://docs.sqlalchemy.org/en/20/core/connections.html#testing-for-database-connectivity)
- [pytest-flask Plugin](https://pytest-flask.readthedocs.io/)

## Contributing

When adding new features:

1. Write tests first (TDD approach recommended)
2. Ensure all tests pass: `pytest`
3. Check coverage: `pytest --cov=api --cov=app`
4. Add new fixtures to `conftest.py` if needed
5. Update this README if adding new test categories

## Test Maintenance

- Review and update tests when API changes
- Add tests for all new features
- Remove tests for deprecated features
- Keep fixtures up to date with model changes
- Maintain >90% overall code coverage
