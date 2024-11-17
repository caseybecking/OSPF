from app import db
from api.base.models import Base

# - Categories
#     - User ID
#     - Categories Group ID
#     - Categories Type ID
#     - Name

class CategoriesModel(Base):
    __tablename__ = 'categories'
    user_id = db.Column('user_id', db.Text, db.ForeignKey('user.id'), nullable=False)
    categories_group_id = db.Column('categories_group_id', db.Text, db.ForeignKey('categories_group.id'), nullable=False)
    categories_type_id = db.Column('categories_type_id', db.Text, db.ForeignKey('categories_type.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)

    def __init__(self, user_id, categories_group_id, categories_type_id, name):
        self.user_id = user_id
        self.categories_group_id = categories_group_id
        self.categories_type_id = categories_type_id
        self.name = name

    def __repr__(self):
        return '<Categories %r>' % self.name
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'categories_group_id': self.categories_group_id,
            'categories_type_id': self.categories_type_id,
            'name': self.name,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()