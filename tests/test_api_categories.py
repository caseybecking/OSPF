"""Tests for Categories API endpoints"""
import json
import pytest


class TestCategoriesTypeAPI:
    """Test categories type API endpoints"""

    def test_create_category_type(self, client, test_user):
        """Test creating a category type via API"""
        response = client.post('/api/categories_type', json={
            'user_id': test_user.id,
            'name': 'Income'
        })

        assert response.status_code == 201
        data = json.loads(response.data)
        # assert data['message'] == 'Category Type created successfully'
        assert data['message'] == 'Categories Type created successfully'

    def test_list_category_types(self, client, test_categories_type):
        """Test listing all category types"""
        response = client.get('/api/categories_type')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'categories_type' in data
        assert len(data['categories_type']) >= 1

        # Verify test category type is in list
        type_ids = [ct['id'] for ct in data['categories_type']]
        assert test_categories_type.id in type_ids

    def test_create_multiple_types(self, client, test_user):
        """Test creating multiple category types"""
        types = ['Income', 'Expense', 'Transfer']

        for type_name in types:
            response = client.post('/api/categories_type', json={
                'user_id': test_user.id,
                'name': type_name
            })
            assert response.status_code == 201


class TestCategoriesGroupAPI:
    """Test categories group API endpoints"""

    def test_create_category_group(self, client, test_user):
        """Test creating a category group via API"""
        response = client.post('/api/categories_group', json={
            'user_id': test_user.id,
            'name': 'Utilities'
        })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Categories Group created successfully'

    def test_list_category_groups(self, client, test_categories_group):
        """Test listing all category groups"""
        response = client.get('/api/categories_group')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'categories_group' in data
        assert len(data['categories_group']) >= 1

        # Verify test category group is in list
        group_ids = [cg['id'] for cg in data['categories_group']]
        assert test_categories_group.id in group_ids

    def test_create_multiple_groups(self, client, test_user):
        """Test creating multiple category groups"""
        groups = ['Groceries', 'Utilities', 'Entertainment', 'Transportation']

        for group_name in groups:
            response = client.post('/api/categories_group', json={
                'user_id': test_user.id,
                'name': group_name
            })
            assert response.status_code == 201


class TestCategoriesAPI:
    """Test categories API endpoints"""

    def test_create_category(self, client, test_user, test_categories_type, test_categories_group):
        """Test creating a category via API"""
        response = client.post('/api/categories', json={
            'user_id': test_user.id,
            'categories_group_id': test_categories_group.id,
            'categories_type_id': test_categories_type.id,
            'name': 'Target'
        })

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['message'] == 'Categories created successfully'

    def test_list_categories(self, client, test_category):
        """Test listing all categories"""
        response = client.get('/api/categories')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'categories' in data
        assert len(data['categories']) >= 1

        # Verify test category is in list
        cat_ids = [c['id'] for c in data['categories']]
        assert test_category.id in cat_ids

    def test_category_includes_hierarchy(self, client, test_category):
        """Test that category list includes type and group data"""
        response = client.get('/api/categories')

        assert response.status_code == 200
        data = json.loads(response.data)

        # Find our test category
        test_cat_data = None
        for cat in data['categories']:
            if cat['id'] == test_category.id:
                test_cat_data = cat
                break

        assert test_cat_data is not None
        assert 'categories_type' in test_cat_data
        assert 'categories_group' in test_cat_data
        assert test_cat_data['categories_type']['id'] == test_category.categories_type_id
        assert test_cat_data['categories_group']['id'] == test_category.categories_group_id

    def test_create_full_hierarchy_via_api(self, client, test_user):
        """Test creating a complete category hierarchy via API"""
        # Create Type
        type_response = client.post('/api/categories_type', json={
            'user_id': test_user.id,
            'name': 'Income'
        })
        assert type_response.status_code == 201

        # Get the created type (from list since we don't have the ID yet)
        types_response = client.get('/api/categories_type')
        types_data = json.loads(types_response.data)
        income_type = next(
            (t for t in types_data['categories_type'] if t['name'] == 'Income'),
            None
        )
        assert income_type is not None

        # Create Group
        group_response = client.post('/api/categories_group', json={
            'user_id': test_user.id,
            'name': 'Salary'
        })
        assert group_response.status_code == 201

        # Get the created group
        groups_response = client.get('/api/categories_group')
        groups_data = json.loads(groups_response.data)
        salary_group = next(
            (g for g in groups_data['categories_group'] if g['name'] == 'Salary'),
            None
        )
        assert salary_group is not None

        # Create Category
        cat_response = client.post('/api/categories', json={
            'user_id': test_user.id,
            'categories_group_id': salary_group['id'],
            'categories_type_id': income_type['id'],
            'name': 'Monthly Salary'
        })
        assert cat_response.status_code == 201

    def test_create_multiple_categories_in_group(self, client, test_user, test_categories_type, test_categories_group):
        """Test creating multiple categories within the same group"""
        stores = ['Walmart', 'Target', 'Costco', 'Kroger']

        for store in stores:
            response = client.post('/api/categories', json={
                'user_id': test_user.id,
                'categories_group_id': test_categories_group.id,
                'categories_type_id': test_categories_type.id,
                'name': store
            })
            assert response.status_code == 201

        # Verify all were created
        categories_response = client.get('/api/categories')
        categories_data = json.loads(categories_response.data)

        # Count categories in our test group
        group_categories = [
            c for c in categories_data['categories']
            if c['categories_group_id'] == test_categories_group.id
        ]
        assert len(group_categories) >= len(stores)

    def test_create_category_missing_required_fields(self, client, test_user):
        """Test creating category with missing required fields"""
        response = client.post('/api/categories', json={
            'user_id': test_user.id,
            'name': 'Incomplete Category'
            # Missing categories_group_id and categories_type_id
        })

        assert response.status_code in [400, 500]

    def test_create_category_invalid_references(self, client, test_user):
        """Test creating category with invalid group/type references"""
        response = client.post('/api/categories', json={
            'user_id': test_user.id,
            'categories_group_id': 'invalid-id',
            'categories_type_id': 'invalid-id',
            'name': 'Invalid Category'
        })

        assert response.status_code in [400, 500]
