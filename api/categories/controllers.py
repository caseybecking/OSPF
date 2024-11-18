from flask import g, request, jsonify, make_response
from flask_restx import Resource, fields
from api.categories.models import CategoriesModel

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