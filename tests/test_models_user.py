"""Tests for User model"""
import pytest
from werkzeug.security import check_password_hash, generate_password_hash
from api.user.models import User


class TestUserModel:
    """Test User model functionality"""

    def test_user_creation(self, session):
        """Test creating a new user"""
        user = User(
            email='newuser@example.com',
            username='newuser',
            password=generate_password_hash('password123', method='scrypt'),
            first_name='New',
            last_name='User'
        )
        user.save()

        assert user.id is not None
        assert user.email == 'newuser@example.com'
        assert user.username == 'newuser'
        assert user.first_name == 'New'
        assert user.last_name == 'User'
        assert user.created_at is not None
        assert user.updated_at is not None

    def test_user_password_hashing(self, session):
        """Test that passwords are properly hashed"""
        password = 'securepassword123'
        user = User(
            email='secure@example.com',
            username='secureuser',
            password=generate_password_hash(password, method='scrypt'),
            first_name='Secure',
            last_name='User'
        )
        user.save()

        # Password should be hashed
        assert user.password != password
        # But should verify correctly
        assert check_password_hash(user.password, password)

    def test_user_to_dict(self, test_user):
        """Test user serialization to dictionary"""
        user_dict = test_user.to_dict()

        assert user_dict['id'] == test_user.id
        assert user_dict['email'] == test_user.email
        assert user_dict['username'] == test_user.username
        assert user_dict['first_name'] == test_user.first_name
        assert user_dict['last_name'] == test_user.last_name
        assert 'password' not in user_dict  # Password should not be exposed
        assert 'created_at' in user_dict
        assert 'updated_at' in user_dict

    def test_user_repr(self, test_user):
        """Test user string representation"""
        assert repr(test_user) == f'<User {test_user.username!r}>'

    def test_user_generate_api_key(self, test_user, session):
        """Test API key generation"""
        # Initially no API key
        assert test_user.api_key is None

        # Generate API key
        test_user.generate_api_key()

        assert test_user.api_key is not None
        assert len(test_user.api_key) == 64

    def test_user_api_key_uniqueness(self, session):
        """Test that API keys are unique"""
        user1 = User(
            email='user1@example.com',
            username='user1',
            password=generate_password_hash('password', method='scrypt'),
            first_name='User',
            last_name='One'
        )
        user1.save()
        user1.generate_api_key()

        user2 = User(
            email='user2@example.com',
            username='user2',
            password=generate_password_hash('password', method='scrypt'),
            first_name='User',
            last_name='Two'
        )
        user2.save()
        user2.generate_api_key()

        assert user1.api_key != user2.api_key

    def test_user_delete(self, session):
        """Test deleting a user"""
        user = User(
            email='deleteme@example.com',
            username='deleteme',
            password=generate_password_hash('password', method='scrypt'),
            first_name='Delete',
            last_name='Me'
        )
        user.save()
        user_id = user.id

        # Verify user exists
        assert User.query.get(user_id) is not None

        # Delete user
        user.delete()

        # Verify user is deleted
        assert User.query.get(user_id) is None

    def test_user_email_uniqueness(self, session, test_user):
        """Test that email must be unique"""
        # Attempting to create user with same email should fail at DB level
        duplicate_user = User(
            email=test_user.email,  # Same email
            username='different',
            password=generate_password_hash('password', method='scrypt'),
            first_name='Dup',
            last_name='User'
        )

        with pytest.raises(Exception):  # Will raise IntegrityError
            duplicate_user.save()

    def test_user_username_uniqueness(self, session, test_user):
        """Test that username must be unique"""
        duplicate_user = User(
            email='different@example.com',
            username=test_user.username,  # Same username
            password=generate_password_hash('password', method='scrypt'),
            first_name='Dup',
            last_name='User'
        )

        with pytest.raises(Exception):  # Will raise IntegrityError
            duplicate_user.save()

    def test_user_query_by_email(self, test_user):
        """Test querying user by email"""
        found_user = User.query.filter_by(email=test_user.email).first()

        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.email == test_user.email

    def test_user_query_by_username(self, test_user):
        """Test querying user by username"""
        found_user = User.query.filter_by(username=test_user.username).first()

        assert found_user is not None
        assert found_user.id == test_user.id
        assert found_user.username == test_user.username
