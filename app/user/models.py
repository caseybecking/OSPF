from flask_login import UserMixin
from app import db
from api.base.models import Base

class User(Base, UserMixin):
    email = db.Column(db.String(100),unique=True)
    password = db.Column(db.String(255))
    username = db.Column(db.String(100),unique=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))

    def __init__(self,email,username,password,first_name,last_name):
        self.email = email
        self.username = username
        self.password = password
        self.first_name = first_name
        self.last_name = last_name
    
    