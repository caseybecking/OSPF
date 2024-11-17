from flask import g, request, jsonify, make_response
from flask_restx import Resource, fields
from api.institution_account.models import InstitutionAccountModel

institution_account_model = g.api.model('InstitutionAccount', {
    'institution_id': fields.String(required=True, description='Institution ID'),
    'user_id': fields.String(required=True, description='User ID'),
    'name': fields.String(required=True, description='Account Name'),
    'number': fields.String(required=True, description='Account Number'),
    'status': fields.String(enum=['active', 'inactive'], required=True, description='Account Status'),
    'balance': fields.Float(required=True, description='Account Balance')
})

@g.api.route('/institution/account')
class InstitutionAccount(Resource):
    @g.api.expect(institution_account_model)
    def post(self):
        data = request.json
        institution_id = data.get('institution_id')
        user_id = data.get('user_id')
        name = data.get('name')
        number = data.get('number')
        status = data.get('status')
        balance = data.get('balance')

        new_account = InstitutionAccountModel(
            institution_id=institution_id,
            user_id=user_id,
            name=name,
            number=number,
            status=status,
            balance=balance
        )
        new_account.save()

        return make_response(jsonify({'message': 'Account created successfully'}), 201)

    def get(self):
        accounts = InstitutionAccountModel.query.all()
        _accounts = [account.to_dict() for account in accounts]
        return make_response(jsonify({'accounts': _accounts}), 200)
