from app import db
from api.base.models import Base


class TransactionModel(Base):
    __tablename__ = 'transaction'
    user_id = db.Column('user_id', db.Text, db.ForeignKey('user.id'), nullable=False)
    categories_id = db.Column('categories_id', db.Text, db.ForeignKey('categories.id'), nullable=False)
    account_id = db.Column('account_id', db.Text, db.ForeignKey('account.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(255), nullable=False)

    def __init__(self, user_id, categories_id, account_id, amount, transaction_type):
        self.user_id = user_id
        self.categories_id = categories_id
        self.account_id = account_id
        self.amount = amount
        self.transaction_type = transaction_type

    def __repr__(self):
        return '<Transaction %r>' % self.id
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'categories_id': self.categories_id,
            'account_id': self.account_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()