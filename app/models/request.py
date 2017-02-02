from app import db
from app.models.proposal import Proposal


class Request(db.Model):
    __tablename__ = 'request'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    user_id = db.Column(db.INTEGER, db.ForeignKey('user.id'))
    meal_type = db.Column(db.String(120))
    location_string = db.Column(db.String(256))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    meal_time = db.Column(db.String(20))
    filled = db.Column(db.Boolean)

    proposals = db.relationship('Proposal', backref='request', lazy='dynamic')

    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'meal_type': self.meal_type,
            'location_string': self.location_string,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'meal_time': self.meal_time,
            'filled': self.filled,
            'proposals': [i.serialize for i in self.proposals]
        }
