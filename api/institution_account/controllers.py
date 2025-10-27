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

        # Validate enum fields (only if provided)
        valid_statuses = ['active', 'inactive']
        valid_types = ['checking', 'savings', 'credit', 'loan', 'investment', 'other']
        valid_classes = ['asset', 'liability']

        if status and status not in valid_statuses:
            return make_response(jsonify({
                'message': f'Invalid status. Must be one of: {valid_statuses}'
            }), 400)

        if account_type and account_type not in valid_types:
            return make_response(jsonify({
                'message': f'Invalid account type. Must be one of: {valid_types}'
            }), 400)

        if account_class and account_class not in valid_classes:
            return make_response(jsonify({
                'message': f'Invalid account class. Must be one of: {valid_classes}'
            }), 400)

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
            account.balance = new_account_balance
            account.save()
            __accounts.append(account.to_dict())
        return make_response(jsonify({'accounts': __accounts}), 200)

@g.api.route('/institution/account/<string:id>')
class InstitutionAccountDetail(Resource):
    def get(self, id):
        """Get a single account by ID"""
        account = InstitutionAccountModel.query.get(id)
        if not account:
            return make_response(jsonify({'message': 'Account not found'}), 404)

        return make_response(jsonify({'account': account.to_dict()}), 200)

    @g.api.expect(institution_account_model)
    def put(self, id):
        """Update an account"""
        account = InstitutionAccountModel.query.get(id)
        if not account:
            return make_response(jsonify({'message': 'Account not found'}), 404)

        data = request.json

        # Validate enum fields if provided
        valid_statuses = ['active', 'inactive']
        valid_types = ['checking', 'savings', 'credit', 'loan', 'investment', 'other']
        valid_classes = ['asset', 'liability']

        if 'status' in data and data['status'] and data['status'] not in valid_statuses:
            return make_response(jsonify({
                'message': f'Invalid status. Must be one of: {valid_statuses}'
            }), 400)

        if 'account_type' in data and data['account_type'] and data['account_type'] not in valid_types:
            return make_response(jsonify({
                'message': f'Invalid account type. Must be one of: {valid_types}'
            }), 400)

        if 'account_class' in data and data['account_class'] and data['account_class'] not in valid_classes:
            return make_response(jsonify({
                'message': f'Invalid account class. Must be one of: {valid_classes}'
            }), 400)

        # Update fields if provided
        if 'name' in data:
            account.name = data['name']
        if 'number' in data:
            account.number = data['number']
        if 'status' in data:
            account.status = data['status']
        if 'balance' in data:
            account.balance = data['balance']
        if 'starting_balance' in data:
            account.starting_balance = data['starting_balance']
        if 'account_type' in data:
            account.account_type = data['account_type']
        if 'account_class' in data:
            account.account_class = data['account_class']
        if 'institution_id' in data:
            account.institution_id = data['institution_id']

        account.save()

        return make_response(jsonify({'message': 'Account updated successfully', 'account': account.to_dict()}), 200)

    def delete(self, id):
        """Delete an account"""
        account = InstitutionAccountModel.query.get(id)
        if not account:
            return make_response(jsonify({'message': 'Account not found'}), 404)

        # Check if there are any transactions linked to this account
        linked_transactions = TransactionModel.query.filter_by(account_id=id).count()
        if linked_transactions > 0:
            return make_response(jsonify({
                'message': f'Cannot delete account. There are {linked_transactions} transaction(s) linked to it. Please delete the transactions first.'
            }), 400)

        account.delete()

        return make_response(jsonify({'message': 'Account deleted successfully'}), 200)