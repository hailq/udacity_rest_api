import datetime

from app import db


def _get_date():
    return datetime.datetime.now()


class BaseModel():
    created_at = db.Column(db.DateTime, default=_get_date)
    modified_at = db.Column(db.DateTime, onupdate=_get_date)
