from flask import g, request, jsonify, make_response
from flask_restx import Resource, fields
from api.institution.models import InstitutionModel

institution_model = g.api.model('Institution', {
    'user_id': fields.String(requierd=True, description='User ID'),
    'name': fields.String(required=True, description='Institution Name'),
    'location': fields.String(description='Location'),
    'description': fields.String(description='Description')
})

@g.api.route('/institution')
class Institution(Resource):
    @g.api.expect(institution_model)
    def post(self):
        data = request.json
        user_id = data.get('user_id')
        name = data.get('name')
        location = data.get('location')
        description = data.get('description')

        new_institution = InstitutionModel(
            user_id=user_id,
            name=name,
            location=location,
            description=description
        )
        new_institution.save()

        return make_response(jsonify({'message': 'Institution created successfully'}), 201)

    def get(self):
        institutions = InstitutionModel.query.all()
        _isntitutions = []
        _isntitutions.append([institution.to_dict() for institution in institutions])
        return make_response(jsonify({'institutions': _isntitutions}), 200)
