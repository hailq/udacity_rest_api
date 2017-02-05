# -*- coding: utf-8 -*-
"""
    Test udacity sample restful api
"""

import os
import unittest
import tempfile
import base64
import json
import random
from app import app, db
from app.models.user import User
from app.models.request import Request
from app.models.proposal import Proposal
from app.models.mealdate import MealDate

from config import configuration


class TestClient():
    def __init__(self, test_app, resource, username=None, password=None, api_url='/api/v1/'):
        self.app = test_app
        self.resource = resource
        self.url = api_url + self.resource

        self.headers = {
            'Content-Type': 'application/json'
        }
        if username is not None and password is not None:
            self.headers['Authorization'] = 'Basic ' + base64.b64encode(username + ":" + password)

    def get(self):
        rv = self.app.get(self.url, headers=self.headers)
        return rv, json.loads(rv.data.decode('utf-8'))

    def get_by_id(self, resource_id):
        rv = self.app.get(self.url + '/' + str(resource_id), headers=self.headers)
        return rv, json.loads(rv.data.decode('utf-8'))

    def post(self, data):
        payload = json.dumps(data) if data is not None else None
        rv = self.app.post(self.url, data=payload, headers=self.headers)
        return rv, json.loads(rv.data.decode('utf-8'))

    def put(self, data, resource_id=None):
        url = self.url
        if resource_id is not None:
            url = url + '/' + str(resource_id)
        payload = json.dumps(data) if data is not None else None
        rv = self.app.put(url, data=payload, headers=self.headers)
        return rv, json.loads(rv.data.decode('utf-8'))

    def delete(self):
        rv = self.app.delete(self.url, headers=self.headers)
        return rv, json.loads(rv.data.decode('utf-8'))


class RestTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

        self.test_user = TestClient(self.app, resource='users', username="me0", password="123456")
        self.test_request = TestClient(self.app, resource='requests', username="me0", password="123456")

        with app.app_context():
            db.create_all()

            user = User(username="me0")
            user.hash_password("123456")
            db.session.add(user)
            db.session.commit()

            request = Request(user_id=user.id, meal_time="Dinner", meal_type="Sushi", location_string="Hanoi",
                              filled=False, latitude='0.0', longitude='0.0')
            db.session.add(request)
            db.session.commit()

    def tearDown(self):
        db.drop_all()

    def new_user(self, username, password):
        return self.test_user.post({
            "username": username,
            "password": password
        })

    # User resource
    def test_post_user(self):
        res_data = self.new_user("me1", "123456")[1]
        assert "OK" in res_data['status']

        res_data = self.new_user("me1", "123456")[1]
        assert 'user already exists' in res_data['message']

    def test_put_user(self):
        updated_data = {
            "email": "test_email@mail.com",
            "picture": "www.google.com"
        }
        res_data = self.test_user.put(updated_data)[1]
        self.assertEqual(updated_data['email'], res_data['data']['email'])
        self.assertEqual(updated_data['picture'], res_data['data']['picture'])

    def test_get_all_user(self):
        res_data = self.test_user.get()[1]
        self.assertEqual("OK", res_data['status'])

    def test_get_one_user(self):
        res_data = self.test_user.get_by_id(1)[1]
        self.assertEqual("OK", res_data['status'])

        res_obj = self.test_user.get_by_id(9999)[0]
        self.assertEqual(404, res_obj.status_code)

    # Request resource
    def test_get_all_request(self):
        res_data = self.test_request.get()[1]
        self.assertEqual("OK", res_data['status'])

    def test_get_one_request(self):
        res_data = self.test_request.get_by_id(1)[1]
        self.assertEqual("OK", res_data['status'])

        res_obj = self.test_request.get_by_id(9999)[0]
        self.assertEqual(404, res_obj.status_code)

    def test_post_request(self):
        data = {
            "meal_time": "Dinner",
            "meal_type": "Sushi",
            "location_string": "Hanoi",
        }
        res_obj, res_data = self.test_request.post(data)
        self.assertEqual(201, res_obj.status_code)
        self.assertEqual(data["meal_time"], res_data["data"]["meal_time"])
        self.assertEqual(data["meal_type"], res_data["data"]["meal_type"])
        self.assertEqual(data["location_string"], res_data["data"]["location_string"])

        data = {
            "meal_time": "Dinner",
            "location_string": "Hanoi",
        }
        res_obj, res_data = self.test_request.post(data)
        self.assertEqual(400, res_obj.status_code)
        self.assertEqual("Missing arguments", res_data["message"])

        data = {
            "meal_type": "Sushi",
            "location_string": "Hanoi",
        }
        res_obj, res_data = self.test_request.post(data)
        self.assertEqual(400, res_obj.status_code)
        self.assertEqual("Missing arguments", res_data["message"])

        data = {
            "meal_time": "Dinner",
            "meal_type": "Sushi",
        }
        res_obj, res_data = self.test_request.post(data)
        self.assertEqual(400, res_obj.status_code)
        self.assertEqual("Missing arguments", res_data["message"])

    def test_put_request(self):
        updated_data = {
            "meal_time": "Dinner",
            "meal_type": "Sushi",
            "location_string": "Hanoi",
            "filled": True
        }
        res_data = self.test_request.put(updated_data, 1)[1]
        self.assertEqual("OK", res_data['status'])


if __name__ == '__main__':
    unittest.main()
