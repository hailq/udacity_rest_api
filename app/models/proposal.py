from app import db
from base import BaseModel


class Proposal(db.Model, BaseModel):
    __tablename__ = 'proposal'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    user_proposed_to = db.Column(db.Integer, index=True)
    user_proposed_from = db.Column(db.Integer, index=True)
    request_id = db.Column(db.INTEGER, db.ForeignKey('request.id'))
    filled = db.Column(db.Boolean)

    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_proposed_to': self.user_proposed_to,
            'user_proposed_from': self.user_proposed_from,
            'request_id': self.request_id,
            'filled': self.filled
        }
