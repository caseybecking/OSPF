from flask import g, request, jsonify, make_response, session
from flask_restx import Resource, fields
from api.institution_account.models import InstitutionAccountModel
from api.transaction.models import TransactionModel

institution_account_model = g.api.model('InstitutionAccount', {
    'institution_id': fields.String(required=True, description='Institution ID'),
    'user_id': fields.String(required=True, description='User ID'),
    'name': fields.String(required=True, description='Account Name'),
    'number': fields.String(required=True, description='Account Number'),
    'status': fields.String(enum=['active', 'inactive'], required=True, description='Account Status'),
    'balance': fields.Float(required=True, description='Account Balance'),
    'starting_balance': fields.Float(required=False, description='Starting Balance'),
    'account_type': fields.String(enum=['checking', 'savings', 'credit', 'loan', 'investment', 'other'], required=True, description='Account Type'),
    'account_class': fields.String(enum=['asset', 'liability'], required=True, description='Account Class')
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
        starting_balance = data.get('starting_balance')
        account_type = data.get('account_type')
        account_class = data.get('account_class')

        new_account = InstitutionAccountModel(
            institution_id=institution_id,
            user_id=user_id,
            name=name,
            number=number,
            status=status,
            balance=balance,
            starting_balance=starting_balance,
            account_type=account_type,
            account_class=account_class
        )
        new_account.save()

        return make_response(jsonify({'message': 'Account created successfully'}), 201)

    def get(self):
        accounts = InstitutionAccountModel.query.all()
        _accounts = [account.to_dict() for account in accounts]
        return make_response(jsonify({'accounts': _accounts}), 200)
    
@g.api.route('/institution/account/update_balance')
class InstitutionAccountUpdateBalance(Resource):
    def get(self):
        __accounts = []
        user_id = session.get('_user_id')
        accounts = InstitutionAccountModel.query.all()
        for account in accounts:
            # get the current account balance
            starting_balance = account.starting_balance
            # get all the transactions for that account
            transactions = TransactionModel.query.filter_by(account_id=account.id, user_id=user_id).all()
            # sum up all the transactions for the account
            total = sum([transaction.amount for transaction in transactions])
            # update the account balance
            new_account_balance = starting_balance + total
            # we need to offset the transactions
            print(f'Updating account {account.name} balance from {account.balance} to {new_account_balance}')
            