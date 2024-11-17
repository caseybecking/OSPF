from app import db
from api.base.models import Base

class InstitutionAccountModel(Base):
    __tablename__ = 'account'
    institution_id = db.Column('institution_id', db.Text, db.ForeignKey('institution.id'), nullable=False)
    user_id = db.Column('user_id', db.Text, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    number = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(255), nullable=False)
    balance = db.Column(db.Float, nullable=False)

    def __init__(self, institution_id, user_id, name, number, status, balance):
        self.institution_id = institution_id
        self.user_id = user_id
        self.name = name
        self.number = number
        self.status = status
        self.balance = balance

    def __repr__(self):
        return '<Account %r>' % self.name
    
    def to_dict(self):
        return {
            'id': self.id,
            'institution_id': self.institution_id,
            'user_id': self.user_id,
            'name': self.name,
            'number': self.number,
            'status': self.status,
            'balance': self.balance,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()


