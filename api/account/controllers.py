from flask import request, g, jsonify, make_response
from flask_restx import Resource, fields
from flask_login import login_user
from werkzeug.security import generate_password_hash, check_password_hash
from api.user.models import User

account_model = g.api.model('Account', {
    'email': fields.String(required=True, description='Email'),
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
    'first_name': fields.String(required=True, description='First Name'),
    'last_name': fields.String(required=True, description='Last Name')
})

login_model = g.api.model('Login', {
    'email': fields.String(required=True, description='Email'),
    'password': fields.String(required=True, description='Password'),
    'remember': fields.Boolean(description='Remember Me')
})

@g.api.route('/account/signup')
class Signup(Resource):
    """
    Signup Resource for creating a new user account.

    This resource handles the POST request to create a new user account. It expects
    a JSON payload with the user's email, username, password, first name, and last name.
    It checks if the email or username already exists in the database and returns an error
    message if they do. Otherwise, it creates a new user with the provided details.

    Methods:
        post: Handle POST requests to create a new user account.
    """
    @g.api.expect(account_model)
    def post(self):
        """
        Handle POST requests to create a new user account.

        This method extracts the user details from the request JSON payload, checks if the
        email or username already exists in the database, and returns an error message if they do.
        If the email and username are unique, it creates a new user with the provided details
        and hashes the password using the scrypt method.

        Returns:
            Response: JSON response with a success or error message.
        """
        data = request.json
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        user_email = User.query.filter_by(email=email).first()
        user_username = User.query.filter_by(username=username).first()

        if user_email:
            return make_response(jsonify({'message': 'User email already exists'}), 400)
        if user_username:
            return make_response(jsonify({'message': 'Username already exists'}), 400)

        new_user = User(
            email=email,
            username=username,
            password=generate_password_hash(password, method='scrypt'),
            first_name=first_name,
            last_name=last_name
        )
        new_user.save()

        return make_response(jsonify({'message': 'User created successfully', 'redirect': '/account/login'}), 201)

@g.api.route('/account/login')
class Login(Resource):
    @g.api.expect(login_model)
    def post(self):
        data = request.json
        email = data.get('email')
        password = data.get('password')
        remember = data.get('remember')

        user = User.query.filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            return make_response(jsonify({'message': 'Invalid Credentials'}), 400)

        login_user(user, remember=remember)

        return make_response(jsonify({'message': 'User logged in successfully', 'redirect': '/'}), 200)
