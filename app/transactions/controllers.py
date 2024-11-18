from flask import Blueprint, render_template, url_for, session
from flask_login import login_required
import requests

transactions_blueprint = Blueprint('transactions', __name__)

@transactions_blueprint.route('/transactions')
@login_required
def transactions():
    """
    Render the transactions page.

    This view function fetches the transactions from an external API and renders
    the transactions/index.html template with the fetched transactions and the user ID
    from the session.

    Returns:
        str: Rendered HTML template for the transactions page.
    """
    api_url = url_for('transaction', _external=True)
    _transactions = requests.get(api_url, timeout=15).json().get('transactions', [])
    user_id = session.get('_user_id')
    return render_template('transactions/index.html', transactions=_transactions, user_id=user_id)
