from flask import Blueprint, render_template, url_for, session
from flask_login import login_required
import requests

institution_blueprint = Blueprint('institution', __name__)

@institution_blueprint.route('/institution')
@login_required
def institution():
    api_url = url_for('institution', _external=True)
    response = requests.get(api_url)
    institutions = response.json().get('institutions', [])
    user_id = session.get('_user_id')

    return render_template('institution/index.html', institutions=institutions, user_id=user_id)
