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
        return '<Institution %r>' % self.name

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()
    