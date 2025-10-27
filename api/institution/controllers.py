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

        # Validate required fields (only user_id and name are required)
        if not all([user_id, name]):
            return make_response(jsonify({
                'message': 'user_id and name are required'
            }), 400)

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
        _isntitutions = [institution.to_dict() for institution in institutions]
        return make_response(jsonify({'institutions': _isntitutions}), 200)

@g.api.route('/institution/<string:id>')
class InstitutionDetail(Resource):
    def get(self, id):
        """Get a single institution by ID"""
        institution = InstitutionModel.query.get(id)
        if not institution:
            return make_response(jsonify({'message': 'Institution not found'}), 404)

        return make_response(jsonify({'institution': institution.to_dict()}), 200)

    @g.api.expect(institution_model)
    def put(self, id):
        """Update an institution"""
        institution = InstitutionModel.query.get(id)
        if not institution:
            return make_response(jsonify({'message': 'Institution not found'}), 404)

        data = request.json

        # Update fields if provided
        if 'name' in data:
            institution.name = data['name']
        if 'location' in data:
            institution.location = data['location']
        if 'description' in data:
            institution.description = data['description']

        institution.save()

        return make_response(jsonify({'message': 'Institution updated successfully', 'institution': institution.to_dict()}), 200)

    def delete(self, id):
        """Delete an institution"""
        from api.institution_account.models import InstitutionAccountModel

        institution = InstitutionModel.query.get(id)
        if not institution:
            return make_response(jsonify({'message': 'Institution not found'}), 404)

        # Check if there are any accounts linked to this institution
        linked_accounts = InstitutionAccountModel.query.filter_by(institution_id=id).count()
        if linked_accounts > 0:
            return make_response(jsonify({
                'message': f'Cannot delete institution. There are {linked_accounts} account(s) linked to it. Please delete or reassign the accounts first.'
            }), 400)

        institution.delete()

        return make_response(jsonify({'message': 'Institution deleted successfully'}), 200)
