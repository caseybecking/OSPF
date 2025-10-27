"""Tests for Institution and Account API endpoints"""
import json
import pytest


class TestInstitutionAPI:
    """Test institution API endpoints"""

    def test_create_institution(self, client, test_user):
        """Test creating an institution via API"""
        response = client.post('/api/institution', json={
            'user_id': test_user.id,
            'name': 'API Test Bank',
            'location': 'API City',
            'description': 'Created via API'
        })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Institution created successfully'

    def test_create_institution_minimal(self, client, test_user):
        """Test creating institution with minimal required fields"""
        response = client.post('/api/institution', json={
            'user_id': test_user.id,
            'name': 'Minimal Bank'
        })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Institution created successfully'

    def test_list_institutions(self, client, test_institution):
        """Test listing all institutions"""
        response = client.get('/api/institution')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'institutions' in data
        assert len(data['institutions']) >= 1

        # Verify test institution is in list
        inst_ids = [inst['id'] for inst in data['institutions']]
        assert test_institution.id in inst_ids

    def test_create_institution_missing_name(self, client, test_user):
        """Test creating institution without required name field"""
        response = client.post('/api/institution', json={
            'user_id': test_user.id,
            'location': 'Somewhere'
            # Missing name
        })

        assert response.status_code in [400, 500]


class TestInstitutionAccountAPI:
    """Test institution account API endpoints"""

    def test_create_account(self, client, test_user, test_institution):
        """Test creating an account via API"""
        response = client.post('/api/institution/account', json={
            'institution_id': test_institution.id,
            'user_id': test_user.id,
            'name': 'API Test Checking',
            'number': '111222333',
            'status': 'active',
            'balance': 2000.00,
            'starting_balance': 1000.00,
            'account_type': 'checking',
            'account_class': 'asset'
        })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Account created successfully'

    def test_create_account_all_types(self, client, test_user, test_institution):
        """Test creating accounts of all types"""
        account_types = [
            ('checking', 'asset'),
            ('savings', 'asset'),
            ('credit', 'liability'),
            ('loan', 'liability'),
            ('investment', 'asset'),
            ('other', 'asset')
        ]

        for acc_type, acc_class in account_types:
            response = client.post('/api/institution/account', json={
                'institution_id': test_institution.id,
                'user_id': test_user.id,
                'name': f'Test {acc_type}',
                'status': 'active',
                'account_type': acc_type,
                'account_class': acc_class
            })

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['message'] == 'Account created successfully'

    def test_list_accounts(self, client, test_account):
        """Test listing all accounts"""
        response = client.get('/api/institution/account')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'accounts' in data
        assert len(data['accounts']) >= 1

        # Verify test account is in list
        acc_ids = [acc['id'] for acc in data['accounts']]
        assert test_account.id in acc_ids

    def test_create_account_minimal(self, client, test_user, test_institution):
        """Test creating account with minimal fields"""
        response = client.post('/api/institution/account', json={
            'institution_id': test_institution.id,
            'user_id': test_user.id,
            'name': 'Minimal Account',
            'status': 'active',
            'account_type': 'checking',
            'account_class': 'asset'
        })

        assert response.status_code == 201

    def test_update_balance_endpoint(self, client, test_account, session):
        """Test the update balance endpoint"""
        # First, verify initial balance
        assert test_account.balance == 1000.00

        # Call update balance endpoint
        response = client.get('/api/institution/account/update_balance')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data

    def test_account_includes_institution_data(self, client, test_account):
        """Test that account list includes institution data"""
        response = client.get('/api/institution/account')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Find our test account
        test_acc_data = None
        for acc in data['accounts']:
            if acc['id'] == test_account.id:
                test_acc_data = acc
                break

        assert test_acc_data is not None
        assert 'institution' in test_acc_data
        assert test_acc_data['institution']['id'] == test_account.institution_id

    def test_create_account_invalid_status(self, client, test_user, test_institution):
        """Test creating account with invalid status"""
        response = client.post('/api/institution/account', json={
            'institution_id': test_institution.id,
            'user_id': test_user.id,
            'name': 'Invalid Status Account',
            'status': 'invalid_status',  # Should only be active/inactive
            'account_type': 'checking',
            'account_class': 'asset'
        })

        # Should fail validation
        assert response.status_code in [400, 500]

    def test_create_account_invalid_type(self, client, test_user, test_institution):
        """Test creating account with invalid type"""
        response = client.post('/api/institution/account', json={
            'institution_id': test_institution.id,
            'user_id': test_user.id,
            'name': 'Invalid Type Account',
            'status': 'active',
            'account_type': 'invalid_type',  # Invalid
            'account_class': 'asset'
        })

        # Should fail validation
        assert response.status_code in [400, 500]

    def test_create_account_invalid_class(self, client, test_user, test_institution):
        """Test creating account with invalid class"""
        response = client.post('/api/institution/account', json={
            'institution_id': test_institution.id,
            'user_id': test_user.id,
            'name': 'Invalid Class Account',
            'status': 'active',
            'account_type': 'checking',
            'account_class': 'invalid_class'  # Should only be asset/liability
        })

        # Should fail validation
        assert response.status_code in [400, 500]
