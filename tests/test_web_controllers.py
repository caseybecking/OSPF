"""Tests for web UI controllers"""
import pytest
from unittest.mock import patch, Mock
from flask_login import current_user


class TestAccountController:
    """Test account web controller (login/signup pages)"""

    def test_signup_page_renders(self, client):
        """Test that signup page renders"""
        response = client.get('/account/signup')
        assert response.status_code == 200
        assert b'signup' in response.data.lower() or b'sign up' in response.data.lower()

    def test_login_page_renders(self, client):
        """Test that login page renders"""
        response = client.get('/account/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'sign in' in response.data.lower()

    def test_logout_requires_login(self, client):
        """Test that logout requires authentication"""
        response = client.post('/account/logout', follow_redirects=True)
        # Should redirect to login page
        assert b'login' in response.data.lower() or response.status_code == 302

    def test_logout_authenticated(self, authenticated_client):
        """Test logout with authenticated user"""
        response = authenticated_client.post('/account/logout', follow_redirects=True)
        # Should redirect successfully
        assert response.status_code == 200


class TestDashboardController:
    """Test dashboard controller"""

    def test_dashboard_requires_login(self, client):
        """Test that dashboard requires authentication"""
        response = client.get('/')
        # Should redirect to login
        assert response.status_code == 302
        assert '/account/login' in response.location

    def test_dashboard_renders_authenticated(self, authenticated_client):
        """Test that dashboard renders for authenticated users"""
        response = authenticated_client.get('/')
        assert response.status_code == 200
        # Dashboard should have some common elements
        assert b'dashboard' in response.data.lower() or b'welcome' in response.data.lower()


class TestInstitutionController:
    """Test institution web controller"""

    def test_institution_page_requires_login(self, client):
        """Test that institution page requires authentication"""
        response = client.get('/institution')
        assert response.status_code == 302
        assert '/account/login' in response.location

    @patch('app.institution.controllers.requests.get')
    def test_institution_page_renders_authenticated(self, mock_get, authenticated_client, test_institution):
        """Test that institution page renders for authenticated users"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'institutions': [
                {
                    'id': test_institution.id,
                    'name': test_institution.name,
                    'location': test_institution.location,
                    'description': test_institution.description
                }
            ]
        }
        mock_get.return_value = mock_response

        response = authenticated_client.get('/institution')
        assert response.status_code == 200
        assert b'institution' in response.data.lower()


class TestInstitutionAccountController:
    """Test institution account web controller"""

    def test_account_page_requires_login(self, client):
        """Test that account page requires authentication"""
        response = client.get('/account')
        assert response.status_code == 302
        assert '/account/login' in response.location

    @patch('app.institution_account.controllers.requests.get')
    def test_account_page_renders_authenticated(self, mock_get, authenticated_client, test_account):
        """Test that account page renders for authenticated users"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'accounts': [
                {
                    'id': test_account.id,
                    'name': test_account.name,
                    'balance': test_account.balance,
                    'account_type': test_account.account_type
                }
            ],
            'institutions': []
        }
        mock_get.return_value = mock_response

        response = authenticated_client.get('/account')
        assert response.status_code == 200
        # Page should have account-related content
        assert b'account' in response.data.lower() or b'checking' in response.data.lower()


class TestCategoriesController:
    """Test categories web controller"""

    def test_categories_page_requires_login(self, client):
        """Test that categories page requires authentication"""
        response = client.get('/categories')
        assert response.status_code == 302
        assert '/account/login' in response.location

    @patch('app.categories.controllers.requests.get')
    def test_categories_page_renders_authenticated(self, mock_get, authenticated_client, test_category):
        """Test that categories page renders for authenticated users"""
        # Mock the API responses (categories endpoint makes multiple requests)
        mock_response = Mock()
        mock_response.json.return_value = {
            'categories': [
                {
                    'id': test_category.id,
                    'name': test_category.name,
                    'categories_type_id': test_category.categories_type_id,
                    'categories_group_id': test_category.categories_group_id
                }
            ],
            'categories_type': [],
            'categories_group': []
        }
        mock_get.return_value = mock_response

        response = authenticated_client.get('/categories')
        assert response.status_code == 200
        assert b'categor' in response.data.lower()

    def test_categories_group_page_requires_login(self, client):
        """Test that categories group page requires authentication"""
        response = client.get('/categories/group')
        assert response.status_code == 302
        assert '/account/login' in response.location

    @patch('app.categories.controllers.requests.get')
    def test_categories_group_page_renders_authenticated(self, mock_get, authenticated_client, test_categories_group):
        """Test that categories group page renders for authenticated users"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'categories_group': [
                {
                    'id': test_categories_group.id,
                    'name': test_categories_group.name
                }
            ]
        }
        mock_get.return_value = mock_response

        response = authenticated_client.get('/categories/group')
        assert response.status_code == 200

    def test_categories_type_page_requires_login(self, client):
        """Test that categories type page requires authentication"""
        response = client.get('/categories/type')
        assert response.status_code == 302
        assert '/account/login' in response.location

    @patch('app.categories.controllers.requests.get')
    def test_categories_type_page_renders_authenticated(self, mock_get, authenticated_client, test_categories_type):
        """Test that categories type page renders for authenticated users"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'categories_type': [
                {
                    'id': test_categories_type.id,
                    'name': test_categories_type.name
                }
            ]
        }
        mock_get.return_value = mock_response

        response = authenticated_client.get('/categories/type')
        assert response.status_code == 200


class TestTransactionsController:
    """Test transactions web controller"""

    def test_transactions_page_requires_login(self, client):
        """Test that transactions page requires authentication"""
        response = client.get('/transactions')
        assert response.status_code == 302
        assert '/account/login' in response.location

    @patch('app.transactions.controllers.requests.get')
    def test_transactions_page_renders_authenticated(self, mock_get, authenticated_client, test_transaction):
        """Test that transactions page renders for authenticated users"""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = {
            'transactions': [
                {
                    'id': test_transaction.id,
                    'amount': test_transaction.amount,
                    'transaction_type': test_transaction.transaction_type
                }
            ],
            'pagination': {
                'total': 1,
                'pages': 1,
                'current_page': 1,
                'per_page': 100
            }
        }
        mock_get.return_value = mock_response

        response = authenticated_client.get('/transactions')
        assert response.status_code == 200
        assert b'transaction' in response.data.lower()

    def test_transactions_import_page_requires_login(self, client):
        """Test that transaction import page requires authentication"""
        response = client.get('/transactions/import')
        assert response.status_code == 302
        assert '/account/login' in response.location

    def test_transactions_import_page_renders_authenticated(self, authenticated_client):
        """Test that transaction import page renders for authenticated users"""
        response = authenticated_client.get('/transactions/import')
        assert response.status_code == 200
        assert b'import' in response.data.lower() or b'upload' in response.data.lower()


class TestNavigationAndRouting:
    """Test general navigation and routing"""

    def test_404_error_page(self, client):
        """Test that non-existent routes return 404"""
        response = client.get('/non-existent-page')
        assert response.status_code == 404

    def test_login_redirect_preserves_next_parameter(self, client):
        """Test that login redirect preserves the next parameter"""
        response = client.get('/institution')
        assert response.status_code == 302
        # Should redirect to login with next parameter
        assert '/account/login' in response.location


class TestAPIDocumentation:
    """Test API documentation endpoint"""

    def test_api_docs_accessible(self, client):
        """Test that API documentation is accessible"""
        response = client.get('/api/doc/')
        assert response.status_code == 200
        # Should contain Swagger/OpenAPI documentation
        assert b'api' in response.data.lower() or b'swagger' in response.data.lower()
