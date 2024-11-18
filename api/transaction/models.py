from app import db
from api.base.models import Base

class TransactionModel(Base):
    """
    TransactionModel represents the transaction table in the database.

    Attributes:
        user_id (str): The ID of the user associated with the transaction.
        categories_id (str): The ID of the category associated with the transaction.
        account_id (str): The ID of the account associated with the transaction.
        amount (float): The amount of the transaction.
        type (str): The type of the transaction.
        external_id (str): The external ID of the transaction.
    """

    __tablename__ = 'transaction'
    user_id = db.Column('user_id', db.Text, db.ForeignKey('user.id'), nullable=False)
    categories_id = db.Column('categories_id', db.Text, db.ForeignKey('categories.id'), nullable=False)
    account_id = db.Column('account_id', db.Text, db.ForeignKey('account.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    transaction_type = db.Column(db.String(255), nullable=False)
    external_id = db.Column(db.String(255), nullable=False)

    def __init__(self, user_id, categories_id, account_id, amount, transaction_type, external_id):
        """
        Initialize a TransactionModel instance.

        Args:
            user_id (str): The ID of the user associated with the transaction.
            categories_id (str): The ID of the category associated with the transaction.
            account_id (str): The ID of the account associated with the transaction.
            amount (float): The amount of the transaction.
            transaction_type (str): The transaction_type of the transaction.
            external_id (str): The external ID of the transaction.
        """
        self.user_id = user_id
        self.categories_id = categories_id
        self.account_id = account_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.external_id = external_id

    def __repr__(self):
        """
        Return a string representation of the TransactionModel instance.

        Returns:
            str: String representation of the transaction.
        """
        return f'<Transaction {self.id!r}>'

    def to_dict(self):
        """
        Convert the TransactionModel instance to a dictionary.

        Returns:
            dict: Dictionary representation of the transaction.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'categories_id': self.categories_id,
            'account_id': self.account_id,
            'amount': self.amount,
            'transaction_type': self.transaction_type,
            'external_id': self.external_id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self):
        """
        Save the TransactionModel instance to the database.
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Delete the TransactionModel instance from the database.
        """
        db.session.delete(self)
        db.session.commit()
