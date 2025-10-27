import os
import csv
from flask import g, request, jsonify, make_response, session
from flask_restx import Resource, fields
from werkzeug.utils import secure_filename
from app.config import Config
from api.categories.models import CategoriesModel
from api.categories_group.models import CategoriesGroupModel
from api.categories_type.models import CategoriesTypeModel

categories_model = g.api.model('Categories', {
    'user_id': fields.String(required=True, description='User ID'),
    'categories_group_id': fields.String(required=True, description='Categories Group ID'),
    'categories_type_id': fields.String(required=True, description='Categories Type ID'),
    'name': fields.String(required=True, description='Name')
})

@g.api.route('/categories')
class Categories(Resource):
    @g.api.expect(categories_model)
    def post(self):
        data = request.json
        user_id = data.get('user_id')
        categories_group_id = data.get('categories_group_id')
        categories_type_id = data.get('categories_type_id')
        name = data.get('name')

        # Validate all required fields are present
        if not all([user_id, categories_group_id, categories_type_id, name]):
            return make_response(jsonify({
                'message': 'All fields are required'
            }), 400)

        # Validate that referenced records exist
        from api.categories_group.models import CategoriesGroupModel
        from api.categories_type.models import CategoriesTypeModel

        group = CategoriesGroupModel.query.get(categories_group_id)
        if not group:
            return make_response(jsonify({
                'message': 'Invalid categories_group_id'
            }), 400)

        cat_type = CategoriesTypeModel.query.get(categories_type_id)
        if not cat_type:
            return make_response(jsonify({
                'message': 'Invalid categories_type_id'
            }), 400)

        new_categories = CategoriesModel(
            user_id=user_id,
            categories_group_id=categories_group_id,
            categories_type_id=categories_type_id,
            name=name
        )
        new_categories.save()

        return make_response(jsonify({'message': 'Categories created successfully'}), 201)

    def get(self):
        categories = CategoriesModel.query.all()
        _categories = [category.to_dict() for category in categories]
        return make_response(jsonify({'categories': _categories}), 200)


@g.api.route('/categories/csv_import')
class CategoriesCSVImport(Resource):
    """Import categories, groups, and types from CSV file"""

    def post(self):
        """
        Import categories from CSV file

        Expected CSV format:
        categories,categories_group,categories_type
        Groceries,Food & Dining,Expense
        Salary,Income,Income
        """
        user_id = session.get('_user_id')

        if not user_id:
            return make_response(jsonify({'message': 'User not authenticated'}), 401)

        if 'file' not in request.files:
            return make_response(jsonify({'message': 'No file provided'}), 400)

        file = request.files['file']

        if file.filename == '':
            return make_response(jsonify({'message': 'No file selected'}), 400)

        if not file.filename.endswith('.csv'):
            return make_response(jsonify({'message': 'File must be a CSV'}), 400)

        try:
            # Save the file
            upload_folder = Config.UPLOAD_FOLDER
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            # Process the CSV
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                csvreader = csv.DictReader(csvfile)

                # Validate headers
                required_headers = ['categories', 'categories_group', 'categories_type']
                if not all(header in csvreader.fieldnames for header in required_headers):
                    return make_response(jsonify({
                        'message': f'CSV must have headers: {", ".join(required_headers)}'
                    }), 400)

                created_types = {}
                created_groups = {}
                created_categories = 0
                skipped_categories = 0

                for row in csvreader:
                    category_name = row['categories'].strip()
                    group_name = row['categories_group'].strip()
                    type_name = row['categories_type'].strip()

                    if not all([category_name, group_name, type_name]):
                        skipped_categories += 1
                        continue

                    # Get or create type
                    if type_name not in created_types:
                        cat_type = CategoriesTypeModel.query.filter_by(
                            name=type_name,
                            user_id=user_id
                        ).first()

                        if not cat_type:
                            cat_type = CategoriesTypeModel(
                                user_id=user_id,
                                name=type_name
                            )
                            cat_type.save()

                        created_types[type_name] = cat_type.id

                    # Get or create group
                    if group_name not in created_groups:
                        cat_group = CategoriesGroupModel.query.filter_by(
                            name=group_name,
                            user_id=user_id
                        ).first()

                        if not cat_group:
                            cat_group = CategoriesGroupModel(
                                user_id=user_id,
                                name=group_name
                            )
                            cat_group.save()

                        created_groups[group_name] = cat_group.id

                    # Check if category already exists
                    existing_category = CategoriesModel.query.filter_by(
                        name=category_name,
                        categories_group_id=created_groups[group_name],
                        categories_type_id=created_types[type_name],
                        user_id=user_id
                    ).first()

                    if existing_category:
                        skipped_categories += 1
                        continue

                    # Create category
                    new_category = CategoriesModel(
                        user_id=user_id,
                        categories_group_id=created_groups[group_name],
                        categories_type_id=created_types[type_name],
                        name=category_name
                    )
                    new_category.save()
                    created_categories += 1

            # Clean up the uploaded file
            os.remove(file_path)

            return make_response(jsonify({
                'message': 'Categories imported successfully',
                'categories_created': created_categories,
                'categories_skipped': skipped_categories,
                'types_processed': len(created_types),
                'groups_processed': len(created_groups)
            }), 201)

        except Exception as e:
            return make_response(jsonify({
                'message': f'Error processing CSV: {str(e)}'
            }), 500)


@g.api.route('/categories/<string:id>')
class CategoriesDetail(Resource):
    def get(self, id):
        """Get a single category by ID"""
        category = CategoriesModel.query.get(id)
        if not category:
            return make_response(jsonify({'message': 'Category not found'}), 404)

        return make_response(jsonify({'category': category.to_dict()}), 200)

    @g.api.expect(categories_model)
    def put(self, id):
        """Update a category"""
        category = CategoriesModel.query.get(id)
        if not category:
            return make_response(jsonify({'message': 'Category not found'}), 404)

        data = request.json

        # Validate foreign keys if provided
        if 'categories_group_id' in data:
            group = CategoriesGroupModel.query.get(data['categories_group_id'])
            if not group:
                return make_response(jsonify({
                    'message': 'Invalid categories_group_id'
                }), 400)

        if 'categories_type_id' in data:
            cat_type = CategoriesTypeModel.query.get(data['categories_type_id'])
            if not cat_type:
                return make_response(jsonify({
                    'message': 'Invalid categories_type_id'
                }), 400)

        # Update fields if provided
        if 'name' in data:
            category.name = data['name']
        if 'categories_group_id' in data:
            category.categories_group_id = data['categories_group_id']
        if 'categories_type_id' in data:
            category.categories_type_id = data['categories_type_id']

        category.save()

        return make_response(jsonify({'message': 'Category updated successfully', 'category': category.to_dict()}), 200)

    def delete(self, id):
        """Delete a category"""
        from api.transaction.models import TransactionModel

        category = CategoriesModel.query.get(id)
        if not category:
            return make_response(jsonify({'message': 'Category not found'}), 404)

        # Check if there are any transactions linked to this category
        linked_transactions = TransactionModel.query.filter_by(categories_id=id).count()
        if linked_transactions > 0:
            return make_response(jsonify({
                'message': f'Cannot delete category. There are {linked_transactions} transaction(s) linked to it. Please delete or reassign the transactions first.'
            }), 400)

        category.delete()

        return make_response(jsonify({'message': 'Category deleted successfully'}), 200)
