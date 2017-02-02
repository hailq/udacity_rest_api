from app import app, db, auth
from app.models.request import Request
from flask import request, jsonify, abort, g

from app.utils.rate_limit import ratelimit

import app.utils.geocode as geocode


@app.route('/api/v1/requests', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def get_request():
    return get_all_open_request()


@app.route('/api/v1/requests/<int:id>', methods=['GET'])
@ratelimit(limit=180, per=60)
def get_one_request(id):
    req = Request.query.filter_by(id=id).first()
    if not req:
        return jsonify({'status': 'Not found', 'data': None}), 404
    return jsonify({'status': 'OK', 'data': req.serialize})


@app.route('/api/v1/requests', methods=['POST'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def post_request():
    return create_new_request()


@app.route('/api/v1/requests/<int:id>', methods=['PUT'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def put_request(id):
    req = Request.query.filter_by(id=id).filter_by(user_id=g.user.id).filter_by(filled=False).one()

    if not req:
        abort(400)

    new_filled = request.json.get('filled')
    new_meal_type = request.json.get('meal_type')
    new_meal_time = request.json.get('meal_time')
    new_location_string = request.json.get('location_string')

    if new_meal_type is not None:
        req.meal_type = new_meal_type

    if new_meal_time is not None:
        req.meal_time = new_meal_time

    if new_filled is not None:
        req.filled = new_filled

    if new_location_string is not None:
        new_latitude, new_longitude = geocode.getGeocodeLocation(new_location_string)

        req.location_string = new_location_string
        req.latitude = new_latitude
        req.longitude = new_longitude

    db.session.commit()

    return jsonify({'status': 'OK', 'message': 'Request updated successfully'}), 200


@app.route('/api/v1/requests/<int:id>', methods=['DELETE'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def delete_request(id):
    req = Request.query.filter_by(id=id).filter_by(user_id=g.user.id).first()

    if not req:
        abort(400)

    db.session.delete(req)
    db.session.commit()

    return jsonify({'status': 'OK', 'message': 'Request deleted successfully'}), 200


def get_all_open_request():
    requests = Request.query.filter(Request.user_id != g.user.id).all()
    return jsonify({'status': 'OK', 'data': [i.serialize for i in requests]})


def create_new_request():
    user_id = g.user.id
    meal_type = request.json.get('meal_type')
    location_string = request.json.get('location_string')
    meal_time = request.json.get('meal_time')
    filled = False

    if meal_type is None or location_string is None or meal_time is None:
        return jsonify({'status': 'Error', 'message': 'Missing arguments'}), 400

    latitude, longitude = geocode.getGeocodeLocation(location_string)

    new_request = Request(user_id=user_id, meal_time=meal_time, meal_type=meal_type, location_string=location_string,
                          filled=filled, latitude=latitude, longitude=longitude)

    db.session.add(new_request)
    db.session.commit()
    return jsonify({
        'status': 'OK',
        'message': 'New request created successfully',
        'data': new_request.serialize
    }), 201
