from flask import Blueprint, render_template, url_for
from flask_login import login_required
import requests


institution_account_blueprint = Blueprint('institution_account', __name__)

@institution_account_blueprint.route('/account')
@login_required
def institution_account():
    api_url = url_for('institution_account', _external=True)
    response = requests.get(api_url)
    accounts = response.json().get('accounts', [])

    return render_template('institution_account/index.html', accounts=accounts)
