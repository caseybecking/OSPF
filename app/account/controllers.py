from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.user.models import User

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