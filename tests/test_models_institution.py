"""Tests for Institution and InstitutionAccount models"""
import pytest
from api.institution.models import InstitutionModel
from api.institution_account.models import InstitutionAccountModel


class TestInstitutionModel:
    """Test Institution model functionality"""

    def test_institution_creation(self, session, test_user):
        """Test creating a new institution"""
        institution = InstitutionModel(
            user_id=test_user.id,
            name='New Bank',
            location='New City',
            description='A new financial institution'
        )
        institution.save()

        assert institution.id is not None
        assert institution.user_id == test_user.id
        assert institution.name == 'New Bank'
        assert institution.location == 'New City'
        assert institution.description == 'A new financial institution'
        assert institution.created_at is not None
        assert institution.updated_at is not None

    def test_institution_to_dict(self, test_institution):
        """Test institution serialization to dictionary"""
        inst_dict = test_institution.to_dict()

        assert inst_dict['id'] == test_institution.id
        assert inst_dict['user_id'] == test_institution.user_id
        assert inst_dict['name'] == test_institution.name
        assert inst_dict['location'] == test_institution.location
        assert inst_dict['description'] == test_institution.description
        assert 'created_at' in inst_dict
        assert 'updated_at' in inst_dict

    def test_institution_repr(self, test_institution):
        """Test institution string representation"""
        assert repr(test_institution) == f'<Institution {test_institution.name!r}>'

    def test_institution_delete(self, session, test_user):
        """Test deleting an institution"""
        institution = InstitutionModel(
            user_id=test_user.id,
            name='Delete Me Bank',
            location='Nowhere',
            description='Test description'
        )
        institution.save()
        inst_id = institution.id

        # Verify institution exists
        assert InstitutionModel.query.get(inst_id) is not None

        # Delete institution
        institution.delete()

        # Verify institution is deleted
        assert InstitutionModel.query.get(inst_id) is None

    def test_institution_user_relationship(self, test_institution, test_user):
        """Test relationship between institution and user"""
        assert test_institution.user_id == test_user.id

    def test_institution_query_by_user(self, test_institution, test_user):
        """Test querying institutions by user"""
        institutions = InstitutionModel.query.filter_by(user_id=test_user.id).all()

        assert len(institutions) >= 1
        assert test_institution in institutions


class TestInstitutionAccountModel:
    """Test InstitutionAccount model functionality"""

    def test_account_creation(self, session, test_user, test_institution):
        """Test creating a new account"""
        account = InstitutionAccountModel(
            institution_id=test_institution.id,
            user_id=test_user.id,
            name='New Savings',
            number='987654321',
            status='active',
            balance=5000.00,
            starting_balance=3000.00,
            account_type='savings',
            account_class='asset'
        )
        account.save()

        assert account.id is not None
        assert account.institution_id == test_institution.id
        assert account.user_id == test_user.id
        assert account.name == 'New Savings'
        assert account.number == '987654321'
        assert account.status == 'active'
        assert account.balance == 5000.00
        assert account.starting_balance == 3000.00
        assert account.account_type == 'savings'
        assert account.account_class == 'asset'
        assert account.created_at is not None
        assert account.updated_at is not None

    def test_account_types(self, session, test_user, test_institution):
        """Test different account types"""
        account_types = ['checking', 'savings', 'credit', 'loan', 'investment', 'other']

        for acc_type in account_types:
            account = InstitutionAccountModel(
                institution_id=test_institution.id,
                user_id=test_user.id,
                name=f'Test {acc_type}',
                status='active',
                balance=0.0,
                starting_balance=0.0,
                account_type=acc_type,
                account_class='asset' if acc_type != 'credit' else 'liability',
                number='000000'
            )
            account.save()
            assert account.account_type == acc_type

    def test_account_classes(self, session, test_user, test_institution):
        """Test account classes (asset vs liability)"""
        # Asset account
        asset_account = InstitutionAccountModel(
            institution_id=test_institution.id,
            user_id=test_user.id,
            name='Asset Account',
            status='active',
            balance=0.0,
            starting_balance=0.0,
            account_type='checking',
            account_class='asset',
            number='000000'
        )
        asset_account.save()
        assert asset_account.account_class == 'asset'

        # Liability account
        liability_account = InstitutionAccountModel(
            institution_id=test_institution.id,
            user_id=test_user.id,
            name='Credit Card',
            status='active',
            balance=0.0,
            starting_balance=0.0,
            account_type='credit',
            account_class='liability',
            number='000000'
        )
        liability_account.save()
        assert liability_account.account_class == 'liability'

    def test_account_status(self, session, test_user, test_institution):
        """Test account status (active/inactive)"""
        # Active account
        active = InstitutionAccountModel(
            institution_id=test_institution.id,
            user_id=test_user.id,
            name='Active Account',
            status='active',
            balance=0.0,
            starting_balance=0.0,
            account_type='checking',
            account_class='asset',
            number='000000'
        )
        active.save()
        assert active.status == 'active'

        # Inactive account
        inactive = InstitutionAccountModel(
            institution_id=test_institution.id,
            user_id=test_user.id,
            name='Closed Account',
            status='inactive',
            balance=0.0,
            starting_balance=0.0,
            account_type='checking',
            account_class='asset',
            number='000000'
        )
        inactive.save()
        assert inactive.status == 'inactive'

    def test_account_to_dict(self, test_account):
        """Test account serialization to dictionary"""
        acc_dict = test_account.to_dict()

        assert acc_dict['id'] == test_account.id
        assert acc_dict['institution_id'] == test_account.institution_id
        assert acc_dict['user_id'] == test_account.user_id
        assert acc_dict['name'] == test_account.name
        assert acc_dict['number'] == test_account.number
        assert acc_dict['status'] == test_account.status
        assert acc_dict['balance'] == test_account.balance
        assert acc_dict['starting_balance'] == test_account.starting_balance
        assert acc_dict['account_type'] == test_account.account_type
        assert acc_dict['account_class'] == test_account.account_class
        assert 'institution' in acc_dict
        assert 'created_at' in acc_dict
        assert 'updated_at' in acc_dict

    def test_account_repr(self, test_account):
        """Test account string representation"""
        assert repr(test_account) == f'<Account {test_account.name!r}>'

    def test_account_institution_relationship(self, test_account, test_institution):
        """Test relationship between account and institution"""
        assert test_account.institution_id == test_institution.id
        assert test_account.institution.id == test_institution.id
        assert test_account.institution.name == test_institution.name

    def test_account_delete(self, session, test_user, test_institution):
        """Test deleting an account"""
        account = InstitutionAccountModel(
            institution_id=test_institution.id,
            user_id=test_user.id,
            name='Delete Me',
            status='active',
            balance=0.0,
            starting_balance=0.0,
            account_type='checking',
            account_class='asset',
            number='000000'
        )
        account.save()
        acc_id = account.id

        # Verify account exists
        assert InstitutionAccountModel.query.get(acc_id) is not None

        # Delete account
        account.delete()

        # Verify account is deleted
        assert InstitutionAccountModel.query.get(acc_id) is None

    def test_account_query_by_institution(self, test_account, test_institution):
        """Test querying accounts by institution"""
        accounts = InstitutionAccountModel.query.filter_by(
            institution_id=test_institution.id
        ).all()

        assert len(accounts) >= 1
        assert test_account in accounts

    def test_account_query_by_user(self, test_account, test_user):
        """Test querying accounts by user"""
        accounts = InstitutionAccountModel.query.filter_by(user_id=test_user.id).all()

        assert len(accounts) >= 1
        assert test_account in accounts

    def test_account_balance_calculations(self, test_account):
        """Test balance tracking"""
        assert test_account.starting_balance == 500.00
        assert test_account.balance == 1000.00
        # Balance increase
        assert test_account.balance > test_account.starting_balance
