from flask import g, request, jsonify, make_response
from flask_restx import Resource, fields
from api.categories_type.models import CategoriesTypeModel

categories_type_model = g.api.model('CategoriesType', {
    'user_id': fields.String(required=True, description='User ID'),
    'name': fields.String(required=True, description='Name')
})

@g.api.route('/categories_type')
class CategoriesType(Resource):
    @g.api.expect(categories_type_model)
    def post(self):
        data = request.json
        user_id = data.get('user_id')
        name = data.get('name')

        new_categories_type = CategoriesTypeModel(
            user_id=user_id,
            name=name
        )
        new_categories_type.save()

        return make_response(jsonify({'message': 'Categories Type created successfully'}), 201)

    def get(self):
        categories_type = CategoriesTypeModel.query.all()
        _categories_type = []
        _categories_type.append([category_type.to_dict() for category_type in categories_type])
        return make_response(jsonify({'categories_type': _categories_type}), 200)