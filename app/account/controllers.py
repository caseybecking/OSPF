from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.user.models import User

account_blueprint = Blueprint('account', __name__)

@account_blueprint.route('/account/signup')  
def signup(): 
    return render_template('account/signup.html')

@account_blueprint.route('/account/signup',methods=['POST'])  
def signup_post():
    email = request.form.get('email') 
    username = request.form.get('username')
    password = request.form.get('password')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')

    user_email = User.query.filter_by(email=email).first()
    user_username = User.query.filter_by(username=username).first()    
    
    if user_email:
        flash("User email already Exists")
        return redirect(url_for('account.signup'))
    if user_username:    
        flash("Username already Exists")
        return redirect(url_for('account.signup'))

    new_user = User(email=email,username=username,password=generate_password_hash(password,method="scrypt"),first_name=first_name,last_name=last_name)
    db.session.add(new_user)
    db.session.commit()

    return redirect(url_for('account.login'))

@account_blueprint.route('/account/login')
def login():
    return render_template('account/login.html')

@account_blueprint.route('/account/login',methods=['POST'])  
def login_post():
    if request.method == 'POST':
        email = request.form.get('email') 
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password,password):
            flash("Invalid Credentials")
            return redirect(url_for('account.login'))

        login_user(user, remember=remember)
        return redirect(url_for('dashboards.index'))


@account_blueprint.route('/account/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('account.login'))