"""Tests for Transaction API endpoints and CSV import"""
import json
import pytest
import os
from io import BytesIO
from datetime import datetime


class TestTransactionAPI:
    """Test transaction API endpoints"""

    def test_create_transaction(self, client, test_user, test_account, test_category):
        """Test creating a transaction via API"""
        response = client.post('/api/transaction', json={
            'user_id': test_user.id,
            'categories_id': test_category.id,
            'account_id': test_account.id,
            'amount': 125.50,
            'transaction_type': 'Withdrawal',
            'external_id': 'API-TEST-001',
            'external_date': datetime.now().isoformat(),
            'description': 'API test transaction'
        })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Transaction created successfully'

    def test_create_transaction_minimal(self, client, test_user, test_account, test_category):
        """Test creating transaction with minimal required fields"""
        response = client.post('/api/transaction', json={
            'user_id': test_user.id,
            'categories_id': test_category.id,
            'account_id': test_account.id,
            'amount': 50.00,
            'transaction_type': 'Deposit'
        })

        assert response.status_code == 201

    def test_list_transactions(self, client, test_transaction):
        """Test listing all transactions"""
        response = client.get('/api/transaction')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'transactions' in data
        assert 'pagination' in data
        assert len(data['transactions']) >= 1

        # Verify test transaction is in list
        trans_ids = [t['id'] for t in data['transactions']]
        assert test_transaction.id in trans_ids

    def test_list_transactions_pagination(self, client, session, test_user, test_account, test_category):
        """Test transaction pagination"""
        from api.transaction.models import TransactionModel

        # Create multiple transactions
        for i in range(15):
            transaction = TransactionModel(
                user_id=test_user.id,
                categories_id=test_category.id,
                account_id=test_account.id,
                amount=10.00 * (i + 1),
                transaction_type='Withdrawal',
                external_id=f'PAGE-TEST-{i}',
                external_date=datetime.now(),
                description=f'Pagination test {i}'
            )
            transaction.save()

        # Test first page with 10 items
        response = client.get('/api/transaction?page=1&per_page=10')
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['pagination']['current_page'] == 1
        assert data['pagination']['per_page'] == 10
        assert data['pagination']['total'] >= 15
        assert len(data['transactions']) == 10

        # Test second page
        response = client.get('/api/transaction?page=2&per_page=10')
        assert response.status_code == 200
        data = json.loads(response.data)

        assert data['pagination']['current_page'] == 2
        assert len(data['transactions']) >= 5

    def test_list_transactions_default_pagination(self, client, test_transaction):
        """Test default pagination (100 items per page)"""
        response = client.get('/api/transaction')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['pagination']['per_page'] == 100
        assert data['pagination']['current_page'] == 1

    def test_transaction_includes_relationships(self, client, test_transaction):
        """Test that transaction list includes account and category data"""
        response = client.get('/api/transaction')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Find our test transaction
        test_trans_data = None
        for trans in data['transactions']:
            if trans['id'] == test_transaction.id:
                test_trans_data = trans
                break

        assert test_trans_data is not None
        assert 'account' in test_trans_data
        assert 'categories' in test_trans_data
        assert test_trans_data['account']['id'] == test_transaction.account_id
        assert test_trans_data['categories']['id'] == test_transaction.categories_id

    def test_create_transaction_missing_required_fields(self, client, test_user):
        """Test creating transaction with missing required fields"""
        response = client.post('/api/transaction', json={
            'user_id': test_user.id,
            'amount': 100.00
            # Missing categories_id, account_id, transaction_type
        })

        assert response.status_code in [400, 500]


class TestTransactionCSVImport:
    """Test CSV import functionality"""

    def test_csv_import_success(self, authenticated_client, test_category, tmp_path):
        """Test successful CSV import"""
        # Create a test CSV file
        csv_content = f"""Transaction ID,Category,Institution,Account,Date,Amount,Description
CSV-001,{test_category.name},Test Bank,Checking,01/15/2024,$50.00,Walmart
CSV-002,{test_category.name},Test Bank,Checking,01/20/2024,$75.50,Target"""

        csv_file = tmp_path / "test_import.csv"
        csv_file.write_text(csv_content)

        # Upload the file
        with open(csv_file, 'rb') as f:
            response = authenticated_client.post(
                '/api/transaction/csv_import',
                data={'file': (f, 'test_import.csv')},
                content_type='multipart/form-data'
            )

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Transactions imported successfully'

    def test_csv_import_creates_institution(self, authenticated_client, test_category, tmp_path):
        """Test that CSV import creates missing institutions"""
        csv_content = f"""Transaction ID,Category,Institution,Account,Date,Amount,Description
NEW-INST-001,{test_category.name},New Bank,Checking,01/15/2024,$100.00,Test"""

        csv_file = tmp_path / "new_institution.csv"
        csv_file.write_text(csv_content)

        with open(csv_file, 'rb') as f:
            response = authenticated_client.post(
                '/api/transaction/csv_import',
                data={'file': (f, 'new_institution.csv')},
                content_type='multipart/form-data'
            )

        assert response.status_code == 201

        # Verify institution was created
        from api.institution.models import InstitutionModel
        new_inst = InstitutionModel.query.filter_by(name='New Bank').first()
        assert new_inst is not None

    def test_csv_import_creates_account(self, authenticated_client, test_category, test_institution, tmp_path):
        """Test that CSV import creates missing accounts"""
        csv_content = f"""Transaction ID,Category,Institution,Account,Date,Amount,Description
NEW-ACC-001,{test_category.name},{test_institution.name},New Savings,01/15/2024,$200.00,Test"""

        csv_file = tmp_path / "new_account.csv"
        csv_file.write_text(csv_content)

        with open(csv_file, 'rb') as f:
            response = authenticated_client.post(
                '/api/transaction/csv_import',
                data={'file': (f, 'new_account.csv')},
                content_type='multipart/form-data'
            )

        assert response.status_code == 201

        # Verify account was created
        from api.institution_account.models import InstitutionAccountModel
        new_acc = InstitutionAccountModel.query.filter_by(name='New Savings').first()
        assert new_acc is not None

    def test_csv_import_skips_duplicates(self, authenticated_client, test_transaction, test_category, tmp_path):
        """Test that CSV import skips duplicate transactions"""
        # Use the external_id from test_transaction
        csv_content = f"""Transaction ID,Category,Institution,Account,Date,Amount,Description
{test_transaction.external_id},{test_category.name},Test Bank,Checking,01/15/2024,$50.00,Duplicate"""

        csv_file = tmp_path / "duplicate.csv"
        csv_file.write_text(csv_content)

        # Count transactions before import
        from api.transaction.models import TransactionModel
        count_before = TransactionModel.query.filter_by(
            external_id=test_transaction.external_id
        ).count()

        with open(csv_file, 'rb') as f:
            response = authenticated_client.post(
                '/api/transaction/csv_import',
                data={'file': (f, 'duplicate.csv')},
                content_type='multipart/form-data'
            )

        # Should still succeed but skip the duplicate
        assert response.status_code == 201

        # Count should be the same (duplicate was skipped)
        count_after = TransactionModel.query.filter_by(
            external_id=test_transaction.external_id
        ).count()
        assert count_after == count_before

    def test_csv_import_handles_positive_negative_amounts(self, authenticated_client, test_category, tmp_path):
        """Test that CSV import correctly handles positive and negative amounts"""
        csv_content = f"""Transaction ID,Category,Institution,Account,Date,Amount,Description
POS-001,{test_category.name},Test Bank,Checking,01/15/2024,$100.00,Positive
NEG-001,{test_category.name},Test Bank,Checking,01/16/2024,$-50.00,Negative"""

        csv_file = tmp_path / "amounts.csv"
        csv_file.write_text(csv_content)

        with open(csv_file, 'rb') as f:
            response = authenticated_client.post(
                '/api/transaction/csv_import',
                data={'file': (f, 'amounts.csv')},
                content_type='multipart/form-data'
            )

        assert response.status_code == 201

        # Verify transactions were created with correct types
        from api.transaction.models import TransactionModel
        pos_trans = TransactionModel.query.filter_by(external_id='POS-001').first()
        neg_trans = TransactionModel.query.filter_by(external_id='NEG-001').first()

        assert pos_trans is not None
        assert neg_trans is not None
        # Positive should be Deposit, negative should be Withdrawal
        assert pos_trans.transaction_type == 'Deposit'
        assert neg_trans.transaction_type == 'Withdrawal'

    def test_csv_import_no_file(self, authenticated_client):
        """Test CSV import with no file provided"""
        response = authenticated_client.post(
            '/api/transaction/csv_import',
            data={},
            content_type='multipart/form-data'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'No file'

    def test_csv_import_blank_filename(self, authenticated_client):
        """Test CSV import with blank filename"""
        response = authenticated_client.post(
            '/api/transaction/csv_import',
            data={'file': (BytesIO(b''), '')},
            content_type='multipart/form-data'
        )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Filename cannot be blank'

    def test_csv_import_invalid_file_type(self, authenticated_client, tmp_path):
        """Test CSV import with invalid file type"""
        # Create a .txt file instead of .csv
        txt_file = tmp_path / "test.txt"
        txt_file.write_text("This is not a CSV file")

        with open(txt_file, 'rb') as f:
            response = authenticated_client.post(
                '/api/transaction/csv_import',
                data={'file': (f, 'test.txt')},
                content_type='multipart/form-data'
            )

        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['message'] == 'Invalid file type'

    def test_csv_import_malformed_csv(self, authenticated_client, tmp_path):
        """Test CSV import with malformed CSV"""
        csv_content = """Transaction ID,Category,Institution,Account,Date,Amount,Description
MALFORMED,Missing,Columns"""  # Not enough columns

        csv_file = tmp_path / "malformed.csv"
        csv_file.write_text(csv_content)

        with open(csv_file, 'rb') as f:
            response = authenticated_client.post(
                '/api/transaction/csv_import',
                data={'file': (f, 'malformed.csv')},
                content_type='multipart/form-data'
            )

        # Should return error
        assert response.status_code == 400

    def test_csv_import_missing_category(self, authenticated_client, tmp_path):
        """Test CSV import with non-existent category"""
        csv_content = """Transaction ID,Category,Institution,Account,Date,Amount,Description
NOCAT-001,NonExistentCategory,Test Bank,Checking,01/15/2024,$50.00,Test"""

        csv_file = tmp_path / "no_category.csv"
        csv_file.write_text(csv_content)

        with open(csv_file, 'rb') as f:
            response = authenticated_client.post(
                '/api/transaction/csv_import',
                data={'file': (f, 'no_category.csv')},
                content_type='multipart/form-data'
            )

        # Should fail because category doesn't exist and can't be auto-created
        assert response.status_code == 400

    def test_csv_import_date_formats(self, authenticated_client, test_category, tmp_path):
        """Test CSV import with different date formats"""
        csv_content = f"""Transaction ID,Category,Institution,Account,Date,Amount,Description
DATE-001,{test_category.name},Test Bank,Checking,01/15/2024,$50.00,Test
DATE-002,{test_category.name},Test Bank,Checking,12/31/2023,$75.00,Test"""

        csv_file = tmp_path / "dates.csv"
        csv_file.write_text(csv_content)

        with open(csv_file, 'rb') as f:
            response = authenticated_client.post(
                '/api/transaction/csv_import',
                data={'file': (f, 'dates.csv')},
                content_type='multipart/form-data'
            )

        assert response.status_code == 201

        # Verify dates were parsed correctly
        from api.transaction.models import TransactionModel
        trans1 = TransactionModel.query.filter_by(external_id='DATE-001').first()
        trans2 = TransactionModel.query.filter_by(external_id='DATE-002').first()

        assert trans1.external_date.month == 1
        assert trans1.external_date.day == 15
        assert trans1.external_date.year == 2024

        assert trans2.external_date.month == 12
        assert trans2.external_date.day == 31
        assert trans2.external_date.year == 2023

    def test_csv_import_requires_authentication(self, client, tmp_path):
        """Test that CSV import requires authentication"""
        csv_content = """Transaction ID,Category,Institution,Account,Date,Amount,Description
AUTH-001,Groceries,Test Bank,Checking,01/15/2024,$50.00,Test"""

        csv_file = tmp_path / "auth_test.csv"
        csv_file.write_text(csv_content)

        # Try without authentication
        with open(csv_file, 'rb') as f:
            response = client.post(
                '/api/transaction/csv_import',
                data={'file': (f, 'auth_test.csv')},
                content_type='multipart/form-data'
            )

        # Should fail because user_id from session will be None
        assert response.status_code in [400, 401, 500]
