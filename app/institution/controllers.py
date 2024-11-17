from flask import Blueprint, render_template
from flask_login import login_required

institution_blueprint = Blueprint('institution', __name__)

@institution_blueprint.route('/institution')
@login_required
def institution():
    return render_template('institution/index.html')
