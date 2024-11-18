from flask import Blueprint, render_template, redirect, url_for
from flask_login import logout_user, login_required

account_blueprint = Blueprint('account', __name__)

@account_blueprint.route('/account/signup')
def signup():
    return render_template('account/signup.html')

@account_blueprint.route('/account/login')
def login():
    return render_template('account/login.html')

@account_blueprint.route('/account/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('account.login'))
