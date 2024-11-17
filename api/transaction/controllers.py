from flask import g, request, jsonify, make_response
from flask_restx import Resource, fields
from api.transaction.models import TransactionModel

transaction_model = g.api.model('Transaction', {
    'user_id': fields.String(required=True, description='User ID'),
    'categories_id': fields.String(required=True, description='Categories ID'),
    'account_id': fields.String(required=True, description='Account ID'),
    'amount': fields.Float(required=True, description='Amount'),
    'transaction_type': fields.String(required=True, description='Transaction Type')
})

@g.api.route('/transaction')
class Transaction(Resource):
    @g.api.expect(transaction_model)
    def post(self):
        data = request.json
        user_id = data.get('user_id')
        categories_id = data.get('categories_id')
        account_id = data.get('account_id')
        amount = data.get('amount')
        transaction_type = data.get('transaction_type')

        new_transaction = TransactionModel(
            user_id=user_id,
            categories_id=categories_id,
            account_id=account_id,
            amount=amount,
            transaction_type=transaction_type
        )
        new_transaction.save()

        return make_response(jsonify({'message': 'Transaction created successfully'}), 201)

    def get(self):
        transactions = TransactionModel.query.all()
        _transactions = []
        _transactions.append([transaction.to_dict() for transaction in transactions])
        return make_response(jsonify({'transactions': _transactions}), 200)
