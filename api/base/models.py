import uuid
from app import db

class Base(db.Model):
    """
    Base represents the base table in the database.
    
    Attributes:
        id (str): The ID of the base.
        created_at (datetime): The date and time the base was created.
        updated_at (datetime): The date and time the base was last updated.    
    """

    __abstract__ = True

    id = db.Column('id', db.Text, default=lambda: str(uuid.uuid4()), primary_key=True)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def save(self):
        """
        Save the Base instance to the database.
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Delete the Base instance from the database.
        """
        db.session.delete(self)
        db.session.commit()
