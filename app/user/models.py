from flask_login import UserMixin
from app import db

class User(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
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
    
    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    