from app import app, db, auth
from app.models.request import Request
from app.models.proposal import Proposal
from app.models.mealdate import MealDate
from flask import request, jsonify, abort, g
from sqlalchemy import or_

from app.utils.rate_limit import ratelimit

import app.utils.restaurant_finder as restaurant_finder


@app.route('/api/v1/dates', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def get_date():
    return get_all_date()


@app.route('/api/v1/dates/<int:id>', methods=['GET'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def get_one_date(id):
    date = MealDate.query \
        .filter_by(id=id) \
        .filter(or_(MealDate.user_1 == g.user.id, MealDate.user_2 == g.user.id)) \
        .first()

    if not date:
        return jsonify({'status': 'Not found', 'data': None}), 404
    return jsonify({'status': 'OK', 'data': date.serialize})


@app.route('/api/v1/dates', methods=['POST'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def post_date():
    return create_new_date()


@app.route('/api/v1/dates/<int:id>', methods=['PUT'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def put_date(id):
    mealdate = MealDate.query \
        .filter_by(id=id) \
        .filter(or_(MealDate.user_1 == g.user.id, MealDate.user_2 == g.user.id)) \
        .first()

    if not mealdate:
        abort(400)

    new_address = request.json.get('address')
    new_name = request.json.get('name')
    new_picture = request.json.get('picture')
    new_time = request.json.get('time')

    if new_address is not None:
        mealdate.restaurant_address = new_address

    if new_name is not None:
        mealdate.restaurant_name = new_name

    if new_picture is not None:
        mealdate.restaurant_picture = new_picture

    if new_time is not None:
        mealdate.meal_time = new_time

    db.session.commit()

    return jsonify({'status': 'OK', 'message': 'Meal date updated successfully'}), 200


@app.route('/api/v1/dates/<int:id>', methods=['DELETE'])
@auth.login_required
@ratelimit(limit=180, per=60, scope_func=lambda: g.user.id)
def delete_date(id):
    mealdate = MealDate.query \
        .filter_by(id=id) \
        .filter(or_(MealDate.user_1 == g.user.id, MealDate.user_2 == g.user.id)) \
        .first()

    if not mealdate:
        abort(400)

    db.session.delete(mealdate)
    db.session.commit()

    return jsonify({'status': 'OK', 'message': 'Meal date deleted successfully'}), 200


def get_all_date():
    dates = MealDate.query.filter(
        or_(MealDate.user_1 == g.user.id, MealDate.user_2 == g.user.id)
    ).all()
    return jsonify({'status': 'OK', 'data': [i.serialize for i in dates]})


def create_new_date():
    user_id = g.user.id
    action = request.json.get('action')
    proposal_id = request.json.get('proposal_id')

    proposal = Proposal.query \
        .filter_by(id=proposal_id) \
        .filter_by(user_proposed_to=user_id).one()

    if action:
        # Accept the proposal
        mealdate = MealDate()
        mealdate.user_1 = proposal.user_proposed_to
        mealdate.user_2 = proposal.user_proposed_from
        mealdate.meal_time = proposal.request.meal_time

        meal_info = restaurant_finder.findARestaurant(proposal.request.meal_type, proposal.request.location_string)

        if meal_info is not None:

            mealdate.restaurant_address = meal_info['address']
            mealdate.restaurant_name = meal_info['name']
            mealdate.restaurant_picture = meal_info['image']

            db.session.add(mealdate)
            db.session.commit()

            return jsonify({
                'status': 'OK',
                'message': 'New date created successfully',
                'data': mealdate.serialize
            }), 201
        else:
            return jsonify({
                'status': 'OK',
                'message': 'Cannot create a date'
            }), 200

    else:
        # Reject the proposal
        db.session.delete(proposal)
        db.session.commit()

        return jsonify({'status': 'OK', 'message': 'Proposal deleted successfully'}), 200
