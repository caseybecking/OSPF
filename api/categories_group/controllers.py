from flask import g, request, jsonify, make_response
from flask_restx import Resource, fields
from api.categories_group.models import CategoriesGroupModel

categories_group_model = g.api.model('CategoriesGroup', {
    'user_id': fields.String(required=True, description='User ID'),
    'name': fields.String(required=True, description='Name')
})

@g.api.route('/categories_group')
class CategoriesGroup(Resource):
    @g.api.expect(categories_group_model)
    def post(self):
        data = request.json
        user_id = data.get('user_id')
        name = data.get('name')

        new_categories_group = CategoriesGroupModel(
            user_id=user_id,
            name=name
        )
        new_categories_group.save()

        return make_response(jsonify({'message': 'Categories Group created successfully'}), 201)

    def get(self):
        categories_group = CategoriesGroupModel.query.all()
        _categories_group = [category_group.to_dict() for category_group in categories_group]
        return make_response(jsonify({'categories_group': _categories_group}), 200)
