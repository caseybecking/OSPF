from flask import Blueprint, render_template
from flask_login import login_required

institution_account_blueprint = Blueprint('institution_account', __name__)

@institution_account_blueprint.route('/account')
@login_required
def institution_account():
    return render_template('institution_account/index.html')
