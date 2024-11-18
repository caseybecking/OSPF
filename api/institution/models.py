from app import db
from api.base.models import Base

class InstitutionModel(Base):
    __tablename__ = 'institution'
    user_id = db.Column('user_id', db.Text, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)


    def __init__(self, user_id, name, location, description):
        self.user_id = user_id
        self.name = name
        self.location = location
        self.description = description

    def __repr__(self):
        return f'<Institution {self.name!r}>'

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'location': self.location,
            'description': self.description,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    