from flask import g, request, jsonify, make_response
from flask_restx import Resource, fields
from api.user.models import User as _user_model

user_model = g.api.model('User', {
    'email': fields.String(required=True, description='Email'),
    'username': fields.String(required=True, description='Username'),
    'password': fields.String(required=True, description='Password'),
    'first_name': fields.String(required=True, description='First Name'),
    'last_name': fields.String(required=True, description='Last Name')
    })

@g.api.route('/user')
class User(Resource):
    @g.api.expect(user_model)
    def post(self):
        data = request.json
        email = data.get('email')
        username = data.get('username')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')

        user_email = _user_model.query.filter_by(email=email).first()
        user_username = _user_model.query.filter_by(username=username).first()

        if user_email:
            return make_response(jsonify({'message': 'User email already exists'}), 400)
        if user_username:
            return make_response(jsonify({'message': 'Username already exists'}), 400)

        new_user = _user_model(
            email=email,
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        new_user.save()

        return make_response(jsonify({'message': 'User created successfully'}), 201)

    def get(self):
        users = _user_model.query.all()
        users = [user.to_dict() for user in users]
        return make_response(jsonify({'users': users}), 200)
