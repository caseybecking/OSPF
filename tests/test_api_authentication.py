"""Tests for authentication API endpoints"""
import json
import pytest


class TestSignupAPI:
    """Test user signup endpoint"""

    def test_signup_success(self, client, session):
        """Test successful user signup"""
        response = client.post('/api/account/signup', json={
            'email': 'newuser@example.com',
            'username': 'newuser',
            'password': 'securepassword',
            'first_name': 'New',
            'last_name': 'User'
        })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'
        assert data['redirect'] == '/account/login'

    def test_signup_duplicate_email(self, client, test_user):
        """Test signup with duplicate email"""
        response = client.post('/api/account/signup', json={
            'email': test_user.email,  # Duplicate email
            'username': 'differentuser',
            'password': 'password',
            'first_name': 'Test',
            'last_name': 'User'
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'User email already exists'

    def test_signup_duplicate_username(self, client, test_user):
        """Test signup with duplicate username"""
        response = client.post('/api/account/signup', json={
            'email': 'different@example.com',
            'username': test_user.username,  # Duplicate username
            'password': 'password',
            'first_name': 'Test',
            'last_name': 'User'
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Username already exists'

    def test_signup_missing_fields(self, client):
        """Test signup with missing required fields"""
        response = client.post('/api/account/signup', json={
            'email': 'incomplete@example.com',
            # Missing username, password, first_name, last_name
        })

        # Should return 400 or validation error
        assert response.status_code in [400, 500]


class TestLoginAPI:
    """Test user login endpoint"""

    def test_login_success(self, client, test_user):
        """Test successful login"""
        response = client.post('/api/account/login', json={
            'email': test_user.email,
            'password': 'testpassword',  # From fixture
            'remember': False
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'User logged in successfully'
        assert data['redirect'] == '/'

    def test_login_with_remember(self, client, test_user):
        """Test login with remember me"""
        response = client.post('/api/account/login', json={
            'email': test_user.email,
            'password': 'testpassword',
            'remember': True
        })

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['message'] == 'User logged in successfully'

    def test_login_invalid_email(self, client):
        """Test login with invalid email"""
        response = client.post('/api/account/login', json={
            'email': 'nonexistent@example.com',
            'password': 'password',
            'remember': False
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Invalid Credentials'

    def test_login_invalid_password(self, client, test_user):
        """Test login with invalid password"""
        response = client.post('/api/account/login', json={
            'email': test_user.email,
            'password': 'wrongpassword',
            'remember': False
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Invalid Credentials'

    def test_login_missing_fields(self, client):
        """Test login with missing fields"""
        response = client.post('/api/account/login', json={
            'email': 'test@example.com',
            # Missing password
        })

        # Should handle missing fields gracefully
        assert response.status_code in [400, 500]


class TestUserAPI:
    """Test user management API endpoints"""

    def test_create_user_via_api(self, client, session):
        """Test creating user via user API endpoint"""
        response = client.post('/api/user', json={
            'email': 'apiuser@example.com',
            'username': 'apiuser',
            'password': 'password123',
            'first_name': 'API',
            'last_name': 'User'
        })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'User created successfully'

    def test_list_all_users(self, client, test_user):
        """Test listing all users"""
        response = client.get('/api/user')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'users' in data
        assert len(data['users']) >= 1

        # Check if test user is in the list
        user_ids = [user['id'] for user in data['users']]
        assert test_user.id in user_ids
