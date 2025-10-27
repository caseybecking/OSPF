"""Tests for Category models (Type, Group, and Categories)"""
import pytest
from api.categories_type.models import CategoriesTypeModel
from api.categories_group.models import CategoriesGroupModel
from api.categories.models import CategoriesModel


class TestCategoriesTypeModel:
    """Test CategoriesType model functionality"""

    def test_category_type_creation(self, session, test_user):
        """Test creating a new category type"""
        cat_type = CategoriesTypeModel(
            user_id=test_user.id,
            name='Income'
        )
        cat_type.save()

        assert cat_type.id is not None
        assert cat_type.user_id == test_user.id
        assert cat_type.name == 'Income'
        assert cat_type.created_at is not None
        assert cat_type.updated_at is not None

    def test_category_type_common_types(self, session, test_user):
        """Test creating common category types"""
        common_types = ['Income', 'Expense', 'Transfer']

        for type_name in common_types:
            cat_type = CategoriesTypeModel(
                user_id=test_user.id,
                name=type_name
            )
            cat_type.save()
            assert cat_type.name == type_name

    def test_category_type_to_dict(self, test_categories_type):
        """Test category type serialization to dictionary"""
        type_dict = test_categories_type.to_dict()

        assert type_dict['id'] == test_categories_type.id
        assert type_dict['user_id'] == test_categories_type.user_id
        assert type_dict['name'] == test_categories_type.name
        assert 'created_at' in type_dict
        assert 'updated_at' in type_dict

    def test_category_type_repr(self, test_categories_type):
        """Test category type string representation"""
        assert repr(test_categories_type) == f'<CategoriesType {test_categories_type.name!r}>'

    def test_category_type_delete(self, session, test_user):
        """Test deleting a category type"""
        cat_type = CategoriesTypeModel(
            user_id=test_user.id,
            name='DeleteMe'
        )
        cat_type.save()
        type_id = cat_type.id

        assert CategoriesTypeModel.query.get(type_id) is not None
        cat_type.delete()
        assert CategoriesTypeModel.query.get(type_id) is None


class TestCategoriesGroupModel:
    """Test CategoriesGroup model functionality"""

    def test_category_group_creation(self, session, test_user):
        """Test creating a new category group"""
        cat_group = CategoriesGroupModel(
            user_id=test_user.id,
            name='Utilities'
        )
        cat_group.save()

        assert cat_group.id is not None
        assert cat_group.user_id == test_user.id
        assert cat_group.name == 'Utilities'
        assert cat_group.created_at is not None
        assert cat_group.updated_at is not None

    def test_category_group_common_groups(self, session, test_user):
        """Test creating common category groups"""
        common_groups = [
            'Groceries', 'Utilities', 'Entertainment',
            'Transportation', 'Healthcare', 'Housing'
        ]

        for group_name in common_groups:
            cat_group = CategoriesGroupModel(
                user_id=test_user.id,
                name=group_name
            )
            cat_group.save()
            assert cat_group.name == group_name

    def test_category_group_to_dict(self, test_categories_group):
        """Test category group serialization to dictionary"""
        group_dict = test_categories_group.to_dict()

        assert group_dict['id'] == test_categories_group.id
        assert group_dict['user_id'] == test_categories_group.user_id
        assert group_dict['name'] == test_categories_group.name
        assert 'created_at' in group_dict
        assert 'updated_at' in group_dict

    def test_category_group_repr(self, test_categories_group):
        """Test category group string representation"""
        assert repr(test_categories_group) == f'<CategoriesGroup {test_categories_group.name!r}>'

    def test_category_group_delete(self, session, test_user):
        """Test deleting a category group"""
        cat_group = CategoriesGroupModel(
            user_id=test_user.id,
            name='DeleteMe'
        )
        cat_group.save()
        group_id = cat_group.id

        assert CategoriesGroupModel.query.get(group_id) is not None
        cat_group.delete()
        assert CategoriesGroupModel.query.get(group_id) is None


class TestCategoriesModel:
    """Test Categories model functionality"""

    def test_category_creation(self, session, test_user, test_categories_type, test_categories_group):
        """Test creating a new category"""
        category = CategoriesModel(
            user_id=test_user.id,
            categories_group_id=test_categories_group.id,
            categories_type_id=test_categories_type.id,
            name='Target'
        )
        category.save()

        assert category.id is not None
        assert category.user_id == test_user.id
        assert category.categories_group_id == test_categories_group.id
        assert category.categories_type_id == test_categories_type.id
        assert category.name == 'Target'
        assert category.created_at is not None
        assert category.updated_at is not None

    def test_category_hierarchy(self, test_category, test_categories_type, test_categories_group):
        """Test category hierarchy relationships"""
        assert test_category.categories_type_id == test_categories_type.id
        assert test_category.categories_group_id == test_categories_group.id

        # Test relationships
        assert test_category.categories_type.id == test_categories_type.id
        assert test_category.categories_group.id == test_categories_group.id

    def test_category_to_dict(self, test_category):
        """Test category serialization to dictionary"""
        cat_dict = test_category.to_dict()

        assert cat_dict['id'] == test_category.id
        assert cat_dict['user_id'] == test_category.user_id
        assert cat_dict['categories_group_id'] == test_category.categories_group_id
        assert cat_dict['categories_type_id'] == test_category.categories_type_id
        assert cat_dict['name'] == test_category.name
        assert 'categories_type' in cat_dict
        assert 'categories_group' in cat_dict
        assert 'created_at' in cat_dict
        assert 'updated_at' in cat_dict

    def test_category_repr(self, test_category):
        """Test category string representation"""
        assert repr(test_category) == f'<Categories {test_category.name!r}>'

    def test_category_delete(self, session, test_user, test_categories_type, test_categories_group):
        """Test deleting a category"""
        category = CategoriesModel(
            user_id=test_user.id,
            categories_group_id=test_categories_group.id,
            categories_type_id=test_categories_type.id,
            name='DeleteMe'
        )
        category.save()
        cat_id = category.id

        assert CategoriesModel.query.get(cat_id) is not None
        category.delete()
        assert CategoriesModel.query.get(cat_id) is None

    def test_category_query_by_type(self, test_category, test_categories_type):
        """Test querying categories by type"""
        categories = CategoriesModel.query.filter_by(
            categories_type_id=test_categories_type.id
        ).all()

        assert len(categories) >= 1
        assert test_category in categories

    def test_category_query_by_group(self, test_category, test_categories_group):
        """Test querying categories by group"""
        categories = CategoriesModel.query.filter_by(
            categories_group_id=test_categories_group.id
        ).all()

        assert len(categories) >= 1
        assert test_category in categories

    def test_category_query_by_user(self, test_category, test_user):
        """Test querying categories by user"""
        categories = CategoriesModel.query.filter_by(user_id=test_user.id).all()

        assert len(categories) >= 1
        assert test_category in categories

    def test_full_category_hierarchy_example(self, session, test_user):
        """Test creating a complete category hierarchy"""
        # Create Type: Income
        income_type = CategoriesTypeModel(
            user_id=test_user.id,
            name='Income'
        )
        income_type.save()

        # Create Group: Salary
        salary_group = CategoriesGroupModel(
            user_id=test_user.id,
            name='Salary'
        )
        salary_group.save()

        # Create Category: Monthly Salary
        monthly_salary = CategoriesModel(
            user_id=test_user.id,
            categories_group_id=salary_group.id,
            categories_type_id=income_type.id,
            name='Monthly Salary'
        )
        monthly_salary.save()

        # Verify hierarchy
        assert monthly_salary.categories_type.name == 'Income'
        assert monthly_salary.categories_group.name == 'Salary'
        assert monthly_salary.name == 'Monthly Salary'

    def test_expense_category_hierarchy(self, session, test_user):
        """Test creating expense category hierarchy"""
        # Type: Expense
        expense_type = CategoriesTypeModel(user_id=test_user.id, name='Expense')
        expense_type.save()

        # Group: Groceries
        groceries_group = CategoriesGroupModel(user_id=test_user.id, name='Groceries')
        groceries_group.save()

        # Categories under Groceries
        stores = ['Walmart', 'Target', 'Costco', 'Whole Foods']
        for store in stores:
            category = CategoriesModel(
                user_id=test_user.id,
                categories_group_id=groceries_group.id,
                categories_type_id=expense_type.id,
                name=store
            )
            category.save()

        # Verify all were created
        grocery_categories = CategoriesModel.query.filter_by(
            categories_group_id=groceries_group.id
        ).all()
        assert len(grocery_categories) == len(stores)
