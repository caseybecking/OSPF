from app import db
from api.base.models import Base

class InstitutionAccountModel(Base):
    __tablename__ = 'account'
    institution_id = db.Column('institution_id', db.Text, db.ForeignKey('institution.id'), nullable=False)
    institution = db.relationship('InstitutionModel', backref='account')
    user_id = db.Column('user_id', db.Text, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    status = db.Column(db.Enum('active', 'inactive',name='status_enum'), nullable=False)
    balance = db.Column(db.Float, nullable=True)
    starting_balance = db.Column(db.Float, nullable=True)
    account_type = db.Column(db.Enum('checking', 'savings', 'credit', 'loan', 'investment', 'other', name='account_type_enum'), nullable=True)
    account_class = db.Column(db.Enum('asset','liability', name='account_class_enum'), nullable=True)
    number = db.Column(db.String(255), nullable=True)

    def __init__(self, institution_id, user_id, name, status, balance, starting_balance, account_type, account_class, number):
        self.institution_id = institution_id
        self.user_id = user_id
        self.name = name
        self.status = status
        self.balance = balance
        self.starting_balance = starting_balance
        self.account_type = account_type
        self.account_class = account_class
        self.number = number

    def __repr__(self):
        return f'<Account {self.name!r}>'

    def to_dict(self):
        return {
            'id': self.id,
            'institution_id': self.institution_id,
            'institution': self.institution.to_dict(),
            'user_id': self.user_id,
            'name': self.name,
            'status': self.status,
            'balance': self.balance,
            'starting_balance': self.starting_balance,
            'account_type': self.account_type,
            'account_class': self.account_class,
            'number': self.number,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
