import os
import csv
from datetime import datetime
from math import ceil
from flask import g, request, jsonify, make_response, session
from flask_restx import Resource, fields
from werkzeug.utils import secure_filename
from app import db
from api.transaction.models import TransactionModel
from api.categories.models import CategoriesModel
from api.institution_account.models import InstitutionAccountModel
from api.institution.models import InstitutionModel

from app.config import Config
from api.helpers import allowed_file, positive_or_negative, clean_dollar_value

transaction_model = g.api.model('Transaction', {
    'user_id': fields.String(required=True, description='User ID'),
    'categories_id': fields.String(required=True, description='Categories ID'),
    'account_id': fields.String(required=True, description='Account ID'),
    'amount': fields.Float(required=True, description='Amount'),
    'transaction_type': fields.String(required=True, description='Transaction Type'),
    'external_id': fields.String(description='External ID'),
    'external_date': fields.DateTime(description='External Date'),
    'description': fields.String(description='Description')
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
        external_id = data.get('external_id')
        external_date = data.get('external_date')
        description = data.get('description')

        new_transaction = TransactionModel(
            user_id=user_id,
            categories_id=categories_id,
            account_id=account_id,
            amount=amount,
            transaction_type=transaction_type,
            external_id=external_id,
            external_date=external_date,
            description=description
        )
        new_transaction.save()

        return make_response(jsonify({'message': 'Transaction created successfully'}), 201)

    def get(self):
        # Extract page and per_page from query parameters, default to page 1, 10 items per page
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=100, type=int)

        # Query with pagination
        transactions_query = TransactionModel.query.paginate(page=page, per_page=per_page, error_out=False)

        # Get the items for the current page
        transactions = transactions_query.items

        # Convert transactions to dictionaries
        _transactions = [transaction.to_dict() for transaction in transactions]

        # Metadata for pagination
        pagination_info = {
            'total': transactions_query.total,  # Total number of items
            'pages': ceil(transactions_query.total / per_page),  # Total number of pages
            'current_page': transactions_query.page,  # Current page number
            'per_page': transactions_query.per_page  # Items per page
        }

        # Return response with pagination metadata
        return make_response(jsonify({'transactions': _transactions, 'pagination': pagination_info}), 200)


@g.api.route('/transaction/csv_import')
class TransactionCSVImport(Resource):
    def post(self):
        user_id = session.get('_user_id')
        if 'file' not in request.files:
            return make_response(jsonify({'message': 'No file'}), 400)

        file = request.files['file']

        if file.filename == '':
            return make_response(jsonify({'message': 'Filename cannot be blank'}), 400)

        if file and allowed_file(file.filename):
            upload_folder = Config.UPLOAD_FOLDER
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            try:
                with open(file_path, newline='') as csvfile:
                    csvreader = csv.reader(csvfile)
                    header = next(csvreader)  # Extract header
                    rows = [row for row in csvreader]

                    for row in rows:
                        row_data = dict(zip(header, row))
                        transaction_exists = self.check_transaction_by_external_id(row_data['Transaction ID'])
                        if transaction_exists:
                            print(f"Transaction {row_data['Transaction ID']} already exists. Skipping...")
                            continue  # Skip processing this row

                        # Ensure category exists or create it
                        category_id = self.ensure_category_exists(row_data['Category'])

                        # Ensure institution exists or create it
                        institution_id = self.ensure_institution_exists(row_data['Institution'])

                        # Ensure account exists or create it
                        account_id = self.ensure_account_exists(row_data['Account'], institution_id)

                        _amount = clean_dollar_value(row_data['Amount'])
                        _transaction_type = positive_or_negative(_amount)

                        dt_object = datetime.strptime(row_data['Date'], "%m/%d/%Y")
                        formatted_timestamp = dt_object.strftime("%Y-%m-%d %H:%M:%S")

                        # Create the transaction
                        self.create_transaction(
                            user_id=user_id,
                            categories_id=category_id,
                            account_id=account_id,
                            amount=_amount,
                            transaction_type=_transaction_type,
                            external_id=row_data['Transaction ID'],
                            external_date=formatted_timestamp,
                            description=row_data.get('Description', None)
                        )
            except Exception as e:
                return make_response(jsonify({'message': str(e)}), 400)
        else:
            return make_response(jsonify({'message': 'Invalid file type'}), 400)

        return make_response(jsonify({'message': 'Transactions imported successfully'}), 201)

    def check_transaction_by_external_id(self,external_id):
        user_id = session.get('_user_id')
        transaction = TransactionModel.query.filter_by(external_id=external_id, user_id=user_id).first()
        return transaction is not None

    def ensure_category_exists(self,category_name):
        user_id = session.get('_user_id')
        category = CategoriesModel.query.filter_by(name=category_name, user_id=user_id).first()
        if not category:
            print(f"Category '{category_name}' does not exist. Creating...")
            # category = CategoriesModel(name=category_name)
            # db.session.add(category)
            # db.session.commit()
        return category.id

    def ensure_institution_exists(self,institution_name):
        user_id = session.get('_user_id')
        institution = InstitutionModel.query.filter_by(name=institution_name,user_id=user_id).first()
        if not institution:
            print(f"InstitutionModel '{institution_name}' does not exist. Creating...")
            institution = InstitutionModel(name=institution_name,user_id=user_id,location="Unknown",description="Unknown")
            db.session.add(institution)
            db.session.commit()
        return institution.id

    def ensure_account_exists(self,account_name, institution_id):
        user_id = session.get('_user_id')
        account = InstitutionAccountModel.query.filter_by(name=account_name,user_id=user_id).first()
        if not account:
            print(f"InstitutionAccountModel '{account_name}' does not exist. Creating...")
            account = InstitutionAccountModel(name=account_name, institution_id=institution_id, user_id=user_id, number="Unknown", status='active', balance=0, starting_balance=0,account_type='other',account_class='asset')
            db.session.add(account)
            db.session.commit()
        return account.id

    def create_transaction(self,user_id, categories_id, account_id, amount, transaction_type, external_id, external_date, description):
        print(f"Creating transaction {external_id}...")
        transaction = TransactionModel(
            user_id=user_id,
            categories_id=categories_id,
            account_id=account_id,
            amount=amount,
            transaction_type=transaction_type,
            external_id=external_id,
            external_date=external_date,
            description=description
        )
        db.session.add(transaction)
        db.session.commit()
        print(f"Transaction {external_id} created successfully.")
