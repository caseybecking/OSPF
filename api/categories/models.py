from app import db
from api.base.models import Base

class CategoriesModel(Base):
    """
    CategoriesModel represents the categories table in the database.

    Attributes:
        user_id (str): The ID of the user associated with the category.
        name (str): The name of the category.
        categories_group_id (str): The ID of the categories group.
        categories_type_id (str): The ID of the categories type.
    """

    __tablename__ = 'categories'
    user_id = db.Column('user_id', db.Text, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    categories_group_id = db.Column('categories_group_id', db.Text, db.ForeignKey('categories_group.id'), nullable=False)
    categories_type_id = db.Column('categories_type_id', db.Text, db.ForeignKey('categories_type.id'), nullable=False)
    categories_group = db.relationship('CategoriesGroupModel', backref='categories')
    categories_type = db.relationship('CategoriesTypeModel', backref='categories')

    def __init__(self, user_id, categories_group_id, categories_type_id, name):
        """
        Initialize a CategoriesModel instance.

        Args:
            user_id (str): The ID of the user associated with the category.
            categories_group_id (str): The ID of the categories group.
            categories_type_id (str): The ID of the categories type.
            name (str): The name of the category.
        """
        self.user_id = user_id
        self.categories_group_id = categories_group_id
        self.categories_type_id = categories_type_id
        self.name = name

    def __repr__(self):
        """
        Return a string representation of the CategoriesModel instance.

        Returns:
            str: String representation of the category.
        """
        return '<Categories %r>' % self.name

    def to_dict(self):
        """
        Convert the CategoriesModel instance to a dictionary.

        Returns:
            dict: Dictionary representation of the category.
        """
        return {
            'id': self.id,
            'user_id': self.user_id,
            'categories_group_id': self.categories_group_id,
            'categories_type_id': self.categories_type_id,
            'categories_group': self.categories_group.to_dict(),
            'categories_type': self.categories_type.to_dict(),
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self):
        """
        Save the CategoriesModel instance to the database.
        """
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """
        Delete the CategoriesModel instance from the database.
        """
        db.session.delete(self)
        db.session.commit()
