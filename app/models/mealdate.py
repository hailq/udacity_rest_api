from app import db
from base import BaseModel


class MealDate(db.Model, BaseModel):
    __tablename__ = 'mealdate'

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    user_1 = db.Column(db.Integer, index=True)
    user_2 = db.Column(db.Integer, index=True)
    restaurant_name = db.Column(db.String(120))
    restaurant_address = db.Column(db.String(120))
    restaurant_picture = db.Column(db.String)
    meal_time = db.Column(db.String(20))

    @property
    def serialize(self):
        return {
            'id': self.id,
            'user_1': self.user_1,
            'user_2': self.user_2,
            'restaurant_name': self.restaurant_name,
            'restaurant_address': self.restaurant_address,
            'restaurant_picture': self.restaurant_picture,
            'meal_time': self.meal_time
        }
