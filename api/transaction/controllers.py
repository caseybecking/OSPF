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
    'merchant': fields.String(description='Merchant Name'),
    'original_statement': fields.String(description='Original Statement'),
    'notes': fields.String(description='Notes'),
    'tags': fields.String(description='Tags'),
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
        merchant = data.get('merchant')
        original_statement = data.get('original_statement')
        notes = data.get('notes')
        tags = data.get('tags')
        description = data.get('description')

        # Validate required fields
        if not all([user_id, categories_id, account_id, amount, transaction_type]):
            return make_response(jsonify({
                'message': 'All required fields must be provided'
            }), 400)

        # Validate amount is a number
        try:
            amount = float(amount)
        except (ValueError, TypeError):
            return make_response(jsonify({
                'message': 'Amount must be a valid number'
            }), 400)

        new_transaction = TransactionModel(
            user_id=user_id,
            categories_id=categories_id,
            account_id=account_id,
            amount=amount,
            transaction_type=transaction_type,
            external_id=external_id,
            external_date=external_date,
            merchant=merchant,
            original_statement=original_statement,
            notes=notes,
            tags=tags,
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
    """
    Import transactions from CSV file

    Expected CSV format:
    Date,Merchant,Category,Account,Original Statement,Notes,Amount,Tags
    """

    def post(self):
        user_id = session.get('_user_id')

        if not user_id:
            return make_response(jsonify({'message': 'User not authenticated'}), 401)

        if 'file' not in request.files:
            return make_response(jsonify({'message': 'No file provided'}), 400)

        file = request.files['file']

        if file.filename == '':
            return make_response(jsonify({'message': 'No file selected'}), 400)

        if not file.filename.endswith('.csv'):
            return make_response(jsonify({'message': 'File must be a CSV'}), 400)

        try:
            upload_folder = Config.UPLOAD_FOLDER
            filename = secure_filename(file.filename)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            created_count = 0
            skipped_count = 0
            error_count = 0
            errors = []

            with open(file_path, newline='', encoding='utf-8') as csvfile:
                csvreader = csv.DictReader(csvfile)

                # Validate required headers
                required_headers = ['Date', 'Merchant', 'Category', 'Account', 'Amount']
                if not all(header in csvreader.fieldnames for header in required_headers):
                    os.remove(file_path)
                    return make_response(jsonify({
                        'message': f'CSV must have headers: {", ".join(required_headers)}'
                    }), 400)

                for row_num, row in enumerate(csvreader, start=2):  # Start at 2 (after header)
                    try:
                        # Get required fields
                        date_str = row.get('Date', '').strip()
                        merchant = row.get('Merchant', '').strip()
                        category_name = row.get('Category', '').strip()
                        account_name = row.get('Account', '').strip()
                        amount_str = row.get('Amount', '').strip()

                        # Get optional fields
                        original_statement = row.get('Original Statement', '').strip()
                        notes = row.get('Notes', '').strip()
                        tags = row.get('Tags', '').strip()

                        # Skip empty rows
                        if not all([date_str, merchant, category_name, account_name, amount_str]):
                            skipped_count += 1
                            continue

                        # Parse date
                        try:
                            # Try multiple date formats
                            for date_format in ["%m/%d/%Y", "%Y-%m-%d", "%m-%d-%Y", "%d/%m/%Y"]:
                                try:
                                    dt_object = datetime.strptime(date_str, date_format)
                                    break
                                except ValueError:
                                    continue
                            else:
                                raise ValueError(f"Unable to parse date: {date_str}")

                            formatted_timestamp = dt_object.strftime("%Y-%m-%d %H:%M:%S")
                        except ValueError as e:
                            errors.append(f"Row {row_num}: {str(e)}")
                            error_count += 1
                            continue

                        # Parse amount
                        try:
                            _amount = clean_dollar_value(amount_str)
                        except:
                            errors.append(f"Row {row_num}: Invalid amount '{amount_str}'")
                            error_count += 1
                            continue

                        _transaction_type = positive_or_negative(_amount)

                        # Create unique external ID from date + merchant + amount
                        external_id = f"{date_str}-{merchant}-{amount_str}".replace('/', '-').replace(' ', '-')

                        # Check if transaction already exists
                        if self.check_transaction_by_external_id(external_id):
                            skipped_count += 1
                            continue

                        # Ensure category exists
                        category_id = self.ensure_category_exists(category_name)
                        if not category_id:
                            errors.append(f"Row {row_num}: Category '{category_name}' not found")
                            error_count += 1
                            continue

                        # Ensure account exists (create if needed with merchant as institution)
                        account_id = self.ensure_account_exists_smart(account_name, merchant)
                        if not account_id:
                            errors.append(f"Row {row_num}: Could not create account '{account_name}'")
                            error_count += 1
                            continue

                        # Store fields separately (no joining)
                        # Description can be used for additional custom info if needed
                        description = None  # Keep empty unless specifically provided

                        # Create transaction with all fields separate
                        self.create_transaction(
                            user_id=user_id,
                            categories_id=category_id,
                            account_id=account_id,
                            amount=_amount,
                            transaction_type=_transaction_type,
                            external_id=external_id,
                            external_date=formatted_timestamp,
                            merchant=merchant,
                            original_statement=original_statement,
                            notes=notes,
                            tags=tags,
                            description=description
                        )
                        created_count += 1

                    except Exception as e:
                        errors.append(f"Row {row_num}: {str(e)}")
                        error_count += 1
                        continue

            # Clean up uploaded file
            os.remove(file_path)

            response_data = {
                'message': 'Import completed',
                'transactions_created': created_count,
                'transactions_skipped': skipped_count,
                'errors': error_count
            }

            if errors:
                # Show first 50 errors to understand patterns
                response_data['error_details'] = errors[:50]
                # Also include a summary of error types
                error_summary = {}
                for error in errors:
                    # Extract error type
                    if "Category" in error and "not found" in error:
                        error_summary['category_not_found'] = error_summary.get('category_not_found', 0) + 1
                    elif "Could not create account" in error:
                        error_summary['account_creation_failed'] = error_summary.get('account_creation_failed', 0) + 1
                    elif "Could not parse" in error:
                        error_summary['date_parse_error'] = error_summary.get('date_parse_error', 0) + 1
                    elif "Invalid amount" in error:
                        error_summary['invalid_amount'] = error_summary.get('invalid_amount', 0) + 1
                    else:
                        error_summary['other'] = error_summary.get('other', 0) + 1
                response_data['error_summary'] = error_summary

            return make_response(jsonify(response_data), 201 if created_count > 0 else 200)

        except Exception as e:
            if os.path.exists(file_path):
                os.remove(file_path)
            return make_response(jsonify({'message': f'Error processing CSV: {str(e)}'}), 500)

    def check_transaction_by_external_id(self,external_id):
        user_id = session.get('_user_id')
        transaction = TransactionModel.query.filter_by(external_id=external_id, user_id=user_id).first()
        return transaction is not None

    def ensure_category_exists(self, category_name):
        """Find category by name, return ID or None if not found"""
        user_id = session.get('_user_id')
        category = CategoriesModel.query.filter_by(name=category_name, user_id=user_id).first()
        if category:
            return category.id
        return None

    def ensure_institution_exists(self,institution_name):
        user_id = session.get('_user_id')
        institution = InstitutionModel.query.filter_by(name=institution_name,user_id=user_id).first()
        if not institution:
            print(f"InstitutionModel '{institution_name}' does not exist. Creating...")
            institution = InstitutionModel(name=institution_name,user_id=user_id,location="Unknown",description="Unknown")
            db.session.add(institution)
            db.session.commit()
        return institution.id

    def ensure_account_exists(self, account_name, institution_id):
        """Legacy method for backward compatibility"""
        user_id = session.get('_user_id')
        account = InstitutionAccountModel.query.filter_by(name=account_name, user_id=user_id).first()
        if not account:
            account = InstitutionAccountModel(
                name=account_name,
                institution_id=institution_id,
                user_id=user_id,
                number="Unknown",
                status='active',
                balance=0,
                starting_balance=0,
                account_type='other',
                account_class='asset'
            )
            db.session.add(account)
            db.session.commit()
        return account.id

    def ensure_account_exists_smart(self, account_name, merchant_name):
        """
        Find or create account with smart institution handling
        Uses merchant name as institution if institution doesn't exist
        """
        user_id = session.get('_user_id')

        # Check if account exists
        account = InstitutionAccountModel.query.filter_by(name=account_name, user_id=user_id).first()
        if account:
            return account.id

        # Account doesn't exist, create it with institution
        # Use merchant as institution name
        institution = InstitutionModel.query.filter_by(name=merchant_name, user_id=user_id).first()
        if not institution:
            # Create institution with merchant name
            institution = InstitutionModel(
                user_id=user_id,
                name=merchant_name,
                location="Auto-created",
                description=f"Auto-created from transaction import for {account_name}"
            )
            db.session.add(institution)
            db.session.commit()

        # Create account
        account = InstitutionAccountModel(
            name=account_name,
            institution_id=institution.id,
            user_id=user_id,
            number="Auto-imported",
            status='active',
            balance=0,
            starting_balance=0,
            account_type='checking',
            account_class='asset'
        )
        db.session.add(account)
        db.session.commit()

        return account.id

    def create_transaction(self,user_id, categories_id, account_id, amount, transaction_type, external_id, external_date, merchant=None, original_statement=None, notes=None, tags=None, description=None):
        print(f"Creating transaction {external_id}...")
        transaction = TransactionModel(
            user_id=user_id,
            categories_id=categories_id,
            account_id=account_id,
            amount=amount,
            transaction_type=transaction_type,
            external_id=external_id,
            external_date=external_date,
            merchant=merchant,
            original_statement=original_statement,
            notes=notes,
            tags=tags,
            description=description
        )
        db.session.add(transaction)
        db.session.commit()
        print(f"Transaction {external_id} created successfully.")


@g.api.route('/transaction/<string:id>')
class TransactionDetail(Resource):
    def get(self, id):
        """Get a single transaction by ID"""
        transaction = TransactionModel.query.get(id)
        if not transaction:
            return make_response(jsonify({'message': 'Transaction not found'}), 404)

        return make_response(jsonify({'transaction': transaction.to_dict()}), 200)

    @g.api.expect(transaction_model)
    def put(self, id):
        """Update a transaction"""
        transaction = TransactionModel.query.get(id)
        if not transaction:
            return make_response(jsonify({'message': 'Transaction not found'}), 404)

        data = request.json

        # Validate amount if provided
        if 'amount' in data:
            try:
                amount = float(data['amount'])
            except (ValueError, TypeError):
                return make_response(jsonify({
                    'message': 'Amount must be a valid number'
                }), 400)

        # Validate foreign keys if provided
        if 'categories_id' in data:
            category = CategoriesModel.query.get(data['categories_id'])
            if not category:
                return make_response(jsonify({
                    'message': 'Invalid categories_id'
                }), 400)

        if 'account_id' in data:
            account = InstitutionAccountModel.query.get(data['account_id'])
            if not account:
                return make_response(jsonify({
                    'message': 'Invalid account_id'
                }), 400)

        # Update fields if provided
        if 'merchant' in data:
            transaction.merchant = data['merchant']
        if 'original_statement' in data:
            transaction.original_statement = data['original_statement']
        if 'notes' in data:
            transaction.notes = data['notes']
        if 'tags' in data:
            transaction.tags = data['tags']
        if 'description' in data:
            transaction.description = data['description']
        if 'amount' in data:
            transaction.amount = float(data['amount'])
        if 'categories_id' in data:
            transaction.categories_id = data['categories_id']
        if 'account_id' in data:
            transaction.account_id = data['account_id']
        if 'transaction_type' in data:
            transaction.transaction_type = data['transaction_type']
        if 'external_date' in data:
            transaction.external_date = data['external_date']
        if 'external_id' in data:
            transaction.external_id = data['external_id']

        transaction.save()

        return make_response(jsonify({'message': 'Transaction updated successfully', 'transaction': transaction.to_dict()}), 200)

    def delete(self, id):
        """Delete a transaction"""
        transaction = TransactionModel.query.get(id)
        if not transaction:
            return make_response(jsonify({'message': 'Transaction not found'}), 404)

        transaction.delete()

        return make_response(jsonify({'message': 'Transaction deleted successfully'}), 200)
