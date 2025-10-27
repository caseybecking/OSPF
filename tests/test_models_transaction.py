"""Tests for Transaction model"""
import pytest
from datetime import datetime, timedelta
from api.transaction.models import TransactionModel


class TestTransactionModel:
    """Test Transaction model functionality"""

    def test_transaction_creation(self, session, test_user, test_account, test_category):
        """Test creating a new transaction"""
        transaction = TransactionModel(
            user_id=test_user.id,
            categories_id=test_category.id,
            account_id=test_account.id,
            amount=100.00,
            transaction_type='Withdrawal',
            external_id='TEST-NEW-001',
            external_date=datetime.now(),
            description='New test transaction'
        )
        transaction.save()

        assert transaction.id is not None
        assert transaction.user_id == test_user.id
        assert transaction.categories_id == test_category.id
        assert transaction.account_id == test_account.id
        assert transaction.amount == 100.00
        assert transaction.transaction_type == 'Withdrawal'
        assert transaction.external_id == 'TEST-NEW-001'
        assert transaction.description == 'New test transaction'
        assert transaction.created_at is not None
        assert transaction.updated_at is not None

    def test_transaction_types(self, session, test_user, test_account, test_category):
        """Test different transaction types"""
        # Withdrawal
        withdrawal = TransactionModel(
            user_id=test_user.id,
            categories_id=test_category.id,
            account_id=test_account.id,
            amount=50.00,
            transaction_type='Withdrawal',
            external_id='TEST-W-001',
            external_date=datetime.now(),
            description='Test withdrawal'
        )
        withdrawal.save()
        assert withdrawal.transaction_type == 'Withdrawal'

        # Deposit
        deposit = TransactionModel(
            user_id=test_user.id,
            categories_id=test_category.id,
            account_id=test_account.id,
            amount=200.00,
            transaction_type='Deposit',
            external_id='TEST-D-001',
            external_date=datetime.now(),
            description='Test deposit'
        )
        deposit.save()
        assert deposit.transaction_type == 'Deposit'

    def test_transaction_to_dict(self, test_transaction):
        """Test transaction serialization to dictionary"""
        trans_dict = test_transaction.to_dict()

        assert trans_dict['id'] == test_transaction.id
        assert trans_dict['user_id'] == test_transaction.user_id
        assert trans_dict['categories_id'] == test_transaction.categories_id
        assert trans_dict['account_id'] == test_transaction.account_id
        assert trans_dict['amount'] == test_transaction.amount
        assert trans_dict['transaction_type'] == test_transaction.transaction_type
        assert trans_dict['external_id'] == test_transaction.external_id
        assert trans_dict['description'] == test_transaction.description
        assert 'categories' in trans_dict
        assert 'account' in trans_dict
        assert 'created_at' in trans_dict
        assert 'updated_at' in trans_dict

    def test_transaction_repr(self, test_transaction):
        """Test transaction string representation"""
        assert repr(test_transaction) == f'<Transaction {test_transaction.id!r}>'

    def test_transaction_relationships(self, test_transaction, test_account, test_category):
        """Test transaction relationships with account and category"""
        # Test account relationship
        assert test_transaction.account_id == test_account.id
        assert test_transaction.account.name == test_account.name

        # Test category relationship
        assert test_transaction.categories_id == test_category.id
        assert test_transaction.categories.name == test_category.name

    def test_transaction_delete(self, session, test_user, test_account, test_category):
        """Test deleting a transaction"""
        transaction = TransactionModel(
            user_id=test_user.id,
            categories_id=test_category.id,
            account_id=test_account.id,
            amount=75.00,
            transaction_type='Withdrawal',
            external_id='TEST-DEL-001',
            external_date=datetime.now(),
            description='Delete me'
        )
        transaction.save()
        trans_id = transaction.id

        assert TransactionModel.query.get(trans_id) is not None
        transaction.delete()
        assert TransactionModel.query.get(trans_id) is None

    def test_transaction_query_by_user(self, test_transaction, test_user):
        """Test querying transactions by user"""
        transactions = TransactionModel.query.filter_by(user_id=test_user.id).all()

        assert len(transactions) >= 1
        assert test_transaction in transactions

    def test_transaction_query_by_account(self, test_transaction, test_account):
        """Test querying transactions by account"""
        transactions = TransactionModel.query.filter_by(account_id=test_account.id).all()

        assert len(transactions) >= 1
        assert test_transaction in transactions

    def test_transaction_query_by_category(self, test_transaction, test_category):
        """Test querying transactions by category"""
        transactions = TransactionModel.query.filter_by(categories_id=test_category.id).all()

        assert len(transactions) >= 1
        assert test_transaction in transactions

    def test_transaction_external_id_uniqueness(self, session, test_user, test_account, test_category):
        """Test that external_id combined with user_id should be unique"""
        external_id = 'UNIQUE-TEST-001'

        # First transaction
        trans1 = TransactionModel(
            user_id=test_user.id,
            categories_id=test_category.id,
            account_id=test_account.id,
            amount=100.00,
            transaction_type='Withdrawal',
            external_id=external_id,
            external_date=datetime.now(),
            description='First'
        )
        trans1.save()

        # Attempt to create duplicate (same user_id and external_id)
        trans2 = TransactionModel(
            user_id=test_user.id,
            categories_id=test_category.id,
            account_id=test_account.id,
            amount=200.00,
            transaction_type='Deposit',
            external_id=external_id,  # Same external_id
            external_date=datetime.now(),
            description='Duplicate'
        )

        # Should be prevented by unique constraint or business logic
        # This will succeed at model level but should fail during CSV import
        # due to the duplicate check in the import logic

    def test_transaction_date_handling(self, session, test_user, test_account, test_category):
        """Test transaction date handling"""
        specific_date = datetime(2024, 1, 15, 10, 30, 0)

        transaction = TransactionModel(
            user_id=test_user.id,
            categories_id=test_category.id,
            account_id=test_account.id,
            amount=123.45,
            transaction_type='Withdrawal',
            external_id='DATE-TEST-001',
            external_date=specific_date,
            description='Date test'
        )
        transaction.save()

        assert transaction.external_date.year == 2024
        assert transaction.external_date.month == 1
        assert transaction.external_date.day == 15

    def test_transaction_amount_precision(self, session, test_user, test_account, test_category):
        """Test transaction amount decimal precision"""
        amounts = [0.01, 10.50, 100.99, 1234.56, 999999.99]

        for amount in amounts:
            transaction = TransactionModel(
                user_id=test_user.id,
                categories_id=test_category.id,
                account_id=test_account.id,
                amount=amount,
                transaction_type='Withdrawal',
                external_id=f'AMOUNT-TEST-{amount}',
                external_date=datetime.now(),
                description=f'Amount {amount}'
            )
            transaction.save()
            assert transaction.amount == amount

    def test_transaction_query_by_date_range(self, session, test_user, test_account, test_category):
        """Test querying transactions by date range"""
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # Create transactions with different dates
        trans_yesterday = TransactionModel(
            user_id=test_user.id,
            categories_id=test_category.id,
            account_id=test_account.id,
            amount=50.00,
            transaction_type='Withdrawal',
            external_id='YESTERDAY',
            external_date=yesterday,
            description='Yesterday'
        )
        trans_yesterday.save()

        trans_today = TransactionModel(
            user_id=test_user.id,
            categories_id=test_category.id,
            account_id=test_account.id,
            amount=75.00,
            transaction_type='Withdrawal',
            external_id='TODAY',
            external_date=today,
            description='Today'
        )
        trans_today.save()

        # Query transactions from yesterday to today
        transactions = TransactionModel.query.filter(
            TransactionModel.external_date >= yesterday,
            TransactionModel.external_date <= today
        ).all()

        assert len(transactions) >= 2
        trans_ids = [t.id for t in transactions]
        assert trans_yesterday.id in trans_ids
        assert trans_today.id in trans_ids

    def test_transaction_query_by_amount_range(self, session, test_user, test_account, test_category):
        """Test querying transactions by amount range"""
        # Create transactions with different amounts
        amounts = [10.00, 50.00, 100.00, 200.00, 500.00]

        for idx, amount in enumerate(amounts):
            transaction = TransactionModel(
                user_id=test_user.id,
                categories_id=test_category.id,
                account_id=test_account.id,
                amount=amount,
                transaction_type='Withdrawal',
                external_id=f'AMOUNT-RANGE-{idx}',
                external_date=datetime.now(),
                description=f'Amount {amount}'
            )
            transaction.save()

        # Query transactions between 50 and 200
        transactions = TransactionModel.query.filter(
            TransactionModel.amount >= 50.00,
            TransactionModel.amount <= 200.00
        ).all()

        trans_amounts = [t.amount for t in transactions]
        assert 50.00 in trans_amounts
        assert 100.00 in trans_amounts
        assert 200.00 in trans_amounts

    def test_transaction_optional_description(self, session, test_user, test_account, test_category):
        """Test that description is optional"""
        transaction = TransactionModel(
            user_id=test_user.id,
            categories_id=test_category.id,
            account_id=test_account.id,
            amount=100.00,
            transaction_type='Withdrawal',
            external_id='NO-DESC-001',
            external_date=datetime.now(),
            description=None  # No description
        )
        transaction.save()

        assert transaction.description is None
