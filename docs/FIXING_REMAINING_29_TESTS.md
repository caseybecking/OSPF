# Fixing the Remaining 29 Test Failures

**Current Status:** 113/142 tests passing (80%)
**Remaining Failures:** 29 tests (21%)

## Breakdown of Failures

### Category 1: API Validation Tests (10 failures)
**Issue:** Missing input validation causes crashes instead of proper error responses

### Category 2: Web Controller Tests (19 failures)
**Issue:** Controllers make HTTP requests that fail in test environment

---

## Category 1: API Validation Fixes (10 tests)

### Problem
When invalid or missing data is provided to API endpoints, the code crashes during database operations instead of returning proper 400 errors.

**Example Error:**
```python
AttributeError: 'NoneType' object has no attribute 'encode'
```

This happens because the code tries to hash None when password is missing.

### Fix 1: Signup Missing Fields

**File:** `api/account/controllers.py`

**Location:** Line ~60-70 in the `Signup.post()` method

**Add validation before password hashing:**

```python
def post(self):
    """Signup endpoint"""
    data = request.get_json()
    email = data.get('email')
    username = data.get('username')
    password = data.get('password')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    # ADD THIS VALIDATION BLOCK:
    if not all([email, username, password, first_name, last_name]):
        return make_response(jsonify({
            'message': 'All fields are required'
        }), 400)

    # Check if user already exists
    existing_user = User.query.filter(
        (User.email == email) | (User.username == username)
    ).first()

    if existing_user:
        return make_response(jsonify({
            'message': 'User with this email or username already exists'
        }), 400)

    # Now safe to hash password
    hashed_password = generate_password_hash(password, method='scrypt')
    ...
```

**Tests Fixed:**
- `test_signup_missing_fields`

---

### Fix 2: Institution Account Invalid Status

**File:** `api/institution_account/controllers.py`

**Location:** In the `post()` method

**Add validation for enum fields:**

```python
def post(self):
    """Create new account"""
    data = request.get_json()

    # ADD VALIDATION FOR ENUMS:
    valid_statuses = ['active', 'inactive']
    valid_types = ['checking', 'savings', 'credit', 'loan', 'investment', 'other']
    valid_classes = ['asset', 'liability']

    status = data.get('status')
    account_type = data.get('account_type')
    account_class = data.get('account_class')

    if status not in valid_statuses:
        return make_response(jsonify({
            'message': f'Invalid status. Must be one of: {valid_statuses}'
        }), 400)

    if account_type not in valid_types:
        return make_response(jsonify({
            'message': f'Invalid account type. Must be one of: {valid_types}'
        }), 400)

    if account_class not in valid_classes:
        return make_response(jsonify({
            'message': f'Invalid account class. Must be one of: {valid_classes}'
        }), 400)

    # Continue with account creation...
```

**Tests Fixed:**
- `test_create_account_invalid_status`
- `test_create_account_invalid_type`
- `test_create_account_invalid_class`

---

### Fix 3: Categories Invalid References

**File:** `api/categories/controllers.py`

**Location:** In the `post()` method

**Add validation for foreign key references:**

```python
def post(self):
    """Create new category"""
    data = request.get_json()

    user_id = data.get('user_id')
    categories_group_id = data.get('categories_group_id')
    categories_type_id = data.get('categories_type_id')
    name = data.get('name')

    # ADD VALIDATION:
    if not all([user_id, categories_group_id, categories_type_id, name]):
        return make_response(jsonify({
            'message': 'All fields are required'
        }), 400)

    # Validate that referenced records exist
    from api.categories_group.models import CategoriesGroupModel
    from api.categories_type.models import CategoriesTypeModel

    group = CategoriesGroupModel.query.get(categories_group_id)
    if not group:
        return make_response(jsonify({
            'message': 'Invalid categories_group_id'
        }), 400)

    cat_type = CategoriesTypeModel.query.get(categories_type_id)
    if not cat_type:
        return make_response(jsonify({
            'message': 'Invalid categories_type_id'
        }), 400)

    # Continue with category creation...
```

**Tests Fixed:**
- `test_create_category_missing_required_fields`
- `test_create_category_invalid_references`

---

### Fix 4: Transaction Missing Required Fields

**File:** `api/transaction/controllers.py`

**Location:** In the `post()` method for creating transactions

**Add validation:**

```python
def post(self):
    """Create new transaction"""
    data = request.get_json()

    user_id = data.get('user_id')
    account_id = data.get('account_id')
    categories_id = data.get('categories_id')
    date = data.get('date')
    amount = data.get('amount')

    # ADD VALIDATION:
    if not all([user_id, account_id, categories_id, date, amount]):
        return make_response(jsonify({
            'message': 'All required fields must be provided'
        }), 400)

    # Validate amount is a number
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return make_response(jsonify({
            'message': 'Amount must be a valid number'
        }), 400)

    # Continue with transaction creation...
```

**Tests Fixed:**
- `test_create_transaction_missing_required_fields`
- `test_create_transaction_invalid_amount`

---

### Fix 5: Institution Missing Required Fields

**File:** `api/institution/controllers.py`

**Location:** In the `post()` method

**Add validation:**

```python
def post(self):
    """Create new institution"""
    data = request.get_json()

    user_id = data.get('user_id')
    name = data.get('name')
    location = data.get('location')
    description = data.get('description')

    # ADD VALIDATION:
    if not all([user_id, name, description]):
        return make_response(jsonify({
            'message': 'user_id, name, and description are required'
        }), 400)

    # Continue with institution creation...
```

**Tests Fixed:**
- `test_create_institution_missing_fields`

---

## Category 2: Web Controller Tests (19 failures)

### Problem
Web controllers call APIs using HTTP requests which fail in test environment:

```python
api_url = url_for('institution', _external=True)
response = requests.get(api_url, timeout=15)  # Fails - no server running
```

### Solution Options

#### Option A: Mock HTTP Requests (Recommended for now)

**File:** `tests/test_web_controllers.py`

**Add mocking to each web controller test:**

```python
import pytest
from unittest.mock import patch, Mock

class TestInstitutionController:
    """Test institution web controller"""

    @patch('app.institution.controllers.requests.get')
    def test_institution_page_renders_authenticated(self, mock_get, authenticated_client):
        """Test institution page renders for authenticated user"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'institutions': [
                {
                    'id': '123',
                    'name': 'Test Bank',
                    'location': 'Test City',
                    'description': 'Test Description'
                }
            ]
        }
        mock_get.return_value = mock_response

        # Now make the request
        response = authenticated_client.get('/institution')

        assert response.status_code == 200
        assert b'Test Bank' in response.data

        # Verify the mock was called
        assert mock_get.called
```

**Apply this pattern to all failing web controller tests:**

1. `test_institution_page_renders_authenticated` - Mock institution list
2. `test_institution_accounts_page_renders_authenticated` - Mock accounts list
3. `test_categories_page_renders_authenticated` - Mock categories hierarchy
4. `test_categories_type_page_renders_authenticated` - Mock types list
5. `test_categories_group_page_renders_authenticated` - Mock groups list
6. `test_transactions_page_renders_authenticated` - Mock transactions list
7. `test_account_page_renders_authenticated` - Mock account details
8. All other web controller rendering tests

**Complete Example for Multiple Endpoints:**

```python
from unittest.mock import patch, Mock

class TestWebControllers:
    """Test all web controllers"""

    @patch('app.institution.controllers.requests.get')
    def test_institution_list(self, mock_get, authenticated_client):
        mock_response = Mock()
        mock_response.json.return_value = {'institutions': []}
        mock_get.return_value = mock_response

        response = authenticated_client.get('/institution')
        assert response.status_code == 200

    @patch('app.categories.controllers.requests.get')
    def test_categories_list(self, mock_get, authenticated_client):
        mock_response = Mock()
        mock_response.json.return_value = {
            'categories': [],
            'categories_type': [],
            'categories_group': []
        }
        mock_get.return_value = mock_response

        response = authenticated_client.get('/categories')
        assert response.status_code == 200

    @patch('app.transaction.controllers.requests.get')
    def test_transactions_list(self, mock_get, authenticated_client):
        mock_response = Mock()
        mock_response.json.return_value = {
            'transactions': [],
            'categories': [],
            'accounts': []
        }
        mock_get.return_value = mock_response

        response = authenticated_client.get('/transactions')
        assert response.status_code == 200
```

---

#### Option B: Refactor Controllers (Better long-term solution)

Instead of making HTTP requests, have controllers directly use the models.

**Example Refactor for `app/institution/controllers.py`:**

```python
# BEFORE:
@institution_blueprint.route('/institution')
@login_required
def institution():
    api_url = url_for('institution', _external=True)
    response = requests.get(api_url, timeout=15)
    institutions = response.json().get('institutions', [])
    return render_template('institution/index.html', institutions=institutions)

# AFTER:
@institution_blueprint.route('/institution')
@login_required
def institution():
    from api.institution.models import InstitutionModel
    from flask_login import current_user

    # Directly query the database
    institutions = InstitutionModel.query.filter_by(
        user_id=current_user.id
    ).all()

    # Convert to dict format expected by template
    institutions = [inst.to_dict() for inst in institutions]

    return render_template('institution/index.html', institutions=institutions)
```

**Benefits:**
- No HTTP overhead
- Faster page loads
- Tests don't need mocking
- Simpler code

**Apply this pattern to:**
- `app/institution/controllers.py`
- `app/categories/controllers.py`
- `app/transaction/controllers.py`
- `app/account/controllers.py`

---

## Summary of Fixes

### Quick Wins (Can be done in 30-60 minutes)

1. **Add input validation to 5 API controllers** (30 min)
   - `api/account/controllers.py` - Signup validation
   - `api/institution_account/controllers.py` - Enum validation
   - `api/categories/controllers.py` - Foreign key validation
   - `api/transaction/controllers.py` - Required fields validation
   - `api/institution/controllers.py` - Required fields validation

2. **Mock HTTP requests in web controller tests** (30 min)
   - Add `@patch('app.*.controllers.requests.get')` decorators
   - Create mock responses for each endpoint
   - Update test assertions

**Expected Result:** 140-142/142 tests passing (98-100%)

### Better Long-term Solution (Can be done in 2-3 hours)

3. **Refactor web controllers** to not use HTTP requests
   - Import models directly
   - Query database directly
   - Remove requests.get() calls
   - Tests will pass without mocking

**Expected Result:** 142/142 tests passing + faster application

---

## Action Plan

### Phase 1: Fix API Validation (Gets to ~123/142 = 87%)

```bash
# Edit the 5 API controller files
# Add validation before database operations
# Run tests to verify
pytest tests/test_api_*.py -v
```

### Phase 2: Mock Web Controller Tests (Gets to 142/142 = 100%)

```bash
# Update test_web_controllers.py
# Add @patch decorators and mock responses
# Run tests to verify
pytest tests/test_web_controllers.py -v
```

### Phase 3 (Optional): Refactor Controllers

```bash
# Refactor web controllers to use models directly
# Remove mocking from tests
# Run all tests
pytest -v
```

---

## Commands to Run After Each Fix

```bash
# Activate venv
source venv/bin/activate

# Run all tests with summary
pytest tests/ --tb=short -v

# Run only API tests
pytest tests/test_api_*.py -v

# Run only web controller tests
pytest tests/test_web_controllers.py -v

# Run with coverage
pytest --cov=api --cov=app --cov-report=term-missing

# Generate HTML coverage report
pytest --cov=api --cov=app --cov-report=html
open htmlcov/index.html
```

---

## Files That Need Changes

### API Controllers (5 files):
1. `api/account/controllers.py`
2. `api/institution_account/controllers.py`
3. `api/categories/controllers.py`
4. `api/transaction/controllers.py`
5. `api/institution/controllers.py`

### Test Files (1 file):
1. `tests/test_web_controllers.py`

### Optional Refactor (4 files):
1. `app/institution/controllers.py`
2. `app/categories/controllers.py`
3. `app/transaction/controllers.py`
4. `app/account/controllers.py`

---

## Next Steps

Would you like me to:
1. **Make all the API validation fixes** (gets to 87% pass rate)
2. **Add mocking to web controller tests** (gets to 100% pass rate)
3. **Or refactor the web controllers** (cleaner long-term solution)

All approaches will get you to 100% passing tests. The choice is between:
- Quick fix (mocking) - 30 min
- Better fix (refactoring) - 2-3 hours but cleaner code
