"""Pytest configuration and fixtures for OSPF tests"""
import os
import pytest
from sqlalchemy import event
from app import create_app
from app.database import db as _db
from api.user.models import User
from api.institution.models import InstitutionModel
from api.institution_account.models import InstitutionAccountModel
from api.categories_type.models import CategoriesTypeModel
from api.categories_group.models import CategoriesGroupModel
from api.categories.models import CategoriesModel
from api.transaction.models import TransactionModel
from werkzeug.security import generate_password_hash


class TestConfig:
    """Test configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'postgresql+psycopg2://security:security@192.168.1.150:5432/ospf_test?sslmode=disable'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = False
    SECRET_KEY = b'test-secret-key'
    DEFAULT_USER_ID = 'test-user-id'
    ALLOWED_EXTENSIONS = {'csv'}
    UPLOAD_FOLDER = 'test_uploads'


@pytest.fixture(scope='session')
def app():
    """Create and configure a test app instance"""
    # Override config with test config
    os.environ['FLASK_ENV'] = 'TESTING'

    _app = create_app()
    _app.config.from_object(TestConfig)

    # Create application context
    ctx = _app.app_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.fixture(scope='session')
def db(app):
    """Create a test database and session"""
    # Create all tables
    _db.create_all()

    yield _db

    # Drop all tables after tests
    _db.drop_all()


@pytest.fixture(scope='function', autouse=True)
def session(db):
    """Create a new database session for each test with automatic cleanup"""
    # Start with a clean session
    db.session.rollback()

    yield db.session

    # Clean up after test - delete all data to ensure test isolation
    db.session.rollback()

    # Delete all rows from all tables
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()


@pytest.fixture
def client(app):
    """Create a test client for the Flask app"""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create a test CLI runner"""
    return app.test_cli_runner()


@pytest.fixture
def test_user(session):
    """Create a test user"""
    user = User(
        email='test@example.com',
        username='testuser',
        password=generate_password_hash('testpassword', method='scrypt'),
        first_name='Test',
        last_name='User'
    )
    user.save()
    return user


@pytest.fixture
def test_institution(session, test_user):
    """Create a test institution"""
    institution = InstitutionModel(
        user_id=test_user.id,
        name='Test Bank',
        location='Test City',
        description='A test bank'
    )
    institution.save()
    return institution


@pytest.fixture
def test_account(session, test_user, test_institution):
    """Create a test account"""
    account = InstitutionAccountModel(
        institution_id=test_institution.id,
        user_id=test_user.id,
        name='Test Checking',
        number='123456789',
        status='active',
        balance=1000.00,
        starting_balance=500.00,
        account_type='checking',
        account_class='asset'
    )
    account.save()
    return account


@pytest.fixture
def test_categories_type(session, test_user):
    """Create a test category type"""
    cat_type = CategoriesTypeModel(
        user_id=test_user.id,
        name='Expense'
    )
    cat_type.save()
    return cat_type


@pytest.fixture
def test_categories_group(session, test_user):
    """Create a test category group"""
    cat_group = CategoriesGroupModel(
        user_id=test_user.id,
        name='Groceries'
    )
    cat_group.save()
    return cat_group


@pytest.fixture
def test_category(session, test_user, test_categories_type, test_categories_group):
    """Create a test category"""
    category = CategoriesModel(
        user_id=test_user.id,
        categories_group_id=test_categories_group.id,
        categories_type_id=test_categories_type.id,
        name='Walmart'
    )
    category.save()
    return category


@pytest.fixture
def test_transaction(session, test_user, test_account, test_category):
    """Create a test transaction"""
    from datetime import datetime
    transaction = TransactionModel(
        user_id=test_user.id,
        categories_id=test_category.id,
        account_id=test_account.id,
        amount=50.00,
        transaction_type='Withdrawal',
        external_id='TEST-001',
        external_date=datetime.now(),
        description='Test purchase'
    )
    transaction.save()
    return transaction


@pytest.fixture
def authenticated_client(client, test_user):
    """Create an authenticated test client"""
    with client.session_transaction() as sess:
        sess['_user_id'] = test_user.id
    return client


@pytest.fixture
def sample_csv_file(tmp_path):
    """Create a sample CSV file for testing imports"""
    csv_content = """Transaction ID,Category,Institution,Account,Date,Amount,Description
TEST-001,Groceries,Test Bank,Checking,01/15/2024,$50.00,Walmart
TEST-002,Salary,Test Bank,Checking,01/01/2024,$2500.00,Monthly Salary
TEST-003,Utilities,Test Bank,Checking,01/10/2024,$150.00,Electric Bill"""

    csv_file = tmp_path / "test_transactions.csv"
    csv_file.write_text(csv_content)
    return str(csv_file)
