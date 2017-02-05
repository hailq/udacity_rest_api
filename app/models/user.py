from app import db
from base import BaseModel

from passlib.apps import custom_app_context as pwd_context
import random, string
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)

secret_key = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))


class User(db.Model, BaseModel):
    __tablename__ = 'user'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    username = db.Column(db.String(32), unique=True, index=True)
    password_hash = db.Column(db.String(64))
    email = db.Column(db.String(120), unique=True, index=True)
    picture = db.Column(db.String)

    requests = db.relationship('Request', backref='user', lazy='dynamic')

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)

    def generate_auth_token(self, expiration=600):
        s = Serializer(secret_key, expires_in=expiration)
        return s.dumps({'id': self.id})

    @property
    def serialize(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'picture': self.picture,
            'requests': [i.serialize for i in self.requests]
        }

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(secret_key)
        try:
            data = s.loads(token)
        except SignatureExpired:
            # Valid Token, but expired
            return None
        except BadSignature:
            # Invalid Token
            return None
        user_id = data['id']
        return user_id
