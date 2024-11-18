import secrets
from flask_login import UserMixin
from app import db
from api.base.models import Base

class User(Base, UserMixin):
    __tablename__ = 'user'
    email = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(255))
    username = db.Column(db.String(100),unique=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    api_key = db.Column(db.String(64), unique=True, nullable=True)

    def __init__(self, email, username, password, first_name, last_name):
        self.email = email
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
        self.api_key = None  # Initialize without an API key

    def __repr__(self):
        return f'<User {self.username!r}>'

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def generate_api_key(self):
        """Generate a new unique API key and save it to the database."""
        self.api_key = secrets.token_hex(32)  # Generate a 64-character API key
        db.session.commit()  # Save the new key to the database
